"""V18: optional object-mask-driven editable vector proposals.

Production Print Then Cut outputs are GENERATED ONLY by V17, untouched by
this experimental branch. No automatic semantic-label assertion is made.
"""
from __future__ import annotations
from datetime import datetime
import copy
import json
import hashlib
import os
from pathlib import Path
import re
import shutil
import tempfile
import uuid
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .engine_v11 import UnsafeCut
from .engine_v12 import _json_default
from .engine_v14 import CRICUT_SVG, NAME
from .engine_v15 import SVG, _mm, _validate_safe_svg
from .engine_v16 import KIT, _fingerprint_folder
from .engine_v17 import process_v17

VERSION = '18.1-beta'
OBJECT_SVG = 'CRICUT_EDITION_OBJETS_PROPOSES.svg'
OBJECT_FIDELITY = 'CRICUT_EDITION_OBJETS_FIDELITE.svg'
OBJECT_PROOF = 'CONTROLE_OBJETS_PROPOSES.png'
OBJECT_REPORT = 'rapport_V18_1.json'
STATUS = 'PRET_V18_1.json'


def _safe_id(s):
    s = re.sub(r'[^A-Za-z0-9_-]+', '_', str(s)).strip('_')[:36]
    return s or 'OBJET'


def _validate_masks(masks, shape):
    """External segmentation masks expected already registered to finished sheet."""
    if masks is None: return None
    arr=np.asarray(masks)
    if arr.ndim==2:arr=arr[None]
    if arr.ndim!=3 or arr.shape[1:]!=shape or not 1<=arr.shape[0]<=16 or arr.size>25000000:
        raise ValueError(f'Masques objets: attendu [N,{shape[0]},{shape[1]}] avec 1..16 masques et au plus 25 millions de pixels, recu {arr.shape}')
    if not np.issubdtype(arr.dtype, np.number) or not np.all(np.isfinite(arr)):
        raise ValueError('Masques objets: valeurs invalides (NaN ou type incorrect)')
    if arr.min() < -0.001 or arr.max()>1.001:
        raise ValueError('Masques objets: valeurs en dehors de 0..1')
    return (arr.astype(np.float32) >= 0.5)


def _auto_proposals(rgb,mask,max_objects=6):
    """Connected hue-family candidates (NOT semantic object recognition).

    Hue separation prevents a red shell and a green body being joined merely
    because their colorful pixels touch. A candidate can still be a fragment.
    """
    if mask.sum()<100:return []
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    saturated=(hsv[:,:,1]>68)&(hsv[:,:,2]>55)&(hsv[:,:,2]<251)&mask
    min_pixels=max(30,int(mask.sum()*.018))
    kernel=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
    entries=[]
    for hue_family in range(12):
        hue_mask=saturated & ((hsv[:,:,0]//15)==hue_family)
        closed=cv2.morphologyEx(hue_mask.astype('uint8'),cv2.MORPH_CLOSE,kernel)>0
        closed &= mask
        n,labels,stats,_=cv2.connectedComponentsWithStats(closed.astype('uint8'),8)
        for i in range(1,n):
            area=int(stats[i,cv2.CC_STAT_AREA])
            if min_pixels<=area < mask.sum()*.88:
                entries.append((area,hue_family,(labels==i)))
    entries.sort(key=lambda x:-x[0])
    proposals=[];covered=np.zeros(mask.shape,dtype=bool)
    for area,family,pixels in entries:
        part=pixels & ~covered
        if int(part.sum()) < min_pixels:continue
        proposals.append(part)
        covered|=part
        if len(proposals)>=max_objects:break
    return proposals


def _contour_d(binary, shift_x=0, shift_y=0):
    """Closed polygon paths with holes via evenodd; no unsupported SVG filters.

    OpenCV contours are approximate - editing SVG is an approximation, not the
    pixel-identical reference PNG. Print pipeline remains unchanged.
    """
    if not np.any(binary):return ''
    contours,_=cv2.findContours(binary.astype('uint8'),cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    segments=[]
    for c in contours:
        if len(c)<3 or cv2.contourArea(c)<1.5:continue
        approx=cv2.approxPolyDP(c,0.55,True).reshape(-1,2)
        if len(approx)<3:continue
        xs=[f'{int(x)+shift_x},{int(y)+shift_y}' for x,y in approx]
        segments.append('M '+' L '.join(xs)+' Z')
    return ' '.join(segments)


def _rgb_palette(rgb, sticker_mask, colors):
    """Palette over nontransparent sticker area; deterministic and fast."""
    arr=np.ascontiguousarray(rgb,dtype=np.uint8)
    from PIL import Image
    # Quantize once per sticker, not once per object.
    img=Image.fromarray(arr,'RGB')
    q=img.quantize(colors=int(colors),method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    indices=np.asarray(q,dtype=np.uint8)
    palette=np.asarray(q.getpalette(),dtype=np.uint8).reshape(-1,3)
    return indices,palette


def _make_fidelity_groups(work, proposal_maps, width, height, labels=()):
    """Assign original paths by rasterized shape intersection, preserving paint order.

    There are *consecutive groups* for each candidate rather than moving all
    regions together: changing z-order may alter the drawing. Original SVG
    d/fill strings and the parent sticker transform remain unchanged.
    """
    from .engine_v15 import REGION_SVG
    from .overlap_assigner import path_mask, assign_by_overlap
    original=ET.parse(work/REGION_SVG).getroot()
    faithful=ET.Element(SVG+'svg',{k:original.attrib[k] for k in ('width','height','viewBox')})
    changed=0;residual_count=0;ambiguous=0;switches=0
    for idx,oldgroup in enumerate([g for g in original if g.tag==SVG+'g'],1):
        x0,y0,proposals=proposal_maps[idx]
        tr=oldgroup.attrib.get('transform','')
        tx=ty=0.0
        if tr:
            t=re.fullmatch(r'translate\(\s*([-+\d.]+)[ ,]+([-+\d.]+)\s*\)',tr)
            if t is None:raise UnsafeCut('V18.1: transform SVG inconnu: '+tr[:100])
            tx,ty=map(float,t.groups())
        group=ET.SubElement(faithful,SVG+'g',dict(oldgroup.attrib))
        if not len(oldgroup):raise UnsafeCut('V18.1: SVG sans calques')
        group.append(copy.deepcopy(oldgroup[0]))
        last_name=None;run=None;serial=0
        local_masks=[m for _,m in proposals]
        for oldlayer in list(oldgroup)[1:]:
            for p in oldlayer.iter(SVG+'path'):
                if local_masks:
                    mask=path_mask(p.get('d',''),local_masks[0].shape,(tx-x0,ty-y0))
                    candidate,details=assign_by_overlap(mask,local_masks)
                else:
                    candidate,details=-1,{'raison':'aucun_masque'}
                if candidate>=0:
                    orig_idx=proposals[candidate][0]
                    tag=(f'OBJET_{candidate+1:02d}_'+
                         (labels[orig_idx] if orig_idx<len(labels) else 'PROPOSITION'))
                    changed+=1
                else:
                    tag='RESIDUEL_A_VERIFIER'
                    residual_count+=1
                    if details['raison']=='indecidable':ambiguous+=1
                if tag!=last_name:
                    serial+=1;switches+=1
                    run=ET.SubElement(group,SVG+'g',{'id':f'S{idx:02d}_{tag}_ORDRE_{serial:03d}'})
                    last_name=tag
                run.append(copy.deepcopy(p))
    _validate_safe_svg(faithful)
    dest=work/OBJECT_FIDELITY
    ET.ElementTree(faithful).write(dest,encoding='utf8',xml_declaration=True)
    fidelity={'test_effectue':False,'rendu_equivalent_a_la_source':False}
    try:
        import cairosvg
        from io import BytesIO
        def render(file):
            return np.asarray(Image.open(BytesIO(cairosvg.svg2png(url=str(file),
                    output_width=width,output_height=height))).convert('RGBA'))
        a=render(work/REGION_SVG);b=render(dest)
        dif=np.abs(a.astype('int16')-b.astype('int16'))
        changed_px=int(np.count_nonzero(np.max(dif,axis=2)>15))
        fidelity={'test_effectue':True,'pixels_differents_seuil_15':changed_px,
                  'pourcentage_pixels_differents':round(100*changed_px/(width*height),5),
                  'rendu_equivalent_a_la_source':changed_px/(width*height)<.0001}
    except ImportError:pass
    return {'cree':True,'fichier':OBJECT_FIDELITY,'chemins_reclasses':changed,
            'chemins_residuels':residual_count,'formes_ambigues':ambiguous,
            'groupes_ordre_de_peinture':switches,
            'nombre_chemins':len(list(faithful.iter(SVG+'path'))),
            'attribution':'intersection_geometrique',
            'ordre_de_peinture_conserve':True,'equivalence_source':fidelity}


def _process_sheet_objects(work:Path, *, masks=None, labels='', colors=10, mode='auto'):
    with Image.open(work/NAME) as im: rgba=np.asarray(im.convert('RGBA'))
    h,w=rgba.shape[:2]
    physical=ET.parse(work/CRICUT_SVG).getroot()
    width_mm=_mm(physical.get('width'));height_mm=_mm(physical.get('height'))
    source_groups=[g for g in physical if g.tag==SVG+'g']
    alpha=rgba[...,3]>127
    n, components, stats,centroids=cv2.connectedComponentsWithStats(alpha.astype('uint8'),8)
    count=n-1
    if count!=len(source_groups):raise UnsafeCut('V18: groupes sticker / PNG differents')
    ext=None; mask_error=None
    if masks is not None:
        try:ext=_validate_masks(masks,(h,w))
        except ValueError as e:
            mask_error=str(e)
            if mode=='masques_requis':raise UnsafeCut(mask_error) from e
    if mode=='masques_requis' and ext is None:
        raise UnsafeCut('V18: masques IA requis mais aucun masque valide fourni')
    # Do not claim external AI was used merely because a mask batch was supplied.
    label_tokens=[_safe_id(x) for x in re.split(r'[,;\n]+',labels) if x.strip()]
    result=ET.Element(SVG+'svg',{'width':f'{width_mm:.4f}mm','height':f'{height_mm:.4f}mm',
                                 'viewBox':f'0 0 {w} {h}','version':'1.1'})
    proof=np.full((h,w,3),244,np.uint8)
    proof[alpha]=rgba[:,:,:3][alpha]
    proof_image=Image.fromarray(proof,'RGB');draw=ImageDraw.Draw(proof_image)
    records=[]; real_objects=0; external_stickers=0
    proposal_maps={}
    # The base white margin is from the V17 SVG (not approximated).
    # Existing source group order may not match connected component IDs.
    # Match using the base white path per group against the original V17 sticker mapping.
    from .engine_v13 import _cut_paths, _polygon_mask
    cut=_cut_paths(work,count)
    used_components=set()
    for idx,group in enumerate(source_groups,1):
        key=f'STICKER_{idx:02d}'
        if group.get('id')!=key: raise UnsafeCut('V18: ordre des stickers source incoherent')
        polygon=_polygon_mask(cut[idx],h,w)>0
        hist=np.bincount(components[polygon].reshape(-1),minlength=n)
        hist[0]=0
        comp=int(hist.argmax())
        if comp==0 or comp in used_components:raise UnsafeCut('V18: appariement sticker ambiguous')
        used_components.add(comp)
        sticker=(components==comp)
        sy,sx=np.where(sticker)
        x0,y0,x1,y1=int(sx.min()),int(sy.min()),int(sx.max()+1),int(sy.max()+1)
        cropmask=sticker[y0:y1,x0:x1]
        crop_rgb=rgba[y0:y1,x0:x1,:3]
        sub=ET.SubElement(result,SVG+'g',{'id':key})
        white=copy.deepcopy(group[0])
        white.attrib['id']=f'{key}_BASE_BLANCHE_ORIGINALE'
        # preserve original group transform on only the base, if any
        if group.get('transform'):
            base_group=ET.SubElement(sub,SVG+'g',{'transform':group.get('transform'),'id':f'{key}_BASE_TRANSFORM'})
            base_group.append(white)
        else:sub.append(white)
        # Candidate connected islands, or masks imported from Florence/SAM.
        proposals=[]
        source_objets='aucun'
        if ext is not None:
            for j,seg in enumerate(ext):
                cut_piece=seg[y0:y1,x0:x1] & cropmask
                part_pixels=int(cut_piece.sum())
                if part_pixels>=max(12,int(cropmask.sum()*.004)) and part_pixels < int(cropmask.sum()*.98):
                    proposals.append((j,cut_piece))
            if proposals:source_objets='masques_externes'
            if not proposals and mode=='masques_requis':
                raise UnsafeCut(f'Sticker {idx}: aucun masque IA utile pour ce sujet')
        if not proposals and mode!='masques_requis':
            proposals=[(j,pr) for j,pr in enumerate(_auto_proposals(crop_rgb,cropmask))]
            source_objets='couleurs_heuristiques' if proposals else 'aucune_proposition'
        assigned=np.zeros_like(cropmask,dtype=bool)
        validated=[]
        for j,candidate in proposals:
            part=(candidate & cropmask & ~assigned)
            if part.sum()<max(10,int(cropmask.sum()*.003)):continue
            assigned|=part
            validated.append((j,part))
        if source_objets=='masques_externes' and len(validated)>0:
            external_stickers+=1
        if source_objets=='masques_externes' and not validated and mode!='masques_requis':
            source_objets='aucun_masque_retenu'
        residual=cropmask & ~assigned
        proposal_maps[idx]=(x0,y0,[(j,part.copy()) for j,part in validated])
        palette_idx,palette=_rgb_palette(crop_rgb,cropmask,colors)
        # Draw residual FIRST, then user-editable objects on top.
        ordered=[('FOND_RESIDUEL',residual,None)]
        ordered += [(f'OBJET_{k:02d}_'+(label_tokens[j] if j<len(label_tokens) else 'PROPOSITION'),part,j)
                    for k,(j,part) in enumerate(validated,1)]
        npaths=0
        for name,maskpart,original_index in ordered:
            if not np.any(maskpart):continue
            obj=ET.SubElement(sub,SVG+'g',{'id':f'{key}_{name}'})
            for color_id in np.unique(palette_idx[maskpart]):
                binary=(palette_idx==color_id) & maskpart
                if int(binary.sum())<2:continue
                d=_contour_d(binary,x0,y0)
                if not d:continue
                color=palette[int(color_id)]
                fill='#%02X%02X%02X'%tuple(map(int,color))
                ET.SubElement(obj,SVG+'path',{'fill':fill,'fill-rule':'evenodd','d':d})
                npaths+=1
        for k,(j,part) in enumerate(validated,1):
            yy,xx=np.where(part)
            if xx.size:
                bounds=[int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+x0),int(yy.max()+y0)]
                draw.rectangle(bounds,outline=(226,76,37),width=max(2,w//700))
                draw.text((bounds[0]+2,bounds[1]+2),f'{idx}.{k}',fill=(14,29,58),stroke_width=2,stroke_fill=(255,255,255))
        records.append({'sticker':idx,'source_objets':source_objets,'composante_raster':comp,'objets_proposes':len(validated),
                        'pixels_associés':int(assigned.sum()),'pixels_restant_editables':int(residual.sum()),
                        'chemins_vectoriels':npaths,
                        'calques':['residuel']+[f'objet_{k:02d}' for k in range(1,len(validated)+1)]})
        real_objects+=len(validated)
    if used_components!=set(range(1,n)):
        raise UnsafeCut('V18: tous les stickers ne sont pas apparies')
    _validate_safe_svg(result)
    total_paths=len(list(result.iter(SVG+'path')))
    if total_paths>5000:raise UnsafeCut(f'V18: SVG objets trop complexe ({total_paths} chemins / maximum 5000)')
    outfile=work/OBJECT_SVG
    ET.ElementTree(result).write(outfile,encoding='utf-8',xml_declaration=True)
    proof_image.save(work/OBJECT_PROOF,optimize=True)
    parsed=ET.parse(outfile).getroot()
    if len(list(parsed.iter(SVG+'path')))!=total_paths:
        raise UnsafeCut('V18: verification SVG apres export echouee')
    # Optional visual QA for a small normalized size; not a fidelity guarantee.
    visual={'teste':False,'raison':'CairoSVG non disponible'}
    try:
        import cairosvg
        from io import BytesIO
        rend=np.asarray(Image.open(BytesIO(cairosvg.svg2png(url=str(outfile),output_width=w,output_height=h))).convert('RGBA'))
        a=rend[...,3]>127
        miss=int(np.count_nonzero(alpha & ~a)); extra=int(np.count_nonzero(a & ~alpha))
        visual={'teste':True,'pixels_masquants':miss,'pixels_en_dehors':extra,
                'ecart_brut_pct':round(100*(miss+extra)/max(1,int(alpha.sum())),4)}
        if extra>max(40,int(alpha.sum()*.045)):
            raise UnsafeCut('V18: couches de couleur depassent fortement la silhouette Print Then Cut')
    except ImportError:pass
    faithful=_make_fidelity_groups(work,proposal_maps,w,h,label_tokens)
    return {'version_fidele_groupes':faithful,
            'mode':'masques_externes_retenus' if external_stickers>0 else 'propositions_automatiques_non_semantiques',
            'nombre_stickers_masques_externes_retenus':external_stickers,
            'masques_externes_utilises':external_stickers>0,
            'nombre_masques_externes':0 if ext is None else int(ext.shape[0]),
            'erreur_masques':mask_error,'objets_proposes':real_objects,'nombre_stickers':count,
            'chemins_svg':total_paths,'fichier':OBJECT_SVG,'apercu':OBJECT_PROOF,
            'fidelite_raster':visual,'par_sticker':records,
            'limitations': ['Les noms generiques OBJET ne constituent pas une identification IA.',
                            'Deplacer un objet ne reconstruit pas ses parties cachees.',
                            'Les couleurs sont simplifiees pour edition, elles ne remplacent pas le PNG imprime.',
                            'Le modele IA semantique doit etre execute par un node de segmentation externe lorsque des masques sont fournis.']}


def _input_preflight(rgb,alpha=None,allow_complex=False):
    """Bound known expensive full-bleed images before running legacy vectorizer.

    This is a conservative CPU workload gate, not scene understanding.
    Rejection does NOT imply an image is unsegmentable by AI.
    """
    h,w=rgb.shape[:2]
    if not isinstance(rgb,np.ndarray) or rgb.ndim!=3 or rgb.shape[2]!=3:
        raise UnsafeCut('V18.1: image HxWx3 RGB requise')
    if h*w>14_000_000:
        raise UnsafeCut('Image trop grande pour le profil V18.1 (>14 MP), traiter par regions en V19')
    if alpha is not None and alpha.shape!=(h,w):raise UnsafeCut('Canal alpha de dimensions incorrectes')
    if h*w>=1_200_000 and (alpha is None or np.min(alpha)>248):
        thumbnail=cv2.resize(rgb,(128,128),interpolation=cv2.INTER_AREA)
        margin=np.concatenate([thumbnail[0],thumbnail[-1],thumbnail[:,0],thumbnail[:,-1]])
        bright_ratio=float(np.mean(np.min(margin,axis=1)>235))
        if bright_ratio<.15 and not allow_complex:
            raise UnsafeCut('SCENE_COMPLEXE_NON_PRISE_EN_CHARGE: image grande sans bord clair/alpha. '
                            'Vectorisation integralement automatique non lancee (risque de calcul excessif). '
                            'Attendre voie photo V19, ou fournir sujet transparent/detoure et dimensions reduites.')
    return {'etat':'poursuite','pixels':h*w,'risque_photo_pleine_page':False}

def process_v18(rgb, output_dir, *, layout='auto',intent='auto',ia_mode='auto',ai_masker=None,
                alpha=None,sheet_width_mm=180,margin_mm=1.5,editable_colors=10,
                runtime_rmbg_stats=None,object_masks=None,object_labels='',object_mode='auto',
                mask_space='planche',mask_transform_json='',allow_complex=False):
    base=Path(output_dir).expanduser();base.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix='.SmartSVG_V18_1_TEMP_',dir=base))
    try:
        _input_preflight(rgb,alpha=alpha,allow_complex=allow_complex)
        report,preview=process_v17(rgb,str(stage),layout=layout,intent=intent,
            ia_mode=ia_mode,ai_masker=ai_masker,alpha=alpha,sheet_width_mm=sheet_width_mm,
            margin_mm=margin_mm,editable_colors=editable_colors,runtime_rmbg_stats=runtime_rmbg_stats)
        work=Path(report['output'])
        if not work.is_dir() or work.parent!=stage:raise UnsafeCut('V18: dossier V17 temporaire inattendu')
        from .coordinate_mapper import resolve_masks
        from PIL import Image as PILImage
        with PILImage.open(work/NAME) as im:
            target_shape=(im.height,im.width)
        try:
            registered,mask_alignment=resolve_masks(object_masks,tuple(rgb.shape[:2]),target_shape,
                                        space=mask_space,transform_json=mask_transform_json)
        except ValueError as e:
            raise UnsafeCut('REPERE_MASQUES_INVALIDE: '+str(e)) from e
        protected=(NAME,CRICUT_SVG,'CRICUT_EDITION_REGIONS_INDEPENDANTES.svg')
        old_hashes={n:hashlib.sha256((work/n).read_bytes()).hexdigest() for n in protected}
        objects=_process_sheet_objects(work,masks=registered,labels=object_labels,
                                        colors=editable_colors,mode=object_mode)
        objects['alignement_masques']=mask_alignment
        new_hashes={n:hashlib.sha256((work/n).read_bytes()).hexdigest() for n in protected}
        if new_hashes!=old_hashes:
            raise UnsafeCut('ALERTE_CRICUT: PNG ou SVG production modifie par l analyse des objets')
        objects['fichiers_production_immuables_sha256']=old_hashes
        # Do not alter the PNG or existing V17 Cricut SVGs.
        quick=work/KIT
        shutil.copy2(work/OBJECT_SVG, quick/'05_MODIFIER_OBJETS_RASTERISES_EXPERIMENTAL.svg')
        fidelity=objects['version_fidele_groupes']
        if fidelity.get('cree') and fidelity.get('equivalence_source',{}).get('rendu_equivalent_a_la_source',False):
            shutil.copy2(work/OBJECT_FIDELITY,quick/'04_MODIFIER_OBJETS_COURBES.svg')
        else:
            # Always provide a faithful editable fallback if masks/shape grouping fail.
            from .engine_v15 import REGION_SVG
            shutil.copy2(work/REGION_SVG,quick/'04_MODIFIER_OBJETS_COURBES.svg')
            fidelity['repli_original_regions']=True
        for old in ('PRET_V17.json','rapport_V17.json'):
            src=work/old
            if src.exists():
                dest=work/'DETAILS_ELEMENTS'/'RAPPORTS_PRECEDENTS'
                dest.mkdir(parents=True,exist_ok=True)
                os.replace(src,dest/old)
        record={'version':VERSION,'objets':objects,'impression_decoupe_base':'moteur V17 INCHANGE',
                'validation_ia_locale_gpu_reelle':False,'validation_cricut_physique':False}
        (work/OBJECT_REPORT).write_text(json.dumps(record,ensure_ascii=False,indent=2,default=_json_default),encoding='utf8')
        (work/'00_LIRE_EN_PREMIER_CRICUT.txt').write_text(
            'SMARTSVG V18 — POUR CRICUT\n\n'
            '01_IMPRIMER_PUIS_DECOUPER.png : seul fichier recommande pour imprimer directement.\n'
            '02_MODIFIER_COULEURS.svg : recolorer les principaux aplats.\n'
            '03_MODIFIER_REGIONS.svg : recolorer regions vectorielles individuellement.\n'
            '04_MODIFIER_OBJETS_PROPOSES.svg : objets candidats editables (experimental).\n\n'
            'IMPORTANT : dans Design Space, utiliser APLATIR apres modification du SVG.\n'
            'Verifier ensuite les silhouettes. Ne pas superposer SVG de contours et PNG.\n'
            'Un objet propose n est PAS necessairement un objet semantique reconnu.\n'
            'Masques IA en repere source : matrice explicite requise si recomposition.\n'
            'Le fichier PNG Print Then Cut n est jamais produit depuis le SVG experimental.\n',encoding='utf8')
        published=base/('SmartSVG_V18_1_'+datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8])
        files=_fingerprint_folder(work)
        (work/STATUS).write_text(json.dumps({'version':VERSION,
            'statut':'PRECONTROLE_REUSSI_EXPORT_OBJETS_EXPERIMENTAL',
            'objets_proposes':objects['objets_proposes'],
            'masques_externes_utilises':objects['masques_externes_utilises'],
            'fichiers':files,'validation_cricut_physique':False},ensure_ascii=False,indent=2),encoding='utf8')
        report.update({'version':VERSION,'output':str(published),'audit_v18':record})
        os.replace(work,published)
        return report, preview
    except Exception as exc:
        (base/('SmartSVG_ECHEC_V18_1_'+uuid.uuid4().hex[:8]+'.json')).write_text(
            json.dumps({'statut':'ECHEC_NON_PUBLIE','erreur':str(exc)},ensure_ascii=False,indent=2),encoding='utf8')
        raise UnsafeCut('SmartSVG V18.1: aucun fichier publie : '+str(exc)) from exc
    finally:
        shutil.rmtree(stage,ignore_errors=True)
