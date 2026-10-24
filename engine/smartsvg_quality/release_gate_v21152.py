"""Conservative V21.15.2 quality gate on *published* real exports.

Never equates technical geometry with Cricut physical certification.
Leaves legacy exports available as drafts but marks unsafe usage as BLOCKED.
"""
from __future__ import annotations
import json
from pathlib import Path
from .white_sheet_v21152 import segment_white_grid, SheetUncertain
from ..controle_export_v212 import run_v212
from ..hd_multisticker_v206 import _save_text
from ..smartsvg_governance.artifact_qa import audit_project, QAError


def run_v21152(pixels, destination, profile='auto', width_mm=40, dpi=300,
                operation='sticker_contour', grid='6x4', segmentation='desactiver',
                masks=None,provider=None,gpu=None):
    """Add guarded white-sheet route without changing any old module or node."""
    white=None; reason=None
    allowed=(profile=='planche_multi' and operation=='sticker_contour'
             and masks is None and segmentation!='forcer' and grid in ('4x3','6x4'))
    if allowed:
        try:
            white=segment_white_grid(pixels,cols=4 if grid=='4x3' else 6,
                                           rows=3 if grid=='4x3' else 4)
            masks=white.masks
        except SheetUncertain as exc:
            reason=str(exc)[:180]
    report,preview=run_v212(pixels,destination,profile,width_mm,dpi,operation,grid,
                            segmentation,masks,provider,gpu)
    report['white_sheet_v21152']={
        'mode':('AUTO_MASQUES_HEURISTIQUES' if white is not None else
                'REFUS_AUTO_FOND_BLANC' if reason is not None else 'NON_APPLICABLE'),
        'ia_executee_pour_fond_blanc':False,
        'masques_issus_de_l_image_sans_annotation_humaine':white is not None,
        'cases_verifiees':list(white.diagnostics) if white is not None else [],
        'cause_refus':reason,
        'restauration_moteurs_legacy':True,
    }
    project=Path(report['dossier']).resolve()
    try:
        qa=audit_project(project/'RAPPORT_V21_2.json', requested_intent=operation)
    except (QAError,OSError,ValueError,KeyError) as exc:
        qa={'status':'BLOCKED','blocking_codes':['AUDIT_INDISPONIBLE'],
            'warning_codes':[],'diagnostic':f'{type(exc).__name__}: {str(exc)[:160]}',
            'objects_tested':0,'pages_tested':0}
    report['controle_v21152']={
        'version':'21.15.2','status':qa['status'],
        'blocking_codes':qa.get('blocking_codes',[]),
        'warning_codes':qa.get('warning_codes',[]),
        'fichiers_provisoires_conserves':True,
        'utilisation_decoupe_sans_verification_autorisee':False,
        'validation_import_design_space':False,
        'validation_physique_explore_5':False,
        'action_requise':('NE PAS DÉCOUPER : corriger les masques ou choisir une carte rectangulaire.'
                         if qa['status']=='BLOCKED' else
                         'Vérifier chaque silhouette et la taille dans Design Space avant découpe.'),
        'rapport_detaille':'CONTROLE_V21_15_2.json',
    }
    # QA is an independently inspectable companion, not injected into SVG/PNG.
    _save_text(project/'CONTROLE_V21_15_2.json',json.dumps(qa,ensure_ascii=False,indent=2,allow_nan=False))
    _save_text(project/'RAPPORT_V21_15_2.json',json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False))
    return report,preview
