"""V20.6 QA: source native detail reporting, single-island contours, 24-item grids."""
import unittest, tempfile, importlib,sys,types,io,json,math
from pathlib import Path
from PIL import Image
import cv2,numpy as np,torch
ROOT=Path(__file__).resolve().parents[1]
if 'sv206test' not in sys.modules:
    p=types.ModuleType('sv206test');p.__path__=[str(ROOT)];sys.modules[p.__name__]=p
core=importlib.import_module('sv206test.hd_multisticker_v206')
node=importlib.import_module('sv206test.node_v206')

class V206Tests(unittest.TestCase):
    def test_register_legacy(self):
        self.assertIn('SmartSVGLineArtV205',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGStudioV20Expert',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGSimpleV206',node.NODE_CLASS_MAPPINGS)
    def test_simple_interface(self):
        x=node.SmartSVGSimpleV206.INPUT_TYPES()['required'];self.assertEqual(len(x),7)
    def test_bad_images(self):
        for x in (np.zeros((10,10)), np.zeros((10,10,3),np.float32),np.zeros((0,10,3),np.uint8)):
            with self.assertRaises(core.ExportError):core._valid_image(x)
    def test_bad_config(self):
        p=np.zeros((20,20,3),np.uint8)
        with tempfile.TemporaryDirectory() as t:
            for kw in ({'dpi':120},{'preset':'bogus'},{'width_mm':float('nan')},{'grille':'9x9'},{'mode_coupe':'surprise'}):
                with self.assertRaises(core.ExportError):core.run_v206(p,t,**kw)
    def test_native_dpi_warns_not_ai_upscale(self):
        im=np.zeros((130,120,3),np.uint8);im[20:110,30:90]=100
        x,m=core._make_card(im,40,300)
        self.assertTrue(m['facteur_interpolation']>3)
        self.assertIn('AGRANDISSEMENT_INTERPOLATION_NE_CREE_PAS_DE_DETAIL',m['avertissements'])
        self.assertEqual(m['densite_export_cible_ppp'],300)
    def test_keep_native_resolution(self):
        im=np.zeros((160,700,3),np.uint8)
        x,m=core._make_card(im,40,300)
        self.assertEqual(m['facteur_interpolation'],1.0)
    def test_real_dpi_metadata(self):
        with tempfile.TemporaryDirectory() as t:
            p=np.full((80,120,3),120,np.uint8)
            r,_=core.run_v206(p,t,'affiche',45,300)
            with Image.open(r['objets'][0]['png']) as im:
                self.assertTrue(abs(im.info['dpi'][0]-300)<1)
    def test_rectangle_cut_path(self):
        with tempfile.TemporaryDirectory() as t:
            a=np.full((120,100,3),255,np.uint8)
            r,_=core.run_v206(a,t,'affiche',50,300)
            self.assertEqual(r['objets'][0]['contour_nombre_chemins'],1)
            svg=Path(r['objets'][0]['svg_contour']).read_text()
            self.assertIn('<svg',svg)
    def test_transparency_respected(self):
        a=np.zeros((120,100,4),np.uint8);a[20:100,30:80]=[240,40,60,255]
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v206(a,t,'logo_cartoon',42,300)
            im=Image.open(r['objets'][0]['png'])
            self.assertEqual(im.mode,'RGBA')
            self.assertEqual(im.getpixel((0,0))[3],0)
            self.assertEqual(r['objets'][0]['source_alpha'],'SOURCE_AVEC_TRANSPARENCE_UTILISEE')
    def test_empty_transparent_rejected(self):
        a=np.zeros((70,60,4),np.uint8)
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(core.ExportError):core.run_v206(a,t,'logo_cartoon')
    def test_logo_letterbox_removed(self):
        a=np.zeros((320,220,3),np.uint8)
        a[65:270]=255
        a[120:200,80:150]=[140,40,80]
        with tempfile.TemporaryDirectory() as t:
            report,_=core.run_v206(a,t,'logo_cartoon',60)
            self.assertGreater(report['recadrage_bandes_logo'][1],55)
            self.assertLess(report['recadrage_bandes_logo'][3],280)
            self.assertEqual(report['objets'][0]['contour_nombre_chemins'],1)
    def test_crop_phone(self):
        im=np.zeros((460,160,3),np.uint8)
        im[110:320]=(60,130,180)
        crop,box,alerts=core._crop_capture(im)
        self.assertLess(crop.shape[0],280)
        self.assertGreater(box[1],75)
    def test_synthetic_multigrid(self):
        a=np.zeros((600,900,3),np.uint8)
        for row in range(4):
            for col in range(6):
                cx=col*150+75;cy=row*150+70
                cv2.circle(a,(cx,cy),43,(col*30+30,row*45+45,160),-1)
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v206(a,t,'planche_multi',23,300)
            self.assertEqual(len(r['objets']),24)
            self.assertTrue(all(x['contour_nombre_chemins']==1 for x in r['objets']))
            self.assertEqual(len(r['planches_cricut']),2)
            self.assertEqual(r['planches_cricut'][0]['ilots_alpha_detectes'],12)
    def test_isolated_detached_flame(self):
        a=np.zeros((180,130,3),np.uint8)
        cv2.circle(a,(55,95),32,(240,90,30),-1)
        cv2.circle(a,(95,36),7,(240,90,30),-1)
        mask=core._foreground_cell(a)
        pic,sil,qa=core._make_sticker(a,mask,30,300)
        _,num=core._path_svg(sil,qa['largeur_finale_avec_marge_mm'],300)
        self.assertEqual(num,1)
        self.assertTrue(qa['contour_convexe_secours'])
    def test_grid_components_cross_boundary(self):
        a=np.zeros((300,400,3),np.uint8)
        cv2.ellipse(a,(110,160),(40,100),0,0,360,(255,110,50),-1)
        cv2.ellipse(a,(300,160),(40,100),0,0,360,(70,140,255),-1)
        res=list(core._grid_component_groups(a,2,1))
        self.assertEqual(len(res),2)
        self.assertTrue(all(x[2] is not None for x in res))
    def test_comfyui_run(self):
        a=torch.from_numpy(np.ones((1,90,90,3),np.float32))
        with tempfile.TemporaryDirectory() as t:
            r=node.SmartSVGSimpleV206().run(a,t,profil='affiche')
            self.assertEqual(r['result'][0].ndim,4)
            self.assertEqual(json.loads(r['result'][1])['nombre_objets_exportes'],1)
    def test_comfyui_reject_batch(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(core.ExportError):node.SmartSVGSimpleV206().run(torch.zeros((2,30,30,3)),t)
    def test_comfyui_reject_nan(self):
        with tempfile.TemporaryDirectory() as t:
            x=torch.zeros((1,30,30,3));x[0,1,1,1]=float('nan')
            with self.assertRaises(core.ExportError):node.SmartSVGSimpleV206().run(x,t)
    def test_auto_profiles(self):
        bg=np.zeros((600,800,3),np.uint8);bg[50:450,60:350]=200
        self.assertEqual(core._source_preset(bg),'planche_multi')
        white=np.full((400,700,3),255,np.uint8)
        self.assertEqual(core._source_preset(white),'logo_cartoon')
    def test_single_cut_has_no_internal_eyes(self):
        c=np.full((140,140,3),180,np.uint8);m=np.zeros((140,140),np.uint8)
        cv2.circle(m,(70,70),45,255,-1)
        cv2.circle(m,(55,60),7,0,-1)
        sticker,alpha,qa=core._make_sticker(c,m,35,300)
        text,paths=core._path_svg(alpha,qa['largeur_finale_avec_marge_mm'],300)
        self.assertEqual(paths,1)
    def test_white_background_grid(self):
        a=np.full((300,400,3),255,np.uint8)
        for row in range(3):
            for col in range(4):
                cv2.circle(a,(50+col*100,50+row*100),20,(30,90,150),-1)
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v206(a,t,'planche_multi',20,300,grille='4x3')
            self.assertEqual(len(r['objets']),12)
            self.assertEqual(r['planches_cricut'][0]['ilots_alpha_detectes'],12)
    def test_complex_background_multi_rejected(self):
        a=np.full((200,300,3),(85,80,90),np.uint8)
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(core.ExportError):core.run_v206(a,t,'planche_multi',20)
    def test_print_sheets_under_conservative_a4(self):
        a=np.zeros((600,900,3),np.uint8)
        for row in range(4):
            for col in range(6):
                cv2.circle(a,(col*150+75,row*150+75),34,(90,120,180),-1)
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v206(a,t,'planche_multi',30)
            self.assertTrue(all(s['statut']=='CREATION_OK' for s in r['planches_cricut']))
            for s in r['planches_cricut']:
                self.assertLess(s['taille_estimee_mm'][0],175)
    def test_multi_single_export_svg_units(self):
        a=np.zeros((600,900,3),np.uint8)
        for row in range(4):
            for col in range(6):
                cv2.rectangle(a,(col*150+45,row*150+40),(col*150+105,row*150+110),(180,90,100),-1)
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v206(a,t,'planche_multi',24)
            x=Path(r['objets'][0]['svg_contour']).read_text()
            self.assertIn('mm',x)
            self.assertIn('viewBox',x)
    def test_report_no_claims_ai(self):
        with tempfile.TemporaryDirectory() as t:
            r,_=core.run_v206(np.zeros((80,80,3),np.uint8),t,'affiche')
            self.assertFalse(r['validation_cricut_physique'])
            self.assertTrue(Path(r['dossier']).joinpath('RAPPORT_V20_6.json').is_file())

if __name__=='__main__':unittest.main()
