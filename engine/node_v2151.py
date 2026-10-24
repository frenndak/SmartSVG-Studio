"""V21.5.1: entirely optional UI layer; fabrication engine remains V21.4."""
from __future__ import annotations
from .node_v214 import (SmartSVGExpressV214, SmartSVGInstancesV214, SmartSVGDiagnosticV214)
from .node_v215 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .smartsvg_core.reporting import checked_report
from .smartsvg_ui.presentation import build_presentation
from .smartsvg_ui.preview_bridge_v2151 import publish_previews
from .smartsvg_compat.registry import merge_registry


def _comfy_output_directory():
    try:
        import folder_paths
        return folder_paths.get_output_directory()
    except (ImportError,AttributeError,RuntimeError):
        return None


class SmartSVGExpressV2151(SmartSVGExpressV214):
    """Independent visual wrapper, preserving all three return ports and input choices."""
    CATEGORY='SmartSVG / 01 CRÉER'
    def run(self,image,dossier_sortie='',projet='Auto - conserver le visuel',
            largeur_mm=40.,qualite_ppp='300',ia_locale='Desactivee',masques_objets=None):
        response=super().run(image=image,dossier_sortie=dossier_sortie,projet=projet,
                             largeur_mm=largeur_mm,qualite_ppp=qualite_ppp,
                             ia_locale=ia_locale,masques_objets=masques_objets)
        tensor,summary,raw=response['result']
        try:
            report=checked_report(raw)
            model=build_presentation(report,mask_external=(masques_objets is not None),
                                     ai_mode=ia_locale)
        except Exception:
            # Once fabrication succeeds, an optional dashboard must never
            # mark the whole job as failed. The full JSON remains accessible.
            response['ui']={'text':[summary+'\nPanneau graphique indisponible; exports non modifies.'],
                            'smartsvg':[],'smartsvg_previews':[]}
            return response
        try:
            previews=publish_previews(report,_comfy_output_directory())
        except Exception:
            # Malformed Pillow images / output directory / anything UI-only:
            # always preserve the fabrication result and its backend report.
            previews=[]
        response['ui']={'text':[summary], 'smartsvg':[model], 'smartsvg_previews':previews}
        return response


class SmartSVGInstancesV2151(SmartSVGInstancesV214):
    CATEGORY='SmartSVG / 02 GUIDAGE IA'


class SmartSVGDiagnosticV2151(SmartSVGDiagnosticV214):
    CATEGORY='SmartSVG / 00 DIAGNOSTIC'


NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
 'SmartSVGExpressV2151':(SmartSVGExpressV2151,'01 · SmartSVG EXPRESS V21.5.1 — atelier Cricut'),
 'SmartSVGInstancesV2151':(SmartSVGInstancesV2151,'02 · SmartSVG GUIDAGE IA V21.5.1'),
 'SmartSVGDiagnosticV2151':(SmartSVGDiagnosticV2151,'00 · SmartSVG DIAGNOSTIC V21.5.1'),
})
