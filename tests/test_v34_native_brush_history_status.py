"""Native read-only brush-history status: revision, provenance, no writes."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from smartsvg_core.native_brush_history_v34 import inspect_native_brush_history
from smartsvg_core.native_subject_preview_v34 import (
    NativeSubjectPreviewError, preview_native_subject_stroke,
)
from smartsvg_core.native_subject_save_v34 import save_native_subject_stroke
from smartsvg_core.project_workspace_g22 import ManagedWorkspace, WorkspaceError
from test_v34_native_subject_preview import NativeSubjectPreviewTests, _png


SUBJECT = "subject-" + "a" * 32
REVISION = "b" * 64
_HAS_CPU = bool(importlib.util.find_spec("numpy") and
                importlib.util.find_spec("PIL"))


class NativeHistoryStatusTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.workspace = ManagedWorkspace(temp.name)
        self.name = "history-check"
        created = self.workspace.create(
            self.name, _png(), profile="Sticker - contour du sujet")
        self.sha = created["sha256"]
        self.path = self.workspace.root / (self.name + ".smartsvg")

    def request(self, **changes):
        args = {"project_path": str(self.path), "expected_sha256": self.sha}
        args.update(changes)
        return args

    @staticmethod
    def response(**changes):
        record = {
            "name": "history-check",
            "project_sha256": REVISION,
            "cricut_certified": False,
            "undo_available": True,
            "undo_subject_id": SUBJECT,
            "redo_available": False,
            "redo_error_code": "BRUSH_NOTHING_TO_REDO",
            "secret_internal_editor_document": {"strokes": ["private"]},
            "private_path": "not-to-be-disclosed",
            "float32": b"never-expose",
        }
        record.update(changes)
        return record

    def call_with_record(self, record):
        ws = SimpleNamespace(subject_brush_history=Mock(return_value=record),
                             change_subject_brush_history=Mock())
        with patch("smartsvg_core.native_brush_history_v34._workspace_from_path",
                   return_value=(ws, "history-check")):
            result = inspect_native_brush_history(
                project_path=str(self.path), expected_sha256=REVISION)
        ws.subject_brush_history.assert_called_once_with(
            "history-check", expected_sha256=REVISION)
        ws.change_subject_brush_history.assert_not_called()
        return result

    def test_real_v1_without_strokes_reports_unavailable_and_is_readonly(self):
        original = self.path.read_bytes()
        status = inspect_native_brush_history(**self.request())
        self.assertEqual(status["project_sha256"], self.sha)
        self.assertFalse(status["undo_available"])
        self.assertFalse(status["redo_available"])
        self.assertTrue(status["undo_reason"].startswith("BRUSH_"))
        self.assertTrue(status["redo_reason"].startswith("BRUSH_"))
        self.assertIs(status["persisted"], False)
        self.assertIs(status["cricut_certified"], False)
        self.assertEqual(self.path.read_bytes(), original)
        self.assertNotIn("editor_document", status)

    def test_status_is_a_strict_whitelist_without_pixels_or_paths(self):
        status = self.call_with_record(self.response())
        self.assertEqual(status["schema"], "smartsvg-native-brush-history-status/1")
        self.assertTrue(status["undo_available"])
        self.assertEqual(status["undo_subject_id"], SUBJECT)
        self.assertFalse(status["redo_available"])
        self.assertEqual(status["redo_reason"], "BRUSH_NOTHING_TO_REDO")
        self.assertEqual(status["project_sha256"], REVISION)
        for private in ("private_path", "float32", "secret_internal_editor_document",
                        "undo_error_code", "redo_subject_id"):
            self.assertNotIn(private, status)

    def test_invalid_history_metadata_cannot_be_presented_as_available(self):
        changes = (
            {"project_sha256": "c" * 64},
            {"name": "other-project"},
            {"cricut_certified": True},
            {"undo_available": 1},
            {"redo_available": "yes"},
            {"undo_subject_id": "forged"},
            {"undo_subject_id": 10},
            {"redo_error_code": None},
            {"redo_error_code": "PRIVATE:/home/user/file"},
        )
        for change in changes:
            with self.subTest(change=change):
                with self.assertRaises(NativeSubjectPreviewError) as error:
                    self.call_with_record(self.response(**change))
                self.assertEqual(error.exception.code,
                                 "INVALID_BRUSH_HISTORY_STATUS")
        for malformed in (None, 1, [], "unexpected"):
            with self.subTest(payload=repr(malformed)):
                with self.assertRaises(NativeSubjectPreviewError):
                    self.call_with_record(malformed)

    def test_stale_revision_and_unmanaged_location_fail_before_read(self):
        before = self.path.read_bytes()
        with self.assertRaises(NativeSubjectPreviewError) as error:
            inspect_native_brush_history(
                **self.request(expected_sha256="0" * 64))
        self.assertEqual(error.exception.code, "PROJECT_CHANGED")
        for invalid in ("bad-sha", "", None, True):
            with self.subTest(revision=invalid):
                with self.assertRaises(NativeSubjectPreviewError) as failure:
                    inspect_native_brush_history(
                        **self.request(expected_sha256=invalid))
                self.assertEqual(failure.exception.code,
                                 "EXPECTED_REVISION_REQUIRED")
        with self.assertRaises(NativeSubjectPreviewError):
            inspect_native_brush_history(
                **self.request(project_path="foreign.smartsvg"))
        self.assertEqual(self.path.read_bytes(), before)

    def test_workspace_failure_keeps_error_code_and_no_writer(self):
        ws = SimpleNamespace(subject_brush_history=Mock(
            side_effect=WorkspaceError("PROJECT_NOT_HEALTHY")),
            change_subject_brush_history=Mock())
        with patch("smartsvg_core.native_brush_history_v34._workspace_from_path",
                   return_value=(ws, "history-check")):
            with self.assertRaises(NativeSubjectPreviewError) as error:
                inspect_native_brush_history(
                    project_path=str(self.path), expected_sha256=REVISION)
        self.assertEqual(error.exception.code, "PROJECT_NOT_HEALTHY")
        ws.change_subject_brush_history.assert_not_called()

    @unittest.skipUnless(_HAS_CPU, "G3.3e real CPU requires NumPy/Pillow")
    def test_real_cpu_stroke_exposes_only_history_status_after_save(self):
        # Reuse the real two-mask synthetic V1 fixture from the native CPU bridge.
        NativeSubjectPreviewTests.setUp(self)
        command = dict(project_path=str(self.path),
                       expected_sha256=self.sha, subject_id=self.subject_id,
                       mode="add", radius=0.05, points=[[0.5, 0.5]])
        preview = preview_native_subject_stroke(**command)
        saved = save_native_subject_stroke(
            **command,
            expected_preview_mask_sha256_float32=preview[
                "preview_mask_sha256_float32"],
            command_id="history-status-fixture", confirmed=True)
        current_sha = saved["project_sha256"]
        before = self.path.read_bytes()
        result = inspect_native_brush_history(
            project_path=str(self.path), expected_sha256=current_sha)
        self.assertTrue(result["undo_available"])
        self.assertEqual(result["undo_subject_id"], self.subject_id)
        self.assertFalse(result["redo_available"])
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(set(result), {
            "schema", "project_sha256", "undo_available", "redo_available",
            "persisted", "cricut_certified", "undo_subject_id", "redo_reason"})


if __name__ == "__main__":
    unittest.main()
