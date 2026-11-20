"""W02 GUI: reject stale subject-picker events without discarding an open draft."""
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))
from native_atelier_tk_v34 import NativeAtelierPanel


class Variable:
    def __init__(self, value):
        self.value = value
    def get(self):
        return self.value
    def set(self, value):
        self.value = value


class StalePickerTests(unittest.TestCase):
    def test_foreign_selection_does_not_close_draft_or_render(self):
        panel = NativeAtelierPanel.__new__(NativeAtelierPanel)
        panel.subjects = {"first": object(), "second": object()}
        panel.selection = Variable("foreign")  # combobox updates before event
        panel._brush_key = ("project", "revision", "first")
        panel._request_close_brush = Mock(return_value=True)
        panel.render = Mock()
        self.assertFalse(panel._pick_subject())
        self.assertEqual(panel.selection.get(), "first")
        panel._request_close_brush.assert_not_called()
        panel.render.assert_not_called()

    def test_stale_selection_without_draft_fails_closed(self):
        panel = NativeAtelierPanel.__new__(NativeAtelierPanel)
        panel.subjects = {"first": object()}
        panel.selection = Variable("removed")
        panel._brush_key = None
        panel.render = Mock()
        self.assertFalse(panel._pick_subject())
        panel.render.assert_not_called()

    def test_valid_selection_still_renders(self):
        panel = NativeAtelierPanel.__new__(NativeAtelierPanel)
        panel.subjects = {"first": object(), "second": object()}
        panel.selection = Variable("first")
        panel._brush_key = None
        panel.render = Mock()
        self.assertTrue(panel._select_subject("second"))
        self.assertEqual(panel.selection.get(), "second")
        panel.render.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
