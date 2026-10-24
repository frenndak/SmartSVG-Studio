"""V20.1.1 regression tests: alpha, border padding, SVG, QA and file-system safety."""
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
PKG = 'smartsvg_v201_tests'
if PKG not in sys.modules:
    pkg = types.ModuleType(PKG)
    pkg.__path__ = [str(ROOT)]
    sys.modules[PKG] = pkg
line = importlib.import_module(PKG + '.lineart_v201')
node = importlib.import_module(PKG + '.node_v201')


def simple_lineart():
    a = np.full((240, 200, 3), 255, np.uint8)
    cv2.ellipse(a, (100, 80), (62, 53), 0, 0, 360, (0, 0, 0), 4)
    cv2.line(a,(54,135),(32,238),(0,0,0),4)
    cv2.line(a,(145,135),(170,238),(0,0,0),4)
    cv2.line(a,(54,135),(60,120),(0,0,0),4)
    cv2.line(a,(145,135),(140,120),(0,0,0),4)
    return a


class TestLineArt2011(unittest.TestCase):
    def test_fully_transparent_black_is_not_ink(self):
        a=np.zeros((120,150,4),np.uint8)
        a[20:100,30:125,:3]=0
        a[20:100,30:125,3]=0
        np.testing.assert_array_equal(line._validate_image(a), np.full((120,150,3),255,np.uint8))
        _,ink=line.extract_ink(a)
        self.assertEqual(np.count_nonzero(ink),0)

    def test_partial_alpha_composites_over_white(self):
        a=np.zeros((48,64,4),np.uint8)
        a[:,:,3]=128
        rgb=line._validate_image(a)
        self.assertTrue(np.all(rgb==127))

    def test_source_rgba_preserved_bit_exact(self):
        a=np.zeros((120,140,4),np.uint8)
        a[:,:,:3]=np.random.default_rng(5).integers(0,256,a[:,:,:3].shape,dtype=np.uint8)
        a[:,:,3]=np.arange(140,dtype=np.uint8)[None,:]
        with tempfile.TemporaryDirectory() as td:
            r=line.process_lineart(a,td,target='carte')
            orig=np.asarray(Image.open(Path(r['root'])/'01_SOURCE'/'original_RGBA.png'))
            np.testing.assert_array_equal(orig,a)
            self.assertEqual(r['report']['version'],'20.1.1-alpha')

    def test_sticker_offset_extends_canvas_and_remains_transparent_outside(self):
        a=simple_lineart()
        with tempfile.TemporaryDirectory() as td:
            out=line.process_lineart(a,td,target='sticker',white_margin_px=16)
            report=out['report']
            root=Path(out['root'])
            crop=np.asarray(Image.open(root/'02_ZONE_UTILE'/'carte_redressee.png'))
            printed=np.asarray(Image.open(out['image']))
            offset=report['decalage_traits_impression_px'][0]
            self.assertEqual(offset,18)
            self.assertEqual(printed.shape[:2],(crop.shape[0]+2*offset,crop.shape[1]+2*offset))
            self.assertEqual(printed[0,0,3],0)
            self.assertTrue(np.any(printed[:,:,3]>0))
            self.assertFalse(report['pret_decoupe_personnage'])
            self.assertIn('SILHOUETTE_GEOMETRIQUE_NON_VALIDEE',report['avertissements'])
            svg=ET.parse(root/'06_SVG'/'contour_selectionne.svg').getroot()
            self.assertIn(str(printed.shape[1]),svg.attrib['viewBox'])

    def test_offset_border_detectable_at_top_when_subject_touches_edge(self):
        # A clipped cut mask is a realistic failure for drawings touching page edges.
        a=np.full((180,140,3),255,np.uint8)
        cv2.rectangle(a,(1,1),(139,179),(0,0,0),3)
        with patch.object(line,'silhouette_candidate',return_value=(np.full((180,140),255,np.uint8),'bord')):
            with tempfile.TemporaryDirectory() as td:
                r=line.process_lineart(a,td,target='sticker',white_margin_px=10)
                x=np.asarray(Image.open(r['image']))
                self.assertTrue(np.any(x[:10,:,3]>0))
                self.assertEqual(x[0,0,3],0)

    def test_missing_subject_explicit_fallback_to_card(self):
        a=np.full((150,150,3),255,np.uint8)
        with tempfile.TemporaryDirectory() as td:
            r=line.process_lineart(a,td,target='personnage')
            self.assertEqual(r['report']['decoupe_generee'],'REPLI_CARTE_SUJET_INDETERMINE')
            self.assertIn('REPLI_CARTE_SANS_SILHOUETTE',r['report']['avertissements'])
            self.assertTrue(r['report']['validation_manuelle_obligatoire'])

    def test_invalid_output_path_rejected(self):
        with self.assertRaises(line.LineArtError):line.process_lineart(simple_lineart(),'   ')
        with self.assertRaises(line.LineArtError):line.process_lineart(simple_lineart(),None)

    @unittest.skipUnless(hasattr(os,'symlink'),'symlink unsupported')
    def test_symlink_ancestor_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/'real').mkdir()
            try:(root/'alias').symlink_to(root/'real',target_is_directory=True)
            except OSError:self.skipTest('OS symlink creation blocked')
            with self.assertRaises(line.LineArtError):
                line.process_lineart(simple_lineart(),root/'alias'/'deep')
            self.assertFalse((root/'real'/'deep').exists())

    def test_failed_save_no_partial_output(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(line,'_save_png',side_effect=OSError('out of disk')):
                with self.assertRaises(OSError):line.process_lineart(simple_lineart(),td,target='sticker')
            self.assertFalse(list(Path(td).iterdir()))

    def test_svg_ink_and_cut_are_xml_and_different(self):
        with tempfile.TemporaryDirectory() as td:
            r=line.process_lineart(simple_lineart(),td,target='carte')
            root=Path(r['root'])
            x=ET.parse(root/'06_SVG'/'traits_vectoriels.svg').getroot()
            y=ET.parse(root/'06_SVG'/'contour_selectionne.svg').getroot()
            self.assertNotEqual(x.find('{http://www.w3.org/2000/svg}path').attrib['fill'],
                                y.find('{http://www.w3.org/2000/svg}path').attrib['fill'])

    def test_old_node_aliases_remain(self):
        for key in ['SmartSVGLineArtV201','SmartSVGStudioV20Express','SmartSVGStudioV20Expert']:
            self.assertIn(key,node.NODE_CLASS_MAPPINGS)

    def test_never_claims_ai_or_physical_validation(self):
        with tempfile.TemporaryDirectory() as td:
            r=line.process_lineart(simple_lineart(),td,target='sticker')
            report=json.loads((Path(r['root'])/'rapport_v20_1.json').read_text())
            self.assertFalse(report['segmentation_ia_executee'])
            self.assertFalse(report['pret_decoupe_personnage'])
            self.assertIn('pixels_seulement',report['unite_dimensions_physiques'])

if __name__ == '__main__':unittest.main()

class TestSvgRasterAccuracy(unittest.TestCase):
    def test_svg_stroke_preserves_thin_scan_lines(self):
        try:
            import cairosvg
        except ImportError:
            self.skipTest('CairoSVG optionnel absent')
        import io
        ink=np.zeros((160,160),np.uint8)
        cv2.rectangle(ink,(8,8),(130,145),255,2)
        cv2.circle(ink,(70,60),20,255,2)
        svg,_=line.svg_ink(ink)
        rendered=np.asarray(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))))[:,:,3]>127
        original=ink>0
        iou=np.count_nonzero(rendered & original)/np.count_nonzero(rendered | original)
        self.assertGreater(iou,.80, f'Precision des traits vectoriels insuffisante: {iou:.2%}')

class TestComfyRGBA(unittest.TestCase):
    def test_alias_node_preserves_transparent_input(self):
        import torch
        a=np.zeros((130,150,4),np.uint8)
        a[:,:,:3]=10
        a[:,:,3]=0
        t=torch.from_numpy(a.astype(np.float32)/255.)[None]
        with tempfile.TemporaryDirectory() as td:
            ret=node.SmartSVGLineArtV2011().run(t,td)
            info=json.loads(ret['result'][1]);root=Path(info['dossier'])
            np.testing.assert_array_equal(np.asarray(Image.open(root/'01_SOURCE'/'original_RGBA.png')),a)
            self.assertEqual(info['pixels_traits'],0)
