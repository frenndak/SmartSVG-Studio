"""SmartSVG V14: audited Cricut-color-layer export, on top of V13's cut geometry.

IMPORTANT: This is not semantic object reconstruction. Color areas are made
more editable for Design Space by merging the same color PER STICKER into one
compound SVG path, without raster images, text or gradients.
"""
from __future__ import annotations
import copy
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import uuid
import xml.etree.ElementTree as ET

from .engine_v11 import UnsafeCut
from .engine_v12 import _json_default
from .engine_v13 import (process_v13, _compare_cut_with_png, _cut_paths,
                         _translation_of_group, _manifest, SVG)

CRICUT_SVG='CRICUT_EDITION_CALQUES_COULEURS.svg'
CRICUT_SVG_DETAIL='CRICUT_EDITION_DETAILLEE.svg'
NAME='IMPORT_CRICUT_IMPRIMER_DECOUPER.png'
ROUNDING='%.3f'
POINTS=re.compile(r'(-?\d+),(-?\d+)')
HEX=re.compile(r'#[0-9a-fA-F]{6}\Z')


def _local_cut_path(d,tx,ty):
    """Build local polygon path for same position after outer g translation."""
    if not re.fullmatch(r'M-?\d+,-?\d+(?: L-?\d+,-?\d+){2,} Z', d):
        raise UnsafeCut('Polygone de base inattendu')
    pts=[(int(x)-tx,int(y)-ty) for x,y in POINTS.findall(d)]
    return 'M'+ ' L'.join(f'{x:.3f},{y:.3f}' for x,y in pts)+' Z'


def _compact_colored_layers(folder, expected, *, source='planche_EDITABLE_SIMPLIFIE.svg', destination=CRICUT_SVG):
    src_root=ET.parse(folder/source).getroot()
    attrs={k:src_root.get(k) for k in ('width','height','viewBox')}
    if not all(attrs.values()):raise UnsafeCut('SVG editable sans dimensions physiques')
    dst=ET.Element(SVG+'svg', {**attrs,'version':'1.1'})
    src_groups=[g for g in src_root if g.tag==SVG+'g']
    if len(src_groups)!=expected: raise UnsafeCut('Nombre de personnages du SVG editable incorrect')
    cut=_cut_paths(folder,expected)
    layers=[]
    total_colorpaths=0
    for idx,source in enumerate(src_groups,1):
        if source.get('id') != f'STICKER_{idx:02d}':
            raise UnsafeCut(f'Ordre ou identifiant sticker incorrect ({idx})')
        tx,ty=_translation_of_group(source)
        group=ET.SubElement(dst,SVG+'g',{
            'id':f'STICKER_{idx:02d}',
            'transform':f'translate({tx:.3f} {ty:.3f})'})
        ET.SubElement(group,SVG+'path',{'id':f'S{idx:02d}_BASE_BORDURE_BLANCHE',
             'd':_local_cut_path(cut[idx],tx,ty),'fill':'#ffffff','fill-rule':'nonzero'})
        colors=[]
        for child in list(source):
            if child.get('data-role')=='white-cut-offset' or child.get('id','').endswith('_FOND'):
                continue
            if child.tag!=SVG+'g':raise UnsafeCut('Element inattendu dans le SVG de couleurs')
            fill=(child.get('fill') or '').strip().lower()
            if not HEX.fullmatch(fill):raise UnsafeCut(f'Couleur non unie : {fill}')
            paths=list(child)
            if any(p.tag!=SVG+'path' for p in paths):raise UnsafeCut('Element non vectoriel dans une couche couleur')
            ds=[]
            for p in paths:
                if p.get('transform') or p.get('opacity') or p.get('clip-path') or p.get('filter'):
                    raise UnsafeCut('Transformation/effet non convertible en calque Cricut')
                for k in ('stroke','style','mask','fill'):
                    if p.get(k):raise UnsafeCut(f'Attribut inattendu dans une forme de couleur : {k}')
                if p.get('fill-rule','evenodd')!='evenodd':raise UnsafeCut('Regle de remplissage inattendue')
                d=p.get('d','').strip()
                if not d or not d[0].upper()=='M':raise UnsafeCut('Chemin couleur vide/invalide')
                ds.append(d)
            if ds:
                # same color group is a single editable cut/color layer
                ET.SubElement(group, SVG+'path', {
                    'id':f'S{idx:02d}_COULEUR_{len(colors)+1:02d}_{fill[1:].upper()}',
                    'fill':fill,'fill-rule':'evenodd','d':' '.join(ds)})
                colors.append(fill)
                total_colorpaths+=1
        layers.append({'sticker':idx,'couches_recoloriables':len(colors),'couleurs':colors})
    count=len(list(dst.iter(SVG+'path')))
    if count>5000: raise UnsafeCut(f'SVG Cricut de {count} chemins (limite 5000)')
    if count != expected+total_colorpaths: raise UnsafeCut('Nombre de chemins Cricut incoherent')
    # Fail on tags unsupported by our audited subset before publishing.
    allowed={SVG+'svg',SVG+'g',SVG+'path'}
    if any(el.tag not in allowed for el in dst.iter()):raise UnsafeCut('Export SVG contient un element interdit')
    outfile=folder/destination
    ET.ElementTree(dst).write(outfile,encoding='utf-8',xml_declaration=True)
    reread=ET.parse(outfile).getroot()
    if len(list(reread.iter(SVG+'path')))!=count:raise UnsafeCut('SVG reimporte incomplet')
    return {'fichier':destination,'groupes_independants':expected,
            'calques_couleur':total_colorpaths,
            'calques_bordure_blanche':expected,'chemins_svg':count,
            'regroupements':layers,'elements_svg_supportes':['svg','g','path'],
            'contient_images_textes_filtres_degrades':False}


def _save_readme(folder, qa, expected, width, height):
    (folder/'MODE_EMPLOI_CRICUT_V14.txt').write_text(
       f'''SMARTSVG V14 — POUR CRICUT DESIGN SPACE (version beta)

UNE PLANCHE / {expected} DESSINS. TAILLE NOMINALE : {width:.2f} x {height:.2f} mm.

A. POUR UNE IMPRESSION FIDELE ET UN CONTOUR PROPRE :
   1) Televerser {NAME} dans Design Space.
   2) Choisir une image pour Imprimer puis decouper.
   3) Verifier taille, bords et apercu AVANT l'impression.
   4) Ne PAS superposer le SVG de contours (sinon risque double decoupe).

B. POUR RETOUCHER LES COULEURS DIRECTEMENT DANS DESIGN SPACE :
   1) Televerser {CRICUT_SVG} ; conserver ses dimensions.
   2) Pour conserver davantage de nuances : utiliser {CRICUT_SVG_DETAIL}.
   3) Degrouper le sticker a modifier, puis recolorer les couches.
   4) Les couches sont des ZONES DE COULEUR, pas des objets IA (yeux, coquille).
   5) Une fois la composition prete : selectionner et APLATIR (Print Then Cut).
   6) Verifier qu'il y a {expected} silhouettes dans l'apercu Machine.
   7) Faire un test papier.

ATTENTION : le SVG vectoriel a couleurs plates simplifiees ne reproduit pas
l'aspect photographique / ombrage du PNG d'origine. Le PNG original est donc
le meilleur choix quand la fidelite des images est prioritaire.

Les dimensions maximales Print Then Cut dependent de la machine, du papier
et de la forme de la planche. Verifier dans Design Space.
La reelle decoupe n'a pas ete testee physiquement par ce logiciel.
''',encoding='utf-8')


def process_v14(rgb, output_dir, *, layout='auto', intent='auto', ia_mode='auto',
                ai_masker=None,alpha=None,sheet_width_mm=180,margin_mm=1.5,editable_colors=10):
    base=Path(output_dir).expanduser()
    base.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='.SmartSVG_V14_TEMP_',dir=base))
    try:
        report, preview=process_v13(rgb,str(staging),layout=layout,intent=intent,
            ia_mode=ia_mode,ai_masker=ai_masker,alpha=alpha,
            sheet_width_mm=sheet_width_mm,margin_mm=margin_mm,
            editable_colors=editable_colors)
        work=Path(report['output'])
        if not work.is_dir() or work.parent!=staging:
            raise UnsafeCut('Sortie de la V13 pas dans le stage attendu')
        expected=int(report['qa_v11']['dessins'])
        compare,_=_compare_cut_with_png(work,expected)
        compact=_compact_colored_layers(work,expected)
        detailed=_compact_colored_layers(work,expected,source='planche_EDITABLE_DETAILLE.svg',destination=CRICUT_SVG_DETAIL)
        for obsolete in ('PRET_V13.json','rapport_V13.json','LIRE_AVANT_CRICUT_V13.txt'):
            p=work/obsolete
            if p.exists():p.unlink()
        fin=base/('SmartSVG_V14_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8])
        width,height=map(float,report['qa_v11']['taille_planche_mm'])
        _save_readme(work,compact,expected,width,height)
        record={'version':'14.0-beta','cricut_editing':compact,'cricut_editing_detaille':detailed,
            'contours_confirmes':compare,'image_principale':NAME,
            'taille_nominale_mm':[width,height],
            'images_et_calques_differents':True,
            'limite_5000_chemins_respectee':True,
            'validation_machine_effectuee':False,
            'segmentation_semantique':False,
            'notes':'Recoloration des zones de couleur, pas extraction d objets.'}
        report['version']='14.0-beta'
        report['output']=str(fin)
        report['rapport_qualite_v14']=record
        report['rapport_qualite_v12']['dossier_unique']=str(fin)
        (work/'rapport_V14.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,default=_json_default),encoding='utf8')
        (work/'PRET_V14.json').write_text(json.dumps({
            'version':'14.0-beta', 'statut':'CONTROLES_FICHIERS_REUSSIS',
            'import_print_then_cut':NAME,'svg_recoloriable':CRICUT_SVG,'svg_detaille':CRICUT_SVG_DETAIL,
            'validation_cricut_reelle':False,'fichiers':_manifest(work)},
            ensure_ascii=False,indent=2,default=_json_default),encoding='utf8')
        os.replace(work,fin)
        return report,preview
    except Exception as e:
        (base/('SmartSVG_ECHEC_V14_'+uuid.uuid4().hex[:8]+'.json')).write_text(
           json.dumps({'statut':'ECHEC_EXPORT_NON_PUBLIE','raison':str(e)},
                      ensure_ascii=False,indent=2),encoding='utf8')
        raise UnsafeCut(f'V14: export refuse : {e}') from e
    finally:
        shutil.rmtree(staging,ignore_errors=True)
