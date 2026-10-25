"""G2.5 frozen-roadmap UI state and project-resume non-regression gate."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'engine'


class ResumeGuideG25Tests(unittest.TestCase):
    def test_resume_states_model(self):
        node=shutil.which('node')
        if not node:
            self.skipTest('Node.js unavailable')
        result=subprocess.run(
            [node,'--test',str(ENGINE/'tests'/'test_g25_resume_states.mjs')],
            cwd=ROOT,capture_output=True,text=True,timeout=45)
        self.assertEqual(result.returncode,0,result.stdout[-8000:]+result.stderr[-4000:])

    def test_project_panel_dom_and_prior_actions(self):
        node=shutil.which('node')
        if not node:
            self.skipTest('Node.js unavailable')
        result=subprocess.run(
            [node,'--test',str(ENGINE/'tests'/'test_g22_project_panel.mjs')],
            cwd=ROOT,capture_output=True,text=True,timeout=45)
        self.assertEqual(result.returncode,0,result.stdout[-8000:]+result.stderr[-4000:])

    def test_ui_only_micro_lot_does_not_add_graph_mutations(self):
        model=(ENGINE/'web'/'js'/'smartsvg_resume_state_g25.mjs').read_text()
        panel=(ENGINE/'web'/'js'/'smartsvg_project_panel_g22.mjs').read_text()
        self.assertNotIn('queuePrompt',model+panel)
        self.assertNotIn('innerHTML',model+panel)
        self.assertNotIn('NODE_CLASS_MAPPINGS',model+panel)
        self.assertIn('graphRestored:false',model)
        self.assertIn('cutVerified:false',model)
