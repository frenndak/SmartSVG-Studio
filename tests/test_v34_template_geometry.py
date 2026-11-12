"""V34-126 / T-V34-16-01..04: in-memory nominal template geometry."""
import importlib.util
import json
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'engine/smartsvg_core/template_geometry_v34.py'
SPEC = importlib.util.spec_from_file_location('template_geometry_v34', MODULE)
templates = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(templates)


class TestV34TemplateGeometry(unittest.TestCase):
    def test_open_tray_reference_geometry(self):
        proposal = templates.open_tray(80, 50, 30, 10)
        geo = proposal['geometry']
        self.assertEqual(geo['bbox_mm'], [0, 0, 140, 110])
        self.assertEqual(geo['area_mm2'], 13000)
        self.assertEqual(len(geo['cut_slits']), 4)
        self.assertEqual(len(geo['score_folds']), 8)
        self.assertEqual(geo['cut_outer'][0], geo['cut_outer'][-1])
        self.assertEqual(len(geo['paths']), 13)
        self.assertEqual([p['operation'] for p in geo['paths']], ['CUT']*5 + ['SCORE']*8)
        self.assertTrue(all(len(s) == 2 for s in geo['cut_slits']))
        self.assertTrue(all(s[0] != s[1] for s in geo['cut_slits']))

    def test_folded_card_reference_geometry(self):
        proposal = templates.folded_card(105, 148)
        geo = proposal['geometry']
        self.assertEqual(geo['bbox_mm'], [0, 0, 210, 148])
        self.assertEqual(geo['score_folds'], [[[105, 0], [105, 148]]])
        self.assertEqual(geo['cut_slits'], [])
        self.assertEqual([p['operation'] for p in geo['paths']], ['CUT', 'SCORE'])
        self.assertEqual(geo['area_mm2'], 31080)

    def test_invalid_dimensions_fail_closed(self):
        bad = (0, -1, True, False, None, '', float('nan'),
               float('inf'), float('-inf'), 10**400)
        for value in bad:
            with self.subTest(value=str(value)[:30]):
                with self.assertRaisesRegex(templates.TemplateGeometryError,
                                            'INVALID_TEMPLATE_DIMENSION'):
                    templates.folded_card(value, 148)
                with self.assertRaisesRegex(templates.TemplateGeometryError,
                                            'INVALID_TEMPLATE_DIMENSION'):
                    templates.open_tray(80, 50, 30, value)
        with self.assertRaisesRegex(templates.TemplateGeometryError,
                                    'INVALID_TEMPLATE_DIMENSION'):
            templates.open_tray(80, 50, 30, 30)
        with self.assertRaisesRegex(templates.TemplateGeometryError,
                                    'INVALID_TEMPLATE_DIMENSION'):
            templates.open_tray(80, 50, 30, 31)

    def test_derived_overflow_rejected(self):
        with self.assertRaisesRegex(templates.TemplateGeometryError,
                                    'INVALID_TEMPLATE_DIMENSION'):
            templates.open_tray(1e308, 50, 1e308, 1)
        with self.assertRaisesRegex(templates.TemplateGeometryError,
                                    'INVALID_TEMPLATE_DIMENSION'):
            templates.folded_card(1e308, 148)

    def test_large_integer_derived_area_overflow_fails_closed(self):
        cases = (
            (templates.folded_card, (10**200, 10**200)),
            (templates.open_tray, (10**200, 10**200, 10**200, 10**199)),
        )
        for maker, args in cases:
            with self.subTest(maker=maker.__name__):
                with self.assertRaisesRegex(templates.TemplateGeometryError,
                                            'INVALID_TEMPLATE_DIMENSION: derived area'):
                    maker(*args)

    def test_large_integer_derived_bounds_overflow_fails_closed(self):
        with self.assertRaisesRegex(templates.TemplateGeometryError,
                                    'INVALID_TEMPLATE_DIMENSION: derived bounds'):
            templates.folded_card(10**308, 148)

    def test_tiny_positive_dimensions_cannot_collapse_cut_or_score(self):
        # The nominal values are positive and areas finite, but rounding
        # collapses actual path endpoints. Reject before any future export.
        cases = (
            (80, 50, 30, 1e-20),  # cut slits disappear: h-t == h
            (1e-20, 50, 30, 10),  # horizontal SCORE: h+w == h
            (80, 1e-20, 30, 10),  # vertical SCORE: h+d == h
        )
        for dimensions in cases:
            with self.subTest(dimensions=dimensions):
                with self.assertRaisesRegex(
                        templates.TemplateGeometryError,
                        'INVALID_TEMPLATE_DIMENSION: collapsed'):
                    templates.open_tray(*dimensions)

    def test_small_representable_tab_width_is_not_rejected(self):
        proposal = templates.open_tray(80, 50, 30, 1e-6)
        for path in proposal['geometry']['paths']:
            points = path['points_mm']
            self.assertTrue(all(a != b for a, b in zip(points, points[1:])))

    def test_repeatable_without_mutation_or_persistence(self):
        dimensions = [80, 50, 30, 10]
        original = dimensions[:]
        first = templates.open_tray(*dimensions)
        second = templates.open_tray(*dimensions)
        self.assertEqual(dimensions, original)
        self.assertEqual(first, second)
        self.assertEqual(json.loads(json.dumps(first)), first)
        self.assertFalse(first['persisted'])
        self.assertEqual(first['handoff']['machine_material_qualification'], 'UNKNOWN')
        self.assertEqual(first['handoff']['design_space_import'], 'NON_EXECUTE')
        self.assertEqual(first['handoff']['physical_validation'], 'NON_EXECUTE')
        self.assertTrue(first['handoff']['requires_manual_score_assignment'])
        self.assertTrue(first['handoff']['requires_manual_attach'])

    def test_path_points_do_not_alias_geometry_catalogue(self):
        # A future UI/preflight consumer may transform one representation;
        # it must not silently rewrite the other in the same preview result.
        for factory, args in (
            (templates.folded_card, (105, 148)),
            (templates.open_tray, (80, 50, 30, 10)),
        ):
            with self.subTest(template=factory.__name__):
                geometry = factory(*args)['geometry']
                sources = ([geometry['cut_outer']] + geometry['cut_slits']
                           + geometry['score_folds'])
                paths = geometry['paths']
                self.assertEqual(len(paths), len(sources))
                for source, path in zip(sources, paths):
                    self.assertEqual(path['points_mm'], source)
                    original = source[0][0]
                    path['points_mm'][0][0] = 999
                    self.assertEqual(source[0][0], original)
                    source[0][0] = 777
                    self.assertEqual(path['points_mm'][0][0], 999)

    def test_no_shared_mutable_output(self):
        first = templates.open_tray(80, 50, 30, 10)
        first['geometry']['cut_outer'][0][0] = 999
        second = templates.open_tray(80, 50, 30, 10)
        self.assertEqual(second['geometry']['cut_outer'][0], [20, 0])


    def test_cut_score_paths_stay_inside_nominal_bounds(self):
        # V34-126/127: a nominal preview must never advertise out-of-bounds
        # CUT/SCORE paths to a later fabrication preflight consumer.
        for maker, args in (
            (templates.folded_card, (105, 148)),
            (templates.open_tray, (80, 50, 30, 10)),
            (templates.open_tray, (80, 50, 30, 1e-6)),
        ):
            with self.subTest(template=maker.__name__, dimensions=args):
                proposal = maker(*args)
                x0, y0, x1, y1 = proposal['geometry']['bbox_mm']
                self.assertEqual((x0, y0), (0, 0))
                for path in proposal['geometry']['paths']:
                    self.assertIn(path['operation'], ('CUT', 'SCORE'))
                    self.assertGreaterEqual(len(path['points_mm']), 2)
                    for x, y in path['points_mm']:
                        self.assertTrue(x0 <= x <= x1)
                        self.assertTrue(y0 <= y <= y1)

    def test_template_operation_ids_are_unique_and_not_persisted(self):
        # A distinct path identity is required before assigning operations
        # manually; previews must not mutate the user's V1 project.
        for maker, args in (
            (templates.folded_card, (105, 148)),
            (templates.open_tray, (80, 50, 30, 10)),
        ):
            with self.subTest(template=maker.__name__):
                proposal = maker(*args)
                paths = proposal['geometry']['paths']
                self.assertEqual(len({p['id'] for p in paths}), len(paths))
                self.assertFalse(proposal['persisted'])
                self.assertEqual(proposal['handoff']['design_space_import'], 'NON_EXECUTE')
                self.assertTrue(proposal['handoff']['requires_manual_score_assignment'])

if __name__ == '__main__':
    unittest.main()
