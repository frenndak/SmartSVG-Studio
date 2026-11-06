"""Native PNG creation uses the real V1 writer, archives and bounded preview."""
from contextlib import contextmanager
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[1] / 'engine'
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))
from test_v34_native_preview_jobs import fixture_module
from smartsvg_core.project_archive import load_project, save_project
from smartsvg_core import project_recovery
from smartsvg_core.project_workspace_g22 import ManagedWorkspace, WorkspaceError


class NativeProjectCreationTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ENGINE / 'smartsvg_core/native_project_create_v34.py').exists(),
                        'Native creation port missing')
        from smartsvg_core import native_project_create_v34
        self.port = native_project_create_v34
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.folder = Path(tmp.name)
        self.source = self.folder / 'original.png'
        self.source.write_bytes(fixture_module.png())
        self.output = self.folder / 'créations'
        self.output.mkdir()

    def create(self, **changes):
        args = dict(source_path=str(self.source), output_root=str(self.output),
                    name='premier', profile='Auto - conserver le visuel', width_mm='40', dpi=300)
        args.update(changes)
        return self.port.create_native_project(**args)

    def test_create_save_and_reopen_preserves_png_and_settings(self):
        original = self.source.read_bytes()
        receipt = self.create(width_mm='27.5', dpi=450)
        path = self.output / 'SmartSVG_Managed_Projects' / 'premier.smartsvg'
        self.assertEqual(receipt.path, str(path))
        self.assertEqual(receipt.sha256, sha256(path.read_bytes()).hexdigest())
        project = load_project(path, expected_sha256=receipt.sha256)
        self.assertEqual(project.project_id, 'premier')
        self.assertEqual(project.document['width_mm'], 27.5)
        self.assertEqual(project.document['dpi'], 450)
        self.assertEqual(project.resources['sources/source-original.png'], original)
        self.assertEqual(self.source.read_bytes(), original)
        self.assertEqual((len(project.masks), len(project.subjects)), (0, 0))
        self.assertEqual(receipt.preview_status, 'READY_PNG')
        self.assertEqual(project.sources[0].provenance, 'manual_native_png_import')
        self.assertFalse(path.with_name('premier.previous.smartsvg').exists())

    def test_duplicate_never_changes_original_archive(self):
        receipt = self.create()
        before = Path(receipt.path).read_bytes()
        with self.assertRaises(self.port.NativeCreateError) as failure:
            self.create(width_mm=55)
        self.assertEqual(failure.exception.code, 'PROJECT_ALREADY_EXISTS')
        self.assertEqual(Path(receipt.path).read_bytes(), before)
        self.assertFalse(Path(receipt.path).with_name('premier.previous.smartsvg').exists())

    def test_invalid_input_never_creates_a_workspace(self):
        for changes in (dict(name='../escape'), dict(name='CON'), dict(width_mm='nan'),
                        dict(dpi=301), dict(profile='unknown')):
            with self.subTest(changes=changes), self.assertRaises(self.port.NativeCreateError):
                self.create(**changes)
            self.assertEqual(list(self.output.iterdir()), [])
        self.source.write_bytes(b'not a PNG')
        with self.assertRaises(self.port.NativeCreateError): self.create()
        self.assertEqual(list(self.output.iterdir()), [])

    def test_missing_and_oversized_source_rejected_before_any_project(self):
        self.source.unlink()
        with self.assertRaises(self.port.NativeCreateError): self.create()
        with self.source.open('wb') as stream:
            stream.truncate(self.port.MAX_IMAGE_BYTES + 1)
        with self.assertRaises(self.port.NativeCreateError): self.create()
        self.assertEqual(list(self.output.iterdir()), [])

    def test_source_symlink_rejected_without_following(self):
        link = self.folder / 'link.png'
        try: link.symlink_to(self.source)
        except OSError: self.skipTest('symlinks unavailable')
        with self.assertRaises(self.port.NativeCreateError): self.create(source_path=str(link))
        self.assertEqual(list(self.output.iterdir()), [])

    def test_larger_valid_source_can_save_with_explicit_preview_unavailable(self):
        self.source.write_bytes(fixture_module.png(2500, 2100))
        receipt = self.create()
        self.assertEqual(receipt.preview_status, 'SOURCE_TOO_LARGE')
        self.assertEqual(load_project(receipt.path).sources[0].width_px, 2500)
        self.assertEqual(self.source.read_bytes(), load_project(receipt.path).resources['sources/source-original.png'])

    def test_write_failure_never_returns_saved_receipt(self):
        with patch('smartsvg_core.project_recovery.save_project', side_effect=OSError('disk full')):
            with self.assertRaises(self.port.NativeCreateError) as failure:
                self.create()
        self.assertEqual(failure.exception.code, 'SAVE_FAILED')
        self.assertFalse(list(self.output.rglob('*.smartsvg')))

    def test_changed_archive_after_save_is_not_reported_as_verified(self):
        original = ManagedWorkspace.create
        def changed(workspace, *args, **kwargs):
            result = original(workspace, *args, **kwargs)
            path = workspace.root / 'premier.smartsvg'
            project = load_project(path)
            save_project(path, replace(project, document={**project.document, 'width_mm':99}), overwrite=True)
            return result
        with patch.object(ManagedWorkspace, 'create', changed):
            with self.assertRaises(self.port.NativeCreateError) as failure:
                self.create()
        self.assertEqual(failure.exception.code, 'CREATE_UNCONFIRMED')
        self.assertEqual(load_project(self.output / 'SmartSVG_Managed_Projects/premier.smartsvg').document['width_mm'], 99)


class CreateOnlyWriterTests(unittest.TestCase):
    def test_orphan_recovery_sidecars_are_preserved_and_prevent_creation(self):
        for suffix in ('previous', 'pending-backup'):
            with self.subTest(suffix=suffix), tempfile.TemporaryDirectory() as directory:
                workspace = ManagedWorkspace(directory)
                sidecar = workspace.root / ('same.'+suffix+'.smartsvg')
                save_project(sidecar, fixture_module.fixture())
                before = sidecar.read_bytes()
                with self.assertRaises(WorkspaceError) as failure:
                    workspace.create('same', fixture_module.png(), profile='Auto - conserver le visuel')
                self.assertEqual(failure.exception.code, 'PROJECT_ALREADY_EXISTS')
                self.assertEqual(sidecar.read_bytes(), before)
                self.assertFalse((workspace.root / 'same.smartsvg').exists())

    def test_create_race_refuses_existing_project_under_the_same_writer_lock(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = ManagedWorkspace(directory)
            target = workspace.root / 'same.smartsvg'
            existing = replace(fixture_module.fixture(), project_id='same')
            original_lock = project_recovery._project_lock
            @contextmanager
            def raced_lock(path):
                # Another creator wins after ManagedWorkspace's initial check,
                # immediately before this operation acquires the real lock.
                save_project(target, existing)
                with original_lock(path): yield
            with patch.object(project_recovery, '_project_lock', raced_lock):
                with self.assertRaises(WorkspaceError) as failure:
                    workspace.create('same', fixture_module.png(), profile='Auto - conserver le visuel')
            self.assertEqual(failure.exception.code, 'PROJECT_ALREADY_EXISTS')
            self.assertEqual(load_project(target).document, existing.document)
            self.assertFalse(target.with_name('same.previous.smartsvg').exists())


if __name__ == '__main__': unittest.main()
