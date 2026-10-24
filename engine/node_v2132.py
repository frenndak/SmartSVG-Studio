"""V21.3.2: discoverability, inline guidance, transparent statuses.

No modifications to historical production or to the wire contracts of existing nodes.
"""
from __future__ import annotations
import copy
import json
from .node_v2131 import (SmartSVGExpressV2131, SmartSVGInstancesV2131,
    NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES)
from .diagnostic_v2132 import _status,render_diagnostic

TOOLTIPS_EXPRESS={
 'dossier_sortie':"Laisser vide pour le dossier de sortie SmartSVG de ComfyUI. Les sous-dossiers de chaque projet sont crees automatiquement.",
 'projet':"Planche 24/12 = fond simple et grille; Sticker = detourage du sujet uniquement si un masque fiable est disponible; Carte = image entiere.",
 'largeur_mm':"Largeur physique souhaitee hors ou avec marge selon le projet; verifier les dimensions finales dans Design Space.",
 'qualite_ppp':"Definit les pixels exportes; ne recree pas les details absents de l'image source.",
 'ia_locale':"Desactivee = ne demarre pas d'IA interne; les masques deja relies a l'entree restent utilises. Obligatoire = erreur si pas de masque.",
 'masques_objets':"Optionnel. Branche ici les masques provenant d'un noeud SAM2 ou d'un guide par instance; ce branchement ne prouve pas leur qualite.",
}
TOOLTIPS_INSTANCES={
 'profil':"Categorie des sujets a trouver. Les modes renards, chien et canard ciblent des instances separees.",
 'source_boites':"Florence-2 detecte des boites; Boites manuelles permet de guider des regions en pixels source.",
 'boites_json':"Mode manuel uniquement : liste JSON [{\"label\":\"renard\",\"bbox\":[x0,y0,x1,y1]}]. Les boites ne sont pas des contours Cricut.",
 'max_objets':"Limite le nombre d'inferences SAM2 et la consommation de memoire. Commencer par 3 pour les renards.",
 'image':"Image de ComfyUI a traiter. Maximum 5 megapixels pour ce noeud IA par instances.",
}

def _decorate(spec,tips):
    fresh=copy.deepcopy(spec)
    for group in ('required','optional'):
        for key,value in list(fresh.get(group,{}).items()):
            if key not in tips:continue
            definition=list(value)
            if len(definition)<2 or not isinstance(definition[1],dict):definition.append({})
            definition[1]['tooltip']=tips[key]
            fresh[group][key]=tuple(definition)
    return fresh


def readable_summary(report,ia_locale,has_masks,old_summary):
    """Simple, explicitly non-certifying status displayed by the Express node."""
    n=report.get('nombre_objets_exportes',0)
    source=('masques branches' if has_masks else ('IA interne demandee' if ia_locale!='Desactivee' else 'aucun masque fourni'))
    qa=report.get('controle_v212',{})
    alerts=qa.get('alertes',{})
    count=sum(int(v) for v in alerts.values()) if isinstance(alerts,dict) else len(alerts or [])
    caution=("Verifier les contours, la taille et l'operation dans Cricut Design Space."
             " Aucun test physique Cricut n'est realise automatiquement.")
    text=f"SMARTSVG — {n} export(s) | Source : {source}\nControle : {count} alerte(s) QA. {caution}"
    return text+'\n'+old_summary


class SmartSVGExpressV2132(SmartSVGExpressV2131):
    CATEGORY='SmartSVG / 01 DEMARRER'
    @classmethod
    def INPUT_TYPES(cls):
        return _decorate(super().INPUT_TYPES(),TOOLTIPS_EXPRESS)
    def run(self,image,dossier_sortie='',projet='Auto - conserver le visuel',largeur_mm=40.,
            qualite_ppp='300',ia_locale='Desactivee',masques_objets=None):
        out=super().run(image=image,dossier_sortie=dossier_sortie,projet=projet,
                        largeur_mm=largeur_mm,qualite_ppp=qualite_ppp,
                        ia_locale=ia_locale,masques_objets=masques_objets)
        tensor,summary,payload=out['result']
        msg=readable_summary(json.loads(payload),ia_locale,masques_objets is not None,summary)
        return {'ui':{'text':[msg]},'result':(tensor,msg,payload)}


class SmartSVGInstancesV2132(SmartSVGInstancesV2131):
    CATEGORY='SmartSVG / 02 GUIDAGE IA'
    @classmethod
    def INPUT_TYPES(cls):
        return _decorate(super().INPUT_TYPES(),TOOLTIPS_INSTANCES)


class SmartSVGDiagnosticV2132:
    CATEGORY='SmartSVG / 00 VERIFIER INSTALLATION'
    RETURN_TYPES=('STRING','STRING')
    RETURN_NAMES=('resume','rapport_json')
    FUNCTION='run'
    OUTPUT_NODE=True
    @classmethod
    def INPUT_TYPES(cls):return {'required':{}}
    def run(self):
        try:
            import nodes
            registry=getattr(nodes,'NODE_CLASS_MAPPINGS',None)
        except ImportError:registry=None
        try:import torch
        except ImportError:torch=None
        report=_status(registry,torch)
        summary=render_diagnostic(report)
        return {'ui':{'text':[summary]},
                'result':(summary,json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False))}

# Keep legacy IDs intact; make historical versions visibly secondary in the UI.
NODE_CLASS_MAPPINGS={**OLD,
    'SmartSVGExpressV2132':SmartSVGExpressV2132,
    'SmartSVGInstancesV2132':SmartSVGInstancesV2132,
    'SmartSVGDiagnosticV2132':SmartSVGDiagnosticV2132}
NODE_DISPLAY_NAME_MAPPINGS={
    **{key: 'Ancien · '+OLD_NAMES.get(key,key) for key in OLD},
    'SmartSVGExpressV2132':'01 - SmartSVG EXPRESS / Image vers Cricut',
    'SmartSVGInstancesV2132':'02 - SmartSVG GUIDAGE IA / Sujets distincts',
    'SmartSVGDiagnosticV2132':'00 - SmartSVG VERIFIER / Installation et GPU',
}
