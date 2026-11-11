"""Regression: malformed archived previews cannot crash native brush admission."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))
from native_atelier_tk_v34 import brush_preview_request, NativeAtelierPanel


class AtelierBrushAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = SimpleNamespace(sha256="a" * 64)
        self.preview = SimpleNamespace(status="READY_PNG", png=b"x" * 40,
                                       width_px=16, height_px=12)
        self.subject = SimpleNamespace(subject_id="subject-" + "b" * 32,
                                       proof_status="verified", preview=self.preview)
        self.path = str(Path.cwd().resolve() / "synthetic.smartsvg")

    def test_verified_subject_routes_to_backend_without_mutation(self):
        request = brush_preview_request(self.snapshot, self.subject, self.path)
        self.assertEqual(request["expected_sha256"], self.snapshot.sha256)
        self.assertEqual(request["subject_id"], self.subject.subject_id)
        self.assertEqual(request["preview_png"], self.preview.png)

    def test_incomplete_snapshot_or_subject_fails_closed(self):
        """Malformed session objects must not crash the Tk event callback."""
        original_snapshot, original_subject = self.snapshot, self.subject
        try:
            for snapshot, subject in (
                (SimpleNamespace(), original_subject),
                (original_snapshot, SimpleNamespace()),
                (original_snapshot, SimpleNamespace(subject_id=original_subject.subject_id)),
                (original_snapshot, SimpleNamespace(subject_id=original_subject.subject_id,
                                                    proof_status="verified")),
            ):
                with self.subTest(snapshot=snapshot, subject=subject):
                    self.assertIsNone(brush_preview_request(snapshot, subject, self.path))
        finally:
            self.snapshot, self.subject = original_snapshot, original_subject

    def test_incomplete_preview_fields_fail_closed(self):
        """Missing metadata in an archived preview must never escape into Tk."""
        original = self.subject.preview
        try:
            for preview in (
                SimpleNamespace(),
                SimpleNamespace(status="READY_PNG"),
                SimpleNamespace(status="READY_PNG", png=b"x" * 40),
                SimpleNamespace(status="READY_PNG", png=b"x" * 40, width_px=16),
                SimpleNamespace(status="READY_PNG", png=b"x" * 40, height_px=12),
            ):
                with self.subTest(preview=vars(preview)):
                    self.subject.preview = preview
                    self.assertIsNone(brush_preview_request(
                        self.snapshot, self.subject, self.path))
        finally:
            self.subject.preview = original

    def test_missing_preview_fails_closed(self):
        self.subject.preview = None
        self.assertIsNone(brush_preview_request(self.snapshot, self.subject, self.path))

    def test_invalid_dimensions_fail_closed_without_exception(self):
        for value in (None, "16", 16.0, True, -1, 0, 2049):
            for axis in ("width_px", "height_px"):
                with self.subTest(value=value, axis=axis):
                    setattr(self.preview, "width_px", 16)
                    setattr(self.preview, "height_px", 12)
                    setattr(self.preview, axis, value)
                    self.assertIsNone(brush_preview_request(
                        self.snapshot, self.subject, self.path))



class RenderMalformedMetadataTests(unittest.TestCase):
    def test_render_rejects_incomplete_subject_without_allocating_image(self):
        class Cell:
            def __init__(self, value=None): self.value = value
            def get(self): return self.value
            def set(self, value): self.value = value
        class Viewport:
            def __init__(self): self.loads = []
            def load(self, value): self.loads.append(value)
        class Button:
            def configure(self, **kwargs): pass
        panel = object.__new__(NativeAtelierPanel)
        panel.snapshot = SimpleNamespace(sha256='a' * 64)
        panel._project_path = '/synthetic/project.smartsvg'
        panel._brush_key = None
        panel._brush_class = None
        panel.selection = Cell('subject-' + 'b' * 32)
        panel.details = Cell()
        panel.viewport = Viewport()
        panel.brush_button = Button()
        panel._update_navigation = lambda: None
        for subject in (
            SimpleNamespace(subject_id=panel.selection.get()),
            SimpleNamespace(subject_id=panel.selection.get(), source_id='source',
                            mask_id='mask', bbox_px=(0, 0, 8, 8)),
            SimpleNamespace(subject_id=panel.selection.get(), source_id='source',
                            mask_id='mask', bbox_px=(0, 0, 8, 8),
                            preview=SimpleNamespace(status='READY_PNG')),
        ):
            with self.subTest(subject=vars(subject)):
                panel.subjects = {panel.selection.get(): subject}
                NativeAtelierPanel.render(panel)
                self.assertIn('Réexaminez', panel.details.get())
                self.assertEqual(panel.viewport.loads[-1], None)


    def test_render_ready_preview_without_proof_status_is_read_only(self):
        """An incomplete legacy record may render but must never enable editing."""
        class Cell:
            def __init__(self, value=None): self.value = value
            def get(self): return self.value
            def set(self, value): self.value = value
        class Viewport:
            def __init__(self): self.loads = []
            def load(self, value): self.loads.append(value)
        class Button:
            def __init__(self): self.state = None
            def configure(self, **kwargs): self.state = kwargs.get('state')
        class Parent:
            def winfo_ismapped(self): return True
        class Tk:
            class TclError(Exception): pass
            @staticmethod
            def PhotoImage(**kwargs): return object()
        panel = object.__new__(NativeAtelierPanel)
        panel.snapshot = SimpleNamespace(sha256='a' * 64)
        panel._project_path = '/synthetic/project.smartsvg'
        panel._brush_key = None
        panel._brush_class = None
        panel.selection = Cell('subject-' + 'b' * 32)
        panel.details = Cell()
        panel.viewport = Viewport()
        panel.brush_button = Button()
        panel.parent = Parent()
        panel.tk = Tk
        panel._update_navigation = lambda: None
        subject = SimpleNamespace(
            subject_id=panel.selection.get(), source_id='source', mask_id='mask',
            bbox_px=(0, 0, 8, 8),
            preview=SimpleNamespace(status='READY_PNG', png=b'x' * 40,
                                    width_px=8, height_px=8))
        panel.subjects = {subject.subject_id: subject}
        NativeAtelierPanel.render(panel)
        self.assertIn('non vérifiée', panel.details.get())
        self.assertEqual(panel.brush_button.state, 'disabled')
        self.assertEqual(len(panel.viewport.loads), 2)


class AtelierProjectHeaderAdmissionTests(unittest.TestCase):
    def test_incomplete_snapshot_header_is_recoverable(self):
        class Cell:
            def __init__(self): self.value = None
            def set(self, value): self.value = value
        panel = object.__new__(NativeAtelierPanel)
        panel.project = Cell()
        for snapshot in (SimpleNamespace(),
                         SimpleNamespace(project_id='demo'),
                         SimpleNamespace(project_id='demo', sha256=None),
                         SimpleNamespace(project_id='demo', sha256='bad'),
                         SimpleNamespace(project_id='', sha256='a' * 64)):
            with self.subTest(snapshot=vars(snapshot)):
                panel.snapshot = snapshot
                panel._project_label()
                self.assertIn('Réexaminez', panel.project.value)
        panel.snapshot = None
        panel._project_label()
        self.assertIn('Ouvrez', panel.project.value)

    def test_verified_header_keeps_short_revision(self):
        class Cell:
            def set(self, value): self.value = value
        panel = object.__new__(NativeAtelierPanel)
        panel.project = Cell()
        panel.snapshot = SimpleNamespace(project_id='demo', sha256='a' * 64)
        panel._project_label()
        self.assertEqual(panel.project.value, 'Projet demo · SHA ' + 'a' * 12)


if __name__ == "__main__":
    unittest.main()
