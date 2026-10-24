"""V21.12.1: image routing, dark-sticker sheets, QA, Cricut-safe status.

New node IDs only: historical IDs and PNG/SVG manufacturing algorithms untouched.
"""
from __future__ import annotations
import copy,json
import numpy as np
import torch
from .node_v2112 import NODE_CLASS_MAPPINGS as OLD,NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .node_v2112 import SmartSVGAutoExpressV2112,SmartSVGReadinessV2112,automatic as old_automatic
from .node_v2111 import _input_pixels,_loadimage_alpha
from .node_v211 import PROJETS
from .smartsvg_ai.routing_v21121 import inspect_route,dark_sheet_masks
from .smartsvg_ai.quality_v21121 import evaluate_masks
from .smartsvg_compat.registry import merge_registry


def automatic(image, ia_locale='Si disponible', alpha_loadimage=None, *, provider=None,
              physical_width_mm=40.):
    if ia_locale not in ('Desactivee','Si disponible','Obligatoire'):
        raise ValueError('Mode IA inconnu')
    rgb=_input_pixels(image)
    effective_alpha=_loadimage_alpha(alpha_loadimage,rgb.shape[:2])
    route=inspect_route(rgb,has_alpha=(effective_alpha is not None))
    masks=None; proof=None
    if (route['type_image']=='FOND_NOIR_UNIFORME' and effective_alpha is None
            and ia_locale!='Obligatoire'):
        masks,proof=dark_sheet_masks(rgb[:,:,:3])
    if masks is not None:
        mask_tensor=torch.from_numpy(np.ascontiguousarray(masks,dtype=np.float32))
        info={'statut':'MASQUES_PROPOSES_A_VERIFIER','methode':'PLANCHE_FOND_NOIR',
              'nombre_sujets':int(masks.shape[0]),'certification_cricut':False,
              'segmentation_semantique_prouvee':False,'avertissements':list(proof['avertissements']),
              'analyse_fond_noir':proof,'version_orchestrateur':'21.12.1'}
    else:
        mask_tensor,info=old_automatic(image,ia_locale,alpha_loadimage,provider=provider)
        # The failed dark hypothesis is advisory, not a hidden success.
        if proof and proof.get('raison'):
            info['hypothese_fond_noir_refusee']=proof['raison']
    info['routage_v21121']=route
    info['controle_qualite_v21121']=evaluate_masks(mask_tensor.detach().cpu().numpy(),
        kind=route['type_image'],method=info.get('methode'),
        physical_width_mm=physical_width_mm,
        additional_flags=info.get('avertissements',()))
    info['version_orchestrateur']='21.12.1'
    info['certification_cricut']=False
    return mask_tensor,info


class SmartSVGRoutingV21121:
    CATEGORY='SmartSVG / 00 DÉMARRER'
    FUNCTION='run'
    RETURN_TYPES=('IMAGE','STRING')
    RETURN_NAMES=('image_source','rapport_routage_json')
    @classmethod
    def INPUT_TYPES(cls):return {'required':{'image':('IMAGE',)}}
    def run(self,image):
        report=inspect_route(_input_pixels(image))
        return {'result':(image,json.dumps(report,ensure_ascii=False,allow_nan=False)),
                'ui':{'text':[f"Image : {report['type_image']} ; stratégie : {report['strategie']}. Aucune IA exécutée."]}}


class SmartSVGAutoMasksV21121:
    CATEGORY='SmartSVG / 01 CRÉER'
    FUNCTION='run'
    RETURN_TYPES=('MASK','IMAGE','STRING')
    RETURN_NAMES=('masques_proposes','image_source','rapport_json')
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'image':('IMAGE',),
           'ia_locale':(['Desactivee','Si disponible','Obligatoire'],{'default':'Si disponible'})},
           'optional':{'alpha_loadimage':('MASK',)}}
    def run(self,image,ia_locale='Si disponible',alpha_loadimage=None):
        masks,report=automatic(image,ia_locale,alpha_loadimage)
        qa=report['controle_qualite_v21121']
        return {'result':(masks,image,json.dumps(report,ensure_ascii=False,allow_nan=False)),
                'ui':{'text':[f"{qa['nombre_masques']} sujet(s) — {qa['statut']} ; vérifier les contours avant Cricut."]}}


class SmartSVGAutoExpressV21121(SmartSVGAutoExpressV2112):
    CATEGORY='SmartSVG / 01 CRÉER'
    @classmethod
    def INPUT_TYPES(cls):return copy.deepcopy(super().INPUT_TYPES())
    def run(self,image,dossier_sortie='',projet='Auto - conserver le visuel',largeur_mm=40.,
            qualite_ppp='300',ia_locale='Si disponible',masques_objets=None,alpha_loadimage=None):
        if projet==PROJETS[4]:
            return super().run(image,dossier_sortie,projet,largeur_mm,qualite_ppp,
                               ia_locale,masques_objets,alpha_loadimage)
        if masques_objets is not None:
            raw_masks=masques_objets.detach().cpu().numpy() if hasattr(masques_objets,'detach') else np.asarray(masques_objets)
            if raw_masks.ndim==2:raw_masks=raw_masks[None]
            kind=inspect_route(_input_pixels(image))['type_image']
            details=evaluate_masks(raw_masks,kind=kind,method='MASQUES_EXTERIEURS_CORRIGES',
                                   physical_width_mm=largeur_mm)
            info={'methode':'MASQUES_FOURNIS','routage_v21121':{'type_image':kind},
                  'nombre_sujets':len(raw_masks),'controle_qualite_v21121':details,
                  'certification_cricut':False}
            masks=masques_objets
        else:
            masks,info=automatic(image,ia_locale,alpha_loadimage,physical_width_mm=largeur_mm)
        # The corrected mask is routed through exactly the existing stable
        # manufacturing engine; never run segmentation a second time.
        response=super().run(image,dossier_sortie,projet,largeur_mm,qualite_ppp,
                             'Desactivee',masks,None)
        png,summary,raw=response['result']
        try:
            payload=json.loads(raw)
            payload['analyse_automatique_v21121']=info
            payload['etat_validation_v21121']=info['controle_qualite_v21121']['statut']
            raw=json.dumps(payload,ensure_ascii=False,indent=2,allow_nan=False)
            summary+='\nV21.12.1 : '+payload['etat_validation_v21121']+' — détourage à vérifier dans Cricut.'
            response['result']=(png,summary,raw)
            if isinstance(response.get('ui'),dict):response['ui']['text']=[summary]
        except (ValueError,TypeError,KeyError):pass
        return response


NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
    'SmartSVGRoutingV21121':(SmartSVGRoutingV21121,'00 · Reconnaître le type d’image — sans IA'),
    'SmartSVGAutoMasksV21121':(SmartSVGAutoMasksV21121,'01 · Détourage intelligent V21.12.1'),
    'SmartSVGAutoExpressV21121':(SmartSVGAutoExpressV21121,'01 · Export Cricut automatique V21.12.1')})
