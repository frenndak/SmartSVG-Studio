"""W02 native-alpha decoder fail-closed regression, independent of W03 PNG export.

Synthetic bytes only; no third-party images, packages, project writes or schema changes.
The trusted archive verifier is patched solely to exercise the second-stage
inflation/filter guard with otherwise valid dimensions.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
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


def _rgba_png(compressed, *, width=2, height=2):
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header) +
            _chunk(b"IDAT", compressed) + _chunk(b"IEND", b""))


# Two 2-pixel RGBA scanlines: 255,0 and 128,255 alpha, with filter 0.
# Foreground counts alpha >= 128, so this fixture contains three foreground pixels.
_ROWS = (b"\x00" + bytes((12, 34, 56, 255, 12, 34, 56, 0)) +
         b"\x00" + bytes((12, 34, 56, 128, 12, 34, 56, 255)))


class NativeAlphaDecoderFailClosedTests(unittest.TestCase):
    def decode(self, compressed, *, width=2, height=2):
        # _verify_png is independently tested in the workspace suite. Pin its
        # result here to exercise decompression guards even when archive
        # admission would reject malformed IDAT before reaching this decoder.
        with patch.object(first, "_verify_png", return_value=(width, height, "RGBA")):
            return first._rgba_alpha_mask(_rgba_png(compressed, width=width, height=height))

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


    def test_chained_predictors_three_rows_preserve_soft_alpha_and_bbox(self):
        # Each predictor must use the *reconstructed* previous scanline,
        # not the prior compressed residuals. RGB differs to catch byte
        # alignment errors even though only alpha is returned.
        rows = [
            bytes((10, 20, 30, 0, 40, 50, 60, 255)),
            bytes((70, 80, 90, 127, 100, 110, 120, 128)),
            bytes((130, 140, 150, 200, 160, 170, 180, 0)),
        ]
        def encode(row, above, predictor):
            out = bytearray()
            for i, value in enumerate(row):
                left = row[i - 4] if i >= 4 else 0
                up = above[i]
                corner = above[i - 4] if i >= 4 else 0
                if predictor == 4:
                    p = left + up - corner
                    distances = (abs(p - left), abs(p - up), abs(p - corner))
                    predicted = (left, up, corner)[distances.index(min(distances))]
                elif predictor == 3:
                    predicted = (left + up) // 2
                else:
                    predicted = 0
                out.append((value - predicted) & 255)
            return bytes((predictor,)) + bytes(out)
        baseline = b"".join(bytes((0,)) + row for row in rows)
        filtered = (encode(rows[0], bytes(8), 0) +
                    encode(rows[1], rows[0], 4) +
                    encode(rows[2], rows[1], 3))
        expected = self.decode(zlib.compress(baseline), height=3)
        actual = self.decode(zlib.compress(filtered), height=3)
        self.assertEqual(actual, expected)
        self.assertEqual(actual[1:], (2, 3, 3, (0, 0, 2, 3)))
        self.assertEqual(struct.unpack("<6f", actual[0])[3],
                         struct.unpack("<f", struct.pack("<f", 128 / 255))[0])

    def test_invalid_filter_is_rejected_without_reusing_previous_scanline(self):
        corrupted = b"\x05" + _ROWS[1:]
        with self.assertRaises(first.NativeFirstSubjectError) as ctx:
            self.decode(zlib.compress(corrupted))
        self.assertEqual(ctx.exception.code, "INVALID_ARCHIVED_SOURCE")
        self.assertEqual(self.decode(zlib.compress(_ROWS))[3], 3)

    def test_invalid_second_row_filter_rejects_after_valid_first_row(self):
        # The first scanline is valid: a late bad predictor must fail closed
        # instead of returning the first row or a partially decoded mask.
        corrupted = _ROWS[:9] + b"\x05" + _ROWS[10:]
        with self.assertRaises(first.NativeFirstSubjectError) as ctx:
            self.decode(zlib.compress(corrupted))
        self.assertEqual(ctx.exception.code, "INVALID_ARCHIVED_SOURCE")
        # A subsequent clean decode must not inherit partial decoder state.
        raw, width, height, foreground, bbox = self.decode(zlib.compress(_ROWS))
        self.assertEqual((width, height, foreground, bbox),
                         (2, 2, 3, (0, 0, 2, 2)))
        self.assertEqual(len(raw), 16)

    def test_parallel_valid_and_invalid_decodes_do_not_share_state(self):
        # Patch admission once outside worker threads: per-thread mock patching
        # would itself introduce shared mutable state into this regression.
        valid = _rgba_png(zlib.compress(_ROWS))
        invalid = _rgba_png(zlib.compress(_ROWS[:9] + bytes((5,)) + _ROWS[10:]))
        with patch.object(first, "_verify_png", return_value=(2, 2, "RGBA")):
            def run(index):
                try:
                    result = first._rgba_alpha_mask(valid if index % 2 == 0 else invalid)
                except first.NativeFirstSubjectError as exc:
                    return ("error", exc.code)
                return ("ok", result)
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(run, range(32)))
        expected = self.decode(zlib.compress(_ROWS))
        for index, result in enumerate(results):
            with self.subTest(index=index):
                if index % 2:
                    self.assertEqual(result, ("error", "INVALID_ARCHIVED_SOURCE"))
                else:
                    self.assertEqual(result, ("ok", expected))

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

    def test_corrupted_adler32_checksum_fails_closed_then_recovers(self):
        # Preserve the compressed payload and corrupt only the zlib trailer.
        # A decoder that stops at the expected byte count must still verify
        # the checksum rather than silently accepting a plausible alpha mask.
        valid = zlib.compress(_ROWS)
        corrupted = valid[:-1] + bytes((valid[-1] ^ 0x01,))
        with self.assertRaises(first.NativeFirstSubjectError) as ctx:
            self.decode(corrupted)
        self.assertEqual(ctx.exception.code, "INVALID_ARCHIVED_SOURCE")
        self.assertEqual(self.decode(valid)[3], 3)

    def test_invalid_zlib_header_is_rejected(self):
        with self.assertRaises(first.NativeFirstSubjectError) as ctx:
            self.decode(b"not a zlib stream")
        self.assertEqual(ctx.exception.code, "INVALID_ARCHIVED_SOURCE")


if __name__ == "__main__":
    unittest.main()
