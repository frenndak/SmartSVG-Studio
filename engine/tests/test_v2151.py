"""V21.5.1: UI-only audits, failure containment, storage and byte parity."""
import hashlib, importlib, json, os, sys, tempfile, types, unittest
from pathlib import Path
from unittest.mock import patch
import cv2
import numpy as np
import torch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
if 'sv2151test' not in sys.modules:
    pkg=types.ModuleType('sv2151test');pkg.__path__=[str(ROOT)];sys.modules[pkg.__name__]=pkg
node=importlib.import_module('sv2151test.node_v2151')
old=importlib.import_module('sv2151test.node_v215')
engine=importlib.import_module('sv2151test.node_v214')
bridge=importlib.import_module('sv2151test.smartsvg_ui.preview_bridge_v2151')


def source():
    img=np.full((145,210,3),250,np.uint8)
    mask=np.zeros((145,210),np.uint8)
    cv2.circle(img,(103,73),35,(140,90,65),-1)
    cv2.circle(mask,(103,73),35,1,-1)
    return torch.from_numpy(img.astype(np.float32)/255)[None],torch.from_numpy(mask)

class TestV2151(unittest.TestCase):
    def test_legacy_nodes_preserved(self):
        for name in ('SmartSVGExpressV214','SmartSVGExpressV215','SmartSVGExpressV2151','SmartSVGInstancesV2151','SmartSVGDiagnosticV2151'):
            self.assertIn(name,node.NODE_CLASS_MAPPINGS)
    def test_ports_and_inputs_unchanged(self):
        self.assertEqual(node.SmartSVGExpressV2151.INPUT_TYPES(),old.SmartSVGExpressV215.INPUT_TYPES())
        self.assertEqual(node.SmartSVGExpressV2151.RETURN_TYPES,old.SmartSVGExpressV215.RETURN_TYPES)
        self.assertEqual(len(node.SmartSVGExpressV2151.INPUT_TYPES()['required']),6)
    def test_ui_only_failure_does_not_fail_fabrication(self):
        img,mask=source()
        with tempfile.TemporaryDirectory() as td:
            with patch.object(node,'build_presentation',side_effect=RuntimeError('view bug')):
                out=node.SmartSVGExpressV2151().run(image=img,dossier_sortie=td,
                    projet='Sticker - contour du sujet',largeur_mm=35.,masques_objets=mask)
            self.assertEqual(out['ui']['smartsvg'],[])
            self.assertEqual(out['ui']['smartsvg_previews'],[])
            report=json.loads(out['result'][2]);obj=report['objets'][0]
            self.assertTrue(Path(obj['fichier_png_cricut']).is_file())
            self.assertIn('indisponible',out['ui']['text'][0])
    def test_unusual_preview_error_is_contained(self):
        img,mask=source()
        with tempfile.TemporaryDirectory() as td:
            with patch.object(node,'publish_previews',side_effect=KeyError('ui metadata')):
                out=node.SmartSVGExpressV2151().run(image=img,dossier_sortie=td,
                    projet='Sticker - contour du sujet',largeur_mm=35.,masques_objets=mask)
            self.assertEqual(out['ui']['smartsvg_previews'],[])
            self.assertEqual(out['ui']['smartsvg'][0]['objets_total'],1)
    def test_fabrication_exception_not_swallowed(self):
        img,mask=source()
        with patch.object(engine.SmartSVGExpressV214,'run',side_effect=ValueError('bad mask')):
            with self.assertRaisesRegex(ValueError,'bad mask'):
                node.SmartSVGExpressV2151().run(image=img,masques_objets=mask)
    def test_same_production_bytes_all_three_versions(self):
        img,mask=source()
        with tempfile.TemporaryDirectory() as td:
            def files(cls,key):
                with patch.object(node,'_comfy_output_directory',return_value=None):
                    res=cls().run(image=img,dossier_sortie=str(Path(td)/key),
                        projet='Sticker - contour du sujet',largeur_mm=35.,masques_objets=mask)
                report=json.loads(res['result'][2]);obj=report['objets'][0]
                return [hashlib.sha256(Path(obj[k]).read_bytes()).digest()
                    for k in ('fichier_png_cricut','fichier_svg_contour','fichier_transparent')]
            self.assertEqual(files(engine.SmartSVGExpressV214,'v214'),files(node.SmartSVGExpressV2151,'v2151'))
    def test_preview_retention_hard_bound(self):
        with tempfile.TemporaryDirectory() as td:
            project=Path(td)/'project';qa=project/'05_CONTROLE_V21_2';qa.mkdir(parents=True)
            Image.new('RGB',(120,110),'white').save(qa/'APERÇU_GLOBAL.png')
            output=Path(td)/'output';dest=output/'SmartSVG_Studio_Previews';dest.mkdir(parents=True)
            for i in range(110):
                file=dest/f'qa_global_{i:014d}.png';file.write_bytes(b'test preview')
                os.utime(file,(100000+i,100000+i))
            result=bridge.publish_previews({'dossier':str(project)},output)
            all_owned=list(dest.glob('qa_*.png'))
            self.assertLessEqual(len(all_owned),bridge.MAX_OWNED_PREVIEWS)
            self.assertTrue((dest/result[0]['filename']).exists())
    def test_preview_not_permanent_with_retention(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'output';folder=out/'SmartSVG_Studio_Previews';folder.mkdir(parents=True)
            previous=folder/'qa_global_abcdef12345678.png';previous.write_bytes(b'sample')
            os.utime(previous,(100000,100000))
            bridge.publish_previews({},out)
            self.assertFalse(previous.exists())
    def test_never_delete_user_output(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'output';folder=out/'SmartSVG_Studio_Previews';folder.mkdir(parents=True)
            user=folder/'my_family_photo.png';user.write_bytes(b'user content')
            bridge.publish_previews({},out)
            self.assertEqual(user.read_bytes(),b'user content')
    def test_dangerous_symlink_source_not_used(self):
        with tempfile.TemporaryDirectory() as td:
            project=Path(td)/'project';qa=project/'05_CONTROLE_V21_2';qa.mkdir(parents=True)
            outsider=Path(td)/'secret.png';Image.new('RGB',(20,20)).save(outsider)
            (qa/'APERÇU_GLOBAL.png').symlink_to(outsider)
            self.assertEqual(bridge.publish_previews({'dossier':str(project)},Path(td)/'output'),[])
    def test_max_side_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            project=Path(td)/'project';qa=project/'05_CONTROLE_V21_2';qa.mkdir(parents=True)
            Image.new('RGB',(1450,1300),'red').save(qa/'APERÇU_GLOBAL.png')
            refs=bridge.publish_previews({'dossier':str(project)},Path(td)/'out',max_side=10000)
            with Image.open(Path(td)/'out'/'SmartSVG_Studio_Previews'/refs[0]['filename']) as im:
                self.assertLessEqual(max(im.size),840)
    def test_ui_payload_counts(self):
        img,mask=source()
        with tempfile.TemporaryDirectory() as td:
            with patch.object(node,'_comfy_output_directory',return_value=None):
                r=node.SmartSVGExpressV2151().run(image=img,dossier_sortie=td,
                    projet='Sticker - contour du sujet',masques_objets=mask)
            self.assertEqual(r['ui']['smartsvg'][0]['objets_total'],1)
            self.assertEqual(r['ui']['smartsvg_previews'],[])
    def test_python_frontend_file_present(self):
        self.assertTrue((ROOT/'web/js/smartsvg_ui_v2151.js').is_file())
        self.assertTrue((ROOT/'web/js/smartsvg_ui_model_v2151.mjs').is_file())

if __name__=='__main__':unittest.main()
