"""G2.3 native editor V21.6 stroke save/reload tests, no copyrighted images."""
from hashlib import sha256
import json
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from smartsvg_core.editor_session_g23 import parse_editor_document,EditorSessionError
from smartsvg_core.project_archive import load_project
from smartsvg_core.project_workspace_g22 import ManagedWorkspace,WorkspaceError


def png():
    def chunk(kind,payload):
        return (struct.pack('>I',len(payload))+kind+payload+
                struct.pack('>I',zlib.crc32(kind+payload)&0xffffffff))
    width,height=12,9
    raw=(b'\x00'+bytes([75,93,110,255])*width)*height
    return (b'\x89PNG\r\n\x1a\n'+
            chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,6,0,0,0))+
            chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))


def editor_document(source='a'*64,count=2):
    return json.dumps({
        'version':1,'width':12,'height':9,'count':count,'source':source,
        'strokes':[
            {'object':0,'mode':'add','radius':0.0125,
             'points':[[0.1,0.2],[0.2,0.3],[0.3,0.4]]},
            {'object':count-1,'mode':'erase','radius':0.005,
             'points':[[0.62,0.43],[0.69,0.48]]},
        ]
    })


class G23EditorSessions(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace=ManagedWorkspace(self.temp.name)
        self.workspace.create('snails',png(),profile='Planche - 12 images (4x3)',
                              width_mm=40,dpi=300,notes='Initial')
        self.path=self.workspace.root/'snails.smartsvg'

    def save(self,value=None,expected=None):
        return self.workspace.save_editor_document('snails',
            editor_json=editor_document() if value is None else value,
            expected_sha256=expected or self.workspace.inspect('snails')['sha256'])

    def test_real_save_reopen_identical_strokes_and_history(self):
        before=self.workspace.inspect('snails')
        self.assertNotIn('editor_session',before)
        response=self.save()
        self.assertEqual(response['strokes_saved'],2)
        self.assertFalse(response['base_masks_persisted'])
        view=self.workspace.inspect('snails')
        self.assertEqual(view['editor_session']['stroke_count'],2)
        self.assertEqual(view['editor_session']['source_fingerprint'],'a'*64)
        self.assertFalse(view['editor_session']['base_masks_persisted'])
        original=json.loads(editor_document())
        recovered=json.loads(self.workspace.editor_document('snails')['editor_json'])
        self.assertEqual(recovered,original)
        self.assertEqual(load_project(self.path).operations[-1]['kind'],'save_editor_v216')
        self.assertEqual(self.workspace.source_png('snails'),png())
        self.assertEqual(view['document']['notes'],'Initial')

    def test_session_load_requires_saved_document(self):
        with self.assertRaisesRegex(WorkspaceError,'EDITOR_SESSION_NOT_FOUND'):
            self.workspace.editor_document('snails')

    def test_revision_conflict_preserves_previous_and_source(self):
        old=self.workspace.inspect('snails')['sha256']
        self.save()
        now=self.path.read_bytes()
        with self.assertRaisesRegex(WorkspaceError,'PROJECT_CHANGED'):
            self.save(expected=old)
        self.assertEqual(self.path.read_bytes(),now)

    def test_source_dimensions_mismatch_is_rejected(self):
        doc=json.loads(editor_document())
        for key in ('width','height'):
            invalid={**doc,key:doc[key]+1}
            with self.subTest(key=key),self.assertRaisesRegex(
                WorkspaceError,'INCOMPATIBLE_EDITOR_SOURCE'):
                self.save(value=json.dumps(invalid))
        self.assertNotIn('editor_session',self.workspace.inspect('snails'))

    def test_invalid_source_sha_and_count_are_rejected(self):
        for change in ({'source':'traversal'}, {'count':0}, {'count':33},
                       {'version':2}, {'count':True}):
            value={**json.loads(editor_document()),**change}
            with self.subTest(change=change),self.assertRaisesRegex(
                WorkspaceError,'INCOMPATIBLE_EDITOR_SOURCE'):
                self.save(value=json.dumps(value))

    def test_malformed_nan_duplicate_keys_and_extra_properties(self):
        valid=editor_document()
        for data in ('{', '{"version":1,"version":2}',
                     valid.replace('"radius": 0.0125','"radius": NaN'),
                     valid[:-1]+',"exec":"unsafe"}'):
            with self.subTest(data=data[:30]),self.assertRaises(WorkspaceError):
                self.save(value=data)

    def test_out_of_bounds_strokes_do_not_write_file(self):
        base=json.loads(editor_document())
        old=self.path.read_bytes()
        for bad in ([0.1,1.1],[-0.1,0.2],[None,0.2],[True,0.3]):
            doc=json.loads(editor_document())
            doc['strokes'][0]['points']=[bad]
            with self.subTest(point=bad),self.assertRaisesRegex(WorkspaceError,
                                                                'INVALID_EDITOR_POINT'):
                self.save(value=json.dumps(doc))
        self.assertEqual(self.path.read_bytes(),old)

    def test_object_index_and_mode_restrictions(self):
        for change in ({'object':2},{'object':-1},{'mode':'exec'},
                       {'radius':0.3},{'radius':0}):
            doc=json.loads(editor_document())
            doc['strokes'][0].update(change)
            with self.subTest(change=change),self.assertRaisesRegex(
                WorkspaceError,'INVALID_EDITOR_STROKE'):
                self.save(value=json.dumps(doc))

    def test_stroke_number_and_utf8_limits(self):
        data=json.loads(editor_document())
        data['strokes']=data['strokes']*201
        with self.assertRaisesRegex(WorkspaceError,'INVALID_EDITOR_STROKES'):
            self.save(value=json.dumps(data))
        with self.assertRaisesRegex(WorkspaceError,'INVALID_EDITOR_SIZE'):
            self.save(value=editor_document()+' '*350001)

    def test_save_previous_editor_version_remains_recoverable(self):
        self.save()
        snapshot=self.workspace.inspect('snails')
        next_doc=json.loads(editor_document())
        next_doc['strokes']=next_doc['strokes'][:1]
        self.save(value=json.dumps(next_doc),expected=snapshot['sha256'])
        project=load_project(self.path)
        self.assertEqual(len(project.document['editor_v216']['strokes']),1)
        self.path.write_bytes(b'corrupt')
        backup=self.workspace.inspect('snails')
        self.assertTrue(backup['recoverable'])
        self.workspace.restore('snails',confirmed=True,
                               expected_recovery_sha256=backup['recovery_sha256'])
        self.assertEqual(len(json.loads(self.workspace.editor_document('snails')['editor_json'])['strokes']),2)

    def test_project_does_not_fake_full_mask_or_cut_proof(self):
        self.save()
        stored=load_project(self.path)
        self.assertEqual(stored.masks,())
        self.assertEqual(stored.subjects,())
        self.assertEqual(stored.qa_results,())
        self.assertFalse(stored.document['cricut_certified'])
        self.assertEqual(stored.document['stage'],
                         'editor_strokes_saved_base_masks_external')

    def test_legacy_operations_and_notes_coexist(self):
        old=self.workspace.inspect('snails')['sha256']
        self.workspace.update_notes('snails',notes='Correction',expected_sha256=old)
        self.save()
        project=load_project(self.path)
        self.assertEqual(project.document['notes'],'Correction')
        self.assertEqual([x['kind'] for x in project.operations],
                         ['update_notes','save_editor_v216'])

    def test_editor_load_fails_closed_on_corrupt_archive(self):
        self.save()
        self.path.write_bytes(b'not a zip')
        with self.assertRaisesRegex(WorkspaceError,'INVALID_PROJECT_CONTENTS'):
            self.workspace.editor_document('snails')


if __name__=='__main__':
    unittest.main()
