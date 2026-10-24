"""V17: safety/geometry/print-layout smoke checks independent of user ComfyUI."""
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
PKG='smartsvg_v17_tests'
if PKG not in sys.modules:
    pkg=types.ModuleType(PKG)
    pkg.__path__=[str(ROOT)]
    sys.modules[PKG]=pkg
engine=importlib.import_module(PKG+'.engine_v17')


def single():
    rgb=np.full((220,310,3),255,np.uint8)
    cv2.ellipse(rgb,(152,108),(70,60),-4,0,360,(65,175,228),-1)
    cv2.circle(rgb,(140,98),26,(225,100,75),-1)
    return rgb


class V17Checks(unittest.TestCase):
    def test_one_image_proof_and_manifest(self):
        with tempfile.TemporaryDirectory() as t:
            report,_=engine.process_v17(single(),t,sheet_width_mm=90,ia_mode='desactiver')
            q=report['audit_v17'];p=Path(report['output'])
            self.assertEqual(q['nombre_stickers'],1)
            self.assertEqual(len(q['geometrie']['stickers']),1)
            self.assertTrue((p/engine.PROOF).is_file())
            self.assertTrue((p/engine.READY).is_file())
            self.assertFalse((p/'PRET_V16.json').exists())
            data=json.loads((p/engine.READY).read_text())
            self.assertEqual(data['statut'],'PRECONTROLE_GEOMETRIQUE_REUSSI_CRICUT_NON_TESTE')
            self.assertIn(engine.PROOF,data['fichiers'])
            self.assertIn('KIT_IMPORT_CRICUT/01_IMPRIMER_PUIS_DECOUPER.png',data['fichiers'])
            self.assertFalse(list(Path(t).glob('.SmartSVG_V17_TEMP_*')))
            self.assertTrue((p/'00_LIRE_EN_PREMIER_CRICUT.txt').is_file())

    def test_two_stickers_distance_and_alpha(self):
        h,w=310,650
        rgb=np.full((h,w,3),255,np.uint8)
        alpha=np.zeros((h,w),np.uint8)
        cv2.circle(alpha,(110,150),65,255,-1)
        cv2.circle(alpha,(535,150),60,255,-1)
        rgb[alpha>0]=(40,120,220)
        with tempfile.TemporaryDirectory() as t:
            r,_=engine.process_v17(rgb,t,alpha=alpha,ia_mode='desactiver',sheet_width_mm=180)
            self.assertEqual(r['audit_v17']['nombre_stickers'],2)
            self.assertEqual(len(r['audit_v17']['geometrie']['stickers']),2)
            self.assertGreater(r['audit_v17']['geometrie']['distance_minimale_mm'],5)
            with Image.open(Path(r['output'])/engine.NAME) as im:
                self.assertEqual(im.mode,'RGBA')

    def test_narrow_feature_warning_without_failing_export(self):
        img=np.zeros((200,320,4),np.uint8)
        cv2.circle(img,(150,145),42,(160,200,90,255),-1)
        cv2.line(img,(150,103),(150,15),(180,200,100,255),2)
        out=engine._sticker_geometry(img,80,1)
        self.assertTrue(out['stickers'][0]['part_details_fins_heuristique_pct']>0)
        self.assertTrue(any('Details fins' in x for x in out['alertes']))

    def test_sticker_index_matches_exported_files_even_if_raster_labels_differ(self):
        img=np.zeros((170,450,4),np.uint8)
        cv2.circle(img,(90,90),40,(25,140,255,255),-1)
        cv2.circle(img,(355,88),40,(200,90,30,255),-1)
        expected=engine._sticker_geometry(img,90,2,sticker_map={1:2,2:1})
        self.assertEqual([x['sticker'] for x in expected['stickers']],[1,2])
        self.assertEqual([x['composante_raster'] for x in expected['stickers']],[2,1])
        with self.assertRaises(engine.UnsafeCut):
            engine._sticker_geometry(img,90,2,sticker_map={1:1,2:1})

    def test_corrupted_number_of_print_components_rejected(self):
        img=np.zeros((130,290,4),np.uint8)
        cv2.circle(img,(60,65),30,(255,0,0,255),-1)
        cv2.circle(img,(235,65),30,(0,255,0,255),-1)
        with self.assertRaises(engine.UnsafeCut):
            engine._sticker_geometry(img,80,1)

    def test_atomic_rollback_after_v16_failure(self):
        with tempfile.TemporaryDirectory() as t:
            with patch.object(engine,'_proof',side_effect=RuntimeError('ecriture indisponible')):
                with self.assertRaisesRegex(engine.UnsafeCut,'export refuse'):
                    engine.process_v17(single(),t,ia_mode='desactiver')
            self.assertFalse(list(Path(t).glob('SmartSVG_V17_*')))
            self.assertTrue(list(Path(t).glob('SmartSVG_ECHEC_V17_*')))
            self.assertFalse(list(Path(t).glob('.SmartSVG_V17_TEMP_*')))

    def test_v17_workflow_mappings(self):
        import torch
        x=importlib.import_module(PKG+'.node_v17')
        self.assertIn('SmartSVGStudioV16Expert',x.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGStudioV17Express',x.NODE_CLASS_MAPPINGS)
        wf=json.loads((ROOT/'example_workflows'/'SmartSVG_Studio_V17_Express.json').read_text())
        self.assertIn('SmartSVGStudioV17Express',{n['type'] for n in wf['nodes']})
        for _,_,_,nid,inp,typ in wf['links']:
            self.assertEqual(wf['nodes'][nid-1]['inputs'][inp]['type'],typ)


if __name__=='__main__':unittest.main()
