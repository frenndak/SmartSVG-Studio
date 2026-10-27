"""G1.3: synthetic, non-copyrighted fixtures and negative ZIP tests."""
import hashlib
import json
from pathlib import Path
import stat
import struct
import tempfile
import unittest
import zipfile
import zlib

from smartsvg_core.project_archive import (
    LoadedProject, ProjectArchiveError, SCHEMA_VERSION, load_project, save_project,
)
from smartsvg_core.project_contracts import (
    Artifact, Mask, QAResult, SourceAsset, Subject,
)


def _png(width, height, color_type):
    channels = 1 if color_type == 0 else 4
    row = bytes([0]) + bytes([100, 120, 140, 255][:channels]) * width
    payload = zlib.compress(row * height)
    def chunk(name, body):
        return struct.pack('>I', len(body)) + name + body + struct.pack('>I', zlib.crc32(name + body) & 0xffffffff)
    ihdr = struct.pack('>IIBBBBB', width, height, 8, color_type, 0, 0, 0)
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr) + chunk(b'IDAT', payload) + chunk(b'IEND', b'')


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _fixture():
    source = _png(16, 12, 6)
    mask = _png(16, 12, 0)
    cut_svg = b'<svg xmlns="http://www.w3.org/2000/svg" width="30mm" height="20mm" viewBox="0 0 30 20"><path d="M0 0L30 0L30 20Z"/></svg>'
    assets = {'sources/source-01.png': source, 'masks/mask-01.png': mask,
              'exports/contour.svg': cut_svg}
    return LoadedProject(
        'project-01', '21.15.2',
        (SourceAsset('source-01', _sha(source), 16, 12),),
        (Mask('mask-01', 'source-01', _sha(mask), 16, 12),),
        (Subject('subject-01', 'source-01', 'mask-01', (1, 1, 14, 10)),),
        (Artifact('artifact-01', ('subject-01',), 'basic_cut_svg',
                  'exports/contour.svg', _sha(cut_svg), 30.0, 20.0),),
        (QAResult('artifact-01', visual='passed', geometry='passed'),),
        {'width_mm': 30.0, 'height_mm': 20.0, 'zoom': 1.2,
         'objects': [{'id': 'subject-01', 'x': 4.0, 'y': 3.0}]},
        [{'revision_id': f'revision-{n}', 'kind': 'move' if n < 12 else 'undo',
          'subject_id': 'subject-01', 'x': n} for n in range(15)],
        assets,
        {'source-01': 'sources/source-01.png'},
        {'mask-01': 'masks/mask-01.png'},
    )


class ArchiveG13Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'test.smartsvg'

    def _write_zip_from(self, updates):
        with zipfile.ZipFile(self.path, 'r') as inp:
            rows = [(name, inp.read(name)) for name in inp.namelist()]
        with zipfile.ZipFile(self.path, 'w', compression=zipfile.ZIP_DEFLATED) as out:
            for name, data in rows:
                out.writestr(name, updates.get(name, data))
            for name, data in updates.items():
                if name not in dict(rows):
                    out.writestr(name, data)

    def test_exact_save_close_open_15_operations_and_3_undo(self):
        initial = _fixture()
        result = save_project(self.path, initial)
        self.assertEqual(result['schema_version'], SCHEMA_VERSION)
        self.assertFalse(result['cut_verified'])
        restored = load_project(self.path)
        self.assertEqual(restored, initial)
        self.assertEqual(sum(op['kind'] == 'undo' for op in restored.operations), 3)
        self.assertEqual(len(restored.resources), 3)
        self.assertEqual(result['sha256'], _sha(self.path.read_bytes()))
        with zipfile.ZipFile(self.path) as archive:
            self.assertEqual(len(archive.namelist()), 11)
            self.assertNotIn('../', ''.join(archive.namelist()))

    def test_no_overwrite_by_default_and_atomic_overwrite(self):
        original = _fixture()
        save_project(self.path, original)
        before = self.path.read_bytes()
        with self.assertRaisesRegex(ProjectArchiveError, 'DESTINATION_EXISTS'):
            save_project(self.path, original)
        self.assertEqual(self.path.read_bytes(), before)
        upgraded = _fixture()
        upgraded.document['objects'][0]['x'] = 9
        save_project(self.path, upgraded, overwrite=True)
        self.assertEqual(load_project(self.path).document['objects'][0]['x'], 9)

    def test_bad_write_never_destroys_last_good_snapshot(self):
        save_project(self.path, _fixture())
        previous = self.path.read_bytes()
        damaged = _fixture()
        damaged.resources['masks/mask-01.png'] = b'not a png'
        with self.assertRaisesRegex(ProjectArchiveError, 'SHA256'):
            save_project(self.path, damaged, overwrite=True)
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertEqual(load_project(self.path).project_id, 'project-01')

    def test_modified_asset_is_rejected_against_manifest(self):
        save_project(self.path, _fixture())
        self._write_zip_from({'masks/mask-01.png': _png(16, 12, 6)})
        with self.assertRaisesRegex(ProjectArchiveError, 'MANIFEST_CONTENT_MISMATCH'):
            load_project(self.path)

    def test_path_traversal_entry_rejected_without_extraction(self):
        save_project(self.path, _fixture())
        self._write_zip_from({'../escape.txt': b'cannot extract'})
        with self.assertRaisesRegex(ProjectArchiveError, 'UNSAFE_ARCHIVE_PATH'):
            load_project(self.path)
        self.assertFalse((Path(self.temp.name).parent / 'escape.txt').exists())

    def test_duplicate_zip_filename_rejected(self):
        save_project(self.path, _fixture())
        with zipfile.ZipFile(self.path, 'a') as f:
            # Same archive member is always ambiguous, including casefold collisions.
            f.writestr('SOURCES/source-01.png', b'fake')
        with self.assertRaisesRegex(ProjectArchiveError, 'DUPLICATE_ARCHIVE_PATH'):
            load_project(self.path)

    def test_symlink_zip_entry_rejected(self):
        save_project(self.path, _fixture())
        with zipfile.ZipFile(self.path, 'a') as archive:
            link = zipfile.ZipInfo('sources/linked.png')
            link.create_system = 3
            link.external_attr = (stat.S_IFLNK | 0o777) << 16
            archive.writestr(link, b'../../../evil')
        with self.assertRaisesRegex(ProjectArchiveError, 'UNSAFE_ZIP_ENTRY'):
            load_project(self.path)

    def test_extra_unmanifested_entry_rejected(self):
        save_project(self.path, _fixture())
        self._write_zip_from({'sources/unlisted.png': b'unknown'})
        with self.assertRaisesRegex(ProjectArchiveError, 'UNDECLARED_OR_MISSING_ENTRY'):
            load_project(self.path)

    def test_duplicate_json_key_rejected(self):
        save_project(self.path, _fixture())
        self._write_zip_from({'manifest.json': b'{"schema_version":"smartsvg-project/1","schema_version":"smartsvg-project/1"}'})
        with self.assertRaisesRegex(ProjectArchiveError, 'DUPLICATE_JSON_KEY'):
            load_project(self.path)

    def test_future_schema_must_not_be_silently_migrated(self):
        save_project(self.path, _fixture())
        with zipfile.ZipFile(self.path) as archive:
            manifest = json.loads(archive.read('manifest.json'))
        manifest['schema_version'] = 'smartsvg-project/99'
        self._write_zip_from({'manifest.json': json.dumps(manifest).encode()})
        with self.assertRaisesRegex(ProjectArchiveError, 'UNSUPPORTED_PROJECT_SCHEMA'):
            load_project(self.path)

    def test_invalid_grayscale_mask_blocks_save(self):
        project = _fixture()
        invalid = _png(16, 12, 6)
        project.resources['masks/mask-01.png'] = invalid
        from dataclasses import replace
        project = replace(project, masks=(replace(project.masks[0], sha256=_sha(invalid)),))
        with self.assertRaisesRegex(ProjectArchiveError, 'MASK_NOT_L8_PNG'):
            save_project(self.path, project)

    def test_wrong_source_size_blocks_save(self):
        from dataclasses import replace
        project = _fixture()
        wrong = _png(20, 12, 6)
        project.resources['sources/source-01.png'] = wrong
        project = replace(project, sources=(replace(project.sources[0], sha256=_sha(wrong)),))
        with self.assertRaisesRegex(ProjectArchiveError, 'SOURCE_PIXEL_DIMENSIONS_MISMATCH'):
            save_project(self.path, project)

    def test_bad_mask_idat_blocks_save_even_when_sha_updated(self):
        from dataclasses import replace
        project = _fixture()
        data = bytearray(project.resources['masks/mask-01.png'])
        # Corrupt one IDAT byte. The member checksum is then deliberately updated.
        data[48] ^= 0x7a
        raw = bytes(data)
        project.resources['masks/mask-01.png'] = raw
        project = replace(project, masks=(replace(project.masks[0], sha256=_sha(raw)),))
        with self.assertRaisesRegex(ProjectArchiveError, 'PNG_CRC_FAILED'):
            save_project(self.path, project)

    def test_invalid_mask_reference_rejected_before_disk_write(self):
        from dataclasses import replace
        project = _fixture()
        project = replace(project, subjects=(replace(project.subjects[0], mask_id='mask-does-not-exist'),))
        with self.assertRaisesRegex(ProjectArchiveError, 'RECORDS_INVALID'):
            save_project(self.path, project)
        self.assertFalse(self.path.exists())

    def test_archive_bomb_exceeds_member_budget(self):
        save_project(self.path, _fixture())
        with zipfile.ZipFile(self.path, 'a', compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr('assets/oversized.bin', b'Z' * (64 * 1024 * 1024 + 1))
        with self.assertRaisesRegex(ProjectArchiveError, 'ZIP_BOMB_OR_OVERSIZED_MEMBER'):
            load_project(self.path)

    def test_json_nan_rejected_without_creating_archive(self):
        project = _fixture()
        project.document['x'] = float('nan')
        with self.assertRaisesRegex(ProjectArchiveError, 'INVALID_JSON_DATA'):
            save_project(self.path, project)
        self.assertFalse(self.path.exists())

    def test_deep_json_graph_rejected_on_save_and_open(self):
        project = _fixture()
        nested = {}
        top = nested
        for _ in range(40):
            next_value = {}
            top['item'] = next_value
            top = next_value
        project.document['deep'] = nested
        with self.assertRaisesRegex(ProjectArchiveError, 'JSON_NESTING_TOO_DEEP'):
            save_project(self.path, project)
        self.assertFalse(self.path.exists())
        # Hostile externally crafted archive: checksummed document and updated manifest
        save_project(self.path, _fixture())
        with zipfile.ZipFile(self.path) as source:
            manifest = json.loads(source.read('manifest.json'))
        payload = json.dumps({'nested': nested}).encode()
        manifest['entries']['document.json'] = {'sha256': _sha(payload), 'size_bytes': len(payload)}
        self._write_zip_from({
            'document.json': payload,
            'manifest.json': json.dumps(manifest).encode(),
        })
        with self.assertRaisesRegex(ProjectArchiveError, 'JSON_NESTING_TOO_DEEP'):
            load_project(self.path)

    def test_cyclic_accessories_rejected_on_save_and_untrusted_load(self):
        from dataclasses import replace
        from smartsvg_core.project_contracts import record_dict
        original = _fixture()
        first = replace(original.subjects[0],
                        accessory_ids=('subject-02',))
        second = replace(original.subjects[0],
                         subject_id='subject-02',
                         accessory_ids=('subject-01',))
        hostile = replace(original, subjects=(first, second))
        with self.assertRaisesRegex(
                ProjectArchiveError, 'RECORDS_INVALID: CYCLIC_ACCESSORY_LINK'):
            save_project(self.path, hostile)
        self.assertFalse(self.path.exists())

        # An attacker can supply coherent ZIP CRC and SHA-256 manifests.
        # The *semantic* reference graph must still fail on reload.
        save_project(self.path, original)
        with zipfile.ZipFile(self.path) as z:
            manifest = json.loads(z.read('manifest.json'))
        subjects_bytes = json.dumps([
            record_dict(subject) for subject in (first, second)
        ], sort_keys=True).encode('utf-8')
        manifest['entries']['subjects.json'] = {
            'sha256': _sha(subjects_bytes),
            'size_bytes': len(subjects_bytes),
        }
        self._write_zip_from({
            'subjects.json': subjects_bytes,
            'manifest.json': json.dumps(manifest).encode('utf-8'),
        })
        with self.assertRaisesRegex(
                ProjectArchiveError, 'RECORDS_INVALID: CYCLIC_ACCESSORY_LINK'):
            load_project(self.path)

    def test_distinct_sources_cannot_share_one_archive_resource(self):
        from dataclasses import replace
        project = _fixture()
        first = project.sources[0]
        project = replace(project, sources=(
            first, replace(first, source_id='source-02')))
        project.source_paths['source-02'] = project.source_paths['source-01']
        # Both IDs have the same declared hash/dimensions, yet different
        # logical ownership. Previously the second record replaced the first
        # entry in the expected-resource dict without any error.
        with self.assertRaisesRegex(ProjectArchiveError, 'RESOURCE_PATH_COLLISION'):
            save_project(self.path, project)
        self.assertFalse(self.path.exists())

    def test_untrusted_resource_maps_fail_as_archive_errors(self):
        from dataclasses import replace
        project = _fixture()
        for field, value, error in (
            ('source_paths', None, 'INVALID_SOURCE_PATH_MAP'),
            ('source_paths', [], 'INVALID_SOURCE_PATH_MAP'),
            ('mask_paths', None, 'INVALID_MASK_PATH_MAP'),
            ('mask_paths', [], 'INVALID_MASK_PATH_MAP'),
            ('resources', None, 'INVALID_RESOURCE_MAP'),
            ('resources', [], 'INVALID_RESOURCE_MAP'),
        ):
            with self.subTest(field=field, value=value):
                damaged = replace(project, **{field: value})
                with self.assertRaisesRegex(ProjectArchiveError, error):
                    save_project(self.path, damaged)
                self.assertFalse(self.path.exists())
        # A valid object remains serializable after every rejected probe.
        save_project(self.path, project)
        self.assertEqual(load_project(self.path), project)

    def test_resource_path_escape_and_alias_collision(self):
        from dataclasses import replace
        project = _fixture()
        project.source_paths['source-01'] = 'sources/../outside.png'
        with self.assertRaisesRegex(ProjectArchiveError, 'UNSAFE_ARCHIVE_PATH'):
            save_project(self.path, project)


if __name__ == '__main__':
    unittest.main()
