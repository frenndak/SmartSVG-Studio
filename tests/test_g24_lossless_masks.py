"""Admission tests for G2.4 float32 mask archive and opt-in node registration."""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'engine'

def load_tests(loader,standard_tests,pattern):
    if str(ENGINE) not in sys.path:
        sys.path.insert(0,str(ENGINE))
    file=ENGINE/'tests'/'test_lossless_masks_g24.py'
    spec=spec_from_file_location('smartsvg_g24_lossless_tests',file)
    mod=module_from_spec(spec)
    spec.loader.exec_module(mod)
    suite=loader.loadTestsFromModule(mod)
    suite.addTests(loader.loadTestsFromTestCase(MaskNodeAdmission))
    return suite

class MaskNodeAdmission(unittest.TestCase):
    def test_node_remains_opt_in(self):
        entry=(ENGINE/'__init__.py').read_text()
        self.assertIn("SMARTSVG_ENABLE_PROJECT_API",entry)
        self.assertIn('node_g24_mask_vault',entry)
        node=(ENGINE/'node_g24_mask_vault.py').read_text()
        self.assertIn("from .smartsvg_core.project_workspace_g22 import ManagedWorkspace",node)
        self.assertIn('edit_fingerprint(rgb,base)',node)
        self.assertIn("_same_png_source(workspace,nom_projet,rgb)",node)
        self.assertNotIn('subprocess.',node)
        self.assertNotIn('os.system(',node)
    def test_no_change_to_existing_comfyui_node_signatures(self):
        node=(ENGINE/'node_v216.py').read_text()
        self.assertIn("def run(self,image,retouches_json='',masque_base=None):",node)
        self.assertIn("RETURN_TYPES=('MASK','IMAGE','STRING')",node)
        archive=(ENGINE/'smartsvg_core'/'project_archive.py').read_text()
        self.assertIn('validate_archive_snapshot(project)',archive)
        self.assertIn("expected[snapshot_path]=('snapshot', None)",archive)
