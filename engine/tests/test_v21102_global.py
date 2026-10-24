"""Cross-functional tests introduced after the global V21.10.1 audit."""
import unittest, tempfile, json
from pathlib import Path
from PIL import Image
from smartsvg_cricut.direct_import_v218 import prepare_cricut_import, REPORT, FOLDER

class GlobalReview(unittest.TestCase):
    def test_opaque_rgba_must_never_be_claimed_as_contour_cut(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"image.png";Image.new("RGBA",(120,100),(10,20,30,255)).save(p)
            r=prepare_cricut_import({"dossier":d,"objets":[{"png":str(p)}]},300)
            item=r["objets"][0]
            self.assertEqual(item["type_decoupe_presumee"],"CADRE_RECTANGULAIRE_SANS_DETOURAGE")
            self.assertEqual(item["statut"],"PRET_POUR_IMPORT_LOCAL_CADRE")
            self.assertEqual(r["cartes_rectangulaires"],1)
    def test_filled_rectangle_with_transparent_padding_is_still_a_rectangle(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"padded_rectangle.png"
            im=Image.new("RGBA",(150,130),(0,0,0,0))
            from PIL import ImageDraw
            ImageDraw.Draw(im).rectangle((15,20,120,90),fill=(190,40,20,255));im.save(p)
            r=prepare_cricut_import({"dossier":d,"objets":[{"png":str(p)}]},300)
            self.assertTrue(r["objets"][0]["alpha_rectangle_plein"])
            self.assertEqual(r["objets"][0]["statut"],"PRET_POUR_IMPORT_LOCAL_CADRE")
    def test_non_rectangular_contour_remains_a_sticker(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"circle.png"
            im=Image.new("RGBA",(150,130),(0,0,0,0))
            from PIL import ImageDraw
            ImageDraw.Draw(im).ellipse((15,20,115,120),fill=(190,40,20,255));im.save(p)
            r=prepare_cricut_import({"dossier":d,"objets":[{"png":str(p)}]},300)
            self.assertFalse(r["objets"][0]["alpha_rectangle_plein"])
            self.assertEqual(r["objets"][0]["statut"],"PRET_POUR_IMPORT_LOCAL")

    def test_project_report_must_not_overwrite_user_content(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"image.png";Image.new("RGBA",(90,90),(10,20,30,255)).save(p)
            folder=Path(d)/FOLDER;folder.mkdir()
            note=folder/"LIRE_AVANT_IMPORT.txt";note.write_text("NE PAS MODIFIER",encoding="utf8")
            r=prepare_cricut_import({"dossier":d,"objets":[{"png":str(p)}]},300)
            self.assertEqual(note.read_text(encoding="utf8"),"NE PAS MODIFIER")
            self.assertEqual(r["statut"],"A_VERIFIER")
            self.assertEqual((folder/"STICKER_001_IMPRIMER_PUIS_DECOUPER.png").read_bytes(),p.read_bytes())
    def test_same_project_repetition_keeps_all_bytes(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"image.png";Image.new("RGBA",(90,90),(10,20,30,255)).save(p)
            report={"dossier":d,"objets":[{"png":str(p)}]}
            a=prepare_cricut_import(report,300)
            b=prepare_cricut_import(report,300)
            self.assertEqual(a["statut"],b["statut"])
            self.assertEqual(b["statut"],"PRET_POUR_IMPORT_LOCAL_AVEC_CADRES")
            self.assertEqual(json.loads((Path(d)/FOLDER/REPORT).read_text(encoding="utf8"))["statut"],b["statut"])

if __name__=='__main__':unittest.main()
