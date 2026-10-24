"""V19.8: bounded, one-to-one alignment of independent segmentation mask batches.

The result is diagnostic by default. A geometric match is NOT proof that two
masks depict the same real-world object, nor is a heuristic score a calibrated
quality estimate. Works on masks already produced elsewhere: no model weights.
"""
from __future__ import annotations

import cv2
import numpy as np

from .mask_compare_v196 import _as_float_masks, _measure, MaskComparisonError

MAX_COMBINED_PIXELS = 28_000_000
MIN_MATCH_IOU = 0.45
AMBIGUOUS_GAP = 0.08


def _hungarian_rect(cost: np.ndarray) -> list[int]:
    """Minimum cost assignment, one column per row (rectangular, m>=n)."""
    nr, nc = cost.shape
    if nc < nr: raise MaskComparisonError('Appariement : matrice trop etroite')
    u = np.zeros(nr+1, dtype=np.float64)
    v = np.zeros(nc+1, dtype=np.float64)
    p = np.zeros(nc+1, dtype=np.int32)
    way = np.zeros(nc+1, dtype=np.int32)
    for i in range(1, nr+1):
        p[0] = i
        j0 = 0
        minv = np.full(nc+1, np.inf)
        used = np.zeros(nc+1, dtype=bool)
        while True:
            used[j0] = True
            i0 = int(p[j0]); delta = np.inf; j1 = -1
            for j in range(1, nc+1):
                if used[j]: continue
                cur = float(cost[i0-1,j-1]) - u[i0] - v[j]
                if cur < minv[j]:
                    minv[j] = cur
                    way[j] = j0
                if minv[j] < delta:
                    delta = minv[j]
                    j1 = j
            if j1 < 0: raise MaskComparisonError('Appariement impossible')
            for j in range(nc+1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                elif j:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0: break
        while j0:
            j1 = int(way[j0]); p[j0] = p[j1]; j0 = j1
    assignment = [-1]*nr
    for j in range(1,nc+1):
        if p[j]:assignment[p[j]-1] = j-1
    return assignment


def _bounding(binary: np.ndarray):
    ys,xs=np.nonzero(binary)
    if ys.size == 0: return None
    return (int(ys.min()),int(ys.max())+1,int(xs.min()),int(xs.max())+1)


def _intersection(a,b,boxa,boxb):
    if boxa is None or boxb is None:return 0
    y0=max(boxa[0],boxb[0]);y1=min(boxa[1],boxb[1]);x0=max(boxa[2],boxb[2]);x1=min(boxa[3],boxb[3])
    if y1<=y0 or x1<=x0:return 0
    return int(np.count_nonzero(a[y0:y1,x0:x1] & b[y0:y1,x0:x1]))


def _iou_matrix(a:np.ndarray,b:np.ndarray):
    a_mask=a>=.5;b_mask=b>=.5
    counts_a=[int(v.sum()) for v in a_mask];counts_b=[int(v.sum()) for v in b_mask]
    boxes_a=[_bounding(v) for v in a_mask];boxes_b=[_bounding(v) for v in b_mask]
    mat=np.zeros((len(a),len(b)),dtype=np.float64)
    for i in range(len(a)):
        for j in range(len(b)):
            inter=_intersection(a_mask[i],b_mask[j],boxes_a[i],boxes_b[j])
            union=counts_a[i]+counts_b[j]-inter
            mat[i,j]=inter/union if union else 0.0
    return mat


def _one_to_one(reference,alternative,threshold=MIN_MATCH_IOU,ambiguous_gap=AMBIGUOUS_GAP):
    overlaps=_iou_matrix(reference,alternative)
    nr,na=overlaps.shape
    # Dummy columns let references remain UNMATCHED. Illegal real matches cost
    # worse than an unmatched dummy, never force a false positive.
    cost=np.full((nr,na+nr),1.0,dtype=np.float64)
    cost[:,:na]=np.where(overlaps>=threshold,1.0-overlaps,1.1)
    assigned=_hungarian_rect(cost)
    mapping={};rejected={}
    for i,j in enumerate(assigned):
        if j>=na or overlaps[i,j]<threshold:
            rejected[i]='aucune_correspondance_suffisante'
            continue
        val=float(overlaps[i,j])
        row=np.delete(overlaps[i,:],j)
        col=np.delete(overlaps[:,j],i)
        next_row=float(row.max()) if row.size else -1
        next_col=float(col.max()) if col.size else -1
        # Ambiguity in either direction: duplicate or nearly identical masks.
        if max(next_row,next_col) >= threshold and val-max(next_row,next_col)<ambiguous_gap:
            rejected[i]='correspondance_ambigue';continue
        mapping[i]=j
    return mapping,rejected,overlaps


def compare_aligned_masks(rgb,reference,alt_b=None,alt_c=None,*,annotation=None,
                          mode='diagnostic',min_match_iou=MIN_MATCH_IOU):
    """Return unmodified or expressly selected reference, pixel-uncertainty map and QA.

    Requires a single RGB source and object masks registered to that source.
    Alternatives may have different order or different number of objects.
    Unsupported/ambiguous objects are never silently replaced.
    """
    if mode not in ('diagnostic','selection_prudente','selection_avec_annotation'):
        raise MaskComparisonError('Mode comparaison V19.8 inconnu')
    x=np.asarray(rgb)
    if x.ndim!=3 or x.shape[2]!=3 or x.dtype!=np.uint8:
        raise MaskComparisonError('IMAGE RGB uint8 HxWx3 requis')
    h,w=x.shape[:2]
    if not .35<=float(min_match_iou)<=.95:
        raise MaskComparisonError('IoU minimum hors plage')
    # Check total raw element count BEFORE conversion to float32. Several
    # large uint8 batches can otherwise cause needless multi-GB allocations.
    raw_samples=sum(np.asarray(batch).size for batch in
                    (reference,alt_b,alt_c,annotation) if batch is not None)
    if raw_samples>MAX_COMBINED_PIXELS:
        raise MaskComparisonError('Budget memoire multi-masques depasse AVANT conversion')
    ref=_as_float_masks(reference,'reference')
    if ref is None:raise MaskComparisonError('Masque reference indispensable')
    if ref.shape[1:] != (h,w):raise MaskComparisonError('Masques reference non alignes avec l image')
    ann=_as_float_masks(annotation,'annotation') if annotation is not None else None
    if ann is not None and ann.shape != ref.shape:
        raise MaskComparisonError('Annotation: memes N,H,W et ordre que le masque reference requis')
    if mode=='selection_avec_annotation' and ann is None:
        raise MaskComparisonError('Selection supervisee impossible sans annotation de verite terrain')
    alt={}; warnings=[]
    for name,value in [('alternative_B',alt_b),('alternative_C',alt_c)]:
        if value is None:continue
        try:
            batch=_as_float_masks(value,name)
            if batch.shape[1:]!=(h,w):raise MaskComparisonError('masques non alignes spatialement')
            alt[name]=batch
        except MaskComparisonError as e:
            warnings.append(f'{name}: {str(e)}')
    if ref.size + sum(v.size for v in alt.values()) + (ann.size if ann is not None else 0)>MAX_COMBINED_PIXELS:
        raise MaskComparisonError('Budget memoire multi-masques depasse')
    selected=ref.copy()
    uncertainty=np.zeros((h,w),dtype=np.uint8)
    # Reference objects that overlap remain ambiguous for downstream cutting.
    active=np.zeros((h,w),dtype=np.uint8)
    for a in ref: active=np.minimum(active+(a>=.5).astype('uint8'),2)
    uncertainty[active>1]=255
    ref_stats=[_measure(x,m) for m in ref]
    obj=[{'index':i+1,'masque_reference':i+1,'selection':'reference',
          'mode_validation':'aucune_verite_terrain' if ann is None else 'annotation_fournie',
          'diagnostic_reference':ref_stats[i], 'alternatives':{}} for i in range(len(ref))]
    unmatched={}; alignments={}
    for name, batch in alt.items():
        mapping,rejected,mat=_one_to_one(ref,batch,float(min_match_iou))
        alignments[name]={str(i+1):{'index_alternatif':j+1,'iou':round(float(mat[i,j]),5)}
                          for i,j in mapping.items()}
        unmatched[name]={str(i+1):cause for i,cause in rejected.items()}
        for i in range(len(ref)):
            if i not in mapping:
                obj[i]['alternatives'][name]={'statut':rejected[i]};continue
            j=mapping[i]; mask=batch[j]
            hard_ref=ref[i]>=.5;hard_alt=mask>=.5
            diff=hard_ref!=hard_alt
            # Boundary uncertainty preview also highlights narrow edge changes.
            if np.any(diff):
                uncertain=cv2.dilate(diff.astype('uint8'),np.ones((3,3),np.uint8),iterations=1)>0
                uncertainty[uncertain]=255
            edge_disagreement=round(float(np.count_nonzero(diff) / max(1,int(np.count_nonzero(hard_ref|hard_alt)))),5)
            q=_measure(x,mask)
            entry={'statut':'apparie','index_alternatif':j+1,
                   'iou_avec_reference':round(float(mat[i,j]),5),
                   'fraction_desaccord':edge_disagreement,'diagnostic':q}
            if ann is not None:
                gt=ann[i]>=.5
                ai=int(np.count_nonzero(hard_alt & gt));au=int(np.count_nonzero(hard_alt | gt))
                ri=int(np.count_nonzero(hard_ref & gt));ru=int(np.count_nonzero(hard_ref | gt))
                entry['iou_avec_annotation']=round(ai/au if au else 1.,5)
                entry['iou_reference_avec_annotation']=round(ri/ru if ru else 1.,5)
            obj[i]['alternatives'][name]=entry
            if mode=='diagnostic' or not q['utilisable']:
                continue
            if obj[i]['selection']!='reference':continue
            if mode=='selection_prudente':
                improve=q['score_heuristique']-ref_stats[i]['score_heuristique']
                # Extremely cautious: high overlap AND very low changed area
                # AND meaningful heuristic gain. No claim of better truth.
                if float(mat[i,j])>=.86 and edge_disagreement<=.17 and improve>=12:
                    selected[i]=mask;obj[i]['selection']=name
                    obj[i]['mode_validation']='heuristique_NON_certifie'
            else:
                if entry['iou_avec_annotation']>=entry['iou_reference_avec_annotation']+.025:
                    selected[i]=mask;obj[i]['selection']=name
                    obj[i]['mode_validation']='comparee_a_annotation_explicite'
    report={'version':'19.8-beta','mode':mode,'nombre_objets_reference':len(ref),
            'alternatives_disponibles':list(alt),'appariements':alignments,
            'sans_appariement_ou_ambigus':unmatched,
            'objets':obj,'incertitude_pixels':int(np.count_nonzero(uncertainty)),
            'masque_reference_modifie':bool(np.any(selected!=ref)),
            'avertissements':warnings,
            'masque_annotation_fourni':ann is not None,
            'sens_de_la_qualite':'IoU avec annotation = qualite mesuree; IoU entre modeles = accord, PAS verite.',
            'limites':'Masques deja calcules seulement; aucune execution de SAM2/FeyNoBg/Finegrain. PNG Cricut non modifie par ce module.',
            'validation_gpu_physique':False,'validation_decoupe_physique':False}
    return selected,uncertainty.astype(np.float32)/255.0,report
