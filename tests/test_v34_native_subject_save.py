"""V34-132 native explicit-save bridge: no second V1 writer or implicit save."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from smartsvg_core.native_subject_preview_v34 import (
    NativeSubjectPreviewError, preview_native_subject_stroke,
)
from smartsvg_core.native_subject_save_v34 import save_native_subject_stroke
from smartsvg_core.project_archive import load_project
from smartsvg_core.project_workspace_g22 import ManagedWorkspace
from test_v34_native_subject_preview import NativeSubjectPreviewTests

_HAS_CPU = bool(importlib.util.find_spec("numpy") and
                importlib.util.find_spec("PIL"))


class NativeSubjectSaveTests(unittest.TestCase):
    def setUp(self):
        # Exactly the same real, synthetic V1 project / two-mask fixture
        # already used for the strict read-only native CPU bridge.
        NativeSubjectPreviewTests.setUp(self)

    command = NativeSubjectPreviewTests.command
    bytes_before = NativeSubjectPreviewTests.bytes_before

    def save(self, digest, *, confirmed=True, command_id="native-brush-save-001",
             **changes):
        return save_native_subject_stroke(
            **self.command(**changes),
            expected_preview_mask_sha256_float32=digest,
            command_id=command_id, confirmed=confirmed,
        )

    def test_absent_or_false_confirmation_never_calls_writer(self):
        before = self.bytes_before()
        with patch.object(ManagedWorkspace, "save_subject_brush") as writer:
            for value in (False, None, "yes", 1, 0):
                with self.subTest(value=value):
                    with self.assertRaises(NativeSubjectPreviewError) as error:
                        self.save("0" * 64, confirmed=value)
                    self.assertEqual(error.exception.code,
                                     "BRUSH_SAVE_CONFIRMATION_REQUIRED")
            writer.assert_not_called()
        self.assertEqual(self.bytes_before(), before)

    def test_bad_command_and_unmanaged_path_refuse_before_writer(self):
        before = self.bytes_before()
        for bad in ("", " " * 5, "a" * 129, "../escape"):
            with self.subTest(command_id=bad):
                with self.assertRaises(NativeSubjectPreviewError) as error:
                    self.save("0" * 64, command_id=bad)
                self.assertEqual(error.exception.code, "INVALID_BRUSH_SAVE_REQUEST")
        with self.assertRaises(NativeSubjectPreviewError) as error:
            self.save("0" * 64, project_path="not-an-absolute.smartsvg")
        self.assertIn(error.exception.code, ("INVALID_PROJECT_PATH",
                                              "UNMANAGED_PROJECT"))
        self.assertEqual(self.bytes_before(), before)

    @unittest.skipUnless(_HAS_CPU, "Real V1 CPU needs NumPy/Pillow")
    def test_confirmed_real_cpu_save_reopens_and_preserves_original_resources(self):
        preview = preview_native_subject_stroke(**self.command())
        before = self.path.read_bytes()
        original = load_project(self.path)
        saved = self.save(preview["preview_mask_sha256_float32"])
        self.assertEqual(saved["status"], "subject_brush_saved")
        self.assertEqual(saved["subject_id"], self.subject_id)
        self.assertEqual(saved["command_id"], "native-brush-save-001")
        self.assertIs(saved["persisted"], True)
        self.assertIs(saved["cricut_certified"], False)
        self.assertNotEqual(self.path.read_bytes(), before)
        self.assertEqual(self.workspace.inspect(self.name)["sha256"],
                         saved["project_sha256"])
        reopened = load_project(self.path)
        self.assertEqual(reopened.resources, original.resources)
        self.assertEqual(reopened.masks, original.masks)
        self.assertEqual(reopened.subjects, original.subjects)
        self.assertEqual(len(reopened.document["editor_v216"]["strokes"]), 1)
        self.assertEqual(reopened.document["editor_v216"]["strokes"][0]["object"], 0)
        self.assertEqual(
            self.path.with_name(self.name + ".previous.smartsvg").read_bytes(),
            before,
        )
        after = self.bytes_before()
        # No false idempotent "saved" response against an old V1 revision.
        with self.assertRaises(NativeSubjectPreviewError) as error:
            self.save(preview["preview_mask_sha256_float32"])
        self.assertEqual(error.exception.code, "PROJECT_CHANGED")
        self.assertEqual(self.bytes_before(), after)

    @unittest.skipUnless(_HAS_CPU, "Real V1 CPU needs NumPy/Pillow")
    def test_writer_committed_but_malformed_receipt_requires_reinspection(self):
        preview = preview_native_subject_stroke(**self.command())
        before = self.path.read_bytes()
        actual_writer = ManagedWorkspace.save_subject_brush

        def committed_with_bad_receipt(workspace, *args, **kwargs):
            actual_writer(workspace, *args, **kwargs)
            return {"status": "unexpected", "persisted": False}

        with patch.object(ManagedWorkspace, "save_subject_brush",
                          autospec=True, side_effect=committed_with_bad_receipt):
            with self.assertRaises(NativeSubjectPreviewError) as error:
                self.save(preview["preview_mask_sha256_float32"])
        self.assertEqual(error.exception.code, "BRUSH_SAVE_OUTCOME_UNKNOWN")
        self.assertNotEqual(self.path.read_bytes(), before)
        self.assertEqual(
            self.path.with_name(self.name + ".previous.smartsvg").read_bytes(),
            before,
        )
        # A stale retry cannot overwrite the committed project.
        after = self.bytes_before()
        with self.assertRaises(NativeSubjectPreviewError) as error:
            self.save(preview["preview_mask_sha256_float32"])
        self.assertEqual(error.exception.code, "PROJECT_CHANGED")
        self.assertEqual(self.bytes_before(), after)

    @unittest.skipUnless(_HAS_CPU, "Real V1 CPU needs NumPy/Pillow")
    def test_wrong_preview_fingerprint_fails_closed_without_writes(self):
        preview = preview_native_subject_stroke(**self.command())
        bad = ("0" if preview["preview_mask_sha256_float32"][0] != "0"
               else "1") + preview["preview_mask_sha256_float32"][1:]
        before = self.bytes_before()
        with patch.object(ManagedWorkspace, "save_subject_brush") as writer:
            with self.assertRaises(NativeSubjectPreviewError) as error:
                self.save(bad)
            self.assertEqual(error.exception.code, "BRUSH_PREVIEW_CHANGED")
            writer.assert_not_called()
        self.assertEqual(self.bytes_before(), before)

    @unittest.skipUnless(_HAS_CPU, "Real V1 CPU needs NumPy/Pillow")
    def test_stale_project_and_forged_subject_do_not_overwrite(self):
        preview = preview_native_subject_stroke(**self.command())
        before = self.bytes_before()
        with self.assertRaises(NativeSubjectPreviewError) as error:
            self.save(preview["preview_mask_sha256_float32"],
                      subject_id="subject-" + "f" * 32)
        self.assertEqual(error.exception.code, "SUBJECT_NOT_VERIFIED")
        self.assertEqual(self.bytes_before(), before)

        self.workspace.update_notes(self.name, notes="Concurrent legitimate note",
                                    expected_sha256=self.sha)
        current = self.bytes_before()
        with self.assertRaises(NativeSubjectPreviewError) as error:
            self.save(preview["preview_mask_sha256_float32"])
        self.assertEqual(error.exception.code, "PROJECT_CHANGED")
        self.assertEqual(self.bytes_before(), current)


if __name__ == "__main__":
    unittest.main()
