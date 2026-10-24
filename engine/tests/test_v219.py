"""V21.9: native resolution, immutable manufacturing data and bounded UI copies."""
import importlib,json,os,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import torch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
if 'sv219test' not in sys.modules:
    pkg=types.ModuleType('sv219test');pkg.__path__=[str(ROOT)];sys.modules[pkg.__name__]=pkg
node=importlib.import_module('sv219test.node_v219')
inspector=importlib.import_module('sv219test.smartsvg_native.inspector')

def source(w=220,h=160):
    yy,xx=np.mgrid[:h,:w]
    rgb=np.stack([xx/(w+1),yy/(h+1),np.full((h,w),.5)],axis=-1).astype('float32')
    mask=np.zeros((2,h,w),dtype='float32');mask[0,20:115,35:125]=1;mask[1,45:145,135:205]=1
    return torch.from_numpy(rgb)[None],torch.from_numpy(mask)

class NativeInspection(unittest.TestCase):
    def test_registry_and_unmodified_express_contract(self):
        self.assertIn('SmartSVGNativeInspectorV219',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGExpressV218',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGMaskEditorV216',node.NODE_CLASS_MAPPINGS)
        self.assertEqual(node.NODE_CLASS_MAPPINGS['SmartSVGExpressV218'].INPUT_TYPES(),
                         node.NODE_CLASS_MAPPINGS['SmartSVGExpressV2151'].INPUT_TYPES())
    def test_identity_of_raster_and_masks_exact_even_soft_edges(self):
        rgb,masks=source();masks[0,30:50,40:60]=.37
        with patch.object(node,'_output_directory',return_value=None):
            out=node.SmartSVGNativeInspectorV219().run(rgb,masks,40)
        self.assertIs(out['result'][0],masks)
        self.assertIs(out['result'][1],rgb)
        self.assertEqual(json.loads(out['result'][2])['nombre_objets'],2)
        self.assertEqual(out['ui']['smartsvg_native'],[])
    def test_full_native_png_no_resize_and_correct_8bit_alpha(self):
        rgb,masks=source(301,199)
        with tempfile.TemporaryDirectory() as td:
            result=inspector.publish_native(rgb[0].numpy(),masks.numpy(),td)
            self.assertEqual((result['largeur_px'],result['hauteur_px']),(301,199))
            names=[result['image'],*result['masks']]
            self.assertEqual(len(names),3)
            for ref in names:
                f=Path(td)/inspector.FOLDER/ref['filename']
                with Image.open(f) as png:
                    self.assertEqual(png.size,(301,199))
                    if 'mask' in f.name:self.assertEqual(png.mode,'L')
            with Image.open(Path(td)/inspector.FOLDER/result['masks'][0]['filename']) as png:
                self.assertEqual(png.getpixel((40,35)),255)
                self.assertEqual(png.getpixel((0,0)),0)
    def test_hole_its_native_coordinate_hint(self):
        rgb,masks=source();masks[0,57:63,75:81]=0
        with patch.object(node,'_output_directory',return_value=None):
            result=json.loads(node.SmartSVGNativeInspectorV219().run(rgb,masks,40)['result'][2])
        hints=result['objets'][0]['points']
        self.assertTrue(any(s['type']=='TROU_INTERIEUR' and 70<=s['x']<=85 and 53<=s['y']<=67 for s in hints))
    def test_detached_micro_island_coordinates(self):
        rgb,masks=source();masks[0,4:6,10:12]=1
        report=inspector.analyse(rgb[0].numpy(),masks.numpy())
        self.assertTrue(any(s['type']=='ILOT_DETACHE' and 8<=s['x']<=14 for s in report['objets'][0]['points']))
    def test_overlap_hint_coordinates(self):
        rgb,masks=source();masks[1,65:85,65:85]=1
        report=inspector.analyse(rgb[0].numpy(),masks.numpy())
        self.assertTrue(any(s['type']=='MASQUES_CHEVAUCHANTS' for s in report['objets'][0]['points']))
    def test_empty_masks_report_blocking_but_no_crash(self):
        rgb,_=source();mask=torch.zeros((1,160,220))
        with patch.object(node,'_output_directory',return_value=None):
            report=json.loads(node.SmartSVGNativeInspectorV219().run(rgb,mask)['result'][2])
        self.assertEqual(report['statut'],'bloquant')
        self.assertEqual(report['objets'][0]['points'][0]['type'],'MASQUE_VIDE')
    def test_mismatch_nan_overlimit_and_bad_width_fail_closed(self):
        rgb,masks=source()
        for bad in (torch.zeros(1,30,30),torch.ones(33,160,220)):
            with self.assertRaises(inspector.NativeInspectionError):node.SmartSVGNativeInspectorV219().run(rgb,bad)
        for width in (float('nan'),0,301):
            with self.assertRaises(inspector.NativeInspectionError):node.SmartSVGNativeInspectorV219().run(rgb,masks,width)
        broken=masks.clone();broken[0,0,0]=float('nan')
        with self.assertRaises(inspector.NativeInspectionError):node.SmartSVGNativeInspectorV219().run(rgb,broken)
        with self.assertRaises(inspector.NativeInspectionError):node.SmartSVGNativeInspectorV219().run(torch.zeros((2,10,10,3)),torch.zeros((1,10,10)))
    def test_preview_failure_is_optional_and_originals_survive(self):
        rgb,masks=source()
        with patch.object(node,'publish_native',side_effect=RuntimeError('disk full')):
            result=node.SmartSVGNativeInspectorV219().run(rgb,masks)
        self.assertIs(result['result'][0],masks)
        self.assertIn('indisponible',result['ui']['text'][-1])
    def test_lifecycle_caps_protect_foreign_and_symlinks(self):
        rgb,masks=source()
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)/inspector.FOLDER;folder.mkdir()
            protected=folder/'ma_photo.png';protected.write_bytes(b'private')
            for i in range(12):
                fname=f'ni_{i:024x}_image.png';p=folder/fname;p.write_bytes(b'obsolete')
                os.utime(p,(10000+i,10000+i))
            result=inspector.publish_native(rgb[0].numpy(),masks.numpy(),td)
            self.assertIsNotNone(result)
            self.assertEqual(protected.read_bytes(),b'private')
            self.assertLessEqual(len([p for p in folder.iterdir() if inspector.PATTERN.fullmatch(p.name)]),32*8+8)
        with tempfile.TemporaryDirectory() as td:
            output=Path(td)/'out';output.mkdir();other=Path(td)/'elsewhere';other.mkdir()
            (output/inspector.FOLDER).symlink_to(other,target_is_directory=True)
            self.assertIsNone(inspector.publish_native(rgb[0].numpy(),masks.numpy(),output))
    def test_too_large_ui_preview_fallback_without_mutation(self):
        rgb,masks=source()
        with tempfile.TemporaryDirectory() as td:
            with patch.object(inspector,'MAX_SESSION_BYTES',5):
                self.assertIsNone(inspector.publish_native(rgb[0].numpy(),masks.numpy(),td))
            folder=Path(td)/inspector.FOLDER
            self.assertFalse(list(folder.glob('ni_*.png')))
    def test_workflows_have_inspector_before_cricut_and_old_node_preserved(self):
        for wf in sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_9_*.json')):
            obj=json.loads(wf.read_text('utf-8'))
            nodes={n['id']:n for n in obj['nodes']}
            inspect_node=next(n for n in nodes.values() if n['type']=='SmartSVGNativeInspectorV219')
            express=next(n for n in nodes.values() if n['type']=='SmartSVGExpressV218')
            editor=next(n for n in nodes.values() if n['type']=='SmartSVGMaskEditorV216')
            self.assertIsNotNone(editor)
            self.assertTrue(any(l[1]==inspect_node['id'] and l[3]==express['id'] and l[5]=='MASK' for l in obj['links']))
            self.assertTrue(any(l[1]==inspect_node['id'] and l[3]==express['id'] and l[5]=='IMAGE' for l in obj['links']))
    def test_live_user_images_no_segmentation_claim(self):
        from PIL import Image
        for file in ('1000077568.jpg','1000077534.jpg','1000077546.png','1000077554.png',
                     '1000077435.png','1000076838.jpg','1000076753.webp'):
            path=Path('/mnt/data')/file
            if not path.exists():continue
            with self.subTest(file=file):
                with Image.open(path) as im:
                    width,height=im.size
                    # Data checked at true original dimensions, but synthetic rectangular mask.
                    # This is NOT a demonstration of correct subject segmentation.
                    fake=np.zeros((1,height,width),dtype=np.float32)
                    fake[0,height//4:3*height//4,width//4:3*width//4]=1
                    # Avoid excessive time in test; QA own mask geometry uses native dimensions.
                    report=inspector.analyse(np.zeros((height,width,3),np.float32),fake)
                    self.assertEqual(report['resolution'],{'largeur_px':width,'hauteur_px':height})
    def test_end_to_end_12_masks_then_cricut_file_exports(self):
        # No IA / no printer: merely checks that added node preserves manufacturing data.
        rgb=torch.ones((1,160,240,3));masks=torch.zeros((12,160,240))
        for i in range(12):
            x=(i%4)*60+8;y=(i//4)*50+6
            masks[i,y:y+23,x:x+24]=1
        with patch.object(node,'_output_directory',return_value=None):
            result=node.SmartSVGNativeInspectorV219().run(rgb,masks,35)
        self.assertIs(result['result'][0],masks)
        with tempfile.TemporaryDirectory() as td:
            old=importlib.import_module('sv219test.node_v218')
            base=old.SmartSVGExpressV218()
            with patch.object(importlib.import_module('sv219test.node_v2151'),'_comfy_output_directory',return_value=None):
                out=base.run(image=rgb,masques_objets=result['result'][0],dossier_sortie=td,
                             projet='Planche - 12 images (4x3)',largeur_mm=35)
            details=json.loads(out['result'][2]);self.assertGreaterEqual(len(details['objets']),12)
            self.assertTrue(Path(details['objets'][0]['fichier_png_cricut']).is_file())

if __name__=='__main__':unittest.main()
