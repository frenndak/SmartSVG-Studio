"""G3.3e-b2b-1: first confirmed stroke, native V1 replay, atomic save.

V34-132/133 and inherited G3.3e: no base-mask mutation or new archive format.
This slice deliberately refuses a nonempty prior editor session; composing
previews, multi-stroke editing and Undo/Redo belong to the following slice.
"""
from dataclasses import replace
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
import test_g33e_subject_brush_preview as fixtures
from smartsvg_core.project_archive import load_project
from smartsvg_core.project_workspace_g22 import WorkspaceError
from smartsvg_core import project_recovery
from smartsvg_core.subject_brush_preview_g33e import preview_subject_brush


@unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'),
                     'CPU brush dependencies not installed in stdlib-only G0')
class SubjectBrushSaveTests(unittest.TestCase):
    def setUp(self):
        fixtures.SubjectBrushPreviewTests.setUp(self)

    def request(self, **changes):
        project, stroke = fixtures.SubjectBrushPreviewTests.command(self, **changes)
        preview = preview_subject_brush(project, **stroke)
        request = dict(
            **stroke, expected_sha256=sha256(self.path.read_bytes()).hexdigest(),
            expected_preview_mask_sha256_float32=preview["preview_mask_sha256_float32"],
            command_id="brush-command-001", confirmed=True)
        request.update(changes)
        return request

    def save(self, request):
        return self.workspace.save_subject_brush("brush-preview", **request)

    def files(self):
        return {p.name: p.read_bytes() for p in self.path.parent.iterdir() if p.is_file()}

    def test_confirmed_save_roundtrips_stroke_without_changing_any_resource(self):
        request = self.request(mode="erase")
        project, stroke = fixtures.SubjectBrushPreviewTests.command(self, mode="erase")
        before_bytes = self.path.read_bytes()
        result = self.save(request)
        reopened = load_project(self.path)
        self.assertEqual(result["status"], "subject_brush_saved")
        self.assertTrue(result["persisted"])
        self.assertFalse(result["cricut_certified"])
        self.assertEqual(result["sha256"], sha256(self.path.read_bytes()).hexdigest())
        self.assertEqual(reopened.resources, project.resources)
        self.assertEqual(reopened.subjects, project.subjects)
        self.assertEqual(reopened.masks, project.masks)
        self.assertEqual(reopened.document["editor_v216"], {
            "version": 1, "width": 16, "height": 12, "count": 2,
            "source": "a" * 64, "strokes": [
                {"object": 0, "mode": "erase", "radius": 0.05, "points": [[0.5, 0.5]]}]})
        self.assertEqual(len(reopened.operations), len(project.operations) + 1)
        self.assertEqual(self.path.with_name("brush-preview.previous.smartsvg").read_bytes(), before_bytes)
        # Existing G2.3 consumer can reopen it without a new reader/schema.
        session = json.loads(self.workspace.editor_document("brush-preview")["editor_json"])
        self.assertEqual(session, reopened.document["editor_v216"])
        # Replay through the existing V21.6 engine, rather than trusting JSON.
        import numpy as np
        import struct
        from smartsvg_editor.strokes import apply_strokes
        raw, meta = self.workspace.base_masks("brush-preview", expected_sha256=result["sha256"])
        corrected = apply_strokes(np.frombuffer(raw, dtype='<f4').reshape(2, 12, 16), session['strokes'])
        self.assertEqual(corrected[0, 6, 8], 0.0)
        self.assertEqual(struct.pack('<f', corrected[0, 0, 0]), struct.pack('<f', 0.35))
        self.assertEqual(corrected[1].tobytes(), struct.pack('<192f', *self.second))

    def test_second_subject_resolves_to_its_own_replay_index(self):
        project, stroke = fixtures.SubjectBrushPreviewTests.command(self, index=1)
        preview = preview_subject_brush(project, **stroke)
        request = {**self.request(), **stroke,
                   'expected_preview_mask_sha256_float32': preview['preview_mask_sha256_float32']}
        self.save(request)
        reopened = load_project(self.path)
        self.assertEqual(reopened.document['editor_v216']['strokes'][0]['object'], 1)
        self.assertEqual(reopened.resources, project.resources)

    def test_retry_after_another_edit_does_not_claim_current_project_is_saved_stroke(self):
        request = self.request()
        saved = self.save(request)
        self.workspace.update_notes('brush-preview', notes='later', expected_sha256=saved['sha256'])
        before = self.files()
        with self.assertRaisesRegex(WorkspaceError, 'PROJECT_CHANGED'):
            self.save(request)
        self.assertEqual(self.files(), before)

    def test_retry_after_native_edit_without_history_is_rejected(self):
        from smartsvg_core.project_archive import save_project
        request = self.request()
        self.save(request)
        project = load_project(self.path)
        save_project(self.path, replace(project, document={
            **project.document, 'notes': 'native writer changed this'}), overwrite=True)
        before = self.files()
        with self.assertRaisesRegex(WorkspaceError, 'PROJECT_CHANGED'):
            self.save(request)
        self.assertEqual(self.files(), before)

    def test_identical_retry_is_readonly_and_does_not_rotate_backup(self):
        request = self.request()
        first = self.save(request)
        before = self.files()
        second = self.save(request)
        self.assertEqual(second["status"], "subject_brush_already_saved")
        self.assertEqual(second["sha256"], first["sha256"])
        self.assertEqual(self.files(), before)

    def test_reused_command_with_different_gesture_is_rejected(self):
        request = self.request()
        self.save(request)
        before = self.files()
        with self.assertRaisesRegex(WorkspaceError, "BRUSH_COMMAND_ID_REUSED"):
            self.save({**request, "radius": 0.06})
        self.assertEqual(self.files(), before)

    def test_retry_revalidates_float32_identity_instead_of_trusting_receipt(self):
        from smartsvg_core.project_archive import save_project
        from smartsvg_core.subject_identity_g33e import BINDINGS_KEY
        request = self.request()
        self.save(request)
        project = load_project(self.path)
        proofs = project.document[BINDINGS_KEY]
        items = [dict(item) for item in proofs['items']]
        items[0]['mask_sha256_float32'] = 'f' * 64
        save_project(self.path, replace(project, document={**project.document,
                     BINDINGS_KEY: {**proofs, 'items': items}}), overwrite=True)
        before = self.files()
        with self.assertRaisesRegex(WorkspaceError, 'INVALID_SUBJECT_PROOF'):
            self.save(request)
        self.assertEqual(self.files(), before)

    def test_confirmation_revision_digest_and_identity_fail_without_writes(self):
        request = self.request()
        cases = [
            ({"confirmed": False}, "BRUSH_SAVE_CONFIRMATION_REQUIRED"),
            ({"confirmed": 1}, "BRUSH_SAVE_CONFIRMATION_REQUIRED"),
            ({"expected_sha256": "f" * 64}, "PROJECT_CHANGED"),
            ({"expected_sha256": "invalid"}, "EXPECTED_REVISION_REQUIRED"),
            ({"expected_preview_mask_sha256_float32": "f" * 64}, "BRUSH_PREVIEW_CHANGED"),
            ({"expected_preview_mask_sha256_float32": "invalid"}, "INVALID_BRUSH_SAVE_REQUEST"),
            ({"command_id": ""}, "INVALID_BRUSH_SAVE_REQUEST"),
            ({"command_id": "x" * 129}, "INVALID_BRUSH_SAVE_REQUEST"),
            ({"subject_id": "subject-" + "f" * 32}, "SUBJECT_NOT_VERIFIED"),
            ({"mask_id": "base-mask-01"}, "SUBJECT_PROOF_MISMATCH"),
            ({"points": [[float("nan"), 0.5]]}, "INVALID_PREVIEW_STROKE"),
        ]
        for changes, error in cases:
            with self.subTest(changes=changes):
                before = self.files()
                with self.assertRaisesRegex(WorkspaceError, error):
                    self.save({**request, **changes})
                self.assertEqual(self.files(), before)

    def test_nonempty_editor_is_preserved_instead_of_overwritten(self):
        request = self.request()
        session = {"version": 1, "width": 16, "height": 12, "count": 2,
                   "source": "a" * 64, "strokes": [
                       {"object": 1, "mode": "add", "radius": 0.1, "points": [[0.2, 0.2]]}]}
        saved = self.workspace.save_editor_document(
            "brush-preview", editor_json=json.dumps(session),
            expected_sha256=request["expected_sha256"])
        request["expected_sha256"] = saved["sha256"]
        before = self.files()
        with self.assertRaisesRegex(WorkspaceError, "BRUSH_EDITOR_SESSION_NOT_EMPTY"):
            self.save(request)
        self.assertEqual(self.files(), before)

    def test_pending_recovery_refuses_save_without_writes(self):
        request = self.request()
        self.path.with_name("brush-preview.pending-backup.smartsvg").write_bytes(self.path.read_bytes())
        before = self.files()
        with self.assertRaisesRegex(WorkspaceError, "PROJECT_NOT_HEALTHY"):
            self.save(request)
        self.assertEqual(self.files(), before)

    def test_unrecognized_history_values_fail_closed_without_raw_exception(self):
        from smartsvg_core.project_archive import save_project
        for entry in (None, 7, 'legacy-string', []):
            with self.subTest(entry=entry):
                request = self.request()
                project = load_project(self.path)
                save_project(self.path, replace(project, operations=[
                    *project.operations, entry]), overwrite=True)
                request['expected_sha256'] = sha256(self.path.read_bytes()).hexdigest()
                before = self.files()
                with self.assertRaisesRegex(WorkspaceError, 'INVALID_BRUSH_HISTORY'):
                    self.save(request)
                self.assertEqual(self.files(), before)
                save_project(self.path, project, overwrite=True)

    def test_concurrent_notes_update_is_not_overwritten_by_brush(self):
        request = self.request()
        from smartsvg_core import project_workspace_g22 as workspace_module
        real_save = workspace_module.save_with_recovery
        def race(path, project, **kwargs):
            self.workspace.update_notes("brush-preview", notes="concurrent", expected_sha256=request["expected_sha256"])
            return real_save(path, project, **kwargs)
        # Patch only the brush call, not update_notes' nested save.
        fired = False
        def once(path, project, **kwargs):
            nonlocal fired
            if fired:
                return real_save(path, project, **kwargs)
            fired = True
            return race(path, project, **kwargs)
        with patch.object(workspace_module, "save_with_recovery", side_effect=once):
            with self.assertRaisesRegex(WorkspaceError, "PROJECT_CHANGED_DURING_SAVE"):
                self.save(request)
        reopened = load_project(self.path)
        self.assertEqual(reopened.document["notes"], "concurrent")
        self.assertNotIn("editor_v216", reopened.document)

    def test_publication_failure_keeps_primary_and_backup(self):
        request = self.request()
        before = self.files()
        with patch.object(project_recovery, "save_project", side_effect=OSError("disk full")):
            with self.assertRaisesRegex(WorkspaceError, "SAVE_FAILED"):
                self.save(request)
        self.assertEqual(self.files(), before)

    def test_readback_mismatch_reports_failure_and_retains_recovery_sidecar(self):
        request = self.request()
        real_save = project_recovery.save_project
        prior = self.path.read_bytes()
        def wrong_session(path, project, **kwargs):
            doc = {**project.document, "editor_v216": {
                **project.document["editor_v216"], "strokes": []}}
            return real_save(path, replace(project, document=doc), **kwargs)
        with patch.object(project_recovery, "save_project", side_effect=wrong_session):
            with self.assertRaisesRegex(WorkspaceError, "SAVE_FAILED"):
                self.save(request)
        self.assertEqual(self.path.with_name("brush-preview.pending-backup.smartsvg").read_bytes(), prior)
        self.assertEqual(self.workspace.inspect("brush-preview")["status"], "PENDING_BACKUP_REVIEW_REQUIRED")


if __name__ == "__main__":
    unittest.main()
