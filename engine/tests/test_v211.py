"""V21.1 independent audit regressions; no AI weights or Cricut hardware used."""
import hashlib
import importlib
import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import cv2
import numpy as np
import torch
from PIL import Image
import sys,types
ROOT=Path(__file__).resolve().parents[1]
if 'sv211test' not in sys.modules:
    p=types.ModuleType('sv211test');p.__path__=[str(ROOT)];sys.modules[p.__name__]=p
prod=importlib.import_module('sv211test.production_v211')
node=importlib.import_module('sv211test.node_v211')
legacy=importlib.import_module('sv211test.multi_subject_v21')
old=importlib.import_module('sv211test.hd_multisticker_v206')

def scene(edge=False):
    rgb=np.full((175,600,3),230,np.uint8)
    mask=np.zeros((175,600),np.uint8)
    cv2.rectangle(rgb,(0 if edge else 30,12),(580,160),(25,150,230),-1)
    cv2.rectangle(mask,(0 if edge else 30,12),(580,160),1,-1)
    return rgb,mask

def grid24():
    img=np.zeros((400,600,3),np.uint8)
    for i in range(4):
        for j in range(6):cv2.circle(img,(50+j*100,50+i*100),22,(130,180,230),-1)
    return img

class Audit(unittest.TestCase):
    def test_baseline_aliases_preserved(self):
        for key in ('SmartSVGSimpleV21','SmartSVGSimpleV206','SmartSVGLineArtV205','SmartSVGExpressV211'):
            self.assertIn(key,node.NODE_CLASS_MAPPINGS)

    def test_five_express_controls_plus_image(self):
        self.assertEqual(len(node.SmartSVGExpressV211.INPUT_TYPES()['required']),6)
        self.assertIn('masques_objets',node.SmartSVGExpressV211.INPUT_TYPES()['optional'])

    def test_all_easy_projects_available(self):
        self.assertEqual(len(node.PROJETS),5)
        self.assertIn('Planche - 24 images (6x4)',node.PROJETS)

    def test_large_mask_refused_without_copy(self):
        class Fake:
            shape=(32,2000,2000)
            dtype='torch.float32'
            def detach(self):raise AssertionError('GPU copy before validation')
        with self.assertRaises(prod.StudioError):prod.preflight_masks(Fake(),(2000,2000))

    def test_misaligned_mask_refused_without_copy(self):
        class Fake:
            shape=(1,9,11)
            dtype='torch.float32'
            def detach(self):raise AssertionError('No copy')
        with self.assertRaises(prod.StudioError):prod.preflight_masks(Fake(),(12,11))

    def test_01_masks_uint_supported(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as t:
            r,_=prod.run_v211(rgb,t,masks=m)
            self.assertEqual(r['nombre_objets_exportes'],1)

    def test_mask_duplicate_suppressed(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as t:
            r,_=prod.run_v211(rgb,t,masks=np.stack([m,m]))
            self.assertEqual(r['nombre_objets_exportes'],1)

    def test_invalid_mask_no_output_folder(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(Exception):prod.run_v211(rgb,t,masks=m[:10,:])
            self.assertEqual(list(Path(t).iterdir()),[])

    def test_force_none_does_not_fallback(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(prod.StudioError):
                prod.run_v211(rgb,t,profile='affiche',segmentation='forcer',
                              provider=lambda *_:{'masks':None,'audit':{}},gpu={'mock':True})
            self.assertFalse(list(Path(t).iterdir()))

    def test_optional_none_explicit_fallback(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as t:
            r,_=prod.run_v211(rgb,t,profile='affiche',segmentation='si_disponible',
                              provider=lambda *_:{'masks':None,'audit':{}},gpu={'mock':True})
            self.assertEqual(r['v21']['mode'],'REPLI_V20_6_SANS_MASQUE')
            self.assertTrue(Path(r['dossier']).exists())

    def test_force_rectangle_rejected(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(prod.StudioError):
                prod.run_v211(rgb,t,profile='affiche',operation='carte_rectangle',segmentation='forcer')

    def test_physical_size_matches_dpi_for_native_large_source(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as t:
            r,_=prod.run_v211(rgb,t,masks=m,width_mm=40,dpi=300)
            obj=r['objets'][0];v=obj['controle_physique_v211']
            self.assertLess(abs(v['largeur_png_mm_si_ppp_respectes']-v['largeur_svg_mm']),.08)
            self.assertLess(v['largeur_png_px'],600)
            self.assertAlmostEqual(float(re.search(r'width="([\d.]+)mm"',Path(obj['fichier_svg_contour']).read_text()).group(1)),v['largeur_svg_mm'],delta=.1)

    def test_legacy_has_mismatch_to_guard_regression(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as t:
            r,_=legacy.run_v21(rgb,t,masks=m,width_mm=40,dpi=300)
            obj=r['objets'][0]
            with Image.open(obj['fichier_png_cricut']) as f:
                self.assertGreater(f.width*25.4/300-obj['largeur_finale_avec_marge_mm'],5)

    def test_450_ppi_physical_size(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as t:
            r,_=prod.run_v211(rgb,t,masks=m,width_mm=45,dpi=450)
            v=r['objets'][0]['controle_physique_v211']
            self.assertLess(abs(v['largeur_png_mm_si_ppp_respectes']-v['largeur_svg_mm']),.08)

    def test_native_transparency_retained(self):
        rgb,m=scene()
        rgba=np.dstack((rgb,np.full(rgb.shape[:2],140,np.uint8)))
        with tempfile.TemporaryDirectory() as t:
            r,_=prod.run_v211(rgba,t,masks=m)
            p=r['objets'][0]['fichier_transparent']
            with Image.open(p) as im:
                self.assertIn(140,np.asarray(im.getchannel('A')))

    def test_border_white_halo_exists_when_subject_at_source_edge(self):
        rgb,m=scene(edge=True)
        with tempfile.TemporaryDirectory() as t:
            r,_=prod.run_v211(rgb,t,masks=m,width_mm=40)
            with Image.open(r['objets'][0]['fichier_png_cricut']) as im:
                a=np.asarray(im.getchannel('A'))
            self.assertFalse(a[:,0].any())
            self.assertTrue(a[:,5].any())

    def test_no_mask_png_and_svg_reconciled(self):
        rgb,_=scene()
        with tempfile.TemporaryDirectory() as t:
            r,_=prod.run_v211(rgb,t,profile='affiche',width_mm=40)
            v=r['objets'][0]['controle_physique_v211']
            self.assertLess(abs(v['largeur_png_mm_si_ppp_respectes']-v['largeur_svg_mm']),.1)

    def test_two_masks_files_and_pages(self):
        rgb,m=scene()
        masks=np.stack([np.where(np.indices(m.shape)[1]<300,m,0),np.where(np.indices(m.shape)[1]>=300,m,0)])
        with tempfile.TemporaryDirectory() as t:
            r,_=prod.run_v211(rgb,t,masks=masks,width_mm=30)
            self.assertEqual(len(r['objets']),2)
            self.assertTrue(r['planches'])
            for o in r['objets']:
                self.assertTrue(Path(o['fichier_png_cricut']).exists())
                self.assertTrue(Path(o['fichier_svg_contour']).exists())

    def test_grid_24_complete_after_repage(self):
        with tempfile.TemporaryDirectory() as t:
            r,_=prod.run_v211(grid24(),t,profile='planche_multi',width_mm=30,dpi=300)
            self.assertEqual(r['nombre_objets_exportes'],24)
            self.assertEqual(len(r['planches_cricut']),2)
            self.assertTrue(all(Path(x['fichier']).exists() for x in r['planches_cricut'] if x['fichier']))

    def test_no_temporary_paths_in_final_json(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as t:
            r,_=prod.run_v211(rgb,t,masks=m)
            full=Path(r['dossier'],'RAPPORT_V21_1.json').read_text()
            self.assertNotIn('.v211_audit_',full)
            self.assertIn(str(r['dossier']),full)

    def test_legacy_named_reports_do_not_contradict_new_sizes(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as t:
            r,_=prod.run_v211(rgb,t,masks=m)
            a=json.loads(Path(r['dossier'],'RAPPORT_V21.json').read_text())
            b=json.loads(Path(r['dossier'],'RAPPORT_V21_1.json').read_text())
            self.assertEqual(a['objets'][0]['controle_physique_v211'],b['objets'][0]['controle_physique_v211'])

    def test_stage_cleaned_after_success(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as t:
            prod.run_v211(rgb,t,masks=m)
            self.assertTrue(all(not x.name.startswith('.v211_audit_') for x in Path(t).iterdir()))

    def test_stage_cleaned_after_failure(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as t:
            with patch.object(prod,'_reconcile_report',side_effect=RuntimeError('simulated write failure')):
                with self.assertRaises(RuntimeError):prod.run_v211(rgb,t,masks=m)
            self.assertFalse(list(Path(t).iterdir()))

    def test_reports_include_warning_not_cut_certification(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as t:
            r,_=prod.run_v211(rgb,t,masks=m)
            self.assertFalse(r['controle_v211']['nouvelles_decoupes_certifiees'])
            self.assertTrue(r['controle_v211']['taille_reelle_dans_design_space_a_verifier'])

    def test_easy_node_tensor_and_human_summary(self):
        rgb,m=scene()
        x=torch.from_numpy(rgb.astype(np.float32)/255)[None]
        with tempfile.TemporaryDirectory() as t:
            ret=node.SmartSVGExpressV211().run(x,t,projet=node.PROJETS[4])
            self.assertEqual(ret['result'][0].ndim,4)
            self.assertIn('A VERIFIER',ret['result'][1])
            self.assertIn('Dossier :',ret['result'][1])

    def test_easy_node_rejects_unknown_option(self):
        x=torch.zeros((1,10,10,3))
        with self.assertRaises(prod.StudioError):node.SmartSVGExpressV211().run(x,projet='inconnu')

    def test_source_image_persisted_verbatim_png(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as t:
            r,_=prod.run_v211(rgb,t,masks=m)
            with Image.open(Path(r['dossier'])/'SOURCE_ORIGINALE.png') as f:
                self.assertTrue(np.array_equal(rgb,np.asarray(f)))

if __name__=='__main__':unittest.main()
