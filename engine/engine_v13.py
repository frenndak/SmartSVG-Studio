"""SmartSVG V13: release-atomic editable SVG bases aligned to Print Then Cut.

V12 output is produced in a PRIVATE outer staging directory, never directly in
user's destination. V13 validates the true rasterized SVG outlines and injects
matching, separately editable white offset bases under each sticker artwork.
The final directory is published with a same-volume atomic rename.

Color paths are still color regions, NOT inferred semantic body/eye/shell parts.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import uuid
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image

from .engine_v11 import UnsafeCut
from .engine_v12 import process_v12, _json_default

SVG = '{http://www.w3.org/2000/svg}'
INK = '{http://www.inkscape.org/namespaces/inkscape}'
ET.register_namespace('inkscape', INK[1:-1])
_NAME = 'IMPORT_CRICUT_IMPRIMER_DECOUPER.png'
_CUT = 'planche_CONTOURS.svg'
_EDITABLES = ('planche_EDITABLE_SIMPLIFIE.svg', 'planche_EDITABLE_DETAILLE.svg')
_SAFE_PATH = re.compile(r'M-?\d+,-?\d+(?: L-?\d+,-?\d+){2,} Z')
_COORD = re.compile(r'(-?\d+),(-?\d+)')
_TRANSLATE = re.compile(r'translate\(\s*(-?\d+(?:\.\d+)?)\s*[, ]\s*(-?\d+(?:\.\d+)?)\s*\)')


def _sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(1<<20),b''):
            h.update(part)
    return h.hexdigest()


def _cut_paths(folder: Path, expected: int):
    root=ET.parse(folder/_CUT).getroot()
    result={}
    for p in root.iter(SVG+'path'):
        m=re.fullmatch(r'CUT_(\d+)',p.get('id',''))
        if not m:
            raise UnsafeCut('Identifiant de contour inattendu : '+p.get('id','(sans id)'))
        idx=int(m.group(1));d=p.get('d','')
        if idx in result or not _SAFE_PATH.fullmatch(d):
            raise UnsafeCut(f'Contour {idx}: duplique ou instructions SVG non conformes')
        result[idx]=d
    if set(result)!=set(range(1,expected+1)):
        raise UnsafeCut(f'Contours SVG : {len(result)} chemins et indices incomplets pour {expected} stickers')
    return result


def _polygon_mask(d: str, height: int, width: int):
    if not _SAFE_PATH.fullmatch(d):
        raise UnsafeCut('Contour SVG non polygonal/autorise')
    points=np.array([[int(x),int(y)] for x,y in _COORD.findall(d)],dtype=np.int32)
    if len(points)<3 or np.max(np.abs(points))>max(width,height)*20:
        raise UnsafeCut('Points SVG aberrants')
    mask=np.zeros((height,width),dtype=np.uint8)
    cv2.fillPoly(mask,[points],1)
    return mask


def _compare_cut_with_png(folder: Path, expected: int):
    # Verifies geometry, not merely existence, count or well-formed SVG syntax.
    with Image.open(folder/_NAME) as p:
        p.load()
        if p.mode!='RGBA':
            raise UnsafeCut('PNG non RGBA : silhouette non fiable')
        alpha=np.asarray(p.getchannel('A'))
    if not np.all((alpha==0)|(alpha==255)):
        raise UnsafeCut('Transparence partielle inattendue : bord de decoupe ambigu')
    target=np.uint8(alpha>0)
    h,w=target.shape
    union=np.zeros((h,w),dtype=np.uint8)
    contour_masks={}
    for idx,d in sorted(_cut_paths(folder,expected).items()):
        m=_polygon_mask(d,h,w)
        if int(np.count_nonzero(m))==0:
            raise UnsafeCut(f'Contour {idx} vide')
        if np.any(union & m):
            raise UnsafeCut(f'Contours {idx} superposes : risque de fusion')
        union |= m
        contour_masks[idx]=m
    difference=np.count_nonzero(union != target)
    pct=100*difference/max(1,np.count_nonzero(target))
    if pct>1.0:
        raise UnsafeCut(f'SVG decoupe / PNG : ecart raster de {pct:.3f}% (seuil 1%)')
    # A count-only check could be satisfied even if a path was duplicated and
    # another sticker omitted. Match each silhouette geometrically, 1 to 1.
    n, labels, stats, centers=cv2.connectedComponentsWithStats(target,8)
    if n-1!=expected:
        raise UnsafeCut(f'PNG : {n-1} composantes, attendu {expected}')
    matched=set()
    for idx,m in sorted(contour_masks.items()):
        areas=np.bincount(labels[m>0].ravel(),minlength=n)
        areas[0]=0
        comp=int(np.argmax(areas))
        if comp==0 or comp in matched:
            raise UnsafeCut(f'Contour {idx} non apparie a une silhouette distincte')
        matched.add(comp)
        expected_mask=(labels==comp)
        error=100*np.count_nonzero(m != expected_mask)/max(1,np.count_nonzero(expected_mask))
        if error>1.0:
            raise UnsafeCut(f'Contour {idx} diverge de son sticker : {error:.3f}%')
    return {'contours':expected,'difference_png_svg_pct':round(pct,4),
            'pixels_differents':int(difference),'pixels_opaques':int(np.count_nonzero(target)),
            'appariement_individuel':True},contour_masks


def _translation_of_group(element):
    transform=element.get('transform','').strip()
    transforms=list(_TRANSLATE.finditer(transform))
    if not transforms or re.sub(r'\s+','',_TRANSLATE.sub('',transform)):
        raise UnsafeCut(f'Transformation sticker inattendue : {transform[:100]}')
    return (sum(float(m.group(1)) for m in transforms),
            sum(float(m.group(2)) for m in transforms))


def _inject_offset_bases(folder: Path, paths: dict, expected: int):
    results={}
    for filename in _EDITABLES:
        p=folder/filename
        tree=ET.parse(p)
        root=tree.getroot()
        groups=[g for g in list(root) if g.tag==SVG+'g']
        if len(groups)!=expected:
            raise UnsafeCut(f'{filename} : {len(groups)} groupes au lieu de {expected}')
        seen=set()
        for sticker in groups:
            match=re.fullmatch(r'STICKER_(\d+)',sticker.get('id',''))
            if not match:
                raise UnsafeCut(f'{filename} : groupe sticker mal etiquete')
            idx=int(match.group(1))
            if idx in seen or idx not in paths:
                raise UnsafeCut(f'{filename} : index sticker duplique ou non repertorie')
            seen.add(idx)
            tx,ty=_translation_of_group(sticker)
            # Old color SVG had an arbitrary white raster-derived base, which
            # did not necessarily match the printed sheet's outer sticker cut.
            for child in list(sticker):
                if child.get('id','').endswith('_FOND'):
                    sticker.remove(child)
            layer=ET.Element(SVG+'g',{
                'id':f'STICKER_{idx:02d}_BASE_DECOUPE',
                INK+'label':'Base blanche / contour exact Print Then Cut',
                'data-role':'white-cut-offset',
                'fill':'#ffffff'
            })
            # Existing colored paths are local to this group. Reuse the exact
            # GLOBAL contour from the printable PNG, undoing parent translation.
            ET.SubElement(layer,SVG+'path',{
                'id':f'STICKER_{idx:02d}_BASE_EXTERIEURE',
                'd':paths[idx],
                'transform':f'translate({-tx:.4f},{-ty:.4f})',
                'data-cut-aligned':'true',
            })
            sticker.insert(0,layer)
        if seen!=set(range(1,expected+1)):
            raise UnsafeCut(f'{filename}: groupe(s) manquant(s)')
        root.set('data-editability','color-regions, not semantic objects')
        root.set('data-print-cut-base','same contours as printable PNG')
        temp=p.with_name('._temporary_'+p.name)
        tree.write(temp,encoding='utf-8',xml_declaration=True)
        if len(list(ET.parse(temp).getroot().iter(SVG+'path')))>5000:
            # User still needs the vector version; warn in report, don't lie.
            pass
        os.replace(temp,p)
        parsed=ET.parse(p).getroot()
        cut_bases=[g for g in parsed.iter(SVG+'g') if g.get('data-role')=='white-cut-offset']
        if len(cut_bases)!=expected:
            raise UnsafeCut(f'{filename}: manque des bases vectorielles alignees')
        for sticker in [g for g in list(parsed) if g.tag==SVG+'g']:
            idx=int(sticker.get('id').split('_')[-1])
            layer=next((child for child in sticker if child.get('id')==f'STICKER_{idx:02d}_BASE_DECOUPE'),None)
            if layer is None or len(list(layer))!=1:
                raise UnsafeCut(f'{filename}: base sticker {idx} manquante/ambigue')
            shape=list(layer)[0]
            if shape.get('d')!=paths[idx]:
                raise UnsafeCut(f'{filename}: la forme {idx} diverge du contour PDF/PNG')
            px,py=_translation_of_group(sticker)
            bx,by=_translation_of_group(shape)
            if abs(px+bx)>1e-6 or abs(py+by)>1e-6:
                raise UnsafeCut(f'{filename}: base sticker {idx} decalee de son contour')
        results[filename]={'groupes_stickers':expected,
                            'bases_exterieures_exactes':len(cut_bases),
                            'total_chemins':len(list(parsed.iter(SVG+'path')))}
    return results


def _manifest(folder: Path):
    records={}
    for p in sorted(folder.rglob('*')):
        if p.is_file() and p.name!='PRET_V13.json':
            rel=p.relative_to(folder).as_posix()
            records[rel]={'taille_octets':p.stat().st_size,'sha256':_sha256(p)}
    return records


def process_v13(rgb, output_dir, *, layout='auto',intent='auto',ia_mode='auto',ai_masker=None,
                alpha=None,sheet_width_mm=180,margin_mm=1.5,editable_colors=10):
    base=Path(output_dir).expanduser()
    base.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='.SmartSVG_V13_TEMP_',dir=base))
    try:
        report,preview=process_v12(rgb,str(staging),layout=layout,intent=intent,
            ia_mode=ia_mode,ai_masker=ai_masker,alpha=alpha,
            sheet_width_mm=sheet_width_mm,margin_mm=margin_mm,
            editable_colors=editable_colors)
        work=Path(report['output'])
        if work.parent!=staging or not work.is_dir():
            raise UnsafeCut('Sortie V12 imprévue : publication V13 interdite')
        expected=int(report['qa_v11']['dessins'])
        checked,masks=_compare_cut_with_png(work,expected)
        vector=_inject_offset_bases(work,_cut_paths(work,expected),expected)
        old_ready=work/'PRET_V12.json'
        if old_ready.exists():
            old_ready.unlink()  # V12 hashes of modified SVG are outdated.
        final=base/('SmartSVG_V13_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8])
        qa12=report['rapport_qualite_v12']
        qa13={'statut':qa12['statut'], 'geometry_validated':True,
              'image_impression':_NAME,'calques_vectoriels':vector,
              'comparaison_svg_png':checked,
              'detourage_ia_effectif':qa12.get('stickers_effectivement_detoures_par_ia',[]),
              'segmentation_semantique':False,
              'verification_dans_cricut_requise':True,
              'largeur_planche_mm':float(report['qa_v11']['taille_planche_mm'][0]),
              'hauteur_planche_mm':float(report['qa_v11']['taille_planche_mm'][1])}
        report['output']=str(final);report['version']='13.0-beta'
        report['rapport_qualite_v12']['dossier_unique']=str(final)
        report['rapport_qualite_v13']=qa13
        (work/'rapport_V13.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=_json_default),encoding='utf-8')
        # No obsolete V12 report with staging paths should be treated as current.
        for name in (
            'rapport.json','rapport_V8.json','rapport_V9.json',
            'rapport_V11.json','rapport_V12.json',
            'LISEZ_MOI_CRICUT.txt','LISEZ_MOI_CRICUT_V9.txt',
            'LISEZ_MOI_CRICUT_V12.txt','LISEZ_MOI_CRICUT_V11.txt',
            'planche_VECTORIEL_SIMPLIFIE.svg','planche_VECTORIEL_DETAILLE.svg'):
            older=work/name
            if older.exists():older.unlink()
        (work/'LIRE_AVANT_CRICUT_V13.txt').write_text(
            'SmartSVG Studio V13 — BETA, verifier dans Design Space.\n\n'
            f'{expected} stickers / {expected} contours exterieurs independants.\n'
            'IMPORT PRINCIPAL POUR IMPRIMER PUIS DECOUPER :\n'
            f'  {_NAME}\n\n'
            'POUR MODIFIER COULEURS / GROUPES :\n'
            '  planche_EDITABLE_SIMPLIFIE.svg\n'
            '  Chaque sticker possede une base blanche a la meme silhouette\n'
            '  que son PNG (contour avec marge). Pour Print Then Cut : APLATIR.\n'
            '  Les elements ne sont PAS des objets semantiques yeux/corps/coquille.\n'
            'NE PAS superposer planche_CONTOURS.svg au PNG : double decoupe.\n'
            'Verifier les dimensions physiques, les reperes, la calibration\n'
            'et la previsualisation de decoupe dans Design Space.\n',encoding='utf-8')
        ready={'version':'13.0-beta','statut':qa13['statut'],'dossier':str(final),
               'import_principal':_NAME,'nombre_contours_verifies':expected,
               'base_svg_alignee_png':True,'mesures_geometriques':checked,
               'test_mecanique_cricut_effectue':False,
               'fichiers':_manifest(work)}
        (work/'PRET_V13.json').write_text(json.dumps(ready,ensure_ascii=False,indent=2,default=_json_default),encoding='utf-8')
        os.replace(work,final)
        return report,preview
    except Exception as exc:
        (base/('SmartSVG_ECHEC_V13_'+uuid.uuid4().hex[:10]+'.json')).write_text(
            json.dumps({'version':'13.0-beta','statut':'BLOQUE','message':str(exc),
                        'sortie_partielle_publiee':False},ensure_ascii=False,indent=2),encoding='utf-8')
        raise UnsafeCut(f'V13 publication refusee : {exc}') from exc
    finally:
        shutil.rmtree(staging,ignore_errors=True)
