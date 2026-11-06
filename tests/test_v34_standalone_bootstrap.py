"""V34-019 bootstrap contract (T-V34-21-01: import/read-only subset).

The full Windows desktop, UI, offline interception and edit/save gates are NOT
claimed here. Synthetic G1.4 projects reuse the existing test fixture.
"""
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"
BOOTSTRAP = ENGINE / "standalone_bootstrap_v34.py"
FIXTURE_FILE = ENGINE / "tests" / "test_project_recovery_g14.py"

if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from smartsvg_core.project_recovery import save_with_recovery


def synthetic_project():
    spec = spec_from_file_location("v34_bootstrap_g14_fixture", FIXTURE_FILE)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.fixture()


class StandaloneBootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.project = self.folder / "test.smartsvg"

    def call_native(self, *args):
        # -I -S excludes environment/site packages; use a different working
        # directory so the bootstrap cannot accidentally rely on repository cwd.
        result = subprocess.run(
            [sys.executable, "-I", "-S", str(BOOTSTRAP), *map(str, args)],
            cwd=self.folder,
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        self.assertFalse(result.stderr, result.stderr)
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            self.fail(f"Invalid bootstrap JSON: {result.stdout!r}: {exc}")
        return result.returncode, payload

    def snapshot(self):
        return {p.name: p.read_bytes() for p in self.folder.iterdir() if p.is_file()}

    def test_status_runs_without_comfyui_or_site_packages(self):
        code, payload = self.call_native("status")
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["comfyui_required"])
        self.assertEqual(payload["phase"], "V34-019_BOOTSTRAP_READONLY")
        self.assertFalse(payload["desktop_ui_available"])
        self.assertFalse(payload["windows_qualified"])
        self.assertEqual(self.snapshot(), {})

    def test_inspect_valid_v1_without_modification(self):
        save_with_recovery(self.project, synthetic_project())
        before = self.snapshot()
        code, payload = self.call_native("inspect", self.project)
        self.assertEqual(code, 0)
        self.assertEqual(payload["status"], "PROJECT_HEALTHY")
        self.assertEqual(payload["project_id"], "project-test")
        self.assertFalse(payload["automatic_restore"])
        self.assertTrue(payload["read_only"])
        self.assertEqual(self.snapshot(), before)

    def test_inspect_recoverable_does_not_restore(self):
        save_with_recovery(self.project, synthetic_project())
        save_with_recovery(self.project, synthetic_project())
        self.project.write_bytes(b"corrupt primary - preserve for diagnosis")
        before = self.snapshot()
        code, payload = self.call_native("inspect", self.project)
        self.assertEqual(code, 2)
        self.assertEqual(payload["status"], "PROJECT_RECOVERABLE")
        self.assertEqual(payload["previous"], "valid")
        self.assertFalse(payload["automatic_restore"])
        self.assertEqual(self.snapshot(), before)

    def test_pending_backup_requires_manual_review(self):
        save_with_recovery(self.project, synthetic_project())
        (self.folder / "test.pending-backup.smartsvg").write_bytes(b"pending")
        before = self.snapshot()
        code, payload = self.call_native("inspect", self.project)
        self.assertEqual(code, 2)
        self.assertEqual(payload["status"], "PENDING_BACKUP_REVIEW_REQUIRED")
        self.assertEqual(self.snapshot(), before)

    def test_invalid_project_is_not_repaired(self):
        self.project.write_bytes(b"broken archive")
        before = self.snapshot()
        code, payload = self.call_native("inspect", self.project)
        self.assertEqual(code, 2)
        self.assertEqual(payload["status"], "PROJECT_UNRECOVERABLE")
        self.assertEqual(self.snapshot(), before)

    def test_missing_project_is_reported_without_creating_file(self):
        code, payload = self.call_native("inspect", self.project)
        self.assertEqual(code, 2)
        self.assertEqual(payload["status"], "PROJECT_MISSING")
        self.assertEqual(self.snapshot(), {})

    def test_other_extension_rejected_without_leaking_path(self):
        foreign = self.folder / "personal-photo.png"
        foreign.write_bytes(b"personal-bytes")
        before = self.snapshot()
        code, payload = self.call_native("inspect", foreign)
        self.assertEqual(code, 2)
        self.assertEqual(payload["error_code"], "INVALID_RECOVERY_PATH")
        self.assertNotIn(str(self.folder), json.dumps(payload))
        self.assertEqual(self.snapshot(), before)

    def test_symlink_project_is_rejected_without_following(self):
        target = self.folder / "real.smartsvg"
        save_with_recovery(target, synthetic_project())
        try:
            self.project.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable in this environment")
        before = self.snapshot()
        code, payload = self.call_native("inspect", self.project)
        self.assertEqual(code, 2)
        self.assertEqual(payload["status"], "PROJECT_UNRECOVERABLE")
        self.assertEqual(self.snapshot(), before)


if __name__ == "__main__":
    unittest.main()
