"""V21.7.1: full automatic conservative PNG HD, historical five Express controls intact."""
from __future__ import annotations
import json
from .node_v217 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .node_v2151 import SmartSVGExpressV2151
from .smartsvg_quality.auto_hd import automatic_hd
from .smartsvg_compat.registry import merge_registry


class SmartSVGExpressV2171(SmartSVGExpressV2151):
    CATEGORY = 'SmartSVG / 01 CRÉER'

    def run(self, image, dossier_sortie='', projet='Auto - conserver le visuel',
            largeur_mm=40., qualite_ppp='300', ia_locale='Desactivee', masques_objets=None):
        # Actual fabrication exceptions remain visible. Only optional HD is nonblocking.
        response = super().run(image=image, dossier_sortie=dossier_sortie, projet=projet,
                               largeur_mm=largeur_mm, qualite_ppp=qualite_ppp,
                               ia_locale=ia_locale, masques_objets=masques_objets)
        tensor, summary, raw = response['result']
        try:
            report = json.loads(raw)
            quality = automatic_hd(report, int(qualite_ppp))
            report['amelioration_hd_v2171'] = quality
            raw = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
            note = (f"HD automatique : {quality['produits'] + quality.get('reutilises', 0)}/{quality['total']} PNG vérifié(s)"
                    f" — {quality['statut']} ; {quality.get('reutilises', 0)} réutilisé(s) (original et SVG conservés).")
        except Exception:
            note = 'HD automatique indisponible ; fichiers Cricut originaux conservés.'
        new_summary = summary + '\n' + note
        response['result'] = (tensor, new_summary, raw)
        if isinstance(response.get('ui'), dict):
            response['ui']['text'] = [new_summary]
        return response


NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS = merge_registry(OLD, OLD_NAMES, {
    'SmartSVGExpressV2171': (SmartSVGExpressV2171,
                              '01 · SmartSVG EXPRESS V21.7.1 — HD automatique Cricut'),
})
