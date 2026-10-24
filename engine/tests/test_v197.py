"""V19.7 per-run real timing and CUDA diagnostic contracts (no model download)."""
from pathlib import Path
from unittest.mock import patch
import importlib
import json
import sys
import tempfile
import time
import types
import unittest
import numpy as np
import cv2
import torch

ROOT=Path(__file__).resolve().parents[1]
PACKAGE='smartsvg_v197_test'
if PACKAGE not in sys.modules:
    m=types.ModuleType(PACKAGE)
    m.__path__=[str(ROOT)]
    sys.modules[PACKAGE]=m
telemetry=importlib.import_module(PACKAGE+'.telemetry_v197')
node=importlib.import_module(PACKAGE+'.node_v197')
base=importlib.import_module(PACKAGE+'.node_v196')


def example():
    img=np.full((100,140,3),230,np.uint8)
    cv2.circle(img,(70,50),34,(70,100,200),-1)
    im=torch.from_numpy(img.astype('float32')/255).unsqueeze(0)
    mask=np.zeros((1,100,140),np.float32)
    cv2.circle(mask[0],(70,50),34,1,-1)
    return im,torch.from_numpy(mask)

class FakeCuda:
    def __init__(self):self.calls=0
    def is_available(self):return True
    def current_device(self):return 0
    def mem_get_info(self,device):return (4000,8000)
    def memory_allocated(self,device):return 1000+self.calls*11
    def memory_reserved(self,device):return 2000
    def max_memory_allocated(self,device):return 3500
    def synchronize(self):self.calls+=1
class FakeTorch:
    def __init__(self):self.cuda=FakeCuda()

class ProfileTests(unittest.TestCase):
    def test_cpu_stages_recorded_without_cuda(self):
        t=telemetry.RunProfile()
        with t.activate():
            with telemetry.track_stage('segmentation de test'):
                time.sleep(.002)
                telemetry.record_output_path('dossier_reference')
        report=t.report()
        self.assertEqual(len(report['etapes']),1)
        self.assertGreater(report['etapes'][0]['secondes_ecoulees'],0)
        self.assertEqual(report['sortie_production'],'dossier_reference')
        self.assertFalse(report['mesure_gpu_reelle_observee'])

    def test_fake_cuda_peak_marked_global_not_per_stage(self):
        fake=FakeTorch()
        t=telemetry.RunProfile(torch_module=fake)
        with t.activate():
            with telemetry.track_stage('test_cuda'):pass
        event=t.report()['etapes'][0]
        self.assertTrue(t.report()['mesure_gpu_reelle_observee'])
        self.assertEqual(event['cuda_apres']['global_peak_allocated_bytes'],3500)
        self.assertIn('variation_allocation_cuda_bytes',event)
        self.assertGreaterEqual(fake.cuda.calls,2)
        self.assertTrue(any('PAS le pic isolé' in x for x in t.report()['limites']))

    def test_exception_recorded_and_propagated(self):
        p=telemetry.RunProfile()
        with self.assertRaisesRegex(ValueError,'simulation'):
            with p.activate():
                with telemetry.track_stage('bad'):
                    raise ValueError('simulation')
        self.assertEqual(p.report()['etapes'][0]['statut'],'ERREUR')
        self.assertIsNone(telemetry.active_profiler())

    def test_nested_profiles_do_not_leak(self):
        a=telemetry.RunProfile();b=telemetry.RunProfile()
        with a.activate():
            with telemetry.track_stage('one'):pass
            with b.activate():
                with telemetry.track_stage('two'):pass
            with telemetry.track_stage('three'):pass
        self.assertEqual([e['etape'] for e in a.events],['one','three'])
        self.assertEqual([e['etape'] for e in b.events],['two'])

    def test_profile_file_is_sidecar_and_has_no_manifest_side_effect(self):
        p=telemetry.RunProfile()
        p.status='REUSSI'
        with tempfile.TemporaryDirectory() as td:
            stable=Path(td)/'SmartSVG_V19.6_existing'
            stable.mkdir();(stable/'PRET.json').write_text('reference')
            f=telemetry.save_profile(p,td)
            self.assertEqual(json.loads(f.read_text())['statut'],'REUSSI')
            self.assertEqual((stable/'PRET.json').read_text(),'reference')
            self.assertEqual(len(list(Path(td).glob('PERFORMANCES_V19_7_*.json'))),1)

    def test_disabled_profile_never_creates_sidecar(self):
        pic,_=example()
        expected=(pic,'production unchanged')
        with tempfile.TemporaryDirectory() as td,patch.object(base.SmartSVGStudioV196Expert,'execute',return_value=expected):
            out=node.SmartSVGStudioV197Expert().execute(image=pic,dossier_sortie=td,profil_performances='desactiver')
            self.assertIs(out,expected)
            self.assertEqual(list(Path(td).glob('PERFORMANCES*.json')),[])

    def test_enabled_profile_stays_non_destructive(self):
        pic,_=example()
        with tempfile.TemporaryDirectory() as td:
            def mock_run(self,**kwargs):
                with telemetry.track_stage('SAM2 / segmentation'):
                    pass
                telemetry.record_output_path(Path(td)/'produced')
                return pic,'Dossier: produced'
            with patch.object(base.SmartSVGStudioV196Expert,'execute',mock_run):
                out=node.SmartSVGStudioV197Expert().execute(image=pic,dossier_sortie=td)
            self.assertIs(out[0],pic)
            self.assertIn('V19.7 profil reel',out[1])
            files=list(Path(td).glob('PERFORMANCES_V19_7_*.json'))
            self.assertEqual(len(files),1)
            report=json.loads(files[0].read_text())
            self.assertEqual(report['statut'],'REUSSI')
            self.assertIn('SAM2 / segmentation',[e['etape'] for e in report['etapes']])
            self.assertEqual(report['sortie_production'],str(Path(td)/'produced'))

    def test_failed_run_writes_failure_report_and_raises(self):
        pic,_=example()
        with tempfile.TemporaryDirectory() as td:
            with patch.object(base.SmartSVGStudioV196Expert,'execute',side_effect=RuntimeError('model unavailable')):
                with self.assertRaisesRegex(RuntimeError,'model unavailable'):
                    node.SmartSVGStudioV197Expert().execute(image=pic,dossier_sortie=td)
            files=list(Path(td).glob('PERFORMANCES*.json'))
            self.assertEqual(len(files),1)
            content=json.loads(files[0].read_text())
            self.assertEqual(content['statut'],'ECHEC')
            self.assertIn('model unavailable',content['echec'])

    def test_success_with_partial_failure_is_explicit(self):
        pic,_=example()
        with tempfile.TemporaryDirectory() as td:
            def mock_run(self,**kwargs):
                try:
                    with telemetry.track_stage('modele absent'):
                        raise RuntimeError('manquant')
                except RuntimeError:
                    pass
                return pic,'Production reussie'
            with patch.object(base.SmartSVGStudioV196Expert,'execute',mock_run):
                out=node.SmartSVGStudioV197Expert().execute(image=pic,dossier_sortie=td)
            self.assertIn('1 etape(s) ont echoue',out[1])
            data=json.loads(next(Path(td).glob('PERFORMANCES_V19_7_*.json')).read_text())
            self.assertEqual(data['statut'],'REUSSI')
            self.assertEqual(data['nombre_erreurs_partielles'],1)
            self.assertEqual(data['erreurs_partielles'][0]['etape'],'modele absent')

    def test_workflow_inputs_order_and_links(self):
        for mode in ['Express','Expert']:
            workflow=json.loads((ROOT/'example_workflows'/f'SmartSVG_Studio_V19_7_{mode}.json').read_text())
            clazz=node.NODE_CLASS_MAPPINGS['SmartSVGStudioV197'+mode]
            group=next(n for n in workflow['nodes'] if n['type']=='SmartSVGStudioV197'+mode)
            widgets=[x['name'] for x in group['inputs'] if x.get('widget')]
            required=[x for x in clazz.INPUT_TYPES()['required'] if x!='image']
            self.assertEqual(required,widgets)
            self.assertEqual(len(widgets),len(group['widgets_values']))
            self.assertEqual(group['widgets_values'][-1],'activer')
            ids={n['id']:n for n in workflow['nodes']}
            for link_id,src,slot,dst,index,typ in workflow['links']:
                self.assertEqual(ids[dst]['inputs'][index]['link'],link_id)
                self.assertEqual(ids[dst]['inputs'][index]['type'],typ)

    def test_v196_comparison_unchanged(self):
        pic,mask=example()
        from smartsvg_v197_test.mask_compare_v196 import compare_mask_sets
        rgb=np.uint8(np.clip(pic[0].numpy()*255,0,255))
        a=mask.numpy()
        x,y=compare_mask_sets(rgb,a,a.copy(),mode='diagnostic')
        np.testing.assert_array_equal(x,a)
        self.assertEqual(y['selection'],['reference'])

if __name__=='__main__': unittest.main()

class ProfileEndToEndTests(unittest.TestCase):
    def test_real_photo_mask_export_profile_and_file_hash_nonregression(self):
        """Actually run the photo exporter, not a mocked wrapper; no AI download."""
        from hashlib import sha256
        pic,mask=example()
        with tempfile.TemporaryDirectory() as td:
            old_dir=Path(td)/'v196';new_dir=Path(td)/'v197'
            old_dir.mkdir();new_dir.mkdir()
            old=base.SmartSVGStudioV196Express().execute_express(
                pic,str(old_dir),type_fichier='photo',segmentation_objets='desactiver',
                analyse_florence='desactiver',masques_objets=mask,
                comparaison_masques='diagnostic')
            new=node.SmartSVGStudioV197Express().execute_express(
                pic,str(new_dir),type_fichier='photo',segmentation_objets='desactiver',
                analyse_florence='desactiver',masques_objets=mask,
                comparaison_masques='diagnostic',profil_performances='activer')
            self.assertEqual(tuple(old[0].shape),tuple(new[0].shape))
            old_outputs=list(old_dir.glob('SmartSVG_V19_5_2_PHOTO_*'))
            new_outputs=list(new_dir.glob('SmartSVG_V19_5_2_PHOTO_*'))
            self.assertEqual((len(old_outputs),len(new_outputs)),(1,1))
            for rel in ('02_OBJETS_PNG/OBJET_01_CRICUT_TEST.png',):
                # Historical files names may differ; compare based on file suffix.
                candidates_old=sorted(old_outputs[0].glob('02_OBJETS_PNG/*_CRICUT_TEST.png'))
                candidates_new=sorted(new_outputs[0].glob('02_OBJETS_PNG/*_CRICUT_TEST.png'))
                self.assertEqual(len(candidates_old),1)
                self.assertEqual(len(candidates_new),1)
                self.assertEqual(sha256(candidates_old[0].read_bytes()).hexdigest(),
                                 sha256(candidates_new[0].read_bytes()).hexdigest())
            profile_files=list(new_dir.glob('PERFORMANCES_V19_7_*.json'))
            self.assertEqual(len(profile_files),1)
            report=json.loads(profile_files[0].read_text('utf8'))
            self.assertEqual(report['statut'],'REUSSI')
            self.assertEqual(report['sortie_production'],str(new_outputs[0]))
            self.assertIn('Comparaison des masques',[e['etape'] for e in report['etapes']])
            self.assertIn('Export photo / Cricut',[e['etape'] for e in report['etapes']])
            self.assertFalse(report['mesure_gpu_reelle_observee'])
            self.assertIn('Export photo / Cricut',report['durees_etapes_s'])

    def test_gpu_sampling_does_not_reset_global_peak(self):
        fake=FakeTorch()
        with patch.object(fake.cuda, 'synchronize', wraps=fake.cuda.synchronize) as sync:
            with patch.object(fake.cuda,'max_memory_allocated',return_value=9080) as max_peak:
                p=telemetry.RunProfile(torch_module=fake)
                with p.activate():
                    with telemetry.track_stage('GPU simulation'):
                        pass
                self.assertGreaterEqual(sync.call_count,2)
                self.assertGreaterEqual(max_peak.call_count,2)
                self.assertEqual(p.report()['etapes'][0]['cuda_avant']['global_peak_allocated_bytes'],9080)
                self.assertFalse(hasattr(fake.cuda,'reset_peak_memory_stats'))

