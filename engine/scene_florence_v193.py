"""Conservative category grounding with RMBG's AILab_Florence2 node.

Florence-2 RMBG 3.x exposes grounding/region-proposals, not a general
captioning endpoint. Do not imply free-form image comprehension: here Florence
is given candidate concepts, returns labels & boxes, and SAM2 generates masks.
No box is ever exported as a mask or as a Cricut sticker.
"""
from __future__ import annotations
import gc
import re
import cv2
import numpy as np
import torch

class FlorenceUnavailable(RuntimeError):pass

MODEL='microsoft/Florence-2-base'
TASK='Phrase Grounding (text boxes)'
# Only known object classes; explicitly exclude scene/background and text by default.
KNOWN={
 'person':('person','people','human','woman','man','girl','boy','child','elf','leprechaun','server','waiter'),
 'gift box':('gift box','present','wrapped gift','gift','present box','package'),
 'beer mug':('beer mug','beer stein','beer glass','mug','beer tankard','steins'),
 'cat':('cat','kitten'), 'dog':('dog','puppy'), 'bird':('bird'),
 'flower':('flower','flowers'), 'toy':('toy','teddy bear','doll'),
 'hat':('hat','top hat'),
}
CHOICES={
 'auto':('person','gift box','beer mug','cat','dog','bird','flower','toy','hat'),
 'personne':('person','hat'),
 'cadeaux':('gift box','person','toy'),
 'chopes':('person','beer mug','hat'),
 'personne_cadeaux':('person','gift box','toy'),
 'animaux':('cat','dog','bird','person'),
}
ORDER={'person':0,'gift box':1,'beer mug':2,'cat':3,'dog':4,'bird':5,'flower':6,'toy':7,'hat':8}

def _normalized_label(label):
    """No arbitrary caption becomes a SAM2 prompt; only whitelist concepts."""
    s=re.sub(r'\s+',' ',re.sub(r'[^a-z0-9 ]',' ',str(label).lower())).strip()
    for key,aliases in KNOWN.items():
        if any(re.search(r'\b'+re.escape(v)+r'\b',s) for v in aliases):return key
    return None

def _parse_predictions(data,shape,scale=(1.,1.),wanted=None):
    if isinstance(data,(tuple,list)) and len(data)==1:data=data[0]
    if not isinstance(data,dict):raise FlorenceUnavailable('Florence2: DATA/JSON invalide, dict attendu')
    bbox=data.get('bboxes');labels=data.get('labels')
    if not isinstance(bbox,(tuple,list)) or not isinstance(labels,(tuple,list)) or len(bbox)!=len(labels):
        raise FlorenceUnavailable('Florence2: bboxes/labels absents ou de longueurs differentes')
    h,w=shape; sx,sy=scale
    results=[]
    for i,(coords,label) in enumerate(zip(bbox,labels)):
        if i>=96:break
        if not isinstance(coords,(tuple,list)) or len(coords)!=4:continue
        try:a=np.asarray(coords,dtype=float)
        except (ValueError,TypeError):continue
        if not np.isfinite(a).all():continue
        x0,y0,x1,y1=(a*np.array([sx,sy,sx,sy])).tolist()
        x0,x1=sorted((x0,x1));y0,y1=sorted((y0,y1))
        x0=max(0.,min(float(w),x0));x1=max(0.,min(float(w),x1));y0=max(0.,min(float(h),y0));y1=max(0.,min(float(h),y1))
        area=(x1-x0)*(y1-y0)
        if area<max(64.,w*h*.0002) or area>w*h*.97:continue
        kind=_normalized_label(label)
        if kind is None or wanted is not None and kind not in wanted:continue
        results.append({'label':kind,'source_label':str(label)[:100],
                        'bbox':[round(x0,1),round(y0,1),round(x1,1),round(y1,1)],
                        'bbox_fraction':round(area/(w*h),5)})
    # Duplicated boxes are not independent detections. Remove high overlap.
    cleaned=[]
    for item in sorted(results,key=lambda x:(ORDER.get(x['label'],99),-x['bbox_fraction'])):
        a=np.array(item['bbox']); duplicate=False
        for old in cleaned:
            if old['label']!=item['label']:continue
            b=np.array(old['bbox'])
            v=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
            denom=(a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-v
            if denom>0 and v/denom>.75:duplicate=True;break
        if not duplicate:cleaned.append(item)
    return cleaned

def inspect_scene(rgb,*,registry=None,profile='auto',max_dimension=1024):
    if profile not in CHOICES:raise ValueError('Profil Florence inconnu')
    if registry is None:
        import nodes
        registry=nodes.NODE_CLASS_MAPPINGS
    cls=registry.get('AILab_Florence2')
    if cls is None:raise FlorenceUnavailable('RMBG: AILab_Florence2 absent. Verifier ComfyUI-RMBG.')
    try:
        req=cls.INPUT_TYPES()['required'];opt=cls.INPUT_TYPES().get('optional',{})
        expected=('image','model_name','task','precision','attention','fill_mask')
        if not all(k in req for k in expected):raise ValueError('required inputs changed')
        if TASK not in req['task'][0] or MODEL not in req['model_name'][0]:raise ValueError('model/task missing')
        if getattr(cls,'FUNCTION',None)!='analyze' or tuple(cls.RETURN_TYPES)[:3]!=('IMAGE','MASK','JSON'):
            raise ValueError('FUNCTION/RETURN_TYPES changed')
    except Exception as exc:raise FlorenceUnavailable('RMBG Florence2 API incompatible : '+str(exc)) from exc
    im=np.asarray(rgb)
    if im.ndim!=3 or im.shape[2]!=3 or im.dtype!=np.uint8:raise ValueError('RGB uint8 HWC requis')
    h,w=im.shape[:2]
    if h*w>5_000_000:raise FlorenceUnavailable('Image >5 MP, redimensionnement demande avant IA')
    ratio=min(1.,max_dimension/max(h,w))
    dw=max(1,int(round(w*ratio)));dh=max(1,int(round(h*ratio)))
    small=cv2.resize(im,(dw,dh),interpolation=cv2.INTER_AREA) if ratio<1 else im
    tensor=torch.from_numpy(np.ascontiguousarray(small.astype(np.float32)/255.)).unsqueeze(0)
    # Text prompt is broad/grounded, not free-language generation. Limit to
    # profile categories. Default keeps a small vocabulary to reduce false positives.
    requested=CHOICES[profile]
    vocabulary='. '.join(requested)+'.'
    dtype='fp16' if torch.cuda.is_available() else 'fp32'
    kw={'image':tensor,'model_name':MODEL,'task':TASK,'precision':dtype,
        'attention':'sdpa','fill_mask':False}
    if 'text_prompt' in opt:kw['text_prompt']=vocabulary
    else:raise FlorenceUnavailable('Florence2 text_prompt input missing')
    if 'keep_model_loaded' in opt:kw['keep_model_loaded']=False
    instance=cls()
    try:
        output=getattr(instance,cls.FUNCTION)(**kw)
        if not isinstance(output,(tuple,list)) or len(output)<3:raise FlorenceUnavailable('Florence2 sortie JSON manquante')
        detections=_parse_predictions(output[2],(h,w),(w/dw,h/dh),set(requested))
    finally:
        del instance,tensor
        gc.collect()
        if torch.cuda.is_available():torch.cuda.empty_cache()
    selected=list(dict.fromkeys(i['label'] for i in detections))[:4]
    return {'prompts':selected,'detections':detections,
            'audit':{'statut':'DETECTIONS_CONSERVATRICES' if selected else 'AUCUNE_CATEGORIE_FIABLE',
                     'provider':'ComfyUI-RMBG/AILab_Florence2 (phrase grounding)',
                     'model':MODEL,'task':TASK,'profil':profile,'categories_candidats':list(requested),
                     'dimension_inference':[dw,dh],'dimension_originale':[w,h],
                     'nombre_boites_filtrees':len(detections),'prompts_proposes':selected,
                     'confiance':'non fournie par cette API; aucune probabilite inventee',
                     'limite':'Classement par lexique de categories, pas reconnaissance ouverte/caption libre; boites != masques'}}
