"""V3.5 W02: keyboard navigation is scoped to the native Atelier subject picker."""
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from native_atelier_tk_v34 import NativeAtelierPanel


class Variable:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class SubjectKeyboardNavigationTests(unittest.TestCase):
    def setUp(self):
        self.panel = NativeAtelierPanel.__new__(NativeAtelierPanel)
        self.panel.subjects = {"one": object(), "two": object(), "three": object()}
        self.panel.selection = Variable("one")
        self.panel._history_future = None
        self.panel._history_confirming = False
        self.rendered = []
        self.panel.render = lambda: self.rendered.append(self.panel.selection.get())

    def test_alt_right_and_left_use_existing_subject_navigation(self):
        self.assertEqual(self.panel._next_subject_key(), "break")
        self.assertEqual(self.panel.selection.get(), "two")
        self.assertEqual(self.panel._previous_subject_key(), "break")
        self.assertEqual(self.panel.selection.get(), "one")
        self.assertEqual(self.rendered, ["two", "one"])

    def test_boundaries_do_not_wrap_or_render(self):
        self.assertEqual(self.panel._previous_subject_key(), "break")
        self.assertEqual(self.panel.selection.get(), "one")
        self.panel.selection.set("three")
        self.assertEqual(self.panel._next_subject_key(), "break")
        self.assertEqual(self.panel.selection.get(), "three")
        self.assertEqual(self.rendered, [])

    def test_busy_history_prevents_navigation(self):
        self.panel._history_confirming = True
        self.assertEqual(self.panel._next_subject_key(), "break")
        self.assertEqual(self.panel.selection.get(), "one")
        self.assertEqual(self.rendered, [])

    def test_unknown_selection_fails_closed(self):
        self.panel.selection.set("missing")
        self.assertEqual(self.panel._next_subject_key(), "break")
        self.assertEqual(self.panel.selection.get(), "missing")
        self.assertEqual(self.rendered, [])

    def test_real_tk_picker_has_scoped_shortcuts(self):
        import tkinter as tk
        from tkinter import ttk
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("No graphical Tk session available")
        self.addCleanup(root.destroy)
        root.withdraw()
        panel = NativeAtelierPanel(root, tk, ttk)
        self.addCleanup(panel.shutdown)
        self.assertTrue(panel.picker.bind("<Alt-Left>"))
        self.assertTrue(panel.picker.bind("<Alt-Right>"))
        self.assertFalse(root.bind("<Alt-Left>"))
        self.assertFalse(root.bind("<Alt-Right>"))


if __name__ == "__main__":
    unittest.main()
