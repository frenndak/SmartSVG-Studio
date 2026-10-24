"""V21.12.1 visual geometry QA - conservative advisory metrics, never machine proof."""
from __future__ import annotations
import numpy as np
import cv2


def evaluate_masks(masks, *, kind, method, physical_width_mm=40., additional_flags=()):
    a=np.asarray(masks)
    if a.ndim!=3 or not a.shape[0] or not 5<=float(physical_width_mm)<=300:
        raise ValueError('Masques ou largeur incorrects')
    h,w=a.shape[1:]
    items=[];overall=[]
    for index,mask in enumerate(a):
        binary=np.ascontiguousarray(mask>=.5,dtype=np.uint8)
        ys,xs=np.nonzero(binary)
        if not len(xs):raise ValueError('Masque vide interdit')
        x0,x1=int(xs.min()),int(xs.max()+1)
        y0,y1=int(ys.min()),int(ys.max()+1)
        roi=binary[y0:y1,x0:x1]
        contours,_=cv2.findContours(roi,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        n,_,stats,_=cv2.connectedComponentsWithStats(roi,8)
        area=int(binary.sum());bounds=(x1-x0)*(y1-y0)
        perimeter=float(sum(cv2.arcLength(c,closed=True) for c in contours))
        compact=round(perimeter**2/max(1,4*np.pi*area),2)
        # 2mm after scaled export might be fragile; metrics are advisories only.
        mm_px=float(physical_width_mm)/max(1,x1-x0)
        warnings=[]
        if min(x0,y0,w-x1,h-y1)<2:warnings.append('PROCHE_DU_BORD_DE_L_IMAGE')
        if n-1>1:warnings.append('COMPOSANTES_MULTIPLES')
        if area/max(1,bounds)>.985:warnings.append('QUASI_RECTANGLE_A_REVOIR')
        if compact>22:warnings.append('CONTOUR_COMPLEXE_A_INSPECTER')
        if x1-x0<30 or y1-y0<30:warnings.append('PETIT_OBJET_SOURCE')
        # Do not label any mask as semantically correct: topology alone is insufficient.
        items.append({'indice':index+1,'cadre_px':[x0,y0,x1-x0,y1-y0],
            'dimensions_estimees_mm':[round((x1-x0)*mm_px,2),round((y1-y0)*mm_px,2)],
            'surface_pixels':area,'occupation_cadre':round(area/max(1,bounds),4),
            'composantes':int(n-1),'complexite_contour':compact,
            'avertissements':warnings,'verification_humaine_necessaire':True})
        overall.extend(warnings)
    overall+=list(additional_flags)
    if kind=='SCENE_OPAQUE_COMPLEXE':overall.append('SUJET_ET_TEXTE_NON_VERIFIES')
    if method=='SEGMENTATION_IA':overall.append('IA_NE_GARANTIT_PAS_LE_SUJET_SOUHAITE')
    state='REVISION_VISUELLE_PRIORITAIRE' if overall else 'PRECONTROLE_GEOMETRIQUE_SEULEMENT'
    return {'statut':state,'nombre_masques':len(items),'largeur_silhouette_mm':float(physical_width_mm),
        'sujets':items,'alertes':sorted(set(overall)),
        'fidelite_semantique_certifiee':False,'import_cricut_execute':False,
        'decoupe_physique_executee':False,
        'conseil':'Examiner les contours et la taille dans Design Space avant d’imprimer et découper.'}
