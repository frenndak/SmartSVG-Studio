"""V19.8 regression + adversarial: no model weights, no network, no GPU required."""
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
PKG='smartsvg_v198_regression'
if PKG not in sys.modules:
    pkg=types.ModuleType(PKG);pkg.__path__=[str(ROOT)];sys.modules[PKG]=pkg
mod=importlib.import_module(PKG+'.mask_alignment_v198')
nodes=importlib.import_module(PKG+'.node_v198')


def image():
    rgb=np.full((135,230,3),225,np.uint8)
    cv2.circle(rgb,(50,70),27,(255,90,90),-1)
    cv2.rectangle(rgb,(140,44),(183,101),(70,90,220),-1)
    return rgb


def masks():
    arr=np.zeros((2,135,230),np.float32)
    cv2.circle(arr[0],(50,70),27,1,-1)
    cv2.rectangle(arr[1],(140,44),(183,101),1,-1)
    return arr


class AlignmentTests(unittest.TestCase):
    def test_swapped_mask_order_recognized_and_reported(self):
        ref=masks();alt=ref[::-1].copy()
        out,u,q=mod.compare_aligned_masks(image(),ref,alt)
        np.testing.assert_array_equal(out,ref)
        self.assertFalse(q['masque_reference_modifie'])
        self.assertEqual(q['appariements']['alternative_B']['1']['index_alternatif'],2)
        self.assertEqual(q['appariements']['alternative_B']['2']['index_alternatif'],1)
        self.assertEqual(int(np.count_nonzero(u)),0)

    def test_partial_missing_alternative_does_not_replace_anything(self):
        ref=masks();alt=ref[1:].copy()
        out,u,q=mod.compare_aligned_masks(image(),ref,alt)
        np.testing.assert_array_equal(out,ref)
        self.assertEqual(q['objets'][0]['alternatives']['alternative_B']['statut'],'aucune_correspondance_suffisante')
        self.assertEqual(q['appariements']['alternative_B']['2']['index_alternatif'],1)

    def test_duplicate_alternatives_are_marked_ambiguous(self):
        ref=masks();alt=np.stack([ref[0],ref[0],ref[1]])
        out,u,q=mod.compare_aligned_masks(image(),ref,alt)
        np.testing.assert_array_equal(out,ref)
        self.assertEqual(q['sans_appariement_ou_ambigus']['alternative_B']['1'],'correspondance_ambigue')
        self.assertEqual(q['objets'][0]['selection'],'reference')

    def test_reference_duplicates_must_abstain(self):
        ref=np.stack([masks()[0]]*2)
        out,u,q=mod.compare_aligned_masks(image(),ref,masks()[0:1])
        self.assertFalse(q['appariements']['alternative_B'])
        self.assertTrue(q['sans_appariement_ou_ambigus']['alternative_B'])

    def test_different_shape_skipped_with_warning(self):
        ref=masks();b=np.ones((1,60,45),np.float32)
        out,u,q=mod.compare_aligned_masks(image(),ref,b)
        self.assertEqual(q['alternatives_disponibles'],[])
        self.assertTrue(q['avertissements'])

    def test_reference_wrong_shape_must_error(self):
        with self.assertRaisesRegex(mod.MaskComparisonError,'non alignes'):
            mod.compare_aligned_masks(image(),np.zeros((1,20,20),np.float32))

    def test_nan_or_255_rejected_not_silently_rescaled(self):
        ref=masks();ref[0,20,20]=float('nan')
        with self.assertRaises(mod.MaskComparisonError):mod.compare_aligned_masks(image(),ref)
        with self.assertRaisesRegex(mod.MaskComparisonError,'hors 0..1'):
            mod.compare_aligned_masks(image(),masks()*255)

    def test_uncertainty_highlights_mask_border_differences(self):
        ref=masks();alt=np.roll(ref,3,axis=2)
        out,u,q=mod.compare_aligned_masks(image(),ref,alt)
        self.assertGreater(np.count_nonzero(u),0)
        np.testing.assert_array_equal(out,ref)
        self.assertGreater(q['incertitude_pixels'],0)
        self.assertEqual(tuple(u.shape),(135,230))

    def test_reference_overlap_is_marked_uncertain(self):
        ref=masks();ref[1]=ref[0]
        out,u,q=mod.compare_aligned_masks(image(),ref)
        self.assertGreater(int(np.count_nonzero(u)),0)
        self.assertFalse(q['masque_reference_modifie'])

    def test_supervised_selection_needs_annotation(self):
        with self.assertRaisesRegex(mod.MaskComparisonError,'annotation'):
            mod.compare_aligned_masks(image(),masks(),mode='selection_avec_annotation')

    def test_supervised_selects_better_mask_matching_truth(self):
        gt=masks();ref=gt.copy();ref[0]=np.roll(ref[0],3,axis=1)
        alt=gt[::-1].copy()
        out,u,q=mod.compare_aligned_masks(image(),ref,alt,annotation=gt,mode='selection_avec_annotation')
        np.testing.assert_array_equal(out,gt)
        self.assertTrue(q['masque_annotation_fourni'])
        self.assertEqual(q['objets'][0]['selection'],'alternative_B')
        self.assertEqual(q['objets'][0]['mode_validation'],'comparee_a_annotation_explicite')

    def test_heuristic_mode_never_claims_ground_truth(self):
        ref=masks();alt=ref.copy()
        _,_,q=mod.compare_aligned_masks(image(),ref,alt,mode='selection_prudente')
        self.assertFalse(q['masque_annotation_fourni'])
        self.assertIn('PAS verite',q['sens_de_la_qualite'])

    def test_hungarian_finds_global_optimum_not_greedy(self):
        mat=np.array([[.99,.98],[.97,.01]])
        assigned=mod._hungarian_rect(1-mat)
        self.assertEqual(assigned,[1,0])

    def test_unmatchable_alt_never_forced(self):
        ref=masks();alt=np.zeros((2,135,230),np.float32)
        out,_,q=mod.compare_aligned_masks(image(),ref,alt)
        self.assertEqual(len(q['sans_appariement_ou_ambigus']['alternative_B']),2)
        np.testing.assert_array_equal(out,ref)

    def test_node_contract_and_tensor_outputs(self):
        cls=nodes.SmartSVGAlignMasksV198()
        im=torch.from_numpy(image().astype('float32')/255.).unsqueeze(0)
        ref=torch.from_numpy(masks())
        other=torch.from_numpy(masks()[::-1].copy())
        result,uncertain,report=cls.run(im,ref,masque_alternative_B=other)
        np.testing.assert_array_equal(result.numpy(),ref.numpy())
        self.assertEqual(tuple(uncertain.shape),(1,135,230))
        self.assertEqual(json.loads(report)['version'],'19.8-beta')

    def test_prod_node_diagnostic_does_not_mutate_cricut_inputs(self):
        im=torch.from_numpy(image().astype('float32')/255.).unsqueeze(0)
        ref=torch.from_numpy(masks())
        alt=torch.from_numpy(masks()[::-1].copy())
        seen=[]
        def fake_prod(self,**kw):
            seen.append(kw)
            return im,'CRICUT_ORIGINAL'
        with tempfile.TemporaryDirectory() as td:
            with patch.object(nodes.SmartSVGStudioV1971Expert,'execute',fake_prod):
                _,msg=nodes.SmartSVGStudioV198Expert().execute(image=im,
                    dossier_sortie=td,masques_objets=ref,
                    masque_alternative_B=alt,alignement_masques='diagnostic')
            self.assertEqual(len(seen),1)
            np.testing.assert_array_equal(seen[0]['masques_objets'].numpy(),ref.numpy())
            self.assertEqual(seen[0]['comparaison_masques'],'desactiver')
            self.assertIn('0/2 masque(s) alternatif(s)',msg)
            qa=list(Path(td).glob('ALIGNEMENT_MASQUES_V19_8_*.json'))
            self.assertEqual(len(qa),1)
            self.assertFalse(json.loads(qa[0].read_text())['masque_reference_modifie'])

    def test_report_write_failure_is_nonfatal(self):
        im=torch.from_numpy(image().astype('float32')/255.).unsqueeze(0)
        with patch.object(nodes.SmartSVGStudioV1971Expert,'execute',return_value=(im,'OK')):
            with patch.object(nodes,'_write_report',side_effect=PermissionError('readonly')):
                _,msg=nodes.SmartSVGStudioV198Expert().execute(image=im,dossier_sortie='ignored',
                     masques_objets=torch.from_numpy(masks()))
        self.assertIn('rapport appariement non enregistre',msg)

    def test_legacy_nodes_kept_and_new_workflows_ordered(self):
        for x in ['SmartSVGStudioV1971Expert','SmartSVGStudioV198Expert','SmartSVGAlignMasksV198']:
            self.assertIn(x,nodes.NODE_CLASS_MAPPINGS)
        for kind in ('Express','Expert'):
            wf=json.loads((ROOT/'example_workflows'/f'SmartSVG_Studio_V19_8_{kind}.json').read_text())
            typ=f'SmartSVGStudioV198{kind}'
            cls=nodes.NODE_CLASS_MAPPINGS[typ]
            nn=next(n for n in wf['nodes'] if n['type']==typ)
            widgets=[n['name'] for n in nn['inputs'] if n.get('widget')]
            expected=[n for n in cls.INPUT_TYPES()['required'] if n!='image']
            self.assertEqual(widgets,expected)
            self.assertEqual(len(widgets),len(nn['widgets_values']))
            by_id={n['id']:n for n in wf['nodes']}
            for lid,sid,slot,did,idx,lt in wf['links']:
                self.assertEqual(by_id[did]['inputs'][idx]['link'],lid)
                self.assertEqual(by_id[did]['inputs'][idx]['type'],lt)

    def test_actual_cricut_export_matches_v1971_in_diagnostic_mode(self):
        from hashlib import sha256
        old=importlib.import_module(PKG+'.node_v1971')
        im=torch.from_numpy(image().astype('float32')/255.).unsqueeze(0)
        ref=torch.from_numpy(masks())
        alt=torch.from_numpy(masks()[::-1].copy())
        with tempfile.TemporaryDirectory() as td:
            base=Path(td)
            old.SmartSVGStudioV1971Express().execute_express(im,str(base/'old'),
                type_fichier='photo',segmentation_objets='desactiver',
                analyse_florence='desactiver',masques_objets=ref,
                comparaison_masques='desactiver',profil_performances='desactiver')
            nodes.SmartSVGStudioV198Express().execute_express(im,str(base/'new'),
                type_fichier='photo',segmentation_objets='desactiver',
                analyse_florence='desactiver',masques_objets=ref,masque_alternative_B=alt,
                comparaison_masques='diagnostic',alignement_masques='diagnostic',
                profil_performances='desactiver')
            a=next((base/'old').glob('SmartSVG_V19_5_2_PHOTO_*'))
            b=next((base/'new').glob('SmartSVG_V19_5_2_PHOTO_*'))
            p1=sorted(a.glob('02_OBJETS_PNG/*_CRICUT_TEST.png'))
            p2=sorted(b.glob('02_OBJETS_PNG/*_CRICUT_TEST.png'))
            self.assertEqual(len(p1),2)
            self.assertEqual(len(p1),len(p2))
            for aa,bb in zip(p1,p2):
                self.assertEqual(sha256(aa.read_bytes()).digest(),sha256(bb.read_bytes()).digest())
            self.assertEqual(len(list((base/'new').glob('ALIGNEMENT_MASQUES_V19_8_*.json'))),1)

    def test_mask_budget_blocks_excessive_batches(self):
        rgb=np.zeros((1200,1300,3),np.uint8)
        big=np.zeros((14,1200,1300),np.uint8)
        with self.assertRaisesRegex(mod.MaskComparisonError,'Budget memoire'):
            mod.compare_aligned_masks(rgb,big,alt_b=big)

    def test_compare_and_export_requires_real_external_reference(self):
        wf=json.loads((ROOT/'example_workflows'/'SmartSVG_Studio_V19_8_Comparer_Puis_Exporter.json').read_text())
        node=next(n for n in wf['nodes'] if n['type']=='SmartSVGAlignMasksV198')
        required=next(n for n in node['inputs'] if n['name']=='masque_reference')
        self.assertIsNone(required['link']) # no fabricated masks
        self.assertTrue(any(link[1]==node['id'] and link[3]==2 and link[-1]=='MASK' for link in wf['links']))

if __name__=='__main__': unittest.main()
