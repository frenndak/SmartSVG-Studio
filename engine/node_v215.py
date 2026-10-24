"""V21.5: stable ComfyUI node ports with optional, bounded frontend QA payload."""
from __future__ import annotations
import json
from .node_v214 import (SmartSVGExpressV214,SmartSVGInstancesV214,SmartSVGDiagnosticV214,
                        NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES)
from .smartsvg_core.reporting import checked_report
from .smartsvg_ui.presentation import build_presentation
from .smartsvg_ui.preview_bridge import publish_previews
from .smartsvg_compat.registry import merge_registry


def _comfy_output_directory():
    try:
        import folder_paths
        return folder_paths.get_output_directory()
    except (ImportError,AttributeError,RuntimeError):
        return None


class SmartSVGExpressV215(SmartSVGExpressV214):
    CATEGORY = 'SmartSVG / 01 CRÉER'
    def run(self,image,dossier_sortie='',projet='Auto - conserver le visuel',
            largeur_mm=40.,qualite_ppp='300',ia_locale='Desactivee',masques_objets=None):
        response=super().run(image=image,dossier_sortie=dossier_sortie,projet=projet,
                             largeur_mm=largeur_mm,qualite_ppp=qualite_ppp,
                             ia_locale=ia_locale,masques_objets=masques_objets)
        tensor,summary,raw=response['result']
        report=checked_report(raw)
        overview=build_presentation(report,mask_external=(masques_objets is not None),ai_mode=ia_locale)
        try:
            images=publish_previews(report,_comfy_output_directory())
        except (OSError,ValueError,RuntimeError):
            images=[]  # UI preview must never invalidate published fabrication files
        # JS only needs this small UI payload; existing 3 return ports unchanged.
        response['ui']={'text':[summary], 'smartsvg':[overview], 'smartsvg_previews':images}
        return response


class SmartSVGInstancesV215(SmartSVGInstancesV214):
    CATEGORY='SmartSVG / 02 GUIDAGE IA'


class SmartSVGDiagnosticV215(SmartSVGDiagnosticV214):
    CATEGORY='SmartSVG / 00 DIAGNOSTIC'

NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
 'SmartSVGExpressV215':(SmartSVGExpressV215,'01 · SmartSVG EXPRESS V21.5 — atelier Cricut'),
 'SmartSVGInstancesV215':(SmartSVGInstancesV215,'02 · SmartSVG GUIDAGE IA V21.5'),
 'SmartSVGDiagnosticV215':(SmartSVGDiagnosticV215,'00 · SmartSVG DIAGNOSTIC V21.5'),
})
