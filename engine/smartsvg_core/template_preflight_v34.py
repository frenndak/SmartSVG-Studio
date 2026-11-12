"""V34-127: fail-closed static preflight for approved template proposals.

This checks only deterministic geometry and the draft handoff contract. It never
writes an SVG, assigns Design Space operations or qualifies a material, tool,
machine, import or physical cut.
"""
from __future__ import annotations

import math
import re

from smartsvg_core.template_geometry_v34 import folded_card, open_tray


MAX_TEMPLATE_POINTS = 256
MAX_POINTS_PER_PATH = 64


class _Invalid(ValueError):
    def __init__(self, code, path_ids=()):
        super().__init__(code)
        self.code = code
        self.path_ids = tuple(dict.fromkeys(path_ids))


def _fail(code, *path_ids):
    raise _Invalid(code, path_ids)


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _point(value, path_id):
    if (not isinstance(value, list) or len(value) != 2
            or not all(_number(coordinate) for coordinate in value)):
        _fail('TEMPLATE_CONTRACT_INVALID', path_id)
    return tuple(value)


def _same(a, b, tolerance=1e-9):
    return abs(a[0] - b[0]) <= tolerance and abs(a[1] - b[1]) <= tolerance


def _cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def _on_segment(point, start, end, tolerance):
    return (abs(_cross(start, end, point)) <= tolerance
            and min(start[0], end[0])-tolerance <= point[0] <= max(start[0], end[0])+tolerance
            and min(start[1], end[1])-tolerance <= point[1] <= max(start[1], end[1])+tolerance)


def _unexpected_intersection(first, second, tolerance):
    a, b = first
    c, d = second
    turns = (_cross(a, b, c), _cross(a, b, d), _cross(c, d, a), _cross(c, d, b))
    if ((turns[0] > tolerance and turns[1] < -tolerance
         or turns[0] < -tolerance and turns[1] > tolerance)
            and (turns[2] > tolerance and turns[3] < -tolerance
                 or turns[2] < -tolerance and turns[3] > tolerance)):
        return True
    contacts = []
    for point, start, end in ((a, c, d), (b, c, d), (c, a, b), (d, a, b)):
        if _on_segment(point, start, end, tolerance):
            contacts.append(point)
    if not contacts:
        return False
    # Approved templates intentionally terminate folds/slits on longer
    # contour or fold segments. Proper crossings were rejected above; only
    # collinear overlap remains unexpected here.
    collinear = all(abs(turn) <= tolerance for turn in turns)
    return collinear and any(
        not ((_same(point, a) or _same(point, b))
             and (_same(point, c) or _same(point, d)))
        for point in contacts)


def _blocked(code, path_ids=()):
    return {
        'schema': 'smartsvg-template-preflight/1',
        'status': 'BLOCKED',
        'blocking_codes': [code],
        'warning_codes': [],
        'path_ids': list(path_ids),
        'static_geometry_verified': False,
        'external_validation': {
            'design_space_import': 'NOT_TESTED',
            'physical_cut': 'NOT_TESTED',
            'machine_material': 'UNKNOWN',
        },
        'scope': 'STATIC_TEMPLATE_GEOMETRY_NOT_MACHINE_QUALIFICATION',
    }


def preflight_template(proposal, usable_sheet_mm=None):
    """Validate one generated draft and optional user-declared usable sheet.

    No automatic rotation, machine capability, material or cutting claim.
    """
    try:
        if not isinstance(proposal, dict):
            _fail('TEMPLATE_CONTRACT_INVALID')
        if (proposal.get('schema') != 'smartsvg-template-preview/1-draft'
                or proposal.get('units') != 'mm'
                or proposal.get('persisted') is not False):
            _fail('TEMPLATE_CONTRACT_INVALID')
        handoff = proposal.get('handoff')
        if (not isinstance(handoff, dict)
                or handoff.get('requires_manual_score_assignment') is not True
                or handoff.get('requires_manual_attach') is not True
                or handoff.get('machine_material_qualification') != 'UNKNOWN'
                or handoff.get('design_space_import') != 'NON_EXECUTE'
                or handoff.get('physical_validation') != 'NON_EXECUTE'):
            _fail('TEMPLATE_CONTRACT_INVALID')

        geometry = proposal.get('geometry')
        if not isinstance(geometry, dict):
            _fail('TEMPLATE_CONTRACT_INVALID')
        bbox = geometry.get('bbox_mm')
        if (not isinstance(bbox, list) or len(bbox) != 4
                or not all(_number(value) for value in bbox)
                or bbox[2] <= 0 or bbox[3] <= 0):
            _fail('TEMPLATE_BOUNDS_INVALID')
        left, top, width, height = bbox
        right, bottom = left + width, top + height
        if not all(math.isfinite(value) for value in (right, bottom)):
            _fail('TEMPLATE_BOUNDS_INVALID')

        paths = geometry.get('paths')
        if not isinstance(paths, list) or not 1 <= len(paths) <= 64:
            _fail('TEMPLATE_CONTRACT_INVALID')
        expected_counts = {
            'folded-card': (1, 1),
            'open-tray-glue-tabs': (5, 8),
        }.get(proposal.get('template_id'))
        if expected_counts is None:
            _fail('TEMPLATE_CONTRACT_INVALID')
        parameters = proposal.get('parameters')
        if not isinstance(parameters, dict):
            _fail('TEMPLATE_CONTRACT_INVALID')
        try:
            if proposal['template_id'] == 'folded-card':
                canonical = folded_card(parameters['width_mm'], parameters['height_mm'])
            else:
                canonical = open_tray(
                    parameters['base_width_mm'], parameters['base_depth_mm'],
                    parameters['wall_height_mm'], parameters['tab_width_mm'])
        except (KeyError, TypeError, ValueError, OverflowError):
            _fail('TEMPLATE_CONTRACT_INVALID')
        if parameters != canonical['parameters']:
            _fail('TEMPLATE_CONTRACT_INVALID')
        if bbox != canonical['geometry']['bbox_mm']:
            _fail('TEMPLATE_BOUNDS_INVALID')

        catalogue = [('cut-outer', 'CUT', True, geometry.get('cut_outer'))]
        slits, folds = geometry.get('cut_slits'), geometry.get('score_folds')
        if not isinstance(slits, list) or not isinstance(folds, list):
            _fail('TEMPLATE_CONTRACT_INVALID')
        expected_catalogue_counts = ((0, 1) if proposal['template_id'] == 'folded-card'
                                     else (4, 8))
        if (len(slits), len(folds)) != expected_catalogue_counts:
            _fail('TEMPLATE_CONTRACT_INVALID')
        catalogue += [(f'cut-slit-{index}', 'CUT', False, points)
                      for index, points in enumerate(slits, 1)]
        catalogue += [(f'score-fold-{index}', 'SCORE', False, points)
                      for index, points in enumerate(folds, 1)]
        if len(paths) != len(catalogue):
            _fail('TEMPLATE_TOPOLOGY_INVALID')

        ids, parsed, segments = set(), [], []
        total_points = 0
        for path, (expected_id, expected_operation, expected_closed, expected_points) in zip(paths, catalogue):
            if not isinstance(path, dict):
                _fail('TEMPLATE_CONTRACT_INVALID')
            path_id = path.get('id')
            if (not isinstance(path_id, str)
                    or not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', path_id)
                    or path_id in ids):
                _fail('TEMPLATE_TOPOLOGY_INVALID', str(path_id))
            ids.add(path_id)
            raw_points = path.get('points_mm')
            if (not isinstance(raw_points, list)
                    or not 2 <= len(raw_points) <= MAX_POINTS_PER_PATH):
                _fail('TEMPLATE_CONTRACT_INVALID', path_id)
            total_points += len(raw_points)
            if total_points > MAX_TEMPLATE_POINTS:
                _fail('TEMPLATE_CONTRACT_INVALID', path_id)
            if (path_id != expected_id or path.get('operation') != expected_operation
                    or path.get('closed') is not expected_closed
                    or raw_points != expected_points):
                _fail('TEMPLATE_TOPOLOGY_INVALID', path_id)
            points = [_point(point, path_id) for point in raw_points]
            if expected_closed != _same(points[0], points[-1]):
                _fail('TEMPLATE_TOPOLOGY_INVALID', path_id)
            for point in points:
                if not (left <= point[0] <= right and top <= point[1] <= bottom):
                    _fail('TEMPLATE_BOUNDS_INVALID', path_id)
            for index, (start, end) in enumerate(zip(points, points[1:])):
                if _same(start, end):
                    _fail('TEMPLATE_TOPOLOGY_INVALID', path_id)
                segments.append((path_id, index, len(points)-1, start, end))
            parsed.append((path_id, expected_operation, points))

        for path, expected_path in zip(paths, canonical['geometry']['paths']):
            if path != expected_path:
                _fail('TEMPLATE_TOPOLOGY_INVALID', path['id'])
        if geometry.get('area_mm2') != canonical['geometry']['area_mm2']:
            _fail('TEMPLATE_TOPOLOGY_INVALID', 'cut-outer')

        counts = (sum(operation == 'CUT' for _, operation, _ in parsed),
                  sum(operation == 'SCORE' for _, operation, _ in parsed))
        if counts != expected_counts:
            _fail('TEMPLATE_TOPOLOGY_INVALID')

        all_points = [point for _, _, points in parsed for point in points]
        actual = (min(p[0] for p in all_points), min(p[1] for p in all_points),
                  max(p[0] for p in all_points), max(p[1] for p in all_points))
        tolerance = max(1.0, width, height) * 1e-9
        if any(abs(a-b) > tolerance for a, b in
               zip(actual, (left, top, right, bottom))):
            _fail('TEMPLATE_BOUNDS_INVALID')

        seen = {}
        for path_id, index, _count, start, end in segments:
            key = tuple(sorted((start, end)))
            if key in seen:
                _fail('TEMPLATE_TOPOLOGY_INVALID', seen[key], path_id)
            seen[key] = path_id
        for position, first in enumerate(segments):
            first_id, first_index, first_count, a, b = first
            for second in segments[position+1:]:
                second_id, second_index, second_count, c, d = second
                if first_id == second_id:
                    adjacent = abs(first_index-second_index) == 1
                    closing = {first_index, second_index} == {0, first_count-1}
                    if adjacent or closing:
                        continue
                if _unexpected_intersection((a, b), (c, d), tolerance):
                    _fail('TEMPLATE_TOPOLOGY_INVALID', first_id, second_id)
                if first_id == second_id and any(
                        _same(p, q) for p in (a, b) for q in (c, d)):
                    _fail('TEMPLATE_TOPOLOGY_INVALID', first_id)

        outer = parsed[0][2]
        area = abs(sum(a[0]*b[1]-b[0]*a[1]
                       for a, b in zip(outer, outer[1:]))) / 2
        declared = geometry.get('area_mm2')
        if (not _number(declared) or declared <= 0
                or abs(area-declared) > max(1.0, area)*1e-9):
            _fail('TEMPLATE_TOPOLOGY_INVALID', 'cut-outer')
    except _Invalid as error:
        return _blocked(error.code, error.path_ids)
    except (ArithmeticError, KeyError, TypeError, ValueError):
        return _blocked('TEMPLATE_CONTRACT_INVALID')

    # A declared usable area is not a machine-specific cuttable area.
    if usable_sheet_mm is not None:
        try:
            valid_sheet = (type(usable_sheet_mm) in (tuple, list)
                           and len(usable_sheet_mm) == 2
                           and all(type(v) in (int, float) and
                                   math.isfinite(v) and v > 0
                                   for v in usable_sheet_mm))
        except (OverflowError, ValueError, TypeError):
            valid_sheet = False
        if not valid_sheet:
            invalid = _blocked('TEMPLATE_SHEET_INVALID')
            invalid.update(static_geometry_verified=True, bbox_mm=list(bbox))
            return invalid
        sheet_width, sheet_height = usable_sheet_mm
        if width > sheet_width or height > sheet_height:
            blocked = _blocked('TEMPLATE_BOUNDS_EXCEEDED')
            blocked.update(
                static_geometry_verified=True, bbox_mm=list(bbox),
                declared_usable_sheet_mm=[sheet_width, sheet_height],
                fits_declared_sheet=False)
            return blocked

    result = {
        'schema': 'smartsvg-template-preflight/1',
        'status': 'REVIEW_REQUIRED',
        'blocking_codes': [],
        'warning_codes': ['CAPABILITY_UNKNOWN'],
        'path_ids': [],
        'static_geometry_verified': True,
        'paths_checked': len(paths),
        'cut_paths': counts[0],
        'score_paths': counts[1],
        'bbox_mm': list(bbox),
        'external_validation': {
            'design_space_import': 'NOT_TESTED',
            'physical_cut': 'NOT_TESTED',
            'machine_material': 'UNKNOWN',
        },
        'scope': 'STATIC_TEMPLATE_GEOMETRY_NOT_MACHINE_QUALIFICATION',
    }
    if usable_sheet_mm is not None:
        result['declared_usable_sheet_mm'] = [sheet_width, sheet_height]
        result['fits_declared_sheet'] = True
    return result
