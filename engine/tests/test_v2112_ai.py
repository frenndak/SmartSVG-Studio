"""V21.12 offline contracts + adversarial segmentation and Cricut non-regression."""
import importlib,sys,types,tempfile,json,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import cv2,torch
ROOT=Path(__file__).resolve().parents[1]
if 'sv2112test' not in sys.modules:
    pkg=types.ModuleType('sv2112test');pkg.__path__=[str(ROOT)];sys.modules[pkg.__name__]=pkg
provider=importlib.import_module('sv2112test.smartsvg_ai.provider_v2112')
node=importlib.import_module('sv2112test.node_v2112')
old=importlib.import_module('sv2112test.node_v21112')

def example(h=128,w=140):
    a=np.zeros((h,w,3),dtype=np.uint8)+50
    m=np.zeros((h,w),dtype=np.float32)
    cv2.ellipse(m,(w//2,h//2),(30,40),20,0,360,1.,-1)
    return a,m

class FakeBiRef:
    FUNCTION='process_image';RETURN_TYPES=('IMAGE','MASK','IMAGE')
    calls=0
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'image':('IMAGE',),'model':(['BiRefNet_lite','BiRefNet-general'],)},
            'optional':{'background':(['Alpha','Color'],),'unload_model':('BOOLEAN',),
                        'mask_blur':('INT',),'process_res':('INT',)}}
    def process_image(self,image,model,**kwargs):
        type(self).calls+=1
        assert model=='BiRefNet_lite' and kwargs['unload_model'] is True
        h,w=image.shape[1:3];m=np.zeros((h,w),dtype=np.float32)
        cv2.ellipse(m,(w//2,h//2),(30,40),20,0,360,1.,-1)
        return (image,torch.from_numpy(m[None]),image)

class FakeRMBG:
    FUNCTION='process_image';RETURN_TYPES=('IMAGE','MASK','IMAGE')
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'image':('IMAGE',),'model':(['RMBG-2.0'],)},
                'optional':{'unload_model':('BOOLEAN',)}}
    def process_image(self,image,model,**kw):
        h,w=image.shape[1:3];m=np.zeros((h,w),dtype=np.float32)
        cv2.circle(m,(w//2,h//2),35,1.,-1)
        return (image,torch.from_numpy(m[None]),image)

class FakeBadBiRef(FakeBiRef):
    def process_image(self,image,model,**kwargs):
        return (image,torch.ones((1,*image.shape[1:3])),image)

class FakeWrongSize(FakeBiRef):
    def process_image(self,image,model,**kwargs):
        return (image,torch.zeros((1,image.shape[2],image.shape[1])),image)

class FakeOOM(FakeBiRef):
    def process_image(self,image,model,**kwargs):
        raise torch.cuda.OutOfMemoryError('out of memory')

class FakeSAM:
    RETURN_TYPES=('IMAGE','MASK','IMAGE');FUNCTION='segment_v2'
    prompts=[]
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'image':('IMAGE',),'prompt':('STRING',),
          'sam2_model':(['sam2.1_hiera_tiny'],),
          'dino_model':([provider.DINO],), 'device':(['Auto','CPU'],)},
          'optional':{'threshold':('FLOAT',),'unload_model':('BOOLEAN',)}}
    def segment_v2(self,image,prompt,sam2_model,dino_model,device,**kw):
        type(self).prompts.append(prompt)
        _,m=example(*image.shape[1:3]);return(image,torch.from_numpy(m[None]),image)

class TestAI(unittest.TestCase):
    def setUp(self):
        FakeBiRef.calls=0;FakeSAM.prompts=[]
    def test_no_models_diagnostic_absent(self):
        info=provider.available({})
        self.assertEqual(len(info),3)
        self.assertTrue(all(v['statut']=='ABSENT' for v in info))
    def test_signature_checked_without_instantiation(self):
        class NoConstructor(FakeBiRef):
            def __init__(self):raise AssertionError('No model should initialize')
        info=provider.available({'BiRefNetRMBG':NoConstructor})
        self.assertEqual(info[0]['statut'],'CONTRAT_COMPATIBLE_NON_EXECUTE')
        self.assertEqual(FakeBiRef.calls,0)
    def test_signature_wrong_model_rejected(self):
        class Wrong(FakeBiRef):
            @classmethod
            def INPUT_TYPES(cls):return {'required':{'image':('IMAGE',),'model':(['NOT_FOUND'],)}}
        self.assertEqual(provider.available({'BiRefNetRMBG':Wrong})[0]['statut'],'INCOMPATIBLE')
    def test_fallback_to_rmbg_for_invalid_birefnet_mask(self):
        arr,_=example()
        with patch.object(provider.torch.cuda,'is_available',return_value=False):
            output=provider.segment_adaptive(arr,registry={'BiRefNetRMBG':FakeBadBiRef,'RMBG':FakeRMBG})
        self.assertEqual(output['audit']['provider'],'RMBG')
        self.assertTrue(output['audit']['inference_effectuee'])
        self.assertFalse(output['audit']['certification_semantique'])
        self.assertEqual(output['masks'].shape,(1,128,140))
    def test_selection_primary_birefnet(self):
        arr,_=example()
        with patch.object(provider.torch.cuda,'is_available',return_value=False):
            output=provider.segment_adaptive(arr,registry={'BiRefNetRMBG':FakeBiRef})
        self.assertEqual(output['audit']['provider'],'BiRefNetRMBG')
        self.assertEqual(FakeBiRef.calls,1)
    def test_sam_fallback(self):
        arr,_=example()
        with patch.object(provider.torch.cuda,'is_available',return_value=False):
            output=provider.segment_adaptive(arr,registry={'SAM2Segment':FakeSAM})
        self.assertEqual(output['audit']['provider'],'SAM2Segment')
        self.assertEqual(FakeSAM.prompts,['person'])
    def test_bad_size_is_not_accepted(self):
        arr,_=example(120,155)
        with patch.object(provider.torch.cuda,'is_available',return_value=False):
            with self.assertRaises(provider.ProviderUnavailable):
                provider.segment_adaptive(arr,registry={'BiRefNetRMBG':FakeWrongSize})
    def test_oom_does_not_try_larger_provider(self):
        arr,_=example()
        with patch.object(provider.torch.cuda,'is_available',return_value=False):
            with self.assertRaisesRegex(provider.ProviderUnavailable,'VRAM'):
                provider.segment_adaptive(arr,registry={'BiRefNetRMBG':FakeOOM,'RMBG':FakeRMBG})
    def test_no_provider_fail_closed(self):
        arr,_=example()
        with self.assertRaisesRegex(provider.ProviderUnavailable,'aucun fournisseur'):
            provider.segment_adaptive(arr,registry={})
    def test_comfy_output_dict_and_rgba_grayscale(self):
        _,m=example();n=provider._mask_from_output({'result':(None,torch.from_numpy(m)[None,:,:,None])},m.shape)
        self.assertEqual(n.shape,(1,*m.shape))
    def test_nan_and_inverted_dimension_fail(self):
        _,m=example()
        for v in (np.full((128,140),np.nan), np.zeros((140,128))):
            with self.assertRaises(provider.ProviderUnavailable):
                provider._mask_from_output((None,v),(128,140))
    def test_old_nodes_unchanged(self):
        for key,value in old.NODE_CLASS_MAPPINGS.items():
            self.assertIs(node.NODE_CLASS_MAPPINGS[key],value)
        self.assertEqual(list(node.SmartSVGAutoExpressV2112.INPUT_TYPES()['required']),
                         list(old.SmartSVGAutoExpressV21112.INPUT_TYPES()['required']))
    def test_white_sheet_skips_model(self):
        a=np.full((260,260,3),255,np.uint8)
        for x in (70,190):
            for y in (70,190):cv2.circle(a,(x,y),25,(90,30,220),-1)
        t=torch.from_numpy(a.astype('float32')/255)[None]
        def forbidden(image):raise AssertionError('AI should not execute on accepted flat artwork')
        m,qa=node.automatic(t,provider=forbidden)
        self.assertEqual(m.shape[0],4)
        self.assertEqual(qa['methode'],'ILLUSTRATION_FOND_BLANC')
    def test_complex_image_needs_real_ai(self):
        a,_=example();t=torch.from_numpy(a.astype('float32')/255)[None]
        # Provider injected into new orchestration, not the legacy node.
        with patch.object(node,'segment_adaptive',lambda img:provider.segment_adaptive(img,registry={'BiRefNetRMBG':FakeBiRef})),\
             patch.object(provider.torch.cuda,'is_available',return_value=False):
            m,qa=node.automatic(t,'Obligatoire')
        self.assertEqual(qa['methode'],'SEGMENTATION_IA')
        self.assertFalse(qa['certification_cricut'])
        self.assertTrue(qa['ia']['execution_effective'])
    def test_missing_provider_no_output_files(self):
        a,_=example();t=torch.from_numpy(a.astype('float32')/255)[None]
        with tempfile.TemporaryDirectory() as d,patch.object(node,'segment_adaptive',lambda img:provider.segment_adaptive(img,registry={})):
            with self.assertRaises(node.AutoMaskError):
                node.SmartSVGAutoExpressV2112().run(t,dossier_sortie=d,ia_locale='Obligatoire')
            self.assertEqual(list(Path(d).iterdir()),[])
    def test_outputs_preserved_with_external_mask(self):
        a,m=example();t=torch.from_numpy(a.astype('float32')/255)[None];tm=torch.from_numpy(m[None])
        with tempfile.TemporaryDirectory() as d1,tempfile.TemporaryDirectory() as d2:
            kw=dict(projet='Sticker - contour du sujet',largeur_mm=37.,qualite_ppp='300',
                    ia_locale='Desactivee',masques_objets=tm)
            orig=old.SmartSVGAutoExpressV21112().run(t,dossier_sortie=d1,**kw)
            new=node.SmartSVGAutoExpressV2112().run(t,dossier_sortie=d2,**kw)
            info0=json.loads(orig['result'][2]);info1=json.loads(new['result'][2])
            for k in ('fichier_png_cricut','fichier_svg_contour'):
                self.assertEqual(Path(info0['objets'][0][k]).read_bytes(),Path(info1['objets'][0][k]).read_bytes())
            self.assertEqual(Path(info0['import_direct_cricut_v218']['objets'][0]['fichier_import']).read_bytes(),
                             Path(info1['import_direct_cricut_v218']['objets'][0]['fichier_import']).read_bytes())
    def test_png_auto_ai_reports_real_model_attempt_and_not_certified(self):
        a,_=example();t=torch.from_numpy(a.astype('float32')/255)[None]
        with tempfile.TemporaryDirectory() as d,patch.object(node,'segment_adaptive',lambda img:provider.segment_adaptive(img,registry={'BiRefNetRMBG':FakeBiRef})),\
             patch.object(provider.torch.cuda,'is_available',return_value=False):
            response=node.SmartSVGAutoExpressV2112().run(t,dossier_sortie=d,
                    projet='Sticker - contour du sujet',largeur_mm=37.,qualite_ppp='300',ia_locale='Obligatoire')
            report=json.loads(response['result'][2])
            self.assertEqual(report['detourage_ia_v2112']['methode'],'SEGMENTATION_IA')
            self.assertTrue(report['detourage_ia_v2112']['ia']['execution_effective'])
            self.assertFalse(report['detourage_ia_v2112']['certification_cricut'])
            self.assertEqual(report['import_direct_cricut_v218']['fichiers_prets'],1)

if __name__=='__main__':unittest.main()
