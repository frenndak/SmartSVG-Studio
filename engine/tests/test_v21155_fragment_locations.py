"""G2.6 non-destructive component focus regression suite."""
import importlib
import sys
import types
import unittest
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if 'ss21155test' not in sys.modules:
    pkg = types.ModuleType('ss21155test')
    pkg.__path__ = [str(ROOT)]
    sys.modules[pkg.__name__] = pkg
core = importlib.import_module('ss21155test.smartsvg_core.subject_inspector_v21154')


class TestFragmentLocations(unittest.TestCase):
    def test_detached_accessory_coordinates_and_no_mask_mutation(self):
        masks = np.zeros((1, 120, 200), np.float32)
        cv2.circle(masks[0], (45, 45), 20, 1, -1)
        cv2.rectangle(masks[0], (128, 80), (137, 91), 1, -1)
        original = masks.copy()
        item = core.inspect_subject_masks(masks)[0]
        self.assertEqual(item['fragments_significatifs'], 2)
        self.assertEqual(item['zones_non_affichees'], 0)
        zone = item['zones_a_examiner'][0]
        self.assertEqual(zone['type'], 'FRAGMENT_SEPARE')
        self.assertEqual(zone['bbox_source_px'], [128, 80, 138, 92])
        self.assertEqual(zone['surface_px'], 120)
        x0, y0, x1, y1 = zone['bbox_apercu_88px']
        self.assertTrue(0 <= x0 <= x1 <= 88 and 0 <= y0 <= y1 <= 88)
        np.testing.assert_array_equal(masks, original)

    def test_one_pixel_micro_is_visible_as_a_review_point(self):
        mask = np.zeros((50, 100), np.float32)
        cv2.circle(mask, (35, 25), 10, 1, -1)
        mask[10, 80] = 1
        item = core.inspect_subject_masks(mask)[0]
        self.assertEqual(item['micro_fragments'], 1)
        zone = item['zones_a_examiner'][0]
        self.assertEqual(zone['type'], 'MICRO_FRAGMENT')
        self.assertEqual(zone['bbox_source_px'], [80, 10, 81, 11])
        self.assertEqual(zone['surface_px'], 1)

    def test_many_islands_bounded_deterministic_and_all_preserved(self):
        mask = np.zeros((260, 350), np.float32)
        cv2.circle(mask, (30, 30), 17, 1, -1)
        for x in range(100, 280, 12):
            for y in range(90, 185, 15):
                mask[y, x] = 1
        snapshot = mask.copy()
        item = core.inspect_subject_masks(mask)[0]
        self.assertEqual(len(item['zones_a_examiner']), core.MAX_FOCUS_ZONES)
        self.assertEqual(item['zones_non_affichees'], 105-core.MAX_FOCUS_ZONES)
        self.assertEqual(item['surface_px'], int(mask.sum()))
        self.assertEqual(item['zones_a_examiner'], core.inspect_subject_masks(mask)[0]['zones_a_examiner'])
        np.testing.assert_array_equal(mask, snapshot)

    def test_crop_mapping_matches_legacy_preview(self):
        loc = core._preview_box([0, 0, 1, 1], [0, 0, 100, 80], (80, 100))
        self.assertEqual(loc[:2], [2, 10])
        self.assertTrue(loc[2] >= loc[0] and loc[3] >= loc[1])

    def test_empty_masks_report_no_areas(self):
        item = core.inspect_subject_masks(np.zeros((20, 30), np.float32))[0]
        self.assertEqual(item['zones_a_examiner'], [])
        self.assertEqual(item['zones_non_affichees'], 0)
        self.assertEqual(item['bords_touches'], [])

    def test_border_location_not_repair(self):
        mask = np.zeros((80, 90), np.float32)
        mask[0:10, 0:20] = 1
        item = core.inspect_subject_masks(mask)[0]
        self.assertEqual(item['bords_touches'], ['GAUCHE', 'HAUT'])
        self.assertEqual(item['zones_a_examiner'], [])
        self.assertEqual(item['surface_px'], 200)

    def test_noise_abstains_without_erasing_source(self):
        mask = np.zeros((310, 310), np.float32)
        mask[::2, ::2] = 1
        before = mask.copy()
        with self.assertRaises(core.SubjectInspectionUnavailable):
            core.inspect_subject_masks(mask)
        np.testing.assert_array_equal(mask, before)


if __name__ == '__main__':
    unittest.main()
