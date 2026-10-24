"""V21.7: screenshot preparation and non-destructive Cricut QA."""
from __future__ import annotations
import json
import numpy as np
import torch
from .node_v216 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES, _output_directory
from .smartsvg_compat.registry import merge_registry
from .smartsvg_quality.prepare import prepare,PreparationError
from .smartsvg_quality.geometry import inspect,GeometryError
from .smartsvg_quality.previews import publish


class SmartSVGPrepareV217:
    """Crop IMAGE before masks are generated; no automatic editing of existing MASKs."""
    CATEGORY='SmartSVG / 01 CRÉER'
    RETURN_TYPES=('IMAGE','STRING')
    RETURN_NAMES=('image_preparee','rapport_recadrage')
    FUNCTION='run'
    OUTPUT_NODE=False

    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'mode':(['Conserver original','Retirer bandes noires (prudent)','Recadrage manuel (%)'],),
            'gauche_pct':('INT',{'default':0,'min':0,'max':45,'step':1}),
            'droite_pct':('INT',{'default':0,'min':0,'max':45,'step':1}),
            'haut_pct':('INT',{'default':0,'min':0,'max':45,'step':1}),
            'bas_pct':('INT',{'default':0,'min':0,'max':45,'step':1}),
        }}

    def run(self,image,mode='Conserver original',gauche_pct=0,droite_pct=0,haut_pct=0,bas_pct=0):
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise PreparationError('Préparation : IMAGE [1,H,W,RGB(A)] attendue')
        a=image[0].detach().cpu().numpy()
        _,report=prepare(a,mode,left=gauche_pct,right=droite_pct,top=haut_pct,bottom=bas_pct)
        x0,y0,x1,y1=report['zone_px']
        # Tensor view maintains exact original values; downstream segmentation sees aligned pixels.
        result=image[:,y0:y1,x0:x1,:].contiguous()
        return (result,json.dumps(report,ensure_ascii=False))


class SmartSVGQualityV217:
    """Read-only QA (pass-through MASK and IMAGE); warnings for physical cutting."""
    CATEGORY='SmartSVG / 01 CRÉER'
    RETURN_TYPES=('MASK','IMAGE','STRING')
    RETURN_NAMES=('masques_inchanges','image_inchangee','rapport_qa_json')
    FUNCTION='run'
    OUTPUT_NODE=True

    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{
            'image':('IMAGE',),
            'masques':('MASK',),
            'largeur_mm':('FLOAT',{'default':40.0,'min':5.0,'max':300.0,'step':0.5}),
        }}

    def run(self,image,masques,largeur_mm=40.0):
        if not isinstance(image,torch.Tensor) or image.ndim!=4 or image.shape[0]!=1 or image.shape[-1] not in (3,4):
            raise GeometryError('QA : IMAGE [1,H,W,RGB(A)] attendue')
        if not isinstance(masques,torch.Tensor) or masques.ndim!=3 or tuple(image.shape[1:3])!=tuple(masques.shape[1:]):
            raise GeometryError('QA : MASK [N,H,W] doit correspondre à IMAGE')
        if image.shape[1]*image.shape[2]>5_000_000 or not 1<=masques.shape[0]<=32 or masques.numel()>50_000_000:
            raise GeometryError('QA : dépasserait la limite CPU de 5 Mp/image, 32 sujets ou 50 Mp de masques')
        a=masques.detach().float().cpu().numpy()
        result=inspect(a,width_mm=largeur_mm)
        report=json.dumps(result,ensure_ascii=False,sort_keys=True)
        message=[f"SmartSVG QA V21.7 : {result['nombre_objets']} sujet(s), {result['nombre_alertes']} alerte(s), statut {result['statut']}."]
        for obj in result['objets']:
            if obj['alertes']:
                message.append('Sujet %d : %s'%(obj['objet'],', '.join(obj['alertes'])))
        if result['statut']=='ok':message.append('Aucune anomalie géométrique détectée ; vérifier malgré tout le SVG et la découpe réelle.')
        out={'result':(masques,image,report),'ui':{'text':message}}
        try:
            preview=publish(image[0].detach().float().cpu().numpy(),a,result,_output_directory())
            if preview:out['ui']['images']=[preview]
        except Exception:
            message.append('Aperçu QA indisponible ; masques et rapport préservés.')
        return out


NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
    'SmartSVGPrepareV217':(SmartSVGPrepareV217,'01 · SmartSVG V21.7 — nettoyer capture / recadrer'),
    'SmartSVGQualityV217':(SmartSVGQualityV217,'01 · SmartSVG V21.7 — contrôle qualité Cricut'),
})
