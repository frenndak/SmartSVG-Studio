"""V34-047 / UX-09: responsive native reader without ComfyUI or Tk worker calls."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from threading import Event, get_ident
import sys
import tempfile
import unittest

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from smartsvg_core.native_preview_jobs_v34 import LatestOnlyJob
from smartsvg_core.project_recovery import save_with_recovery
from standalone_desktop_v34 import load_native_preview

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


if __name__ == "__main__":
    unittest.main()
