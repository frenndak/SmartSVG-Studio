"""V21.15.4 advisory per-subject mask diagnostics + focus-zone localization (CPU, no pixel mutations).

A diagnostic is *not* a quality certification or an inference. This routine
accepts masks supplied by existing nodes and reports potential repair points.
"""
from __future__ import annotations

import numpy as np
import cv2

MAX_MASKS = 32
MAX_SOURCE_PIXELS = 5_000_000
MAX_TOTAL_MASK_PIXELS = 50_000_000
MAX_FOCUS_ZONES = 12
MAX_CONNECTED_REGIONS = 20_000


class SubjectInspectionUnavailable(ValueError):
    """Return the old selection without a diagnostic when limits are exceeded."""



def _preview_box(bbox, entire, canvas):
    """Project source exclusive bbox into the 88px V21.13.1 contact-sheet tile.

    Use exactly the historical preview crop, zoom, centering and padding
    equations, without allocating another high-resolution raster.
    """
    height, width = canvas
    ex0, ey0, ex1, ey1 = entire
    bw, bh = ex1 - ex0, ey1 - ey0
    pad = max(3, int(max(bw, bh) * .06))
    cx0, cy0 = max(0, ex0 - pad), max(0, ey0 - pad)
    cx1, cy1 = min(width, ex1 + pad), min(height, ey1 + pad)
    crop_w, crop_h = cx1 - cx0, cy1 - cy0
    ratio = min(84 / crop_w, 84 / crop_h)
    resized_w = max(1, round(crop_w * ratio))
    resized_h = max(1, round(crop_h * ratio))
    offset_x, offset_y = (88 - resized_w) // 2, (88 - resized_h) // 2
    x0, y0, x1, y1 = bbox
    return [
        max(0, min(88, round(offset_x + (x0 - cx0) * resized_w / crop_w))),
        max(0, min(88, round(offset_y + (y0 - cy0) * resized_h / crop_h))),
        max(0, min(88, round(offset_x + (x1 - cx0) * resized_w / crop_w))),
        max(0, min(88, round(offset_y + (y1 - cy0) * resized_h / crop_h))),
    ]


def _focus_zones(regions, entire, canvas):
    """Bounded advisory per-component locations, never destructive edits."""
    if not len(regions):
        return [], 0
    # The largest component is the reference silhouette. Separate accessories
    # remain present and can be intentional, so these are only review markers.
    primary = int(np.argmax(regions[:, cv2.CC_STAT_AREA]))
    zones = []
    for idx, info in enumerate(regions):
        if idx == primary:
            continue
        x, y, bw, bh, count = (int(v) for v in info)
        bbox = [x, y, x + bw, y + bh]
        zones.append({
            'type': 'MICRO_FRAGMENT' if count < 8 else 'FRAGMENT_SEPARE',
            'surface_px': count,
            'bbox_source_px': bbox,
            'bbox_apercu_88px': _preview_box(bbox, entire, canvas),
        })
    # Stable priority: major separate shapes first, then micro-fragments.
    zones.sort(key=lambda z: (z['type'] == 'MICRO_FRAGMENT', -z['surface_px'],
                              z['bbox_source_px'][1], z['bbox_source_px'][0]))
    return zones[:MAX_FOCUS_ZONES], max(0, len(zones) - MAX_FOCUS_ZONES)

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
        if len(regions) > MAX_CONNECTED_REGIONS:
            raise SubjectInspectionUnavailable('Trop de fragments pour une inspection CPU sûre')
        area = int(binary.sum())
        warnings = []
        if area == 0:
            results.append({'numero': i+1, 'surface_px': 0, 'bbox_source_px': None,
                            'fragments_significatifs': 0, 'micro_fragments': 0, 'zones_a_examiner': [],
                            'zones_non_affichees': 0, 'bords_touches': [],
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
        touched = ([side for side, hit in (('GAUCHE', x0 == 0),
                                           ('HAUT', y0 == 0),
                                           ('DROITE', x1 == w),
                                           ('BAS', y1 == h)) if hit])
        if touched:
            warnings.append('TOUCHE_BORD_IMAGE')
        if area / ((x1-x0)*(y1-y0)) >= 0.985:
            warnings.append('SILHOUETTE_RECTANGULAIRE')
        if area < 50:
            warnings.append('SUJET_TRES_PETIT')
        zones, hidden = _focus_zones(regions, [x0, y0, x1, y1], (h, w))
        results.append({'numero': i+1, 'surface_px': area,
                        'zones_a_examiner': zones, 'zones_non_affichees': hidden,
                        'bords_touches': touched,
                        'bbox_source_px': [x0, y0, x1, y1],
                        'fragments_significatifs': significant,
                        'micro_fragments': micro,
                        'codes': warnings,
                        'etat': 'A_VERIFIER' if warnings else 'INSPECTION_VISUELLE_REQUISE'})
    return results
