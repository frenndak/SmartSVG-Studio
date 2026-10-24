"""SmartSVG V14.1. QA enhancements on top of a known cut geometry engine."""
from __future__ import annotations
from collections import Counter
from datetime import datetime
from pathlib import Path
from io import BytesIO
import hashlib
import json
import os
import re
import shutil
import tempfile
import uuid
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image
from .engine_v11 import UnsafeCut
from .engine_v12 import _json_default
from .engine_v13 import _manifest, SVG
from .engine_v14 import process_v14, CRICUT_SVG, CRICUT_SVG_DETAIL, NAME

VERSION='14.1-beta'
SVG_NAMES={'svg_compact':CRICUT_SVG,'svg_detaille':CRICUT_SVG_DETAIL}
# Moderate guideposts only: compound paths and CPU time can be high even when
# SVG element count is lower than Cricut's hard 5000-path limit.
COMPLEXITY_WARN={'segments':10000,'sous_chemins':950}

def analyze_svg(path):
    root=ET.parse(path).getroot()
    paths=list(root.iter(SVG+'path'))
    if len(paths)>5000:raise UnsafeCut('SVG depasse 5000 chemins Cricut')
    totals=Counter()
    for p in paths:
        d=p.get('d','')
        # Count SVG command letters, not letters in attributes.
        counts=Counter(re.findall(r'[MmLlHhVvCcSsQqTtAaZz]',d))
        totals['sous_chemins']+=counts['M']+counts['m']
        totals['cubic_beziers']+=counts['C']+counts['c']
        totals['segments']+=sum(v for cmd,v in counts.items() if cmd.upper() not in ('M','Z'))
        totals['fermatures']+=counts['Z']+counts['z']
    tags={el.tag.rsplit('}',1)[-1] for el in root.iter()}
    if tags-{'svg','g','path'}:raise UnsafeCut('SVG Cricut contient des elements inattendus: '+str(tags))
    return {'chemins':len(paths),'sous_chemins':totals['sous_chemins'],
            'segments':totals['segments'],'beziers_cubiques':totals['cubic_beziers'],
            'taille_octets':path.stat().st_size,
            'avertissements':(['Nombre de segments eleve'] if totals['segments']>COMPLEXITY_WARN['segments'] else []) +
               (['Beaucoup de sous-chemins dans les formes composees'] if totals['sous_chemins']>COMPLEXITY_WARN['sous_chemins'] else [])}

def image_fidelity(folder, name):
    """Compare a rendered SVG to the ACTUAL PNG for print; not other SVGs.

    CairoSVG optional: Windows installs without Cairo need no new dependency.
    Missing CairoSVG is reported explicitly as 'not tested'.
    """
    try:
        import cairosvg
    except (ImportError,OSError) as exc:
        return {'mesure_effectuee':False,'motif':'CairoSVG indisponible: '+str(exc)[:150]}
    with Image.open(folder/NAME) as png:
        target=np.asarray(png.convert('RGBA')).copy()
    h,w=target.shape[:2]
    try:
        raw=cairosvg.svg2png(url=str(folder/name),output_width=w,output_height=h)
        rendered=np.asarray(Image.open(BytesIO(raw)).convert('RGBA')).copy()
    except Exception as exc:
        return {'mesure_effectuee':False,'motif':'Rendu du SVG indisponible: '+str(exc)[:150]}
    alpha=target[...,3]>0
    if int(alpha.sum())==0:raise UnsafeCut('PNG impression vide')
    # SVG may AA edge; compare colors against same compositing to white for
    # consistent interpretation near antialiased edges.
    source=target[...,:3].astype(np.float32)
    r=rendered[...,:3].astype(np.float32)
    src_comp=source * (target[...,3:4]/255.) + 255*(1-target[...,3:4]/255.)
    ren_comp=r * (rendered[...,3:4]/255.) + 255*(1-rendered[...,3:4]/255.)
    dif=np.abs(src_comp-ren_comp).mean(axis=2)[alpha]
    return {'mesure_effectuee':True,'ecart_moyen_rgb':round(float(dif.mean()),3),
            'pixels_ecart_plus_de_20_pct':round(float(np.mean(dif>20)*100),2),
            'pixels_ecart_plus_de_40_pct':round(float(np.mean(dif>40)*100),2),
            'reference':'PNG_PRINT ORIGINAL, pas SVG V13/V14',
            'avertissement':('Le SVG simplifie differe sensiblement du PNG a imprimer' if float(dif.mean())>12 else None)}

def process_v141(rgb, output_dir, *, layout='auto',intent='auto',ia_mode='auto',
                 ai_masker=None,alpha=None,sheet_width_mm=180,margin_mm=1.5,
                 editable_colors=10,runtime_rmbg_stats=None):
    base=Path(output_dir).expanduser()
    base.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='.SmartSVG_V141_TEMP_',dir=base))
    try:
        report,preview=process_v14(rgb,str(staging),layout=layout,intent=intent,
            ia_mode=ia_mode,ai_masker=ai_masker,alpha=alpha,
            sheet_width_mm=sheet_width_mm,margin_mm=margin_mm,editable_colors=editable_colors)
        work=Path(report['output'])
        if not work.is_dir() or work.parent!=staging:
            raise UnsafeCut('V14: sortie inattendue hors repertoire de staging')
        expected=int(report['qa_v11']['dessins'])
        used=sum(1 for item in report['items'] if item.get('mask_used')=='IA_locale')
        attempted=sum(bool(item.get('ai_called')) for item in report['items'])
        failed=[{'sticker':int(item['index']),'statut':item.get('ai_status')} for item in report['items']
                if str(item.get('ai_status','')).startswith('echec_IA')]
        if ia_mode=='forcer' and used!=expected:
            raise UnsafeCut('IA forcee: tous les stickers doivent utiliser un masque IA')
        if runtime_rmbg_stats is None:runtime_rmbg_stats=[]
        if attempted==0:state='NON_UTILISEE (image jugée simple ou IA désactivée)'
        elif used==expected and not failed:state='UTILISEE SUR TOUS LES STICKERS'
        elif used>0:state='PARTIELLE: masques IA et classiques melanges'
        else:state='TENTEE MAIS AUCUN MASQUE IA RETENU'
        audit={'stickers':expected,'ia':{'mode':ia_mode,'etat':state,'tentatives':attempted,
              'utilises':used,'echecs':failed,'inferences':list(runtime_rmbg_stats)},
              'complexite_svg':{key:analyze_svg(work/filename) for key,filename in SVG_NAMES.items()},
              'fidelite_png':{key:image_fidelity(work,filename) for key,filename in SVG_NAMES.items()},
              'validation_cricut_reelle':False,'segmentation_semantique':False,
              'explication':'Les zones couleurs sont editables, pas des objets comme oeil/coquille.'}
        warnings=[]
        for key,record in audit['fidelite_png'].items():
            if record.get('avertissement'):warnings.append(f'{key}: {record["avertissement"]}')
        for key,record in audit['complexite_svg'].items():
            for w in record['avertissements']:warnings.append(f'{key}: {w}')
        if attempted and not used:warnings.append('IA tentee mais rejetee: verifier rapport et masque source')
        audit['avertissements']=warnings
        # Replace the misleading old READY manifest, keep previous engine reports
        # for diagnostics while publishing a single ready-to-use v14.1 manifest.
        (work/'PRET_V14.json').unlink(missing_ok=True)
        # Previous intermediate reports refer to historical staged paths. Keep
        # them for diagnosis, but do not confuse the user with two READY reports.
        diagnostics=work/'DETAILS_ELEMENTS'/'DIAGNOSTICS_VERSIONS_ANTERIEURES'
        for obsolete in ('rapport_V14.json','MODE_EMPLOI_CRICUT_V14.txt'):
            source=work/obsolete
            if source.is_file():
                diagnostics.mkdir(parents=True,exist_ok=True)
                os.replace(source,diagnostics/obsolete)
        final=base/('SmartSVG_V14_1_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8])
        report['version']=VERSION
        report['output']=str(final)
        report['audit_v141']=audit
        (work/'rapport_V14_1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=_json_default),encoding='utf8')
        (work/'A_LIRE_CRICUT_V14_1.txt').write_text(
             f'SmartSVG 14.1 - {expected} sticker(s) sur une seule planche.\n'
             f'Pour impression fidele : IMPORT_CRICUT_IMPRIMER_DECOUPER.png.\n'
             f'Pour recoloration : {CRICUT_SVG} (aplatissement a verifier dans Design Space).\n'
             'Ne pas importer les contours SVG en superposition du PNG.\n'
             f'IA : {state}.\n'
             'Design Space : importer, verifier dimensions / contour, imprimer et faire un essai papier.\n'
             'Pas de couches semantiques type Magic Layers.\n',encoding='utf8')
        (work/'PRET_V14_1.json').write_text(json.dumps({
             'statut':'CONTROLES_LOGICIELS_REUSSIS' if not warnings else 'AVERTISSEMENTS_A_CONTROLER',
             'version':VERSION,'fichier_principal_png':NAME,
             'fichier_svg_cricut':CRICUT_SVG,'validation_cricut_reelle':False,
             'fichiers':_manifest(work)},ensure_ascii=False,indent=2,default=_json_default),encoding='utf8')
        os.replace(work,final)
        return report,preview
    except Exception as e:
        (base/('SmartSVG_ECHEC_V141_'+uuid.uuid4().hex[:8]+'.json')).write_text(
            json.dumps({'statut':'ECHEC_EXPORT_NON_PUBLIE','raison':str(e)},ensure_ascii=False,indent=2),encoding='utf8')
        raise UnsafeCut('SmartSVG V14.1: export refuse: '+str(e)) from e
    finally:
        shutil.rmtree(staging,ignore_errors=True)
