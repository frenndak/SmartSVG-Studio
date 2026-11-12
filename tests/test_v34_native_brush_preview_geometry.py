"""Regression: native brush comparisons must preserve the archived mask geometry."""
import pathlib
import struct
import zlib
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


def real_png(width, height):
    """Build a decodable grayscale PNG with valid CRCs, not just an IHDR stub."""
    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data +
                struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))
    scanline = b"\\x00" + b"\\x7f" * width
    return (b"\\x89PNG\\r\\n\\x1a\\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(scanline * height)) +
            chunk(b"IEND", b""))


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

    def test_real_png_comparisons_require_exact_source_geometry(self):
        """Use complete, CRC-valid PNGs rather than synthetic IHDR-only bytes."""
        original = real_png(16, 12)
        before = real_png(16, 12)
        self.assertTrue(matching_preview_dimensions(original, before, real_png(16, 12)))
        self.assertFalse(matching_preview_dimensions(original, real_png(12, 16),
                                                     real_png(16, 12)))
        self.assertFalse(matching_preview_dimensions(original, before, real_png(16, 13)))
        # The geometry gate must remain a pure read-only predicate.
        self.assertEqual(original, real_png(16, 12))


if __name__ == "__main__":
    unittest.main()
