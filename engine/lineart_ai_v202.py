"""SmartSVG V20.2: align a REAL supplied/AI mask with a photographed line-art card.

This additive pipeline keeps V20.1.1 exports unchanged. AI outputs remain
unverified cut CANDIDATES. No rectangles or ink envelopes masquerade as AI masks.
"""
from __future__ import annotations
import json
import os
import shutil
import tempfile
from pathlib import Path
from uuid import uuid4
import cv2
import numpy as np
from PIL import Image
from . import lineart_v201 as line
from .cricut_choice_v2012 import process_choice, OPTIONS as CRICUT_OPERATIONS, _rescale_svg

MAX_MASK_PIXELS_TOTAL = 32_000_000
MAX_MASKS = 16

class LineArtSegmentationError(line.LineArtError):
    pass


def validate_masks(masks, shape, *, max_masks=MAX_MASKS):
    """Accept MASK [N,H,W] / [H,W]; allow uint8 0..255 or float [0,1]."""
    if masks is None:
        return None
    # Check tensor shape and budget BEFORE copying any GPU data into RAM.
    # A 16 x 6000 x 6000 GPU tensor should be rejected without CPU transfer.
    if hasattr(masks,'detach'):
        raw_shape=tuple(int(v) for v in masks.shape)
        if len(raw_shape) not in (2,3):
            raise LineArtSegmentationError('MASK tenseur : H,W ou N,H,W requis')
        nh=1 if len(raw_shape)==2 else raw_shape[0]
        hw=raw_shape[-2:]
        if (nh<1 or nh>max_masks or hw!=tuple(shape)
                or nh*hw[0]*hw[1]>MAX_MASK_PIXELS_TOTAL):
            raise LineArtSegmentationError('MASK tenseur: forme/dimensions/budget hors limites')
        masks=masks.detach().cpu().numpy()
    arr=np.asarray(masks)
    if arr.ndim==2:
        arr=arr[None]
    if (arr.ndim!=3 or arr.shape[0]<1 or arr.shape[0]>max_masks or
            arr.shape[1:] != tuple(shape) or arr.size>MAX_MASK_PIXELS_TOTAL):
        raise LineArtSegmentationError('MASK: forme [N,H,W], dimensions source et budget memoire requis')
    if arr.dtype.kind not in 'fiu' or not np.isfinite(arr).all():
        raise LineArtSegmentationError('MASK: nombres reels finis requis')
    lo=float(arr.min());hi=float(arr.max())
    if lo<0 or hi>255:
        raise LineArtSegmentationError('MASK: valeurs hors bornes')
    if arr.dtype.kind == 'f':
        if hi>1.001:raise LineArtSegmentationError('MASK flottant: plage [0,1] obligatoire')
        output=arr.astype(np.float32,copy=True)
    else:
        # uint8 binary 0/1 is already normalized; uint8 gray 0..255 is divided.
        output=arr.astype(np.float32,copy=True)/(255. if hi>1 else 1.)
    return np.ascontiguousarray(np.clip(output,0,1))


def align_masks(masks, rgb, card, geometry, *, space='source', rectify=True):
    """Map source-space MASKs through EXACT same homography as crop_card.

    Returns float32 masks in coordinate system of clean LineArt card.
    """
    rgb=line._validate_image(rgb)
    h,w=rgb.shape[:2]
    tw,th=geometry['dimensions']
    if space not in ('source','carte_redressee'):
        raise LineArtSegmentationError('Espace masque inconnu')
    expected=(h,w) if space=='source' else (th,tw)
    arr=validate_masks(masks,expected)
    if arr is None:return None
    if space=='carte_redressee':
        return arr
    if not card['detected']:
        if (h,w)!=(th,tw):raise LineArtSegmentationError('Geometrie sans cadre incoherente')
        return arr
    pts=line._order_corners(card['points'])
    if rectify:
        dst=np.asarray([[0,0],[tw-1,0],[tw-1,th-1],[0,th-1]],np.float32)
        matrix=cv2.getPerspectiveTransform(pts,dst)
        aligned=np.stack([cv2.warpPerspective(mask,matrix,(tw,th),
                            flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
                          for mask in arr])
    else:
        x1=max(0,int(np.floor(pts[:,0].min())))
        y1=max(0,int(np.floor(pts[:,1].min())))
        aligned=arr[:,y1:y1+th,x1:x1+tw]
    if aligned.shape[1:] != (th,tw):
        raise LineArtSegmentationError('Transformation des masques incoherente')
    return np.ascontiguousarray(np.clip(aligned,0,1),dtype=np.float32)


def choose_subject(masks):
    """Conservative candidate ranking. NEVER implies semantic correctness.

    Ambiguous near-equal candidates are recorded, not silently merged.
    """
    if masks is None:return None,{'statut':'AUCUN_MASQUE','candidats':[]}
    n,h,w=masks.shape
    candidates=[]
    yy,xx=np.ogrid[:h,:w]
    for i in range(n):
        binary=masks[i]>=.5
        area=int(binary.sum());frac=area/(h*w)
        if frac<.002 or frac>.92:
            candidates.append({'index':i,'fraction_surface':round(frac,5),'accepte':False,
                               'raison':'MASQUE_TROP_PETIT_OU_TROP_GRAND'})
            continue
        # object may touch bottom of image but cannot be nearly full-canvas.
        ys,xs=np.nonzero(binary)
        xcenter=float(xs.mean()/w);ycenter=float(ys.mean()/h)
        distance=float(np.hypot(xcenter-.5,ycenter-.48))
        # large meaningful silhouette, less preference for edge spurious art
        score=float(np.sqrt(frac)-.24*distance)
        candidates.append({'index':i,'fraction_surface':round(frac,5),'accepte':True,
                           'score_heuristique':round(score,5),'contact_bord':bool(
                           binary[0].any() or binary[-1].any() or binary[:,0].any() or binary[:,-1].any())})
    eligible=sorted((x for x in candidates if x['accepte']), key=lambda x:x['score_heuristique'],reverse=True)
    if not eligible:return None,{'statut':'AUCUN_SUJET_ADMISSIBLE','candidats':candidates}
    top=eligible[0]
    ambiguous=len(eligible)>1 and (top['score_heuristique']-eligible[1]['score_heuristique']<.025)
    return masks[top['index']].copy(), {'statut':'CANDIDAT_AMBIGU' if ambiguous else 'CANDIDAT_NON_VALIDE',
                                       'candidats':candidates,'index_retenu':top['index'],
                                       'ambiguite':bool(ambiguous)}


def make_print_candidate(ink, mask, offset=10):
    """Opaque white inside a closed silhouette; transparent outside; black ink.

    Does not alter mask source. Dark line art outside mask is intentionally cut;
    warnings in QA tell users to inspect areas lost at the boundary.
    """
    h,w=ink.shape
    if mask.shape != (h,w):raise LineArtSegmentationError('Masque et lineart non alignes')
    if not isinstance(offset,(int,np.integer)) or offset<0 or offset>60:
        raise LineArtSegmentationError('Marge blanche hors limites')
    solid=np.uint8(mask>=.5)*255
    # Exterior contour only, fill internal holes so no unexpected cut-out holes.
    contours,_=cv2.findContours(solid,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    solid=np.zeros_like(solid)
    cv2.drawContours(solid,contours,-1,255,-1)
    padding=offset+2 if offset else 0
    if padding:
        solid=cv2.copyMakeBorder(solid,padding,padding,padding,padding,cv2.BORDER_CONSTANT,value=0)
        ink=cv2.copyMakeBorder(ink,padding,padding,padding,padding,cv2.BORDER_CONSTANT,value=0)
        if offset:
            solid=cv2.dilate(solid,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(offset*2+1,offset*2+1)))
    alpha=solid
    print_rgb=np.repeat((255-ink)[:,:,None],3,axis=2)
    print_rgba=np.dstack([print_rgb,alpha])
    return print_rgba,solid,padding


def _infer_on_card(card_rgb,*,mode,profile,analyse_florence,prompt='',segmenter=None,florence=None):
    """RMBG bridges in sequence. Uses only documented upstream hooks."""
    if mode=='desactiver':return None,{'statut':'NON_LANCE'}
    if segmenter is None:
        from .auto_segment_v192 import segment_scene as segmenter
    audit={'statut':'TENTATIVE','prompts':[], 'florence':{'statut':'DESACTIVE'}}
    custom=prompt.strip()
    if not custom and analyse_florence!='desactiver':
        try:
            if florence is None:
                from .scene_florence_v193 import inspect_scene as florence
            res=florence(card_rgb,profile=profile)
            audit['florence']=res['audit']
            if res['prompts']:custom=';'.join(res['prompts'])
            elif analyse_florence=='forcer':raise LineArtSegmentationError('Florence-2 : aucune categorie')
        except Exception as exc:
            audit['florence']={'statut':'ECHEC','erreur':f'{type(exc).__name__}: {str(exc)[:150]}'}
            if analyse_florence=='forcer':raise
    # For cartoons Florence can miss, so prompt person is the conservative fallback.
    res=segmenter(card_rgb,profile=profile,custom_prompts=custom)
    audit['sam2']=res['audit']
    audit['prompts']=res['audit'].get('prompts',[])
    audit['statut']='MASQUES_PRODUITS' if res['masks'] is not None else 'AUCUN_MASQUE'
    return res['masks'],audit


def process_lineart_ai(rgb, output_dir, *,source='auto',target='sticker',mode='doux',
                       rectify=True,white_margin_px=10,ia='auto',profile='personne',
                       analyse_florence='auto',prompt='',masks=None,mask_space='source',
                       operation='imprimer_decouper_contour',width_mm=90,
                       segmenter=None,florence=None):
    """V20.2 end-to-end: alignment -> inference/external mask -> safe QA export.

    The historical PNG/V20.1.1 report is NEVER overwritten. When no model or
    input mask is available, QA clearly states that no IA cut candidate exists.
    """
    if operation not in CRICUT_OPERATIONS:
        raise LineArtSegmentationError('Operation Cricut non reconnue')
    if not isinstance(width_mm,(int,float)) or not np.isfinite(width_mm) or not (20<=width_mm<=280):
        raise LineArtSegmentationError('Largeur finale Cricut hors limites')
    raw=np.asarray(rgb)
    clean=line._validate_image(raw)
    if ia not in ('auto','forcer','desactiver'):raise LineArtSegmentationError('Mode IA inconnu')
    if profile not in ('auto','personne','cadeaux','chopes','personne_cadeaux','animaux'):
        raise LineArtSegmentationError('Profil segmentation inconnu')
    if analyse_florence not in ('auto','forcer','desactiver'):
        raise LineArtSegmentationError('Mode Florence inconnu')
    if not isinstance(prompt,str) or len(prompt)>360:
        raise LineArtSegmentationError('Prompt trop long ou invalide')
    # Geometry is recomputed by the immutable V20.1.1 processor with same input,
    # thresholds and transform. We validate the dimensions after base generation.
    card=line.detect_card(raw)
    cropped,geometry=line.crop_card(raw,card,rectify=rectify)
    provenance='AUCUNE';inference={'statut':'NON_LANCE'};ai_executed=False
    if masks is not None:
        aligned=align_masks(masks,raw,card,geometry,space=mask_space,rectify=rectify)
        provenance='MASK_EXTERNE_COMFYUI'
        inference={'statut':'MASK_EXTERNE','nombre':int(aligned.shape[0])}
    else:
        aligned=None
        if ia!='desactiver':
            try:
                inferred,inference=_infer_on_card(cropped,mode=ia,profile=profile,
                        analyse_florence=analyse_florence,prompt=prompt,
                        segmenter=segmenter,florence=florence)
                ai_executed=True
                aligned=validate_masks(inferred,cropped.shape[:2])
                provenance='RMBG_SAM2_FLORENCE_OPTIONNEL' if aligned is not None else 'AUCUNE'
            except Exception as exc:
                inference={'statut':'ECHEC','erreur':f'{type(exc).__name__}: {str(exc)[:200]}'}
                if ia=='forcer':raise
    subject,selection=choose_subject(aligned)
    # Force without a usable mask must abort before creating any export.
    if ia=='forcer' and subject is None:
        raise LineArtSegmentationError('IA forcee: aucun masque sujet utilisable')
    base=process_choice(raw,output_dir,source=source,mode=mode,target=target,
                        rectify=rectify,white_margin_px=white_margin_px,
                        operation=operation,width_mm=width_mm)
    root=Path(base['root']);qa=root/'08_SEGMENTATION_IA_V20_2'
    stage=None
    try:
        # Independent geometry check catches accidental crop divergence.
        actual=np.asarray(Image.open(root/'02_ZONE_UTILE'/'carte_redressee.png'))
        if actual.shape != cropped.shape or not np.array_equal(actual,cropped):
            raise LineArtSegmentationError('Echec controle homographie: image et masques incoherents')
        stage=Path(tempfile.mkdtemp(prefix='.pending_ia_',dir=root))
        report={'version':'20.2-beta','origine_masque':provenance,
                'inference':inference,'segmentation_ia_appelee':ai_executed,
                'masque_ia_produit':bool(subject is not None),'selection':selection,
                'masque_entree_repere':mask_space if masks is not None else 'carte_redressee',
                'dimensions_carte':[int(cropped.shape[1]),int(cropped.shape[0])],
                'validation_manuelle_obligatoire':True,
                'pret_cricut_sans_verification':False,
                'operation_cricut':operation,
                'operation_geometrique_fichier':base['recommended_file'],
                'dossier_operations_historiques':base['cricut_root'],
                'masque_ia_utilise_uniquement_pour_contour_exterieur':True,
                'avertissements':['SEGMENTATION_NE_GARANTIT_PAS_SILHOUETTE_EXACTE'],
                'fichiers':{}}
        if subject is not None:
            ink=np.asarray(Image.open(root/'04_LINEART'/'traits_fins.png'))
            result,solid,padding=make_print_candidate(ink,subject,white_margin_px if target=='sticker' else 0)
            Image.fromarray(np.uint8(subject*255+.5),'L').save(stage/'masque_ia_original.png')
            Image.fromarray(solid,'L').save(stage/'contour_candidate.png')
            Image.fromarray(result,'RGBA').save(stage/'STICKER_IA_A_VERIFIER.png')
            (stage/'contour_ia_CANDIDAT.svg').write_text(line.svg_cut(solid),encoding='utf8')
            # SVG Cricut = une silhouette extérieure à la bonne taille physique.
            # Le PNG ne porte PAS les chemins des yeux ou des cheveux.
            with Image.open(root/'02_ZONE_UTILE'/'carte_redressee.png') as original:
                source_w=original.width
            svg_width_mm=float(width_mm)*solid.shape[1]/source_w
            _rescale_svg(stage/'contour_ia_CANDIDAT.svg',
                         stage/'02_DECOUPER_CONTOUR_IA_A_VERIFIER.svg',svg_width_mm)
            shutil.copyfile(stage/'STICKER_IA_A_VERIFIER.png',
                            stage/'01_IMPRIMER_DECOUPER_CONTOUR_IA_A_VERIFIER.png')
            # Les détails intérieurs ne changent pas avec le masque : mêmes exports
            # que V20.1.2, pour éviter toute double découpe accidentelle.
            report['choix_cricut_ia']={
                'imprimer_decouper_contour':'01_IMPRIMER_DECOUPER_CONTOUR_IA_A_VERIFIER.png',
                'decouper_contour_seul':'02_DECOUPER_CONTOUR_IA_A_VERIFIER.svg',
                'decouper_tous_les_traits':None,
                'dessiner_au_stylo':None,
                'tout_preparer':'01_IMPRIMER_DECOUPER_CONTOUR_IA_A_VERIFIER.png'}
            report['largeur_silhouette_ia_mm']=round(svg_width_mm,3)
            report['fichiers']={name:name for name in ('masque_ia_original.png','contour_candidate.png',
                   'STICKER_IA_A_VERIFIER.png','contour_ia_CANDIDAT.svg',
                   '01_IMPRIMER_DECOUPER_CONTOUR_IA_A_VERIFIER.png',
                   '02_DECOUPER_CONTOUR_IA_A_VERIFIER.svg')}
            report['decalage_traits_px']=[padding,padding]
            report['couverture_masque_source_px']=int(np.count_nonzero(subject>=.5))
            ink_count=int(np.count_nonzero(ink))
            inner=int(np.count_nonzero((ink>0)&(subject>=.5)))
            report['traits_sur_masque_pct']=round(100*inner/max(1,ink_count),2)
            if ink_count and inner/ink_count<.55:
                report['avertissements'].append('TRAITS_POTENTIELLEMENT_COUPES_PAR_MASQUE_IA')
            # Visual QA uses pink fill only as an overlay, never as a cut proof.
            rgb_view=np.repeat((255-ink)[:,:,None],3,axis=2).astype(np.uint8)
            overlay=rgb_view.astype(np.float32)
            alpha=(subject>=.5)
            overlay[alpha]=.66*overlay[alpha]+.34*np.float32([245,55,155])
            comparison=np.concatenate([rgb_view,np.uint8(np.clip(overlay,0,255))],axis=1)
            Image.fromarray(comparison,'RGB').save(stage/'apercu_ia_superposition.png')
            report['fichiers']['apercu_ia_superposition.png']='apercu_ia_superposition.png'
            report['couverture_decoupe_px']=int(np.count_nonzero(solid))
            if selection.get('ambiguite'):
                report['avertissements'].append('PLUSIEURS_SUJETS_POSSIBLES_CHOIX_A_VERIFIER')
            if any(x.get('contact_bord') for x in selection.get('candidats',[]) if x['index']==selection.get('index_retenu')):
                report['avertissements'].append('SUJET_TOUCHE_BORD_DE_CARTE')
        else:
            report['avertissements'].append('AUCUN_CONTOUR_IA_EXPORTABLE')
        # Aucune opération de découpe interne ne dépend du masque IA.
        report['fichier_mode_choisi']=base['recommended_file']
        report['provenance_fichier_mode_choisi']='GEOMETRIQUE_OU_TRAITS_V20_1_2'
        if subject is not None and operation in ('imprimer_decouper_contour',
                                                  'decouper_contour_seul','tout_preparer'):
            selected_name=(report['choix_cricut_ia']['decouper_contour_seul'] if
                           operation=='decouper_contour_seul' else
                           report['choix_cricut_ia']['imprimer_decouper_contour'])
            report['fichier_mode_choisi']=str(qa/selected_name)
            report['provenance_fichier_mode_choisi']='MASQUE_IA_CANDIDAT_A_VERIFIER'
            report['avertissements'].append('NE_PAS_DECOUPER_AVANT_CONTROLE_VISUEL')
        (stage/'GUIDE_CHOIX_V20_2.txt').write_text(
            'Contenu du dossier 08_CHOIX_CRICUT : modes V20.1.2 non modifies.\n'
            'Dans ce dossier IA : 01_ = imprimer + decouper contour IA candidat;\n'
            '02_ = contour IA candidat en Decoupe de base.\n'
            '03_ (tous les traits) et 04_ (stylo) restent dans 08_CHOIX_CRICUT.\n'
            'NE PAS IMPORTER simultanement 01 et 02 pour le meme sticker.\n'
            'Aucune silhouette IA ne peut etre tenue pour valide sans controle manuel.\n',
            encoding='utf8')
        (stage/'rapport_v20_2.json').write_text(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf8')
        os.replace(stage,qa);stage=None
    except BaseException:
        if stage is not None:shutil.rmtree(stage,ignore_errors=True)
        # The baseline directory was created in this call, never user owned.
        shutil.rmtree(root,ignore_errors=True)
        raise
    return {'root':str(root),'base':base,'qa':str(qa),'report':report,
            'image_candidat':str(qa/'STICKER_IA_A_VERIFIER.png') if subject is not None else None,
            'fichier_mode_choisi':report['fichier_mode_choisi'],
            'mode_choisi_provenance':report['provenance_fichier_mode_choisi'],
            'choix':base['choice_report']}
