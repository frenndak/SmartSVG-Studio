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
        viewport.canvas.xview_moveto(1)
        viewport.canvas.yview_moveto(1)
        self.assertGreater(viewport.canvas.xview()[0], 0)
        self.assertGreater(viewport.canvas.yview()[0], 0)

        viewport.load(tk.PhotoImage(master=root, width=32, height=16))
        root.update()
        self.assertEqual(viewport.canvas.xview()[0], 0)
        self.assertEqual(viewport.canvas.yview()[0], 0)
        viewport.load(None)
        self.assertEqual(viewport.canvas.find_all(), ())
