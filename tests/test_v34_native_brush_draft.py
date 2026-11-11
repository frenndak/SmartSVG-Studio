"""Native G3.3e brush draft: normalized gestures, stale reads and no writer."""
from concurrent.futures import Future
from pathlib import Path
from threading import Event
from types import SimpleNamespace
import math
import struct
import sys
import tempfile
import time
import unittest
import zlib

ENGINE = Path(__file__).resolve().parents[1] / 'engine'
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from native_brush_draft_tk_v34 import (
    NativeBrushDraftPanel, MAX_GESTURE_POINTS, normalized_mask_point,
    bounded_tk_png,
)


def _png(width=32, height=16):
    def chunk(kind, data):
        return (struct.pack('>I', len(data)) + kind + data
                + struct.pack('>I', zlib.crc32(kind + data) & 0xffffffff))
    row = b'\x00' + bytes((20, 80, 130, 255)) * width
    return (b'\x89PNG\r\n\x1a\n'
            + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(row * height))
            + chunk(b'IEND', b''))


class NativeBrushMappingTests(unittest.TestCase):
    def test_letterbox_and_edges_never_map_outside_image(self):
        box = (40, 20, 200, 100)
        self.assertEqual(normalized_mask_point(140, 70, box), [0.5, 0.5])
        self.assertEqual(normalized_mask_point(40, 20, box), [0.0, 0.0])
        self.assertIsNone(normalized_mask_point(240, 70, box))
        self.assertIsNone(normalized_mask_point(140, 120, box))
        self.assertIsNone(normalized_mask_point(39, 70, box))
        self.assertIsNone(normalized_mask_point(140, 19, box))
        self.assertEqual(normalized_mask_point(239, 119, box), [0.995, 0.99])

    def test_png_bounds_reject_compressed_dimensions_before_tk(self):
        original = _png()
        self.assertTrue(bounded_tk_png(original))
        huge = bytearray(original)
        struct.pack_into('>I', huge, 16, 50000)
        self.assertFalse(bounded_tk_png(bytes(huge)))
        self.assertFalse(bounded_tk_png(b'not-a-png'))
        self.assertFalse(bounded_tk_png(original[:30]))
        self.assertFalse(bounded_tk_png(original + b'X' * 9_000_000))

    def test_invalid_numbers_and_boxes_fail_closed(self):
        cases = [
            (0, 0, None), (0, 0, (0, 0, 0, 50)),
            (0, 0, (0, 0, 50, -3)), (0, 0, (0, 0, 50)),
            (float('nan'), 0, (0, 0, 50, 50)),
            (0, math.inf, (0, 0, 50, 50)),
            (0, 0, (0, 0, math.inf, 50)),
            (True, 0, (0, 0, 50, 50)),
            (0, 0, (0, 0, '50', 50)),
        ]
        for x, y, box in cases:
            with self.subTest(box=box, x=x, y=y):
                self.assertIsNone(normalized_mask_point(x, y, box))


class NativeBrushDraftTkTests(unittest.TestCase):
    def setUp(self):
        try:
            import tkinter as tk
            from tkinter import ttk
            root = tk.Tk()
        except (ImportError, tk.TclError) as exc:
            self.skipTest(f'Tk unavailable: {exc}')
        self.root, self.tk, self.ttk = root, tk, ttk
        self.addCleanup(root.destroy)
        self.preview_calls = []
        self._fn = lambda **request: self._preview(**request)
        self.panel = NativeBrushDraftPanel(root, root, tk, ttk, preview_fn=self._fn)
        self.addCleanup(self.panel.shutdown)
        self.root.update()
        self.sha = 'a' * 64
        self.subject = 'subject-' + 'b' * 32
        self.source = _png()
        self.workdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.workdir.cleanup)
        self.project = Path(self.workdir.name) / 'my-project.smartsvg'
        self.project.write_bytes(b'my original V1 archive - never modify')
        self.before = self.project.read_bytes()

    def _preview(self, **request):
        self.preview_calls.append(request)
        return dict(subject_id=request['subject_id'],
                    project_sha256=request['expected_sha256'], persisted=False,
                    before_png_l8=self.source, after_png_l8=self.source,
                    changed_pixels=3, preview_mask_sha256_float32='c' * 64)

    def load(self):
        self.panel.load(project_path=str(self.project),
                        expected_sha256=self.sha,
                        subject_id=self.subject, preview_png=self.source)
        self.root.update()

    def stroke(self):
        left, top, width, height = self.panel._box
        cx, cy = left + width // 2, top + height // 2
        self.panel._press(SimpleNamespace(x=cx, y=cy))
        self.panel._drag(SimpleNamespace(x=cx+1, y=cy))
        self.panel._release(None)

    def receive(self):
        end = time.monotonic() + 8
        while self.panel._busy and time.monotonic() < end:
            self.root.update()
            time.sleep(0.01)
        self.root.update()
        self.assertFalse(self.panel._busy)

    def test_actual_mouse_stroke_calls_proven_backend_and_never_writes(self):
        self.load()
        self.stroke()
        self.assertTrue(self.panel.preview())
        self.receive()
        self.assertEqual(len(self.preview_calls), 1)
        request = self.preview_calls[0]
        self.assertEqual(request['project_path'], str(self.project))
        self.assertEqual(request['subject_id'], self.subject)
        self.assertEqual(request['expected_sha256'], self.sha)
        self.assertEqual(request['mode'], 'add')
        self.assertEqual(request['radius'], 0.05)
        self.assertGreaterEqual(len(request['points']), 1)
        self.assertLessEqual(len(request['points']), MAX_GESTURE_POINTS)
        self.assertTrue(all(0 <= x < 1 and 0 <= y < 1 for x, y in request['points']))
        self.assertIsNotNone(self.panel._result_images)
        self.panel.show('before')
        self.assertEqual(self.panel._variant, 'before')
        self.panel.show('after')
        self.panel.discard()
        self.assertIsNone(self.panel._result_images)
        self.assertEqual(self.project.read_bytes(), self.before)

    def test_cpu_digest_is_pinned_and_discard_invalidates_save_signature(self):
        self.load()
        self.stroke()
        self.assertTrue(self.panel.preview())
        self.receive()
        self.assertIsNotNone(self.panel._result_images)
        self.assertEqual(self.panel._verified_save_request[0], 'c' * 64)
        self.panel.discard()
        self.assertIsNone(self.panel._verified_save_request)
        self.assertEqual(self.project.read_bytes(), self.before)

    def test_missing_cpu_digest_refuses_preview_without_writing(self):
        self.panel.shutdown()
        def missing(**request):
            return dict(subject_id=request['subject_id'],
                        project_sha256=request['expected_sha256'],
                        persisted=False, before_png_l8=self.source,
                        after_png_l8=self.source, changed_pixels=1)
        self.panel = NativeBrushDraftPanel(
            self.root, self.root, self.tk, self.ttk, preview_fn=missing)
        self.load()
        self.stroke()
        self.assertTrue(self.panel.preview())
        self.receive()
        self.assertIsNone(self.panel._verified_save_request)
        self.assertIsNone(self.panel._result_images)
        self.assertEqual(self.project.read_bytes(), self.before)

    def test_click_on_letterbox_keeps_existing_comparison_and_revision(self):
        self.load()
        self.stroke()
        self.assertTrue(self.panel.preview())
        self.receive()
        result = self.panel._result_images
        token = self.panel._token
        calls = len(self.preview_calls)
        self.panel._press(SimpleNamespace(x=-10, y=-10))
        self.panel._release(None)
        self.assertIs(self.panel._result_images, result)
        self.assertEqual(self.panel._token, token)
        self.assertEqual(len(self.preview_calls), calls)
        self.assertEqual(self.project.read_bytes(), self.before)

    def test_mode_and_radius_changes_invalidate_stale_comparison(self):
        self.load()
        self.stroke()
        points = [p[:] for p in self.panel._points]
        self.assertTrue(self.panel.preview())
        self.receive()
        self.assertIsNotNone(self.panel._result_images)
        self.panel.mode.set('Effacer')
        self.panel.mode_picker.event_generate('<<ComboboxSelected>>')
        self.root.update()
        self.assertIsNone(self.panel._result_images)
        self.assertEqual(self.panel._points, points)
        self.assertTrue(self.panel.preview())
        self.receive()
        self.assertEqual(self.preview_calls[-1]['mode'], 'erase')
        self.assertIsNotNone(self.panel._result_images)
        self.panel.radius.set('0.10')
        self.panel.radius_picker.event_generate('<<ComboboxSelected>>')
        self.root.update()
        self.assertIsNone(self.panel._result_images)
        self.assertTrue(self.panel.preview())
        self.receive()
        self.assertEqual(self.preview_calls[-1]['radius'], 0.10)
        self.assertEqual(self.project.read_bytes(), self.before)

    def test_malformed_or_huge_png_never_reaches_tk_decoder(self):
        from unittest.mock import patch
        huge = bytearray(self.source)
        struct.pack_into('>I', huge, 16, 60000)
        with patch.object(self.tk, 'PhotoImage',
                          side_effect=AssertionError('unbounded decode')):
            self.panel.load(project_path=str(self.project), expected_sha256=self.sha,
                            subject_id=self.subject, preview_png=bytes(huge))
        self.assertIsNone(self.panel._identity)
        self.assertEqual(self.project.read_bytes(), self.before)
        # Exercise a real async reply with a pinned request: missing CPU proof
        # or stale generation must not short-circuit this PNG decoder guard.
        self.panel.shutdown()
        def malformed(**request):
            return dict(
                subject_id=request['subject_id'],
                project_sha256=request['expected_sha256'],
                persisted=False,
                before_png_l8=bytes(huge), after_png_l8=self.source,
                changed_pixels=1, preview_mask_sha256_float32='c' * 64)
        self.panel = NativeBrushDraftPanel(
            self.root, self.root, self.tk, self.ttk, preview_fn=malformed)
        self.load()
        self.stroke()
        self.assertTrue(self.panel.preview())
        with patch.object(self.tk, 'PhotoImage',
                          side_effect=AssertionError('unbounded decode')):
            self.receive()
        self.assertIsNone(self.panel._result_images)
        self.assertIn('refusé', self.panel.status.get())
        self.assertEqual(self.project.read_bytes(), self.before)

    def test_missing_proof_invalid_source_and_outside_click_refused(self):
        self.panel.load(project_path=str(self.project), expected_sha256='invalid',
                        subject_id=self.subject, preview_png=self.source)
        self.assertIsNone(self.panel._identity)
        self.assertFalse(self.panel.preview())
        self.load()
        self.panel._press(SimpleNamespace(x=-10, y=-10))
        self.panel._release(None)
        self.assertEqual(self.panel._points, [])
        self.assertFalse(self.panel.preview())
        self.assertEqual(self.preview_calls, [])
        self.assertEqual(self.project.read_bytes(), self.before)

    def test_overlong_drag_fails_closed_instead_of_silent_truncation(self):
        self.load()
        left, top, width, height = self.panel._box
        for i in range(MAX_GESTURE_POINTS + 3):
            self.panel._append(left + (i + 1) % width, top + 1)
        self.assertTrue(self.panel._overflow)
        self.assertFalse(self.panel.preview())
        self.assertEqual(self.preview_calls, [])
        self.panel.discard()
        self.assertFalse(self.panel._overflow)
        self.assertEqual(self.project.read_bytes(), self.before)

    def test_save_requires_preview_and_explicit_confirmation(self):
        from unittest.mock import Mock
        writer = Mock()
        self.panel.shutdown()
        self.panel = NativeBrushDraftPanel(
            self.root, self.root, self.tk, self.ttk, preview_fn=self._fn,
            save_fn=writer, confirm_fn=lambda: False)
        self.load()
        self.assertFalse(self.panel.save())
        self.stroke()
        self.assertFalse(self.panel.save())
        self.assertTrue(self.panel.preview())
        self.receive()
        self.assertFalse(self.panel.save())
        writer.assert_not_called()
        self.assertEqual(self.project.read_bytes(), self.before)

    def test_confirmed_save_reuses_exact_cpu_gesture_and_invalidates_panel(self):
        from unittest.mock import Mock
        writer = Mock(return_value={
            'status': 'subject_brush_saved', 'persisted': True,
            'subject_id': self.subject, 'project_sha256': 'd' * 64})
        refreshed = Mock()
        self.panel.shutdown()
        self.panel = NativeBrushDraftPanel(
            self.root, self.root, self.tk, self.ttk, preview_fn=self._fn,
            save_fn=writer, confirm_fn=lambda: True, on_saved=refreshed)
        self.load()
        self.stroke()
        self.assertTrue(self.panel.preview())
        self.receive()
        expected = [p[:] for p in self.panel._points]
        self.assertTrue(self.panel.save())
        kwargs = writer.call_args.kwargs
        self.assertEqual(kwargs['points'], expected)
        self.assertEqual(kwargs['expected_preview_mask_sha256_float32'], 'c'*64)
        self.assertEqual(kwargs['expected_sha256'], self.sha)
        self.assertEqual(kwargs['subject_id'], self.subject)
        self.assertIs(kwargs['confirmed'], True)
        self.assertTrue(kwargs['command_id'].startswith('native-'))
        refreshed.assert_called_once()
        self.assertIsNone(self.panel._identity)
        self.assertIsNone(self.panel._verified_save_request)
        self.assertFalse(self.panel.save())
        writer.assert_called_once()
        # Mock writer intentionally does not touch the archive.
        self.assertEqual(self.project.read_bytes(), self.before)

    def test_uncertain_writer_receipt_forces_reinspection_not_retry(self):
        from unittest.mock import Mock
        writer = Mock(return_value={'persisted': False})
        self.panel.shutdown()
        self.panel = NativeBrushDraftPanel(
            self.root, self.root, self.tk, self.ttk, preview_fn=self._fn,
            save_fn=writer, confirm_fn=lambda: True)
        self.load()
        self.stroke()
        self.assertTrue(self.panel.preview())
        self.receive()
        self.assertFalse(self.panel.save())
        self.assertIn('réexaminez', self.panel.status.get())
        self.assertIsNone(self.panel._identity)
        self.assertIsNone(self.panel._verified_save_request)
        self.assertFalse(self.panel.save())
        writer.assert_called_once()
        self.assertEqual(self.project.read_bytes(), self.before)

    def test_cpu_job_freezes_mouse_gesture_and_pins_exact_preview_request(self):
        started, release = Event(), Event()
        def slow(**request):
            started.set()
            if not release.wait(5):
                raise RuntimeError('timeout')
            return self._preview(**request)
        self.panel.shutdown()
        self.panel = NativeBrushDraftPanel(
            self.root, self.root, self.tk, self.ttk, preview_fn=slow)
        self.load()
        self.stroke()
        original = [point[:] for point in self.panel._points]
        self.assertTrue(self.panel.preview())
        token = self.panel._token
        try:
            self.assertTrue(started.wait(timeout=5))
            left, top, width, height = self.panel._box
            event = SimpleNamespace(x=left + width // 3, y=top + height // 3)
            # Queued drag and new press cannot mutate an in-flight gesture.
            self.panel._drag(event)
            self.panel._press(event)
            self.panel._drag(event)
            self.assertEqual(self.panel._points, original)
            self.assertEqual(self.panel._token, token)
            self.assertTrue(self.panel._busy)
            release.set()
            self.receive()
            digest, accepted_token, frozen = self.panel._verified_save_request
            self.assertEqual(digest, 'c' * 64)
            self.assertEqual(accepted_token, token)
            self.assertEqual(frozen[0], (str(self.project), self.sha, self.subject))
            self.assertEqual(frozen[1:3], ('add', 0.05))
            self.assertEqual(frozen[3], tuple(tuple(p) for p in original))
            self.assertEqual(self.preview_calls[0]['points'], original)
            self.assertEqual(self.project.read_bytes(), self.before)
        finally:
            release.set()

    def test_stroke_change_during_cpu_work_refuses_stale_reply(self):
        started, release = Event(), Event()
        def slow(**request):
            started.set()
            if not release.wait(5):
                raise RuntimeError('timeout')
            return self._preview(**request)
        self.panel.shutdown()
        self.panel = NativeBrushDraftPanel(
            self.root, self.root, self.tk, self.ttk, preview_fn=slow)
        self.load()
        self.stroke()
        self.assertTrue(self.panel.preview())
        try:
            self.assertTrue(started.wait(timeout=5))
            # Simulate an unexpected external mutation bypassing Tk gestures.
            self.panel._points.append([0.1, 0.2])
            release.set()
            self.receive()
            self.assertIsNone(self.panel._verified_save_request)
            self.assertIsNone(self.panel._result_images)
            self.assertIn('refusé', self.panel.status.get())
            self.assertEqual(self.project.read_bytes(), self.before)
        finally:
            release.set()

    def test_previous_result_is_ignored_on_project_change(self):
        started, release = Event(), Event()
        def slow(**request):
            started.set()
            if not release.wait(5):
                raise RuntimeError('timeout')
            return self._preview(**request)
        self.panel.shutdown()
        self.panel = NativeBrushDraftPanel(
            self.root, self.root, self.tk, self.ttk, preview_fn=slow)
        self.load()
        self.stroke()
        self.assertTrue(self.panel.preview())
        try:
            self.assertTrue(started.wait(timeout=5))
            self.panel.load()
            self.assertIsNone(self.panel._identity)
            release.set()
            for _ in range(6):
                self.root.update()
                time.sleep(0.03)
            self.assertIsNone(self.panel._result_images)
            self.assertEqual(self.project.read_bytes(), self.before)
        finally:
            release.set()

    def test_shutdown_rejects_late_canvas_gestures_without_mutating_archive(self):
        self.load()
        self.stroke()
        self.panel.shutdown()
        points_before = [point[:] for point in self.panel._points]
        self.panel._press(SimpleNamespace(x=10, y=10))
        self.panel._drag(SimpleNamespace(x=11, y=10))
        # A late release must not touch controls in a destroyed Tk window.
        from unittest.mock import patch
        with patch.object(self.panel, '_controls',
                          side_effect=AssertionError('closed widget accessed')):
            self.panel._release(None)
        self.panel.discard()
        self.assertEqual(self.panel._points, points_before)
        self.assertFalse(self.panel.preview())
        self.assertEqual(self.project.read_bytes(), self.before)

    def test_late_before_after_callback_does_not_draw_destroyed_widgets(self):
        self.load()
        self.stroke()
        self.assertTrue(self.panel.preview())
        self.receive()
        self.assertIsNotNone(self.panel._result_images)
        variant_before = self.panel._variant
        self.panel.shutdown()
        from unittest.mock import patch
        with patch.object(self.panel, '_draw',
                          side_effect=AssertionError('closed canvas accessed')):
            self.panel.show('before')
            self.panel.show('after')
        self.assertEqual(self.panel._variant, variant_before)
        self.assertEqual(self.project.read_bytes(), self.before)

    def test_late_resize_after_shutdown_does_not_touch_destroyed_canvas(self):
        self.load()
        self.panel.shutdown()
        from unittest.mock import patch
        with patch.object(self.panel.canvas, 'delete',
                          side_effect=AssertionError('closed canvas accessed')):
            self.panel._draw()
            self.panel._draw(SimpleNamespace(width=200, height=100))
        self.assertEqual(self.project.read_bytes(), self.before)

    def test_closed_panel_never_reenables_before_after_controls(self):
        self.load()
        self.stroke()
        self.assertTrue(self.panel.preview())
        self.receive()
        self.assertIsNotNone(self.panel._result_images)
        self.panel.shutdown()
        # An async or late UI refresh must not re-enable a closed panel.
        self.panel._controls()
        self.assertEqual(str(self.panel.before_button.cget('state')), 'disabled')
        self.assertEqual(str(self.panel.after_button.cget('state')), 'disabled')
        self.assertEqual(self.project.read_bytes(), self.before)

    def test_invalid_backend_pixel_count_is_rejected_without_tk_callback_crash(self):
        # The counter is rendered after the backend exception handler; a
        # missing or malformed value must fail closed before images are shown.
        for bad_count in (None, True, -1, "3", 2.5):
            with self.subTest(bad_count=bad_count):
                self.panel.shutdown()
                def bad(**request):
                    return dict(subject_id=request['subject_id'],
                                project_sha256=request['expected_sha256'],
                                persisted=False, before_png_l8=self.source,
                                after_png_l8=self.source,
                                changed_pixels=bad_count)
                self.panel = NativeBrushDraftPanel(
                    self.root, self.root, self.tk, self.ttk, preview_fn=bad)
                self.load()
                self.stroke()
                self.assertTrue(self.panel.preview())
                self.receive()
                self.assertIsNone(self.panel._result_images)
                self.assertIn('refusé', self.panel.status.get())
                self.assertEqual(self.project.read_bytes(), self.before)

    def test_rejected_backend_data_is_not_displayed(self):
        self.panel.shutdown()
        def bad(**request):
            return dict(subject_id='subject-' + '0'*32,
                        project_sha256=request['expected_sha256'],
                        persisted=False, before_png_l8=self.source,
                        after_png_l8=self.source, changed_pixels=1)
        self.panel = NativeBrushDraftPanel(
            self.root, self.root, self.tk, self.ttk, preview_fn=bad)
        self.load()
        self.stroke()
        self.assertTrue(self.panel.preview())
        self.receive()
        self.assertIsNone(self.panel._result_images)
        self.assertIn('refusé', self.panel.status.get())
        self.assertEqual(self.project.read_bytes(), self.before)


if __name__ == '__main__':
    unittest.main()
