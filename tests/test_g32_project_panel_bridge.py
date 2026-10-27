"""G3.2: opt-in bridge from full-screen Express to existing managed projects.

Tests do not start ComfyUI or write a project; G2.2's own Node and Python
regression suites remain the authority for I/O, SHA safety and recovery.
"""
from pathlib import Path
import re
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"engine/web/js/smartsvg_express_atelier_preview.html"
PANEL=ROOT/"engine/web/js/smartsvg_project_panel_g22.mjs"
BACKEND=ROOT/"engine/smartsvg_core/project_workspace_g22.py"

class ProjectPanelBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page=HTML.read_text(encoding="utf-8")
        cls.panel=PANEL.read_text(encoding="utf-8")
        cls.backend=BACKEND.read_text(encoding="utf-8")

    def test_click_only_and_backend_remains_existing_component(self):
        for marker in ('id="realProjectButton"','id="realProjectHost"',
                       'id="realProjectMount"','aria-controls="realProjectHost"',
                       'aria-expanded="false"',
                       'import("./smartsvg_project_panel_g22.mjs")',
                       'import("../../scripts/api.js")',
                       'createProjectPanel(api,settings,"atelier-g32")',
                       'realProjectLoading=true',
                       'host.hidden=!host.hidden'):
            with self.subTest(marker=marker):
                self.assertIn(marker,self.page)
        self.assertIn('["http:","https:"]',self.page)
        self.assertIn('Gestion réelle via ComfyUI local',self.page)
        self.assertNotIn('queuePrompt',self.page)
        self.assertNotIn('fetch(',self.page)

    def test_declared_profile_and_dpi_match_real_g22_contract(self):
        profiles=re.search(r'<select id="realProjectProfile">([\s\S]*?)</select>',self.page)
        self.assertIsNotNone(profiles)
        values=re.findall(r'<option value="([^"]+)"',profiles.group(1))
        self.assertEqual(len(values),5)
        for value in values:
            self.assertIn(repr(value),self.backend)
        dpi=re.search(r'<select id="realProjectDpi">([\s\S]*?)</select>',self.page)
        self.assertIsNotNone(dpi)
        self.assertEqual(set(re.findall(r'<option value="(\d+)"',dpi.group(1))),
                         {"300","450"})
        self.assertIn("value not in (300, 450)",self.backend)
        self.assertIn('dpi:Number($("realProjectDpi").value)',self.page)

    def test_user_actions_preserve_native_project_safety(self):
        self.assertIn("input.type='file';file.accept='image/png'",self.panel)
        self.assertIn("method:'POST',headers:{'X-SmartSVG-UI':'1'}",self.panel)
        self.assertIn('expected_sha256:loaded.sha256',self.panel)
        self.assertIn("window.confirm(",self.panel)
        self.assertIn("api.fetchApi",self.panel)
        self.assertIn("création depuis un <strong>PNG uniquement</strong>",self.page)
        self.assertIn("aucune sauvegarde automatique",self.page)

    def test_real_g22_browser_regressions(self):
        node=shutil.which("node")
        if not node:
            self.skipTest("Node.js not installed")
        result=subprocess.run(
            [node,"--test",str(ROOT/"engine/tests/test_g22_project_panel.mjs")],
            cwd=ROOT,capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,
                         (result.stdout+"\n"+result.stderr)[-3000:])

if __name__=="__main__":
    unittest.main()
