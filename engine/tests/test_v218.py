"""V21.8 CPU integration, adversarial transparency and Cricut handoff tests."""
from __future__ import annotations
import hashlib, importlib, json, os, sys, tempfile, types, unittest
from pathlib import Path
from unittest.mock import patch
import cv2
import numpy as np
from PIL import Image
import torch

ROOT=Path(__file__).resolve().parents[1]
if 'sv218test' not in sys.modules:
    pack=types.ModuleType('sv218test');pack.__path__=[str(ROOT)];sys.modules[pack.__name__]=pack
node=importlib.import_module('sv218test.node_v218')
old=importlib.import_module('sv218test.node_v2171')
mod=importlib.import_module('sv218test.smartsvg_cricut.direct_import_v218')


def sample():
    h,w=134,180
    rgb=np.full((h,w,3),.94,np.float32)
    mask=np.zeros((h,w),np.float32)
    cv2.ellipse(mask,(95,70),(46,36),0,0,360,1,-1)
    rgb[mask>0]=[.2,.4,.8]
    return torch.from_numpy(rgb)[None],torch.from_numpy(mask)


def run(cls,folder):
    image,mask=sample()
    return cls().run(image=image,masques_objets=mask,dossier_sortie=folder,
        projet='Sticker - contour du sujet',largeur_mm=40,qualite_ppp='300')

class CricutDirectImport(unittest.TestCase):
    def test_legacy_ports_registry(self):
        self.assertEqual(node.SmartSVGExpressV218.INPUT_TYPES(),old.SmartSVGExpressV2171.INPUT_TYPES())
        self.assertEqual(node.SmartSVGExpressV218.RETURN_TYPES,old.SmartSVGExpressV2171.RETURN_TYPES)
        self.assertIn('SmartSVGExpressV2151',node.NODE_CLASS_MAPPINGS)
        self.assertIn('SmartSVGExpressV218',node.NODE_CLASS_MAPPINGS)

    def test_full_pipeline_cricut_ready_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as td:
            before=json.loads(run(old.SmartSVGExpressV2171,td+'/old')['result'][2])
            response=run(node.SmartSVGExpressV218,td+'/new')
            after=json.loads(response['result'][2]);check=after['import_direct_cricut_v218']
            self.assertEqual(check['statut'],'PRET_POUR_IMPORT_LOCAL')
            self.assertEqual(check['fichiers_prets'],1)
            self.assertFalse(check['import_design_space_reel_teste'])
            item=after['objets'][0];output=Path(check['objets'][0]['fichier_import'])
            self.assertIn('00_IMPORTER_DANS_CRICUT',str(output))
            self.assertEqual(output.read_bytes(),Path(item['fichier_png_cricut']).read_bytes())
            for k in ('fichier_png_cricut','fichier_svg_contour','fichier_transparent'):
                sha=lambda r:hashlib.sha256(Path(r['objets'][0][k]).read_bytes()).hexdigest()
                self.assertEqual(sha(before),sha(after))
            self.assertEqual(check['objets'][0]['composantes_alpha'],1)
            self.assertIn('Flat Graphic',Path(check['dossier'],'LIRE_AVANT_IMPORT.txt').read_text())
            self.assertIn('import direct',node.NODE_DISPLAY_NAME_MAPPINGS['SmartSVGExpressV218'])

    def test_12_mask_one_file_board_one_file_per_sticker(self):
        with tempfile.TemporaryDirectory() as td:
            image=np.full((420,620,3),.92,np.float32)
            masks=np.zeros((12,420,620),np.float32)
            yy,xx=np.ogrid[:420,:620]
            for i in range(12):
                cx,cy=75+(i%4)*150,70+(i//4)*130
                sel=(xx-cx)**2+(yy-cy)**2<28**2
                masks[i,sel]=1
                image[sel]=[.2,.5,.8]
            response=node.SmartSVGExpressV218().run(
                image=torch.from_numpy(image)[None],masques_objets=torch.from_numpy(masks),
                dossier_sortie=td,projet='Planche - 12 images (4x3)',largeur_mm=26,qualite_ppp='300')
            doc=json.loads(response['result'][2]);qa=doc['import_direct_cricut_v218']
            self.assertEqual(qa['fichiers_prets'],12)
            self.assertEqual(qa['planches_pretes'],1)
            self.assertEqual(qa['planches'][0]['composantes_alpha'],12)

    def test_donut_internal_hole_is_not_claimed_ready(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);a=np.zeros((120,120,4),np.uint8)
            a[20:100,20:100]=[240,20,30,255];a[46:75,46:75]=0
            src=p/'original.png';Image.fromarray(a,'RGBA').save(src)
            report={'dossier':td,'objets':[{'png':str(src)}]}
            r=mod.prepare_cricut_import(report,300)
            self.assertEqual(r['fichiers_prets'],0)
            self.assertIn('Trous transparents',r['objets'][0]['raison'])

    def test_multiple_islands_and_empty_image_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);a=np.zeros((100,140,4),np.uint8)
            a[15:35,15:35]=[240,20,30,255]
            a[50:80,90:120]=[30,20,240,255]
            src=p/'twice.png';Image.fromarray(a,'RGBA').save(src)
            r=mod.prepare_cricut_import({'dossier':td,'objets':[{'png':str(src)}]},300)
            self.assertEqual(r['fichiers_prets'],0)
            self.assertIn('2 zones de decoupe',r['objets'][0]['raison'])
            a[:]=0;Image.fromarray(a,'RGBA').save(src)
            r=mod.prepare_cricut_import({'dossier':td,'objets':[{'png':str(src)}]},300)
            self.assertEqual(r['fichiers_prets'],0)

    def test_relative_and_external_paths_denied(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);project=root/'project';project.mkdir()
            outsider=root/'private.png';Image.new('RGBA',(40,40),'red').save(outsider)
            for testpath in (str(outsider),'private.png'):
                r=mod.prepare_cricut_import({'dossier':str(project),'objets':[{'png':testpath}]},300)
                self.assertEqual(r['fichiers_prets'],0)
            symlink=project/'linked.png';symlink.symlink_to(outsider)
            r=mod.prepare_cricut_import({'dossier':str(project),'objets':[{'png':str(symlink)}]},300)
            self.assertEqual(r['fichiers_prets'],0)

    def test_svg_only_has_no_color_artwork(self):
        with tempfile.TemporaryDirectory() as td:
            report=json.loads(run(node.SmartSVGExpressV218,td)['result'][2])
            assert report['import_direct_cricut_v218']['fichiers_prets']==1
            svg=Path(report['objets'][0]['fichier_svg_contour']).read_text()
            self.assertNotIn('<image',svg)
            self.assertIn('<path',svg)
            self.assertIn('PNG',Path(report['import_direct_cricut_v218']['dossier'],'LIRE_AVANT_IMPORT.txt').read_text())

    def test_failure_of_optional_audit_does_not_break_exports(self):
        with tempfile.TemporaryDirectory() as td:
            with patch.object(node,'prepare_cricut_import',side_effect=RuntimeError('test')):
                r=run(node.SmartSVGExpressV218,td)
            doc=json.loads(r['result'][2]);self.assertTrue(Path(doc['objets'][0]['fichier_png_cricut']).exists())
            self.assertIn('indisponible',r['result'][1])

    def test_opaque_no_mask_is_explicitly_a_rectangle(self):
        with tempfile.TemporaryDirectory() as td:
            im,_=sample()
            r=node.SmartSVGExpressV218().run(image=im,dossier_sortie=td,
                projet='Auto - conserver le visuel',largeur_mm=40,qualite_ppp='300',ia_locale='Desactivee')
            doc=json.loads(r['result'][2]);qa=doc['import_direct_cricut_v218']
            self.assertEqual(qa['statut'],'PRET_POUR_IMPORT_LOCAL_AVEC_CADRES')
            self.assertEqual(qa['cartes_rectangulaires'],1)
            self.assertEqual(qa['objets'][0]['type_decoupe_presumee'],'CADRE_RECTANGULAIRE_SANS_DETOURAGE')

    def test_incoherent_physical_width_is_never_ready(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);source=p/'image.png'
            Image.new('RGBA',(100,100),'orange').save(source)
            doc={'dossier':td,'objets':[{'png':str(source),'largeur_finale_avec_marge_mm':50.0}]}
            qa=mod.prepare_cricut_import(doc,300)
            self.assertEqual(qa['fichiers_prets'],0)
            self.assertIn('Taille physique incoherente',qa['objets'][0]['raison'])

    def test_user_files_never_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td);src=p/'main.png';Image.new('RGBA',(60,70),'red').save(src)
            dest=p/mod.FOLDER;dest.mkdir();target=dest/'STICKER_001_IMPRIMER_PUIS_DECOUPER.png'
            target.write_bytes(b'user-data')
            r=mod.prepare_cricut_import({'dossier':td,'objets':[{'png':str(src)}]},300)
            self.assertEqual(target.read_bytes(),b'user-data')
            self.assertEqual(r['fichiers_prets'],0)

if __name__=='__main__':unittest.main()
