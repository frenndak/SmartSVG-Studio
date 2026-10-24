"""SmartSVG V19.6 -- cautious, bounded comparison of already generated masks.

Important: scores are heuristic consistency diagnostics, NOT calibrated neural
model confidences or validated segmentation quality measurements. In the absence
of ground-truth labels no system can establish which contour is *correct*.
"""
from __future__ import annotations
import numpy as np
import cv2

MAX_OBJECTS=16
MAX_TOTAL_SAMPLES=28_000_000
NAMES=('reference','alternative_B','alternative_C')

class MaskComparisonError(ValueError):
    pass


def _as_float_masks(value, name):
    """Validate N,H,W, floats 0..1, no silent rescaling/transposition."""
    if value is None:return None
    x=np.asarray(value)
    if x.ndim==2:x=x[None]
    if x.ndim!=3 or x.shape[0]<1 or x.shape[0]>MAX_OBJECTS or min(x.shape[1:])<2:
        raise MaskComparisonError(f'{name}: masques [N,H,W] attendus (1..16), obtenu {x.shape}')
    if x.size>MAX_TOTAL_SAMPLES or not np.issubdtype(x.dtype,np.number):
        raise MaskComparisonError(f'{name}: budget pixels ou type de donnees interdit')
    if not np.isfinite(x).all():raise MaskComparisonError(f'{name}: NaN ou infinite interdit')
    lo=float(x.min());hi=float(x.max())
    if lo<-.0001 or hi>1.0001:
        raise MaskComparisonError(f'{name}: valeurs hors 0..1; normaliser les masques 0..255 AVANT import')
    return np.clip(x.astype(np.float32),0,1)


def _edge_match(rgb, mask):
    """Boundary/image-gradient correlation; contrast is not correctness."""
    h,w=mask.shape
    ys,xs=np.where(mask>=.5)
    if ys.size==0:return 0.0
    extra=9
    y0=max(0,int(ys.min())-extra);y1=min(h,int(ys.max())+extra+1)
    x0=max(0,int(xs.min())-extra);x1=min(w,int(xs.max())+extra+1)
    roi=rgb[y0:y1,x0:x1]
    m=mask[y0:y1,x0:x1]
    if max(m.shape)>3500: # cheap bounded downsampling for large regions
        ratio=3500/max(m.shape);new=(max(2,int(m.shape[1]*ratio)),max(2,int(m.shape[0]*ratio)))
        roi=cv2.resize(roi,new,interpolation=cv2.INTER_AREA)
        m=cv2.resize(m,new,interpolation=cv2.INTER_LINEAR)
    gray=cv2.cvtColor(roi,cv2.COLOR_RGB2GRAY).astype('float32')/255.
    dx=cv2.Sobel(gray,cv2.CV_32F,1,0,ksize=3)
    dy=cv2.Sobel(gray,cv2.CV_32F,0,1,ksize=3)
    grad=cv2.magnitude(dx,dy)
    # robust normalization: 90th percentile sampled at most 65k positions
    flat=grad.ravel()[::max(1,grad.size//65000)]
    scale=max(.05,float(np.percentile(flat,90)))
    grad=np.clip(grad/scale,0,1)
    hard=(m>=.5).astype('uint8')
    band=cv2.morphologyEx(hard,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))>0
    if not np.any(band):return 0.0
    return float(np.mean(grad[band]))


def _measure(rgb, mask):
    m=mask>=.5
    h,w=m.shape
    area=int(m.sum())
    if area<16 or area>int(.99*h*w):
        return {'utilisable':False,'raison':'masque vide, quasi vide ou couvre presque toute l image',
                'surface_pct':round(100*area/(h*w),3),'score_heuristique':0.}
    n,_,stats,_=cv2.connectedComponentsWithStats(m.astype('uint8'),8)
    sizes=[int(stats[i,cv2.CC_STAT_AREA]) for i in range(1,n)]
    largest=max(sizes) if sizes else 0
    fragment=(area-largest)/max(area,1)
    small=sum(s<max(16,int(area*.003)) for s in sizes)
    ys,xs=np.where(m)
    border=bool((xs.min()==0) or (ys.min()==0) or (xs.max()==w-1) or (ys.max()==h-1))
    gradient=_edge_match(rgb,mask)
    soft_frac=float(np.mean((mask>.02)&(mask<.98)))
    # Penalties are advisory: a real hair strand can be a tiny island, and a
    # cropped person may legitimately touch the border.
    score=float(np.clip(40+35*gradient-38*fragment-min(17,small*2)- (5 if border else 0),0,100))
    return {'utilisable':True,'score_heuristique':round(score,3),
            'surface_pct':round(100*area/(h*w),3),
            'alignement_contraste_bord':round(gradient,4),
            'fraction_fragmentee':round(fragment,5),
            'petits_fragments':small,'touche_bord':border,
            'fraction_pixels_semi_transparents':round(soft_frac,5),
            'note':'score de coherence interne, NON probabilite de bon detourage'}


def _iou(a,b):
    aa=a>=.5; bb=b>=.5
    union=int(np.count_nonzero(aa|bb))
    return float(np.count_nonzero(aa&bb)/union) if union else 0.


def compare_mask_sets(rgb, reference, alt_b=None, alt_c=None, *, mode='diagnostic', min_iou=.68,
                      min_score_gain=9., annotated=None):
    """Return original or prudently-selected mask set + inspectable metrics.

    Compare by positional index ONLY if all candidates have same N,H,W. A
    changed number/order of objects is not a fair candidate comparison.
    """
    if mode not in ('conservateur','diagnostic','selection_prudente'):
        raise MaskComparisonError('mode inconnu')
    rgb=np.asarray(rgb)
    if rgb.ndim!=3 or rgb.shape[2]!=3 or rgb.dtype!=np.uint8:
        raise MaskComparisonError('IMAGE source HxWx3 uint8 requise')
    h,w=rgb.shape[:2]
    primary=_as_float_masks(reference,'reference')
    if primary is None:raise MaskComparisonError('masque reference requis: ne pas fabriquer de masque de secours')
    if primary.shape[1:]!=(h,w):
        raise MaskComparisonError('masques reference non alignes sur les pixels de l IMAGE')
    candidates=[primary];warnings=[]
    for name,data in zip(NAMES[1:],(alt_b,alt_c)):
        if data is None:
            candidates.append(None);continue
        try:
            value=_as_float_masks(data,name)
            if value.shape!=primary.shape:
                raise MaskComparisonError(f'{name}: dimensions ou nombre d objets different; ordre non comparable')
            candidates.append(value)
        except MaskComparisonError as exc:
            candidates.append(None);warnings.append(str(exc))
    ground_truth=_as_float_masks(annotated,'masque_annote') if annotated is not None else None
    if ground_truth is not None and ground_truth.shape!=primary.shape:
        raise MaskComparisonError('masque annote: dimensions ou nombre d objets incompatibles')
    # Protect against large simultaneous candidates in memory.
    if primary.size*(sum(x is not None for x in candidates)+(ground_truth is not None))>MAX_TOTAL_SAMPLES:
        raise MaskComparisonError('budget total multi-masques depasse')
    selected=primary.copy()
    objects=[];alternatives_available=sum(x is not None for x in candidates[1:])
    for i in range(primary.shape[0]):
        base=_measure(rgb,primary[i]); stats=[base]
        chosen=0;gain=0.
        for j in (1,2):
            candidate=candidates[j]
            if candidate is None:stats.append(None);continue
            measured=_measure(rgb,candidate[i]);overlap=_iou(primary[i],candidate[i])
            measured['iou_vs_reference']=round(overlap,5)
            stats.append(measured)
            if mode=='selection_prudente' and base['utilisable'] and measured['utilisable']:
                delta=measured['score_heuristique']-base['score_heuristique']
                if overlap>=min_iou and delta>=min_score_gain and delta>gain:
                    chosen=j;gain=float(delta)
        if chosen:
            selected[i]=candidates[chosen][i]
        # With a manually annotated reference, expose REAL supervised overlap
        # metrics. Do not silently change selection based on labels.
        if ground_truth is not None:
            gt=ground_truth[i]>=.5
            for j,sc in enumerate(stats):
                if sc is None:continue
                present=candidates[j][i]>=.5
                inter=int(np.count_nonzero(present & gt))
                union=int(np.count_nonzero(present | gt))
                size=int(np.count_nonzero(present))+int(np.count_nonzero(gt))
                sc['iou_avec_annotation']=round(inter/union,5) if union else 1.
                sc['dice_avec_annotation']=round(2*inter/size,5) if size else 1.
        objects.append({'index':i+1,'scores':dict(zip(NAMES,stats)),'selection':NAMES[chosen],
                       'gain_heuristique':round(gain,3),
                       'explication':'Une comparaison sans masque de verite terrain ne garantit PAS une meilleure segmentation.'})
    used=[x['selection'] for x in objects]
    report={'version':'19.6-beta','mode':mode,'nombre_objets':len(objects),
            'variantes_comparees':1+alternatives_available,
            'selection':used,'objets':objects,'avertissements':warnings,
            'annotation_manuelle_utilisee':ground_truth is not None,
            'test_gpu_reel':False,
            'limite':'Le classement suppose l alignement et le meme ordre des objets. Un score eleve ne prouve pas la qualite du detourage.',
            'cricut':'Les masques originaux restent inchanges; verifier manuellement les contours dans Design Space.'}
    return selected, report
