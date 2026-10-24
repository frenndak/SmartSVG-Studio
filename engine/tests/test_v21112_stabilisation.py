"""V21.11.2: non-regression, guided width, read-only diagnostics, local-only status."""
from __future__ import annotations
import unittest, tempfile, types, importlib, sys, json, math
from unittest.mock import patch
from pathlib import Path
import numpy as np
import torch
import cv2
ROOT=Path(__file__).resolve().parents[1]
if 'ss21112test' not in sys.modules:
    p=types.ModuleType('ss21112test');p.__path__=[str(ROOT)];sys.modules[p.__name__]=p
node=importlib.import_module('ss21112test.node_v21112')
old=importlib.import_module('ss21112test.node_v2111')
readiness=importlib.import_module('ss21112test.smartsvg_compat.readiness_v21112')

class FakeSAM:
    RETURN_TYPES=('IMAGE','MASK')
    FUNCTION='segment_v2'
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'image':('IMAGE',),'prompt':('STRING',),
                'sam2_model':(['sam2.1_hiera_tiny'],),
                'dino_model':(['GroundingDINO_SwinT_OGC (694MB)'],),
                'device':(['Auto'],)}}


def sample(h=128,w=160):
    img=np.full((h,w,3),240,dtype=np.uint8)
    mask=np.zeros((h,w),dtype=np.float32)
    cv2.circle(mask,(w//2,h//2),36,1.,-1)
    cv2.circle(img,(w//2,h//2),36,(55,45,200),-1)
    return torch.from_numpy(img.astype(np.float32)/255)[None],torch.from_numpy(mask[None])

class TestsV21112(unittest.TestCase):
    def test_provider_absent_reports_not_tested(self):
        data=readiness.diagnose(registry={},cuda=False,modules={'torch':True,'PIL':True,'cv2':True})
        self.assertEqual(data['rmbg_sam2']['statut'],'ABSENT')
        self.assertFalse(data['inference_effectuee'])
        self.assertEqual(data['statut'],'FONDS_SIMPLES_SEULEMENT')

    def test_provider_incompatible_no_false_success(self):
        data=readiness.diagnose(registry={'SAM2Segment':type('Wrong',(),{'INPUT_TYPES':classmethod(lambda cls:{'required':{}})})},cuda=True,modules={'torch':True,'PIL':True,'cv2':True})
        self.assertEqual(data['rmbg_sam2']['statut'],'INCOMPATIBLE')
        self.assertFalse(data['inference_effectuee'])

    def test_provider_compatible_is_not_execution_proof(self):
        data=readiness.diagnose(registry={'SAM2Segment':FakeSAM},cuda=True,modules={'torch':True,'PIL':True,'cv2':True})
        self.assertEqual(data['rmbg_sam2']['statut'],'CONTRAT_COMPATIBLE_NON_EXECUTE')
        self.assertEqual(data['statut'],'IA_A_TESTER_EN_REEL')
        self.assertEqual(data['modele_disponible_sur_disque'],'NON_VERIFIE')

    def test_missing_dependency(self):
        data=readiness.diagnose(registry={},cuda=False,modules={'torch':False,'PIL':True,'cv2':True})
        self.assertEqual(data['statut'],'DEPENDANCES_MANQUANTES')

    def test_readiness_workflow_contract(self):
        obj=node.SmartSVGReadinessV21112()
        output=obj.run()['result'][0]
        self.assertFalse(json.loads(output)['inference_effectuee'])
        self.assertEqual(node.SmartSVGReadinessV21112.RETURN_TYPES,('STRING',))

    def test_width_from_unified_report(self):
        image,mask=sample()
        with patch('ss21112test.node_v2110.publish_native',return_value={'image':{'type':'output','filename':'source.png','subfolder':'qa'},'masks':[{'type':'output','filename':'mask.png','subfolder':'qa'}]}):
            a=node.SmartSVGUnifiedEditorV21112().run(image,masque_base=mask,largeur_mm=72.)
        self.assertEqual(a['result'][3],72.)
        info=json.loads(a['result'][2]);self.assertTrue(info['largeur_export_reelle_mm_connue'])
        self.assertEqual(info['largeur_qa_mm'],72.)
        self.assertEqual(a['ui']['smartsvg_unified'][0]['qa_width_mm'],72.)
        self.assertTrue(a['ui']['smartsvg_unified'][0]['real_size'])

    def test_qa_really_changes_with_width(self):
        img,mask=sample()
        a=node.SmartSVGUnifiedEditorV21112().run(img,masque_base=mask,largeur_mm=20.)
        b=node.SmartSVGUnifiedEditorV21112().run(img,masque_base=mask,largeur_mm=80.)
        self.assertTrue(torch.equal(a['result'][0],b['result'][0]))
        self.assertEqual(a['result'][0].shape,mask.shape)
        self.assertEqual(float(a['result'][3]),20.)
        self.assertEqual(float(b['result'][3]),80.)

    def test_old_editor_keeps_width_estimate_and_three_ports(self):
        img,mask=sample()
        obj=importlib.import_module('ss21112test.node_v2110').SmartSVGUnifiedEditorV2110()
        a=obj.run(img,masque_base=mask)
        info=json.loads(a['result'][2])
        self.assertEqual(len(a['result']),3)
        self.assertFalse(info['largeur_export_reelle_mm_connue'])
        self.assertEqual(info['largeur_qa_hypothese_mm'],40.)

    def test_bad_width_refused(self):
        img,mask=sample()
        for value in (0.,301.,float('nan'),float('inf'),True):
            with self.subTest(value=value),self.assertRaises(ValueError):
                node.SmartSVGUnifiedEditorV21112().run(img,masque_base=mask,largeur_mm=value)

    def test_new_express_report_and_manufacturing_unchanged(self):
        img,mask=sample()
        with tempfile.TemporaryDirectory() as d1,tempfile.TemporaryDirectory() as d2:
            kwargs={'projet':'Sticker - contour du sujet','largeur_mm':40.,
                    'qualite_ppp':'300','ia_locale':'Desactivee','masques_objets':mask}
            orig=old.SmartSVGAutoExpressV2111().run(img,dossier_sortie=d1,**kwargs)
            new=node.SmartSVGAutoExpressV21112().run(img,dossier_sortie=d2,**kwargs)
            r0=json.loads(orig['result'][2]);r1=json.loads(new['result'][2])
            status=r1['parcours_simple_v21112']
            self.assertEqual(status['statut'],'CONTROLE_LOCAL_OK_VERIFICATION_VISUELLE')
            self.assertFalse(status['decoupe_physique_executee'])
            self.assertFalse(status['import_design_space_execute'])
            f0=Path(r0['import_direct_cricut_v218']['objets'][0]['fichier_import'])
            f1=Path(r1['import_direct_cricut_v218']['objets'][0]['fichier_import'])
            self.assertEqual(f0.read_bytes(),f1.read_bytes())
            # Both original manufacturing files and their local import copies stay unchanged.
            for key in ('fichier_png_cricut','fichier_svg_contour'):
                self.assertEqual(Path(r0['objets'][0][key]).read_bytes(),Path(r1['objets'][0][key]).read_bytes())
            self.assertIn('CONTROLE_LOCAL_OK',new['result'][1])

    def test_registry_legacy_identities_retained(self):
        for k,v in old.NODE_CLASS_MAPPINGS.items():
            self.assertIs(node.NODE_CLASS_MAPPINGS[k],v)
        self.assertEqual(len(node.SmartSVGAutoExpressV21112.INPUT_TYPES()['required']),6)
        self.assertEqual(len(node.SmartSVGAutoExpressV21112.INPUT_TYPES()['optional']),2)

if __name__=='__main__':unittest.main()
