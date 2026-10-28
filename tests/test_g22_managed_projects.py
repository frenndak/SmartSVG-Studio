"""G2.2 project persistence and browser controls, via existing admission CI."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'engine'


def load_tests(loader, standard_tests, pattern):
    if str(ENGINE) not in sys.path:
        sys.path.insert(0,str(ENGINE))
    path=ENGINE/'tests'/'test_project_workspace_g22.py'
    spec=spec_from_file_location('smartsvg_g22_workspace_tests',path)
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    result=loader.loadTestsFromModule(module)
    result.addTests(loader.loadTestsFromTestCase(ProjectPanelJSTests))
    return result


class ProjectPanelJSTests(unittest.TestCase):
    def test_project_panel_node_js(self):
        node=shutil.which('node')
        if not node:
            self.skipTest('Node.js unavailable')
        r=subprocess.run([node,'--test',str(ENGINE/'tests'/'test_g22_project_panel.mjs')],
            cwd=ROOT,capture_output=True,text=True,timeout=35)
        self.assertEqual(r.returncode,0,r.stdout[-7000:]+r.stderr[-5000:])

    def test_optional_endpoints_not_registered_unconditionally(self):
        entry=(ENGINE/'__init__.py').read_text()
        self.assertIn("SMARTSVG_ENABLE_PROJECT_API",entry)
        self.assertIn("== '1'",entry)
        routes=(ENGINE/'project_routes_g22.py').read_text()
        self.assertIn("X-SmartSVG-UI",routes)
        self.assertIn("@routes.post(prefix+'/resolve-pending')",routes)
        self.assertIn("expected_pending_sha256=fields.get('expected_pending_sha256')",routes)
        self.assertIn("confirmed=fields.get('confirmed')=='yes'",routes)
        self.assertNotIn('os.system',routes)
