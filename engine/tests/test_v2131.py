"""V21.3.1 adversarial suite. This is not an evaluation of real IA weights."""
import importlib, json, sys, tempfile, types, unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import cv2
import torch
ROOT=Path(__file__).resolve().parents[1]
if 'sv2131test' not in sys.modules:
    package=types.ModuleType('sv2131test');package.__path__=[str(ROOT)]
    sys.modules['sv2131test']=package
seg=importlib.import_module('sv2131test.instances_v2131')
old=importlib.import_module('sv2131test.instances_v213')
node=importlib.import_module('sv2131test.node_v2131')

def fixture():
    im=np.full((160,300,3),210,np.uint8)
    positions=(50,150,250)
    boxes=[]
    for x in positions:
        cv2.circle(im,(x,80),23,(50,80,100),-1)
        boxes.append({'label':'fox','bbox':[x-30,45,x+30,115]})
    return im,boxes

def make_mask(crop,label):
    gray=cv2.cvtColor(crop,cv2.COLOR_RGB2GRAY)
    return np.float32(gray<150)

class AuditV2131(unittest.TestCase):
    def test_provenance_injected_not_claimed_florence(self):
        im,boxes=fixture()
        masks,report=seg.segment_instances(im,detector=lambda *_:boxes,masker=make_mask)
        self.assertEqual(report['source_boites'],'DETECTEUR_INJECTE_NON_PROUVE')
        self.assertEqual(report['source_masques'],'FOURNISSEUR_INJECTE_NON_PROUVE')
        self.assertEqual(len(masks),3)

    def test_old_provenance_was_false_positive(self):
        im,boxes=fixture()
        _,report=old.segment_instances(im,detector=lambda *_:boxes,masker=make_mask)
        self.assertEqual(report['source_boites'],'FLORENCE_2_EXECUTE')

    def test_manual_french_renards(self):
        im,boxes=fixture()
        boxes[0]['label']='Renard';boxes[1]['label']='RENARDS';boxes[2]['label']='fox'
        mask,report=seg.segment_instances(im,source='Boîtes manuelles',boxes_json=json.dumps(boxes),masker=make_mask)
        self.assertEqual(len(mask),3)
        self.assertEqual([entry['label'] for entry in report['instances']],['fox']*3)
        self.assertEqual(report['source_boites'],'BOITES_MANUELLES_NON_SEGMENTATION')

    def test_aliases_all_supported(self):
        for name,want in [('chien','dog'),('canards','duck'),('personne','person'),('humain','human'),('chat','cat'),('oiseaux','bird')]:
            with self.subTest(name=name):self.assertEqual(seg.canonical_label(name),want)

    def test_forbidden_synonyms_remain_forbidden(self):
        items=[{'label':'chien','bbox':[1,1,80,80]}]
        boxes,w=seg.normalize_boxes(items,(150,150),('fox',))
        self.assertEqual(boxes,[])
        self.assertIn('CATEGORIE_NON_AUTORISEE',w[0])

    def test_unicode_weird_label_not_crash(self):
        self.assertEqual(seg.canonical_label(None),'')
        self.assertEqual(seg.canonical_label('x'*100),'')

    def test_out_of_memory_interrupts_entire_batch(self):
        im,boxes=fixture();count=[0]
        def fail(crop,label):
            count[0]+=1
            if count[0]==2:raise RuntimeError('CUDA out of memory. Tried to allocate 2 GiB')
            return make_mask(crop,label)
        with self.assertRaisesRegex(seg.InstanceError,'OOM_CUDA'):
            seg.segment_instances(im,detector=lambda *_:boxes,masker=fail)
        self.assertEqual(count[0],2)

    def test_simulated_failure_can_preserve_other_masks(self):
        im,boxes=fixture();count=[0]
        def fail(crop,label):
            count[0]+=1
            if count[0]==2:raise RuntimeError('provider image unavailable')
            return make_mask(crop,label)
        m,r=seg.segment_instances(im,detector=lambda *_:boxes,masker=fail)
        self.assertEqual(len(m),2)
        self.assertEqual(sum(v['statut']=='ECHEC_SEGMENTATION' for v in r['instances']),1)

    def test_outputs_same_as_v213_on_well_separated_scene(self):
        im,boxes=fixture()
        a,_=old.segment_instances(im,detector=lambda *_:boxes,masker=make_mask)
        b,_=seg.segment_instances(im,detector=lambda *_:boxes,masker=make_mask)
        self.assertTrue(np.array_equal(a,b))

    def test_overlaps_report_on_both_instances(self):
        im=np.full((130,220,3),215,np.uint8)
        boxes=[{'label':'fox','bbox':[20,20,125,112]}, {'label':'fox','bbox':[85,20,190,112]}]
        def elliptical(crop,label):
            h,w=crop.shape[:2];m=np.zeros((h,w),np.float32)
            cv2.ellipse(m,(w//2,h//2),(39,32),0,0,360,1,-1)
            return m
        m,r=seg.segment_instances(im,detector=lambda *_:boxes,masker=elliptical)
        self.assertEqual(len(m),2)
        self.assertTrue(all('CHEVAUCHEMENT_INSTANCES_A_VERIFIER' in e['avertissements'] for e in r['instances']))
        self.assertEqual(r['masques_avec_chevauchement'],2)

    def test_overlap_missing_not_falsely_reported(self):
        im,boxes=fixture();m,r=seg.segment_instances(im,detector=lambda *_:boxes,masker=make_mask)
        self.assertEqual(r['masques_avec_chevauchement'],0)

    def test_neighbor_contamination_flagged(self):
        im=np.full((140,250,3),200,np.uint8)
        boxes=[{'label':'fox','bbox':[20,35,110,110]}, {'label':'fox','bbox':[100,35,205,110]}]
        i=[0]
        def candidate(crop,label):
            i[0]+=1;h,w=crop.shape[:2];m=np.zeros((h,w),np.float32)
            if i[0]==1:
                cv2.rectangle(m,(12,10),(w-1,h-10),1,-1)
            else:
                cv2.ellipse(m,(w//2,h//2),(30,26),0,0,360,1,-1)
            return m
        _,r=seg.segment_instances(im,detector=lambda *_:boxes,masker=candidate)
        self.assertGreaterEqual(r['masques_avec_suspicion_autre_sujet'],1)
        self.assertIn('EMPIETEMENT_ZONE_AUTRE_SUJET_A_VERIFIER',r['instances'][0]['avertissements'])

    def test_contamination_is_only_a_warning(self):
        im=np.full((140,250,3),200,np.uint8)
        boxes=[{'label':'fox','bbox':[20,35,110,110]},{'label':'fox','bbox':[100,35,205,110]}]
        def candidate(crop,label):
            h,w=crop.shape[:2];m=np.zeros((h,w),np.float32)
            cv2.ellipse(m,(w//2,h//2),(44,29),0,0,360,1,-1)
            return m
        m,r=seg.segment_instances(im,detector=lambda *_:boxes,masker=candidate)
        self.assertEqual(m.shape[1:],(140,250))
        self.assertFalse(r['certification_decoupe_cricut'])

    def test_mem_budget_prevents_provider_call(self):
        im=np.ones((2250,2000,3),np.uint8)*200
        boxes=[{'label':'fox','bbox':[20+(i%4)*410,15+(i//4)*600,350+(i%4)*410,500+(i//4)*600]} for i in range(12)]
        called=[0]
        def provider(crop,label):called[0]+=1;return np.zeros(crop.shape[:2],np.float32)
        with self.assertRaises(seg.InstanceError):
            seg.segment_instances(im,detector=lambda *_:boxes,max_objects=12,masker=provider)
        self.assertEqual(called[0],0)

    def test_node_registered_and_no_extra_express_widgets(self):
        self.assertIn('SmartSVGInstancesV2131',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGInstancesV213',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGExpressV212',node.NODE_CLASS_MAPPINGS)
        self.assertEqual(len(node.SmartSVGExpressV2131.INPUT_TYPES()['required']),6)
        self.assertEqual(len(node.SmartSVGInstancesV2131.INPUT_TYPES()['required']),5)

    def test_guidance_boxes_not_certified_cut(self):
        im,boxes=fixture();m,r=seg.segment_instances(im,detector=lambda *_:boxes,masker=make_mask)
        self.assertFalse(r['validation_semantique_humaine'])
        self.assertFalse(r['certification_decoupe_cricut'])
        self.assertEqual(len(m),3)

    def test_bad_nan_manual_rejected(self):
        im,_=fixture()
        with self.assertRaises(seg.InstanceError):
            seg.segment_instances(im,source='Boîtes manuelles',boxes_json='[{"label":"renard","bbox":[NaN,2,40,60]}]',masker=make_mask)

    def test_invalid_boxes_fail_without_inference(self):
        im,_=fixture();called=[False]
        def mask(*args):called[0]=True;raise AssertionError('must not run')
        with self.assertRaises(seg.InstanceError):
            seg.segment_instances(im,source='Boîtes manuelles',boxes_json='[]',masker=mask)
        self.assertFalse(called[0])

    def test_no_photo_to_mask_fabrication(self):
        im,_=fixture()
        with self.assertRaises(seg.InstanceError):
            seg.segment_instances(im,source='Boîtes manuelles',boxes_json='[]',masker=make_mask)

    def test_preview_informs_source_and_dimensions(self):
        im,boxes=fixture();m,r=seg.segment_instances(im,detector=lambda *_:boxes,masker=make_mask)
        p=seg.render_preview(im,m,r,max_side=300)
        self.assertEqual(p.size,(300,160))

    def test_old_nodes_still_registered(self):
        self.assertIn('SmartSVGExpressV213',node.NODE_CLASS_MAPPINGS)

if __name__=='__main__':unittest.main()
