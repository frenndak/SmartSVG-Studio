"""V34-130 / T-V34-17-09: conservative, user-facing Cricut PNG handoff.

This stdlib test checks the actual literal written by prepare_cricut_import,
without importing the optional cv2/NumPy/Pillow production pipeline.
It does NOT qualify Design Space, Windows, or physical cutting.
"""
from __future__ import annotations

import ast
from pathlib import Path
import unittest


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



if __name__ == "__main__":
    unittest.main()
