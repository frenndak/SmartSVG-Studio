"""V19 photo extraction, source fidelity, honest fallbacks, ComfyUI routing."""
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

ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg19_testpkg'
if PKG not in sys.modules:
    p=types.ModuleType(PKG);p.__path__=[str(ROOT)];sys.modules[PKG]=p
photo=importlib.import_module(PKG+'.photo_v19')
node=importlib.import_module(PKG+'.node_v19')


def artificial():
    a=np.full((160,230,3),[176,209,229],np.uint8)
    cv2.circle(a,(76,85),38,(30,30,215),-1)
    cv2.rectangle(a,(146,52),(201,127),(195,45,48),-1)
    mask=np.zeros((2,160,230),np.float32)
    cv2.circle(mask[0],(76,85),38,1.,-1)
    cv2.rectangle(mask[1],(146,52),(201,127),1.,-1)
    return a,mask


class TestV19(unittest.TestCase):
    def test_independent_masks_keep_original_pixels(self):
        a,m=artificial()
        with tempfile.TemporaryDirectory() as t:
            result,_=photo.process_photo(a,t,masks=m,labels='rond;rectangle',mode='masques_requis')
            rep=result['audit_v19'];p=Path(result['output'])
            self.assertEqual(rep['nombre_objets_extraits'],2)
            self.assertEqual(rep['statut'],'EXTRACTIONS_A_VALIDER_VISUELLEMENT')
            self.assertTrue(rep['masques_reels_externes'])
            self.assertEqual(np.asarray(Image.open(p/'01_ORIGINAL.png')).tolist(),a.tolist())
            for obj in rep['objets']:
                l,y,r,b=obj['bbox_source_px']
                arr=np.asarray(Image.open(p/obj['fichier_rgba']).convert('RGBA'))
                original=a[y:b,l:r]
                self.assertTrue(np.array_equal(arr[:,:,:3][arr[:,:,3]>0],original[arr[:,:,3]>0]))
                self.assertEqual(arr.shape[:2],(b-y,r-l))
                self.assertTrue((p/obj['fichier_cricut_test']).is_file())
            ready=json.loads((p/'PRET_V19.json').read_text())
            self.assertIn('01_ORIGINAL.png',ready['fichiers'])
            self.assertFalse(list(Path(t).glob('.SmartSVG_V19_TEMP_*')))

    def test_no_model_does_not_fake_segmentation(self):
        with tempfile.TemporaryDirectory() as t:
            r,_=photo.process_photo(artificial()[0],t,mode='auto')
            q=r['audit_v19']
            self.assertEqual(q['nombre_objets_extraits'],0)
            self.assertEqual(q['statut'],'A_VERIFIER_MASQUES_INSUFFISANTS')
            self.assertTrue((Path(r['output'])/'01_ORIGINAL.png').is_file())
            self.assertFalse((Path(r['output'])/'02_OBJETS_PNG').exists())

    def test_rmbg_single_mask_is_not_semantic(self):
        a,m=artificial()
        with tempfile.TemporaryDirectory() as t:
            r,_=photo.process_photo(a,t,mode='auto',foreground_provider=lambda arr: m[0])
            q=r['audit_v19']
            self.assertEqual(q['nombre_objets_extraits'],1)
            self.assertEqual(q['objets'][0]['mask_source'],'RMBG_DETOURAGE_GLOBAL_NON_SEMANTIQUE')
            self.assertEqual(q['objets'][0]['confiance_decoupe'],None)

    def test_forced_provider_error_blocks(self):
        a,_=artificial()
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(photo.PhotoExtractionError):
                photo.process_photo(a,t,require_provider=True,mode='auto',
                    foreground_provider=lambda im:(_ for _ in ()).throw(RuntimeError('failure')))
            self.assertFalse(list(Path(t).glob('SmartSVG_V19_PHOTO*')))
            self.assertEqual(len(list(Path(t).glob('SmartSVG_ECHEC_V19*'))),1)

    def test_guided_box_not_misrepresented_as_ai(self):
        a,_=artificial()
        with tempfile.TemporaryDirectory() as t:
            payload='{"objects":[{"label":"colored disk","bbox":[25,30,124,138]}]}'
            r,_=photo.process_photo(a,t,boxes_json=payload,mode='boites_guidees')
            q=r['audit_v19'];self.assertEqual(q['nombre_objets_extraits'],1)
            self.assertEqual(q['objets'][0]['mask_source'],'GRABCUT_BOITE_GUIDEE_NON_IA')
            self.assertFalse(q['masques_reels_externes'])

    def test_nan_wrong_size_and_out_of_bounds_rejected(self):
        a,m=artificial()
        for invalid in [np.ones((1,10,10)),np.full((1,160,230),np.nan),np.ones((1,160,230))*1.3]:
            with tempfile.TemporaryDirectory() as t:
                with self.assertRaises(photo.PhotoExtractionError):
                    photo.process_photo(a,t,masks=invalid,mode='masques_requis')
        with self.assertRaises(photo.PhotoExtractionError):
            photo._boxes_json('{"objects":[{"bbox":[0,1,340,150]}]}',(160,230))

    def test_overlapping_masks_reported_not_destructively_erased(self):
        a,m=artificial()
        m[1]=m[0]
        with tempfile.TemporaryDirectory() as t:
            r,_=photo.process_photo(a,t,masks=m,labels='one;two')
            q=r['audit_v19'];self.assertGreater(q['chevauchement_pixels'],0)
            self.assertTrue(any('chevauchants' in warn for warn in q['avertissements']))

    def test_photo_and_snails_routing(self):
        from PIL import Image
        for image,expected in [('1000077453.png','photo'),('1000077462.png','photo'),('3411ae50-11b3-4d6a-8eac-851b40d05eb8.jpg','stickers')]:
            p=Path('/mnt/data')/image
            if not p.is_file():continue
            rgb=np.asarray(Image.open(p).convert('RGB'))
            self.assertEqual(node._detect_scene(rgb),expected)

    def test_workflow_valid(self):
        for label in ('Express','Expert'):
            j=json.loads((ROOT/'example_workflows'/f'SmartSVG_Studio_V19_{label}.json').read_text())
            nodes={n['id']:n for n in j['nodes']}
            target=next(n for n in nodes.values() if n['type']==f'SmartSVGStudioV19{label}')
            self.assertIn('type_fichier',[p['name'] for p in target['inputs']])
            for lid,src,slot,dst,input_idx,typ in j['links']:
                self.assertEqual(nodes[dst]['inputs'][input_idx]['link'],lid)
                self.assertEqual(nodes[dst]['inputs'][input_idx]['type'],typ)

if __name__=='__main__':unittest.main()

class AdditionalV19Safety(unittest.TestCase):
    def test_original_png_transparency_not_resurrected(self):
        image=np.full((150,200,3),[30,80,120],np.uint8)
        source_alpha=np.zeros((150,200),np.uint8)
        cv2.circle(source_alpha,(90,75),40,255,-1)
        mask=np.ones((150,200),np.float32)
        with tempfile.TemporaryDirectory() as td:
            r,_=photo.process_photo(image,td,masks=mask,alpha=source_alpha)
            f=Path(r['output'])
            saved=np.asarray(Image.open(f/'01_ORIGINAL.png').convert('RGBA'))
            self.assertTrue(np.array_equal(saved[:,:,3],source_alpha))
            cut=np.asarray(Image.open(f/r['audit_v19']['objets'][0]['fichier_rgba']).convert('RGBA'))
            self.assertLess(cut.shape[1],image.shape[1])

    def test_large_grabcut_guided_rejected_early(self):
        img=np.full((700,700,3),255,np.uint8)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(photo.PhotoExtractionError,'budget CPU'):
                photo.process_photo(img,td,boxes_json='{"objects":[{"bbox":[50,50,450,500]}]}',mode='boites_guidees')
            self.assertFalse(list(Path(td).glob('SmartSVG_V19_PHOTO*')))
