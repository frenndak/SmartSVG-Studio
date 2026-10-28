"""G0 regression gate for transactional .smartsvg backups (synthetic only)."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'engine'))
sys.path.insert(0, str(ROOT / 'engine' / 'tests'))
from test_project_recovery_g14 import fixture  # synthetic 8x6 PNG, no user assets
from smartsvg_core.project_archive import ProjectArchiveError, load_project
from smartsvg_core.project_recovery import (
    RecoveryError, _pending, inspect_project, resolve_pending_backup, save_with_recovery,
)


class TransactionalRecoveryGate(unittest.TestCase):
    def test_failed_third_revision_preserves_original_previous(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'demo.smartsvg'
            backup = path.with_name('demo.previous.smartsvg')
            save_with_recovery(path, fixture(1))
            save_with_recovery(path, fixture(2))
            original_primary, original_backup = path.read_bytes(), backup.read_bytes()
            with patch('smartsvg_core.project_recovery.save_project',
                       side_effect=ProjectArchiveError('simulated-disk-failure')):
                with self.assertRaisesRegex(RecoveryError, 'SAVE_FAILED'):
                    save_with_recovery(path, fixture(3))
            self.assertEqual(path.read_bytes(), original_primary)
            self.assertEqual(backup.read_bytes(), original_backup)
            self.assertEqual(load_project(backup).document['objects'][0]['x'], 1)
            self.assertFalse(_pending(path).exists())

    def test_interrupted_commit_requires_explicit_resolution(self):
        from smartsvg_core import project_recovery
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'demo.smartsvg'
            backup = path.with_name('demo.previous.smartsvg')
            save_with_recovery(path, fixture(1))
            save_with_recovery(path, fixture(2))
            old_primary, old_backup = path.read_bytes(), backup.read_bytes()
            original_copy = project_recovery._atomic_copy
            count = [0]
            def interrupted_copy(source, destination):
                count[0] += 1
                if count[0] == 2:
                    raise KeyboardInterrupt('simulated-stop')
                return original_copy(source, destination)
            with patch('smartsvg_core.project_recovery._atomic_copy', side_effect=interrupted_copy):
                with self.assertRaises(KeyboardInterrupt):
                    save_with_recovery(path, fixture(3))
            self.assertEqual(backup.read_bytes(), old_backup)
            self.assertEqual(_pending(path).read_bytes(), old_primary)
            self.assertEqual(inspect_project(path).status, 'PENDING_BACKUP_REVIEW_REQUIRED')
            with self.assertRaisesRegex(RecoveryError, 'RECOVERY_CONFIRMATION_REQUIRED'):
                resolve_pending_backup(path)
            result = resolve_pending_backup(path, confirmed=True)
            self.assertEqual(result['status'], 'pending_backup_finalized')
            self.assertEqual(backup.read_bytes(), old_primary)
            self.assertFalse(_pending(path).exists())


if __name__ == '__main__':
    unittest.main()
