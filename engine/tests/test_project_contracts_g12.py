"""G1.2 records: referential integrity, mm/alpha truth and certification hygiene."""
import hashlib
import json
import unittest
from dataclasses import replace

from smartsvg_core.project_contracts import (
    Artifact, Mask, QAResult, RecordError, SourceAsset, Subject,
    SCHEMA_VERSION, record_dict, validate_project_records,
)

H = hashlib.sha256(b'synthetic fixture').hexdigest()


def fixtures():
    source = SourceAsset('source-01', H, 100, 80)
    mask = Mask('mask-01', 'source-01', H, 100, 80)
    subject = Subject('subject-01', 'source-01', 'mask-01', (10, 5, 65, 70))
    artifact = Artifact('artifact-01', ('subject-01',), 'print_then_cut_png',
                        'exports/sticker.png', H, 40.0, 32.0, 300)
    qa = QAResult('artifact-01', visual='passed', geometry='passed')
    return source, mask, subject, artifact, qa


class ContractsG12Tests(unittest.TestCase):
    def verify(self, items=None):
        s, m, sub, a, q = fixtures() if items is None else items
        return validate_project_records(sources=[s], masks=[m], subjects=[sub],
                                        artifacts=[a], qa_results=[q])

    def test_roundtrip_to_json_and_metadata_summary(self):
        rows = fixtures()
        self.assertEqual(self.verify()['schema_version'], SCHEMA_VERSION)
        self.assertEqual(self.verify()['subjects'], 1)
        encoded = json.loads(json.dumps([record_dict(v) for v in rows], allow_nan=False))
        self.assertEqual(encoded[2]['bbox_px'], [10, 5, 65, 70])
        self.assertEqual(encoded[3]['width_mm'], 40.0)
        self.assertFalse(encoded[4]['physical_cut'] == 'passed')

    def test_invalid_identity_and_digest(self):
        s, *_ = fixtures()
        for values in ({'source_id':'../escape'}, {'sha256':'abcdef'}, {'width_px':True},
                       {'width_px':100000,'height_px':100000}, {'color_mode':'CMYK'}):
            with self.subTest(values=values), self.assertRaises(RecordError):
                replace(s, **values)

    def test_mask_polarity_or_size_cannot_masquerade(self):
        s, m, sub, a, q = fixtures()
        with self.assertRaisesRegex(RecordError, 'MASK_MUST_BE_L8'):
            replace(m, polarity='background_white')
        with self.assertRaisesRegex(RecordError, 'MASK_SOURCE_MISMATCH'):
            self.verify((s, replace(m, width_px=99), sub, a, q))

    def test_bbox_and_references(self):
        s, m, sub, a, q = fixtures()
        for subject, error in ((replace(sub, bbox_px=(90, 0, 20, 20)), 'BBOX_OUT_OF_SOURCE'),
                               (replace(sub, mask_id='missing'), 'SUBJECT_SOURCE_MASK_MISMATCH'),
                               (replace(sub, accessory_ids=('missing',)), 'INVALID_ACCESSORY_LINK')):
            with self.subTest(error=error), self.assertRaisesRegex(RecordError, error):
                self.verify((s, m, subject, a, q))
        with self.assertRaisesRegex(RecordError, 'DUPLICATE_ID'):
            validate_project_records(sources=[s,s], masks=[m], subjects=[sub], artifacts=[a])


    def test_accessory_graph_rejects_direct_and_long_cycles(self):
        # A link can be individually valid and still create a dependency
        # cycle. The metadata validator must reject this before exporters
        # try to resolve nested or attached subjects.
        source, mask, original, artifact, qa = fixtures()
        a = replace(original, subject_id='subject-A', accessory_ids=('subject-B',))
        b = replace(original, subject_id='subject-B', accessory_ids=('subject-A',))
        for subjects in (
            [a, b],
            [replace(a, accessory_ids=('subject-C',)),
             b, replace(original, subject_id='subject-C',
                        accessory_ids=('subject-B',))],
        ):
            with self.subTest(subjects=[item.subject_id for item in subjects]):
                with self.assertRaisesRegex(RecordError, 'CYCLIC_ACCESSORY_LINK'):
                    validate_project_records(
                        sources=[source], masks=[mask], subjects=subjects,
                        artifacts=[], qa_results=[])

    def test_accessory_graph_accepts_long_acyclic_chain(self):
        # Iterative traversal also supports many valid accessories without
        # depending on the Python recursion limit or mutating frozen records.
        source, mask, original, _, _ = fixtures()
        subjects = [
            replace(original, subject_id=f'subject-{i:04d}',
                    accessory_ids=((f'subject-{i+1:04d}',) if i < 1499 else ()))
            for i in range(1500)
        ]
        before = subjects[0].accessory_ids
        result = validate_project_records(
            sources=[source], masks=[mask], subjects=subjects,
            artifacts=[], qa_results=[])
        self.assertEqual(result['subjects'], 1500)
        self.assertEqual(subjects[0].accessory_ids, before)

    def test_accessory_graph_accepts_branching_and_disconnected_subjects(self):
        source, mask, original, _, _ = fixtures()
        subjects = [
            replace(original, subject_id='main-subject',
                    accessory_ids=('accessory-1', 'accessory-2')),
            replace(original, subject_id='accessory-1', accessory_ids=()),
            replace(original, subject_id='accessory-2', accessory_ids=()),
            replace(original, subject_id='independent', accessory_ids=()),
        ]
        result = validate_project_records(
            sources=[source], masks=[mask], subjects=subjects, artifacts=[])
        self.assertEqual(result['subjects'], 4)

    def test_export_path_and_mm(self):
        _, _, _, a, _ = fixtures()
        for values in ({'file_path':'../outside.png'}, {'file_path':'C:\\outside.png'},
                       {'file_path':'/tmp/out.png'}, {'file_path':'out.svg'},
                       {'width_mm':float('nan')}, {'height_mm':float('inf')},
                       {'width_mm':True}, {'ppi':0}, {'ppi':None}):
            with self.subTest(values=values), self.assertRaises(RecordError):
                replace(a, **values)
        self.assertEqual(replace(a, use='basic_cut_svg', file_path='cut.svg', ppi=None).use,
                         'basic_cut_svg')

    def test_artifact_path_rejects_windows_device_names_and_controls(self):
        _, _, _, artifact, _ = fixtures()
        bad_paths = (
            'exports/CON.png', 'exports/con.png', 'exports/AUX.PNG',
            'exports/NUL.png', 'exports/COM1.png', 'exports/lpt9.png',
            'exports/COM¹.png', 'exports/com².PNG', 'exports/COM³.png',
            'exports/LPT¹.png', 'exports/lpt².png', 'exports/LPT³.png',
            'CON/out.png', 'exports/folder./out.png',
            'exports/folder /out.png', 'exports/out?.png',
            'exports/out*.png', 'exports/out|.png',
            'exports/out\x00.png', 'exports/out\n.png',
            'exports/out\x7f.png',
        )
        for path in bad_paths:
            with self.subTest(path=repr(path)), self.assertRaisesRegex(
                    RecordError, 'INVALID_ARTIFACT_PATH'):
                replace(artifact, file_path=path)
        for path in ('exports/étiquette 01.png', 'exports/CONTOUR.png',
                     'exports/normal.sticker.png'):
            with self.subTest(path=path):
                self.assertEqual(replace(artifact, file_path=path).file_path, path)

    def test_artifact_path_rejects_unicode_format_controls(self):
        # Bidi overrides and invisible format characters can misrepresent
        # an otherwise valid PNG/SVG filename in a UI or project listing.
        _, _, _, artifact, _ = fixtures()
        for character in ('\u202e', '\u202a', '\u2066', '\u2069',
                          '\u200b', '\u200d'):
            path = f'exports/sticker{character}gnp.png'
            with self.subTest(codepoint=hex(ord(character))), self.assertRaisesRegex(
                    RecordError, 'INVALID_ARTIFACT_PATH'):
                replace(artifact, file_path=path)
        # Do not reject ordinary Unicode filenames with visible accents.
        path = 'exports/étiquette 01.png'
        self.assertEqual(replace(artifact, file_path=path).file_path, path)

    def test_artifact_path_rejects_invisible_combining_grapheme_joiner(self):
        # U+034F is default-ignorable despite being category Mn, not Cf.
        # It must not create a visually indistinguishable output filename.
        _, _, _, artifact, _ = fixtures()
        self.assertEqual(artifact.file_path, 'exports/sticker.png')
        with self.assertRaisesRegex(RecordError, 'INVALID_ARTIFACT_PATH'):
            replace(artifact, file_path='exports/sticker\u034f.png')
        # Ordinary combining accents are valid and remain normalizable.
        accented = 'exports/cafe\u0301.png'
        self.assertEqual(replace(artifact, file_path=accented).file_path, accented)

    def test_artifact_path_rejects_default_ignorable_variation_selectors(self):
        # Variation selectors are Mn (not Cf) but can make distinct paths
        # visually indistinguishable, bypassing the portable-path alias check.
        _, _, _, artifact, _ = fixtures()
        for selector in ('\uFE00', '\uFE0F', '\U000E0100', '\U000E01EF'):
            path = f'exports/sticker{selector}.png'
            with self.subTest(codepoint=hex(ord(selector))), self.assertRaisesRegex(
                    RecordError, 'INVALID_ARTIFACT_PATH'):
                replace(artifact, file_path=path)
        # Preserve ordinary combining accents, including decomposed Unicode.
        accented = 'exports/cafe\u0301.png'
        self.assertEqual(replace(artifact, file_path=accented).file_path, accented)

    def test_artifact_path_rejects_unicode_line_and_paragraph_separators(self):
        # C1 controls (including U+0085 NEXT LINE) can split UI/log lines,
        # just like U+2028/U+2029. Preserve ordinary visible accents.
        _, _, _, artifact, _ = fixtures()
        for separator in ('\u0080', '\u0085', '\u009f', '\u2028', '\u2029'):
            path = f'exports/sticker{separator}.png'
            with self.subTest(codepoint=hex(ord(separator))), self.assertRaisesRegex(
                    RecordError, 'INVALID_ARTIFACT_PATH'):
                replace(artifact, file_path=path)
        for path in ('exports/étiquette 01.png', 'exports/cafe\u0301.png'):
            with self.subTest(path=path):
                self.assertEqual(replace(artifact, file_path=path).file_path, path)

    def test_json_array_records_are_deeply_immutable(self):
        # Lists from untrusted JSON must not mutate frozen validated records.
        s, m, original_sub, original_art, q = fixtures()
        bbox = [10, 5, 65, 70]
        accessories = []
        subject_ids = ['subject-01']
        sub = replace(original_sub, bbox_px=bbox, accessory_ids=accessories)
        artifact = replace(original_art, subject_ids=subject_ids)
        self.assertIsInstance(sub.bbox_px, tuple)
        self.assertIsInstance(sub.accessory_ids, tuple)
        self.assertIsInstance(artifact.subject_ids, tuple)
        bbox[2] = 10_000_000
        accessories.append('missing')
        subject_ids.append('missing')
        self.assertEqual(sub.bbox_px, (10, 5, 65, 70))
        self.assertEqual(sub.accessory_ids, ())
        self.assertEqual(artifact.subject_ids, ('subject-01',))
        with self.assertRaises(TypeError):
            sub.bbox_px[2] = 10_000_000
        with self.assertRaises(AttributeError):
            sub.accessory_ids.append('missing')
        with self.assertRaises(AttributeError):
            artifact.subject_ids.append('missing')
        result = self.verify((s, m, sub, artifact, q))
        self.assertEqual(result['subjects'], 1)
        # JSON remains list-shaped for project persistence.
        encoded = json.loads(json.dumps([record_dict(sub), record_dict(artifact)]))
        self.assertEqual(encoded[0]['bbox_px'], [10, 5, 65, 70])
        self.assertEqual(encoded[0]['accessory_ids'], [])
        self.assertEqual(encoded[1]['subject_ids'], ['subject-01'])
        for record, values in ((sub, {'bbox_px': [0, 0, -1, 5]}),
                               (sub, {'accessory_ids': ['invalid/id']}),
                               (artifact, {'subject_ids': ['invalid/id']})):
            with self.subTest(values=values), self.assertRaises(RecordError):
                replace(record, **values)

    def test_huge_mm_integer_raises_record_error_not_overflow(self):
        _, _, _, artifact, _ = fixtures()
        for values in (
            {'width_mm': 10**400},
            {'height_mm': 10**400},
            {'width_mm': -(10**400)},
            {'height_mm': float('inf')},
        ):
            with self.subTest(values=values), self.assertRaisesRegex(
                    RecordError, 'INVALID_NUMBER'):
                replace(artifact, **values)
        self.assertEqual(replace(artifact, width_mm=45).width_mm, 45)

    def test_artifact_paths_must_be_unique_on_portable_filesystems(self):
        s, m, sub, artifact, qa = fixtures()

        def validate_pair(second):
            return validate_project_records(
                sources=[s], masks=[m], subjects=[sub],
                artifacts=[artifact, second], qa_results=[qa])

        # A distinct artifact ID must never overwrite another artifact file.
        with self.assertRaisesRegex(RecordError, 'DUPLICATE_FILE_PATH'):
            validate_pair(replace(artifact, artifact_id='artifact-02',
                                  sha256='0' * 64))
        # Windows aliases paths that differ only by case, including extension.
        with self.assertRaisesRegex(RecordError, 'DUPLICATE_FILE_PATH'):
            validate_pair(replace(artifact, artifact_id='artifact-02',
                                  file_path='EXPORTS/STICKER.PNG'))
        # Even identical content cannot assign two artifact IDs to one path.
        with self.assertRaisesRegex(RecordError, 'DUPLICATE_FILE_PATH'):
            validate_pair(replace(artifact, artifact_id='artifact-02'))
        # Distinct names remain valid; neither original is modified.
        result = validate_pair(replace(artifact, artifact_id='artifact-02',
                                       file_path='exports/sticker_02.png'))
        self.assertEqual(result['artifacts'], 2)
        self.assertEqual(artifact.file_path, 'exports/sticker.png')

    def test_artifact_paths_unicode_normalization_aliases(self):
        s, m, sub, artifact, qa = fixtures()
        first = replace(artifact, file_path='exports/étiquette.png')
        second = replace(artifact, artifact_id='artifact-02',
                         file_path='exports/e\u0301tiquette.png')
        with self.assertRaisesRegex(RecordError, 'DUPLICATE_FILE_PATH'):
            validate_project_records(sources=[s], masks=[m], subjects=[sub],
                                     artifacts=[first, second], qa_results=[qa])

    def test_qa_never_promotes_simulation_to_real(self):
        with self.assertRaisesRegex(RecordError, 'IMPORT_PASS_REQUIRES_REAL_EVIDENCE'):
            QAResult('artifact-01', design_space_import='passed', import_evidence='fixture')
        with self.assertRaisesRegex(RecordError, 'CUT_PASS_REQUIRES_IMPORT_AND_REAL_EVIDENCE'):
            QAResult('artifact-01', physical_cut='passed', environment='real', physical_evidence='photo')
        qa = QAResult('artifact-01', design_space_import='passed', physical_cut='passed',
                      environment='real', import_evidence='real-import-01', physical_evidence='real-cut-01')
        self.assertEqual(qa.physical_cut, 'passed')

    def test_qa_status_rejects_unhashable_metadata_with_record_error(self):
        # Untrusted JSON can contain arrays/objects in fields requiring a status.
        for field in ('visual', 'geometry', 'design_space_import', 'physical_cut'):
            for bad in ([], {}, ['passed']):
                with self.subTest(field=field, bad=bad), self.assertRaisesRegex(
                        RecordError, f'{field}: INVALID_STATUS'):
                    QAResult('artifact-01', **{field: bad})
        # Preserve the supported status values and real-evidence contract.
        for status in ('not_tested', 'passed', 'failed'):
            self.assertEqual(QAResult('artifact-01', visual=status).visual, status)

    def test_unknown_artifact_and_subject_rejected(self):
        s, m, sub, a, q = fixtures()
        with self.assertRaisesRegex(RecordError, 'UNKNOWN_ARTIFACT_SUBJECT'):
            self.verify((s, m, sub, replace(a, subject_ids=('unknown',)), q))
        with self.assertRaisesRegex(RecordError, 'UNKNOWN_QA_ARTIFACT'):
            self.verify((s, m, sub, a, replace(q, artifact_id='missing')))

    def test_false_qualified_status_and_invalid_record_collection(self):
        s, m, sub, a, q = fixtures()
        with self.assertRaises(RecordError):
            replace(q, geometry='certified')
        with self.assertRaises(RecordError):
            validate_project_records(sources=[record_dict(s)], masks=[m],
                                     subjects=[sub], artifacts=[a])


if __name__ == '__main__':
    unittest.main()
