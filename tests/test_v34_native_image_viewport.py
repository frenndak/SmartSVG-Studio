"""Exercise the native image controls with actual Tk when available."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'engine'))


class ImageViewportTests(unittest.TestCase):
    def test_fit_preserves_aspect_and_never_enlarges(self):
        from native_image_viewport_v34 import fit_factor

        self.assertEqual(fit_factor(960, 470, 480, 235), 2)
        self.assertEqual(fit_factor(300, 471, 480, 235), 3)
        self.assertEqual(fit_factor(8, 12, 480, 235), 1)

    def test_fit_factor_handles_transient_zero_canvas_without_division(self):
        from native_image_viewport_v34 import fit_factor

        # Tk can report a zero-sized canvas while constructing/minimizing.
        self.assertEqual(fit_factor(12, 8, 0, 0), 12)
        self.assertEqual(fit_factor(12, 8, 0, 4), 12)
        self.assertEqual(fit_factor(12, 8, 6, 0), 8)
        # Never upscale a tiny source.
        self.assertEqual(fit_factor(1, 1, 400, 300), 1)
        for dimensions in ((0, 8), (12, 0), (-1, 8), (12, -1)):
            with self.subTest(dimensions=dimensions):
                with self.assertRaises(ValueError):
                    fit_factor(*dimensions, 400, 300)

    def test_configure_during_zero_size_layout_preserves_viewport_and_manual_zoom(self):
        from native_image_viewport_v34 import NativeImageViewport

        class FakeImage:
            def width(self): return 960
            def height(self): return 470
            def subsample(self, factor): return self

        class FakeCanvas:
            w, h = 0, 0
            def winfo_width(self): return self.w
            def winfo_height(self): return self.h

        viewport = NativeImageViewport.__new__(NativeImageViewport)
        viewport.original = FakeImage()
        viewport.canvas = FakeCanvas()
        viewport.fit_scale = None
        viewport.auto_fit = True
        shown = []
        viewport._show = lambda image: shown.append(image)
        # Exercise the actual Configure callback and fit consumer, not only
        # the pure fit_factor helper. No Tk window or V1 write is needed.
        viewport._resize(None)
        self.assertEqual(len(shown), 1)
        self.assertGreaterEqual(viewport.fit_scale, 1)
        viewport.canvas.w, viewport.canvas.h = 482, 237
        viewport._resize(None)
        self.assertEqual(viewport.fit_scale, 2)
        viewport.actual_size()
        self.assertFalse(viewport.auto_fit)
        self.assertIsNone(viewport.fit_scale)
        before = len(shown)
        viewport.canvas.w, viewport.canvas.h = 0, 0
        viewport._resize(None)
        self.assertEqual(len(shown), before)
        self.assertIsNone(viewport.fit_scale)

    def test_incremental_zoom_keeps_manual_scale_across_resizes_and_clamps(self):
        from native_image_viewport_v34 import NativeImageViewport

        class FakeImage:
            def __init__(self, width=960, height=470):
                self.w, self.h = width, height
            def width(self): return self.w
            def height(self): return self.h
            def subsample(self, factor):
                return FakeImage(max(1, self.w // factor),
                                 max(1, self.h // factor))

        class FakeCanvas:
            w, h = 482, 237
            def winfo_width(self): return self.w
            def winfo_height(self): return self.h

        viewport = NativeImageViewport.__new__(NativeImageViewport)
        viewport.original = FakeImage()
        viewport.canvas = FakeCanvas()
        viewport.fit_scale = None
        viewport.auto_fit = True
        shown = []
        viewport._show = lambda image: shown.append(
            (image.width(), image.height()))

        viewport.fit()
        self.assertEqual(viewport.fit_scale, 2)
        self.assertEqual(shown[-1], (480, 235))
        viewport.zoom_in()
        self.assertEqual(viewport.fit_scale, 1)
        self.assertFalse(viewport.auto_fit)
        self.assertEqual(shown[-1], (960, 470))
        viewport.canvas.w, viewport.canvas.h = 202, 102
        viewport._resize(None)
        self.assertEqual(viewport.fit_scale, 1,
                         'Manual zoom must survive resizing the Atelier pane')
        viewport.zoom_out()
        self.assertEqual(viewport.fit_scale, 2)
        self.assertEqual(shown[-1], (480, 235))
        viewport.fit()
        self.assertEqual(viewport.fit_scale, 5)
        self.assertTrue(viewport.auto_fit)
        viewport.actual_size()
        self.assertIsNone(viewport.fit_scale)
        self.assertFalse(viewport.auto_fit)
        self.assertEqual(shown[-1], (960, 470))
        self.assertEqual(viewport._zoom_out_key(None), 'break')
        self.assertEqual(viewport.fit_scale, 2)
        self.assertEqual(viewport._zoom_in_key(None), 'break')
        self.assertEqual(viewport.fit_scale, 1)
        # Keyboard fit restores auto-fit; 0 restores native pixels.
        self.assertEqual(viewport._fit_key(None), 'break')
        self.assertTrue(viewport.auto_fit)
        self.assertEqual(viewport.fit_scale, 5)
        self.assertEqual(viewport._actual_size_key(None), 'break')
        self.assertFalse(viewport.auto_fit)
        self.assertIsNone(viewport.fit_scale)
        self.assertEqual(shown[-1], (960, 470))
        for _ in range(40):
            viewport.zoom_out()
        self.assertEqual(viewport.fit_scale, 32)
        viewport.zoom_out()
        self.assertEqual(viewport.fit_scale, 32)
        for _ in range(40):
            viewport.zoom_in()
        self.assertEqual(viewport.fit_scale, 1)
        no_image = len(shown)
        viewport.original = None
        viewport.zoom_in()
        viewport.zoom_out()
        viewport.actual_size()
        self.assertEqual(len(shown), no_image)

    def test_native_pixels_pan_and_reset_on_image_replacement(self):
        import tkinter as tk
        from tkinter import ttk
        from native_image_viewport_v34 import NativeImageViewport

        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest('No graphical Tk session available')
        self.addCleanup(root.destroy)
        viewport = NativeImageViewport(root, tk, ttk)
        original = tk.PhotoImage(master=root, width=960, height=470)
        original.put('#123456', to=(900, 440))
        viewport.load(original)
        root.update()
        self.assertEqual((viewport.display.width(), viewport.display.height()), (480, 235))

        viewport.actual_size()
        root.update()
        self.assertEqual(viewport.display.get(900, 440), (18, 52, 86))
        # Real Tk key bindings, not only direct handler calls.
        # Windows CI has no foreground WM focus: focus_set() is ignored.
        # Force focus only in this isolated Tk test so actual key-event
        # dispatch is exercised, rather than just calling the handlers.
        viewport.canvas.focus_force()
        root.update()
        self.assertEqual(root.focus_get(), viewport.canvas)
        viewport.canvas.event_generate('<Home>')
        root.update()
        self.assertTrue(viewport.auto_fit)
        self.assertEqual(viewport.fit_scale, 2)
        viewport.canvas.event_generate('<Key-0>')
        root.update()
        self.assertFalse(viewport.auto_fit)
        self.assertIsNone(viewport.fit_scale)
        viewport.canvas.xview_moveto(1)
        viewport.canvas.yview_moveto(1)
        self.assertGreater(viewport.canvas.xview()[0], 0)
        self.assertGreater(viewport.canvas.yview()[0], 0)

        # Exercise the actual mouse bindings, not just Canvas scrolling APIs.
        viewport.canvas.xview_moveto(0)
        viewport.canvas.yview_moveto(0)
        root.update()
        viewport.canvas.event_generate('<ButtonPress-1>', x=120, y=100)
        viewport.canvas.event_generate('<B1-Motion>', x=40, y=30)
        root.update()
        self.assertGreater(viewport.canvas.xview()[0], 0)
        self.assertGreater(viewport.canvas.yview()[0], 0)

        # Use a large image so both zoom levels remain scrollable.
        viewport.load(tk.PhotoImage(master=root, width=1920, height=940))
        root.update()
        viewport.actual_size()
        root.update()
        # Zooming a panned image must retain its relative viewport centre.
        viewport.canvas.xview_moveto(0.45)
        viewport.canvas.yview_moveto(0.30)
        root.update()
        before_x = sum(viewport.canvas.xview()) / 2
        before_y = sum(viewport.canvas.yview()) / 2
        viewport.zoom_out()
        root.update()
        after_x = sum(viewport.canvas.xview()) / 2
        after_y = sum(viewport.canvas.yview()) / 2
        self.assertAlmostEqual(before_x, after_x, delta=0.08)
        self.assertAlmostEqual(before_y, after_y, delta=0.08)

        viewport.load(tk.PhotoImage(master=root, width=32, height=16))
        root.update()
        self.assertEqual(viewport.canvas.xview()[0], 0)
        self.assertEqual(viewport.canvas.yview()[0], 0)
        viewport.load(None)
        self.assertEqual(viewport.canvas.find_all(), ())

    def test_real_tk_configure_zero_size_then_restore_preserves_manual_zoom(self):
        import tkinter as tk
        from tkinter import ttk
        from native_image_viewport_v34 import NativeImageViewport

        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest('No graphical Tk session available')
        self.addCleanup(root.destroy)
        viewport = NativeImageViewport(root, tk, ttk)
        viewport.load(tk.PhotoImage(master=root, width=960, height=470))
        root.update()
        viewport.actual_size()
        root.update()
        self.assertFalse(viewport.auto_fit)
        self.assertIsNone(viewport.fit_scale)

        # Dispatch a real Tk Configure event with zero reported dimensions.
        # The callback reads winfo_* rather than event.width/height; this
        # proves event dispatch and state safety, not a zero-sized WM canvas.
        viewport.canvas.event_generate('<Configure>', width=0, height=0)
        root.update()
        self.assertFalse(viewport.auto_fit)
        self.assertIsNone(viewport.fit_scale)
        viewport.canvas.event_generate('<Configure>', width=480, height=235)
        root.update()
        self.assertFalse(viewport.auto_fit)
        self.assertIsNone(viewport.fit_scale)
        viewport.fit()
        root.update()
        self.assertTrue(viewport.auto_fit)
        self.assertGreaterEqual(viewport.fit_scale, 1)
