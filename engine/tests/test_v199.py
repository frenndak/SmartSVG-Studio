"""V19.9 regression: no downloaded models, simulated external RMBG contract."""
from pathlib import Path
from unittest.mock import patch
import importlib
import json
import sys
import tempfile
import types
import unittest
import cv2
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg_v199_tests'
if PKG not in sys.modules:
    pkg=types.ModuleType(PKG);pkg.__path__=[str(ROOT)];sys.modules[PKG]=pkg
core=importlib.import_module(PKG+'.adaptive_refiner_v199')
node=importlib.import_module(PKG+'.node_v199')

def img(h=160,w=220):
    x=np.full((h,w,3),210,np.uint8)
    cv2.circle(x,(60,80),33,(40,90,210),-1)
    cv2.rectangle(x,(135,54),(175,109),(220,90,45),-1)
    return x

def mask(h=160,w=220):
    a=np.zeros((2,h,w),np.float32)
    cv2.circle(a[0],(60,80),33,1.,-1)
    cv2.rectangle(a[1],(135,54),(175,109),1.,-1)
    return a

class FakeBiRef:
    RETURN_TYPES=('IMAGE','MASK','IMAGE')
    FUNCTION='process_image'
    called=[]
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'image':('IMAGE',),'model':(['Lucida','BiRefNet-portrait'],)},
                'optional':{'background':(['Alpha','Color'],),'unload_model':('BOOLEAN',)}}
    def process_image(self, image, model, **kw):
        self.called.append((model,kw,tuple(image.shape)))
        a=np.zeros((1,image.shape[1],image.shape[2]),np.float32)
        a[:,3:-3,3:-3]=.9
        return image,torch.from_numpy(a),image

class TestsV199(unittest.TestCase):
    def test_image_mask_validation_and_255(self):
        x=img();b=mask()
        np.testing.assert_allclose(core.validate_masks(x,(b*255).astype('uint8')),b)
        for invalid in (np.zeros((1,9,10)),np.full((2,160,220),float('nan')),
                        np.full((2,160,220),300,dtype='int16')):
            with self.assertRaises(core.RefinementError):core.validate_masks(x,invalid)
    def test_diagnostic_no_changes_even_if_provider_differs(self):
        x=img();b=mask()
        out,prop,u,qa=core.adaptive_refine(x,b,model_runner=lambda crop:np.zeros(crop.shape[:2],np.float32),max_passes=2)
        np.testing.assert_array_equal(out,b)
        np.testing.assert_array_equal(prop,b)
        self.assertTrue(qa['candidats'])
        self.assertEqual(qa['appels_modele_reussis'],2)
        self.assertEqual(qa['masques_proposes'],0)
    def test_proposals_without_promotion(self):
        x=img();b=mask();shifts=[cv2.dilate(mm,np.ones((3,3),np.uint8)).astype(np.float32) for mm in b]
        def enlarge(crop):
            # Produces full foreground and is rejected as poor agreement.
            return np.ones(crop.shape[:2],np.float32)
        out,alt,u,qa=core.adaptive_refine(x,b,mode='proposition',model_runner=enlarge)
        np.testing.assert_array_equal(out,b)
        self.assertFalse(qa['selection_modifiee'])
        self.assertGreater(qa['incertitude_pixels'],0)
    def test_perfect_provider_masks_no_false_change(self):
        x=img();b=mask();k=[0]
        def same(crop):
            # Construct the expected original mask from same non-background color.
            return np.any(crop!=210,axis=2).astype(np.float32)
        out,alt,u,qa=core.adaptive_refine(x,b,model_runner=same,min_agreement=.65)
        np.testing.assert_array_equal(out,b)
        self.assertEqual(qa['appels_modele_reussis'],2)
        self.assertTrue(all(s['statut']=='CANDIDAT' for s in qa['candidats']))
    def test_annotation_required(self):
        with self.assertRaisesRegex(core.RefinementError,'Annotation'):
            core.adaptive_refine(img(),mask(),mode='adopter_annotation',model_runner=lambda c:np.zeros(c.shape[:2]))
    def test_supervised_promotes_improved_mask_only(self):
        x=img();gt=mask();bad=gt.copy();bad[0]=cv2.erode(gt[0],np.ones((5,5),np.uint8)); k=[]
        def truth_crop(crop):return np.any(crop!=210,axis=2).astype(np.float32)
        chosen,alt,u,r=core.adaptive_refine(x,bad,annotation=gt,mode='adopter_annotation',model_runner=truth_crop)
        self.assertTrue(np.any(chosen[0]!=bad[0]))
        self.assertTrue(r['selection_modifiee'])
        self.assertTrue(any(c['statut']=='ADOPTE_SUR_ANNOTATION' for c in r['candidats']))
    def test_missing_registry_model_fails_without_fake_mask(self):
        with self.assertRaisesRegex(core.RefinementError,'absent'):
            core.adaptive_refine(img(),mask(),registry={})
    def test_real_registry_contract_mock_and_serial_per_object(self):
        FakeBiRef.called=[]
        chosen,alt,u,r=core.adaptive_refine(img(),mask(),registry={'BiRefNetRMBG':FakeBiRef})
        self.assertEqual(len(FakeBiRef.called),2)
        self.assertTrue(all(k[1].get('unload_model') is True for k in FakeBiRef.called))
        np.testing.assert_array_equal(chosen,mask())
    def test_invalid_registry_return_rejected(self):
        class Bad(FakeBiRef):
            RETURN_TYPES=('MASK',)
        with self.assertRaisesRegex(core.RefinementError,'incompatible'):
            core.adaptive_refine(img(),mask(),registry={'BiRefNetRMBG':Bad})
    def test_runner_nan_caught(self):
        sel,alt,u,r=core.adaptive_refine(img(),mask(),model_runner=lambda c:np.full(c.shape[:2],np.nan))
        self.assertTrue(all(x['statut']=='ECHEC_MODELE' for x in r['candidats']))
        np.testing.assert_array_equal(sel,mask())
    def test_no_unprompted_masks_if_models_missing(self):
        with patch.object(node,'_primary',return_value=(None,{'status':'AUCUN_MASQUE'})):
            with self.assertRaisesRegex(core.RefinementError,'Aucun masque'):
                node.run_adaptive(img(),model_runner=lambda crop:np.zeros(crop.shape[:2]))
    def test_standalone_comfy_contract(self):
        x=torch.from_numpy(img().astype('float32')/255).unsqueeze(0)
        m=torch.from_numpy(mask())
        with patch.object(node,'run_adaptive',return_value=(mask(),mask(),np.zeros((160,220),np.float32),{'version':'19.9-beta'})):
            a,b,u,q=node.SmartSVGAdaptiveV199().run(x,masques_objets=m)
        self.assertEqual(tuple(a.shape),(2,160,220))
        self.assertEqual(tuple(u.shape),(1,160,220))
        self.assertEqual(json.loads(q)['version'],'19.9-beta')
    def test_express_default_delegates_without_refinement(self):
        x=torch.from_numpy(img().astype('float32')/255).unsqueeze(0)
        with patch.object(node.SmartSVGStudioV198Expert,'execute',return_value=(x,'CRICUT')) as fake:
            _,text=node.SmartSVGStudioV199Expert().execute(image=x,raffinement_ia='desactiver')
        self.assertEqual(text,'CRICUT');self.assertEqual(fake.call_count,1)
    def test_express_diagnostic_preserves_source_masks(self):
        x=torch.from_numpy(img().astype('float32')/255).unsqueeze(0)
        m=torch.from_numpy(mask())
        report={'version':'19.9-beta','mode':'diagnostic','appels_modele_reussis':2,'masques_proposes':0,'candidats':[]}
        with tempfile.TemporaryDirectory() as td:
            with patch.object(node,'run_adaptive',return_value=(mask(),mask(),np.zeros((160,220),np.float32),report)):
                with patch.object(node.SmartSVGStudioV198Expert,'execute',return_value=(x,'CRICUT')) as fake:
                    _,txt=node.SmartSVGStudioV199Expert().execute(image=x,dossier_sortie=td,type_fichier='photo',
                                   raffinement_ia='diagnostic',masques_objets=m)
            self.assertIn('V19.9',txt)
            np.testing.assert_array_equal(fake.call_args.kwargs['masques_objets'].numpy(),mask())
            self.assertTrue(list(Path(td).glob('ALIGNEMENT_MASQUES_V19_8_*.json')) or list(Path(td).glob('QA_MATTING_V19_9/*.png')))
    def test_legacy_registry_and_required_new_nodes(self):
        for k in ('SmartSVGStudioV198Express','SmartSVGStudioV199Express','SmartSVGAdaptiveV199'):
            self.assertIn(k,node.NODE_CLASS_MAPPINGS)
    def test_budget_limits(self):
        with self.assertRaises(core.RefinementError):core.adaptive_refine(img(),mask(),max_passes=5)
        with self.assertRaises(core.RefinementError):core.adaptive_refine(img(),mask(),margin=2)
    def test_overlap_is_uncertain(self):
        m=mask();m[1]=m[0]
        _,_,u,r=core.adaptive_refine(img(),m,max_passes=0)
        self.assertGreater(np.count_nonzero(u),0)
        self.assertEqual(len(r['candidats']),0)
    def test_proposal_qa_written_outside_png(self):
        b=mask();c=b.copy();c[0]=cv2.dilate(c[0],np.ones((3,3),np.uint8))
        with tempfile.TemporaryDirectory() as td:
            qa={'mode':'proposition','version':'19.9'}
            p=node._save_qa(td,b,c,np.zeros((160,220),np.float32),qa)
            self.assertTrue(p.exists())
            self.assertEqual(len(list((Path(td)/'QA_MATTING_V19_9').glob('*.png'))),2)
            self.assertFalse(list(Path(td).glob('*CRICUT*')))

if __name__=='__main__':unittest.main()

class EndToEndV199(unittest.TestCase):
    def test_actual_photo_export_same_bytes_with_diagnostic_matting_off(self):
        from hashlib import sha256
        from smartsvg_v199_tests.node_v198 import SmartSVGStudioV198Expert
        x=torch.from_numpy(img().astype('float32')/255).unsqueeze(0)
        m=torch.from_numpy(mask())
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/'historique';b=Path(td)/'v199'
            kw={'type_fichier':'photo','masques_objets':m,'segmentation_objets':'desactiver',
                'profil_performances':'desactiver'}
            SmartSVGStudioV198Expert().execute(image=x,dossier_sortie=str(a),**kw)
            _,text=node.SmartSVGStudioV199Expert().execute(image=x,dossier_sortie=str(b),
                raffinement_ia='diagnostic',max_passes_ia=0,**kw)
            old=sorted(a.rglob('*CRICUT_TEST.png'));new=sorted(b.rglob('*CRICUT_TEST.png'))
            self.assertEqual(len(old),2)
            self.assertEqual(len(new),2)
            for f,g in zip(old,new):
                self.assertEqual(sha256(f.read_bytes()).hexdigest(),sha256(g.read_bytes()).hexdigest())
            qa=list(b.glob('RAFFINEMENT_IA_V19_9_*.json'))
            self.assertEqual(len(qa),1)
            self.assertIn('V19.9',text)
    def test_new_workflows_have_valid_widget_order_and_links(self):
        for kind in ('Express','Expert'):
            wf=json.loads((ROOT/'example_workflows'/f'SmartSVG_Studio_V19_9_{kind}.json').read_text())
            cls=node.NODE_CLASS_MAPPINGS['SmartSVGStudioV199'+kind]
            n=next(x for x in wf['nodes'] if x['type']=='SmartSVGStudioV199'+kind)
            expected=[k for k in cls.INPUT_TYPES()['required'] if k!='image']
            widgets=[s['name'] for s in n['inputs'] if s.get('widget')]
            self.assertEqual(widgets,expected)
            self.assertEqual(len(widgets),len(n['widgets_values']))
            for id,src,srcslot,dest,destslot,tp in wf['links']:
                target=next(x for x in wf['nodes'] if x['id']==dest)
                self.assertEqual(target['inputs'][destslot]['link'],id)
        photo=json.loads((ROOT/'example_workflows'/'SmartSVG_Studio_V19_9_Photo_Orchestration.json').read_text())
        n=next(x for x in photo['nodes'] if x['type']=='SmartSVGStudioV199Express')
        widgets=[x['name'] for x in n['inputs'] if x.get('widget')]
        self.assertEqual(n['widgets_values'][widgets.index('raffinement_ia')],'diagnostic')
    def test_external_masks_are_prioritized_over_primary_ai_calls(self):
        b=mask()
        with patch.object(node,'_primary',side_effect=AssertionError('should not call Florence/SAM')):
            selected,alternative,uncertain,qa=node.run_adaptive(img(),reference=b,max_passes=0)
        np.testing.assert_array_equal(selected,b)
        self.assertEqual(qa['provenance']['source'],'MASK_ComfyUI')
