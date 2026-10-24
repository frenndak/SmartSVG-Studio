"""SmartSVG V20.1.2: explicit Cricut operations, no silent equivalence of ink paths and outer contour.

Additive companion to V20.1.1's line-art pipeline. No model is invoked. This
module exports options side by side so users cannot accidentally interpret an
ink SVG as a sticker cut contour.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import tempfile
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image

from .lineart_v201 import LineArtError, process_lineart

OPTIONS = ('imprimer_decouper_contour', 'decouper_contour_seul',
           'decouper_tous_les_traits', 'dessiner_au_stylo', 'tout_preparer')


def _validate_mask(a):
    a = np.asarray(a)
    if a.ndim != 2 or a.dtype != np.uint8 or min(a.shape)<48 or a.size>12_000_000:
        raise LineArtError('Masque noir/blanc uint8 invalide pour operation Cricut')
    return a > 127


def _svg_header(w, h, physical_width_mm):
    height_mm = float(physical_width_mm) * h / w
    return (f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{physical_width_mm:.3f}mm" height="{height_mm:.3f}mm" '
            f'viewBox="0 0 {w} {h}">')


def svg_cut_ink_regions(ink, width_mm=90.):
    """Basic Cut: around both SIDES of dark strokes, not their medial axes."""
    b = _validate_mask(ink)
    h,w = b.shape
    contours, _ = cv2.findContours((b.astype(np.uint8)*255),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    paths = []
    for c in contours:
        if len(c)<3 or cv2.contourArea(c)<2: continue
        poly = cv2.approxPolyDP(c, .55, True)[:,0]
        if len(poly) < 3: continue
        paths.append('M ' + ' L '.join(f'{int(x)} {int(y)}' for x,y in poly) + ' Z')
    # Fill rule retains holes; no stroke avoids double paths around the same region.
    path_str = ' '.join(paths)
    svg = (_svg_header(w,h,width_mm) +
           f'<path fill="#000000" fill-rule="evenodd" d="{path_str}"/></svg>')
    return svg, len(paths)


def _skeletonize(binary):
    """OpenCV-only morphological skeleton; avoids new ComfyUI dependencies."""
    b=np.uint8(binary)*255
    skel=np.zeros_like(b)
    element=cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    for _ in range(512):
        if not np.any(b): break
        opened=cv2.morphologyEx(b,cv2.MORPH_OPEN,element)
        skel |= cv2.subtract(b,opened)
        b=cv2.erode(b,element)
    else:
        raise LineArtError('Trace au stylo trop epaisse pour squelette borne')
    return skel>0


def _trace_skeleton(skeleton):
    ys,xs=np.nonzero(skeleton)
    pixels={(int(y),int(x)) for y,x in zip(ys,xs)}
    if len(pixels)>250_000:
        raise LineArtError('Trop de pixels de stylo; nettoyez le dessin')
    steps=((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
    def neigh(pt):
        y,x=pt
        return [(y+dy,x+dx) for dy,dx in steps if (y+dy,x+dx) in pixels]
    nbr={p:neigh(p) for p in pixels}
    visited=set()
    lines=[]
    def edge(p,q):return (p,q) if p<q else (q,p)
    def walk(p,q):
        chain=[p,q]
        visited.add(edge(p,q))
        prev, cur = p,q
        while len(nbr[cur])==2:
            successors=[x for x in nbr[cur] if x!=prev and edge(cur,x) not in visited]
            if not successors:break
            nxt=successors[0]
            chain.append(nxt)
            visited.add(edge(cur,nxt))
            prev,cur=cur,nxt
            if cur==p: break
        return chain
    # Branch/end points first; remaining edges are closed cycles.
    for p in sorted(pixels):
        if len(nbr[p])!=2:
            if len(nbr[p])==0:lines.append([p]);continue
            for q in nbr[p]:
                if edge(p,q) not in visited: lines.append(walk(p,q))
    for p in sorted(pixels):
        for q in nbr[p]:
            if edge(p,q) not in visited: lines.append(walk(p,q))
    if len(lines)>12000:
        raise LineArtError('Trop de fragments pour un trace au stylo fiable')
    return lines


def svg_draw_centerlines(ink, width_mm=90.):
    b=_validate_mask(ink)
    h,w=b.shape
    lines=_trace_skeleton(_skeletonize(b))
    paths=[]
    for line in lines:
        points=np.asarray([(x,y) for y,x in line],dtype=np.int32).reshape(-1,1,2)
        if len(points)>=3:
            points=cv2.approxPolyDP(points,.72,False)[:,0]
        else:points=points[:,0]
        if len(points)==1:
            # Single dot: short stroke for the pen instead of an invalid empty path.
            x,y=points[0]; d=f'M {x} {y} l .1 0'
        else:
            d='M '+' L '.join(f'{int(x)} {int(y)}' for x,y in points)
        paths.append(d)
    svg=(_svg_header(w,h,width_mm)+'<g fill="none" stroke="#000000" '
         'stroke-width="0.8" stroke-linejoin="round" stroke-linecap="round">'+
         ''.join('<path d="'+d+'"/>' for d in paths)+'</g></svg>')
    return svg, len(paths)


def _rescale_svg(svg_file, output_file, width_mm):
    root=ET.parse(svg_file).getroot()
    view=root.get('viewBox')
    if not view:raise LineArtError('SVG contour sans viewBox')
    try:
        _,_,w,h=map(float,view.split())
    except Exception as exc:raise LineArtError('ViewBox SVG incorrect') from exc
    if w<=0 or h<=0:raise LineArtError('Dimensions SVG incorrectes')
    root.set('width',f'{width_mm:.3f}mm')
    root.set('height',f'{(width_mm*h/w):.3f}mm')
    ET.ElementTree(root).write(output_file,encoding='utf-8',xml_declaration=True)


def process_choice(rgb, output_dir, *, source='auto', mode='doux', target='sticker',
                   rectify=True, white_margin_px=10, operation='imprimer_decouper_contour',
                   width_mm=90):
    if operation not in OPTIONS:raise LineArtError('Operation Cricut non reconnue')
    if not isinstance(width_mm,(int,float)) or not np.isfinite(width_mm) or not (20<=width_mm<=280):
        raise LineArtError('Largeur cible: entre 20 et 280 mm')
    result=process_lineart(rgb,output_dir,source=source,mode=mode,target=target,
                           rectify=rectify,white_margin_px=white_margin_px)
    root=Path(result['root'])
    ink=np.asarray(Image.open(root/'04_LINEART'/'traits_fins.png').convert('L'))
    img_png=Path(result['image'])
    # Build the entire supplementary folder and commit atomically.
    tmp=Path(tempfile.mkdtemp(prefix='.preparation_cricut_',dir=str(root)))
    final=root/'08_CHOIX_CRICUT'
    try:
        # Independent, explicitly named deliverables. Do not import ALL these layers
        # together into a Cricut project unless deliberately combining operations.
        names={
           'imprimer_decouper_contour':'01_IMPRIMER_PUIS_DECOUPER_UNIQUEMENT_CONTOUR.png',
           'decouper_contour_seul':'02_DECOUPER_SEULEMENT_CONTOUR_EXTERIEUR.svg',
           'decouper_tous_les_traits':'03_DECOUPER_CHAQUE_TRAIT.svg',
           'dessiner_au_stylo':'04_DESSINER_LES_TRAITS_STYLO.svg',
        }
        shutil.copyfile(img_png,tmp/names['imprimer_decouper_contour'])
        # SVG viewbox of outer contour contains the padding (if sticker), while
        # requested width_mm refers to the unpadded illustration source width.
        with Image.open(root/'02_ZONE_UTILE'/'carte_redressee.png') as original:
            original_width=original.width
        with Image.open(img_png) as sticker:
            output_width=sticker.width
        outer_mm=round(float(width_mm)*output_width/original_width,3)
        _rescale_svg(root/'06_SVG'/'contour_selectionne.svg',
                     tmp/names['decouper_contour_seul'],outer_mm)
        cut_svg,cut_paths=svg_cut_ink_regions(ink,float(width_mm))
        (tmp/names['decouper_tous_les_traits']).write_text(cut_svg,encoding='utf8')
        pen_paths=0
        pen_error=None
        try:
            pen_svg,pen_paths=svg_draw_centerlines(ink,float(width_mm))
        except LineArtError as exc:
            pen_error=str(exc)
            if operation=='dessiner_au_stylo':
                raise LineArtError('Mode stylo indisponible sur ce dessin trop complexe : '+pen_error) from exc
        else:
            (tmp/names['dessiner_au_stylo']).write_text(pen_svg,encoding='utf8')
        if pen_error:
            del names['dessiner_au_stylo']
        # Warn if no ink exists instead of implying a meaningful result.
        has_ink=bool(np.any(ink>127))
        warnings=[]
        if not has_ink:warnings.append('AUCUN_TRAIT_DETECTE')
        if pen_error:warnings.append('TRACES_STYLO_INDISPONIBLES_IMAGE_TROP_COMPLEXE')
        if result['report']['decoupe_generee']!='CARTE_GEOMETRIQUE':
            warnings.append('CONTOUR_PERSONNAGE_BROUILLON_NON_VALIDE')
        if result['report']['decoupe_generee']=='REPLI_CARTE_SUJET_INDETERMINE':
            warnings.append('SUJET_NON_DETECTE_LE_CONTOUR_EST_CELUI_DE_LA_CARTE')
        if cut_paths>150:
            warnings.append('TROP_DE_PETITS_TRAITS_ATTENTION_TEMPS_DE_DECOUPE_ET_DECHIRURES')
        if pen_paths>1500:
            warnings.append('TROP_DE_PETITES_LIGNES_STYLO_RESULTAT_A_CONTROLER')
        advice=(
            'SmartSVG V20.1.2 - IMPORTATION DANS CRICUT DESIGN SPACE\n'
            '\n'
            '1. STICKER / IMPRIMER PUIS DECOUPER : importer 01_*.png en '
            'Imprimer puis decouper. La machine decoupe le bord exterieur de '
            'la zone opaque (interieur du personnage imprime, NON decoupe).\n'
            '2. UNIQUEMENT LA SILHOUETTE : importer 02_*.svg et choisir '
            'Decoupe de base. Aucun trait interne n y est present.\n'
            '3. TOUTES LES LIGNES DECOUPEES : importer 03_*.svg en Decoupe '
            'de base. Chaque zone noire possede un contour, pouvant produire '
            'DEUX bords de coupe pour un trait epais. Risque de petites pieces.\n'
            '4. STYLO (si disponible) : importer 04_*.svg, choisir Dessiner / Stylo, '
            'puis utiliser Attacher si combine avec une couche de decoupe.\n'
            'Ne jamais superposer automatiquement les SVG de coupe avec le PNG '
            'Print Then Cut : ce serait provoquer des coupes interieures.\n'
            'Dimension : largeur du dessin original %s mm (les SVG ont la taille physique). '
            'Dans Design Space, ajuster manuellement la taille du PNG si necessaire.\n'
            'ATTENTION : la silhouette du personnage reste un BROUILLON geomtrique, '
            'pas un masque IA valide ; inspecter avant de lancer la machine.\n' % width_mm
        )
        (tmp/'A_LIRE_AVANT_CRICUT.txt').write_text(advice,encoding='utf8')
        chosen='imprimer_decouper_contour' if operation=='tout_preparer' else operation
        report={
            'version':'20.1.2-alpha','operation_choisie':operation,
            'fichier_recommande': names[chosen],
            'exports_disponibles':names,
            'largeur_dessin_mm':float(width_mm),'largeur_silhouette_avec_marge_mm':outer_mm,
            'svg_coupe_traces':cut_paths,'svg_stylo_lignes':pen_paths,
            'stylo_erreur':pen_error,
            'operation_design_space':{
                'imprimer_decouper_contour':'Imprimer puis decouper',
                'decouper_contour_seul':'Decoupe de base',
                'decouper_tous_les_traits':'Decoupe de base',
                'dessiner_au_stylo':'Dessiner / Stylo'},
            'pret_decoupe_personnage':False,
            'segmentation_ia_executee':False,
            'operations_non_equivalentes':True,
            'avertissements':warnings,
            'usage':'Un seul mode par import pour eviter une double decoupe accidentelle',
        }
        (tmp/'CHOIX_CRICUT_V20_1_2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
        os.replace(tmp,final)
    except BaseException:
        shutil.rmtree(tmp,ignore_errors=True)
        raise
    return {**result,'cricut_root':str(final),'choice_report':report,
            'recommended_file':str(final/names[chosen])}
