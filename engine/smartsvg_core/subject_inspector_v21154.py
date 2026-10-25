"""V21.15.4 advisory per-subject mask diagnostics (CPU, no pixel mutations).

A diagnostic is *not* a quality certification or an inference. This routine
accepts masks supplied by existing nodes and reports potential repair points.
"""
from __future__ import annotations

import numpy as np
import cv2

MAX_MASKS = 32
MAX_SOURCE_PIXELS = 5_000_000
MAX_TOTAL_MASK_PIXELS = 50_000_000


class SubjectInspectionUnavailable(ValueError):
    """Return the old selection without a diagnostic when limits are exceeded."""


def inspect_subject_masks(masks, *, expected_shape=None):
    """Return one immutable-data report per mask in original 1-based order.

    Only a *copy* of one thresholded mask at a time is analyzed. Original float
    masks and small independent fragments are deliberately preserved.
    Bounding coordinates are [x0,y0,x1,y1] with exclusive upper boundaries.
    """
    a = np.asarray(masks)
    if a.ndim == 2:
        a = a[None, ...]
    if a.ndim != 3 or a.dtype.kind not in 'fiu':
        raise SubjectInspectionUnavailable('Masques [N,H,W] numériques requis')
    n, h, w = a.shape
    if (n < 1 or n > MAX_MASKS or h < 1 or w < 1 or h*w > MAX_SOURCE_PIXELS
            or a.size > MAX_TOTAL_MASK_PIXELS or (expected_shape and (h, w) != tuple(expected_shape))):
        raise SubjectInspectionUnavailable('Nombre ou dimensions de masques non pris en charge')
    results = []
    for i in range(n):
        source = a[i]
        if not np.isfinite(source).all() or np.min(source) < 0 or np.max(source) > 1:
            raise SubjectInspectionUnavailable('Masque non fini ou hors plage [0,1]')
        binary = np.ascontiguousarray(source >= 0.5, dtype=np.uint8)
        count, _, stats, _ = cv2.connectedComponentsWithStats(binary, 8)
        regions = stats[1:]
        area = int(binary.sum())
        warnings = []
        if area == 0:
            results.append({'numero': i+1, 'surface_px': 0, 'bbox_source_px': None,
                            'fragments_significatifs': 0, 'micro_fragments': 0,
                            'codes': ['MASQUE_VIDE'], 'etat': 'A_VERIFIER'})
            continue
        x0 = int(regions[:, cv2.CC_STAT_LEFT].min())
        y0 = int(regions[:, cv2.CC_STAT_TOP].min())
        x1 = int((regions[:, cv2.CC_STAT_LEFT]+regions[:, cv2.CC_STAT_WIDTH]).max())
        y1 = int((regions[:, cv2.CC_STAT_TOP]+regions[:, cv2.CC_STAT_HEIGHT]).max())
        significant = int(np.count_nonzero(regions[:, cv2.CC_STAT_AREA] >= 8))
        micro = int(np.count_nonzero(regions[:, cv2.CC_STAT_AREA] < 8))
        if significant > 1:
            warnings.append('FRAGMENTS_DETACHES')
        if micro > 2:
            warnings.append('MICRO_FRAGMENTS')
        if x0 == 0 or y0 == 0 or x1 == w or y1 == h:
            warnings.append('TOUCHE_BORD_IMAGE')
        if area / ((x1-x0)*(y1-y0)) >= 0.985:
            warnings.append('SILHOUETTE_RECTANGULAIRE')
        if area < 50:
            warnings.append('SUJET_TRES_PETIT')
        results.append({'numero': i+1, 'surface_px': area,
                        'bbox_source_px': [x0, y0, x1, y1],
                        'fragments_significatifs': significant,
                        'micro_fragments': micro,
                        'codes': warnings,
                        'etat': 'A_VERIFIER' if warnings else 'INSPECTION_VISUELLE_REQUISE'})
    return results
