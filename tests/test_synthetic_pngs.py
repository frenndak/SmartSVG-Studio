"""Cross-platform, dependency-free tests for original synthetic PNG fixtures."""
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from make_synthetic_pngs import synthesize, png_bytes


def unpack_png(path):
    data = path.read_bytes()
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("invalid PNG signature")
    p, idat, dims = 8, b"", None
    while p < len(data):
        length = int.from_bytes(data[p:p + 4], "big")
        tag = data[p + 4:p + 8]
        payload = data[p + 8:p + 8 + length]
        crc = int.from_bytes(data[p + 8 + length:p + 12 + length], "big")
        if (zlib.crc32(tag + payload) & 0xFFFFFFFF) != crc:
            raise ValueError("bad CRC")
        if tag == b"IHDR":
            dims = struct.unpack(">IIBBBBB", payload)
        if tag == b"IDAT":
            idat += payload
        p += 12 + length
        if tag == b"IEND":
            break
    pixels = zlib.decompress(idat)
    return dims, pixels


class SyntheticPNGTests(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.addCleanup(self.t.cleanup)
        self.root = Path(self.t.name)

    def test_generate_four_valid_rgba_pngs(self):
        files = synthesize(self.root)
        self.assertEqual(len(files), 4)
        for file in files:
            with self.subTest(file=file.name):
                dims, scanlines = unpack_png(file)
                self.assertEqual(dims, (144, 144, 8, 6, 0, 0, 0))
                self.assertEqual(len(scanlines), 144 * (1 + 144 * 4))
                self.assertEqual(scanlines[0], 0)
        self.assertEqual((self.root / "sticker_alpha.png").read_bytes(),
                         png_bytes(144, 144, lambda x, y:
                                   (0, 0, 0, 0) if not ((x-72)**2 + (y-72)**2 <= 62**2)
                                   else ((255, 225, 104, 255) if (x-72)**2+(y-72)**2 <= 28**2
                                         else (252, 155, 90, 255))))

    def test_transparency_and_opaque_controls(self):
        synthesize(self.root)
        _, a = unpack_png(self.root / "sticker_alpha.png")
        _, b = unpack_png(self.root / "photo_factice_opaque.png")
        self.assertEqual(a[4], 0)  # (0,0) transparent alpha
        self.assertEqual(b[4], 255)  # (0,0) opaque alpha
        self.assertEqual(a[72 * 577 + 1 + 72 * 4 + 3], 255)

    def test_no_overwrite(self):
        synthesize(self.root)
        with self.assertRaisesRegex(FileExistsError, "WILL_NOT_OVERWRITE"):
            synthesize(self.root)

    def test_invalid_size(self):
        with self.assertRaisesRegex(ValueError, "IMAGE_SIZE"):
            png_bytes(0, 1, lambda x, y: (0, 0, 0, 0))

    def test_invalid_rgba(self):
        with self.assertRaisesRegex(ValueError, "INVALID_RGBA"):
            png_bytes(1, 1, lambda x, y: (1, 2, 3, 999))


if __name__ == "__main__":
    unittest.main()
