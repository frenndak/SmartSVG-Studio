"""V34-126: deterministic, in-memory CUT/SCORE geometry for two paper templates.

Nominal millimetres only. This module never writes .smartsvg, exports a file,
assigns Design Space operations, or claims machine/material compatibility.
"""
from __future__ import annotations

import math


class TemplateGeometryError(ValueError):
    """Invalid user-provided dimensions or non-finite derived geometry."""


def _positive_mm(value, label):
    if type(value) not in (int, float):
        raise TemplateGeometryError(f"INVALID_TEMPLATE_DIMENSION: {label}")
    try:
        finite = math.isfinite(value)
    except (OverflowError, ValueError):
        finite = False
    if not finite or value <= 0:
        raise TemplateGeometryError(f"INVALID_TEMPLATE_DIMENSION: {label}")
    return value


def _checked_bounds(width, height):
    try:
        finite = math.isfinite(width) and math.isfinite(height)
    except (OverflowError, ValueError):
        finite = False
    if not finite:
        raise TemplateGeometryError("INVALID_TEMPLATE_DIMENSION: derived bounds")
    return [0, 0, width, height]


def _proposal(template_id, parameters, bbox, outer, slits, folds, area):
    try:
        finite = math.isfinite(area)
    except (OverflowError, ValueError):
        finite = False
    if not finite or area <= 0:
        raise TemplateGeometryError("INVALID_TEMPLATE_DIMENSION: derived area")
    paths = [{"id": "cut-outer", "operation": "CUT", "closed": True,
              "points_mm": outer}]
    paths.extend({"id": f"cut-slit-{i}", "operation": "CUT", "closed": False,
                  "points_mm": segment} for i, segment in enumerate(slits, 1))
    paths.extend({"id": f"score-fold-{i}", "operation": "SCORE", "closed": False,
                  "points_mm": segment} for i, segment in enumerate(folds, 1))
    return {
        "schema": "smartsvg-template-preview/1-draft", "template_id": template_id,
        "units": "mm", "parameters": parameters,
        "geometry": {"bbox_mm": bbox, "cut_outer": outer,
                     "cut_slits": slits, "score_folds": folds,
                     "area_mm2": area, "paths": paths},
        "handoff": {"requires_manual_score_assignment": True,
                    "requires_manual_attach": True,
                    "machine_material_qualification": "UNKNOWN",
                    "design_space_import": "NON_EXECUTE",
                    "physical_validation": "NON_EXECUTE"},
        "persisted": False,
    }


def folded_card(width_mm, height_mm):
    """Card folded in half: flat dimensions 2*width x height, one SCORE."""
    w = _positive_mm(width_mm, "width_mm")
    h = _positive_mm(height_mm, "height_mm")
    bbox = _checked_bounds(2 * w, h)
    outer = [[0, 0], [2*w, 0], [2*w, h], [0, h], [0, 0]]
    return _proposal("folded-card", {"width_mm": w, "height_mm": h},
                     bbox, outer, [], [[[w, 0], [w, h]]], 2*w*h)


def open_tray(base_width_mm, base_depth_mm, wall_height_mm, tab_width_mm):
    """Open tray with four explicit CUT slits and eight unassigned SCORE folds."""
    w = _positive_mm(base_width_mm, "base_width_mm")
    d = _positive_mm(base_depth_mm, "base_depth_mm")
    h = _positive_mm(wall_height_mm, "wall_height_mm")
    t = _positive_mm(tab_width_mm, "tab_width_mm")
    if t >= h:
        raise TemplateGeometryError("INVALID_TEMPLATE_DIMENSION: tab_width_mm >= wall_height_mm")
    x1, x2, x3, x4 = h-t, h, h+w, h+w+t
    y1, y2, y3 = h, h+d, 2*h+d
    bbox = _checked_bounds(w+2*h, d+2*h)
    outer = [[x1, 0], [x4, 0], [x4, y1], [w+2*h, y1],
             [w+2*h, y2], [x4, y2], [x4, y3], [x1, y3],
             [x1, y2], [0, y2], [0, y1], [x1, y1], [x1, 0]]
    slits = [ [[x1, y1], [x2, y1]], [[x3, y1], [x4, y1]],
              [[x1, y2], [x2, y2]], [[x3, y2], [x4, y2]] ]
    folds = [ [[x2, y1], [x3, y1]], [[x2, y2], [x3, y2]],
              [[x2, y1], [x2, y2]], [[x3, y1], [x3, y2]],
              [[x2, 0], [x2, y1]], [[x3, 0], [x3, y1]],
              [[x2, y2], [x2, y3]], [[x3, y2], [x3, y3]] ]
    return _proposal("open-tray-glue-tabs",
                     {"base_width_mm": w, "base_depth_mm": d,
                      "wall_height_mm": h, "tab_width_mm": t},
                     bbox, outer, slits, folds,
                     w*d + 2*h*(w+d) + 4*t*h)
