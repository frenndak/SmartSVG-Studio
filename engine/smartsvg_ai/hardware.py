"""Non-inferential status adapter for the existing RMBG/GPU diagnostic."""
from __future__ import annotations

def diagnostic_report(registry=None, torch_module=None):
    # Pure lazy wrapper: loading this module does not import models or weights.
    from ..diagnostic_v2132 import diagnostics
    return diagnostics(registry,torch_module)


def summary(report):
    name=report.get('gpu_nom') or 'non identifié'
    return (f'SmartSVG V21.4 — installation uniquement\n'
            f'GPU : {report.get("cuda", "NON_VERIFIE")} • {name}\n'
            f'Florence-2 : {report.get("florence_noeud", "ABSENT")}\n'
            f'SAM2 : {report.get("sam2_noeud", "ABSENT")}\n'
            'Aucun modèle n’est exécuté par ce diagnostic ; aucune découpe certifiée.')
