#!/usr/bin/env python3
"""CPU-only, synthetic functional smoke checks for the LIVE SmartSVG engine.

No ComfyUI, torch, model weights, user files, GPU, Design Space, or hardware.
These tests intentionally exercise production code in engine/, not a copy of
the frozen V21.15.2 ZIP. The historical archive is verified separately.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "engine"))

import cv2  # noqa: E402
import numpy as np  # noqa: E402
from smartsvg_quality.white_sheet_v21152 import SheetUncertain, segment_white_grid  # noqa: E402


class LiveWhiteSheetSmoke(unittest.TestCase):
    @staticmethod
    def twelve_subjects() -> np.ndarray:
        canvas = np.full((360, 480, 3), 255, dtype=np.uint8)
        for row in range(3):
            for col in range(4):
                x, y = col * 120 + 60, row * 120 + 60
                cv2.circle(canvas, (x, y), 34, (50, 110, 190), -1)
                cv2.circle(canvas, (x, y), 34, (0, 0, 0), 2)
        return canvas

    def test_twelve_subjects_are_independent(self) -> None:
        result = segment_white_grid(self.twelve_subjects(), cols=4, rows=3)
        self.assertEqual(result.masks.shape, (12, 360, 480))
        self.assertEqual(len(result.diagnostics), 12)
        for index, mask in enumerate(result.masks):
            row, col = divmod(index, 4)
            self.assertEqual(int(mask[row * 120 + 60, col * 120 + 60]), 1)
            self.assertEqual(cv2.connectedComponents((mask > 0).astype(np.uint8), 8)[0] - 1, 1)

    def test_unknown_sheet_must_not_invent_silhouettes(self) -> None:
        with self.assertRaises(SheetUncertain):
            segment_white_grid(np.full((360, 480, 3), 255, dtype=np.uint8), cols=4, rows=3)

    def test_rectangle_is_not_silently_a_sticker(self) -> None:
        canvas = np.full((360, 480, 3), 255, dtype=np.uint8)
        for row in range(3):
            for col in range(4):
                cv2.rectangle(canvas, (col * 120 + 20, row * 120 + 20),
                              (col * 120 + 99, row * 120 + 99), (0, 120, 200), -1)
        with self.assertRaises(SheetUncertain):
            segment_white_grid(canvas, cols=4, rows=3)

    def test_floating_point_input_is_rejected(self) -> None:
        with self.assertRaises(SheetUncertain):
            segment_white_grid(self.twelve_subjects().astype(np.float32), cols=4, rows=3)


class LiveSVGPublicationSmoke(unittest.TestCase):
    def test_real_editable_vector_export_keeps_source_and_complete_files(self):
        from smartsvg_vector.layers_v2113 import vectorize_flat_art, save_svg
        from smartsvg_vector.svg_publication import save_svg as publication
        from inspect_svg_contracts import inspect_svg
        self.assertIs(save_svg, publication, 'historical node import must use the secured writer')
        image = np.full((80, 120, 3), 255, dtype=np.uint8)
        mask = np.zeros((80, 120), dtype=np.float32)
        image[10:70, 10:60] = (220, 40, 60)
        image[10:70, 60:110] = (40, 80, 220)
        mask[10:70, 10:110] = 1
        before = (image.tobytes(), mask.tobytes())
        payload, _, audit = vectorize_flat_art(image, mask, colors=2, width_mm=45)
        self.assertEqual(audit['calques_couleur'], 2)
        self.assertFalse(audit['svg_decoupe_cricut_certifie'])
        with tempfile.TemporaryDirectory() as folder:
            first = Path(save_svg(payload, folder))
            second = Path(save_svg(payload, folder))
            self.assertNotEqual(first, second)
            self.assertEqual(first.read_bytes(), payload)
            self.assertEqual(second.read_bytes(), payload)
            contract = inspect_svg(first, profile='editable')
            self.assertEqual(contract['width_mm'], 45)
            self.assertGreaterEqual(contract['vector_elements'], 2)
            self.assertFalse(contract['design_space_import_verified'])
            self.assertEqual(list(Path(folder).glob('.smartsvg_svg_*')), [])
        self.assertEqual((image.tobytes(), mask.tobytes()), before)


class LiveBasicCutGrammarSmoke(unittest.TestCase):
    def test_real_export_quality_gate_rejects_incomplete_curves_without_changes(self):
        import json
        from PIL import Image, ImageDraw
        from smartsvg_governance.artifact_qa import audit_project
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            png=root/'sticker.png'
            image=Image.new('RGBA',(120,120))
            ImageDraw.Draw(image).ellipse((10,10,110,110),fill=(230,50,60,255))
            image.save(png,dpi=(300,300))
            svg=root/'cut.svg'
            report=root/'report.json'
            report.write_text(json.dumps({'objets':[{
                'png':str(png),'svg_contour':str(svg),
                'largeur_finale_avec_marge_mm':10.16,
            }]}),encoding='utf-8')
            cases=[('M0 0 C1 2 3 4 Z','BLOCKED'),
                   ('M0 0 A2 2 0 2 0 10 10 Z','BLOCKED'),
                   ('M1 1 L9 1 L9 9 Z','REVIEW_REQUIRED'),
                   ('M1 1 C1 5 5 9 9 1 Z','REVIEW_REQUIRED')]
            for path,status in cases:
                with self.subTest(path=path):
                    svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" '
                        'width="10.16mm" height="10.16mm" viewBox="0 0 10.16 10.16">'
                        '<path d="'+path+'"/></svg>',encoding='utf-8')
                    before={p.name:p.read_bytes() for p in root.iterdir()}
                    decision=audit_project(report)
                    self.assertEqual(decision['status'],status)
                    if status=='BLOCKED':
                        self.assertIn('FICHIER_NON_VERIFIABLE',decision['blocking_codes'])
                    self.assertEqual(decision['external_validation']['physical_cut'],'NOT_TESTED')
                    self.assertEqual(decision['external_validation']['design_space_import'],'NOT_TESTED')
                    self.assertEqual({p.name:p.read_bytes() for p in root.iterdir()},before)


class LiveProductionExportPipelineSmoke(unittest.TestCase):
    @staticmethod
    def production_module():
        # Load the real relative-import package without executing the plugin's
        # ComfyUI __init__. No pipeline function or dependency is mocked.
        import importlib
        import types
        package='smartsvg_live_production_contracts'
        if package not in sys.modules:
            module=types.ModuleType(package)
            module.__path__=[str(ROOT/'engine')]
            sys.modules[package]=module
        return importlib.import_module(package+'.production_v211')

    @staticmethod
    def artwork():
        image=np.full((100,140,3),255,np.uint8)
        mask=np.zeros((100,140),np.uint8)
        cv2.circle(mask,(70,50),30,1,-1)
        x=np.indices(mask.shape)[1]
        image[(mask>0)&(x<70)]=(220,40,80)
        image[(mask>0)&(x>=70)]=(40,80,220)
        return image,mask

    def test_real_production_print_contour_and_color_outputs_keep_contracts_distinct(self):
        import hashlib
        import xml.etree.ElementTree as ET
        from PIL import Image
        from inspect_svg_contracts import inspect_svg
        from smartsvg_governance.artifact_qa import audit_project
        from smartsvg_cricut.direct_import_v218 import prepare_cricut_import
        from smartsvg_cricut.delivery_v21122 import delivery_manifest
        from smartsvg_vector.layers_v2113 import vectorize_flat_art, save_svg
        production=self.production_module()
        # Fixture acceptance values established independently of exporter output:
        # 25 mm content, 1.2 mm halo and 4 safety pixels per edge. At 300 ppi:
        # 295 content pixels + 2*(14+4) = 331; at 450: 443 + 2*(21+4) = 493.
        expected_sizes={300:(331,28.0246666667),450:(493,27.8275555556)}
        for dpi in (300,450):
            with self.subTest(dpi=dpi),tempfile.TemporaryDirectory() as folder:
                image,mask=self.artwork()
                source=(image.tobytes(),mask.tobytes())
                report,_=production.run_v211(image,folder,profile='affiche',
                    width_mm=25,dpi=dpi,masks=mask)
                root=Path(report['dossier'])
                self.assertEqual(len(report['objets']),1)
                item=report['objets'][0]
                png=Path(item['fichier_png_cricut'])
                contour=Path(item['fichier_svg_contour'])
                # These are actual files emitted by the historical producer.
                png_bytes,contour_bytes=png.read_bytes(),contour.read_bytes()
                geometry=inspect_svg(contour,profile='cut')
                expected_pixels,expected_mm=expected_sizes[dpi]
                self.assertAlmostEqual(geometry['width_mm'],expected_mm,delta=0.001)
                self.assertAlmostEqual(geometry['height_mm'],expected_mm,delta=0.001)
                with Image.open(png) as printed:
                    self.assertEqual(printed.size,(expected_pixels,expected_pixels))
                    self.assertEqual(printed.mode,'RGBA')
                    self.assertAlmostEqual(printed.info['dpi'][0],dpi,delta=0.1)
                    self.assertAlmostEqual(printed.info['dpi'][1],dpi,delta=0.1)
                    self.assertAlmostEqual(printed.width*25.4/dpi,geometry['width_mm'],delta=0.01)
                    self.assertAlmostEqual(printed.height*25.4/dpi,geometry['height_mm'],delta=0.01)
                before={p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()}
                audit=audit_project(root/'RAPPORT_V21_1.json')
                self.assertEqual(audit['status'],'REVIEW_REQUIRED')
                self.assertEqual(audit['blocking_codes'],[])
                self.assertEqual({p.relative_to(root):p.read_bytes() for p in root.rglob('*') if p.is_file()},before)
                handoff=prepare_cricut_import(report,dpi)
                self.assertEqual(handoff['statut'],'PRET_POUR_IMPORT_LOCAL')
                transferred=Path(handoff['objets'][0]['fichier_import'])
                self.assertNotEqual(transferred,png)
                self.assertEqual(transferred.read_bytes(),png_bytes)
                self.assertTrue(handoff['ne_pas_ajouter_svg_contour'])
                report['import_direct_cricut_v218']=handoff
                delivery=delivery_manifest(report)
                self.assertEqual(delivery['statut'],'CONTROLE_LOCAL_COMPLET_A_REVISER')
                for role,original in [('impression',png_bytes),('png_fabrication',png_bytes),
                                      ('svg_contour',contour_bytes)]:
                    record=delivery['objets'][0]['fichiers'][role]
                    self.assertEqual(record['sha256'],hashlib.sha256(original).hexdigest())
                    self.assertEqual(record['octets'],len(original))
                payload,_,vector=vectorize_flat_art(image,mask,colors=2,width_mm=25)
                # One existing vectorizer supports two separate intended uses.
                # Separate files are not proof of Design Space layer assignment.
                color_cut=Path(save_svg(payload,str(root),prefix='COULEURS_A_DECOUPER'))
                editable=Path(save_svg(payload,str(root),prefix='EDITION_COULEURS'))
                self.assertEqual(len({png,contour,color_cut,editable}),4)
                self.assertEqual(inspect_svg(color_cut,profile='cut')['width_mm'],25)
                self.assertEqual(inspect_svg(editable,profile='editable')['width_mm'],25)
                self.assertEqual(vector['calques_couleur'],2)
                groups=[node for node in ET.fromstring(payload).iter() if node.tag.endswith('}g')]
                self.assertEqual(len(groups),2)
                self.assertEqual(len({group.get('id') for group in groups}),2)
                self.assertEqual(len({group.get('fill') for group in groups}),2)
                self.assertFalse(vector['svg_decoupe_cricut_certifie'])
                self.assertFalse(delivery['certification_cricut'])
                self.assertFalse(delivery['validation_physique'])
                self.assertEqual(audit['external_validation']['design_space_import'],'NOT_TESTED')
                self.assertEqual((png.read_bytes(),contour.read_bytes()),(png_bytes,contour_bytes))
                self.assertEqual((image.tobytes(),mask.tobytes()),source)

    def test_changed_manufactured_png_cannot_reuse_prior_successful_delivery(self):
        from PIL import Image
        from smartsvg_cricut.direct_import_v218 import prepare_cricut_import
        from smartsvg_cricut.delivery_v21122 import delivery_manifest
        with tempfile.TemporaryDirectory() as folder:
            image,mask=self.artwork()
            report,_=self.production_module().run_v211(image,folder,profile='affiche',
                width_mm=25,dpi=300,masks=mask)
            item=report['objets'][0]
            png=Path(item['fichier_png_cricut'])
            contour=Path(item['fichier_svg_contour'])
            contour_bytes=contour.read_bytes()
            handoff=prepare_cricut_import(report,300)
            self.assertEqual(handoff['statut'],'PRET_POUR_IMPORT_LOCAL')
            destination=Path(handoff['objets'][0]['fichier_import'])
            previous=destination.read_bytes()
            # Inject another valid raster revision after successful handoff.
            with Image.open(png) as original:
                changed=original.copy()
            changed.putpixel((changed.width//2,changed.height//2),(1,2,3,255))
            changed.save(png,dpi=(300,300))
            modified=png.read_bytes()
            self.assertNotEqual(modified,previous)
            report['import_direct_cricut_v218']=handoff
            stale=delivery_manifest(report)
            self.assertEqual(stale['statut'],'REVISIONS_NECESSAIRES')
            self.assertIn('PNG_IMPRESSION_DIFFERENT_DU_PNG_FABRICATION',
                stale['objets'][0]['avertissements'])
            retried=prepare_cricut_import(report,300)
            self.assertEqual(retried['statut'],'A_VERIFIER')
            self.assertEqual(retried['fichiers_prets'],0)
            self.assertEqual(destination.read_bytes(),previous)
            self.assertEqual(png.read_bytes(),modified)
            self.assertEqual(contour.read_bytes(),contour_bytes)


class LivePNGDensitySmoke(unittest.TestCase):
    @staticmethod
    def sticker(folder, name, dpi):
        from PIL import Image, ImageDraw
        path = Path(folder)/name
        image = Image.new('RGBA', (120, 120))
        ImageDraw.Draw(image).ellipse((10, 10, 110, 110), fill=(230, 50, 60, 255))
        image.save(path, **({'dpi': dpi} if dpi is not None else {}))
        return path

    def test_matching_density_and_legacy_absence_preserve_png_bytes(self):
        from smartsvg_cricut.direct_import_v218 import prepare_cricut_import
        for axes in [(300, 300), (450, 450), None]:
            with self.subTest(axes=axes), tempfile.TemporaryDirectory() as folder:
                source = self.sticker(folder, 'source.png', axes)
                original = source.read_bytes()
                dpi = axes[0] if axes else 300
                result = prepare_cricut_import({'dossier': folder, 'objets': [{'png': str(source)}]}, dpi)
                record = result['objets'][0]
                self.assertEqual(result['statut'], 'PRET_POUR_IMPORT_LOCAL')
                self.assertEqual(Path(record['fichier_import']).read_bytes(), original)
                self.assertEqual(source.read_bytes(), original)
                if axes:
                    self.assertTrue(all(abs(value-dpi) <= 0.1 for value in record['densite_metadata_axes_ppp']))
                else:
                    self.assertIn('absentes', record['densite_avertissement'])

    def test_contradictory_or_anisotropic_png_is_not_copied_over_previous_export(self):
        from smartsvg_cricut.direct_import_v218 import prepare_cricut_import, FOLDER
        for axes in [(450, 450), (300, 450), (450, 300)]:
            with self.subTest(axes=axes), tempfile.TemporaryDirectory() as folder:
                source = self.sticker(folder, 'source.png', (300, 300))
                previous = source.read_bytes()
                target_folder = Path(folder)/FOLDER;target_folder.mkdir()
                target = target_folder/'STICKER_001_IMPRIMER_PUIS_DECOUPER.png'
                target.write_bytes(previous)
                source = self.sticker(folder, 'source.png', axes)
                original = source.read_bytes()
                result = prepare_cricut_import({'dossier': folder, 'objets': [{
                    'png': str(source), 'largeur_finale_avec_marge_mm': 120*25.4/300}]}, 300)
                self.assertEqual(result['fichiers_prets'], 0)
                self.assertEqual(result['statut'], 'A_VERIFIER')
                self.assertIn('Densite PNG incoherente', result['objets'][0]['raison'])
                self.assertNotIn('fichier_import', result['objets'][0])
                self.assertEqual(target.read_bytes(), previous)
                self.assertEqual(source.read_bytes(), original)

    def test_sheet_density_conflict_cannot_promote_batch_to_ready(self):
        from smartsvg_cricut.direct_import_v218 import prepare_cricut_import, FOLDER
        with tempfile.TemporaryDirectory() as folder:
            source = self.sticker(folder, 'source.png', (300, 300))
            sheet = self.sticker(folder, 'sheet.png', (300, 450))
            original = sheet.read_bytes()
            result = prepare_cricut_import({'dossier': folder, 'objets': [{'png': str(source)}],
                'planches': [{'statut': 'CREATION_OK', 'fichier': str(sheet), 'objets': 1}]}, 300)
            self.assertEqual(result['fichiers_prets'], 1)
            self.assertEqual(result['planches_pretes'], 0)
            self.assertEqual(result['statut'], 'PARTIEL')
            self.assertIn('Densite PNG incoherente', result['planches'][0]['raison'])
            self.assertFalse((Path(folder)/FOLDER/'PLANCHE_01_IMPRIMER_PUIS_DECOUPER.png').exists())
            self.assertEqual(sheet.read_bytes(), original)


if __name__ == "__main__":
    unittest.main(verbosity=2)
