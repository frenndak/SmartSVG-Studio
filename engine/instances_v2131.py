"""SmartSVG V21.3.1 - audited conservative per-instance Florence-2 -> SAM2 orchestration.

Runs a mask model *on each detected crop*, not on a combined class prompt.
A box is never a cut shape. Failure is explicit; no synthetic inference.
"""
from __future__ import annotations

import gc
import json
import math
import re
import unicodedata
from typing import Any
import cv2
import numpy as np

MAX_IMAGE_PIXELS = 5_000_000
MAX_OBJECTS = 12
MAX_TOTAL_MASK_VALUES = 50_000_000
MAX_CROP_PIXELS = 4_000_000
CROP_MARGIN = .12
PROFILE_PROMPTS = {
    'Trois renards': ('fox',),
    'Courage / chien': ('dog',),
    'Canard / objet': ('duck',),
    'Personnages': ('person', 'human'),
    'Animaux': ('fox', 'dog', 'duck', 'cat', 'bird'),
    'Automatique': ('person', 'fox', 'dog', 'duck', 'cat', 'bird'),
}

class InstanceError(ValueError): pass

# French interface aliases are canonicalized before matching allowed English
# prompt classes. No free-text semantic guesses are made from the labels.
LABEL_ALIASES = {
    'renard':'fox', 'renards':'fox', 'foxes':'fox',
    'chien':'dog', 'chiens':'dog', 'dogs':'dog',
    'canard':'duck', 'canards':'duck', 'ducks':'duck',
    'personne':'person', 'personnes':'person', 'people':'person',
    'humain':'human', 'humains':'human', 'humans':'human',
    'chat':'cat', 'chats':'cat', 'cats':'cat',
    'oiseau':'bird', 'oiseaux':'bird', 'birds':'bird',
}

def canonical_label(value):
    if not isinstance(value,str) or len(value)>80:
        return ''
    value=''.join(c for c in unicodedata.normalize('NFKD',value.lower().strip())
                  if not unicodedata.combining(c)).replace('_',' ')
    return LABEL_ALIASES.get(value,value)

def _cuda_oom(exc):
    # Never continue after an actual CUDA allocator failure. A partially
    # successful batch could otherwise be published as a complete extraction.
    name=type(exc).__name__.lower()
    message=str(exc).lower()
    return name=='outofmemoryerror' or ('cuda' in message and 'out of memory' in message) or 'cudnn_status_alloc_failed' in message


def validate_rgb(image):
    im=np.asarray(image)
    if im.dtype!=np.uint8 or im.ndim!=3 or im.shape[2]!=3:
        raise InstanceError('RGB uint8 [H,W,3] requis')
    if not 1<=im.shape[0]*im.shape[1]<=MAX_IMAGE_PIXELS:
        raise InstanceError('Image >5 Mp ou vide : réduire avant détection')
    return im


def _box(source,shape):
    h,w=shape
    try:
        a=np.array(source,dtype=np.float64)
    except (ValueError, TypeError) as exc:
        raise InstanceError('Coordonnées de boîte invalides') from exc
    if a.shape!=(4,) or not np.isfinite(a).all():
        raise InstanceError('Boîte non finie ou dimensions invalides')
    x0,y0,x1,y1=map(float,a)
    if x1<=x0 or y1<=y0:
        raise InstanceError('Boîte inversée ou dégénérée')
    # Reject boxes outside image instead of silently clamping a wrong coordinate space.
    if x0<0 or y0<0 or x1>w or y1>h:
        raise InstanceError('Boîte hors image : coordonnées source requises')
    if (x1-x0)*(y1-y0)<max(64,w*h*.0001):
        raise InstanceError('Boîte trop petite')
    return (int(math.floor(x0)),int(math.floor(y0)),int(math.ceil(x1)),int(math.ceil(y1)))


def _iou_box(a,b):
    inter=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    sa=(a[2]-a[0])*(a[3]-a[1]);sb=(b[2]-b[0])*(b[3]-b[1])
    return inter/(sa+sb-inter) if sa+sb>inter else 0.


def normalize_boxes(items,shape,allowed,max_objects=6):
    if not isinstance(items,(list,tuple)) or len(items)>96:
        raise InstanceError('Liste de boîtes invalide ou trop longue')
    if not isinstance(max_objects,int) or isinstance(max_objects,bool) or not 1<=max_objects<=MAX_OBJECTS:
        raise InstanceError('Budget objets invalide')
    candidates=[];warnings=[]
    for n,item in enumerate(items):
        if not isinstance(item,dict):
            warnings.append(f'BOITE_{n+1}_FORMAT_INVALIDE');continue
        label=canonical_label(item.get('label',''))
        if label not in allowed:
            warnings.append(f'BOITE_{n+1}_CATEGORIE_NON_AUTORISEE');continue
        try:coords=_box(item.get('bbox'),shape)
        except InstanceError as exc:
            warnings.append(f'BOITE_{n+1}_{str(exc)[:80]}');continue
        if any(label==p['label'] and _iou_box(coords,p['bbox'])>.82 for p in candidates):
            warnings.append(f'BOITE_{n+1}_DOUBLON');continue
        candidates.append({'label':label,'bbox':coords,'source_index':n+1})
        if len(candidates)>=max_objects:
            if n<len(items)-1:warnings.append('BUDGET_NOMBRE_OBJETS_ATTEINT')
            break
    return candidates,warnings


def manual_boxes(raw,shape,allowed,max_objects=6):
    if not isinstance(raw,str) or len(raw)>12000:raise InstanceError('Boîtes JSON trop volumineuses')
    try:data=json.loads(raw)
    except (TypeError,ValueError) as exc:raise InstanceError('JSON des boîtes invalide') from exc
    if not isinstance(data,list):raise InstanceError('JSON attendu : liste de boîtes')
    return normalize_boxes(data,shape,allowed,max_objects)


def expand_crop(box,shape,margin=CROP_MARGIN):
    h,w=shape;x0,y0,x1,y1=box
    mx=max(5,int(round((x1-x0)*margin)));my=max(5,int(round((y1-y0)*margin)))
    c=(max(0,x0-mx),max(0,y0-my),min(w,x1+mx),min(h,y1+my))
    if (c[2]-c[0])*(c[3]-c[1])>MAX_CROP_PIXELS:
        raise InstanceError('Région >4 Mp : réduire source avant IA')
    return c


def _mask_local(data,crop_shape):
    if hasattr(data,'detach'):data=data.detach().float().cpu().numpy()
    m=np.asarray(data)
    while m.ndim>2 and m.shape[0]==1:m=m[0]
    if m.shape!=crop_shape or m.ndim!=2 or m.dtype.kind not in 'biuf' or not np.isfinite(m).all():
        raise InstanceError('Masque SAM2 local invalide/dimensions incohérentes')
    if m.size==0 or m.min()<-.001 or m.max()>1.001:raise InstanceError('Masque SAM2 hors 0..1')
    return np.clip(m.astype(np.float32),0,1)


def _mask_iou(a,b):
    x=a>=.5;y=b>=.5
    overlap=int(np.count_nonzero(x&y));union=int(np.count_nonzero(x|y))
    return overlap/union if union else 0.


def _score_proposal(mask,box,crop,fullshape):
    x0,y0,x1,y1=box; cx0,cy0,_,_=crop
    bb=(mask>=.5)
    pixels=int(bb.sum())
    if pixels < max(30,mask.size*.0004):raise InstanceError('Masque absent ou trop petit')
    if pixels>mask.size*.90:raise InstanceError('Masque couvrant presque tout le recadrage')
    rx0=x0-cx0;ry0=y0-cy0;rx1=x1-cx0;ry1=y1-cy0
    in_bbox=int(np.count_nonzero(bb[ry0:ry1,rx0:rx1]))
    fraction=in_bbox/pixels
    if fraction<.55:raise InstanceError('Masque largement hors de la boîte guidée')
    # Ensure source bbox center region contains meaningful mask; no image comprehension claimed.
    xmid=(rx0+rx1)//2;ymid=(ry0+ry1)//2
    r=max(3,int(min(rx1-rx0,ry1-ry0)*.12))
    center=bb[max(0,ymid-r):min(bb.shape[0],ymid+r+1),max(0,xmid-r):min(bb.shape[1],xmid+r+1)]
    if center.size and center.mean()<.015:
        raise InstanceError('Masque absent du centre de la boîte : association douteuse')
    b=bb
    border=int(b[0,:].sum()+b[-1,:].sum()+b[:,0].sum()+b[:,-1].sum())
    components=cv2.connectedComponents(np.uint8(b),8)[0]-1
    flags=[]
    if border:flags.append('MASQUE_TOUCHE_BORD_RECADRAGE')
    if components>1:flags.append('MASQUE_FRAGMENTE')
    if fraction<.80:flags.append('MASQUE_PARTIELLEMENT_HORS_BOITE')
    if x0==0 or y0==0 or x1==fullshape[1] or y1==fullshape[0]:
        flags.append('BOITE_TOUCHE_BORD_IMAGE_SOURCE')
    return {'aire_px':pixels,'fraction_dans_boite':round(fraction,4),
            'composantes':components,'avertissements':flags}


def segment_instances(image, *, profile='Trois renards', source='Florence-2',
                      boxes_json='[]', max_objects=6, detector=None,masker=None):
    """Returns only *real* masks from masker; dependency-injection tests are not inference.

    detector(rgb,profile)-> list of {label,bbox}; masker(cropped_rgb,prompt)-> HxW mask.
    """
    rgb=validate_rgb(image);h,w=rgb.shape[:2]
    if profile not in PROFILE_PROMPTS:raise InstanceError('Profil inconnu')
    if source not in ('Florence-2','Boîtes manuelles'):raise InstanceError('Source des boîtes inconnue')
    allowed=PROFILE_PROMPTS[profile]
    if source=='Boîtes manuelles':
        boxes,warnings=manual_boxes(boxes_json,(h,w),allowed,max_objects)
        detection_source='BOITES_MANUELLES_NON_SEGMENTATION'
    else:
        detector_live = detector is None
        if detector is None:detector=detect_florence_boxes
        raw=detector(rgb,profile)
        boxes,warnings=normalize_boxes(raw,(h,w),allowed,max_objects)
        detection_source=('FLORENCE_2_EXECUTE' if detector_live else 'DETECTEUR_INJECTE_NON_PROUVE')
    if not boxes:raise InstanceError('Aucune boîte valable : aucun faux masque produit')
    # Refuse a mask batch that cannot fit before triggering costly inference.
    if len(boxes)*h*w>MAX_TOTAL_MASK_VALUES:
        raise InstanceError('Trop d’instances pour ce format; réduire max_objets ou image')
    if masker is None:masker=segment_sam2_crop
    outputs=[];info=[]
    for item in boxes:
        bb=item['bbox'];crop=expand_crop(bb,(h,w));x0,y0,x1,y1=crop
        local=rgb[y0:y1,x0:x1]
        entry={'label':item['label'],'bbox':list(bb),'recadrage':list(crop),
               'numero_detection':item['source_index'],'statut':'NON_DETOURE'}
        try:
            mask=_mask_local(masker(local,item['label']),(y1-y0,x1-x0))
            validation=_score_proposal(mask,bb,crop,(h,w))
            full=np.zeros((h,w),np.float32)
            full[y0:y1,x0:x1]=mask
            if any(_mask_iou(full,prior)>.83 for prior in outputs):
                entry.update({'statut':'REJETE_DOUBLON_MASQUE'});info.append(entry);continue
            # Mark overlapping output masks for downstream QA without arbitrarily erasing pixels.
            collisions=[i+1 for i,previous in enumerate(outputs) if np.any((previous>=.5)&(full>=.5))]
            if collisions:
                validation['avertissements'].append('CHEVAUCHEMENT_INSTANCES_A_VERIFIER')
                # Symmetric QA: the earlier accepted instance is affected too.
                for earlier in info:
                    if earlier.get('sortie_numero') in collisions:
                        earlier.setdefault('avertissements',[])
                        if 'CHEVAUCHEMENT_INSTANCES_A_VERIFIER' not in earlier['avertissements']:
                            earlier['avertissements'].append('CHEVAUCHEMENT_INSTANCES_A_VERIFIER')
            # Possible spill into an *exclusive* area of another detection box.
            # It is warning-only: geometric overlap is not semantic proof.
            # Calculate exclusively on the local crop, avoiding two extra
            # full-resolution boolean masks for every candidate (8GB PC target).
            ch,cw=mask.shape
            exclusive=np.zeros((ch,cw),np.uint8)
            for other in boxes:
                if other is item:continue
                ax0,ay0,ax1,ay1=other['bbox']
                sx0=max(ax0,x0);sy0=max(ay0,y0)
                sx1=min(ax1,x1);sy1=min(ay1,y1)
                if sx0<sx1 and sy0<sy1:
                    exclusive[sy0-y0:sy1-y0,sx0-x0:sx1-x0]=1
            bx0,by0,bx1,by1=bb
            exclusive[by0-y0:by1-y0,bx0-x0:bx1-x0]=0
            suspicious=int(np.count_nonzero((mask>=.5)&(exclusive!=0)))
            if suspicious:
                validation['pixels_zone_autre_boite_hors_boite_sujet']=suspicious
                if suspicious/max(1,int(np.count_nonzero(full>=.5))) >= .05:
                    validation['avertissements'].append('EMPIETEMENT_ZONE_AUTRE_SUJET_A_VERIFIER')
            outputs.append(full)
            entry.update({'statut':'MASQUE_PROPOSE_A_VERIFIER','sortie_numero':len(outputs),**validation})
        except Exception as exc:
            if _cuda_oom(exc):
                raise InstanceError('OOM_CUDA : traitement interrompu; aucun lot partiel publié') from exc
            entry.update({'statut':'ECHEC_SEGMENTATION','erreur':f'{type(exc).__name__}: {str(exc)[:140]}'})
        info.append(entry)
    if not outputs:raise InstanceError('SAM2 n’a produit aucun masque admissible (aucun export fictif)')
    if len(outputs)*h*w>MAX_TOTAL_MASK_VALUES:raise InstanceError('Lot de masques supérieur au budget mémoire')
    report={'version':'21.3.1-beta','source_boites':detection_source,
            'source_masques':'SAM2Segment' if masker is segment_sam2_crop else 'FOURNISSEUR_INJECTE_NON_PROUVE',
            'nombre_boites':len(boxes),'nombre_masques':len(outputs),
            'masques_avec_chevauchement':sum('CHEVAUCHEMENT_INSTANCES_A_VERIFIER' in e.get('avertissements',[]) for e in info),
            'masques_avec_suspicion_autre_sujet':sum('EMPIETEMENT_ZONE_AUTRE_SUJET_A_VERIFIER' in e.get('avertissements',[]) for e in info),
            'validation_semantique_humaine':False,'certification_decoupe_cricut':False,
            'avertissements_detection':warnings,'instances':info,
            'limite':'Une boîte n’est jamais un masque; les sujets superposés peuvent rester mélangés.'}
    return np.stack(outputs),report



def render_preview(rgb,masks,report,max_side=1100):
    """Visualization only: box and mask overlays, NEVER used as an exportable cut file."""
    from PIL import Image,ImageDraw,ImageFont
    source=validate_rgb(rgb)
    h,w=source.shape[:2]
    if not isinstance(masks,np.ndarray) or masks.ndim!=3 or masks.shape[1:]!=(h,w):
        raise InstanceError('Aperçu : masque non aligné')
    canvas=source.copy()
    palette=[(40,195,96),(242,149,43),(60,155,235),(211,69,160),(195,200,55),(109,82,222)]
    for n,mask in enumerate(masks):
        color=np.array(palette[n%len(palette)],np.float32)
        selected=mask>=.5
        canvas[selected]=np.uint8(.7*canvas[selected]+.3*color)
        contours,_=cv2.findContours(np.uint8(selected),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(canvas,contours,-1,tuple(map(int,color)),2)
    out=Image.fromarray(canvas,'RGB')
    painter=ImageDraw.Draw(out)
    for entry in report.get('instances',[]):
        x0,y0,x1,y1=entry['bbox'];accepted=entry['statut']=='MASQUE_PROPOSE_A_VERIFIER'
        c=(20,145,38) if accepted else (210,58,54)
        painter.rectangle((x0,y0,x1,y1),outline=c,width=2)
        painter.text((max(1,x0),max(1,y0-15)),f"{entry['numero_detection']} {entry['label']} {'OK' if accepted else 'A VERIFIER'}",fill=c,stroke_width=1,stroke_fill='white')
    ratio=min(1,max_side/max(w,h))
    if ratio<1:out=out.resize((round(w*ratio),round(h*ratio)),Image.Resampling.LANCZOS)
    return out

def detect_florence_boxes(rgb,profile):
    """Calls RMBG AILab_Florence2 phrase-grounding on downscaled image.

    Parsing deliberately keeps multiple detections of the same category.
    """
    import torch,nodes
    cls=nodes.NODE_CLASS_MAPPINGS.get('AILab_Florence2')
    if cls is None:raise InstanceError('Florence-2 RMBG absent')
    required=cls.INPUT_TYPES().get('required',{});optional=cls.INPUT_TYPES().get('optional',{})
    model='microsoft/Florence-2-base';task='Phrase Grounding (text boxes)'
    if cls.FUNCTION!='analyze' or tuple(cls.RETURN_TYPES)[:3]!=('IMAGE','MASK','JSON'):
        raise InstanceError('Interface Florence-2 incompatible')
    if model not in required.get('model_name',([],))[0] or task not in required.get('task',([],))[0] or 'text_prompt' not in optional:
        raise InstanceError('Modèle ou entrée text_prompt Florence-2 indisponible')
    h,w=rgb.shape[:2];ratio=min(1.,1024/max(h,w));dw=max(1,round(w*ratio));dh=max(1,round(h*ratio))
    small=cv2.resize(rgb,(dw,dh),interpolation=cv2.INTER_AREA) if ratio<1 else rgb
    image=torch.from_numpy(np.ascontiguousarray(small.astype(np.float32)/255))[None]
    opts={'image':image,'model_name':model,'task':task,
          'precision':'fp16' if torch.cuda.is_available() else 'fp32',
          'attention':'sdpa','fill_mask':False,
          'text_prompt':'. '.join(PROFILE_PROMPTS[profile])+'.'}
    if 'keep_model_loaded' in optional:opts['keep_model_loaded']=False
    inst=cls()
    try:raw=getattr(inst,cls.FUNCTION)(**opts)
    finally:
        del inst,image
        gc.collect()
        if torch.cuda.is_available():torch.cuda.empty_cache()
    if not isinstance(raw,(list,tuple)) or len(raw)<3 or not isinstance(raw[2],dict):
        raise InstanceError('Réponse JSON Florence-2 absente')
    predictions=raw[2];bboxes=predictions.get('bboxes',[]);labels=predictions.get('labels',[])
    if not isinstance(bboxes,(list,tuple)) or not isinstance(labels,(list,tuple)) or len(bboxes)!=len(labels):
        raise InstanceError('Boîtes/libellés Florence-2 invalides')
    results=[]
    for coords,label in zip(bboxes[:96],labels[:96]):
        if not isinstance(coords,(list,tuple)) or len(coords)!=4:continue
        words=re.sub(r'[^a-z ]',' ',str(label).lower()).split()
        words=[canonical_label(word) for word in words]
        allowed=[a for a in PROFILE_PROMPTS[profile] if a in words]
        if not allowed:continue
        try:
            a=np.asarray(coords,dtype=float)
            if not np.isfinite(a).all():continue
            # Florence detected on resized image; scale back to original pixel coords.
            source_coords=(a*np.array([w/dw,h/dh,w/dw,h/dh])).tolist()
            results.append({'label':allowed[0],'bbox':source_coords})
        except (ValueError,TypeError):continue
    return results


def segment_sam2_crop(rgb,prompt):
    """SAM2 per crop, using validated RMBG contract; mask from actual node output."""
    import torch,nodes
    from .auto_segment_v192 import _registry_class,MODEL,DINO,_mask_from_output
    cls=_registry_class(nodes.NODE_CLASS_MAPPINGS)
    tensor=torch.from_numpy(np.ascontiguousarray(rgb.astype(np.float32)/255))[None]
    obj=cls()
    try:
        result=getattr(obj,cls.FUNCTION)(image=tensor,prompt=prompt,sam2_model=MODEL,
            dino_model=DINO,device='Auto',threshold=.38,mask_blur=0,mask_offset=0,
            background='Alpha',background_color='#FFFFFF',invert_output=False)
        return _mask_from_output(result,rgb.shape[:2])
    finally:
        del obj,tensor
        gc.collect()
        if torch.cuda.is_available():torch.cuda.empty_cache()
