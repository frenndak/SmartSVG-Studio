"""Portable V14.1 tests without ComfyUI or user-file dependencies."""
import importlib
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import cv2
import torch
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
MOD='smartsvg_v141_testpackage'
package=types.ModuleType(MOD)
package.__path__=[str(ROOT)]
sys.modules[MOD]=package
core=importlib.import_module(MOD+'.engine_v141')
bridge=importlib.import_module(MOD+'.rmbg_bridge')


def single():
    im=np.full((220,280,3),255,np.uint8)
    cv2.circle(im,(138,115),67,(75,140,210),-1)
    cv2.circle(im,(115,90),20,(15,90,185),-1)
    return im

def multi():
    im=np.zeros((200,370,3),np.uint8)
    a=np.zeros(im.shape[:2],np.uint8)
    cv2.circle(a,(80,85),36,255,-1)
    cv2.rectangle(a,(255,65),(318,136),255,-1)
    im[a>0]=[80,180,100]
    return im,a


class BridgeTests(unittest.TestCase):
    def test_optional_params_passed_and_cached(self):
        events={'init':0,'calls':[]}
        class RMBG:
            def __init__(self):events['init']+=1
            @classmethod
            def INPUT_TYPES(cls):
                return {'required':{'image':('IMAGE',),'model':(['INSPYRENET','BEN'],)},
                        'optional':{'process_res':('INT',{'default':1024}),
                                    'sensitivity':('FLOAT',{'default':0.9}),
                                    'background':(['White','Alpha'],),
                                    'unload_model':('BOOLEAN',{'default':True})}}
            def process_image(self,img,model,**kw):
                events['calls'].append((model,dict(kw)))
                assert kw['process_res']==768 and kw['background']=='Alpha'
                return img, torch.ones((1,img.shape[1],img.shape[2]))
        o=types.SimpleNamespace(_rmbg_backend=None,_rmbg_backend_class=None)
        for shape in ((36,40,3),(24,26,3)):
            mask,meta=bridge.invoke_rmbg(o,np.zeros(shape,np.uint8),{'RMBG':RMBG})
            self.assertEqual(mask.shape,shape[:2])
            self.assertEqual(meta['resolution'],768)
        self.assertEqual(events['init'],1)
        self.assertEqual(len(events['calls']),2)
        self.assertIn('sensitivity',events['calls'][0][1])

    def test_invalid_mask_rejected(self):
        class RMBG:
            @classmethod
            def INPUT_TYPES(cls):return {'required':{'image':('IMAGE',),'model':(['INSPYRENET'],)}}
            def process_image(self,img,model,**kw):
                return img,torch.full((1,img.shape[1],img.shape[2]),float('nan'))
        with self.assertRaisesRegex(RuntimeError,'non finies'):
            bridge.invoke_rmbg(types.SimpleNamespace(),np.zeros((25,30,3),np.uint8),{'RMBG':RMBG})

    def test_missing_model_rejected(self):
        with self.assertRaisesRegex(RuntimeError,'introuvable'):
            bridge.invoke_rmbg(types.SimpleNamespace(),np.zeros((25,30,3),np.uint8),{})

class EngineTests(unittest.TestCase):
    def test_single_and_manifest(self):
        with tempfile.TemporaryDirectory() as td:
            report,preview=core.process_v141(single(),td,ia_mode='desactiver')
            p=Path(report['output'])
            self.assertEqual(report['audit_v141']['stickers'],1)
            self.assertTrue((p/'PRET_V14_1.json').exists())
            self.assertTrue((p/core.CRICUT_SVG).exists())
            self.assertFalse((p/'PRET_V14.json').exists())
            self.assertGreater(report['audit_v141']['complexite_svg']['svg_compact']['segments'],0)
            status=json.loads((p/'PRET_V14_1.json').read_text('utf-8'))
            self.assertFalse(status['validation_cricut_reelle'])
            from hashlib import sha256
            for filename,meta in status['fichiers'].items():
                self.assertEqual(sha256((p/filename).read_bytes()).hexdigest(),meta['sha256'])
            self.assertEqual(len(list(Path(td).glob('.SmartSVG_V141_TEMP_*'))),0)

    def test_transparent_irregular(self):
        im,a=multi()
        with tempfile.TemporaryDirectory() as td:
            r,_=core.process_v141(im,td,alpha=a,ia_mode='desactiver')
            self.assertEqual(r['audit_v141']['stickers'],2)
            svg=core.analyze_svg(Path(r['output'])/core.CRICUT_SVG)
            self.assertLess(svg['chemins'],5000)

    def test_force_ai_requires_real_mask(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(core.UnsafeCut):
                core.process_v141(single(),td,ia_mode='forcer',ai_masker=None)
            self.assertFalse(list(Path(td).glob('SmartSVG_V14_1_*')))
            self.assertTrue(list(Path(td).glob('SmartSVG_ECHEC_V141_*.json')))

    def test_force_ai_positive(self):
        def segmentation(arr):
            return (np.any(arr<245,axis=2)).astype(np.float32)
        with tempfile.TemporaryDirectory() as td:
            report,_=core.process_v141(single(),td,ia_mode='forcer',ai_masker=segmentation)
            self.assertEqual(report['audit_v141']['ia']['utilises'],1)
            self.assertEqual(report['audit_v141']['ia']['tentatives'],1)

    def test_fail_closed_on_vector_issue(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(core,'analyze_svg',side_effect=RuntimeError('corrupt')):
                with self.assertRaises(core.UnsafeCut):
                    core.process_v141(single(),td,ia_mode='desactiver')
            self.assertFalse(list(Path(td).rglob('IMPORT_CRICUT_IMPRIMER_DECOUPER.png')))
            self.assertFalse(list(Path(td).glob('SmartSVG_V14_1_*')))
            self.assertTrue(list(Path(td).glob('SmartSVG_ECHEC_V141_*.json')))

    def test_without_cairosvg_is_explicit(self):
        with tempfile.TemporaryDirectory() as td:
            r,_=core.process_v141(single(),td,ia_mode='desactiver')
            with patch.dict(sys.modules,{'cairosvg':None}):
                status=core.image_fidelity(Path(r['output']),core.CRICUT_SVG)
            self.assertFalse(status['mesure_effectuee'])

    def test_documented_workflow(self):
        wf=json.loads((ROOT/'example_workflows'/'SmartSVG_Studio_V16_Expert.json').read_text('utf8'))
        self.assertEqual(len([n for n in wf['nodes'] if n['type']=='SmartSVGStudioV16Expert']),1)
        for lid,src,slot,dst,inp,typ in wf['links']:
            target=next(n for n in wf['nodes'] if n['id']==dst)
            self.assertEqual(target['inputs'][inp]['link'],lid)

if __name__=='__main__':unittest.main()

class ComfyNodeTests(unittest.TestCase):
    def test_node_forced_ai_full_simulated(self):
        module_name='smartsvg_v141_node_integration'
        spec=importlib.util.spec_from_file_location(module_name,ROOT/'__init__.py',
                                                      submodule_search_locations=[str(ROOT)])
        plugin=importlib.util.module_from_spec(spec)
        sys.modules[module_name]=plugin
        spec.loader.exec_module(plugin)
        self.assertIn('SmartSVGStudioV16Expert',plugin.NODE_CLASS_MAPPINGS)
        captured=[]
        class FakeRMBG:
            @classmethod
            def INPUT_TYPES(cls):
                return {'required':{'image':('IMAGE',),'model':(['INSPYRENET'],)},
                        'optional':{'process_res':('INT',{'default':1024}),
                                    'sensitivity':('FLOAT',{'default':0.5})}}
            def process_image(self,img,model,**kw):
                captured.append(dict(kw))
                arr=img[0].numpy()
                fg=np.uint8(np.any(arr<.96,axis=2)).astype('float32')
                return img,torch.from_numpy(fg).unsqueeze(0)
        mocked_nodes=types.ModuleType('nodes')
        mocked_nodes.NODE_CLASS_MAPPINGS={'RMBG':FakeRMBG}
        with tempfile.TemporaryDirectory() as td, patch.dict(sys.modules,{'nodes':mocked_nodes}):
            image=torch.from_numpy(single().astype('float32')/255).unsqueeze(0)
            mask=torch.zeros((1,image.shape[1],image.shape[2]),dtype=torch.float32)
            result,report=plugin.NODE_CLASS_MAPPINGS["SmartSVGStudioV16Expert"]().execute(image,td,ia_locale='forcer',masque_png=mask)
            self.assertEqual(tuple(result.shape[1:]),(220,280,3))
            self.assertIn('IA:',report)
            self.assertEqual(captured[0]['process_res'],768)
            manifest=list(Path(td).glob('SmartSVG_V17_*/rapport_V17.json'))
            self.assertEqual(len(manifest),1)
            detail=json.loads(manifest[0].read_text('utf-8'))['audit_precedent']
            self.assertEqual(detail['audit_v141']['ia']['utilises'],1)
            self.assertEqual(detail['audit_v141']['ia']['inferences'][0]['modele'],'INSPYRENET')
