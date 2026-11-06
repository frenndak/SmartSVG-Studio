"""V34-018/025 native creation positive and negative regression cases."""
import hashlib
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))
from smartsvg_core.native_png_create_v34 import create_native_png_project
from smartsvg_core.project_workspace_g22 import WorkspaceError
from smartsvg_core.project_archive import load_project


def chunk(kind, payload):
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(
        ">I", zlib.crc32(kind + payload) & 0xffffffff)


def png():
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00\xff")) +
            chunk(b"IEND", b""))


class NativePngCreationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "source.png"
        self.source.write_bytes(png())

    def test_create_reopen_and_preserve_original(self):
        result = create_native_png_project(self.root, "sample", self.source)
        archive = Path(result["archive"])
        self.assertTrue(archive.is_file())
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), result["sha256"])
        self.assertEqual(result["source_sha256"], hashlib.sha256(png()).hexdigest())
        loaded = load_project(archive)
        self.assertEqual(loaded.project_id, "sample")
        self.assertEqual(loaded.resources["sources/source-original.png"], png())
        self.assertFalse(result["cricut_certified"])

    def test_refuses_overwrite(self):
        create_native_png_project(self.root, "sample", self.source)
        with self.assertRaises(WorkspaceError) as caught:
            create_native_png_project(self.root, "sample", self.source)
        self.assertEqual(caught.exception.code, "PROJECT_ALREADY_EXISTS")

    def test_rejects_invalid_png_without_creating_project(self):
        self.source.write_bytes(b"not a png")
        with self.assertRaises(WorkspaceError):
            create_native_png_project(self.root, "invalid", self.source)
        self.assertFalse((self.root / "SmartSVG_Managed_Projects" / "invalid.smartsvg").exists())

    def test_rejects_symlink_source(self):
        link = self.root / "link.png"
        try:
            link.symlink_to(self.source)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaises(WorkspaceError) as caught:
            create_native_png_project(self.root, "linked", link)
        self.assertEqual(caught.exception.code, "INVALID_SOURCE_PATH")


if __name__ == "__main__":
    unittest.main()
