"""V21.5 tests: bounded non-destructive visual bridge + stable node contracts."""
import importlib,hashlib,json,re,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
import cv2
import numpy as np
import torch
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
if 'smartsvg215test' not in sys.modules:
    p=types.ModuleType('smartsvg215test');p.__path__=[str(ROOT)];sys.modules['smartsvg215test']=p
ui=importlib.import_module('smartsvg215test.smartsvg_ui.presentation')
bridge=importlib.import_module('smartsvg215test.smartsvg_ui.preview_bridge')
node=importlib.import_module('smartsvg215test.node_v215')
old=importlib.import_module('smartsvg215test.node_v214')


def fixture():
    img=np.full((150,190,3),250,np.uint8)
    mask=np.zeros((150,190),np.uint8)
    cv2.circle(img,(95,70),32,(90,140,215),-1)
    cv2.circle(mask,(95,70),32,1,-1)
    return torch.from_numpy(img.astype(np.float32)/255)[None],torch.from_numpy(mask)

class UIContractTests(unittest.TestCase):
    def test_legacy_node_ports(self):
        self.assertEqual(node.SmartSVGExpressV215.RETURN_TYPES,old.SmartSVGExpressV214.RETURN_TYPES)
        self.assertEqual(node.SmartSVGExpressV215.INPUT_TYPES(),old.SmartSVGExpressV214.INPUT_TYPES())
    def test_legacy_aliases(self):
        for key in ('SmartSVGExpressV215','SmartSVGExpressV214','SmartSVGExpressV2132','SmartSVGSimpleV206','SmartSVGLineArtV205'):
            self.assertIn(key,node.NODE_CLASS_MAPPINGS)
    def test_no_extra_express_setting(self):
        spec=node.SmartSVGExpressV215.INPUT_TYPES()
        self.assertEqual(len(spec['required']),6)
    def test_empty_report(self):
        result=ui.build_presentation({},mask_external=False)
        self.assertEqual(result['objets_total'],0)
        self.assertFalse(result['decoupe_cricut_certifiee'])
    def test_mask_source_honesty(self):
        report={'nombre_objets_exportes':2}
        self.assertIn('masques externes',ui.build_presentation(report,mask_external=True)['provenance'])
        self.assertIn('demandée',ui.build_presentation(report,ai_mode='Si disponible')['provenance'])
    def test_cards_maximum(self):
        report={'controle_v212':{'objets':[{'verdict':'RISQUE_ELEVE','largeur_png_mm_si_ppp_respectes':31,'avertissements':['bad']*30}]*80}}
        model=ui.build_presentation(report)
        self.assertEqual(len(model['objets']),32)
        self.assertEqual(len(model['objets'][0]['alertes']),6)
    def test_malformed_data_no_crash(self):
        report={'nombre_objets_exportes':'unknown','planches_cricut':[],
                'controle_v212':{'objets':[None,[],{'largeur_png_mm_si_ppp_respectes':'nan','verdict':'GOOD'}]}}
        r=ui.build_presentation(report)
        self.assertEqual(r['objets_total'],1)
        self.assertIsNone(r['objets'][0]['largeur_mm'])
        self.assertEqual(r['objets'][0]['etat'],'A_VERIFIER')
    def test_alert_count_ignores_bool_and_negative(self):
        r=ui.build_presentation({'controle_v212':{'alertes':{'a':True,'b':-1,'c':5}}})
        self.assertEqual(r['alertes_total'],5)
    def test_no_absolute_paths_in_object_cards(self):
        r=ui.build_presentation({'controle_v212':{'objets':[{'fichier_png_cricut':'/secret/user/something.png'}]}})
        self.assertNotIn('/secret',json.dumps(r))
    def test_preview_source_bound_to_qa(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'project';qa=root/'05_CONTROLE_V21_2';qa.mkdir(parents=True)
            Image.new('RGB',(90,75),'white').save(qa/'APERÇU_GLOBAL.png')
            Image.new('RGB',(80,55),'white').save(qa/'OBJET_01_AVANT_APRES.png')
            (root/'other.png').write_bytes(b'dont copy')
            sources=bridge.preview_sources({'dossier':str(root)})
            self.assertEqual(len(sources),2)
            self.assertNotIn('other.png',[s[0] for s in sources])
    def test_symlink_previews_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'project';qa=root/'05_CONTROLE_V21_2';qa.mkdir(parents=True)
            out=Path(temp)/'outsider.png';Image.new('RGB',(80,80)).save(out)
            (qa/'APERÇU_GLOBAL.png').symlink_to(out)
            self.assertEqual(bridge.preview_sources({'dossier':str(root)}),[])
    def test_preview_copy_to_output_and_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'project';qa=root/'05_CONTROLE_V21_2';qa.mkdir(parents=True)
            Image.new('RGB',(1024,640),'red').save(qa/'APERÇU_GLOBAL.png')
            outputs=bridge.publish_previews({'dossier':str(root)},Path(temp)/'out')
            self.assertEqual(len(outputs),1)
            self.assertEqual(outputs[0]['subfolder'],'SmartSVG_Studio_Previews')
            image=Path(temp)/'out'/outputs[0]['subfolder']/outputs[0]['filename']
            self.assertTrue(image.exists())
            with Image.open(image) as im:
                self.assertLessEqual(max(im.size),840)
                self.assertEqual(im.mode,'RGB')
    def test_preview_output_does_not_modify_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'project';qa=root/'05_CONTROLE_V21_2';qa.mkdir(parents=True)
            src=qa/'APERÇU_GLOBAL.png';Image.new('RGB',(120,95),'blue').save(src)
            digest=hashlib.sha256(src.read_bytes()).hexdigest()
            bridge.publish_previews({'dossier':str(root)},Path(temp)/'out')
            self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(),digest)
    def test_disallow_symlink_output_root(self):
        with tempfile.TemporaryDirectory() as temp:
            target=Path(temp)/'real';target.mkdir();alias=Path(temp)/'link';alias.symlink_to(target, target_is_directory=True)
            self.assertEqual(bridge.publish_previews({},alias),[])
    def test_missing_folder_paths_graceful(self):
        with patch.object(node,'_comfy_output_directory',return_value=None):
            self.assertIsNone(node._comfy_output_directory())
    def test_web_files_declared(self):
        p=ROOT/'web/js/smartsvg_ui.js'
        self.assertTrue(p.is_file())
        self.assertIn('registerExtension',p.read_text())
    def test_report_node_produces_visual_payload(self):
        image,mask=fixture()
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(node,'_comfy_output_directory',return_value=Path(temp)/'output'):
                out=node.SmartSVGExpressV215().run(image=image,dossier_sortie=str(Path(temp)/'projects'),
                    projet='Sticker - contour du sujet',largeur_mm=35.,masques_objets=mask)
            self.assertEqual(out['result'][0].ndim,4)
            self.assertIn('smartsvg',out['ui'])
            self.assertEqual(out['ui']['smartsvg'][0]['objets_total'],1)
            self.assertTrue(out['ui']['smartsvg_previews'])
            self.assertFalse(out['ui']['smartsvg'][0]['decoupe_cricut_certifiee'])
    def test_preview_failure_does_not_break_production(self):
        image,mask=fixture()
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(node,'publish_previews',side_effect=OSError('read-only')):
                out=node.SmartSVGExpressV215().run(image=image,dossier_sortie=temp,
                    projet='Sticker - contour du sujet',largeur_mm=35.,masques_objets=mask)
            self.assertEqual(out['ui']['smartsvg_previews'],[])
            self.assertEqual(out['ui']['smartsvg'][0]['objets_total'],1)
    def test_unchanged_png_svg_between_v214_v215(self):
        image,mask=fixture()
        with tempfile.TemporaryDirectory() as temp:
            def files(cls,label):
                out=cls().run(image=image,dossier_sortie=str(Path(temp)/label),
                    projet='Sticker - contour du sujet',largeur_mm=35.,masques_objets=mask)
                report=json.loads(out['result'][2]);o=report['objets'][0]
                return [hashlib.sha256(Path(o[key]).read_bytes()).hexdigest()
                        for key in ('fichier_png_cricut','fichier_svg_contour','fichier_transparent')]
            with patch.object(node,'_comfy_output_directory',return_value=None):
                self.assertEqual(files(old.SmartSVGExpressV214,'old'),files(node.SmartSVGExpressV215,'new'))

if __name__=='__main__':unittest.main()
