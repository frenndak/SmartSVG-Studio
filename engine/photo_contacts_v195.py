"""V19.5: overlap QA and OPTIONAL proposed per-object exclusive masks.

Never alter original masks or Cricut printing files. Masks may overlap legitimately
(e.g. fingers before a beer glass) and no heuristic can reconstruct hidden pixels.
"""
from __future__ import annotations
import json
import hashlib
import os
import shutil
import tempfile
import uuid
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from .photo_detail_v194 import process_photo_v194, inspect_mask
from .photo_v19 import PhotoExtractionError

MAX_MASK_PIXELS_TOTAL = 32_000_000
MAX_OBJECTS = 16
VERSION = '19.5.2-beta'


def _validate_mask_set(masks):
    """Validate all masks BEFORE distance transforms or pairwise comparisons.

    Bound the combined source pixels, reject NaN/dtype mismatches and reject
    shapes that might otherwise broadcast with hard-to-diagnose errors.
    """
    if not isinstance(masks, (list, tuple)) or len(masks)>MAX_OBJECTS:
        raise PhotoExtractionError('V19.5.1: 16 masques au maximum')
    if not masks:
        return [], None
    shape=None
    total=0
    for m in masks:
        if not isinstance(m, np.ndarray) or m.dtype!=np.uint8 or m.ndim!=2:
            raise PhotoExtractionError('V19.5.1: masque numpy uint8 en niveaux de gris 2D attendu')
        if m.size==0 or min(m.shape)<=0:
            raise PhotoExtractionError('V19.5.1: masque vide ou dimensions nulles')
        if shape is None: shape=m.shape
        if m.shape!=shape:
            raise PhotoExtractionError('V19.5.1: tailles des masques incompatibles')
        total+=m.size
        if total>MAX_MASK_PIXELS_TOTAL:
            raise PhotoExtractionError('V19.5.1: budget memoire total de 32 millions de pixels depasse')
    # PNG masks are normally 0..255, but some ComfyUI/Python integrations
    # provide uint8 binary 0/1. Treat that explicitly rather than silently
    # reporting zero overlap for real foreground pixels.
    normalized=[]
    for m in masks:
        if m.max()<=1:
            normalized.append(m>0)
        else:
            normalized.append(m>=128)
    return normalized,shape


def _mask_path_inside_root(root, relative):
    """Reject absolute paths, traversal and symlinks in a purported mask file."""
    if not isinstance(relative, str) or not relative or '\x00' in relative:
        raise PhotoExtractionError('V19.5.1: chemin de masque vide ou invalide')
    rel=Path(relative)
    if rel.is_absolute() or '..' in rel.parts or rel.parts[0] != '03_MASQUES':
        raise PhotoExtractionError('V19.5.1: chemin de masque externe au dossier securise')
    # Anchor against the actual staging root, not the resolved directory
    # itself: a malicious symlink at 03_MASQUES would otherwise redefine the
    # trusted root and make external paths appear valid.
    staging=root.resolve()
    expected_root=staging/'03_MASQUES'
    if expected_root.is_symlink() or not expected_root.is_dir():
        raise PhotoExtractionError('V19.5.2: dossier des masques absent ou lien symbolique')
    resolved=(staging/rel).resolve()
    if not resolved.is_relative_to(expected_root):
        raise PhotoExtractionError('V19.5.2: chemin de masque resolu hors repertoire')
    if resolved.is_symlink():
        raise PhotoExtractionError('V19.5.2: masque lien symbolique interdit')
    return resolved


def _manifest_streamed(root):
    """Hash files in bounded memory, including QA reports and experimental files."""
    info={}
    for path in sorted(root.rglob('*')):
        if not path.is_file() or path.name=='PRET_V19_5_2.json':
            continue
        h=hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda:f.read(1024*1024),b''):
                h.update(block)
        info[path.relative_to(root).as_posix()]={'octets':path.stat().st_size, 'sha256':h.hexdigest()}
    return info


def _load_masks(folder:Path, objects:list, expected_shape=None):
    if len(objects)>MAX_OBJECTS:
        raise PhotoExtractionError('V19.5: nombre de masques trop eleve')
    result=[];shape=None;pixel_sum=0
    for entry in objects:
        mask_path=_mask_path_inside_root(folder,entry['fichier_masque'])
        # Read only PNG header metadata first. Avoid decoding a compressed
        # 50MP mask before discovering it violates the 32M pixel budget.
        with Image.open(mask_path) as im:
            if im.format!='PNG' or im.mode!='L':
                raise PhotoExtractionError('V19.5.2: masque PNG gris requis')
            w,h=im.size
            if w<=0 or h<=0:
                raise PhotoExtractionError('V19.5.2: dimensions masque invalides')
            pixel_sum+=w*h
            if pixel_sum>MAX_MASK_PIXELS_TOTAL:
                raise PhotoExtractionError('V19.5.2: budget pixels depasse AVANT decodage')
            if shape is not None and shape!=(h,w):
                raise PhotoExtractionError('V19.5.2: les masques n ont pas les memes dimensions')
            if expected_shape is not None and tuple(expected_shape)!=(h,w):
                raise PhotoExtractionError('V19.5.2: masque incoherent avec image SOURCE')
            # This load is deliberately AFTER the header-only budget check.
            mask=np.asarray(im,dtype=np.uint8).copy()
        if shape is None:shape=mask.shape
        result.append(mask)
    return result


def analyze_overlaps(masks:list[np.ndarray],mm_per_px:float):
    """Pairwise independent overlap analysis. Values are observations not AI scores."""
    if not 0<mm_per_px<=10:raise PhotoExtractionError('V19.5: echelle mm invalide')
    if not masks:
        return {'nombre_objets':0,'pixels_en_commun':0,'pourcentage_image_en_commun':0.0,
                'paires':[],'nombre_paires_chevauchantes':0}
    binary,shape=_validate_mask_set(masks)
    cover=np.zeros(shape,np.uint8)
    for b in binary:cover+=b.astype(np.uint8)
    pairs=[]
    for i in range(len(masks)):
        for j in range(i+1,len(masks)):
            p=int(np.count_nonzero(binary[i]&binary[j]))
            if p==0:continue
            a=int(binary[i].sum());b=int(binary[j].sum())
            ratio=p/max(1,min(a,b))
            pairs.append({'objet_a':i+1,'objet_b':j+1,'pixels_communs':p,
                          'surface_commune_mm2':round(p*mm_per_px**2,2),
                          'fraction_du_plus_petit_pct':round(100*ratio,2),
                          'situation':'fort_recouvrement_a_verifier' if ratio>=.3 else 'zone_de_contact_a_verifier'})
    union=int(np.count_nonzero(cover>1))
    return {'nombre_objets':len(masks),'pixels_en_commun':union,
            'pourcentage_image_en_commun':round(100*union/cover.size,4),
            'nombre_paires_chevauchantes':len(pairs),'paires':pairs,
            'portee':'chevauchements observes, pas preuve d erreur de segmentation'}


def propose_exclusive_masks(masks:list[np.ndarray]):
    """Tentative geometric disambiguation using *exclusive* seeds.

    Pixels where a unique owner is present are held exactly. Shared pixels are
    given to closest reliable owner; ties are marked unresolved, not assigned.
    If 2 masks are almost identical, reject proposal (no reliable seeds).
    """
    binary,shape=_validate_mask_set(masks)
    if len(binary)<2:return None, {'proposition_valide':False,'motif':'moins de deux masques'}
    count=np.zeros(shape,np.uint8)
    for b in binary:count+=b.astype(np.uint8)
    shared=count>1
    if not shared.any():return None, {'proposition_valide':False,'motif':'aucun chevauchement'}
    seeds=[(b & (count==1)) for b in binary]
    coverage=[int(s.sum())/max(1,int(b.sum())) for s,b in zip(seeds,binary)]
    if any(v<.02 for v in coverage):
        return None, {'proposition_valide':False,'motif':'zones exclusives insuffisantes : masques identiques ou imbriques',
                      'fractions_exclusives':coverage}
    # Memory bounded ownership computation. V19.5 stacked and sorted all N
    # complete float32 distance maps (possibly hundreds of MiB). Keep only
    # the smallest and second-smallest eligible distances, plus a winner ID.
    best=np.full(shape,np.inf,np.float32)
    second=np.full(shape,np.inf,np.float32)
    winners=np.full(shape,-1,np.int16)
    for i,(seed,eligible_mask) in enumerate(zip(seeds,binary)):
        distance=cv2.distanceTransform((~seed).astype('uint8'),cv2.DIST_L2,5)
        eligible=shared & eligible_mask
        improved=eligible & (distance<best)
        second[improved]=best[improved]
        best[improved]=distance[improved]
        winners[improved]=i
        runner=eligible & (~improved) & (distance<second)
        second[runner]=distance[runner]
        # Drop the full distance image before processing the next mask.
        del distance,eligible,improved,runner
    if np.any(shared & (winners<0)) or np.any(shared & ~np.isfinite(second)):
        raise PhotoExtractionError('V19.5.1: partage sans deux proprietaires valides')
    # Compare only on pixels where both candidates are finite (no inf-inf).
    ambiguous=np.zeros(shape,dtype=bool)
    ambiguous[shared]=(second[shared]-best[shared])<=1.0
    proposed=[]
    for i,m in enumerate(masks):
        # Normalize uint8 0/1 to actual 8-bit PNG mask output. Ordinary
        # 0..255 masks, including softly anti-aliased values, are unchanged.
        out=(m*255).astype(np.uint8) if int(m.max())<=1 else m.copy()
        out[shared & ((winners!=i)|ambiguous)]=0
        proposed.append(out)
    result_overlap=sum(int(np.count_nonzero((x>=128)&(y>=128))) for i,x in enumerate(proposed)
                       for y in proposed[i+1:])
    if result_overlap:
        raise PhotoExtractionError('V19.5: proposition encore chevauchante')
    attributed=int(shared.sum())-int(ambiguous.sum())
    if attributed<=0:
        return None, {'proposition_valide':False,
                      'motif':'100 % des pixels partages restent ambigus',
                      'pixels_restant_ambigus':int(ambiguous.sum())}
    return proposed, {'proposition_valide':True,'pixels_partages':int(shared.sum()),
                      'pixels_partages_attribues':attributed,
                      'pourcentage_partage_attribue':round(100*attributed/int(shared.sum()),2),
                      'pixels_restant_ambigus':int(ambiguous.sum()),
                      'seuil_ambiguite_px':1.0,'fractions_exclusives':coverage,
                      'methodologie':'plus proche zone exclusive, sans reconstruire les parties cachees',
                      'pour_cricut_directement':False,
                      'distance_memory_strategy':'two_best_maps_not_full_stack',
                      'non_semantic_geometric_proposal':True}


def _overlay_preview(source:np.ndarray, masks:list[np.ndarray], output:Path):
    if source.ndim!=3 or source.shape[2]!=3:raise PhotoExtractionError('V19.5: source RGB attendue')
    h,w=source.shape[:2]
    if any(m.shape!=(h,w) for m in masks):raise PhotoExtractionError('V19.5: aperçu masques non alignes')
    base=source.copy()
    colors=[(240,65,77),(31,184,166),(255,182,53),(75,146,243)]
    cover=np.zeros((h,w),np.uint8)
    for i,m in enumerate(masks):
        binary=m>=128
        cover+=binary.astype(np.uint8)
        contours,_=cv2.findContours(binary.astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(base,contours,-1,colors[i%4],max(1,round(w/600)))
    overlapping=cover>1
    if overlapping.any():
        base[overlapping]=np.clip(base[overlapping].astype('float32')*.35+
                                  np.array([255,0,250],np.float32)*.65,0,255).astype('uint8')
    im=Image.fromarray(base,'RGB')
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,min(w,500),28),fill=(15,25,36))
    d.text((7,7),f'CONTACTS : {int(overlapping.sum())} pixels (magenta)',fill=(255,255,255))
    im.save(output,format='PNG',optimize=True)



def _proposal_preview(source,originals,proposed,output):
    """Visualize ONLY allocations in formerly shared regions, never an export mask.

    Green/blue/amber = newly attributed pixels, magenta = unresolved. This
    preview is deliberately diagnostic and must not be used for Print Then Cut.
    """
    h,w=source.shape[:2]
    if any(m.shape!=(h,w) for m in originals+proposed):
        raise PhotoExtractionError('V19.5.1: aperçu de proposition non aligne')
    count=np.zeros((h,w),np.uint8)
    for m in originals: count+=(m>=128).astype(np.uint8)
    shared=count>1
    mapped=np.zeros((h,w),np.uint8)
    overlay=source.copy()
    colors=[(35,210,95),(30,136,255),(255,196,25),(137,82,234)]
    for i,m in enumerate(proposed):
        sel=shared & (m>=128)
        mapped[sel]+=1
        color=np.asarray(colors[i%len(colors)],dtype=np.float32)
        overlay[sel]=np.clip(.3*overlay[sel].astype(np.float32)+.7*color,0,255).astype('uint8')
    if np.any(mapped>1):
        raise PhotoExtractionError('V19.5.1: aperçu revele une proposition encore chevauchante')
    unresolved=shared & (mapped==0)
    overlay[unresolved]=[255,0,250]
    image=Image.fromarray(overlay,'RGB');draw=ImageDraw.Draw(image)
    draw.rectangle((0,0,min(w,700),33),fill=(15,24,39))
    draw.text((7,8),f'EXPERIMENTAL / NON CRICUT : {int(shared.sum())} partages, {int(unresolved.sum())} ambigus',fill=(255,255,255))
    image.save(output,format='PNG',optimize=True)
    return {'pixels_initiaux_partages':int(shared.sum()),
            'pixels_nouveaux_attribues':int(shared.sum()-unresolved.sum()),
            'pixels_restants_non_attribues':int(unresolved.sum())}


def _sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def _audit_cricut_alpha_coverage(folder:Path, objects:list):
    """Guarantee all surviving translucent subject pixels have a white printable base.

    This is a software alpha-support guarantee, not physical Cricut validation.
    Historic full-color cutouts are not rewritten by this function.
    """
    result=[]
    for item in objects:
        with Image.open(folder/item['fichier_rgba']) as f:
            if f.mode!='RGBA':raise PhotoExtractionError('V19.5.2: extraction non RGBA')
            original_alpha=np.asarray(f.getchannel('A'),dtype=np.uint8)
        with Image.open(folder/item['fichier_cricut_test']) as f:
            if f.mode!='RGBA':raise PhotoExtractionError('V19.5.2: PNG Cricut non RGBA')
            print_alpha=np.asarray(f.getchannel('A'),dtype=np.uint8)
        padding=int(item['geometrie_cricut']['padding_px'])
        h,w=original_alpha.shape
        if padding<0 or print_alpha.shape!=(h+2*padding,w+2*padding):
            raise PhotoExtractionError('V19.5.2: decalage et taille PNG Cricut incompatibles')
        inset=print_alpha[padding:padding+h,padding:padding+w]
        missing=int(np.count_nonzero((original_alpha>0)&(inset==0)))
        if missing:
            raise PhotoExtractionError('V19.5.2: %d pixels source invisibles sur PNG Cricut'%missing)
        result.append({'objet':int(item['id']),'pixels_visibles_reference':int(np.count_nonzero(original_alpha)),
                       'pixels_hors_base_blanche':missing,
                       'controle_support_alpha':'OK',
                       'ne_certifie_pas_la_decoupe_physique':True})
    return result


def process_photo_v195(rgb,output_dir,*,contact_mode='conservateur',**kwargs):
    if contact_mode not in ('conservateur','proposer_separation'):
        raise PhotoExtractionError('V19.5: mode contacts invalide')
    base=Path(output_dir).expanduser();base.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.SmartSVG_V195_TEMP_',dir=base))
    try:
        prior,preview=process_photo_v194(rgb,str(stage),**kwargs)
        folder=Path(prior['output'])
        if folder.parent!=stage:raise PhotoExtractionError('V19.5: chemin staging inattendu')
        old_objects=prior['audit_v19']['objets']
        protected=[p for p in folder.rglob('*') if p.is_file()]
        old_hash={str(p.relative_to(folder)):_sha(p) for p in protected}
        with Image.open(folder/'01_ORIGINAL.png') as img:source=np.asarray(img.convert('RGB'))
        masks=_load_masks(folder,old_objects,expected_shape=source.shape[:2])
        alpha_coverage=_audit_cricut_alpha_coverage(folder,old_objects)
        scale=float(kwargs.get('width_mm',180))/source.shape[1]
        qa=analyze_overlaps(masks,scale)
        object_qa=[]
        for item,mask in zip(old_objects,masks):
            detail=inspect_mask(mask.astype('float32')/255,mm_per_px=scale)
            object_qa.append({'objet':item['id'],'label':item['label'],
                              'confiance_ia':None,'mesures':detail})
        variants=[]; proposal={'proposition_valide':False,'motif':'mode conservateur'}
        proposal_preview=None; allocation_checks=None
        if contact_mode=='proposer_separation':
            adjusted,proposal=propose_exclusive_masks(masks)
            if adjusted is not None:
                out=folder/'05_PROPOSITIONS_CONTACTS'
                out.mkdir(exist_ok=True)
                for item,mask in zip(old_objects,adjusted):
                    basename=f'{int(item["id"]):02d}_CONTACTS_EXPERIMENTAL_MASQUE.png'
                    dest=out/basename
                    Image.fromarray(mask,'L').save(dest,format='PNG')
                    variants.append(str(dest.relative_to(folder)))
                proposal_preview='05_PROPOSITIONS_CONTACTS/APERCU_REPARTITION_EXPERIMENTALE.png'
                allocation_checks=_proposal_preview(source,masks,adjusted,folder/proposal_preview)
        _overlay_preview(source,masks,folder/'CONTROLE_CHEVAUCHEMENTS_V19_5.png')
        warnings=[]
        if qa['pixels_en_commun']:
            warnings.append('Chevauchement entre objets: peut representer une occlusion naturelle, ne pas supprimer automatiquement')
        if proposal.get('pixels_restant_ambigus',0):
            warnings.append('Des pixels ambigus restent non attribues dans les propositions experimentales')
        report={'version':VERSION,'mode_contacts':contact_mode,'nombre_objets':len(old_objects),
                'qualite':object_qa,'contacts':qa,'proposition_separation':proposal,
                'fichiers_experimentaux':variants,'apercu':'CONTROLE_CHEVAUCHEMENTS_V19_5.png',
                'apercu_proposition_experimentale':proposal_preview,
                'controle_attribution':allocation_checks,
                'controle_support_alpha_cricut':alpha_coverage,
                'avertissements':warnings,'sources_et_exports_cricut_originaux_preserves':True,
                'schema_masks_accepte':'uint8 0..255 ou binaire 0/1; PNG interne sur 0..255',
                'validation_inference_ia_reelle':False,'validation_design_space':False,
                'aucune_reconstruction_objets_caches':True}
        for relative,expected in old_hash.items():
            if _sha(folder/relative)!=expected:
                raise PhotoExtractionError('V19.5: un fichier historique a change '+relative)
        # Preserve old diagnostics, publish only latest READY at root.
        oldready=folder/'PRET_V19_4.json'
        if oldready.is_file():
            d=folder/'DIAGNOSTICS_VERSIONS_ANTERIEURES'
            d.mkdir(exist_ok=True)
            os.replace(oldready,d/oldready.name)
        (folder/'QUALITE_DETOURAGE_V19_5_2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
        (folder/'LIRE_QUALITE_V19_5_2.txt').write_text(
            'V19.5.1: le detourage RGBA original et le fichier CRICUT_TEST restent inchanges.\n'
            'Les zones magenta signalent les chevauchements ; certains sont legitimement des mains devant un objet.\n'
            '05_PROPOSITIONS_CONTACTS contient seulement des MASK experimentaux et non des fichiers Cricut certifies.\n'
            'Ces masques ne reconstruisent ni doigts ni parties cachees.\n'
            'APERCU_REPARTITION_EXPERIMENTALE : couleurs = pixels attribues, magenta = pixels non resolus.\n',encoding='utf8')
        (folder/'PRET_V19_5_2.json').write_text(json.dumps({
            'version':VERSION,'statut':prior['audit_v19']['statut'],
            'contacts':qa['nombre_paires_chevauchantes'],
            'test_gpu_reel':False,'test_cricut_reel':False,'fichiers':_manifest_streamed(folder)},
            ensure_ascii=False,indent=2),encoding='utf8')
        published=base/('SmartSVG_V19_5_2_PHOTO_'+uuid.uuid4().hex[:10])
        os.replace(folder,published)
        prior['output']=str(published)
        prior['audit_v195']=report
        return prior,preview
    except Exception as e:
        (base/('SmartSVG_ECHEC_V1952_'+uuid.uuid4().hex[:8]+'.json')).write_text(
            json.dumps({'erreur':str(e),'aucune_sortie_validee_publiee':True},ensure_ascii=False),encoding='utf8')
        raise PhotoExtractionError('SmartSVG V19.5.2: '+str(e)) from e
    finally:
        shutil.rmtree(stage,ignore_errors=True)
