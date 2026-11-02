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

    def report(self, sheets, *, upstream_status='PRET_POUR_IMPORT_LOCAL'):
        return {
            'dossier': str(self.root),
            'objets': [{'png': str(self.png), 'svg_contour': str(self.svg)}],
            'import_direct_cricut_v218': {
                'statut': upstream_status,
                'objets': [{
                    'fichier_import': str(self.png),
                    'statut': 'PRET_POUR_IMPORT_LOCAL',
                }],
                'planches': sheets,
            },
        }

    def test_tampered_handoff_png_is_not_marked_ready(self):
        # Preflight may have run before a copy was replaced or corrupted.
        altered = self.root / 'altered_import.png'
        altered.write_bytes(b'different valid-looking file bytes')
        report = self.report([])
        report['import_direct_cricut_v218']['objets'][0]['fichier_import'] = str(altered)
        manifest = delivery.delivery_manifest(report)
        self.assertEqual(manifest['statut'], 'REVISIONS_NECESSAIRES')
        self.assertEqual(manifest['png_import_precontroles'], 0)
        self.assertEqual(manifest['objets'][0]['etat'], 'REVISION_PRIORITAIRE')
        self.assertIn('PNG_IMPRESSION_DIFFERENT_DU_PNG_FABRICATION',
                      manifest['objets'][0]['avertissements'])
        self.assertEqual(altered.read_bytes(), b'different valid-looking file bytes')
        self.assertEqual(self.png.read_bytes(), b'synthetic non-empty fixture')

    def test_matching_handoff_png_copy_is_still_ready(self):
        copied = self.root / 'identical_import.png'
        copied.write_bytes(self.png.read_bytes())
        report = self.report([])
        report['import_direct_cricut_v218']['objets'][0]['fichier_import'] = str(copied)
        manifest = delivery.delivery_manifest(report)
        self.assertEqual(manifest['statut'], 'CONTROLE_LOCAL_COMPLET_A_REVISER')
        self.assertEqual(manifest['png_import_precontroles'], 1)
        self.assertEqual(manifest['objets'][0]['avertissements'], [])

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
                report = self.report(sheets)
                if sheets:
                    report['planches'] = [
                        {'statut': 'CREATION_OK', 'fichier': str(self.sheet)},
                    ]
                manifest = delivery.delivery_manifest(report)
                self.assertEqual(manifest['statut'],
                                 'CONTROLE_LOCAL_COMPLET_A_REVISER')
                self.assertEqual(manifest['planches_precontrolees'],
                                 len(sheets))

    def test_failed_or_missing_upstream_batch_status_never_becomes_complete(self):
        # A failed handoff metadata write can leave individually valid PNGs.
        # Delivery must not erase that batch-level warning.
        for upstream in ('PARTIEL', 'A_VERIFIER', None, 'INFORMATION_INDISPONIBLE'):
            with self.subTest(upstream=upstream):
                report = self.report([], upstream_status=upstream)
                manifest = delivery.delivery_manifest(report)
                self.assertEqual(manifest['png_import_precontroles'], 1)
                self.assertEqual(manifest['statut'], 'REVISIONS_NECESSAIRES')
        missing = self.report([])
        del missing['import_direct_cricut_v218']['statut']
        self.assertEqual(delivery.delivery_manifest(missing)['statut'],
                         'REVISIONS_NECESSAIRES')

    def test_explicit_null_imported_sheets_cannot_claim_complete_delivery(self):
        # A truncated upstream report with `planches: null` is not equivalent
        # to a legacy report that never declared a sheet collection.
        with self.assertRaisesRegex(delivery.DeliveryError,
                                    'Collection de planches Cricut'):
            delivery.delivery_manifest(self.report(None))
        legacy = self.report([])
        del legacy['import_direct_cricut_v218']['planches']
        self.assertEqual(delivery.delivery_manifest(legacy)['statut'],
                         'CONTROLE_LOCAL_COMPLET_A_REVISER')

    def test_malformed_sheet_collection_fails_closed(self):
        for sheets in ('not-a-list', [None], [{'statut': 'A_VERIFIER'}, None]):
            with self.subTest(sheets=sheets):
                with self.assertRaisesRegex(delivery.DeliveryError,
                                            'Collection de planches'):
                    delivery.delivery_manifest(self.report(sheets))


    def test_missing_manufactured_sheet_cannot_be_hidden_by_stale_handoff(self):
        # An upstream report still declares a manufactured page, while a
        # stale/truncated handoff claims READY with no pages.
        report = self.report([])
        report['planches'] = [{'statut': 'CREATION_OK', 'fichier': str(self.sheet)}]
        manifest = delivery.delivery_manifest(report)
        self.assertEqual(manifest['statut'], 'REVISIONS_NECESSAIRES')
        self.assertEqual(manifest['planches_precontrolees'], 0)
        self.assertIn('PLANCHES_FABRIQUEES_NON_RECONCILIEES',
                      manifest['avertissements'])

    def test_imported_sheet_without_manufactured_provenance_fails_closed(self):
        # A stale or forged handoff must not invent a sheet absent from the
        # manufacturing report, even when its local PNG is readable.
        report = self.report([
            {'statut': 'PRET_POUR_IMPORT_LOCAL',
             'fichier_import': str(self.sheet)},
        ])
        original = self.sheet.read_bytes()
        manifest = delivery.delivery_manifest(report)
        self.assertEqual(manifest['planches_precontrolees'], 1)
        self.assertEqual(manifest['statut'], 'REVISIONS_NECESSAIRES')
        self.assertIn('PLANCHES_FABRIQUEES_NON_RECONCILIEES',
                      manifest['avertissements'])
        self.assertEqual(self.sheet.read_bytes(), original)

    def test_manufactured_and_imported_sheets_are_reconciled(self):
        report = self.report([
            {'statut': 'PRET_POUR_IMPORT_LOCAL', 'fichier_import': str(self.sheet)},
        ])
        report['planches_cricut'] = [
            {'statut': 'CREATION_OK', 'fichier': str(self.sheet)},
        ]
        manifest = delivery.delivery_manifest(report)
        self.assertEqual(manifest['statut'], 'CONTROLE_LOCAL_COMPLET_A_REVISER')
        self.assertEqual(manifest['planches_precontrolees'], 1)
        self.assertEqual(manifest['avertissements'], [])

    def test_equal_sheet_counts_do_not_hide_wrong_sheet_bytes(self):
        # A stale handoff can repeat one page while omitting another; the
        # counts and per-page preflight statuses still appear correct.
        original = self.root / 'manufactured_other.png'
        original.write_bytes(b'other manufactured sheet bytes')
        report = self.report([
            {'statut': 'PRET_POUR_IMPORT_LOCAL', 'fichier_import': str(self.sheet)},
        ])
        report['planches'] = [{'statut': 'CREATION_OK', 'fichier': str(original)}]
        manifest = delivery.delivery_manifest(report)
        self.assertEqual(manifest['planches_precontrolees'], 1)
        self.assertEqual(manifest['statut'], 'REVISIONS_NECESSAIRES')
        self.assertIn('PLANCHES_FABRIQUEES_NON_RECONCILIEES',
                      manifest['avertissements'])
        self.assertEqual(original.read_bytes(), b'other manufactured sheet bytes')

    def test_sheet_copy_with_identical_bytes_is_reconciled(self):
        copied = self.root / 'copied_sheet.png'
        copied.write_bytes(self.sheet.read_bytes())
        report = self.report([
            {'statut': 'PRET_POUR_IMPORT_LOCAL', 'fichier_import': str(copied)},
        ])
        report['planches_cricut'] = [
            {'statut': 'CREATION_OK', 'fichier': str(self.sheet)},
        ]
        manifest = delivery.delivery_manifest(report)
        self.assertEqual(manifest['statut'], 'CONTROLE_LOCAL_COMPLET_A_REVISER')
        self.assertEqual(manifest['avertissements'], [])

    def test_missing_manufactured_sheet_cannot_be_claimed_ready(self):
        report = self.report([
            {'statut': 'PRET_POUR_IMPORT_LOCAL', 'fichier_import': str(self.sheet)},
        ])
        report['planches'] = [
            {'statut': 'CREATION_OK', 'fichier': str(self.root / 'missing_source.png')},
        ]
        manifest = delivery.delivery_manifest(report)
        self.assertEqual(manifest['statut'], 'REVISIONS_NECESSAIRES')
        self.assertIn('PLANCHES_FABRIQUEES_NON_RECONCILIEES',
                      manifest['avertissements'])

    def test_falsy_malformed_manufactured_sheets_never_become_complete(self):
        # An explicitly declared empty mapping/string/None must not be treated
        # as an absent optional collection by the truthy fallback.
        for key in ('planches', 'planches_cricut'):
            for invalid in ({}, '', None):
                with self.subTest(key=key, invalid=repr(invalid)):
                    report = self.report([])
                    report[key] = invalid
                    with self.assertRaisesRegex(delivery.DeliveryError,
                                                'Collection de planches fabriquees'):
                        delivery.delivery_manifest(report)
        # Validate both aliases, even if a valid empty list takes precedence.
        report = self.report([])
        report['planches'] = []
        report['planches_cricut'] = {}
        with self.assertRaisesRegex(delivery.DeliveryError,
                                    'Collection de planches fabriquees'):
            delivery.delivery_manifest(report)

    def test_conflicting_manufactured_sheet_aliases_fail_closed(self):
        # Both legacy aliases are present; a matching first alias must not
        # conceal a different second source with the same number of sheets.
        other=self.root/'conflicting_sheet.png'
        other.write_bytes(b'conflicting manufactured sheet')
        report=self.report([
            {'statut':'PRET_POUR_IMPORT_LOCAL','fichier_import':str(self.sheet)},
        ])
        report['planches']=[{'statut':'CREATION_OK','fichier':str(self.sheet)}]
        report['planches_cricut']=[{'statut':'CREATION_OK','fichier':str(other)}]
        manifest=delivery.delivery_manifest(report)
        self.assertEqual(manifest['statut'],'REVISIONS_NECESSAIRES')
        self.assertIn('PLANCHES_FABRIQUEES_NON_RECONCILIEES',
                      manifest['avertissements'])
        self.assertEqual(self.sheet.read_bytes(),b'synthetic non-empty fixture')
        self.assertEqual(other.read_bytes(),b'conflicting manufactured sheet')

    def test_matching_manufactured_sheet_aliases_remain_compatible(self):
        copy=self.root/'equivalent_sheet.png'
        copy.write_bytes(self.sheet.read_bytes())
        report=self.report([
            {'statut':'PRET_POUR_IMPORT_LOCAL','fichier_import':str(self.sheet)},
        ])
        report['planches']=[{'statut':'CREATION_OK','fichier':str(self.sheet)}]
        report['planches_cricut']=[{'statut':'CREATION_OK','fichier':str(copy)}]
        manifest=delivery.delivery_manifest(report)
        self.assertEqual(manifest['statut'],'CONTROLE_LOCAL_COMPLET_A_REVISER')
        self.assertEqual(manifest['avertissements'],[])

    def test_mismatched_manufactured_sheet_alias_counts_fail_closed(self):
        report=self.report([
            {'statut':'PRET_POUR_IMPORT_LOCAL','fichier_import':str(self.sheet)},
        ])
        report['planches']=[{'statut':'CREATION_OK','fichier':str(self.sheet)}]
        report['planches_cricut']=[
            {'statut':'CREATION_OK','fichier':str(self.sheet)},
            {'statut':'CREATION_OK','fichier':str(self.sheet)},
        ]
        manifest=delivery.delivery_manifest(report)
        self.assertEqual(manifest['statut'],'REVISIONS_NECESSAIRES')
        self.assertIn('PLANCHES_FABRIQUEES_NON_RECONCILIEES',
                      manifest['avertissements'])

    def test_empty_vs_nonempty_manufactured_aliases_fail_closed(self):
        # A truthy-only alias comparison previously accepted either ordering:
        # one explicit [] contradicted a real manufactured sheet, yet the
        # other alias matched the imported sheet and was marked complete.
        for empty_key in ('planches', 'planches_cricut'):
            with self.subTest(empty_key=empty_key):
                report=self.report([
                    {'statut':'PRET_POUR_IMPORT_LOCAL',
                     'fichier_import':str(self.sheet)},
                ])
                report['planches']=[
                    {'statut':'CREATION_OK','fichier':str(self.sheet)},
                ]
                report['planches_cricut']=[
                    {'statut':'CREATION_OK','fichier':str(self.sheet)},
                ]
                report[empty_key]=[]
                manifest=delivery.delivery_manifest(report)
                self.assertEqual(manifest['statut'],'REVISIONS_NECESSAIRES')
                self.assertIn('PLANCHES_FABRIQUEES_NON_RECONCILIEES',
                              manifest['avertissements'])
                self.assertEqual(self.sheet.read_bytes(),
                                 b'synthetic non-empty fixture')

    def test_two_explicitly_empty_manufactured_aliases_remain_compatible(self):
        report=self.report([])
        report['planches']=[]
        report['planches_cricut']=[]
        manifest=delivery.delivery_manifest(report)
        self.assertEqual(manifest['statut'],'CONTROLE_LOCAL_COMPLET_A_REVISER')
        self.assertEqual(manifest['avertissements'],[])

    def test_stale_preflight_cannot_override_failed_manufacturing_status(self):
        # The PNG remains byte-identical, but upstream manufacturing rejected it.
        for status in ('NB_DECOUPES_INCOHERENT_VERIFIER',
                       'TAILLE_POTENTIELLEMENT_TROP_GRANDE_DESIGN_SPACE',
                       None):
            with self.subTest(status=status):
                report = self.report([
                    {'statut': 'PRET_POUR_IMPORT_LOCAL',
                     'fichier_import': str(self.sheet)},
                ])
                report['planches'] = [
                    {'statut': status, 'fichier': str(self.sheet)},
                ]
                original = self.sheet.read_bytes()
                manifest = delivery.delivery_manifest(report)
                self.assertEqual(manifest['statut'], 'REVISIONS_NECESSAIRES')
                self.assertIn('PLANCHES_FABRIQUEES_NON_RECONCILIEES',
                              manifest['avertissements'])
                self.assertEqual(self.sheet.read_bytes(), original)

    def test_second_alias_rejected_status_is_not_hidden_by_matching_bytes(self):
        # Two aliases with identical bytes must not conceal a rejected sheet.
        report = self.report([
            {'statut': 'PRET_POUR_IMPORT_LOCAL',
             'fichier_import': str(self.sheet)},
        ])
        report['planches'] = [
            {'statut': 'CREATION_OK', 'fichier': str(self.sheet)},
        ]
        report['planches_cricut'] = [
            {'statut': 'NB_DECOUPES_INCOHERENT_A_VERIFIER',
             'fichier': str(self.sheet)},
        ]
        manifest = delivery.delivery_manifest(report)
        self.assertEqual(manifest['statut'], 'REVISIONS_NECESSAIRES')
        self.assertIn('PLANCHES_FABRIQUEES_NON_RECONCILIEES',
                      manifest['avertissements'])

    def test_malformed_manufactured_sheet_collection_fails_closed(self):
        report = self.report([])
        report['planches'] = {'unexpected': 'mapping'}
        with self.assertRaisesRegex(delivery.DeliveryError,
                                    'Collection de planches fabriquees'):
            delivery.delivery_manifest(report)


if __name__ == '__main__':
    unittest.main()
