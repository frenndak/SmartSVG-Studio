"""V3.5 W02: keyboard navigation is scoped to the native Atelier subject picker."""
from pathlib import Path
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from native_atelier_tk_v34 import NativeAtelierPanel
from native_brush_draft_tk_v34 import NativeBrushDraftPanel


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

    def prepare_draft(self):
        self.brush = self.panel._brush_panel = SimpleNamespace(
            has_draft=True, shutdown=Mock())
        self.dialog = self.panel._brush_dialog = SimpleNamespace(
            lift=Mock(), destroy=Mock())
        self.panel._brush_key = ('project', 'revision', 'one')

    def test_leave_requires_confirmation_and_keeps_draft_on_cancel(self):
        self.prepare_draft()
        with patch('tkinter.messagebox.askyesno', return_value=False) as ask:
            self.assertFalse(self.panel._request_close_brush())
        self.assertEqual(ask.call_args.kwargs['default'], 'no')
        self.assertIs(ask.call_args.kwargs['parent'], self.dialog)
        self.assertIs(self.panel._brush_panel, self.brush)
        self.brush.shutdown.assert_not_called()
        self.dialog.destroy.assert_not_called()

    def test_accepting_discard_closes_once_and_empty_panel_needs_no_prompt(self):
        self.prepare_draft()
        with patch('tkinter.messagebox.askyesno', return_value=True) as ask:
            self.assertTrue(self.panel._request_close_brush())
            self.assertTrue(self.panel._request_close_brush())
            self.assertEqual(ask.call_count, 1)
        self.assertIsNone(self.panel._brush_panel)
        self.brush.shutdown.assert_called_once()
        self.dialog.destroy.assert_called_once()
        self.prepare_draft()
        self.brush.has_draft = False
        with patch('tkinter.messagebox.askyesno') as ask:
            self.assertTrue(self.panel._request_close_brush())
            ask.assert_not_called()

    def test_button_and_picker_keep_selected_subject_when_discard_is_declined(self):
        self.prepare_draft()
        with patch('tkinter.messagebox.askyesno', return_value=False):
            self.assertFalse(self.panel.next_subject())
            self.assertEqual(self.panel.selection.get(), 'one')
            self.panel.selection.set('three')  # ttk sets the variable before the event
            self.panel._pick_subject()
        self.assertEqual(self.panel.selection.get(), 'one')
        self.assertEqual(self.rendered, [])
        self.assertIs(self.panel._brush_panel, self.brush)
        with patch('tkinter.messagebox.askyesno', return_value=True):
            self.assertTrue(self.panel.next_subject())
        self.assertEqual(self.rendered, ['two'])
        self.assertIsNone(self.panel._brush_panel)

    def test_discard_prompt_keeps_active_subject_during_nested_events(self):
        self.prepare_draft()
        def confirm(*_args, **_kwargs):
            self.assertEqual(self.panel.selection.get(), 'one')
            self.assertFalse(self.panel.next_subject())
            return False
        with patch('tkinter.messagebox.askyesno', side_effect=confirm) as ask:
            self.panel.selection.set('two')
            self.panel._pick_subject()
            ask.assert_called_once()
        self.assertEqual(self.panel.selection.get(), 'one')
        self.brush.shutdown.assert_not_called()

    def test_both_active_and_redo_only_edits_count_as_drafts(self):
        brush = NativeBrushDraftPanel.__new__(NativeBrushDraftPanel)
        fields = ('_points', '_strokes', '_redo_points', '_redo_strokes')
        for field in fields:
            setattr(brush, field, [])
        for field in fields:
            with self.subTest(field=field):
                self.assertFalse(brush.has_draft)
                setattr(brush, field, [object()])
                self.assertTrue(brush.has_draft)
                setattr(brush, field, [])

    def test_real_tk_close_protocol_and_picker_preserve_unconfirmed_draft(self):
        import tkinter as tk
        from tkinter import ttk
        from standalone_desktop_v34 import load_native_preview
        from test_v34_native_app_shell import create_atelier_project

        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("No graphical Tk session available")
        self.addCleanup(root.destroy)
        with tempfile.TemporaryDirectory() as directory:
            path, _ = create_atelier_project(directory)
            before = path.read_bytes()
            state, _ = load_native_preview(path)
            panel = NativeAtelierPanel(root, tk, ttk)
            self.addCleanup(panel.shutdown)
            panel.load(state['atelier_snapshot'], project_path=str(path))
            self.assertTrue(panel.open_brush())
            first, second = tuple(panel.subjects)
            brush, dialog = panel._brush_panel, panel._brush_dialog
            brush._points = [[0.25, 0.25]]
            self.assertTrue(brush.add_draft_zone())
            brush._points = [[0.5, 0.5]]
            root.update()
            with patch('tkinter.messagebox.askyesno', return_value=False) as ask:
                close_command = dialog.protocol('WM_DELETE_WINDOW')
                self.assertTrue(close_command)
                root.tk.call(close_command)
                panel.selection.set(second)
                panel.picker.event_generate('<<ComboboxSelected>>')
                root.update()
                self.assertEqual(ask.call_count, 2)
                self.assertEqual(panel.selection.get(), first)
                self.assertTrue(dialog.winfo_exists())
                self.assertIs(panel._brush_panel, brush)
                self.assertEqual(len(brush._strokes), 1)
                self.assertEqual(brush._points, [[0.5, 0.5]])
                self.assertEqual(path.read_bytes(), before)
            with patch('tkinter.messagebox.askyesno', return_value=True):
                self.assertTrue(panel.next_subject())
            self.assertEqual(panel.selection.get(), second)
            self.assertFalse(dialog.winfo_exists())
            self.assertEqual(path.read_bytes(), before)

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

    def test_real_tk_picker_delivers_alt_arrows_for_persisted_subjects(self):
        import tkinter as tk
        from tkinter import ttk
        from standalone_desktop_v34 import load_native_preview
        from test_v34_native_app_shell import create_atelier_project

        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("No graphical Tk session available")
        self.addCleanup(root.destroy)
        root.geometry("800x600")
        panel = NativeAtelierPanel(root, tk, ttk)
        self.addCleanup(panel.shutdown)

        with tempfile.TemporaryDirectory() as directory:
            project, expected_ids = create_atelier_project(directory)
            before = project.read_bytes()
            state, _preview = load_native_preview(project)
            self.assertTrue(state["ok"])
            snapshot = state["atelier_snapshot"]
            self.assertEqual(
                {subject.subject_id for subject in snapshot.subjects},
                set(expected_ids),
            )

            panel.load(snapshot, project_path=str(project))
            subjects = tuple(panel.subjects)
            self.assertEqual(len(subjects), 2)
            root.update()
            panel.picker.focus_force()
            root.update()
            self.assertEqual(root.focus_get(), panel.picker)
            self.assertEqual(panel.selection.get(), subjects[0])

            panel.picker.event_generate("<Alt-Right>")
            root.update()
            self.assertEqual(panel.selection.get(), subjects[1])
            panel.picker.event_generate("<Alt-Left>")
            root.update()
            self.assertEqual(panel.selection.get(), subjects[0])
            self.assertEqual(project.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
