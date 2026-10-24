"""V21.9.1 cross-review: native geometry, preview memory, atomic Cricut handoff."""
from __future__ import annotations
import tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import numpy as np
from PIL import Image
from tests.test_v219 import inspector
from tests.test_v218 import mod

class NativePatches(unittest.TestCase):
    def test_overlap_does_not_copy_other_masks_for_each_object(self):
        h,w=120,160
        im=np.zeros((h,w,3),np.float32)
        masks=np.zeros((24,h,w),np.float32)
        for i in range(24):
            x=4+6*i;masks[i,20:80,x:x+15]=1
        with patch.object(inspector.np,'delete',side_effect=AssertionError('unnecessary NxN allocation')):
            report=inspector.analyse(im,masks,width_mm=32)
        self.assertEqual(len(report['objets']),24)
        self.assertTrue(any(p['type']=='MASQUES_CHEVAUCHANTS' for p in report['objets'][2]['points']))

    def test_contact_on_small_component_is_localized(self):
        mask=np.zeros((110,155),np.float32)
        mask[35:95,50:130]=1
        mask[0,4:7]=1  # only small disconnected component touches edge
        points=inspector.find_spots(mask)
        self.assertTrue(any(p['type']=='BORD_IMAGE' and p['y']==0 for p in points))
        self.assertTrue(any(p['type']=='ILOT_DETACHE' for p in points))

    def test_preview_bounded_failure_leaves_no_temp_files(self):
        im=np.zeros((100,120,3),np.float32)
        mask=np.ones((2,100,120),np.float32)
        with tempfile.TemporaryDirectory() as td:
            with patch.object(inspector,'MAX_SESSION_BYTES',50):
                self.assertIsNone(inspector.publish_native(im,mask,td))
            folder=Path(td)/inspector.FOLDER
            self.assertEqual(list(folder.glob('ni_*.png')),[])

class CricutCopyPatches(unittest.TestCase):
    @staticmethod
    def create_source(root):
        source=root/'src.png'
        image=np.zeros((85,100,4),np.uint8)
        image[15:65,22:78,:]=[70,145,235,255]
        Image.fromarray(image,'RGBA').save(source)
        return source

    def test_idempotent_rerun_bytes_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);src=self.create_source(root)
            report={'dossier':td,'objets':[{'png':str(src)}]}
            a=mod.prepare_cricut_import(report,300)
            target=Path(a['objets'][0]['fichier_import']);before=target.read_bytes()
            b=mod.prepare_cricut_import(report,300)
            self.assertEqual(b['fichiers_prets'],1)
            # A fully filled rectangular alpha region is not a character silhouette.
            self.assertEqual(b['statut'],'PRET_POUR_IMPORT_LOCAL_AVEC_CADRES')
            self.assertEqual(before,target.read_bytes())

    def test_changed_same_filename_is_never_labeled_current(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);src=self.create_source(root)
            report={'dossier':td,'objets':[{'png':str(src)}]}
            a=mod.prepare_cricut_import(report,300)
            target=Path(a['objets'][0]['fichier_import']);before=target.read_bytes()
            with Image.open(src) as im:
                im=im.copy();im.putpixel((30,30),(255,0,0,255));im.save(src)
            b=mod.prepare_cricut_import(report,300)
            self.assertEqual(b['fichiers_prets'],0)
            self.assertEqual(b['statut'],'A_VERIFIER')
            self.assertIn('contenu different',b['objets'][0]['raison'])
            self.assertIn('ANCIEN PNG',b['objets'][0]['avertissement'])
            self.assertEqual(target.read_bytes(),before)

    def test_portable_exclusive_create_without_hardlinks(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);src=self.create_source(root);dest=root/'target.png'
            with patch.object(mod.os,'link',side_effect=OSError('filesystem has no hardlink support')):
                mod._copy_atomic(src,dest)
            self.assertEqual(mod._sha256_file(dest),mod._sha256_file(src))
            self.assertFalse(list(root.glob('.tmp_*')))

    def test_concurrent_creation_cannot_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);src=self.create_source(root);dest=root/'target.png'
            def competitor(tmp,final):
                Path(final).write_bytes(b'other workflow')
                raise FileExistsError('already exists')
            with patch.object(mod.os,'link',side_effect=competitor):
                with self.assertRaises(mod.ImportAuditError):mod._copy_atomic(src,dest)
            self.assertEqual(dest.read_bytes(),b'other workflow')
            self.assertFalse(list(root.glob('.tmp_*')))

if __name__=='__main__':unittest.main()
