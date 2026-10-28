"""Validate G3.3b real subject handoff as a local opt-in diagnostic.

Does not certify browser rendering or real GPU/ComfyUI results.
"""
from pathlib import Path
import shutil
import subprocess
import unittest
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'engine/tests/test_g33_subject_handoff.mjs'

class RealSubjectHandoffTests(unittest.TestCase):
    def test_node_handoff_security_and_non_destructive_contracts(self):
        node=shutil.which('node')
        if not node:
            self.skipTest('Node.js unavailable')
        for suite in (JS, ROOT/'engine/tests/test_g33_subject_selection.mjs'):
            result=subprocess.run([node,'--test',str(suite)],cwd=ROOT,
                                  text=True,capture_output=True,timeout=30)
            self.assertEqual(result.returncode,0,(result.stdout+result.stderr)[-6000:])

    def test_sender_and_reception_reuse_real_g26_inspector(self):
        html=(ROOT/'engine/web/js/smartsvg_express_atelier_preview.html').read_text()
        source=(ROOT/'engine/web/js/smartsvg_subject_inspector_v21154.js').read_text()
        for txt in ('G2.6','source_sha256','chosenRealSubjects',
                    'realSubjectsStatus','receiveSubjects','realSubjectsGrid',
                    '90 secondes','aucun export ni masque modifié'):
            with self.subTest(marker=txt):
                self.assertIn(txt,html)
        self.assertIn('smartsvg_subjects_v21154',source)
        self.assertIn('normalizeSubjectInspection(latest)',source)
        self.assertIn('share.addEventListener',source)
        self.assertNotIn('queuePrompt',html)
        self.assertNotIn('fetch(',html)

if __name__=='__main__':
    unittest.main()
