"""Regression tests for V15 (no GPU, internet, or user drawings needed)."""
import importlib
import json
import sys
import tempfile
import types
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg_v15_unit'
package=types.ModuleType(PKG)
package.__path__=[str(ROOT)]
sys.modules[PKG]=package
engine=importlib.import_module(PKG+'.engine_v15')


def example():
    img=np.full((240,280,3),255,dtype=np.uint8)
    cv2.circle(img,(130,124),62,(80,200,70),-1)
    cv2.ellipse(img,(150,100),(32,40),0,0,360,(70,90,225),-1)
    return img


class TestV15(unittest.TestCase):
    def test_single_complete(self):
        with tempfile.TemporaryDirectory() as td:
            report,_=engine.process_v15(example(),td,ia_mode='desactiver')
            folder=Path(report['output'])
            qa=report['audit_v15']
            self.assertEqual(qa['nombre_stickers'],1)
            self.assertTrue(qa['controle_svg_compact']['teste'])
            self.assertEqual(qa['controle_svg_compact']['manquants_hors_tolerance'],0)
            self.assertTrue((folder/engine.REGION_SVG).is_file())
            self.assertEqual(len(list((folder/engine.SINGLES).glob('*.svg'))),1)
            root=ET.parse(next((folder/engine.SINGLES).glob('*.svg'))).getroot()
            x,y,w,h=engine._viewbox(root)
            self.assertLess(w,280)
            self.assertLess(h,240)
            self.assertGreater(engine._mm(root.get('width')),1)
            self.assertEqual(len([g for g in root if g.tag==engine.SVG+'g']),1)
            self.assertEqual(len(list(folder.glob('PRET_*.json'))),1)
            from hashlib import sha256
            status=json.loads((folder/'PRET_V15.json').read_text('utf8'))
            for name,info in status['fichiers'].items():
                self.assertEqual(sha256((folder/name).read_bytes()).hexdigest(),info['sha256'])
            self.assertIn('EDITER_STICKERS_SEPAREMENT/STICKER_01_EDITABLE.svg',status['fichiers'])
            self.assertTrue((folder/'PRET_V15.json').is_file())
            self.assertFalse(list(Path(td).glob('.SmartSVG_V15_TEMP_*')))

    def test_transparent_two_regions(self):
        im=np.zeros((210,390,3),np.uint8)
        alpha=np.zeros(im.shape[:2],np.uint8)
        cv2.circle(alpha,(85,115),52,255,-1)
        cv2.rectangle(alpha,(255,64),(338,165),255,-1)
        im[alpha>0]=[80,155,210]
        with tempfile.TemporaryDirectory() as td:
            report,_=engine.process_v15(im,td,alpha=alpha,ia_mode='desactiver')
            self.assertEqual(report['audit_v15']['nombre_stickers'],2)
            self.assertEqual(len(report['audit_v15']['fichiers_individuels']),2)
            self.assertTrue(report['audit_v15']['controle_svg_regions']['teste'])

    def test_fail_closed_on_alpha_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            def faulty(work,svg_name=engine.CRICUT_SVG,tolerance=2):
                raise engine.UnsafeCut('SVG altere volontairement')
            with patch.object(engine,'alpha_preflight',side_effect=faulty):
                with self.assertRaisesRegex(engine.UnsafeCut,'export refuse'):
                    engine.process_v15(example(),td,ia_mode='desactiver')
            self.assertFalse(list(Path(td).glob('SmartSVG_V15_*')))
            self.assertTrue(list(Path(td).glob('SmartSVG_ECHEC_V15_*.json')))

    def test_tampered_svg_detected(self):
        with tempfile.TemporaryDirectory() as td:
            r,_=engine.process_v15(example(),td,ia_mode='desactiver')
            folder=Path(r['output'])
            svg=folder/engine.CRICUT_SVG
            root=ET.parse(svg)
            root.getroot()[0].set('transform','translate(500 500)')
            root.write(svg,encoding='utf-8',xml_declaration=True)
            with self.assertRaisesRegex(engine.UnsafeCut,'defauts silhouette'):
                engine.alpha_preflight(folder)

    def test_cairosvg_missing_is_reported(self):
        with tempfile.TemporaryDirectory() as td:
            r,_=engine.process_v15(example(),td,ia_mode='desactiver')
            with patch.dict(sys.modules,{'cairosvg':None}):
                qa=engine.alpha_preflight(Path(r['output']))
            self.assertFalse(qa['teste'])
            self.assertFalse(qa['verification_raster_svg_ok'])

    def test_region_svg_has_no_images_text_strokes_gradients(self):
        with tempfile.TemporaryDirectory() as td:
            r,_=engine.process_v15(example(),td,ia_mode='desactiver')
            file=Path(r['output'])/engine.REGION_SVG
            root=ET.parse(file).getroot()
            self.assertTrue(engine._validate_safe_svg(root))
            self.assertGreater(r['audit_v15']['regions_editables']['nombre_chemins'],0)
            self.assertLess(r['audit_v15']['regions_editables']['nombre_chemins'],5000)

    def test_invalid_viewbox_and_dimensions(self):
        with self.assertRaises(engine.UnsafeCut):engine._viewbox(ET.Element(engine.SVG+'svg',{'viewBox':'0 0 0 100'}))
        with self.assertRaises(engine.UnsafeCut):engine._mm('12px')

if __name__=='__main__':unittest.main()
