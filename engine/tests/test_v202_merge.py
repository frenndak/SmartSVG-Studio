"""V20.2 fusion regression: IA cannot silently change all-traits or pen mode."""
import hashlib, importlib, json, sys, tempfile, types, unittest
from pathlib import Path
import cv2, numpy as np, torch
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg_v202_merge_pkg'
if PKG not in sys.modules:
    mod=types.ModuleType(PKG);mod.__path__=[str(ROOT)];sys.modules[PKG]=mod
ai=importlib.import_module(PKG+'.lineart_ai_v202')
node=importlib.import_module(PKG+'.node_v202')
legacy=importlib.import_module(PKG+'.cricut_choice_v2012')

def scene():
    a=np.full((320,260,3),255,np.uint8)
    cv2.ellipse(a,(130,100),(66,77),0,0,360,(0,0,0),3)
    cv2.line(a,(75,180),(48,315),(0,0,0),4)
    cv2.line(a,(190,180),(211,315),(0,0,0),4)
    cv2.circle(a,(110,100),8,(0,0,0),2)
    return a

def mask():
    a=np.zeros((320,260),np.uint8)
    cv2.ellipse(a,(130,105),(70,80),0,0,360,255,-1)
    cv2.rectangle(a,(78,173),(184,310),255,-1)
    return a

class TestMerge(unittest.TestCase):
    def test_old_v2012_registered(self):
        self.assertIn('SmartSVGLineArtV2012',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGStudioV20Express',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGLineArtV202',node.NODE_CLASS_MAPPINGS)
    def test_new_widget_selection(self):
        req=node.SmartSVGLineArtV202.INPUT_TYPES()['required']
        self.assertIn('operation_cricut',req)
        self.assertIn('largeur_finale_mm',req)
        self.assertEqual(req['operation_cricut'][0],list(legacy.OPTIONS))
    def test_ia_print_not_ink_svg(self):
        with tempfile.TemporaryDirectory() as t:
            r=ai.process_lineart_ai(scene(),t,masks=mask(),ia='desactiver',
                                     operation='imprimer_decouper_contour')
            self.assertTrue(Path(r['fichier_mode_choisi']).exists())
            self.assertEqual(r['mode_choisi_provenance'],'MASQUE_IA_CANDIDAT_A_VERIFIER')
            self.assertTrue(r['fichier_mode_choisi'].endswith('01_IMPRIMER_DECOUPER_CONTOUR_IA_A_VERIFIER.png'))
            self.assertFalse(r['report']['pret_cricut_sans_verification'])
            self.assertTrue(Path(r['root'],'08_CHOIX_CRICUT','03_DECOUPER_CHAQUE_TRAIT.svg').exists())
            self.assertEqual(np.asarray(Image.open(r['fichier_mode_choisi'])).shape[2],4)
    def test_ia_cut_uses_svg_with_physical_mm(self):
        with tempfile.TemporaryDirectory() as t:
            r=ai.process_lineart_ai(scene(),t,masks=mask(),ia='desactiver',
                                     operation='decouper_contour_seul',width_mm=85)
            self.assertTrue(r['fichier_mode_choisi'].endswith('02_DECOUPER_CONTOUR_IA_A_VERIFIER.svg'))
            from xml.etree import ElementTree as ET
            root=ET.parse(r['fichier_mode_choisi']).getroot()
            self.assertTrue(root.get('width').endswith('mm'))
            self.assertAlmostEqual(float(root.get('width').removesuffix('mm')),
                r['report']['largeur_silhouette_ia_mm'],places=3)
    def test_ia_cannot_change_all_ink(self):
        with tempfile.TemporaryDirectory() as t:
            r=ai.process_lineart_ai(scene(),t,masks=mask(),ia='desactiver',
                                     operation='decouper_tous_les_traits')
            self.assertEqual(r['mode_choisi_provenance'],'GEOMETRIQUE_OU_TRAITS_V20_1_2')
            self.assertTrue(r['fichier_mode_choisi'].endswith('03_DECOUPER_CHAQUE_TRAIT.svg'))
            self.assertEqual(Path(r['fichier_mode_choisi']).read_bytes(),
                             Path(r['root'],'08_CHOIX_CRICUT','03_DECOUPER_CHAQUE_TRAIT.svg').read_bytes())
    def test_ia_does_not_modify_base_print_vs_v2012(self):
        with tempfile.TemporaryDirectory() as t:
            old=legacy.process_choice(scene(),t,operation='imprimer_decouper_contour')
            new=ai.process_lineart_ai(scene(),t,masks=mask(),ia='desactiver')
            self.assertEqual(Path(old['recommended_file']).read_bytes(),
                             Path(new['base']['recommended_file']).read_bytes())
    def test_no_ia_fallback_reports_geometric_draft(self):
        with tempfile.TemporaryDirectory() as t:
            def absent(*a,**k):raise RuntimeError('models missing')
            r=ai.process_lineart_ai(scene(),t,ia='auto',segmenter=absent,analyse_florence='desactiver')
            self.assertIsNone(r['image_candidat'])
            self.assertEqual(r['mode_choisi_provenance'],'GEOMETRIQUE_OU_TRAITS_V20_1_2')
            self.assertTrue(Path(r['fichier_mode_choisi']).exists())
            self.assertIn('AUCUN_CONTOUR_IA_EXPORTABLE',r['report']['avertissements'])
    def test_new_comfy_node_returns_choice(self):
        t=torch.from_numpy(scene().astype(np.float32)/255.)[None]
        with tempfile.TemporaryDirectory() as temp:
            result=node.SmartSVGLineArtV202().run(t,temp,operation_cricut='decouper_tous_les_traits',
                        masques_objets=torch.from_numpy(mask()[None]),segmentation_ia='desactiver')
            report=json.loads(result['result'][1]);self.assertEqual(report['choix_cricut']['operation_choisie'],'decouper_tous_les_traits')
            self.assertTrue(report['fichier_mode_choisi'].endswith('.svg'))
    def test_out_of_range_input_prevents_writes(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ai.LineArtSegmentationError):
                ai.process_lineart_ai(scene(),t,operation='invalid')
            self.assertEqual(list(Path(t).iterdir()),[])
    def test_external_mask_zero_alpha_source_unchanged(self):
        img=np.dstack([scene(),np.full((320,260),150,np.uint8)])
        with tempfile.TemporaryDirectory() as t:
            r=ai.process_lineart_ai(img,t,masks=mask(),ia='desactiver')
            np.testing.assert_array_equal(np.asarray(Image.open(Path(r['root'],'01_SOURCE','original_RGBA.png'))),img)
    def test_source_vs_card_mask_shape_validation(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ai.LineArtSegmentationError):
                ai.process_lineart_ai(scene(),t,masks=np.zeros((25,28),np.uint8),ia='desactiver')
            self.assertEqual(list(Path(t).iterdir()),[])
    def test_no_fake_ia_on_blank_source(self):
        blank=np.full((120,135,3),255,np.uint8)
        with tempfile.TemporaryDirectory() as t:
            r=ai.process_lineart_ai(blank,t,ia='desactiver')
            self.assertFalse(r['report']['masque_ia_produit'])
            self.assertTrue(Path(r['fichier_mode_choisi']).exists())

if __name__=='__main__':unittest.main()
