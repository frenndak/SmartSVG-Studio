"""V20.1 line-art tests: CPU behavior, source integrity and Cricut QA."""
from pathlib import Path
import importlib, sys, tempfile, types, unittest, hashlib
import xml.etree.ElementTree as ET
import numpy as np
import cv2
import torch
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg_v201_tests'
if PKG not in sys.modules:
    pkg=types.ModuleType(PKG);pkg.__path__=[str(ROOT)];sys.modules[PKG]=pkg
line=importlib.import_module(PKG+'.lineart_v201')
node=importlib.import_module(PKG+'.node_v201')


def card_scene():
    image=np.full((480,360,3),220,np.uint8)
    cv2.rectangle(image,(68,45),(290,425),(45,45,45),2)
    cv2.ellipse(image,(178,211),(68,84),0,0,360,(24,24,24),3)
    cv2.circle(image,(159,190),10,(20,20,20),2)
    cv2.circle(image,(198,190),10,(20,20,20),2)
    cv2.rectangle(image,(118,296),(245,388),(25,25,25),3)
    cv2.rectangle(image,(322,70),(358,370),(60,60,60),1)
    return image


class TestLineArtV201(unittest.TestCase):
    def test_auto_frame_detected_off_center(self):
        r=line.detect_card(card_scene())
        self.assertTrue(r['detected'],r)
        self.assertEqual(len(r['points']),4)
        self.assertGreater(r['score'],0)
    def test_crop_perspective_returns_rgb(self):
        a=card_scene();c=line.detect_card(a)
        out,geometry=line.crop_card(a,c,rectify=True)
        self.assertEqual(out.shape[-1],3)
        self.assertGreater(out.shape[0],out.shape[1])
        self.assertEqual(geometry['redressement'],'homographie')
    def test_missing_card_never_claimed_as_detected(self):
        a=np.full((250,200,3),255,np.uint8)
        r=line.detect_card(a)
        self.assertFalse(r['detected'])
        out,_=line.crop_card(a,r)
        np.testing.assert_array_equal(out,a)
    def test_ink_is_binary_and_detail_preserved(self):
        a=card_scene()
        clean,ink=line.extract_ink(a,inset=0)
        self.assertEqual(clean.dtype,np.uint8)
        self.assertTrue(set(np.unique(ink)).issubset({0,255}))
        self.assertGreater(int(np.count_nonzero(ink)),300)
    def test_inset_removes_border(self):
        a=card_scene();_,ink=line.extract_ink(a,inset=5)
        self.assertEqual(int(ink[:5].sum()+ink[-5:].sum()+ink[:,:5].sum()+ink[:,-5:].sum()),0)
    def test_blank_has_no_subject(self):
        mask=np.zeros((200,120),np.uint8)
        proposal,status=line.silhouette_candidate(mask)
        self.assertIsNone(proposal)
    def test_open_body_proposal_is_filled_not_hollow(self):
        a=np.zeros((300,180),np.uint8)
        cv2.ellipse(a,(90,85),(40,58),0,0,360,255,3)
        cv2.line(a,(40,180),(30,298),255,3)
        cv2.line(a,(140,180),(152,298),255,3)
        cv2.line(a,(40,180),(65,132),255,3)
        cv2.line(a,(140,180),(116,132),255,3)
        result,_=line.silhouette_candidate(a)
        self.assertIsNotNone(result)
        self.assertEqual(int(result[230,90]),255)
    def test_svg_parses_and_is_layer_independent(self):
        a=np.zeros((130,130),np.uint8)
        cv2.circle(a,(65,65),43,255,3)
        ink,n=line.svg_ink(a)
        path=line.svg_cut(a)
        self.assertGreater(n,0)
        ET.fromstring(ink)
        ET.fromstring(path)
        self.assertIn('fill-rule="evenodd"',ink)
    def test_invalid_dimensions_rejected(self):
        for x in [np.zeros((10,200,3),np.uint8),np.zeros((6000,6000,3),np.uint8),np.zeros((100,100),np.uint8)]:
            with self.assertRaises(line.LineArtError):line._validate_image(x)
    def test_invalid_parameters_rejected_before_export(self):
        with tempfile.TemporaryDirectory() as td:
            for kw in [dict(target='wrong'),dict(mode='wrong'),dict(white_margin_px=100),dict(source='wrong')]:
                with self.assertRaises(line.LineArtError):line.process_lineart(card_scene(),td,**kw)
    def test_card_export_preserves_original_and_files(self):
        x=card_scene();digest=hashlib.sha256(x.tobytes()).hexdigest()
        with tempfile.TemporaryDirectory() as td:
            out=line.process_lineart(x,td,target='carte')
            root=Path(out['root'])
            self.assertEqual(hashlib.sha256(x.tobytes()).hexdigest(),digest)
            np.testing.assert_array_equal(np.asarray(Image.open(root/'01_SOURCE'/'original_RGB.png')),x)
            self.assertEqual(out['report']['decoupe_generee'],'CARTE_GEOMETRIQUE')
            self.assertEqual(out['report']['segmentation_ia_executee'],False)
            self.assertTrue((root/'06_SVG'/'contour_selectionne.svg').is_file())
            self.assertTrue((root/'07_QA'/'avant_apres.png').is_file())
            self.assertTrue((root/'rapport_v20_1.json').is_file())
    def test_sticker_export_explicitly_draft(self):
        with tempfile.TemporaryDirectory() as td:
            res=line.process_lineart(card_scene(),td,target='sticker')
            self.assertIn('PROPOSITION',res['report']['decoupe_generee'])
            p=Image.open(res['image'])
            self.assertEqual(p.mode,'RGBA')
            self.assertLess(np.asarray(p)[:,:,3].min(),255)
    def test_atomic_no_final_if_save_failed(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as td:
            with patch.object(line,'_save_png',side_effect=OSError('storage failed')):
                with self.assertRaises(OSError):line.process_lineart(card_scene(),td)
            self.assertEqual(list(Path(td).iterdir()),[])
    def test_comfyui_node_registers_old_nodes(self):
        for name in ('SmartSVGLineArtV201','SmartSVGStudioV20Expert','SmartSVGStudioV20Express','SmartSVGAdaptiveV20'):
            self.assertIn(name,node.NODE_CLASS_MAPPINGS)
        kinds=node.SmartSVGLineArtV201.INPUT_TYPES()['required']
        self.assertIn('source',kinds)
    def test_comfyui_node_can_export(self):
        x=card_scene()
        with tempfile.TemporaryDirectory() as td:
            img=torch.from_numpy(x.astype('float32')/255)[None]
            ret=node.SmartSVGLineArtV201().run(img,td,source='photo_ecran')
            preview,report=ret['result']
            self.assertEqual(preview.ndim,4)
            self.assertIn('CARTE_GEOMETRIQUE',report)
            self.assertEqual(len(ret['ui']['text']),1)

if __name__=='__main__':unittest.main()
