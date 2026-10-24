"""V21.12.1 - routing and classification must be read-only/fail closed.

Includes dark multisticker synthesis and preservation of the old node registry.
"""
import importlib,sys,types,unittest,json,tempfile
from pathlib import Path
from unittest.mock import patch
import numpy as np,torch,cv2
ROOT=Path(__file__).resolve().parents[1]
if 'sv21121unit' not in sys.modules:
    mod=types.ModuleType('sv21121unit');mod.__path__=[str(ROOT)];sys.modules[mod.__name__]=mod
node=importlib.import_module('sv21121unit.node_v21121')
route=importlib.import_module('sv21121unit.smartsvg_ai.routing_v21121')
qa=importlib.import_module('sv21121unit.smartsvg_ai.quality_v21121')
old=importlib.import_module('sv21121unit.node_v2112')

def dark_sheet(rows=2,cols=3,cell=110):
    a=np.full((rows*cell,cols*cell,3),12,dtype=np.uint8)
    for y in range(rows):
        for x in range(cols):
            cv2.ellipse(a,(x*cell+cell//2,y*cell+cell//2),(27,35),0,0,360,
                        (50+25*x,100+22*y,185),-1)
    return a

def tensor(a):return torch.from_numpy(a.astype(np.float32)/255.)[None]

class TestRoutingV21121(unittest.TestCase):
    def test_dark_background_recognized_without_ocr(self):
        a=dark_sheet()
        r=route.inspect_route(a)
        self.assertEqual(r['type_image'],'FOND_NOIR_UNIFORME')
        self.assertFalse(r['texte_extrait_ocr'])
        self.assertFalse(r['contenu_semantique_reconnu'])

    def test_dark_sheet_six_distinct_silhouettes(self):
        m,report=route.dark_sheet_masks(dark_sheet())
        self.assertEqual(m.shape,(6,220,330))
        self.assertFalse(report['certification_semantique'])
        for one in m:
            self.assertEqual(cv2.connectedComponents(np.uint8(one),8)[0]-1,1)

    def test_dark_sheet_auto_does_not_call_provider(self):
        def forbidden(a):raise AssertionError('No GPU on simple background')
        m,info=node.automatic(tensor(dark_sheet()),provider=forbidden)
        self.assertEqual(m.shape[0],6)
        self.assertEqual(info['methode'],'PLANCHE_FOND_NOIR')
        self.assertFalse(info['controle_qualite_v21121']['fidelite_semantique_certifiee'])
        self.assertEqual(info['routage_v21121']['type_image'],'FOND_NOIR_UNIFORME')

    def test_default_loadimage_alpha_sentinel_still_detects_dark_sheet(self):
        img=tensor(dark_sheet())
        sentinel=torch.zeros((1,64,64))
        m,report=node.automatic(img,'Desactivee',alpha_loadimage=sentinel)
        self.assertEqual(m.shape[0],6)
        self.assertEqual(report['routage_v21121']['type_image'],'FOND_NOIR_UNIFORME')

    def test_black_empty_screen_refused(self):
        im=np.full((220,330,3),12,np.uint8)
        m,r=route.dark_sheet_masks(im)
        self.assertIsNone(m)
        self.assertEqual(r['raison'],'DENSITE_AVANT_PLAN_SUSPECTE')
        with self.assertRaises(old.AutoMaskError):node.automatic(tensor(im),'Desactivee')

    def test_dark_picture_with_random_noise_refused(self):
        rng=np.random.default_rng(123)
        im=rng.integers(0,70,(220,330,3),dtype=np.uint8)
        a,r=route.dark_sheet_masks(im)
        self.assertIsNone(a)

    def test_white_artwork_legacy_path_preserved(self):
        im=np.full((220,330,3),255,np.uint8)
        for x in (60,165,270):
            for y in (55,165):cv2.circle(im,(x,y),28,(120,40,185),-1)
        masks,report=node.automatic(tensor(im),'Desactivee')
        self.assertEqual(report['methode'],'ILLUSTRATION_FOND_BLANC')
        self.assertEqual(report['routage_v21121']['type_image'],'FOND_BLANC_UNIFORME')
        self.assertEqual(masks.shape[0],6)

    def test_complex_image_flags_semantic_uncertainty(self):
        a=np.full((240,260,3),65,dtype=np.uint8)
        a[0,:]=120;a[-1,:]=130
        def artificial(img):
            m=np.zeros(img.shape[:2],np.float32);cv2.circle(m,(130,120),60,1,-1)
            return {'masks':m,'audit':{'model':'MOCK'}}
        mask,report=node.automatic(tensor(a),'Obligatoire',provider=artificial)
        q=report['controle_qualite_v21121']
        self.assertEqual(report['methode'],'SEGMENTATION_IA')
        self.assertIn('SUJET_ET_TEXTE_NON_VERIFIES',q['alertes'])
        self.assertFalse(q['fidelite_semantique_certifiee'])

    def test_bad_alpha_not_misidentified_as_completed_cutout(self):
        im=np.full((220,330,3),255,dtype=np.uint8)
        # Equal white image, non-alpha LoadImage has sentinel 64x64.
        with self.assertRaises(old.AutoMaskError):
            node.automatic(tensor(im),'Desactivee',alpha_loadimage=torch.ones((1,64,64)))

    def test_quality_report_has_explicit_non_certified_units(self):
        b=np.zeros((1,220,330),np.float32)
        cv2.circle(b[0],(160,110),35,1,-1)
        r=qa.evaluate_masks(b,kind='FOND_NOIR_UNIFORME',method='PLANCHE_FOND_NOIR',physical_width_mm=50.)
        self.assertEqual(r['nombre_masques'],1)
        self.assertEqual(r['largeur_silhouette_mm'],50.)
        self.assertEqual(r['statut'],'PRECONTROLE_GEOMETRIQUE_SEULEMENT')
        self.assertFalse(r['import_cricut_execute'])

    def test_invalid_dimensions_and_width_rejected(self):
        m=np.ones((1,220,330),np.float32)
        with self.assertRaises(ValueError):qa.evaluate_masks(m,kind='FOND_NOIR_UNIFORME',method='X',physical_width_mm=0.)
        with self.assertRaises(ValueError):route.inspect_route(np.zeros((220,330),np.uint8))

    def test_same_five_express_controls_and_old_registry(self):
        self.assertEqual(list(node.SmartSVGAutoExpressV21121.INPUT_TYPES()['required']),
                         list(old.SmartSVGAutoExpressV2112.INPUT_TYPES()['required']))
        for k,v in old.NODE_CLASS_MAPPINGS.items():self.assertIs(node.NODE_CLASS_MAPPINGS[k],v)

    def test_routing_node_has_no_model_call(self):
        a=tensor(dark_sheet())
        ret=node.SmartSVGRoutingV21121().run(a)
        report=json.loads(ret['result'][1]);self.assertIs(ret['result'][0],a)
        self.assertFalse(report['contenu_semantique_reconnu'])

    def test_no_false_files_on_failure(self):
        img=tensor(np.full((220,330,3),12,np.uint8))
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(old.AutoMaskError):
                node.SmartSVGAutoExpressV21121().run(img,dossier_sortie=folder,ia_locale='Desactivee')
            self.assertFalse(any(Path(folder).iterdir()))

if __name__=='__main__':unittest.main()
