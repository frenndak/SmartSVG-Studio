"""V19.5 conservative overlap geometry, no true AI/GPU claims."""
from pathlib import Path
from unittest.mock import patch
import importlib
import json
import sys
import tempfile
import types
import unittest
import hashlib

import cv2
import numpy as np
from PIL import Image
import torch

ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg_v195_testpackage'
if PKG not in sys.modules:
    pkg=types.ModuleType(PKG);pkg.__path__=[str(ROOT)];sys.modules[PKG]=pkg
v=importlib.import_module(PKG+'.photo_contacts_v195')
node=importlib.import_module(PKG+'.node_v195')
legacy=importlib.import_module(PKG+'.photo_detail_v194')


def fixture():
    rgb=np.full((180,280,3),[234,222,201],np.uint8)
    a=np.zeros((180,280),np.uint8)
    b=np.zeros_like(a)
    cv2.circle(a,(106,98),54,255,-1)
    cv2.circle(b,(169,98),54,255,-1)
    rgb[a>0]=[88,160,231]
    rgb[b>0]=[200,78,35]
    return rgb,a,b

class TestContacts(unittest.TestCase):
    def test_pairwise_geometry(self):
        rgb,a,b=fixture()
        q=v.analyze_overlaps([a,b],mm_per_px=.5)
        self.assertEqual(q['nombre_objets'],2)
        self.assertEqual(q['nombre_paires_chevauchantes'],1)
        self.assertGreater(q['pixels_en_commun'],100)
        self.assertAlmostEqual(q['paires'][0]['surface_commune_mm2'], q['pixels_en_commun']*.25,delta=.01)

    def test_no_overlap_and_no_masks(self):
        rgb,a,b=fixture()
        b=np.roll(b,105,axis=1)
        self.assertEqual(v.analyze_overlaps([],mm_per_px=.4)['nombre_objets'],0)
        q=v.analyze_overlaps([a,b],mm_per_px=.4)
        self.assertEqual(q['nombre_paires_chevauchantes'],0)
        out,why=v.propose_exclusive_masks([a,b])
        self.assertIsNone(out)
        self.assertEqual(why['motif'],'aucun chevauchement')

    def test_proposal_has_no_intersection_preserves_unshared(self):
        _,a,b=fixture()
        changed,reason=v.propose_exclusive_masks([a,b])
        self.assertTrue(reason['proposition_valide'])
        self.assertEqual(int(np.count_nonzero((changed[0]>=128)&(changed[1]>=128))),0)
        exclusive_a=(a>=128)&(b<128)
        exclusive_b=(b>=128)&(a<128)
        np.testing.assert_array_equal(changed[0][exclusive_a],a[exclusive_a])
        np.testing.assert_array_equal(changed[1][exclusive_b],b[exclusive_b])
        self.assertGreater(reason['pixels_partages'],0)

    def test_identical_and_near_nested_fail_closed(self):
        _,a,b=fixture()
        for candidate in (a.copy(), cv2.erode(a,np.ones((5,5),np.uint8))):
            out,qa=v.propose_exclusive_masks([a,candidate])
            self.assertIsNone(out)
            self.assertFalse(qa['proposition_valide'])

    def test_invalid_geometry(self):
        _,a,b=fixture()
        with self.assertRaises(v.PhotoExtractionError):v.analyze_overlaps([a,b],0)
        with self.assertRaises(v.PhotoExtractionError):v.analyze_overlaps([a,b[:3]],1)

    def test_original_files_unchanged_conservative(self):
        rgb,a,b=fixture()
        with tempfile.TemporaryDirectory() as td:
            prior,_=legacy.process_photo_v194(rgb,str(Path(td)/'old'),masks=np.stack([a,b]).astype('float32')/255,
                                              labels='person;glass',mode='masques_requis',width_mm=110)
            upgraded,_=v.process_photo_v195(rgb,str(Path(td)/'new'),masks=np.stack([a,b]).astype('float32')/255,
                                            labels='person;glass',mode='masques_requis',width_mm=110)
            old=Path(prior['output']);new=Path(upgraded['output'])
            qa=upgraded['audit_v195'];self.assertGreater(qa['contacts']['pixels_en_commun'],0)
            self.assertEqual(qa['fichiers_experimentaux'],[])
            for item in prior['audit_v19']['objets']:
                for name in ('fichier_rgba','fichier_cricut_test','fichier_masque'):
                    f=item[name]
                    self.assertEqual(hashlib.sha256((old/f).read_bytes()).hexdigest(),hashlib.sha256((new/f).read_bytes()).hexdigest())
            self.assertTrue((new/'PRET_V19_5_2.json').is_file())
            self.assertFalse((new/'PRET_V19_4.json').exists())
            self.assertTrue((new/'CONTROLE_CHEVAUCHEMENTS_V19_5.png').is_file())

    def test_optional_proposals_not_print_ready(self):
        rgb,a,b=fixture()
        with tempfile.TemporaryDirectory() as td:
            rep,_=v.process_photo_v195(rgb,td,masks=np.stack([a,b]).astype('float32')/255,
                                       labels='person;glass',mode='masques_requis',contact_mode='proposer_separation',width_mm=110)
            qa=rep['audit_v195']
            self.assertTrue(qa['proposition_separation']['proposition_valide'])
            self.assertEqual(len(qa['fichiers_experimentaux']),2)
            self.assertFalse(qa['proposition_separation']['pour_cricut_directement'])
            out=Path(rep['output'])
            self.assertFalse(any('CRICUT' in x for x in qa['fichiers_experimentaux']))
            files=[np.asarray(Image.open(out/f).convert('L')) for f in qa['fichiers_experimentaux']]
            self.assertFalse(np.any((files[0]>=128)&(files[1]>=128)))

    def test_fully_identical_masks_no_fake_output(self):
        rgb,a,b=fixture()
        with tempfile.TemporaryDirectory() as td:
            rep,_=v.process_photo_v195(rgb,td,masks=np.stack([a,a]).astype('float32')/255,
                        mode='masques_requis',contact_mode='proposer_separation')
            self.assertEqual(rep['audit_v195']['fichiers_experimentaux'],[])
            self.assertFalse(rep['audit_v195']['proposition_separation']['proposition_valide'])

    def test_empty_photo_no_fake_extract(self):
        rgb,_,_=fixture()
        with tempfile.TemporaryDirectory() as td:
            rep,_=v.process_photo_v195(rgb,td,mode='analyse_seule')
            self.assertEqual(rep['audit_v195']['nombre_objets'],0)
            self.assertEqual(rep['audit_v195']['contacts']['pixels_en_commun'],0)
            self.assertFalse(list(Path(rep['output']).glob('02_OBJETS_PNG/*.png')))

    def test_atomic_failure_does_not_publish(self):
        rgb,a,b=fixture()
        with tempfile.TemporaryDirectory() as td,patch.object(v,'analyze_overlaps',side_effect=RuntimeError('crash simulation')):
            with self.assertRaises(v.PhotoExtractionError):
                v.process_photo_v195(rgb,td,masks=a[None].astype('float32')/255,mode='masques_requis')
            self.assertFalse(list(Path(td).glob('SmartSVG_V19_5_2_PHOTO_*')))
            self.assertTrue(list(Path(td).glob('SmartSVG_ECHEC_V1952_*')))

    def test_node_manual_masks_avoid_auto_models(self):
        rgb,a,b=fixture()
        tensor=torch.from_numpy(rgb.astype('float32')/255).unsqueeze(0)
        m=torch.from_numpy(np.stack([a,b]).astype('float32')/255)
        with tempfile.TemporaryDirectory() as td,patch.object(node,'inspect_scene',side_effect=AssertionError('Florence called')),patch.object(node,'segment_scene',side_effect=AssertionError('SAM called')):
            result,msg=node.SmartSVGStudioV195Express().execute_express(tensor,td,type_fichier='photo',
                                            masques_objets=m,contacts_objets='proposer_separation')
            self.assertIn('V19.5',msg)
            folder=next(Path(td).glob('SmartSVG_V19_5_2_PHOTO_*'))
            self.assertTrue((folder/'QUALITE_DETOURAGE_V19_5_2.json').is_file())

    def test_workflows_match_required_widgets_and_connections(self):
        for mode in ('Express','Expert'):
            data=json.loads((ROOT/'example_workflows'/f'SmartSVG_Studio_V19_5_{mode}.json').read_text())
            smart=next(n for n in data['nodes'] if n['type']==f'SmartSVGStudioV195{mode}')
            required=node.NODE_CLASS_MAPPINGS[f'SmartSVGStudioV195{mode}'].INPUT_TYPES()['required']
            self.assertEqual([x['name'] for x in smart['inputs'] if x.get('widget')],[k for k in required if k!='image'])
            self.assertEqual(len(smart['widgets_values']),len(required)-1)
            for link in data['links']:
                lid,src,slot,dst,idx,typ=link
                target=next(n for n in data['nodes'] if n['id']==dst)
                self.assertEqual(target['inputs'][idx]['link'],lid)
                self.assertEqual(target['inputs'][idx]['type'],typ)

if __name__=='__main__':unittest.main()
