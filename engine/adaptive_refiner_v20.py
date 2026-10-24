"""V20.0: conservative isolated ROI matting and anti-cross-object safeguards.

Source mask remains unchanged in 'diagnostic' and 'proposition' modes.
A candidate is *not* proof of more accurate matting; supervised promotion
needs an explicit ground-truth annotation aligned to the original image.
"""
from __future__ import annotations
import gc
import math
import time
import cv2
import numpy as np
import torch

MAX_IMAGE_PIXELS=5_000_000
MAX_BATCH_PIXELS=25_000_000
MAX_OBJECTS=16
MAX_REFINEMENTS=4

class RefinementError(ValueError): pass


def validate_masks(rgb, masks):
    src=np.asarray(rgb)
    if src.ndim!=3 or src.shape[2]!=3 or src.dtype!=np.uint8 or src.shape[0]==0 or src.shape[1]==0 or src.shape[0]*src.shape[1]>MAX_IMAGE_PIXELS:
        raise RefinementError('Image RGB uint8 invalide ou >5 MP')
    if masks is None:return None
    m=np.asarray(masks)
    if m.ndim==2:m=m[None]
    if m.ndim!=3 or not 1<=len(m)<=MAX_OBJECTS or m.shape[1:]!=src.shape[:2] or m.size>MAX_BATCH_PIXELS:
        raise RefinementError('Masques: dimensions, quantite ou budget non valides')
    if not np.issubdtype(m.dtype,np.number) or not np.isfinite(m).all():raise RefinementError('Masques NaN ou non numeriques')
    lo=float(m.min());hi=float(m.max())
    # External mask conventions: 0..1 floating, 0/1 integer, 0/255 uint8.
    if lo < 0 or hi>1:
        if np.issubdtype(m.dtype,np.integer) and lo>=0 and hi<=255:
            m=m.astype(np.float32)/255.
        else:raise RefinementError('Valeurs de masque hors 0..1')
    return np.ascontiguousarray(m,dtype=np.float32)


def _bbox(binary, margin, width, height):
    ys,xs=np.nonzero(binary)
    if not len(xs):return None
    x0,x1=int(xs.min()),int(xs.max())+1;y0,y1=int(ys.min()),int(ys.max())+1
    pad=max(20,int(math.ceil(max(x1-x0,y1-y0)*margin)))
    return max(0,x0-pad),max(0,y0-pad),min(width,x1+pad),min(height,y1+pad)


def _risk(mask, overlap):
    fg=(mask>=.5).astype(np.uint8)
    if fg.sum()==0:return 0.,{'vide':True}
    edge=cv2.morphologyEx(fg,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))>0
    area=int(fg.sum());perim=int(edge.sum())
    ncomp, _, _, _=cv2.connectedComponentsWithStats(fg,8)
    count=max(0,ncomp-1)
    thin=(mask>.01)&(mask<.99)
    score=min(1.,(perim/max(area,1))*2.8)+min(1.,float(np.count_nonzero(thin))/max(area,1))*0.65+min(1.,float(np.count_nonzero(overlap& (fg>0)))/max(area,1))*0.7
    return float(score),{'surface_px':area,'contour_px':perim,'composantes':count,'pixels_transparents':int(np.count_nonzero(thin)),
                         'pixels_superposes':int(np.count_nonzero(overlap & (fg>0)))}


def _get_refiner(registry, model):
    cls=registry.get('BiRefNetRMBG')
    if cls is None:raise RefinementError('RMBG: BiRefNetRMBG absent')
    try:
        spec=cls.INPUT_TYPES()
        req=spec['required']; opt=spec.get('optional',{})
        if 'image' not in req or 'model' not in req or model not in req['model'][0]:
            raise ValueError(f'modele {model} non propose dans RMBG')
        if getattr(cls,'FUNCTION',None)!='process_image' or tuple(getattr(cls,'RETURN_TYPES',()))[:2]!=('IMAGE','MASK'):
            raise ValueError('FUNCTION ou RETURN_TYPES ont change')
    except Exception as exc:raise RefinementError('Interface BiRefNetRMBG incompatible: '+str(exc)[:160]) from exc
    return cls,opt


def _crop_mask(result,original_hw):
    if not isinstance(result,(tuple,list)) or len(result)<2:raise RefinementError('Sortie du modele incomplet')
    a=result[1]
    if hasattr(a,'detach'):a=a.detach().float().cpu().numpy()
    a=np.asarray(a)
    if a.ndim==4 and a.shape[1]==1:a=a[:,0,:,:]
    while a.ndim>2 and a.shape[0]==1:a=a[0]
    if a.ndim!=2 or a.shape!=original_hw or not np.issubdtype(a.dtype,np.number) or not np.isfinite(a).all():
        raise RefinementError('Masque matting invalide ou mal dimensionne')
    if a.min() < -1.e-4 or a.max()>1.0001:raise RefinementError('Matting hors 0..1')
    return np.clip(a,0,1).astype(np.float32)


def _compare_to_truth(base, candidate, annotation):
    a=base>=.5;b=candidate>=.5;gt=annotation>=.5
    ia=int(np.count_nonzero(a & gt));ua=int(np.count_nonzero(a | gt))
    ib=int(np.count_nonzero(b & gt));ub=int(np.count_nonzero(b | gt))
    return (ia/ua if ua else 1.),(ib/ub if ub else 1.)


def adaptive_refine(rgb, masks, *, registry=None, model='Lucida', max_passes=2,
                    mode='diagnostic', annotation=None, margin=.20,
                    model_runner=None, min_agreement=.67):
    """Return selected, optional candidates, uncertain map, provenance report.

    A model_runner(crop_rgb_uint8)->crop_mask_float is a testing adapter; in
    production the actual RMBG node is invoked via registry, one object at a time.
    """
    if mode not in ('diagnostic','proposition','adopter_annotation'):
        raise RefinementError('Mode de raffinement inconnu')
    if not 0<=int(max_passes)<=MAX_REFINEMENTS:raise RefinementError('Nombre maximal de passages invalide')
    if not .05<=float(margin)<=.5:raise RefinementError('Marge ROI hors plage')
    if not .3<=float(min_agreement)<=.95:raise RefinementError('Seuil recouvrement hors plage')
    base=validate_masks(rgb,masks)
    if base is None:raise RefinementError('Masque SAM2 ou externe obligatoire')
    truth=validate_masks(rgb,annotation) if annotation is not None else None
    if truth is not None and truth.shape!=base.shape:raise RefinementError('Annotation non alignee')
    if mode=='adopter_annotation' and truth is None:
        raise RefinementError('Annotation requise pour adopter un masque')
    h,w=rgb.shape[:2]
    selected=base.copy();candidates=base.copy(); uncertain=np.zeros((h,w),np.uint8)
    shared=np.zeros((h,w),np.uint8)
    for mask in base:shared=np.minimum(2, shared+(mask>=.5).astype(np.uint8))
    overlap=shared>1
    uncertain[overlap]=255
    planned=[]
    for i,m in enumerate(base):
        risk,stats=_risk(m,overlap)
        if stats.get('vide'):continue
        bbox=_bbox(m>=.5,float(margin),w,h)
        if bbox is None:continue
        planned.append((risk,i,bbox,stats))
    planned.sort(key=lambda x:(-x[0],x[1]))
    chosen=planned[:int(max_passes)]
    report={'version':'20.0-beta','mode':mode,'modele_demande':model,'max_passes':int(max_passes),
            'objets_retenus_pour_second_passage':[x[1]+1 for x in chosen],
            'candidats':[],'appels_modele_tentes':len(chosen),'appels_modele_reussis':0,'incertitude_pixels':0,
            'source_masques_originale_modifiee':False,'selection_modifiee':False,
            'verite_terrain':truth is not None,'verification_gpu_reelle':False,
            'avertissement':'IoU entre deux IA mesure un accord, PAS une exactitude. Mode diagnostic ne modifie pas l export Cricut.'}
    runner=model_runner
    if chosen and runner is None:
        if registry is None:
            import nodes
            registry=nodes.NODE_CLASS_MAPPINGS
        cls,opt=_get_refiner(registry,model)
        def runner(crop):
            node=cls()
            tensor=torch.from_numpy(np.ascontiguousarray(crop).astype(np.float32)/255).unsqueeze(0)
            params={'image':tensor,'model':model}
            settings={'background':'Alpha','background_color':'#FFFFFF','sensitivity':1.,
                      'mask_blur':0,'mask_offset':0,'invert_output':False,'refine_foreground':False,
                      'unload_model':True}
            for k,v in settings.items():
                if k in opt:params[k]=v
            try:
                raw=getattr(node,cls.FUNCTION)(**params)
                return _crop_mask(raw,crop.shape[:2])
            finally:
                backend=getattr(node,'model',None)
                if backend is not None and hasattr(backend,'clear_model'):
                    try:backend.clear_model()
                    except Exception:pass
                del node,tensor
                gc.collect()
                try:
                    if torch.cuda.is_available():torch.cuda.empty_cache()
                except Exception:
                    pass  # CUDA cleanup failures must not invalidate successful inference
    # Bound work to 4 region crops; source masks can be larger but no hidden
    # full-image batches are allocated. Never load SAM2 and matting concurrently.
    for risk,i,(x0,y0,x1,y1),stats in chosen:
        rec={'objet':i+1,'bbox_source_xyxy':[x0,y0,x1,y1], 'risque_heuristique':round(risk,5),**stats}
        start=time.perf_counter()
        try:
            crop=np.ascontiguousarray(rgb[y0:y1,x0:x1])
            proposal=np.asarray(runner(crop))
            if proposal.ndim!=2 or proposal.shape!=crop.shape[:2] or not np.issubdtype(proposal.dtype,np.number) or not np.isfinite(proposal).all():
                raise RefinementError('Masque de second passage mal forme')
            if proposal.min()<0 or proposal.max()>1:raise RefinementError('Masque secondaire hors 0..1')
            proposal=proposal.astype(np.float32)
            report['appels_modele_reussis']+=1
            old=base[i,y0:y1,x0:x1]
            a=old>=.5;b=proposal>=.5
            denom=int(np.count_nonzero(a|b));inter=int(np.count_nonzero(a&b));iou=inter/denom if denom else 1.
            changed=(a!=b)
            # Highlight disagreement only inside a bounded ROI, not artificial
            # confidence or fabricated object-occlusion ordering.
            changed=cv2.dilate(changed.astype(np.uint8),np.ones((3,3),np.uint8),iterations=1)>0
            uncertain[y0:y1,x0:x1][changed]=255
            # An unprompted matting model can include a second object in the ROI.
            # Pixels held by *another* base mask beyond a 2px tolerance band
            # are not safe to assign to this object solely because IoU is high.
            neighbors=np.zeros_like(a,dtype=np.uint8)
            for other_index in range(len(base)):
                if other_index!=i:
                    neighbors |= (base[other_index,y0:y1,x0:x1]>=.5).astype(np.uint8)
            core_neighbors=cv2.erode(neighbors,np.ones((3,3),np.uint8),iterations=1)>0
            own_tolerant=cv2.dilate(a.astype(np.uint8),np.ones((3,3),np.uint8),iterations=2)>0
            intrusion=int(np.count_nonzero(b & core_neighbors & ~own_tolerant))
            max_intrusion=max(8,int(np.count_nonzero(a)*.005))
            # A newly grown foreground touching an *internal* ROI boundary
            # means the crop may have cut through a different object.
            roi_leaks=np.zeros_like(b,dtype=np.uint8)
            edges=((slice(0,1),slice(None),y0>0),
                   (slice(-1,None),slice(None),y1<h),
                   (slice(None),slice(0,1),x0>0),
                   (slice(None),slice(-1,None),x1<w))
            for yy,xx,interior in edges:
                if interior:
                    roi_leaks[yy,xx] = (b[yy,xx] & ~a[yy,xx]).astype(np.uint8)
            border_leak=int(np.count_nonzero(roi_leaks))
            accepted=bool(iou>=min_agreement and np.count_nonzero(b)>max(30,np.count_nonzero(a)*.25)
                          and intrusion<=max_intrusion and border_leak==0)
            if intrusion>max_intrusion:status='REFUSE_EMPIETEMENT_AUTRE_OBJET'
            elif border_leak:status='REFUSE_FUITE_BORD_ROI'
            elif not accepted:status='REFUSE_ACCORD_INSUFFISANT'
            else:status='CANDIDAT'
            rec.update({'statut':status, 'intrusion_autres_objets_px':intrusion,
                        'intrusion_tolerance_px':max_intrusion,'fuite_bord_roi_px':border_leak,
                        'iou_avec_base':round(iou,5),'accord_seuil':min_agreement,
                        'fraction_diff':round(float(np.count_nonzero(a!=b)/max(denom,1)),5)})
            if accepted:
                # Propose complete crop mask, but outside the rectangle is left
                # as the original; do not silently inject foreground elsewhere.
                trial=base[i].copy();trial[y0:y1,x0:x1]=proposal
                candidates[i]=trial
                if mode=='adopter_annotation':
                    original_iou,new_iou=_compare_to_truth(base[i],trial,truth[i])
                    rec['iou_annotation_base']=round(original_iou,5)
                    rec['iou_annotation_candidat']=round(new_iou,5)
                    if new_iou>=original_iou+.025:
                        selected[i]=trial;rec['statut']='ADOPTE_SUR_ANNOTATION'
            del proposal,crop
        except Exception as exc:
            rec.update({'statut':'ECHEC_MODELE','erreur':f'{type(exc).__name__}: {str(exc)[:175]}'})
        rec['duree_s']=round(time.perf_counter()-start,5)
        report['candidats'].append(rec)
    report['incertitude_pixels']=int(np.count_nonzero(uncertain))
    report['selection_modifiee']=bool(np.any(selected!=base))
    report['masques_proposes']=sum(rec['statut'] in ('CANDIDAT','ADOPTE_SUR_ANNOTATION') for rec in report['candidats'])
    return selected,candidates,uncertain.astype(np.float32)/255,report
