"""V3.5 W02/T-SEL-02: compose bounded native brush zones before saving."""
from pathlib import Path
import sys
import unittest


ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from native_brush_draft_tk_v34 import (  # noqa: E402
    MAX_DRAFT_STROKES, NativeBrushDraftPanel, dispatch_preview_request,
    _MODES, _VISIBLE_MODES,
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

    def test_visible_mask_intentions_keep_engine_modes_and_distinguish_zone_history(self):
        self.assertEqual(_VISIBLE_MODES, ("Garder (masque)", "Masquer (masque)"))
        self.assertEqual([_MODES[label] for label in _VISIBLE_MODES],
                         ["add", "erase"])
        self.assertNotIn("Ajouter", _VISIBLE_MODES)
        self.assertNotIn("Effacer", _VISIBLE_MODES)
        panel = self.make_panel()
        panel.mode.set(_VISIBLE_MODES[0])
        self.assertTrue(panel.add_draft_zone())
        self.assertEqual(panel._strokes[0]["mode"], "add")
        panel.mode.set(_VISIBLE_MODES[1])
        panel._points = [[0.6, 0.7]]
        self.assertEqual(panel._draft_strokes()[-1]["mode"], "erase")
        self.assertIsNone(panel._verified_save_request)

    def test_tk_constructor_wires_visible_readonly_mode_picker_and_change_event(self):
        """Verify the actual constructor call shape without requiring a display."""
        import ast
        import inspect
        import textwrap

        tree = ast.parse(textwrap.dedent(inspect.getsource(NativeBrushDraftPanel.__init__)))
        assignments = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Assign)
            and any(isinstance(target, ast.Attribute)
                    and target.attr == "mode_picker" for target in node.targets)
        ]
        self.assertEqual(len(assignments), 1)
        picker = assignments[0].value
        self.assertIsInstance(picker, ast.Call)
        self.assertIsInstance(picker.func, ast.Attribute)
        self.assertEqual(picker.func.attr, "Combobox")
        options = {kw.arg: kw.value for kw in picker.keywords}
        self.assertIsInstance(options["values"], ast.Name)
        self.assertEqual(options["values"].id, "_VISIBLE_MODES")
        self.assertEqual(ast.literal_eval(options["state"]), "readonly")
        self.assertIsInstance(options["textvariable"], ast.Attribute)
        self.assertEqual(options["textvariable"].attr, "mode")
        bindings = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "bind"
            and isinstance(node.func.value, ast.Attribute)
            and node.func.value.attr == "mode_picker"
        ]
        self.assertTrue(any(
            len(call.args) >= 2
            and isinstance(call.args[0], ast.Constant)
            and call.args[0].value == "<<ComboboxSelected>>"
            and isinstance(call.args[1], ast.Attribute)
            and call.args[1].attr == "_parameter_changed"
            for call in bindings
        ))

    def test_brush_actions_remain_visible_at_large_text_scale(self):
        try:
            import tkinter as tk
            from tkinter import ttk
        except ImportError:
            self.skipTest('Tk unavailable')
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest('Graphical Tk unavailable')
        root.geometry('560x540')
        root.tk.call('tk', 'scaling', 2.0)
        panel = NativeBrushDraftPanel(root, root, tk, ttk)
        try:
            root.update()
            actions = (panel.preview_button, panel.before_button, panel.after_button,
                       panel.undo_button, panel.redo_button, panel.discard_button,
                       panel.save_button, panel.add_zone_button,
                       panel.remove_zone_button, panel.restore_zone_button)
            for button in actions:
                with self.subTest(label=button.cget('text')):
                    self.assertTrue(button.winfo_viewable())
                    self.assertGreaterEqual(button.winfo_width(), button.winfo_reqwidth())
                    self.assertLessEqual(button.winfo_rootx() + button.winfo_width(),
                                         root.winfo_rootx() + root.winfo_width())
                    self.assertLessEqual(button.winfo_rooty() + button.winfo_height(),
                                         root.winfo_rooty() + root.winfo_height())
            self.assertGreaterEqual(panel.canvas.winfo_height(), 64)
        finally:
            panel.shutdown()
            root.destroy()

    def test_real_tk_mode_picker_values_and_selection_invalidate_preview(self):
        """Exercise the real ttk widget when a graphical Tk session exists."""
        try:
            import tkinter as tk
            from tkinter import ttk
        except ImportError as exc:
            self.skipTest(f"Tk unavailable: {type(exc).__name__}")
        try:
            root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest(f"Graphical Tk unavailable: {type(exc).__name__}")
        root.withdraw()
        panel = None
        try:
            parent = ttk.Frame(root)
            parent.pack()
            panel = NativeBrushDraftPanel(root, parent, tk, ttk)
            picker = panel.mode_picker
            # An unbound panel deliberately disables editing until a verified Subject is selected.
            self.assertEqual(str(picker.cget("state")), "disabled")
            panel._identity = ("C:/synthetic.smartsvg", "a" * 64,
                               "subject-" + "b" * 32)
            panel._controls()
            self.assertEqual(tuple(picker.cget("values")), _VISIBLE_MODES)
            self.assertEqual(str(picker.cget("state")), "readonly")
            self.assertEqual(picker.get(), _VISIBLE_MODES[0])
            self.assertNotIn("Ajouter", picker.cget("values"))
            panel._identity = ("C:/synthetic.smartsvg", "a" * 64,
                               "subject-" + "b" * 32)
            panel._verified_save_request = ("stale",)
            panel._inflight_request = ("stale",)
            previous_token = panel._token
            picker.current(1)
            picker.event_generate("<<ComboboxSelected>>")
            root.update()
            self.assertEqual(panel.mode.get(), _VISIBLE_MODES[1])
            self.assertEqual(_MODES[panel.mode.get()], "erase")
            self.assertIsNone(panel._verified_save_request)
            self.assertIsNone(panel._inflight_request)
            self.assertGreater(panel._token, previous_token)
            self.assertEqual(str(picker.cget("state")), "readonly")
        finally:
            if panel is not None:
                panel.shutdown()
            root.destroy()

    def test_invalid_mode_or_radius_rejects_zone_without_mutating_draft(self):
        for field, invalid in (("mode", "mode-inconnu"), ("radius", "999")):
            with self.subTest(field=field):
                panel = self.make_panel()
                getattr(panel, field).set(invalid)
                before = [point[:] for point in panel._points]
                self.assertFalse(panel.add_draft_zone())
                self.assertEqual(panel._strokes, [])
                self.assertEqual(panel._points, before)
                self.assertEqual(panel._token, 4)
                self.assertEqual(panel._verified_save_request, ("stale",))
                self.assertIn("invalide", panel.status.get())

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
