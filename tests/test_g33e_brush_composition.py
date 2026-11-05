"""V34-132 / G3.3e-b2b-2: compose saved V21.6 strokes before preview/save."""
from dataclasses import replace
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import struct
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'engine'))
import test_g33e_subject_brush_preview as fixtures
from smartsvg_core.project_archive import load_project, save_project
from smartsvg_core.subject_brush_preview_g33e import preview_subject_brush, SubjectBrushPreviewError
from smartsvg_core.project_workspace_g22 import WorkspaceError


@unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'),
                     'CPU brush dependencies not installed in stdlib-only G0')
class BrushCompositionTests(unittest.TestCase):
    def setUp(self):
        fixtures.SubjectBrushPreviewTests.setUp(self)

    def gesture(self, index=0, **changes):
        return fixtures.SubjectBrushPreviewTests.command(self, index=index, **changes)

    def save(self, index=0, command_id='composed-1', **changes):
        project, command = self.gesture(index, **changes)
        preview = preview_subject_brush(project, **command)
        request = dict(**command, expected_sha256=sha256(self.path.read_bytes()).hexdigest(),
                       expected_preview_mask_sha256_float32=preview['preview_mask_sha256_float32'],
                       command_id=command_id, confirmed=True)
        saved = self.workspace.save_subject_brush('brush-preview', **request)
        return saved, request, preview

    def native_session(self, initial_strokes, **changes):
        project = load_project(self.path)
        session = dict(version=1, width=16, height=12, count=2, source='a'*64,
                       strokes=initial_strokes)
        session.update(changes)
        save_project(self.path, replace(project, document={
            **project.document, 'editor_v216': session}), overwrite=True)

    def test_preview_starts_from_saved_pixels_and_preserves_distant_first_stroke(self):
        first, _, preview1 = self.save(points=[[0.8, 0.8]])
        project, command = self.gesture(mode='erase', points=[[0.5, 0.5]])
        before = self.path.read_bytes()
        preview2 = preview_subject_brush(project, **command)
        self.assertEqual(preview2['before_png_l8'], preview1['after_png_l8'])
        values = struct.unpack('<192f', preview2['preview_float32'])
        self.assertEqual(values[9*16+12], 1.0)  # retained previous added pixel
        self.assertEqual(values[6*16+8], 0.0)   # new erase at original foreground
        self.assertEqual(self.path.read_bytes(), before)

    def test_successive_save_reopens_full_session_and_retry_does_not_append_twice(self):
        first, request1, _ = self.save(points=[[0.8, 0.8]])
        resources = load_project(self.path).resources
        second, request2, preview2 = self.save(command_id='composed-2', mode='erase')
        project = load_project(self.path)
        self.assertEqual(len(project.document['editor_v216']['strokes']), 2)
        self.assertEqual(project.resources, resources)
        import numpy as np
        from smartsvg_editor.strokes import apply_strokes
        raw, _ = self.workspace.base_masks('brush-preview', expected_sha256=second['sha256'])
        replay = apply_strokes(np.frombuffer(raw, dtype='<f4').reshape(2,12,16),
                               project.document['editor_v216']['strokes'])
        self.assertEqual(sha256(replay[0].tobytes()).hexdigest(), preview2['preview_mask_sha256_float32'])
        files = {p.name:p.read_bytes() for p in self.path.parent.iterdir()}
        retry = self.workspace.save_subject_brush('brush-preview', **request2)
        self.assertEqual(retry['status'], 'subject_brush_already_saved')
        self.assertEqual({p.name:p.read_bytes() for p in self.path.parent.iterdir()}, files)
        with self.assertRaisesRegex(WorkspaceError, 'PROJECT_CHANGED'):
            self.workspace.save_subject_brush('brush-preview', **request1)

    def test_edits_to_another_subject_are_retained(self):
        self.save(index=1, points=[[0.8,0.8]])
        second, _, _ = self.save(command_id='subject-a', mode='erase')
        project = load_project(self.path)
        self.assertEqual([s['object'] for s in project.document['editor_v216']['strokes']], [1,0])
        # Previewing another edit to A must tolerate B's already-saved pixels.
        _, command = self.gesture(points=[[0.2,0.7]])
        preview_subject_brush(project, **command)
        self.assertEqual(self.workspace.inspect('brush-preview')['sha256'], second['sha256'])

    def test_legacy_native_editor_strokes_are_included_without_receipts(self):
        self.native_session([dict(object=1, mode='add', radius=0.05, points=[[0.8,0.8]])])
        saved, _, _ = self.save(mode='erase')
        session = json.loads(self.workspace.editor_document('brush-preview')['editor_json'])
        self.assertEqual(len(session['strokes']), 2)
        self.assertEqual(session['strokes'][0]['object'], 1)

    def test_invalid_saved_session_never_silently_falls_back_to_base(self):
        for change in ({'source':'f'*64}, {'count':1}, {'strokes':'invalid'}):
            with self.subTest(change=change):
                self.native_session([], **change)
                project, command = self.gesture()
                before = self.path.read_bytes()
                with self.assertRaisesRegex(SubjectBrushPreviewError, 'INVALID_SAVED_EDITOR_SESSION'):
                    preview_subject_brush(project, **command)
                self.assertEqual(self.path.read_bytes(), before)

    def test_existing_stroke_and_point_budgets_apply_to_composed_session(self):
        cases = [[dict(object=0, mode='add', radius=0.05, points=[[0.8,0.8]])]*400,
                 [dict(object=0, mode='add', radius=0.05, points=[[0.8,0.8]]*120)]*100]
        for strokes in cases:
            with self.subTest(count=len(strokes)):
                self.native_session(strokes)
                project, command = self.gesture()
                before = self.path.read_bytes()
                with self.assertRaisesRegex(SubjectBrushPreviewError, 'BRUSH_SESSION_LIMIT'):
                    preview_subject_brush(project, **command)
                self.assertEqual(self.path.read_bytes(), before)

    def test_workspace_preview_keeps_composed_editor_document_internal(self):
        self.save(points=[[0.8,0.8]])
        _, command = self.gesture(mode='erase')
        result = self.workspace.preview_subject_brush_readonly('brush-preview',
            expected_sha256=sha256(self.path.read_bytes()).hexdigest(), **command)
        self.assertNotIn('editor_document', result)
        self.assertNotIn('preview_float32', result)

    def test_retry_at_400_strokes_reconstructs_before_command_without_exceeding_budget(self):
        self.native_session([dict(object=0, mode='add', radius=0.05,
                                 points=[[0.8,0.8]])]*399)
        saved, request, _ = self.save(mode='erase')
        before = self.path.read_bytes()
        result = self.workspace.save_subject_brush('brush-preview', **request)
        self.assertEqual(result['status'], 'subject_brush_already_saved')
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(len(load_project(self.path).document['editor_v216']['strokes']), 400)


if __name__ == '__main__':
    unittest.main()
