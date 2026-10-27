"""G3.3 pre-install UI: behavior checks without a Windows/ComfyUI runtime.

These tests run a synthetic event-driven DOM harness in Node.js; they are
not visual browser certification. GitHub Actions must not infer hardware QA.
"""
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"engine/web/js/smartsvg_express_atelier_preview.html"
EXPRESS=ROOT/"engine/web/js/smartsvg_express_start_g15.js"
HARNESS=ROOT/"tests/g33_ux_dom_smoke.mjs"

class ExpressUXPreinstallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page=HTML.read_text(encoding="utf-8")
        cls.express=EXPRESS.read_text(encoding="utf-8")

    def test_all_six_steps_have_descriptive_accessible_names(self):
        steps=re.findall(r'<button class="step" data-step="([^"]+)"[^>]+>',self.page)
        self.assertEqual(steps,["source","clean","subjects","retouch","cut","export"])
        for i,step in enumerate(steps,1):
            tag=re.search(r'<button class="step" data-step="'+step+r'"[^>]+>',self.page).group(0)
            self.assertIn('aria-label="Étape '+str(i)+' : ',tag)
        self.assertIn("scroll-snap-type:x proximity",self.page)
        self.assertIn(".workflow .step-label{display:block",self.page)
        self.assertIn('const steps=["source","clean","subjects","retouch","cut","export"]',self.page)

    def test_preview_link_never_misreports_noopener_popup_as_blocked(self):
        self.assertIn("workspacePreview.target='_blank'",self.express)
        self.assertIn("workspacePreview.rel='noopener noreferrer'",self.express)
        self.assertIn("workspacePreview.href=url.href",self.express)
        self.assertNotIn("window?.open?.(",self.express)

    def test_import_race_and_memory_guard_with_non_destructive_reset(self):
        for marker in ("const token=++fileToken", "token!==fileToken",
                       "token===fileToken", "20_000_000",
                       "Number.isSafeInteger(pixels)", "URL.revokeObjectURL(blob)",
                       "aucun sujet réel n'a encore été détecté", 
                       "selected=new Set(Array.from({length:SAMPLE_COUNT}"):
            with self.subTest(marker=marker):
                self.assertIn(marker,self.page)
        self.assertNotIn('$("resetSelect").addEventListener("click",resetDemo)',self.page)
        self.assertIn("SOURCE IMPORTÉE",self.page)

    def test_no_implicit_comfyui_run_and_explicit_live_module_limits(self):
        self.assertNotIn("queuePrompt",self.page)
        self.assertNotIn("XMLHttpRequest",self.page)
        self.assertIn('import("./smartsvg_project_panel_g22.mjs")',self.page)
        self.assertIn('import("./smartsvg_cut_review_panel_g27.mjs")',self.page)
        self.assertIn("Aucun traitement IA",self.page)

    def test_synthetic_dom_events_in_node(self):
        node=shutil.which("node")
        if not node:
            self.skipTest("Node.js unavailable")
        result=subprocess.run([node,"--test",str(HARNESS)],
                              cwd=ROOT,text=True,capture_output=True,timeout=30)
        self.assertEqual(result.returncode,0,
                         (result.stdout+"\n"+result.stderr)[-5000:])

if __name__=="__main__":
    unittest.main()
