"""SmartSVG V21.11.2 stabilization: environment check, common physical width and clear handoff.

Never replaces old node IDs, and does not modify manufacturing PNG/SVG algorithms.
"""
from __future__ import annotations
import json
import copy
from .node_v2111 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .node_v2111 import SmartSVGAutoExpressV2111
from .node_v2110 import SmartSVGUnifiedEditorV2110
from .smartsvg_compat.readiness_v21112 import diagnose
from .smartsvg_compat.registry import merge_registry


class SmartSVGReadinessV21112:
    CATEGORY='SmartSVG / 00 DÉMARRER'
    FUNCTION='run'
    OUTPUT_NODE=True
    RETURN_TYPES=('STRING',)
    RETURN_NAMES=('rapport_diagnostic_json',)
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'action':(['Vérifier mon installation'],)}}
    def run(self,action='Vérifier mon installation'):
        report=diagnose()
        text=(f"SmartSVG : {report['statut']} | RMBG/SAM2 : {report['rmbg_sam2']['statut']} | "
              f"CUDA visible : {'oui' if report['cuda_visible'] else 'non'} | "
              "Inférence, modèles et découpe physique non testés. " + report['conseil'])
        return {'result':(json.dumps(report,ensure_ascii=False,allow_nan=False),),
                'ui':{'text':[text]}}


class SmartSVGUnifiedEditorV21112(SmartSVGUnifiedEditorV2110):
    """Same reversible strokes; one measured width forwarded unchanged to Express."""
    CATEGORY='SmartSVG / 01 CRÉER'
    RETURN_TYPES=('MASK','IMAGE','STRING','FLOAT')
    RETURN_NAMES=('masques_corriges','image_source','diagnostic_json','largeur_mm_pour_express')
    @classmethod
    def INPUT_TYPES(cls):
        spec=copy.deepcopy(super().INPUT_TYPES())
        spec.setdefault('optional',{})['largeur_mm']=(
            'FLOAT',{'default':40.0,'min':5.0,'max':300.0,'step':1.0,
            'tooltip':'Largeur réelle du sticker, envoyée aussi vers largeur_mm du nœud Express'})
        return spec
    def run(self,image,retouches_json='',masque_base=None,largeur_mm=40.0):
        response=super().run(image,retouches_json,masque_base,
                             _qa_width_mm=largeur_mm,_qa_real=True)
        masks,source,raw=response['result']
        response['result']=(masks,source,raw,float(largeur_mm))
        return response


class SmartSVGAutoExpressV21112(SmartSVGAutoExpressV2111):
    """Explicit local-only status and a non-technical handoff; same five widgets."""
    CATEGORY='SmartSVG / 01 CRÉER'
    def run(self, image, dossier_sortie='', projet='Auto - conserver le visuel',
            largeur_mm=40.,qualite_ppp='300',ia_locale='Si disponible',
            masques_objets=None,alpha_loadimage=None):
        result=super().run(image,dossier_sortie,projet,largeur_mm,qualite_ppp,
                           ia_locale,masques_objets,alpha_loadimage)
        preview,summary,raw=result['result']
        try:
            report=json.loads(raw)
            imp=report.get('import_direct_cricut_v218') or {}
            masks=report.get('detourage_automatique_v2111') or {}
            silhouettes=int(imp.get('fichiers_prets',0))-int(imp.get('cartes_rectangulaires',0))
            if silhouettes>0 and silhouettes==imp.get('nombre_objets') and masks.get('methode'):
                level='CONTROLE_LOCAL_OK_VERIFICATION_VISUELLE'
                step='Importer les PNG de 00_IMPORTER_DANS_CRICUT, puis vérifier les contours et dimensions dans Design Space.'
            elif int(imp.get('cartes_rectangulaires',0))>0:
                level='CARTE_RECTANGULAIRE'
                step='Découpe rectangulaire : ne pas confondre avec une silhouette détourée.'
            else:
                level='CORRECTION_OU_VERIFICATION_REQUISE'
                step='Inspecter le masque et le dossier de fabrication ; aucun succès Cricut réel garanti.'
            report['parcours_simple_v21112']={'statut':level,
                  'sujets_precontroles_localement':max(0,silhouettes),
                  'import_design_space_execute':False,'decoupe_physique_executee':False,
                  'action':step}
            raw=json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)
            summary+='\nÉtat SmartSVG : '+level+' — '+step
            result['result']=(preview,summary,raw)
            if isinstance(result.get('ui'),dict):
                result['ui']['text']=[summary]
                result['ui']['smartsvg_steps_v21112']=[{
                    'statut':level,'sujets':max(0,silhouettes),
                    'cartes':int(imp.get('cartes_rectangulaires',0)),
                    'action':step,'certifie_physiquement':False}]
        except (KeyError,TypeError,ValueError):
            # Manufacturing success remains valid even if a status panel fails.
            pass
        return result

NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
    'SmartSVGReadinessV21112':(SmartSVGReadinessV21112,'00 · Vérifier mon installation SmartSVG'),
    'SmartSVGUnifiedEditorV21112':(SmartSVGUnifiedEditorV21112,'01 · Corriger et inspecter — taille Cricut réelle'),
    'SmartSVGAutoExpressV21112':(SmartSVGAutoExpressV21112,'01 · SMARTSVG AUTO — Export Cricut guidé'),
})
