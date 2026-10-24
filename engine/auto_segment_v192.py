"""SAM2/GroundingDINO provider bridge for installed ComfyUI-RMBG.

Uses the upstream-verified SAM2Segment INPUT_TYPES/FUNCTION/RETURN_TYPES contract.
Does not claim Florence-2 inference, nor turn bounding boxes into masks.
Works with external registered nodes, not a copied model implementation.
"""
from __future__ import annotations
import gc
import re
import numpy as np
import cv2
import torch

MODEL='sam2.1_hiera_tiny'
DINO='GroundingDINO_SwinT_OGC (694MB)'
PRESETS={
    'auto':['person','gift box','beer mug'],
    'personne':['person'],
    'cadeaux':['gift box','present'],
    'chopes':['person','beer mug'],
    'personne_cadeaux':['person','gift box','present'],
    'animaux':['cat','dog','bird'],
}

class SegmentationUnavailable(RuntimeError): pass

def get_prompts(profile='auto',custom=''):
    if custom and str(custom).strip():
        entries=[s.strip() for s in re.split(r'[;\n,]+',str(custom)) if s.strip()]
    else:
        entries=PRESETS.get(profile)
        if entries is None:raise ValueError('Profil de segmentation inconnu')
    if not entries or len(entries)>4 or any(len(s)>90 for s in entries):
        raise ValueError('De 1 a 4 prompts (<=90 caracteres chacun) sont autorises')
    return entries

def _registry_class(registry):
    cls=registry.get('SAM2Segment')
    if cls is None:raise SegmentationUnavailable('RMBG: le noeud SAM2Segment est absent. Verifier son installation.')
    try:
        spec=cls.INPUT_TYPES()
        required=spec.get('required',{})
        if not set(('image','prompt','sam2_model','dino_model','device')).issubset(required):
            raise ValueError('required inputs differ')
        sam_choices=required['sam2_model'][0]
        dino_choices=required['dino_model'][0]
        if MODEL not in sam_choices or DINO not in dino_choices:
            raise ValueError('Models not advertised by node')
        if tuple(getattr(cls,'RETURN_TYPES',()))[:2]!=('IMAGE','MASK'):
            raise ValueError('expected IMAGE,MASK output')
        if getattr(cls,'FUNCTION',None)!='segment_v2':
            raise ValueError('expected segment_v2')
    except Exception as e:
        raise SegmentationUnavailable('API SAM2Segment RMBG incompatible : '+str(e)[:130]) from e
    return cls

def _mask_from_output(out,shape):
    if not isinstance(out,(tuple,list)) or len(out)<2:raise SegmentationUnavailable('SAM2: sortie MASK introuvable')
    mask=out[1]
    if hasattr(mask,'detach'):mask=mask.detach().float().cpu().numpy()
    mask=np.asarray(mask)
    while mask.ndim>2 and mask.shape[0]==1:mask=mask[0]
    if mask.ndim!=2 or mask.shape!=shape:raise SegmentationUnavailable(f'SAM2: masque aux dimensions incorrectes : {mask.shape}')
    if not np.issubdtype(mask.dtype,np.number) or not np.isfinite(mask).all():
        raise SegmentationUnavailable('SAM2: masque non numerique ou non fini')
    if float(mask.min())<-.001 or float(mask.max())>1.001:
        raise SegmentationUnavailable('SAM2: masque hors [0,1]')
    return np.clip(mask.astype(np.float32),0,1)

def _instances(mask, label):
    """Split disjoint accessory components; do not split person's hands/body."""
    if label.lower().strip() in ('person','human','woman','man','cat','dog','bird'):
        return [mask]
    binary=(mask>=.5).astype(np.uint8)
    n,components,stats,_=cv2.connectedComponentsWithStats(binary,8)
    main_area=max(50,int(binary.size*.00035))
    parts=[(int(stats[i,4]),i) for i in range(1,n) if int(stats[i,4])>=main_area]
    parts.sort(reverse=True)
    if len(parts)<2:return [mask]
    return [np.where(components==i,mask,0).astype(np.float32) for _,i in parts[:6]]

def segment_scene(rgb, *, registry=None, profile='auto', custom_prompts='', threshold=.38, max_results=12):
    """Local inference. Fail safe on missing dependency; caller controls fallback.

    Only simple prompt-to-mask segmentation; NO unprompted object understanding.
    Model downloads are handled by ComfyUI-RMBG at first use.
    """
    if registry is None:
        import nodes
        registry=nodes.NODE_CLASS_MAPPINGS
    cls=_registry_class(registry)
    prompts=get_prompts(profile,custom_prompts)
    rgb=np.asarray(rgb)
    if rgb.ndim!=3 or rgb.shape[2]!=3 or rgb.dtype!=np.uint8:
        raise ValueError('Source RGB uint8 attendue')
    h,w=rgb.shape[:2]
    if h*w>5_000_000:raise SegmentationUnavailable('Scene >5MP : reduire la resolution pour inference IA')
    if not .05<=threshold<=.95:raise ValueError('Seuil de detection hors [0.05,0.95]')
    backend=cls()
    image=torch.from_numpy(np.ascontiguousarray(rgb).astype(np.float32)/255.).unsqueeze(0)
    masks=[];labels=[];details=[]
    try:
        fn=getattr(backend,cls.FUNCTION)
        for prompt in prompts:
            try:
                out=fn(image=image,prompt=prompt,sam2_model=MODEL,dino_model=DINO,device='Auto',
                       threshold=float(threshold),mask_blur=0,mask_offset=0,background='Alpha',
                       background_color='#FFFFFF',invert_output=False)
                m=_mask_from_output(out,(h,w))
                parts=_instances(m,prompt)
                accepted=0
                for j,part in enumerate(parts,1):
                    area=int(np.count_nonzero(part>=.5))
                    if area <max(85,int(h*w*.00035)) or area>int(h*w*.96):continue
                    # Remove almost identical masks from different text prompts.
                    duplicate=False
                    for previous in masks:
                        a=part>=.5;b=previous>=.5
                        denom=int(np.count_nonzero(a|b))
                        if denom and np.count_nonzero(a&b)/denom>.85:
                            duplicate=True;break
                    if duplicate:continue
                    masks.append(part);labels.append(prompt if len(parts)==1 else f'{prompt}_{j}')
                    accepted+=1
                    if len(masks)>=max_results:break
                details.append({'prompt':prompt,'masques_valides':accepted,'statut':'OK'})
            except Exception as exc:
                details.append({'prompt':prompt,'masques_valides':0,'statut':'ECHEC','erreur':str(exc)[:220]})
            if len(masks)>=max_results:break
    finally:
        del backend
        gc.collect()
        if torch.cuda.is_available():torch.cuda.empty_cache()
    return {'masks':np.stack(masks) if masks else None,'labels':labels,
            'audit':{'provider':'RMBG/SAM2Segment + GroundingDINO (text prompts)',
                     'modele_sam2':MODEL,'modele_detection':DINO,
                     'prompts':prompts,'tentatives':details,
                     'masques_acceptes':len(masks),'verification_GPU_reelle_dans_cet_environnement':False,
                     'limites':'Prompts generiques; les objets non mentionnes peuvent etre ignores; un meme masque peut regrouper plusieurs objets'}}
