"""W04 Basic Cut admission: reject malformed vector inputs without state leakage."""
import hashlib
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))
from smartsvg_core.native_basic_cut_v35 import BasicCutError, preview_basic_cut

VALID = (((0, 0), (20, 0), (20, 10), (0, 10)),)
NS = "{http://www.w3.org/2000/svg}"


class BasicCutMalformedInputTests(unittest.TestCase):
    def test_malformed_contours_fail_closed_then_valid_readback(self):
        malformed = (
            (((0, 0), (20, 0), (20, True), (0, 10)),),
            (((0, 0), (20, 0), (20, float("nan")), (0, 10)),),
            (((0, 0), (20, 0), (20, 10), (20, 10), (0, 10)),),
            (((0, 0), (5, 0), (10, 0)),),
            (((0, 0), (20, 0), (20, 11), (0, 10)),),
        )
        baseline = preview_basic_cut(rings=VALID, width_mm=20, height_mm=10)
        for rings in malformed:
            with self.subTest(rings=rings):
                with self.assertRaises(BasicCutError):
                    preview_basic_cut(rings=rings, width_mm=20, height_mm=10)
                recovered = preview_basic_cut(rings=VALID, width_mm=20, height_mm=10)
                self.assertEqual(recovered.svg, baseline.svg)
                self.assertEqual(recovered.sha256, baseline.sha256)
                self.assertEqual(hashlib.sha256(recovered.svg).hexdigest(), recovered.sha256)
                root = ET.fromstring(recovered.svg)
                self.assertEqual(root.get("viewBox"), "0 0 20 10")
                self.assertEqual(root.find(NS + "path").get("fill-rule"), "evenodd")
                self.assertFalse(recovered.physical_cut_tested)

    def test_invalid_container_and_physical_units(self):
        for rings in (None, {}, [], "not vector geometry", [None]):
            with self.subTest(rings=rings), self.assertRaises(BasicCutError):
                preview_basic_cut(rings=rings, width_mm=20, height_mm=10)
        for size in (True, float("nan"), float("inf"), -1, 0, 10001):
            with self.subTest(size=size), self.assertRaises(BasicCutError):
                preview_basic_cut(rings=VALID, width_mm=20, height_mm=size)


if __name__ == "__main__":
    unittest.main()
