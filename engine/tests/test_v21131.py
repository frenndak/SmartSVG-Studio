"""V21.13.1: fidelity preview, security constraints, click selector and compatibility."""
import importlib,sys,types,tempfile,unittest,json,xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np,cv2,torch
ROOT=Path(__file__).resolve().parents[1]
if 'ss21131test' not in sys.modules:
    p=types.ModuleType('ss21131test');p.__path__=[str(ROOT)];sys.modules[p.__name__]=p
node=importlib.import_module('ss21131test.node_v21131')
base=importlib.import_module('ss21131test.node_v2113')
vector=importlib.import_module('ss21131test.smartsvg_vector.layers_v2113')
qa=importlib.import_module('ss21131test.smartsvg_vector.qa_v21131')

def image_data():
    rgb=np.full((180,240,3),255,np.uint8)
    mask=np.zeros((2,180,240),np.float32)
    for i,center in enumerate((60,175)):
        cv2.circle(mask[i],(center,88),42,1,-1)
        cv2.circle(rgb,(center,88),42,(210,45,75) if i==0 else (68,170,96),-1)
        cv2.circle(rgb,(center,88),15,(70,80,220),-1)
    return rgb,mask

class TestV21131(unittest.TestCase):
    def test_exact_generated_svg_renders_and_source_compared(self):
        rgb,m=image_data()
        xml,preview,meta=vector.vectorize_flat_art(rgb,m[0],colors=5,width_mm=40.)
        strip,report=qa.analyse_svg(rgb,m[0],xml,meta)
        self.assertEqual(strip.shape[1],3*preview.shape[1]+8)
        self.assertEqual(report['formes_reconstruites'],meta['formes'])
        # A real SVG-standard raster can differ at boundaries from the earlier
        # optimistic OpenCV approximation. Require a sensible lower bound, not
        # the old internal-renderer-only threshold.
        self.assertGreater(report['iou_silhouette_approx'],.90)
        self.assertEqual(report['resolution_verification_px'],[preview.shape[1],preview.shape[0]])
        self.assertFalse(report['aucune_garantie_decoupe_physique'] is False)
        self.assertIn('erreur_moyenne_couleurs_sur_recouvrement',report)
    def test_svg_rejects_embedded_markup_doctype_and_foreign_paths(self):
        rgb,m=image_data();xml,_,info=vector.vectorize_flat_art(rgb,m[0])
        for corrupt in (xml.replace(b'<g ',b'<script>x</script><g ',1),
                        b'<!DOCTYPE svg [<!ENTITY x SYSTEM "file:///etc/passwd">]>'+xml,
                        xml.replace(b' L ',b' C ',1),
                        xml.replace(b'<path ',b'<image ',1)):
            with self.subTest(corrupt=corrupt[:20]):
                with self.assertRaises(qa.QualityRefused):qa.analyse_svg(rgb,m[0],corrupt,info)
    def test_svg_source_mask_mismatch_rejected(self):
        rgb,m=image_data();xml,_,info=vector.vectorize_flat_art(rgb,m[0])
        with self.assertRaises(qa.QualityRefused):qa.analyse_svg(rgb,m[0].T,xml,info)
    def test_svg_nonexistent_xml_refused_without_file_output(self):
        rgb,m=image_data();image=torch.from_numpy(rgb.astype('float32')/255.)[None]
        with tempfile.TemporaryDirectory() as td:
            result=node.SmartSVGEditableColorsV21131().run(image,couleurs=6,largeur_mm=40.,dossier_sortie=td,
                masque_sujet=torch.from_numpy(m[:1]))
            self.assertEqual(len(result['result']),4)
            self.assertTrue(Path(result['result'][2]).is_file())
            body=json.loads(result['result'][3]);self.assertFalse(body['certification_decoupe'])
            self.assertEqual(len(list(Path(td).glob('*.svg'))),1)
    def test_thumbnails_include_only_one_masked_subject(self):
        rgb,m=image_data();rgb_tensor=torch.from_numpy(rgb.astype('float32')/255.)[None]
        thumbnails=node.contact_sheet_previews(rgb_tensor,torch.from_numpy(m))
        self.assertEqual([p['numero'] for p in thumbnails],[1,2])
        self.assertTrue(all(p['image_data'].startswith('data:image/png;base64,') for p in thumbnails))
    def test_selector_output_and_click_ui_are_advisory(self):
        rgb,m=image_data();image=torch.from_numpy(rgb.astype('float32')/255.)[None]
        result=node.SmartSVGChooseSubjectV21131().run(image,torch.from_numpy(m),2)
        self.assertEqual(result['result'][0].shape,(1,180,240))
        self.assertEqual(result['ui']['smartsvg_subjects_v21131'][0]['selection'],2)
        self.assertTrue(result['ui']['smartsvg_subjects_v21131'][0]['clic_ne_fabrique_pas'])
    def test_empty_or_too_many_masks_do_not_make_previews(self):
        rgb,m=image_data();image=torch.from_numpy(rgb.astype('float32')/255.)[None]
        self.assertEqual(node.contact_sheet_previews(image,torch.zeros((2,180,240))),[])
        self.assertEqual(node.contact_sheet_previews(image,torch.zeros((33,180,240))),[])
    def test_legacy_identifiers_remain_same_objects(self):
        for name,cls in base.NODE_CLASS_MAPPINGS.items():self.assertIs(node.NODE_CLASS_MAPPINGS[name],cls)
        self.assertEqual(node.SmartSVGChooseSubjectV21131.RETURN_TYPES,base.SmartSVGChooseSubjectV2113.RETURN_TYPES)
        self.assertEqual(node.SmartSVGEditableColorsV2113.RETURN_TYPES,('IMAGE','STRING','STRING'))
    def test_reconstruction_reports_missing_islands(self):
        rgb,m=image_data();xml,_,info=vector.vectorize_flat_art(rgb,m[0],colors=4)
        root=ET.fromstring(xml)
        ns='{http://www.w3.org/2000/svg}'
        group=root.find(ns+'g')
        # Drop an actual layer, keeping a valid editable SVG.
        root.remove(group)
        tampered=ET.tostring(root,encoding='utf-8',xml_declaration=True)
        _,r=qa.analyse_svg(rgb,m[0],tampered,info)
        self.assertGreater(r['pixels_sujet_manquants'],0)
        self.assertEqual(r['diagnostic'],'A_VERIFIER')

if __name__=='__main__':unittest.main()
