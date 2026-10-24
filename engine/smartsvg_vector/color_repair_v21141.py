"""V21.14.1: bounded color-aware SVG reconstruction, intentionally experimental.

The V21.14 silhouette base remains underneath legacy vector layers. To improve
color recovery, this optional pass adds a handful of source-derived *vector*
regions, limited to areas the V21.13 original SVG failed to cover. It refuses
any candidate that worsens coverage or color fidelity and keeps the old SVG.

The manufactured Print Then Cut PNG and its cut-path SVG are never modified.
"""
from __future__ import annotations
import re
import cv2
import numpy as np
from .layers_v2113 import VectorizationRefused,MAX_PATHS,MAX_POINTS,MAX_BYTES
from .recovery_v2114 import vectorize_recovered,_rings,_cut_risk
from .qa_v21131 import _strict_render,_standard_render,analyse_svg

_MIN_FRAGMENT = 35
_MAX_ACCENTS = 10
_MAX_ADDED_POINTS = 6500
_MAX_ADDED_PATHS = 12


def _render_svg(svg):
    approximate,qa = _strict_render(svg)
    h,w=approximate.shape[:2]
    standard=_standard_render(svg,w,h)
    return (standard if standard is not None else approximate),bool(standard is not None),qa


def _masked_full_color_mae(image,mask,svg,info):
    """Composite alpha onto white; measure RGB MAE across *all source subject pixels*.

    Missing subject pixels are therefore penalized as blank white, whereas the
    historical conditional color metric excluded all missing pixels.
    """
    raster,verified,_ = _render_svg(svg)
    h,w=raster.shape[:2]
    x0,y0,x1,y1=info['zone_sujet_originale']
    sub=np.asarray(image,dtype=np.uint8)[y0:y1,x0:x1,:3]
    interpolation=cv2.INTER_AREA if sub.shape[1]>w or sub.shape[0]>h else cv2.INTER_LINEAR
    src=cv2.resize(sub,(w,h),interpolation=interpolation)
    m=np.asarray(mask)[y0:y1,x0:x1]
    reference=cv2.resize(np.uint8(m>=.5),(w,h),interpolation=cv2.INTER_NEAREST).astype(bool)
    if not reference.any():raise VectorizationRefused('Masque de comparaison vide')
    alpha=raster[:,:,3:4].astype(np.float32)/255.
    shown=raster[:,:,:3].astype(np.float32)*alpha+255.*(1-alpha)
    color_error=float(np.mean(np.abs(src.astype(np.float32)-shown)[reference]))
    return round(color_error,4),verified


def _candidate_colored_regions(source,reference,old_svg,base_svg,info):
    """Recover up to ten large disconnected regions omitted by the old SVG.

    Average RGB is measured separately for each region, not a guessed global
    shade. No k-means RNG, no image embedding, no opacity/transform/external URL.
    """
    old_raster,_,_ = _render_svg(old_svg)
    h,w=old_raster.shape[:2]
    x0,y0,x1,y1=info['zone_sujet_originale']
    crop=np.asarray(source,dtype=np.uint8)[y0:y1,x0:x1,:3]
    interp=cv2.INTER_AREA if crop.shape[1]>w or crop.shape[0]>h else cv2.INTER_LINEAR
    crop=cv2.resize(crop,(w,h),interpolation=interp)
    actual=np.asarray(reference)[y0:y1,x0:x1]
    mask=cv2.resize(np.uint8(actual>=.5),(w,h),interpolation=cv2.INTER_NEAREST).astype(bool)
    missing=np.ascontiguousarray(mask & (old_raster[:,:,3]<128),dtype=np.uint8)
    count,labels,stats,_=cv2.connectedComponentsWithStats(missing,8)
    areas=sorted(((int(stats[j,cv2.CC_STAT_AREA]),j) for j in range(1,count)),reverse=True)
    chosen=[];shape_count=0;points_total=0
    min_area=max(_MIN_FRAGMENT,round(mask.sum()*.0004))
    for area,label in areas:
        if area<min_area or len(chosen)>=_MAX_ACCENTS:break
        component=np.ascontiguousarray(labels==label,dtype=np.uint8)
        paths,_=_rings(component)
        if not paths:continue
        points=sum(len(re.findall(r'-?\d+,-?\d+',path)) for path in paths)
        if shape_count+len(paths)>_MAX_ADDED_PATHS or points_total+points>_MAX_ADDED_POINTS:
            break
        rgb=np.mean(crop[component>0],axis=0).round().clip(0,255).astype(np.uint8)
        color='#'+''.join(f'{int(v):02x}' for v in rgb)
        chosen.append((color,paths,area));shape_count+=len(paths);points_total+=points
    if not chosen:return None,0,0
    # Only append after the full underlay, and before old palette layers.
    # The old palette remains in front, so existing color shapes are unaltered.
    index=base_svg.find(b'<g id="couleur_')
    if index<0:raise VectorizationRefused('SVG base de palette non conforme')
    added=''.join(
        f'<g id="reparation_couleur_{i:02d}" data-smartsvg-layer="color" fill="{color}" fill-rule="evenodd">'+
        ''.join(f'<path d="{d}"/>' for d in paths)+'</g>'
        for i,(color,paths,_) in enumerate(chosen,1)).encode('ascii')
    result=base_svg[:index]+added+base_svg[index:]
    if len(result)>MAX_BYTES:return None,0,0
    _,geometry=_strict_render(result)
    if geometry['formes_reconstruites']>MAX_PATHS or geometry['points_reconstruits']>MAX_POINTS:
        return None,0,0
    return result,shape_count,points_total


def _initial_svg_from_recovered(recovered,info):
    """Remove the 21.14 inserted layer without recalculating the k-means palette.

    This is bounded to exact, internally generated identifiers; unexpected
    output is refused rather than naively editing arbitrary user-supplied SVG.
    """
    if not info.get('sous_couche_silhouette_ajoutee'):
        return recovered
    begin=recovered.find(b'<g id="fond_silhouette_21_14"')
    end=recovered.find(b'<g id="couleur_')
    if begin<0 or end<=begin or recovered.count(b'<g id="fond_silhouette_21_14"')!=1:
        raise VectorizationRefused('Sous-couche originale du SVG introuvable')
    clean=recovered[:begin]+recovered[end:]
    _strict_render(clean)
    return clean


def vectorize_color_repaired(image,mask,*,colors=8,width_mm=40.,max_side=900):
    """True editable vector output with explicit fidelity/performance trade-offs."""
    base,preview,info,comparison,quality=vectorize_recovered(
        image,mask,colors=colors,width_mm=width_mm,max_side=max_side)
    original=_initial_svg_from_recovered(base,info)
    try:
        patch,number,new_points=_candidate_colored_regions(image,mask,original,base,info)
    except (ValueError,IndexError):
        # Do not paper over corrupt SVG; strict errors need to be observable.
        raise
    color_before,exact_base=_masked_full_color_mae(image,mask,base,info)
    new_svg=base
    accepted=False
    if patch is not None:
        picture,candidate_quality=analyse_svg(image,mask,patch,info)
        color_after,exact_candidate=_masked_full_color_mae(image,mask,patch,info)
        # Restrict to candidates that preserve silhouette and improve a color
        # metric. Tiny numerical renderer differences cannot trigger acceptance.
        if (candidate_quality['iou_silhouette_approx']+0.00005>=quality['iou_silhouette_approx']
            and color_after<=color_before-0.02
            and candidate_quality['erreur_moyenne_couleurs_sur_recouvrement']
                <=quality['erreur_moyenne_couleurs_sur_recouvrement']+0.05):
            new_svg=patch;comparison=picture;quality=candidate_quality;accepted=True
    color_final,exact_final=_masked_full_color_mae(image,mask,new_svg,info)
    # Redo cut-risk accounting only if an extra color group was actually kept.
    metrics=_cut_risk(new_svg,width_mm) if accepted else info['risques_decoupe']
    final_info={**info,'version':'21.14.1',
        'correction_couleur_ajoutee':accepted,
        'formes_ajoutees_pour_couleur':number if accepted else 0,
        'points_ajoutes_pour_couleur':new_points if accepted else 0,
        'formes':quality['formes_reconstruites'],
        'points':quality['points_reconstruits'],
        'calques_couleur':metrics['calques'],
        'risques_decoupe':metrics,
        'mae_rvb_sur_toute_silhouette_avant':color_before,
        'mae_rvb_sur_toute_silhouette_apres':color_final,
        'mesure_couleur_rendu_standard':bool(exact_final),
        'iou_silhouette_apres':quality['iou_silhouette_approx'],
        'erreur_couleur_apres':quality['erreur_moyenne_couleurs_sur_recouvrement'],
        'metrique_couleur_expliquee':'RGB moyen sur tous les pixels du sujet, fond blanc lorsque le SVG est transparent ; plus petit = meilleur.',
        'usage_svg_multicouche':'EXPERIMENTAL_FORMES_COLOREES_EDITABLES',
        'cricut_svg_multicouche_pret_a_decouper':False,
        'validation_dans_design_space':False,
        'validation_sur_cricut_physique':False}
    return new_svg,preview,final_info,comparison,quality
