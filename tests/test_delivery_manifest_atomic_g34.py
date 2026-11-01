"""V3.4: no-overwrite delivery manifest, including concurrent publishers and fallback."""
from __future__ import annotations

import errno
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / 'engine/smartsvg_cricut/delivery_v21122.py'
SPEC = importlib.util.spec_from_file_location('smartsvg_delivery_g34', MODULE_PATH)
delivery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(delivery)


class TestDeliveryManifestAtomicG34(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.folder = self.root / '07_LIVRAISON_STICKERS_V21_12_2'
        self.final = self.folder / 'MANIFESTE_STICKERS.json'

    def assert_no_staging(self):
        self.assertEqual(list(self.folder.glob('.manifest_*.tmp')), [])

    def test_publishes_json_and_refuses_replacement(self):
        output = delivery.write_delivery(self.root, {'version': 1, 'statut': 'non certifie'})
        self.assertEqual(output, str(self.final))
        original = self.final.read_bytes()
        self.assertEqual(json.loads(original)['version'], 1)
        with self.assertRaisesRegex(delivery.DeliveryError, 'aucun ecrasement'):
            delivery.write_delivery(self.root, {'version': 2})
        self.assertEqual(self.final.read_bytes(), original)
        self.assert_no_staging()

    def test_concurrent_manifest_is_not_overwritten_by_hardlink(self):
        competitor = b'ANOTHER WRITER MUST BE PRESERVED'
        def race(source, target):
            Path(target).write_bytes(competitor)
            raise FileExistsError(errno.EEXIST, 'exists', str(target))
        with patch.object(delivery.os, 'link', side_effect=race):
            with self.assertRaisesRegex(delivery.DeliveryError, 'aucun ecrasement'):
                delivery.write_delivery(self.root, {'version': 1})
        self.assertEqual(self.final.read_bytes(), competitor)
        self.assert_no_staging()

    def test_fallback_without_hardlinks_is_exclusive(self):
        with patch.object(delivery.os, 'link', side_effect=OSError(errno.EOPNOTSUPP, 'unsupported')):
            delivery.write_delivery(self.root, {'version': 1})
        self.assertEqual(json.loads(self.final.read_text(encoding='utf8'))['version'], 1)
        self.assert_no_staging()

    def test_fallback_concurrent_create_refuses_overwrite(self):
        competitor = b'EXISTING MANIFEST'
        original_open = Path.open
        def race_open(path, mode='r', *args, **kwargs):
            if path == self.final and mode == 'xb':
                path.write_bytes(competitor)
            return original_open(path, mode, *args, **kwargs)
        with patch.object(delivery.os, 'link', side_effect=OSError(errno.EOPNOTSUPP, 'unsupported')):
            with patch.object(Path, 'open', autospec=True, side_effect=race_open):
                with self.assertRaisesRegex(delivery.DeliveryError, 'aucun ecrasement'):
                    delivery.write_delivery(self.root, {'version': 1})
        self.assertEqual(self.final.read_bytes(), competitor)
        self.assert_no_staging()

    def test_fallback_copy_failure_removes_partial_manifest(self):
        with patch.object(delivery.os, 'link', side_effect=OSError(errno.EOPNOTSUPP, 'unsupported')):
            with patch.object(delivery.os, 'fsync', side_effect=[None, OSError(errno.ENOSPC, 'full')]):
                with self.assertRaises(OSError):
                    delivery.write_delivery(self.root, {'version': 1})
        self.assertFalse(self.final.exists())
        self.assert_no_staging()

    def test_fallback_failure_preserves_concurrent_replacement(self):
        # A competitor replaces the exclusive target after it was opened.
        # Failure cleanup must never unlink that competitor's file.
        competitor = b'CONCURRENT MANIFEST MUST SURVIVE'
        original_fsync = delivery.os.fsync
        calls = 0

        def replace_and_fail(fd):
            nonlocal calls
            calls += 1
            if calls == 1:
                return original_fsync(fd)  # fsync of staging file
            self.final.unlink()
            self.final.write_bytes(competitor)
            raise OSError(errno.ENOSPC, 'simulated fallback write failure')

        with patch.object(delivery.os, 'link',
                          side_effect=OSError(errno.EOPNOTSUPP, 'unsupported')):
            with patch.object(delivery.os, 'fsync', side_effect=replace_and_fail):
                with self.assertRaises(OSError):
                    delivery.write_delivery(self.root, {'version': 1})
        self.assertEqual(self.final.read_bytes(), competitor)
        self.assert_no_staging()

    def test_invalid_manifest_does_not_publish(self):
        with self.assertRaises(TypeError):
            delivery.write_delivery(self.root, {'invalid': object()})
        self.assertFalse(self.final.exists())
        self.assert_no_staging()


if __name__ == '__main__':
    unittest.main()
