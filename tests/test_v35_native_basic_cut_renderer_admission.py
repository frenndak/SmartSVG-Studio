"""W04 Basic Cut: malformed renderer output must fail closed and recover."""
import importlib.util
from io import BytesIO
from pathlib import Path
import sys
import unittest
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
from smartsvg_core.native_basic_cut_subject_v35 import inspect_native_basic_cut_subject


@unittest.skipUnless(HAS_CPU, "NumPy/Pillow required; run on CPU/Windows job")
class BasicCutRendererAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.inputs = dict(
            project_path="/synthetic/v1.smartsvg",
            expected_sha256="a" * 64,
            subject_id="subject-" + "b" * 32,
            width_mm=20.0,
        )

    def rendered(self, data, dimensions=(2, 2)):
        return dict(
            png=data, dimensions_px=list(dimensions),
            project_sha256=self.inputs["expected_sha256"],
            subject_id=self.inputs["subject_id"],
            source_sha256="c" * 64,
            rendered_mask_sha256="d" * 64,
            width_mm=20.0, height_mm=20.0,
        )

    def png(self, *, mode="RGBA", fmt="PNG"):
        image = Image.new(mode, (2, 2), (255, 0, 0, 255) if mode == "RGBA" else (255, 0, 0))
        stream = BytesIO()
        image.save(stream, format=fmt)
        return stream.getvalue()

    def inspect_rendered(self, rendered):
        with patch("smartsvg_core.native_basic_cut_subject_v35._render",
                   return_value=rendered) as renderer:
            result = inspect_native_basic_cut_subject(**self.inputs)
            renderer.assert_called_once_with(**self.inputs)
            return result

    def test_corrupt_truncated_wrong_format_and_size_fail_closed_then_recover(self):
        valid = self.rendered(self.png())
        baseline = self.inspect_rendered(valid)
        malformed = (
            self.rendered(b"not an image"),
            self.rendered(self.png()[:24]),
            self.rendered(self.png(fmt="TIFF")),
            self.rendered(self.png(mode="RGB")),
            self.rendered(self.png(), dimensions=(3, 2)),
        )
        for bad in malformed:
            with self.subTest(kind=bad["png"][:12], dimensions=bad["dimensions_px"]):
                with self.assertRaisesRegex(BasicCutError, "INVALID_RENDERED_PNG"):
                    self.inspect_rendered(bad)
                recovered = self.inspect_rendered(valid)
                self.assertEqual(recovered.svg, baseline.svg)
                self.assertEqual(recovered.svg_sha256, baseline.svg_sha256)
                self.assertFalse(recovered.persisted)
                self.assertFalse(recovered.design_space_import_tested)
                self.assertFalse(recovered.physical_cut_tested)

    def test_header_rejections_do_not_decode_pixels_and_recover(self):
        # Header checks must precede png.load(): compressed, oversized
        # PNGs should not allocate a full decoded RGBA buffer.
        oversized = Image.new("RGBA", (2300, 2300), (20, 40, 60, 255))
        encoded = BytesIO()
        oversized.save(encoded, format="PNG")
        invalid = (
            self.rendered(encoded.getvalue(), dimensions=(2300, 2300)),
            self.rendered(self.png(), dimensions=(3, 2)),
            self.rendered(self.png(mode="RGB")),
        )
        for rendered in invalid:
            with self.subTest(dimensions=rendered["dimensions_px"],
                              size=len(rendered["png"])):
                with patch("PIL.Image.Image.load",
                           side_effect=AssertionError("decoded before admission")):
                    with self.assertRaisesRegex(BasicCutError, "INVALID_RENDERED_PNG"):
                        self.inspect_rendered(rendered)
        # A failed request must not poison the next valid preview.
        recovered = self.inspect_rendered(self.rendered(self.png()))
        self.assertEqual(recovered.status, "BASIC_CUT_PREVIEW_READY")
        self.assertFalse(recovered.persisted)

    def test_native_renderer_cas_failure_is_not_reclassified(self):
        from smartsvg_core.native_ptc_export_v35 import NativePTCError
        with patch("smartsvg_core.native_basic_cut_subject_v35._render",
                   side_effect=NativePTCError("PROJECT_CHANGED")):
            with self.assertRaisesRegex(NativePTCError, "PROJECT_CHANGED"):
                inspect_native_basic_cut_subject(**self.inputs)


if __name__ == "__main__":
    unittest.main()
