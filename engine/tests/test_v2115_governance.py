"""V21.15 G0/G1.1 preflight, negative cases and V19.2 compatibility repair."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from smartsvg_governance.corpus import make_manifest,make_review_template,build_fixtures,sha
from smartsvg_governance.inventory import (inventory,read_graph,_warn_graph,registry_from_root,write_inventory)

ROOT=Path(__file__).resolve().parents[1]


class G0PreflightTests(unittest.TestCase):
    def test_baseline_engine_unchanged_except_entrypoint(self):
        old=json.loads((ROOT/'INSTALLATION_MANIFEST_V21_14_1.json').read_text('utf-8'))['fichiers_sha256']
        changed=[name for name,digest in old.items() if not (ROOT/name).is_file() or sha(ROOT/name)!=digest]
        self.assertEqual(changed,['__init__.py',
            'web/js/smartsvg_ui_model_v2151.mjs', 'web/js/smartsvg_ui_v2151.js'])
        # Only the entrypoint and the explicitly versioned UI bridge can differ
        # from B0. All legacy engines/workflows remain byte-identical.

    def test_corpus_without_private_files_is_honestly_blocked(self):
        with tempfile.TemporaryDirectory() as folder:
            d=Path(folder); report=make_manifest(None,d/'fixtures')
            self.assertEqual(len(report['real_cases']),9)
            self.assertEqual(len(report['synthetic_cases']),2)
            self.assertEqual(report['gate']['g0_2'],'BLOCKED_SOURCES')
            self.assertTrue(report['gate']['G0_to_G1'].startswith('NO_GO'))
            self.assertEqual(len(make_review_template(report)['reviews']),9)
            self.assertTrue(all(r['licensing'].startswith('user_supplied') for r in report['real_cases']))

    def test_synthetic_truth_and_negative_control(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); rows=build_fixtures(root)
            for row in rows:
                self.assertEqual(sha(root/row['source']),row['source_sha256'])
                self.assertEqual(sha(root/row['gt_mask']),row['mask_sha256'])
            ring=Image.open(root/'R-01_mask.png')
            self.assertEqual(ring.getpixel((80,55)),0)
            self.assertEqual(ring.getpixel((80,20)),255)
            self.assertEqual(ring.getpixel((0,0)),0)
            rejection=Image.open(root/'R-02_mask.png')
            self.assertIsNone(rejection.getbbox())

    def test_corpus_does_not_redistribute_originals(self):
        roots=[p.name for p in (ROOT/'governance'/'fixtures').iterdir()]
        self.assertTrue(roots)
        self.assertEqual(set(roots),{'R-01.png','R-01_mask.png','R-02.png','R-02_mask.png'})


class G11PreInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mapping,_=registry_from_root(ROOT)

    def test_inventory_and_registrations(self):
        result=inventory(ROOT)
        self.assertEqual(result['workflow_count'],186)
        self.assertEqual(result['workflow_parsed'],186)
        # V21.15.4 registers one new optional inspector; historic 99 remain.
        self.assertEqual(result['node_registration_count'],100)
        self.assertIn('SmartSVGChooseSubjectV21154',self.mapping)
        self.assertIn('SmartSVGExpressV21152',self.mapping)
        self.assertEqual(result['unresolved_types'],[])
        self.assertEqual(result['warnings'],[])

    def test_historical_nodes_kept_by_identity(self):
        self.assertIn('SmartSVGStudioV192Expert',self.mapping)
        self.assertIn('SmartSVGStudioV192Express',self.mapping)
        self.assertEqual(self.mapping['SmartSVGStudioV192Express'].FUNCTION,'execute_express')
        self.assertEqual(set(self.mapping['SmartSVGStudioV192Express'].INPUT_TYPES()['required']),
                         set(['image','dossier_sortie','largeur_planche_mm','type_fichier',
                              'ia_locale','segmentation_objets','profil_segmentation']))

    def test_legacy_express_setting_is_forwarded(self):
        from unittest.mock import patch
        node=self.mapping['SmartSVGStudioV192Express']()
        with patch.object(type(node),'execute',return_value=('ok','dry-run')) as fn:
            result=node.execute_express(None,'temporary',ia_locale='desactiver')
            self.assertEqual(result,('ok','dry-run'))
            self.assertEqual(fn.call_args.kwargs['ia_locale'],'desactiver')

    def test_every_serialized_known_node_has_matching_ports(self):
        for path in (ROOT/'example_workflows').glob('*.json'):
            graph=read_graph(path)
            for node in graph['nodes']:
                cls=self.mapping.get(node['type'])
                if cls is None:continue
                available=cls.INPUT_TYPES()
                fields=list(available.get('required',{}))+list(available.get('optional',{}))
                with self.subTest(workflow=path.name,node=node['type']):
                    actual={p['name'] for p in node.get('inputs',[])}
                    self.assertTrue(set(available.get('required',{})) <= actual)
                    self.assertTrue(actual <= set(fields))
                    self.assertEqual([o['type'] for o in node.get('outputs',[])],list(cls.RETURN_TYPES))

    def test_malformed_and_unknown_types_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'bad.json'
            p.write_text(json.dumps({'nodes':[],'links':[]}),encoding='utf-8')
            self.assertEqual(read_graph(p)['nodes'],[])
            p.write_text('{not json',encoding='utf-8')
            with self.assertRaises(json.JSONDecodeError):read_graph(p)
            warnings=_warn_graph({'nodes':[{'id':1,'type':'MaliciousUnknown'}], 'links':[[1,1,0,999,0,'MASK']]},set(self.mapping))
            self.assertTrue(any('TYPE_INCONNU' in item for item in warnings))
            self.assertIn('LIEN_NOEUD_ABSENT',warnings)
            p.unlink()
            try:
                p.symlink_to(ROOT/'README.md')
            except (OSError, NotImplementedError):
                return  # Windows without developer-mode symlink privileges
            with self.assertRaises(ValueError):read_graph(p)

    def test_outputs_generated_without_mutating_workflows(self):
        with tempfile.TemporaryDirectory() as folder:
            w=ROOT/'example_workflows/SmartSVG_Studio_V19_2_Express.json'
            before=hashlib.sha256(w.read_bytes()).digest()
            report=write_inventory(ROOT,Path(folder))
            self.assertEqual(report['workflow_count'],186)
            for name in ('workflow_inventory.csv','node_inventory.csv','compatibility_map.md','inventory_result.json'):
                self.assertTrue((Path(folder)/name).is_file())
            self.assertEqual(before,hashlib.sha256(w.read_bytes()).digest())

if __name__=='__main__':unittest.main()
