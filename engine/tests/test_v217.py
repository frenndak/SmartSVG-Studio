"""V21.7 quality and preparation regressions; no GPU/Comfy UI needed."""
from __future__ import annotations
import importlib,json,sys,tempfile,time,types,unittest
from pathlib import Path
from unittest.mock import patch
import cv2
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1]
if 'sv217test' not in sys.modules:
    m=types.ModuleType('sv217test');m.__path__=[str(ROOT)];sys.modules[m.__name__]=m
node=importlib.import_module('sv217test.node_v217')
geo=importlib.import_module('sv217test.smartsvg_quality.geometry')
prep=importlib.import_module('sv217test.smartsvg_quality.prepare')
preview=importlib.import_module('sv217test.smartsvg_quality.previews')


def img(w=180,h=120):return torch.zeros((1,h,w,3),dtype=torch.float32)
def mask(w=180,h=120):
    m=np.zeros((1,h,w),dtype=np.float32)
    m[0,20:100,40:140]=1
    return m

class Preparation(unittest.TestCase):
    def test_noop_bitwise_rgb_alpha_and_device(self):
        a=torch.rand((1,120,180,4),dtype=torch.float32)
        actual,report=node.SmartSVGPrepareV217().run(a)
        self.assertTrue(torch.equal(a,actual))
        self.assertFalse(json.loads(report)['modifie'])
    def test_manual_exact_box_preserves_values(self):
        a=torch.rand((1,120,180,3))
        cropped,s=node.SmartSVGPrepareV217().run(a,'Recadrage manuel (%)',10,20,25,25)
        self.assertTrue(torch.equal(cropped,a[:,30:90,18:144,:]))
        self.assertEqual(json.loads(s)['zone_px'],[18,30,144,90])
    def test_black_bands_synthetic(self):
        a=np.zeros((500,280,3),dtype=np.float32)
        a[75:395]=np.random.default_rng(8).uniform(.12,.75,size=(320,280,3))
        a[:40]=.8;a[435:]=.8
        crop,report=prep.prepare(a,'Retirer bandes noires (prudent)')
        self.assertTrue(report['modifie'])
        self.assertEqual(report['zone_px'],[0,75,280,395])
        self.assertEqual(crop.shape,(320,280,3))
    def test_dark_scene_safe(self):
        a=np.random.default_rng(73).uniform(.01,.17,size=(380,240,3)).astype(np.float32)
        _,r=prep.prepare(a,'Retirer bandes noires (prudent)')
        self.assertFalse(r['modifie'])
    def test_ambiguous_multi_content_fail_safe(self):
        a=np.ones((800,300,3),dtype=np.float32)*.6
        a[200:260]=0
        a[500:570]=0
        # only one non-black region is bracketed but short 240px and unmatched at lower end.
        _,r=prep.prepare(a,'Retirer bandes noires (prudent)')
        self.assertFalse(r['modifie'])
    def test_reject_invalid_inputs(self):
        for x in [-1,46,1.2,True]:
            with self.assertRaises(prep.PreparationError):prep.crop_manual(np.zeros((120,180,3)),left=x)
        with self.assertRaises(prep.PreparationError):node.SmartSVGPrepareV217().run(torch.zeros(2,30,30,3))
        with self.assertRaises(prep.PreparationError):prep.prepare(np.full((130,150,3),np.nan))
    def test_dont_erase_source_mask_contract(self):
        a=img()
        res=node.SmartSVGPrepareV217().run(a,'Conserver original')[0]
        self.assertEqual(tuple(res.shape),tuple(a.shape))
        self.assertIn('SmartSVGMaskEditorV216',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGExpressV2151',node.NODE_CLASS_MAPPINGS)
    def test_seven_user_cases_conservative(self):
        paths={
          '1000077568.jpg':False,
          '1000077534.jpg':False,
          '1000077546.png':False,
          '1000077554.png':False,
          '1000077435.png':False,
          '1000076838.jpg':True,
          '1000076753.webp':False,
        }
        from PIL import Image
        for filename,expect in paths.items():
            p=Path('/mnt/data')/filename
            if not p.exists():continue # portable archive also tests synthetic screenshots
            a=np.asarray(Image.open(p).convert('RGB'),dtype=np.float32)/255
            _,r=prep.prepare(a,'Retirer bandes noires (prudent)')
            with self.subTest(filename=filename):
                self.assertEqual(r['modifie'],expect)
                if expect:self.assertEqual(r['zone_px'][1:4:2],[334,1026])

class Quality(unittest.TestCase):
    def test_mask_pass_through_exact_and_json(self):
        image=img();m=torch.from_numpy(mask())
        with patch.object(node,'_output_directory',return_value=None):
            out=node.SmartSVGQualityV217().run(image,m,20)
        self.assertIs(out['result'][0],m)
        self.assertIs(out['result'][1],image)
        qa=json.loads(out['result'][2])
        self.assertEqual(qa['statut'],'ok')
        self.assertEqual(qa['objets'][0]['composants'],1)
        self.assertEqual(qa['objets'][0]['largeur_px'],100)
    def test_detect_detached_micro_island(self):
        m=mask();m[0,1:3,2:4]=1
        qa=geo.inspect(m,width_mm=40)
        flags=qa['objets'][0]['alertes']
        self.assertIn('ILOTS_DETACHES',flags)
        self.assertIn('MICRO_ILOTS',flags)
        self.assertEqual(m[0,1,2],1) # never delete automatically
    def test_detect_micro_hole(self):
        m=mask();m[0,47:49,63:65]=0
        qa=geo.inspect(m,width_mm=20)
        self.assertIn('MICRO_TROUS',qa['objets'][0]['alertes'])
    def test_detect_border_and_overlap(self):
        a=np.zeros((2,120,180),dtype=np.float32)
        a[0,5:50,0:70]=1;a[1,10:65,30:90]=1
        r=geo.inspect(a)
        self.assertTrue(all('MASQUES_CHEVAUCHANTS' in o['alertes'] for o in r['objets']))
        self.assertIn('MASQUE_TOUCHE_BORD_IMAGE',r['objets'][0]['alertes'])
        self.assertEqual(r['nombre_objets'],2)
    def test_empty_mask_is_blocking_not_crash(self):
        m=np.zeros((2,30,30),dtype=np.float32)
        r=geo.inspect(m)
        self.assertEqual(r['statut'],'bloquant')
        self.assertIn('MASQUE_VIDE',r['objets'][0]['alertes'])
    def test_tiny_dangling_bridge_detect(self):
        m=np.zeros((1,120,180),dtype=np.float32)
        m[0,30:90,15:60]=1;m[0,30:90,90:155]=1;m[0,59:61,60:90]=1
        q=geo.inspect(m,width_mm=20)
        self.assertIn('PASSAGE_FIN_A_VERIFIER',q['objets'][0]['alertes'])
    def test_threshold_and_mm_respecting(self):
        m=mask();m[:]*=.49
        self.assertEqual(geo.inspect(m,threshold=.5)['statut'],'bloquant')
        self.assertEqual(geo.inspect(m,threshold=.4,width_mm=20)['statut'],'ok')
        with self.assertRaises(geo.GeometryError):geo.inspect(m,width_mm=0)
        with self.assertRaises(geo.GeometryError):geo.inspect(m,width_mm=float('nan'))
    def test_reject_mismatch_and_nonfinite(self):
        with self.assertRaises(geo.GeometryError):node.SmartSVGQualityV217().run(img(),torch.zeros(1,50,50))
        bad=mask();bad[0,0,0]=np.nan
        with self.assertRaises(geo.GeometryError):geo.inspect(bad)
    def test_optional_preview_failure_no_export_failure(self):
        with patch.object(node,'publish',side_effect=RuntimeError('preview')):
            out=node.SmartSVGQualityV217().run(img(),torch.from_numpy(mask()),20)
        self.assertEqual(json.loads(out['result'][2])['statut'],'ok')
        self.assertIn('indisponible',out['ui']['text'][-1])
    def test_preview_lifecycle_no_foreign_delete(self):
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)/preview.FOLDER;folder.mkdir()
            keep=folder/'rapport_photo.png';keep.write_bytes(b'keep')
            for i in range(57):
                file=folder/f'qa217_{i:024x}.png';file.write_bytes(b'old')
                import os;os.utime(file,(1+i,1+i))
            base=img()[0].numpy();m=mask();r=geo.inspect(m)
            obj=preview.publish(base,m,r,td)
            self.assertTrue((folder/obj['filename']).exists())
            self.assertEqual(keep.read_bytes(),b'keep')
            self.assertLessEqual(len(list(folder.glob('qa217_*.png'))),preview.MAX_FILES)
    def test_32_objects_qa_bounds(self):
        masks=np.zeros((32,64,64),dtype=np.float32)
        for i in range(32):masks[i,10+i//4:20+i//4,10+i%4*12:18+i%4*12]=1
        self.assertEqual(geo.inspect(masks)['nombre_objets'],32)
        with self.assertRaises(geo.GeometryError):geo.inspect(np.zeros((33,64,64),np.float32))


class Integration(unittest.TestCase):
    def test_twelve_objects_quality_then_export(self):
        """No models: 12 non-overlapping synthetic subjects prove wiring and file outputs."""
        import hashlib
        from unittest.mock import patch
        rgb=np.ones((420,600,3),dtype=np.float32)
        masks=np.zeros((12,420,600),dtype=np.float32)
        yy,xx=np.ogrid[:420,:600]
        for i in range(12):
            cx,cy=(i%4)*150+75,(i//4)*140+70
            region=((xx-cx)**2+(yy-cy)**2)<32**2
            masks[i][region]=1
            rgb[region]=(.2+(i%4)*.18,.25+(i//4)*.1,.4)
        image=torch.from_numpy(rgb).unsqueeze(0)
        sources=torch.from_numpy(masks)
        report=node.SmartSVGQualityV217().run(image,sources,35)
        self.assertIs(report['result'][0],sources)
        self.assertEqual(json.loads(report['result'][2])['nombre_objets'],12)
        engine=importlib.import_module('sv217test.node_v2151')
        with tempfile.TemporaryDirectory() as td:
            with patch.object(engine,'_comfy_output_directory',return_value=None):
                export=engine.SmartSVGExpressV2151().run(image=image,
                    masques_objets=report['result'][0],dossier_sortie=td,
                    projet='Planche - 12 images (4x3)',largeur_mm=35)
            exported=json.loads(export['result'][2]);objects=exported['objets']
            self.assertEqual(len(objects),12)
            for obj in objects:
                self.assertTrue(Path(obj['fichier_svg_contour']).stat().st_size>100)
                self.assertTrue(Path(obj['fichier_png_cricut']).stat().st_size>100)

if __name__=='__main__':unittest.main()
