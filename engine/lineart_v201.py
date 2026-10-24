"""SmartSVG V20.1.1: audited CPU-only line-art photo / scan processing.

This module NEVER asserts that geometric silhouette proposals are semantic masks.
Separate, transparent and original image exports are retained for human QA.
"""
from __future__ import annotations

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

MAX_PIXELS = 12_000_000
MAX_DIMENSION = 7000


class LineArtError(ValueError):
    pass


def _validate_image(rgb):
    a=np.asarray(rgb)
    if a.ndim!=3 or a.shape[-1] not in (3,4) or min(a.shape[:2])<48:
        raise LineArtError('Image RGB/RGBA [H,W,3/4], minimum 48 pixels par cote requise')
    if max(a.shape[:2])>MAX_DIMENSION or a.shape[0]*a.shape[1]>MAX_PIXELS:
        raise LineArtError('Image trop grande pour le traitement line-art sur CPU')
    if a.dtype!=np.uint8:
        raise LineArtError('Pixels uint8 RGB/RGBA requis')
    if not np.isfinite(a).all():raise LineArtError('Pixels invalides')
    if a.shape[-1] == 4:
        # Flatten transparency over paper white for analysis; never interpret
        # fully transparent RGB garbage as black ink. Source itself is exported unchanged.
        alpha = a[:,:,3:4].astype(np.uint16)
        return np.ascontiguousarray(((a[:,:,:3].astype(np.uint16)*alpha + 255*(255-alpha)+127)//255).astype(np.uint8))
    return np.ascontiguousarray(a[:,:,:3])


def _order_corners(points):
    p=np.asarray(points,dtype=np.float32).reshape(4,2)
    # Use y-first grouping to avoid ambiguous sum/diff for tilted rectangles.
    yorder=p[np.argsort(p[:,1])]
    top=yorder[:2][np.argsort(yorder[:2,0])]
    bottom=yorder[2:][np.argsort(yorder[2:,0])]
    return np.asarray([top[0],top[1],bottom[1],bottom[0]],np.float32)


def detect_card(rgb):
    """Conservative geometric candidate, with a pass/fail rather than fake confidence."""
    img=_validate_image(rgb)
    h,w=img.shape[:2]
    scale=min(1.,1250./max(h,w))
    if scale<1: tmp=cv2.resize(img,(round(w*scale),round(h*scale)),interpolation=cv2.INTER_AREA)
    else:tmp=img
    g=cv2.cvtColor(tmp,cv2.COLOR_RGB2GRAY)
    g=cv2.GaussianBlur(g,(5,5),0.9)
    t=cv2.adaptiveThreshold(g,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                            cv2.THRESH_BINARY_INV,35,8)
    contours,_=cv2.findContours(t,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
    hh,ww=g.shape
    candidates=[]
    for c in contours:
        x,y,cw,ch=cv2.boundingRect(c)
        frac=cw*ch/(ww*hh)
        if not (.07<=frac<=.83 and cw>=ww*.25 and ch>=hh*.25):continue
        if min(cw,ch)<110:continue
        poly=cv2.approxPolyDP(cv2.convexHull(c),.023*cv2.arcLength(cv2.convexHull(c),True),True)
        if len(poly)!=4:continue
        area=cv2.contourArea(poly)
        rectangularity=area/(cw*ch)
        if rectangularity<.77:continue
        pts=_order_corners(poly)
        edge_lengths=[np.linalg.norm(pts[(i+1)%4]-pts[i]) for i in range(4)]
        if min(edge_lengths)<min(ww,hh)*.18:continue
        distance=math.hypot((x+cw/2)/ww-.5,(y+ch/2)/hh-.5)
        center_score=max(0,1.-distance)
        score=frac*2.4+rectangularity*.3+center_score*.15
        candidates.append((score,pts,rectangularity,frac))
    if not candidates:return {'detected':False,'points':None,'score':None,'note':'Aucun cadre fiable; image entiere conservee'}
    candidates.sort(key=lambda p:p[0],reverse=True)
    best=candidates[0]
    points=(best[1]/scale).round(2)
    return {'detected':True,'points':points.tolist(),
            'score':round(float(best[0]),3),
            'note':'Cadre geometrique propose; verifier le recadrage'}


def crop_card(rgb,card,rectify=True):
    a=_validate_image(rgb)
    if not card['detected']:
        return a.copy(),{'redressement':'aucun','dimensions':[a.shape[1],a.shape[0]]}
    pts=_order_corners(card['points'])
    tw=int(round(max(np.linalg.norm(pts[1]-pts[0]),np.linalg.norm(pts[2]-pts[3]))))
    th=int(round(max(np.linalg.norm(pts[3]-pts[0]),np.linalg.norm(pts[2]-pts[1]))))
    if tw<48 or th<48 or tw*th>MAX_PIXELS or tw>MAX_DIMENSION or th>MAX_DIMENSION:
        raise LineArtError('Perspective du cadre invalide ou trop grande')
    if rectify:
        dst=np.asarray([[0,0],[tw-1,0],[tw-1,th-1],[0,th-1]],np.float32)
        matrix=cv2.getPerspectiveTransform(pts,dst)
        out=cv2.warpPerspective(a,matrix,(tw,th),flags=cv2.INTER_LINEAR,
                                borderMode=cv2.BORDER_REPLICATE)
        return out,{'redressement':'homographie','dimensions':[tw,th]}
    x1=max(0,int(math.floor(pts[:,0].min())));x2=min(a.shape[1],int(math.ceil(pts[:,0].max()))+1)
    y1=max(0,int(math.floor(pts[:,1].min())));y2=min(a.shape[0],int(math.ceil(pts[:,1].max()))+1)
    return a[y1:y2,x1:x2].copy(),{'redressement':'cadre_rectangle_englobant','dimensions':[x2-x1,y2-y1]}


def extract_ink(rgb,source='auto',mode='doux',inset=0):
    """Illumination compensation, suppresses low-amplitude screen raster.

    Keeps grayscale and two ink variants. No inpainting or hallucinated lines.
    """
    a=_validate_image(rgb)
    h,w=a.shape[:2]
    if mode not in ('doux','fort'):raise LineArtError('Nettoyage inconnu')
    gray=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)
    smooth=cv2.GaussianBlur(gray,(5,5),1.2 if mode=='doux' else 1.5)
    sigma=max(8.,min(40.,min(w,h)*.035))
    bg=cv2.GaussianBlur(smooth,(0,0),sigmaX=sigma)
    darkness=np.maximum(bg.astype(np.float32)-smooth.astype(np.float32),0)
    cleaned=np.uint8(255.-np.clip(darkness*(2.7 if mode=='doux' else 3.15),0,255))
    threshold=14. if mode=='doux' else 22.
    ink=(darkness>threshold).astype(np.uint8)*255
    # Do not remove eyes, hair decorations or other small legit details by default.
    if inset:
        inset=max(1,min(int(inset),min(h,w)//8))
        ink[:inset]=0;ink[-inset:]=0;ink[:,:inset]=0;ink[:,-inset:]=0
    # Only isolated single-pixel camera noise is removed.
    n,labels,stats,_=cv2.connectedComponentsWithStats(ink,8)
    for i in range(1,n):
        if stats[i,cv2.CC_STAT_AREA]==1:ink[labels==i]=0
    return cleaned,ink


def silhouette_candidate(ink):
    """Conservative geometric envelope, never a claimed AI portrait mask."""
    src=np.asarray(ink)
    if src.ndim!=2 or src.dtype!=np.uint8:raise LineArtError('Masque noir/blanc uint8 requis')
    h,w=src.shape
    # Connect broken line art with an explicitly approximate morphological envelope.
    k=max(5,int(round(min(h,w)*.018))|1)
    dilated=cv2.dilate(src,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
    n,lab,stats,_=cv2.connectedComponentsWithStats(dilated,8)
    if n<2:return None,'Pas assez de traits pour une silhouette'
    candidates=[i for i in range(1,n) if stats[i,cv2.CC_STAT_AREA]>=.02*h*w]
    if not candidates:return None,'Aucune silhouette continue suffisamment grande'
    # Favor region nearest image centre while rejecting near full-canvas mask.
    scored=[]
    for i in candidates:
        x,y,cw,ch,area=stats[i]
        if cw*ch>=.98*w*h:continue
        center=abs((x+cw/2)-w/2)/w+abs((y+ch/2)-h/2)/h
        scored.append((area/(h*w)-center*.12,i))
    if not scored:return None,'Silhouette indeterminee (masque recouvrant toute la carte)'
    _,idx=max(scored)
    candidate=np.uint8(lab==idx)*255
    cnts,_=cv2.findContours(candidate,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:return None,'Contour externe introuvable'
    largest=max(cnts,key=cv2.contourArea)
    mask=np.zeros_like(src)
    cv2.drawContours(mask,[largest],-1,255,-1)
    # Many drawings end at the bottom of a page: the torso is not a closed region.
    # Fill left-to-right scanline spans of the dominant connected envelope to
    # prevent transparent holes cutting through the neck, shoulders or torso.
    # This is still a DRAFT; no semantic recovery is claimed.
    yy=np.where(np.any(mask!=0,axis=1))[0]
    if yy.size:
        for row in yy:
            xx=np.where(mask[row]!=0)[0]
            if len(xx)>1:mask[row,int(xx[0]):int(xx[-1])+1]=255
    r=max(1,round(min(h,w)*.005))
    if r>1:
        k2=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*r+1,2*r+1))
        mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,k2)
    touches=(np.any(mask[0]) or np.any(mask[-1]) or np.any(mask[:,0]) or np.any(mask[:,-1]))
    return mask, ('Candidat geometrique: sujet au bord, silhouette probablement ouverte' if touches
                   else 'Candidat geometrique uniquement; validation visuelle obligatoire')


def _svg_path_from_contour(c,epsilon=.55):
    poly=cv2.approxPolyDP(c,epsilon,True)[:,0]
    if len(poly)<3:return ''
    return 'M '+' L '.join(f'{int(x)} {int(y)}' for x,y in poly)+' Z'


def svg_ink(ink):
    h,w=ink.shape
    contours,_=cv2.findContours(ink,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    paths=[_svg_path_from_contour(c) for c in contours if cv2.contourArea(c)>=2.0]
    paths=[p for p in paths if p]
    # One compound evenodd path preserves outline holes and face/eye details.
    data=' '.join(paths)
    xml=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
         f'width="{w}" height="{h}"><path fill="#111111" stroke="#111111" stroke-width="1" fill-rule="evenodd" d="{data}"/></svg>')
    return xml,len(paths)


def svg_cut(mask):
    h,w=mask.shape
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    paths=[_svg_path_from_contour(c,1.25) for c in contours if cv2.contourArea(c)>16]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}"><path fill="none" stroke="#000000" '
            f'stroke-width="1" d="{" ".join(paths)}"/></svg>')


def _save_png(array,path):
    Image.fromarray(array).save(path,format='PNG')


def process_lineart(rgb,output_dir,*,source='auto',mode='doux',target='carte',
                    rectify=True,white_margin_px=10):
    """Extract, clean and trace. New outputs only; no legacy Cricut writes.

    'personnage' cut is a geometric DRAFT. The reliable output is card cropping.
    """
    a=_validate_image(rgb)
    if source not in ('auto','scan','photo','capture_ecran','photo_ecran'):raise LineArtError('Type de source invalide')
    if target not in ('carte','personnage','sticker'):raise LineArtError('Type de decoupe invalide')
    if mode not in ('doux','fort'):raise LineArtError('Mode de nettoyage invalide')
    if not isinstance(white_margin_px,(int,np.integer)) or not (0<=white_margin_px<=60):
        raise LineArtError('Marge hors limites')
    if not isinstance(output_dir,(str,os.PathLike)) or not str(output_dir).strip():
        raise LineArtError('Dossier de sortie vide')
    output=Path(output_dir).expanduser()
    # Prevent surprise writes through existing symlink ancestors. A standard
    # ComfyUI path with no symlinks continues to be accepted.
    for part in (output,*output.parents):
        if part.is_symlink():raise LineArtError('Lien symbolique dans le chemin de sortie interdit')
    output.mkdir(parents=True,exist_ok=True)
    card=detect_card(a)
    cropped,geometry=crop_card(a,card,rectify=rectify)
    h,w=cropped.shape[:2]
    inset=max(6,round(min(h,w)*.016)) if card['detected'] else 0
    cleaned,ink=extract_ink(cropped,source,mode,inset=inset)
    # Also export a strong variant without overwriting the detailed one.
    cleaned_strong,ink_strong=extract_ink(cropped,source,'fort',inset=inset)
    # The synthetic card contour is a rectangle in the perspective-corrected local view.
    card_mask=np.full((h,w),255,np.uint8)
    subject_mask,subject_note=silhouette_candidate(ink_strong)
    if target=='carte': selected=card_mask; export_status='CARTE_GEOMETRIQUE'
    elif subject_mask is None:
        selected=card_mask;export_status='REPLI_CARTE_SUJET_INDETERMINE'
    else:
        selected=subject_mask;export_status='PROPOSITION_SUJET_NON_VALIDEE'
    # A Cricut offset must grow OUTSIDE the original bitmap. V20.1 dilated a
    # mask inside its old canvas, silently clipping the sticker border at edges.
    # Pad FIRST; add ink aligned at the new origin; grow mask after padding.
    padding=0
    aligned_ink=ink
    if target=='sticker' and white_margin_px:
        padding=int(white_margin_px)+2
        selected=cv2.copyMakeBorder(selected,padding,padding,padding,padding,cv2.BORDER_CONSTANT,value=0)
        aligned_ink=cv2.copyMakeBorder(ink,padding,padding,padding,padding,cv2.BORDER_CONSTANT,value=0)
        k=2*int(white_margin_px)+1
        selected=cv2.dilate(selected,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(k,k)))
    # Transparent outer margin, opaque white interior, black lineart ink.
    printable=np.stack([255-aligned_ink]*3,axis=-1)
    print_rgba=np.dstack([printable,selected])
    # Explicit alpha cut silhouette; geometry not passed off as semantic foreground.
    line_svg,n_paths=svg_ink(ink)
    cut_svg=svg_cut(selected)
    from hashlib import sha256
    key=uuid4().hex[:12]
    name='LineArt_V20_1_'+key
    final=output/name
    tmp=Path(tempfile.mkdtemp(prefix='.pending_lineart_',dir=str(output)))
    try:
        dirs=['01_SOURCE','02_ZONE_UTILE','03_NETTOYAGE','04_LINEART','05_CONTOURS','06_SVG','07_QA']
        for d in dirs:(tmp/d).mkdir()
        _save_png(np.asarray(rgb),tmp/'01_SOURCE'/('original_RGBA.png' if np.asarray(rgb).shape[-1]==4 else 'original_RGB.png'))
        _save_png(cropped,tmp/'02_ZONE_UTILE'/'carte_redressee.png')
        _save_png(cleaned,tmp/'03_NETTOYAGE'/'gris_corrige_doux.png')
        _save_png(cleaned_strong,tmp/'03_NETTOYAGE'/'gris_corrige_fort.png')
        _save_png(ink,tmp/'04_LINEART'/'traits_fins.png')
        _save_png(ink_strong,tmp/'04_LINEART'/'traits_cricut.png')
        _save_png(card_mask,tmp/'05_CONTOURS'/'cadre.png')
        if subject_mask is not None:
            _save_png(subject_mask,tmp/'05_CONTOURS'/'personnage_CANDIDAT_A_VERIFIER.png')
        _save_png(selected,tmp/'05_CONTOURS'/'masque_selectionne.png')
        _save_png(print_rgba,tmp/'05_CONTOURS'/'IMPRIMER_PUIS_DECOUPER_BROUILLON.png')
        (tmp/'06_SVG'/'traits_vectoriels.svg').write_text(line_svg,encoding='utf8')
        (tmp/'06_SVG'/'contour_selectionne.svg').write_text(cut_svg,encoding='utf8')
        # Inspection thumbnail 3 columns with original card, clean grayscale, strokes.
        target_h=min(850,h)
        target_w=max(1,round(w*target_h/h))
        panes=[]
        for pane in [cropped,np.repeat(cleaned[:,:,None],3,axis=2),np.repeat((255-ink)[:,:,None],3,axis=2)]:
            panes.append(cv2.resize(pane,(target_w,target_h),interpolation=cv2.INTER_AREA))
        preview=np.concatenate(panes,axis=1)
        _save_png(preview,tmp/'07_QA'/'avant_apres.png')
        warning_codes=[]
        if not card['detected']:
            warning_codes.append('CADRE_NON_DETECTE_IMAGE_ENTIERE')
        else:
            warning_codes.append('CADRE_DETECTE_VALIDATION_VISUELLE')
        if source in ('photo_ecran','photo'):
            warning_codes.append('PHOTO_OPTIMALE_NON_GARANTIE')
        if target in ('personnage','sticker'):
            warning_codes.append('SILHOUETTE_GEOMETRIQUE_NON_VALIDEE')
        if export_status=='REPLI_CARTE_SUJET_INDETERMINE':
            warning_codes.append('REPLI_CARTE_SANS_SILHOUETTE')
        if subject_mask is not None and ('au bord' in subject_note):
            warning_codes.append('SILHOUETTE_OUVERTE_AU_BORD')
        if np.count_nonzero(ink)<max(5,h*w*.0005):
            warning_codes.append('TRAITS_PEU_DETECTES')
        # Raster ink and cut paths remain two distinct objects: the printed area
        # must never be advertised as a validated person silhouette.
        report={
            'version':'20.1.1-alpha','source_type':source,'source_dimensions':[a.shape[1],a.shape[0]],
            'card':card,'perspective':geometry,'mode_nettoyage':mode,
            'decoupe_demandee':target,'decoupe_generee':export_status,
            'contour_personnage_note':subject_note,'trait_paths_svg':n_paths,
            'pixels_traits':int(np.count_nonzero(ink)),
            'pixels_decoupe':int(np.count_nonzero(selected)),
            'dimensions_png_impression':[int(print_rgba.shape[1]),int(print_rgba.shape[0])],
            'decalage_traits_impression_px':[padding,padding],
            'marge_exterieure_px':int(white_margin_px) if target=='sticker' else 0,
            'unite_dimensions_physiques':'pixels_seulement_pas_de_DPI_ni_de_mm_calibres',
            'pret_decoupe_personnage':False,
            'validation_manuelle_obligatoire':True,
            'avertissements':warning_codes,
            'segmentation_ia_executee':False,
            'limites':['Line-art trace from photograph; no recovery of missing original pixels',
                       'Personnage is a geometric DRAFT, not a segmentation proof',
                       'SVG represents ink outline regions, not editable semantic hair/face layers',
                       'No real Cricut print-and-cut hardware validation'],
        }
        (tmp/'rapport_v20_1.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf8')
        final=output/name
        os.replace(tmp,final)
    except BaseException:
        shutil.rmtree(tmp,ignore_errors=True)
        raise
    return {'root':str(final),'preview':preview,'report':report,
            'image':str(final/'05_CONTOURS'/'IMPRIMER_PUIS_DECOUPER_BROUILLON.png')}
