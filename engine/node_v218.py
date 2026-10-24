"""V21.8 single-file Cricut handoff. Five Express widgets and three ports preserved."""
from __future__ import annotations
import json
from .node_v2171 import SmartSVGExpressV2171, NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .smartsvg_cricut.direct_import_v218 import prepare_cricut_import
from .smartsvg_compat.registry import merge_registry

class SmartSVGExpressV218(SmartSVGExpressV2171):
    CATEGORY='SmartSVG / 01 CRÉER'
    def run(self,image,dossier_sortie='',projet='Auto - conserver le visuel',
            largeur_mm=40.,qualite_ppp='300',ia_locale='Desactivee',masques_objets=None):
        response=super().run(image=image,dossier_sortie=dossier_sortie,projet=projet,
            largeur_mm=largeur_mm,qualite_ppp=qualite_ppp,ia_locale=ia_locale,masques_objets=masques_objets)
        preview,summary,raw=response['result']
        try:
            report=json.loads(raw)
            check=prepare_cricut_import(report,int(qualite_ppp))
            report['import_direct_cricut_v218']=check
            raw=json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)
            message=(f"Dossier Import Cricut : {check['fichiers_prets']}/{check['nombre_objets']} "
                     f"PNG precontroles, {check['planches_pretes']} planche(s), "
                     f"{check['cartes_rectangulaires']} cadre(s) sans detourage. "
                     f"Statut : {check['statut']}. "
                     'Choisir Flat Graphic / Imprimer puis decouper; verifier la taille et le contour.')
        except Exception as exc:
            message=f'Controle Import Cricut indisponible ({type(exc).__name__}); PNG originaux conserves.'
        summary+='\n'+message
        response['result']=(preview,summary,raw)
        if isinstance(response.get('ui'),dict):response['ui']['text']=[summary]
        return response

NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
    'SmartSVGExpressV218':(SmartSVGExpressV218,'01 · SmartSVG EXPRESS V21.8 — import direct Cricut')})
