"""SmartSVG V16: Cricut-first delivery pack on top of the audited V15 engine.

No claim of semantic reconstruction or native .cricut project generation.
ComfyUI inference is inherited from RMBG bridge; local CPU tests don't validate a GPU.
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
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image

from .engine_v11 import UnsafeCut
from .engine_v12 import _json_default
from .engine_v13 import _cut_paths, _polygon_mask, _compare_cut_with_png
from .engine_v14 import CRICUT_SVG, CRICUT_SVG_DETAIL, NAME
from .engine_v15 import (process_v15, REGION_SVG, SINGLES, _viewbox, _mm,
                          _validate_safe_svg, alpha_preflight)

VERSION = '16.0-beta'
KIT = 'KIT_IMPORT_CRICUT'
STATUS = 'PRET_V16.json'


def _sha256_streamed(path):
    h = hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):
            h.update(chunk)
    return h.hexdigest()


def _fingerprint_folder(folder: Path):
    files = {}
    for p in sorted(folder.rglob('*')):
        if p.is_file() and p.name != STATUS:
            rel = p.relative_to(folder).as_posix()
            files[rel] = {'sha256':_sha256_streamed(p),'octets':p.stat().st_size}
    return files


def _apply_pixel_density(png_path:Path, physical_width_mm:float):
    if physical_width_mm <= 0: raise UnsafeCut('Largeur physique non positive')
    with Image.open(png_path) as im:
        if im.mode != 'RGBA':raise UnsafeCut('Image Cricut non RGBA')
        image=im.copy()
    effective_dpi=image.width*25.4/physical_width_mm
    if not 30 <= effective_dpi <= 2400:
        raise UnsafeCut(f'Resolution physique incoherente: {effective_dpi:.1f} DPI')
    image.save(png_path, format='PNG', dpi=(effective_dpi,effective_dpi),optimize=True)
    with Image.open(png_path) as check:
        recorded=check.info.get('dpi',(0,0))
        if check.mode != 'RGBA' or abs(recorded[0]-effective_dpi)>0.2:
            raise UnsafeCut('Ecriture des metadonnees DPI incomplete')
    return round(effective_dpi,2)


def _create_individual_pngs(work:Path, count:int, physical_width_mm:float):
    """Crop from the FINAL PRINT raster and isolate exactly one sticker alpha.

    This retains print fidelity (shadows/reflections), unlike vector renders.
    All source pixels belonging to a neighboring sticker are made transparent.
    """
    sheet = np.asarray(Image.open(work/NAME).convert('RGBA'))
    alpha = sheet[:,:,3]
    if np.any((alpha!=0)&(alpha!=255)):
        raise UnsafeCut('Alpha imprime non binaire')
    h,w=alpha.shape
    n,labels,stats,_ = cv2.connectedComponentsWithStats((alpha>0).astype(np.uint8),8)
    if n-1 != count:
        raise UnsafeCut(f'PNG individuel : {n-1} objets au lieu de {count}')
    cut = _cut_paths(work,count)
    dest = work/SINGLES
    dest.mkdir(exist_ok=True)
    scale = float(physical_width_mm)/w
    exports=[]
    for idx in range(1,count+1):
        svg_file=dest/f'STICKER_{idx:02d}_EDITABLE.svg'
        if not svg_file.exists():raise UnsafeCut(f'SVG individuel manquant : {idx}')
        svg_root=ET.parse(svg_file).getroot()
        _validate_safe_svg(svg_root)
        x0,y0,bw,bh=_viewbox(svg_root)
        if any(abs(round(v)-v)>1e-6 for v in (x0,y0,bw,bh)):
            raise UnsafeCut('Recadrage individuel non entier')
        x0,y0,bw,bh=map(int,(x0,y0,bw,bh))
        if bw<=0 or bh<=0:raise UnsafeCut('Dimensions sticker impossibles')
        if abs(_mm(svg_root.get('width'))-bw*scale)>0.01:
            raise UnsafeCut('Taille physique differente du SVG individuel')
        poly = _polygon_mask(cut[idx],h,w)
        histogram=np.bincount(labels[poly>0].reshape(-1),minlength=n)
        histogram[0]=0
        target_label=int(histogram.argmax())
        if target_label==0:raise UnsafeCut(f'Contour sticker {idx} sans silhouette visible')
        if any(item['composante']==target_label for item in exports):
            raise UnsafeCut('Contour associe deux fois a la meme silhouette')
        component = (labels==target_label)
        if not component.any():raise UnsafeCut('Image individuelle vide')
        # No pixel of a neighbor is ever allowed into an individual PNG.
        canvas=np.zeros((bh,bw,4),dtype=np.uint8)
        sx0=max(0,x0);sy0=max(0,y0)
        sx1=min(w,x0+bw);sy1=min(h,y0+bh)
        if sx1>sx0 and sy1>sy0:
            region=sheet[sy0:sy1,sx0:sx1].copy()
            wanted=component[sy0:sy1,sx0:sx1]
            region[~wanted]=0
            canvas[sy0-y0:sy1-y0,sx0-x0:sx1-x0]=region
        a=canvas[:,:,3]>0
        if np.count_nonzero(a)==0:
            raise UnsafeCut('Image individuelle recadree vide')
        if int(np.count_nonzero(a)) != int(np.count_nonzero(component)):
            raise UnsafeCut('Image individuelle tronquee a la bordure')
        output=dest/f'STICKER_{idx:02d}_IMPRIMER_DECOUPER.png'
        Image.fromarray(canvas,'RGBA').save(output,format='PNG',dpi=(25.4/scale,25.4/scale),optimize=True)
        with Image.open(output) as verify:
            if verify.size!=(bw,bh) or verify.mode!='RGBA':raise UnsafeCut('Export PNG individuel invalide')
        exports.append({'sticker':idx,'composante':target_label,
                        'svg':f'{SINGLES}/{svg_file.name}',
                        'png':f'{SINGLES}/{output.name}',
                        'dimensions_mm':[round(bw*scale,3),round(bh*scale,3)],
                        'pixels_imprimes':int(component.sum())})
    if len(exports)!=count:raise UnsafeCut('Incomplet: exports individuels')
    return exports


def _create_quick_kit(work:Path):
    names={
        '01_IMPRIMER_PUIS_DECOUPER.png':NAME,
        '02_MODIFIER_COULEURS.svg':CRICUT_SVG,
        '03_MODIFIER_REGIONS.svg':REGION_SVG,
    }
    dest=work/KIT
    dest.mkdir(exist_ok=True)
    for final,src in names.items():
        if not (work/src).is_file():raise UnsafeCut('Export principal absent : '+src)
        shutil.copy2(work/src,dest/final)
        if _sha256_streamed(work/src)!=_sha256_streamed(dest/final):
            raise UnsafeCut('Copie kit Cricut incorrecte : '+final)
    return names


def process_v16(rgb, output_dir, *, layout='auto', intent='auto', ia_mode='auto', ai_masker=None,
                alpha=None, sheet_width_mm=180, margin_mm=1.5, editable_colors=10,
                runtime_rmbg_stats=None):
    """Fail-closed: stage a whole V15 run, add a Cricut kit, publish once."""
    base=Path(output_dir).expanduser()
    base.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='.SmartSVG_V16_TEMP_',dir=base))
    try:
        report,preview=process_v15(rgb,str(staging),layout=layout,intent=intent,
            ia_mode=ia_mode,ai_masker=ai_masker,alpha=alpha,
            sheet_width_mm=sheet_width_mm,margin_mm=margin_mm,
            editable_colors=editable_colors,runtime_rmbg_stats=runtime_rmbg_stats)
        work=Path(report['output'])
        if not work.is_dir() or work.parent!=staging:
            raise UnsafeCut('V15 a produit un dossier inattendu')
        count=int(report['audit_v15']['nombre_stickers'])
        main=work/NAME
        with Image.open(main) as im:
            width,height=im.size
        # Physical width is established by the editable SVG, not guessed from the original image.
        root=ET.parse(work/CRICUT_SVG).getroot()
        measured_width_mm=_mm(root.get('width'))
        measured_height_mm=_mm(root.get('height'))
        if abs(measured_width_mm-width/float(height)*measured_height_mm)>0.05:
            raise UnsafeCut('Dimensions SVG non proportionnelles au PNG')
        checked,_ = _compare_cut_with_png(work,count)
        dpi=_apply_pixel_density(main,measured_width_mm)
        individ=_create_individual_pngs(work,count,measured_width_mm)
        kit=_create_quick_kit(work)
        # Verify renamed/created files still agree with PNG alpha shape.
        cut_check,_=_compare_cut_with_png(work,count)
        if checked['contours']!=cut_check['contours'] or checked['pixels_opaques']!=cut_check['pixels_opaques']:
            raise UnsafeCut('Metadonnees PNG ont altere les masques')
        # Do not present heuristically edited SVG as pixel-identical to print raster.
        fidelity=report['audit_v141']['fidelite_png'].get('svg_compact',{})
        warnings=[]
        if dpi<200:
            warnings.append(f'Resolution originale faible pour impression tres fine ({dpi:.0f} DPI). Les metadonnees DPI n ajoutent aucun detail.')
        if fidelity.get('mesure_effectuee') and fidelity.get('ecart_moyen_rgb',0)>15:
            warnings.append('SVG editable : nuances/degrades differents du PNG original. Favoriser PNG si fidelite prioritaire.')
        if not report['audit_v15']['controle_svg_compact']['teste']:
            warnings.append('Controle raster SVG indisponible: verifier son apparence dans Design Space.')
        final=base/('SmartSVG_V16_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8])
        # Prevent stale "ready" files from earlier versions in the root.
        archive=work/'DETAILS_ELEMENTS'/'RAPPORTS_PRECEDENTS'
        archive.mkdir(parents=True,exist_ok=True)
        for name in ( 'PRET_V15.json','LIRE_EN_PREMIER.txt','rapport_V15.json'):
            if (work/name).exists():os.replace(work/name,archive/name)
        audit={'version':VERSION,'nombre_stickers':count,
               'largeur_planche_mm':round(measured_width_mm,3),
               'hauteur_planche_mm':round(measured_height_mm,3),
               'dimensions_pixels':[width,height],
               'densite_pixels_effective_dpi':dpi,
               'metadonnees_png_dpi_ecrites':True,
               'png_individuels':individ,
               'kit_import_cricut':kit,
               'comparaison_svg_png_contours':cut_check,
               'alertes':warnings,
               'compatibilite_design_space_testee':False,
               'decoupe_machine_testee':False,
               'ia_cuda_testee_sur_pc_utilisateur':False,
               'calques_semantiques_yeux_corps_coquille':False,
        }
        report['output']=str(final)
        report['version']=VERSION
        report['audit_v16']=audit
        (work/'rapport_V16.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=_json_default),encoding='utf-8')
        quick=f'''SMARTSVG STUDIO V16 — GUIDE CRICUT DESIGN SPACE\n\nCOMMENCER ICI : {KIT}/\n\nA. IMPRIMER PUIS DECOUPER SANS MODIFIER LE DESSIN\n  1. Televerser 01_IMPRIMER_PUIS_DECOUPER.png dans Design Space comme Image plate (Flat Graphic).\n  2. Verifier la taille : {measured_width_mm:.1f} x {measured_height_mm:.1f} mm (la taille peut varier a l'import).\n  3. Previsualiser la decoupe : {count} contours exterieurs, PAS un rectangle, PAS les yeux ou les pois.\n  4. Choisir Imprimer puis decouper. Imprimer et decouper dans LA MEME session Design Space.\n  5. Si la coupe est decalee, calibrer Print Then Cut.\n\nB. MODIFIER LES COULEURS AVANT D'IMPRIMER\n  1. Televerser 02_MODIFIER_COULEURS.svg ou 03_MODIFIER_REGIONS.svg.\n  2. Dissocier le sticker souhaite, recolorer ou repositionner les formes.\n  3. Selectionner les calques a imprimer, puis APLATIR (pas seulement Attacher).\n  4. Verifier la silhouette dans l'aperçu. La version SVG perd certaines nuances.\n\nC. UN SEUL MOTIF : {SINGLES}/\n  STICKER_XX_IMPRIMER_DECOUPER.png pour une impression fidele;\n  STICKER_XX_EDITABLE.svg pour les couleurs.\n\nIMPORTANT\n  Ne JAMAIS superposer planche_CONTOURS.svg au PNG : double decoupe.\n  Ne PAS preimprimer une feuille en dehors de Design Space, cela supprime les reperes machine.\n  Il n'existe PAS de projet natif .cricut genere ici.\n  Les SVG contiennent des regions colorees, PAS des objets semantiques (oeil/corps/coquille).\n  DPI effectif source: {dpi:.1f}. Les metadonnees PNG ne creent aucun nouveau detail.\n  La surface Print Then Cut varie selon l'imprimante, le papier et le contour : verifier Design Space.\n  Calibration et test de decoupe reel toujours necessaires.\n'''
        (work/'00_LIRE_EN_PREMIER_CRICUT.txt').write_text(quick,encoding='utf-8')
        (work/KIT/'00_LIRE_AVANT_IMPORT.txt').write_text(quick,encoding='utf-8')
        status={'version':VERSION,'statut':'GEOMETRIE_CONTROLEE_CRICUT_NON_TESTE',
                'nombre_stickers':count,'kit':KIT,'largeur_planche_mm':measured_width_mm,
                'hauteur_planche_mm':measured_height_mm,'rmbg_usage':report['audit_v141']['ia']['etat'],
                'avertissements':warnings,'fichiers':_fingerprint_folder(work)}
        (work/STATUS).write_text(json.dumps(status,ensure_ascii=False,indent=2,default=_json_default),encoding='utf-8')
        # Publishing a single folder is atomic on the target volume.
        os.replace(work,final)
        return report,preview
    except Exception as exc:
        (base/('SmartSVG_ECHEC_V16_'+uuid.uuid4().hex[:8]+'.json')).write_text(
            json.dumps({'statut':'ECHEC_NON_PUBLIE','erreur':str(exc)},ensure_ascii=False,indent=2),encoding='utf-8')
        raise UnsafeCut('SmartSVG V16: export refuse : '+str(exc)) from exc
    finally:
        shutil.rmtree(staging,ignore_errors=True)
