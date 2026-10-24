"""V19.6 independent consistency tests; no model weight downloads."""
import importlib
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np
import torch

ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg_v196_testpkg'
if PKG not in sys.modules:
    p=types.ModuleType(PKG);p.__path__=[str(ROOT)];sys.modules[PKG]=p
core=importlib.import_module(PKG+'.mask_compare_v196')
nodes=importlib.import_module(PKG+'.node_v196')


def source():
    im=np.zeros((160,200,3),np.uint8)
    im[:]=[210,220,200]
    cv2.circle(im,(92,75),42,(50,90,180),-1)
    return im


def mask():
    m=np.zeros((160,200),np.float32)
    cv2.circle(m,(92,75),42,1,-1)
    return m

class MaskComparisonTests(unittest.TestCase):
    def test_identical_masks_do_not_create_fake_improvement(self):
        a=mask()
        selected,detail=core.compare_mask_sets(source(),a,a.copy(),mode='selection_prudente')
        self.assertEqual(detail['selection'],['reference'])
        np.testing.assert_array_equal(selected[0],a)

    def test_no_change_in_diagnostic_mode(self):
        a=mask();b=a.copy();b[:15,:]=1
        selected,detail=core.compare_mask_sets(source(),a,b,mode='diagnostic')
        self.assertEqual(detail['selection'],['reference'])
        self.assertEqual(detail['variantes_comparees'],2)
        np.testing.assert_array_equal(selected[0],a)

    def test_far_away_candidate_not_automatically_selected(self):
        a=mask();b=np.zeros_like(a);cv2.circle(b,(171,125),18,1,-1)
        out,report=core.compare_mask_sets(source(),a,b,mode='selection_prudente')
        self.assertEqual(report['selection'],['reference'])
        self.assertLess(report['objets'][0]['scores']['alternative_B']['iou_vs_reference'],.68)

    def test_obvious_fragmentation_can_be_selected_if_close(self):
        a=mask()
        # Repeated detached noise impacts reference fragmentation/quality.
        for i in range(8):cv2.circle(a,(12+i*20,12),3,1,-1)
        b=mask()
        out,report=core.compare_mask_sets(source(),a,b,mode='selection_prudente')
        self.assertEqual(report['selection'],['alternative_B'])
        np.testing.assert_array_equal(out[0],b)

    def test_missing_reference_rejected(self):
        with self.assertRaisesRegex(core.MaskComparisonError,'reference requis'):
            core.compare_mask_sets(source(),None,mask())

    def test_wrong_shape_alternative_ignored_with_warning(self):
        a=mask();b=np.ones((50,80),np.float32)
        out,report=core.compare_mask_sets(source(),a,b,mode='selection_prudente')
        self.assertEqual(report['selection'],['reference'])
        self.assertTrue(report['avertissements'])

    def test_nans_rejected_and_source_unchanged(self):
        a=mask();original=a.copy();a[20,20]=float('nan')
        with self.assertRaises(core.MaskComparisonError):core.compare_mask_sets(source(),a)
        self.assertEqual(float(original.max()),1.0)

    def test_oversized_and_wrong_scale_rejected(self):
        with self.assertRaisesRegex(core.MaskComparisonError,'hors 0..1'):
            core.compare_mask_sets(source(),mask()*255)
        with self.assertRaisesRegex(core.MaskComparisonError,'budget'):
            core._as_float_masks(np.zeros((16,1600,1400),np.uint8),'enorme')

    def test_multi_object_batches(self):
        a=mask();b=np.roll(a,70,axis=1)
        stack=np.stack([a,b]);out,details=core.compare_mask_sets(source(),stack,stack.copy())
        self.assertEqual(out.shape,stack.shape)
        self.assertEqual(details['nombre_objets'],2)

    def test_different_object_counts_cannot_be_reordered(self):
        a=mask()
        out,report=core.compare_mask_sets(source(),a,np.stack([a,a]))
        self.assertTrue(any('nombre d objets' in x for x in report['avertissements']))
        self.assertEqual(report['selection'],['reference'])

    def test_manually_annotated_truth_reports_supervised_iou_dice(self):
        truth=mask();a=truth.copy();a[:7,:]=1
        selected,report=core.compare_mask_sets(source(),a,truth,annotated=truth,mode='diagnostic')
        obj=report['objets'][0]['scores']
        self.assertTrue(report['annotation_manuelle_utilisee'])
        self.assertEqual(obj['alternative_B']['iou_avec_annotation'],1.0)
        self.assertEqual(obj['alternative_B']['dice_avec_annotation'],1.0)
        self.assertLess(obj['reference']['iou_avec_annotation'],1.0)
        np.testing.assert_array_equal(selected[0],a)

    def test_manual_truth_must_be_aligned(self):
        with self.assertRaisesRegex(core.MaskComparisonError,'masque annote'):
            core.compare_mask_sets(source(),mask(),annotated=np.zeros((20,30),np.float32))

    def test_compare_node_contract(self):
        c=nodes.SmartSVGCompareMasksV196()
        image=torch.tensor(source(),dtype=torch.float32).unsqueeze(0)/255
        a=torch.from_numpy(mask()).unsqueeze(0)
        output,text=c.run(image,a,mode_comparaison='diagnostic',masque_alternative_B=a)
        self.assertEqual(tuple(output.shape),(1,160,200))
        self.assertFalse(json.loads(text)['test_gpu_reel'])

    def test_integrated_node_preserves_reference_when_diagnostic(self):
        im=torch.tensor(source(),dtype=torch.float32).unsqueeze(0)/255
        a=torch.from_numpy(mask()).unsqueeze(0)
        called=[]
        def fake_run(self,**kw):
            called.append(kw)
            return im,'Dossier: exemple_test\n'
        with patch.object(nodes.SmartSVGStudioV195Expert,'execute',fake_run):
            node=nodes.SmartSVGStudioV196Expert()
            pic,report=node.execute(image=im,dossier_sortie='unused',type_fichier='photo',
                masques_objets=a,masque_alternative_B=a,comparaison_masques='diagnostic')
        self.assertEqual(len(called),1)
        np.testing.assert_array_equal(called[0]['masques_objets'].numpy(),a.numpy())
        self.assertIn('masques alternatifs retenus',report)

    def test_integrated_missing_reference_not_replaced(self):
        node=nodes.SmartSVGStudioV196Expert()
        with self.assertRaises(core.MaskComparisonError):
            node.execute(image=torch.tensor(source(),dtype=torch.float32).unsqueeze(0)/255,
                dossier_sortie='ignored',masque_alternative_B=torch.from_numpy(mask()).unsqueeze(0))

    def test_gpu_diagnostic_is_read_only(self):
        x=nodes.SmartSVGGpuDiagnosticV196()
        report=json.loads(x.inspect()[0])
        self.assertIn('cuda_disponible',report)
        self.assertFalse(report['validation_gpu_reelle_effectuee'])

    def test_workflows_match_node_input_contract(self):
        for kind in ('Express','Expert'):
            w=json.loads((ROOT/'example_workflows'/f'SmartSVG_Studio_V19_6_{kind}.json').read_text('utf8'))
            cls=nodes.NODE_CLASS_MAPPINGS[f'SmartSVGStudioV196{kind}']
            main=[n for n in w['nodes'] if n['type']==f'SmartSVGStudioV196{kind}'][0]
            req=[x for x in cls.INPUT_TYPES()['required'] if x!='image']
            self.assertEqual([x['name'] for x in main['inputs'] if x.get('widget')],req)
            self.assertEqual(len(main['widgets_values']),len(req))
            for link in w['links']:
                self.assertEqual(w['nodes'][link[3]-1]['inputs'][link[4]]['link'],link[0])

if __name__=='__main__':unittest.main()

class RealPhotoExportV196(unittest.TestCase):
    def test_revised_node_with_external_mask_produces_cricut_png(self):
        # Actual production code, two diagnostic candidates, no IA weights.
        im=source();ref=mask()[None]
        clean=ref.copy()
        tensor=torch.from_numpy(im.astype('float32')/255).unsqueeze(0)
        original=torch.from_numpy(ref.copy())
        with tempfile.TemporaryDirectory() as td:
            node=nodes.SmartSVGStudioV196Express()
            preview,message=node.execute_express(tensor,td,type_fichier='photo',
                segmentation_objets='desactiver',analyse_florence='desactiver',
                masques_objets=original,masque_alternative_B=torch.from_numpy(clean),
                comparaison_masques='diagnostic')
            self.assertIn('0/1 masques alternatifs retenus',message)
            folders=list(Path(td).glob('SmartSVG_V19_5_2_PHOTO_*'))
            self.assertEqual(len(folders),1)
            f=folders[0]
            self.assertTrue((f/'PRET_V19_5_2.json').is_file())
            pngs=list(f.glob('02_OBJETS_PNG/*_CRICUT_TEST.png'))
            self.assertEqual(len(pngs),1)
            self.assertEqual(tuple(preview.shape[:1]),(1,))
            np.testing.assert_array_equal(original.numpy(),ref)
