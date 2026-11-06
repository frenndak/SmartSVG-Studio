"""V34-019: offline read-only desktop shell, synthetic archive contracts.

These tests do NOT claim a Tk window was opened on Windows. The actual GUI
requires a display; the headless probe and project-state logic run in CI.
"""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
SHELL = ENGINE / "standalone_desktop_v34.py"
FIXTURE = ENGINE / "tests" / "test_project_recovery_g14.py"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from smartsvg_core.project_recovery import save_with_recovery
from standalone_desktop_v34 import inspect_native_project


def synthetic_project():
    spec = spec_from_file_location("v34_desktop_g14_fixture", FIXTURE)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.fixture()


class NativeDesktopShellTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.directory = Path(tmp.name)
        self.path = self.directory / "projet.smartsvg"

    def snapshot(self):
        return {p.name: p.read_bytes() for p in self.directory.iterdir() if p.is_file()}

    def test_probe_runs_without_site_packages_tkinter_or_comfyui(self):
        output = subprocess.run(
            [sys.executable, "-I", "-S", str(SHELL), "--probe"],
            cwd=self.directory, capture_output=True, text=True, timeout=20)
        self.assertEqual(output.returncode, 0, output.stderr)
        result = json.loads(output.stdout)
        self.assertTrue(result["ok"])
        self.assertTrue(result["tkinter_lazy"])
        self.assertFalse(result["comfyui_required"])
        self.assertFalse(result["desktop_ui_tested"])
        self.assertFalse(result["windows_qualified"])
        self.assertEqual(self.snapshot(), {})

    def test_healthy_project_readonly_resource_counts(self):
        save_with_recovery(self.path, synthetic_project())
        before = self.snapshot()
        state = inspect_native_project(self.path)
        self.assertTrue(state["ok"])
        self.assertEqual(state["project_id"], "project-test")
        self.assertEqual((state["sources"], state["masks"], state["subjects"],
                          state["artifacts"]), (1, 1, 1, 0))
        self.assertFalse(state["automatic_restore"])
        self.assertFalse(state["windows_qualified"])
        self.assertEqual(self.snapshot(), before)

    def test_missing_project_no_creation(self):
        state = inspect_native_project(self.path)
        self.assertEqual(state["status"], "PROJECT_MISSING")
        self.assertFalse(state["ok"])
        self.assertEqual(self.snapshot(), {})

    def test_corrupt_project_never_repaired(self):
        self.path.write_bytes(b"corrupt archive")
        before = self.snapshot()
        state = inspect_native_project(self.path)
        self.assertEqual(state["status"], "PROJECT_UNRECOVERABLE")
        self.assertEqual(self.snapshot(), before)

    def test_recoverable_project_no_automatic_restore(self):
        save_with_recovery(self.path, synthetic_project())
        save_with_recovery(self.path, synthetic_project())
        self.path.write_bytes(b"corrupt main")
        before = self.snapshot()
        state = inspect_native_project(self.path)
        self.assertEqual(state["status"], "PROJECT_RECOVERABLE")
        self.assertEqual(state["previous"], "valid")
        self.assertFalse(state["automatic_restore"])
        self.assertEqual(self.snapshot(), before)

    def test_pending_backup_stops_as_is(self):
        save_with_recovery(self.path, synthetic_project())
        (self.directory / "projet.pending-backup.smartsvg").write_bytes(b"pending")
        before = self.snapshot()
        state = inspect_native_project(self.path)
        self.assertEqual(state["status"], "PENDING_BACKUP_REVIEW_REQUIRED")
        self.assertEqual(self.snapshot(), before)

    def test_changed_archive_between_inspections_fails_closed(self):
        save_with_recovery(self.path, synthetic_project())
        before = self.snapshot()
        with patch("standalone_desktop_v34._archive_sha256",
                   side_effect=["before", "after"]):
            state = inspect_native_project(self.path)
        self.assertFalse(state["ok"])
        self.assertEqual(state["status"], "PROJECT_CHANGED_DURING_INSPECTION")
        self.assertNotIn("project_id", state)
        self.assertEqual(self.snapshot(), before)

    def test_unexpected_extension_rejected_without_leaking_path(self):
        wrong = self.directory / "private.png"
        wrong.write_bytes(b"private")
        before = self.snapshot()
        state = inspect_native_project(wrong)
        self.assertEqual(state["error_code"], "INVALID_RECOVERY_PATH")
        self.assertNotIn(str(self.directory), str(state))
        self.assertEqual(self.snapshot(), before)

    def test_symlink_project_refused(self):
        target = self.directory / "vrai.smartsvg"
        save_with_recovery(target, synthetic_project())
        try:
            self.path.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks not available")
        before = self.snapshot()
        state = inspect_native_project(self.path)
        self.assertEqual(state["status"], "PROJECT_UNRECOVERABLE")
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
