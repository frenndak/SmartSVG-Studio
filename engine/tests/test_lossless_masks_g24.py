"""G2.4 full-res mask extension with byte-exact float32 archive regression."""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import json
import struct
import tempfile
import unittest
import zlib

from smartsvg_core.project_archive import load_project,save_project,ProjectArchiveError
from smartsvg_core.project_workspace_g22 import ManagedWorkspace,WorkspaceError
from smartsvg_core.mask_snapshot_g24 import (
    SNAPSHOT_PATH,SNAPSHOT_KEY,create_snapshot,decode_snapshot,encode_preview_l8,
    MaskSnapshotError,
)


def chunk(kind,data):
    return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)


def source_png(width=12,height=9):
    row=b'\x00'+bytes([128,80,150,255])*width
    return b'\x89PNG\r\n\x1a\n'+chunk(
        b'IHDR',struct.pack('>IIBBBBB',width,height,8,6,0,0,0))+chunk(
        b'IDAT',zlib.compress(row*height))+chunk(b'IEND',b'')


def mask_bytes(count=2,width=12,height=9):
    vals=[]
    for mask in range(count):
        for y in range(height):
            for x in range(width):
                vals.append((float((x+y+mask)%11)/10.0))
    return struct.pack('<'+'f'*len(vals),*vals)


class G24MaskArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ws=ManagedWorkspace(self.temp.name)
        self.ws.create('snails',source_png(),profile='Planche - 12 images (4x3)')
        self.path=self.ws.root/'snails.smartsvg'
        self.raw=mask_bytes()
        self.img='a'*64
        self.editor='b'*64

    def capture(self,raw=None,sha=None,shape=(2,9,12),image=None,editor=None):
        return self.ws.save_base_masks('snails',
            raw_float32=self.raw if raw is None else raw,shape=shape,
            image_fingerprint=image or self.img,
            editor_fingerprint=editor or self.editor,
            expected_sha256=sha or self.ws.inspect('snails')['sha256'])

    def test_exact_soft_mask_bytes_survive_save_and_reload(self):
        saved=self.capture()
        self.assertTrue(saved['base_masks_exact'])
        self.assertFalse(saved['certified'])
        rec=self.ws.inspect('snails')
        self.assertEqual(rec['base_masks']['count'],2)
        self.assertEqual(rec['base_masks']['dimensions_px'],[12,9])
        out,meta=self.ws.base_masks('snails',expected_sha256=rec['sha256'])
        self.assertEqual(out,self.raw)
        self.assertEqual(meta['editor_fingerprint'],self.editor)
        self.assertEqual(len(load_project(self.path).masks),2)
        self.assertEqual(len(load_project(self.path).resources[SNAPSHOT_PATH])>0,True)

    def test_preview_is_full_resolution_but_l8_only(self):
        self.capture()
        p=load_project(self.path)
        frame=12*9*4
        for i in range(2):
            mask=p.resources[f'masks/base-mask-{i:02d}.png']
            self.assertEqual(mask,encode_preview_l8(self.raw[i*frame:(i+1)*frame],12,9))
            self.assertEqual(mask[16:24],struct.pack('>II',12,9))
        self.assertTrue(p.document[SNAPSHOT_KEY]['base_masks_exact'])

    def test_previous_native_source_and_operations_remain_intact(self):
        self.capture()
        p=load_project(self.path)
        self.assertEqual(p.resources['sources/source-original.png'],source_png())
        self.assertEqual(p.operations[-1]['kind'],'capture_base_masks_float32_v1')
        self.assertEqual(p.qa_results,())
        self.assertEqual(p.document['cricut_certified'],False)

    def test_revisions_capture_second_snapshot_without_mixing(self):
        self.capture()
        old=self.ws.inspect('snails')['sha256']
        # Change one real float32 pixel; the old mask remains in .previous.
        second=struct.pack('<f',.77)+self.raw[4:]
        self.capture(raw=second,sha=old)
        rec=self.ws.inspect('snails')
        self.assertEqual(rec['base_masks']['count'],2)
        self.assertEqual(self.ws.base_masks('snails',expected_sha256=rec['sha256'])[0],second)
        self.assertNotEqual(self.raw,second)
        self.path.write_bytes(b'damaged new mask archive')
        recovery=self.ws.inspect('snails')
        self.assertTrue(recovery['recoverable'])
        self.ws.restore('snails',confirmed=True,
            expected_recovery_sha256=recovery['recovery_sha256'])
        current=self.ws.inspect('snails')
        self.assertEqual(
            self.ws.base_masks('snails',expected_sha256=current['sha256'])[0],
            self.raw)

    def test_corrupted_main_restores_previous_exact_floats(self):
        self.capture()
        self.capture()
        self.path.write_bytes(b'bad zip')
        status=self.ws.inspect('snails')
        self.assertTrue(status['recoverable'])
        self.ws.restore('snails',confirmed=True,
                        expected_recovery_sha256=status['recovery_sha256'])
        sha=self.ws.inspect('snails')['sha256']
        self.assertEqual(self.ws.base_masks('snails',expected_sha256=sha)[0],self.raw)

    def test_old_g22_project_without_snapshot_still_reads(self):
        with self.assertRaisesRegex(WorkspaceError,'BASE_MASK_SNAPSHOT_NOT_FOUND'):
            self.ws.base_masks('snails',expected_sha256=self.ws.inspect('snails')['sha256'])
        self.assertEqual(len(load_project(self.path).masks),0)

    def test_disallow_float32_nan_and_inf(self):
        for invalid in (float('nan'),float('inf'),-1.0,2.0):
            bad=struct.pack('<f',invalid)+self.raw[4:]
            with self.subTest(value=invalid),self.assertRaises(WorkspaceError):
                self.capture(raw=bad)
        self.assertNotIn('base_masks',self.ws.inspect('snails'))

    def test_disallow_oversized_and_wrong_shapes(self):
        for shape in ((33,1,1),(2,0,12),(2,9,14),(1,1,1),(2,1000,5000)):
            with self.subTest(shape=shape),self.assertRaises(WorkspaceError):
                self.capture(shape=shape)

    def test_reject_revision_conflict_no_change(self):
        old=self.ws.inspect('snails')['sha256']
        self.capture()
        new=self.path.read_bytes()
        with self.assertRaisesRegex(WorkspaceError,'PROJECT_CHANGED'):
            self.capture(sha=old)
        self.assertEqual(new,self.path.read_bytes())

    def test_refuse_editor_session_bound_to_different_base_masks(self):
        self.capture()
        old=self.ws.inspect('snails')
        doc=json.dumps({'version':1,'width':12,'height':9,'count':2,
                        'source':'c'*64,'strokes':[]})
        with self.assertRaisesRegex(WorkspaceError,'EDITOR_MASK_SNAPSHOT_MISMATCH'):
            self.ws.save_editor_document('snails',editor_json=doc,
                expected_sha256=old['sha256'])

    def test_saved_editor_strokes_with_matching_fingerprint_stay_usable(self):
        self.capture()
        old=self.ws.inspect('snails')
        doc=json.dumps({'version':1,'width':12,'height':9,'count':2,
                        'source':self.editor,'strokes':[{
                            'object':0,'mode':'add','radius':.02,'points':[[.5,.5]]}]})
        self.ws.save_editor_document('snails',editor_json=doc,
            expected_sha256=old['sha256'])
        read=json.loads(self.ws.editor_document('snails')['editor_json'])
        self.assertEqual(read['source'],self.editor)
        self.assertEqual(len(read['strokes']),1)

    def test_previews_and_float_payload_are_mutually_checked(self):
        self.capture()
        project=load_project(self.path)
        tampered=dict(project.resources)
        tampered['masks/base-mask-00.png']=tampered['masks/base-mask-01.png']
        with self.assertRaisesRegex(ProjectArchiveError,'MASK_SNAPSHOT_INVALID'):
            save_project(self.ws.root/'corrupt.smartsvg',
                replace(project,resources=tampered))
        self.assertFalse((self.ws.root/'corrupt.smartsvg').exists())

    def test_compressed_payload_tampering_fails_closed(self):
        self.capture()
        project=load_project(self.path)
        changed=dict(project.resources)
        changed[SNAPSHOT_PATH]=b'corrupt compressed bytes'
        with self.assertRaisesRegex(ProjectArchiveError,'MASK_SNAPSHOT_INVALID'):
            save_project(self.ws.root/'bad_resource.smartsvg',
                replace(project,resources=changed))

    def test_orphan_supplement_fails_closed(self):
        project=load_project(self.path)
        altered=dict(project.resources)
        altered[SNAPSHOT_PATH]=zlib.compress(self.raw)
        with self.assertRaisesRegex(ProjectArchiveError,'RESOURCE_SET_MISMATCH'):
            save_project(self.ws.root/'orphan.smartsvg',
                replace(project,resources=altered))

    def test_l8_cannot_replace_soft_float32_values(self):
        packed=struct.pack('<f',0.1234567)
        preview=encode_preview_l8(packed,1,1)
        self.assertTrue(preview.startswith(b'\x89PNG'))
        self.assertNotEqual(struct.unpack('<f',packed)[0],round(0.1234567*255)/255)

    def test_snapshot_payload_rejects_zlib_bomb_and_trailing_data(self):
        meta,payload=create_snapshot(self.raw,(2,9,12),
            image_fingerprint=self.img,editor_fingerprint=self.editor)
        for sample in (payload+b'extra',zlib.compress(b'\0'*1_000_000)):
            with self.subTest(n=len(sample)),self.assertRaises(MaskSnapshotError):
                decode_snapshot(meta,sample)


    def test_g33e_identity_catalog_is_lossless_read_only_and_order_specific(self):
        self.capture()
        before=self.path.read_bytes()
        state=self.ws.inspect('snails')
        evidence=state['base_masks']['mask_identity']
        self.assertEqual(evidence['version'],1)
        self.assertEqual(evidence['identity_kind'],'snapshot_position_plus_float32_digest')
        self.assertFalse(evidence['persistent_subject_ids'])
        self.assertEqual(len(evidence['bindings']),2)
        step=12*9*4
        self.assertEqual([row['mask_id'] for row in evidence['bindings']],
                         ['base-mask-00','base-mask-01'])
        self.assertEqual([row['mask_index'] for row in evidence['bindings']],[0,1])
        self.assertEqual([row['mask_sha256_float32'] for row in evidence['bindings']],
                         [sha256(self.raw[i*step:(i+1)*step]).hexdigest() for i in range(2)])
        self.assertTrue(all(row['has_foreground'] for row in evidence['bindings']))
        self.assertTrue(all(row['subject_id'] is None for row in evidence['bindings']))
        self.assertEqual(self.ws.base_masks('snails',expected_sha256=state['sha256'])[0],self.raw)
        self.assertEqual(self.path.read_bytes(),before)
        self.assertNotIn('resources',str(evidence))
        self.assertNotIn(self.raw[:24],str(evidence).encode())

    def test_g33e_duplicate_float32_slices_and_empty_masks_are_exposed_not_claimed_stable(self):
        step=12*9*4
        duplicate=self.raw[:step]*2
        self.capture(raw=duplicate)
        rows=self.ws.inspect('snails')['base_masks']['mask_identity']['bindings']
        self.assertEqual(rows[0]['mask_sha256_float32'],rows[1]['mask_sha256_float32'])
        self.assertIsNone(rows[0]['subject_id'])
        empty=bytes(step)+self.raw[step:]
        current=self.ws.inspect('snails')['sha256']
        self.capture(raw=empty,sha=current)
        rows=self.ws.inspect('snails')['base_masks']['mask_identity']['bindings']
        self.assertFalse(rows[0]['has_foreground'])
        self.assertTrue(rows[1]['has_foreground'])

    def test_g33e_soft_values_below_g26_cutoff_are_not_a_detectable_subject(self):
        # G2.6 thresholds a float32 mask at >= 0.5, not merely > 0.
        step=12*9*4
        soft_only=struct.pack('<'+'f'*(12*9),*([0.1]*(12*9)))+self.raw[step:]
        self.capture(raw=soft_only)
        evidence=self.ws.inspect('snails')['base_masks']['mask_identity']
        self.assertFalse(evidence['bindings'][0]['has_foreground'])
        self.assertTrue(evidence['bindings'][1]['has_foreground'])
        self.assertEqual(self.ws.base_masks('snails',
            expected_sha256=self.ws.inspect('snails')['sha256'])[0],soft_only)

    def test_g33e_mask_permutation_changes_revision_and_content_order(self):
        step=12*9*4
        self.capture()
        first=self.ws.inspect('snails')
        ordered=[row['mask_sha256_float32']
                 for row in first['base_masks']['mask_identity']['bindings']]
        self.capture(raw=self.raw[step:]+self.raw[:step],sha=first['sha256'])
        second=self.ws.inspect('snails')
        reversed_digests=[row['mask_sha256_float32']
                          for row in second['base_masks']['mask_identity']['bindings']]
        self.assertEqual(reversed_digests,list(reversed(ordered)))
        self.assertNotEqual(first['sha256'],second['sha256'])

    def test_g33e_subject_id_only_when_real_subject_record_exists(self):
        from smartsvg_core.project_contracts import Subject
        self.capture()
        original=load_project(self.path)
        id_source=original.sources[0].source_id
        entity=Subject('real-subject-01',id_source,'base-mask-00',(1,1,4,4))
        # save_project is intentionally create-only: construct a separate
        # synthetic .smartsvg fixture instead of overwriting a healthy file.
        target=self.ws.root/'subject_fixture.smartsvg'
        save_project(target,replace(original,project_id='subject_fixture',
                                    subjects=(entity,)))
        state=self.ws.inspect('subject_fixture')['base_masks']['mask_identity']
        self.assertEqual(state['bindings'][0]['subject_id'],'real-subject-01')
        self.assertIsNone(state['bindings'][1]['subject_id'])
        self.assertFalse(state['persistent_subject_ids'])
        self.assertEqual(self.ws.base_masks('subject_fixture',
            expected_sha256=self.ws.inspect('subject_fixture')['sha256'])[0],self.raw)


if __name__=='__main__':
    unittest.main()
