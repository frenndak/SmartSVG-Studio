"""V21.2 QA overlay and transaction tests; no actual ML inference claimed."""
import importlib
import json
import re
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
import cv2
import numpy as np
import torch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
if 'sv212test' not in sys.modules:
    x=types.ModuleType('sv212test');x.__path__=[str(ROOT)];sys.modules['sv212test']=x
qa=importlib.import_module('sv212test.controle_export_v212')
prior=importlib.import_module('sv212test.production_v211')
node=importlib.import_module('sv212test.node_v212')

def sample():
    rgb=np.full((160,260,3),255,np.uint8)
    m=np.zeros((160,260),np.uint8)
    cv2.circle(m,(90,81),32,1,-1)
    cv2.circle(rgb,(90,81),32,(60,125,220),-1)
    return rgb,m

class TestV212(unittest.TestCase):
    def test_old_nodes_still_registered(self):
        for name in ('SmartSVGExpressV211','SmartSVGSimpleV21','SmartSVGSimpleV206','SmartSVGLineArtV205'):
            self.assertIn(name,node.NODE_CLASS_MAPPINGS)

    def test_still_five_controls_plus_image(self):
        self.assertEqual(len(node.SmartSVGExpressV212.INPUT_TYPES()['required']),6)
        self.assertIn('masques_objets',node.SmartSVGExpressV212.INPUT_TYPES()['optional'])

    def test_real_export_with_mask(self):
        rgb,m=sample()
        with tempfile.TemporaryDirectory() as t:
            r,_=qa.run_v212(rgb,t,masks=m,width_mm=32)
            q=r['controle_v212']
            self.assertEqual(q['nombre_objets_inspectes'],1)
            self.assertFalse(q['precision_semantique_mesuree'])
            self.assertFalse(q['modele_IA_execute_sur_GPU_local_prouve'])
            self.assertTrue(Path(q['apercu_global']).is_file())
            self.assertTrue(Path(q['objets'][0]['apercu']).is_file())
            self.assertTrue(Path(r['dossier'],'RAPPORT_V21_2.json').is_file())
            self.assertEqual(q['objets'][0]['geometrie_imprimable']['composantes'],1)

    def test_no_mask_no_fake_claim(self):
        rgb,_=sample()
        with tempfile.TemporaryDirectory() as t:
            r,_=qa.run_v212(rgb,t,profile='affiche')
            self.assertIn('REPLI',r['v21']['mode'])
            self.assertFalse(r['controle_v212']['precision_semantique_mesuree'])

    def test_rectangle_never_calls_provider(self):
        rgb,m=sample()
        def fail(*args):raise AssertionError('IA unexpectedly invoked')
        with tempfile.TemporaryDirectory() as t:
            r,_=qa.run_v212(rgb,t,profile='affiche',operation='carte_rectangle',
                             masks=m,provider=fail)
            self.assertEqual(r['v21']['mode'],'CADRE_RECTANGULAIRE_CHOISI')

    def test_v211_print_files_byte_identical(self):
        import hashlib
        rgb,m=sample()
        with tempfile.TemporaryDirectory() as t:
            a,_=prior.run_v211(rgb,t,masks=m,width_mm=33)
            b,_=qa.run_v212(rgb,t,masks=m,width_mm=33)
            for key in ('fichier_png_cricut','fichier_svg_contour','fichier_transparent'):
                p=Path(a['objets'][0][key]);q=Path(b['objets'][0][key])
                self.assertEqual(hashlib.sha256(p.read_bytes()).digest(),hashlib.sha256(q.read_bytes()).digest(),key)

    def test_file_report_no_temporary_paths(self):
        rgb,m=sample()
        with tempfile.TemporaryDirectory() as t:
            r,_=qa.run_v212(rgb,t,masks=m)
            for key in ('RAPPORT_V21_2.json','RAPPORT_V21_1.json','RAPPORT_V21.json'):
                s=Path(r['dossier'],key).read_text()
                self.assertNotIn('.v212_preparation_',s)
                self.assertIn(str(r['dossier']),s)
            self.assertEqual(len(list(Path(t).glob('.*'))),0)

    def test_atomic_rollback_if_qa_crashes(self):
        rgb,m=sample()
        with tempfile.TemporaryDirectory() as t:
            with patch.object(qa,'audit_staged_exports',side_effect=RuntimeError('simulate QA error')):
                with self.assertRaises(RuntimeError):qa.run_v212(rgb,t,masks=m)
            self.assertEqual(list(Path(t).iterdir()),[])

    def test_bad_mask_still_rejected(self):
        rgb,m=sample()
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(Exception):qa.run_v212(rgb,t,masks=m[:-1])
            self.assertEqual(list(Path(t).iterdir()),[])

    def test_mask_duplicates_conservative(self):
        rgb,m=sample()
        with tempfile.TemporaryDirectory() as t:
            r,_=qa.run_v212(rgb,t,masks=np.stack([m,m]))
            self.assertEqual(len(r['objets']),1)
            self.assertEqual(r['controle_v212']['nombre_objets_inspectes'],1)

    def test_source_png_alpha_does_not_disappear(self):
        rgb,m=sample()
        rgba=np.dstack((rgb,np.full(m.shape,160,np.uint8)))
        with tempfile.TemporaryDirectory() as t:
            r,_=qa.run_v212(rgba,t,masks=m)
            with Image.open(r['objets'][0]['fichier_transparent']) as im:
                self.assertIn(160,np.asarray(im.getchannel('A')))

    def test_qa_detects_broken_svg_width(self):
        rgb,m=sample()
        with tempfile.TemporaryDirectory() as t:
            r,_=prior.run_v211(rgb,t,masks=m)
            project=Path(r['dossier']);svg=Path(r['objets'][0]['fichier_svg_contour'])
            svg.write_text(re.sub(r'width="[0-9.]+mm"','width="99mm"',svg.read_text(),count=1))
            audit=qa.audit_staged_exports(project,r,Path(t)/'final',300)
            self.assertIn('ECART_DIMENSION_PNG_SVG',audit['objets'][0]['avertissements'])
            self.assertEqual(audit['objets'][0]['verdict'],'RISQUE_ELEVE')

    def test_rectangle_cut_edge_not_falsely_flagged(self):
        rgb,_=sample()
        with tempfile.TemporaryDirectory() as t:
            r,_=qa.run_v212(rgb,t,profile="affiche",operation="carte_rectangle")
            self.assertNotIn("DECOUPE_TOUCHE_BORD_DU_FICHIER",
                             r["controle_v212"]["objets"][0]["avertissements"])

    def test_qa_warns_when_cut_touches_file_edge(self):
        alpha=np.zeros((50,50),np.uint8);alpha[:,:20]=255
        met=qa._alpha_metrics(alpha)
        self.assertTrue(met['touche_bord_fichier'])

    def test_qa_fragments_and_holes(self):
        m=np.zeros((100,100),np.uint8);cv2.rectangle(m,(10,10),(60,70),255,-1)
        cv2.rectangle(m,(30,30),(40,40),0,-1);m[90:95,90:95]=255
        met=qa._alpha_metrics(m)
        self.assertEqual(met['composantes'],2)
        self.assertGreaterEqual(met['trous'],1)

    def test_prevent_path_escape(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'proj';p.mkdir()
            with self.assertRaises(qa.QAError):qa._safe(p,Path(t)/'outer.png')

    def test_prevent_symlink_file(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'proj';p.mkdir();outside=Path(t)/'outside.png';outside.write_bytes(b'no')
            (p/'fake.png').symlink_to(outside)
            with self.assertRaises(qa.QAError):qa._safe(p,p/'fake.png')

    def test_too_big_png_rejected_before_load(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'big.png';Image.new('RGB',(6000,5000),'white').save(p)
            with self.assertRaises(qa.QAError):qa._read_png(p)

    def test_no_false_gpu_measurements(self):
        rgb,m=sample()
        with tempfile.TemporaryDirectory() as t:
            r,_=qa.run_v212(rgb,t,masks=m)
            self.assertIs(r['controle_v212']['modele_IA_execute_sur_GPU_local_prouve'],False)

    def test_express_output_is_displayable(self):
        rgb,m=sample();x=torch.tensor(rgb.astype(np.float32)/255)[None]
        with tempfile.TemporaryDirectory() as t:
            output=node.SmartSVGExpressV212().run(x,t,masques_objets=torch.tensor(m))
            self.assertEqual(output['result'][0].ndim,4)
            self.assertIn('A VERIFIER AVANT CRICUT',output['result'][1])
            self.assertEqual(json.loads(output['result'][2])['controle_v212']['nombre_objets_inspectes'],1)

    def test_optional_ai_force_fails_without_gpu(self):
        rgb,m=sample()
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(Exception):qa.run_v212(rgb,t,profile='affiche',segmentation='forcer')
            self.assertEqual(list(Path(t).iterdir()),[])

if __name__=='__main__':unittest.main()
