"""Regression: native brush comparisons must preserve the archived mask geometry."""
import pathlib
import struct
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "engine"))
from native_brush_draft_tk_v34 import matching_preview_dimensions


def header(width, height):
    # The helper checks the bounded PNG envelope and IHDR dimensions; this
    # synthetic header is not used as an actual decoded image.
    return (b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR"
            + struct.pack(">II", width, height) + b"\x08\x00\x00\x00\x00"
            + b"\x00" * 8)


class NativeBrushPreviewGeometryTests(unittest.TestCase):
    def test_matching_source_and_cpu_comparisons(self):
        original = header(32, 24)
        self.assertTrue(matching_preview_dimensions(original, header(32, 24),
                                                    header(32, 24)))

    def test_mismatched_before_or_after_refused(self):
        original = header(32, 24)
        self.assertFalse(matching_preview_dimensions(original, header(24, 32),
                                                     header(32, 24)))
        self.assertFalse(matching_preview_dimensions(original, header(32, 24),
                                                     header(32, 25)))

    def test_malformed_or_oversized_comparison_refused(self):
        original = header(32, 24)
        self.assertFalse(matching_preview_dimensions(original, b"bad",
                                                     header(32, 24)))
        self.assertFalse(matching_preview_dimensions(original, header(2049, 24),
                                                     header(32, 24)))


if __name__ == "__main__":
    unittest.main()
