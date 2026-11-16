"""V3.5 W02/T-SEL-05: a brush draft point can be undone without persistence."""
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from native_brush_draft_tk_v34 import NativeBrushDraftPanel


class Variable:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class BrushDraftUndoTests(unittest.TestCase):
    def make_panel(self):
        panel = NativeBrushDraftPanel.__new__(NativeBrushDraftPanel)
        panel._closed = False
        panel._identity = ("C:/synthetic.smartsvg", "a" * 64, "subject-" + "b" * 32)
        panel._busy = False
        panel._save_pending = False
        panel._points = [[0.1, 0.2], [0.3, 0.4]]
        panel._redo_points = []
        panel._overflow = True
        panel._result_images = None
        panel._verified_save_request = ("stale",)
        panel._inflight_request = ("stale",)
        panel._variant = "after"
        panel._token = 7
        panel.status = Variable()
        panel._draw_calls = 0
        panel._control_calls = 0
        panel._draw = lambda: setattr(panel, "_draw_calls", panel._draw_calls + 1)
        panel._controls = lambda: setattr(panel, "_control_calls", panel._control_calls + 1)
        panel._save_fn = lambda **_kwargs: self.fail("undo must never call the writer")
        return panel

    def test_undo_removes_only_last_point_and_invalidates_stale_preview_proofs(self):
        panel = self.make_panel()

        self.assertTrue(panel.undo_draft_point())

        self.assertEqual(panel._points, [[0.1, 0.2]])
        self.assertEqual(panel._token, 8)
        self.assertFalse(panel._overflow)
        self.assertIsNone(panel._verified_save_request)
        self.assertIsNone(panel._inflight_request)
        self.assertIn("1 point", panel.status.get())
        self.assertEqual(panel._draw_calls, 1)
        self.assertEqual(panel._control_calls, 1)

    def test_undo_fails_closed_while_busy_saved_or_empty(self):
        for attribute, value in (
            ("_busy", True),
            ("_save_pending", True),
            ("_result_images", {"after": object()}),
            ("_points", []),
            ("_identity", None),
            ("_closed", True),
        ):
            with self.subTest(attribute=attribute):
                panel = self.make_panel()
                setattr(panel, attribute, value)
                before = list(panel._points)
                self.assertFalse(panel.undo_draft_point())
                self.assertEqual(panel._points, before)
                self.assertEqual(panel._token, 7)
                self.assertEqual(panel._draw_calls, 0)
                self.assertEqual(panel._control_calls, 0)

    def test_ctrl_z_handler_is_scoped_and_consumes_the_key(self):
        panel = self.make_panel()

        self.assertEqual(panel._undo_draft_key(), "break")
        self.assertEqual(panel._points, [[0.1, 0.2]])

    def test_redo_restores_last_undone_point_and_invalidates_stale_proofs(self):
        panel = self.make_panel()

        self.assertTrue(panel.undo_draft_point())
        panel._verified_save_request = ("stale",)
        panel._inflight_request = ("stale",)

        self.assertTrue(panel.redo_draft_point())

        self.assertEqual(panel._points, [[0.1, 0.2], [0.3, 0.4]])
        self.assertEqual(panel._redo_points, [])
        self.assertEqual(panel._token, 9)
        self.assertIsNone(panel._verified_save_request)
        self.assertIsNone(panel._inflight_request)
        self.assertEqual(panel._draw_calls, 2)
        self.assertEqual(panel._control_calls, 2)

    def test_new_point_after_undo_discards_the_redo_branch(self):
        panel = self.make_panel()
        panel._box = (0, 0, 100, 100)

        self.assertTrue(panel.undo_draft_point())
        panel._append(50, 50)

        self.assertEqual(panel._points, [[0.1, 0.2], [0.5, 0.5]])
        self.assertEqual(panel._redo_points, [])
        self.assertFalse(panel.redo_draft_point())

    def test_redo_fails_closed_without_a_verified_available_draft(self):
        for attribute, value in (
            ("_busy", True),
            ("_save_pending", True),
            ("_result_images", {"after": object()}),
            ("_redo_points", []),
            ("_identity", None),
            ("_closed", True),
        ):
            with self.subTest(attribute=attribute):
                panel = self.make_panel()
                panel._redo_points = [[0.3, 0.4]]
                panel._points = [[0.1, 0.2]]
                setattr(panel, attribute, value)
                before = list(panel._points)
                self.assertFalse(panel.redo_draft_point())
                self.assertEqual(panel._points, before)
                self.assertEqual(panel._token, 7)
                self.assertEqual(panel._draw_calls, 0)
                self.assertEqual(panel._control_calls, 0)

    def test_ctrl_y_handler_is_scoped_and_consumes_the_key(self):
        panel = self.make_panel()
        self.assertTrue(panel.undo_draft_point())

        self.assertEqual(panel._redo_draft_key(), "break")
        self.assertEqual(panel._points, [[0.1, 0.2], [0.3, 0.4]])

    def test_escape_discards_only_the_local_draft_and_consumes_the_key(self):
        panel = self.make_panel()
        panel._redo_points = [[0.5, 0.6]]
        panel._result_images = {"after": object()}

        self.assertEqual(panel._discard_draft_key(), "break")

        self.assertEqual(panel._points, [])
        self.assertEqual(panel._redo_points, [])
        self.assertIsNone(panel._result_images)
        self.assertIsNone(panel._verified_save_request)
        self.assertIsNone(panel._inflight_request)
        self.assertEqual(panel._token, 8)
        self.assertEqual(panel._draw_calls, 1)
        self.assertEqual(panel._control_calls, 1)


class BrushDraftUndoTkTests(unittest.TestCase):
    def test_real_canvas_owns_ctrl_z_binding_without_global_shortcut(self):
        import tkinter as tk
        from tkinter import ttk
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("No graphical Tk session available")
        self.addCleanup(root.destroy)
        root.geometry("600x450")
        panel = NativeBrushDraftPanel(root, root, tk, ttk)
        self.addCleanup(panel.shutdown)

        self.assertTrue(panel.canvas.bind("<Control-z>"))
        self.assertTrue(panel.canvas.bind("<Control-y>"))
        self.assertTrue(panel.canvas.bind("<Escape>"))
        self.assertFalse(root.bind("<Control-z>"))
        self.assertFalse(root.bind("<Control-y>"))
        self.assertFalse(root.bind("<Escape>"))
        self.assertEqual(str(panel.undo_button.cget("state")), "disabled")
        self.assertEqual(str(panel.redo_button.cget("state")), "disabled")

        root.update()
        window_left = root.winfo_rootx()
        window_right = window_left + root.winfo_width()
        for button in (
                panel.preview_button, panel.before_button, panel.after_button,
                panel.undo_button, panel.redo_button,
                panel.discard_button, panel.save_button):
            with self.subTest(button=button.cget("text")):
                self.assertTrue(button.winfo_ismapped())
                self.assertGreaterEqual(button.winfo_rootx(), window_left)
                self.assertLessEqual(
                    button.winfo_rootx() + button.winfo_width(), window_right)
        self.assertLess(
            panel.preview_button.winfo_rooty(), panel.undo_button.winfo_rooty())

        panel._identity = (
            "C:/synthetic.smartsvg", "a" * 64, "subject-" + "b" * 32
        )
        panel._points = [[0.1, 0.2], [0.3, 0.4]]
        panel._controls()
        root.update()
        panel.canvas.focus_force()
        root.update()
        self.assertEqual(root.focus_get(), panel.canvas)
        self.assertEqual(str(panel.undo_button.cget("state")), "normal")
        self.assertEqual(str(panel.redo_button.cget("state")), "disabled")

        panel.canvas.event_generate("<Control-z>")
        root.update()

        self.assertEqual(panel._points, [[0.1, 0.2]])
        self.assertEqual(str(panel.undo_button.cget("state")), "normal")
        self.assertEqual(str(panel.redo_button.cget("state")), "normal")

        panel.canvas.event_generate("<Control-y>")
        root.update()

        self.assertEqual(panel._points, [[0.1, 0.2], [0.3, 0.4]])
        self.assertEqual(str(panel.redo_button.cget("state")), "disabled")

        panel.canvas.event_generate("<Escape>")
        root.update()

        self.assertEqual(panel._points, [])
        self.assertEqual(str(panel.undo_button.cget("state")), "disabled")
        self.assertEqual(str(panel.redo_button.cget("state")), "disabled")


if __name__ == "__main__":
    unittest.main()
