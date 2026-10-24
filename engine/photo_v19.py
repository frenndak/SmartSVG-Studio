"""SmartSVG V19: independent source-coordinate image/object extraction.

No vectorization of full-bleed scenes. Masked PNGs preserve original pixels.
Modes are explicit: connected AI masks, optional single foreground RMBG,
box-Guided GrabCut (experimental), or a source-only diagnostic.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
import uuid
import os
from datetime import datetime
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from .photo_geometry_v191 import cutout_with_white_border, InvalidCutout

MAX_PIXELS=14_000_000
MAX_OBJECTS=16
MAX_MASK_PIXELS_TOTAL=32_000_000  # keep peak CPU memory bounded on 6GB RAM

class PhotoExtractionError(ValueError):pass

def _slug(s):
    return (re.sub('[^a-zA-Z0-9_-]+','_',str(s)).strip('_')[:36] or 'OBJET').upper()

def _manifest(root):
    files={}
    for path in sorted(root.rglob('*')):
        if path.is_file() and path.name!='PRET_V19.json':
            sha=hashlib.sha256(path.read_bytes()).hexdigest()
            files[path.relative_to(root).as_posix()]={'octets':path.stat().st_size,'sha256':sha}
    return files

def _masks_arr(masks,hw):
    if masks is None:return None
    a=np.asarray(masks)
    if a.ndim==2:a=a[None]
    if a.ndim!=3 or a.shape[1:]!=hw or not 1<=a.shape[0]<=MAX_OBJECTS:
        raise PhotoExtractionError(f'Masques non alignes : attendu [N,{hw[0]},{hw[1]}], N=1..{MAX_OBJECTS}, recu {a.shape}')
    if a.size>MAX_MASK_PIXELS_TOTAL:
        raise PhotoExtractionError('Masques trop volumineux pour traitement securise : 32 millions de valeurs au maximum. Reduire ou fractionner la scene.')
    if not np.issubdtype(a.dtype,np.number) or not np.isfinite(a).all():
        raise PhotoExtractionError('Masques invalides, trop nombreux ou non finis')
    if float(a.min())<-.001 or float(a.max())>1.001:
        raise PhotoExtractionError('Masque en dehors de 0..1')
    return np.clip(a.astype(np.float32),0,1)

def _boxes_json(s,hw):
    if not str(s).strip():return []
    try:parsed=json.loads(s)
    except (ValueError,TypeError) as e:raise PhotoExtractionError(f'JSON boites invalide: {e}') from e
    if isinstance(parsed,dict):parsed=parsed.get('objects',parsed.get('boxes',[]))
    if not isinstance(parsed,list) or len(parsed)>MAX_OBJECTS:raise PhotoExtractionError('Liste de boites attendue, 16 objets maximum')
    h,w=hw;out=[]
    for j,it in enumerate(parsed):
        if not isinstance(it,dict):raise PhotoExtractionError('Boite JSON non objet')
        box=it.get('bbox')
        if not isinstance(box,list) or len(box)!=4:raise PhotoExtractionError('bbox attendue [x0,y0,x1,y1]')
        try:v=np.asarray(box,dtype=np.float64)
        except Exception as e:raise PhotoExtractionError('coordonnees boite non numeriques') from e
        if not np.isfinite(v).all():raise PhotoExtractionError('Boite NaN')
        x0,y0,x1,y1=map(float,v)
        if not (0<=x0<x1<=w and 0<=y0<y1<=h):raise PhotoExtractionError('Boite hors dimensions SOURCE')
        if (x1-x0)*(y1-y0)<100:raise PhotoExtractionError('Boite trop petite')
        label=str(it.get('label',f'objet_{j+1}'))[:100]
        score=it.get('score')
        if score is not None and (not isinstance(score,(float,int)) or not 0<=score<=1):
            raise PhotoExtractionError('Score doit etre 0..1')
        out.append({'label':label,'bbox':[int(x0),int(y0),int(x1),int(y1)],'score':score,
                    'origine_boite':str(it.get('source','coordonnees_fournies'))[:90]})
    return out

def _grabcut_box(rgb,bbox):
    """Bounded, box-guided *proposal*, never treated as model-based segmentation."""
    h,w=rgb.shape[:2]
    factor=min(1.,480/max(h,w))
    hh=max(2,int(round(h*factor)));ww=max(2,int(round(w*factor)))
    small=cv2.resize(rgb,(ww,hh),interpolation=cv2.INTER_AREA) if factor<1 else rgb.copy()
    x0,y0,x1,y1=bbox
    x0=max(1,int(x0*factor)); y0=max(1,int(y0*factor))
    x1=min(ww-1,int(x1*factor)); y1=min(hh-1,int(y1*factor))
    if x1-x0<8 or y1-y0<8:raise PhotoExtractionError('Boite reduite trop petite pour GrabCut')
    m=np.zeros((hh,ww),np.uint8)
    cv2.setNumThreads(2)
    try:
        cv2.grabCut(cv2.cvtColor(small,cv2.COLOR_RGB2BGR),m,(x0,y0,x1-x0,y1-y0),
                    np.zeros((1,65),np.float64),np.zeros((1,65),np.float64),2,cv2.GC_INIT_WITH_RECT)
    except cv2.error as e:
        raise PhotoExtractionError('GrabCut refuse boite: '+str(e)[:100]) from e
    fg=np.where((m==cv2.GC_FGD)|(m==cv2.GC_PR_FGD),1.,0.).astype(np.float32)
    if factor<1: fg=cv2.resize(fg,(w,h),interpolation=cv2.INTER_LINEAR)
    return fg

def _mask_to_rgba(rgb,mask):
    rgba=np.dstack((rgb,np.uint8(np.clip(mask*255,0,255)+.5)))
    rgba[rgba[...,3]==0,:3]=0
    return rgba

def _draw_preview(rgb,objects,filepath):
    im=Image.fromarray(rgb.copy(),'RGB').convert('RGBA')
    overlay=Image.new('RGBA',im.size,(0,0,0,0))
    ctx=ImageDraw.Draw(overlay)
    for idx,ob in enumerate(objects,1):
        x0,y0,x1,y1=ob['bbox_source_px']
        color= [(255,64,90,210),(0,200,180,210),(250,195,15,210),(80,160,255,210)][(idx-1)%4]
        ctx.rectangle([x0,y0,x1,y1],outline=tuple(color),width=5)
        ctx.rectangle([x0,y0-29 if y0>30 else y0,x0+min(350,21*len(ob['label'])+55),y0 if y0>30 else y0+30], fill=color)
        ctx.text((x0+4,y0-26 if y0>30 else y0+3),f'{idx:02d} {ob["label"][:23]}',fill=(10,18,30,255))
    Image.alpha_composite(im,overlay).convert('RGB').save(filepath,compress_level=2)

def process_photo(rgb,output_dir,*,masks=None,labels='',boxes_json='',mode='auto',
                  foreground_provider=None,alpha=None,white_offset_mm=1.5,
                  width_mm=180,mask_origin='masques_externes',require_provider=False,segmentation_metadata=None):
    rgb=np.asarray(rgb)
    if rgb.dtype!=np.uint8 or rgb.ndim!=3 or rgb.shape[2]!=3:
        raise PhotoExtractionError('Photo : image RGB uint8 attendue')
    h,w=rgb.shape[:2]
    if not (0<h*w<=MAX_PIXELS):raise PhotoExtractionError('Photo au-dela du budget 14 MP')
    if not (20<=width_mm<=400) or not (0<=white_offset_mm<=5):raise PhotoExtractionError('Dimensions physiques invalides')
    if mode not in ('auto','masques_requis','boites_guidees','analyse_seule'):
        raise PhotoExtractionError('Mode photo inconnu')
    parsed=_boxes_json(boxes_json,(h,w))
    if alpha is not None:
        alpha=np.asarray(alpha)
        if alpha.shape!=(h,w) or not np.isfinite(alpha).all():raise PhotoExtractionError('Alpha source incorrect')
    base=Path(output_dir).expanduser();base.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.SmartSVG_V19_TEMP_',dir=base))
    try:
        source=stage/'01_ORIGINAL.png'
        if alpha is not None:
            a=np.uint8(np.clip(alpha,0,255))
            Image.fromarray(np.dstack((rgb,a)),'RGBA').save(source,compress_level=2)
        else:
            Image.fromarray(rgb,'RGB').save(source,compress_level=2)
        mm_per_px=width_mm/w
        external=_masks_arr(masks,(h,w))
        computed=[]; origins=[]
        label_tokens=[x.strip() for x in re.split(r'[;\n,]+',str(labels)) if x.strip()]
        if external is not None and mode!='analyse_seule':
            computed=list(external)
            origins=[mask_origin]*len(computed)
        elif mode=='boites_guidees' and parsed:
            if h*w>300000:
                raise PhotoExtractionError('GrabCut guide interdit sur grande scene : budget CPU depasse. Relier les masques SAM/Florence2.')
            for box in parsed:
                computed.append(_grabcut_box(rgb,box['bbox']))
                origins.append('GRABCUT_BOITE_GUIDEE_NON_IA')
        elif mode=='auto' and foreground_provider is not None:
            try:
                m=foreground_provider(rgb)
                if isinstance(m,tuple):m=m[0]
                computed=list(_masks_arr(m,(h,w)))
                origins=['RMBG_DETOURAGE_GLOBAL_NON_SEMANTIQUE']*len(computed)
            except Exception as e:
                if require_provider:
                    raise PhotoExtractionError('IA locale forcee : '+str(e)[:180]) from e
                # No silent switch to a fake segmentation; label failure.
                origin_error=f'RMBG non utilisable: {type(e).__name__}: {str(e)[:160]}'
                computed=[]
        if require_provider and not computed:
            raise PhotoExtractionError('IA locale forcee mais aucun masque valide')
        if mode=='masques_requis' and not computed:
            raise PhotoExtractionError('Aucun masque IA valide: sortie objets interdite')
        # Preserve the transparency of a PNG already provided by the user.
        if alpha is not None and computed:
            computed=[np.asarray(m,dtype=np.float32)*(np.asarray(alpha,dtype=np.float32)/255.) for m in computed]
        prepared=[]
        min_area=max(80,int(h*w*.0003))
        for idx,mask in enumerate(computed):
            binary=mask>=.5
            area=int(binary.sum())
            if area<min_area or area>int(h*w*.995):continue
            ys,xs=np.where(binary)
            left,top,right,bottom=int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)
            box=parsed[idx] if len(parsed)==len(computed) else None
            label=label_tokens[idx] if idx<len(label_tokens) else (box['label'] if box else ('SUJET_PRINCIPAL' if len(computed)==1 else f'OBJET_{idx+1:02d}'))
            prepared.append({'label':label,'mask':mask,'bbox_source_px':[left,top,right,bottom],
                             'source':origins[idx], 'pixels_visibles':area,
                             'score_detection_fournie':box['score'] if box else None})
        if mode=='masques_requis' and len(prepared)==0:
            raise PhotoExtractionError('Masques fournis mais aucun objet valide')
        # Do not apply overlap erasure: the entire mask geometry of each
        # detected item remains inspectable. Flag ambiguous overlap explicitly.
        overlap=0
        if prepared:
            cover=np.zeros((h,w),np.uint8)
            for p in prepared:cover+=(p['mask']>=.5).astype(np.uint8)
            overlap=int((cover>1).sum())
        output_objects=[]
        if prepared:
            folder=stage/'02_OBJETS_PNG'
            folder.mkdir()
            masksdir=stage/'03_MASQUES'
            masksdir.mkdir()
            for idx,item in enumerate(prepared,1):
                label=item['label']; mask=item['mask'];l,t,r,b=item['bbox_source_px']
                base_name=f'{idx:02d}_{_slug(label)}'
                # Local crops with padding outside the source canvas avoid losing
                # hair, fingers and the sticker white border at image boundaries.
                try:
                    raw,printable,bounds,geometry=cutout_with_white_border(
                        rgb,mask,mm_per_px=mm_per_px,white_offset_mm=white_offset_mm)
                except InvalidCutout as exc:
                    raise PhotoExtractionError(str(exc)) from exc
                l,t,r,b=bounds
                resolution=25.4/mm_per_px
                Image.fromarray(raw,'RGBA').save(
                    folder/f'{base_name}_DETOURE.png',dpi=(resolution,resolution),compress_level=2)
                Image.fromarray(np.uint8(np.clip(mask*255,0,255)+.5),'L').save(
                    masksdir/f'{base_name}_MASQUE.png',compress_level=2)
                Image.fromarray(printable,'RGBA').save(
                    folder/f'{base_name}_CRICUT_TEST.png',dpi=(resolution,resolution),compress_level=2)
                binary=(mask>=.5).astype(np.uint8)
                ncomp,_,area_stats,_=cv2.connectedComponentsWithStats(binary,8)
                visible_components=int(sum(int(area_stats[k,cv2.CC_STAT_AREA])>=max(5,int(item['pixels_visibles']*.001)) for k in range(1,ncomp)))
                output_objects.append({'id':idx,'label':label,'mask_source':item['source'],
                    'confiance_detector_fournie':item['score_detection_fournie'],
                    'confiance_decoupe':None,
                    'bbox_source_px':list(bounds),
                    'taille_detourage_mm':[round((r-l)*mm_per_px,2),round((b-t)*mm_per_px,2)],
                    'pixels_visibles':item['pixels_visibles'],
                    'composantes_separees_pour_decoupe':visible_components,
                    'geometrie_cricut':geometry,
                    'fichier_rgba':f'02_OBJETS_PNG/{base_name}_DETOURE.png',
                    'fichier_cricut_test':f'02_OBJETS_PNG/{base_name}_CRICUT_TEST.png',
                    'fichier_masque':f'03_MASQUES/{base_name}_MASQUE.png'})
        _draw_preview(rgb,output_objects or [{'label':'BOITE GUIDE : '+o['label'], 'bbox_source_px':o['bbox']} for o in parsed],stage/'00_APERCU_ANALYSE.png')
        warnings=[]
        if overlap>w*h*.002:warnings.append(f'Masques chevauchants : {overlap} pixels; les extractions se recouvrent')
        for obj in output_objects:
            if obj['composantes_separees_pour_decoupe']>1:
                warnings.append(f'Objet {obj["id"]}: {obj["composantes_separees_pour_decoupe"]} ilots distincts; verifier les contours Cricut')
        if not output_objects:warnings.append('AUCUN OBJET DETOURE. Brancher un MASK SAM/Florence2/RMBG, ou fournir des boites guidees.')
        if parsed and mode!='boites_guidees' and not computed:
            warnings.append('Boites annotees (apercu uniquement), aucune segmentation deduite.')
        if mode=='analyse_seule' and masks is not None:warnings.append('Mode analyse_seule: les masques fournis sont volontairement ignores.')
        if 'origin_error' in locals():warnings.append(origin_error)
        status=('A_VERIFIER_MASQUES_INSUFFISANTS' if not output_objects else
                'EXTRACTIONS_A_VALIDER_VISUELLEMENT')
        record={'version':'19.2-beta','branche':'PHOTO_ET_ILLUSTRATION',
                'statut':status,'dimensions_source':[w,h],
                'nombre_objets_extraits':len(output_objects),
                'securite_memoire_max_masques_pixels':MAX_MASK_PIXELS_TOTAL,
                'masques_reels_externes':external is not None and not (segmentation_metadata or {}).get('statut')=='OK',
                'masques_externes_fournis_non_verifies_comme_ia':external is not None and not (segmentation_metadata or {}).get('statut')=='OK',
                'masques_automatiques_sam2':external is not None and (segmentation_metadata or {}).get('statut')=='OK',
                'mode':mode,'reconnaissance_automatique_objets':'NON_VERIFIEE',
                'segmentation_auto_locale':('SAM2/GroundingDINO sur prompts, si rapport indique OK; sinon RMBG fond global ou aucun masque'),
                'fond_original_non_modifie':True,'chevauchement_pixels':overlap,
                'avertissements':warnings,'objets':output_objects,
                'validation_cricut_physique':False,'reconstruction_parties_cachees':False,
                'marge_blanc_imprimable':True,'diagnostic_methode':'Masque fourni ou detourage RMBG; origine modele non certifiee',
                'boites_annotations_fournies':parsed,
                'segmentation_automatique_v192':segmentation_metadata}
        (stage/'rapport_analyse.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
        (stage/'LIRE_EN_PREMIER.txt').write_text(
            'V19 PHOTO : 01_ORIGINAL.png conserve tous les pixels originaux.\n'
            'Les fichiers 02_OBJETS_PNG sont des extractions potentielles et necessitent un examen visuel.\n'
            'La reconnaissance semantique n est pas fournie sans modeles de segmentation connectes.\n'
            'Pour Cricut: importer l image RGBA / CRICUT_TEST.png dans Imprimer puis decouper, verifier dimensions et contours.\n'
            'Ne pas imprimer directement une photo opaque comme un sticker detoure.\n',encoding='utf8')
        (stage/'PRET_V19.json').write_text(json.dumps({'version':'19.2-beta','statut':status,'validation_cricut_physique':False,'fichiers':_manifest(stage)},ensure_ascii=False,indent=2),encoding='utf8')
        final=base/('SmartSVG_V19_PHOTO_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6])
        os.replace(stage,final)
        return {'output':str(final),'audit_v19':record},Image.open(final/'00_APERCU_ANALYSE.png').convert('RGB')
    except Exception as e:
        (base/('SmartSVG_ECHEC_V19_'+uuid.uuid4().hex[:7]+'.json')).write_text(
            json.dumps({'status':'AUCUN_EXPORT_PUBLIE','erreur':str(e)},ensure_ascii=False,indent=2),encoding='utf8')
        raise PhotoExtractionError('V19 extraction refusee : '+str(e)) from e
    finally:
        shutil.rmtree(stage,ignore_errors=True)
