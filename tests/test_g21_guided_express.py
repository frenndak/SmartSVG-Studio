"""Run the unified G2.1 Express browser model and UI tests on the private CI."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
JS_TEST=ROOT / "engine" / "tests" / "test_g21_guided_express.mjs"

class ExpressGuideG21Tests(unittest.TestCase):
    def test_guide_browser_semantics(self):
        node=shutil.which("node")
        if not node:
            self.skipTest("Node.js unavailable")
        result=subprocess.run([node,"--test",str(JS_TEST)],cwd=ROOT,
                              capture_output=True,text=True,timeout=35)
        self.assertEqual(result.returncode,0,
                         result.stdout[-8000:] + result.stderr[-5000:])
    def test_no_new_comfyui_node_classes(self):
        src=(ROOT/"engine"/"web"/"js"/"smartsvg_express_start_g15.js").read_text()
        self.assertNotIn('NODE_CLASS_MAPPINGS',src)
        self.assertNotIn('queuePrompt',src)
