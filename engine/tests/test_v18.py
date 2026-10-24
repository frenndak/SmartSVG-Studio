"""Integration + edge-case tests for semantic proposals without GPU."""
from pathlib import Path
from unittest.mock import patch
import importlib
import json
import sys
import tempfile
import types
import unittest

import cv2
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg_v18_tests'
if PKG not in sys.modules:
    pkg=types.ModuleType(PKG);pkg.__path__=[str(ROOT)];sys.modules[PKG]=pkg
eng=importlib.import_module(PKG+'.engine_v18')


def one():
    rgb=np.full((200,300,3),255,np.uint8)
    cv2.circle(rgb,(90,100),51,(45,190,80),-1)
    cv2.circle(rgb,(176,99),49,(220,75,85),-1)
    cv2.circle(rgb,(100,89),8,(20,20,20),-1)
    return rgb


class V18Tests(unittest.TestCase):
    def test_one_print_preserved_and_object_file(self):
        with tempfile.TemporaryDirectory() as t:
            olddir=Path(t)/'old'; newdir=Path(t)/'new'
            old,_=eng.process_v17(one(),str(olddir),ia_mode='desactiver',sheet_width_mm=80)
            latest,_=eng.process_v18(one(),str(newdir),ia_mode='desactiver',sheet_width_mm=80)
            p1=Path(old['output']);p2=Path(latest['output'])
            self.assertEqual((p1/eng.NAME).read_bytes(),(p2/eng.NAME).read_bytes())
            self.assertEqual((p1/eng.CRICUT_SVG).read_bytes(),(p2/eng.CRICUT_SVG).read_bytes())
            self.assertTrue((p2/eng.KIT/'04_MODIFIER_OBJETS_COURBES.svg').is_file())
            q=latest['audit_v18']['objets']
            self.assertEqual(q['nombre_stickers'],1)
            self.assertGreaterEqual(q['objets_proposes'],1)
            self.assertFalse(q['masques_externes_utilises'])
            self.assertTrue(q['version_fidele_groupes']['equivalence_source']['rendu_equivalent_a_la_source'])
            self.assertFalse(q['version_fidele_groupes'].get('repli_original_regions',False))
            self.assertTrue((p2/eng.STATUS).is_file())
            self.assertNotIn('PRET_V17.json', [p.name for p in p2.iterdir()])

    def test_explicit_ai_object_mask_and_name(self):
        rgb=one();mask=np.zeros((1,200,300),np.float32)
        cv2.circle(mask[0],(176,99),49,1,-1)
        with tempfile.TemporaryDirectory() as t:
            report,_=eng.process_v18(rgb,t,object_masks=mask,object_labels='Coquille',
                    object_mode='masques_requis',ia_mode='desactiver',sheet_width_mm=80)
            q=report['audit_v18']['objets']
            self.assertTrue(q['masques_externes_utilises'])
            self.assertGreater(q['objets_proposes'],0)
            txt=(Path(report['output'])/eng.OBJECT_SVG).read_text()
            self.assertIn('Coquille',txt)
            self.assertIn('FOND_RESIDUEL',txt)
            faithful=(Path(report['output'])/eng.OBJECT_FIDELITY).read_text()
            self.assertIn('Coquille',faithful)
            self.assertTrue(q['fidelite_raster']['teste'])

    def test_invalid_mask_fail_closed(self):
        rgb=one()
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(eng.UnsafeCut):
                eng.process_v18(rgb,t,object_masks=np.zeros((1,25,25),np.float32),
                    object_mode='masques_requis',ia_mode='desactiver')
            self.assertFalse(list(Path(t).glob('SmartSVG_V18_*')))
            self.assertTrue(list(Path(t).glob('SmartSVG_ECHEC_V18_*')))

    def test_invalid_mask_auto_rejected_not_silently_resized(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(eng.UnsafeCut,'REPERE_MASQUES_INVALIDE'):
                eng.process_v18(one(),t,object_masks=np.zeros((1,3,3),np.float32),ia_mode='desactiver')
            self.assertFalse(list(Path(t).glob('SmartSVG_V18_1_*')))

    def test_nan_mask_rejected(self):
        with self.assertRaises(ValueError):
            eng._validate_masks(np.full((2,100,80),float('nan')),(100,80))

    def test_workflows_have_valid_connections(self):
        for kind in ('Express','Expert'):
            data=json.loads((ROOT/'example_workflows'/f'SmartSVG_Studio_V18_{kind}.json').read_text())
            nodes={n['id']:n for n in data['nodes']}
            self.assertEqual(sum(n['type']==f'SmartSVGStudioV18{kind}' for n in data['nodes']),1)
            for lid,src,slot,dst,inp,typ in data['links']:
                self.assertEqual(nodes[dst]['inputs'][inp]['link'],lid)
                self.assertEqual(nodes[dst]['inputs'][inp]['type'],typ)
            self.assertTrue(any(i['name']=='masques_objets' for n in data['nodes'] if n['id']==2 for i in n['inputs']))

    def test_multi_sheet_two_elements(self):
        rgb=np.full((270,600,3),255,np.uint8)
        alpha=np.zeros((270,600),np.uint8)
        cv2.ellipse(alpha,(135,135),(70,80),0,0,360,255,-1)
        cv2.ellipse(alpha,(440,135),(75,80),0,0,360,255,-1)
        rgb[alpha>0]=(60,170,220)
        with tempfile.TemporaryDirectory() as t:
            r,_=eng.process_v18(rgb,t,alpha=alpha,ia_mode='desactiver',sheet_width_mm=175)
            q=r['audit_v18']['objets']
            self.assertEqual(q['nombre_stickers'],2)
            self.assertEqual(len(q['par_sticker']),2)

if __name__=='__main__':unittest.main()
