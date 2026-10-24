"""SmartSVG Studio 15: Cricut edit-pack and rasterized alpha preflight.

No semantic-object recognition is claimed. ComfyUI inference is inherited from
V14.1 and must be validated on the user's actual GPU/RMBG installation.
"""
from __future__ import annotations
import copy
from datetime import datetime
import io
import json
import hashlib
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
from .engine_v13 import SVG, _cut_paths, _COORD, _manifest
from .engine_v14 import CRICUT_SVG, CRICUT_SVG_DETAIL, NAME
from .engine_v141 import process_v141, analyze_svg

VERSION='15.0-beta'
REGION_SVG='CRICUT_EDITION_REGIONS_INDEPENDANTES.svg'
SINGLES='EDITER_STICKERS_SEPAREMENT'


def _viewbox(root):
    box=root.get('viewBox','').replace(',',' ').split()
    if len(box)!=4:raise UnsafeCut('SVG sans viewBox valide')
    a=list(map(float,box))
    if a[2]<=0 or a[3]<=0:raise UnsafeCut('viewBox invalide')
    return a


def _mm(s):
    if not s or not s.endswith('mm'):raise UnsafeCut('SVG sans dimensions physiques en mm')
    return float(s[:-2])


def _validate_safe_svg(root):
    if any(e.tag not in {SVG+'svg', SVG+'g', SVG+'path'} for e in root.iter()):
        raise UnsafeCut('SVG: elements incompatibles avec le profil Cricut')
    for e in root.iter():
        if any(k in e.attrib for k in ('style','clip-path','mask','filter','opacity','stroke','href')):
            raise UnsafeCut('SVG: attribut de rendu non gere')
    return True


def make_region_svg(work:Path, sticker_count:int):
    """One shape per original V13 color region, with named editable layers.

    This is the *detailed-edit* counterpart to V14's compact-by-color SVG.
    It retains the exact color paths, including compound holes, without
    pretending that each region is an eye/shell/body semantic object.
    """
    original=ET.parse(work/'planche_EDITABLE_SIMPLIFIE.svg').getroot()
    # Legacy source may contain Inkscape metadata, intentionally discarded.
    src_groups=[g for g in original if g.tag==SVG+'g']
    if len(src_groups)!=sticker_count:raise UnsafeCut('Regions : nombre de groupes sticker incorrect')
    compact=ET.parse(work/CRICUT_SVG).getroot()
    cut_bases={g.get('id'):copy.deepcopy(g[0]) for g in compact if g.tag==SVG+'g'}
    target=ET.Element(SVG+'svg',{k:original.get(k) for k in ('width','height','viewBox')})
    all_regions=0
    counters=[]
    for index,src in enumerate(src_groups,1):
        key=f'STICKER_{index:02d}'
        if src.get('id')!=key or key not in cut_bases:
            raise UnsafeCut('Regions: groupe manquant ou mal trie')
        dst=ET.SubElement(target,SVG+'g',{'id':key,'transform':src.get('transform','')})
        dst.append(copy.deepcopy(cut_bases[key]))
        localcount=0
        for color_idx,layer in enumerate(src,1):
            if layer.get('data-role')=='white-cut-offset' or layer.get('id','').endswith('_FOND'):
                continue
            fill=layer.get('fill','')
            if not(fill.startswith('#') and len(fill)==7):
                raise UnsafeCut('Regions: couleur inattendue')
            cg=ET.SubElement(dst,SVG+'g',{'id':f'S{index:02d}_COULEUR_{color_idx:02d}_{fill[1:].upper()}'})
            for p in layer:
                if p.tag!=SVG+'path':raise UnsafeCut('Regions: objet non vectoriel')
                d=p.get('d','').strip()
                if not d.startswith('M'):raise UnsafeCut('Regions: tracé sans point de départ')
                localcount+=1
                ET.SubElement(cg,SVG+'path',{'id':f'S{index:02d}_REGION_{localcount:03d}',
                    'd':d,'fill':fill,'fill-rule':'evenodd'})
        all_regions+=localcount
        counters.append({'sticker':index,'regions_vectorielles':localcount})
    _validate_safe_svg(target)
    dest=work/REGION_SVG
    ET.ElementTree(target).write(dest,encoding='utf-8',xml_declaration=True)
    qa=analyze_svg(dest)
    if qa['chemins']>5000:raise UnsafeCut('Regions : depasse la limite 5000 chemins Cricut')
    return {'fichier':REGION_SVG,'regions_total':all_regions,'par_sticker':counters,
            'nombre_chemins':qa['chemins']}


def make_individual_svgs(work:Path,sticker_count:int):
    """A per-sticker Cricut SVG crop with physically correct millimetre sizing.

    The one-sheet outputs remain the primary delivery. These files let users
    edit ONE snail independently without navigating a 12-sticker graph.
    """
    root=ET.parse(work/CRICUT_SVG).getroot()
    global_x,global_y,global_w,global_h=_viewbox(root)
    width_mm=_mm(root.get('width'))
    height_mm=_mm(root.get('height'))
    if abs(width_mm/global_w-height_mm/global_h)>0.0001:
        raise UnsafeCut('Dimensions physiques incoherentes avec viewBox')
    scale=width_mm/global_w
    cut=_cut_paths(work,sticker_count)
    groups={g.get('id'):g for g in root if g.tag==SVG+'g'}
    dest=work/SINGLES
    dest.mkdir(exist_ok=True)
    items=[]
    for idx in range(1,sticker_count+1):
        key=f'STICKER_{idx:02d}'
        if key not in groups:raise UnsafeCut('Sticker absent de la planche SVG : '+key)
        coordinates=[(int(x),int(y)) for x,y in _COORD.findall(cut[idx])]
        if len(coordinates)<3:raise UnsafeCut('Contour sticker vide')
        xs=[x for x,y in coordinates];ys=[y for x,y in coordinates]
        pad=5
        x0=min(xs)-pad; y0=min(ys)-pad
        w=max(xs)-min(xs)+2*pad; h=max(ys)-min(ys)+2*pad
        out=ET.Element(SVG+'svg',{'width':f'{scale*w:.4f}mm','height':f'{scale*h:.4f}mm',
                                   'viewBox':f'{x0} {y0} {w} {h}','version':'1.1'})
        out.append(copy.deepcopy(groups[key]))
        _validate_safe_svg(out)
        filename=f'STICKER_{idx:02d}_EDITABLE.svg'
        file=dest/filename
        ET.ElementTree(out).write(file,encoding='utf-8',xml_declaration=True)
        a=analyze_svg(file)
        items.append({'sticker':idx,'fichier':f'{SINGLES}/{filename}',
                      'dimensions_mm':[round(scale*w,3),round(scale*h,3)],
                      'chemins':a['chemins']})
    return items


def alpha_preflight(work:Path, svg_name=CRICUT_SVG, tolerance=4):
    """Checks flattened SVG silhouette vs actual print PNG, not just cut-only SVG.

    Minor renderer disagreement and polygon approximation can extend 1–4px.
    Areas further than 4 pixels from the expected mask are considered material.
    The report remains explicit about exact maximum tolerance.
    """
    try:
        import cairosvg
    except (ImportError, OSError) as e:
        return {'teste':False,'motif':f'CairoSVG indisponible: {str(e)[:130]}',
                'verification_raster_svg_ok':False,'validation_design_space_reelle':False}
    png=np.asarray(Image.open(work/NAME).convert('RGBA'))
    h,w=png.shape[:2]
    data=cairosvg.svg2png(url=str(work/svg_name),output_width=w,output_height=h)
    rendered=np.asarray(Image.open(io.BytesIO(data)).convert('RGBA'))
    a=png[...,3]>127;b=rendered[...,3]>127
    if not np.any(a):raise UnsafeCut('Print Then Cut : image sans contenu')
    kernel=cv2.getStructuringElement(cv2.MORPH_RECT,(2*tolerance+1,2*tolerance+1))
    miss=(a & ~(cv2.dilate(b.astype('uint8'),kernel)>0))
    extra=(b & ~(cv2.dilate(a.astype('uint8'),kernel)>0))
    serious=int(miss.sum()+extra.sum())
    reference=int(a.sum())
    ratio=100*serious/reference
    if ratio>0.02:raise UnsafeCut(f'SVG: {ratio:.3f}% de defauts silhouette au-dela de {tolerance}px')
    # Separate cosmetic contour rasterization from interior errors.
    fine=cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))
    miss_fine=a & ~(cv2.dilate(b.astype('uint8'),fine)>0)
    extra_fine=b & ~(cv2.dilate(a.astype('uint8'),fine)>0)
    fine_pct=100*float(miss_fine.sum()+extra_fine.sum())/reference
    return {'teste':True,'fichier':svg_name,'pixels_reference':reference,
            'tolerance_bord_pixels':tolerance,'manquants_hors_tolerance':int(miss.sum()),'excedents_hors_tolerance':int(extra.sum()),
            'ecart_total_brut_pct':round(float(100*np.count_nonzero(a^b)/reference),4),
            'ecart_hors_tolerance_pct':round(float(ratio),5),
            'ecart_hors_2px_pct':round(float(fine_pct),5),
            'avertissement_bord':('Difference de contour de plus de 2px : examiner visuellement' if fine_pct>0.02 else None),
            'verification_raster_svg_ok':True,'validation_design_space_reelle':False,
            'note':'Le rendu SVG a ete compare au masque d impression; la decoupe physique reste a tester.'}


def process_v15(rgb, output_dir, *, layout='auto',intent='auto',ia_mode='auto',ai_masker=None,
                alpha=None,sheet_width_mm=180,margin_mm=1.5,editable_colors=10,runtime_rmbg_stats=None):
    base=Path(output_dir).expanduser();base.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix='.SmartSVG_V15_TEMP_',dir=base))
    try:
        report,preview=process_v141(rgb,str(temp),layout=layout,intent=intent,
            ia_mode=ia_mode,ai_masker=ai_masker,alpha=alpha,
            sheet_width_mm=sheet_width_mm,margin_mm=margin_mm,
            editable_colors=editable_colors,runtime_rmbg_stats=runtime_rmbg_stats)
        work=Path(report['output'])
        if not work.is_dir() or work.parent!=temp:raise UnsafeCut('Repertoire temporaire inattendu')
        expected=report['audit_v141']['stickers']
        # Actual overall edition SVG silhouette must match the print artwork.
        qa=alpha_preflight(work)
        region=make_region_svg(work,expected)
        individuals=make_individual_svgs(work,expected)
        # Also evaluate the region-editor silhouette separately if CairoSVG is present.
        qa_region=alpha_preflight(work,REGION_SVG)
        compact=analyze_svg(work/CRICUT_SVG)
        assert len(individuals)==expected
        audit={'version':VERSION,'nombre_stickers':expected,'controle_svg_compact':qa,
               'controle_svg_regions':qa_region,'regions_editables':region,
               'fichiers_individuels':individuals,
               'limite_cricut_5000_respectee':compact['chemins']<=5000 and region['nombre_chemins']<=5000,
               'segmentation_semantique':False,'validation_gpu_reelle':False,
               'validation_design_space_reelle':False,'validation_machine_reelle':False}
        final=base/('SmartSVG_V15_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8])
        report['output']=str(final);report['version']=VERSION;report['audit_v15']=audit
        # Only ONE ready/manifest at the root. Keep previous reports as diagnostics.
        archive=work/'DETAILS_ELEMENTS'/'RAPPORTS_PRECEDENTS';archive.mkdir(parents=True,exist_ok=True)
        for name in ('PRET_V14_1.json','rapport_V14_1.json','A_LIRE_CRICUT_V14_1.txt'):
            p=work/name
            if p.exists():os.replace(p,archive/name)
        (work/'rapport_V15.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=_json_default),encoding='utf8')
        (work/'LIRE_EN_PREMIER.txt').write_text(
            'SMARTSVG STUDIO 15 — UTILISATION CRICUT\n\n'
            '1. Impression fidele : IMPORT_CRICUT_IMPRIMER_DECOUPER.png. Importer en image PLATE, et verifier dimensions et formes dans Design Space.\n'
            '2. Edition RAPIDE : CRICUT_EDITION_CALQUES_COULEURS.svg (1 groupe/sticker, 1 forme/couleur).\n'
            '3. Edition PLUS PRECISE : CRICUT_EDITION_REGIONS_INDEPENDANTES.svg (formes par regions de couleur).\n'
            '4. Un seul personnage : fichiers du sous-dossier EDITER_STICKERS_SEPAREMENT.\n'
            '5. Pour un SVG multicouche, selectionner les calques puis APLATIR pour Imprimer puis decouper.\n'
            '6. NE PAS importer le SVG de contours en plus de la planche PNG : risque de double decoupe.\n'
            '7. Il ne s agit PAS encore de calques semantiques par yeux/coquille/corps.\n'
            '8. Le rendu visuel SVG peut simplifier les ombres/degrades. Un test physique reste indispensable.\n',
            encoding='utf8')
        def all_files_with_hashes():
            result={}
            for p in sorted(work.rglob('*')):
                if p.is_file() and p.name!='PRET_V15.json':
                    rel=p.relative_to(work).as_posix()
                    digest=hashlib.sha256(p.read_bytes()).hexdigest()
                    result[rel]={'octets':p.stat().st_size,'sha256':digest}
            return result
        status={'version':VERSION,'statut':'CONTROLES_GEOMETRIQUES_REUSSIS' if qa['teste'] and qa_region['teste'] else 'AVERTISSEMENT_RENDU_SVG_NON_VERIFIE',
            'nombre_stickers':expected,'export_principal':NAME,'svg_rapide':CRICUT_SVG,'svg_regions':REGION_SVG,
            'svg_individuels':SINGLES,'validation_cricut_reelle':False,'fichiers':all_files_with_hashes()}
        (work/'PRET_V15.json').write_text(json.dumps(status,ensure_ascii=False,indent=2,default=_json_default),encoding='utf8')
        os.replace(work,final)
        return report,preview
    except Exception as exc:
        (base/('SmartSVG_ECHEC_V15_'+uuid.uuid4().hex[:8]+'.json')).write_text(
            json.dumps({'statut':'ECHEC_NON_PUBLIE','message':str(exc)},ensure_ascii=False,indent=2),encoding='utf8')
        raise UnsafeCut('SmartSVG V15: export refuse: '+str(exc)) from exc
    finally:
        shutil.rmtree(temp,ignore_errors=True)
