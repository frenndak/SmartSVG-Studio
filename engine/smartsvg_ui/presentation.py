"""V21.5: bounded, honest UI model for ComfyUI frontend.

Pure functions: safe for CPU tests, require no ComfyUI runtime or browser.
No claim of semantic accuracy, model execution or Cricut certification.
"""
from __future__ import annotations
from pathlib import Path

MAX_OBJECTS = 32
MAX_ALERTS = 6
MAX_UI_TEXT = 280


def _short(value, cap=MAX_UI_TEXT):
    return str(value or '')[:cap]


def _count(alerts):
    if not isinstance(alerts, dict):
        return 0
    return sum(int(v) for v in alerts.values()
               if isinstance(v, int) and not isinstance(v, bool) and v > 0)


def build_presentation(report, *, mask_external=False, ai_mode='Desactivee'):
    """Build a serializable, size-bounded report for browser display.

    Never surface arbitrary full absolute paths, raw masks, or base64 images in UI.
    The detailed JSON output of the node remains independently available.
    """
    if not isinstance(report, dict):
        raise ValueError('SmartSVG: rapport manquant')
    qa = report.get('controle_v212')
    qa = qa if isinstance(qa, dict) else {}
    objects = qa.get('objets') if isinstance(qa.get('objets'),list) else []
    if len(objects) > MAX_OBJECTS:
        objects = objects[:MAX_OBJECTS]
    cards = []
    for index, item in enumerate(objects):
        if not isinstance(item,dict):
            continue
        flags = item.get('avertissements') if isinstance(item.get('avertissements'),list) else []
        mm = item.get('largeur_png_mm_si_ppp_respectes')
        try:
            measured_mm = round(float(mm),2)
            if not 0 < measured_mm <= 5000:
                measured_mm = None
        except (ValueError,TypeError,OverflowError):
            measured_mm = None
        state = item.get('verdict')
        if state not in ('RISQUE_ELEVE','A_VERIFIER'):
            state = 'A_VERIFIER'
        cards.append({
            'numero': index + 1,
            'etat': state,
            'largeur_mm': measured_mm,
            'alertes':[_short(x,120) for x in flags[:MAX_ALERTS]],
            'nombre_alertes':len(flags),
        })
    count = report.get('nombre_objets_exportes')
    if not isinstance(count, int) or isinstance(count,bool) or count<0:
        count = len(cards)
    origin = 'masques externes fournis' if mask_external else (
        'IA interne demandée — résultat à vérifier' if ai_mode != 'Desactivee'
        else 'aucune IA interne demandée')
    model = {
        'version': '21.5-beta',
        'objets_total': min(count,100000),
        'planches_total':len(report.get('planches_cricut') or report.get('planches') or []),
        'alertes_total':_count(qa.get('alertes')),
        'provenance':origin,
        'chemin_sortie':_short(report.get('dossier'),420),
        'objets':cards,
        'controle_qualite_disponible':bool(objects),
        'detourage_semantique_certifie':False,
        'decoupe_cricut_certifiee':False,
        'action_requise':'Vérifier taille, silhouette et opération dans Cricut Design Space.',
    }
    return model
