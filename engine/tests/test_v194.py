"""V19.4 QA and conservative alpha edge tests. No real SAM/Florence model."""
from pathlib import Path
from unittest.mock import patch
import importlib,sys,tempfile,types,unittest,json,hashlib
import cv2
import numpy as np
from PIL import Image
import torch
ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg_v194_tests'
if PKG not in sys.modules:
    pkg=types.ModuleType(PKG);pkg.__path__=[str(ROOT)];sys.modules[PKG]=pkg
quality=importlib.import_module(PKG+'.photo_detail_v194')
node=importlib.import_module(PKG+'.node_v194')

def scene():
    rgb=np.full((160,240,3),(235,230,210),np.uint8)
    cv2.circle(rgb,(113,81),42,(40,150,215),-1)
    m=np.zeros(rgb.shape[:2],np.float32)
    cv2.circle(m,(113,81),42,1,-1)
    return rgb,m

class QA(unittest.TestCase):
    def test_structural_metrics(self):
        im,m=scene();cv2.rectangle(m,(25,22),(31,27),1,-1)
        d=quality.inspect_mask(m,mm_per_px=.4)
        self.assertEqual(d['pixels_semi_transparents'],0)
        self.assertEqual(d['composantes_significatives'],2)
        self.assertTrue(d['alertes'])
        self.assertIsNone(d['confiance_ia'])
    def test_boundary_and_hole_warning(self):
        im,m=scene();cv2.circle(m,(113,81),9,0,-1)
        m[0:5,0:6]=1
        d=quality.inspect_mask(m,mm_per_px=.4)
        self.assertTrue(d['touche_bord'])
        self.assertGreater(d['trous_internes'],0)
    def test_guided_filter_bounds_and_preserves_core(self):
        rgb,m=scene()
        out,meta=quality.soften_edges(rgb,m,radius=2)
        self.assertTrue(meta['applique'])
        self.assertEqual(out[80,113],1)
        self.assertEqual(out[0,0],0)
        self.assertTrue(np.all((out>=0)&(out<=1)))
        self.assertLess(np.count_nonzero(np.abs(out-m)>.01),3000)
    def test_soft_mask_preserved(self):
        rgb,m=scene();m[78,156]=.25
        out,meta=quality.soften_edges(rgb,m)
        self.assertFalse(meta['applique'])
        np.testing.assert_array_equal(out,m)
    def test_invalid_data_rejected(self):
        rgb,m=scene()
        for bad in (np.full(m.shape,np.nan),m+10):
            with self.assertRaises(quality.PhotoExtractionError):quality.soften_edges(rgb,bad)
        with self.assertRaises(quality.PhotoExtractionError):quality.inspect_mask(m,mm_per_px=-1)
    def test_legacy_files_never_mutated(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as td:
            result,_=quality.process_photo_v194(rgb,td,masks=m[None],labels='sujet',
                            mode='masques_requis',refinement_mode='bords_doux',width_mm=100)
            folder=Path(result['output']);report=json.loads((folder/'rapport_analyse.json').read_text())
            audit=json.loads((folder/'QUALITE_DETOURAGE_V19_4.json').read_text())
            self.assertEqual(len(audit['qualite_objets']),1)
            self.assertTrue(audit['fichiers_historiques_sha256_preserves'])
            self.assertTrue((folder/'PRET_V19_4.json').exists())
            r=report['objets'][0]
            self.assertTrue((folder/r['fichier_rgba']).exists())
            self.assertTrue((folder/r['fichier_cricut_test']).exists())
            with Image.open(folder/'01_ORIGINAL.png') as im:
                np.testing.assert_array_equal(np.asarray(im.convert('RGB')),rgb)
            generated=audit['qualite_objets'][0]['produits_filtres']
            self.assertEqual(len(generated),2)
            for name in generated:self.assertTrue((folder/name).is_file())
    def test_default_creates_only_audit_not_variants(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as td:
            r,_=quality.process_photo_v194(rgb,td,masks=m[None],mode='masques_requis',width_mm=100)
            folder=Path(r['output'])
            self.assertEqual(json.loads((folder/'QUALITE_DETOURAGE_V19_4.json').read_text())['raffinement'],'conservateur')
            self.assertFalse(list(folder.rglob('*BORDS_DOUX*')))
    def test_no_mask_creates_diagnostic_not_fake_extract(self):
        rgb,_=scene()
        with tempfile.TemporaryDirectory() as td:
            r,_=quality.process_photo_v194(rgb,td,mode='analyse_seule')
            self.assertEqual(r['audit_v194']['nombre_objets'],0)
            self.assertFalse((Path(r['output'])/'02_OBJETS_PNG').exists())
    def test_fail_atomic(self):
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as td,patch.object(quality,'inspect_mask',side_effect=RuntimeError('broken')):
            with self.assertRaises(quality.PhotoExtractionError):
                quality.process_photo_v194(rgb,td,masks=m[None],mode='masques_requis')
            self.assertFalse(list(Path(td).glob('SmartSVG_V19_4_PHOTO_*')))
            self.assertTrue(list(Path(td).glob('SmartSVG_ECHEC_V194_*')))
    def test_node_manual_masks_avoid_models(self):
        rgb,m=scene()
        tensor=torch.from_numpy(rgb.astype('float32')/255).unsqueeze(0)
        mask=torch.from_numpy(m[None])
        with tempfile.TemporaryDirectory() as td,patch.object(node,'inspect_scene',side_effect=AssertionError('Florence called')),patch.object(node,'segment_scene',side_effect=AssertionError('SAM called')):
            result,text=node.SmartSVGStudioV194Express().execute_express(tensor,td,type_fichier='photo',masques_objets=mask,raffinement_contours='bords_doux')
            self.assertIn('SmartSVG V19.4 PHOTO',text)
            folder=next(Path(td).glob('SmartSVG_V19_4_PHOTO_*'))
            self.assertTrue((folder/'QUALITE_DETOURAGE_V19_4.json').is_file())
    def test_workflow_widget_alignment(self):
        for kind in ('Express','Expert'):
            path=ROOT/'example_workflows'/f'SmartSVG_Studio_V19_4_{kind}.json'
            g=json.loads(path.read_text())
            smart=next(n for n in g['nodes'] if n['type']==f'SmartSVGStudioV194{kind}')
            req=node.NODE_CLASS_MAPPINGS[f'SmartSVGStudioV194{kind}'].INPUT_TYPES()['required']
            widgets=[x['name'] for x in smart['inputs'] if x.get('widget')]
            self.assertEqual(widgets,[k for k in req if k!='image'])
            self.assertEqual(len(widgets),len(smart['widgets_values']))
            for link_id,src,slot,dst,idx,typ in g['links']:
                target=next(n for n in g['nodes'] if n['id']==dst)
                self.assertEqual(target['inputs'][idx]['link'],link_id)

if __name__=='__main__':unittest.main()

class ExtraChecks(unittest.TestCase):
    def test_conservative_v193_files_byte_identical(self):
        import hashlib
        previous=importlib.import_module(PKG+'.photo_v19')
        rgb,m=scene()
        with tempfile.TemporaryDirectory() as td:
            a,_=previous.process_photo(rgb,str(Path(td)/'v193'),masks=m[None],mode='masques_requis',width_mm=100)
            b,_=quality.process_photo_v194(rgb,str(Path(td)/'v194'),masks=m[None],mode='masques_requis',width_mm=100)
            one=Path(a['output']);two=Path(b['output'])
            raw=json.loads((one/'rapport_analyse.json').read_text())['objets'][0]
            for file in ['01_ORIGINAL.png',raw['fichier_rgba'],raw['fichier_cricut_test'],raw['fichier_masque']]:
                self.assertEqual(hashlib.sha256((one/file).read_bytes()).digest(),hashlib.sha256((two/file).read_bytes()).digest(),file)
            self.assertEqual(len(list(two.glob('PRET_*.json'))),1)
            self.assertTrue((two/'DIAGNOSTICS_VERSIONS_ANTERIEURES/PRET_V19.json').exists())
    def test_overlaps_risk_retained(self):
        rgb,m=scene(); other=np.roll(m,12,axis=1)
        with tempfile.TemporaryDirectory() as td:
            r,_=quality.process_photo_v194(rgb,td,masks=np.stack([m,other]),width_mm=90,mode='masques_requis')
            self.assertGreater(r['audit_v194']['chevauchement_pixels_masques'],0)
