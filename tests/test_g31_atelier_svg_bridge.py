"""G3.1 contract: the full-screen atelier launches the *existing* real G2.9
SVG review on explicit request, not a new validator or automatic ComfyUI job.
"""
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
UI=ROOT/"engine/web/js/smartsvg_express_atelier_preview.html"
PANEL=ROOT/"engine/web/js/smartsvg_cut_review_panel_g27.mjs"
MODEL=ROOT/"engine/web/js/smartsvg_cut_review_model_g27.mjs"
GRAMMAR=ROOT/"engine/web/js/smartsvg_svg_path_grammar_g29.mjs"

class AtelierSVGBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=UI.read_text(encoding="utf-8")

    def test_real_review_is_explicit_and_accessible(self):
        for field in ('id="realContourButton"','id="realContourHost"',
                      'id="realContourMount"','aria-expanded="false"',
                      'aria-controls="realContourHost"','id="realContourHost"'):
            self.assertIn(field,self.text)
        self.assertIn('aria-label="Contrôles réels de chemins SVG"',self.text)
        self.assertIn('"click",async()=>',self.text)
        self.assertIn('await import("./smartsvg_cut_review_panel_g27.mjs")',self.text)
        self.assertIn('createCutReviewPanel("atelier-g31")',self.text)
        self.assertIn('host.hidden=!host.hidden',self.text)
        self.assertIn('realPanelLoading=true',self.text)

    def test_only_touches_real_g27_g29_validators(self):
        for module in (PANEL,MODEL,GRAMMAR):
            self.assertTrue(module.exists(),str(module))
        self.assertIn("inspectCutSvg",MODEL.read_text())
        self.assertIn("inspectSvgPathGrammar",MODEL.read_text())
        self.assertIn("createCutReviewPanel",PANEL.read_text())
        self.assertIn("selectedSvg",PANEL.read_text())
        self.assertIn("await file.text()",PANEL.read_text())
        # No actual SVG data goes into the 12 fictitious button HTML.
        self.assertNotIn("queuePrompt",self.text)
        self.assertNotIn("fetch(",self.text)
        self.assertNotIn("<script src=",self.text)
        self.assertIn('["http:","https:"]',self.text)

    def test_svg_inspector_is_not_mislabeled_as_certified(self):
        self.assertIn("un vrai SVG de contours",self.text)
        self.assertIn("brouillon local à contrôler dans Design Space",self.text)
        self.assertIn("12 escargots ci-dessus restent une démonstration",self.text)
        self.assertIn("APERÇU NON CERTIFIÉ",self.text)

    def test_existing_cut_engine_regressions_in_node(self):
        node=shutil.which("node")
        if not node:
            self.skipTest("Node.js unavailable in this environment")
        files=[str(ROOT/"engine/tests/test_g27_cut_review.mjs"),
               str(ROOT/"engine/tests/test_g29_path_grammar.mjs")]
        result=subprocess.run([node,"--test",*files],cwd=ROOT,text=True,
                              capture_output=True,timeout=30)
        self.assertEqual(result.returncode,0,
                         (result.stdout+"\n"+result.stderr)[-2500:])

if __name__=="__main__":unittest.main()
