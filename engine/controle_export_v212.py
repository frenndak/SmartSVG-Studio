"""V21.2: non-destructive, source-backed quality sheets and export verification.

This evaluates exported geometry and file consistency, NOT semantic segmentation
accuracy or actual Cricut hardware behavior.  Staging/publication handled in run_v212.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from uuid import uuid4
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from . import production_v211 as legacy

class QAError(legacy.StudioError):pass

MAX_IMAGE_PIXELS=28_000_000
MAX_SVG_BYTES=3_000_000
MAX_OBJECTS_PREVIEW=32


def _safe(project, path):
    if path is None: return None
    p=Path(path)
    if not p.is_absolute():p=project/p
    try:rel=legacy._relative_under(p,project)
    except legacy.StudioError as exc:raise QAError(str(exc)) from exc
    target=project/rel
    if target.is_symlink() or not target.is_file():raise QAError('Sortie manquante ou lien symbolique: '+str(rel))
    return target


def _read_png(path):
    with Image.open(path) as im:
        if im.width<1 or im.height<1 or im.width*im.height>MAX_IMAGE_PIXELS:
            raise QAError('Dimensions PNG de sortie non raisonnables')
        return im.convert('RGBA').copy(),im.info.get('dpi')


def _svg_width_mm(svg_path):
    """Read the width of the actual SVG root, never an XML comment or child.

    SVGs come from our exporter, but quality checks must still reject a
    malformed or deceptive document. Do not permit DTD/entity definitions.
    """
    if svg_path is None:return None
    if svg_path.stat().st_size>MAX_SVG_BYTES:
        raise QAError('SVG trop volumineux pour validation automatique')
    s=svg_path.read_text(encoding='utf8')
    if re.search(r'<!\s*(?:DOCTYPE|ENTITY)\b',s,re.I):
        raise QAError('SVG avec declaration DTD/ENTITY interdite')
    try:root=ET.fromstring(s)
    except ET.ParseError as exc:
        raise QAError('SVG invalide pour le precontrole Cricut') from exc
    if root.tag.rsplit('}',1)[-1]!='svg':return None
    m=re.fullmatch(r'\s*(\d+(?:\.\d+)?)mm\s*',root.attrib.get('width',''))
    if not m:return None
    value=float(m.group(1))
    if not math.isfinite(value) or value<=0 or value>5000:
        raise QAError('Largeur SVG incoherente')
    return value


def _alpha_metrics(alpha):
    active=np.uint8(alpha>=128)
    n,_,stats,_=cv2.connectedComponentsWithStats(active,8)
    areas=sorted((int(s[cv2.CC_STAT_AREA]) for s in stats[1:]),reverse=True)
    total=int(active.sum())
    h,w=active.shape
    contours,hierarchy=cv2.findContours(active,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    holes=(sum(1 for hinfo in hierarchy[0] if hinfo[3]>=0)
           if hierarchy is not None else 0)
    border=bool(active[0].any() or active[-1].any() or active[:,0].any() or active[:,-1].any())
    return {'masque_surface_px':total,'surface_relative':round(total/(h*w),5),
            'composantes':len(areas),'aire_fragments_hors_principal_px':sum(areas[1:]),
            'trous':holes,'touche_bord_fichier':border,
            'pixels_transparence_partielle':int(((alpha>0)&(alpha<255)).sum())}


def _thumb(img,size=160,background=(245,245,245)):
    tile=Image.new('RGB',(size,size),background)
    tmp=img.copy();tmp.thumbnail((size-12,size-12),Image.Resampling.LANCZOS)
    tile.paste(tmp,((size-tmp.width)//2,(size-tmp.height)//2),tmp if tmp.mode=='RGBA' else None)
    return tile


def _sha(path):
    hasher=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):hasher.update(chunk)
    return hasher.hexdigest()


def audit_staged_exports(stage,report,final,dpi):
    """Generate QA PNGs and JSON *inside staged production project*.

    Report paths may still point to stage. Returns a new diagnostics dict whose
    paths already point to final. No changes to printable source files.
    """
    project=Path(stage).resolve(); final=Path(final).absolute()
    qa_dir=project/'05_CONTROLE_V21_2';qa_dir.mkdir(exist_ok=False)
    objects=report.get('objets',[])
    if len(objects)>32:raise QAError('Nombre de sorties trop important pour QA')
    rows=[];thumbs=[];alerts=[]
    is_rectangle=(report.get('operation')=='carte_rectangle' or
                  report.get('v21',{}).get('mode')=='CADRE_RECTANGULAIRE_CHOISI')
    src=_safe(project,project/'SOURCE_ORIGINALE.png')
    source_img,_=_read_png(src)
    for i,obj in enumerate(objects,1):
        p=_safe(project,obj.get('fichier_png_cricut') or obj.get('png'))
        svg=_safe(project,obj.get('fichier_svg_contour') or obj.get('svg_contour'))
        native=_safe(project,obj.get('fichier_transparent')) if obj.get('fichier_transparent') else None
        if p is None: continue
        print_img,metadata_dpi=_read_png(p)
        alpha=np.asarray(print_img.getchannel('A'))
        native_image,_=_read_png(native) if native else (None,None)
        met=_alpha_metrics(alpha)
        svg_mm=_svg_width_mm(svg)
        physical=round(print_img.width*25.4/dpi,3)
        flags=[]
        if svg is not None and svg_mm is None:flags.append('SVG_SANS_LARGEUR_MM')
        if svg_mm is not None and abs(svg_mm-physical)>25.4/dpi+0.012:
            flags.append('ECART_DIMENSION_PNG_SVG')
        if met['composantes']>1:flags.append('COUPES_POTENTIELLEMENT_MULTIPLES')
        # A deliberately rectangular card is supposed to touch its canvas edges.
        # This is only a risk for cut-out stickers with an intended outer margin.
        if met['touche_bord_fichier'] and not is_rectangle:
            flags.append('DECOUPE_TOUCHE_BORD_DU_FICHIER')
        if native_image is not None:
            nat_alpha=np.asarray(native_image.getchannel('A'))
            nat_metrics=_alpha_metrics(nat_alpha)
            if nat_metrics['composantes']>1:flags.append('SUJET_SOURCE_FRAGMENTE')
            if nat_metrics['touche_bord_fichier']:flags.append('SUJET_SOURCE_COUPE_OU_TROP_SERRE')
        else:nat_metrics=None
        if obj.get('avertissements'):
            flags.extend(str(f) for f in obj['avertissements']
                         if not (is_rectangle
                                 and str(f)=='DECOUPE_TOUCHE_BORD_DU_FICHIER'))
        flags=list(dict.fromkeys(flags))
        status='RISQUE_ELEVE' if any(x in flags for x in (
            'ECART_DIMENSION_PNG_SVG','SVG_SANS_LARGEUR_MM',
            'DECOUPE_TOUCHE_BORD_DU_FICHIER')) else 'A_VERIFIER'
        info={'numero':i,'fichier_png_cricut':str(final/p.relative_to(project)),
              'sha256_png_cricut':_sha(p),'svg':str(final/svg.relative_to(project)) if svg else None,
              'largeur_png_px':print_img.width,'hauteur_png_px':print_img.height,
              'largeur_png_mm_si_ppp_respectes':physical,
              'largeur_svg_mm':svg_mm,
              'metadonnees_ppp':list(metadata_dpi) if metadata_dpi else None,
              'geometrie_imprimable':met,'geometrie_originale':nat_metrics,
              'avertissements':flags,'verdict':'A_VERIFIER' if status=='A_VERIFIER' else status,
              'precision_semantique_mesuree':False,'decoupe_cricut_certifiee':False}
        rows.append(info);alerts.extend(flags)
        panel=Image.new('RGB',(540,210),'white')
        draw=ImageDraw.Draw(panel)
        for col,kind in enumerate((source_img,native_image or print_img,print_img)):
            panel.paste(_thumb(kind,155),(10+col*178,27))
        for x,label in ((10,'SOURCE'),(188,'DETOURE' if native is not None else 'VISUEL'),(366,'IMPRESSION')):
            draw.text((x,7),label,fill=(35,35,35))
        draw.text((11,191),f'{i:02d}  |  {physical:.1f} mm  |  {status}',fill=(35,35,35))
        if i<=MAX_OBJECTS_PREVIEW:
            rel=f'05_CONTROLE_V21_2/OBJET_{i:02d}_AVANT_APRES.png'
            legacy.old._save_png(project/rel,panel,96)
            info['apercu']=str(final/rel)
            thumbs.append(panel)
    if thumbs:
        count=min(len(thumbs),24)
        board=Image.new('RGB',(540*2,210*math.ceil(count/2)),(250,250,250))
        for i,panel in enumerate(thumbs[:count]):board.paste(panel,((i%2)*540,(i//2)*210))
    else:
        board=Image.new('RGB',(700,180),'white')
        ImageDraw.Draw(board).text((16,16),'AUCUN MASQUE SEGMENTE - SORTIES COMPLETES / CADRES SEULEMENT',fill='black')
    legacy.old._save_png(qa_dir/'APERÇU_GLOBAL.png',board,96)
    audit={'version':'21.2-beta','nombre_objets_inspectes':len(rows),
        'statut':'A_VERIFIER_AVANT_CRICUT',
        'annotations_de_reference_fournies':False,
        'precision_semantique_mesuree':False,
        'modele_IA_execute_sur_GPU_local_prouve':False,
        'controle_sur_fichiers_reellement_exportes':True,
        'taille_dans_design_space_a_verifier':True,
        'aucun_fichier_cricut_modifie_par_QA':True,
        'apercu_global':str(final/'05_CONTROLE_V21_2/APERÇU_GLOBAL.png'),
        'alertes':dict((k,alerts.count(k)) for k in sorted(set(alerts))),
        'objets':rows}
    legacy.old._save_text(qa_dir/'CONTROLE_QUALITE.json',json.dumps(audit,ensure_ascii=False,indent=2,allow_nan=False))
    return audit


def run_v212(pixels,destination,profile='auto',width_mm=40,dpi=300,
             operation='sticker_contour',grid='6x4',segmentation='desactiver',
             masks=None,provider=None,gpu=None):
    # The old pipeline publishes only inside a private staging destination.
    target=Path(destination).expanduser().absolute()
    if target.is_symlink():raise QAError('Destination symbolique interdite')
    target.mkdir(parents=True,exist_ok=True)
    if not target.is_dir():raise QAError('Destination invalide')
    workspace=Path(tempfile.mkdtemp(prefix='.v212_preparation_',dir=target))
    try:
        report,preview=legacy.run_v211(pixels,workspace,profile,width_mm,dpi,operation,
                                       grid,segmentation,masks,provider,gpu)
        project=Path(report['dossier']).resolve()
        if project.parent!=workspace.resolve():raise QAError('Production hors dossier temporaire')
        final=target/('SmartSVG_V21_2_'+uuid4().hex[:12])
        if final.exists():raise QAError('Collision nom de publication')
        quality=audit_staged_exports(project,report,final,dpi)
        updated=legacy._rewrite_paths(report,project,final)
        updated['dossier']=str(final)
        updated['controle_v212']=quality
        updated['version_consolidation']='21.2-beta'
        for oldname in ('RAPPORT_V21_2.json','RAPPORT_V21_1.json',
                        'RAPPORT_V21.json','RAPPORT_V20_6.json'):
            f=project/oldname
            if f.exists() or oldname=='RAPPORT_V21_2.json':
                legacy.old._save_text(f,json.dumps(updated,ensure_ascii=False,indent=2,allow_nan=False))
        os.replace(project,final)
        return updated,preview
    finally:
        shutil.rmtree(workspace,ignore_errors=True)
