"""V21: explicit source-aware subject segmentation / fail-safe and old compatibility."""
import importlib
import json
import tempfile
import sys
import types
import unittest
from pathlib import Path
import cv2
import numpy as np
import torch
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
if 'sv21test' not in sys.modules:
    pkg=types.ModuleType('sv21test');pkg.__path__=[str(ROOT)];sys.modules[pkg.__name__]=pkg
core=importlib.import_module('sv21test.multi_subject_v21')
node=importlib.import_module('sv21test.node_v21')
legacy=importlib.import_module('sv21test.hd_multisticker_v206')

def demo():
    src=np.full((180,280,3),[180,210,240],np.uint8)
    cv2.circle(src,(65,80),40,(230,75,60),-1)
    cv2.rectangle(src,(180,40),(245,125),(50,130,200),-1)
    masks=np.zeros((2,180,280),np.float32)
    cv2.circle(masks[0],(65,80),40,1.,-1)
    cv2.rectangle(masks[1],(180,40),(245,125),1.,-1)
    return src,masks

class TestV21(unittest.TestCase):
    def test_inherit_all_old_nodes(self):
        self.assertIn('SmartSVGSimpleV206',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGLineArtV205',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGSimpleV21',node.NODE_CLASS_MAPPINGS)

    def test_seven_simple_choices_and_optional_mask(self):
        d=node.SmartSVGSimpleV21.INPUT_TYPES()
        self.assertEqual(len(d['required']),8)
        self.assertIn('masques_objets',d['optional'])
        self.assertIn('desactiver',d['required']['segmentation_ia'][0])

    def test_uint_zero_one_is_not_blank(self):
        src,m=demo()
        n=core._masks_normalize(m.astype(np.uint8),src.shape[:2])
        self.assertEqual(int(np.count_nonzero(n[0])),int(np.count_nonzero(m[0])))

    def test_uint_zero_255(self):
        _,m=demo()
        n=core._masks_normalize((m*255).astype(np.uint8),(180,280))
        self.assertEqual(n.max(),1.0)

    def test_invalid_integer_levels(self):
        for value in (2,100,256):
            m=np.zeros((180,280),np.uint16);m[10:30,10:30]=value
            with self.assertRaises(core.V21Error):core._masks_normalize(m,(180,280))

    def test_invalid_shape(self):
        _,m=demo()
        with self.assertRaises(core.V21Error):core._masks_normalize(m,(200,280))

    def test_too_many_masks(self):
        with self.assertRaises(core.V21Error):core._masks_normalize(np.zeros((33,20,20)),(20,20))

    def test_non_finite(self):
        m=np.zeros((20,20),np.float32);m[0,0]=float('nan')
        with self.assertRaises(core.V21Error):core._masks_normalize(m,(20,20))

    def test_duplicates_suppressed(self):
        _,m=demo()
        chosen,audit=core._unique_masks(np.stack([m[0],m[0],m[1]]),(180,280))
        self.assertEqual(len(chosen),2)
        self.assertEqual(audit[1]['raison'],'DOUBLON_QUASI_IDENTIQUE')

    def test_blank_mask_is_hard_error(self):
        src,_=demo()
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(core.V21Error):core.run_v21(src,t,masks=np.zeros((180,280)))
            self.assertEqual(list(Path(t).iterdir()),[])

    def test_foreground_preserves_native_color_and_alpha(self):
        src,m=demo()
        m[0][70,65]=.25
        rgba,b=core._subject_crop(src,m[0])
        self.assertEqual(rgba.shape[2],4)
        self.assertEqual(tuple(rgba[70-b[1],65-b[0],:3]),tuple(src[70,65]))
        self.assertGreater(rgba[70-b[1],65-b[0],3],0)
        self.assertLess(rgba[70-b[1],65-b[0],3],255)

    def test_existing_source_alpha_multiplied(self):
        src,m=demo();rgba=np.dstack([src,np.full((180,280),128,np.uint8)])
        crop,b=core._subject_crop(rgba,m[0])
        self.assertEqual(crop[80-b[1],65-b[0],3],128)

    def test_subjects_export_png_and_svg(self):
        src,m=demo()
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v21(src,t,profile='scene_decorative',width_mm=35,masks=m)
            self.assertEqual(r['nombre_objets_exportes'],2)
            self.assertEqual(r['statut'],'MASQUES_DISPONIBLES_CONTOURS_A_VERIFIER')
            for item in r['objets']:
                self.assertEqual(item['nombre_chemins'],1)
                self.assertTrue(Path(item['fichier_png_cricut']).is_file())
                self.assertIn('mm',Path(item['fichier_svg_contour']).read_text())
                with Image.open(item['fichier_transparent']) as im:
                    self.assertEqual(im.mode,'RGBA')
            self.assertTrue(Path(r['dossier'],'RAPPORT_V21.json').is_file())

    def test_soft_mask_survives_native_cutout(self):
        src,m=demo()
        m[0][80,90]=.08
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v21(src,t,masks=m[:1])
            with Image.open(r['objets'][0]['fichier_transparent']) as im:
                al=np.asarray(im.getchannel('A'))
            self.assertTrue(np.any((al>0)&(al<255)))

    def test_overlap_flag_not_erased(self):
        src,m=demo()
        m[1][60:100,70:105]=1
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v21(src,t,masks=m)
            self.assertTrue(r['recouvrements'])
            self.assertTrue(any('OBJET_EN_RECOUVREMENT_VERIFIER' in x['avertissements'] for x in r['objets']))

    def test_masks_external_priority_skips_provider(self):
        src,m=demo()
        def broken(*_):raise AssertionError('AI must never be called')
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v21(src,t,segmentation='forcer',masks=m,provider=broken)
            self.assertEqual(r['nombre_objets_exportes'],2)

    def test_forced_ai_no_gpu_fails(self):
        src,_=demo()
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(core.V21Error):core.run_v21(src,t,segmentation='forcer')

    def test_optional_ai_no_gpu_fallback(self):
        src,_=demo()
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v21(src,t,segmentation='si_disponible',profile='affiche')
            self.assertFalse(r['v21']['masque_ia_obtenu'])

    def test_provider_mocked_and_labeled(self):
        src,m=demo();prompts=[]
        def provider(rgb,prompt):
            prompts.append(prompt)
            return {'masks':m,'audit':{'provider':'TEST_FAKE'}}
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v21(src,t,profile='capture_produit',segmentation='forcer',provider=provider,gpu={'test':True})
            self.assertEqual(prompts,['duck'])
            self.assertEqual(r['nombre_objets_exportes'],2)
            self.assertEqual(r['analyse_ia']['fournisseur']['provider'],'TEST_FAKE')
            self.assertFalse(r['inference_ia_gpu_prouvee'])

    def test_invalid_external_never_fallback(self):
        src,m=demo()
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(core.V21Error):core.run_v21(src,t,masks=m[:,1:,:])
            self.assertFalse(list(Path(t).iterdir()))

    def test_no_mask_preserves_v206_exports(self):
        src,_=demo()
        with tempfile.TemporaryDirectory() as t:
            a,_=legacy.run_v206(src,t,'affiche',40,300)
            b,_=core.run_v21(src,t,profile='affiche',width_mm=40,segmentation='desactiver')
            from hashlib import sha256
            self.assertEqual(sha256(Path(a['objets'][0]['png']).read_bytes()).digest(),
                             sha256(Path(b['objets'][0]['png']).read_bytes()).digest())
            self.assertEqual(sha256(Path(a['objets'][0]['svg_contour']).read_bytes()).digest(),
                             sha256(Path(b['objets'][0]['svg_contour']).read_bytes()).digest())

    def test_24_character_grid_preserved(self):
        src=np.zeros((600,900,3),np.uint8)
        for row in range(4):
            for col in range(6):
                cv2.circle(src,(col*150+75,row*150+75),36,(130,100,240),-1)
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v21(src,t,profile='planche_multi',width_mm=30)
            self.assertEqual(r['nombre_objets_exportes'],24)
            self.assertEqual(len(r['planches_cricut']),2)
            self.assertFalse(r['v21']['separation_semantique_effectuee'])

    def test_multi_masks_pages_fit_limit(self):
        src=np.full((200,200,3),128,np.uint8)
        masks=np.zeros((8,200,200),np.uint8)
        for i in range(8):cv2.circle(masks[i],(20+i*22,100),9,1,-1)
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v21(src,t,masks=masks,width_mm=55)
            self.assertGreaterEqual(len(r['planches']),2)
            for page in r['planches']:
                if 'taille_estimee_mm' in page:
                    w,h=page['taille_estimee_mm']
                    self.assertLessEqual(w,170.5)
                    self.assertLessEqual(h,240.5)

    def test_comfyui_tensor_return(self):
        src,_=demo()
        x=torch.tensor(src.astype(np.float32)/255.)[None]
        with tempfile.TemporaryDirectory() as t:
            out=node.SmartSVGSimpleV21().run(x,t,profil='affiche')
            self.assertEqual(out['result'][0].ndim,4)
            self.assertIn('v21',json.loads(out['result'][1]))

    def test_reject_nan_image(self):
        x=torch.zeros((1,20,20,3));x[0,0,0,0]=float('nan')
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(core.V21Error):node.SmartSVGSimpleV21().run(x,t)

if __name__=='__main__':unittest.main()

class TestV21FailSafe(unittest.TestCase):
    def test_optional_provider_invalid_mask_falls_back(self):
        src,_=demo()
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v21(src,t,profile='affiche',segmentation='si_disponible',
                provider=lambda *_:{'masks':np.zeros((60,60),np.uint8),'audit':{}},gpu={'simulated':True})
            self.assertEqual(r['v21']['analyse_ia']['statut'],'IA_SANS_MASQUE_VALIDE_REPLI')
            self.assertFalse(r['v21']['separation_semantique_effectuee'])

    def test_forced_provider_invalid_mask_fails(self):
        src,_=demo()
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(core.V21Error):
                core.run_v21(src,t,profile='affiche',segmentation='forcer',
                    provider=lambda *_:{'masks':np.zeros((60,60),np.uint8),'audit':{}},gpu={'simulated':True})

class TestV21ExplicitCut(unittest.TestCase):
    def test_rectangle_operation_not_masked_sticker(self):
        src,m=demo()
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v21(src,t,profile='affiche',operation='carte_rectangle',masks=m)
            self.assertEqual(r['v21']['mode'],'CADRE_RECTANGULAIRE_CHOISI')
            self.assertTrue(r['v21']['masques_fournis_ignores'])
            self.assertTrue(Path(r['objets'][0]['png']).name.endswith('CADRE.png'))
            self.assertEqual(len(r['objets']),1)
