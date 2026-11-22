"""W04 verified subject alpha -> genuine vector Basic Cut, with negative paths."""
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import importlib.util
import sys
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

HAS_CPU = all(importlib.util.find_spec(name) for name in ("numpy", "PIL"))
if HAS_CPU:
    from PIL import Image
else:
    Image = None

from smartsvg_core.native_basic_cut_v35 import BasicCutError
from smartsvg_core.native_basic_cut_subject_v35 import (
    inspect_native_basic_cut_subject, _mask_rings,
)


@unittest.skipUnless(HAS_CPU, "NumPy/Pillow required; run on CPU/Windows job")
class NativeBasicCutSubjectTests(unittest.TestCase):
    def setUp(self):
        self.project = dict(project_path="/synthetic/v1.smartsvg",
                            expected_sha256="a" * 64,
                            subject_id="subject-" + "b" * 32,
                            width_mm=80.0)

    def _render_result(self, alpha_rows, **changes):
        h, w = len(alpha_rows), len(alpha_rows[0])
        image = Image.new("RGBA", (w, h), (35, 55, 85, 255))
        image.putalpha(Image.frombytes(
            "L", (w, h), bytes(v for row in alpha_rows for v in row)))
        encoded = BytesIO()
        image.save(encoded, format="PNG")
        result = dict(png=encoded.getvalue(), dimensions_px=[w, h],
                      project_sha256=self.project["expected_sha256"],
                      subject_id=self.project["subject_id"],
                      source_sha256="c" * 64,
                      rendered_mask_sha256="d" * 64,
                      width_mm=80, height_mm=80 * h / w)
        result.update(changes)
        return result

    def inspect(self, rows, *, width_mm=None):
        rendered = self._render_result(rows)
        args = dict(self.project)
        if width_mm is not None:
            args["width_mm"] = width_mm
        with patch("smartsvg_core.native_basic_cut_subject_v35._render",
                   return_value=rendered) as render:
            value = inspect_native_basic_cut_subject(**args)
            render.assert_called_once_with(**args)
        self.assertEqual(rendered["png"], self._render_result(rows)["png"])
        return value

    def test_real_edited_alpha_yields_two_closed_vector_rings_and_sha(self):
        rows = [[0] * 8 for _ in range(6)]
        for y in range(1, 5):
            for x in range(1, 7):
                rows[y][x] = 180
        for y in range(2, 4):
            for x in range(3, 5):
                rows[y][x] = 0
        preview = self.inspect(rows)
        self.assertEqual(preview.status, "BASIC_CUT_PREVIEW_READY")
        self.assertEqual(preview.ring_count, 2)
        self.assertEqual(preview.width_mm, 80.0)
        self.assertEqual(preview.height_mm, 60.0)
        self.assertEqual(preview.project_sha256, "a" * 64)
        self.assertEqual(preview.source_sha256, "c" * 64)
        self.assertEqual(preview.rendered_mask_sha256, "d" * 64)
        self.assertEqual(preview.svg_sha256, sha256(preview.svg).hexdigest())
        root = ET.fromstring(preview.svg)
        self.assertEqual(root.attrib["viewBox"], "0 0 80 60")
        self.assertEqual(root.attrib["width"], "80mm")
        self.assertEqual(root.attrib["height"], "60mm")
        path = root.find("{http://www.w3.org/2000/svg}path")
        self.assertEqual(path.attrib["fill-rule"], "evenodd")
        self.assertEqual(path.attrib["d"].count("M "), 2)
        self.assertEqual(path.attrib["d"].count(" Z"), 2)
        self.assertFalse(preview.persisted)
        self.assertFalse(preview.design_space_import_tested)
        self.assertFalse(preview.physical_cut_tested)
        self.assertEqual(preview.svg, self.inspect(rows).svg)

    def test_alpha_threshold_and_physical_scale_are_explicit(self):
        rows = [[0, 0, 0, 0], [0, 127, 128, 0], [0, 128, 255, 0],
                [0, 0, 0, 0]]
        preview = self.inspect(rows, width_mm=45.12567)
        self.assertEqual(preview.ring_count, 1)
        self.assertEqual(preview.width_mm, 45.12567)
        self.assertEqual(preview.height_mm, 45.12567)

    def test_disconnected_islands_refused_instead_of_lost(self):
        rows = [[255, 0, 0], [0, 0, 0], [0, 0, 255]]
        with self.assertRaisesRegex(BasicCutError, "MULTIPLE_CUT_COMPONENTS"):
            self.inspect(rows)

    def test_diagonal_corner_contact_is_refused_not_silently_joined(self):
        rows = [[255, 0], [0, 255]]
        with self.assertRaisesRegex(BasicCutError, "AMBIGUOUS_CORNER_CONTACT"):
            self.inspect(rows)

    def test_empty_or_low_alpha_refused_without_svg(self):
        with self.assertRaisesRegex(BasicCutError, "EMPTY_CUT_SILHOUETTE"):
            self.inspect([[0, 127], [0, 0]])

    def test_boundary_budget_rejects_checkerboard_before_tracing(self):
        rows = [[255 if (x + y) % 2 else 0 for x in range(128)]
                for y in range(128)]
        with self.assertRaisesRegex(BasicCutError, "SILHOUETTE_TOO_COMPLEX"):
            self.inspect(rows)

    def test_noisy_mask_fails_before_allocating_edge_coordinate_arrays(self):
        rows = [[255 if (x + y) % 2 else 0 for x in range(128)]
                for y in range(128)]
        with patch("numpy.argwhere", side_effect=AssertionError("unbounded allocation")):
            with self.assertRaisesRegex(BasicCutError, "SILHOUETTE_TOO_COMPLEX"):
                self.inspect(rows)

    def test_opaque_large_rectangle_simplifies_to_four_vertices(self):
        rows = [[255] * 140 for _ in range(100)]
        preview = self.inspect(rows)
        root = ET.fromstring(preview.svg)
        d = root.find("{http://www.w3.org/2000/svg}path").attrib["d"]
        self.assertEqual(d.count(" L "), 3)
        self.assertEqual(preview.ring_count, 1)

    def test_real_pinned_native_renderer_error_propagates_no_fallback(self):
        from smartsvg_core.native_ptc_export_v35 import NativePTCError
        with patch("smartsvg_core.native_basic_cut_subject_v35._render",
                   side_effect=NativePTCError("PROJECT_CHANGED")):
            with self.assertRaisesRegex(NativePTCError, "PROJECT_CHANGED"):
                inspect_native_basic_cut_subject(**self.project)


if __name__ == "__main__":
    unittest.main()
