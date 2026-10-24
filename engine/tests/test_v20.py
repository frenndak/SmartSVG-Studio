"""V20 major regression: adversarial object leakage, QA transactions, compatibility."""
from pathlib import Path
from unittest.mock import patch
import importlib, sys, types, tempfile, unittest, json
import cv2, numpy as np, torch
ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg_v20_tests'
if PKG not in sys.modules:
    module=types.ModuleType(PKG);module.__path__=[str(ROOT)];sys.modules[PKG]=module
core=importlib.import_module(PKG+'.adaptive_refiner_v20')
legacy=importlib.import_module(PKG+'.adaptive_refiner_v199')
node=importlib.import_module(PKG+'.node_v20')


def sample():
    rgb=np.full((160,220,3),200,np.uint8)
    masks=np.zeros((2,160,220),np.float32)
    cv2.circle(masks[0],(74,80),30,1.,-1)
    cv2.rectangle(masks[1],(109,67),(135,97),1.,-1)
    rgb[masks[0]>.5]=(48,80,166)
    rgb[masks[1]>.5]=(18,140,35)
    return rgb,masks

class TestV20(unittest.TestCase):
    def test_contamination_that_old_version_accepted_is_rejected(self):
        rgb,m=sample()
        def both(crop):return (np.min(crop,axis=2)<195).astype(np.float32)
        _, old, _, old_report=legacy.adaptive_refine(rgb,m,mode='proposition',model_runner=both,max_passes=2)
        _, new, _, new_report=core.adaptive_refine(rgb,m,mode='proposition',model_runner=both,max_passes=2)
        old_rec=next(c for c in old_report['candidats'] if c['objet']==1)
        new_rec=next(c for c in new_report['candidats'] if c['objet']==1)
        self.assertEqual(old_rec['statut'],'CANDIDAT')
        self.assertEqual(new_rec['statut'],'REFUSE_EMPIETEMENT_AUTRE_OBJET')
        self.assertGreater(new_rec['intrusion_autres_objets_px'],8)
        np.testing.assert_array_equal(new,m)
        self.assertFalse(np.array_equal(old,m))
    def test_border_leak_rejected_even_with_good_iou(self):
        rgb,m=sample()
        def grow_to_edge(crop):
            result=np.all(crop==[48,80,166],axis=2).astype(np.float32)
            result[0,:]=1.
            return result
        _, candidate,_,qa=core.adaptive_refine(rgb,m[:1],mode='proposition',model_runner=grow_to_edge,max_passes=1)
        self.assertEqual(qa['candidats'][0]['statut'],'REFUSE_FUITE_BORD_ROI')
        np.testing.assert_array_equal(candidate,m[:1])
    def test_normal_good_mask_keeps_candidate(self):
        rgb,m=sample()
        # These arrays are 1/0 on original RGB, matting base remains stable.
        def own(crop):return np.all(crop==[48,80,166],axis=2).astype(np.float32)
        _,candidate,_,r=core.adaptive_refine(rgb,m,mode='proposition',model_runner=own,max_passes=2)
        self.assertEqual(next(c for c in r['candidats'] if c['objet']==1)['statut'],'CANDIDAT')
        np.testing.assert_array_equal(candidate,m)
    def test_annotation_promotion_protected_from_neighbors(self):
        rgb,m=sample()
        bad=m.copy();bad[0]=cv2.erode(m[0],np.ones((5,5),np.uint8))
        def both(crop):return (np.min(crop,axis=2)<195).astype(np.float32)
        out,_,_,r=core.adaptive_refine(rgb,bad,mode='adopter_annotation',annotation=m,model_runner=both,max_passes=1)
        np.testing.assert_array_equal(out,bad)
        self.assertFalse(r['selection_modifiee'])
    def test_good_supervised_promotion_still_works(self):
        rgb,m=sample();bad=m.copy();bad[0]=cv2.erode(m[0],np.ones((5,5),np.uint8))
        def own(crop):return np.all(crop==[48,80,166],axis=2).astype(np.float32)
        out,_,_,r=core.adaptive_refine(rgb,bad,mode='adopter_annotation',annotation=m,model_runner=own,max_passes=2)
        self.assertTrue(r['selection_modifiee'])
        self.assertEqual(next(c for c in r['candidats'] if c['objet']==1)['statut'],'ADOPTE_SUR_ANNOTATION')
        np.testing.assert_array_equal(out[0],m[0])
    def test_reject_zero_height_image(self):
        with self.assertRaises(core.RefinementError):
            core.validate_masks(np.zeros((0,120,3),np.uint8),np.zeros((1,0,120),np.float32))
    def test_express_mode_diagnostic_preserves_source_masks(self):
        rgb,m=sample()
        selected,variants,uncertain,report,original=node.run_adaptive(rgb,reference=m,model_runner=lambda c:np.zeros(c.shape[:2]),max_passes=0)
        np.testing.assert_array_equal(selected,m)
        np.testing.assert_array_equal(original,m)
        self.assertEqual(report['version'],'20.0-beta')
    def test_qa_staged_then_committed_with_source_masks(self):
        rgb,m=sample();alt=m.copy();alt[0]=cv2.dilate(m[0],np.ones((3,3),np.uint8)).astype(np.float32)
        with tempfile.TemporaryDirectory() as td:
            result=node._save_qa(td,m,alt,np.zeros(rgb.shape[:2]),{'mode':'proposition'})
            qa=json.loads(result.read_text(encoding='utf8'))
            self.assertEqual(qa['masques_alternatifs_exportes'],1)
            self.assertTrue(qa['export_qa_atomique'])
            self.assertEqual(len(qa['fichiers_qa']),3)
            self.assertTrue(all(Path(x).is_file() for x in qa['fichiers_qa']))
            self.assertFalse(list((Path(td)/'QA_MATTING_V20').glob('.pending_*')))
            self.assertFalse(list(Path(td).glob('*CRICUT*')))
    def test_qa_failed_image_save_rolls_back(self):
        rgb,m=sample();alt=m.copy();alt[0]=.5
        with tempfile.TemporaryDirectory() as td:
            qa=Path(td)/'QA_MATTING_V20'
            with patch.object(node.Image.Image,'save',side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    node._save_qa(td,m,alt,np.zeros(rgb.shape[:2]),{'mode':'proposition'})
            self.assertFalse(list(qa.iterdir()))
    def test_qa_symlink_escape_blocked(self):
        rgb,m=sample()
        with tempfile.TemporaryDirectory() as td, tempfile.TemporaryDirectory() as outside:
            try:(Path(td)/'QA_MATTING_V20').symlink_to(outside,target_is_directory=True)
            except (NotImplementedError,OSError):self.skipTest('symlink unavailable')
            with self.assertRaises(ValueError):node._save_qa(td,m,m,np.zeros(rgb.shape[:2]),{})
            self.assertFalse(list(Path(outside).iterdir()))
    def test_qa_bad_dimension_is_atomic(self):
        rgb,m=sample()
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):node._save_qa(td,m,m[:1],np.zeros(rgb.shape[:2]),{})
            self.assertEqual(list((Path(td)/'QA_MATTING_V20').iterdir()),[])
    def test_qa_serialization_error_rolls_back(self):
        rgb,m=sample()
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(TypeError):node._save_qa(td,m,m,np.zeros(rgb.shape[:2]),{'bad':object()})
            self.assertEqual(list((Path(td)/'QA_MATTING_V20').iterdir()),[])
    def test_missing_primary_does_not_retry_legacy_background_removal(self):
        rgb,m=sample()
        img=torch.from_numpy(rgb.astype('float32')/255).unsqueeze(0)
        with patch.object(node,'run_adaptive',side_effect=core.RefinementError('model not loaded')):
            with patch.object(node.SmartSVGStudioV198Expert,'execute',return_value=(img,'FALLBACK')) as base:
                _,message=node.SmartSVGStudioV20Expert().execute(image=img,type_fichier='photo',raffinement_ia='diagnostic')
        kw=base.call_args.kwargs
        self.assertEqual(kw['ia_locale'],'desactiver')
        self.assertEqual(kw['strategie_photo'],'analyse_seule')
        self.assertIn('second passage non realise',message)
    def test_standalone_input_output_shape(self):
        rgb,m=sample();img=torch.from_numpy(rgb.astype(np.float32)/255)[None];m0=torch.from_numpy(m)
        with patch.object(node,'run_adaptive',return_value=(m,m,np.zeros(rgb.shape[:2]),{'version':'20.0-beta'},m)):
            selected,alternative,uncertainty,text=node.SmartSVGAdaptiveV20().run(img,masques_objets=m0)
        self.assertEqual(tuple(selected.shape),(2,160,220))
        self.assertEqual(tuple(uncertainty.shape),(1,160,220))
        self.assertEqual(json.loads(text)['version'],'20.0-beta')
    def test_preflight_is_readonly_and_reports_no_inference(self):
        mock_nodes=types.SimpleNamespace(NODE_CLASS_MAPPINGS={})
        with patch.dict(sys.modules,{'nodes':mock_nodes}):
            with patch.object(node.torch.cuda,'is_available',return_value=False):
                result=node.SmartSVGEnvironmentV20().run()
                self.assertEqual(result['ui']['text'][0],result['result'][0])
                info=json.loads(result['result'][0])
        self.assertFalse(info['execution_modele_ia'])
        self.assertFalse(info['cuda']['disponible'])
        self.assertEqual(info['installation_rmbg'],'absente_ou_non_chargee')
    def test_preflight_recognizes_actual_florence_node_id(self):
        mock_nodes=types.SimpleNamespace(NODE_CLASS_MAPPINGS={'SAM2Segment':object(), 'AILab_Florence2':object()})
        with patch.dict(sys.modules,{'nodes':mock_nodes}):
            with patch.object(node.torch.cuda,'is_available',return_value=False):
                report=json.loads(node.SmartSVGEnvironmentV20().run()['result'][0])
        self.assertTrue(report['modules_disponibles']['AILab_Florence2'])
        self.assertTrue(report['modules_disponibles']['SAM2Segment'])
        self.assertEqual(report['installation_rmbg'],'partielle_ou_complete')
    def test_compat_all_versions_in_registry(self):
        for name in ('SmartSVGStudioV199Express','SmartSVGStudioV198Expert','SmartSVGStudioV20Express','SmartSVGEnvironmentV20','SmartSVGAdaptiveV20'):
            self.assertIn(name,node.NODE_CLASS_MAPPINGS)
    def test_v20_workflows_have_correct_widgets_and_links(self):
        for kind in ('Express','Expert'):
            wf=json.loads((ROOT/'example_workflows'/f'SmartSVG_Studio_V20_{kind}.json').read_text())
            klass=node.NODE_CLASS_MAPPINGS['SmartSVGStudioV20'+kind]
            n=next(n for n in wf['nodes'] if n['type']=='SmartSVGStudioV20'+kind)
            names=[item['name'] for item in n['inputs'] if item.get('widget')]
            expected=[x for x in klass.INPUT_TYPES()['required'] if x!='image']
            self.assertEqual(names,expected)
            self.assertEqual(len(n['widgets_values']),len(names))
            for link,*details in wf['links']:
                target=next(x for x in wf['nodes'] if x['id']==details[2])
                self.assertEqual(target['inputs'][details[3]]['link'],link)

if __name__=='__main__':unittest.main()
