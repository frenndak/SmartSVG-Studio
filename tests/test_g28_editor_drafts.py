"""G2.8 browser-local stroke draft recovery tests via public admission CI."""
from pathlib import Path
import shutil
import subprocess
import unittest
ROOT=Path(__file__).resolve().parents[1]
class EditorDraftG28Tests(unittest.TestCase):
    def test_drafts_and_recovery_node(self):
        node=shutil.which('node')
        if node is None:self.skipTest('Node.js unavailable')
        result=subprocess.run([node,'--test',str(ROOT/'engine/tests/test_g28_editor_drafts.mjs')],
            cwd=ROOT,text=True,capture_output=True,timeout=35)
        self.assertEqual(result.returncode,0,result.stdout[-9000:]+result.stderr[-4500:])
    def test_no_raw_image_or_unsolicited_graph_execution(self):
        store=(ROOT/'engine/web/js/smartsvg_editor_draft_g28.mjs').read_text()
        editor=(ROOT/'engine/web/js/smartsvg_editor_v216.js').read_text()
        self.assertIn('source:meta.source',store)
        self.assertIn('decodeDocument(meta,data.document)',store)
        self.assertIn('editorDraftStore(draftStorage,meta,node.id)',editor)
        self.assertNotIn('queuePrompt',store)
        self.assertNotIn('fetchApi',store)
        self.assertNotIn('innerHTML',store)
if __name__=='__main__':unittest.main()
