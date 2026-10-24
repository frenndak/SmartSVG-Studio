"""V21.11 automatic conservative masks / guided Cricut output.

The 5 Express settings, three ports and historical node IDs are preserved.
"""
from __future__ import annotations
import json
import numpy as np
import torch
from .node_v2110 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .node_v218 import SmartSVGExpressV218
from .node_v211 import PROJETS
from .smartsvg_ai.auto_masks_v2111 import AutoMaskError,generate_masks,_accept
from .smartsvg_compat.registry import merge_registry


def _input_pixels(image):
    if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
        raise AutoMaskError('IMAGE [1,H,W,RGB(A)] attendue')
    if image.shape[1]*image.shape[2]>5_000_000 or min(image.shape[1:3])<=0:
        raise AutoMaskError('Source pour détourage automatique limitée à 5 Mp')
    a=image[0].detach().float().cpu().numpy()
    if not np.isfinite(a).all() or a.min()<-.001 or a.max()>1.001:
        raise AutoMaskError('Pixels non finis ou hors 0..1')
    return np.uint8(np.round(np.clip(a,0,1)*255))


def _loadimage_alpha(mask, expected_hw):
    """ComfyUI LoadImage yields inverted alpha: 0 opaque, 1 transparent.

    A default zero mask on a nontransparent image is treated as 'no alpha'.
    Shape and range are checked BEFORE flattening/conversion.
    """
    if mask is None:return None
    if not isinstance(mask,torch.Tensor):
        raise AutoMaskError('MASK alpha LoadImage doit etre un tenseur')
    if mask.ndim==3 and mask.shape[0]==1:mask=mask[0]
    # Real LoadImage has returned [1,64,64] all-zero for RGB/JPEG
    # in several ComfyUI builds; it is a sentinel, not an alpha channel.
    if (mask.ndim==2 and tuple(mask.shape)==(64,64)
            and tuple(expected_hw)!=(64,64) and not torch.count_nonzero(mask).item()):
        return None
    if mask.ndim!=2 or tuple(mask.shape)!=tuple(expected_hw):
        raise AutoMaskError(f'MASK alpha LoadImage : attendu {tuple(expected_hw)}, obtenu {tuple(mask.shape)}')
    a=mask.detach().float().cpu().numpy()
    if not np.isfinite(a).all() or a.min()<-.001 or a.max()>1.001:
        raise AutoMaskError('MASK alpha LoadImage hors 0..1')
    # The fallback mask produced by LoadImage for an opaque PNG is all zero.
    if float(a.max())<=.001:return None
    return np.ascontiguousarray(a,dtype=np.float32)


def _validate_external_masks(mask, expected_hw):
    if not isinstance(mask,torch.Tensor):
        raise AutoMaskError('MASK externe doit etre un tenseur ComfyUI')
    a=mask.detach().float().cpu().numpy()
    accepted,flags=_accept(a,pixel_count=expected_hw[0]*expected_hw[1],
                           expected_hw=expected_hw,source='MASK_EXTERNE')
    if accepted is None:
        raise AutoMaskError('MASK externe refuse : '+', '.join(flags))
    return torch.from_numpy(accepted),flags


def _infer(image, mode, alpha_loadimage=None):
    data=_input_pixels(image)
    alpha=_loadimage_alpha(alpha_loadimage,data.shape[:2])
    masks,qa=generate_masks(data,allow_ai=(mode!='Desactivee'),
                            force_ai=(mode=='Obligatoire'),supplied_alpha=alpha)
    if masks is None:
        raise AutoMaskError('V21.11.1 : aucun contour fiable. '+qa.get('explication','')+' Diagnostic : '+
                            json.dumps(qa,ensure_ascii=False,default=str)[:650])
    return torch.from_numpy(np.ascontiguousarray(masks)),qa


class SmartSVGAutoMasksV2111:
    CATEGORY='SmartSVG / 01 CRÉER'
    FUNCTION='run'
    RETURN_TYPES=('MASK','IMAGE','STRING')
    RETURN_NAMES=('masques_a_verifier','image_source','rapport_detourage_json')
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'image':('IMAGE',),
                            'ia_locale':(['Desactivee','Si disponible','Obligatoire'],{'default':'Si disponible',
                            'tooltip':'Fond blanc simple sans IA, puis IA compatible si nécessaire. Ne certifie pas les contours.'})},
                'optional':{'alpha_loadimage':('MASK',)}}
    def run(self,image,ia_locale='Si disponible',alpha_loadimage=None):
        masks,info=_infer(image,ia_locale,alpha_loadimage)
        return {'result':(masks,image,json.dumps(info,ensure_ascii=False,allow_nan=False)),
                'ui':{'text':[f"V21.11.1 : {info['nombre_sujets']} masque(s) proposé(s), méthode {info['methode']}. Inspecter et corriger avant Cricut."]}}


class SmartSVGAutoExpressV2111(SmartSVGExpressV218):
    """Five-widget Express with automatic mask sourcing and refusal of fake cutouts."""
    CATEGORY='SmartSVG / 01 CRÉER'
    @classmethod
    def INPUT_TYPES(cls):
        import copy
        options=copy.deepcopy(super().INPUT_TYPES())
        field=list(options['required']['ia_locale'])
        props=dict(field[1]);props['default']='Si disponible'
        field[1]=props
        options['required']['ia_locale']=tuple(field)
        options.setdefault('optional',{})['alpha_loadimage']=('MASK',)
        return options

    def run(self,image,dossier_sortie='',projet='Auto - conserver le visuel',largeur_mm=40.,
            qualite_ppp='300',ia_locale='Si disponible',masques_objets=None,alpha_loadimage=None):
        if projet==PROJETS[4]:
            # A deliberately requested rectangular card must keep working even
            # without any detachable silhouette. Do not spend VRAM on masking.
            response=super().run(image=image,dossier_sortie=dossier_sortie,
                projet=projet,largeur_mm=largeur_mm,qualite_ppp=qualite_ppp,
                ia_locale='Desactivee',masques_objets=None)
            return response
        if masques_objets is None:
            masks,qa=_infer(image,ia_locale,alpha_loadimage)
            # No second, implicit SAM2 pass in the legacy manufacturing function.
            mode='Desactivee'
        else:
            masks,flags=_validate_external_masks(masques_objets,tuple(image.shape[1:3]))
            qa={'statut':'MASQUES_EXTERNES_A_VERIFIER','methode':'MASK_COMFYUI',
                'avertissements':flags,
                'nombre_sujets':int(masks.shape[0]) if hasattr(masks,'shape') else None,
                'validation_physique':False}
            mode='Desactivee'
        response=super().run(image=image,dossier_sortie=dossier_sortie,projet=projet,
                             largeur_mm=largeur_mm,qualite_ppp=qualite_ppp,
                             ia_locale=mode,masques_objets=masks)
        tensor,summary,raw=response['result']
        try:
            payload=json.loads(raw)
            payload['detourage_automatique_v2111']=qa
            raw=json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False)
        except (TypeError,ValueError):
            pass
        summary += '\nV21.11 : masques proposés / non certifiés. Vérifier la silhouette dans Design Space.'
        response['result']=(tensor,summary,raw)
        if 'ui' in response and isinstance(response['ui'],dict):response['ui']['text']=[summary]
        return response

NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
    'SmartSVGAutoMasksV2111':(SmartSVGAutoMasksV2111,'01 · SmartSVG V21.11.1 — détecter silhouettes automatiquement'),
    'SmartSVGAutoExpressV2111':(SmartSVGAutoExpressV2111,'01 · SmartSVG EXPRESS V21.11.1 — Auto vers Cricut'),
})
