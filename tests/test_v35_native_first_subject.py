"""W02 native first Subject: actual V1 writer, archive and RGBA filter regressions."""
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

from smartsvg_core import native_first_subject_v35 as first
from smartsvg_core.mask_binding_g33e import snapshot_mask_bindings
from smartsvg_core.mask_snapshot_g24 import SNAPSHOT_KEY, decode_snapshot, SNAPSHOT_PATH
from smartsvg_core.project_archive import load_project
from smartsvg_core.project_workspace_g22 import ManagedWorkspace, WorkspaceError


def _chunk(name, raw):
    return (struct.pack(">I", len(raw)) + name + raw +
            struct.pack(">I", zlib.crc32(name + raw) & 0xffffffff))


def _paeth(a, b, c):
    p = a + b - c
    da, db, dc = abs(p - a), abs(p - b), abs(p - c)
    return a if da <= db and da <= dc else b if db <= dc else c


def png(*, width=6, height=5, rgba=True, opacity="silhouette", filters=True):
    channels = 4 if rgba else 3
    prev = bytes(width * channels)
    lines = []
    for y in range(height):
        pixel = bytearray()
        for x in range(width):
            alpha = (128 if x == 3 and y == 3 else 255) if (
                1 <= x <= 3 and 1 <= y <= 3) else 0
            if opacity == "opaque":
                alpha = 255
            elif opacity == "empty":
                alpha = 0
            pixel.extend((30 + x, 50 + y, 70, alpha) if rgba
                         else (30 + x, 50 + y, 70))
        kind = y % 5 if filters else 0
        filtered = bytearray()
        for i, item in enumerate(pixel):
            a = pixel[i - channels] if i >= channels else 0
            b = prev[i]
            c = prev[i - channels] if i >= channels else 0
            predictor = (0, a, b, (a + b) // 2, _paeth(a, b, c))[kind]
            filtered.append((item - predictor) & 255)
        lines.append(bytes([kind]) + bytes(filtered))
        prev = bytes(pixel)
    header = struct.pack(">IIBBBBB", width, height, 8, 6 if rgba else 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", header) + _chunk(
        b"IDAT", zlib.compress(b"".join(lines))) + _chunk(b"IEND", b"")


class FirstAlphaSubjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = ManagedWorkspace(self.temp.name)
        self.name = "alpha-source"
        self.source = png()
        created = self.workspace.create(
            self.name, self.source, profile="Sticker - contour du sujet",
            source_provenance="manual_native_png_import")
        self.initial_sha = created["sha256"]
        self.path = self.workspace.root / (self.name + ".smartsvg")

    def state(self):
        return self.workspace.inspect(self.name)

    def files(self):
        return {p.name: p.read_bytes() for p in self.workspace.root.iterdir()
                if p.is_file()}

    def inspect(self, sha=None):
        return first.inspect_first_alpha_subject(
            project_path=str(self.path),
            expected_sha256=sha or self.state()["sha256"])

    def confirm(self, preview, sha=None):
        return first.confirm_first_alpha_subject(
            project_path=str(self.path),
            expected_sha256=sha or preview["project_sha256"],
            candidate_sha256=preview["candidate_sha256"],
            confirmed=True)

    def test_all_png_filters_decode_exact_alpha_and_inspection_never_writes(self):
        before = self.files()
        preview = self.inspect()
        self.assertEqual(preview["status"], "ALPHA_PREVIEW_READY")
        self.assertEqual(preview["dimensions_px"], [6, 5])
        self.assertEqual(preview["bbox_px"], [1, 1, 3, 3])
        self.assertEqual(preview["foreground_pixels"], 9)
        self.assertTrue(preview["preview_only"])
        self.assertFalse(preview["persisted"])
        self.assertFalse(preview["cricut_certified"])
        self.assertNotIn("raw_float32", preview)
        self.assertEqual(self.files(), before)
        raw, width, height, foreground, _box = first._rgba_alpha_mask(self.source)
        self.assertEqual((width, height, foreground), (6, 5, 9))
        self.assertEqual(struct.unpack("<f", raw[(3 * 6 + 3) * 4:(3 * 6 + 4) * 4])[0],
                         struct.unpack("<f", struct.pack("<f", 128 / 255))[0])
        self.assertEqual(struct.unpack("<f", raw[:4])[0], 0.0)

    def test_explicit_confirmation_uses_existing_writer_and_reopens_verified_subject(self):
        before = load_project(self.path)
        preview = self.inspect()
        self.assertEqual(before.subjects, ())
        receipt = self.confirm(preview)
        self.assertEqual(receipt["status"], "FIRST_SUBJECT_CREATED")
        self.assertRegex(receipt["subject_id"], r"^subject-[0-9a-f]{32}$")
        self.assertTrue(receipt["persisted"])
        self.assertFalse(receipt["cricut_certified"])
        self.assertNotEqual(receipt["project_sha256"], preview["project_sha256"])
        after = load_project(self.path, expected_sha256=receipt["project_sha256"])
        self.assertEqual(after.resources["sources/source-original.png"], self.source)
        self.assertEqual(len(after.subjects), 1)
        self.assertEqual(len(after.masks), 1)
        self.assertEqual(after.subjects[0].bbox_px, (1, 1, 3, 3))
        self.assertEqual(list(after.subjects[0].bbox_px), preview["bbox_px"])
        self.assertEqual(after.subjects[0].subject_id, receipt["subject_id"])
        proof = snapshot_mask_bindings(after)
        self.assertEqual(proof["bindings"][0]["subject_proof_status"], "verified")
        meta = after.document[SNAPSHOT_KEY]
        raw = decode_snapshot(meta, after.resources[SNAPSHOT_PATH])
        self.assertEqual(sha256(raw).hexdigest(), preview["candidate_sha256"])
        with self.assertRaises(first.NativeFirstSubjectError) as mismatch:
            self.confirm(preview)
        self.assertEqual(mismatch.exception.code, "PROJECT_CHANGED")

    def test_declined_or_stale_confirmation_has_no_side_effect(self):
        preview = self.inspect()
        before = self.files()
        with self.assertRaises(first.NativeFirstSubjectError) as no:
            first.confirm_first_alpha_subject(
                project_path=str(self.path),
                expected_sha256=preview["project_sha256"],
                candidate_sha256=preview["candidate_sha256"],
                confirmed=False)
        self.assertEqual(no.exception.code, "ALPHA_CONFIRMATION_REQUIRED")
        with self.assertRaises(first.NativeFirstSubjectError) as changed:
            first.confirm_first_alpha_subject(
                project_path=str(self.path),
                expected_sha256=preview["project_sha256"],
                candidate_sha256="f" * 64, confirmed=True)
        self.assertEqual(changed.exception.code, "ALPHA_CANDIDATE_CHANGED")
        self.assertEqual(self.files(), before)

    def test_first_mask_phase_can_be_resumed_only_by_a_new_explicit_confirmation(self):
        preview = self.inspect()
        original = ManagedWorkspace.save_base_masks
        def commit_then_fail(workspace, *args, **kwargs):
            original(workspace, *args, **kwargs)
            raise WorkspaceError("IO_LOST_AFTER_PUBLICATION")
        with patch.object(ManagedWorkspace, "save_base_masks", commit_then_fail):
            with self.assertRaises(first.NativeFirstSubjectError) as error:
                self.confirm(preview)
        self.assertEqual(error.exception.code, "MASK_PUBLICATION_UNCERTAIN")
        partial = load_project(self.path)
        self.assertEqual(len(partial.masks), 1)
        self.assertFalse(partial.subjects)
        self.assertEqual(partial.resources["sources/source-original.png"], self.source)
        with self.assertRaises(first.NativeFirstSubjectError) as stale:
            self.confirm(preview)
        self.assertEqual(stale.exception.code, "PROJECT_CHANGED")
        renewed = self.inspect()
        self.assertEqual(renewed["status"], "RESUME_MASK_BINDING")
        with patch.object(ManagedWorkspace, "save_base_masks",
                          side_effect=AssertionError("must not re-write mask")):
            receipt = self.confirm(renewed)
        self.assertEqual(receipt["status"], "FIRST_SUBJECT_CREATED")
        self.assertEqual(snapshot_mask_bindings(load_project(self.path))
                         ["bindings"][0]["subject_proof_status"], "verified")

    def test_new_alpha_subject_runs_real_cpu_brush_preview_when_available(self):
        # G0 deliberately has no third-party CPU packages; the Windows
        # stability runner installs them and must execute this test.
        import importlib.util
        if not all(importlib.util.find_spec(name) is not None
                   for name in ("numpy", "PIL", "cv2")):
            self.skipTest("Native CPU brush dependencies unavailable in G0")
        from smartsvg_core.native_subject_preview_v34 import preview_native_subject_stroke
        preview = self.inspect()
        receipt = self.confirm(preview)
        before = self.files()
        result = preview_native_subject_stroke(
            project_path=str(self.path),
            expected_sha256=receipt["project_sha256"],
            subject_id=receipt["subject_id"],
            mode="add", radius=0.05, points=[[0.5, 0.5]])
        self.assertIs(result["persisted"], False)
        self.assertEqual(result["subject_id"], receipt["subject_id"])
        self.assertEqual(result["project_sha256"], receipt["project_sha256"])
        self.assertIs(result["cricut_certified"], False)
        self.assertEqual(self.files(), before)

    def test_lost_binding_ack_never_retries_a_committed_subject(self):
        preview = self.inspect()
        original = ManagedWorkspace.register_subject_identity
        def bind_then_fail(workspace, *args, **kwargs):
            original(workspace, *args, **kwargs)
            raise WorkspaceError("ACK_LOST_AFTER_SUBJECT_COMMIT")

        with patch.object(ManagedWorkspace, "register_subject_identity", bind_then_fail):
            with self.assertRaises(first.NativeFirstSubjectError) as error:
                self.confirm(preview)
        self.assertEqual(error.exception.code, "SUBJECT_BINDING_OUTCOME_UNCERTAIN")
        reopened = load_project(self.path)
        self.assertEqual(len(reopened.subjects), 1)
        self.assertEqual(len(reopened.masks), 1)
        self.assertEqual(reopened.resources["sources/source-original.png"], self.source)
        with self.assertRaises(first.NativeFirstSubjectError) as stale:
            self.confirm(preview)
        self.assertEqual(stale.exception.code, "PROJECT_CHANGED")
        with self.assertRaises(first.NativeFirstSubjectError) as already:
            self.inspect()
        self.assertEqual(already.exception.code, "SUBJECT_ALREADY_PRESENT")
        self.assertEqual(len(load_project(self.path).subjects), 1)

    def test_existing_different_mask_is_not_silently_replaced(self):
        raw = struct.pack("<30f", *([1.0] * 30))
        state = self.state()
        self.workspace.save_base_masks(
            self.name, raw_float32=raw, shape=[1, 5, 6],
            image_fingerprint="a" * 64, editor_fingerprint="b" * 64,
            expected_sha256=state["sha256"])
        before = self.files()
        with self.assertRaises(first.NativeFirstSubjectError) as context:
            self.inspect()
        self.assertEqual(context.exception.code, "EXISTING_MASK_REQUIRES_REVIEW")
        self.assertEqual(self.files(), before)

    def test_non_rgba_and_opaque_images_need_explicit_manual_selection(self):
        for data in (png(rgba=False), png(opacity="opaque"),
                     png(opacity="empty")):
            with self.subTest(data=sha256(data).hexdigest()):
                with self.assertRaises(first.NativeFirstSubjectError) as error:
                    first._rgba_alpha_mask(data)
                self.assertEqual(error.exception.code, "MANUAL_SELECTION_REQUIRED")

    def test_invalid_sha_or_unmanaged_project_is_refused_before_write(self):
        before = self.files()
        for version in ("f" * 64, "invalid", None):
            with self.subTest(version=version):
                with self.assertRaises(first.NativeFirstSubjectError):
                    first.inspect_first_alpha_subject(
                        project_path=str(self.path), expected_sha256=version)
        with self.assertRaises(first.NativeFirstSubjectError):
            first.inspect_first_alpha_subject(
                project_path=str(Path(self.temp.name) / "other.smartsvg"),
                expected_sha256=self.initial_sha)
        self.assertEqual(self.files(), before)


if __name__ == "__main__":
    unittest.main()
