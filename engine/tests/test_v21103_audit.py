"""Fresh-archive audit regressions: HD provenance and honest physical-size QA."""
import json
import importlib, sys, types
import tempfile
import unittest
from pathlib import Path
import numpy as np
import torch
from PIL import Image, ImageDraw
ROOT=Path(__file__).resolve().parents[1]
if 'sv21103test' not in sys.modules:
    pkg=types.ModuleType('sv21103test');pkg.__path__=[str(ROOT)];sys.modules[pkg.__name__]=pkg
hd=importlib.import_module('sv21103test.smartsvg_quality.auto_hd')
node=importlib.import_module('sv21103test.node_v2110')
automatic_hd, FOLDER = hd.automatic_hd, hd.FOLDER
SmartSVGUnifiedEditorV2110=node.SmartSVGUnifiedEditorV2110

class GlobalFreshArchiveAudit(unittest.TestCase):
    def _img(self, folder):
        p=Path(folder)/'art.png';im=Image.new('RGBA',(90,90),(0,0,0,0))
        ImageDraw.Draw(im).ellipse((11,15,75,79),fill=(180,40,55,255));im.save(p)
        return p

    def test_hd_is_reusable_when_inputs_and_bytes_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            src=self._img(d);payload={'dossier':d,'objets':[{'png':str(src)}]}
            a=automatic_hd(payload,300)
            self.assertEqual((a['produits'],a['reutilises'],a['statut']),(1,0,'complete'))
            out=Path(a['fichiers'][0]['fichier_hd']);original=out.read_bytes()
            b=automatic_hd(payload,300)
            self.assertEqual((b['produits'],b['reutilises'],b['statut']),(0,1,'complete'))
            self.assertEqual(out.read_bytes(),original)
            self.assertTrue(out.with_name(out.stem+'.provenance.json').is_file())

    def test_no_reuse_of_changed_original(self):
        with tempfile.TemporaryDirectory() as d:
            src=self._img(d);payload={'dossier':d,'objets':[{'png':str(src)}]}
            a=automatic_hd(payload,300);out=Path(a['fichiers'][0]['fichier_hd']);digest=out.read_bytes()
            Image.new('RGBA',(90,90),(1,2,3,255)).save(src)
            b=automatic_hd(payload,300)
            self.assertEqual((b['produits'],b['reutilises']), (0,0))
            self.assertEqual(b['statut'],'ignore');self.assertEqual(out.read_bytes(),digest)

    def test_no_reuse_of_tampered_hd(self):
        with tempfile.TemporaryDirectory() as d:
            src=self._img(d);payload={'dossier':d,'objets':[{'png':str(src)}]}
            a=automatic_hd(payload,300);out=Path(a['fichiers'][0]['fichier_hd'])
            out.write_bytes(b'altered-file')
            b=automatic_hd(payload,300)
            self.assertEqual(b['reutilises'],0);self.assertEqual(out.read_bytes(),b'altered-file')

    def test_old_HD_without_provenance_never_assumed_valid(self):
        with tempfile.TemporaryDirectory() as d:
            src=self._img(d);folder=Path(d)/FOLDER;folder.mkdir()
            old=folder/'sujet_001_HD.png';old.write_bytes(b'user-created-file')
            r=automatic_hd({'dossier':d,'objets':[{'png':str(src)}]},300)
            self.assertEqual(r['reutilises'],0);self.assertEqual(old.read_bytes(),b'user-created-file')

    def test_editor_admits_qa_scale_is_hypothetical(self):
        with tempfile.TemporaryDirectory():
            image=torch.ones((1,40,40,3),dtype=torch.float32)
            mask=torch.zeros((1,40,40));mask[0,7:25,7:25]=1.0
            r=SmartSVGUnifiedEditorV2110().run(image,'',mask)
            data=json.loads(r['result'][2])
            self.assertEqual(data['largeur_qa_hypothese_mm'],40.0)
            self.assertFalse(data['largeur_export_reelle_mm_connue'])
            self.assertIn('hypothétiques',r['ui']['text'][0])

if __name__=='__main__':unittest.main()
