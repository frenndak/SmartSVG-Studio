"""V20.2 tests: real mask geometry, provider wiring, safe QA, history."""
import importlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import cv2
import numpy as np
from PIL import Image
import torch

ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg_v202_testpkg'
if PKG not in sys.modules:
    pkg=types.ModuleType(PKG);pkg.__path__=[str(ROOT)];sys.modules[PKG]=pkg
ai=importlib.import_module(PKG+'.lineart_ai_v202')
node=importlib.import_module(PKG+'.node_v202')
line=importlib.import_module(PKG+'.lineart_v201')

def drawing():
    a=np.full((350,260,3),250,np.uint8)
    cv2.ellipse(a,(132,115),(57,73),0,0,360,(0,0,0),3)
    cv2.line(a,(76,195),(45,345),(0,0,0),4)
    cv2.line(a,(191,195),(219,345),(0,0,0),4)
    cv2.circle(a,(111,118),10,(0,0,0),2)
    cv2.circle(a,(150,118),10,(0,0,0),2)
    return a

def oval(shape):
    h,w=shape
    mask=np.zeros((h,w),np.float32)
    cv2.ellipse(mask,(w//2,h//2),(w//4,h//3),0,0,360,1,-1)
    return mask

class TestV202(unittest.TestCase):
    def test_binary_uint8_01(self):
        m=np.zeros((1,70,75),np.uint8);m[:,10:40,12:50]=1
        a=ai.validate_masks(m,(70,75))
        self.assertEqual(a.max(),1)
    def test_binary_uint8_0255(self):
        m=np.zeros((70,75),np.uint8);m[10:40,12:50]=255
        a=ai.validate_masks(m,(70,75))
        self.assertEqual(a.max(),1)
    def test_float_255_is_rejected(self):
        with self.assertRaises(ai.LineArtSegmentationError):
            ai.validate_masks(np.ones((70,75),np.float32)*255,(70,75))
    def test_nan_rejected(self):
        x=np.ones((70,75),np.float32);x[3,4]=float('nan')
        with self.assertRaises(ai.LineArtSegmentationError):ai.validate_masks(x,(70,75))
    def test_wrong_mask_shape_rejected(self):
        with self.assertRaises(ai.LineArtSegmentationError):ai.validate_masks(np.ones((80,80)),(70,75))
    def test_oversized_batch_rejected(self):
        with self.assertRaises(ai.LineArtSegmentationError):
            ai.validate_masks(np.ones((17,70,75),dtype=np.uint8),(70,75))
    def test_source_to_crop_homography_maps_exactly(self):
        rgb=np.full((280,240,3),255,np.uint8)
        card={'detected':True,'points':[[20.,10.],[210.,15.],[215.,245.],[25.,250.]]}
        m=np.zeros((280,240),np.uint8);cv2.rectangle(m,(80,80),(150,180),255,-1)
        crop,geo=line.crop_card(rgb,card,True)
        aligned=ai.align_masks(m,rgb,card,geo,space='source',rectify=True)
        self.assertEqual(aligned.shape[1:],crop.shape[:2])
        expected=cv2.warpPerspective(m.astype(np.float32)/255.,
            cv2.getPerspectiveTransform(line._order_corners(card['points']),
            np.float32([[0,0],[crop.shape[1]-1,0],[crop.shape[1]-1,crop.shape[0]-1],[0,crop.shape[0]-1]])),
            (crop.shape[1],crop.shape[0]),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT)
        self.assertLess(float(np.max(np.abs(aligned[0]-expected))),1e-6)
    def test_uncropped_no_card_identity(self):
        rgb=drawing();m=oval(rgb.shape[:2]);c={'detected':False,'points':None}
        got=ai.align_masks(m,rgb,c,{'dimensions':[260,350]})
        np.testing.assert_array_equal(got[0],m)
    def test_already_cropped_mask_does_not_double_warp(self):
        rgb=drawing();card=line.detect_card(rgb);crop,geo=line.crop_card(rgb,card)
        m=oval(crop.shape[:2])
        actual=ai.align_masks(m,rgb,card,geo,space='carte_redressee')
        np.testing.assert_array_equal(actual[0],m)
    def test_mask_choice_rejects_full_frame(self):
        mask=np.ones((1,100,90),np.float32)
        selected,r=ai.choose_subject(mask)
        self.assertIsNone(selected)
        self.assertEqual(r['statut'],'AUCUN_SUJET_ADMISSIBLE')
    def test_ambiguous_two_subjects_flagged(self):
        m=np.zeros((2,200,200),np.float32)
        cv2.circle(m[0],(75,100),42,1,-1)
        cv2.circle(m[1],(125,100),42,1,-1)
        _,r=ai.choose_subject(m)
        self.assertTrue(r['ambiguite'])
    def test_print_padding_outside_frame(self):
        ink=np.zeros((100,90),np.uint8);ink[0,45]=255
        mask=np.zeros_like(ink,dtype=np.float32);mask[:90,10:80]=1.
        rgba,solid,pad=ai.make_print_candidate(ink,mask,12)
        self.assertEqual(rgba.shape,(128,118,4))
        self.assertEqual(pad,14)
        self.assertEqual(rgba[0,0,3],0)
        self.assertTrue(np.any(solid[:14,:]>0))
    def test_print_closes_internal_holes(self):
        mask=np.ones((110,110),np.float32)
        mask[20:35,20:35]=0
        rgba,cut,_=ai.make_print_candidate(np.zeros((110,110),np.uint8),mask,0)
        self.assertEqual(int(cut[28,28]),255)
        self.assertEqual(int(rgba[28,28,3]),255)
    def test_external_mask_qa_png_and_original_preserved(self):
        rgb=drawing();mask=oval(rgb.shape[:2])
        with tempfile.TemporaryDirectory() as td:
            r=ai.process_lineart_ai(rgb,td,masks=mask,ia='desactiver',target='sticker')
            root=Path(r['root']);self.assertTrue(Path(r['image_candidat']).is_file())
            self.assertEqual(r['report']['origine_masque'],'MASK_EXTERNE_COMFYUI')
            self.assertFalse(r['report']['segmentation_ia_appelee'])
            self.assertFalse(r['report']['pret_cricut_sans_verification'])
            np.testing.assert_array_equal(np.asarray(Image.open(root/'01_SOURCE'/'original_RGB.png')),rgb)
            self.assertTrue((root/'06_SVG'/'traits_vectoriels.svg').is_file())
            self.assertTrue((root/'08_SEGMENTATION_IA_V20_2'/'contour_ia_CANDIDAT.svg').is_file())
    def test_auto_no_models_does_not_fabricate_mask(self):
        with tempfile.TemporaryDirectory() as td:
            def no_model(*a,**kw):raise RuntimeError('absent')
            r=ai.process_lineart_ai(drawing(),td,segmenter=no_model,
                analyse_florence='desactiver',ia='auto')
            self.assertIsNone(r['image_candidat'])
            self.assertFalse(r['report']['masque_ia_produit'])
            self.assertEqual(r['report']['inference']['statut'],'ECHEC')
    def test_forcer_without_models_raises_without_output(self):
        with tempfile.TemporaryDirectory() as td:
            def no_model(*a,**kw):raise RuntimeError('absent')
            with self.assertRaises(RuntimeError):
                ai.process_lineart_ai(drawing(),td,segmenter=no_model,analyse_florence='desactiver',ia='forcer')
            self.assertFalse(list(Path(td).iterdir()))
    def test_sam2_stub_is_actually_invoked(self):
        calls=[]
        def run(rgb,profile,custom_prompts):
            calls.append((rgb.shape,profile,custom_prompts))
            return {'masks':oval(rgb.shape[:2])[None],
                    'audit':{'prompts':['person'],'statut':'MOCK'}}
        with tempfile.TemporaryDirectory() as td:
            result=ai.process_lineart_ai(drawing(),td,ia='forcer',segmenter=run,
                                analyse_florence='desactiver')
            self.assertTrue(result['report']['segmentation_ia_appelee'])
            self.assertTrue(result['report']['masque_ia_produit'])
            self.assertEqual(calls[0][1],'personne')
    def test_florence_prompts_pass_to_sam2(self):
        seen=[]
        def florence(*a,**k):return {'audit':{'statut':'OK'},'prompts':['person']}
        def model(rgb,profile,custom_prompts):
            seen.append(custom_prompts)
            return {'masks':oval(rgb.shape[:2])[None], 'audit':{'prompts':['person']}}
        with tempfile.TemporaryDirectory() as td:
            ai.process_lineart_ai(drawing(),td,ia='forcer',florence=florence,
                segmenter=model,analyse_florence='auto')
            self.assertEqual(seen,['person'])
    def test_mask_priority_no_model_call(self):
        def broken(*a,**k):raise AssertionError('Must not invoke model')
        with tempfile.TemporaryDirectory() as td:
            r=ai.process_lineart_ai(drawing(),td,masks=oval(drawing().shape[:2]),
                segmenter=broken,florence=broken)
            self.assertEqual(r['report']['origine_masque'],'MASK_EXTERNE_COMFYUI')
    def test_atomic_qa_failure_rolls_back_new_folder(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(ai.Image.Image,'save',side_effect=OSError('disk fail')):
                with self.assertRaises(OSError):
                    ai.process_lineart_ai(drawing(),td,masks=oval(drawing().shape[:2]))
            self.assertEqual(list(Path(td).iterdir()),[])
    def test_legacy_cricut_pixels_unchanged(self):
        import hashlib
        def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
        x=drawing()
        with tempfile.TemporaryDirectory() as td:
            old=line.process_lineart(x,td,target='sticker')
            new=ai.process_lineart_ai(x,td,target='sticker',ia='desactiver')
            for sub in ('04_LINEART/traits_fins.png',
                        '05_CONTOURS/IMPRIMER_PUIS_DECOUPER_BROUILLON.png',
                        '06_SVG/traits_vectoriels.svg'):
                self.assertEqual(sha(Path(old['root'])/sub),sha(Path(new['root'])/sub),sub)
    def test_prevalidation_gpu_tensor_skips_cpu_copy(self):
        class FakeGpuTensor:
            shape=(17,100,100)
            def detach(self):raise AssertionError('Unwanted GPU transfer')
        with self.assertRaises(ai.LineArtSegmentationError):
            ai.validate_masks(FakeGpuTensor(),(100,100))
    def test_invalid_comfy_image_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                node.SmartSVGLineArtV202().run(torch.zeros((2,100,100,3)),td)
    def test_comfy_node_and_history(self):
        self.assertIn('SmartSVGStudioV20Expert',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGLineArtV2011',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGLineArtV202',node.NODE_CLASS_MAPPINGS)
        self.assertIn('masques_objets',node.SmartSVGLineArtV202.INPUT_TYPES()['optional'])
    def test_comfy_node_external_mask(self):
        rgb=drawing();m=oval(rgb.shape[:2]);t=torch.from_numpy(rgb.astype(np.float32)/255.)[None]
        with tempfile.TemporaryDirectory() as td:
            result=node.SmartSVGLineArtV202().run(t,td,masques_objets=torch.from_numpy(m[None]),
                              segmentation_ia='desactiver')
            self.assertIn('MASK_EXTERNE_COMFYUI',result['result'][1])
            self.assertEqual(result['result'][0].shape[0],1)

if __name__=='__main__':unittest.main()
