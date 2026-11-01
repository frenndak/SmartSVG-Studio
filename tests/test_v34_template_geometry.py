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

    def test_no_shared_mutable_output(self):
        first = templates.open_tray(80, 50, 30, 10)
        first['geometry']['cut_outer'][0][0] = 999
        second = templates.open_tray(80, 50, 30, 10)
        self.assertEqual(second['geometry']['cut_outer'][0], [20, 0])


if __name__ == '__main__':
    unittest.main()
