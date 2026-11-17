"""V3.5 W02/T-SEL-02: compose bounded native brush zones before saving."""
from pathlib import Path
import sys
import unittest


ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from native_brush_draft_tk_v34 import (  # noqa: E402
    MAX_DRAFT_STROKES, NativeBrushDraftPanel, dispatch_preview_request,
)


class Variable:
    def __init__(self, value=""):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class MultiZoneDraftTests(unittest.TestCase):
    def make_panel(self):
        panel = NativeBrushDraftPanel.__new__(NativeBrushDraftPanel)
        panel._closed = False
        panel._identity = ("C:/synthetic.smartsvg", "a" * 64,
                           "subject-" + "b" * 32)
        panel._busy = False
        panel._save_pending = False
        panel._points = [[0.1, 0.2], [0.3, 0.4]]
        panel._redo_points = []
        panel._strokes = []
        panel._redo_strokes = []
        panel._overflow = False
        panel._result_images = None
        panel._verified_save_request = ("stale",)
        panel._inflight_request = ("stale",)
        panel._variant = "after"
        panel._token = 4
        panel.mode = Variable("Ajouter")
        panel.radius = Variable("0.05")
        panel.status = Variable()
        panel._draw = lambda: None
        panel._controls = lambda: None
        return panel

    def test_add_zone_freezes_mode_radius_and_points_then_opens_a_new_zone(self):
        panel = self.make_panel()

        self.assertTrue(panel.add_draft_zone())

        self.assertEqual(panel._strokes, [{
            "mode": "add", "radius": 0.05,
            "points": [[0.1, 0.2], [0.3, 0.4]],
        }])
        self.assertEqual(panel._points, [])
        self.assertEqual(panel._redo_points, [])
        self.assertIsNone(panel._verified_save_request)
        self.assertIsNone(panel._inflight_request)
        self.assertIn("1 zone", panel.status.get())

        panel.mode.set("Effacer")
        panel.radius.set("0.10")
        panel._points = [[0.6, 0.7]]
        self.assertEqual(panel._draft_strokes(), [
            {"mode": "add", "radius": 0.05,
             "points": [[0.1, 0.2], [0.3, 0.4]]},
            {"mode": "erase", "radius": 0.10,
             "points": [[0.6, 0.7]]},
        ])

    def test_zone_limit_and_remove_last_zone_fail_closed(self):
        panel = self.make_panel()
        panel._strokes = [
            {"mode": "add", "radius": 0.02, "points": [[0.1, 0.1]]}
            for _ in range(MAX_DRAFT_STROKES)
        ]
        before = list(panel._strokes)

        self.assertFalse(panel.add_draft_zone())
        self.assertEqual(panel._strokes, before)
        self.assertIn(str(MAX_DRAFT_STROKES), panel.status.get())

        panel._points = []
        self.assertTrue(panel.remove_last_draft_zone())
        self.assertEqual(len(panel._strokes), MAX_DRAFT_STROKES - 1)
        self.assertEqual(len(panel._redo_strokes), 1)
        self.assertTrue(panel.remove_last_draft_zone())

    def test_removed_zone_can_be_restored_locally_without_calling_a_writer(self):
        panel = self.make_panel()
        zone = {"mode": "erase", "radius": 0.10,
                "points": [[0.2, 0.3], [0.4, 0.5]]}
        panel._points = []
        panel._strokes = [zone]
        panel._save_fn = lambda **_request: self.fail("local redo called writer")
        panel._save_many_fn = lambda **_request: self.fail("local redo called writer")

        self.assertTrue(panel.remove_last_draft_zone())
        zone["points"][0][0] = 0.9
        self.assertEqual(panel._strokes, [])
        self.assertEqual(panel._redo_strokes[0]["points"][0][0], 0.2)

        self.assertTrue(panel.restore_last_draft_zone())
        self.assertEqual(panel._strokes, [{
            "mode": "erase", "radius": 0.10,
            "points": [[0.2, 0.3], [0.4, 0.5]],
        }])
        self.assertEqual(panel._redo_strokes, [])
        self.assertIsNone(panel._verified_save_request)
        self.assertIsNone(panel._inflight_request)

    def test_ctrl_z_and_ctrl_y_fall_back_to_zone_history(self):
        panel = self.make_panel()
        panel._points = []
        panel._strokes = [{
            "mode": "add", "radius": 0.05, "points": [[0.1, 0.2]],
        }]

        self.assertEqual(panel._undo_draft_key(), "break")
        self.assertEqual(panel._strokes, [])
        self.assertEqual(len(panel._redo_strokes), 1)
        self.assertEqual(panel._redo_draft_key(), "break")
        self.assertEqual(len(panel._strokes), 1)
        self.assertEqual(panel._redo_strokes, [])

    def test_new_point_after_zone_undo_discards_zone_redo_branch(self):
        panel = self.make_panel()
        panel._points = []
        panel._box = (0, 0, 100, 100)
        panel._strokes = [{
            "mode": "add", "radius": 0.05, "points": [[0.1, 0.2]],
        }]
        self.assertTrue(panel.remove_last_draft_zone())

        panel._append(50, 50)

        self.assertEqual(panel._redo_strokes, [])
        self.assertFalse(panel.restore_last_draft_zone())

    def test_preview_dispatch_uses_legacy_contract_for_one_zone_and_batch_for_many(self):
        calls = []

        def one(**request):
            calls.append(("one", request))
            return "single"

        def many(**request):
            calls.append(("many", request))
            return "batch"

        identity = {
            "project_path": "C:/synthetic.smartsvg",
            "expected_sha256": "a" * 64,
            "subject_id": "subject-" + "b" * 32,
        }
        first = {"mode": "add", "radius": 0.05, "points": [[0.1, 0.2]]}
        second = {"mode": "erase", "radius": 0.10, "points": [[0.6, 0.7]]}

        self.assertEqual(
            dispatch_preview_request(one, many, {**identity, "strokes": [first]}),
            "single")
        self.assertEqual(calls[-1], ("one", {**identity, **first}))
        self.assertEqual(
            dispatch_preview_request(
                one, many, {**identity, "strokes": [first, second]}),
            "batch")
        self.assertEqual(calls[-1], (
            "many", {**identity, "strokes": [first, second]}))

    def test_remove_zone_is_blocked_during_cpu_or_after_preview(self):
        for attribute, value in (
            ("_busy", True), ("_save_pending", True),
            ("_result_images", {"after": object()}), ("_closed", True),
        ):
            with self.subTest(attribute=attribute):
                panel = self.make_panel()
                panel._strokes = [
                    {"mode": "add", "radius": 0.05,
                     "points": [[0.1, 0.2]]}
                ]
                panel._points = []
                setattr(panel, attribute, value)
                self.assertFalse(panel.remove_last_draft_zone())
                self.assertEqual(len(panel._strokes), 1)

    def test_discard_enabled_for_frozen_only_draft_and_disabled_when_saving(self):
        class Button:
            def __init__(self):
                self.state = None

            def configure(self, **options):
                self.state = options.get("state")

        panel = self.make_panel()
        panel._points = []
        panel._strokes = [{
            "mode": "add", "radius": 0.05, "points": [[0.1, 0.2]],
        }]
        panel.mode_picker = Button()
        panel.radius_picker = Button()
        panel.preview_button = Button()
        panel.undo_button = Button()
        panel.redo_button = Button()
        panel.discard_button = Button()
        panel.save_button = Button()
        panel.add_zone_button = Button()
        panel.remove_zone_button = Button()
        panel.restore_zone_button = Button()
        panel.before_button = Button()
        panel.after_button = Button()
        panel._controls = NativeBrushDraftPanel._controls.__get__(panel)

        panel._controls()
        self.assertEqual(panel.discard_button.state, "normal")
        self.assertEqual(panel.preview_button.state, "normal")

        panel._save_pending = True
        panel._controls()
        self.assertEqual(panel.discard_button.state, "disabled")

        panel._save_pending = False
        panel._strokes = []
        panel._controls()
        self.assertEqual(panel.discard_button.state, "disabled")

    def test_confirmed_multi_zone_save_uses_grouped_writer_once(self):
        panel = self.make_panel()
        panel._strokes = [{
            "mode": "add", "radius": 0.05, "points": [[0.1, 0.2]],
        }]
        panel.mode.set("Effacer")
        panel.radius.set("0.10")
        panel._points = [[0.6, 0.7]]
        strokes = panel._draft_strokes()
        bound = panel._bound_request(strokes)
        panel._result_images = {"after": object()}
        panel._verified_save_request = ("c" * 64, panel._token, bound)
        panel._confirm_fn = lambda: True
        panel._on_saved = None
        calls = []
        panel._save_fn = lambda **_request: self.fail("batch used single writer")

        def save_many(**request):
            calls.append(request)
            return {
                "status": "subject_brushes_saved", "persisted": True,
                "subject_id": panel._identity[2], "project_sha256": "d" * 64,
            }

        panel._save_many_fn = save_many

        self.assertTrue(panel.save())
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0]["strokes"], strokes)
        self.assertTrue(calls[0]["confirmed"])
        self.assertEqual(calls[0]["expected_preview_mask_sha256_float32"],
                         "c" * 64)
        self.assertIsNone(panel._identity)
        self.assertEqual(panel._strokes, [])

    def test_multi_zone_save_never_calls_writer_without_literal_confirmation(self):
        panel = self.make_panel()
        panel._strokes = [{
            "mode": "add", "radius": 0.05, "points": [[0.1, 0.2]],
        }]
        strokes = panel._draft_strokes()
        bound = panel._bound_request(strokes)
        panel._result_images = {"after": object()}
        panel._verified_save_request = ("c" * 64, panel._token, bound)
        panel._confirm_fn = lambda: False
        panel._on_saved = None
        panel._save_many_fn = lambda **_request: self.fail("writer called")
        panel._save_fn = lambda **_request: self.fail("writer called")

        self.assertFalse(panel.save())
        self.assertEqual(panel._identity[1], "a" * 64)


if __name__ == "__main__":
    unittest.main()
