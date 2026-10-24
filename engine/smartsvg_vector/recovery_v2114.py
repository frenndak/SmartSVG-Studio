"""V21.14 experimental SVG color-underlay repair and geometric cut-risk audit.

Legacy vectorization is called unmodified. A bounded, editable color layer is
inserted underneath the existing color paths to recover the original subject
silhouette. No raster images or hidden cuts are embedded in the SVG. This
improves silhouette IoU but cannot recover missing internal color detail.
"""
from __future__ import annotations
import re
import xml.etree.ElementTree as ET
import cv2
import numpy as np
from .layers_v2113 import vectorize_flat_art,VectorizationRefused,MAX_PATHS,MAX_POINTS,MAX_BYTES
from .qa_v21131 import _strict_render,_standard_render,analyse_svg,QualityRefused

NAMESPACE='{http://www.w3.org/2000/svg}'
_COLOR=re.compile(r'^#[0-9a-fA-F]{6}$')

def _rings(binary):
    contours,hierarchy=cv2.findContours(np.ascontiguousarray(binary,dtype=np.uint8),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
    if hierarchy is None:return [],0
    H=hierarchy[0];items=[];skipped=0
    for i,outer in enumerate(contours):
        if H[i][3]!=-1:continue
        if cv2.contourArea(outer)<3:
            skipped+=1;continue
        pieces=[outer]
        sub=int(H[i][2])
        while sub>=0:
            if cv2.contourArea(contours[sub])>=3:pieces.append(contours[sub])
            else:skipped+=1
            sub=int(H[sub][0])
        ds=[]
        for c in pieces:
            coords=cv2.approxPolyDP(c,.12,True).reshape(-1,2)
            if len(coords)<3:continue
            ds.append('M '+' L '.join(f'{int(x)},{int(y)}' for x,y in coords)+' Z')
        if ds:items.append(' '.join(ds))
    return items,skipped

def _underlay_color(svg, cropped_rgb, reference_mask):
    """Select from existing palette by the color error on the missing area.

    On Windows without native Cairo DLLs, fall back to the conservative OpenCV
    internal rasterizer, and explicitly report that the choice is approximate.
    """
    old,_=_strict_render(svg)
    h,w=old.shape[:2]
    standard=_standard_render(svg,w,h)
    displayed=standard if standard is not None else old
    hole=reference_mask & (displayed[:,:,3]<128)
    src=np.asarray(cropped_rgb,dtype=np.uint8)
    palette=[]
    parsed=ET.fromstring(svg)
    for group in parsed.findall(NAMESPACE+'g'):
        fill=group.attrib.get('fill','')
        if _COLOR.fullmatch(fill):palette.append(fill)
    if not palette:raise VectorizationRefused('Palette du SVG manquante')
    if not hole.any():
        # No content missing; adding an underlay is unnecessary.
        return None,0.,bool(standard is not None)
    pixels=src[hole].astype(np.int16)
    # Subsample deterministically to bound work even at maximum image size.
    samples=pixels[::max(1,len(pixels)//30000)]
    errors=[]
    for color in palette:
        c=np.array([int(color[i:i+2],16) for i in (1,3,5)],dtype=np.int16)
        errors.append(float(np.mean(np.abs(samples-c))))
    ix=int(np.argmin(errors))
    return palette[ix],errors[ix],bool(standard is not None)

def _cut_risk(svg,width_mm,*,minimum_detail_mm=.8):
    """Illustrative physical scale, NOT Cricut cut certification."""
    root=ET.fromstring(svg)
    w=int(root.attrib['viewBox'].split()[2])
    mm_per_px=float(width_mm)/w
    total=0;narrow=0;small=0;min_width=None;groups=0
    for group in root.findall(NAMESPACE+'g'):
        groups+=1
        for el in group.findall(NAMESPACE+'path'):
            d=el.attrib['d']
            # Dialect already validated by _strict_render (closed M/L/Z).
            rings=re.findall(r'M\s+(-?\d+,-?\d+(?:\s+L\s+-?\d+,-?\d+)+)\s+Z',d)
            for ring in rings:
                coords=np.asarray([[int(q) for q in val.split(',')]
                                   for val in re.findall(r'-?\d+,-?\d+',ring)],dtype=np.int32)
                if len(coords)<3:continue
                area=abs(float(cv2.contourArea(coords)))
                perimeter=float(cv2.arcLength(coords,True))
                approximate_width=2*area/perimeter*mm_per_px if perimeter>0 else 0.
                if min_width is None or approximate_width<min_width:min_width=approximate_width
                if approximate_width<minimum_detail_mm:narrow+=1
                if area*(mm_per_px**2)<1.:small+=1
                total+=1
    return {'version':'21.14','calques':groups,'anneaux_contours':total,
            'anneaux_fins_a_verifier':narrow,'formes_surface_inf_1mm2_a_verifier':small,
            'largeur_equivalente_min_mm':round(min_width or 0.,4),
            'seuil_indicatif_detail_mm':minimum_detail_mm,
            'chaque_forme_peut_devenir_une_decoupe':True,
            'certification_decoupe_cricut':False,
            'recommandation':'Pour imprimer un autocollant, utiliser le PNG aplati Print Then Cut, pas le SVG multicouche.'}

def vectorize_recovered(image, mask, *, colors=8,width_mm=40.,max_side=900):
    """Vectorize then overlay original silhouette underneath the palette layers.

    Returns (svg bytes, preview RGB, audit, comparison RGB). This version may
    add one editable color underlay; it never modifies the original PNG source.
    """
    original,preview,info=vectorize_flat_art(image,mask,colors=colors,width_mm=width_mm,max_side=max_side)
    rgb=np.asarray(image,dtype=np.uint8)[:,:,:3]
    reference=np.asarray(mask)
    if reference.ndim!=2 or reference.shape!=rgb.shape[:2]:raise VectorizationRefused('Masque non aligné')
    x0,y0,x1,y1=info['zone_sujet_originale']
    w,h=info['taille_travail']
    local=cv2.resize(np.uint8(reference[y0:y1,x0:x1]>=.5),(w,h),interpolation=cv2.INTER_NEAREST)
    sample=rgb[y0:y1,x0:x1]
    rgb_crop=cv2.resize(sample,(w,h),interpolation=cv2.INTER_AREA if max(sample.shape[:2])>max(h,w) else cv2.INTER_LINEAR)
    underlay_color,estimated_error,exact_palette=_underlay_color(original,rgb_crop,local.astype(bool))
    contours,skipped=_rings(local)
    if not contours or len(contours)>100 or len(contours)+info['formes']>MAX_PATHS:
        raise VectorizationRefused('Masque avec trop de fragments pour un SVG multicouche fiable')
    extra_points=sum(len(re.findall(r'-?\d+,-?\d+',d)) for d in contours)
    if extra_points+info['points']>MAX_POINTS:raise VectorizationRefused('Trop de points vectoriels')
    if underlay_color:
        # All attributes are from hard-coded safe values or an internally
        # generated palette. This does not embed external files or URLs.
        base=(' <g id="fond_silhouette_21_14" data-smartsvg-layer="color" '
              f'fill="{underlay_color}" fill-rule="evenodd">'+
              ''.join('<path d="'+d+'"/>' for d in contours)+'</g>')
        spot=original.find(b'<g id="couleur_')
        if spot<0:raise VectorizationRefused('SVG de palette non conforme')
        candidate=original[:spot]+base.encode('ascii')+original[spot:]
    else:candidate=original
    if len(candidate)>MAX_BYTES:raise VectorizationRefused('SVG trop volumineux')
    # Mandatory strict dialect validation before standard rendering.
    _strict_render(candidate)
    comparison,qa=analyse_svg(image,mask,candidate,info)
    original_qa=analyse_svg(image,mask,original,info)[1]
    new_iou=qa['iou_silhouette_approx'];old_iou=original_qa['iou_silhouette_approx']
    if underlay_color and new_iou<old_iou-.001:
        # Never regress geometric fidelity for the sake of an extra layer.
        candidate=original;comparison,qa=analyse_svg(image,mask,original,info)
        underlay_color=None
    info={**info,'version':'21.14','formes':info['formes']+(len(contours) if underlay_color else 0),
          'points':info['points']+(extra_points if underlay_color else 0),
          'calques_couleur':info['calques_couleur']+(1 if underlay_color else 0),
          'sous_couche_silhouette_ajoutee':bool(underlay_color),
          'couleur_sous_couche':underlay_color,
          'estimation_erreur_couleur_sous_couche':round(estimated_error,2),
          'couleur_choisie_par_rendu_svg_standard':exact_palette,
          'micro_contours_masque_omis':skipped,
          'fidelite_silhouette_avant':old_iou,
          'fidelite_silhouette_apres':qa['iou_silhouette_approx'],
          'erreur_couleur_avant':original_qa['erreur_moyenne_couleurs_sur_recouvrement'],
          'erreur_couleur_apres':qa['erreur_moyenne_couleurs_sur_recouvrement'],
          'indication':'La sous-couche récupère la silhouette, pas les détails ni les couleurs perdus.',
          'qualite_visuelle_certifiee':False,
          'cricut_svg_multicouche_pret_a_decouper':False}
    info['risques_decoupe']=_cut_risk(candidate,width_mm)
    return candidate,preview,info,comparison,qa
