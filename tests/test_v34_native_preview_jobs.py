"""V34-047 / UX-09: responsive native reader without ComfyUI or Tk worker calls."""
from dataclasses import replace
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from threading import Event, get_ident
from unittest.mock import patch
import sys
import tempfile
import unittest

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from smartsvg_core.native_preview_jobs_v34 import LatestOnlyJob
from smartsvg_core.project_archive import save_project
from smartsvg_core.project_recovery import save_with_recovery
from standalone_desktop_v34 import inspect_native_project, load_native_preview

FIXTURE = ENGINE / "tests" / "test_project_recovery_g14.py"
spec = spec_from_file_location("v34_worker_fixture", FIXTURE)
fixture_module = module_from_spec(spec)
spec.loader.exec_module(fixture_module)


class NativePreviewJobTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "source.smartsvg"

    def test_real_project_preview_on_worker_no_writes(self):
        save_with_recovery(self.path, fixture_module.fixture())
        before = {p.name: p.read_bytes() for p in self.path.parent.iterdir()}
        jobs = LatestOnlyJob(load_native_preview)
        self.addCleanup(jobs.close)
        version, future = jobs.submit(str(self.path))
        state, preview = future.result(timeout=15)
        self.assertTrue(jobs.current(version))
        self.assertTrue(state["ok"])
        self.assertEqual(preview.status, "READY_PNG")
        self.assertEqual(preview.source_id, "source-a")
        self.assertEqual({p.name: p.read_bytes() for p in self.path.parent.iterdir()},
                         before)

    def test_new_selection_invalidates_older_generation(self):
        entered = Event()
        release = Event()

        def slow_read(value):
            if value == "old":
                entered.set()
                if not release.wait(timeout=10):
                    raise RuntimeError("read timed out")
            return value

        jobs = LatestOnlyJob(slow_read)
        self.addCleanup(jobs.close)
        try:
            old_version, old = jobs.submit("old")
            self.assertTrue(entered.wait(timeout=5))
            new_version, new = jobs.submit("new")
            self.assertFalse(jobs.current(old_version))
            self.assertTrue(jobs.current(new_version))
            release.set()
            self.assertEqual(old.result(timeout=5), "old")
            self.assertEqual(new.result(timeout=5), "new")
        finally:
            release.set()

    def test_intermediate_queued_request_is_cancelled(self):
        entered = Event()
        release = Event()
        def read(value):
            if value == "block":
                entered.set()
                if not release.wait(timeout=10):
                    raise RuntimeError("blocked")
            return value

        jobs = LatestOnlyJob(read)
        self.addCleanup(jobs.close)
        try:
            jobs.submit("block")
            self.assertTrue(entered.wait(timeout=5))
            second_version, second = jobs.submit("second")
            last_version, last = jobs.submit("last")
            self.assertFalse(jobs.current(second_version))
            self.assertTrue(second.cancelled())
            release.set()
            self.assertTrue(jobs.current(last_version))
            self.assertEqual(last.result(timeout=5), "last")
        finally:
            release.set()

    def test_close_rejects_new_requests_and_stale_results(self):
        jobs = LatestOnlyJob(lambda value: value)
        version, future = jobs.submit("a")
        self.assertEqual(future.result(timeout=5), "a")
        jobs.close()
        self.assertFalse(jobs.current(version))
        with self.assertRaisesRegex(RuntimeError, "NATIVE_JOB_QUEUE_CLOSED"):
            jobs.submit("b")

    def test_worker_runs_off_gui_thread(self):
        main_id = get_ident()
        jobs = LatestOnlyJob(lambda _: get_ident())
        self.addCleanup(jobs.close)
        _, future = jobs.submit("x")
        self.assertNotEqual(future.result(timeout=5), main_id)

    def test_missing_project_reports_error_without_creation(self):
        jobs = LatestOnlyJob(load_native_preview)
        self.addCleanup(jobs.close)
        _, future = jobs.submit(str(self.path))
        state, preview = future.result(timeout=5)
        self.assertEqual(state["status"], "PROJECT_MISSING")
        self.assertIsNone(preview)
        self.assertFalse(self.path.exists())

    def test_pending_backup_stays_readonly(self):
        save_with_recovery(self.path, fixture_module.fixture())
        sidecar = self.path.parent / "source.pending-backup.smartsvg"
        sidecar.write_bytes(b"pending")
        before = {p.name: p.read_bytes() for p in self.path.parent.iterdir()}
        jobs = LatestOnlyJob(load_native_preview)
        self.addCleanup(jobs.close)
        _, future = jobs.submit(str(self.path))
        state, preview = future.result(timeout=5)
        self.assertEqual(state["status"], "PENDING_BACKUP_REVIEW_REQUIRED")
        self.assertIsNone(preview)
        self.assertEqual({p.name: p.read_bytes() for p in self.path.parent.iterdir()},
                         before)


    def test_same_project_id_replaced_after_inspection_is_not_mixed(self):
        original = fixture_module.fixture()
        save_project(self.path, original)
        # Different VALID archive, with the SAME project ID. The old code
        # compared only project_id, silently mixing its old summary and the
        # new content. This regression checks the exact swap boundary.
        second_path = self.path.parent / "replacement.smartsvg"
        save_project(second_path, replace(original, app_version="v34-swapped"))
        replacement_bytes = second_path.read_bytes()
        self.assertNotEqual(self.path.read_bytes(), replacement_bytes)
        first_inspect = inspect_native_project

        def swap_after_inspection(path):
            result = first_inspect(path)
            self.path.write_bytes(replacement_bytes)
            return result

        with patch("standalone_desktop_v34.inspect_native_project",
                   side_effect=swap_after_inspection):
            state, preview = load_native_preview(self.path)
        self.assertFalse(state["ok"])
        self.assertEqual(state["status"], "PROJECT_CHANGED_DURING_INSPECTION")
        self.assertIsNone(preview)
        self.assertEqual(self.path.read_bytes(), replacement_bytes)

    def test_same_id_swapped_after_second_read_is_rejected(self):
        original = fixture_module.fixture()
        save_project(self.path, original)
        second_path = self.path.parent / "replacement.smartsvg"
        save_project(second_path, replace(original, app_version="v34-swapped"))
        replacement_bytes = second_path.read_bytes()
        from standalone_desktop_v34 import load_project as original_load

        def swap_after_second_load(path):
            result = original_load(path)
            self.path.write_bytes(replacement_bytes)
            return result

        with patch("standalone_desktop_v34.load_project",
                   side_effect=swap_after_second_load):
            state, preview = load_native_preview(self.path)
        self.assertFalse(state["ok"])
        self.assertEqual(state["status"], "PROJECT_CHANGED_DURING_INSPECTION")
        self.assertIsNone(preview)

    def test_no_snapshot_on_non_project_extension(self):
        foreign = self.path.parent / "secret.txt"
        foreign.write_text("local-only", encoding="utf-8")
        before = foreign.read_bytes()
        state, preview = load_native_preview(foreign)
        self.assertFalse(state["ok"])
        self.assertEqual(state["error_code"], "INVALID_RECOVERY_PATH")
        self.assertIsNone(preview)
        self.assertEqual(foreign.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
