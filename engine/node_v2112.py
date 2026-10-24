"""SmartSVG V21.12: adaptive RMBG masks with strictly preserved Cricut exports.

Only the new V21.12 IDs activate the new provider. All old workflows remain valid.
"""
from __future__ import annotations
import copy
import json
import numpy as np
import torch
from .node_v21112 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .node_v21112 import SmartSVGAutoExpressV21112,SmartSVGReadinessV21112
from .node_v2111 import _input_pixels,_loadimage_alpha
from .smartsvg_ai.auto_masks_v2111 import generate_masks,AutoMaskError
from .smartsvg_ai.provider_v2112 import segment_adaptive,available
from .smartsvg_compat.registry import merge_registry
from .node_v211 import PROJETS


def automatic(image,ia_locale='Si disponible',alpha_loadimage=None,*,provider=None):
    if ia_locale not in ('Desactivee','Si disponible','Obligatoire'):
        raise AutoMaskError('Choix IA inconnu')
    rgb=_input_pixels(image)
    alpha=_loadimage_alpha(alpha_loadimage,rgb.shape[:2])
    if provider is None:provider=segment_adaptive
    masks,info=generate_masks(rgb,allow_ai=ia_locale!='Desactivee',
                              force_ai=ia_locale=='Obligatoire',
                              supplied_alpha=alpha,provider=provider)
    info['version_orchestrateur']='21.12'
    info['verifie_sur_cette_machine']=False
    info['qualite_semantique_certifiee']=False
    if masks is None:
        raise AutoMaskError('Aucune silhouette sûre à exporter : '+
            json.dumps(info,ensure_ascii=False,default=str)[:750])
    return torch.from_numpy(np.ascontiguousarray(masks)),info


class SmartSVGAutoMasksV2112:
    CATEGORY='SmartSVG / 01 CRÉER'
    FUNCTION='run'
    RETURN_TYPES=('MASK','IMAGE','STRING')
    RETURN_NAMES=('masques_proposes','image_source','diagnostic_json')
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'image':('IMAGE',),
            'ia_locale':(['Desactivee','Si disponible','Obligatoire'],{'default':'Si disponible'})},
            'optional':{'alpha_loadimage':('MASK',)}}
    def run(self,image,ia_locale='Si disponible',alpha_loadimage=None):
        masks,info=automatic(image,ia_locale,alpha_loadimage)
        return {'result':(masks,image,json.dumps(info,ensure_ascii=False,allow_nan=False)),
                'ui':{'text':[f"V21.12 : {info['nombre_sujets']} masque(s) proposés ({info['methode']}) — vérifier avant découpe."]}}


class SmartSVGAutoExpressV2112(SmartSVGAutoExpressV21112):
    CATEGORY='SmartSVG / 01 CRÉER'
    @classmethod
    def INPUT_TYPES(cls):
        return copy.deepcopy(super().INPUT_TYPES())
    def run(self,image,dossier_sortie='',projet='Auto - conserver le visuel',largeur_mm=40.,
            qualite_ppp='300',ia_locale='Si disponible',masques_objets=None,alpha_loadimage=None):
        # User-selected rectangular cards are not restricted by automatic stickers.
        if projet==PROJETS[4] or masques_objets is not None:
            return super().run(image,dossier_sortie,projet,largeur_mm,qualite_ppp,
                               ia_locale,masques_objets,alpha_loadimage)
        masks,info=automatic(image,ia_locale,alpha_loadimage)
        result=super().run(image,dossier_sortie,projet,largeur_mm,qualite_ppp,
                           'Desactivee',masks,None)
        png,summary,raw=result['result']
        try:
            report=json.loads(raw)
            report['detourage_ia_v2112']=info
            # The mask port of the parent is a transport mechanism only.
            report['masque_externe_interne_utilise']='Masque précontrôlé transmis depuis l’orchestrateur V21.12'
            raw=json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)
            summary+=f"\nV21.12 : {info['methode']} — silhouette à contrôler visuellement dans Design Space."
            result['result']=(png,summary,raw)
            if isinstance(result.get('ui'),dict):result['ui']['text']=[summary]
        except (ValueError,TypeError,KeyError):pass
        return result


class SmartSVGReadinessV2112(SmartSVGReadinessV21112):
    CATEGORY='SmartSVG / 00 DÉMARRER'
    def run(self,action='Vérifier mon installation'):
        result=super().run(action)
        raw,=result['result']
        try:info=json.loads(raw)
        except (ValueError,TypeError):info={}
        providers=available()
        info['fournisseurs_v2112']=providers
        info['inference_effectuee']=False
        info['modeles_charges_sur_gpu']=False
        n=sum(x['statut']=='CONTRAT_COMPATIBLE_NON_EXECUTE' for x in providers)
        info['statut_ia_v2112']='INTERFACES_DETECTEES_NON_TESTEES' if n else 'AUCUNE_INTERFACE_IA_COMPATIBLE'
        return {'result':(json.dumps(info,ensure_ascii=False,allow_nan=False),),
                'ui':{'text':[f"IA V21.12 : {n} fournisseur(s) compatibles sur le papier. Inférence réelle et VRAM NON vérifiées."]}}


NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
 'SmartSVGAutoMasksV2112':(SmartSVGAutoMasksV2112,'01 · Détecter automatiquement avec IA V21.12'),
 'SmartSVGAutoExpressV2112':(SmartSVGAutoExpressV2112,'01 · SMARTSVG AUTO IA V21.12 vers Cricut'),
 'SmartSVGReadinessV2112':(SmartSVGReadinessV2112,'00 · Vérifier les modèles IA V21.12'),
})
