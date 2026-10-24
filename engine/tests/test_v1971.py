"""V19.7.1 adversarial observability, fallback and nonregression tests."""
from pathlib import Path
from unittest.mock import patch
import importlib, json, sys, tempfile, time, types, unittest
import torch

ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg_v1971_regression'
if PKG not in sys.modules:
    pkg=types.ModuleType(PKG);pkg.__path__=[str(ROOT)];sys.modules[PKG]=pkg
tele=importlib.import_module(PKG+'.telemetry_v197')
node=importlib.import_module(PKG+'.node_v197')
base=importlib.import_module(PKG+'.node_v196')

class FakeCUDA:
    def __init__(self,sync_error=False,memory_error=False,changing_device=False):
        self.sync_error=sync_error;self.memory_error=memory_error
        self.changing_device=changing_device;self.device_calls=0
    def is_available(self):return True
    def current_device(self):
        self.device_calls+=1
        return self.device_calls%2 if self.changing_device else 0
    def get_device_name(self,device):return 'FAKE_GPU'
    def memory_allocated(self,device):return 1000
    def memory_reserved(self,device):return 1500
    def max_memory_allocated(self,device):return 2500
    def mem_get_info(self,device):
        if self.memory_error:raise RuntimeError('mem_get_info unavailable')
        return (500,8000)
    def synchronize(self):
        if self.sync_error:raise RuntimeError('CUDA synchronization failed')

class FakeTorch:
    def __init__(self,**kwargs):self.cuda=FakeCUDA(**kwargs)

class TelemetryCorrections(unittest.TestCase):
    def test_sync_failure_was_silent_now_explicit(self):
        profile=tele.RunProfile(torch_module=FakeTorch(sync_error=True))
        with profile.activate():
            with tele.track_stage('SAM2 fake'):pass
        stage=profile.report()['etapes'][0]
        self.assertEqual(stage['statut'],'OK')
        self.assertFalse(stage['chronometrage_gpu_synchronise'])
        self.assertFalse(stage['synchronisation_cuda_avant']['reussie'])
        self.assertFalse(stage['synchronisation_cuda_apres']['reussie'])
        self.assertEqual(profile.report()['synchronisation_cuda_echouee_etapes'],['SAM2 fake'])
        self.assertTrue(stage['cuda_apres']['available'])

    def test_partial_cuda_info_is_not_misreported_as_cuda_unavailable(self):
        profile=tele.RunProfile(torch_module=FakeTorch(memory_error=True))
        with profile.activate():
            with tele.track_stage('Finegrain fake'):pass
        stage=profile.report()['etapes'][0]
        self.assertTrue(stage['cuda_apres']['available'])
        self.assertEqual(stage['cuda_apres']['allocated_bytes'],1000)
        self.assertIn('device_memory_info',stage['cuda_apres']['mesures_indisponibles'])
        self.assertNotIn('free_device_bytes',stage['cuda_apres'])
        self.assertEqual(profile.report()['captures_gpu_partielles_etapes'],['Finegrain fake'])
        self.assertTrue(stage['chronometrage_gpu_synchronise'])

    def test_changing_device_cannot_be_called_synchronized_same_gpu(self):
        p=tele.RunProfile(torch_module=FakeTorch(changing_device=True))
        with p.activate():
            with tele.track_stage('stage'):pass
        self.assertFalse(p.report()['etapes'][0]['chronometrage_gpu_synchronise'])

    def test_nested_exclusive_time_and_total_not_summed(self):
        p=tele.RunProfile(torch_module=FakeTorch())
        with p.activate():
            with tele.track_stage('parent'):
                time.sleep(.002)
                with tele.track_stage('child'):
                    time.sleep(.012)
                time.sleep(.002)
        d=p.report();e={x['etape']:x for x in d['etapes']}
        self.assertLess(e['parent']['secondes_exclusives_approximatives'],e['parent']['secondes_ecoulees'])
        self.assertLess(e['parent']['secondes_exclusives_approximatives'],e['child']['secondes_ecoulees'])
        self.assertIn('child',d['durees_exclusives_approximatives_s'])

    def test_cpu_rss_is_optional_and_labeled_process(self):
        p=tele.RunProfile(torch_module=FakeTorch())
        with patch.object(tele,'_cpu_rss',side_effect=[2300,2700]):
            with p.activate():
                with tele.track_stage('ram'):pass
        e=p.report()['etapes'][0]
        self.assertEqual(e['rss_processus_avant_bytes'],2300)
        self.assertEqual(e['rss_processus_apres_bytes'],2700)
        self.assertEqual(e['variation_rss_processus_bytes'],400)
        self.assertTrue(any('processus ComfyUI' in x for x in p.report()['limites']))

    def test_cpu_rss_absence_not_error(self):
        p=tele.RunProfile(torch_module=FakeTorch())
        with patch.object(tele,'_cpu_rss',return_value=None):
            with p.activate():
                with tele.track_stage('no rss'):pass
        e=p.report()['etapes'][0]
        self.assertIsNone(e['rss_processus_avant_bytes'])
        self.assertNotIn('variation_rss_processus_bytes',e)

    def test_cancel_propagates_and_stage_does_not_leak(self):
        p=tele.RunProfile(torch_module=FakeTorch())
        with self.assertRaises(KeyboardInterrupt):
            with p.activate():
                with tele.track_stage('cancelled'):raise KeyboardInterrupt()
        self.assertIsNone(tele.active_profiler())
        self.assertEqual(p.events[0]['statut'],'ERREUR')
        self.assertEqual(p.events[0]['etape'],'cancelled')
        with p.activate():
            with tele.track_stage('after cancellation'):pass
        self.assertEqual(p.events[-1]['secondes_exclusives_approximatives'],p.events[-1]['secondes_ecoulees'])

    def test_profile_atomic_file_and_metadata(self):
        p=tele.RunProfile(torch_module=FakeTorch())
        p.status='REUSSI'
        with tempfile.TemporaryDirectory() as td:
            d=Path(td)
            first=tele.save_profile(p,d)
            second=tele.save_profile(p,d)
            self.assertNotEqual(first,second)
            self.assertEqual(json.loads(first.read_text())['version'],'19.7.1-beta')
            self.assertEqual(json.loads(second.read_text())['statut'],'REUSSI')
            self.assertFalse(list(d.glob('*.tmp')))

    def test_diagnostic_write_failure_nonfatal_but_visible(self):
        image=torch.zeros((1,25,35,3),dtype=torch.float32)
        with tempfile.TemporaryDirectory() as td:
            with patch.object(base.SmartSVGStudioV196Expert,'execute',return_value=(image,'export ok')):
                with patch.object(node,'save_profile',side_effect=PermissionError('unwritable')):
                    out=node.SmartSVGStudioV197Expert().execute(image=image,dossier_sortie=td)
            self.assertIs(out[0],image)
            self.assertIn('ATTENTION: mesure terminee mais rapport performances non enregistre',out[1])
            self.assertIn('export ok',out[1])

    def test_report_remains_json_serializable_after_failed_sensor(self):
        p=tele.RunProfile(torch_module=FakeTorch(memory_error=True,sync_error=True))
        with p.activate():
            with tele.track_stage('bad sensor'):pass
        json.dumps(p.report(),allow_nan=False)
        self.assertFalse(p.report()['preuve_inference_GPU_modele_specifique'])

if __name__=='__main__':unittest.main()

class NewNodeContract(unittest.TestCase):
    def test_new_nodes_and_workflows_are_registered(self):
        bridge=importlib.import_module(PKG+'.node_v1971')
        for variant in ('Express','Expert'):
            kind=f'SmartSVGStudioV1971{variant}'
            self.assertIn(kind,bridge.NODE_CLASS_MAPPINGS)
            self.assertIn(f'SmartSVGStudioV197{variant}',bridge.NODE_CLASS_MAPPINGS)
            d=json.loads((ROOT/'example_workflows'/f'SmartSVG_Studio_V19_7_1_{variant}.json').read_text('utf8'))
            n=next(x for x in d['nodes'] if x['type']==kind)
            required=[x for x in bridge.NODE_CLASS_MAPPINGS[kind].INPUT_TYPES()['required'] if x!='image']
            widgets=[x['name'] for x in n['inputs'] if x.get('widget')]
            self.assertEqual(required,widgets)
            self.assertEqual(len(widgets),len(n['widgets_values']))
            indexed={x['id']:x for x in d['nodes']}
            for lid,src,slot,dst,inp,typ in d['links']:
                self.assertEqual(indexed[dst]['inputs'][inp]['link'],lid)
                self.assertEqual(indexed[dst]['inputs'][inp]['type'],typ)

class ProductionNonRegression(unittest.TestCase):
    def test_actual_photo_export_v1971_matches_v197(self):
        import cv2, numpy as np
        from hashlib import sha256
        bridge=importlib.import_module(PKG+'.node_v1971')
        img=np.full((94,136,3),255,np.uint8)
        cv2.circle(img,(67,48),30,(130,50,200),-1)
        rgb=torch.from_numpy(np.ascontiguousarray(img.astype('float32')/255)).unsqueeze(0)
        a=np.zeros((1,94,136),np.float32)
        cv2.circle(a[0],(67,48),30,1,-1)
        mask=torch.from_numpy(a)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            def call(cls,subfolder):
                return cls().execute_express(rgb,str(root/subfolder),type_fichier='photo',
                    segmentation_objets='desactiver',analyse_florence='desactiver',
                    masques_objets=mask,profil_performances='activer')
            output_old=call(node.SmartSVGStudioV197Express,'old')
            output_new=call(bridge.SmartSVGStudioV1971Express,'new')
            self.assertEqual(output_old[0].shape,output_new[0].shape)
            oldfile=next((root/'old').rglob('*_CRICUT_TEST.png'))
            newfile=next((root/'new').rglob('*_CRICUT_TEST.png'))
            self.assertEqual(sha256(oldfile.read_bytes()).hexdigest(),sha256(newfile.read_bytes()).hexdigest())
            newprofile=next((root/'new').glob('PERFORMANCES*.json'))
            details=json.loads(newprofile.read_text())
            self.assertEqual(details['version'],'19.7.1-beta')
            self.assertFalse(details['mesure_gpu_reelle_observee'])
            self.assertIn('Export photo / Cricut',details['durees_etapes_s'])
