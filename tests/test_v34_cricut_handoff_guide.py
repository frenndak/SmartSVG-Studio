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


if __name__ == "__main__":
    unittest.main()
