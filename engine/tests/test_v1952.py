"""V19.5.2 adversarial audit: pixel encoding, boundaries, path confinement, load budgets."""
import importlib, sys, types, unittest, tempfile
from pathlib import Path
from unittest.mock import patch
import numpy as np
import cv2
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
NAME='smartsvg_v1952_test'
if NAME not in sys.modules:
    pkg=types.ModuleType(NAME);pkg.__path__=[str(ROOT)];sys.modules[NAME]=pkg
contact=importlib.import_module(NAME+'.photo_contacts_v195')
geometry=importlib.import_module(NAME+'.photo_geometry_v191')


def overlaps():
    a=np.zeros((160,240),np.uint8)
    b=a.copy()
    cv2.circle(a,(90,90),54,1,-1)
    cv2.circle(b,(145,90),54,1,-1)
    return a,b

class TestAuditV1952(unittest.TestCase):
    def test_uint8_zero_one_masks_are_not_silently_empty(self):
        a,b=overlaps()
        q=contact.analyze_overlaps([a,b],.5)
        self.assertEqual(q['pixels_en_commun'],int(np.count_nonzero((a>0)&(b>0))))
        self.assertGreater(q['pixels_en_commun'],10)
        out,report=contact.propose_exclusive_masks([a,b])
        self.assertTrue(report['proposition_valide'])
        self.assertTrue(any(np.any(x==255) for x in out))
        self.assertFalse(np.any((out[0]>=128)&(out[1]>=128)))
        np.testing.assert_array_equal(a,(a>0).astype('uint8'))

    def test_mixed_binary_encodings(self):
        a,b=overlaps()
        q=contact.analyze_overlaps([a,b*255],.4)
        self.assertEqual(q['pixels_en_commun'],int(np.count_nonzero((a>0)&(b>0))))
        out,meta=contact.propose_exclusive_masks([a,b*255])
        self.assertTrue(meta['proposition_valide'])
        self.assertFalse(np.any((out[0]>=128)&(out[1]>=128)))
        self.assertTrue(np.any(out[0]==255))

    def test_soft_alpha_preserved_in_ordinary_255_masks(self):
        a,b=overlaps();a=a*255;b=b*255
        a[90,90]=190
        out,meta=contact.propose_exclusive_masks([a,b])
        self.assertTrue(meta['proposition_valide'])
        self.assertEqual(a.dtype,np.uint8)
        self.assertEqual(int(a[90,90]),190)
        # Exclusive alpha unchanged; pixels in shared areas may be removed.
        x,y=30,90
        if a[y,x]>=128 and b[y,x]<128:self.assertEqual(int(out[0][y,x]),int(a[y,x]))

    def test_soft_hair_support_survives_printable_at_zero_margin(self):
        src=np.full((100,100,3),[160,55,120],np.uint8)
        mask=np.zeros((100,100),np.float32)
        cv2.circle(mask,(50,50),19,.95,-1)
        cv2.circle(mask,(50,50),24,.2,3)
        source,printed,_,meta=geometry.cutout_with_white_border(src,mask,mm_per_px=.4,white_offset_mm=0)
        pad=meta['padding_px'];h,w=source.shape[:2]
        printed_area=printed[pad:pad+h,pad:pad+w,3]
        invisible=int(np.count_nonzero((source[:,:,3]>0)&(printed_area==0)))
        self.assertEqual(invisible,0)
        self.assertTrue(meta['support_alpha_faible_inclus'])

    def test_original_color_cutout_preserved(self):
        src=np.full((100,100,3),[180,33,44],np.uint8)
        mask=np.zeros((100,100),np.float32)
        mask[10:40,20:70]=.3
        rgba,printed,_,_=geometry.cutout_with_white_border(src,mask,mm_per_px=.5,white_offset_mm=0)
        self.assertEqual(int(rgba[5,5,3]),77)
        self.assertTrue(np.all(rgba[rgba[:,:,3]>0,:3]==[180,33,44]))

    def test_root_mask_directory_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);work=base/'project';work.mkdir()
            outside=base/'external';outside.mkdir()
            (work/'03_MASQUES').symlink_to(outside,target_is_directory=True)
            with self.assertRaises(contact.PhotoExtractionError):
                contact._mask_path_inside_root(work,'03_MASQUES/source.png')

    def test_internal_symlink_to_external_file_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);folder=base/'work'/'03_MASQUES';folder.mkdir(parents=True)
            external=base/'secret.png';external.touch()
            (folder/'fake.png').symlink_to(external)
            with self.assertRaises(contact.PhotoExtractionError):
                contact._mask_path_inside_root(folder.parent,'03_MASQUES/fake.png')

    def test_mask_header_overbudget_rejected_before_loading_pixels(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);folder=base/'03_MASQUES';folder.mkdir()
            # 40M pixels violates 32M; png compresses to a tiny file.
            name='large.png';Image.new('L',(8000,5000),0).save(folder/name,optimize=True)
            objects=[{'fichier_masque':f'03_MASQUES/{name}'}]
            with patch.object(contact.np,'asarray',side_effect=AssertionError('DECODED BEFORE LIMIT')):
                with self.assertRaisesRegex(contact.PhotoExtractionError,'AVANT decodage'):
                    contact._load_masks(base,objects)

    def test_distinct_mask_shapes_fail_before_distance(self):
        a,b=overlaps()
        with self.assertRaises(contact.PhotoExtractionError):
            contact.propose_exclusive_masks([a,b[:90]])

    def test_zero_one_proposal_no_input_mutation(self):
        a,b=overlaps();previous=(a.copy(),b.copy())
        contact.propose_exclusive_masks([a,b])
        np.testing.assert_array_equal(a,previous[0]);np.testing.assert_array_equal(b,previous[1])

if __name__=='__main__':unittest.main()

class TestProductionGuarantees(unittest.TestCase):
    def test_printable_alpha_coverage_check_passes(self):
        src=np.full((70,80,3),130,np.uint8)
        mask=np.zeros((70,80),np.float32)
        cv2.circle(mask,(35,30),13,.88,-1)
        cv2.circle(mask,(35,30),20,.21,2)
        rgb,printed,_,geometry_data=geometry.cutout_with_white_border(src,mask,mm_per_px=.4,white_offset_mm=0)
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'02_OBJETS_PNG').mkdir()
            Image.fromarray(rgb,'RGBA').save(root/'02_OBJETS_PNG/raw.png')
            Image.fromarray(printed,'RGBA').save(root/'02_OBJETS_PNG/print.png')
            item={'id':1,'fichier_rgba':'02_OBJETS_PNG/raw.png','fichier_cricut_test':'02_OBJETS_PNG/print.png','geometrie_cricut':geometry_data}
            result=contact._audit_cricut_alpha_coverage(root,[item])
            self.assertEqual(result[0]['pixels_hors_base_blanche'],0)

    def test_tampered_png_missing_translucent_pixels_rejected(self):
        src=np.full((70,80,3),130,np.uint8)
        mask=np.zeros((70,80),np.float32)
        cv2.circle(mask,(35,30),13,.9,-1)
        cv2.circle(mask,(35,30),20,.2,2)
        raw,printed,_,meta=geometry.cutout_with_white_border(src,mask,mm_per_px=.4,white_offset_mm=0)
        yy,xx=np.where(raw[:,:,3]>0)
        assert len(xx)>0
        pad=meta['padding_px']
        printed[yy[-1]+pad,xx[-1]+pad,3]=0
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'02_OBJETS_PNG').mkdir()
            Image.fromarray(raw,'RGBA').save(root/'02_OBJETS_PNG/raw.png')
            Image.fromarray(printed,'RGBA').save(root/'02_OBJETS_PNG/print.png')
            item={'id':1,'fichier_rgba':'02_OBJETS_PNG/raw.png','fichier_cricut_test':'02_OBJETS_PNG/print.png','geometrie_cricut':meta}
            with self.assertRaisesRegex(contact.PhotoExtractionError,'pixels source invisibles'):
                contact._audit_cricut_alpha_coverage(root,[item])

    def test_source_mask_dimensions_checked_at_header(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'03_MASQUES').mkdir()
            Image.new('L',(100,80),255).save(root/'03_MASQUES/m.png')
            with patch.object(contact.np,'asarray',side_effect=AssertionError('DECODED BEFORE SHAPE CHECK')):
                with self.assertRaisesRegex(contact.PhotoExtractionError,'image SOURCE'):
                    contact._load_masks(root,[{'fichier_masque':'03_MASQUES/m.png'}],expected_shape=(30,40))
