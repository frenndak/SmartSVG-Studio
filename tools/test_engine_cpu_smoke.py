#!/usr/bin/env python3
"""CPU-only, synthetic functional smoke checks for the LIVE SmartSVG engine.

No ComfyUI, torch, model weights, user files, GPU, Design Space, or hardware.
These tests intentionally exercise production code in engine/, not a copy of
the frozen V21.15.2 ZIP. The historical archive is verified separately.
"""
from __future__ import annotations

import sys
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
