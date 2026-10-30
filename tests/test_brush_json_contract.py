"""G2.3/G3.3e: strict V21.6 brush JSON admission without optional ML deps.

These tests import the actual decoder with stubs only for numpy/Pillow, which
are unused by decode(). The replay raster path is tested in engine/tests.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "engine" / "smartsvg_editor" / "strokes.py"


def load_decoder():
    pil = ModuleType("PIL")
    pil.Image = ModuleType("PIL.Image")
    pil.ImageDraw = ModuleType("PIL.ImageDraw")
    spec = importlib.util.spec_from_file_location("smartsvg_strokes_json_contract", SOURCE)
    module = importlib.util.module_from_spec(spec)
    with mock.patch.dict(sys.modules, {
        "numpy": ModuleType("numpy"), "PIL": pil,
        "PIL.Image": pil.Image, "PIL.ImageDraw": pil.ImageDraw,
    }):
        spec.loader.exec_module(module)
    return module


class BrushJsonAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.strokes = load_decoder()

    def valid(self):
        return json.dumps({
            "version": 1, "width": 64, "height": 48, "count": 1,
            "source": "a" * 64,
            "strokes": [{"object": 0, "mode": "add",
                         "radius": 0.12, "points": [[0.5, 0.5]]}],
        })

    def parse(self, payload):
        return self.strokes.decode(
            payload, width=64, height=48, count=1, fingerprint="a" * 64)

    def test_canonical_single_stroke_remains_valid(self):
        result = self.parse(self.valid())
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["mode"], "add")
        self.assertEqual(result[0]["points"], [(0.5, 0.5)])

    def test_reject_duplicate_keys_at_root_and_stroke_depth(self):
        valid = self.valid()
        cases = (
            ('"version": 1', '"version": 2, "version": 1'),
            ('"mode": "add"', '"mode": "erase", "mode": "add"'),
            ('"object": 0', '"object": 99, "object": 0'),
            ('"radius": 0.12', '"radius": 0.01, "radius": 0.12'),
        )
        for old, replacement in cases:
            with self.subTest(field=old):
                self.assertIn(old, valid)
                with self.assertRaises(self.strokes.StrokeError):
                    self.parse(valid.replace(old, replacement, 1))

    def test_reject_deeply_nested_json_without_uncaught_recursion(self):
        with self.assertRaises(self.strokes.StrokeError):
            self.parse("[" * 1200 + "]" * 1200)

    def test_reject_nonfinite_number(self):
        with self.assertRaises(self.strokes.StrokeError):
            self.parse(self.valid().replace("0.12", "NaN", 1))


if __name__ == "__main__":
    unittest.main()
