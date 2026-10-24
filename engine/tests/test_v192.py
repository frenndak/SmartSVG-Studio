"""V19.2 SAM2 bridge tests: GPU substituted with registered fake only."""
import importlib,sys,types,tempfile,unittest,json
from pathlib import Path
from unittest.mock import patch
import numpy as np
import torch
from PIL import Image

PKG='smartsvg_v192_testpackage'
ROOT=Path(__file__).resolve().parents[1]
if PKG not in sys.modules:
    mod=types.ModuleType(PKG);mod.__path__=[str(ROOT)];sys.modules[PKG]=mod
bridge=importlib.import_module(PKG+'.auto_segment_v192')
node_mod=importlib.import_module(PKG+'.node_v192')

class FakeSAM2:
    FUNCTION='segment_v2'
    RETURN_TYPES=('IMAGE','MASK','IMAGE')
    calls=[]
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'image':('IMAGE',), 'prompt':('STRING',),
            'sam2_model':(['sam2.1_hiera_tiny'],),
            'dino_model':(['GroundingDINO_SwinT_OGC (694MB)'],),
            'device':(['Auto','CPU','GPU'],)}}
    def segment_v2(self, image, prompt, sam2_model, dino_model, device, **kw):
        self.calls.append(prompt)
        h,w=image.shape[1:3]
        result=torch.zeros(1,h,w)
        if prompt in ('person','gift box','beer mug'):
            if prompt=='person':result[:,15:90,15:75]=1
            elif prompt=='gift box':result[:,35:100,94:151]=1
            elif prompt=='beer mug':result[:,50:100,160:190]=1
        return image,result,image

class FakeBrokenSAM(FakeSAM2):
    def segment_v2(self,image,prompt,**kwargs):
        return image,torch.full((1,image.shape[1],image.shape[2]),float('nan')),image

class SAMBridge(unittest.TestCase):
    def setUp(self):
        self.rgb=np.zeros((125,210,3),np.uint8)
        FakeSAM2.calls.clear()
    def test_registered_node_auto_three_masks(self):
        res=bridge.segment_scene(self.rgb,registry={'SAM2Segment':FakeSAM2})
        self.assertEqual(res['labels'],['person','gift box','beer mug'])
        self.assertEqual(res['masks'].shape,(3,125,210))
        self.assertEqual(res['audit']['masques_acceptes'],3)
        self.assertEqual(FakeSAM2.calls,['person','gift box','beer mug'])
    def test_missing_node_is_explicit(self):
        with self.assertRaisesRegex(bridge.SegmentationUnavailable,'absent'):
            bridge.segment_scene(self.rgb,registry={})
    def test_invalid_api_fails(self):
        class Wrong:
            RETURN_TYPES=('IMAGE','STRING')
            FUNCTION='segment_v2'
            @classmethod
            def INPUT_TYPES(cls):return FakeSAM2.INPUT_TYPES()
        with self.assertRaisesRegex(bridge.SegmentationUnavailable,'incompatible'):
            bridge.segment_scene(self.rgb,registry={'SAM2Segment':Wrong})
    def test_nan_and_bad_geometry_rejected(self):
        for bad in [torch.full((1,125,210),float('nan')),torch.zeros(1,123,210)]:
            with self.assertRaises(bridge.SegmentationUnavailable):
                bridge._mask_from_output((None,bad,None),(125,210))
    def test_empty_no_fake_object(self):
        r=bridge.segment_scene(self.rgb,registry={'SAM2Segment':FakeSAM2},custom_prompts='not_found')
        self.assertIsNone(r['masks'])
        self.assertEqual(r['audit']['masques_acceptes'],0)
    def test_duplicate_masks_deduplicated(self):
        class Duplicate(FakeSAM2):
            def segment_v2(self,image,prompt,**kw):
                h,w=image.shape[1:3]
                arr=torch.zeros(1,h,w);arr[:,20:90,20:120]=1
                return image,arr,image
        r=bridge.segment_scene(self.rgb,registry={'SAM2Segment':Duplicate},custom_prompts='gift box;present')
        self.assertEqual(len(r['labels']),1)
    def test_prompts_capped(self):
        with self.assertRaises(ValueError):bridge.get_prompts(custom='a;b;c;d;e')
    def test_external_mask_priority_and_provenance(self):
        tensor=torch.from_numpy(self.rgb.astype(np.float32)/255).unsqueeze(0)
        ext=torch.zeros((1,125,210),dtype=torch.float32)
        ext[:,20:90,30:100]=1
        n=node_mod.SmartSVGStudioV192Express()
        with tempfile.TemporaryDirectory() as td,patch.object(node_mod,'segment_scene',side_effect=AssertionError('should not run')):
            _,msg=n.execute_express(tensor,td,largeur_planche_mm=90,type_fichier='photo',masques_objets=ext,segmentation_objets='auto')
            rep=list(Path(td).glob('SmartSVG_V19_PHOTO_*/rapport_analyse.json'))
            self.assertEqual(len(rep),1)
            data=json.loads(rep[0].read_text('utf8'))
            self.assertEqual(data['nombre_objets_extraits'],1)
            self.assertEqual(data['objets'][0]['mask_source'],'MASK_ComfyUI_source')
            self.assertIn('objet(s)',msg)
    def test_forced_missing_node_fails_without_publishing(self):
        tensor=torch.from_numpy(self.rgb.astype(np.float32)/255).unsqueeze(0)
        n=node_mod.SmartSVGStudioV192Express()
        with tempfile.TemporaryDirectory() as td, patch.object(node_mod,'segment_scene',side_effect=bridge.SegmentationUnavailable('not installed')):
            with self.assertRaisesRegex(RuntimeError,'Segmentation locale forcee'):
                n.execute_express(tensor,td,type_fichier='photo',segmentation_objets='forcer')
            self.assertFalse(list(Path(td).glob('SmartSVG_V19_PHOTO_*')))
    def test_model_failure_saved_as_diagnostic(self):
        tensor=torch.from_numpy(self.rgb.astype(np.float32)/255).unsqueeze(0)
        n=node_mod.SmartSVGStudioV192Express()
        with tempfile.TemporaryDirectory() as td,patch.object(node_mod,'segment_scene',side_effect=bridge.SegmentationUnavailable('missing')):
            with patch.object(n,'_rmbg_mask',side_effect=RuntimeError('no RMBG')):
                n.execute_express(tensor,td,type_fichier='photo',segmentation_objets='auto')
            p=next(Path(td).glob('SmartSVG_V19_PHOTO_*/rapport_analyse.json'))
            d=json.loads(p.read_text('utf8'))
            self.assertEqual(d['nombre_objets_extraits'],0)
            self.assertEqual(d['segmentation_automatique_v192']['statut'],'ECHEC_MODELE_LOCAL')
    def test_complete_auto_provider_pipeline_on_photo(self):
        tensor=torch.from_numpy(self.rgb.astype(np.float32)/255).unsqueeze(0)
        n=node_mod.SmartSVGStudioV192Express()
        # This is a simulated provider, not an actual neural inference.
        real_bridge=lambda rgb,**kwargs:bridge.segment_scene(rgb,registry={'SAM2Segment':FakeSAM2},**kwargs)
        with tempfile.TemporaryDirectory() as td,patch.object(node_mod,'segment_scene',side_effect=real_bridge):
            _,text=n.execute_express(tensor,td,type_fichier='photo',segmentation_objets='forcer')
            p=next(Path(td).glob('SmartSVG_V19_PHOTO_*/rapport_analyse.json'))
            j=json.loads(p.read_text('utf8'))
            self.assertEqual(j['nombre_objets_extraits'],3)
            self.assertTrue(j['masques_automatiques_sam2'])
            self.assertTrue(all(x['mask_source']=='AUTO_SAM2_DINO_SOURCE' for x in j['objets']))
            for ob in j['objets']:
                self.assertTrue((p.parent/ob['fichier_cricut_test']).is_file())
                self.assertTrue((p.parent/ob['fichier_rgba']).is_file())
            self.assertIn('3 objet(s)',text)

    def test_workflow_wiring(self):
        for kind in ('Express','Expert'):
            j=json.loads((ROOT/'example_workflows'/f'SmartSVG_Studio_V19_2_{kind}.json').read_text('utf8'))
            nodes={n['id']:n for n in j['nodes']}
            smart=nodes[2]
            self.assertEqual(smart['type'],'SmartSVGStudioV192'+kind)
            for id_,src,slot,dst,idx,typ in j['links']:
                self.assertEqual(nodes[dst]['inputs'][idx]['link'],id_)
            self.assertIn('segmentation_objets',[i['name'] for i in smart['inputs']])

if __name__=='__main__':unittest.main()
