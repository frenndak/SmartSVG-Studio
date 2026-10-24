"""V19.4 conservative edge refinement and quantitative mask QA.

Matting is an *approximation*: no hallucinated hair, hidden limb reconstruction,
or ML confidence. Production/original extracted PNGs are immutable.
"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import os
import tempfile
import uuid
from io import BytesIO

import cv2
import numpy as np
from PIL import Image, ImageDraw
from .photo_geometry_v191 import cutout_with_white_border
from .photo_v19 import process_photo, PhotoExtractionError, _manifest

MAX_PIXELS=14_000_000


def inspect_mask(mask: np.ndarray, *, mm_per_px: float):
    mask=np.asarray(mask,dtype=np.float32)
    if mask.ndim!=2 or mask.size>MAX_PIXELS or not np.isfinite(mask).all() or mask.min()<-.001 or mask.max()>1.001:
        raise PhotoExtractionError('V19.4: masque invalide')
    if not 0<mm_per_px<=10: raise PhotoExtractionError('V19.4: echelle physique invalide')
    mask=np.clip(mask,0,1)
    support=mask>=.5
    total=int(support.sum())
    if total==0:raise PhotoExtractionError('V19.4: masque vide')
    h,w=mask.shape
    n,labels,stats,_=cv2.connectedComponentsWithStats(support.astype('uint8'),8)
    major=max(5,int(total*.003))
    areas=[int(stats[k,cv2.CC_STAT_AREA]) for k in range(1,n)]
    small=sum(1 for x in areas if x<major)
    significant=sum(1 for x in areas if x>=major)
    largest=max(areas) if areas else 0
    ys,xs=np.where(support)
    touch=any([xs.min()==0,xs.max()==w-1,ys.min()==0,ys.max()==h-1])
    # Connected holes in the inverted binary mask, excluding image border.
    inv=(~support).astype('uint8')
    hn,_,hstats,_=cv2.connectedComponentsWithStats(inv,8)
    holes=sum(1 for k in range(1,hn) if hstats[k,0]>0 and hstats[k,1]>0
              and hstats[k,0]+hstats[k,2]<w and hstats[k,1]+hstats[k,3]<h
              and hstats[k,cv2.CC_STAT_AREA]>=6)
    # A rough estimate, not an AI model confidence score.
    smooth=int(np.count_nonzero((mask>0.01)&(mask<0.99)))
    edge=cv2.morphologyEx(support.astype('uint8'),cv2.MORPH_GRADIENT,np.ones((3,3),np.uint8))>0
    edge_pixels=int(edge.sum())
    isolated_fraction=(total-largest)/total
    warnings=[]
    if touch:warnings.append('Sujet au contact du bord de la photo; verifier cheveux/objets tronques')
    if significant>1:warnings.append('Plusieurs ilots significatifs; risque de coupes independantes')
    if small>3:warnings.append('Nombreux petits ilots: risque de poussiere de segmentation')
    if holes>0:warnings.append(f'{holes} trous internes, leur aspect peut changer sur le sticker a bord blanc')
    if smooth==0:warnings.append('Masque binaire: le raffinement ne peut pas recreer les details absents')
    return {'pixels_sujet':total,'fraction_petit_ilots':round(isolated_fraction,5),
        'composantes_significatives':significant,'petits_ilots':small,'trous_internes':holes,
        'touche_bord':bool(touch),'pixels_contour':edge_pixels,
        'pixels_semi_transparents':smooth,
        'bbox_px':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],
        'largeur_bbox_mm':round((int(xs.max())-int(xs.min())+1)*mm_per_px,2),
        'alertes':warnings,'confiance_ia':None}


def guided_filter_gray(rgb: np.ndarray, p: np.ndarray, radius:int=3, eps:float=.007):
    """Small edge-aware guided filter using OpenCV core; no opencv-contrib needed."""
    if not 1<=radius<=6:raise ValueError('radius 1..6')
    I=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY).astype('float32')/255
    src=p.astype('float32')
    box=lambda a:cv2.boxFilter(a,cv2.CV_32F,(radius*2+1,)*2,normalize=True,borderType=cv2.BORDER_REFLECT)
    mi=box(I);mp=box(src)
    cov=box(I*src)-mi*mp
    var=box(I*I)-mi*mi
    a=cov/(var+eps)
    b=mp-a*mi
    return np.clip(box(a)*I+box(b),0,1)


def soften_edges(rgb:np.ndarray, mask:np.ndarray, *, radius=2):
    """Refine only a narrow unknown band; no large object drift or magic hair.

    Existing nonbinary masks are preserved. Binary masks receive an optional
    guided-filtered soft edge, but their interior >radius pixels stay untouched.
    """
    arr=np.asarray(rgb,dtype=np.uint8)
    m=np.asarray(mask,dtype=np.float32)
    if arr.shape[:2]!=m.shape or arr.ndim!=3 or arr.shape[2]!=3 or arr.size>3*MAX_PIXELS:
        raise PhotoExtractionError('V19.4: image / masque incompatibles')
    if not np.isfinite(m).all() or m.min()<0 or m.max()>1:raise PhotoExtractionError('Masque hors 0..1')
    if not 1<=radius<=4:raise PhotoExtractionError('Rayon de correction hors limites')
    if np.any((m>0.01)&(m<0.99)):
        return m.copy(),{'applique':False,'raison':'masque alpha deja progressif; original conserve',
                         'pixels_modifies':0,'deplacement_maximal_pixels':0}
    binary=(m>=.5).astype('uint8')
    if not binary.any() or binary.all():
        return m.copy(),{'applique':False,'raison':'masque vide ou image entierement opaque',
                         'pixels_modifies':0,'deplacement_maximal_pixels':0}
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(radius*2+1,)*2)
    outer=cv2.dilate(binary,k)>0
    inner=cv2.erode(binary,k)>0
    candidate=guided_filter_gray(arr,binary.astype('float32'),radius=radius)
    # Hard core and hard distant background remain identical to input.
    refined=m.copy()
    boundary=outer & ~inner
    refined[boundary]=candidate[boundary]
    refined[inner]=1
    refined[~outer]=0
    changed=int(np.count_nonzero(np.abs(refined-m)>.01))
    return refined,{'applique':True,'rayon_bord_pixels':radius,'pixels_modifies':changed,
                    'deplacement_maximal_pixels':radius,
                    'limite':'adoucissement guide par couleur, pas recuperation des cheveux absents'}


def _verify_sha_stable(folder, checksums):
    for name,digest in checksums.items():
        p=folder/name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=digest:
            raise PhotoExtractionError('V19.4: fichier historique modifie '+name)


def process_photo_v194(rgb,output_dir,*,refinement_mode='conservateur',**kwargs):
    if refinement_mode not in ('conservateur','bords_doux'):
        raise PhotoExtractionError('Mode de raffinement inconnu')
    dest=Path(output_dir).expanduser();dest.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.SmartSVG_V194_TEMP_',dir=dest))
    try:
        old,preview=process_photo(rgb,str(stage),**kwargs)
        root=Path(old['output'])
        if root.parent!=stage: raise PhotoExtractionError('Dossier temporaire photo inattendu')
        objects=old['audit_v19']['objets']
        core_files=[]
        for rel in ['01_ORIGINAL.png','rapport_analyse.json','PRET_V19.json']:
            if (root/rel).exists():core_files.append(rel)
        for obj in objects:
            core_files.extend([obj['fichier_rgba'],obj['fichier_cricut_test'],obj['fichier_masque']])
        hashes={rel:hashlib.sha256((root/rel).read_bytes()).hexdigest() for rel in core_files}
        source=np.asarray(Image.open(root/'01_ORIGINAL.png').convert('RGB'))
        w=source.shape[1]
        effective_mm_per_px=float(kwargs.get('width_mm',180))/w
        quality=[]
        warnings=[]
        for obj in objects:
            mask=np.asarray(Image.open(root/obj['fichier_masque']).convert('L'),dtype=np.float32)/255
            metrics=inspect_mask(mask,mm_per_px=effective_mm_per_px)
            if refinement_mode=='bords_doux':
                refined,delta=soften_edges(source,mask,radius=2)
            else:
                refined=None
                delta={'applique':False,'raison':'mode conservateur: masque preserve sans traitement',
                       'pixels_modifies':0,'deplacement_maximal_pixels':0}
            entry={'id':obj['id'],'label':obj['label'],'mesures':metrics,'adoucissement':delta,
                   'originals_preserves':True,'produits_filtres':[]}
            warnings.extend('Objet '+str(obj['id'])+': '+msg for msg in metrics['alertes'])
            if refinement_mode=='bords_doux' and delta['applique'] and delta['pixels_modifies']>0:
                from .photo_geometry_v191 import cutout_with_white_border
                raw,printable,_,geo=cutout_with_white_border(source,refined,
                          mm_per_px=effective_mm_per_px,white_offset_mm=kwargs.get('white_offset_mm',1.5))
                stem=Path(obj['fichier_rgba']).stem.removesuffix('_DETOURE')
                fname=f'02_OBJETS_PNG/{stem}_BORDS_DOUX_EXPERIMENTAL.png'
                pname=f'03_MASQUES/{stem}_BORDS_DOUX_MASQUE.png'
                res=25.4/effective_mm_per_px
                Image.fromarray(raw,'RGBA').save(root/fname,format='PNG',dpi=(res,res))
                Image.fromarray(np.uint8(np.clip(refined*255+.5,0,255)),'L').save(root/pname,format='PNG')
                entry['produits_filtres']=[fname,pname]
                entry['adoucissement']['variantes_cricut_non_certifiees']=True
            quality.append(entry)
        _verify_sha_stable(root,hashes)
        audit={'version':'19.4-beta','source':'analyse quantitative de masques fournis par SAM/Florence/RMBG ou import',
               'raffinement':refinement_mode,'nombre_objets':len(objects),'qualite_objets':quality,
               'chevauchement_pixels_masques':old['audit_v19'].get('chevauchement_pixels',0),
               'avertissements':warnings,'fichiers_historiques_sha256_preserves':True,
               'IA_validee_sur_GPU':False,'decoupe_Cricut_reelle':False,
               'aucune_reconstruction_cheveux_absents':True}
        (root/'QUALITE_DETOURAGE_V19_4.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
        (root/'LIRE_QUALITE_V19_4.txt').write_text(
            'V19.4 — VERIFICATION DES CONTOURS\nLe PNG original et les détourages historiques restent inchangés.\n'
            'Les variantes BORDS_DOUX sont experimentales : elles adoucissent une bordure, ne recreent pas les cheveux.\n'
            'Pour Cricut, prendre CRICUT_TEST.png et verifier les contours dans Design Space.\n'
            'Voir QUALITE_DETOURAGE_V19_4.json pour les trous, ilots, contact bord et transparences.\n',encoding='utf8')
        legacy=root/'PRET_V19.json'
        if legacy.is_file():
            legacy_archive=root/'DIAGNOSTICS_VERSIONS_ANTERIEURES'
            legacy_archive.mkdir(exist_ok=True)
            os.replace(legacy,legacy_archive/'PRET_V19.json')
        (root/'PRET_V19_4.json').write_text(json.dumps({
            'version':'19.4-beta','statut':old['audit_v19']['statut'],
            'test_gpu':False,'test_cricut':False,'fichiers':_manifest(root)},ensure_ascii=False,indent=2),encoding='utf8')
        published=dest/('SmartSVG_V19_4_PHOTO_'+uuid.uuid4().hex[:10])
        os.replace(root,published)
        old['output']=str(published)
        old['audit_v194']=audit
        return old,preview
    except Exception as exc:
        (dest/('SmartSVG_ECHEC_V194_'+uuid.uuid4().hex[:8]+'.json')).write_text(
            json.dumps({'erreur':str(exc),'aucune_sortie_finale_publiee':True},ensure_ascii=False),encoding='utf8')
        raise PhotoExtractionError('SmartSVG V19.4: '+str(exc)) from exc
    finally:
        import shutil
        shutil.rmtree(stage,ignore_errors=True)
