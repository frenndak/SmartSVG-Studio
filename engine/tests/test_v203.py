"""V20.3 tests: GPU sensor partial failure, policy, ComfyUI integration, no export drift."""
import importlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import numpy as np
import torch
import cv2
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg_v203_tests'
if PKG not in sys.modules:
    pkg=types.ModuleType(PKG);pkg.__path__=[str(ROOT)];sys.modules[PKG]=pkg
budget=importlib.import_module(PKG+'.gpu_budget_v203')
node=importlib.import_module(PKG+'.node_v203')
node_old=importlib.import_module(PKG+'.node_v202')

def scene():
    im=np.full((200,165,3),255,np.uint8)
    cv2.ellipse(im,(82,80),(43,54),0,0,360,(0,0,0),3)
    cv2.line(im,(40,140),(20,198),(0,0,0),3)
    cv2.line(im,(125,140),(140,198),(0,0,0),3)
    return im

def fake_gpu(free=5.,total=8.):
    return {'cuda_disponible':True,'index_gpu':0,
            'vram_libre_globale_bytes':int(free*budget.GIB),
            'vram_physique_bytes':int(total*budget.GIB),
            'pytorch_alloue_bytes':int(.9*budget.GIB),
            'pytorch_reserve_bytes':int(1.2*budget.GIB)}

class FakeCuda:
    def __init__(self, *,fault=None):self.fault=fault
    def is_available(self):return True
    def current_device(self):return 0
    def get_device_properties(self,index):return types.SimpleNamespace(name='Mock 8GB',total_memory=8*budget.GIB)
    def mem_get_info(self,index):return (4*budget.GIB,8*budget.GIB)
    def memory_allocated(self,index):return 2*budget.GIB
    def memory_reserved(self,index):
        if self.fault=='reserve':raise RuntimeError('probe failed')
        return 3*budget.GIB
    def max_memory_allocated(self,index):return 5*budget.GIB

class TestGpuBudget(unittest.TestCase):
    def test_cpu_snapshot(self):
        v=budget.gpu_snapshot(types.SimpleNamespace(cuda=types.SimpleNamespace(is_available=lambda:False)))
        self.assertFalse(v['cuda_disponible']);self.assertEqual(v['raison'],'cuda_indisponible')
    def test_good_snapshot(self):
        x=budget.gpu_snapshot(types.SimpleNamespace(cuda=FakeCuda()))
        self.assertEqual(x['vram_libre_globale_bytes'],4*budget.GIB)
        self.assertEqual(x['pytorch_pic_historique_alloue_bytes'],5*budget.GIB)
        self.assertFalse(x['capteurs_partiels'])
    def test_partial_sensor_does_not_discard_free_vram(self):
        x=budget.gpu_snapshot(types.SimpleNamespace(cuda=FakeCuda(fault='reserve')))
        self.assertTrue(x['capteurs_partiels']);self.assertIn('vram_libre_globale_bytes',x)
        self.assertNotIn('pytorch_reserve_bytes',x)
    def test_broken_driver_data_does_not_crash(self):
        fake=FakeCuda();fake.mem_get_info=lambda _: -1
        d=budget.gpu_snapshot(types.SimpleNamespace(cuda=fake))
        self.assertTrue(d['capteurs_partiels'])
        self.assertNotIn('vram_libre_globale_bytes',d)
    def test_numeric_nan_driver_data_rejected(self):
        fake=FakeCuda();fake.mem_get_info=lambda _: (float('nan'),8*budget.GIB)
        d=budget.gpu_snapshot(types.SimpleNamespace(cuda=fake))
        self.assertTrue(d['capteurs_partiels'])
        self.assertNotIn('vram_libre_globale_bytes',d)
    def test_no_cuda_protected_skips_auto(self):
        x=budget.policy_decision({'cuda_disponible':False},policy='protege',ia='auto')
        self.assertEqual(x['action'],'SAUTER_IA_GARDER_EXPORTS')
    def test_gpu_low_protected_skips_auto(self):
        x=budget.policy_decision(fake_gpu(2.),policy='protege',ia='auto')
        self.assertEqual(x['action'],'SAUTER_IA_GARDER_EXPORTS')
    def test_strict_aborts(self):
        x=budget.policy_decision(fake_gpu(1.),policy='strict',ia='auto')
        self.assertEqual(x['action'],'ABANDON_EXPLICITE')
    def test_forced_ia_not_downgraded(self):
        x=budget.policy_decision({'cuda_disponible':False},policy='protege',ia='forcer')
        self.assertEqual(x['action'],'ABANDON_EXPLICITE')
    def test_diagnostic_mode_only_warns(self):
        x=budget.policy_decision(fake_gpu(.5),policy='diagnostic',ia='auto')
        self.assertEqual(x['action'],'TENTER_IA_AVEC_ALERTE')
    def test_supplied_masks_bypass_gate(self):
        x=budget.policy_decision({'cuda_disponible':False},policy='strict',ia='auto',external_masks=True)
        self.assertEqual(x['action'],'PROCEDER')
    def test_disabled_ia_bypass_gate(self):
        x=budget.policy_decision({'cuda_disponible':False},policy='strict',ia='desactiver')
        self.assertEqual(x['action'],'PROCEDER')
    def test_unknown_gpu_memory_protects(self):
        x=budget.policy_decision({'cuda_disponible':True},policy='protege')
        self.assertEqual(x['reason'] if 'reason' in x else x['raison'],'MEMOIRE_GPU_INCONNUE')
    def test_invalid_thresholds(self):
        for k in [float('nan'),-1,float('inf'),True,17]:
            with self.subTest(k=k):
                with self.assertRaises(ValueError):budget.policy_decision(fake_gpu(),free_min_gib=k)
    def test_snapshot_comparison_not_a_model_peak(self):
        a=fake_gpu(4);b=fake_gpu(3.75);b['pytorch_alloue_bytes']+=200000
        x=budget.compare_snapshots(a,b,budget.time.perf_counter()-0.01,model_was_called=True)
        self.assertTrue(x['appel_modele_interne_signale'])
        self.assertFalse(x['inference_gpu_prouvee']);self.assertFalse(x['pic_vram_de_l_inference_mesure'])
        self.assertEqual(x['delta_pytorch_alloue_bytes'],200000)
    def test_mismatched_devices_not_compared(self):
        a=fake_gpu();b=fake_gpu();b['index_gpu']=1
        x=budget.compare_snapshots(a,b,budget.time.perf_counter())
        self.assertFalse(x['gpu_identique_avant_apres'])
        self.assertNotIn('delta_pytorch_alloue_bytes',x)
    def test_node_registration_backwards_compatible(self):
        self.assertIn('SmartSVGLineArtV202',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGStudioV20Expert',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGLineArtV203',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGGPUPreflightV203',node.NODE_CLASS_MAPPINGS)
    def test_preflight_no_model(self):
        with patch.object(node,'gpu_snapshot',return_value={'cuda_disponible':False}):
            payload=json.loads(node.SmartSVGGPUPreflightV203().run()['result'][0])
        self.assertFalse(payload['modeles_execution'])
        self.assertEqual(payload['garde_fou']['action'],'SAUTER_IA_GARDER_EXPORTS')

class TestNode(unittest.TestCase):
    def setUp(self):
        self.img=torch.from_numpy(scene().astype(np.float32)/255)[None]
    def test_protected_offline_exports_but_no_ia(self):
        with tempfile.TemporaryDirectory() as t,patch.object(node,'gpu_snapshot',return_value={'cuda_disponible':False}):
            result=node.SmartSVGLineArtV203().run(self.img,t,segmentation_ia='auto')
            report=json.loads(result['result'][1]);self.assertEqual(report['profil_gpu_v20_3']['ia_effective_demandee'],'desactiver')
            self.assertFalse(report['analyse']['masque_ia_produit'])
            self.assertTrue(Path(report['fichier_mode_choisi']).is_file())
            self.assertTrue(Path(report['rapport_gpu_enregistre']).is_file())
    def test_strict_raises_without_exports(self):
        with tempfile.TemporaryDirectory() as t,patch.object(node,'gpu_snapshot',return_value={'cuda_disponible':False}):
            with self.assertRaises(RuntimeError):node.SmartSVGLineArtV203().run(self.img,t,politique_gpu='strict')
            self.assertFalse(list(Path(t).iterdir()))
    def test_forcer_raises_without_exports(self):
        with tempfile.TemporaryDirectory() as t,patch.object(node,'gpu_snapshot',return_value={'cuda_disponible':False}):
            with self.assertRaises(RuntimeError):node.SmartSVGLineArtV203().run(self.img,t,segmentation_ia='forcer')
            self.assertFalse(list(Path(t).iterdir()))
    def test_external_mask_allowed_without_gpu_and_ia_original_preserved(self):
        mask=np.zeros((1,200,165),np.float32)
        cv2.ellipse(mask[0],(82,105),(50,82),0,0,360,1,-1)
        with tempfile.TemporaryDirectory() as t,patch.object(node,'gpu_snapshot',return_value={'cuda_disponible':False}):
            result=node.SmartSVGLineArtV203().run(self.img,t,politique_gpu='strict',masques_objets=torch.from_numpy(mask))
            data=json.loads(result['result'][1])
            self.assertTrue(data['analyse']['masque_ia_produit'])
            self.assertEqual(data['profil_gpu_v20_3']['decision_prevol']['raison'],'MASQUES_EXTERNES_PRIORITAIRES')
    def test_identical_historic_cricut_files(self):
        with tempfile.TemporaryDirectory() as t,patch.object(node,'gpu_snapshot',return_value={'cuda_disponible':False}):
            old=node_old.SmartSVGLineArtV202().run(self.img,t,segmentation_ia='desactiver')
            new=node.SmartSVGLineArtV203().run(self.img,t,segmentation_ia='desactiver')
            path_old=Path(json.loads(old['result'][1])['fichier_mode_choisi'])
            path_new=Path(json.loads(new['result'][1])['fichier_mode_choisi'])
            self.assertEqual(path_old.read_bytes(),path_new.read_bytes())
    def test_all_traits_unchanged(self):
        with tempfile.TemporaryDirectory() as t,patch.object(node,'gpu_snapshot',return_value={'cuda_disponible':False}):
            kw={'segmentation_ia':'desactiver','operation_cricut':'decouper_tous_les_traits'}
            old=node_old.SmartSVGLineArtV202().run(self.img,t,**kw)
            new=node.SmartSVGLineArtV203().run(self.img,t,**kw)
            self.assertEqual(Path(json.loads(old['result'][1])['fichier_mode_choisi']).read_bytes(),
                             Path(json.loads(new['result'][1])['fichier_mode_choisi']).read_bytes())
    def test_gpu_report_write_failure_does_not_kill_production(self):
        with tempfile.TemporaryDirectory() as t,patch.object(node,'gpu_snapshot',return_value={'cuda_disponible':False}):
            original_replace=node.os.replace
            def fail_qa_only(src,dst):
                if '.pending_gpu_' in str(src):raise OSError('blocked')
                return original_replace(src,dst)
            with patch.object(node.os,'replace',side_effect=fail_qa_only):
                result=node.SmartSVGLineArtV203().run(self.img,t,segmentation_ia='desactiver')
            d=json.loads(result['result'][1]);self.assertTrue(d['rapport_gpu_enregistre'].startswith('ECHEC_ECRITURE_QA_GPU'))
            self.assertTrue(Path(d['fichier_mode_choisi']).exists())

if __name__=='__main__':unittest.main()
