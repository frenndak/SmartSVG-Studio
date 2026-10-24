"""Unit/integration contract tests for a unified native inspector and editor."""
import importlib, json, sys, tempfile, types, unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
import torch
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
if 'sv2110test' not in sys.modules:
    pkg=types.ModuleType('sv2110test');pkg.__path__=[str(ROOT)];sys.modules[pkg.__name__]=pkg
node=importlib.import_module('sv2110test.node_v2110')
strokes=importlib.import_module('sv2110test.smartsvg_editor.strokes')

def fixture(w=100,h=80,n=2):
    src=torch.zeros((1,h,w,3),dtype=torch.float32)
    src[...,0]=.75;src[...,1]=.36
    masks=torch.zeros((n,h,w),dtype=torch.float32)
    masks[0,15:54,20:56]=1
    if n>1:masks[1,22:60,64:92]=1
    return src,masks

class Unified(unittest.TestCase):
    def test_registry_preserves_legacy_and_express(self):
        names=node.NODE_CLASS_MAPPINGS
        for k in ('SmartSVGMaskEditorV216','SmartSVGNativeInspectorV219','SmartSVGExpressV218','SmartSVGUnifiedEditorV2110'):
            self.assertIn(k,names)
        self.assertEqual(names['SmartSVGExpressV218'].INPUT_TYPES(),names['SmartSVGExpressV2151'].INPUT_TYPES())
        self.assertEqual(node.SmartSVGUnifiedEditorV2110.RETURN_TYPES,('MASK','IMAGE','STRING'))

    def test_saved_retouches_have_real_effect_and_source_unchanged(self):
        img,masks=fixture()
        fp=strokes.edit_fingerprint(img[0].numpy(),masks.numpy())
        doc=json.dumps(dict(version=1,width=100,height=80,count=2,source=fp,
            strokes=[dict(object=0,mode='add',radius=.07,points=[[.85,.1]]),
                     dict(object=0,mode='erase',radius=.04,points=[[.3,.3]])]))
        with patch.object(node,'_output_directory',return_value=None):
            out=node.SmartSVGUnifiedEditorV2110().run(img,doc,masks)
        edited=out['result'][0]
        self.assertIs(out['result'][1],img)
        self.assertEqual(edited.shape,masks.shape)
        self.assertFalse(torch.equal(edited[0],masks[0]))
        self.assertTrue(torch.equal(edited[1],masks[1]))
        self.assertEqual(int(edited[0,8,85]),1)
        self.assertEqual(int(edited[0,24,30]),0)
        self.assertTrue(torch.equal(masks[0,15:54,20:56],torch.ones((39,36))))
        info=json.loads(out['result'][2]);self.assertEqual(info['traits_appliques'],2)

    def test_published_base_never_doubles_saved_strokes(self):
        img,masks=fixture();fp=strokes.edit_fingerprint(img[0].numpy(),masks.numpy())
        doc=json.dumps(dict(version=1,width=100,height=80,count=2,source=fp,
            strokes=[dict(object=0,mode='add',radius=.05,points=[[.92,.08]])]))
        with tempfile.TemporaryDirectory() as td,patch.object(node,'_output_directory',return_value=td):
            output=node.SmartSVGUnifiedEditorV2110().run(img,doc,masks)
            meta=output['ui']['smartsvg_unified'][0]
            filename=Path(td)/'SmartSVG_Studio_Native_V219'/meta['masks'][0]['filename']
            with Image.open(filename) as original:
                self.assertEqual(original.getpixel((92,6)),0)
            self.assertEqual(float(output['result'][0][0,6,92]),1)
            self.assertEqual((meta['width'],meta['height'],meta['count']),(100,80,2))
            self.assertEqual(meta['source'],fp)
            self.assertEqual(meta['image']['type'],'output')
            self.assertEqual(len(meta['objects']),2)

    def test_repeated_runs_match_exact_and_forbid_old_segmentation(self):
        img,masks=fixture();fp=strokes.edit_fingerprint(img[0].numpy(),masks.numpy())
        doc=json.dumps(dict(version=1,width=100,height=80,count=2,source=fp,
            strokes=[dict(object=1,mode='add',radius=.035,points=[[.5,.8]])]))
        with patch.object(node,'_output_directory',return_value=None):
            first=node.SmartSVGUnifiedEditorV2110().run(img,doc,masks)
            second=node.SmartSVGUnifiedEditorV2110().run(img,doc,masks)
        self.assertTrue(torch.equal(first['result'][0],second['result'][0]))
        alternate=masks.clone();alternate[0,5,5]=1
        with self.assertRaises(strokes.StrokeError):node.SmartSVGUnifiedEditorV2110().run(img,doc,alternate)

    def test_empty_mask_first_run_then_manual_draw(self):
        img,_=fixture();engine=node.SmartSVGUnifiedEditorV2110()
        with patch.object(node,'_output_directory',return_value=None):
            empty=engine.run(img,'')
        self.assertEqual(empty['result'][0].shape,(1,80,100))
        self.assertTrue(json.loads(empty['result'][2])['masque_vide'])
        fp=strokes.edit_fingerprint(img[0].numpy(),np.zeros((1,80,100),dtype=np.float32))
        document=json.dumps(dict(version=1,width=100,height=80,count=1,source=fp,
             strokes=[dict(object=0,mode='add',radius=.05,points=[[.5,.5]])]))
        with patch.object(node,'_output_directory',return_value=None):
            edited=engine.run(img,document)
        self.assertFalse(json.loads(edited['result'][2])['masque_vide'])

    def test_ui_failure_only_ui_and_real_edits_remain(self):
        img,masks=fixture()
        for fail in ('analyse','publish_native'):
            with patch.object(node,fail,side_effect=RuntimeError('mocked disk / QA error')):
                with patch.object(node,'_output_directory',return_value=None):
                    result=node.SmartSVGUnifiedEditorV2110().run(img,'',masks)
            self.assertTrue(torch.equal(result['result'][0],masks))
            self.assertTrue(result['ui']['text'])
            if fail=='analyse':self.assertEqual(json.loads(result['result'][2])['inspection'],'indisponible')

    def test_original_express_print_cut_files_exactly_preserved(self):
        """Same base masks through unified empty edit must yield byte-identical PNG/SVG."""
        import hashlib
        img,masks=fixture(180,130)
        with patch.object(node,'_output_directory',return_value=None):
            edited=node.SmartSVGUnifiedEditorV2110().run(img,'',masks)
        self.assertTrue(torch.equal(edited['result'][0],masks))
        old=importlib.import_module('sv2110test.node_v218')
        v2151=importlib.import_module('sv2110test.node_v2151')
        with tempfile.TemporaryDirectory() as td:
            output=[]
            for label,actual in [('legacy',masks),('unified',edited['result'][0])]:
                folder=Path(td)/label
                with patch.object(v2151,'_comfy_output_directory',return_value=None):
                    old.SmartSVGExpressV218().run(image=img,masques_objets=actual,
                        dossier_sortie=str(folder),projet='Sticker - contour du sujet',largeur_mm=35)
                files=sorted(p for p in folder.rglob('*') if p.is_file() and p.suffix.lower() in ('.svg','.png'))
                self.assertTrue(files)
                output.append({"/".join(p.relative_to(folder).parts[1:]):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
            self.assertEqual(output[0],output[1])

    def test_native_overlap_maximum_32_subjects_has_exact_counts(self):
        native = importlib.import_module('sv2110test.smartsvg_native.inspector')
        img = np.zeros((32,32,3),dtype=np.float32)
        masks = np.zeros((32,32,32),dtype=np.float32)
        masks[:,6:23,8:25] = 1.0
        report = native.analyse(img,masks,width_mm=40.)
        self.assertEqual(report['nombre_objets'],32)
        self.assertEqual(len(report['objets']),32)
        self.assertTrue(all(any(p['type']=='MASQUES_CHEVAUCHANTS' for p in o['points']) for o in report['objets']))
        counts = np.sum(masks>=.5,axis=0,dtype=np.uint8)
        self.assertEqual(counts.dtype,np.uint8)
        self.assertEqual(int(counts[15,15]),32)

    def test_bad_masks_and_nan_are_rejected(self):
        img,masks=fixture()
        for invalid in [torch.ones((1,10,10)),torch.ones((33,80,100)),torch.ones((80,100))]:
            with self.assertRaises(strokes.StrokeError):node.SmartSVGUnifiedEditorV2110().run(img,'',invalid)
        bad=masks.clone();bad[0,0,0]=float('nan')
        with self.assertRaises(strokes.StrokeError):node.SmartSVGUnifiedEditorV2110().run(img,'',bad)

    def test_new_workflows_valid_and_outputs_to_express(self):
        for path in sorted((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_10_*.json')):
            workflow=json.loads(path.read_text(encoding='utf8'))
            ids={n['id']:n for n in workflow['nodes']}
            unified=next(n for n in ids.values() if n['type']=='SmartSVGUnifiedEditorV2110')
            express=next(n for n in ids.values() if n['type']=='SmartSVGExpressV218')
            self.assertTrue(any(l[1]==unified['id'] and l[3]==express['id'] and l[5]=='MASK' for l in workflow['links']))
            self.assertTrue(any(l[1]==unified['id'] and l[3]==express['id'] and l[5]=='IMAGE' for l in workflow['links']))
            self.assertFalse(any(n['type']=='SmartSVGNativeInspectorV219' for n in ids.values()))
            self.assertTrue(all(any(l[0]==input_['link'] for l in workflow['links'])
                for n in ids.values() for input_ in n.get('inputs',[]) if input_.get('link') is not None))
        self.assertEqual(len(list((ROOT/'example_workflows').glob('SmartSVG_Studio_V21_10_*.json'))),3)

if __name__=='__main__':unittest.main()
