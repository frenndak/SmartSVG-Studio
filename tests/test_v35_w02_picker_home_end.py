"""W02 picker-local Home/End navigation: no draft loss or foreign selection."""
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from native_atelier_tk_v34 import NativeAtelierPanel


class PickerJumpTests(unittest.TestCase):
    def panel(self, *, busy=False, active="b", draft=None):
        selection = SimpleNamespace(value=active)
        selection.get = lambda: selection.value
        selection.set = lambda value: setattr(selection, "value", value)
        panel = SimpleNamespace(
            busy=busy, subjects={"a": object(), "b": object(), "c": object()},
            selection=selection, _brush_key=draft, _request_close_brush=Mock(return_value=True),
            render=Mock())
        return panel

    def test_home_end_select_boundaries_and_render(self):
        p = self.panel()
        p._select_subject = lambda subject: NativeAtelierPanel._select_subject(p, subject)
        self.assertEqual(NativeAtelierPanel._first_subject_key(p), "break")
        self.assertEqual(p.selection.get(), "a")
        self.assertEqual(NativeAtelierPanel._last_subject_key(p), "break")
        self.assertEqual(p.selection.get(), "c")
        self.assertEqual(p.render.call_count, 2)

    def test_busy_or_empty_never_changes_selection(self):
        p = self.panel(busy=True)
        p._select_subject = Mock()
        self.assertEqual(NativeAtelierPanel._last_subject_key(p), "break")
        p._select_subject.assert_not_called()
        self.assertEqual(p.selection.get(), "b")
        p.busy = False
        p.subjects = {}
        self.assertEqual(NativeAtelierPanel._first_subject_key(p), "break")
        p._select_subject.assert_not_called()

    def test_unsaved_brush_draft_cancel_restores_original_selection(self):
        p = self.panel(active="b", draft=("project", "sha", "b"))
        p._select_subject = lambda subject: NativeAtelierPanel._select_subject(p, subject)
        p._request_close_brush.return_value = False
        self.assertEqual(NativeAtelierPanel._first_subject_key(p), "break")
        self.assertEqual(p.selection.get(), "b")
        p.render.assert_not_called()
        p._request_close_brush.assert_called_once()
        p._request_close_brush.return_value = True
        self.assertEqual(NativeAtelierPanel._last_subject_key(p), "break")
        self.assertEqual(p.selection.get(), "c")
        p.render.assert_called_once()

    def test_single_subject_is_stable(self):
        p = self.panel(active="a")
        p.subjects = {"a": object()}
        p._select_subject = lambda subject: NativeAtelierPanel._select_subject(p, subject)
        self.assertEqual(NativeAtelierPanel._last_subject_key(p), "break")
        self.assertEqual(p.selection.get(), "a")


if __name__ == "__main__":
    unittest.main()
