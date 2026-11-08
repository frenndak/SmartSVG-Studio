"""V34-132 native bridge: exact Subject evidence, revision pins and no writes."""
import importlib.util
from hashlib import sha256
from pathlib import Path
import struct
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import zlib

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from smartsvg_core.native_subject_preview_v34 import (
    NativeSubjectPreviewError, preview_native_subject_stroke,
)
from smartsvg_core.project_workspace_g22 import ManagedWorkspace, WorkspaceError


def _png(width=16, height=12):
    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data +
                struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff))
    row = b"\x00" + bytes([95]) * (width * 4)
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(row * height)) +
            chunk(b"IEND", b""))


class NativeSubjectPreviewTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.workspace = ManagedWorkspace(temp.name)
        self.name = "native-subject"
        created = self.workspace.create(self.name, _png(),
            profile="Sticker - contour du sujet")
        first = [0.0] * (16 * 12)
        second = [0.0] * (16 * 12)
        first[6 * 16 + 8] = 0.6
        second[3 * 16 + 3] = 0.75
        raw = struct.pack("<384f", *(first + second))
        self.workspace.save_base_masks(
            self.name, raw_float32=raw, shape=[2, 12, 16],
            image_fingerprint="b" * 64, editor_fingerprint="a" * 64,
            expected_sha256=created["sha256"])
        catalog = self.workspace.inspect(self.name)["base_masks"]["mask_identity"]
        self.binding = catalog["bindings"][0]
        registered = self.workspace.register_subject_identity(
            self.name, mask_index=0, mask_id=self.binding["mask_id"],
            mask_sha256_float32=self.binding["mask_sha256_float32"],
            source_id=catalog["source_id"], source_sha256="a" * 64,
            expected_sha256=self.workspace.inspect(self.name)["sha256"],
            confirmed=True, expires_at_ms=int(time.time() * 1000) + 60_000)
        self.subject_id = registered["subject_id"]
        self.path = self.workspace.root / (self.name + ".smartsvg")
        self.sha = self.workspace.inspect(self.name)["sha256"]

    def command(self, **changes):
        args = dict(project_path=str(self.path), expected_sha256=self.sha,
                    subject_id=self.subject_id, mode="add",
                    radius=0.05, points=[[0.5, 0.5]])
        args.update(changes)
        return args

    def bytes_before(self):
        return {p.name: p.read_bytes()
                for p in self.workspace.root.iterdir() if p.is_file()}

    def test_verified_subject_resolves_index_only_in_backend_and_restricts_output(self):
        before = self.bytes_before()
        backend = dict(project_sha256=self.sha, subject_id=self.subject_id,
            mask_id=self.binding["mask_id"], before_png_l8=b"before",
            after_png_l8=b"after", dimensions_px=[16, 12],
            changed_pixels=4, preview_mask_sha256_float32="e" * 64,
            persisted=False, preview_float32=b"secret-float32",
            editor_document={"strokes": [1]}, private_path="never-expose")
        with patch.object(ManagedWorkspace, "preview_subject_brush_readonly",
                          return_value=backend) as preview:
            result = preview_native_subject_stroke(**self.command())
        preview.assert_called_once()
        kwargs = preview.call_args.kwargs
        self.assertEqual(kwargs["subject_id"], self.subject_id)
        self.assertEqual(kwargs["mask_id"], self.binding["mask_id"])
        self.assertEqual(kwargs["mask_sha256_float32"],
                         self.binding["mask_sha256_float32"])
        self.assertEqual(kwargs["source_id"], "source-original")
        self.assertEqual(kwargs["source_sha256"], "a" * 64)
        self.assertEqual(kwargs["expected_sha256"], self.sha)
        self.assertNotIn("mask_index", kwargs)
        self.assertNotIn("preview_float32", result)
        self.assertNotIn("editor_document", result)
        self.assertNotIn("private_path", result)
        self.assertEqual(result["changed_pixels"], 4)
        self.assertIs(result["persisted"], False)
        self.assertIs(result["cricut_certified"], False)
        self.assertEqual(self.bytes_before(), before)

    def test_reject_missing_wrong_or_unverified_selection_before_backend(self):
        before = self.bytes_before()
        bad_cases = [
            ({"subject_id": "subject-" + "f" * 32}, "SUBJECT_NOT_VERIFIED"),
            ({"subject_id": "subject-invalid"}, "INVALID_SUBJECT_ID"),
            ({"expected_sha256": "0" * 64}, "PROJECT_CHANGED"),
            ({"expected_sha256": "invalid"}, "EXPECTED_REVISION_REQUIRED"),
        ]
        with patch.object(ManagedWorkspace, "preview_subject_brush_readonly") as preview:
            for change, error in bad_cases:
                with self.subTest(error=error), self.assertRaises(NativeSubjectPreviewError) as context:
                    preview_native_subject_stroke(**self.command(**change))
                self.assertEqual(context.exception.code, error)
            preview.assert_not_called()
        self.assertEqual(self.bytes_before(), before)

    def test_project_without_masks_never_produces_brush_preview(self):
        created = self.workspace.create("empty-native", _png(),
                                        profile="Sticker - contour du sujet")
        path = self.workspace.root / "empty-native.smartsvg"
        before = path.read_bytes()
        with self.assertRaises(NativeSubjectPreviewError) as context:
            preview_native_subject_stroke(
                **self.command(project_path=str(path),
                               expected_sha256=created["sha256"]))
        self.assertEqual(context.exception.code, "NO_VERIFIED_MASKS")
        self.assertEqual(path.read_bytes(), before)

    def test_unmanaged_paths_refused_without_workspace_or_file_writes(self):
        before = self.bytes_before()
        outside = self.path.parent.parent / "outside.smartsvg"
        outside.write_bytes(self.path.read_bytes())
        outside_bytes = outside.read_bytes()
        for path in (str(outside), str(self.path.with_name("native-subject.previous.smartsvg")),
                     str(self.path.parent.parent), "relative.smartsvg", "\x00bad.smartsvg"):
            with self.subTest(path=repr(path)), self.assertRaises(NativeSubjectPreviewError) as context:
                preview_native_subject_stroke(**self.command(project_path=path))
            self.assertIn(context.exception.code, {"UNMANAGED_PROJECT", "INVALID_PROJECT_PATH"})
        self.assertEqual(outside.read_bytes(), outside_bytes)
        self.assertEqual(self.bytes_before(), before)

    def test_existing_backend_revision_failure_is_explicit_and_read_only(self):
        before = self.bytes_before()
        with patch.object(ManagedWorkspace, "preview_subject_brush_readonly",
                          side_effect=WorkspaceError("PROJECT_CHANGED_DURING_PREVIEW")):
            with self.assertRaises(NativeSubjectPreviewError) as context:
                preview_native_subject_stroke(**self.command())
        self.assertEqual(context.exception.code, "PROJECT_CHANGED_DURING_PREVIEW")
        self.assertEqual(self.bytes_before(), before)

    def test_changed_backend_identity_is_never_presented_as_valid(self):
        before = self.bytes_before()
        with patch.object(ManagedWorkspace, "preview_subject_brush_readonly",
                          return_value={"project_sha256": self.sha,
                                        "subject_id": "subject-" + "f" * 32,
                                        "mask_id": self.binding["mask_id"],
                                        "persisted": False}):
            with self.assertRaises(NativeSubjectPreviewError) as context:
                preview_native_subject_stroke(**self.command())
        self.assertEqual(context.exception.code, "PREVIEW_IDENTITY_CHANGED")
        self.assertEqual(self.bytes_before(), before)

    @unittest.skipUnless(importlib.util.find_spec("numpy") and
                         importlib.util.find_spec("PIL"),
                         "Native CPU brush needs NumPy and Pillow")
    def test_real_cpu_preview_preserves_archive_and_other_subject(self):
        before = self.bytes_before()
        result = preview_native_subject_stroke(**self.command())
        self.assertEqual(result["subject_id"], self.subject_id)
        self.assertEqual(result["project_sha256"], self.sha)
        self.assertEqual(result["dimensions_px"], [16, 12])
        self.assertGreater(result["changed_pixels"], 0)
        self.assertNotEqual(result["before_png_l8"], result["after_png_l8"])
        self.assertTrue(result["before_png_l8"].startswith(b"\x89PNG"))
        self.assertTrue(result["after_png_l8"].startswith(b"\x89PNG"))
        self.assertEqual(self.bytes_before(), before)


if __name__ == "__main__":
    unittest.main()
