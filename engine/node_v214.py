"""V21.4: thin compatibility façade over modular contracts, AI, Cricut, UX.

The underlying image/segmentation/vectorization engines are unchanged.
All historical ComfyUI node IDs are preserved.
"""
from __future__ import annotations
import json
from .node_v2132 import (SmartSVGExpressV2132, SmartSVGInstancesV2132,
                         SmartSVGDiagnosticV2132,
                         NODE_CLASS_MAPPINGS as OLD,
                         NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES)
from .smartsvg_core.contracts import ExpressRequest
from .smartsvg_core.reporting import checked_report,render_express_report
from .smartsvg_cricut.inspection import report_dimension_disagreements
from .smartsvg_ai.hardware import summary as gpu_summary
from .smartsvg_compat.registry import merge_registry


class SmartSVGExpressV214(SmartSVGExpressV2132):
    """Single recommended Express node; compatible with the V21.3.2 ports."""
    CATEGORY='SmartSVG / 01 CRÉER'
    @classmethod
    def INPUT_TYPES(cls):
        return super().INPUT_TYPES()

    def run(self,image,dossier_sortie='',projet='Auto - conserver le visuel',
            largeur_mm=40.,qualite_ppp='300',ia_locale='Desactivee',masques_objets=None):
        intent=ExpressRequest.from_widgets(projet=projet,largeur_mm=largeur_mm,
                                           qualite_ppp=qualite_ppp,ia_locale=ia_locale,
                                           masques_objets=masques_objets)
        output=super().run(image=image,dossier_sortie=dossier_sortie,projet=projet,
                           largeur_mm=largeur_mm,qualite_ppp=qualite_ppp,
                           ia_locale=ia_locale,masques_objets=masques_objets)
        tensor,old_summary,payload=output['result']
        report=checked_report(payload)
        extra=report_dimension_disagreements(report)
        text=render_express_report(report,intent,old_summary)
        if extra:text+='\nPrécontrôle : '+', '.join(extra[:5])
        return {'ui':{'text':[text]},'result':(tensor,text,payload)}


class SmartSVGInstancesV214(SmartSVGInstancesV2132):
    CATEGORY='SmartSVG / 02 GUIDER IA'


class SmartSVGDiagnosticV214(SmartSVGDiagnosticV2132):
    CATEGORY='SmartSVG / 00 VÉRIFIER'
    def run(self):
        response=super().run()
        original,json_payload=response['result']
        try:
            report=checked_report(json_payload)
            summary=gpu_summary(report)
        except (ValueError, TypeError):
            summary=original
        return {'ui':{'text':[summary]},'result':(summary,json_payload)}


NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(
    OLD,OLD_NAMES,{
      'SmartSVGExpressV214':(SmartSVGExpressV214,'01 · SmartSVG EXPRESS — image vers Cricut'),
      'SmartSVGInstancesV214':(SmartSVGInstancesV214,'02 · SmartSVG GUIDAGE IA — sujets distincts'),
      'SmartSVGDiagnosticV214':(SmartSVGDiagnosticV214,'00 · SmartSVG DIAGNOSTIC — installation'),
    })
