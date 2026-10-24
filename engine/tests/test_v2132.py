"""V21.3.2 UX and safe diagnostics; no GPU or model is required."""
from __future__ import annotations
import importlib, json, sys, types, unittest
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1]
if 'sv2132test' not in sys.modules:
    pkg=types.ModuleType('sv2132test');pkg.__path__=[str(ROOT)];sys.modules['sv2132test']=pkg
node=importlib.import_module('sv2132test.node_v2132')
diag=importlib.import_module('sv2132test.diagnostic_v2132')

class FakeCuda:
    def __init__(self,available,free=2*1024**3,total=8*1024**3):
        self.available=available;self.free=free;self.total=total
    def is_available(self):return self.available
    def get_device_name(self):return 'GPU TEST'
    def mem_get_info(self):return self.free,self.total

class AuditUX(unittest.TestCase):
    def test_current_and_legacy_registered(self):
        self.assertIn('SmartSVGInstancesV2131',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGExpressV2131',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGExpressV2132',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGDiagnosticV2132',node.NODE_CLASS_MAPPINGS)
    def test_legacy_name_and_current_name_distinct(self):
        self.assertTrue(node.NODE_DISPLAY_NAME_MAPPINGS['SmartSVGExpressV2131'].startswith('Ancien'))
        self.assertTrue(node.NODE_DISPLAY_NAME_MAPPINGS['SmartSVGExpressV2132'].startswith('01'))
    def test_express_ports_and_widgets_unchanged(self):
        old=node.SmartSVGExpressV2131.INPUT_TYPES()
        new=node.SmartSVGExpressV2132.INPUT_TYPES()
        self.assertEqual(tuple(old['required']),tuple(new['required']))
        self.assertEqual(tuple(old['optional']),tuple(new['optional']))
        self.assertEqual(node.SmartSVGExpressV2132.RETURN_TYPES,node.SmartSVGExpressV2131.RETURN_TYPES)
    def test_all_express_settings_have_tooltips(self):
        spec=node.SmartSVGExpressV2132.INPUT_TYPES()
        self.assertEqual(len(spec['required']),6)
        self.assertTrue(all(v[1]['tooltip'] for k,v in spec['required'].items() if k!='image'))
        self.assertIn('masques_objets',spec['optional'])
    def test_original_specs_not_mutated(self):
        node.SmartSVGExpressV2132.INPUT_TYPES()
        self.assertNotIn('tooltip',node.SmartSVGExpressV2131.INPUT_TYPES()['required']['projet'][1])
    def test_instances_settings_have_tooltips(self):
        inp=node.SmartSVGInstancesV2132.INPUT_TYPES()['required']
        self.assertEqual(len(inp),5)
        self.assertTrue(all(x[1]['tooltip'] for x in inp.values()))
    def test_external_mask_vs_disabled_internal_ia_clarity(self):
        report={'nombre_objets_exportes':3,'controle_v212':{'alertes':{'CHEVAUCHEMENT':2}}}
        txt=node.readable_summary(report,'Desactivee',True,'original')
        self.assertIn('masques branches',txt)
        self.assertIn('2 alerte(s)',txt)
        self.assertIn('Cricut Design Space',txt)
    def test_no_mask_not_claimed_ai(self):
        txt=node.readable_summary({'nombre_objets_exportes':1},'Desactivee',False,'')
        self.assertIn('aucun masque fourni',txt)
    def test_diagnostic_missing_all(self):
        status=diag.diagnostics({},types.SimpleNamespace(cuda=FakeCuda(False)))
        self.assertEqual(status['cuda'],'INDISPONIBLE')
        self.assertFalse(status['modeles_poids_charges_et_testes'])
        self.assertNotEqual(status['sam2_noeud'],'INTERFACE_COMPATIBLE')
        self.assertFalse(status['validation_cricut_reelle'])
    def test_diagnostic_no_registry_no_torch(self):
        d=diag.diagnostics(None,None)
        self.assertEqual(d['florence_noeud'],'ABSENT')
        self.assertEqual(d['cuda'],'NON_VERIFIE')
    def test_diagnostic_partial_cuda_failure(self):
        class BadCuda(FakeCuda):
            def mem_get_info(self):raise RuntimeError('read error')
        d=diag.diagnostics({},types.SimpleNamespace(cuda=BadCuda(True)))
        self.assertEqual(d['cuda'],'DISPONIBLE')
        self.assertIsNone(d['vram_libre_gio'])
        self.assertIn('MESURE_VRAM_INDISPONIBLE',d['avertissements'])
    def test_diagnostic_valid_cuda_memory(self):
        d=diag.diagnostics({},types.SimpleNamespace(cuda=FakeCuda(True)))
        self.assertEqual(d['vram_libre_gio'],2)
        self.assertEqual(d['vram_totale_gio'],8)
    def test_diagnostic_node_does_not_execute_model(self):
        fake_nodes=types.ModuleType('nodes');fake_nodes.NODE_CLASS_MAPPINGS={}
        fake_torch=types.ModuleType('torch');fake_torch.cuda=FakeCuda(False)
        with patch.dict(sys.modules,{'nodes':fake_nodes,'torch':fake_torch}):
            out=node.SmartSVGDiagnosticV2132().run()
        self.assertIn('GPU',out['result'][0]);self.assertFalse(json.loads(out['result'][1])['detourage_ia_execute'])
    def test_workflows_use_new_nodes_and_valid_ports(self):
        files=sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_3_2_*.json'))
        self.assertEqual(len(files),8)
        for f in files:
            a=json.loads(f.read_text(encoding='utf8'))
            known={n['id']:n for n in a['nodes']}
            self.assertEqual(len(known),len(a['nodes']))
            for n in a['nodes']:
                if n['type'].startswith('SmartSVG'):
                    cls=node.NODE_CLASS_MAPPINGS[n['type']]
                    inputs=cls.INPUT_TYPES()
                    self.assertEqual([i['name'] for i in n['inputs']],list(inputs['required'])+list(inputs.get('optional',{})))
                    self.assertEqual([o['type'] for o in n['outputs']],list(cls.RETURN_TYPES))
            for link in a['links']:
                self.assertIn(link[1],known);self.assertIn(link[3],known)
    def test_diagnostic_has_no_input(self):
        self.assertEqual(node.SmartSVGDiagnosticV2132.INPUT_TYPES(),{'required':{}})
    def test_model_status_not_proof_weights(self):
        class Flor:
            @classmethod
            def INPUT_TYPES(cls):return {'required':{'model_name':None,'task':None,'image':None}}
        status=diag.diagnostics({'AILab_Florence2':Flor},None)
        self.assertEqual(status['florence_noeud'],'INTERFACE_PRESENTE')
        self.assertFalse(status['modeles_poids_charges_et_testes'])

if __name__=='__main__':unittest.main()
