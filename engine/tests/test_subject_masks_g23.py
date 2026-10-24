"""G2.3 mask persistence, multi-subject restore, malicious PNG guard tests."""
from hashlib import sha256
from pathlib import Path
import struct
import tempfile
import unittest
import zlib

from smartsvg_core.mask_inspection_g23 import inspect_l8_mask
from smartsvg_core.project_archive import load_project
from smartsvg_core.project_workspace_g22 import ManagedWorkspace, WorkspaceError


def chunk(tag, content):
    return (struct.pack('>I', len(content)) + tag + content +
            struct.pack('>I', zlib.crc32(tag + content) & 0xffffffff))


def png(w, h, *, color=0, pixels=None, filt=0):
    channels={0:1,2:3,6:4}[color]
    if pixels is None:
        pixels=bytes([0])*w*h*channels
    raw = bytearray()
    for y in range(h):
        row=bytearray(pixels[y*w*channels:(y+1)*w*channels])
        if filt == 1:
            for x in range(len(row)-1, -1, -1):
                if x:
                    row[x]=(row[x]-pixels[y*w*channels+x-1])&255
        if filt == 2 and y:
            for x in range(len(row)):
                row[x]=(row[x]-pixels[(y-1)*w*channels+x])&255
        raw.append(filt)
        raw.extend(row)
    return (b'\x89PNG\r\n\x1a\n' +
            chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,color,0,0,0)) +
            chunk(b'IDAT',zlib.compress(bytes(raw)))+chunk(b'IEND',b''))


def make_mask(w=16,h=12, rect=(3,2,5,4), filt=0):
    values=bytearray(w*h)
    x0,y0,ww,hh=rect
    for y in range(y0,y0+hh):
        for x in range(x0,x0+ww):
            values[y*w+x]=255
    return png(w,h,pixels=bytes(values),filt=filt)


class SubjectMasksG23Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.space=ManagedWorkspace(self.tmp.name)
        self.original=png(16,12,color=6)
        self.space.create('snails',self.original,profile='Planche - 12 images (4x3)')
        self.filename=self.space.root/'snails.smartsvg'

    def put(self, subject='escargot1', mask=None, sha=None):
        return self.space.put_subject_mask('snails',subject_id=subject,
            mask_png=make_mask() if mask is None else mask,
            expected_sha256=sha or self.space.inspect('snails')['sha256'])

    def test_persist_mask_bounding_box_and_exact_image_bytes(self):
        result=self.put()
        self.assertEqual(result['bbox_px'],[3,2,5,4])
        self.assertEqual(result['selected_pixels'],20)
        self.assertFalse(result['certified'])
        restored=load_project(self.filename)
        self.assertEqual(len(restored.masks),1)
        self.assertEqual(restored.subjects[0].subject_id,'escargot1')
        self.assertEqual(restored.subjects[0].bbox_px,(3,2,5,4))
        self.assertEqual(restored.operations[-1]['kind'],'add_subject_mask')
        self.assertEqual(self.space.subject_mask_png('snails','escargot1'),make_mask())
        self.assertEqual(self.space.source_png('snails'),self.original)
        self.assertFalse(restored.document['cricut_certified'])

    def test_reopen_preserves_multiple_masks_with_independent_ids(self):
        first=make_mask(rect=(2,2,3,5))
        second=make_mask(rect=(9,1,4,6))
        self.put('one',first)
        self.put('two',second)
        report=self.space.inspect('snails')
        self.assertEqual(report['mask_count'],2)
        self.assertEqual(len(report['subjects']),2)
        self.assertEqual(report['operations_count'],2)
        self.assertEqual(self.space.subject_mask_png('snails','one'),first)
        self.assertEqual(self.space.subject_mask_png('snails','two'),second)
        self.assertEqual(load_project(self.filename).subjects[1].bbox_px,(9,1,4,6))

    def test_update_one_subject_keeps_other_and_creates_previous_snapshot(self):
        one=make_mask(rect=(1,1,4,4))
        two=make_mask(rect=(10,2,3,5))
        self.put('one',one)
        self.put('two',two)
        before=self.filename.read_bytes()
        replacement=make_mask(rect=(2,4,7,3))
        result=self.put('one',replacement)
        self.assertTrue(result['previous_available'])
        self.assertEqual(self.space.subject_mask_png('snails','one'),replacement)
        self.assertEqual(self.space.subject_mask_png('snails','two'),two)
        project=load_project(self.filename)
        self.assertEqual(project.operations[-1]['kind'],'replace_subject_mask')
        self.assertEqual(project.operations[-1]['previous_sha256'],sha256(one).hexdigest())
        self.assertEqual(project.operations[-1]['bbox_px'],[2,4,7,3])
        self.assertEqual((self.space.root/'snails.previous.smartsvg').read_bytes(),before)

    def test_undo_note_is_historical_not_replayable_brush_strokes(self):
        self.put('one')
        self.assertEqual(len(load_project(self.filename).operations),1)
        self.assertEqual(len(load_project(self.filename).artifacts),0)
        self.assertEqual(len(load_project(self.filename).qa_results),0)

    def test_full_frame_and_blank_masks_rejected_without_corrupting_archive(self):
        before=self.filename.read_bytes()
        for source, error in [(png(16,12,pixels=b'\x00'*192),'MASK_EMPTY'),
                              (png(16,12,pixels=b'\xff'*192),'MASK_FULL_FRAME')]:
            with self.subTest(error=error),self.assertRaisesRegex(WorkspaceError,error):
                self.put('bad',source)
            self.assertEqual(self.filename.read_bytes(),before)

    def test_rgb_mask_rejected(self):
        rgb=png(16,12,color=2)
        with self.assertRaisesRegex(WorkspaceError,'MASK_NOT_L8'):
            self.put('bad',rgb)

    def test_wrong_size_rejected(self):
        with self.assertRaisesRegex(WorkspaceError,'MASK_DIMENSIONS_MISMATCH'):
            self.put('bad',make_mask(w=17,h=12))

    def test_crc_attack_rejected(self):
        candidate=bytearray(make_mask())
        candidate[-6]^=42
        with self.assertRaisesRegex(WorkspaceError,'MASK_PNG_CRC_FAILED'):
            self.put('bad',bytes(candidate))

    def test_invalid_filter_rejected_after_resigning_crc(self):
        values=b'\x05'+b'\x00'*16
        source=(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR',struct.pack('>IIBBBBB',16,12,8,0,0,0,0)) +
             chunk(b'IDAT',zlib.compress(values*12)) + chunk(b'IEND',b''))
        with self.assertRaisesRegex(WorkspaceError,'INVALID_MASK_FILTER'):
            self.put('bad',source)

    def test_deflate_overrun_rejected(self):
        source=(b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',16,12,8,0,0,0,0))+
                chunk(b'IDAT',zlib.compress(b'\xff'*100000)) + chunk(b'IEND',b''))
        with self.assertRaisesRegex(WorkspaceError,'INVALID_MASK_PIXELS'):
            self.put('bad',source)

    def test_filtered_rows_reconstruct_true_pixels(self):
        for filter_method in (0,1,2):
            with self.subTest(filter=filter_method):
                data=make_mask(filt=filter_method)
                result=inspect_l8_mask(data,16,12)
                self.assertEqual(result['bbox_px'],(3,2,5,4))
                self.assertEqual(result['selected_pixels'],20)

    def test_unchanged_mask_denied_without_new_revision(self):
        self.put('one')
        old=self.filename.read_bytes()
        with self.assertRaisesRegex(WorkspaceError,'MASK_UNCHANGED'):
            self.put('one')
        self.assertEqual(self.filename.read_bytes(),old)

    def test_stale_fingerprint_refused_preserves_latest(self):
        old=self.space.inspect('snails')['sha256']
        self.put('one')
        current=self.filename.read_bytes()
        with self.assertRaisesRegex(WorkspaceError,'PROJECT_CHANGED'):
            self.put('two',expected_sha256=old,mask=make_mask(rect=(6,2,5,6)))
        self.assertEqual(self.filename.read_bytes(),current)

    def test_recovery_restores_preexisting_masks_after_corruption(self):
        first=make_mask(rect=(1,1,4,4))
        self.put('one',first)
        self.put('one',make_mask(rect=(6,2,5,6)))
        self.filename.write_bytes(b'corrupt')
        health=self.space.inspect('snails')
        self.assertTrue(health['recoverable'])
        self.space.restore('snails',confirmed=True,
                           expected_recovery_sha256=health['recovery_sha256'])
        self.assertEqual(self.space.subject_mask_png('snails','one'),first)

    def test_invalid_subject_id_rejected_no_write(self):
        before=self.filename.read_bytes()
        for bad in ('../a','a.b','', 'a'*49, 'été', 'C:/a'):
            with self.subTest(bad=bad),self.assertRaisesRegex(WorkspaceError,'INVALID_SUBJECT_ID'):
                self.put(bad)
        self.assertEqual(before,self.filename.read_bytes())

    def test_missing_mask_read_does_not_access_other_paths(self):
        with self.assertRaisesRegex(WorkspaceError,'SUBJECT_NOT_FOUND'):
            self.space.subject_mask_png('snails','unknown')
        with self.assertRaisesRegex(WorkspaceError,'INVALID_SUBJECT_ID'):
            self.space.subject_mask_png('snails','../private')

    def test_mask_upload_never_certifies_cut_or_generates_svg(self):
        self.put()
        archive=load_project(self.filename)
        self.assertFalse(archive.document['cricut_certified'])
        self.assertEqual(archive.artifacts,())
        self.assertEqual(archive.qa_results,())
        self.assertFalse(any(x.endswith('.svg') for x in archive.resources))


if __name__=='__main__':
    unittest.main()
