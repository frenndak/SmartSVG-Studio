"""Regression + adversarial tests of non-destructive quality controls."""
import importlib
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import cv2
import numpy as np
import torch
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]; PKG='smartsvg_v204_tests'
if PKG not in sys.modules:
    p=types.ModuleType(PKG);p.__path__=[str(ROOT)];sys.modules[PKG]=p
q=importlib.import_module(PKG+'.mask_quality_v204')
node=importlib.import_module(PKG+'.node_v204')
legacy=importlib.import_module(PKG+'.node_v203')

def ell(h=128,w=112):
    m=np.zeros((h,w),np.float32);cv2.ellipse(m,(w//2,h//2),(25,36),0,0,360,1,-1)
    return m

def scene():
    a=np.full((230,180,3),255,np.uint8)
    cv2.ellipse(a,(90,85),(40,57),0,0,360,(0,0,0),3)
    cv2.line(a,(50,145),(25,225),(0,0,0),3)
    cv2.line(a,(130,145),(155,225),(0,0,0),3)
    return torch.from_numpy(a.astype('float32')/255)[None]

class TestMaskQA(unittest.TestCase):
    def test_empty(self):
        x=q.analyze_mask(np.zeros((60,60),np.float32));self.assertEqual(x['verdict'],'RISQUE_ELEVE')
        self.assertIn('MASQUE_VIDE',x['signaux'])
    def test_integer_unit_mask(self):
        m=np.array([[0,1],[1,0]],dtype=np.uint8)
        self.assertEqual(int(q.normalize_masks(m).sum()),2)
    def test_binary_255_mask(self):
        m=np.array([[0,255],[255,0]],dtype=np.uint8)
        self.assertEqual(int(q.normalize_masks(m).sum()),2)
    def test_float_mask_01(self):
        x=q.normalize_masks(np.array([[0,.2],[.5,1.]],np.float32));self.assertAlmostEqual(float(x[0,0,1]),.2)
    def test_invalid_float_range(self):
        with self.assertRaises(q.QualityError):q.normalize_masks(np.array([[0,255.]],np.float32))
    def test_invalid_negative(self):
        with self.assertRaises(q.QualityError):q.normalize_masks(np.array([[-1,0]],np.int16))
    def test_nan(self):
        with self.assertRaises(q.QualityError):q.normalize_masks(np.array([[float('nan')]],np.float32))
    def test_shape(self):
        with self.assertRaises(q.QualityError):q.normalize_masks(np.zeros((1,2,3,4),np.float32))
    def test_memory_budget_before_gpu_cpu_transfer(self):
        class Huge:
            shape=(16,5000,5000)
            def detach(self):raise AssertionError('MUST NOT COPY')
        with self.assertRaises(q.QualityError):q.normalize_masks(Huge())
    def test_nonmatching_dimensions(self):
        with self.assertRaises(q.QualityError):q.normalize_masks(np.zeros((12,13),np.uint8),height=13)
    def test_ordinary_unverified(self):
        x=q.analyze_mask(ell());self.assertEqual(x['verdict'],'A_VERIFIER')
        self.assertFalse(x['decoupe_physique_validee'])
    def test_border_contact(self):
        m=ell();m[:2,50:60]=1
        x=q.analyze_mask(m);self.assertIn('SILHOUETTE_TOUCHE_BORD_IMAGE',x['signaux'])
    def test_big_mask(self):
        x=q.analyze_mask(np.ones((40,40),np.float32));self.assertIn('SUJET_OCCUPE_PRESQUE_TOUTE_IMAGE',x['signaux'])
    def test_two_large_islands(self):
        m=ell();m[3:26,3:26]=1
        x=q.analyze_mask(m);self.assertIn('PLUSIEURS_ILOTS_IMPORTANTS',x['signaux'])
    def test_holes(self):
        m=ell();m[60:70,40:52]=0
        x=q.analyze_mask(m);self.assertGreaterEqual(x['mesures']['trous_internes_detectes'],1)
    def test_ink_outside(self):
        m=ell();ink=np.full(m.shape,255,np.uint8)
        x=q.analyze_mask(m,ink);self.assertIn('PLUS_DE_35_PCT_TRAITS_HORS_SILHOUETTE',x['signaux'])
    def test_no_ink(self):
        x=q.analyze_mask(ell(),np.zeros(ell().shape,np.uint8));self.assertEqual(x['mesures']['traits_perdus_pct'],0)
    def test_unaligned_ink(self):
        with self.assertRaises(q.QualityError):q.analyze_mask(ell(),np.zeros((5,5),np.uint8))
    def test_overlay(self):
        img=q.draw_overlay(ell(),np.full(ell().shape,255,np.uint8));self.assertEqual(img.shape,(128,112,3))
        self.assertTrue(np.any(np.all(img==np.array([210,40,195]),axis=2)))
    def test_atomic_json(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'a'/'report.json';q.atomic_json(p,{'a':1})
            self.assertEqual(json.loads(p.read_text())['a'],1)
            self.assertFalse(list(p.parent.glob('.pending*')))
    def test_atomic_symlink(self):
        with tempfile.TemporaryDirectory() as t:
            a=Path(t)/'real';a.mkdir();b=Path(t)/'link';b.symlink_to(a,target_is_directory=True)
            with self.assertRaises(q.QualityError):q.atomic_json(b/'bad.json',{'a':1})
    def test_missing_model_mask(self):
        with tempfile.TemporaryDirectory() as t:
            data,report=q.audit_output_root(t)
            self.assertIsNone(data);self.assertEqual(report['verdict'],'AUCUN_CONTOUR_IA')
    def test_manifest_old_nodes(self):
        for key in ('SmartSVGLineArtV203','SmartSVGLineArtV202','SmartSVGStudioV20Expert'):
            self.assertIn(key,node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGLineArtV204',node.NODE_CLASS_MAPPINGS)
    def test_batch_reversed_object_order_is_audited_not_changed(self):
        a=ell();b=np.flip(a,axis=1).copy();b[:,:15]=1
        batch=np.stack([b,a])
        report=q.analyze_batch(batch)
        self.assertEqual(report['nombre_masques'],2)
        self.assertTrue(report['aucun_masque_modifie'])
        self.assertEqual(report['par_masque'][0]['index_masque'],0)
    def test_batch_overlap(self):
        a=ell();b=np.roll(a,20,axis=1)
        report=q.analyze_batch(np.stack([a,b]))
        self.assertGreater(report['paires_avec_recouvrement'][0]['pixels_partages'],0)
    def test_batch_nonoverlap(self):
        a=np.zeros((90,110),np.float32);b=a.copy()
        a[5:20,5:20]=1;b[45:60,70:90]=1
        self.assertFalse(q.analyze_batch(np.stack([a,b]))['paires_avec_recouvrement'])
    def test_quality_node_preserves_tensor_unchanged(self):
        mask=torch.from_numpy(ell()[None].copy());out=node.SmartSVGMaskQualityV204().run(mask)
        self.assertIs(out['result'][0],mask)
        self.assertTrue(json.loads(out['result'][1])['aucun_masque_modifie'])
    def test_batch_rejects_nan(self):
        a=np.zeros((2,30,30),np.float32);a[0,0,0]=float('nan')
        with self.assertRaises(q.QualityError):q.analyze_batch(a)
    def test_control_option_declared(self):
        a=node.SmartSVGLineArtV204.INPUT_TYPES()['required']
        self.assertIn('controle_contours',a);self.assertIn('politique_gpu',a)

class TestFlow(unittest.TestCase):
    def setUp(self):self.image=scene()
    def test_without_mask_preserves_legacy_file(self):
        with tempfile.TemporaryDirectory() as t, patch.object(legacy,'gpu_snapshot',return_value={'cuda_disponible':False}):
            kw={'segmentation_ia':'desactiver','operation_cricut':'decouper_tous_les_traits'}
            a=legacy.SmartSVGLineArtV203().run(self.image,t,**kw)
            b=node.SmartSVGLineArtV204().run(self.image,t,**kw)
            ra=json.loads(a['result'][1]);rb=json.loads(b['result'][1])
            pa=Path(ra['fichier_mode_choisi']);pb=Path(rb['fichier_mode_choisi'])
            self.assertEqual(hashlib.sha256(pa.read_bytes()).digest(),hashlib.sha256(pb.read_bytes()).digest())
            self.assertEqual(rb['qualite_masque_v20_4']['statut'],'AUCUN_MASQUE_IA')
    def test_supplied_mask_produces_separate_diagnostic(self):
        mask=np.zeros((1,230,180),np.float32);cv2.ellipse(mask[0],(90,115),(50,80),0,0,360,1,-1)
        with tempfile.TemporaryDirectory() as t, patch.object(legacy,'gpu_snapshot',return_value={'cuda_disponible':False}):
            old=legacy.SmartSVGLineArtV203().run(self.image,t,masques_objets=torch.from_numpy(mask))
            new=node.SmartSVGLineArtV204().run(self.image,t,masques_objets=torch.from_numpy(mask))
            a=json.loads(old['result'][1]);b=json.loads(new['result'][1]);qa=b['qualite_masque_v20_4']
            self.assertIn(qa['verdict'],('A_VERIFIER','RISQUE_ELEVE'))
            self.assertTrue(Path(qa['fichier_apercu']).exists());self.assertTrue(Path(qa['fichier_rapport']).exists())
            self.assertEqual(Path(a['fichier_mode_choisi']).read_bytes(),Path(b['fichier_mode_choisi']).read_bytes())
            self.assertTrue(qa['validation_humaine_obligatoire'])
    def test_disabled_control(self):
        with tempfile.TemporaryDirectory() as t, patch.object(legacy,'gpu_snapshot',return_value={'cuda_disponible':False}):
            x=node.SmartSVGLineArtV204().run(self.image,t,segmentation_ia='desactiver',controle_contours='desactiver')
            self.assertEqual(json.loads(x['result'][1])['qualite_masque_v20_4']['statut'],'DESACTIVE')
    def test_failed_qa_does_not_break_existing_output(self):
        with tempfile.TemporaryDirectory() as t,patch.object(legacy,'gpu_snapshot',return_value={'cuda_disponible':False}),patch.object(node,'audit_output_root',side_effect=OSError('fault')):
            x=node.SmartSVGLineArtV204().run(self.image,t,segmentation_ia='desactiver')
            result=json.loads(x['result'][1]);self.assertEqual(result['qualite_masque_v20_4']['statut'],'ECHEC_DIAGNOSTIC')
            self.assertTrue(Path(result['fichier_mode_choisi']).is_file())

if __name__=='__main__':unittest.main()
