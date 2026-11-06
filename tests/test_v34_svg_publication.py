"""V34-131 / T-V34-17-08 partial: publish complete SVGs without replacement.

Exercise the real stdlib publication module, not a copy of its functions.
No graphical browser, image dependency, Design Space or machine claim.
"""
import errno
import importlib.util
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'svg_publication_v34', ROOT / 'engine/smartsvg_vector/svg_publication.py')
publication = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(publication)
SVG = b'<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" width="40mm" height="20mm" viewBox="0 0 40 20"><path d="M0 0H40V20H0Z"/></svg>'


class SVGPublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def assert_no_staging(self):
        self.assertEqual(list(self.folder.glob('.smartsvg_svg_*')), [])

    def test_bytes_and_versioned_names_are_preserved(self):
        old = self.folder / 'art_001.svg'
        old.write_bytes(b'existing user artwork')
        first = Path(publication.save_svg(SVG, str(self.folder), 'art'))
        second = Path(publication.save_svg(SVG, str(self.folder), 'art'))
        self.assertEqual([first.name, second.name], ['art_002.svg', 'art_003.svg'])
        self.assertEqual(first.read_bytes(), SVG)
        self.assertEqual(second.read_bytes(), SVG)
        self.assertEqual(old.read_bytes(), b'existing user artwork')
        self.assert_no_staging()

    def test_final_name_is_absent_until_complete_staging_is_synced(self):
        real_sync, real_link = publication.os.fsync, publication.os.link
        def sync(fd):
            self.assertEqual(list(self.folder.glob('art_*.svg')), [])
            self.assertEqual(next(self.folder.glob('.smartsvg_svg_*')).read_bytes(), SVG)
            real_sync(fd)
        def link(source, target):
            self.assertEqual(Path(source).read_bytes(), SVG)
            self.assertFalse(Path(target).exists())
            real_link(source, target)
        with patch.object(publication.os, 'fsync', side_effect=sync), patch.object(publication.os, 'link', side_effect=link):
            result = publication.save_svg(SVG, str(self.folder), 'art')
        self.assertEqual(Path(result).read_bytes(), SVG)
        self.assert_no_staging()

    def test_write_failure_cleans_temporary_file_and_never_publishes(self):
        real_open = publication.os.fdopen
        class InterruptedWriter:
            def __init__(self, fd, mode): self.file = real_open(fd, mode)
            def __enter__(self): return self
            def __exit__(self, *args): self.file.close()
            def write(self, data):
                self.file.write(data[:20])
                raise OSError('simulated partial write')
        with patch.object(publication.os, 'fdopen', side_effect=InterruptedWriter):
            with self.assertRaises(OSError): publication.save_svg(SVG, str(self.folder))
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_sync_failure_does_not_leave_a_visible_svg(self):
        with patch.object(publication.os, 'fsync', side_effect=OSError('interrupted fsync')):
            with self.assertRaises(OSError): publication.save_svg(SVG, str(self.folder))
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_staging_corruption_is_detected_before_publication(self):
        real_sync = publication.os.fsync
        def corrupt(fd):
            real_sync(fd)
            next(self.folder.glob('.smartsvg_svg_*')).write_bytes(b'corrupted')
        with patch.object(publication.os, 'fsync', side_effect=corrupt):
            with self.assertRaisesRegex(ValueError, 'incoherente'):
                publication.save_svg(SVG, str(self.folder))
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_competing_publisher_is_kept_and_next_name_is_selected(self):
        real_link = publication.os.link
        def race(source, target):
            if Path(target).name == 'art_001.svg':
                Path(target).write_bytes(b'concurrent complete file')
                raise FileExistsError(errno.EEXIST, 'exists')
            return real_link(source, target)
        with patch.object(publication.os, 'link', side_effect=race):
            result = publication.save_svg(SVG, str(self.folder), 'art')
        self.assertEqual(Path(result).name, 'art_002.svg')
        self.assertEqual((self.folder/'art_001.svg').read_bytes(), b'concurrent complete file')
        self.assertEqual(Path(result).read_bytes(), SVG)
        self.assert_no_staging()

    @unittest.skipIf(publication.os.name == 'nt', 'POSIX fail-closed branch')
    def test_no_hardlinks_fails_without_exposing_streaming_or_renaming(self):
        with patch.object(publication.os, 'link', side_effect=OSError(errno.EOPNOTSUPP, 'unsupported')):
            with patch.object(publication.os, 'rename') as rename:
                with self.assertRaisesRegex(ValueError, 'Publication atomique impossible'):
                    publication.save_svg(SVG, str(self.folder))
                rename.assert_not_called()
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_full_version_namespace_preserves_all_existing_files(self):
        for i in range(1, 1000): (self.folder/f'art_{i:03d}.svg').write_bytes(b'previous')
        with self.assertRaisesRegex(ValueError, 'Trop de versions'):
            publication.save_svg(SVG, str(self.folder), 'art')
        self.assertEqual(len(list(self.folder.iterdir())), 999)
        self.assertTrue(all(p.read_bytes() == b'previous' for p in self.folder.iterdir()))
        self.assert_no_staging()

    def test_symlink_name_is_skipped_without_touching_target(self):
        target = self.folder/'user.svg';target.write_bytes(b'keep this')
        try: (self.folder/'art_001.svg').symlink_to(target)
        except OSError: self.skipTest('symlinks unavailable')
        result = publication.save_svg(SVG, str(self.folder), 'art')
        self.assertEqual(Path(result).name, 'art_002.svg')
        self.assertEqual(target.read_bytes(), b'keep this')
        self.assert_no_staging()

    def test_parallel_exports_return_unique_complete_files(self):
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda _: publication.save_svg(SVG, str(self.folder), 'art'), range(12)))
        self.assertEqual(len(set(results)), 12)
        self.assertTrue(all(Path(path).read_bytes() == SVG for path in results))
        self.assert_no_staging()

    def test_invalid_arguments_do_not_create_export_files(self):
        for payload, folder, prefix in [(b'<svg/>',str(self.folder),'art'),
                (SVG,'relative','art'),(SVG,str(self.folder),'../art')]:
            with self.subTest(prefix=prefix, folder=folder):
                with self.assertRaises(ValueError): publication.save_svg(payload, folder, prefix)
        self.assertEqual(list(self.folder.iterdir()), [])

    def test_default_comfyui_output_location_is_retained(self):
        import types
        with patch.dict('sys.modules', {'folder_paths':types.SimpleNamespace(get_output_directory=lambda:str(self.folder))}):
            result = Path(publication.save_svg(SVG))
        self.assertEqual(result.parent, self.folder/'SmartSVG_Studio'/'SVG_Multicouche')
        self.assertEqual(result.read_bytes(), SVG)
