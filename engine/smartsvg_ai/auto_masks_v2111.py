"""V21.11 conservative auto masking: alpha, flat-colour artwork, optional verified SAM2.

Never substitutes a rectangular image crop for segmentation. Machine/semantic
confidence is NOT asserted by a shape heuristic or presence of a model output.
"""
from __future__ import annotations
import numpy as np
import cv2
from ..smartsvg_core.silhouette_guard_v21111 import near_rectangle

MAX_PIXELS = 5_000_000
MAX_MASKS = 32
MAX_TOTAL = 50_000_000

class AutoMaskError(ValueError):
    pass


def _validate(rgb_or_rgba):
    a=np.asarray(rgb_or_rgba)
    if a.ndim!=3 or a.shape[2] not in (3,4) or a.dtype!=np.uint8:
        raise AutoMaskError('Image RGB/RGBA uint8 requise')
    h,w=a.shape[:2]
    if not h or not w or h*w>MAX_PIXELS:
        raise AutoMaskError('Image trop grande : maximum 5 millions de pixels')
    return a


def _component_info(binary, *, min_area, limit=MAX_MASKS, with_masks=False):
    """Return (total_count, components). Never turn >limit into zero components.

    Connected components are labelled once; no full-size float32 masks are made
    merely to audit the number of islands.
    """
    n,lab,stats,_=cv2.connectedComponentsWithStats(np.ascontiguousarray(binary,dtype=np.uint8),8)
    candidates=sorted(((int(stats[i,cv2.CC_STAT_AREA]),i) for i in range(1,n)
                      if int(stats[i,cv2.CC_STAT_AREA])>=min_area),reverse=True)
    count=len(candidates)
    if not with_masks or count>limit:return count,[]
    return count,[np.ascontiguousarray(lab==i,dtype=np.uint8) for _,i in candidates]


def _components(binary, *, min_area, limit=MAX_MASKS):
    """Legacy internal helper used to materialize alpha components."""
    _,components=_component_info(binary,min_area=min_area,limit=limit,with_masks=True)
    return components


def _is_rectangle(mask):
    return near_rectangle(mask>=.5)


def _accept(masks, *, pixel_count, source, expected_hw=None):
    if masks is None:return None,['AUCUN_MASQUE']
    try:
        a=np.asarray(masks)
    except (TypeError,ValueError,RuntimeError):
        return None,['MASQUES_FORMAT_INVALIDE']
    if a.ndim==2:a=a[None]
    # A matching number of pixels is NOT sufficient (H/W can be swapped).
    if (expected_hw is None or len(expected_hw)!=2 or
        a.ndim!=3 or not 1<=a.shape[0]<=MAX_MASKS or
        tuple(a.shape[1:])!=tuple(expected_hw) or
        a.shape[1]*a.shape[2]!=pixel_count or
        a.size>MAX_TOTAL or a.dtype.kind not in 'biuf' or not np.isfinite(a).all()):
        return None,['MASQUES_FORMAT_INVALIDE']
    if a.min()<-.001 or a.max()>1.001:return None,['MASQUES_PLAGE_INVALIDE']
    flags=[]
    for i,m in enumerate(a):
        count=int(np.count_nonzero(m>=.5))
        if count<max(65,int(pixel_count*.00045)) or count>int(pixel_count*.94):
            return None,['MASQUE_VIDE_TROP_PETIT_OU_PLEIN']
        if _is_rectangle(m):
            return None,['SILHOUETTE_RECTANGULAIRE_OU_QUASI_RECTANGULAIRE_REFUSEE']
        count_islands,_=_component_info(m>=.5,min_area=20)
        if count_islands>MAX_MASKS:
            return None,[f'SUJET_{i+1}_TROP_D_ILOTS_{count_islands}']
        if count_islands>1:flags.append(f'SUJET_{i+1}_ILOTS_A_VERIFIER_{count_islands}')
        if (m[0]>=.5).any() or (m[-1]>=.5).any() or (m[:,0]>=.5).any() or (m[:,-1]>=.5).any():
            flags.append(f'SUJET_{i+1}_TOUCHE_BORD')
    if source=='IA':flags.append('SORTIE_IA_NON_CERTIFIEE_HUMAINEMENT')
    return np.ascontiguousarray(a,dtype=np.float32),flags


def _bands(signal, minsize, threshold=.009):
    k=max(9,int(len(signal)*.009)|1)
    blurred=np.convolve(signal,np.ones(k,dtype=np.float32)/k,'same')
    indices=np.flatnonzero(blurred>threshold)
    if not len(indices):return []
    ranges=np.split(indices,np.flatnonzero(np.diff(indices)>1)+1)
    return [(int(g[0]),int(g[-1])+1) for g in ranges if len(g)>=minsize]


def _flat_artwork(rgb):
    """A high-precision *candidate* only for white, even-background colour drawings.

    Separates disconnected bands (e.g. 4x3 sticker sheets) by colour saturation;
    dotted black *cut guides* are intentionally not treated as sticker outlines.
    The source image is never modified by this function.
    """
    h,w=rgb.shape[:2]
    edge=np.concatenate((rgb[0],rgb[-1],rgb[:,0],rgb[:,-1])).astype(np.float32)
    median=np.median(edge,axis=0)
    # Require genuinely plain near-white edge; do not apply to photos/screenshots.
    if median.min()<233 or np.percentile(np.max(abs(edge-median),axis=1),95)>15:
        return None,{'raison':'FOND_NON_UNIFORME_OU_NON_BLANC'}
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    foreground=np.uint8((hsv[:,:,1]>=47)&(hsv[:,:,2]>55))
    if not .04<float(foreground.mean())<.68:
        return None,{'raison':'COULEUR_ABSENTE_OU_TROP_ETENDUE'}
    xs=_bands(foreground.mean(axis=0),max(12,int(w*.06)))
    ys=_bands(foreground.mean(axis=1),max(12,int(h*.055)))
    if not xs or not ys or len(xs)*len(ys)>MAX_MASKS:
        return None,{'raison':'STRUCTURE_SUJETS_INDETERMINEE'}
    # Check the entire mask budget BEFORE allocating per-subject full-frame buffers.
    if len(xs)*len(ys)*h*w>MAX_TOTAL:
        return None,{'raison':'BUDGET_MEMOIRE_MASQUES'}
    result=[]; qa=[]
    for y0,y1 in ys:
        for x0,x1 in xs:
            dx=min(10,max(2,(x1-x0)//25));dy=min(10,max(2,(y1-y0)//25))
            bx0=max(0,x0-dx); bx1=min(w,x1+dx)
            by0=max(0,y0-dy); by1=min(h,y1+dy)
            # Colour projection locates each card; the actual silhouette must
            # also include dark outlines and white petals enclosed by outlines.
            # Unlike the saturation-only proposal this avoids detached eye/flower
            # centres, and rejects dashed guide frames as tiny components.
            rgb_cell=rgb[by0:by1,bx0:bx1]
            view=np.uint8(rgb_cell.min(axis=2)<205)
            closed=cv2.morphologyEx(view,cv2.MORPH_CLOSE,
                cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
            n,labels,stats,_=cv2.connectedComponentsWithStats(closed,8)
            components=sorted([(int(stats[i,cv2.CC_STAT_AREA]),i) for i in range(1,n)],reverse=True)
            if not components or components[0][0]<(bx1-bx0)*(by1-by0)*.07:
                return None,{'raison':'ZONE_COLOREE_TROP_PETITE'}
            selected=np.uint8(labels==components[0][1])*255
            contours,_=cv2.findContours(selected,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            filled=np.zeros_like(view)
            cv2.drawContours(filled,contours,-1,255,cv2.FILLED)
            proportion=float(np.count_nonzero(filled)/filled.size)
            if not .07<proportion<.86:
                return None,{'raison':'TAUX_REMPLISSAGE_SUSPECT'}
            whole=np.zeros((h,w),dtype=np.uint8)
            whole[by0:by1,bx0:bx1]=filled//255
            if _is_rectangle(whole):return None,{'raison':'ZONE_RECTANGULAIRE'}
            result.append(whole)
            qa.append({'bbox_case':[bx0,by0,bx1,by1], 'coverage':round(proportion,4),
                       'fragments_detectes':len(components)})
    return np.stack(result).astype(np.float32),{'cases_colonnes':len(xs),'cases_lignes':len(ys),'qa_cases':qa}


def generate_masks(image, *, allow_ai=False, force_ai=False, provider=None, supplied_alpha=None):
    """Return (MASK or None, audit). Optional provider(rgb)->dict masks is injected/real.

    AI is never claimed unless provider actually executed. Absent or suspect
    results fail closed; no silent rectangular exports.
    """
    a=_validate(image);h,w=a.shape[:2]
    evidence={'version':'21.11.1','dimensions_px':[w,h],'certification_cricut':False,
              'segmentation_semantique_prouvee':False,'statut':'CORRECTION_NECESSAIRE',
              'methode':None,'avertissements':[],'nombre_sujets':0}
    if supplied_alpha is not None and a.shape[-1]==4:
        raise AutoMaskError('Alpha RGBA et masque LoadImage fournis ensemble : source ambigue')
    if supplied_alpha is not None:
        external=np.asarray(supplied_alpha)
        if external.ndim!=2 or external.shape!=(h,w) or external.dtype.kind not in 'biuf' or not np.isfinite(external).all():
            raise AutoMaskError('MASK de LoadImage : dimensions/valeurs invalides')
        if external.min()<-.001 or external.max()>1.001:
            raise AutoMaskError('MASK de LoadImage hors [0,1]')
        # ComfyUI LoadImage: MASK=1-alpha. Empty MASK on an opaque source is
        # NOT evidence of a ready cutout and must fall through to detection.
        alpha=np.ascontiguousarray(1.-external,dtype=np.float32)
    elif a.shape[-1]==4:
        alpha=np.ascontiguousarray(a[:,:,3].astype(np.float32)/255.)
    else:
        alpha=None
    if alpha is not None and not force_ai:
        if alpha.min()<.98 and alpha.max()>.05:
            alpha_count,cc=_component_info(alpha>=.5,min_area=max(65,int(h*w*.00045)),
                                            with_masks=True)
            if alpha_count>MAX_MASKS:
                evidence['avertissements'].append(f'ALPHA_TROP_D_ILOTS_{alpha_count}')
            if cc and len(cc)*h*w<=MAX_TOTAL:
                candidate=np.stack([alpha*ccmask for ccmask in cc])
                result,flags=_accept(candidate,pixel_count=h*w,expected_hw=(h,w),source='ALPHA')
                if result is not None:
                    evidence.update({'statut':'MASQUES_PROPOSES_A_VERIFIER','methode':('ALPHA_LOADIMAGE' if supplied_alpha is not None else 'ALPHA_ORIGINAL'),
                                     'nombre_sujets':len(result),'avertissements':flags})
                    return result,evidence
            evidence['avertissements'].extend(flags if cc and 'flags' in locals() else [])
            evidence['avertissements'].append('ALPHA_INSUFFISANT_OU_RECTANGULAIRE')
    output,detail=_flat_artwork(a[:,:,:3]) if not force_ai else (None,{"raison":"IA_OBLIGATOIRE"})
    if output is not None:
        result,flags=_accept(output,pixel_count=h*w,expected_hw=(h,w),source='HEURISTIQUE')
        if result is not None:
            evidence.update({'statut':'MASQUES_PROPOSES_A_VERIFIER','methode':'ILLUSTRATION_FOND_BLANC',
                             'nombre_sujets':len(result),'avertissements':flags,
                             'analyse':detail,'segmentation_semantique_prouvee':False})
            return result,evidence
    else:evidence['avertissements'].append(detail['raison'])
    if allow_ai:
        try:
            if provider is None:
                from ..auto_segment_v192 import segment_scene
                provider=lambda rgb:segment_scene(rgb,profile='auto',
                    custom_prompts='person;animal;cartoon character;toy',max_results=12)
            inference=provider(a[:,:,:3])
            if not isinstance(inference,dict):raise AutoMaskError('Fournisseur IA : sortie invalide')
            result,flags=_accept(inference.get('masks'),pixel_count=h*w,expected_hw=(h,w),source='IA')
            evidence['ia']={'execution_effective':True,'diagnostic_fournisseur':inference.get('audit')}
            if result is not None:
                evidence.update({'statut':'MASQUES_PROPOSES_A_VERIFIER','methode':'SEGMENTATION_IA',
                                 'nombre_sujets':len(result),'avertissements':evidence['avertissements']+flags})
                return result,evidence
            evidence['avertissements'].extend(flags)
        except Exception as exc:
            evidence['ia']={'execution_effective':False,'erreur':f'{type(exc).__name__}: {str(exc)[:180]}'}
            evidence['avertissements'].append('IA_INDISPONIBLE_OU_INCOMPATIBLE')
    evidence['explication']='Aucun détourage fiable : fournir MASK externe, corriger dans l’éditeur ou installer un fournisseur IA compatible.'
    return None,evidence
