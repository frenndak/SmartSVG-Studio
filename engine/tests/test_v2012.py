"""V20.1.2: Cricut cut-outline vs cut-ink vs pen; contract and regressions."""
import importlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
import xml.etree.ElementTree as ET

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg_v2012_tests'
if PKG not in sys.modules:
    mod=types.ModuleType(PKG)
    mod.__path__=[str(ROOT)]
    sys.modules[PKG]=mod
choice=importlib.import_module(PKG+'.cricut_choice_v2012')
node=importlib.import_module(PKG+'.node_v2012')

def pic():
    a=np.full((220,180,3),255,np.uint8)
    cv2.ellipse(a,(90,65),(60,48),0,0,360,(0,0,0),3)
    cv2.circle(a,(72,63),6,(0,0,0),2)
    cv2.circle(a,(108,63),6,(0,0,0),2)
    cv2.line(a,(53,130),(38,219),(0,0,0),4)
    cv2.line(a,(127,130),(144,219),(0,0,0),4)
    return a

class TestCricutOps(unittest.TestCase):
    def test_default_recommends_png_sticker_and_only_outer_alpha(self):
        with tempfile.TemporaryDirectory() as t:
            r=choice.process_choice(pic(),t)
            report=r['choice_report']
            self.assertEqual(report['operation_choisie'],'imprimer_decouper_contour')
            self.assertEqual(report['fichier_recommande'],'01_IMPRIMER_PUIS_DECOUPER_UNIQUEMENT_CONTOUR.png')
            alpha=np.asarray(Image.open(r['recommended_file']))[:,:,3]
            self.assertGreater(np.count_nonzero(alpha),0)
            self.assertEqual(np.count_nonzero((alpha>0) & (alpha<255)),0)
            self.assertFalse(report['pret_decoupe_personnage'])

    def test_distinct_svg_operations_cut_every_stroke_vs_single_outline(self):
        with tempfile.TemporaryDirectory() as t:
            r=choice.process_choice(pic(),t)
            folder=Path(r['cricut_root'])
            out=ET.parse(folder/'02_DECOUPER_SEULEMENT_CONTOUR_EXTERIEUR.svg').getroot()
            ink=ET.parse(folder/'03_DECOUPER_CHAQUE_TRAIT.svg').getroot()
            self.assertEqual(len(out.findall('.//{http://www.w3.org/2000/svg}path')),1)
            self.assertIn('evenodd',ink.find('.//{http://www.w3.org/2000/svg}path').attrib['fill-rule'])
            self.assertGreater(r['choice_report']['svg_coupe_traces'],1)
            self.assertNotEqual((folder/'02_DECOUPER_SEULEMENT_CONTOUR_EXTERIEUR.svg').read_bytes(),
                                (folder/'03_DECOUPER_CHAQUE_TRAIT.svg').read_bytes())

    def test_ink_svg_has_no_stroke_that_doubles_cut(self):
        ink=np.zeros((100,100),np.uint8)
        cv2.rectangle(ink,(10,10),(90,90),255,4)
        xml,_=choice.svg_cut_ink_regions(ink)
        root=ET.fromstring(xml)
        path=root.find('{http://www.w3.org/2000/svg}path')
        self.assertNotIn('stroke',path.attrib)
        self.assertEqual(path.get('fill-rule'),'evenodd')

    def test_pen_svg_is_stroke_only(self):
        ink=np.zeros((100,100),np.uint8)
        cv2.line(ink,(10,12),(90,12),255,3)
        xml,count=choice.svg_draw_centerlines(ink)
        root=ET.fromstring(xml)
        group=root.find('{http://www.w3.org/2000/svg}g')
        self.assertEqual(group.get('fill'),'none')
        self.assertGreater(count,0)
        self.assertTrue(group.findall('{http://www.w3.org/2000/svg}path'))

    def test_outer_svg_dimensions_match_padded_png(self):
        with tempfile.TemporaryDirectory() as t:
            r=choice.process_choice(pic(),t,width_mm=85,white_margin_px=11)
            root=Path(r['cricut_root'])
            svg=ET.parse(root/'02_DECOUPER_SEULEMENT_CONTOUR_EXTERIEUR.svg').getroot()
            with Image.open(r['recommended_file']) as img:
                w,h=img.size
            self.assertAlmostEqual(float(svg.get('width').removesuffix('mm')),
                                   r['choice_report']['largeur_silhouette_avec_marge_mm'],places=3)
            self.assertAlmostEqual(float(svg.get('height').removesuffix('mm')),
                                   r['choice_report']['largeur_silhouette_avec_marge_mm']*h/w,places=3)

    def test_chosen_operation_only_changes_recommendation_not_original_png(self):
        with tempfile.TemporaryDirectory() as t:
            a=choice.process_choice(pic(),t,operation='imprimer_decouper_contour')
            b=choice.process_choice(pic(),t,operation='decouper_tous_les_traits')
            self.assertEqual(Path(a['image']).read_bytes(),Path(b['image']).read_bytes())
            self.assertEqual(Path(a['cricut_root'],'03_DECOUPER_CHAQUE_TRAIT.svg').read_bytes(),
                             Path(b['recommended_file']).read_bytes())

    def test_all_modes_exported_once_even_if_one_selected(self):
        with tempfile.TemporaryDirectory() as t:
            r=choice.process_choice(pic(),t,operation='tout_preparer')
            self.assertEqual(len(r['choice_report']['exports_disponibles']),4)
            for name in r['choice_report']['exports_disponibles'].values():
                self.assertTrue((Path(r['cricut_root'])/name).exists())

    def test_invalid_operation_and_physical_width_fail_before_writing(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(choice.LineArtError):choice.process_choice(pic(),t,operation='undefined')
            with self.assertRaises(choice.LineArtError):choice.process_choice(pic(),t,width_mm=4)
            with self.assertRaises(choice.LineArtError):choice.process_choice(pic(),t,width_mm=float('nan'))
            self.assertFalse(list(Path(t).iterdir()))

    def test_wrong_mask_rejected(self):
        with self.assertRaises(choice.LineArtError):choice.svg_cut_ink_regions(np.zeros((100,100,3),np.uint8))
        with self.assertRaises(choice.LineArtError):choice.svg_draw_centerlines(np.zeros((100,100),np.float32))

    def test_no_subject_reverts_to_card_explicit_warning(self):
        blank=np.full((110,130,3),255,np.uint8)
        with tempfile.TemporaryDirectory() as t:
            r=choice.process_choice(blank,t)
            self.assertIn('SUJET_NON_DETECTE_LE_CONTOUR_EST_CELUI_DE_LA_CARTE',r['choice_report']['avertissements'])
            self.assertIn('AUCUN_TRAIT_DETECTE',r['choice_report']['avertissements'])

    def test_old_nodes_still_registered(self):
        for key in ('SmartSVGLineArtV201','SmartSVGLineArtV2011','SmartSVGStudioV20Express','SmartSVGLineArtV2012'):
            self.assertIn(key,node.NODE_CLASS_MAPPINGS)

    def test_comfy_node_selected_file_user_facing(self):
        import torch
        tensor=torch.from_numpy(pic().astype(np.float32)/255)[None]
        with tempfile.TemporaryDirectory() as t:
            r=node.SmartSVGLineArtV2012().run(tensor,t,operation_cricut='decouper_tous_les_traits')
            msg=json.loads(r['result'][1])
            self.assertTrue(msg['fichier_recommande'].endswith('03_DECOUPER_CHAQUE_TRAIT.svg'))
            self.assertTrue(Path(msg['fichier_recommande']).exists())

    def test_new_workflow_has_widgets_in_correct_order(self):
        cls=node.SmartSVGLineArtV2012
        expected=[n for n in cls.INPUT_TYPES()['required'] if n!='image']
        for fname in ('SmartSVG_Studio_V20_1_2_Sticker_Contour.json',
                      'SmartSVG_Studio_V20_1_2_Coupe_Tous_Traits.json'):
            wf=json.loads((ROOT/'example_workflows'/fname).read_text('utf8'))
            n=next(n for n in wf['nodes'] if n['type']=='SmartSVGLineArtV2012')
            self.assertEqual([i['name'] for i in n['inputs'] if i.get('widget')],expected)
            self.assertEqual(len(n['widgets_values']),len(expected))

    def test_source_png_unchanged_after_choice(self):
        rgba=np.full((120,140,4),255,np.uint8)
        rgba[:,:,3]=np.arange(140,dtype=np.uint8)
        with tempfile.TemporaryDirectory() as t:
            r=choice.process_choice(rgba,t)
            original=np.asarray(Image.open(Path(r['root'])/'01_SOURCE'/'original_RGBA.png'))
            np.testing.assert_array_equal(original,rgba)

    def test_print_png_matches_v2011_engine_byte_for_byte(self):
        old=importlib.import_module(PKG+'.lineart_v201')
        with tempfile.TemporaryDirectory() as t:
            a=old.process_lineart(pic(),t,target='sticker')
            b=choice.process_choice(pic(),t,target='sticker')
            self.assertEqual(Path(a['image']).read_bytes(),Path(b['recommended_file']).read_bytes())

    def test_export_failure_does_not_leave_partial_choice_folder(self):
        with tempfile.TemporaryDirectory() as t:
            with patch.object(choice,'svg_draw_centerlines',side_effect=OSError('simulated failure')):
                with self.assertRaises(OSError):choice.process_choice(pic(),t)
            for root in Path(t).iterdir():
                self.assertFalse((root/'08_CHOIX_CRICUT').exists())
                self.assertFalse(list(root.glob('.preparation_cricut_*')))

if __name__=='__main__':unittest.main()
