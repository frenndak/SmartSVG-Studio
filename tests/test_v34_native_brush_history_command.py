"""Native history mutations: real V1 round trips and failure boundaries."""
from __future__ import annotations

from hashlib import sha256
import importlib
import importlib.util
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[1] / 'engine'
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

import test_v34_native_subject_preview as fixtures
from smartsvg_core.native_subject_preview_v34 import NativeSubjectPreviewError, preview_native_subject_stroke
from smartsvg_core.native_subject_save_v34 import save_native_subject_stroke
from smartsvg_core.project_archive import load_project
from smartsvg_core.project_workspace_g22 import ManagedWorkspace
from smartsvg_core import project_recovery

HAS_CPU = bool(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'))


class NativeHistoryCommandTests(unittest.TestCase):
    def setUp(self):
        fixtures.NativeSubjectPreviewTests.setUp(self)

    def files(self):
        return fixtures.NativeSubjectPreviewTests.bytes_before(self)

    def change(self, **changes):
        module = 'smartsvg_core.native_brush_history_command_v34'
        self.assertIsNotNone(importlib.util.find_spec(module), 'Native history command is not implemented')
        command = importlib.import_module(module).change_native_brush_history
        request = dict(project_path=str(self.path), expected_sha256=self.sha,
                       subject_id=self.subject_id, action='undo',
                       command_id='native-undo-001', confirmed=True)
        request.update(changes)
        return command(**request)

    def seed_stroke(self, *, command_id='native-seed-001', **changes):
        request = fixtures.NativeSubjectPreviewTests.command(self, **changes)
        preview = preview_native_subject_stroke(**request)
        saved = save_native_subject_stroke(
            **request, expected_preview_mask_sha256_float32=preview['preview_mask_sha256_float32'],
            command_id=command_id, confirmed=True)
        self.sha = saved['project_sha256']
        return load_project(self.path)

    def test_confirmation_is_literal_and_refusal_never_changes_files(self):
        before = self.files()
        for confirmed in (False, None, 1, 0, 'yes', [], {}):
            with self.subTest(confirmed=confirmed):
                with self.assertRaises(NativeSubjectPreviewError) as error:
                    self.change(confirmed=confirmed)
                self.assertEqual(error.exception.code, 'BRUSH_HISTORY_CONFIRMATION_REQUIRED')
                self.assertEqual(self.files(), before)

    def test_invalid_requests_and_unmanaged_paths_never_write(self):
        before = self.files()
        for changes, code in (
            ({'expected_sha256': 'bad'}, 'EXPECTED_REVISION_REQUIRED'),
            ({'subject_id': 'mask-index-0'}, 'INVALID_SUBJECT_ID'),
            ({'action': 'delete'}, 'INVALID_BRUSH_HISTORY_REQUEST'),
            ({'action': True}, 'INVALID_BRUSH_HISTORY_REQUEST'),
            ({'command_id': '../escape'}, 'INVALID_BRUSH_HISTORY_REQUEST'),
            ({'command_id': 'a' * 129}, 'INVALID_BRUSH_HISTORY_REQUEST'),
            ({'project_path': 'relative.smartsvg'}, 'UNMANAGED_PROJECT'),
        ):
            with self.subTest(changes=changes):
                with self.assertRaises(NativeSubjectPreviewError) as error:
                    self.change(**changes)
                self.assertEqual(error.exception.code, code)
                self.assertEqual(self.files(), before)

    def test_empty_history_and_stale_revision_never_write(self):
        before = self.files()
        for changes, code in (({}, 'BRUSH_NOTHING_TO_UNDO'),
                              ({'expected_sha256': 'f' * 64}, 'PROJECT_CHANGED')):
            with self.subTest(changes=changes):
                with self.assertRaises(NativeSubjectPreviewError) as error:
                    self.change(**changes)
                self.assertEqual(error.exception.code, code)
                self.assertEqual(self.files(), before)

    def test_malformed_availability_cannot_enable_a_mutation(self):
        before = self.files()
        valid = dict(name=self.name, project_sha256=self.sha, cricut_certified=False,
                     undo_available=True, undo_subject_id=self.subject_id)
        for changes in ({'name': 'another-project'}, {'project_sha256': 'f' * 64},
                        {'cricut_certified': True}, {'cricut_certified': 0},
                        {'undo_available': 1}, {'undo_available': None},
                        {'undo_available': False, 'undo_error_code': '/private/path'}):
            with self.subTest(changes=changes):
                with patch.object(ManagedWorkspace, 'subject_brush_history',
                                  return_value={**valid, **changes}):
                    with self.assertRaises(NativeSubjectPreviewError) as error:
                        self.change()
                self.assertEqual(error.exception.code, 'INVALID_BRUSH_HISTORY_STATUS')
                self.assertEqual(self.files(), before)

    @unittest.skipUnless(HAS_CPU, 'Real brush round trip requires NumPy/Pillow')
    def test_real_undo_redo_reopen_preserves_resources_notes_and_exports(self):
        original = load_project(self.path)
        saved = self.seed_stroke()
        self.workspace.update_notes(self.name, notes='À conserver', expected_sha256=self.sha)
        self.sha = sha256(self.path.read_bytes()).hexdigest()
        export = self.path.parent / 'already-exported.svg'
        export.write_bytes(b'<svg/>')
        before_undo = self.path.read_bytes()
        undone = self.change()
        self.assertEqual(undone, {
            'status': 'brush_history_undo', 'project_sha256': sha256(self.path.read_bytes()).hexdigest(),
            'subject_id': self.subject_id, 'action': 'undo', 'command_id': 'native-undo-001',
            'persisted': True, 'cricut_certified': False,
        })
        reopened = load_project(self.path)
        self.assertNotIn('editor_v216', reopened.document)
        self.assertEqual(reopened.document['notes'], 'À conserver')
        self.assertEqual(self.path.with_name(self.name + '.previous.smartsvg').read_bytes(), before_undo)
        self.sha = undone['project_sha256']
        # The bridge reopens its workspace from the path on each invocation.
        redone = self.change(action='redo', command_id='native-redo-001')
        self.assertEqual(redone['status'], 'brush_history_redo')
        reopened = load_project(self.path)
        self.assertEqual(reopened.document['editor_v216'], saved.document['editor_v216'])
        self.assertEqual(reopened.resources, original.resources)
        self.assertEqual(reopened.masks, original.masks)
        self.assertEqual(reopened.subjects, original.subjects)
        self.assertEqual(reopened.document['notes'], 'À conserver')
        self.assertEqual(export.read_bytes(), b'<svg/>')

    @unittest.skipUnless(HAS_CPU, 'Real brush round trip requires NumPy/Pillow')
    def test_different_subject_is_not_silently_undone(self):
        self.seed_stroke()
        before = self.files()
        with self.assertRaises(NativeSubjectPreviewError) as error:
            self.change(subject_id='subject-' + '0' * 32)
        self.assertEqual(error.exception.code, 'BRUSH_HISTORY_SUBJECT_CHANGED')
        self.assertEqual(self.files(), before)

    @unittest.skipUnless(HAS_CPU, 'Real brush round trip requires NumPy/Pillow')
    def test_stale_retry_cannot_apply_a_second_mutation(self):
        self.seed_stroke()
        self.change()
        before = self.files()
        with self.assertRaises(NativeSubjectPreviewError) as error:
            self.change()
        self.assertEqual(error.exception.code, 'PROJECT_CHANGED')
        self.assertEqual(self.files(), before)

    @unittest.skipUnless(HAS_CPU, 'Real brush round trip requires NumPy/Pillow')
    def test_pending_recovery_and_disk_full_preserve_previous_files(self):
        self.seed_stroke()
        before = self.files()
        with patch.object(project_recovery, 'save_project', side_effect=OSError('private/disk-full')):
            with self.assertRaises(NativeSubjectPreviewError) as error:
                self.change()
        self.assertEqual(error.exception.code, 'SAVE_FAILED')
        self.assertEqual(self.files(), before)
        pending = self.path.with_name(self.name + '.pending-backup.smartsvg')
        pending.write_bytes(self.path.read_bytes())
        before = self.files()
        with self.assertRaises(NativeSubjectPreviewError) as error:
            self.change()
        self.assertEqual(error.exception.code, 'PROJECT_NOT_HEALTHY')
        self.assertEqual(self.files(), before)

    @unittest.skipUnless(HAS_CPU, 'Real brush round trip requires NumPy/Pillow')
    def test_invalid_receipt_after_commit_is_unknown_without_automatic_retry(self):
        self.seed_stroke()
        before = self.path.read_bytes()
        writer = ManagedWorkspace.change_subject_brush_history

        def committed(workspace, *args, **kwargs):
            result = writer(workspace, *args, **kwargs)
            return {**result, 'action': 'redo'}

        with patch.object(ManagedWorkspace, 'change_subject_brush_history', committed):
            with self.assertRaises(NativeSubjectPreviewError) as error:
                self.change()
        self.assertEqual(error.exception.code, 'BRUSH_HISTORY_OUTCOME_UNKNOWN')
        self.assertNotEqual(self.path.read_bytes(), before)
        self.assertNotIn('editor_v216', load_project(self.path).document)
        self.assertEqual(self.path.with_name(self.name + '.previous.smartsvg').read_bytes(), before)

    @unittest.skipUnless(HAS_CPU, 'Real brush round trip requires NumPy/Pillow')
    def test_exception_after_real_commit_does_not_claim_no_change(self):
        self.seed_stroke()
        before = self.path.read_bytes()
        writer = ManagedWorkspace.change_subject_brush_history

        def committed(workspace, *args, **kwargs):
            writer(workspace, *args, **kwargs)
            raise OSError('private/path')

        with patch.object(ManagedWorkspace, 'change_subject_brush_history', committed):
            with self.assertRaises(NativeSubjectPreviewError) as error:
                self.change()
        self.assertEqual(error.exception.code, 'BRUSH_HISTORY_OUTCOME_UNKNOWN')
        self.assertNotIn('private', str(error.exception))
        self.assertNotEqual(self.path.read_bytes(), before)

    @unittest.skipUnless(HAS_CPU, 'Real brush round trip requires NumPy/Pillow')
    def test_further_commit_before_readback_prevents_false_success(self):
        self.seed_stroke()
        writer = ManagedWorkspace.change_subject_brush_history

        def competing(workspace, *args, **kwargs):
            receipt = writer(workspace, *args, **kwargs)
            workspace.update_notes(self.name, notes='Other session', expected_sha256=receipt['sha256'])
            return receipt

        with patch.object(ManagedWorkspace, 'change_subject_brush_history', competing):
            with self.assertRaises(NativeSubjectPreviewError) as error:
                self.change()
        self.assertEqual(error.exception.code, 'BRUSH_HISTORY_OUTCOME_UNKNOWN')
        self.assertEqual(load_project(self.path).document['notes'], 'Other session')

    @unittest.skipUnless(HAS_CPU, 'Real brush round trip requires NumPy/Pillow')
    def test_each_receipt_field_is_checked_after_real_commit(self):
        writer = ManagedWorkspace.change_subject_brush_history
        for i, changes in enumerate((
            {'name': 'different-project'}, {'command_id': 'other-command'},
            {'status': 'brush_history_redo'}, {'persisted': 1},
            {'persisted': False}, {'cricut_certified': True}, {'cricut_certified': 0},
            {'sha256': 'bad'}, {'sha256': None},
        )):
            with self.subTest(changes=changes):
                self.seed_stroke(command_id=f'native-seed-{i}')

                def forged(workspace, *args, **kwargs):
                    return {**writer(workspace, *args, **kwargs), **changes}

                with patch.object(ManagedWorkspace, 'change_subject_brush_history', forged):
                    with self.assertRaises(NativeSubjectPreviewError) as error:
                        self.change(command_id=f'native-undo-{i}')
                self.assertEqual(error.exception.code, 'BRUSH_HISTORY_OUTCOME_UNKNOWN')
                self.assertNotIn('editor_v216', load_project(self.path).document)
                self.sha = sha256(self.path.read_bytes()).hexdigest()

    @unittest.skipUnless(HAS_CPU, 'Real brush round trip requires NumPy/Pillow')
    def test_new_edit_after_undo_refuses_redo_without_losing_audit(self):
        self.seed_stroke()
        self.sha = self.change()['project_sha256']
        self.seed_stroke(command_id='new-branch', points=[[0.8, 0.8]])
        before = self.files()
        operations = len(load_project(self.path).operations)
        with self.assertRaises(NativeSubjectPreviewError) as error:
            self.change(action='redo', command_id='native-invalid-redo')
        self.assertEqual(error.exception.code, 'BRUSH_NOTHING_TO_REDO')
        self.assertEqual(self.files(), before)
        self.assertEqual(len(load_project(self.path).operations), operations)

    @unittest.skipUnless(HAS_CPU, 'Real brush round trip requires NumPy/Pillow')
    def test_backup_rotation_failure_can_leave_committed_primary_and_pending_recovery(self):
        self.seed_stroke()
        before = self.files()
        copy = project_recovery._atomic_copy

        def interrupted(source, destination, **kwargs):
            if str(destination).endswith('.previous.smartsvg'):
                raise project_recovery.RecoveryError('SAVE_FAILED')
            return copy(source, destination, **kwargs)

        with patch.object(project_recovery, '_atomic_copy', interrupted):
            with self.assertRaises(NativeSubjectPreviewError) as error:
                self.change()
        # SAVE_FAILED is a recovery code, NOT a promise that nothing changed.
        self.assertEqual(error.exception.code, 'SAVE_FAILED')
        self.assertNotIn('editor_v216', load_project(self.path).document)
        pending = self.path.with_name(self.name + '.pending-backup.smartsvg')
        previous = self.path.with_name(self.name + '.previous.smartsvg')
        self.assertEqual(pending.read_bytes(), before[self.path.name])
        self.assertEqual(previous.read_bytes(), before[previous.name])
        after = self.files()
        with self.assertRaises(NativeSubjectPreviewError) as retry:
            self.change()
        self.assertEqual(retry.exception.code, 'PROJECT_CHANGED')
        self.assertEqual(self.files(), after)

    @unittest.skipUnless(HAS_CPU, 'Real brush round trip requires NumPy/Pillow')
    def test_notes_saved_between_availability_and_writer_are_not_overwritten(self):
        saved = self.seed_stroke()
        writer = ManagedWorkspace.change_subject_brush_history

        def competing(workspace, *args, **kwargs):
            workspace.update_notes(self.name, notes='Concurrent notes', expected_sha256=self.sha)
            return writer(workspace, *args, **kwargs)

        with patch.object(ManagedWorkspace, 'change_subject_brush_history', competing):
            with self.assertRaises(NativeSubjectPreviewError) as error:
                self.change()
        self.assertEqual(error.exception.code, 'PROJECT_CHANGED')
        reopened = load_project(self.path)
        self.assertEqual(reopened.document['notes'], 'Concurrent notes')
        self.assertEqual(reopened.document['editor_v216'], saved.document['editor_v216'])


if __name__ == '__main__':
    unittest.main()
