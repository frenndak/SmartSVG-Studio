"""Cricut/photo V19.1 regression checks; no GPU or model needed."""
import sys,types,importlib,tempfile,unittest,hashlib,json
from pathlib import Path
import numpy as np, cv2
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
PKG='smartsvg191_pkg'
if PKG not in sys.modules:
    p=types.ModuleType(PKG);p.__path__=[str(ROOT)];sys.modules[PKG]=p
photo=importlib.import_module(PKG+'.photo_v19')
geom=importlib.import_module(PKG+'.photo_geometry_v191')
node=importlib.import_module(PKG+'.node_v19')

def scene(w=140,h=115):
    yy,xx=np.mgrid[:h,:w]
    rgb=np.zeros((h,w,3),np.uint8)
    rgb[:,:,0]=(xx*3)%255;rgb[:,:,1]=(yy*2)%255;rgb[:,:,2]=100
    return rgb

class TestV191(unittest.TestCase):
    def test_object_touches_photo_border_margin_not_clipped(self):
        im=scene()
        a=np.zeros(im.shape[:2],np.float32)
        a[:61,:42]=1.
        raw,white,bounds,meta=geom.cutout_with_white_border(im,a,mm_per_px=.1,white_offset_mm=1.5)
        self.assertEqual(bounds,(0,0,42,61))
        self.assertEqual(raw.shape[:2],(61,42))
        self.assertEqual(white.shape[:2],(97,78))
        self.assertEqual(white[meta['padding_px'],meta['padding_px'],3],255)
        self.assertEqual(white[0,0,3],0)
        self.assertEqual(meta['rayon_marge_px'],15)

    def test_soft_haar_edge_survives_crop(self):
        im=scene()
        a=np.zeros(im.shape[:2],np.float32)
        a[35:65,35:65]=1
        a[34,36:64]=.04
        raw,white,bounds,meta=geom.cutout_with_white_border(im,a,mm_per_px=.2,white_offset_mm=.6)
        self.assertEqual(bounds[1],34)
        self.assertEqual(raw[0,1,3],10)
        self.assertTrue(np.all(raw[0,1,:3] == im[34,36]))

    def test_holes_are_white_filled_no_inner_cut(self):
        im=scene()
        a=np.zeros(im.shape[:2],np.float32)
        cv2.circle(a,(55,55),32,1,-1)
        cv2.circle(a,(55,55),13,0,-1)
        raw,white,bounds,meta=geom.cutout_with_white_border(im,a,mm_per_px=.2,white_offset_mm=1)
        # Center hole must be OPAQUE white in print-ready layer to avoid inner cuts.
        yc=55-bounds[1]+meta['padding_px'];xc=55-bounds[0]+meta['padding_px']
        self.assertTrue(np.array_equal(white[yc,xc],[255,255,255,255]))
        self.assertEqual(raw[55-bounds[1],55-bounds[0],3],0)

    def test_border_composites_faded_edges_onto_white(self):
        im=np.zeros((60,60,3),np.uint8)
        im[:,:,0]=200
        mask=np.zeros((60,60),np.float32)
        mask[20:40,20:40]=1.
        mask[19,22:38]=.25
        raw,white,bounds,geo=geom.cutout_with_white_border(im,mask,mm_per_px=.2,white_offset_mm=.6)
        self.assertTrue(set(np.unique(white[...,3])).issubset({0,255}))
        self.assertTrue(np.any(np.all(white[:,:,:3]==[255,255,255],axis=2) & (white[...,3]==255)))

    def test_mask_budget_rejects_oversized_batch(self):
        # Approximately 34m uint8 -> rejected before large float32 conversion
        masks=np.zeros((16,1450,1500),np.uint8)
        with self.assertRaisesRegex(photo.PhotoExtractionError,'32 millions'):
            photo._masks_arr(masks,(1450,1500))

    def test_full_export_border_physical_dimension_and_sha(self):
        im=scene();a=np.zeros(im.shape[:2],np.float32);a[:65,:40]=1
        with tempfile.TemporaryDirectory() as td:
            result,_=photo.process_photo(im,td,masks=a,mode='masques_requis',width_mm=70,white_offset_mm=2.0)
            folder=Path(result['output']);d=result['audit_v19']
            self.assertEqual(d['nombre_objets_extraits'],1)
            o=d['objets'][0]
            self.assertEqual(o['geometrie_cricut']['rayon_marge_px'],4)
            with Image.open(folder/o['fichier_cricut_test']) as out:
                self.assertEqual(out.mode,'RGBA')
                self.assertEqual(out.size[0],54)
                self.assertTrue(out.getpixel((6,6))[3]>0)
                self.assertAlmostEqual(25.4*out.width/out.info['dpi'][0],out.width*.5,delta=.05)
            manifest=json.loads((folder/'PRET_V19.json').read_text())
            for name,m in manifest['fichiers'].items():
                self.assertEqual(hashlib.sha256((folder/name).read_bytes()).hexdigest(),m['sha256'])

    def test_multi_island_warning(self):
        im=scene();a=np.zeros(im.shape[:2],np.float32)
        cv2.circle(a,(40,50),12,1,-1);cv2.circle(a,(100,50),12,1,-1)
        with tempfile.TemporaryDirectory() as td:
            r,_=photo.process_photo(im,td,masks=a,mode='masques_requis')
            self.assertEqual(r['audit_v19']['objets'][0]['composantes_separees_pour_decoupe'],2)
            self.assertTrue(any('ilots distincts' in s for s in r['audit_v19']['avertissements']))

    def test_routing_mid_size_photo_and_sticker_sheet(self):
        image=np.zeros((600,650,3),np.uint8)
        image[:]=[80,40,90]
        self.assertEqual(node._detect_scene(image),'photo')
        image[:]=255
        self.assertEqual(node._detect_scene(image),'stickers')
        self.assertIn('SmartSVGStudioV191Express',node.NODE_CLASS_MAPPINGS)

    def test_real_reference_photos_remain_diagnostic_without_ai(self):
        # Masks from Florence/SAM are NOT available in this Linux CPU test.
        # Verify honest diagnostic instead of claiming automatic separation.
        for name in ('1000077453.png','1000077462.png'):
            src=Path('/mnt/data')/name
            if not src.exists():continue
            original=np.asarray(Image.open(src).convert('RGB'))
            self.assertEqual(node._detect_scene(original),'photo')
            with tempfile.TemporaryDirectory() as td:
                r,_=photo.process_photo(original,td,mode='analyse_seule')
                self.assertEqual(r['audit_v19']['nombre_objets_extraits'],0)
                self.assertEqual(r['audit_v19']['statut'],'A_VERIFIER_MASQUES_INSUFFISANTS')

    def test_no_false_semantic_success_without_mask(self):
        with tempfile.TemporaryDirectory() as td:
            r,_=photo.process_photo(scene(),td,mode='auto')
            self.assertEqual(r['audit_v19']['nombre_objets_extraits'],0)
            self.assertFalse(r['audit_v19']['masques_externes_fournis_non_verifies_comme_ia'])

if __name__=='__main__':unittest.main()
