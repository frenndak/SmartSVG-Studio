"""Admission gate for real G2.3 brush-session persistence and V216 browser tests."""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'engine'


def load_tests(loader,standard_tests,pattern):
    if str(ENGINE) not in sys.path:
        sys.path.insert(0,str(ENGINE))
    filename=ENGINE/'tests'/'test_editor_sessions_g23.py'
    spec=spec_from_file_location('smartsvg_g23_editor_tests',filename)
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    suite=loader.loadTestsFromModule(module)
    suite.addTests(loader.loadTestsFromTestCase(EditorBridgeJS))
    return suite


class EditorBridgeJS(unittest.TestCase):
    def test_v216_project_bridge_js(self):
        node=shutil.which('node')
        if not node:
            self.skipTest('Node.js unavailable')
        result=subprocess.run(
            [node,'--test',str(ENGINE/'tests'/'test_g23_editor_bridge.mjs')],
            cwd=ROOT,capture_output=True,text=True,timeout=45)
        self.assertEqual(result.returncode,0,result.stdout[-7000:]+result.stderr[-4000:])

    def test_current_route_remains_opt_in_and_no_new_node_ids(self):
        entry=(ENGINE/'__init__.py').read_text()
        self.assertIn("SMARTSVG_ENABLE_PROJECT_API",entry)
        routes=(ENGINE/'project_routes_g22.py').read_text()
        self.assertIn("X-SmartSVG-UI",routes)
        self.assertIn("@routes.post(prefix+'/editor/save')",routes)
        editor=(ENGINE/'web'/'js'/'smartsvg_editor_v216.js').read_text()
        self.assertIn("createEditorProjectControls",editor)
        self.assertNotIn("NODE_CLASS_MAPPINGS",editor)
