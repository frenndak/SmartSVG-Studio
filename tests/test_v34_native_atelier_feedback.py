"""Negative UI tests for bounded, read-only archived-mask diagnostics (V34-132)."""
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

ENGINE = Path(__file__).resolve().parents[1] / 'engine'
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from native_atelier_tk_v34 import NativeAtelierPanel, brush_preview_request
from smartsvg_core.source_preview_v34 import SourcePreview


class Variable:
    def __init__(self, value=''):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class AtelierFeedbackTests(unittest.TestCase):
    def setUp(self):
        self.loaded_images = []
        self.decoded = []
        self.panel = NativeAtelierPanel.__new__(NativeAtelierPanel)
        self.panel.snapshot = SimpleNamespace(project_id='synthetic', sha256='a' * 64)
        self.panel.selection = Variable('subject-synthetic')
        self.panel.details = Variable()
        self.panel.subject_position = Variable()
        self.panel.previous_button = SimpleNamespace(configure=lambda **_kwargs: None)
        self.panel.next_button = SimpleNamespace(configure=lambda **_kwargs: None)
        self.panel.viewport = SimpleNamespace(
            load=lambda image: self.loaded_images.append(image))
        self.panel.parent = SimpleNamespace(winfo_ismapped=lambda: True)
        self.panel.tk = SimpleNamespace(PhotoImage=lambda **kwargs: self.decoded.append(kwargs))

    def load_status(self, status, proof='png_only'):
        subject = SimpleNamespace(
            subject_id='subject-synthetic',
            source_id='source-synthetic',
            mask_id='mask-synthetic',
            bbox_px=(0, 1, 2, 3),
            proof_status=proof,
            preview=SourcePreview(status),
        )
        self.panel.subjects = {subject.subject_id: subject}
        self.panel.render()
        return self.panel.details.get()

    def test_every_rejected_preview_has_distinct_safe_guidance_and_never_decodes(self):
        cases = {
            'SOURCE_MISSING': 'Ressource du masque absente',
            'SOURCE_INVALID_PNG': 'PNG du masque invalide',
            'SOURCE_CHANGED': 'empreinte attendues',
            'SOURCE_TOO_LARGE': 'Masque trop volumineux',
        }
        for status, expected in cases.items():
            with self.subTest(status=status):
                message = self.load_status(status)
                self.assertIn(expected, message)
                self.assertIn('Masque mask-synthetic', message)
                self.assertNotIn('C:\\', message)
                self.assertNotIn('/home/', message)
                self.assertIsNone(self.loaded_images[-1])
        self.assertEqual(self.decoded, [])

    def test_future_unknown_preview_or_proof_status_fails_closed_without_crashing(self):
        message = self.load_status('FUTURE_STATUS', 'future-proof-status')
        self.assertIn('Liaison de masque non vérifiée', message)
        self.assertIn('Aperçu indisponible pour ce masque', message)
        self.assertIn('F5', message)
        self.assertIsNone(self.loaded_images[-1])
        self.assertEqual(self.decoded, [])



class BrushHandoffTests(unittest.TestCase):
    def setUp(self):
        from smartsvg_core.native_atelier_v34 import AtelierSnapshot, AtelierSubject
        self.path = str(Path.cwd() / 'synthetic.smartsvg')
        self.sha = 'b' * 64
        self.subject_id = 'subject-' + 'a' * 32
        self.subject = AtelierSubject(
            self.subject_id, 'source-synthetic', 'mask-synthetic',
            (0, 0, 8, 8), 'verified', SourcePreview('READY_PNG', b'0' * 33, width_px=8, height_px=8))
        self.snapshot = AtelierSnapshot('synthetic', self.sha, (self.subject,))

    def test_only_verified_subject_and_absolute_revision_are_eligible(self):
        from dataclasses import replace
        request = brush_preview_request(self.snapshot, self.subject, self.path)
        self.assertEqual(request['subject_id'], self.subject_id)
        self.assertEqual(request['expected_sha256'], self.sha)
        self.assertEqual(request['project_path'], self.path)
        self.assertIsNone(brush_preview_request(self.snapshot, self.subject, 'relative.smartsvg'))
        self.assertIsNone(brush_preview_request(replace(self.snapshot, sha256='bad'),
                                                self.subject, self.path))
        self.assertIsNone(brush_preview_request(self.snapshot,
                         replace(self.subject, proof_status='legacy_subject_record'), self.path))
        self.assertIsNone(brush_preview_request(self.snapshot,
                         replace(self.subject, proof_status='png_only'), self.path))
        self.assertIsNone(brush_preview_request(self.snapshot,
                         replace(self.subject, subject_id='wrong'), self.path))
        self.assertIsNone(brush_preview_request(self.snapshot,
                         replace(self.subject, preview=SourcePreview('SOURCE_CHANGED')), self.path))
        # Archive inspection permits a dimension the brush Tk loader rejects.
        for width, height in ((2049, 8), (8, 2049), (0, 8), (8, 0)):
            with self.subTest(size=(width, height)):
                self.assertIsNone(brush_preview_request(
                    self.snapshot, replace(self.subject, preview=SourcePreview(
                        'READY_PNG', self.subject.preview.png,
                        width_px=width, height_px=height)), self.path))
        self.assertIsNotNone(brush_preview_request(
            self.snapshot, replace(self.subject, preview=SourcePreview(
                'READY_PNG', self.subject.preview.png,
                width_px=2048, height_px=2048)), self.path))
        self.assertIsNone(brush_preview_request(
            self.snapshot, replace(self.subject, preview=SourcePreview(
                'READY_PNG', b'a' * (8 * 1024 * 1024 + 1),
                width_px=8, height_px=8)), self.path))

    def test_tk_handoff_closes_stale_draft_on_selection_change_and_refresh(self):
        import tkinter as tk
        from tkinter import ttk
        from unittest.mock import patch
        from types import ModuleType
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest('No graphical Tk session available')
        self.addCleanup(root.destroy)
        root.withdraw()
        created = []

        class FakeBrush:
            def __init__(self, *_args, **kwargs):
                self._identity = None
                self.on_saved = kwargs.get('on_saved')
                self.closed = 0
                created.append(self)

            def load(self, **request):
                self.request = request
                self._identity = (request['project_path'],
                                  request['expected_sha256'], request['subject_id'])

            def shutdown(self):
                self.closed += 1

        module = ModuleType('native_brush_draft_tk_v34')
        module.NativeBrushDraftPanel = FakeBrush
        with patch.dict(sys.modules, {'native_brush_draft_tk_v34': module}):
            confirmed_saves = []
            atelier = NativeAtelierPanel(
                root, tk, ttk, on_saved=confirmed_saves.append)
            self.addCleanup(atelier.shutdown)
            atelier.load(self.snapshot, project_path=self.path)
            self.assertEqual(str(atelier.brush_button.cget('state')), 'normal')
            self.assertTrue(atelier.open_brush())
            self.assertEqual(created[-1].request['expected_sha256'], self.sha)
            self.assertEqual(created[-1].request['subject_id'], self.subject_id)
            valid = {'subject_id': self.subject_id, 'persisted': True,
                     'project_sha256': 'd' * 64}
            created[-1].on_saved(valid)
            self.assertEqual(confirmed_saves, [valid])
            created[-1].on_saved({**valid, 'persisted': False})
            created[-1].on_saved({**valid, 'subject_id': 'other'})
            self.assertEqual(confirmed_saves, [valid])
            # Same subject does not create duplicate workers/windows.
            self.assertTrue(atelier.open_brush())
            self.assertEqual(len(created), 1)
            atelier.selection.set('subject-not-present')
            atelier.render()
            self.assertEqual(created[-1].closed, 1)
            self.assertIsNone(atelier._brush_dialog)
            # A late success from the closed dialog must not refresh a new subject.
            created[-1].on_saved(valid)
            self.assertEqual(confirmed_saves, [valid])
            self.assertEqual(str(atelier.brush_button.cget('state')), 'disabled')
            atelier.load(self.snapshot, project_path=self.path)
            self.assertTrue(atelier.open_brush())
            atelier.load(None)
            self.assertEqual(created[-1].closed, 1)
            self.assertIsNone(atelier._brush_dialog)
            self.assertEqual(str(atelier.brush_button.cget('state')), 'disabled')
            # A verified oversized mask must not launch a doomed Tk dialog.
            from dataclasses import replace
            too_big = replace(self.subject, preview=SourcePreview(
                'READY_PNG', self.subject.preview.png,
                width_px=3000, height_px=8))
            oversized = replace(self.snapshot, subjects=(too_big,))
            atelier.load(oversized, project_path=self.path)
            self.assertEqual(str(atelier.brush_button.cget('state')), 'disabled')
            self.assertFalse(atelier.open_brush())
            self.assertEqual(len(created), 2)

    def test_real_atelier_opens_integrated_native_brush_without_writes(self):
        """E3 integration test: actual Atelier -> actual native brush widget.

        This Windows GUI smoke complements the separate strict real-CPU
        qualification of the V1 Subject bridge. No workspace writer is used.
        """
        import struct
        import tempfile
        import tkinter as tk
        import zlib
        from dataclasses import replace
        from tkinter import ttk
        from native_brush_draft_tk_v34 import NativeBrushDraftPanel

        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest('No graphical Tk session available')
        self.addCleanup(root.destroy)
        root.withdraw()

        def png_chunk(kind, data):
            return (struct.pack('>I', len(data)) + kind + data
                    + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff))

        width, height = 8, 8
        png = (b'\x89PNG\r\n\x1a\n'
               + png_chunk(b'IHDR', struct.pack('>IIBBBBB',
                                               width, height, 8, 6, 0, 0, 0))
               + png_chunk(b'IDAT', zlib.compress(
                   (b'\x00' + b'\xff\x00\x00\xff' * width) * height))
               + png_chunk(b'IEND', b''))

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'synthetic.smartsvg'
            original = b'UNTOUCHED SYNTHETIC FILE'
            path.write_bytes(original)
            subject = replace(self.subject, preview=SourcePreview(
                'READY_PNG', png, width_px=width, height_px=height))
            snapshot = replace(self.snapshot, subjects=(subject,))
            atelier = NativeAtelierPanel(root, tk, ttk)
            self.addCleanup(atelier.shutdown)
            self.assertIs(atelier._brush_class, NativeBrushDraftPanel)
            atelier.load(snapshot, project_path=str(path))
            self.assertEqual(str(atelier.brush_button.cget('state')), 'normal')
            self.assertTrue(atelier.open_brush())
            self.assertIsInstance(atelier._brush_panel, NativeBrushDraftPanel)
            self.assertEqual(atelier._brush_panel._identity,
                             (str(path), self.sha, self.subject_id))
            self.assertEqual(path.read_bytes(), original)
            atelier.load(None)
            self.assertIsNone(atelier._brush_dialog)
            self.assertIsNone(atelier._brush_panel)
            self.assertEqual(path.read_bytes(), original)

    def test_malformed_or_duplicate_subject_catalog_never_enables_brush(self):
        """Missing/duplicate V1 Subject IDs must not crash Tk or retarget masks."""
        import tempfile
        import tkinter as tk
        from dataclasses import replace
        from tkinter import ttk

        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest('No graphical Tk session available')
        self.addCleanup(root.destroy)
        root.withdraw()
        panel = NativeAtelierPanel(root, tk, ttk)
        self.addCleanup(panel.shutdown)

        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'untouched.smartsvg'
            initial = b'UNCHANGED SYNTHETIC PROJECT'
            project.write_bytes(initial)
            duplicate = replace(self.subject, mask_id='other-mask-same-subject-id')
            cases = (
                SimpleNamespace(project_id='synthetic', sha256=self.sha),
                replace(self.snapshot, subjects=None),
                replace(self.snapshot, subjects=[self.subject]),
                replace(self.snapshot, subjects=(SimpleNamespace(),)),
                replace(self.snapshot, subjects=(self.subject, duplicate)),
                replace(self.snapshot, sha256='invalid'),
            )
            for candidate in cases:
                with self.subTest(candidate=repr(candidate)[:160]):
                    panel.load(candidate, project_path=str(project))
                    self.assertEqual(panel.subjects, {})
                    self.assertEqual(panel.selection.get(), '')
                    self.assertIn('Réexaminez le projet (F5)', panel.details.get())
                    self.assertEqual(str(panel.brush_button.cget('state')), 'disabled')
                    self.assertFalse(panel.open_brush())
                    self.assertEqual(project.read_bytes(), initial)

            # A normal inspector tuple must remain eligible for inspection.
            panel.load(self.snapshot, project_path=str(project))
            self.assertEqual(tuple(panel.subjects), (self.subject_id,))
            self.assertEqual(panel.selection.get(), self.subject_id)
            self.assertEqual(project.read_bytes(), initial)

    def test_native_subject_navigation_is_bounded_and_invalidates_stale_brush(self):
        import tkinter as tk
        from tkinter import ttk
        from dataclasses import replace
        from unittest.mock import patch
        from types import ModuleType
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest('No graphical Tk session available')
        self.addCleanup(root.destroy)
        root.withdraw()
        closed = []

        class FakeBrush:
            def __init__(self, *_args):
                self._identity = None
                self.shut = False

            def load(self, **request):
                self._identity = (request['project_path'],
                                  request['expected_sha256'],
                                  request['subject_id'])

            def shutdown(self):
                closed.append(self._identity)
                self.shut = True

        second = replace(
            self.subject, subject_id='subject-' + 'c' * 32,
            mask_id='mask-second')
        project = replace(self.snapshot, subjects=(self.subject, second))
        module = ModuleType('native_brush_draft_tk_v34')
        module.NativeBrushDraftPanel = FakeBrush
        with patch.dict(sys.modules, {'native_brush_draft_tk_v34': module}):
            panel = NativeAtelierPanel(root, tk, ttk)
            self.addCleanup(panel.shutdown)
            panel.load(project, project_path=self.path)
            self.assertEqual(panel.selection.get(), self.subject_id)
            self.assertIn('1 sur 2', panel.subject_position.get())
            self.assertEqual(str(panel.previous_button.cget('state')), 'disabled')
            self.assertEqual(str(panel.next_button.cget('state')), 'normal')
            self.assertFalse(panel.previous_subject())
            self.assertTrue(panel.open_brush())
            self.assertTrue(panel.next_subject())
            self.assertEqual(panel.selection.get(), second.subject_id)
            self.assertIn('2 sur 2', panel.subject_position.get())
            self.assertEqual(str(panel.next_button.cget('state')), 'disabled')
            self.assertEqual(len(closed), 1)
            self.assertEqual(closed[0][2], self.subject_id)
            self.assertFalse(panel.next_subject())
            self.assertTrue(panel.previous_subject())
            self.assertEqual(panel.selection.get(), self.subject_id)
            panel.selection.set('subject-not-present')
            panel.render()
            self.assertEqual(str(panel.next_button.cget('state')), 'disabled')
            self.assertEqual(str(panel.previous_button.cget('state')), 'disabled')
            self.assertFalse(panel.next_subject())
            panel.load(None)
            self.assertEqual(panel.subject_position.get(), '')
            self.assertEqual(str(panel.next_button.cget('state')), 'disabled')


if __name__ == '__main__':
    unittest.main()
