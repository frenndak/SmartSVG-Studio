"""V21.13.2: accurate, explicitly qualified vector preview; legacy IDs preserved."""
from __future__ import annotations
import json
from .node_v21131 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .node_v21131 import SmartSVGEditableColorsV21131
from .smartsvg_compat.registry import merge_registry

class SmartSVGEditableColorsV21132(SmartSVGEditableColorsV21131):
    CATEGORY='SmartSVG / 03 VECTORISER'
    def run(self,image,couleurs=8,largeur_mm=40.,dossier_sortie='',masque_sujet=None):
        result=super().run(image,couleurs,largeur_mm,dossier_sortie,masque_sujet)
        comparison,preview,path,raw=result['result']
        report=json.loads(raw)
        quality=report['comparaison_v21131']
        io=quality['iou_silhouette_approx']
        exact=quality['rendu_standard_verifie']
        verdict=quality['diagnostic']
        report['revision_diagnostic']='21.13.2'
        report['source_du_score']='CairoSVG (rendu SVG standard)' if exact else 'OpenCV (estimation conservative)'
        report['diagnostic_fidelite']=verdict
        report['utilisable_comme_png_print_then_cut']=False
        report['svg_multicouche_decoupe_physique_certifiee']=False
        status=(f'Comparaison SVG : IoU silhouette {io*100:.1f}% · '
                f'{"rendu SVG standard" if exact else "estimation OpenCV seulement"} · '
                f'{verdict}. SVG multicouche EXPÉRIMENTAL ; vérifier Inkscape/Cricut.')
        result['result']=(comparison,preview,path,json.dumps(report,ensure_ascii=False,allow_nan=False))
        if isinstance(result.get('ui'),dict):result['ui']['text']=[status]
        return result

NODE_CLASS_MAPPINGS,NODE_DISPLAY_NAME_MAPPINGS=merge_registry(OLD,OLD_NAMES,{
    'SmartSVGEditableColorsV21132':(SmartSVGEditableColorsV21132,
        '03 · SVG couleurs éditables + fidélité vérifiée (V21.13.2)'),
})
