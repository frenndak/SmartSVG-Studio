"""V21.15.4 additive subject inspector; no changed legacy ComfyUI node ports."""
from __future__ import annotations

import numpy as np
import torch

from .node_v21152 import NODE_CLASS_MAPPINGS as OLD, NODE_DISPLAY_NAME_MAPPINGS as OLD_NAMES
from .node_v21131 import SmartSVGChooseSubjectV21131
from .smartsvg_core.subject_inspector_v21154 import (
    inspect_subject_masks, SubjectInspectionUnavailable,
)
from .smartsvg_compat.registry import merge_registry
from .smartsvg_editor.strokes import edit_fingerprint


class SmartSVGChooseSubjectV21154(SmartSVGChooseSubjectV21131):
    """Use existing mask-selection semantics; annotate optional thumbnail UI."""
    CATEGORY = 'SmartSVG / 01 CRÉER'

    def run(self, image, masques_objets, numero_sujet=1):
        response = super().run(image, masques_objets, numero_sujet)
        try:
            if not isinstance(masques_objets, torch.Tensor):
                raise SubjectInspectionUnavailable('Masques tensoriels attendus')
            raw = masques_objets.detach().float().cpu().numpy()
            # Base selector validated the dimensions and selected mask already.
            reports = inspect_subject_masks(raw, expected_shape=tuple(image.shape[1:3]))
            preview = response['ui'].get('smartsvg_subjects_v21131') or []
            previews = {item['numero']: item['image_data'] for item in preview[0].get('sujets', [])} if preview else {}
            source_sha = edit_fingerprint(image[0].detach().float().cpu().numpy(), raw)
            items = [{**item, 'image_data': previews.get(item['numero'])} for item in reports]
            response['ui']['smartsvg_subjects_v21154'] = [{
                'selection': int(numero_sujet), 'sujets': items,
                'source_sha256': source_sha, 'width_px': int(image.shape[2]),
                'height_px': int(image.shape[1]), 'count': len(items),
                'modifications_automatiques': False,
                'decoupe_certifiee': False,
                'clic_ne_fabrique_pas': True,
            }]
            flagged = sum(bool(item['codes']) for item in items)
            response['ui']['text'].append(
                f'Inspection : {flagged}/{len(items)} masque(s) avec points à vérifier. '
                'Aucun fragment supprimé ; relancer après sélection ou correction.')
        except (SubjectInspectionUnavailable, ValueError, TypeError, RuntimeError, MemoryError) as exc:
            response['ui']['text'].append(
                'Inspection des sujets indisponible ; la sélection historique reste inchangée : '
                + str(exc)[:140])
        return response


NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS = merge_registry(OLD, OLD_NAMES, {
    'SmartSVGChooseSubjectV21154': (
        SmartSVGChooseSubjectV21154,
        '01 · Inspecter et choisir les silhouettes (V21.15.4)'),
})
