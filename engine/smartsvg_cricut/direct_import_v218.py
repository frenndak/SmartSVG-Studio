"""V21.8 conservative single-file Cricut Print Then Cut export and local preflight.

An RGBA PNG by itself is the printable artwork *and* its transparency-defined
cut silhouette in Design Space's Flat Graphic workflow.  The auxiliary cut-only
SVG is never required for Print Then Cut and must not be stacked above the PNG.
Local inspection cannot validate Cricut's proprietary import or physical cut.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import uuid
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image
# Independent copy: this module is also imported as a top-level package by
# several historical validators, not only through the ComfyUI plugin package.
def near_rectangle(binary, *, threshold=0.985):
    b=np.asarray(binary,dtype=np.bool_)
    if b.ndim!=2:raise ValueError('Alpha 2D requis')
    ys,xs=np.nonzero(b)
    if xs.size==0:return True
    area=(int(xs.max())-int(xs.min())+1)*(int(ys.max())-int(ys.min())+1)
    return xs.size/area >= threshold

FOLDER = '00_IMPORTER_DANS_CRICUT'
REPORT = 'RAPPORT_IMPORT_CRICUT_V21_8.json'
MAX_PIXELS = 32_000_000
MAX_ITEMS = 32
A4_SAFE_WIDTH_MM = 175.0  # deliberately below Explore A4 maxima (not a guaranteed fit)
A4_SAFE_HEIGHT_MM = 240.0


class ImportAuditError(ValueError):
    pass


def _project(report):
    base=report.get('dossier')
    if not isinstance(base,str) or not base or not Path(base).is_absolute():
        raise ImportAuditError('Dossier projet absolu manquant')
    p=Path(base)
    if p.is_symlink() or not p.is_dir():
        raise ImportAuditError('Dossier projet incorrect ou symbolique')
    return p.resolve(strict=True)


def _source(project, raw):
    if not isinstance(raw,str) or not raw or len(raw)>4096:
        raise ImportAuditError('Chemin PNG manquant')
    p=Path(raw)
    if not p.is_absolute() or p.suffix.lower()!='.png' or p.is_symlink():
        raise ImportAuditError('PNG invalide, relatif ou lien symbolique')
    try:
        real=p.resolve(strict=True)
        real.relative_to(project)
    except (OSError,ValueError):
        raise ImportAuditError('PNG hors du projet ou absent') from None
    if not real.is_file():raise ImportAuditError('PNG introuvable')
    return real


def _topology(path):
    """Look at alpha as Design Space would, not at separate cut-only SVG.

    127 is only a simulation threshold; proprietary Design Space may differ.
    Count all visible islands, and substantial transparent holes that could
    become interior cuts. This does not modify the picture.
    """
    with Image.open(path) as im:
        if im.format!='PNG' or im.mode!='RGBA':
            raise ImportAuditError('PNG doit etre RGBA avec transparence')
        w,h=im.size
        if not w or not h or w*h>MAX_PIXELS:
            raise ImportAuditError('PNG vide ou trop volumineux')
        a=np.asarray(im.getchannel('A'),dtype=np.uint8)
        d=im.info.get('dpi')
        dpi=float(d[0]) if d and 50<float(d[0])<1200 else None
    binary=np.uint8(a>=128)
    n,_,stats,_=cv2.connectedComponentsWithStats(binary,8)
    components=n-1
    if components==0:raise ImportAuditError('PNG entierement transparent')
    contours,hierarchy=cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    holes=0
    if hierarchy is not None:
        for contour,parent_data in zip(contours,hierarchy[0]):
            if parent_data[3]>=0 and abs(cv2.contourArea(contour))>=8:
                holes+=1
    rectangle_exact=(components==1 and int(stats[1,cv2.CC_STAT_AREA])==int(stats[1,cv2.CC_STAT_WIDTH])*int(stats[1,cv2.CC_STAT_HEIGHT]))
    rectangle_entier=(components==1 and near_rectangle(binary))
    edge=bool(binary[0,:].any() or binary[-1,:].any() or binary[:,0].any() or binary[:,-1].any())
    return {'taille_px':[w,h], 'mode':'RGBA', 'composantes_alpha':components,
            'trous_transparents_significatifs':holes,'contact_bord':edge,
            'densite_metadata_ppp':round(dpi,2) if dpi else None,
            'alpha_opaque_pixels':int(stats[1:,cv2.CC_STAT_AREA].sum()),
            'alpha_totalement_opaque':bool(np.all(a==255)),
            'alpha_rectangle_plein':rectangle_exact,
            'alpha_quasi_rectangle':rectangle_entier and not rectangle_exact}


def _svg_preflight(png:Path,svg_raw,project,expected_width_mm):
    if not svg_raw:return {'statut':'INFORMATION_INDISPONIBLE','raison':'SVG de controle non renseigne'}
    try:
        svg=Path(svg_raw)
        if not svg.is_absolute() or svg.suffix.lower()!='.svg' or svg.is_symlink():
            raise ImportAuditError('SVG invalide')
        real=svg.resolve(strict=True)
        real.relative_to(project)
        root=ET.parse(real).getroot()
        if root.tag.rsplit('}',1)[-1]!='svg':raise ImportAuditError('Racine SVG incorrecte')
        width=root.get('width','')
        if not width.endswith('mm'):raise ImportAuditError('SVG sans largeur physique mm')
        width=float(width[:-2])
        paths=[e for e in root.iter() if e.tag.rsplit('}',1)[-1]=='path']
        if not paths:raise ImportAuditError('SVG sans chemin')
        if any(e.tag.rsplit('}',1)[-1] not in ('svg','path','g','title','desc') for e in root.iter()):
            raise ImportAuditError('SVG contient des elements non simplifies')
        if expected_width_mm and abs(width-expected_width_mm)>.2:
            raise ImportAuditError('Largeur SVG differente du PNG de reference')
        return {'statut':'OK_LOCAL','largeur_svg_mm':round(width,3),'nombre_chemins_svg':len(paths),
                'note':'Contour SVG diagnostic uniquement; ne PAS le superposer au PNG.'}
    except (OSError,ValueError,ET.ParseError,ImportAuditError) as e:
        return {'statut':'A_VERIFIER','raison':str(e)[:160]}


def _sha256_file(path):
    digest=hashlib.sha256()
    with open(path,'rb') as inp:
        for block in iter(lambda:inp.read(1024*1024),b''):
            digest.update(block)
    return digest.digest()


def _copy_atomic(src,dest):
    # Re-running a completed project must be idempotent for identical outputs,
    # but must never overwrite a user file or silently retain stale artwork.
    source_digest=_sha256_file(src)
    if dest.is_symlink():
        raise ImportAuditError('Destination symbolique interdite')
    if dest.exists():
        if dest.is_file() and _sha256_file(dest)==source_digest:
            return
        raise ImportAuditError('Destination deja existante avec contenu different ; conserver ou changer de projet')
    tmp=dest.with_name('.tmp_'+uuid.uuid4().hex+'.png')
    try:
        shutil.copyfile(src,tmp)
        if _sha256_file(tmp)!=source_digest:
            raise ImportAuditError('Copie de fichier incoherente')
        # Exclusive creation: os.replace() had a race that could replace a
        # file created by another workflow between check and rename.
        try:
            os.link(tmp,dest)
        except FileExistsError:
            if not dest.is_symlink() and dest.is_file() and _sha256_file(dest)==source_digest:
                return
            raise ImportAuditError('Destination creee concurremment') from None
        except OSError:
            # FAT/network volumes may not support hard links. Use an exclusive
            # create as a portable, never-overwrite fallback on Windows too.
            try:
                fd=os.open(dest,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
            except FileExistsError:
                if not dest.is_symlink() and dest.is_file() and _sha256_file(dest)==source_digest:
                    return
                raise ImportAuditError('Destination creee concurremment') from None
            try:
                with os.fdopen(fd,'wb') as target, open(tmp,'rb') as original:
                    shutil.copyfileobj(original,target,length=1024*1024)
                    target.flush();os.fsync(target.fileno())
                if _sha256_file(dest)!=source_digest:
                    raise ImportAuditError('Copie finale non conforme')
            except BaseException:
                dest.unlink(missing_ok=True)
                raise
    finally:
        tmp.unlink(missing_ok=True)


def _write_text_preserving_existing(dest, contents):
    """Do not silently overwrite a project note or QA report on re-execution."""
    staging=dest.with_name('.smartsvg_metadata_'+uuid.uuid4().hex)
    try:
        staging.write_text(contents,encoding='utf-8')
        _copy_atomic(staging,dest)
    finally:
        staging.unlink(missing_ok=True)


def prepare_cricut_import(report:dict,dpi:int) ->dict:
    """Publish only locally preflighted original Print Then Cut PNGs.

    All errors after manufacturing must be isolated from fabrication output.
    No automatic retouch of shapes, no assertions about actual Cricut hardware.
    """
    root=_project(report)
    if not isinstance(dpi,int) or dpi not in (300,450):
        raise ImportAuditError('Densite de fabrication inconnue')
    objs=report.get('objets',[])
    if not isinstance(objs,list) or not 1<=len(objs)<=MAX_ITEMS:
        raise ImportAuditError('Nombre objets hors limites')
    dest=root/FOLDER
    if dest.is_symlink():raise ImportAuditError('Destination Cricut symbolique')
    dest.mkdir(exist_ok=True)
    if dest.resolve()!=root/FOLDER:raise ImportAuditError('Dossier de destination incorrect')
    result={'version':'21.8','statut':'A_VERIFIER','fichiers_prets':0,'nombre_objets':len(objs),
            'planches_pretes':0,'cartes_rectangulaires':0,'objets':[],'planches':[],
            'import_design_space_reel_teste':False,'decoupe_physique_testee':False,
            'format_recommande':'PNG RGBA, Flat Graphic / Imprimer puis decouper',
            'ne_pas_ajouter_svg_contour':True,'dossier':str(dest)}
    for index,obj in enumerate(objs,1):
        rec={'objet':index,'statut':'A_VERIFIER'};result['objets'].append(rec)
        try:
            if not isinstance(obj,dict):raise ImportAuditError('Objet du rapport invalide')
            source=_source(root,obj.get('fichier_png_cricut') or obj.get('png'))
            geo=_topology(source);rec.update(geo)
            rec['source']=str(source)
            physical=obj.get('largeur_finale_avec_marge_mm')
            if physical is not None:
                physical=float(physical)
                expected=geo['taille_px'][0]*25.4/dpi
                rec['largeur_attendue_mm']=round(physical,3)
                if abs(physical-expected)>.20:
                    raise ImportAuditError(f'Taille physique incoherente: {physical:.2f}mm vs {expected:.2f}mm')
            else:physical=geo['taille_px'][0]*25.4/dpi
            rec['controle_svg']=_svg_preflight(source,
                    obj.get('fichier_svg_contour') or obj.get('svg_contour'),root,physical)
            # Each sticker must correspond to exactly one exterior cut island.
            if geo['composantes_alpha']!=1:
                raise ImportAuditError(f'{geo["composantes_alpha"]} zones de decoupe au lieu de 1')
            if geo['trous_transparents_significatifs']:
                raise ImportAuditError('Trous transparents internes: decoupes supplementaires possibles')
            if rec['controle_svg']['statut']=='A_VERIFIER':
                raise ImportAuditError('Contour SVG incoherent; inspection humaine necessaire')
            if geo['contact_bord']:
                rec['avertissement']='Contour au bord du PNG; verifier dans Design Space'
            card=(geo['alpha_rectangle_plein'] or geo['alpha_quasi_rectangle'] or
                  (report.get('v21',{}).get('mode')=='REPLI_V20_6_SANS_MASQUE'
                   and obj.get('source_alpha')!='SOURCE_AVEC_TRANSPARENCE_UTILISEE'))
            if card:
                rec['type_decoupe_presumee']='CADRE_RECTANGULAIRE_SANS_DETOURAGE'
                rec['avertissement']='Silhouette rectangulaire ou quasi rectangulaire : ne pas valider comme detourage du personnage ; controler dans Design Space'
            else:
                rec['type_decoupe_presumee']='SILHOUETTE_ALPHA_UNE_ZONE' 
            name=f'STICKER_{index:03d}_IMPRIMER_PUIS_DECOUPER.png'
            _copy_atomic(source,dest/name)
            rec['fichier_import']=str(dest/name)
            rec['statut']='PRET_POUR_IMPORT_LOCAL_CADRE' if card else 'PRET_POUR_IMPORT_LOCAL'
            result['fichiers_prets']+=1
            if card:result['cartes_rectangulaires']+=1
        except (OSError,ValueError,ImportAuditError,Image.DecompressionBombError,MemoryError) as exc:
            rec['raison']=str(exc)[:200]
            if 'Destination deja existante' in rec['raison'] or 'Destination creee concurremment' in rec['raison']:
                rec['avertissement']='ANCIEN PNG EVENTUELLEMENT PRESENT : ne pas l importer sans comparer au rapport courant'
    pages=report.get('planches') or report.get('planches_cricut') or []
    if isinstance(pages,list):
        for i,p in enumerate(pages,1):
            rec={'planche':i,'statut':'A_VERIFIER'};result['planches'].append(rec)
            try:
                if not isinstance(p,dict) or p.get('statut')!='CREATION_OK':
                    raise ImportAuditError('Planche non produite ou avertissement de fabrication')
                source=_source(root,p.get('fichier'))
                geo=_topology(source);rec.update(geo)
                expected=len(p.get('elements_source') or []) or int(p.get('objets') or 0)
                if not 1<=expected<=MAX_ITEMS or geo['composantes_alpha']!=expected:
                    raise ImportAuditError(f'Ilots de decoupe : {geo["composantes_alpha"]} / attendus {expected}')
                if geo['trous_transparents_significatifs']:
                    raise ImportAuditError('Planche contenant des trous transparents')
                ww=geo['taille_px'][0]*25.4/dpi
                hh=geo['taille_px'][1]*25.4/dpi
                rec['dimensions_estimees_mm']=[round(ww,2),round(hh,2)]
                if ww>A4_SAFE_WIDTH_MM or hh>A4_SAFE_HEIGHT_MM:
                    raise ImportAuditError('Taille hors enveloppe prudente A4; choisir fichiers individuels')
                name=f'PLANCHE_{i:02d}_IMPRIMER_PUIS_DECOUPER.png'
                _copy_atomic(source,dest/name)
                rec['fichier_import']=str(dest/name)
                rec['statut']='PRET_POUR_IMPORT_LOCAL'
                rec['note']='Une seule image importee; les sujets ne sont pas repositionnables separement.'
                result['planches_pretes']+=1
            except (OSError,ValueError,ImportAuditError,Image.DecompressionBombError,MemoryError) as exc:
                rec['raison']=str(exc)[:200]
                if 'Destination deja existante' in rec['raison'] or 'Destination creee concurremment' in rec['raison']:
                    rec['avertissement']='ANCIEN PNG EVENTUELLEMENT PRESENT : ne pas l importer sans comparer au rapport courant'
    result['statut']=('PRET_POUR_IMPORT_LOCAL_AVEC_CADRES' if result['fichiers_prets']==len(objs) and result['cartes_rectangulaires'] else
                      'PRET_POUR_IMPORT_LOCAL' if result['fichiers_prets']==len(objs) else
                      'PARTIEL' if result['fichiers_prets'] else 'A_VERIFIER')
    readme=(
        'SMARTSVG — IMPORT CRICUT EN 1 FICHIER (V21.8)\n\n'
        '1. Ouvrir Design Space, puis Televerser / Upload.\n'
        '2. Choisir STICKER_..._IMPRIMER_PUIS_DECOUPER.png ou la PLANCHE.\n'
        '3. Conserver le fond transparent. Choisir Flat Graphic (image aplatie).\n'
        '4. Verifier dans le canevas : operation Imprimer puis decouper, silhouette et taille en mm.\n'
        '5. Cliquer Creer, choisir le papier et imprimer directement DEPUIS Design Space.\n'
        '6. NE PAS ajouter le SVG de contour par-dessus : cela double les decoupes.\n\n'
        'Un PNG est une image aplatie, pas un SVG vectoriel multicouche editable.\n'
        'Ce precontrole logiciel ne prouve PAS la compatibilite de ton installation Cricut\n'
        'ni la qualite de la decoupe physique. Faire une decoupe test.\n'
        'Pour des stickers individuels repositionnables, importer un PNG par objet.\n'
        'Pour conserver leur disposition en une seule importation, utiliser la planche PNG.\n'
        'A4 : marge prudente interne 175 x 240 mm, ce n est pas une garantie de Cricut.\n'
    )
    try:
        _write_text_preserving_existing(dest/'LIRE_AVANT_IMPORT.txt',readme)
        _write_text_preserving_existing(dest/REPORT,json.dumps(result,ensure_ascii=False,indent=2))
    except (OSError,ImportAuditError) as exc:
        # Manufacturing and already verified PNG files remain intact, but
        # a stale README/report must never cause a misleading 'ready' status.
        result['avertissement_fichiers_accompagnement']=str(exc)[:200]
        result['statut']='A_VERIFIER'
    return result
