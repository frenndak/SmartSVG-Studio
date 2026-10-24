"""V21.14.1: real renderer quality gate, bounded colors, historical isolation."""
from __future__ import annotations
import importlib,sys,types,tempfile,json,unittest
from pathlib import Path
from unittest.mock import patch
import cv2,numpy as np,torch
R=Path(__file__).resolve().parents[1]
if 'ss21141test' not in sys.modules:
    pkg=types.ModuleType('ss21141test');pkg.__path__=[str(R)];sys.modules[pkg.__name__]=pkg
new=importlib.import_module('ss21141test.smartsvg_vector.color_repair_v21141')
old=importlib.import_module('ss21141test.smartsvg_vector.recovery_v2114')
node=importlib.import_module('ss21141test.node_v21141')
prev=importlib.import_module('ss21141test.node_v2114')
qa=importlib.import_module('ss21141test.smartsvg_vector.qa_v21131')

def art():
    a=np.full((140,170,3),255,np.uint8)
    m=np.zeros(a.shape[:2],np.float32)
    cv2.ellipse(m,(84,72),(51,47),0,0,360,1.,-1)
    cv2.ellipse(a,(84,72),(51,47),0,0,360,(75,196,48),-1)
    cv2.circle(a,(95,80),22,(230,69,124),-1)
    return a,m
class TestColorRepair(unittest.TestCase):
    def test_true_vectors_not_png_and_dialect(self):
        image,mask=art();xml,_,info,_,quality=new.vectorize_color_repaired(image,mask)
        self.assertNotIn(b'<image',xml);self.assertNotIn(b'data:image',xml)
        _,shape=qa._strict_render(xml)
        self.assertEqual(shape['formes_reconstruites'],info['formes'])
        self.assertFalse(info['cricut_svg_multicouche_pret_a_decouper'])
        self.assertFalse(info['validation_dans_design_space'])
        self.assertEqual(info['usage_svg_multicouche'],'EXPERIMENTAL_FORMES_COLOREES_EDITABLES')
    def test_color_error_non_regression_and_mask_coverage(self):
        image,mask=art();xml,_,info,_,q=new.vectorize_color_repaired(image,mask)
        self.assertLessEqual(info['mae_rvb_sur_toute_silhouette_apres'],info['mae_rvb_sur_toute_silhouette_avant']+.001)
        self.assertLessEqual(info['formes_ajoutees_pour_couleur'],12)
        self.assertLessEqual(info['points_ajoutes_pour_couleur'],6500)
        self.assertGreaterEqual(q['iou_silhouette_approx']+.0001,info['fidelite_silhouette_apres'])
    def test_is_deterministic_and_does_not_change_numpy_rng(self):
        image,mask=art();np.random.seed(8141)
        first=np.random.random();np.random.seed(8141)
        a=new.vectorize_color_repaired(image,mask)[0]
        self.assertEqual(first,np.random.random())
        self.assertEqual(a,new.vectorize_color_repaired(image,mask)[0])
    def test_fallback_when_candidate_is_bad(self):
        im,mask=art()
        with patch.object(new,'_candidate_colored_regions',return_value=(None,0,0)):
            xml,_,info,_,_=new.vectorize_color_repaired(im,mask)
        legacy=old.vectorize_recovered(im,mask)[0]
        self.assertEqual(xml,legacy)
        self.assertEqual(info['formes_ajoutees_pour_couleur'],0)
    def test_legacy_source_and_cricut_nodes_not_modified(self):
        for n,cls in prev.NODE_CLASS_MAPPINGS.items():self.assertIs(node.NODE_CLASS_MAPPINGS[n],cls)
        im,mask=art();before=old.vectorize_recovered(im,mask)[0]
        new.vectorize_color_repaired(im,mask)
        self.assertEqual(before,old.vectorize_recovered(im,mask)[0])
    def test_new_comfy_node_4_outputs_and_file(self):
        im,mask=art()
        with tempfile.TemporaryDirectory() as d:
            result=node.SmartSVGEditableColorsV21141().run(
                torch.from_numpy(im.astype(np.float32)/255)[None],
                dossier_sortie=d,masque_sujet=torch.from_numpy(mask[None]),largeur_mm=40.)
            self.assertEqual(len(result['result']),4)
            path=Path(result['result'][2]);self.assertTrue(path.is_file())
            audit=json.loads(result['result'][3]);self.assertIn('mae_rvb_sur_toute_silhouette_apres',audit)
            self.assertFalse(audit['certification_decoupe'])
            self.assertEqual(path.read_bytes()[:5],b'<?xml')
    def test_bad_data_refused_without_export(self):
        im,mask=art()
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                node.SmartSVGEditableColorsV21141().run(
                    torch.full((1,*im.shape),float('nan')),
                    dossier_sortie=d,masque_sujet=torch.from_numpy(mask[None]))
            self.assertFalse(list(Path(d).iterdir()))
    def test_qa_renderer_type_disclosed(self):
        im,mask=art()
        with patch.object(new,'_standard_render',return_value=None),patch.object(old,'_standard_render',return_value=None),patch.object(qa,'_standard_render',return_value=None):
            xml,_,info,_,q=new.vectorize_color_repaired(im,mask)
        self.assertFalse(info['mesure_couleur_rendu_standard'])
        self.assertFalse(q['rendu_standard_verifie'])
    def test_compare_masks_bad_format(self):
        im,mask=art()
        with self.assertRaises((ValueError,new.VectorizationRefused)):
            new.vectorize_color_repaired(im,np.full(mask.shape,np.nan,np.float32))
    def test_palette_limit_and_unchanged_legacy_signature(self):
        self.assertEqual(node.SmartSVGEditableColorsV21141.RETURN_TYPES,
                        prev.SmartSVGEditableColorsV2114.RETURN_TYPES)
        self.assertEqual(list(node.SmartSVGEditableColorsV21141.INPUT_TYPES()['required']),
                         list(prev.SmartSVGEditableColorsV2114.INPUT_TYPES()['required']))
if __name__=='__main__':unittest.main()
