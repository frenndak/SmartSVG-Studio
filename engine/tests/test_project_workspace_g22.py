"""G2.2 real managed-project integration against synthetic PNG data."""
from dataclasses import replace
from hashlib import sha256
import struct
import zlib
import shutil
from pathlib import Path
import tempfile
import unittest

from smartsvg_core.project_archive import load_project, save_project
from smartsvg_core.project_workspace_g22 import ManagedWorkspace, WorkspaceError
from smartsvg_core.project_recovery import save_with_recovery


def png(w=12,h=9,mode='RGBA'):
    color, bpp = {'RGBA':(6,4), 'RGB':(2,3), 'L':(0,1)}[mode]
    row = b'\x00' + bytes([95])* (w*bpp)
    def chunk(tag, payload):
        return (struct.pack('>I', len(payload)) + tag + payload +
                struct.pack('>I', zlib.crc32(tag+payload)&0xffffffff))
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR', struct.pack('>IIBBBBB', w,h,8,color,0,0,0)) +
            chunk(b'IDAT', zlib.compress(row*h)) +
            chunk(b'IEND',b''))


class G22ManagedWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace=ManagedWorkspace(self.temp.name)
        self.png=png()

    def create(self,name='snails',source=None,notes='première version'):
        return self.workspace.create(name,self.png if source is None else source,
            profile='Planche - 12 images (4x3)',width_mm=40,dpi=300,notes=notes)

    def test_create_and_open_real_roundtrip(self):
        result=self.create()
        self.assertEqual(result['source_dimensions_px'],[12,9])
        self.assertFalse(result['certified'])
        saved=self.workspace.inspect('snails')
        self.assertEqual(saved['status'],'PROJECT_HEALTHY')
        self.assertEqual(saved['document']['profile'],'Planche - 12 images (4x3)')
        self.assertEqual(saved['document']['stage'],'source_imported_only')
        self.assertEqual(self.workspace.source_png('snails'),self.png)
        self.assertEqual(self.workspace.list_projects()[0]['name'],'snails')

    def test_notes_revision_preserves_source_and_backup(self):
        self.create()
        state=self.workspace.inspect('snails')
        result=self.workspace.update_notes('snails',notes='corriger les antennes',
            expected_sha256=state['sha256'])
        self.assertEqual(result['status'],'updated')
        now=self.workspace.inspect('snails')
        self.assertEqual(now['document']['notes'],'corriger les antennes')
        self.assertEqual(now['operations_count'],1)
        self.assertEqual(now['previous'],'valid')
        self.assertEqual(self.workspace.source_png('snails'),self.png)

    def test_no_silent_overwrite(self):
        self.create()
        old=self.workspace.inspect('snails')['sha256']
        with self.assertRaisesRegex(WorkspaceError,'PROJECT_ALREADY_EXISTS'):
            self.create()
        self.assertEqual(self.workspace.inspect('snails')['sha256'],old)

    def test_traversal_absolute_and_special_names_rejected(self):
        for name in ('../escape','x/y','C:\\evil','x.previous','', 'project_previous',
                     'a'*49,'éléphant'):
            with self.subTest(name=name),self.assertRaisesRegex(WorkspaceError,'INVALID_PROJECT_NAME'):
                self.create(name)

    def test_png_required_corrupt_truncated_and_wrong_type_refused(self):
        for source in (b'not png'*9,self.png[:50],b'A'*120):
            with self.subTest(length=len(source)),self.assertRaises(WorkspaceError):
                self.create('bad',source=source)
            self.assertFalse((self.workspace.root/'bad.smartsvg').exists())
        with self.assertRaisesRegex(WorkspaceError,'INVALID_IMAGE_MODE|INVALID_PNG'):
            self.create('jpeg',source=b'\xff\xd8'+b'x'*90)

    def test_corrupted_png_chunk_crc_rejected(self):
        source=bytearray(self.png)
        source[-5] ^= 0x10
        with self.assertRaisesRegex(WorkspaceError, 'PNG_CRC_FAILED'):
            self.create('badcrc',source=bytes(source))
        self.assertFalse((self.workspace.root/'badcrc.smartsvg').exists())

    def test_png_invalid_row_filter_rejected_with_fresh_crc(self):
        def chunk(kind, payload):
            return (struct.pack('>I',len(payload))+kind+payload+
                    struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff))
        source=(self.png[:33]+
                chunk(b'IDAT',zlib.compress((b'\x09'+b'\x7f'*48)*9))+
                chunk(b'IEND',b''))
        with self.assertRaisesRegex(WorkspaceError,'INVALID_PNG_FILTER'):
            self.create('badfilter',source=source)

    def test_png_overinflation_rejected_even_with_valid_crc(self):
        def chunk(kind,payload):
            return (struct.pack('>I',len(payload))+kind+payload+
                    struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff))
        source=(self.png[:33]+chunk(b'IDAT',zlib.compress(b'\x00'*10000))+
                chunk(b'IEND',b''))
        with self.assertRaisesRegex(WorkspaceError,'INVALID_PNG_PIXELS'):
            self.create('zipbomb',source=source)

    def test_image_size_and_profile_limits(self):
        with self.assertRaisesRegex(WorkspaceError,'INVALID_PROFILE'):
            self.workspace.create('bad',self.png,profile='print cut now')
        for value in (-1,0,float('nan'),500):
            with self.subTest(value=value),self.assertRaisesRegex(WorkspaceError,'INVALID_WIDTH'):
                self.workspace.create('bad',self.png,profile='Sticker - contour du sujet',
                                      width_mm=value)
        with self.assertRaisesRegex(WorkspaceError,'INVALID_DPI'):
            self.workspace.create('bad',self.png,profile='Sticker - contour du sujet',dpi=301)

    def test_unicode_notes_and_empty_notes(self):
        self.create(notes='Projet de Noël 🎄')
        first=self.workspace.inspect('snails')
        self.assertEqual(first['document']['notes'],'Projet de Noël 🎄')
        self.workspace.update_notes('snails',notes='',expected_sha256=first['sha256'])
        self.assertEqual(self.workspace.inspect('snails')['document']['notes'],'')

    def test_oversize_notes_rejected_without_overwriting(self):
        self.create()
        old=self.workspace.inspect('snails')['sha256']
        with self.assertRaisesRegex(WorkspaceError,'INVALID_NOTES'):
            self.workspace.update_notes('snails',notes='!'*1600,expected_sha256=old)
        self.assertEqual(self.workspace.inspect('snails')['sha256'],old)

    def test_optimistic_revision_refusal(self):
        self.create()
        with self.assertRaisesRegex(WorkspaceError,'PROJECT_CHANGED'):
            self.workspace.update_notes('snails',notes='stale',expected_sha256='0'*64)
        self.assertEqual(self.workspace.inspect('snails')['document']['notes'],'première version')

    def test_real_recovery_with_fingerprint_and_confirmation(self):
        self.create()
        snap=self.workspace.inspect('snails')
        self.workspace.update_notes('snails',notes='version2',expected_sha256=snap['sha256'])
        location=self.workspace.root/'snails.smartsvg'
        location.write_bytes(b'bad-new-version')
        state=self.workspace.inspect('snails')
        self.assertTrue(state['recoverable'])
        self.assertIn(self.workspace.inspect('snails')['name'],
                      [r['name'] for r in self.workspace.list_projects()])
        with self.assertRaisesRegex(WorkspaceError,'RESTORE_CONFIRMATION_REQUIRED'):
            self.workspace.restore('snails',
                expected_recovery_sha256=state['recovery_sha256'])
        with self.assertRaisesRegex(WorkspaceError,'RECOVERY_SNAPSHOT_CHANGED'):
            self.workspace.restore('snails',confirmed=True,expected_recovery_sha256='0'*64)
        result=self.workspace.restore('snails',confirmed=True,
                                      expected_recovery_sha256=state['recovery_sha256'])
        self.assertEqual(result['status'],'restored_from_previous')
        self.assertEqual(self.workspace.inspect('snails')['document']['notes'],'première version')

    def test_orphan_backup_still_listed_and_restorable(self):
        self.create()
        old=self.workspace.inspect('snails')
        self.workspace.update_notes('snails',notes='next',expected_sha256=old['sha256'])
        (self.workspace.root/'snails.smartsvg').unlink()
        listed=self.workspace.list_projects()
        self.assertEqual(listed[0]['status'],'PROJECT_RECOVERABLE')
        self.workspace.restore('snails',confirmed=True,
                               expected_recovery_sha256=listed[0]['recovery_sha256'])
        self.assertEqual(self.workspace.inspect('snails')['status'],'PROJECT_HEALTHY')

    def test_do_not_restore_over_valid_file(self):
        self.create()
        first=self.workspace.inspect('snails')
        self.workspace.update_notes('snails',notes='new',expected_sha256=first['sha256'])
        with self.assertRaisesRegex(WorkspaceError,'NOT_RECOVERABLE'):
            self.workspace.restore('snails',confirmed=True,
                expected_recovery_sha256='0'*64)

    def test_symlink_project_file_is_rejected(self):
        external=Path(self.temp.name)/'outside.smartsvg'
        external.write_bytes(b'private bytes')
        (self.workspace.root/'snails.smartsvg').symlink_to(external)
        with self.assertRaisesRegex(WorkspaceError,'UNSAFE_PROJECT_PATH'):
            self.workspace.inspect('snails')
        self.assertEqual(external.read_bytes(),b'private bytes')

    def test_pending_transaction_after_publish_requires_explicit_sha_pinned_resolution(self):
        self.create()
        first=self.workspace.inspect('snails')
        self.workspace.update_notes('snails',notes='version2',expected_sha256=first['sha256'])
        path=self.workspace.root/'snails.smartsvg'
        previous=self.workspace.root/'snails.previous.smartsvg'
        pending=self.workspace.root/'snails.pending-backup.smartsvg'
        old_backup=previous.read_bytes()
        shutil.copyfile(path,pending)
        current=load_project(path)
        save_project(path,replace(current,document={**current.document,'notes':'version3'}),
                     overwrite=True)
        state=self.workspace.inspect('snails')
        self.assertEqual(state['status'],'PENDING_BACKUP_REVIEW_REQUIRED')
        self.assertTrue(state['pending_resolution_available'])
        self.assertNotIn('sha256',state)
        self.assertEqual(previous.read_bytes(),old_backup)
        args={'expected_pending_sha256':state['pending_sha256'],
              'expected_primary_sha256':state['primary_sha256'],
              'expected_previous_sha256':state['previous_sha256']}
        with self.assertRaisesRegex(WorkspaceError,'RECOVERY_CONFIRMATION_REQUIRED'):
            self.workspace.resolve_pending('snails',**args)
        with self.assertRaisesRegex(WorkspaceError,'RECOVERY_SNAPSHOT_CHANGED'):
            self.workspace.resolve_pending('snails',confirmed=True,
                **{**args,'expected_previous_sha256':'0'*64})
        self.assertEqual(previous.read_bytes(),old_backup)
        self.assertTrue(pending.exists())
        result=self.workspace.resolve_pending('snails',confirmed=True,**args)
        self.assertEqual(result['status'],'pending_backup_finalized')
        self.assertFalse(pending.exists())
        self.assertEqual(load_project(path).document['notes'],'version3')
        self.assertEqual(load_project(previous).document['notes'],'version2')

    def test_pending_before_publish_and_foreign_snapshot_fail_closed(self):
        self.create()
        first=self.workspace.inspect('snails')
        self.workspace.update_notes('snails',notes='version2',expected_sha256=first['sha256'])
        path=self.workspace.root/'snails.smartsvg'
        previous=self.workspace.root/'snails.previous.smartsvg'
        pending=self.workspace.root/'snails.pending-backup.smartsvg'
        old_backup=previous.read_bytes()
        shutil.copyfile(path,pending)
        state=self.workspace.inspect('snails')
        args={'expected_pending_sha256':state['pending_sha256'],
              'expected_primary_sha256':state['primary_sha256'],
              'expected_previous_sha256':state['previous_sha256']}
        self.assertTrue(state['pending_resolution_available'])
        self.assertEqual(self.workspace.resolve_pending('snails',confirmed=True,**args)['status'],
                         'unpublished_candidate_discarded')
        self.assertEqual(previous.read_bytes(),old_backup)
        self.assertFalse(pending.exists())
        self.create('foreign')
        shutil.copyfile(self.workspace.root/'foreign.smartsvg',pending)
        state=self.workspace.inspect('snails')
        self.assertFalse(state['pending_resolution_available'])
        with self.assertRaisesRegex(WorkspaceError,'NO_VALID_RECOVERY_SNAPSHOT'):
            self.workspace.resolve_pending('snails',confirmed=True,**args)
        self.assertTrue(pending.exists())
        self.assertEqual(previous.read_bytes(),old_backup)

    def test_project_holds_no_fabrication_evidence(self):
        self.create()
        original=load_project(self.workspace.root/'snails.smartsvg')
        self.assertEqual(original.artifacts,())
        self.assertEqual(original.qa_results,())
        self.assertEqual(original.masks,())
        self.assertEqual(original.subjects,())
        self.assertEqual(original.document['cricut_certified'],False)

    def test_project_names_do_not_leak_absolute_host_paths(self):
        self.create()
        summary=self.workspace.inspect('snails')
        self.assertNotIn(str(self.workspace.root),repr(summary))
        self.assertNotIn(str(self.workspace.root),repr(self.workspace.list_projects()))


if __name__=='__main__':
    unittest.main()
