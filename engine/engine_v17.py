"""SmartSVG Studio V17: audited Cricut preflight, numbered inspection proof,
physical-size checks, and atomic delivery on the V16 production engine.

Deliberate scope: printer/cutter QA, not semantic vectorization, and never
claims to predict Cricut registration/sensor behavior or printer calibration.
"""
from __future__ import annotations
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .engine_v11 import UnsafeCut
from .engine_v12 import _json_default
from .engine_v14 import NAME, CRICUT_SVG
from .engine_v15 import REGION_SVG
from .engine_v16 import process_v16, _fingerprint_folder, KIT

VERSION = '17.0-beta'
READY = 'PRET_V17.json'
PROOF = 'CONTROLE_VISUEL_NUMEROTE.png'
REPORT = 'rapport_V17.json'


def _min_gap_px(labels: np.ndarray, component: int) -> float | None:
    """Approximate nearest other sticker in raster pixels (8-connectivity elsewhere).

    OpenCV L2 distanceTransform is finite-precision raster approximation; never
    use this as a micron-level physical guarantee.
    """
    mask = (labels > 0) & (labels != component)
    if not bool(mask.any()):
        return None
    inv = (~mask).astype('uint8')
    dt = cv2.distanceTransform(inv, cv2.DIST_L2, 5)
    local = dt[labels == component]
    return float(local.min()) if local.size else None


def _largest_holes(mask: np.ndarray) -> int:
    """Number of interior transparent connected components (not exterior)."""
    inv=(~mask).astype('uint8')
    n,_,stats,_=cv2.connectedComponentsWithStats(inv, 8)
    h,w=mask.shape
    return sum(1 for i in range(1,n)
               if stats[i,0]>0 and stats[i,1]>0 and
               stats[i,0]+stats[i,2]<w and stats[i,1]+stats[i,3]<h and stats[i,4]>4)


def _sticker_geometry(sheet: np.ndarray, width_mm: float, expected: int, sticker_map=None):
    h,w=sheet.shape[:2]
    if sheet.ndim!=3 or sheet.shape[2]!=4:
        raise UnsafeCut('Controle V17: PNG non RGBA')
    mask=(sheet[:,:,3]>127)
    if not mask.any():raise UnsafeCut('Controle V17: planche transparente vide')
    n, labels, stats, centroids=cv2.connectedComponentsWithStats(mask.astype('uint8'), 8)
    count=n-1
    if count!=expected:
        raise UnsafeCut(f'Controle V17 : {count} composantes opaques, attendu {expected}')
    mm_px=width_mm/w
    if sticker_map is not None:
        if set(sticker_map)!=set(range(1,n)) or set(sticker_map.values())!=set(range(1,n)):
            raise UnsafeCut('Controle V17: appariement numero/composante non bijectif')
    result=[]
    all_gaps=[]
    risks=[]
    for comp in range(1,n):
        x,y,bw,bh,area=map(int,stats[comp,:5])
        crop=(labels[y:y+bh,x:x+bw]==comp).astype('uint8')
        contours,_=cv2.findContours(crop,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        perimeter=sum(cv2.arcLength(c,True) for c in contours)
        # About a 1.2mm-diameter opening: removes unstable thin protrusions.
        # This is indicative only; paper, pressure, blade, and material vary.
        diameter=int(round(1.2/mm_px))
        diameter=max(3,min(31,diameter|1))
        kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(diameter,diameter))
        opened=cv2.morphologyEx(crop,cv2.MORPH_OPEN,kernel)
        thin_fraction=100.0*float(np.count_nonzero((crop>0)&(opened==0)))/area
        gap_px=_min_gap_px(labels,comp)
        gap_mm=None if gap_px is None else float(gap_px*mm_px)
        if gap_mm is not None:all_gaps.append(gap_mm)
        bbox=[round(bw*mm_px,2),round(bh*mm_px,2)]
        notices=[]
        if min(bbox)<5:notices.append('Motif tres petit : dimensions sous 5 mm')
        if thin_fraction>4.0:notices.append('Details fins detectes : risque avec certains papiers/lames')
        if gap_mm is not None and gap_mm<2.0:notices.append('Espace entre stickers inferieur a 2 mm')
        if x<=1 or y<=1 or x+bw>=w-1 or y+bh>=h-1:
            raise UnsafeCut(f'Sticker {comp} touche le bord de la planche')
        item={'sticker':sticker_map[comp] if sticker_map is not None else comp,
              'composante_raster':comp,
              'centre_px':[round(float(centroids[comp,0]),1),round(float(centroids[comp,1]),1)],
              'dimensions_motif_mm':bbox,'surface_opaque_mm2':round(area*mm_px**2,2),
              'perimetre_approximatif_mm':round(perimeter*mm_px,2),
              'distance_plus_proche_autre_sticker_mm':None if gap_mm is None else round(gap_mm,2),
              'part_details_fins_heuristique_pct':round(thin_fraction,2),
              'ouverture_morphologique_test_mm':round(diameter*mm_px,2),
              'trous_transparents_internes':_largest_holes(crop>0),
              'risques':notices,
              'bbox_pixels':[x,y,bw,bh]}
        result.append(item)
        risks.extend([f'Sticker raster {comp}: {s}' for s in notices])
    result.sort(key=lambda d:d['sticker'])
    return {'nombre_stickers':expected,
            'duree_de_decoupe':'non mesuree',
            'pixel_en_mm':round(mm_px,6),
            'distance_minimale_mm':None if not all_gaps else round(min(all_gaps),2),
            'stickers':result,
            'alertes':risks,
            'precision_distances':'approximation sur masque raster; pas une mesure mecanique'}


def _proof(sheet: np.ndarray, metrics: dict, target: Path):
    """Proof only; never used for actual printing/cutting."""
    h,w=sheet.shape[:2]
    arr=np.zeros((h,w,3),dtype=np.uint8)
    arr[:]=[238,240,243]
    opaque=sheet[:,:,3:4].astype(np.float32)/255.0
    arr=np.uint8(sheet[:,:,:3]*opaque+arr*(1-opaque))
    result=Image.fromarray(arr,'RGB')
    draw=ImageDraw.Draw(result)
    thickness=max(2,round(w/800))
    for m in metrics['stickers']:
        index=m['sticker']
        x,y,bw,bh=m['bbox_pixels']
        draw.rectangle((x,y,x+bw,y+bh),outline=(228,89,34),width=thickness)
        label=f'{index:02d}  {m["dimensions_motif_mm"][0]:g}x{m["dimensions_motif_mm"][1]:g}mm'
        approx=max(15,round(w/85))
        # Prefer packaged system fonts, otherwise PIL default; avoids font files in release.
        try:font=ImageFont.truetype('DejaVuSans.ttf',approx)
        except OSError:font=ImageFont.load_default()
        rect=draw.textbbox((0,0),label,font=font)
        lw=rect[2]-rect[0]+12
        lh=rect[3]-rect[1]+12
        # Keep labels inside their own sticker bounding rectangle so labels
        # never appear beside the NEXT row (a subtle real-sheet QA bug).
        ty=max(0,min(h-lh,y+bh-lh-2))
        tx=max(0,min(w-lw,x+2))
        draw.rectangle((tx,ty,tx+lw,ty+lh),fill=(20,36,51))
        draw.text((tx+6,ty+5),label,fill=(255,255,255),font=font)
    result.save(target,format='PNG',optimize=True)
    return result


def _cricut_guide(qa: dict):
    w,h=qa['dimensions_mm'];dpi=qa['effective_dpi'];count=qa['nombre_stickers']
    return f'''SMARTSVG STUDIO V17 — GUIDE EXPRESS CRICUT

POUR IMPRIMER SANS RETOUCHER LE DESSIN :
  1. Ouvrir KIT_IMPORT_CRICUT/01_IMPRIMER_PUIS_DECOUPER.png.
  2. Televerser ce PNG en Image plate / Flat Graphic.
  3. Mettre la taille a {w:.1f} x {h:.1f} mm si Design Space ne la conserve pas.
  4. Controle : voir {count} silhouettes exterieures, jamais un rectangle unique.
  5. Utiliser Imprimer puis decouper DANS Design Space, meme session.
  6. Calibrer la machine si la coupe est decalee.

POUR MODIFIER LES COULEURS ET LES REGIONS :
  - 02_MODIFIER_COULEURS.svg : moins de calques, changement de couleurs rapide.
  - 03_MODIFIER_REGIONS.svg : zones vectorielles plus independantes, complexe.
  - Dissocier seulement le dessin voulu, modifier, puis APLATIR avant impression.
  - Verifier de nouveau les silhouettes apres les modifications.

PRE-CONTROLE V17 :
  - Dimensions de planche : {w:.1f} x {h:.1f} mm.
  - Densite effective des pixels : {dpi:.0f} DPI (origine).
  - Ecart minimum entre motifs (approx.) : {qa['geometrie']['distance_minimale_mm']} mm.
  - {len(qa['alertes'])} alerte(s) de precontrole non bloquantes.
  - Voir CONTROLE_VISUEL_NUMEROTE.png et rapport_V17.json.

IMPORTANT :
  - L'A4 ne garantit pas que la planche rentre dans la zone Print Then Cut !
    La zone varie suivant machine, papier ET geometrie, a verifier dans Design Space.
  - Ne pas importer le SVG des contours par-dessus le PNG (double decoupe).
  - Les metadonnees DPI ne creent aucun detail d'impression supplementaire.
  - Ne pas imprimer la planche en dehors du flux Design Space.
  - Les SVG ne reconnaissent pas encore semantiquement les yeux/corps/coquilles.
  - Le Controle V17 ne remplace pas un vrai test de lame et de papier.

AIDE OFFICIELLE :
  https://help.cricut.com/hc/fr/articles/360009387274
  https://help.cricut.com/hc/fr/articles/360009429814
'''


def process_v17(rgb,output_dir,*,layout='auto',intent='auto',ia_mode='auto',ai_masker=None,
                alpha=None,sheet_width_mm=180,margin_mm=1.5,editable_colors=10,runtime_rmbg_stats=None):
    base=Path(output_dir).expanduser();base.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.SmartSVG_V17_TEMP_',dir=base))
    try:
        old_report, preview=process_v16(rgb,str(stage),layout=layout,intent=intent,
            ia_mode=ia_mode,ai_masker=ai_masker,alpha=alpha,
            sheet_width_mm=sheet_width_mm,margin_mm=margin_mm,
            editable_colors=editable_colors,runtime_rmbg_stats=runtime_rmbg_stats)
        work=Path(old_report['output'])
        if not work.is_dir() or work.parent !=stage:
            raise UnsafeCut('V17 : sortie precedente dans un repertoire inattendu')
        with Image.open(work/NAME) as im: sheet=np.asarray(im.convert('RGBA'))
        o=old_report['audit_v16']
        component_map={int(item['composante']):int(item['sticker'])
                       for item in o['png_individuels']}
        if len(component_map)!=int(o['nombre_stickers']):
            raise UnsafeCut('V17: fichiers individuels manquants ou doublons')
        geometry=_sticker_geometry(sheet,float(o['largeur_planche_mm']),
                                   int(o['nombre_stickers']),sticker_map=component_map)
        sheet_h_mm=float(o['hauteur_planche_mm'])
        qa={'version':VERSION,'nombre_stickers':geometry['nombre_stickers'],
            'dimensions_mm':[float(o['largeur_planche_mm']),sheet_h_mm],
            'effective_dpi':float(o['densite_pixels_effective_dpi']),
            'geometrie':geometry,'alertes':list(geometry['alertes']),
            'export_format':'PNG plat pour impression / SVG pour edition',
            'type_de_calques':'groupes par stickers et regions de couleur, pas semantique',
            'ai_mode_demande':ia_mode,
            'ai_resultat':old_report['audit_v141']['ia'].get('etat','inconnu'),
            'verification_gpu_physique':False,
            'verification_design_space_reelle':False,
            'verification_machine_cricut_reelle':False}
        if qa['effective_dpi']<250:
            qa['alertes'].append('Resolution source inferieure a 250 DPI a cette taille : possible manque de nettete sur impression de tres fins details.')
        qa['alerte_zone_A4']='Dimension en mm indicative; verifier la zone Print Then Cut NON RECTANGULAIRE dans Design Space.'
        _proof(sheet,geometry,work/PROOF)
        # Only the V17 status file remains in root, older info retained as diagnostics.
        archive=work/'DETAILS_ELEMENTS'/'RAPPORTS_PRECEDENTS';archive.mkdir(parents=True,exist_ok=True)
        for name in ('PRET_V16.json','rapport_V16.json','00_LIRE_EN_PREMIER_CRICUT.txt'):
            f=work/name
            if f.exists():os.replace(f,archive/name)
        work.joinpath('00_LIRE_EN_PREMIER_CRICUT.txt').write_text(_cricut_guide(qa),encoding='utf-8')
        work.joinpath(REPORT).write_text(json.dumps({'audit_v17':qa,'audit_precedent':old_report},
                                    ensure_ascii=False,indent=2,default=_json_default),encoding='utf8')
        final=base/('SmartSVG_V17_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8])
        status={'version':VERSION,'statut':'PRECONTROLE_GEOMETRIQUE_REUSSI_CRICUT_NON_TESTE',
                'nombre_stickers':qa['nombre_stickers'],
                'kit_cricut':KIT,'alertes':qa['alertes'],
                'fichiers':_fingerprint_folder(work)}
        work.joinpath(READY).write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding='utf8')
        old_report['output']=str(final);old_report['version']=VERSION;old_report['audit_v17']=qa
        os.replace(work,final)
        return old_report,preview
    except Exception as exc:
        base.joinpath('SmartSVG_ECHEC_V17_'+uuid.uuid4().hex[:8]+'.json').write_text(
            json.dumps({'statut':'ECHEC_NON_PUBLIE','erreur':str(exc)},ensure_ascii=False,indent=2),encoding='utf8')
        raise UnsafeCut('SmartSVG V17 : export refuse : '+str(exc)) from exc
    finally:
        shutil.rmtree(stage,ignore_errors=True)
