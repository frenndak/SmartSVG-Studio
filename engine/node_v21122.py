"""V21.12.2: reliable large batches, precise local checks, old ports preserved."""
from __future__ import annotations
import copy,json,time
from .node_v21121 import NODE_CLASS_MAPPINGS as OLD,NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .node_v21121 import SmartSVGAutoExpressV21121
from .production_v211 import defer_intermediate_sheets
from .smartsvg_cricut.delivery_v21122 import delivery_manifest,write_delivery
from .smartsvg_compat.registry import merge_registry

class SmartSVGAutoExpressV21122(SmartSVGAutoExpressV21121):
    CATEGORY='SmartSVG / 01 CRÉER'
    @classmethod
    def INPUT_TYPES(cls):return copy.deepcopy(super().INPUT_TYPES())

    def run(self,image,dossier_sortie='',projet='Auto - conserver le visuel',largeur_mm=40.,
            qualite_ppp='300',ia_locale='Si disponible',masques_objets=None,alpha_loadimage=None):
        before=time.perf_counter()
        # Page building in the legacy stage is redundant: the size-reconciliation
        # stage regenerates the pages. Opt in per execution, not global state.
        with defer_intermediate_sheets():
            response=super().run(image,dossier_sortie,projet,largeur_mm,
                                 qualite_ppp,ia_locale,masques_objets,alpha_loadimage)
        preview,summary,raw=response['result']
        # Manifest is optional and must never turn successful manufacturing into
        # an apparent failure. Do not touch the manufacturing PNG/SVG at all.
        try:
            report=json.loads(raw)
            audit=delivery_manifest(report)
            audit['optimisation']={'planches_intermediaires_evitees':True,
               'temps_pipeline_s':round(time.perf_counter()-before,2),
               'benchmark_materiel_utilisateur':False}
            try:audit['manifeste']=write_delivery(report['dossier'],audit)
            except (OSError,ValueError) as exc:
                audit['avertissement_manifeste']=str(exc)[:130]
            report['livraison_v21122']=audit
            raw=json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False)
            summary+='\nV21.12.2 : '+audit['statut']+' — fichiers non certifiés physiquement.'
            response['result']=(preview,summary,raw)
            if isinstance(response.get('ui'),dict):response['ui']['text']=[summary]
        except Exception as exc:
            response['result']=(preview,summary+'\nManifeste facultatif indisponible: '+type(exc).__name__,raw)
        return response

NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
 'SmartSVGAutoExpressV21122':(SmartSVGAutoExpressV21122,
     '01 · SmartSVG V21.12.2 — Lot optimisé et fichiers Cricut'),
})
