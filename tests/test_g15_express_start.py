"""Run G1.5 frontend tests on exact PR head in the existing GitHub CI."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEST_FILE = ROOT / "engine" / "tests" / "test_g15_express_start.mjs"


class ExpressStarterG15Tests(unittest.TestCase):
    def test_browser_model_and_dom_contracts(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js required for G1.5 JS UI tests")
        result = subprocess.run(
            [node, "--test", str(TEST_FILE)],
            cwd=ROOT, capture_output=True, text=True, timeout=35,
        )
        self.assertEqual(
            result.returncode, 0,
            "G1.5 Node tests failed:\n" + result.stdout[-7000:] + result.stderr[-7000:],
        )

    def test_g15_adds_no_new_comfyui_node_ids(self):
        src = (ROOT / "engine" / "web" / "js" / "smartsvg_express_start_g15.js").read_text()
        self.assertNotIn("NODE_CLASS_MAPPINGS", src)
        self.assertNotIn("onExecuted", src)
        self.assertIn("nodeCreated", src)


if __name__ == "__main__":
    unittest.main()
