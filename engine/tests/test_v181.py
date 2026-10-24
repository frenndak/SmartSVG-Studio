import importlib,sys,types,unittest,tempfile,json
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
name='smartsvg_v181_tests'; pkg=types.ModuleType(name);pkg.__path__=[str(ROOT)];sys.modules[name]=pkg
mapper=importlib.import_module(name+'.coordinate_mapper')
clf=importlib.import_module(name+'.overlap_assigner')
engine=importlib.import_module(name+'.engine_v18')


def one():
    a=np.full((160,210,3),255,np.uint8);cv2.circle(a,(105,75),45,(160,60,30),-1);return a

class TestCoordinateMapper(unittest.TestCase):
    def test_translation_and_bbox(self):
        c=mapper.CoordinateMapper(np.array([[1,0,12],[0,1,25],[0,0,1.]]),(100,100),(150,150))
        self.assertTrue(np.allclose(c.map_points([[2,3]]),[[14,28]]))
        self.assertTrue(np.allclose(c.inverse().map_points([[14,28]]),[[2,3]]))
        self.assertTrue(np.allclose(c.map_bbox([2,3,4,5]),[14,28,4,5]))
        masks=np.zeros((1,100,100),np.float32);masks[0,20:40,30:50]=1
        transformed=c.warp_masks(masks)
        self.assertEqual(float(transformed.sum()),400.)
        self.assertEqual(float(transformed[0,45,42]),1.)

    def test_rotation_roundtrip(self):
        c=mapper.CoordinateMapper(np.array([[0,-1,99],[1,0,0],[0,0,1.]]),(100,100),(100,100))
        v=np.array([[10,20],[20,50],[56,2]])
        self.assertTrue(np.allclose(c.inverse().map_points(c.map_points(v)),v,atol=1e-6))

    def test_resize_crop_reproject(self):
        c=mapper.CoordinateMapper(np.array([[2.,0,-30],[0,2.,-10],[0,0,1.]]),(50,50),(80,80))
        m=np.zeros((1,50,50),dtype=np.float32);m[0,10:20,20:30]=1
        warped=c.warp_masks(m)
        self.assertEqual(warped.shape,(1,80,80))
        self.assertEqual(warped[0,15,15],1.)

    def test_incompatible_space_explicit_rejection(self):
        masks=np.ones((1,20,20),np.float32)
        with self.assertRaisesRegex(ValueError,'non alignés'):
            mapper.resolve_masks(masks,(20,20),(40,40),space='planche')
        with self.assertRaisesRegex(ValueError,'matrice'):
            mapper.resolve_masks(masks,(20,20),(40,40),space='source')
        reg,info=mapper.resolve_masks(masks,(20,20),(40,40),'source','{"source_vers_planche":[[2,0,0],[0,2,0],[0,0,1]]}')
        self.assertEqual(reg.shape,(1,40,40))
        self.assertEqual(info['statut'],'reprojection_source_vers_planche')

    def test_noninvertible_and_nan_rejected(self):
        with self.assertRaises(ValueError):mapper.CoordinateMapper(np.zeros((3,3)),(2,2),(2,2))
        with self.assertRaises(ValueError):mapper.resolve_masks(np.full((1,5,5),np.nan),(5,5),(10,10),'source','[[2,0,0],[0,2,0],[0,0,1]]')

class TestOverlap(unittest.TestCase):
    def test_long_curve_not_median_misclassification(self):
        path='M 2,2 L 160,2 L 160,16 L 2,16 Z'
        painted=clf.path_mask(path,(25,180))
        a=np.zeros((25,180),bool);a[2:17,2:132]=True
        b=np.zeros_like(a);b[2:17,132:161]=True
        index,diag=clf.assign_by_overlap(painted,[a,b]);self.assertEqual(index,0)
        self.assertGreater(diag['recouvrement_max_pct'],70.)
    def test_ambiguous_overlap_to_residual(self):
        painted=clf.path_mask('M 0,0 L 99,0 L 99,20 L 0,20 Z',(22,100))
        a=np.zeros((22,100),bool);a[:,:50]=True
        b=~a
        index,diag=clf.assign_by_overlap(painted,[a,b]);self.assertEqual(index,-1)
        self.assertEqual(diag['raison'],'indecidable')
    def test_cubic_and_hole(self):
        path='M 5,5 C 10,5 15,10 15,15 L 5,15 Z'
        binary=clf.path_mask(path,(30,30));self.assertTrue(binary.sum()>10)
        self.assertIsNone(clf.path_mask('M 0,0 Q 1,2 5,5 Z',(30,30)))

class TestProcess(unittest.TestCase):
    def test_opaque_highres_photo_early_reject(self):
        im=np.full((1100,1300,3),(96,140,172),np.uint8)
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(engine.UnsafeCut,'SCENE_COMPLEXE_NON_PRISE_EN_CHARGE'):
                engine.process_v18(im,t,ia_mode='desactiver')
            self.assertFalse(list(Path(t).glob('SmartSVG_V18_1_*')))
            self.assertTrue(list(Path(t).glob('SmartSVG_ECHEC_V18_1_*')))

    def test_single_fidelity_and_mask_provenance(self):
        im=one(); mask=np.zeros((1,*im.shape[:2]),np.float32)
        cv2.circle(mask[0],(105,75),28,1,-1)
        with tempfile.TemporaryDirectory() as t:
            r,_=engine.process_v18(im,t,object_masks=mask,mask_space='source',mask_transform_json='[[1,0,0],[0,1,0],[0,0,1]]',object_mode='masques_requis',ia_mode='desactiver',sheet_width_mm=100)
            p=Path(r['output']); info=r['audit_v18']['objets']
            self.assertEqual(info['alignement_masques']['statut'],'reprojection_source_vers_planche')
            self.assertTrue((p/'KIT_IMPORT_CRICUT/01_IMPRIMER_PUIS_DECOUPER.png').is_file())
            self.assertTrue(info['version_fidele_groupes']['ordre_de_peinture_conserve'])
            self.assertEqual(info['version_fidele_groupes']['equivalence_source']['pixels_differents_seuil_15'],0)
            self.assertEqual(info['version_fidele_groupes']['nombre_chemins'],sum(1 for _ in __import__('xml.etree.ElementTree',fromlist=['ElementTree']).parse(p/'CRICUT_EDITION_REGIONS_INDEPENDANTES.svg').getroot().iter('{http://www.w3.org/2000/svg}path')))

if __name__=='__main__':unittest.main()

class TestProvenance(unittest.TestCase):
    def test_all_zero_mask_not_false_success(self):
        im=one()
        with tempfile.TemporaryDirectory() as t:
            r,_=engine.process_v18(im,t,object_masks=np.zeros((1,*im.shape[:2]),np.float32),
                                  mask_space='planche',object_mode='auto',ia_mode='desactiver',sheet_width_mm=100)
            q=r['audit_v18']['objets']
            self.assertFalse(q['masques_externes_utilises'])
            self.assertEqual(q['nombre_stickers_masques_externes_retenus'],0)
            self.assertEqual(q['mode'],'propositions_automatiques_non_semantiques')

    def test_same_resolution_does_not_authorize_source_mapping(self):
        with self.assertRaisesRegex(ValueError,'explicite obligatoire'):
            mapper.resolve_masks(np.ones((1,20,20),np.float32),(20,20),(20,20),space='source')


class TestNodesV181(unittest.TestCase):
    def test_express_workflow_and_single_export(self):
        import torch
        import json
        x=importlib.import_module(name+'.node_v181')
        self.assertIn('SmartSVGStudioV181Express',x.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGStudioV16Expert',x.NODE_CLASS_MAPPINGS)
        for mode in ('Express','Expert'):
            wf=json.loads((ROOT/'example_workflows'/f'SmartSVG_Studio_V18_1_{mode}.json').read_text('utf8'))
            nodes={n['id']:n for n in wf['nodes']}
            self.assertTrue(any(n['type']==f'SmartSVGStudioV181{mode}' for n in nodes.values()))
            for lid,src,slot,dst,inp,kind in wf['links']:
                self.assertEqual(nodes[dst]['inputs'][inp]['link'],lid)
                self.assertEqual(nodes[dst]['inputs'][inp]['type'],kind)
        with tempfile.TemporaryDirectory() as t:
            inp=torch.from_numpy(one().astype('float32')/255).unsqueeze(0)
            preview,message=x.SmartSVGStudioV181Express().execute_express(inp,t,largeur_planche_mm=100,ia_locale='desactiver')
            self.assertIn('Methode reels:',message)
            self.assertEqual(preview.shape[0],1)
            self.assertEqual(len(list(Path(t).glob('SmartSVG_V18_1_*'))),1)
