"""Execute G2.5 responsive state, async project UI and safety tests in admission CI."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'engine'

class ExpressUXG25(unittest.TestCase):
    def test_guided_express_node_js(self):
        node=shutil.which('node')
        if node is None:
            self.skipTest('Node.js is unavailable')
        result=subprocess.run([node,'--test',str(ENGINE/'tests'/'test_g25_express_ux.mjs')],
            cwd=ROOT,text=True,capture_output=True,timeout=45)
        self.assertEqual(result.returncode,0,
            result.stdout[-7500:]+result.stderr[-4000:])

    def test_unchanged_node_ids_and_only_manual_project_actions(self):
        root=(ENGINE/'web'/'js'/'smartsvg_express_start_g15.js').read_text()
        ux=(ENGINE/'web'/'js'/'smartsvg_express_ux_g25.mjs').read_text()
        self.assertIn("root.appendChild(projectDetails)",root)
        self.assertNotIn('app.queuePrompt',root)
        self.assertNotIn('innerHTML',root)
        self.assertNotIn('fetch(',ux)
        self.assertNotIn('NODE_CLASS_MAPPINGS',ux)

if __name__=='__main__':
    unittest.main()
