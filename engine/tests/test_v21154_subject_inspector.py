"""V21.15.4: no-trimming subject diagnostics and backwards-compatible node."""
import importlib
import json
import sys
import types
import unittest
from pathlib import Path

import cv2
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
if 'ss21154test' not in sys.modules:
    package = types.ModuleType('ss21154test')
    package.__path__ = [str(ROOT)]
    sys.modules[package.__name__] = package
node = importlib.import_module('ss21154test.node_v21154')
old = importlib.import_module('ss21154test.node_v21152')
core = importlib.import_module('ss21154test.smartsvg_core.subject_inspector_v21154')


def synthetic():
    masks = np.zeros((4, 180, 240), np.float32)
    cv2.circle(masks[0], (40, 60), 25, 1, -1)
    cv2.circle(masks[0], (85, 60), 6, 1, -1)  # detached accessory
    cv2.rectangle(masks[1], (130, 20), (194, 100), 1, -1)
    cv2.circle(masks[2], (130, 130), 25, 1, -1)
    cv2.line(masks[2], (130, 130), (130, 179), 1, 2)  # clipped to edge
    # Fourth mask deliberately blank; must remain 4th instead of renumbered.
    rgb = np.full((180, 240, 3), 255, np.uint8)
    for i, color in enumerate(((115, 60, 90), (40, 150, 70), (110, 80, 240))):
        rgb[masks[i] > 0] = color
    return rgb, masks


class TestSubjectInspector(unittest.TestCase):
    def test_fragments_borders_rectangle_and_empty_are_not_silently_removed(self):
        _, masks = synthetic()
        original = masks.copy()
        out = core.inspect_subject_masks(masks, expected_shape=(180, 240))
        self.assertEqual([x['numero'] for x in out], [1, 2, 3, 4])
        self.assertIn('FRAGMENTS_DETACHES', out[0]['codes'])
        self.assertEqual(out[0]['fragments_significatifs'], 2)
        self.assertEqual(out[0]['surface_px'], int(masks[0].sum()))
        self.assertIn('SILHOUETTE_RECTANGULAIRE', out[1]['codes'])
        self.assertIn('TOUCHE_BORD_IMAGE', out[2]['codes'])
        self.assertEqual(out[3]['codes'], ['MASQUE_VIDE'])
        self.assertIsNone(out[3]['bbox_source_px'])
        np.testing.assert_array_equal(original, masks)

    def test_solid_circle_requires_review_not_ready_claim(self):
        m = np.zeros((1, 120, 120), np.float32)
        cv2.circle(m[0], (60, 60), 34, 1, -1)
        result = core.inspect_subject_masks(m)
        self.assertEqual(result[0]['codes'], [])
        self.assertEqual(result[0]['etat'], 'INSPECTION_VISUELLE_REQUISE')

    def test_small_artifacts_warn_without_erasure(self):
        m = np.zeros((1, 100, 100), np.float32)
        cv2.circle(m[0], (30, 30), 15, 1, -1)
        for x in (55, 60, 65, 70):
            m[0, 65, x] = 1
        result = core.inspect_subject_masks(m)[0]
        self.assertEqual(result['micro_fragments'], 4)
        self.assertIn('MICRO_FRAGMENTS', result['codes'])
        self.assertEqual(int(m.sum()), result['surface_px'])

    def test_unsafe_or_enormous_masks_are_refused_without_modification(self):
        with self.assertRaises(core.SubjectInspectionUnavailable):
            core.inspect_subject_masks(np.zeros((33, 12, 12), np.float32))
        with self.assertRaises(core.SubjectInspectionUnavailable):
            core.inspect_subject_masks(np.full((2, 12, 12), np.nan, np.float32))
        with self.assertRaises(core.SubjectInspectionUnavailable):
            core.inspect_subject_masks(np.full((1, 12, 12), -0.1, np.float32))
        with self.assertRaises(core.SubjectInspectionUnavailable):
            core.inspect_subject_masks(np.zeros((2, 12, 12), np.float32), expected_shape=(13, 12))
        with self.assertRaises(core.SubjectInspectionUnavailable):
            core.inspect_subject_masks(np.zeros((1, 3000, 3000), np.float32))

    def test_new_node_preserves_old_mask_output_and_user_selection(self):
        rgb, masks = synthetic()
        image = torch.from_numpy(rgb.astype(np.float32) / 255)[None]
        tensor = torch.from_numpy(masks)
        new = node.SmartSVGChooseSubjectV21154().run(image, tensor, 1)
        legacy = node.SmartSVGChooseSubjectV21131().run(image, tensor, 1)
        self.assertEqual(len(new['result']), len(legacy['result']))
        self.assertTrue(torch.equal(new['result'][0], legacy['result'][0]))
        self.assertEqual(new['result'][2], legacy['result'][2])
        data = new['ui']['smartsvg_subjects_v21154'][0]
        self.assertEqual(len(data['sujets']), 4)
        self.assertIsNone(data['sujets'][3]['image_data'])
        self.assertTrue(data['sujets'][0]['image_data'].startswith('data:image/png;base64,'))
        self.assertFalse(data['modifications_automatiques'])
        self.assertFalse(data['decoupe_certifiee'])

    def test_diagnostics_unavailable_never_breaks_selection(self):
        # 5 MP per image, but more than 50M mask pixels -> diagnostic abstains.
        image = torch.zeros((1, 1400, 1200, 3), dtype=torch.float32)
        image[:, 0:300, 0:300, :] = 0.4
        multi = torch.zeros((31, 1400, 1200), dtype=torch.float32)
        multi[0, 20:160, 20:160] = 1
        response = node.SmartSVGChooseSubjectV21154().run(image, multi, 1)
        self.assertEqual(response['result'][0].shape, (1, 1400, 1200))
        self.assertNotIn('smartsvg_subjects_v21154', response['ui'])
        self.assertIn('indisponible', response['ui']['text'][-1])

    def test_registration_is_additive_and_ports_unchanged(self):
        for key, cls in old.NODE_CLASS_MAPPINGS.items():
            self.assertIs(node.NODE_CLASS_MAPPINGS[key], cls)
        self.assertIs(node.NODE_CLASS_MAPPINGS['SmartSVGChooseSubjectV21154'],
                      node.SmartSVGChooseSubjectV21154)
        self.assertEqual(node.SmartSVGChooseSubjectV21154.INPUT_TYPES(),
                         node.SmartSVGChooseSubjectV21131.INPUT_TYPES())
        self.assertEqual(node.SmartSVGChooseSubjectV21154.RETURN_TYPES,
                         node.SmartSVGChooseSubjectV21131.RETURN_TYPES)


if __name__ == '__main__':
    unittest.main()
