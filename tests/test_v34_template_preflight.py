"""V34-127 / T-V34-16-02,05,06: static template preflight."""
import copy
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'engine'
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))
GEOMETRY = ROOT / 'engine/smartsvg_core/template_geometry_v34.py'
PREFLIGHT = ROOT / 'engine/smartsvg_core/template_preflight_v34.py'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


templates = load('template_geometry_for_preflight', GEOMETRY)
preflight = load('template_preflight_v34', PREFLIGHT)


class TemplatePreflightTests(unittest.TestCase):
    def test_reference_templates_require_review_without_machine_claim(self):
        cases = (
            (templates.open_tray(80, 50, 30, 10), (13, 5, 8, [0, 0, 140, 110])),
            (templates.folded_card(105, 148), (2, 1, 1, [0, 0, 210, 148])),
        )
        for proposal, expected in cases:
            with self.subTest(template=proposal['template_id']):
                result = preflight.preflight_template(proposal)
                self.assertEqual(result['status'], 'REVIEW_REQUIRED')
                self.assertTrue(result['static_geometry_verified'])
                self.assertEqual(
                    (result['paths_checked'], result['cut_paths'],
                     result['score_paths'], result['bbox_mm']), expected)
                self.assertEqual(result['warning_codes'], ['CAPABILITY_UNKNOWN'])
                self.assertEqual(result['external_validation'], {
                    'design_space_import': 'NOT_TESTED',
                    'physical_cut': 'NOT_TESTED',
                    'machine_material': 'UNKNOWN',
                })

    def test_preflight_is_repeatable_and_does_not_mutate_draft(self):
        proposal = templates.open_tray(80, 50, 30, 10)
        before = copy.deepcopy(proposal)
        first = preflight.preflight_template(proposal)
        second = preflight.preflight_template(proposal)
        self.assertEqual(first, second)
        self.assertEqual(proposal, before)
        self.assertFalse(proposal['persisted'])

    def test_duplicate_segment_blocks_with_localized_paths(self):
        proposal = templates.open_tray(80, 50, 30, 10)
        proposal['geometry']['cut_slits'][1] = copy.deepcopy(
            proposal['geometry']['cut_slits'][0])
        proposal['geometry']['paths'][2]['points_mm'] = copy.deepcopy(
            proposal['geometry']['cut_slits'][0])
        result = preflight.preflight_template(proposal)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(result['blocking_codes'], ['TEMPLATE_TOPOLOGY_INVALID'])
        self.assertEqual(result['path_ids'], ['cut-slit-2'])

    def test_interior_crossing_blocks_but_intentional_endpoints_pass(self):
        proposal = templates.folded_card(105, 148)
        # The normal SCORE endpoints touch the outer contour and remain valid.
        self.assertEqual(preflight.preflight_template(proposal)['status'], 'REVIEW_REQUIRED')
        proposal['geometry']['score_folds'][0] = [[0, 74], [210, 74]]
        proposal['geometry']['paths'][1]['points_mm'] = [[0, 74], [210, 74]]
        result = preflight.preflight_template(proposal)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(result['path_ids'], ['score-fold-1'])

    def test_out_of_bounds_and_mismatched_catalogue_fail_closed(self):
        proposal = templates.folded_card(105, 148)
        proposal['geometry']['bbox_mm'][2] = 209
        self.assertEqual(
            preflight.preflight_template(proposal)['blocking_codes'],
            ['TEMPLATE_BOUNDS_INVALID'])
        proposal = templates.folded_card(105, 148)
        proposal['geometry']['paths'][1]['operation'] = 'CUT'
        self.assertEqual(
            preflight.preflight_template(proposal)['blocking_codes'],
            ['TEMPLATE_TOPOLOGY_INVALID'])

    def test_oversized_public_catalogues_fail_before_topology_work(self):
        proposal = templates.open_tray(80, 50, 30, 10)
        oversized = [[index, 0] for index in range(65)]
        proposal['geometry']['cut_outer'] = oversized
        proposal['geometry']['paths'][0]['points_mm'] = copy.deepcopy(oversized)
        result = preflight.preflight_template(proposal)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(result['blocking_codes'], ['TEMPLATE_CONTRACT_INVALID'])
        self.assertEqual(result['path_ids'], ['cut-outer'])

        proposal = templates.open_tray(80, 50, 30, 10)
        proposal['geometry']['cut_slits'] = proposal['geometry']['cut_slits'] * 1000
        result = preflight.preflight_template(proposal)
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertEqual(result['blocking_codes'], ['TEMPLATE_CONTRACT_INVALID'])

    def test_malformed_public_inputs_never_raise_or_gain_capability(self):
        bad = (None, [], {}, {'schema': 'smartsvg-template-preview/1-draft'})
        for value in bad:
            with self.subTest(value=value):
                result = preflight.preflight_template(value)
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertFalse(result['static_geometry_verified'])
                self.assertNotIn('CAPABILITY_UNKNOWN', result['warning_codes'])
                self.assertEqual(result['external_validation']['physical_cut'], 'NOT_TESTED')

    def test_declared_usable_sheet_fit_preserves_geometry_and_honest_scope(self):
        proposal = templates.open_tray(80, 50, 30, 10)
        original = copy.deepcopy(proposal)
        result = preflight.preflight_template(proposal, usable_sheet_mm=(140, 110))
        self.assertEqual(result['status'], 'REVIEW_REQUIRED')
        self.assertTrue(result['static_geometry_verified'])
        self.assertTrue(result['fits_declared_sheet'])
        self.assertEqual(result['declared_usable_sheet_mm'], [140, 110])
        self.assertEqual(result['external_validation']['physical_cut'], 'NOT_TESTED')
        self.assertEqual(proposal, original)
        self.assertNotIn('fits_declared_sheet', preflight.preflight_template(proposal))

    def test_sheet_smaller_than_developed_bbox_blocks_in_declared_orientation(self):
        proposal = templates.folded_card(105, 148)
        for sheet in ((209, 148), (210, 147), (148, 210)):
            with self.subTest(sheet=sheet):
                blocked = preflight.preflight_template(proposal, usable_sheet_mm=sheet)
                self.assertEqual(blocked['status'], 'BLOCKED')
                self.assertEqual(blocked['blocking_codes'], ['TEMPLATE_BOUNDS_EXCEEDED'])
                self.assertTrue(blocked['static_geometry_verified'])
                self.assertFalse(blocked['fits_declared_sheet'])
                self.assertEqual(blocked['bbox_mm'], [0, 0, 210, 148])
                self.assertEqual(blocked['external_validation']['design_space_import'], 'NOT_TESTED')
        self.assertEqual(
            preflight.preflight_template(proposal, usable_sheet_mm=(210, 148))['status'],
            'REVIEW_REQUIRED')

    def test_invalid_sheet_is_blocked_without_mutating_canonical_geometry(self):
        proposal = templates.open_tray(80, 50, 30, 10)
        original = copy.deepcopy(proposal)
        bad_sheets = ([], [140], [140, 110, 1], [0, 110], [-1, 110],
                      [float('nan'), 110], [float('inf'), 110],
                      [True, 110], ['140', 110], [10**400, 110], {})
        for sheet in bad_sheets:
            with self.subTest(sheet=str(sheet)[:35]):
                result = preflight.preflight_template(proposal, usable_sheet_mm=sheet)
                self.assertEqual(result['status'], 'BLOCKED')
                self.assertEqual(result['blocking_codes'], ['TEMPLATE_SHEET_INVALID'])
                self.assertTrue(result['static_geometry_verified'])
                self.assertEqual(result['external_validation']['physical_cut'], 'NOT_TESTED')
        self.assertEqual(proposal, original)


if __name__ == '__main__':
    unittest.main()
