"""V21.12.2: skip only redundant sheet render, outputs and old API preserved."""
import unittest,types,sys,importlib,json,tempfile
from pathlib import Path
from unittest.mock import patch
import numpy as np,cv2,torch
ROOT=Path(__file__).resolve().parents[1]
if 'sv21122tests' not in sys.modules:
    pkg=types.ModuleType('sv21122tests');pkg.__path__=[str(ROOT)];sys.modules[pkg.__name__]=pkg
node=importlib.import_module('sv21122tests.node_v21122')
prior=importlib.import_module('sv21122tests.node_v21121')
prod=importlib.import_module('sv21122tests.production_v211')
v21=importlib.import_module('sv21122tests.multi_subject_v21')
manifest=importlib.import_module('sv21122tests.smartsvg_cricut.delivery_v21122')

def inputs():
    rgb=np.full((120,190,3),242,dtype=np.uint8)
    masks=np.zeros((2,120,190),dtype=np.float32)
    cv2.circle(masks[0],(45,56),30,1,-1)
    cv2.ellipse(masks[1],(145,58),(20,34),0,0,360,1,-1)
    rgb[masks[0]>0]=[221,80,50];rgb[masks[1]>0]=[56,85,221]
    return torch.from_numpy(rgb.astype('float32')/255)[None],torch.from_numpy(masks)

class TestBatchOptimization(unittest.TestCase):
    def test_context_isolation(self):
        self.assertFalse(prod._DEFER_SHEETS.get())
        with prod.defer_intermediate_sheets():
            self.assertTrue(prod._DEFER_SHEETS.get())
            with prod.defer_intermediate_sheets():self.assertTrue(prod._DEFER_SHEETS.get())
            self.assertTrue(prod._DEFER_SHEETS.get())
        self.assertFalse(prod._DEFER_SHEETS.get())
        with self.assertRaisesRegex(ValueError,'test'):
            with prod.defer_intermediate_sheets():raise ValueError('test')
        self.assertFalse(prod._DEFER_SHEETS.get())

    def test_legacy_and_optimized_produce_identical_print_files(self):
        image,masks=inputs()
        args=dict(projet='Sticker - contour du sujet',largeur_mm=28.,qualite_ppp='300',
                  ia_locale='Desactivee',masques_objets=masks)
        call_count=[]
        make_pages=v21._make_pages
        def count(*a,**k):call_count.append(1);return make_pages(*a,**k)
        with tempfile.TemporaryDirectory() as old_dir,tempfile.TemporaryDirectory() as new_dir,patch.object(v21,'_make_pages',count):
            old=prior.SmartSVGAutoExpressV21121().run(image,dossier_sortie=old_dir,**args)
            self.assertEqual(len(call_count),2)
            call_count.clear()
            new=node.SmartSVGAutoExpressV21122().run(image,dossier_sortie=new_dir,**args)
            self.assertEqual(len(call_count),1)
            a,b=(json.loads(k['result'][2]) for k in (old,new))
            self.assertEqual(a['nombre_objets_exportes'],b['nombre_objets_exportes'])
            self.assertEqual(len(a['planches']),len(b['planches']))
            for k in ('planches',):
                for x,y in zip(a[k],b[k]):
                    self.assertEqual(Path(x['fichier']).read_bytes(),Path(y['fichier']).read_bytes())
            for x,y in zip(a['objets'],b['objets']):
                for name in ('fichier_png_cricut','fichier_svg_contour'):
                    self.assertEqual(Path(x[name]).read_bytes(),Path(y[name]).read_bytes())
            for x,y in zip(a['import_direct_cricut_v218']['objets'],b['import_direct_cricut_v218']['objets']):
                self.assertEqual(Path(x['fichier_import']).read_bytes(),Path(y['fichier_import']).read_bytes())
            audit=b['livraison_v21122']
            self.assertEqual(audit['sujets_fabriques'],2)
            self.assertEqual(audit['png_import_precontroles'],2)
            self.assertFalse(audit['validation_physique'])
            self.assertTrue(Path(audit['manifeste']).is_file())
            self.assertEqual(audit['optimisation']['planches_intermediaires_evitees'],True)

    def test_internal_cut_hole_filled_only_on_new_opt_in(self):
        rgb=np.full((180,180,3),210,dtype=np.uint8)
        mask=np.zeros((180,180),dtype=np.float32)
        cv2.circle(mask,(90,90),60,1.,-1)
        cv2.circle(mask,(90,90),27,0.,-1)
        image=torch.from_numpy(rgb.astype('float32')/255)[None]
        masks=torch.from_numpy(mask[None])
        args=dict(projet='Sticker - contour du sujet',largeur_mm=32.,qualite_ppp='300',
                  ia_locale='Desactivee',masques_objets=masks)
        with tempfile.TemporaryDirectory() as old_dir,tempfile.TemporaryDirectory() as new_dir:
            a=prior.SmartSVGAutoExpressV21121().run(image,dossier_sortie=old_dir,**args)
            b=node.SmartSVGAutoExpressV21122().run(image,dossier_sortie=new_dir,**args)
            old=json.loads(a['result'][2]);new=json.loads(b['result'][2])
            self.assertEqual(old['import_direct_cricut_v218']['fichiers_prets'],0)
            self.assertEqual(new['import_direct_cricut_v218']['fichiers_prets'],1)
            self.assertEqual(new['livraison_v21122']['png_import_precontroles'],1)
            # The native cutout (with the hole) remains byte-for-byte unchanged.
            key='fichier_transparent'
            self.assertEqual(Path(old['objets'][0][key]).read_bytes(),Path(new['objets'][0][key]).read_bytes())

    def test_missing_import_is_not_misreported_as_ready(self):
        image,masks=inputs()
        with tempfile.TemporaryDirectory() as d:
            r=node.SmartSVGAutoExpressV21122().run(image,dossier_sortie=d,
                projet='Sticker - contour du sujet',largeur_mm=28.,qualite_ppp='300',
                ia_locale='Desactivee',masques_objets=masks)
            report=json.loads(r['result'][2]);old=report['import_direct_cricut_v218']['objets'][0]['fichier_import']
            Path(old).unlink()
            x=manifest.delivery_manifest(report)
            self.assertEqual(x['statut'],'REVISIONS_NECESSAIRES')
            self.assertEqual(x['png_import_precontroles'],1)
            self.assertIn('FICHIER_IMPRESSION_INEXPLOITABLE',str(x['objets'][0]['avertissements']))

    def test_manifest_rejects_external_symlink_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);file=root/'foo.png';file.write_bytes(b'hi')
            self.assertEqual(manifest._owned_file(root,str(file)),file.resolve())
            outside=root.parent/'other.tmp'
            with self.assertRaises(manifest.DeliveryError):manifest._owned_file(root,str(outside))
            link=root/'symlink.png';link.symlink_to(file)
            with self.assertRaises(manifest.DeliveryError):manifest._owned_file(root,str(link))
            data={'test':1}
            manifest.write_delivery(root,data)
            with self.assertRaises(manifest.DeliveryError):manifest.write_delivery(root,data)
            self.assertTrue((root/'07_LIVRAISON_STICKERS_V21_12_2/MANIFESTE_STICKERS.json').is_file())

    def test_old_node_ids_and_five_controls_preserved(self):
        for name,cls in prior.NODE_CLASS_MAPPINGS.items():
            self.assertIs(node.NODE_CLASS_MAPPINGS[name],cls)
        a=node.SmartSVGAutoExpressV21122.INPUT_TYPES()
        self.assertEqual(len(a['required']),6)
        self.assertEqual(len(a['optional']),2)
        self.assertEqual(node.SmartSVGAutoExpressV21122.RETURN_TYPES,prior.SmartSVGAutoExpressV21121.RETURN_TYPES)

if __name__=='__main__':unittest.main()
