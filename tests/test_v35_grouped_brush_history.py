"""V3.5 W02: one confirmed multi-zone batch is one durable Undo unit."""
from dataclasses import replace
from hashlib import sha256
import importlib.util
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))
sys.path.insert(0, str(ROOT / "tests"))
import test_g33e_subject_brush_preview as fixtures
from smartsvg_core.native_subject_save_v34 import save_native_subject_strokes
from smartsvg_core.project_archive import load_project, save_project
from smartsvg_core.project_workspace_g22 import WorkspaceError
from smartsvg_core.subject_brush_preview_g33e import preview_subject_brush_strokes


@unittest.skipUnless(importlib.util.find_spec("numpy") and importlib.util.find_spec("PIL"),
                     "CPU brush dependencies not installed in stdlib-only G0")
class GroupedBrushHistoryTests(unittest.TestCase):
    def setUp(self):
        fixtures.SubjectBrushPreviewTests.setUp(self)
        self.strokes = [
            {"mode": "add", "radius": 0.03, "points": [[0.2, 0.2]]},
            {"mode": "add", "radius": 0.03, "points": [[0.8, 0.8]]},
            {"mode": "erase", "radius": 0.03, "points": [[0.5, 0.5]]},
        ]

    def request(self, *, command_id="grouped-001"):
        project, values = fixtures.SubjectBrushPreviewTests.command(self)
        identity = {key: values[key] for key in (
            "subject_id", "mask_id", "mask_sha256_float32",
            "source_id", "source_sha256")}
        preview = preview_subject_brush_strokes(
            project, **identity, strokes=self.strokes)
        return dict(
            **identity, strokes=self.strokes,
            expected_sha256=sha256(self.path.read_bytes()).hexdigest(),
            expected_preview_mask_sha256_float32=
                preview["preview_mask_sha256_float32"],
            command_id=command_id, confirmed=True,
        )

    def rendered(self):
        import numpy as np
        from smartsvg_editor.strokes import apply_strokes
        project = load_project(self.path)
        raw, meta = self.workspace.base_masks(
            "brush-preview", expected_sha256=sha256(self.path.read_bytes()).hexdigest())
        strokes = project.document.get("editor_v216", {}).get("strokes", [])
        return apply_strokes(
            np.frombuffer(raw, dtype="<f4").reshape(meta["shape"]), strokes).tobytes()

    def history(self, action, command_id):
        return self.workspace.change_subject_brush_history(
            "brush-preview",
            expected_sha256=sha256(self.path.read_bytes()).hexdigest(),
            action=action, command_id=command_id, confirmed=True)

    def test_group_save_roundtrip_undo_redo_is_one_operation(self):
        original = load_project(self.path)
        before = self.rendered()
        saved = self.workspace.save_subject_brushes(
            "brush-preview", **self.request())
        after = self.rendered()
        project = load_project(self.path)

        self.assertEqual(saved["status"], "subject_brushes_saved")
        self.assertEqual(len(project.document["editor_v216"]["strokes"]), 3)
        self.assertEqual(len(project.operations), len(original.operations) + 1)
        self.assertEqual(project.operations[-1]["kind"],
                         "save_subject_brushes_v35_w02_v1")
        self.assertEqual(project.operations[-1]["strokes"],
                         project.document["editor_v216"]["strokes"][-3:])
        self.assertNotEqual(after, before)
        self.assertEqual(project.resources, original.resources)

        undone = self.history("undo", "undo-grouped")
        self.assertEqual(undone["status"], "brush_history_undo")
        self.assertEqual(self.rendered(), before)
        self.assertNotIn("editor_v216", load_project(self.path).document)

        redone = self.history("redo", "redo-grouped")
        self.assertEqual(redone["status"], "brush_history_redo")
        self.assertEqual(self.rendered(), after)
        self.assertEqual(load_project(self.path).resources, original.resources)

    def test_group_retry_is_readonly_and_native_boundary_hides_writer_details(self):
        request = self.request()
        first = self.workspace.save_subject_brushes("brush-preview", **request)
        before = {p.name: p.read_bytes() for p in self.path.parent.iterdir()}
        retry = self.workspace.save_subject_brushes("brush-preview", **request)
        self.assertEqual(retry["status"], "subject_brushes_already_saved")
        self.assertEqual(first["sha256"], retry["sha256"])
        self.assertEqual(
            {p.name: p.read_bytes() for p in self.path.parent.iterdir()}, before)
        with self.assertRaisesRegex(WorkspaceError, "BRUSH_COMMAND_ID_REUSED"):
            self.workspace.save_subject_brushes(
                "brush-preview", **{**request, "strokes": self.strokes[:-1]})
        self.assertEqual(
            {p.name: p.read_bytes() for p in self.path.parent.iterdir()}, before)

        # A fresh archive exercises the native subject-ID-only boundary.
        fixtures.SubjectBrushPreviewTests.setUp(self)
        project, values = fixtures.SubjectBrushPreviewTests.command(self)
        identity = {key: values[key] for key in (
            "subject_id", "mask_id", "mask_sha256_float32",
            "source_id", "source_sha256")}
        preview = preview_subject_brush_strokes(project, **identity, strokes=self.strokes)
        result = save_native_subject_strokes(
            project_path=str(self.path),
            expected_sha256=sha256(self.path.read_bytes()).hexdigest(),
            subject_id=values["subject_id"], strokes=self.strokes,
            expected_preview_mask_sha256_float32=
                preview["preview_mask_sha256_float32"],
            command_id="native-grouped", confirmed=True)
        self.assertEqual(result["status"], "subject_brushes_saved")
        self.assertNotIn("mask_id", result)
        self.assertNotIn("strokes", result)
        pixels = struct.unpack("<384f", self.rendered())
        self.assertEqual(pixels[round(0.2 * 11) * 16 + round(0.2 * 15)], 1.0)

    def test_corrupt_group_receipt_fails_closed_without_history_write(self):
        self.workspace.save_subject_brushes("brush-preview", **self.request())
        project = load_project(self.path)
        corrupt = {**project.operations[-1], "stroke_count": 2}
        save_project(self.path, replace(project, operations=[
            *project.operations[:-1], corrupt]), overwrite=True)
        before = {p.name: p.read_bytes() for p in self.path.parent.iterdir()}
        with self.assertRaisesRegex(WorkspaceError, "INVALID_BRUSH_HISTORY"):
            self.history("undo", "corrupt-group")
        self.assertEqual(
            {p.name: p.read_bytes() for p in self.path.parent.iterdir()}, before)


if __name__ == "__main__":
    unittest.main()
