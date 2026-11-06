"""V34-130 / T-V34-17-09: conservative, user-facing Cricut PNG handoff.

This stdlib test checks the actual literal written by prepare_cricut_import,
without importing the optional cv2/NumPy/Pillow production pipeline.
It does NOT qualify Design Space, Windows, or physical cutting.
"""
from __future__ import annotations

import ast
import hashlib
import math
import os
import shutil
import uuid
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET


SOURCE = (Path(__file__).resolve().parents[1]
          / "engine" / "smartsvg_cricut" / "direct_import_v218.py")


def handoff_text() -> str:
    module = ast.parse(SOURCE.read_text(encoding="utf-8"))
    function = next(node for node in module.body
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                    and node.name == "prepare_cricut_import")
    assignment = next(node for node in ast.walk(function)
                      if isinstance(node, ast.Assign)
                      and any(isinstance(target, ast.Name) and target.id == "readme"
                              for target in node.targets))
    guide = ast.literal_eval(assignment.value)
    if not isinstance(guide, str):
        raise AssertionError("The handoff must remain an explicit readable guide")
    return guide


class TestV34CricutHandoffGuide(unittest.TestCase):
    def test_print_then_cut_steps_are_ordered_and_not_mislabelled(self):
        guide = handoff_text()
        steps = [guide.index(f"{i}. ") for i in range(7)]
        self.assertEqual(steps, sorted(steps))
        for fragment in ("Flat Graphic", "IMPRIMER_PUIS_DECOUPER.png",
                         "NE PAS ajouter le SVG", "DEPUIS Design Space",
                         "taille en mm"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, guide)

    def test_a4_explore5_guidance_is_explicit_and_non_certifying(self):
        guide = handoff_text()
        for fragment in ("A4 / Explore 5", "paysage sur le tapis",
                         "haut a gauche", "marques de capteur",
                         "Design Space les ajoute", "175 x 240 mm",
                         "pas une garantie", "decoupe test"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, guide)

    def test_online_upload_and_preflight_limits_are_disclosed(self):
        guide = handoff_text()
        for fragment in ("connexion Internet requise", "televersement initial",
                         "SmartSVG fonctionne localement", "PARTIEL",
                         "A_VERIFIER", "RAPPORT_IMPORT_CRICUT_V21_8.json",
                         "ne prouve PAS"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, guide)



def handoff_status_classifier():
    """Execute the real dependency-free production helper, not a mock copy."""
    module = ast.parse(SOURCE.read_text(encoding="utf-8"))
    helper = next(node for node in module.body
                  if isinstance(node, ast.FunctionDef)
                  and node.name == "_classify_handoff_status")
    namespace = {}
    exec(compile(ast.Module(body=[helper], type_ignores=[]),
                 str(SOURCE), "exec"), namespace)
    return namespace["_classify_handoff_status"]


class TestV34HandoffBatchStatus(unittest.TestCase):
    def test_failed_requested_sheet_never_marks_whole_batch_ready(self):
        classify = handoff_status_classifier()
        result = dict(fichiers_prets=1, nombre_objets=1,
                      cartes_rectangulaires=0, planches_pretes=0,
                      planches=[{"statut": "A_VERIFIER"}])
        self.assertEqual(classify(result, pages_well_formed=True), "PARTIEL")
        result["planches"] = [{"statut": "PRET_POUR_IMPORT_LOCAL"},
                              {"statut": "A_VERIFIER"}]
        result["planches_pretes"] = 1
        self.assertEqual(classify(result, pages_well_formed=True), "PARTIEL")

    def test_complete_batches_and_no_sheet_request_stay_ready(self):
        classify = handoff_status_classifier()
        result = dict(fichiers_prets=1, nombre_objets=1,
                      cartes_rectangulaires=0, planches_pretes=0,
                      planches=[])
        self.assertEqual(classify(result, pages_well_formed=True),
                         "PRET_POUR_IMPORT_LOCAL")
        result["planches"] = [{"statut": "PRET_POUR_IMPORT_LOCAL"}]
        result["planches_pretes"] = 1
        self.assertEqual(classify(result, pages_well_formed=True),
                         "PRET_POUR_IMPORT_LOCAL")
        result["cartes_rectangulaires"] = 1
        self.assertEqual(classify(result, pages_well_formed=True),
                         "PRET_POUR_IMPORT_LOCAL_AVEC_CADRES")

    def test_invalid_page_collection_and_partial_items_fail_closed(self):
        classify = handoff_status_classifier()
        result = dict(fichiers_prets=1, nombre_objets=1,
                      cartes_rectangulaires=0, planches_pretes=0,
                      planches=[])
        self.assertEqual(classify(result, pages_well_formed=False), "PARTIEL")
        result["fichiers_prets"] = 0
        self.assertEqual(classify(result, pages_well_formed=False), "A_VERIFIER")
        result["planches"] = [{"statut": "PRET_POUR_IMPORT_LOCAL"}]
        result["planches_pretes"] = 1
        self.assertEqual(classify(result, pages_well_formed=True), "PARTIEL")

    def test_production_preflight_calls_the_classifier(self):
        module = ast.parse(SOURCE.read_text(encoding="utf-8"))
        function = next(node for node in module.body
                        if isinstance(node, ast.FunctionDef)
                        and node.name == "prepare_cricut_import")
        calls = [node for node in ast.walk(function)
                 if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name)
                 and node.func.id == "_classify_handoff_status"]
        self.assertEqual(len(calls), 1)
        self.assertTrue(any(keyword.arg == "pages_well_formed"
                            for keyword in calls[0].keywords))




def handoff_pages_selector():
    """Run the actual dependency-free production selector from its AST."""
    module = ast.parse(SOURCE.read_text(encoding="utf-8"))
    helper = next(node for node in module.body
                  if isinstance(node, ast.FunctionDef)
                  and node.name == "_select_handoff_pages")
    namespace = {}
    exec(compile(ast.Module(body=[helper], type_ignores=[]),
                 str(SOURCE), "exec"), namespace)
    return namespace["_select_handoff_pages"]


class TestV34MalformedManufacturedSheets(unittest.TestCase):
    def test_explicit_falsy_invalid_aliases_are_not_silently_absent(self):
        select = handoff_pages_selector()
        classify = handoff_status_classifier()
        for key in ("planches", "planches_cricut"):
            for invalid in (None, {}, "", False, 0):
                with self.subTest(key=key, invalid=repr(invalid)):
                    pages, well_formed = select({key: invalid})
                    self.assertEqual(pages, [])
                    self.assertFalse(well_formed)
                    result = dict(fichiers_prets=1, nombre_objets=1,
                                  cartes_rectangulaires=0, planches_pretes=0,
                                  planches=pages)
                    self.assertEqual(
                        classify(result, pages_well_formed=well_formed),
                        "PARTIEL")

    def test_valid_and_absent_collections_preserve_legacy_handoff(self):
        select = handoff_pages_selector()
        self.assertEqual(select({}), ([], True))
        self.assertEqual(select({"planches": []}), ([], True))
        sheets = [{"statut": "CREATION_OK", "fichier": "/example.png"}]
        self.assertEqual(select({"planches_cricut": sheets}), (sheets, True))
        # A declared empty alias contradicts a nonempty manufactured batch.
        self.assertEqual(select({"planches": [], "planches_cricut": sheets}),
                         ([], False))
        self.assertEqual(select({"planches": sheets, "planches_cricut": []}),
                         ([], False))
        self.assertEqual(select({"planches": sheets, "planches_cricut": sheets}),
                         (sheets, True))
        # A malformed second alias must not be ignored behind a valid first.
        self.assertEqual(select({"planches": sheets, "planches_cricut": {}}),
                         ([], False))

    def test_conflicting_manufactured_aliases_cannot_claim_ready(self):
        select = handoff_pages_selector()
        classify = handoff_status_classifier()
        sheet = {"statut": "CREATION_OK", "fichier": "/a.png"}
        cases = [
            {"planches": [], "planches_cricut": [sheet]},
            {"planches": [sheet], "planches_cricut": []},
            {"planches": [sheet], "planches_cricut":
             [{"statut": "CREATION_OK", "fichier": "/other.png"}]},
            {"planches": [sheet], "planches_cricut":
             [{"statut": "A_VERIFIER", "fichier": "/a.png"}]},
            {"planches": [sheet], "planches_cricut": [None]},
        ]
        for report in cases:
            with self.subTest(report=report):
                pages, well_formed = select(report)
                self.assertEqual((pages, well_formed), ([], False))
                batch = dict(fichiers_prets=1, nombre_objets=1,
                             cartes_rectangulaires=0, planches_pretes=0,
                             planches=pages)
                self.assertEqual(
                    classify(batch, pages_well_formed=well_formed), "PARTIEL")
        self.assertEqual(select({"planches": [sheet],
                                 "planches_cricut": [dict(sheet)]}),
                         ([sheet], True))

    def test_real_preflight_uses_checked_selector_for_batch_status(self):
        module = ast.parse(SOURCE.read_text(encoding="utf-8"))
        function = next(node for node in module.body
                        if isinstance(node, ast.FunctionDef)
                        and node.name == "prepare_cricut_import")
        selector_calls = [node for node in ast.walk(function)
                          if isinstance(node, ast.Call)
                          and isinstance(node.func, ast.Name)
                          and node.func.id == "_select_handoff_pages"]
        self.assertEqual(len(selector_calls), 1)
        classifier = next(node for node in ast.walk(function)
                          if isinstance(node, ast.Call)
                          and isinstance(node.func, ast.Name)
                          and node.func.id == "_classify_handoff_status")
        self.assertTrue(any(keyword.arg == "pages_well_formed"
                            and isinstance(keyword.value, ast.Name)
                            and keyword.value.id == "pages_well_formed"
                            for keyword in classifier.keywords))


class TestV34PhysicalWidthFailClosed(unittest.TestCase):
    """Exercise real dependency-free production helpers without cv2/Pillow."""

    @staticmethod
    def helpers():
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        names = {"_positive_mm", "_svg_preflight"}
        nodes = [node for node in tree.body
                 if isinstance(node, ast.FunctionDef) and node.name in names]
        if {node.name for node in nodes} != names:
            raise AssertionError("Missing production physical-width helpers")
        class ImportAuditError(ValueError):
            pass
        namespace = dict(math=math, Path=Path, ET=ET,
                         ImportAuditError=ImportAuditError)
        exec(compile(ast.Module(body=nodes, type_ignores=[]),
                     str(SOURCE), "exec"), namespace)
        return namespace

    def test_nonfinite_and_nonpositive_dimensions_are_rejected(self):
        ns = self.helpers()
        validate = ns["_positive_mm"]
        for value in ("nan", "NaN", "inf", "-inf", "1e309",
                      "0", "-1", "not-a-number", None):
            with self.subTest(value=value):
                with self.assertRaises(ns["ImportAuditError"]):
                    validate(value, "Largeur physique")
        self.assertEqual(validate(25.4, "Largeur physique"), 25.4)
        self.assertEqual(validate("25.4", "Largeur physique"), 25.4)

    def test_boolean_physical_width_is_not_numeric(self):
        ns = self.helpers()
        validate = ns["_positive_mm"]
        for value in (True, False):
            with self.subTest(value=value):
                with self.assertRaises(ns["ImportAuditError"]):
                    validate(value, "Largeur physique")

    def test_svg_width_nan_cannot_be_reported_ok_local(self):
        ns = self.helpers()
        inspect = ns["_svg_preflight"]
        with tempfile.TemporaryDirectory() as td:
            project = Path(td)
            svg = project / "contour.svg"
            for value in ("NaN", "Infinity", "-1", "0", "1e309"):
                with self.subTest(width=value):
                    svg.write_text(
                        '<svg xmlns="http://www.w3.org/2000/svg" '
                        f'width="{value}mm"><path d="M0 0 L1 1"/></svg>',
                        encoding="utf-8")
                    self.assertEqual(
                        inspect(project / "unused.png", str(svg),
                                project, 25.4)["statut"], "A_VERIFIER")
            svg.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg" '
                'width="25.4mm"><path d="M0 0 L1 1"/></svg>',
                encoding="utf-8")
            result = inspect(project / "unused.png", str(svg), project, 25.4)
            self.assertEqual(result["statut"], "OK_LOCAL", result)

    def test_png_handoff_validates_physical_width_before_copy(self):
        tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
        function = next(node for node in tree.body
                        if isinstance(node, ast.FunctionDef)
                        and node.name == "prepare_cricut_import")
        calls = [node for node in ast.walk(function)
                 if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name)
                 and node.func.id == "_positive_mm"]
        self.assertEqual(len(calls), 1)
        self.assertTrue(any(isinstance(arg, ast.Constant)
                            and arg.value == "Largeur physique"
                            for arg in calls[0].args))


def atomic_png_copy_helpers():
    """Execute the actual production helpers without optional image libraries."""
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    names = {"_sha256_file", "_copy_atomic"}
    nodes = [node for node in tree.body
             if isinstance(node, ast.FunctionDef) and node.name in names]
    if {node.name for node in nodes} != names:
        raise AssertionError("Missing production atomic PNG helpers")

    class ImportAuditError(ValueError):
        pass

    namespace = dict(hashlib=hashlib, os=os, shutil=shutil, uuid=uuid,
                     Path=Path, ImportAuditError=ImportAuditError)
    exec(compile(ast.Module(body=nodes, type_ignores=[]),
                 str(SOURCE), "exec"), namespace)
    return namespace


class TestV34AtomicPngPublication(unittest.TestCase):
    def test_normal_publish_is_complete_and_idempotent(self):
        helpers = atomic_png_copy_helpers()
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "source.png"
            dest = Path(td) / "destination.png"
            src.write_bytes(b"synthetic complete PNG fixture")
            helpers["_copy_atomic"](src, dest)
            self.assertEqual(dest.read_bytes(), src.read_bytes())
            helpers["_copy_atomic"](src, dest)
            self.assertEqual(dest.read_bytes(), src.read_bytes())
            self.assertEqual(list(Path(td).glob(".tmp_*")), [])

    @unittest.skipIf(os.name == "nt", "POSIX no-hardlink fallback only")
    def test_no_hardlinks_fail_closed_before_partial_png_is_visible(self):
        # The old O_EXCL streaming fallback published the destination after
        # only a few bytes had been copied; a concurrent reader could consume
        # a truncated image. POSIX rename would overwrite a concurrent file.
        helpers = atomic_png_copy_helpers()
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "source.png"
            dest = Path(td) / "destination.png"
            src.write_bytes(b"synthetic complete PNG fixture")
            with patch.object(os, "link", side_effect=OSError("no hardlinks")):
                with patch.object(shutil, "copyfileobj",
                                  side_effect=AssertionError("partial publish")):
                    with self.assertRaisesRegex(
                            helpers["ImportAuditError"],
                            "Publication atomique impossible"):
                        helpers["_copy_atomic"](src, dest)
            self.assertFalse(dest.exists())
            self.assertEqual(src.read_bytes(),
                             b"synthetic complete PNG fixture")
            self.assertEqual(list(Path(td).glob(".tmp_*")), [])


def manufactured_sheet_count_helper():
    """Execute the production validator from its exact AST, without cv2."""
    module = ast.parse(SOURCE.read_text(encoding="utf-8"))
    helper = next(node for node in module.body
                  if isinstance(node, ast.FunctionDef)
                  and node.name == "_sheet_expected_count")
    class ImportAuditError(ValueError):
        pass
    namespace = {"ImportAuditError": ImportAuditError}
    exec(compile(ast.Module(body=[helper], type_ignores=[]),
                 str(SOURCE), "exec"), namespace)
    return namespace["_sheet_expected_count"], ImportAuditError


class TestV34ManufacturedSheetCounts(unittest.TestCase):
    def test_legacy_valid_counts_are_preserved(self):
        count, _ = manufactured_sheet_count_helper()
        for page, expected in [
            ({"elements_source": [0]}, 1),
            ({"elements_source": [0, 1]}, 2),
            ({"objets": 2}, 2),
            ({"objets": "02"}, 2),
            ({"elements_source": [], "objets": 1}, 1),
        ]:
            with self.subTest(page=page):
                self.assertEqual(count(page), expected)

    def test_malformed_elements_never_pass_by_length_or_raise_typeerror(self):
        count, error = manufactured_sheet_count_helper()
        for invalid in (True, False, None, {"one": 1}, "one", 1.5):
            with self.subTest(value=repr(invalid)):
                with self.assertRaises(error):
                    count({"elements_source": invalid, "objets": 1})

    def test_malformed_fallback_count_fails_closed(self):
        count, error = manufactured_sheet_count_helper()
        for invalid in (True, False, None, 1.5, "1.5", "9" * 100):
            with self.subTest(value=repr(invalid)):
                with self.assertRaises(error):
                    count({"objets": invalid})

    def test_real_sheet_preflight_uses_validated_count(self):
        module = ast.parse(SOURCE.read_text(encoding="utf-8"))
        function = next(node for node in module.body
                        if isinstance(node, ast.FunctionDef)
                        and node.name == "prepare_cricut_import")
        calls = [node for node in ast.walk(function)
                 if isinstance(node, ast.Call)
                 and isinstance(node.func, ast.Name)
                 and node.func.id == "_sheet_expected_count"]
        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
