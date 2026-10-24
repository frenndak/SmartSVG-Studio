"""V21 — unified, conservative, source-faithful subject exports for Cricut.

Supports masks from external ComfyUI nodes, optional pre-guarded SAM2 invocation,
and the complete V20.6 no-mask workflow. No semantic object recognition is
asserted unless an external mask provider actually runs. Never labels a cut
contour validated solely because a mask or SVG was produced.
"""
from __future__ import annotations
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
import uuid

import cv2
import numpy as np
from PIL import Image

from . import hd_multisticker_v206 as legacy

MAX_MASKS=32
MAX_MASK_VALUES=50_000_000
MAX_PREVIEW_PX=32_000_000
SEGMENTATION=('desactiver','si_disponible','forcer')
PROMPTS={'affiche':'person;bird', 'logo_cartoon':'dog',
         'capture_produit':'duck', 'scene_decorative':'fox',
         'planche_multi':'', 'auto':'person;animal'}

class V21Error(legacy.ExportError):pass


def _masks_normalize(masks,shape):
    """Accept strict [H,W] or [N,H,W] masks, float 0..1 or uint 0..1/255.

    A 0/1 uint mask must stay nonempty; reject arbitrary uint scales.
    """
    if hasattr(masks,'detach'):
        masks=masks.detach().cpu().numpy()
    data=np.asarray(masks)
    if data.ndim==2:data=data[None]
    if data.ndim!=3 or tuple(data.shape[1:])!=tuple(shape):
        raise V21Error(f'Masques non alignes avec la source : {data.shape} / {shape}')
    if not 1<=data.shape[0]<=MAX_MASKS or data.size>MAX_MASK_VALUES:
        raise V21Error('Nombre ou volume des masques depasse le budget V21')
    if data.dtype.kind not in ('b','u','i','f') or not np.isfinite(data).all():
        raise V21Error('Masques non numeriques ou non finis')
    if data.size==0 or data.min()<0:raise V21Error('Masque negatif ou vide')
    maximum=float(data.max())
    if maximum<=1.00001:
        data=data.astype(np.float32)
    elif data.dtype.kind in ('u','i') and maximum<=255:
        # Not silently normalizing unknown bit depths (e.g. integer 100).
        unique=np.unique(data)
        if np.any((unique!=0)&(unique!=255)):
            raise V21Error('Masque entier non standard : utiliser 0/1 ou 0/255')
        data=data.astype(np.float32)/255.
    else:
        raise V21Error('Masques hors plage 0..1 ou 0/255')
    return np.ascontiguousarray(data,dtype=np.float32)


def _unique_masks(masks,shape):
    source=_masks_normalize(masks,shape)
    selected=[];diagnostics=[]
    for index,m in enumerate(source):
        binary=m>=.5
        pixels=int(binary.sum())
        reason=None
        if pixels<max(30,round(binary.size*.00012)):
            reason='MASQUE_VIDE_OU_TROP_PETIT'
        elif pixels>binary.size*.94:
            reason='MASQUE_COUVRE_PRESQUE_TOUTE_IMAGE'
        else:
            for prev in selected:
                other=prev[1]>=.5
                overlap=np.count_nonzero(binary&other)
                union=pixels+int(other.sum())-overlap
                if union and overlap/union>.97:
                    reason='DOUBLON_QUASI_IDENTIQUE';break
        diagnostics.append({'entree':index+1,'aire_px':pixels,
                            'statut':'REJETE' if reason else 'RETENU',
                            'raison':reason})
        if not reason:selected.append((index,m))
    return selected,diagnostics


def _bbox_positive(alpha):
    ys,xs=np.nonzero(alpha>1./255)
    if not len(xs):return None
    return (int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1))


def _subject_crop(image,mask):
    """Preserve RGB and feathered alpha; keep source alpha when present."""
    m=np.clip(mask.astype(np.float32),0,1)
    if image.shape[2]==4:
        m=m*(image[:,:,3].astype(np.float32)/255.)
    bb=_bbox_positive(m)
    if bb is None:raise V21Error('Masque sans pixels visibles')
    x0,y0,x1,y1=bb
    # Two source pixels of safety margin for semitransparent edges.
    x0=max(0,x0-2);y0=max(0,y0-2)
    x1=min(image.shape[1],x1+2);y1=min(image.shape[0],y1+2)
    pix=image[y0:y1,x0:x1,:3]
    alpha=np.uint8(np.clip(np.round(m[y0:y1,x0:x1]*255),0,255))
    out=np.dstack((pix,alpha))
    return out,(x0,y0,x1,y1)


def _save_atomic(path,image,dpi):
    legacy._save_png(path,image,dpi)


def _report_json(path,data):
    legacy._save_text(path,json.dumps(data,indent=2,ensure_ascii=False,allow_nan=False))


def _pairwise_overlap(mask_a,mask_b):
    a=mask_a>=.5;b=mask_b>=.5
    inter=int(np.count_nonzero(a&b))
    return inter,round(inter/max(1,int(np.count_nonzero(a|b))),4)


def _make_pages(images,stage,final,dpi):
    """Size-safe transparent pages; never reduce individual sticker dimensions."""
    if not images:return []
    capw=170.;caph=240. # conservative planning only, not guaranteed by Cricut
    results=[];queue=list(enumerate(images,1));page=0
    while queue:
        best=None
        for columns in range(1,min(6,len(queue))+1):
            candidate=queue[:min(12,len(queue))]
            sample=[im for _,im in candidate]
            maxw=max(a.width for a in sample)
            maxh=max(a.height for a in sample)
            gap=round(3*dpi/25.4)
            if (columns*maxw+(columns+1)*gap)*25.4/dpi>capw:continue
            rows=max(1,math.floor((caph*dpi/25.4-gap)/(maxh+gap)))
            count=min(len(candidate),columns*rows)
            if count and (best is None or count>best[0]):best=(count,columns)
        if best is None:
            results.append({'statut':'ELEMENT_TROP_GRAND','elements_restants':len(queue),
                            'validation_cricut':False})
            break
        count,columns=best
        take=queue[:count]
        page+=1
        rel=f'03_PLANCHES/PLANCHE_{page:02d}_VERIFIER.png'
        summ=legacy._save_sheet([im for _,im in take],stage/rel,dpi,columns=columns)
        if summ['statut']=='TROP_GRAND':
            results.append({'statut':'LIMITE_PIXELS','elements_restants':len(queue)})
            break
        summ['fichier']=str(final/rel)
        summ['elements_source']=[i for i,_ in take]
        summ['validation_cricut']=False
        if summ['ilots_alpha_detectes']!=len(take):
            summ['statut']='NB_DECOUPES_INCOHERENT_VERIFIER'
        results.append(summ)
        del queue[:count]
    return results


def _render_subjects(image,masks,dest,profile,width_mm,dpi,mode,source,*,defer_pages=False):
    image=legacy._valid_image(image)
    shape=image.shape[:2]
    chosen,audit=_unique_masks(masks,shape)
    if not chosen:raise V21Error('Aucun masque suffisamment fiable : aucun faux detourage cree')
    dest=Path(dest).expanduser().absolute()
    if dest.is_symlink():raise V21Error('Destination symbolique refusee')
    dest.mkdir(parents=True,exist_ok=True)
    final=dest/('SmartSVG_V21_'+uuid.uuid4().hex[:10])
    stage=Path(tempfile.mkdtemp(prefix='.SmartSVG_V21_en_cours_',dir=dest))
    try:
        for directory in ('01_OBJETS','02_CONTOURS','03_PLANCHES','04_CONTROLES'):
            (stage/directory).mkdir()
        _save_atomic(stage/'SOURCE_ORIGINALE.png',Image.fromarray(image),dpi)
        images=[];qa=[];overlaps=[]
        for a,(original_index,mask) in enumerate(chosen):
            for other_index,othermask in chosen[:a]:
                p,iou=_pairwise_overlap(mask,othermask)
                if p>=10:overlaps.append({'entre':[original_index+1,other_index+1],
                                           'pixels_partages':p,'iou':iou,
                                           'a_verifier':True})
        for idx,(original_index,mask) in enumerate(chosen,1):
            rgba,bbox=_subject_crop(image,mask)
            name=f'OBJET_{idx:02d}'
            rel_original=f'01_OBJETS/{name}_DETOURE_TRANSPARENT.png'
            _save_atomic(stage/rel_original,Image.fromarray(rgba,'RGBA'),dpi)
            binary=np.uint8(rgba[:,:,3]>5)*255
            sticker,cut,info=legacy._make_sticker(rgba,binary,width_mm,dpi)
            rel_png=f'01_OBJETS/{name}_IMPRIMER_DECOUPER_VERIFIER.png'
            rel_svg=f'02_CONTOURS/{name}_CONTOUR_SEUL.svg'
            _save_atomic(stage/rel_png,sticker,dpi)
            svg,npaths=legacy._path_svg(cut,info['largeur_finale_avec_marge_mm'],dpi)
            legacy._save_text(stage/rel_svg,svg)
            n_comp=cv2.connectedComponentsWithStats(np.uint8(mask>=.5),8)[0]-1
            info.update({'numero':idx,'entree_masque':original_index+1,'bbox_source':list(bbox),
                         'pixels_source_visibles':int(np.count_nonzero(rgba[:,:,3]>0)),
                         'fragments_masque':int(n_comp),'nombre_chemins':npaths,
                         'source_masque':source,
                         'fichier_transparent':str(final/rel_original),
                         'fichier_png_cricut':str(final/rel_png),
                         'fichier_svg_contour':str(final/rel_svg),
                         'validation_contour':'A_VERIFIER_PAR_HUMAIN',
                         'ne_pas_utiliser_svg_comme_lignes_internes':True})
            if n_comp>1:info['avertissements'].append('MASQUE_FRAGMENTE_A_VERIFIER')
            if npaths!=1:info['avertissements'].append('PLUSIEURS_CHEMINS_DE_COUPE')
            if any(x['entre'][0]==original_index+1 or x['entre'][1]==original_index+1 for x in overlaps):
                info['avertissements'].append('OBJET_EN_RECOUVREMENT_VERIFIER')
            qa.append(info);images.append(sticker)
        overview=legacy._preview(images,min(6,len(images)))
        _save_atomic(stage/'04_CONTROLES/APERCU_SUJETS.png',overview,dpi)
        pages=(_make_pages(images,stage,final,dpi) if not defer_pages else []) if mode=='sticker_contour' else []
        result={'version':'21.0-beta','profil':profile,'operation':mode,
                'dossier':str(final),'statut':'MASQUES_DISPONIBLES_CONTOURS_A_VERIFIER',
                'provenance_masques':source,'nombre_objets_exportes':len(qa),
                'nombre_masques_recus':len(audit),'tri_des_masques':audit,
                'recouvrements':overlaps,'objets':qa,'planches':pages,
                'qualite_fichier_png':'INTERPOLATION_CLASSIQUE_SANS_NOUVEAUX_DETAILS',
                'validation_decoupe_cricut':False,'inference_ia_gpu_prouvee':False,
                'apercu':str(final/'04_CONTROLES/APERCU_SUJETS.png')}
        _report_json(stage/'RAPPORT_V21.json',result)
        os.replace(stage,final)
        return result,overview
    except BaseException:
        shutil.rmtree(stage,ignore_errors=True)
        raise


def run_v21(pixels,destination,profile='auto',width_mm=40,dpi=300,
            operation='sticker_contour',grid='6x4',segmentation='desactiver',masks=None,
            provider=None,gpu=None,*,defer_pages=False):
    """Production with optional external masks or actual SAM2; safe V20.6 fallback.

    provider(rgb, prompt) can be injected for testing. No inference is emulated.
    """
    legacy._valid_image(pixels)
    if profile not in legacy.PRESETS or operation not in legacy.CUTS or dpi not in legacy.DPI or grid not in ('6x4','4x3','3x3','auto'):
        raise V21Error('Configuration V21 invalide')
    if segmentation not in SEGMENTATION:raise V21Error('Mode IA invalide')
    if isinstance(width_mm,bool) or not math.isfinite(float(width_mm)) or not 15<=float(width_mm)<=180:
        raise V21Error('Taille invalide')
    # A requested rectangular card takes precedence over object segmentation.
    # Do not burn GPU and then silently make stickers despite this user choice.
    if operation=='carte_rectangle' and profile!='planche_multi':
        report,preview=legacy.run_v206(pixels,destination,profile,width_mm,dpi,operation,grid)
        report['v21']={'version':'21.0-beta','mode':'CADRE_RECTANGULAIRE_CHOISI',
                       'masques_fournis_ignores':masks is not None,
                       'ia_interne_non_executee':True,
                       'separation_semantique_effectuee':False,
                       'raison':'Operation Cricut cadre rectangulaire explicitement choisie'}
        _report_json(Path(report['dossier'])/'RAPPORT_V21.json',report)
        return report,preview
    metadata={'statut':'NON_DEMANDE','fournisseur':None}
    provided=masks
    if provided is not None:
        metadata={'statut':'MASQUES_EXTERNES_REÇUS','fournisseur':'MASK_COMFYUI'}
    elif segmentation!='desactiver' and profile!='planche_multi':
        if provider is None:
            from .auto_segment_v192 import segment_scene
            provider=lambda rgb,prompt:segment_scene(rgb,profile='auto',custom_prompts=prompt)
        if gpu is None:
            from .gpu_budget_v203 import gpu_snapshot,policy_decision
            check=policy_decision(gpu_snapshot(),policy='protege',ia=('forcer' if segmentation=='forcer' else 'auto'))
            if check['action']!='PROCEDER':
                metadata={'statut':'IA_NON_EXECUTEE_BUDGET_GPU','garde_fou':check}
                if segmentation=='forcer':raise V21Error('IA demandee explicitement mais GPU indisponible/insuffisant')
            else:metadata={'statut':'GOULET_GPU_FRANCHI','garde_fou':check}
        else:
            metadata={'statut':'GOULET_GPU_TEST_SIMULE','avertissement':'Pas une verification CUDA reelle'}
        if metadata['statut'] in ('GOULET_GPU_FRANCHI','GOULET_GPU_TEST_SIMULE'):
            try:
                choice=legacy._source_preset(pixels[:,:,:3]) if profile=='auto' else profile
                prompt=PROMPTS[choice]
                # Specific, non-empty and bounded prompts only.
                inference=provider(pixels[:,:,:3],prompt)
                provided=inference.get('masks')
                metadata.update({'statut':'IA_APPELEE','fournisseur':inference.get('audit',{}),
                                 'masques_retournes':0 if provided is None else (int(np.asarray(provided).shape[0]) if np.asarray(provided).ndim==3 else 1)})
            except Exception as exc:
                metadata={'statut':'ECHEC_IA','erreur':f'{type(exc).__name__}: {str(exc)[:150]}'}
                if segmentation=='forcer':raise V21Error('Segmentation IA obligatoire echouee') from exc
    if provided is not None:
        # External invalid masks = hard failure. In optional *internal* mode,
        # bad/no masks = explicit fallback instead of a false subject.
        external=(masks is not None)
        try:
            normalized=_masks_normalize(provided,pixels.shape[:2])
            result,preview=_render_subjects(pixels,normalized,destination,profile,width_mm,dpi,operation,metadata['statut'],defer_pages=defer_pages)
        except V21Error as exc:
            if external or segmentation=='forcer':raise
            metadata={'statut':'IA_SANS_MASQUE_VALIDE_REPLI',
                      'erreur':f'{type(exc).__name__}: {str(exc)[:155]}',
                      'aucune_segmentation_claim':True}
        else:
            result['analyse_ia']=metadata
            _report_json(Path(result['dossier'])/'RAPPORT_V21.json',result)
            return result,preview
    report,preview=legacy.run_v206(pixels,destination,profile,width_mm,dpi,operation,grid)
    report['v21']={'version':'21.0-beta','mode':'REPLI_V20_6_SANS_MASQUE',
                   'masque_ia_obtenu':False,'analyse_ia':metadata,
                   'separation_semantique_effectuee':False,
                   'message':'Exports conservateurs; seule une IA/MASK peut detourer un sujet sur fond complexe.'}
    _report_json(Path(report['dossier'])/'RAPPORT_V21.json',report)
    return report,preview
