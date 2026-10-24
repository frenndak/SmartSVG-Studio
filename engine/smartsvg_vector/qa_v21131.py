"""Auditable SVG vector geometry: render *generated* closed M/L/Z paths to pixels.

No external URLs, code or scripts are ever rendered. This internal renderer is
restricted to the known SVG dialect emitted by SmartSVG V21.13. It verifies
rather than assumes that a palette preview reflects paths exported to Inkscape.
"""
from __future__ import annotations
import math
import io
import re
import xml.etree.ElementTree as ET
import cv2
import numpy as np
from PIL import Image

class QualityRefused(ValueError):pass

PATH_RE=re.compile(r'^M\s+-?\d+,-?\d+(?:\s+L\s+-?\d+,-?\d+)+(?:\s+Z)(?:\s+M\s+-?\d+,-?\d+(?:\s+L\s+-?\d+,-?\d+)+(?:\s+Z))*$')
TOKEN_RE=re.compile(r'\b[M LZ]\b|(-?\d+),(-?\d+)')
MAX_QA_PIXELS=600_000
MAX_PATHS=1200
MAX_POINTS=110_000

def _strict_render(xml):
    if not isinstance(xml,bytes) or len(xml)>5_000_000 or b'<!DOCTYPE' in xml.upper() or b'<!ENTITY' in xml.upper():
        raise QualityRefused('SVG inattendu ou dangereux')
    try:root=ET.fromstring(xml)
    except ET.ParseError as exc:raise QualityRefused('SVG non analysable') from exc
    ns='{http://www.w3.org/2000/svg}'
    if root.tag!=ns+'svg':raise QualityRefused('SVG non pris en charge')
    if set(root.attrib)-{'viewBox','width','height','version'}:
        raise QualityRefused('Attribut SVG externe ou transformation inconnue')
    try:
        x,y,w,h=map(int,root.attrib['viewBox'].split())
        assert x==0 and y==0 and 1<=w and 1<=h and w*h<=MAX_QA_PIXELS
        assert re.fullmatch(r'\d+(?:\.\d+)?mm',root.attrib['width'])
        assert re.fullmatch(r'\d+(?:\.\d+)?mm',root.attrib['height'])
    except (AssertionError,ValueError,KeyError):raise QualityRefused('Dimensions du SVG invalides')
    rgba=np.zeros((h,w,4),np.uint8)
    forms=0;points=0;thin=0
    for element in root:
        if element.tag in (ns+'title',ns+'desc'):continue
        if element.tag!=ns+'g' or element.attrib.get('data-smartsvg-layer')!='color':
            raise QualityRefused('Calque SVG inconnu')
        if set(element.attrib)-{'id','data-smartsvg-layer','fill','fill-rule'}:
            raise QualityRefused('Transformation/calque inattendu')
        color=element.attrib.get('fill','')
        if not re.fullmatch(r'#[0-9a-fA-F]{6}',color):raise QualityRefused('Couleur invalide')
        rgb=tuple(int(color[i:i+2],16) for i in (1,3,5))
        if element.attrib.get('fill-rule')!='evenodd':raise QualityRefused('Règle de remplissage inconnue')
        for shape in element:
            if shape.tag!=ns+'path':raise QualityRefused('Contenu vectoriel inconnu')
            if set(shape.attrib)!={'d'}:raise QualityRefused('Attribut de chemin inattendu')
            d=shape.attrib.get('d','')
            if not PATH_RE.fullmatch(d):raise QualityRefused('Commande path non admise')
            # Interpret even-odd. Exterior and hole rings toggle, not overwrite
            # each other, so order is independent for generated CCOMP families.
            rings=re.findall(r'M\s+(-?\d+,-?\d+(?:\s+L\s+-?\d+,-?\d+)+)\s+Z',d)
            if not rings:raise QualityRefused('Path vide')
            binary=np.zeros((h,w),np.uint8)
            for ring in rings:
                coords=np.asarray([[int(v) for v in point.split(',')]
                    for point in re.findall(r'-?\d+,-?\d+',ring)],dtype=np.int32)
                if len(coords)<3 or len(coords)>MAX_POINTS:raise QualityRefused('Contour invalide')
                points+=len(coords)
                if points>MAX_POINTS:raise QualityRefused('Trop de points')
                bounds=np.max(np.abs(coords))
                if bounds>max(w,h)*2:raise QualityRefused('Coordonnées hors cadre')
                polygon=np.zeros((h,w),np.uint8)
                cv2.fillPoly(polygon,[coords],1)
                binary=cv2.bitwise_xor(binary,polygon)
                area=abs(float(cv2.contourArea(coords)))
                length=float(cv2.arcLength(coords,True))
                if length and 2*area/length < 1.5:thin+=1
            forms+=1
            if forms>MAX_PATHS:raise QualityRefused('Trop de formes')
            active=binary>0
            rgba[active,:3]=rgb
            rgba[active,3]=255
    if not forms:raise QualityRefused('Aucune forme vectorielle')
    return rgba,{'formes_reconstruites':forms,'points_reconstruits':points,
                 'formes_potentiellement_fines':thin}


def _standard_render(xml,w,h):
    """Optional real SVG 1.1 renderer; executed only after strict dialect validation."""
    try:
        import cairosvg
    except (ImportError,OSError):
        # On Windows, Python package may be present while native Cairo DLLs
        # are missing. This is an unavailable renderer, not a malformed SVG.
        return None
    try:
        png=cairosvg.svg2png(bytestring=xml,output_width=w,output_height=h,unsafe=False)
        # SVG was bounded to 600k pixels before requesting the render.
        image=np.asarray(Image.open(io.BytesIO(png)).convert('RGBA'),dtype=np.uint8)
        if image.shape!=(h,w,4):raise QualityRefused('Résolution SVG inattendue')
        return image
    except Exception as exc:
        raise QualityRefused('Rendu SVG standard impossible') from exc

def _compare(rgb,subject_mask,xml,audit):
    im=np.asarray(rgb)
    if im.ndim!=3 or im.shape[-1] not in (3,4) or im.dtype!=np.uint8:
        raise QualityRefused('Image originale RGB/RGBA uint8 requise')
    original=np.asarray(subject_mask)
    if original.ndim!=2 or original.shape!=im.shape[:2] or not np.isfinite(original).all():
        raise QualityRefused('Masque original absent ou non aligné')
    x0,y0,x1,y1=audit['zone_sujet_originale']
    reconstructed,geometry=_strict_render(xml)
    h,w=reconstructed.shape[:2]
    actual=_standard_render(xml,w,h)
    rendered=actual if actual is not None else reconstructed
    standard_renderer=actual is not None
    sub=im[y0:y1,x0:x1,:3]
    source=cv2.resize(sub,(w,h),interpolation=cv2.INTER_AREA if sub.shape[1]>w or sub.shape[0]>h else cv2.INTER_LINEAR)
    mask=cv2.resize(np.uint8(original[y0:y1,x0:x1]>=.5),(w,h),interpolation=cv2.INTER_NEAREST).astype(bool)
    vect=rendered[:,:,3]>=128
    union=int(np.count_nonzero(mask|vect));intersection=int(np.count_nonzero(mask&vect))
    iou=intersection/union if union else 0.
    rgbdelta=np.abs(source.astype(np.int16)-rendered[:,:,:3].astype(np.int16))
    color_mae=float(np.mean(rgbdelta[mask&vect])) if intersection else 255.
    missing=int(np.count_nonzero(mask&~vect));extra=int(np.count_nonzero(vect&~mask))
    # At physical width, raster samples convert to approximate sizes. These are
    # warnings, not blade-physics predictions or cut certification.
    width_mm=float(audit['largeur_mm']);mm_per_pixel=width_mm/w
    minimum_radius_mm=.45
    dist=cv2.distanceTransform(np.uint8(vect),cv2.DIST_L2,3)
    narrow=np.uint8((dist>0)&(dist*mm_per_pixel<minimum_radius_mm))
    contours,_=cv2.findContours(narrow,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    significant_narrow=sum(cv2.contourArea(c)>=1 for c in contours)
    # Source | SVG reconstructed | differences, with consistent framing.
    orig_white=np.full((h,w,3),255,np.uint8);orig_white[mask]=source[mask]
    svg_white=np.full((h,w,3),255,np.uint8);svg_white[vect]=rendered[vect,:3]
    heat=np.full((h,w,3),255,np.uint8)
    error=np.mean(rgbdelta.astype(np.float32),axis=2)
    both=mask&vect
    # Purple: vector changed colour, red: dropped, blue: leaked outside mask.
    heat[both]=np.uint8(np.clip(255-error[both,None]*1.5,0,255))
    heat[mask&~vect]=[233,60,65]
    heat[vect&~mask]=[52,125,228]
    heat[both&(error>45)]=[171,94,190]
    separator=np.full((h,4,3),[135,145,155],np.uint8)
    strip=np.concatenate((orig_white,separator,svg_white,separator,heat),axis=1)
    report={'version':'21.13.2','iou_silhouette_approx':round(iou,5),
      'erreur_moyenne_couleurs_sur_recouvrement':round(color_mae,2),
      'pixels_sujet_manquants':missing,'pixels_supplémentaires':extra,
      'surface_sujet_reference_px':int(mask.sum()),'surface_svg_px':int(vect.sum()),
      'zones_fines_a_verifier':int(significant_narrow),
      'seuil_epaisseur_illustratif_mm':minimum_radius_mm*2,
      'resolution_verification_px':[w,h],
      'aperçu':'source / SVG reconstruit / différences (rouge=manquant, bleu=excès, violet=écart couleur)',
      'rendu_svg_reconstruit_par':'CairoSVG (SVG 1.1)' if standard_renderer else 'OpenCV M/L/Z (estimation)',
      'rendu_standard_verifie':bool(standard_renderer),
      'mesure_limitee_si_pas_de_rendu_standard':not standard_renderer,
      'aucune_garantie_decoupe_physique':True,'a_verifier_visuellement':True,
      'diagnostic':'A_VERIFIER' if (not standard_renderer or iou<.98 or color_mae>35 or missing>0) else 'PRECONTROLE_VISUEL_LOCAL'}
    report.update(geometry)
    return strip,report

def analyse_svg(image,mask,svg,audit):
    return _compare(image,mask,svg,audit)
