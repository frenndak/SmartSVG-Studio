"""V16 Cricut delivery contract: PNGs, physical size, editability and atomic release."""
from pathlib import Path
from unittest.mock import patch
import hashlib
import importlib
import json
import os
import sys
import tempfile
import types
import unittest
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg_v16_tests'
if PKG not in sys.modules:
    pkg=types.ModuleType(PKG)
    pkg.__path__=[str(ROOT)]
    sys.modules[PKG]=pkg
engine=importlib.import_module(PKG+'.engine_v16')

def single():
    img=np.full((280,330,3),255,dtype=np.uint8)
    cv2.circle(img,(155,155),72,(80,210,80),-1)
    cv2.circle(img,(172,141),40,(70,80,220),-1)
    return img

class V16Tests(unittest.TestCase):
    def test_one_image_and_kit(self):
        with tempfile.TemporaryDirectory() as td:
            r,_=engine.process_v16(single(),td,ia_mode='desactiver',sheet_width_mm=80)
            work=Path(r['output'])
            self.assertEqual(r['audit_v16']['nombre_stickers'],1)
            self.assertEqual(len(list((work/engine.SINGLES).glob('*_IMPRIMER_DECOUPER.png'))),1)
            self.assertEqual(len(list((work/engine.SINGLES).glob('*.svg'))),1)
            self.assertEqual(len(list((work/engine.KIT).glob('*.svg'))),2)
            self.assertEqual(len(list((work/engine.KIT).glob('*.png'))),1)
            self.assertTrue((work/engine.STATUS).is_file())
            self.assertFalse((work/'PRET_V15.json').exists())
            self.assertFalse(list(Path(td).glob('.SmartSVG_V16_TEMP_*')))
            d=json.loads((work/engine.STATUS).read_text(encoding='utf8'))
            self.assertEqual(d['statut'],'GEOMETRIE_CONTROLEE_CRICUT_NON_TESTE')
            for name,meta in d['fichiers'].items():
                p=work/name
                self.assertTrue(p.is_file(),name)
                self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(),meta['sha256'])

    def test_physical_png_dimensions(self):
        with tempfile.TemporaryDirectory() as td:
            r,_=engine.process_v16(single(),td,ia_mode='desactiver',sheet_width_mm=80)
            work=Path(r['output'])
            with Image.open(work/engine.NAME) as im:
                self.assertEqual(im.mode,'RGBA')
                mm=25.4*im.width/im.info['dpi'][0]
                self.assertAlmostEqual(mm,80,delta=.05)
            svg=ET.parse(work/engine.CRICUT_SVG).getroot()
            self.assertAlmostEqual(engine._mm(svg.get('width')),80,places=1)
            png=next((work/engine.SINGLES).glob('*_IMPRIMER_DECOUPER.png'))
            individual_svg=next((work/engine.SINGLES).glob('*.svg'))
            small_root=ET.parse(individual_svg).getroot()
            with Image.open(png) as im:
                expected_mm=engine._mm(small_root.get('width'))
                self.assertAlmostEqual(25.4*im.width/im.info['dpi'][0],expected_mm,delta=.05)

    def test_two_transparent_stickers_individual_pngs_isolated(self):
        h,w=250,480
        rgb=np.zeros((h,w,3),np.uint8)
        a=np.zeros((h,w),np.uint8)
        cv2.circle(a,(102,124),65,255,-1)
        cv2.circle(a,(375,122),57,255,-1)
        rgb[a>0]=[255,80,90]
        # Distinctive second sticker RGB allows detecting leaks in first PNG.
        rgb[(a>0)&(np.indices(a.shape)[1]>240)]=[40,220,70]
        with tempfile.TemporaryDirectory() as td:
            r,_=engine.process_v16(rgb,td,alpha=a,ia_mode='desactiver',sheet_width_mm=180)
            work=Path(r['output'])
            self.assertEqual(r['audit_v16']['nombre_stickers'],2)
            pngs=sorted((work/engine.SINGLES).glob('*.png'))
            self.assertEqual(len(pngs),2)
            with Image.open(pngs[0]) as im:
                arr=np.asarray(im.convert('RGBA'))
                p=arr[arr[:,:,3]>0,:3]
                self.assertFalse(np.any(np.all(p==[40,220,70],axis=1)))
            with Image.open(pngs[1]) as im:
                arr=np.asarray(im.convert('RGBA'))
                p=arr[arr[:,:,3]>0,:3]
                self.assertFalse(np.any(np.all(p==[255,80,90],axis=1)))

    def test_reject_failed_additional_export_and_cleanup(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(engine,'_create_individual_pngs',side_effect=engine.UnsafeCut('scenario de panne')):
                with self.assertRaisesRegex(engine.UnsafeCut,'export refuse'):
                    engine.process_v16(single(),td,ia_mode='desactiver')
            self.assertFalse(list(Path(td).glob('SmartSVG_V16_*')))
            self.assertTrue(list(Path(td).glob('SmartSVG_ECHEC_V16_*.json')))
            self.assertFalse(list(Path(td).glob('.SmartSVG_V16_TEMP_*')))

    def test_node_express_default_and_workflow(self):
        torch=None
        try:import torch
        except ImportError:self.skipTest('PyTorch non present')
        node=importlib.import_module(PKG+'.node_v16')
        cfg=node.SmartSVGStudioV16Express.INPUT_TYPES()
        self.assertEqual(set(cfg['required']),{'image','dossier_sortie','largeur_planche_mm','ia_locale'})
        example=json.loads((ROOT/'example_workflows/SmartSVG_Studio_V16_Express.json').read_text('utf8'))
        self.assertEqual(example['nodes'][1]['type'],'SmartSVGStudioV16Express')
        self.assertEqual(example['links'][1][4],4)
        with tempfile.TemporaryDirectory() as td:
            tensor=torch.tensor(single(),dtype=torch.float32).unsqueeze(0)/255.
            n=node.SmartSVGStudioV16Express()
            preview,msg=n.execute_express(tensor,td,largeur_planche_mm=90,ia_locale='desactiver')
            self.assertIn('KIT A IMPORTER',msg)
            self.assertEqual(tuple(preview.shape[:1]),(1,))
            self.assertEqual(len(list(Path(td).glob('SmartSVG_V16_*'))),1)

if __name__=='__main__':unittest.main()
