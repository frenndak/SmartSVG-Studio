"""V21.14: empirical fidelity, safety and isolation of old Cricut outputs."""
from __future__ import annotations
import importlib,sys,types,unittest,json,tempfile,xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch
import numpy as np,torch,cv2
ROOT=Path(__file__).resolve().parents[1]
if 'v2114test' not in sys.modules:
    package=types.ModuleType('v2114test');package.__path__=[str(ROOT)];sys.modules[package.__name__]=package
vector=importlib.import_module('v2114test.smartsvg_vector.layers_v2113')
modern=importlib.import_module('v2114test.smartsvg_vector.recovery_v2114')
qa=importlib.import_module('v2114test.smartsvg_vector.qa_v21131')
node=importlib.import_module('v2114test.node_v2114')
old=importlib.import_module('v2114test.node_v21132')

def sample():
    im=np.full((160,200,3),255,np.uint8); mask=np.zeros((160,200),np.float32)
    cv2.ellipse(mask,(90,80),(56,50),0,0,360,1,-1)
    cv2.ellipse(im,(90,80),(56,50),0,0,360,(40,180,60),-1)
    cv2.circle(im,(100,80),23,(200,60,120),-1)
    return im,mask

class TestV2114(unittest.TestCase):
    def test_underlay_is_real_editable_geometry(self):
        im,mask=sample()
        xml,preview,info,picture,quality=modern.vectorize_recovered(im,mask,colors=4)
        self.assertFalse(b'<image' in xml or b'data:image' in xml)
        root=ET.fromstring(xml)
        layers=root.findall('{http://www.w3.org/2000/svg}g')
        self.assertTrue(all(len(g.findall('{http://www.w3.org/2000/svg}path'))>0 for g in layers))
        self.assertTrue(info['sous_couche_silhouette_ajoutee'])
        self.assertEqual(info['formes'],quality['formes_reconstruites'])
        self.assertFalse(info['cricut_svg_multicouche_pret_a_decouper'])
        self.assertGreaterEqual(info['fidelite_silhouette_apres']+.001,info['fidelite_silhouette_avant'])

    def test_quality_color_tradeoff_explicit(self):
        im,mask=sample()
        xml,_,audit,_,quality=modern.vectorize_recovered(im,mask)
        self.assertIn('erreur_couleur_avant',audit)
        self.assertIn('erreur_couleur_apres',audit)
        self.assertIn('risques_decoupe',audit)
        self.assertFalse(audit['risques_decoupe']['certification_decoupe_cricut'])
        self.assertEqual(audit['risques_decoupe']['calques'],audit['calques_couleur'])
        self.assertIn('anneaux_fins_a_verifier',audit['risques_decoupe'])

    def test_repeated_execution_identical_and_rng_unchanged(self):
        im,mask=sample()
        np.random.seed(66231);expect=np.random.random();np.random.seed(66231)
        a=modern.vectorize_recovered(im,mask)[0]
        self.assertEqual(expect,np.random.random())
        b=modern.vectorize_recovered(im,mask)[0]
        self.assertEqual(a,b)

    def test_bad_mask_refused(self):
        im,mask=sample()
        for m in (np.full((160,200),np.nan,dtype=np.float32),np.zeros((200,160),dtype=np.float32),np.ones((160,200),dtype=np.float32)):
            with self.subTest(m=m.shape),self.assertRaises((ValueError,vector.VectorizationRefused)):
                modern.vectorize_recovered(im,m)

    def test_nonexistent_renderer_fallback_is_not_certified(self):
        im,mask=sample()
        with patch.object(qa,'_standard_render',return_value=None),patch.object(modern,'_standard_render',return_value=None):
            xml,_,info,_,quality=modern.vectorize_recovered(im,mask)
        self.assertFalse(quality['rendu_standard_verifie'])
        self.assertFalse(info['couleur_choisie_par_rendu_svg_standard'])
        self.assertEqual(quality['diagnostic'],'A_VERIFIER')

    def test_old_vectorizer_stays_identical(self):
        im,mask=sample()
        a=vector.vectorize_flat_art(im,mask,colors=5)
        modern.vectorize_recovered(im,mask,colors=5)
        b=vector.vectorize_flat_art(im,mask,colors=5)
        self.assertEqual(a[0],b[0])
        np.testing.assert_array_equal(a[1],b[1])

    def test_bounded_file_export_and_legacy_node_identity(self):
        im,mask=sample()
        with tempfile.TemporaryDirectory() as t:
            result=node.SmartSVGEditableColorsV2114().run(
                torch.from_numpy(im.astype(np.float32)/255.)[None],couleurs=5,
                largeur_mm=27.,dossier_sortie=t,masque_sujet=torch.from_numpy(mask[None]))
            self.assertEqual(len(result['result']),4)
            file=Path(result['result'][2]);self.assertTrue(file.exists())
            info=json.loads(result['result'][-1]);self.assertEqual(info['largeur_mm'],27.)
            self.assertIn('risques_decoupe',info)
            self.assertFalse(info['certification_decoupe'])
            self.assertEqual(info['fichier_svg_editable'],str(file))
            self.assertIn('NE PAS utiliser',result['ui']['text'][0])
        for key,cls in old.NODE_CLASS_MAPPINGS.items():
            self.assertIs(node.NODE_CLASS_MAPPINGS[key],cls)
        self.assertEqual(node.SmartSVGEditableColorsV2114.RETURN_TYPES,old.SmartSVGEditableColorsV21132.RETURN_TYPES)
        self.assertEqual(list(node.SmartSVGEditableColorsV2114.INPUT_TYPES()['required']),list(old.SmartSVGEditableColorsV21132.INPUT_TYPES()['required']))

    def test_does_not_modify_legacy_svg_or_cricut_engine(self):
        im,mask=sample();original=vector.vectorize_flat_art(im,mask,colors=8)[0]
        modern.vectorize_recovered(im,mask,colors=8)
        self.assertEqual(original,vector.vectorize_flat_art(im,mask,colors=8)[0])

    def test_qa_rejects_mutated_svg_with_external_attributes(self):
        im,mask=sample();xml,_,audit,_,_=modern.vectorize_recovered(im,mask)
        for unsafe in (xml.replace(b'<g ',b'<g transform="scale(3)" ',1),
                       xml.replace(b'<path ',b'<path opacity="0.1" ',1),
                       xml.replace(b'<svg ',b'<svg onload="evil()" ',1)):
            with self.subTest(unsafe=unsafe[:50]),self.assertRaises(qa.QualityRefused):
                qa._strict_render(unsafe)

if __name__=='__main__':unittest.main()
