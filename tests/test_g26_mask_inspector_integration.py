"""Integration gate for the additive mask inspector and V21.6 focused editing.

ComfyUI/torch/OpenCV inference and a real browser remain separate evidence
classes; these CPU-only Node tests check the actual UI models.
"""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'engine'

class MaskInspectorIntegration(unittest.TestCase):
    def test_browser_subject_inspector_and_mask_focus_models(self):
        node=shutil.which('node')
        if not node:self.skipTest('Node.js unavailable')
        suites=[
            'test_v21154_inspector.mjs',
            'test_v21155_fragment_locations.mjs',
            'test_v21156_mask_focus.mjs',
        ]
        p=subprocess.run([node,'--test',*map(lambda x:str(ENGINE/'tests'/x),suites)],
            cwd=ROOT,text=True,capture_output=True,timeout=45)
        self.assertEqual(p.returncode,0,p.stdout[-11000:]+p.stderr[-4000:])

    def test_additive_registry_retains_g22_g24_and_existing_editor(self):
        init=(ENGINE/'__init__.py').read_text()
        editor=(ENGINE/'web/js/smartsvg_editor_v216.js').read_text()
        self.assertIn('from .node_v21154 import NODE_CLASS_MAPPINGS',init)
        self.assertIn('SMARTSVG_ENABLE_PROJECT_API',init)
        self.assertIn('node_g24_mask_vault',init)
        self.assertIn('createEditorProjectControls(api,app,node)',editor)
        self.assertIn('editorDraftStore(draftStorage,meta,node.id)',editor)
        self.assertIn('validatedFocus(pendingFocus,node._smartsvgV216Meta)',editor)
        self.assertIn('void loadMask(current)',editor)
        self.assertNotIn('queuePrompt',editor)

if __name__=='__main__':unittest.main()
