"""G1.4 test corpus: synthetic projects, no user-owned images."""
from dataclasses import replace
import hashlib
import os
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import zlib

from smartsvg_core.project_archive import LoadedProject, ProjectArchiveError, load_project
from smartsvg_core.project_contracts import Mask, SourceAsset, Subject
from smartsvg_core.project_recovery import (
    RecoveryError, _project_lock, inspect_project, recover_previous,
    recovery_message, save_with_recovery,
)


def png(width=8, height=6, grey=False):
    color = 0 if grey else 6
    bpp = 1 if grey else 4
    row = b'\x00' + (b'\x7f' * (width * bpp))
    def chunk(typ, buf):
        return struct.pack('>I', len(buf)) + typ + buf + struct.pack('>I', zlib.crc32(typ + buf) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, color, 0, 0, 0)) +
            chunk(b'IDAT', zlib.compress(row * height)) + chunk(b'IEND', b''))


def fixture(x=3, project_id='project-test'):
    image, mask = png(), png(grey=True)
    sha = lambda data: hashlib.sha256(data).hexdigest()
    return LoadedProject(
        project_id=project_id, app_version='21.15.2',
        sources=(SourceAsset('source-a', sha(image), 8, 6),),
        masks=(Mask('mask-a', 'source-a', sha(mask), 8, 6),),
        subjects=(Subject('subject-a', 'source-a', 'mask-a', (0, 0, 8, 6)),),
        artifacts=(), qa_results=(),
        document={'objects': [{'subject_id': 'subject-a', 'x': x}]},
        operations=[{'op': 'move', 'x': x}, {'op': 'undo'}, {'op': 'redo'}],
        resources={'sources/source-a.png': image, 'masks/mask-a.png': mask},
        source_paths={'source-a': 'sources/source-a.png'},
        mask_paths={'mask-a': 'masks/mask-a.png'},
    )


class ProjectRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'design.smartsvg'
        self.backup = self.path.with_name('design.previous.smartsvg')

    def test_first_save_and_health_status(self):
        result = save_with_recovery(self.path, fixture())
        self.assertFalse(result['previous_available'])
        self.assertFalse(result['physical_cut_verified'])
        self.assertFalse(self.backup.exists())
        report = inspect_project(self.path)
        self.assertEqual((report.status, report.primary, report.previous),
                         ('PROJECT_HEALTHY', 'valid', 'missing'))

    def test_overwrite_preserves_exact_last_snapshot(self):
        save_with_recovery(self.path, fixture(3))
        old = self.path.read_bytes()
        result = save_with_recovery(self.path, fixture(10))
        self.assertTrue(result['previous_available'])
        self.assertEqual(self.backup.read_bytes(), old)
        self.assertEqual(load_project(self.path).document['objects'][0]['x'], 10)
        self.assertEqual(load_project(self.backup).document['objects'][0]['x'], 3)

    def test_three_revisions_preserve_single_last_good_backup(self):
        for x in (1, 2, 3):
            save_with_recovery(self.path, fixture(x))
        self.assertEqual(load_project(self.path).document['objects'][0]['x'], 3)
        self.assertEqual(load_project(self.backup).document['objects'][0]['x'], 2)

    def test_recovery_does_not_start_without_confirmation(self):
        save_with_recovery(self.path, fixture(3))
        save_with_recovery(self.path, fixture(7))
        self.path.write_bytes(b'broken-main')
        assert inspect_project(self.path).status == 'PROJECT_RECOVERABLE'
        with self.assertRaisesRegex(RecoveryError, 'RECOVERY_CONFIRMATION_REQUIRED'):
            recover_previous(self.path)
        self.assertEqual(self.path.read_bytes(), b'broken-main')
        answer = recover_previous(self.path, confirmed=True)
        self.assertEqual(answer['status'], 'restored_from_previous')
        self.assertTrue(answer['previous_retained'])
        self.assertEqual(load_project(self.path).document['objects'][0]['x'], 3)
        self.assertEqual(self.backup.read_bytes(), self.path.read_bytes())

    def test_good_current_is_never_silently_overwritten(self):
        save_with_recovery(self.path, fixture(2))
        save_with_recovery(self.path, fixture(8))
        before = self.path.read_bytes()
        with self.assertRaisesRegex(RecoveryError, 'RECOVERY_WOULD_OVERWRITE_VALID_PROJECT'):
            recover_previous(self.path, confirmed=True)
        self.assertEqual(self.path.read_bytes(), before)

    def test_invalid_main_is_not_replaced_during_regular_save(self):
        save_with_recovery(self.path, fixture(2))
        save_with_recovery(self.path, fixture(3))
        self.path.write_bytes(b'corrupt')
        before_backup = self.backup.read_bytes()
        with self.assertRaisesRegex(RecoveryError, 'NO_VALID_RECOVERY_SNAPSHOT'):
            save_with_recovery(self.path, fixture(4))
        self.assertEqual(self.path.read_bytes(), b'corrupt')
        self.assertEqual(self.backup.read_bytes(), before_backup)

    def test_corrupted_previous_only_reported_not_repaired(self):
        save_with_recovery(self.path, fixture(1))
        save_with_recovery(self.path, fixture(2))
        self.backup.write_bytes(b'invalid-backup')
        self.path.write_bytes(b'invalid-main')
        report = inspect_project(self.path)
        self.assertEqual(report.status, 'PROJECT_UNRECOVERABLE')
        with self.assertRaisesRegex(RecoveryError, 'NO_VALID_RECOVERY_SNAPSHOT'):
            recover_previous(self.path, confirmed=True)

    def test_absent_both_reports_missing(self):
        result = inspect_project(self.path)
        self.assertEqual(result.status, 'PROJECT_MISSING')
        self.assertIsNone(result.project_id)

    def test_missing_main_recoverable_from_previous(self):
        save_with_recovery(self.path, fixture(2))
        save_with_recovery(self.path, fixture(3))
        self.path.unlink()
        self.assertEqual(inspect_project(self.path).status, 'PROJECT_RECOVERABLE')
        recover_previous(self.path, confirmed=True)
        self.assertEqual(load_project(self.path).document['objects'][0]['x'], 2)

    def test_corrupt_existing_backup_is_never_overwritten(self):
        save_with_recovery(self.path, fixture(1))
        save_with_recovery(self.path, fixture(2))
        self.backup.write_bytes(b'possibly-salvageable')
        main_bytes = self.path.read_bytes()
        with self.assertRaisesRegex(RecoveryError, 'BACKUP_CONFLICT'):
            save_with_recovery(self.path, fixture(3))
        self.assertEqual(self.backup.read_bytes(), b'possibly-salvageable')
        self.assertEqual(self.path.read_bytes(), main_bytes)

    def test_foreign_project_backup_is_never_overwritten(self):
        from smartsvg_core.project_archive import save_project
        save_with_recovery(self.path, fixture(1))
        save_project(self.backup, fixture(9, project_id='other-project'))
        backup_bytes = self.backup.read_bytes()
        with self.assertRaisesRegex(RecoveryError, 'BACKUP_CONFLICT'):
            save_with_recovery(self.path, fixture(2))
        self.assertEqual(self.backup.read_bytes(), backup_bytes)
        self.assertEqual(load_project(self.path).document['objects'][0]['x'], 1)

    def test_failed_publish_keeps_good_main_and_snapshot(self):
        save_with_recovery(self.path, fixture(2))
        old = self.path.read_bytes()
        with patch('smartsvg_core.project_recovery.save_project',
                   side_effect=ProjectArchiveError('simulated-disk-failure')):
            with self.assertRaisesRegex(RecoveryError, 'SAVE_FAILED'):
                save_with_recovery(self.path, fixture(3))
        self.assertEqual(self.path.read_bytes(), old)
        self.assertEqual(self.backup.read_bytes(), old)
        self.assertEqual(inspect_project(self.path).status, 'PROJECT_HEALTHY')
        save_with_recovery(self.path, fixture(4))
        self.assertEqual(load_project(self.path).document['objects'][0]['x'], 4)

    def test_failed_backup_copy_preserves_last_good_previous(self):
        save_with_recovery(self.path, fixture(1))
        save_with_recovery(self.path, fixture(2))
        old_current = self.path.read_bytes()
        old_backup = self.backup.read_bytes()
        with patch('smartsvg_core.project_recovery.shutil.copyfileobj', side_effect=OSError('disk full')):
            with self.assertRaisesRegex(RecoveryError, 'SAVE_FAILED'):
                save_with_recovery(self.path, fixture(3))
        self.assertEqual(self.path.read_bytes(), old_current)
        self.assertEqual(self.backup.read_bytes(), old_backup)
        self.assertEqual(list(self.path.parent.glob('.smartsvg-recover-*')), [])

    def test_os_file_lock_rejects_simultaneous_write(self):
        with _project_lock(self.path):
            with self.assertRaisesRegex(RecoveryError, 'PROJECT_LOCKED'):
                save_with_recovery(self.path, fixture())
        save_with_recovery(self.path, fixture())
        self.assertEqual(inspect_project(self.path).status, 'PROJECT_HEALTHY')

    def test_wrong_project_identity_blocks_replacing_current(self):
        save_with_recovery(self.path, fixture(project_id='p-alpha'))
        old = self.path.read_bytes()
        with self.assertRaisesRegex(RecoveryError, 'PROJECT_CHANGED_DURING_SAVE'):
            save_with_recovery(self.path, fixture(project_id='p-beta'))
        self.assertEqual(self.path.read_bytes(), old)

    def test_bad_path_rejected(self):
        with self.assertRaisesRegex(RecoveryError, 'INVALID_RECOVERY_PATH'):
            inspect_project(self.path.with_suffix('.txt'))

    def test_user_message_is_french_and_actionable(self):
        message = recovery_message('PROJECT_RECOVERABLE')
        self.assertIn('sauvegarde précédente', message['message_fr'])
        self.assertIn('confirmer', message['action_fr'])
        self.assertFalse(inspect_project(self.path).physical_cut_verified)

    def test_unknown_error_code_has_safe_fallback(self):
        self.assertEqual(recovery_message('surprise')['code'], 'SAVE_FAILED')

    def test_backup_is_not_executable_or_reclassified_as_cut(self):
        save_with_recovery(self.path, fixture(1))
        save_with_recovery(self.path, fixture(2))
        info = inspect_project(self.path)
        self.assertFalse(info.automatic_restore)
        self.assertFalse(info.physical_cut_verified)
        self.assertEqual(info.project_id, 'project-test')


if __name__ == '__main__':
    unittest.main()
