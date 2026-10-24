"""V21.15.2: conservative sheet segmentation, security, gate & integration."""
import importlib,sys,types,unittest,tempfile,os,json
from pathlib import Path
import numpy as np,cv2
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
if 'sv21152test' not in sys.modules:
    p=types.ModuleType('sv21152test');p.__path__=[str(ROOT)];sys.modules[p.__name__]=p
sheet=importlib.import_module('sv21152test.smartsvg_quality.white_sheet_v21152')
release=importlib.import_module('sv21152test.smartsvg_quality.release_gate_v21152')
node=importlib.import_module('sv21152test.node_v21152')

class TestWhiteSheet(unittest.TestCase):
    def sheet(self):
        a=np.full((360,480,3),255,np.uint8)
        for r in range(3):
            for c in range(4):
                x,y=c*120,r*120
                cv2.circle(a,(x+60,y+60),34,(65,120,190),-1)
                cv2.circle(a,(x+60,y+60),34,(0,0,0),2)
                # dashed dark rectangular 'vignette' surrounding a subject
                for yy in range(y+5,y+115,14):
                    cv2.line(a,(x+5,yy),(x+5,min(y+110,yy+7)),(45,45,45),1)
                for xx in range(x+8,x+115,14):
                    cv2.line(a,(xx,y+5),(min(x+110,xx+6),y+5),(45,45,45),1)
        return a
    def test_12_individuals_no_border(self):
        a=self.sheet();r=sheet.segment_white_grid(a)
        self.assertEqual(r.masks.shape,(12,360,480))
        for k,m in enumerate(r.masks):
            self.assertEqual(cv2.connectedComponents((m>0).astype('uint8'),8)[0]-1,1)
            self.assertLess(float(m.sum())/(120*120),.6)
            rr,cc=divmod(k,4)
            self.assertEqual(int(m[rr*120+60,cc*120+60]),1)
            self.assertEqual(int(m[rr*120+5,cc*120+5]),0)
    def test_black_sheet_refused(self):
        with self.assertRaises(sheet.SheetUncertain):sheet.segment_white_grid(np.zeros((360,480,3),np.uint8))
    def test_plain_white_empty_refused(self):
        with self.assertRaises(sheet.SheetUncertain):sheet.segment_white_grid(np.full((360,480,3),255,np.uint8))
    def test_rectangle_must_not_be_subject(self):
        a=np.full((360,480,3),255,np.uint8)
        for r in range(3):
            for c in range(4):
                cv2.rectangle(a,(c*120+20,r*120+20),(c*120+99,r*120+99),(0,100,150),-1)
        with self.assertRaises(sheet.SheetUncertain):sheet.segment_white_grid(a)
    def test_partial_sheet_abstains(self):
        a=self.sheet();a[:120,:120]=255
        with self.assertRaises(sheet.SheetUncertain):sheet.segment_white_grid(a)
    def test_grids_and_channels_rejected(self):
        with self.assertRaises(sheet.SheetUncertain):sheet.segment_white_grid(self.sheet(),cols=4,rows=4)
        with self.assertRaises(sheet.SheetUncertain):sheet.segment_white_grid(self.sheet().astype('float32'))
    def test_legacy_identity_and_ports(self):
        self.assertIn('SmartSVGExpressV2151',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGExpressV21152',node.NODE_CLASS_MAPPINGS)
        self.assertEqual(node.SmartSVGExpressV21152.INPUT_TYPES(),
                         node.SmartSVGExpressV2151.INPUT_TYPES())
        self.assertEqual(node.SmartSVGExpressV21152.RETURN_TYPES,
                         node.SmartSVGExpressV2151.RETURN_TYPES)
    def test_real_png_svg_and_qa_are_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            report,_=release.run_v21152(self.sheet(),tmp,profile='planche_multi',width_mm=16,
                                             grid='4x3',segmentation='desactiver')
            self.assertEqual(report['white_sheet_v21152']['mode'],'AUTO_MASQUES_HEURISTIQUES')
            self.assertEqual(report['nombre_objets_exportes'],12)
            self.assertEqual(report['controle_v21152']['status'],'REVIEW_REQUIRED')
            self.assertTrue(Path(report['dossier'],'CONTROLE_V21_15_2.json').is_file())
            self.assertTrue(Path(report['dossier'],'RAPPORT_V21_15_2.json').is_file())
            self.assertEqual(len(report['controle_v21152']['blocking_codes']),0)
            qa=json.loads(Path(report['dossier'],'CONTROLE_V21_15_2.json').read_text())
            self.assertEqual(len(qa['objects']),12)
            self.assertTrue(all(not x['geometry']['near_rectangle'] for x in qa['objects']))
    def test_fallback_blocks_false_cut(self):
        with tempfile.TemporaryDirectory() as tmp:
            sample=np.full((105,115,3),170,np.uint8)
            report,_=release.run_v21152(sample,tmp,profile='auto',width_mm=18)
            self.assertEqual(report['white_sheet_v21152']['mode'],'NON_APPLICABLE')
            self.assertEqual(report['controle_v21152']['status'],'BLOCKED')

if __name__=='__main__':unittest.main()
