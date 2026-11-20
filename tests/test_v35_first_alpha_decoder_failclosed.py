"""W02 native-alpha decoder fail-closed regression, independent of W03 PNG export.

Synthetic bytes only; no third-party images, packages, project writes or schema changes.
The trusted archive verifier is patched solely to exercise the second-stage
inflation/filter guard with otherwise valid dimensions.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path
import unittest
from unittest.mock import patch
import zlib

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from smartsvg_core import native_first_subject_v35 as first


def _chunk(kind, data):
    return (struct.pack(">I", len(data)) + kind + data +
            struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))


def _rgba_png(compressed):
    header = struct.pack(">IIBBBBB", 2, 2, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header) +
            _chunk(b"IDAT", compressed) + _chunk(b"IEND", b""))


# Two 2-pixel RGBA scanlines: 255,0 and 128,255 alpha, with filter 0.
# Foreground counts alpha >= 128, so this fixture contains three foreground pixels.
_ROWS = (b"\x00" + bytes((12, 34, 56, 255, 12, 34, 56, 0)) +
         b"\x00" + bytes((12, 34, 56, 128, 12, 34, 56, 255)))


class NativeAlphaDecoderFailClosedTests(unittest.TestCase):
    def decode(self, compressed):
        # _verify_png is independently tested in the workspace suite. Pin its
        # result here to exercise decompression guards even when archive
        # admission would reject malformed IDAT before reaching this decoder.
        with patch.object(first, "_verify_png", return_value=(2, 2, "RGBA")):
            return first._rgba_alpha_mask(_rgba_png(compressed))

    def test_valid_rgba_keeps_soft_alpha_and_exact_bbox(self):
        raw, width, height, foreground, bbox = self.decode(zlib.compress(_ROWS))
        self.assertEqual((width, height, foreground, bbox),
                         (2, 2, 3, (0, 0, 2, 2)))
        values = struct.unpack("<4f", raw)
        self.assertEqual(values[0:2], (1.0, 0.0))
        self.assertEqual(values[2], struct.unpack("<f", struct.pack("<f", 128 / 255))[0])
        self.assertEqual(values[3], 1.0)

    def test_all_png_predictors_reconstruct_alpha_without_pixel_drift(self):
        # Independently encode the second scanline with each PNG predictor.
        first_row, second_row = _ROWS[1:9], _ROWS[10:18]
        expected = self.decode(zlib.compress(_ROWS))[0]
        for predictor in range(5):
            encoded = bytearray()
            for i, value in enumerate(second_row):
                left = second_row[i - 4] if i >= 4 else 0
                above = first_row[i]
                upper_left = first_row[i - 4] if i >= 4 else 0
                if predictor == 0:
                    predicted = 0
                elif predictor == 1:
                    predicted = left
                elif predictor == 2:
                    predicted = above
                elif predictor == 3:
                    predicted = (left + above) // 2
                else:
                    p = left + above - upper_left
                    da, db, dc = abs(p - left), abs(p - above), abs(p - upper_left)
                    predicted = (left if da <= db and da <= dc
                                 else above if db <= dc else upper_left)
                encoded.append((value - predicted) & 255)
            scanlines = b"\x00" + first_row + bytes([predictor]) + bytes(encoded)
            with self.subTest(predictor=predictor):
                raw, width, height, foreground, bbox = self.decode(
                    zlib.compress(scanlines))
                self.assertEqual((width, height, foreground, bbox),
                                 (2, 2, 3, (0, 0, 2, 2)))
                self.assertEqual(raw, expected)

    def test_invalid_filter_is_rejected_without_reusing_previous_scanline(self):
        corrupted = b"\x05" + _ROWS[1:]
        with self.assertRaises(first.NativeFirstSubjectError) as ctx:
            self.decode(zlib.compress(corrupted))
        self.assertEqual(ctx.exception.code, "INVALID_ARCHIVED_SOURCE")
        self.assertEqual(self.decode(zlib.compress(_ROWS))[3], 3)

    def test_truncated_compressed_stream_is_rejected(self):
        with self.assertRaises(first.NativeFirstSubjectError) as ctx:
            self.decode(zlib.compress(_ROWS)[:-2])
        self.assertEqual(ctx.exception.code, "INVALID_ARCHIVED_SOURCE")

    def test_extra_decompressed_scanline_is_rejected(self):
        with self.assertRaises(first.NativeFirstSubjectError) as ctx:
            self.decode(zlib.compress(_ROWS + b"\x00" * 9))
        self.assertEqual(ctx.exception.code, "INVALID_ARCHIVED_SOURCE")

    def test_trailing_second_zlib_stream_is_rejected(self):
        with self.assertRaises(first.NativeFirstSubjectError) as ctx:
            self.decode(zlib.compress(_ROWS) + zlib.compress(_ROWS))
        self.assertEqual(ctx.exception.code, "INVALID_ARCHIVED_SOURCE")

    def test_invalid_zlib_header_is_rejected(self):
        with self.assertRaises(first.NativeFirstSubjectError) as ctx:
            self.decode(b"not a zlib stream")
        self.assertEqual(ctx.exception.code, "INVALID_ARCHIVED_SOURCE")


if __name__ == "__main__":
    unittest.main()
