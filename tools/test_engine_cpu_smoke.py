#!/usr/bin/env python3
"""CPU-only, synthetic functional smoke checks for the LIVE SmartSVG engine.

No ComfyUI, torch, model weights, user files, GPU, Design Space, or hardware.
These tests intentionally exercise production code in engine/, not a copy of
the frozen V21.15.2 ZIP. The historical archive is verified separately.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))

import cv2  # noqa: E402
import numpy as np  # noqa: E402
from smartsvg_quality.white_sheet_v21152 import SheetUncertain, segment_white_grid  # noqa: E402


class LiveWhiteSheetSmoke(unittest.TestCase):
    @staticmethod
    def twelve_subjects() -> np.ndarray:
        canvas = np.full((360, 480, 3), 255, dtype=np.uint8)
        for row in range(3):
            for col in range(4):
                x, y = col * 120 + 60, row * 120 + 60
                cv2.circle(canvas, (x, y), 34, (50, 110, 190), -1)
                cv2.circle(canvas, (x, y), 34, (0, 0, 0), 2)
        return canvas

    def test_twelve_subjects_are_independent(self) -> None:
        result = segment_white_grid(self.twelve_subjects(), cols=4, rows=3)
        self.assertEqual(result.masks.shape, (12, 360, 480))
        self.assertEqual(len(result.diagnostics), 12)
        for index, mask in enumerate(result.masks):
            row, col = divmod(index, 4)
            self.assertEqual(int(mask[row * 120 + 60, col * 120 + 60]), 1)
            self.assertEqual(cv2.connectedComponents((mask > 0).astype(np.uint8), 8)[0] - 1, 1)

    def test_unknown_sheet_must_not_invent_silhouettes(self) -> None:
        with self.assertRaises(SheetUncertain):
            segment_white_grid(np.full((360, 480, 3), 255, dtype=np.uint8), cols=4, rows=3)

    def test_rectangle_is_not_silently_a_sticker(self) -> None:
        canvas = np.full((360, 480, 3), 255, dtype=np.uint8)
        for row in range(3):
            for col in range(4):
                cv2.rectangle(canvas, (col * 120 + 20, row * 120 + 20),
                              (col * 120 + 99, row * 120 + 99), (0, 120, 200), -1)
        with self.assertRaises(SheetUncertain):
            segment_white_grid(canvas, cols=4, rows=3)

    def test_floating_point_input_is_rejected(self) -> None:
        with self.assertRaises(SheetUncertain):
            segment_white_grid(self.twelve_subjects().astype(np.float32), cols=4, rows=3)


class LiveSVGPublicationSmoke(unittest.TestCase):
    def test_real_editable_vector_export_keeps_source_and_complete_files(self):
        from smartsvg_vector.layers_v2113 import vectorize_flat_art, save_svg
        from smartsvg_vector.svg_publication import save_svg as publication
        from inspect_svg_contracts import inspect_svg
        self.assertIs(save_svg, publication, 'historical node import must use the secured writer')
        image = np.full((80, 120, 3), 255, dtype=np.uint8)
        mask = np.zeros((80, 120), dtype=np.float32)
        image[10:70, 10:60] = (220, 40, 60)
        image[10:70, 60:110] = (40, 80, 220)
        mask[10:70, 10:110] = 1
        before = (image.tobytes(), mask.tobytes())
        payload, _, audit = vectorize_flat_art(image, mask, colors=2, width_mm=45)
        self.assertEqual(audit['calques_couleur'], 2)
        self.assertFalse(audit['svg_decoupe_cricut_certifie'])
        with tempfile.TemporaryDirectory() as folder:
            first = Path(save_svg(payload, folder))
            second = Path(save_svg(payload, folder))
            self.assertNotEqual(first, second)
            self.assertEqual(first.read_bytes(), payload)
            self.assertEqual(second.read_bytes(), payload)
            contract = inspect_svg(first, profile='editable')
            self.assertEqual(contract['width_mm'], 45)
            self.assertGreaterEqual(contract['vector_elements'], 2)
            self.assertFalse(contract['design_space_import_verified'])
            self.assertEqual(list(Path(folder).glob('.smartsvg_svg_*')), [])
        self.assertEqual((image.tobytes(), mask.tobytes()), before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
