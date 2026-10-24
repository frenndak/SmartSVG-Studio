"""Read-only Cricut geometry QA on exact mask dimensions.

Values are *estimates* from a mask prior to the export engine's contour
simplification, bleed, offsets or Design Space interpretation.
Never deletes islands or fills holes; leaves original floating masks intact.
"""
from __future__ import annotations
import cv2
import math
import numpy as np

MAX_INSTANCES=32
MAX_PIXELS=5_000_000
MAX_TOTAL=50_000_000

class GeometryError(ValueError):pass


def _check(masks,width_mm):
    a=np.asarray(masks)
    if a.ndim!=3 or a.shape[0]<1 or a.shape[0]>MAX_INSTANCES or min(a.shape[1:])<1 or a.shape[1]*a.shape[2]>MAX_PIXELS or a.size>MAX_TOTAL:
        raise GeometryError('QA : masques [N,H,W], N <= 32, <= 5 Mp/image et 50 Mp cumulés')
    if not np.issubdtype(a.dtype,np.number) or not np.isfinite(a).all() or a.min()<-.001 or a.max()>1.001:
        raise GeometryError('QA : masques non finis ou hors de 0..1')
    if isinstance(width_mm,bool) or not isinstance(width_mm,(int,float)) or not math.isfinite(width_mm) or width_mm<5 or width_mm>300:
        raise GeometryError('QA : largeur finale entre 5 et 300 mm')
    return a


def inspect(masks, *,width_mm=40.,threshold=.5,min_island_mm2=.35,min_hole_mm2=.35,min_neck_mm=.35):
    a=_check(masks,width_mm)
    if any(not isinstance(x,(int,float)) or isinstance(x,bool) or not math.isfinite(x) for x in (threshold,min_island_mm2,min_hole_mm2,min_neck_mm)):
        raise GeometryError('QA : seuils non finis')
    if not (0<threshold<1 and 0<min_island_mm2<=5 and 0<min_hole_mm2<=5 and 0<min_neck_mm<=2):
        raise GeometryError('QA : seuils hors limites')
    n,h,w=a.shape
    binary=np.ascontiguousarray(a>=threshold)
    summary=[]
    overlap=(np.sum(binary,axis=0,dtype=np.uint8)>1) if n>1 else np.zeros((h,w),dtype=bool)
    has_overlap=bool(np.any(overlap))
    for i in range(n):
        mask=np.uint8(binary[i])
        pixel_count=int(np.count_nonzero(mask))
        if pixel_count==0:
            summary.append({'objet':i+1,'etat':'bloquant','surface_px':0,'composants':0,
                'alertes':['MASQUE_VIDE'],'largeur_px':0,'mm_par_pixel_estime':None})
            continue
        y,x=np.nonzero(mask)
        x0=int(x.min());x1=int(x.max())+1;y0=int(y.min());y1=int(y.max())+1
        object_width=x1-x0
        # Express's requested width corresponds to the selected object's crop bbox.
        mm_per_px=float(width_mm)/object_width
        mm2=mm_per_px**2
        count,labels,stats,_=cv2.connectedComponentsWithStats(mask,8)
        comps=[int(stats[j,cv2.CC_STAT_AREA]) for j in range(1,count)]
        micro=sum(1 for area in comps if area*mm2 < min_island_mm2)
        # Holes must be fully enclosed within the mask. RETR_CCOMP yields direct inner contours.
        contours,hierarchy=cv2.findContours(mask,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
        tiny_holes=0;holes=0
        if hierarchy is not None:
            for index,entry in enumerate(hierarchy[0]):
                if entry[3]>=0:
                    holes+=1
                    if abs(float(cv2.contourArea(contours[index])))*mm2 < min_hole_mm2:
                        tiny_holes+=1
        # Detect fragile necks by topology change after opening with a metric kernel.
        # Limit kernel to 31px for runtime and avoid claiming a reliable pass at extreme pixel/mm scales.
        diameter=round(min_neck_mm/mm_per_px)
        narrow=False;resolution_warning=False
        if diameter<2:
            resolution_warning=True
        elif diameter>31:
            resolution_warning=True
        else:
            k=max(3,int(diameter)|1)
            opened=cv2.morphologyEx(mask,cv2.MORPH_OPEN,
                cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
            after=cv2.connectedComponents(opened,8)[0]-1
            if after>len(comps) or (after==0 and pixel_count>0):narrow=True
        touch=(x0<=1 or y0<=1 or x1>=w-1 or y1>=h-1)
        flags=[]
        if len(comps)>1: flags.append('ILOTS_DETACHES')
        if micro:flags.append('MICRO_ILOTS')
        if tiny_holes:flags.append('MICRO_TROUS')
        if narrow:flags.append('PASSAGE_FIN_A_VERIFIER')
        if resolution_warning:flags.append('PRECISION_INSUFFISANTE_POUR_TEST_PASSAGE_FIN')
        if touch:flags.append('MASQUE_TOUCHE_BORD_IMAGE')
        if has_overlap and bool(np.any(binary[i] & overlap)):
            flags.append('MASQUES_CHEVAUCHANTS')
        summary.append({'objet':i+1,'etat':'a_verifier' if flags else 'ok',
            'surface_px':pixel_count,'largeur_px':object_width,'mm_par_pixel_estime':round(mm_per_px,5),
            'boite_px':[x0,y0,x1,y1], 'composants':len(comps),'micro_ilots':micro,
            'trous':holes,'micro_trous':tiny_holes,'alerte_bord':touch,'alertes':flags})
    return {'version':'21.7','type':'audit_geometrique_non_destructif',
        'largeur_finale_mm_hypothese':float(width_mm),'seuil_masque':float(threshold),
        'nombre_objets':n,'objets':summary,'nombre_alertes':sum(len(o['alertes']) for o in summary),
        'statut':'bloquant' if any(o['etat']=='bloquant' for o in summary) else
            'a_verifier' if any(o['etat']=='a_verifier' for o in summary) else 'ok',
        'important':'Indicateurs de masque avant fabrication; ne certifient pas la découpe Cricut physique, le SVG interne ou la précision du détourage IA.'}
