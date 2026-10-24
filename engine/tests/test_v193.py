"""V19.3 Florence contract and end-to-end mocked Florence/SAM, no checkpoints."""
from pathlib import Path
import importlib,sys,types,tempfile,unittest,json
from unittest.mock import patch
import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg_v193_testpackage'
if PKG not in sys.modules:
    m=types.ModuleType(PKG);m.__path__=[str(ROOT)];sys.modules[PKG]=m
fl=importlib.import_module(PKG+'.scene_florence_v193')
node=importlib.import_module(PKG+'.node_v193')

class FakeFlorence:
    FUNCTION='analyze'
    RETURN_TYPES=('IMAGE','MASK','JSON')
    calls=[]
    data={'bboxes':[[12,14,95,113],[121,31,210,119],[14,14,95,110],[-20,0,0,1]],
          'labels':['woman','gift box','person','unknown']}
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'image':('IMAGE',),'model_name':(['microsoft/Florence-2-base'],),
            'task':(['Phrase Grounding (text boxes)'],),'precision':(['fp16','fp32'],),
            'attention':(['sdpa'],),'fill_mask':('BOOLEAN',)},
            'optional':{'text_prompt':('STRING',{'default':''}),'keep_model_loaded':('BOOLEAN',{'default':False})}}
    def analyze(self,**kw):
        self.calls.append(kw)
        return kw['image'],torch.zeros((1,kw['image'].shape[1],kw['image'].shape[2])),[self.data]

class FlorenceTests(unittest.TestCase):
    def setUp(self):
        FakeFlorence.calls.clear()
        self.im=np.zeros((145,240,3),np.uint8)
    def test_inference_contract_categories_and_dedup(self):
        res=fl.inspect_scene(self.im,registry={'AILab_Florence2':FakeFlorence},profile='personne_cadeaux')
        self.assertEqual(res['prompts'],['person','gift box'])
        self.assertEqual(len(res['detections']),2)
        self.assertIn('person',FakeFlorence.calls[0]['text_prompt'])
        self.assertEqual(FakeFlorence.calls[0]['keep_model_loaded'],False)
        self.assertEqual(res['audit']['confiance'],'non fournie par cette API; aucune probabilite inventee')
    def test_missing_node_is_explicit(self):
        with self.assertRaises(fl.FlorenceUnavailable):fl.inspect_scene(self.im,registry={})
    def test_contract_change_is_explicit(self):
        class Wrong(FakeFlorence):RETURN_TYPES=('MASK',)
        with self.assertRaises(fl.FlorenceUnavailable):fl.inspect_scene(self.im,registry={'AILab_Florence2':Wrong})
    def test_no_fake_classes_or_masks(self):
        v=fl._parse_predictions({'bboxes':[[1,1,120,120],[2,2,100,120]],'labels':['background','random wall']},(145,240),wanted=set(fl.CHOICES['auto']))
        self.assertEqual(v,[])
    def test_invalid_boxes(self):
        rows={'bboxes':[[1,2,3],['bad',2,5,9],[float('nan'),4,8,9],[0,0,120,130]],'labels':['person']*4}
        good=fl._parse_predictions(rows,(145,240),wanted={'person'})
        self.assertEqual(len(good),1)
        for data in ({'boxes':[]},'caption',{'bboxes':[],'labels':['person']}):
            with self.assertRaises(fl.FlorenceUnavailable):fl._parse_predictions(data,(145,240))
    def test_downsample_coordinates(self):
        big=np.zeros((1600,2400,3),np.uint8)
        class Center(FakeFlorence):
            def analyze(self,**kw):
                return kw['image'],None,[{'bboxes':[[100,100,200,200]],'labels':['beer mug']}]
        r=fl.inspect_scene(big,registry={'AILab_Florence2':Center},profile='chopes')
        self.assertEqual(r['audit']['dimension_inference'],[1024,683])
        self.assertAlmostEqual(r['detections'][0]['bbox'][0],100*2400/1024,places=1)
    def test_external_masks_override_models(self):
        tensor=torch.zeros((1,130,210,3));mask=torch.zeros((1,130,210));mask[:,20:100,25:110]=1
        n=node.SmartSVGStudioV193Express()
        with tempfile.TemporaryDirectory() as td,patch.object(node,'inspect_scene',side_effect=AssertionError('no florence')),patch.object(node,'segment_scene',side_effect=AssertionError('no SAM')):
            _,t=n.execute_express(tensor,td,type_fichier='photo',masques_objets=mask,segmentation_objets='auto')
            folder=next(Path(td).glob('SmartSVG_V19_PHOTO_*'))
            report=json.loads((folder/'rapport_analyse.json').read_text('utf8'))
            self.assertEqual(report['nombre_objets_extraits'],1)
            self.assertEqual(report['segmentation_automatique_v192']['analyse_florence_v193']['statut'],'NON_LANCEE')
    def test_florence_guides_sam_real_output_contract_mock(self):
        rgb=np.zeros((125,210,3),np.uint8);tensor=torch.from_numpy(rgb.astype('float32')).unsqueeze(0)
        masks=np.zeros((2,125,210),np.float32);masks[0,10:90,12:90]=1;masks[1,34:110,104:185]=1
        seen=[]
        def plan(*args,**kw):return {'prompts':['person','gift box'], 'detections':[{'label':'person','bbox':[0,0,40,40]}], 'audit':{'statut':'DETECTIONS_CONSERVATRICES'}}
        def sam(*args,**kw):
            seen.append(kw['custom_prompts'])
            return {'masks':masks,'labels':['person','gift box'],'audit':{'masques_acceptes':2,'provider':'FAKE'}}
        n=node.SmartSVGStudioV193Express()
        with tempfile.TemporaryDirectory() as td,patch.object(node,'inspect_scene',side_effect=plan),patch.object(node,'segment_scene',side_effect=sam):
            _,txt=n.execute_express(tensor,td,type_fichier='photo',segmentation_objets='forcer',analyse_florence='forcer')
            folder=next(Path(td).glob('SmartSVG_V19_PHOTO_*'))
            doc=json.loads((folder/'rapport_analyse.json').read_text('utf8'))
            self.assertEqual(seen,['person;gift box'])
            self.assertEqual(doc['nombre_objets_extraits'],2)
            self.assertEqual(doc['segmentation_automatique_v192']['analyse_florence_v193']['statut'],'DETECTIONS_CONSERVATRICES')
    def test_force_no_florence_fails_before_publication(self):
        image=torch.zeros(1,130,210,3)
        with tempfile.TemporaryDirectory() as td,patch.object(node,'inspect_scene',side_effect=fl.FlorenceUnavailable('missing')):
            with self.assertRaisesRegex(RuntimeError,'Florence2 forcee'):
                node.SmartSVGStudioV193Express().execute_express(image,td,type_fichier='photo',analyse_florence='forcer',segmentation_objets='auto')
            self.assertFalse(list(Path(td).glob('SmartSVG_V19_PHOTO_*')))
    def test_auto_fallback_and_explicit_audit(self):
        image=torch.zeros(1,130,210,3)
        def fake_sam(im,**kwargs):
            self.assertEqual(kwargs['custom_prompts'],'')
            return {'masks':None,'labels':[],'audit':{'masques_acceptes':0}}
        n=node.SmartSVGStudioV193Express()
        with tempfile.TemporaryDirectory() as td,patch.object(node,'inspect_scene',side_effect=fl.FlorenceUnavailable('weights absent')),patch.object(node,'segment_scene',side_effect=fake_sam),patch.object(n,'_rmbg_mask',side_effect=RuntimeError('RMBG not available')):
            n.execute_express(image,td,type_fichier='photo',analyse_florence='auto')
            doc=json.loads((next(Path(td).glob('SmartSVG_V19_PHOTO_*'))/'rapport_analyse.json').read_text('utf8'))
            self.assertEqual(doc['nombre_objets_extraits'],0)
            self.assertEqual(doc['segmentation_automatique_v192']['analyse_florence_v193']['statut'],'ECHEC_ANALYSE')
    def test_workflow_wiring(self):
        for flavor in ('Express','Expert'):
            path=ROOT/'example_workflows'/f'SmartSVG_Studio_V19_3_{flavor}.json'
            d=json.loads(path.read_text('utf8'))
            nodes={x['id']:x for x in d['nodes']}
            smart=next(x for x in d['nodes'] if x['type']=='SmartSVGStudioV193'+flavor)
            self.assertIn('analyse_florence',[x['name'] for x in smart['inputs']])
            actual=__import__(PKG+'.node_v193',fromlist=['NODE_CLASS_MAPPINGS']).NODE_CLASS_MAPPINGS[f'SmartSVGStudioV193{flavor}'].INPUT_TYPES()['required']
            widgets=[x['name'] for x in smart['inputs'] if x.get('widget')]
            self.assertEqual(widgets,[k for k in actual if k!='image'])
            self.assertEqual(len(widgets),len(smart['widgets_values']))
            for id_,src,slot,dst,idx,typ in d['links']:
                self.assertEqual(nodes[dst]['inputs'][idx]['link'],id_)
                self.assertEqual(nodes[dst]['inputs'][idx]['type'],typ)

if __name__=='__main__':unittest.main()
