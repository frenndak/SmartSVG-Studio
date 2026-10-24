"""V21.13 vector geometry and per-subject selection, adversarial failure modes."""
import importlib,sys,types,unittest,tempfile,xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch
import numpy as np,torch,cv2
ROOT=Path(__file__).resolve().parents[1]
if 'ss2113_test' not in sys.modules:
    pkg=types.ModuleType('ss2113_test');pkg.__path__=[str(ROOT)];sys.modules[pkg.__name__]=pkg
v=importlib.import_module('ss2113_test.smartsvg_vector.layers_v2113')
n=importlib.import_module('ss2113_test.node_v2113')
old=importlib.import_module('ss2113_test.node_v21122')

def art():
    rgb=np.full((175,230,3),255,np.uint8)
    # Two independent cartoon subjects on a white source.
    cv2.circle(rgb,(60,85),46,(235,54,66),-1)
    cv2.circle(rgb,(60,85),18,(53,79,225),-1)
    cv2.circle(rgb,(165,85),40,(68,204,91),-1)
    cv2.rectangle(rgb,(146,74),(180,102),(235,179,66),-1)
    m=np.zeros((2,175,230),np.float32)
    cv2.circle(m[0],(60,85),46,1,-1)
    cv2.circle(m[1],(165,85),40,1,-1)
    return rgb,m

class TestV2113(unittest.TestCase):
    def test_mask_selection_exact_and_fragments(self):
        rgb,m=art()
        # Deliberately detached small fragment retained in original mask.
        m[1,20:24,205:209]=1
        img=torch.tensor(rgb.copy(),dtype=torch.float32)[None]/255
        mask,meta=n.select_subject(img,torch.tensor(m),2)
        self.assertEqual(tuple(mask.shape),(1,175,230))
        self.assertEqual(meta['indice_selectionne'],2)
        self.assertTrue(meta['fragments_detaches_a_verifier'])
        self.assertEqual(float(mask[0,21,206]),1)
        self.assertEqual(meta['sujets_disponibles'],2)
        with self.assertRaises(ValueError):n.select_subject(img,torch.tensor(m),3)
    def test_wrong_mask_dimensions_rejected(self):
        rgb,m=art();img=torch.tensor(rgb.copy(),dtype=torch.float32)[None]/255
        with self.assertRaises(ValueError):n.select_subject(img,torch.zeros((1,230,175)),1)
    def test_editable_svg_real_groups_no_embedded_raster(self):
        rgb,m=art();xml,preview,qa=v.vectorize_flat_art(rgb,m[0],colors=6,width_mm=45.)
        self.assertLess(preview.shape[0],175)
        self.assertLess(preview.shape[1],230)
        self.assertEqual(qa['taille_originale'],[230,175])
        root=ET.fromstring(xml)
        self.assertEqual(root.tag.rsplit('}',1)[-1],'svg')
        groups=root.findall('{http://www.w3.org/2000/svg}g')
        self.assertGreaterEqual(len(groups),2)
        self.assertEqual(len(groups),qa['calques_couleur'])
        self.assertGreaterEqual(qa['formes'],2)
        self.assertTrue(all(g.attrib['data-smartsvg-layer']=='color' for g in groups))
        self.assertFalse(b'<image' in xml or b'data:image' in xml)
        self.assertFalse(qa['qualite_semantique_certifiee'])
        self.assertFalse(qa['imprimable_identique_original'])
        self.assertEqual(root.attrib['width'],'45mm')
        for g in groups:self.assertTrue(g.findall('{http://www.w3.org/2000/svg}path'))
    def test_svg_openable_and_saves_without_overwrite(self):
        rgb,m=art();svg,_,_=v.vectorize_flat_art(rgb,m[0],colors=5,width_mm=40.)
        with tempfile.TemporaryDirectory() as tmp:
            a=Path(v.save_svg(svg,tmp));b=Path(v.save_svg(svg,tmp))
            self.assertNotEqual(a,b);self.assertEqual(a.read_bytes(),svg)
            self.assertEqual(b.read_bytes(),svg)
            with self.assertRaises(ValueError):v.save_svg(svg,'relative-path')
    def test_photo_complex_rejected_without_fabrication(self):
        rng=np.random.default_rng(17)
        noise=rng.integers(0,255,(320,380,3),dtype=np.uint8)
        mask=np.zeros((320,380),np.float32);cv2.circle(mask,(180,160),112,1,-1)
        with self.assertRaisesRegex(v.VectorizationRefused,'photographique'):
            v.vectorize_flat_art(noise,mask)
    def test_transparent_alpha_with_no_mask(self):
        rgb,m=art();rgba=np.concatenate([rgb, np.uint8(m[0]*255)[:,:,None]],axis=-1)
        svg,_,r=v.vectorize_flat_art(rgba,None)
        self.assertGreater(r['calques_couleur'],1)
    def test_reject_full_rectangular_mask(self):
        rgb,_=art()
        with self.assertRaises(v.VectorizationRefused):v.vectorize_flat_art(rgb,np.ones(rgb.shape[:2]))
    def test_node_outputs_and_svg(self):
        rgb,m=art();image=torch.from_numpy(rgb.astype(np.float32)/255)[None]
        with tempfile.TemporaryDirectory() as td:
            resp=n.SmartSVGEditableColorsV2113().run(image,couleurs=6,largeur_mm=38.,dossier_sortie=td,
                     masque_sujet=torch.tensor(m[:1]))
            result=resp['result'];self.assertEqual(len(result),3)
            self.assertEqual(result[0].shape[0],1)
            self.assertTrue(Path(result[1]).is_file())
    def test_regression_registry_same_objects(self):
        for key,value in old.NODE_CLASS_MAPPINGS.items():self.assertIs(n.NODE_CLASS_MAPPINGS[key],value)
        self.assertIn('SmartSVGAutoExpressV21122',n.NODE_CLASS_MAPPINGS)

if __name__=='__main__':unittest.main()
