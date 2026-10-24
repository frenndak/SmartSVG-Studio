"""V21.7.1 automatic enhancement tests, CPU only, preserving Cricut geometry."""
from __future__ import annotations
import hashlib, importlib, json, os, sys, tempfile, types, unittest
from pathlib import Path
from unittest.mock import patch
import cv2
import numpy as np
import torch
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if 'sv2171test' not in sys.modules:
    m=types.ModuleType('sv2171test');m.__path__=[str(ROOT)];sys.modules[m.__name__]=m
node=importlib.import_module('sv2171test.node_v2171')
hd=importlib.import_module('sv2171test.smartsvg_quality.auto_hd')
old=importlib.import_module('sv2171test.node_v2151')

def sample():
    h,w=116,156
    rgb=np.full((h,w,3),.93,np.float32)
    masks=np.zeros((h,w),np.float32)
    cv2.circle(masks,(77,60),35,1,-1)
    rgb[masks>0]=[.3,.43,.82]
    return torch.from_numpy(rgb)[None],torch.from_numpy(masks)

def run_node(cls,directory,dpi='300'):
    image, mask=sample()
    return cls().run(image=image, masques_objets=mask,dossier_sortie=directory,
                     projet='Sticker - contour du sujet',largeur_mm=35,qualite_ppp=dpi)

class AutomaticHD(unittest.TestCase):
    def test_ports_and_legacy_registry(self):
        self.assertEqual(node.SmartSVGExpressV2171.INPUT_TYPES(),old.SmartSVGExpressV2151.INPUT_TYPES())
        self.assertEqual(node.SmartSVGExpressV2171.RETURN_TYPES,old.SmartSVGExpressV2151.RETURN_TYPES)
        self.assertEqual(len(node.SmartSVGExpressV2171.INPUT_TYPES()['required']),6)
        for key in ('SmartSVGExpressV2151','SmartSVGMaskEditorV216','SmartSVGPrepareV217',
                    'SmartSVGQualityV217','SmartSVGExpressV2171'):
            self.assertIn(key,node.NODE_CLASS_MAPPINGS)

    def test_one_output_hd_and_native_files_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            r1=json.loads(run_node(old.SmartSVGExpressV2151,td+'/legacy')['result'][2])
            r2=run_node(node.SmartSVGExpressV2171,td+'/new')
            report=json.loads(r2['result'][2]);quality=report['amelioration_hd_v2171']
            self.assertEqual(quality['statut'],'complete')
            self.assertEqual((quality['produits'],quality['total']),(1,1))
            def hashes(r):
                obj=r['objets'][0]
                return [hashlib.sha256(Path(obj[k]).read_bytes()).hexdigest()
                        for k in ('fichier_png_cricut','fichier_svg_contour','fichier_transparent')]
            self.assertEqual(hashes(r1),hashes(report))
            with Image.open(report['objets'][0]['fichier_png_cricut']) as original, \
                 Image.open(quality['fichiers'][0]['fichier_hd']) as result:
                self.assertGreater(result.width,original.width)
                self.assertEqual(result.mode,'RGBA')
                self.assertTrue(hd._alpha_compatible(original,result))
                self.assertAlmostEqual(original.width*25.4/300,result.width*25.4/600,delta=.05)
            self.assertIn('HD automatique : 1/1',r2['result'][1])
            independent=Path(report['dossier'])/hd.FOLDER/'RAPPORT_HD_V21_7_1.json'
            self.assertEqual(json.loads(independent.read_text('utf-8'))['produits'],1)

    def test_450_ppp_auto_goes_to_600_and_is_not_fake_x2(self):
        with tempfile.TemporaryDirectory() as td:
            report=json.loads(run_node(node.SmartSVGExpressV2171,td,'450')['result'][2])
            with Image.open(report['objets'][0]['fichier_png_cricut']) as original, \
                 Image.open(report['amelioration_hd_v2171']['fichiers'][0]['fichier_hd']) as output:
                self.assertAlmostEqual(output.width/original.width,600/450,delta=.01)

    def test_fabrication_errors_are_not_swallowed(self):
        img,mask=sample()
        with patch.object(old.SmartSVGExpressV2151,'run',side_effect=ValueError('manufacture error')):
            with self.assertRaisesRegex(ValueError,'manufacture error'):
                node.SmartSVGExpressV2171().run(img,masques_objets=mask)

    def test_hd_failure_does_not_break_original(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(node,'automatic_hd',side_effect=RuntimeError('gpu unavailable')):
                r=run_node(node.SmartSVGExpressV2171,td)
            report=json.loads(r['result'][2]);self.assertNotIn('amelioration_hd_v2171',report)
            self.assertTrue(Path(report['objets'][0]['fichier_png_cricut']).exists())
            self.assertIn('indisponible',r['result'][1])

    def test_fail_closed_for_empty_report(self):
        with tempfile.TemporaryDirectory() as td:
            report={'dossier':td,'objets':[]}
            self.assertEqual(hd.automatic_hd(report,300)['statut'],'ignore')

    def test_block_symlink_outside_path_and_preserve_foreign_files(self):
        with tempfile.TemporaryDirectory() as td:
            project=Path(td)/'project';project.mkdir()
            secret=Path(td)/'sensitive.png';Image.new('RGBA',(32,30),'red').save(secret)
            before=secret.read_bytes()
            bad={'dossier':str(project),'objets':[{'fichier_png_cricut':str(secret)}]}
            rep=hd.automatic_hd(bad,300)
            self.assertEqual(rep['produits'],0)
            self.assertIn('hors du dossier',rep['fichiers'][0]['raison'])
            self.assertEqual(before,secret.read_bytes())
            source=project/'linked.png';source.symlink_to(secret)
            bad['objets'][0]['fichier_png_cricut']=str(source)
            rep=hd.automatic_hd(bad,300)
            self.assertEqual(rep['produits'],0)
            self.assertIn('symbolique',rep['fichiers'][0]['raison'])

    def test_hd_memory_cap_skips_without_allocating(self):
        with tempfile.TemporaryDirectory() as td:
            project=Path(td);original=project/'source.png'
            Image.new('RGBA',(1900,1600),(22,33,44,255)).save(original)
            rep=hd.automatic_hd({'dossier':td,'objets':[{'png':str(original)}]},300)
            self.assertEqual(rep['produits'],0)
            self.assertIn('limite',rep['fichiers'][0]['raison'].lower())
            self.assertFalse((project/hd.FOLDER/'sujet_001_HD.png').exists())

    def test_noise_gate_is_nondestructive(self):
        noisy=np.random.default_rng(12).integers(0,256,(220,180,3),dtype=np.uint8)
        src=Image.fromarray(np.dstack([noisy,np.full((220,180),255,np.uint8)]),'RGBA')
        got,note,noise=hd._enhance_rgb_preserving_alpha(src,(360,440))
        self.assertEqual(got.size,(360,440))
        self.assertIn('reéchantillonnage seul',note)
        self.assertGreater(noise,5.0)
        self.assertEqual(np.asarray(got)[:,:,3].min(),255)

    def test_soft_edge_and_svg_wont_be_replaced(self):
        with tempfile.TemporaryDirectory() as td:
            mask=np.zeros((100,140),np.uint8);cv2.ellipse(mask,(70,50),(45,25),0,0,360,255,-1)
            rgba=np.full((100,140,4),255,np.uint8);rgba[:,:,3]=cv2.GaussianBlur(mask,(3,3),0)
            file=Path(td)/'native.png';Image.fromarray(rgba,'RGBA').save(file)
            sha=hashlib.sha256(file.read_bytes()).hexdigest()
            out=hd.automatic_hd({'dossier':td,'objets':[{'png':str(file)}]},300)
            self.assertEqual(out['produits'],1)
            self.assertEqual(sha,hashlib.sha256(file.read_bytes()).hexdigest())

    def test_12_subjects_full_pipeline(self):
        image=np.ones((320,480,3),np.float32)
        masks=np.zeros((12,320,480),np.float32)
        yy,xx=np.ogrid[:320,:480]
        for i in range(12):
            cx,cy=(i%4)*120+60,(i//4)*105+52
            m=((xx-cx)**2+(yy-cy)**2)<26**2
            masks[i,m]=1
            image[m]=[.17+.1*(i%4),.34,.65]
        with tempfile.TemporaryDirectory() as td:
            result=node.SmartSVGExpressV2171().run(
                image=torch.from_numpy(image)[None],masques_objets=torch.from_numpy(masks),
                dossier_sortie=td, projet='Planche - 12 images (4x3)',largeur_mm=35)
            doc=json.loads(result['result'][2]);quality=doc['amelioration_hd_v2171']
            self.assertEqual(quality['produits'],12)
            self.assertEqual(quality['total'],12)
            self.assertEqual(len(doc['objets']),12)
            self.assertEqual(len(doc.get('planches_cricut',doc.get('planches',[]))),1)

    def test_seven_example_input_styles_processor_only(self):
        # Optional photos attached to the conversation; tests still pass in a clean install.
        names=('1000077568.jpg','1000077534.jpg','1000077546.png',
               '1000077554.png','1000077435.png','1000076838.jpg','1000076753.webp')
        for name in names:
            p=Path('/mnt/data')/name
            if not p.exists():continue
            with self.subTest(filename=name):
                with Image.open(p) as im:
                    rgb=im.convert('RGB');rgb.thumbnail((380,380))
                    src=rgb.convert('RGBA')
                saved=np.asarray(src).copy()
                result,method,noise=hd._enhance_rgb_preserving_alpha(src,(src.width*2,src.height*2))
                self.assertEqual(result.size,(src.width*2,src.height*2))
                self.assertGreaterEqual(noise,0)
                self.assertTrue(hd._alpha_compatible(src,result))
                self.assertTrue(np.array_equal(saved,np.asarray(src)))

if __name__ == '__main__': unittest.main()
