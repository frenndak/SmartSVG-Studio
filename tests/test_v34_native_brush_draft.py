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
                    changed_pixels=3)

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
        self.load()
        result = dict(subject_id=self.subject, project_sha256=self.sha,
                      persisted=False, before_png_l8=self.source,
                      after_png_l8=bytes(huge), changed_pixels=1)
        completed = Future()
        completed.set_result(result)
        with patch.object(self.tk, 'PhotoImage',
                          side_effect=AssertionError('unbounded decode')):
            self.panel._receive(self.panel._token, 0, completed)
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
