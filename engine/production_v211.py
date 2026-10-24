"""V21.1 conservative, transactional Cricut production and physical-size reconciliation.

Legacy V21 remains unchanged. Processing takes place in an isolated staging parent;
finished outputs are published atomically. This module never claims that Design
Space imports DPI or cut operations with the expected physical settings.
"""
from __future__ import annotations
import copy
from contextvars import ContextVar
from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
from uuid import uuid4

import cv2
import numpy as np
from PIL import Image
from . import multi_subject_v21 as v21
from . import hd_multisticker_v206 as old

MAX_MASK_VALUES=v21.MAX_MASK_VALUES

# New exports may skip one expendable intermediate sheet render. ContextVar
# prevents the option from leaking into concurrent/legacy ComfyUI workflows.
_DEFER_SHEETS=ContextVar('smartsvg_defer_intermediate_sheets',default=False)
_FILL_CUT_HOLES=ContextVar('smartsvg_fill_sticker_cut_holes',default=False)

@contextmanager
def defer_intermediate_sheets():
    token=_DEFER_SHEETS.set(True)
    token_holes=_FILL_CUT_HOLES.set(True)
    try:yield
    finally:
        _FILL_CUT_HOLES.reset(token_holes)
        _DEFER_SHEETS.reset(token)



class StudioError(v21.V21Error):
    pass


def preflight_masks(masks,shape):
    """Reject impossible tensors *before* a large GPU->CPU transfer."""
    if masks is None:return
    s=tuple(getattr(masks,'shape',()))
    if len(s)==2:s=(1,)+s
    if len(s)!=3 or tuple(s[1:])!=tuple(shape):
        raise StudioError(f'MASK doit avoir [H,W] ou [N,H,W] et correspondre à IMAGE; reçu {s}')
    if not 1<=s[0]<=v21.MAX_MASKS or math.prod(s)>MAX_MASK_VALUES:
        raise StudioError('Lot de masques trop volumineux (budget GPU/CPU)')
    dt=str(getattr(masks,'dtype',''))
    if 'complex' in dt or 'object' in dt:
        raise StudioError('Format de masques non pris en charge')


def _resample_print(img,new_size):
    """Correct dimensions preserving white-edge RGBA without black RGB bleed."""
    if img.mode=='RGBA':
        a=np.asarray(img.getchannel('A'),dtype=np.uint8)
        rgb=np.asarray(img.convert('RGB'),dtype=np.float32)
        alpha=a.astype(np.float32)/255
        premult=np.uint8(np.clip(np.round(rgb*alpha[:,:,None]),0,255))
        premult=Image.fromarray(premult,'RGB').resize(new_size,Image.Resampling.LANCZOS)
        new_a=img.getchannel('A').resize(new_size,Image.Resampling.LANCZOS)
        an=np.asarray(new_a,dtype=np.float32)/255
        p=np.asarray(premult,dtype=np.float32)
        # White RGB on transparent pixels avoids halos in Cricut raster previews.
        out=np.uint8(np.clip(np.round(np.where(an[:,:,None]>.002,p/np.maximum(an[:,:,None],.002),255)),0,255))
        return Image.fromarray(np.dstack((out,np.asarray(new_a))), 'RGBA')
    return img.resize(new_size,Image.Resampling.LANCZOS)


def _new_subject_sticker(native_rgba, content_width_mm, dpi):
    """Pad first, dilate afterwards: a subject at the source edge gets full halo."""
    if native_rgba.mode!='RGBA':native_rgba=native_rgba.convert('RGBA')
    w,h=native_rgba.size
    target=max(1,round(float(content_width_mm)*dpi/25.4))
    th=max(1,round(target*h/w))
    radius=max(1,round(1.2*dpi/25.4))
    pad=radius+4
    tw=target+2*pad;hh=th+2*pad
    if tw*hh>old.MAX_OUTPUT_PIXELS:raise StudioError('Masque imprimable trop grand')
    scaled=_resample_print(native_rgba,(target,th))
    source_alpha=np.asarray(scaled.getchannel('A'))
    alpha=np.zeros((hh,tw),np.uint8)
    alpha[pad:pad+th,pad:pad+target]=np.uint8(source_alpha>5)*255
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(radius*2+1,radius*2+1))
    cut=cv2.dilate(alpha,kernel)
    cut,used_hull=old._make_single_backing(cut)
    if _FILL_CUT_HOLES.get():
        # Sticker Print Then Cut should have a single EXTERIOR cut and no
        # unintended inner cutouts through the white backing. The native RGBA
        # source remains unchanged, and SVG is rebuilt from this final alpha.
        boundaries,_=cv2.findContours(cut,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        filled=np.zeros_like(cut)
        cv2.drawContours(filled,boundaries,-1,255,thickness=cv2.FILLED)
        cut=filled
    rgba=np.zeros((hh,tw,4),np.uint8)
    rgba[:,:,:3]=255;rgba[:,:,3]=cut
    # Print source over opaque WHITE backing; retain the original alpha in native cutout.
    a=source_alpha.astype(np.float32)/255
    rgb=np.asarray(scaled.convert('RGB'),np.float32)
    blended=np.uint8(np.clip(np.round(rgb*a[:,:,None]+255*(1-a[:,:,None])),0,255))
    rgba[pad:pad+th,pad:pad+target,:3]=blended
    # For very small original alpha, white cut base must not have a visible hole.
    physical=tw*25.4/dpi
    return Image.fromarray(rgba,'RGBA'),physical,used_hull


def _rewrite_print(png,svg,info,dpi):
    with Image.open(png) as im:
        native=im.convert('RGBA').copy()
    physical=float(info.get('largeur_finale_avec_marge_mm') or 0)
    if not .5<=physical<=500:
        raise StudioError('Largeur physique PNG indéterminée; aucune conversion aveugle')
    target_w=max(1,round(physical*dpi/25.4))
    target_h=max(1,round(native.height*target_w/native.width))
    if target_w*target_h>old.MAX_OUTPUT_PIXELS:
        raise StudioError('Export imprimable trop volumineux')
    converted=_resample_print(native,(target_w,target_h))
    # Contour SVG and PNG use the SAME destination alpha geometry and SAME mm.
    alpha=np.asarray(converted.getchannel('A'))
    pathtext,npaths=old._path_svg(alpha,physical,dpi)
    if not npaths:raise StudioError('Silhouette perdue lors de la mise à l’échelle')
    old._save_png(png,converted,dpi)
    if svg is not None:old._save_text(svg,pathtext)
    info['dimensions_px_export']=list(converted.size)
    info['densite_export_cible_ppp']=dpi
    info['controle_physique_v211']={
        'largeur_png_px':target_w,
        'largeur_png_mm_si_ppp_respectes':round(25.4*target_w/dpi,3),
        'largeur_svg_mm':round(physical,3),
        'largeur_initiale_px':native.width,
        'pixels_source_natifs_preserves_dans_original':True,
        'redimensionnement_export':round(target_w/native.width,4),
        'taille_import_design_space_a_verifier':True}
    info['nombre_chemins']=npaths if 'nombre_chemins' in info else info.get('nombre_chemins')
    if 'contour_nombre_chemins' in info:info['contour_nombre_chemins']=npaths
    if npaths!=1:
        warns=info.setdefault('avertissements',[])
        if 'CONTOURS_MULTIPLES_APRES_MISE_A_ECHELLE' not in warns:
            warns.append('CONTOURS_MULTIPLES_APRES_MISE_A_ECHELLE')
    return converted


def _relative_under(path,root):
    p=Path(path).resolve(strict=False)
    try:return p.relative_to(root.resolve())
    except ValueError:raise StudioError('Chemin de sortie non contenu dans le projet')


def _rewrite_paths(data,old_root,new_root):
    if isinstance(data,dict):return {k:_rewrite_paths(v,old_root,new_root) for k,v in data.items()}
    if isinstance(data,list):return [_rewrite_paths(v,old_root,new_root) for v in data]
    if isinstance(data,str):
        try:
            old=str(old_root);new=str(new_root)
            if data==old:return new
            if data.startswith(old+os.sep):return new+data[len(old):]
        except Exception:pass
    return data


def _remake_pages(report,project,final,dpi,images):
    # Remove all old sheets from the staging tree before rebuilding to avoid
    # stale mislabeled artifacts with a different DPI/size contract.
    for relative in ('03_PLANCHES',):
        directory=project/relative
        if directory.is_dir():
            for png in directory.glob('PLANCHE_*.png'):png.unlink()
    if 'planches' in report:
        report['planches']=v21._make_pages(images,project,final,dpi)
        return
    if 'planches_cricut' in report:
        original=report['planches_cricut'];report['planches_cricut']=[]
        for k in range(0,len(images),12):
            file=project/f'PLANCHE_CRICUT_{k//12+1:02d}_A_VERIFIER.png'
            summary=old._save_sheet(images[k:k+12],file,dpi,columns=4)
            summary['fichier']=str(final/file.relative_to(project)) if file.exists() else None
            summary['validation_cricut']=False
            if summary.get('statut')=='CREATION_OK':
                wmm,hmm=summary['taille_estimee_mm']
                if wmm>175 or hmm>240:
                    summary['statut']='TAILLE_POTENTIELLEMENT_TROP_GRANDE_DESIGN_SPACE'
                if summary['ilots_alpha_detectes']!=len(images[k:k+12]):
                    summary['statut']='NB_DECOUPES_INCOHERENT_A_VERIFIER'
            report['planches_cricut'].append(summary)


def _reconcile_report(report,project,final,dpi,requested_width_mm):
    qa=[];print_images=[]
    for item in report.get('objets',[]):
        p=item.get('fichier_png_cricut') or item.get('png')
        svg=item.get('fichier_svg_contour') or item.get('svg_contour')
        if not p:continue
        png=project/_relative_under(p,project)
        svg_path=project/_relative_under(svg,project) if svg else None
        if 'fichier_transparent' in item:
            nativepath=project/_relative_under(item['fichier_transparent'],project)
            with Image.open(nativepath) as im: native=im.convert('RGBA').copy()
            content_width=report.get('largeur_element_mm', report.get('largeur_mm', None))
            if content_width is None:
                # V21 masks do not record the request in their legacy report:
                # derive it from requested physical width and old native crop size.
                # Instead of deriving from output pixels, the caller supplies it.
                content_width=requested_width_mm
            image,real_mm,hull=_new_subject_sticker(native,float(content_width),dpi)
            item['largeur_finale_avec_marge_mm']=round(real_mm,3)
            if hull:item.setdefault('avertissements',[]).append('ENVELOPPE_CONVEXE_DE_SECOURS_A_VERIFIER')
            old._save_png(png,image,dpi)
            paths,npaths=old._path_svg(np.asarray(image.getchannel('A')),real_mm,dpi)
            if svg_path:old._save_text(svg_path,paths)
            item['dimensions_px_export']=list(image.size)
            item['nombre_chemins']=npaths
            item['controle_physique_v211']={
                'largeur_png_px':image.width,
                'largeur_png_mm_si_ppp_respectes':round(25.4*image.width/dpi,3),
                'largeur_svg_mm':round(real_mm,3),
                'source_originale_natif_preservee':True,
                'marge_calculee_apres_agrandissement_du_canvas':True,
                'taille_import_design_space_a_verifier':True}
        else:
            image=_rewrite_print(png,svg_path,item,dpi)
        print_images.append(image)
        qa.append({'fichier':str(final/png.relative_to(project)),
                   'taille_px':list(image.size),'largeur_mm':item['largeur_finale_avec_marge_mm']})
    if print_images:_remake_pages(report,project,final,dpi,print_images)
    report=_rewrite_paths(report,project,final)
    report['controle_v211']={
       'version':'21.1-beta','exports_imprimables_recalibres':len(qa),
       'largeur_pixels_et_mm_coherents_si_dpi_respecte':True,
       'source_originale_conservee':True,
       'contours_svg_regeneres_sur_alpha_final':True,
       'taille_reelle_dans_design_space_a_verifier':True,
       'nouvelles_decoupes_certifiees':False,
       'fichiers':qa}
    report['dossier']=str(final)
    return report


def run_v211(pixels,destination,profile='auto',width_mm=40,dpi=300,
             operation='sticker_contour',grid='6x4',segmentation='desactiver',
             masks=None,provider=None,gpu=None):
    old._valid_image(pixels)
    preflight_masks(masks,pixels.shape[:2])
    if segmentation=='forcer' and masks is None and operation=='carte_rectangle' and profile!='planche_multi':
        raise StudioError('Mode IA obligatoire incompatible avec découpe rectangulaire choisie')
    target=Path(destination).expanduser().absolute()
    if target.is_symlink():raise StudioError('Dossier cible symbolique non autorisé')
    target.mkdir(parents=True,exist_ok=True)
    if not target.is_dir():raise StudioError('Le chemin de destination n’est pas un dossier')
    stageparent=Path(tempfile.mkdtemp(prefix='.v211_audit_',dir=target))
    try:
        r,preview=v21.run_v21(pixels,stageparent,profile,width_mm,dpi,operation,
                              grid,segmentation,masks,provider=provider,gpu=gpu,
                              defer_pages=_DEFER_SHEETS.get())
        if segmentation=='forcer' and masks is None and not r.get('nombre_objets_exportes'):
            raise StudioError('Aucun masque IA obtenu en mode obligatoire')
        if segmentation=='forcer' and masks is None and 'v21' in r:
            raise StudioError('IA obligatoire : le fournisseur n’a renvoyé aucun masque utilisable')
        project=Path(r['dossier']).resolve()
        if project.parent!=stageparent.resolve():raise StudioError('Sortie temporaire hors staging')
        final=target/('SmartSVG_V21_1_'+uuid4().hex[:12])
        if final.exists():raise StudioError('Nom de dossier déjà existant')
        r=_reconcile_report(r,project,final,dpi,width_mm)
        r['controle_v211']['publication_atomique']=True
        # The legacy nested report also references final paths, not discarded temp paths.
        old._save_text(project/'RAPPORT_V21_1.json',json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False))
        for original_report in ('RAPPORT_V21.json','RAPPORT_V20_6.json'):
            p=project/original_report
            if p.exists():
                # Never leave conflicting pre-recalibration millimeters in a
                # legacy-named report; expose the canonical corrected values.
                old._save_text(p,json.dumps(r,ensure_ascii=False,indent=2,allow_nan=False))
        os.replace(project,final)
        return r,preview
    except BaseException:
        raise
    finally:
        shutil.rmtree(stageparent,ignore_errors=True)
