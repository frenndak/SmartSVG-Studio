"""SmartSVG Studio V12: fail-closed staging, QA manifest, physical risk diagnostics.

The actual PNG print + exterior cut SVG still originate from V11's shared
binary owner mask; no false promises of Magic Layers / semantic reconstruction.
V12 exports nothing as READY until all mandatory artifacts pass QA.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import hashlib
import json
import os
import shutil
import tempfile
import uuid
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image

from .engine_v11 import process_v11, UnsafeCut, _components

NS = '{http://www.w3.org/2000/svg}'
MANDATORY = (
    'IMPORT_CRICUT_IMPRIMER_DECOUPER.png',
    'planche_CONTROLE_CONTOURS.png',
    'planche_CONTOURS.svg',
    'planche_EDITABLE_SIMPLIFIE.svg',
    'planche_EDITABLE_DETAILLE.svg',
    'rapport_V11.json',
)


def _json_default(value):
    # OpenCV / NumPy can return np.bool_, np.int32, np.float64 inside QA.
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f'Non serialisable: {type(value).__name__}')


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as inp:
        for data in iter(lambda: inp.read(1 << 20), b''):
            digest.update(data)
    return digest.hexdigest()


def _preflight_files(folder: Path, report: dict) -> dict:
    """Verify actual bytes, transparency, printable topology and SVG semantics."""
    expected = report['qa_v11']['dessins']
    files = {}
    for name in MANDATORY:
        item = folder/name
        if not item.is_file() or item.stat().st_size < 50:
            raise UnsafeCut('Livrable absent ou vide : '+name)
        files[name] = {'bytes':item.stat().st_size, 'sha256':_sha256(item)}
    with Image.open(folder/MANDATORY[0]) as im:
        im.load()
        if im.mode != 'RGBA':
            raise UnsafeCut('Le PNG Cricut ne conserve pas sa transparence RGBA')
        arr = np.asarray(im)
        if arr.shape[0]*arr.shape[1] > 20_000_000:
            raise UnsafeCut('Planche de sortie trop grande')
        alpha = (arr[...,3]>0).astype(np.uint8)
        if not np.any(alpha==0):
            raise UnsafeCut('Le PNG ne contient aucune transparence externe')
        if np.any(alpha[0]) or np.any(alpha[-1]) or np.any(alpha[:,0]) or np.any(alpha[:,-1]):
            raise UnsafeCut('Un motif touche le bord externe de la planche')
        _, _, components = _components(alpha, 1)
        if len(components) != expected:
            raise UnsafeCut(f'PNG: {len(components)} ilots opaques pour {expected} stickers')
    root = ET.parse(folder/'planche_CONTOURS.svg').getroot()
    paths = list(root.iter(NS+'path'))
    if len(paths)!=expected:
        raise UnsafeCut(f'SVG contours: {len(paths)} chemins pour {expected} stickers')
    ids = [p.get('id') for p in paths]
    if len(set(ids))!=expected or any(not p.get('d','').strip().endswith('Z') for p in paths):
        raise UnsafeCut('Chemins SVG de decoupe mal etiquetes ou ouverts')
    if list(root.iter(NS+'image')):
        raise UnsafeCut('SVG contours contient une image incorporee')
    editable = {}
    for name in ('planche_EDITABLE_SIMPLIFIE.svg','planche_EDITABLE_DETAILLE.svg'):
        tree=ET.parse(folder/name).getroot()
        children = [g for g in list(tree) if g.tag==NS+'g']
        count=len(list(tree.iter(NS+'path')))
        embedded=len(list(tree.iter(NS+'image')))
        if len(children)!=expected or embedded:
            raise UnsafeCut(f'{name}: groupes absents ou images matricielles incorporees')
        editable[name]={'groupes_stickers':len(children),'chemins_vectoriels':count,
                        'compatible_limite_5000_chemins':count<=5000}
    return {'dimensions_px':[int(alpha.shape[1]), int(alpha.shape[0])],
            'composants_png':len(components),'chemins_contour':len(paths),
            'svg_editables':editable,'fichiers':files}


def _thin_detail_report(folder: Path, qa: dict, limit_mm: float = 0.8) -> list:
    """Informational fragility heuristic, not a measured Cricut cutting limit.

    A morphological opening removes whiskers / thin appendages; comparing the
    losses helps reveal snails' fragile antennae. Never auto-delete those parts.
    """
    mm_size=qa['taille_planche_mm'][0]
    res_px=qa.get('resolution_impression_dpi',0)
    if not res_px or not mm_size:
        return []
    px_per_mm=res_px/25.4
    # A geometric opening at diameter about limit_mm (not tool-specific).
    radius = max(1,min(9,round(limit_mm*px_per_mm/2)))
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*radius+1,2*radius+1))
    rows=[]
    for it in qa.get('par_sticker',[]):
        idx=it['sticker']
        p=folder/f'element_{idx:02d}_PRINT.png'
        if not p.exists():continue
        alpha=np.asarray(Image.open(p).convert('RGBA'))[...,3]
        m=np.uint8(alpha>127)*255
        if not np.any(m):continue
        opened=cv2.morphologyEx(m,cv2.MORPH_OPEN,kernel)
        loss=float(np.count_nonzero((m>0)&(opened==0)))/max(1,np.count_nonzero(m))*100
        rows.append({'sticker':idx,'ouverture_test_mm':limit_mm,
                     'surface_antenne_ou_detail_fin_perdue_pct':round(loss,2),
                     'verification_recommandee':loss>=3.0})
    return rows


def _failure_record(base: Path, exc: BaseException):
    # Fail closed: no partially generated sticker artwork in the root folder.
    filename=base / ('SmartSVG_ECHEC_V12_'+uuid.uuid4().hex[:10]+'.json')
    filename.write_text(json.dumps({'version':'12.0-beta','statut':'BLOQUE',
           'raison':str(exc),'fichiers_cricut_publies':False,
           'conseil':'Consulter les logs ComfyUI, verifier image / transparence / IA.'},
           ensure_ascii=False,indent=2),encoding='utf-8')
    return filename


def process_v12(rgb, output_dir, *, layout='auto',intent='auto',ia_mode='auto',ai_masker=None,
                alpha=None,sheet_width_mm=180,margin_mm=1.5,editable_colors=10):
    """Isolate all versions' intermediary files, publish only QA-checked files."""
    base=Path(output_dir).expanduser()
    base.mkdir(parents=True,exist_ok=True)
    # Each run has a private staging root, eliminating stale validated outputs.
    staged_root=Path(tempfile.mkdtemp(prefix='.SmartSVG_V12_TEMP_',dir=base))
    published=False
    try:
        report,preview=process_v11(rgb,str(staged_root),layout=layout,intent=intent,
            ia_mode=ia_mode,ai_masker=ai_masker,alpha=alpha,
            sheet_width_mm=sheet_width_mm,margin_mm=margin_mm,editable_colors=editable_colors)
        workdir=Path(report['output'])
        if not workdir.is_dir() or staged_root not in workdir.parents:
            raise UnsafeCut('Sortie V11 hors du repertoire temporaire prevu')
        qa=report['qa_v11']
        if qa['contours_total'] != qa['dessins']:
            raise UnsafeCut('Controle V12: dessin sans contour propre')
        preflight=_preflight_files(workdir,report)
        thin=_thin_detail_report(workdir,qa)
        all_alerts=list(qa.get('alertes',[]))
        # Rounding by the source image's pixel pitch is an informational note,
        # not a failure or a production QA warning.
        info=[a for a in all_alerts if a.startswith('MARGE ARRONDIE')]
        warnings=[a for a in all_alerts if not a.startswith('MARGE ARRONDIE')]
        if qa.get('resolution_impression_dpi',300)<250:
            info.append('IMPRESSION: resolution de la source inferieure a 250 DPI; un sur-echantillonnage ne recree pas les details manquants.')
        if any(d['verification_recommandee'] for d in thin):
            warnings.append('DETAILS FINS: antennes/petales fins potentiellement fragiles. Examiner le controle de decoupe et faire un essai papier.')
        if any(not el['compatible_limite_5000_chemins'] for el in preflight['svg_editables'].values()):
            warnings.append('SVG EDITABLE: depasse potentiellement la limite Cricut de 5000 chemins; importer le PNG pour imprimer/découper.')
        # One global destination; previews and reports share the same folder.
        dirname='SmartSVG_V12_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:6]
        final=base/dirname
        updated=dict(report)
        updated['output']=str(final)
        updated['version']='12.0-beta'
        updated['rapport_qualite_v12']={'statut':'CONTROLES_LOGICIELS_REUSSIS' if not warnings else 'AVERTISSEMENTS_A_CONTROLER',
                                       'nombre_stickers':qa['dessins'],
                                       'dossier_unique':str(final),
                                       'preflight':{k:v for k,v in preflight.items() if k!='fichiers'},
                                       'risques_details_fins':thin,
                                       'informations':info,
                                       'alertes':warnings,
                                       'verification_dans_design_space_obligatoire':True,
                                       'validation_decoupe_physique':False,
                                       'validation_gpu_dans_notre_environnement':False,
                                       'stickers_effectivement_detoures_par_ia':[
                                           int(x['index']) for x in report.get('items',[]) if x.get('mask_used')=='IA_locale']}

        (workdir/'rapport_V12.json').write_text(json.dumps(updated,ensure_ascii=False,indent=2,default=_json_default),encoding='utf-8')
        # Older report stores V11's stage path; avoid contradictory project state.
        (workdir/'rapport_V11.json').write_text(json.dumps({'ancien_rapport':'rapport_V12.json',
                   'message':'Rapport V12 de reference; fichier V11 conserve pour compatibilite.'},
                   ensure_ascii=False,indent=2),encoding='utf-8')
        instructions=f'''SMARTSVG STUDIO V12 — IMPRESSION & DECOUPE CRICUT\n\n{qa['dessins']} autocollant(s); {qa['contours_total']} contour(s) independants.\n\nFICHIER PRINCIPAL: IMPORT_CRICUT_IMPRIMER_DECOUPER.png\nDimensions attendues : {qa['taille_planche_mm'][0]:.2f} x {qa['taille_planche_mm'][1]:.2f} mm.\nImporter PNG dans Cricut Design Space comme image plate, puis Print Then Cut.\nNe PAS superposer planche_CONTOURS.svg : double-decoupe possible.\nSVG de couleurs = tracés par couleur, PAS objets reconnus par IA.\nLes bordures/marges et contraintes capteur se valident dans Design Space.\nLa machine doit etre calibree et la decoupe testee sur papier.\n\nAVERTISSEMENTS :\n'''+('\n'.join('* '+s for s in warnings) or '(aucun avertissement logiciel)')+'\n\nINFORMATIONS :\n'+('\n'.join('* '+s for s in info) or '(aucune)')+'\n'
        (workdir/'LISEZ_MOI_CRICUT_V12.txt').write_text(instructions,encoding='utf-8')
        # Keep user-facing, whole-sheet exports at the root. Per-item raster
        # intermediates are retained for diagnosis but no longer clutter the
        # main folder with 12/24 files to import accidentally.
        detail_files=[p for p in workdir.glob('element_*') if p.is_file()]
        if detail_files:
            details=workdir/'DETAILS_ELEMENTS'
            details.mkdir(exist_ok=True)
            for p in detail_files:
                os.replace(p,details/p.name)
        # V11 and V9 backwards-compatible aliases point to identical bytes;
        # not expose two "main" PNGs which lead to user-side mistakes.
        for obsolete in ('planche_IMPRIMER_DECOUPER.png','planche_CONTOURS_12.svg'):
            p=workdir/obsolete
            if p.is_file():p.unlink()
        # Create inspection manifest last, before publication.
        files={}
        for p in sorted(workdir.iterdir()):
            if p.is_file() and p.name not in ('PRET_V12.json',):
                files[p.name]={'bytes':p.stat().st_size,'sha256':_sha256(p)}
        ready={'statut':'CONTROLES_LOGICIELS_REUSSIS' if not warnings else 'AVERTISSEMENTS_A_CONTROLER',
               'version':'12.0-beta','photos_originales_reconstituees':False,
               'coupes_cricut_test_physique':False,'dossier':str(final),
               'fichiers':files,'document_principal':'IMPORT_CRICUT_IMPRIMER_DECOUPER.png'}
        if detail_files:
            ready['fichiers_intermediaires'] = len(detail_files)
            ready['sous_dossier_intermediaires'] = 'DETAILS_ELEMENTS'
        (workdir/'PRET_V12.json').write_text(json.dumps(ready,ensure_ascii=False,indent=2,default=_json_default),encoding='utf-8')
        # Same volume means rename of entire directory is atomic under NTFS.
        os.replace(workdir,final)
        published=True
        updated['output']=str(final)
        return updated,preview
    except Exception as exc:
        err=_failure_record(base,exc)
        raise UnsafeCut(f'Export V12 non publie. Diagnostic : {err}. Erreur : {exc}') from exc
    finally:
        # Discard legacy intermediary outputs on failure AND after publication.
        shutil.rmtree(staged_root,ignore_errors=True)
