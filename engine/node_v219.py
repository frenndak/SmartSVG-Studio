"""V21.9 optional full-source-resolution contour inspection before Cricut export."""
from __future__ import annotations
import json
import numpy as np
import torch
from .node_v218 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .node_v216 import _output_directory
from .smartsvg_compat.registry import merge_registry
from .smartsvg_native.inspector import NativeInspectionError, analyse, publish_native


class SmartSVGNativeInspectorV219:
    """Inspect source-accurate cuts. Returns original mask and image objects unchanged."""
    CATEGORY='SmartSVG / 01 CRÉER'
    FUNCTION='run'
    RETURN_TYPES=('MASK','IMAGE','STRING')
    RETURN_NAMES=('masques_inchanges','image_inchangee','diagnostic_natif_json')
    OUTPUT_NODE=True

    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'image':('IMAGE',),'masques':('MASK',),
                            'largeur_mm':('FLOAT',{'default':40.,'min':5.,'max':300.,'step':0.5})}}

    def run(self,image,masques,largeur_mm=40.):
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise NativeInspectionError('Inspection native : IMAGE [1,H,W,RGB(A)] requise')
        if not isinstance(masques,torch.Tensor) or masques.ndim!=3:
            raise NativeInspectionError('Inspection native : MASK [N,H,W] requis')
        if (tuple(image.shape[1:3])!=tuple(masques.shape[1:]) or image.shape[1]*image.shape[2]>5_000_000
            or masques.numel()>50_000_000 or not 1<=masques.shape[0]<=32):
            raise NativeInspectionError('Inspection native : source et masques non alignés ou trop volumineux')
        image_np=image[0].detach().float().cpu().numpy()
        masks_np=masques.detach().float().cpu().numpy()
        report=analyse(image_np,masks_np,width_mm=largeur_mm)
        result={'result':(masques,image,json.dumps(report,ensure_ascii=False,allow_nan=False)),
                'ui':{'text':[f"Inspection native V21.9 : {len(masks_np)} sujet(s), statut {report['statut']}. "
                               'Aucun masque modifié. Les alertes restent indicatives.'], 'smartsvg_native':[]}}
        try:
            copies=publish_native(image_np,masks_np,_output_directory())
            if copies:
                result['ui']['smartsvg_native']=[{'version':1,'width':copies['largeur_px'],
                    'height':copies['hauteur_px'],'count':len(masks_np), 'image':copies['image'],
                    'masks':copies['masks'], 'objects':report['objets']}]
            else:
                result['ui']['text'].append('Copies natives indisponibles / limite disque atteinte ; export Cricut inchangé.')
        except Exception:
            result['ui']['text'].append('Visualisation native indisponible ; export Cricut inchangé.')
        return result

NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
    'SmartSVGNativeInspectorV219':(SmartSVGNativeInspectorV219,'01 · SmartSVG V21.9 — inspecter contours natifs')})
