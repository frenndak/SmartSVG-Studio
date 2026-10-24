"""V21.3 conservative instance-by-instance segmentation regressions."""
import importlib, json, tempfile, unittest, types, sys
from pathlib import Path
from unittest.mock import patch
import numpy as np, cv2, torch
ROOT=Path(__file__).resolve().parents[1]
if 'sv213test' not in sys.modules:
    p=types.ModuleType('sv213test');p.__path__=[str(ROOT)];sys.modules[p.__name__]=p
seg=importlib.import_module('sv213test.instances_v213')
node=importlib.import_module('sv213test.node_v213')
qa=importlib.import_module('sv213test.controle_export_v212')


def sample():
    im=np.full((180,320,3),(185,208,220),np.uint8)
    for x in (65,160,255):cv2.circle(im,(x,92),28,(66,124,190),-1)
    boxes=[{'label':'fox','bbox':[x-31,58,x+31,125]} for x in (65,160,255)]
    return im,boxes

def masks(im,label):
    h,w=im.shape[:2]
    gray=cv2.cvtColor(im,cv2.COLOR_RGB2GRAY)
    mask=np.uint8(gray<172)
    # Simple synthetic fixture provider, never mislabel as real inference.
    return mask.astype(np.float32)

class InstanceV213(unittest.TestCase):
    def test_categories(self):
        self.assertIn('fox',seg.PROFILE_PROMPTS['Trois renards'])
        self.assertIn('duck',seg.PROFILE_PROMPTS['Canard / objet'])

    def test_manual_boxes_three(self):
        im,boxes=sample();data=json.dumps(boxes)
        m,r=seg.segment_instances(im,source='Boîtes manuelles',boxes_json=data,masker=masks)
        self.assertEqual(m.shape,(3,180,320))
        self.assertEqual(r['nombre_masques'],3)
        self.assertTrue(all(it['statut']=='MASQUE_PROPOSE_A_VERIFIER' for it in r['instances']))
        self.assertFalse(r['validation_semantique_humaine'])
        for i in range(3):self.assertTrue(m[i].sum()>1200)

    def test_detect_injected_multiple_same_class(self):
        im,boxes=sample()
        m,r=seg.segment_instances(im,detector=lambda *_:boxes,masker=masks)
        self.assertEqual(len(m),3)
        self.assertEqual(r['source_boites'],'FLORENCE_2_EXECUTE')

    def test_export_end_to_end(self):
        im,boxes=sample();m,r=seg.segment_instances(im,detector=lambda *_:boxes,masker=masks)
        with tempfile.TemporaryDirectory() as t:
            output,_=qa.run_v212(im,t,masks=m,width_mm=31)
            self.assertEqual(output['nombre_objets_exportes'],3)
            for record in output['objets']:
                self.assertTrue(Path(record['fichier_png_cricut']).is_file())
                self.assertTrue(Path(record['fichier_svg_contour']).is_file())
            self.assertEqual(output['controle_v212']['nombre_objets_inspectes'],3)

    def test_empty_detection_fails(self):
        im,_=sample()
        with self.assertRaises(seg.InstanceError):seg.segment_instances(im,detector=lambda *_:[],masker=masks)

    def test_wrong_json_fails(self):
        im,_=sample()
        with self.assertRaises(seg.InstanceError):seg.segment_instances(im,source='Boîtes manuelles',boxes_json='{"wrong":true}',masker=masks)

    def test_boxes_out_of_image_not_used(self):
        im,_=sample()
        with self.assertRaises(seg.InstanceError):seg.segment_instances(im,source='Boîtes manuelles',boxes_json='[{"label":"fox","bbox":[-4,0,100,100]}]',masker=masks)

    def test_boxes_nan_not_used(self):
        im,_=sample()
        with self.assertRaises(seg.InstanceError):seg.segment_instances(im,source='Boîtes manuelles',boxes_json='[{"label":"fox","bbox":[NaN,0,100,100]}]',masker=masks)

    def test_categories_prevent_invalid_label(self):
        im,_=sample()
        with self.assertRaises(seg.InstanceError):seg.segment_instances(im,source='Boîtes manuelles',boxes_json='[{"label":"background","bbox":[0,0,100,100]}]',masker=masks)

    def test_duplicate_boxes(self):
        im,boxes=sample();boxes=[boxes[0],boxes[0],boxes[1]]
        m,r=seg.segment_instances(im,detector=lambda *_:boxes,masker=masks)
        self.assertEqual(len(m),2)
        self.assertIn('DOUBLON',';'.join(r['avertissements_detection']))

    def test_duplicate_masks(self):
        im,boxes=sample();boxes=[boxes[0],boxes[2]]
        def provider(crop,label):return np.ones(crop.shape[:2],np.float32)
        with self.assertRaises(seg.InstanceError):seg.segment_instances(im,detector=lambda *_:boxes,masker=provider)

    def test_masks_do_not_include_other_instances(self):
        im,boxes=sample();m,r=seg.segment_instances(im,detector=lambda *_:boxes,masker=masks)
        for i in range(3):
            yy,xx=np.nonzero(m[i]>.5)
            self.assertLess(xx.max()-xx.min(),90)

    def test_crop_quality_rejection(self):
        im,boxes=sample()
        def empty(crop,label):return np.zeros(crop.shape[:2],np.float32)
        with self.assertRaises(seg.InstanceError):seg.segment_instances(im,detector=lambda *_:boxes,masker=empty)

    def test_bad_float_values(self):
        im,boxes=sample()
        def bad(crop,label):return np.full(crop.shape[:2],np.nan,np.float32)
        with self.assertRaises(seg.InstanceError):seg.segment_instances(im,detector=lambda *_:boxes,masker=bad)

    def test_wrong_dimensions(self):
        im,boxes=sample()
        def bad(crop,label):return np.ones((3,4),np.float32)
        with self.assertRaises(seg.InstanceError):seg.segment_instances(im,detector=lambda *_:boxes,masker=bad)

    def test_one_failed_instance_preserves_others(self):
        im,boxes=sample();i=[0]
        def intermittent(crop,label):
            i[0]+=1
            if i[0]==2:raise RuntimeError('OOM simulated')
            return masks(crop,label)
        m,r=seg.segment_instances(im,detector=lambda *_:boxes,masker=intermittent)
        self.assertEqual(len(m),2)
        self.assertEqual(sum(it['statut']=='ECHEC_SEGMENTATION' for it in r['instances']),1)

    def test_node_input_five_controls_express(self):
        self.assertEqual(len(node.SmartSVGExpressV213.INPUT_TYPES()['required']),6)
        self.assertIn('masques_objets',node.SmartSVGExpressV213.INPUT_TYPES()['optional'])
        self.assertIn('SmartSVGExpressV212',node.NODE_CLASS_MAPPINGS)

    def test_node_receives_mask_output(self):
        self.assertEqual(node.SmartSVGInstancesV213.RETURN_TYPES,('MASK','IMAGE','STRING'))

    def test_visual_preview_diagnostic(self):
        im,boxes=sample()
        m,r=seg.segment_instances(im,detector=lambda *_:boxes,masker=masks)
        im2=seg.render_preview(im,m,r,max_side=180)
        self.assertEqual(im2.height,101)
        self.assertEqual(im2.mode,'RGB')

    def test_budget_limit(self):
        with self.assertRaises(seg.InstanceError):seg.normalize_boxes([], (100,100),('fox',),13)

    def test_not_a_sam2_score(self):
        im,boxes=sample()
        m,r=seg.segment_instances(im,detector=lambda *_:boxes,masker=masks)
        self.assertEqual(r['source_masques'],'FOURNISSEUR_INJECTE_NON_PROUVE')
        self.assertFalse(r['certification_decoupe_cricut'])

    def test_reject_too_many_fullsize_masks_before_inference(self):
        im=np.full((2250,2000,3),255,np.uint8)
        boxes=[{'label':'fox','bbox':[20+(i%4)*410,15+(i//4)*600,350+(i%4)*410,500+(i//4)*600]} for i in range(12)]
        called=[False]
        def no_inference(*a):called[0]=True;return np.zeros((1,1),np.float32)
        with self.assertRaises(seg.InstanceError):
            seg.segment_instances(im,detector=lambda *_:boxes,max_objects=12,masker=no_inference)
        self.assertFalse(called[0])

    def test_florence_fake_registry_scale(self):
        im=np.full((1152,1536,3),190,np.uint8)
        class MockFlorence:
            FUNCTION='analyze'
            RETURN_TYPES=('IMAGE','MASK','JSON')
            @classmethod
            def INPUT_TYPES(cls):
                return {'required':{'model_name':(['microsoft/Florence-2-base'],),
                      'task':(['Phrase Grounding (text boxes)'],)},
                        'optional':{'text_prompt':('STRING',),'keep_model_loaded':('BOOLEAN',)}}
            def analyze(self,**k):
                self.kw=k
                return (None,None,{'bboxes':[[10,20,180,200],[190,20,320,200]],
                                    'labels':['fox','fox']})
        with unittest.mock.patch.dict(sys.modules,{'nodes':types.SimpleNamespace(NODE_CLASS_MAPPINGS={'AILab_Florence2':MockFlorence})}):
            boxes=seg.detect_florence_boxes(im,'Trois renards')
        self.assertEqual(len(boxes),2)
        self.assertEqual(boxes[0]['bbox'][0],15)

    def test_florence_wrong_api_rejected(self):
        im,_=sample()
        class Broken:
            FUNCTION='oops';RETURN_TYPES=('IMAGE',)
            @classmethod
            def INPUT_TYPES(cls):return {'required':{},'optional':{}}
        with unittest.mock.patch.dict(sys.modules,{'nodes':types.SimpleNamespace(NODE_CLASS_MAPPINGS={'AILab_Florence2':Broken})}):
            with self.assertRaises(seg.InstanceError):seg.detect_florence_boxes(im,'Trois renards')

    def test_masks_overlap_warns(self):
        im,boxes=sample()
        # Overlapping box crops and two independently returned candidates.
        boxes=[{'label':'fox','bbox':[35,50,115,140]},
               {'label':'fox','bbox':[90,50,185,140]}]
        def masked(crop,label):
            y,x=crop.shape[:2]
            m=np.zeros((y,x),np.float32);cv2.ellipse(m,(x//2,y//2),(32,30),0,0,360,1,-1)
            return m
        m,r=seg.segment_instances(im,detector=lambda *_:boxes,masker=masked)
        self.assertEqual(len(m),2)
        self.assertTrue(any('CHEVAUCHEMENT' in str(v) for v in r['instances']))

    def test_source_image_not_mutated(self):
        im,boxes=sample();before=im.copy()
        seg.segment_instances(im,detector=lambda *_:boxes,masker=masks)
        self.assertTrue(np.array_equal(im,before))

    def test_touching_border_warns(self):
        im,boxes=sample();bb={'label':'fox','bbox':[0,0,120,150]}
        m,r=seg.segment_instances(im,detector=lambda *_:[bb],masker=masks)
        self.assertIn('BOITE_TOUCHE_BORD_IMAGE_SOURCE',r['instances'][0]['avertissements'])

if __name__=='__main__':unittest.main()
