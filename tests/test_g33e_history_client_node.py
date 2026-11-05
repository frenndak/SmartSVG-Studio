from pathlib import Path
import shutil
import subprocess
import unittest


class BrushHistoryClientNodeTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'),'Node.js runtime unavailable')
    def test_history_client_and_controls(self):
        root=Path(__file__).resolve().parents[1]
        result=subprocess.run([shutil.which('node'),'--test',
            str(root/'tools/test_subject_brush_history_client_g33e.mjs')],
            cwd=root,capture_output=True,text=True,timeout=25)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
