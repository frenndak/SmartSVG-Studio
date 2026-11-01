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

    def test_no_hardlinks_fails_closed_without_partial_manifest(self):
        # A fallback copy into final would expose incomplete JSON before fsync.
        with patch.object(delivery.os, 'link',
                          side_effect=OSError(errno.EOPNOTSUPP, 'unsupported')):
            with self.assertRaisesRegex(delivery.DeliveryError, 'Publication atomique impossible'):
                delivery.write_delivery(self.root, {'version': 1})
        self.assertFalse(self.final.exists())
        self.assert_no_staging()

    def test_hardlink_failure_preserves_concurrent_manifest(self):
        competitor = b'CONCURRENT MANIFEST MUST SURVIVE'
        def race_link(source, target):
            Path(target).write_bytes(competitor)
            raise OSError(errno.EACCES, 'hardlink denied')
        with patch.object(delivery.os, 'link', side_effect=race_link):
            with self.assertRaisesRegex(delivery.DeliveryError, 'Publication atomique impossible'):
                delivery.write_delivery(self.root, {'version': 1})
        self.assertEqual(self.final.read_bytes(), competitor)
        self.assert_no_staging()

    def test_invalid_manifest_does_not_publish(self):
        with self.assertRaises(TypeError):
            delivery.write_delivery(self.root, {'invalid': object()})
        self.assertFalse(self.final.exists())
        self.assert_no_staging()



class TestDeliveryManifestSheetStatusG34(unittest.TestCase):
    """A complete delivery requires every requested sheet to pass preflight."""

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.png = self.root / 'sticker.png'
        self.svg = self.root / 'contour.svg'
        self.sheet = self.root / 'sheet.png'
        for path in (self.png, self.svg, self.sheet):
            path.write_bytes(b'synthetic non-empty fixture')

    def report(self, sheets):
        return {
            'dossier': str(self.root),
            'objets': [{'png': str(self.png), 'svg_contour': str(self.svg)}],
            'import_direct_cricut_v218': {
                'objets': [{
                    'fichier_import': str(self.png),
                    'statut': 'PRET_POUR_IMPORT_LOCAL',
                }],
                'planches': sheets,
            },
        }

    def test_failed_sheet_does_not_mark_complete_delivery(self):
        manifest = delivery.delivery_manifest(self.report([
            {'statut': 'A_VERIFIER', 'fichier_import': str(self.sheet)},
        ]))
        self.assertEqual(manifest['png_import_precontroles'], 1)
        self.assertEqual(manifest['planches_precontrolees'], 0)
        self.assertEqual(manifest['statut'], 'REVISIONS_NECESSAIRES')

    def test_missing_requested_sheet_does_not_mark_complete_delivery(self):
        manifest = delivery.delivery_manifest(self.report([
            {'statut': 'PRET_POUR_IMPORT_LOCAL',
             'fichier_import': str(self.root / 'missing.png')},
        ]))
        self.assertEqual(manifest['statut'], 'REVISIONS_NECESSAIRES')
        self.assertEqual(manifest['planches_precontrolees'], 0)

    def test_all_valid_sheets_and_no_sheet_request_are_complete(self):
        for sheets in (
            [],
            [{'statut': 'PRET_POUR_IMPORT_LOCAL',
              'fichier_import': str(self.sheet)}],
        ):
            with self.subTest(sheets=sheets):
                manifest = delivery.delivery_manifest(self.report(sheets))
                self.assertEqual(manifest['statut'],
                                 'CONTROLE_LOCAL_COMPLET_A_REVISER')
                self.assertEqual(manifest['planches_precontrolees'],
                                 len(sheets))

    def test_malformed_sheet_collection_fails_closed(self):
        for sheets in ('not-a-list', [None], [{'statut': 'A_VERIFIER'}, None]):
            with self.subTest(sheets=sheets):
                with self.assertRaisesRegex(delivery.DeliveryError,
                                            'Collection de planches'):
                    delivery.delivery_manifest(self.report(sheets))


if __name__ == '__main__':
    unittest.main()
