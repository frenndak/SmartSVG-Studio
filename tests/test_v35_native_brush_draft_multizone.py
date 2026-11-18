"""V3.5 W02/T-SEL-02: compose bounded native brush zones before saving."""
from pathlib import Path
from types import SimpleNamespace
import importlib.util
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

    def test_uncertain_save_retains_every_zone_but_blocks_retry(self):
        panel = self.make_panel()
        panel._strokes = [{"mode": "add", "radius": 0.05,
                           "points": [[0.2, 0.3], [0.3, 0.4]]}]
        panel._points = [[0.6, 0.7], [0.7, 0.8]]
        panel._redo_strokes = [{"mode": "erase", "radius": 0.02,
                                "points": [[0.8, 0.9]]}]
        panel._redo_points = [[0.9, 0.9]]
        before = panel._draft_strokes()
        redo_before = [dict(panel._redo_strokes[0])]
        panel._result_images = {"after": object()}
        panel._variant = "before"
        panel._confirm_fn = lambda: True
        panel._on_saved = None
        calls = []
        def uncertain(**_kwargs):
            calls.append(True)
            raise OSError("private writer failure")
        panel._save_many_fn = uncertain
        bound = panel._bound_request(before)
        panel._verified_save_request = ("c" * 64, panel._token, bound)

        self.assertFalse(panel.save())
        self.assertEqual(panel._draft_strokes(), before)
        self.assertEqual(panel._redo_strokes, redo_before)
        self.assertEqual(panel._redo_points, [[0.9, 0.9]])
        self.assertEqual(panel._variant, "after")
        self.assertTrue(panel.has_draft)
        self.assertIsNone(panel._identity)
        self.assertIsNone(panel._verified_save_request)
        self.assertFalse(panel.save())
        self.assertEqual(len(calls), 1)
        self.assertIn("brouillon", panel.status.get().lower())
        self.assertNotIn("private", panel.status.get())

    def test_uncertain_draft_offers_recheck_but_not_edit_or_save(self):
        class Button:
            def __init__(self): self.options = {}
            def configure(self, **options): self.options.update(options)
        panel = self.make_panel()
        panel._recovery_identity, panel._identity = panel._identity, None
        panel._result_images = None
        for name in ('mode_picker', 'radius_picker', 'preview_button', 'undo_button',
                     'redo_button', 'discard_button', 'save_button', 'add_zone_button',
                     'remove_zone_button', 'restore_zone_button', 'before_button', 'after_button'):
            setattr(panel, name, Button())
        panel._controls = NativeBrushDraftPanel._controls.__get__(panel)
        panel._controls()
        self.assertEqual(panel.preview_button.options['state'], 'normal')
        self.assertEqual(panel.preview_button.options['text'], 'Vérifier et recalculer')
        self.assertEqual(panel.discard_button.options['state'], 'normal')
        for name in ('mode_picker', 'radius_picker', 'undo_button', 'save_button', 'add_zone_button'):
            self.assertEqual(getattr(panel, name).options['state'], 'disabled')

    def test_abandoning_an_uncertain_draft_does_not_claim_project_unchanged(self):
        panel = self.make_panel()
        panel._recovery_identity, panel._identity = panel._identity, None
        self.assertTrue(panel.discard())
        self.assertFalse(panel.has_draft)
        self.assertIsNone(panel._recovery_identity)
        self.assertIn('vérifiez', panel.status.get().lower())
        self.assertNotIn('pas été modifié', panel.status.get())

    def test_late_recheck_cannot_restore_an_abandoned_draft(self):
        from threading import Event
        from smartsvg_core.native_preview_jobs_v34 import LatestOnlyJob
        started, release = Event(), Event()
        panel = self.make_panel()
        panel._recovery_identity, panel._identity = panel._identity, None
        pending = []
        panel.root = SimpleNamespace(after=lambda _delay, callback: pending.append(callback))

        def delayed(_request):
            started.set()
            if not release.wait(5):
                raise TimeoutError('test timeout')
            return {}
        panel._job = LatestOnlyJob(delayed)
        try:
            self.assertTrue(panel.preview())
            future = panel._job._future
            self.assertTrue(started.wait(5))
            self.assertTrue(panel.discard())
            release.set()
            future.result(timeout=15)
            pending.pop(0)()
            self.assertIsNone(panel._identity)
            self.assertIsNone(panel._recovery_identity)
            self.assertIsNone(panel._verified_save_request)
            self.assertFalse(panel.has_draft)
        finally:
            release.set()
            panel._job.close()

    def test_ui_limits_match_brush_preview_contract(self):
        from native_brush_draft_tk_v34 import MAX_GESTURE_POINTS, MAX_DRAFT_POINTS_TOTAL
        from smartsvg_core.subject_brush_preview_g33e import (
            MAX_PREVIEW_POINTS, MAX_PREVIEW_POINTS_TOTAL, MAX_PREVIEW_STROKES,
        )
        self.assertEqual(MAX_GESTURE_POINTS, MAX_PREVIEW_POINTS)
        self.assertEqual(MAX_DRAFT_STROKES, MAX_PREVIEW_STROKES)
        self.assertEqual(MAX_DRAFT_POINTS_TOTAL, MAX_PREVIEW_POINTS_TOTAL)

    @unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'),
                         'The real brush writer requires NumPy/Pillow')
    def test_successive_mouse_gestures_reach_the_real_grouped_writer(self):
        from hashlib import sha256
        import tempfile
        from test_v34_native_app_shell import create_atelier_project
        from smartsvg_core.native_subject_preview_v34 import preview_native_subject_strokes
        from smartsvg_core.native_subject_save_v34 import save_native_subject_strokes
        from smartsvg_core.project_archive import load_project

        with tempfile.TemporaryDirectory() as directory:
            path, subjects = create_atelier_project(directory)
            subject = next(iter(subjects))
            original = load_project(path)
            panel = self.make_panel()
            panel._identity = (str(path), sha256(path.read_bytes()).hexdigest(), subject)
            panel._points = []
            panel._box = (0, 0, 100, 100)
            panel.canvas = SimpleNamespace(focus_set=lambda: None)
            for x, y in ((20, 20), (80, 80)):
                panel._press(SimpleNamespace(x=x, y=y))
                panel._release(None)
            strokes = panel._draft_strokes()
            self.assertEqual(len(strokes), 2)
            self.assertEqual(strokes[0]['points'], [[0.2, 0.2]])
            self.assertEqual(strokes[1]['points'], [[0.8, 0.8]])
            preview = preview_native_subject_strokes(
                project_path=str(path), expected_sha256=panel._identity[1],
                subject_id=subject, strokes=strokes)
            panel._result_images = {'after': object()}
            panel._verified_save_request = (
                preview['preview_mask_sha256_float32'], panel._token,
                panel._bound_request(strokes))
            panel._confirm_fn = lambda: True
            panel._save_many_fn = save_native_subject_strokes
            panel._on_saved = None
            self.assertTrue(panel.save())

            reopened = load_project(path)
            self.assertEqual(len(reopened.document['editor_v216']['strokes']), 2)
            self.assertEqual(reopened.operations[-1]['kind'], 'save_subject_brushes_v35_w02_v1')
            self.assertEqual(reopened.resources, original.resources)
            self.assertEqual(reopened.subjects, original.subjects)

    @unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'),
                         'The real brush writer requires NumPy/Pillow')
    def test_uncertain_save_rechecks_revision_before_enabling_retry(self):
        from hashlib import sha256
        import tempfile
        from test_v34_native_app_shell import create_atelier_project
        from smartsvg_core.native_preview_jobs_v34 import LatestOnlyJob
        from smartsvg_core.native_subject_preview_v34 import (
            preview_native_subject_stroke, preview_native_subject_strokes,
        )
        from smartsvg_core.native_subject_save_v34 import save_native_subject_strokes
        from smartsvg_core.project_archive import load_project

        class Scheduler:
            def __init__(self): self.pending = []
            def after(self, _delay, callback): self.pending.append(callback)

        class Photo:
            def __init__(self, **_kwargs): pass
            def width(self): return 4
            def height(self): return 3

        for committed in (False, True):
            with self.subTest(committed=committed), tempfile.TemporaryDirectory() as directory:
                path, subjects = create_atelier_project(directory)
                subject = next(iter(subjects))
                panel = self.make_panel()
                panel._identity = (str(path), sha256(path.read_bytes()).hexdigest(), subject)
                panel._points = [[0.8, 0.8]]
                panel._strokes = [{"mode": "add", "radius": 0.05,
                                   "points": [[0.2, 0.2]]}]
                strokes = panel._draft_strokes()
                initial = preview_native_subject_strokes(
                    project_path=str(path), expected_sha256=panel._identity[1],
                    subject_id=subject, strokes=strokes)
                panel._identity_png = initial['before_png_l8']
                panel._result_images = {'after': object()}
                panel._verified_save_request = (
                    initial['preview_mask_sha256_float32'], panel._token,
                    panel._bound_request(strokes))
                panel._confirm_fn = lambda: True
                panel._on_saved = None
                panel.root = Scheduler()
                panel.tk = SimpleNamespace(PhotoImage=Photo)
                panel._job = LatestOnlyJob(lambda request: dispatch_preview_request(
                    preview_native_subject_stroke, preview_native_subject_strokes, request))

                def uncertain(**request):
                    if committed:
                        save_native_subject_strokes(**request)
                    raise OSError('uncertain result')
                panel._save_many_fn = uncertain
                try:
                    self.assertFalse(panel.save())
                    self.assertTrue(panel.has_draft)
                    self.assertIsNone(panel._identity)
                    self.assertFalse(panel.save())
                    revision_after_failure = path.read_bytes()

                    # The read-only check must never apply or repeat a write.
                    self.assertTrue(panel.preview())
                    future = panel._job._future
                    try:
                        future.result(timeout=15)
                    except Exception:
                        if not committed:
                            raise
                    panel.root.pending.pop(0)()
                    self.assertEqual(path.read_bytes(), revision_after_failure)

                    if committed:
                        self.assertIsNone(panel._identity)
                        self.assertTrue(panel.has_draft)
                        self.assertFalse(panel.save())
                        self.assertIn('modifié', panel.status.get().lower())
                        self.assertEqual(len(load_project(path).document['editor_v216']['strokes']), 2)
                    else:
                        self.assertIsNotNone(panel._identity)
                        self.assertIsNotNone(panel._verified_save_request)
                        panel._save_many_fn = save_native_subject_strokes
                        self.assertTrue(panel.save())
                        self.assertEqual(len(load_project(path).document['editor_v216']['strokes']), 2)
                finally:
                    panel._job.close()

    def test_next_gesture_preserves_preceding_stroke(self):
        panel = self.make_panel()
        panel._box = (0, 0, 100, 100)
        panel.canvas = SimpleNamespace(focus_set=lambda: None)
        panel._result_images = {"after": object()}
        panel._variant = "before"

        panel._press(SimpleNamespace(x=60, y=70))
        self.assertEqual(panel._strokes, [{"mode": "add", "radius": 0.05,
            "points": [[0.1, 0.2], [0.3, 0.4]]}])
        self.assertEqual(panel._points, [[0.6, 0.7]])
        self.assertIsNone(panel._verified_save_request)
        self.assertIsNone(panel._result_images)
        self.assertEqual(panel._variant, "after")

        panel._press(SimpleNamespace(x=80, y=90))
        self.assertEqual(len(panel._strokes), 2)
        self.assertEqual(panel._strokes[1]["points"], [[0.6, 0.7]])
        self.assertEqual(panel._points, [[0.8, 0.9]])

    def test_next_gesture_at_zone_limit_keeps_current_and_previous_zones(self):
        panel = self.make_panel()
        panel._box = (0, 0, 100, 100)
        panel.canvas = SimpleNamespace(focus_set=lambda: None)
        panel._strokes = [{"mode": "add", "radius": 0.05,
                           "points": [[0.1, 0.2]]}
                          for _ in range(MAX_DRAFT_STROKES - 1)]
        before = panel._draft_strokes()
        panel._press(SimpleNamespace(x=60, y=70))
        panel._drag(SimpleNamespace(x=61, y=71))
        panel._release(None)
        self.assertEqual(panel._draft_strokes(), before)
        self.assertIn(str(MAX_DRAFT_STROKES), panel.status.get())

    def test_total_point_limit_is_enforced_before_preview(self):
        panel = self.make_panel()
        panel._box = (0, 0, 100, 100)
        panel._strokes = [{"mode": "add", "radius": 0.05,
                           "points": [[j / 100.0, i / 10.0] for j in range(60)]}
                          for i in range(4)]
        panel._points = [[j / 100.0, 0.8] for j in range(15)]
        panel._append(50, 50)  # exactly 256 points
        self.assertEqual(sum(len(s["points"]) for s in panel._draft_strokes()), 256)
        self.assertFalse(panel._overflow)
        before = panel._draft_strokes()

        panel._append(51, 51)  # point 257 is not silently submitted
        self.assertEqual(panel._draft_strokes(), before)
        self.assertTrue(panel._overflow)
        self.assertIn("256", panel.status.get())
        self.assertFalse(panel.preview())
        self.assertTrue(panel.undo_draft_point())
        self.assertFalse(panel._overflow)

    def test_starting_a_new_zone_at_total_limit_does_not_erase_draft(self):
        panel = self.make_panel()
        panel._box = (0, 0, 100, 100)
        panel.canvas = SimpleNamespace(focus_set=lambda: None)
        panel._strokes = [{"mode": "add", "radius": 0.05,
                           "points": [[j / 100.0, i / 10.0] for j in range(60)]}
                          for i in range(4)]
        panel._points = [[j / 100.0, 0.8] for j in range(16)]
        before = panel._draft_strokes()
        panel._press(SimpleNamespace(x=60, y=70))
        self.assertEqual(panel._draft_strokes(), before)
        self.assertIn("256", panel.status.get())



if __name__ == "__main__":
    unittest.main()
