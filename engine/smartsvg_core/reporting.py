"""Defensive summaries: never describe model availability as inference proof."""
from __future__ import annotations
import json
from collections.abc import Mapping
from typing import Any
from .contracts import ExpressRequest


def _alerts(value: Any):
    if isinstance(value, Mapping):
        return sum(max(0, int(v)) for v in value.values() if isinstance(v, (int, float)) and v >= 0)
    if isinstance(value, list):
        return len(value)
    return 0


def render_express_report(report: dict, request: ExpressRequest, legacy_summary: str) -> str:
    if not isinstance(report, dict):
        raise ValueError('Rapport SmartSVG non structuré')
    qa=report.get('controle_v212')
    qa=qa if isinstance(qa,dict) else {}
    warning_count=_alerts(qa.get('alertes'))
    exported=report.get('nombre_objets_exportes', 0)
    if not isinstance(exported,int) or exported < 0:
        exported='non vérifié'
    # The exact presence of external MASK input is not proof of a valid segmentation.
    origin = ('Masques externes fournis, résultat à vérifier' if request.external_masks
              else ('IA interne non demandée' if request.ai_mode == 'Desactivee'
                    else 'IA locale demandée : exécution à confirmer dans le rapport'))
    label=(f'SmartSVG V21.4 • {exported} export(s) • {request.width_mm:g} mm • {request.dpi} ppp\n'
           f'Provenance : {origin}\n'
           f'Qualité : {warning_count} alerte(s) connues ; découpe Cricut NON CERTIFIÉE\n'
           'À vérifier dans Design Space : taille, silhouette, type d’opération.')
    dossier=report.get('dossier')
    if isinstance(dossier,str):label+='\nProjet : '+dossier[:300]
    # Do not dump large JSON or old verbose status into the text widget.
    return label+'\n'+str(legacy_summary)[:1200]


def checked_report(payload: str, max_characters: int = 12_000_000) -> dict:
    if not isinstance(payload, str) or len(payload)>max_characters:
        raise ValueError('Rapport SmartSVG absent ou excessif')
    result=json.loads(payload)
    if not isinstance(result,dict):
        raise ValueError('Rapport SmartSVG JSON doit être un objet')
    return result
