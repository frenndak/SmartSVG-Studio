"""End-to-end V21.6 CPU mask replay, strict persistence and legacy safety."""
import importlib, json, os, tempfile, time, types, sys, unittest, hashlib
from pathlib import Path
from unittest.mock import patch
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[1]
if 'sv216test' not in sys.modules:
    mod=types.ModuleType('sv216test');mod.__path__=[str(ROOT)];sys.modules[mod.__name__]=mod
node=importlib.import_module('sv216test.node_v216')
strokes=importlib.import_module('sv216test.smartsvg_editor.strokes')
previews=importlib.import_module('sv216test.smartsvg_editor.previews')

def image(w=64,h=48,color=.6):
    return torch.full((1,h,w,3),float(color),dtype=torch.float32)
def document(img,count,marks,base=None):
    a=img[0].numpy()
    if base is None:base=torch.zeros((count,img.shape[1],img.shape[2]),dtype=torch.float32)
    return json.dumps({'version':1,'width':int(img.shape[2]),'height':int(img.shape[1]),
         'count':count,'source':strokes.edit_fingerprint(a,base),'strokes':marks})
def stroke(obj=0,mode='add',x=.5,y=.5,r=.12):
    return {'object':obj,'mode':mode,'radius':r,'points':[[x,y]]}

class V216(unittest.TestCase):
    def test_registration_legacy_preserved(self):
        self.assertIn('SmartSVGMaskEditorV216',node.NODE_CLASS_MAPPINGS)
        self.assertTrue(node.SmartSVGMaskEditorV216.OUTPUT_NODE)
        for name in ('SmartSVGExpressV214','SmartSVGExpressV215','SmartSVGExpressV2151', 'SmartSVGInstancesV2151'):
            self.assertIn(name,node.NODE_CLASS_MAPPINGS)
        self.assertEqual(node.NODE_CLASS_MAPPINGS['SmartSVGExpressV2151'].INPUT_TYPES(),
            importlib.import_module('sv216test.node_v2151').SmartSVGExpressV2151.INPUT_TYPES())
    def test_add_manual_without_mask(self):
        img=image()
        out=node.SmartSVGMaskEditorV216().run(img,document(img,1,[stroke()]))
        mask,original,report=out['result']
        self.assertEqual(tuple(mask.shape),(1,48,64))
        self.assertIs(original,img)
        self.assertEqual(mask[0,24,32].item(),1)
        self.assertEqual(mask[0,0,0].item(),0)
        self.assertEqual(json.loads(report)['traits_appliques'],1)
    def test_subtract_and_preserve_soft_edges(self):
        img=image();base=torch.full((1,48,64),.4)
        doc=document(img,1,[stroke(mode='add'),stroke(mode='erase',r=.03)],base)
        mask=node.SmartSVGMaskEditorV216().run(img,doc,base)['result'][0]
        self.assertEqual(mask[0,24,32].item(),0)
        self.assertEqual(mask[0,0,0].item(),base[0,0,0].item())
        self.assertEqual(mask[0,24,26].item(),1)
        self.assertTrue(torch.all(base == base[0,0,0]))
    def test_multi_mask_only_target_is_edited(self):
        img=image();base=torch.zeros((3,48,64))
        doc=document(img,3,[stroke(obj=2)])
        mask=node.SmartSVGMaskEditorV216().run(img,doc,base)['result'][0]
        self.assertEqual(mask[0].sum().item(),0);self.assertEqual(mask[1].sum().item(),0)
        self.assertGreater(mask[2].sum().item(),0)
    def test_replay_deterministic_and_original_immutable(self):
        img=image();base=torch.ones((2,48,64))
        doc=document(img,2,[stroke(1,'erase'),stroke(1,'add',.6,.3,.02)],base)
        instance=node.SmartSVGMaskEditorV216()
        a=instance.run(img,doc,base)['result'][0]
        b=instance.run(img,doc,base)['result'][0]
        self.assertTrue(torch.equal(a,b));self.assertEqual(base[1,24,32].item(),1)
    def test_changes_in_base_mask_fail_closed(self):
        img=image();base=torch.zeros((1,48,64));doc=document(img,1,[stroke()],base)
        changed=base.clone();changed[0,0,0]=1
        with self.assertRaisesRegex(strokes.StrokeError,'Image ou dimensions'):
            node.SmartSVGMaskEditorV216().run(img,doc,changed)

    def test_bad_edited_image_digest_fail_closed(self):
        img=image();doc=document(img,1,[stroke()]);changed=image(color=.7)
        with self.assertRaisesRegex(strokes.StrokeError,'Image ou dimensions'):
            node.SmartSVGMaskEditorV216().run(changed,doc)
    def test_bad_image_shapes_and_masks(self):
        img=image()
        with self.assertRaises(strokes.StrokeError):node.SmartSVGMaskEditorV216().run(img,masque_base=torch.zeros((2,5,5)))
        with self.assertRaises(strokes.StrokeError):node.SmartSVGMaskEditorV216().run(torch.zeros((2,48,64,3)))
        with self.assertRaises(strokes.StrokeError):node.SmartSVGMaskEditorV216().run(img,masque_base=torch.zeros((33,48,64)))
    def test_limits_invalid_nonfinite_and_malformed_points(self):
        img=image()
        for marks in [[stroke(x=-.1)],[stroke(r=.4)],[stroke(obj=True)],[stroke(mode='fill')],[stroke(x=float('nan'))],
                      [stroke()]*401,[{'object':0,'mode':'add','radius':.01,'points':[[.1,.1]]*1501}]]:
            with self.subTest(marks=len(marks)):
                with self.assertRaises(strokes.StrokeError):node.SmartSVGMaskEditorV216().run(img,document(img,1,marks))
        with self.assertRaises(strokes.StrokeError):node.SmartSVGMaskEditorV216().run(img,'{}')
    def test_duplicate_brush_json_fields_fail_closed_without_mask_mutation(self):
        # G2.3 rejects duplicate JSON keys. V21.6 replay must not silently
        # accept a last-wins stroke command (G3.3e-b2a prerequisite, #71).
        img=image()
        base=torch.full((1,48,64),.25,dtype=torch.float32)
        original=base.clone()
        valid=document(img,1,[stroke()],base)
        for old,new in (
            ('"version": 1', '"version": 2, "version": 1'),
            ('"mode": "add"', '"mode": "erase", "mode": "add"'),
            ('"object": 0', '"object": 99, "object": 0'),
            ('"radius": 0.12', '"radius": 0.01, "radius": 0.12'),
        ):
            self.assertIn(old,valid)
            with self.subTest(field=old):
                with self.assertRaises(strokes.StrokeError):
                    node.SmartSVGMaskEditorV216().run(
                        img,valid.replace(old,new,1),base)
                self.assertTrue(torch.equal(base,original))
        # Maliciously deep JSON must produce a bounded user-facing error,
        # not leak an uncaught RecursionError from the JSON decoder.
        with self.assertRaises(strokes.StrokeError):
            node.SmartSVGMaskEditorV216().run(img,'['*1200+']'*1200,base)
        self.assertTrue(torch.equal(base,original))
        # A valid canonical document still replays the intended brush.
        result=node.SmartSVGMaskEditorV216().run(img,valid,base)['result'][0]
        self.assertEqual(result[0,24,32].item(),1)
        self.assertTrue(torch.equal(base,original))

    def test_empty_document_keeps_base_identically(self):
        img=image();base=torch.rand((2,48,64))
        result=node.SmartSVGMaskEditorV216().run(img,'',base)['result'][0]
        self.assertTrue(torch.equal(base,result))
    def test_preview_is_optional_failure_protected(self):
        img=image()
        with patch.object(node,'publish',side_effect=Exception('preview failure')):
            out=node.SmartSVGMaskEditorV216().run(img,document(img,1,[stroke()]))
        self.assertGreater(out['result'][0].sum().item(),0)
        self.assertEqual(out['ui']['smartsvg_editor'],[])
    def test_preview_png_ref_and_cap_and_protection(self):
        img=image();rgb=img[0].numpy();base=np.zeros((1,48,64),dtype=np.float32)
        with tempfile.TemporaryDirectory() as td:
            folder=Path(td)/previews.FOLDER;folder.mkdir()
            for i in range(115):
                filename=f'ed_{i:024x}_image.png'; f=folder/filename;f.write_bytes(b'old')
                os.utime(f,(100000+i,100000+i))
            foreign=folder/'protect_manual.png';foreign.write_bytes(b'no')
            result=previews.publish(rgb,base,td)
            self.assertEqual(len(result['masks']),1)
            self.assertTrue((folder/result['image']['filename']).exists())
            self.assertLessEqual(len(list(folder.glob('ed_*.png'))),previews.MAX_OWNED)
            self.assertEqual(foreign.read_bytes(),b'no')
    def test_symlink_preview_folder_rejected(self):
        img=image();rgb=img[0].numpy()
        with tempfile.TemporaryDirectory() as td:
            outside=Path(td)/'outside';outside.mkdir()
            output=Path(td)/'out';output.mkdir();(output/previews.FOLDER).symlink_to(outside,target_is_directory=True)
            self.assertIsNone(previews.publish(rgb,np.zeros((1,48,64)),output))
    def test_one_run_full_export_consumes_corrected_mask(self):
        img=image();mask=node.SmartSVGMaskEditorV216().run(img,document(img,1,[stroke(r=.17)]))['result'][0]
        with tempfile.TemporaryDirectory() as td:
            express=importlib.import_module('sv216test.node_v2151').SmartSVGExpressV2151()
            with patch.object(importlib.import_module('sv216test.node_v2151'),'_comfy_output_directory',return_value=None):
                result=express.run(image=img,masques_objets=mask,dossier_sortie=td,
                                   projet='Sticker - contour du sujet',largeur_mm=35)
            report=json.loads(result['result'][2])
            self.assertTrue(Path(report['objets'][0]['fichier_svg_contour']).exists())
            self.assertTrue(Path(report['objets'][0]['fichier_png_cricut']).exists())
    def test_brush_changes_actual_cricut_png_and_svg(self):
        img=image(160,160)
        original=torch.zeros((1,160,160),dtype=torch.float32)
        original[:,30:130,30:130]=1
        edits=document(img,1,[stroke(mode='erase',x=.76,y=.5,r=.13)],original)
        modified=node.SmartSVGMaskEditorV216().run(img,edits,original)['result'][0]
        self.assertFalse(torch.equal(original,modified))
        engine=importlib.import_module('sv216test.node_v2151')
        with tempfile.TemporaryDirectory() as td:
            def files(mask,sub):
                with patch.object(engine,'_comfy_output_directory',return_value=None):
                    out=engine.SmartSVGExpressV2151().run(img,dossier_sortie=str(Path(td)/sub),
                            projet='Sticker - contour du sujet',largeur_mm=40,masques_objets=mask)
                obj=json.loads(out['result'][2])['objets'][0]
                return [hashlib.sha256(Path(obj[k]).read_bytes()).hexdigest()
                        for k in ('fichier_png_cricut','fichier_svg_contour')]
            before=files(original,'before');after=files(modified,'after')
            self.assertNotEqual(before[0],after[0])
            self.assertNotEqual(before[1],after[1])

    def test_24_subjects_two_sheets_png_svg_byte_parity(self):
        # Synthetic 6x4 regression independent of private/unshipped Pokémon art.
        h,w=560,840
        rgb=np.full((h,w,3),.98,dtype=np.float32)
        masks=np.zeros((24,h,w),dtype=np.float32)
        ygrid,xgrid=np.ogrid[:h,:w]
        for i in range(24):
            cx,cy=(i%6)*140+70,(i//6)*140+70
            inside=(xgrid-cx)**2+(ygrid-cy)**2 <= 37**2
            masks[i][inside]=1
            rgb[inside]=[.15+(i%6)*.09,.5,.9-(i//6)*.15]
        source=torch.from_numpy(rgb)[None]
        base=torch.from_numpy(masks)
        unchanged=node.SmartSVGMaskEditorV216().run(source,'',base)['result'][0]
        engine=importlib.import_module('sv216test.node_v2151')
        with tempfile.TemporaryDirectory() as td:
            def produce(mask,folder):
                with patch.object(engine,'_comfy_output_directory',return_value=None):
                    response=engine.SmartSVGExpressV2151().run(image=source,masques_objets=mask,
                        dossier_sortie=str(Path(td)/folder),projet='Planche - 24 images (6x4)',largeur_mm=32)
                report=json.loads(response['result'][2]);root=Path(report['dossier'])
                files={str(x.relative_to(root)):hashlib.sha256(x.read_bytes()).hexdigest()
                       for x in root.rglob('*') if x.is_file() and x.suffix.lower() in ('.png','.svg')}
                return report,files
            original,files_before=produce(base,'avant')
            corrected,files_after=produce(unchanged,'apres')
            self.assertEqual(original['nombre_objets_exportes'],24)
            self.assertEqual(corrected['nombre_objets_exportes'],24)
            self.assertEqual(len(corrected['planches']),2)
            self.assertEqual(len(files_after),101)
            self.assertEqual(files_before,files_after)

    def test_new_workflow_links_and_ports(self):
        for p in (ROOT/'example_workflows').glob('SmartSVG_Studio_V21_6_*.json'):
            d=json.loads(p.read_text(encoding='utf-8'))
            nodes={n['id']:n for n in d['nodes']}
            self.assertEqual(len(nodes),len(d['nodes']))
            for n in nodes.values():
                if n['type'] not in node.NODE_CLASS_MAPPINGS:continue
                cls=node.NODE_CLASS_MAPPINGS[n['type']]; ports=list(cls.INPUT_TYPES()['required'])+list(cls.INPUT_TYPES().get('optional',{}))
                self.assertEqual(ports,[x['name'] for x in n['inputs']])
                self.assertEqual(list(cls.RETURN_TYPES),[x['type'] for x in n['outputs']])
            for link_id,source,out,target,port,t in d['links']:
                self.assertEqual(nodes[source]['outputs'][out]['type'],t)
                self.assertEqual(nodes[target]['inputs'][port]['type'],t)
                self.assertEqual(nodes[target]['inputs'][port]['link'],link_id)

if __name__=='__main__':unittest.main()
