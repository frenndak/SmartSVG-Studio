"""V21.12.1: conservative image routing and dark-background multi-sticker extraction.

No OCR, object recognition or semantic claim. No model execution in inspect_route.
Dark extraction requires near-black border, separated large components and a
well-spaced arrangement; otherwise AI/manual route. Returns suggested MASKs.
"""
from __future__ import annotations
import cv2
import numpy as np
from .auto_masks_v2111 import _accept, MAX_TOTAL, MAX_MASKS

BLACK_CUTOFF = 48


def inspect_route(image, *, has_alpha=False):
    a=np.asarray(image)
    if a.ndim!=3 or a.shape[2] not in (3,4) or a.dtype!=np.uint8:
        raise ValueError('IMAGE RGB/RGBA uint8 requise')
    h,w=a.shape[:2]
    if min(h,w)==0 or h*w>5_000_000:raise ValueError('Taille source trop grande')
    rgb=a[:,:,:3]
    # Use pixels on four edges only, not an expensive full-image model.
    edge=np.concatenate((rgb[0],rgb[-1],rgb[:,0],rgb[:,-1])).astype(np.float32)
    median=np.median(edge,axis=0)
    p95=float(np.percentile(np.max(abs(edge-median),axis=1),95))
    black=bool(np.max(median)<35 and p95<14)
    white=bool(np.min(median)>233 and p95<16)
    if has_alpha or a.shape[2]==4:
        kind='TRANSPARENCE_POSSIBLE'; mode='MASQUE_ALPHA_D_ABORD'
    elif black:
        kind='FOND_NOIR_UNIFORME';mode='PLANCHE_SOMBRE_OU_IA'
    elif white:
        kind='FOND_BLANC_UNIFORME';mode='DETECTION_SIMPLE_OU_IA'
    else:
        kind='SCENE_OPAQUE_COMPLEXE';mode='IA_OU_CORRECTION'
    return {'type_image':kind,'strategie':mode,'dimensions_px':[w,h],
            'bord_median_rgb':median.astype(int).tolist(),
            'variation_bord_p95':round(p95,2),
            'contenu_semantique_reconnu':False,
            'texte_extrait_ocr':False,
            'besoin_de_validation_visuelle':True,
            'fonds_uniformes_ne_garantissent_pas_un_detourage':True}


def dark_sheet_masks(image):
    """Conservative extraction of *separated* graphic assets against black.

    Requires >=3 similarly sized independent foreground components and a solid
    near-black border; individual all-black characters and photos fail closed.
    Components outside the kept contours are documented (not silently called
    complete fidelity). Returns (masks or None, evidence).
    """
    a=np.asarray(image)
    if a.ndim!=3 or a.shape[2]!=3 or a.dtype!=np.uint8:
        raise ValueError('RGB uint8 attendu')
    h,w=a.shape[:2]
    meta={'methode':'ILLUSTRATION_FOND_NOIR','masques_prets_pour_decoupe':False,
          'certification_semantique':False,'raison':None,'fragments_ignores':0}
    route=inspect_route(a)
    if route['type_image']!='FOND_NOIR_UNIFORME':
        meta['raison']='FOND_NOIR_NON_CONFIRME';return None,meta
    fg=np.ascontiguousarray(a.max(axis=2)>BLACK_CUTOFF,dtype=np.uint8)
    fraction=float(fg.mean())
    if not 0.035<fraction<0.58:
        meta['raison']='DENSITE_AVANT_PLAN_SUSPECTE';return None,meta
    labels_count,labels,stats,centers=cv2.connectedComponentsWithStats(fg,8)
    min_area=max(650,int(h*w*.0024))
    keep=[i for i in range(1,labels_count) if int(stats[i,cv2.CC_STAT_AREA])>=min_area]
    if not (3<=len(keep)<=MAX_MASKS) or h*w*len(keep)>MAX_TOTAL:
        meta['raison']='COMPOSANTES_OU_MEMOIRE_HORS_LIMITES';return None,meta
    areas=np.array([stats[i,cv2.CC_STAT_AREA] for i in keep],dtype=np.int64)
    if areas.min()<areas.mean()*.3 or areas.max()>areas.mean()*2.5:
        meta['raison']='TAILLES_DE_SUJETS_INCOHERENTES';return None,meta
    total=int(np.count_nonzero(fg))
    explained=float(areas.sum()/max(1,total))
    if explained<.92:
        meta['raison']='TROP_DE_FRAGMENTS_HORS_SUJETS';return None,meta
    # Exclude cases where the interior is mostly one dark photographic plane.
    # A detached bright component must be enclosed well within the image.
    for i in keep:
        x,y,bw,bh,area=map(int,stats[i]);
        if x<=2 or y<=2 or x+bw>=w-2 or y+bh>=h-2:
            meta['raison']='SUJET_TOUS_BORDS';return None,meta
    keep.sort(key=lambda i:(int(centers[i][1]//max(1,h//8)),float(centers[i][1]),float(centers[i][0])))
    # Use top-to-bottom scanline grouping for deterministic reading order.
    # Sort by row using component vertical centres clustered into bands.
    keep.sort(key=lambda i:float(centers[i][1]))
    rows=[]; typical_h=float(np.median([stats[i,cv2.CC_STAT_HEIGHT] for i in keep]))
    for i in keep:
        if not rows or abs(float(centers[i][1])-float(np.median([centers[v][1] for v in rows[-1]])))>typical_h*.60:
            rows.append([i])
        else:rows[-1].append(i)
    keep=[i for row in rows for i in sorted(row,key=lambda i:float(centers[i][0]))]
    stack=np.zeros((len(keep),h,w),dtype=np.uint8)
    details=[]
    for slot,i in enumerate(keep):
        x,y,bw,bh,area=map(int,stats[i]);pad=3
        x0=max(0,x-pad);x1=min(w,x+bw+pad);y0=max(0,y-pad);y1=min(h,y+bh+pad)
        local=np.uint8(labels[y0:y1,x0:x1]==i)
        # Exterior silhouette, filling internal black outlines/holes.
        contours,_=cv2.findContours(local,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        filled=np.zeros_like(local)
        cv2.drawContours(filled,contours,-1,1,cv2.FILLED)
        stack[slot,y0:y1,x0:x1]=filled
        details.append({'bbox_px':[x,y,bw,bh],'surface_pixels':int(filled.sum())})
    result,flags=_accept(stack,pixel_count=h*w,expected_hw=(h,w),source='HEURISTIQUE')
    if result is None:
        meta['raison']='MASQUE_REFUSE_'+','.join(flags);return None,meta
    fragments=sum(1 for i in range(1,labels_count)
                  if i not in set(keep) and int(stats[i,cv2.CC_STAT_AREA])>=150)
    meta.update({'nombre_sujets':len(keep),'proportion_pixels_expliques':round(explained,4),
                 'fragments_ignores':int(fragments),'sujets':details,'avertissements':flags+
                 (['DETAILS_DETACHES_POTENTIELLEMENT_MANQUANTS'] if fragments else []),
                 'statut':'MASQUES_PROPOSES_A_VERIFIER'})
    return result,meta
