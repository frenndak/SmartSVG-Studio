"""V21.11.1 adversarial checks for alpha, topology, shape, memory and handoff."""
import importlib, sys, types, unittest, tempfile, json
from pathlib import Path
import numpy as np
import cv2
import torch
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
if 'sv21111test' not in sys.modules:
    p=types.ModuleType('sv21111test');p.__path__=[str(ROOT)];sys.modules[p.__name__]=p
core=importlib.import_module('sv21111test.smartsvg_ai.auto_masks_v2111')
node=importlib.import_module('sv21111test.node_v2111')
cricut=importlib.import_module('sv21111test.smartsvg_cricut.direct_import_v218')


def sample(h=160,w=190):
    rgb=np.full((h,w,3),240,dtype=np.uint8)
    alpha=np.zeros((h,w),dtype=np.uint8)
    cv2.circle(alpha,(w//2,h//2),min(h,w)//4,255,-1)
    cv2.circle(rgb,(w//2,h//2),min(h,w)//4,(70,40,200),-1)
    mask=torch.from_numpy((1-alpha.astype('float32')/255)[None])
    return rgb,alpha,mask

class TestV21111Correctifs(unittest.TestCase):
    def test_alpha_from_real_loadimage_polarity(self):
        rgb,alpha,masked=sample()
        image=torch.from_numpy(rgb.astype('float32')/255)[None]
        out=node.SmartSVGAutoMasksV2111().run(image,'Desactivee',alpha_loadimage=masked)
        masks,unchanged,report=out['result']
        self.assertIs(unchanged,image)
        self.assertEqual(json.loads(report)['methode'],'ALPHA_LOADIMAGE')
        self.assertTrue(np.array_equal(masks.numpy()[0]>=.5,alpha>=128))

    def test_loadimage_jpeg_default_mask_64(self):
        # ComfyUI returns a 64x64 all-zero MASK for a non-alpha JPEG.
        rgb,_,_=sample()
        image=torch.from_numpy(rgb.astype('float32')/255)[None]
        self.assertIsNone(node._loadimage_alpha(torch.zeros((1,64,64)),rgb.shape[:2]))
        # Should not accidentally manufacture an alpha silhouette.
        with self.assertRaisesRegex(core.AutoMaskError,'attendu'):
            node._loadimage_alpha(torch.ones((1,64,64)),rgb.shape[:2])

    def test_alpha_bad_shape_is_not_accepted(self):
        rgb,_,_=sample()
        m=np.zeros((rgb.shape[1],rgb.shape[0]),dtype=np.float32)
        with self.assertRaisesRegex(core.AutoMaskError,'dimensions'):
            core.generate_masks(rgb,supplied_alpha=m)

    def test_alpha_fallback_for_opaque_loadimage(self):
        rgb=np.full((160,190,3),255,dtype=np.uint8)
        m,r=core.generate_masks(rgb,supplied_alpha=np.zeros((160,190),dtype='float32'))
        self.assertIsNone(m)
        self.assertIn('COULEUR_ABSENTE_OU_TROP_ETENDUE',r['avertissements'])

    def test_no_accidental_flip_of_explicit_mask(self):
        rgb,alpha,mask=sample()
        m,r=core.generate_masks(rgb,supplied_alpha=mask[0].numpy())
        self.assertEqual(r['methode'],'ALPHA_LOADIMAGE')
        self.assertGreater(m[0,80,95],.99)
        self.assertLess(m[0,0,0],.01)

    def test_transposed_loadimage_mask_refused(self):
        rgb,alpha,mask=sample(160,190)
        image=torch.from_numpy(rgb.astype('float32')/255)[None]
        with self.assertRaisesRegex(core.AutoMaskError,'attendu'):
            node.SmartSVGAutoMasksV2111().run(image,'Desactivee',alpha_loadimage=mask.transpose(1,2))

    def test_external_transposed_mask_even_same_pixel_count_refused(self):
        rgb,alpha,mask=sample(160,190)
        image=torch.from_numpy(rgb.astype('float32')/255)[None]
        with self.assertRaisesRegex(core.AutoMaskError,'FORMAT_INVALIDE'):
            node.SmartSVGAutoExpressV2111().run(image,masques_objets=torch.zeros((1,190,160)))

    def test_ai_transposed_shape_refused(self):
        rgb,_,_=sample()
        candidate=np.zeros((190,160),dtype='float32')
        cv2.circle(candidate,(80,90),20,1.,-1)
        m,report=core.generate_masks(rgb,force_ai=True,allow_ai=True,
                                provider=lambda _: {'masks':candidate,'audit':{'mock':True}})
        self.assertIsNone(m)
        self.assertIn('MASQUES_FORMAT_INVALIDE',report['avertissements'])

    def test_near_rect_with_single_missing_pixel_is_rejected(self):
        rgb=np.full((210,210,3),210,dtype=np.uint8)
        m=np.zeros((210,210),dtype='float32');m[20:190,20:190]=1.;m[20,20]=0.
        masks,issues=core._accept(m,pixel_count=210*210,expected_hw=(210,210),source='IA')
        self.assertIsNone(masks)
        self.assertIn('QUASI_RECTANGULAIRE',issues[0])

    def test_circle_remains_accepted(self):
        rgb,alpha,_=sample()
        masks,issues=core._accept(alpha.astype('float32')/255,pixel_count=160*190,
                               expected_hw=(160,190),source='IA')
        self.assertIsNotNone(masks)

    def test_islands_over_32_produce_explicit_refusal(self):
        m=np.zeros((320,320),dtype='float32')
        for i in range(33):
            x=14+(i%7)*43;y=14+(i//7)*55
            cv2.circle(m,(x,y),4,1.,-1)
        out,issues=core._accept(m,pixel_count=m.size,expected_hw=m.shape,source='IA')
        self.assertIsNone(out)
        self.assertIn('TROP_D_ILOTS_33',issues[0])

    def test_many_disconnected_alpha_reports_explicit_warning(self):
        rgb=np.zeros((320,320,3),dtype=np.uint8)
        visible=np.zeros((320,320),dtype=np.float32)
        for i in range(33):
            cv2.circle(visible,(14+(i%7)*43,14+(i//7)*55),5,1.,-1)
        _,report=core.generate_masks(rgb,supplied_alpha=(1-visible))
        self.assertIn('ALPHA_TROP_D_ILOTS_33',report['avertissements'])

    def test_cricut_preflight_classifies_near_rectangle_as_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            a=np.zeros((210,210,4),dtype=np.uint8)
            a[20:190,20:190,:3]=[120,50,200]
            a[20:190,20:190,3]=255;a[20,20,3]=0
            src=root/'source.png';Image.fromarray(a,'RGBA').save(src,dpi=(300,300))
            geo=cricut._topology(src)
            self.assertTrue(geo['alpha_quasi_rectangle'])
            report={'dossier':str(root),'objets':[{'png':str(src)}]}
            prep=cricut.prepare_cricut_import(report,300)
            self.assertEqual(prep['cartes_rectangulaires'],1)
            self.assertEqual(prep['objets'][0]['statut'],'PRET_POUR_IMPORT_LOCAL_CADRE')

    def test_nonrect_cricut_classified_as_silhouette(self):
        with tempfile.TemporaryDirectory() as tmp:
            a=np.zeros((210,210,4),dtype=np.uint8)
            cv2.circle(a,(105,105),70,(100,200,60,255),-1)
            src=Path(tmp)/'circle.png';Image.fromarray(a,'RGBA').save(src)
            self.assertFalse(cricut._topology(src)['alpha_rectangle_plein'])

    def test_mask_budget_is_checked_before_fullframe_allocations(self):
        rgb=np.full((280,280,3),255,dtype=np.uint8)
        for yy in [70,210]:
            for xx in [70,210]:cv2.circle(rgb,(xx,yy),38,(100,20,120),-1)
        old=core.MAX_TOTAL
        try:
            core.MAX_TOTAL=280*280*2
            out,reason=core._flat_artwork(rgb)
            self.assertIsNone(out)
            self.assertEqual(reason['raison'],'BUDGET_MEMOIRE_MASQUES')
        finally:core.MAX_TOTAL=old

    def test_automatic_alpha_real_manufacturing_handoff(self):
        rgb,alpha,mask=sample()
        image=torch.from_numpy(rgb.astype('float32')/255)[None]
        with tempfile.TemporaryDirectory() as tmp:
            response=node.SmartSVGAutoExpressV2111().run(image,dossier_sortie=tmp,
                         projet='Sticker - contour du sujet',largeur_mm=30.,
                         qualite_ppp='300',ia_locale='Desactivee',alpha_loadimage=mask)
            result=json.loads(response['result'][2]);pre=result['import_direct_cricut_v218']
            self.assertEqual(pre['fichiers_prets'],1)
            self.assertEqual(pre['cartes_rectangulaires'],0)
            self.assertEqual(result['detourage_automatique_v2111']['methode'],'ALPHA_LOADIMAGE')
            self.assertTrue(Path(pre['objets'][0]['fichier_import']).is_file())

    def test_external_good_mask_passes_without_reinversion(self):
        rgb,alpha,_=sample()
        image=torch.from_numpy(rgb.astype('float32')/255)[None]
        m,flags=node._validate_external_masks(torch.from_numpy(alpha.astype('float32')/255)[None],alpha.shape)
        self.assertEqual(float(m[0,80,95]),1.)

if __name__=='__main__':unittest.main()
