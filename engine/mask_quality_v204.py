"""SmartSVG V20.4: independent, non-destructive, conservative mask QA.

No score here is a probability of semantic accuracy. It audits binary topology,
print/cut feasibility, clipped edges and loss of source line-art. Nothing here
changes source masks or the authoritative Cricut exports.
"""
from __future__ import annotations
import json
import math
import os
from pathlib import Path
import tempfile
from uuid import uuid4

import cv2
import numpy as np
from PIL import Image

MAX_PIXELS = 8_000_000
MAX_MASKS = 16

class QualityError(ValueError):
    pass


def normalize_masks(value, *, height=None, width=None):
    """Accept ComfyUI [N,H,W] or [H,W] without hidden huge GPU->CPU copies."""
    if hasattr(value,'detach'):
        s=tuple(int(n) for n in value.shape)
        if len(s) not in (2,3):raise QualityError('Dimensions MASK invalides')
        n=1 if len(s)==2 else s[0]
        if n<1 or n>MAX_MASKS or n*s[-2]*s[-1]>MAX_PIXELS:
            raise QualityError('Budget ou nombre de masques depasse')
        value=value.detach().cpu().numpy()
    a=np.asarray(value)
    if a.ndim==2:a=a[None]
    if (a.ndim!=3 or a.shape[0] not in range(1,MAX_MASKS+1)
        or min(a.shape[1:])<1 or a.size>MAX_PIXELS):
        raise QualityError('Masque invalide ou trop volumineux')
    if (height is not None and a.shape[1]!=height) or (width is not None and a.shape[2]!=width):
        raise QualityError('Dimensions masque et image incompatibles')
    if a.dtype.kind not in 'fiu' or not np.isfinite(a).all():
        raise QualityError('Valeurs de masque non numeriques ou non finies')
    lo=float(a.min());hi=float(a.max())
    if lo<0 or hi>255:raise QualityError('Valeurs hors plage')
    if a.dtype.kind=='f':
        if hi>1+1e-4:raise QualityError('Masque flottant hors 0..1')
        arr=np.asarray(a,dtype=np.float32)
    else:
        arr=a.astype(np.float32)/(255.0 if hi>1 else 1.0)
    return np.ascontiguousarray(np.clip(arr,0,1))


def analyze_mask(mask, ink=None, *, min_island_pixels=12, max_small_fraction=.015):
    """Heuristics and explainable flags, not semantic verification.

    ink: uint8 image with ink as positive values (255 black ink).
    """
    arr=normalize_masks(mask)
    if arr.shape[0]!=1:raise QualityError('Analyse d un seul objet requise')
    m=arr[0]
    h,w=m.shape
    fg=(m>=.5).astype(np.uint8)
    total=int(fg.sum());size=h*w
    frac=total/size
    flags=[]
    metrics={'surface_px':total,'fraction_surface':round(frac,6),
             'largeur_px':w,'hauteur_px':h,
             'pixels_semi_transparents':int(np.count_nonzero((m>.01)&(m<.99))),
             'contact_haut':bool(fg[0].any()),
             'contact_bas':bool(fg[-1].any()),
             'contact_gauche':bool(fg[:,0].any()),
             'contact_droite':bool(fg[:,-1].any())}
    if not total: flags.append('MASQUE_VIDE')
    if frac>.90:flags.append('SUJET_OCCUPE_PRESQUE_TOUTE_IMAGE')
    if 0<frac<.002:flags.append('SUJET_TROP_PETIT')
    if any(metrics['contact_'+s] for s in ('haut','bas','gauche','droite')):
        flags.append('SILHOUETTE_TOUCHE_BORD_IMAGE')
    if total:
        n, _, stats, _=cv2.connectedComponentsWithStats(fg,8)
        areas=[int(x) for x in stats[1:,cv2.CC_STAT_AREA]]
        largest=max(areas,default=0)
        minor=sum(v for v in areas if v<max(min_island_pixels,largest*.005))
        metrics['composantes']=len(areas)
        metrics['aire_composante_principale_px']=largest
        metrics['aire_ilots_secondaires_px']=total-largest
        metrics['fraction_ilots_secondaires']=round((total-largest)/total,6)
        metrics['petits_fragments_px']=minor
        if (len(areas)>1 and (total-largest)/total>max_small_fraction):
            flags.append('PLUSIEURS_ILOTS_IMPORTANTS')
        contours,_=cv2.findContours(fg,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        metrics['contours_exterieurs']=len(contours)
        perimeter=sum(float(cv2.arcLength(c,True)) for c in contours)
        metrics['perimetre_exterieur_px']=round(perimeter,2)
        metrics['complexite_perimetre_sur_racine_aire']=round(perimeter/math.sqrt(total),3)
        if perimeter/math.sqrt(total)>35:flags.append('CONTOUR_POTENTIELLEMENT_TROP_COMPLEXE')
        # Holes are important for decal/stencil workflows, but outer silhouette
        # print-then-cut normally fills them. Report, do not automatically cut.
        allcontours,hierarchy=cv2.findContours(fg,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        holes=sum(1 for hinfo in hierarchy[0] if hinfo[3]>=0) if hierarchy is not None else 0
        metrics['trous_internes_detectes']=holes
        if holes:flags.append('TROUS_INTERNES_IGNOREES_PAR_CONTOUR_EXTERIEUR')
    else:
        metrics.update(composantes=0,aire_composante_principale_px=0,aire_ilots_secondaires_px=0,
                       fraction_ilots_secondaires=0,petits_fragments_px=0,contours_exterieurs=0,
                       perimetre_exterieur_px=0,complexite_perimetre_sur_racine_aire=0,trous_internes_detectes=0)
    if ink is not None:
        k=np.asarray(ink)
        if k.ndim!=2 or k.shape!=m.shape or k.dtype.kind not in 'iuf':
            raise QualityError('LineArt non aligne')
        if not np.isfinite(k).all():raise QualityError('LineArt non fini')
        # ink-positive convention; white background in image is 0
        marks=k>0
        inkcount=int(marks.sum());included=int((marks & (fg>0)).sum())
        metrics['traits_total_px']=inkcount
        metrics['traits_dans_masque_px']=included
        metrics['traits_perdus_pct']=round(100*(inkcount-included)/inkcount,2) if inkcount else 0.
        if inkcount>100 and (inkcount-included)/inkcount>.35:
            flags.append('PLUS_DE_35_PCT_TRAITS_HORS_SILHOUETTE')
    verdict='A_VERIFIER' if total and not flags else 'RISQUE_ELEVE' if flags else 'A_VERIFIER'
    return {'version':'20.4-beta','statut':'DIAGNOSTIC_NON_CERTIFIANT',
            'verdict':verdict,'signaux':flags,'mesures':metrics,
            'validation_humaine_obligatoire':True,
            'decoupe_physique_validee':False,
            'note':'Une silhouette sans anomalie geometrique peut tout de meme representer le mauvais objet.'}


def draw_overlay(mask, ink=None):
    arr=normalize_masks(mask)
    if arr.shape[0]!=1:raise QualityError('Apercu d un seul objet requis')
    m=arr[0];h,w=m.shape
    view=np.full((h,w,3),255,np.uint8)
    if ink is not None:
        if np.asarray(ink).shape!=(h,w):raise QualityError('Image non alignee')
        view[np.asarray(ink)>0]=[65,65,65]
    fg=(m>=.5).astype(np.uint8)
    edges=cv2.morphologyEx(fg,cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))>0
    view[edges]=[230,46,55]
    if ink is not None:
        view[(np.asarray(ink)>0)&(fg==0)]=[210,40,195]
    return view


def atomic_json(destination, payload):
    """Fail closed on symlinks, avoid partially written QA report."""
    p=Path(destination)
    if p.parent.is_symlink() or p.is_symlink():raise QualityError('Lien symbolique interdit')
    p.parent.mkdir(parents=True,exist_ok=True)
    temp=None
    try:
        with tempfile.NamedTemporaryFile('w',encoding='utf-8',dir=p.parent,prefix='.pending_qa_',suffix='.tmp',delete=False) as f:
            temp=Path(f.name)
            json.dump(payload,f,ensure_ascii=False,allow_nan=False,indent=2)
            f.flush();os.fsync(f.fileno())
        os.replace(temp,p)
    finally:
        if temp is not None: temp.unlink(missing_ok=True)
    return str(p)


def audit_output_root(root):
    """Read ONLY artifacts produced by our exporter; caller must supply its run root."""
    p=Path(root)
    qa=p/'08_SEGMENTATION_IA_V20_2'
    maskfile=qa/'masque_ia_original.png'
    inkfile=p/'04_LINEART'/'traits_fins.png'
    if not maskfile.is_file():
        return None,{'version':'20.4-beta','statut':'AUCUN_MASQUE_IA',
                     'verdict':'AUCUN_CONTOUR_IA','validation_humaine_obligatoire':True}
    if maskfile.is_symlink() or inkfile.is_symlink():raise QualityError('Fichier QA symbolique interdit')
    # Reject PNG decompression bombs before decoding.
    with Image.open(maskfile) as im:
        if im.width*im.height>MAX_PIXELS:raise QualityError('Image QA trop grande')
        mask=np.asarray(im.convert('L'))
    ink=None
    if inkfile.is_file():
        with Image.open(inkfile) as im:
            if im.width*im.height>MAX_PIXELS:raise QualityError('LineArt trop grand')
            ink=np.asarray(im.convert('L'))
    report=analyze_mask(mask,ink)
    return (mask,ink),report


def analyze_batch(masks):
    """Cross-model mask QA including suspicious pairwise overlap; no object ID claims."""
    a=normalize_masks(masks)
    records=[]
    for i,m in enumerate(a):
        r=analyze_mask(m)
        r['index_masque']=i
        records.append(r)
    overlaps=[]
    # Boolean occupancy can have legitimate occlusion, so no auto segmentation
    # decision is made based on overlap alone.
    b=a>=.5
    for i in range(len(a)):
        for j in range(i+1,len(a)):
            intersection=int(np.count_nonzero(b[i] & b[j]))
            if not intersection:continue
            union=int(np.count_nonzero(b[i] | b[j]))
            overlaps.append({'masque_a':i,'masque_b':j,'pixels_partages':intersection,
                             'iou':round(intersection/max(union,1),5),
                             'identite_potentielle':intersection/max(union,1)>.90})
    return {'version':'20.4-beta','statut':'DIAGNOSTIC_NON_CERTIFIANT',
            'nombre_masques':len(a),'par_masque':records,
            'paires_avec_recouvrement':overlaps,
            'aucun_masque_modifie':True,'validation_humaine_obligatoire':True,
            'note':'Des chevauchements peuvent etre legitimes (mains, objets tenus). Ne pas fusionner automatiquement.'}
