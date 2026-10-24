"""G2.3: register synthetic mask persistence tests in existing admission CI."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'engine'

def load_tests(loader, standard_tests, pattern):
    if str(ENGINE) not in sys.path:
        sys.path.insert(0, str(ENGINE))
    file = ENGINE / 'tests' / 'test_subject_masks_g23.py'
    spec = spec_from_file_location('smartsvg_g23_subject_tests', file)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    suite = loader.loadTestsFromModule(module)
    suite.addTests(loader.loadTestsFromTestCase(IntegrationGuardTests))
    return suite

class IntegrationGuardTests(unittest.TestCase):
    def test_new_mask_endpoints_are_same_opt_in_workspace(self):
        routes = (ENGINE / 'project_routes_g22.py').read_text()
        self.assertIn("prefix+'/mask'", routes)
        self.assertIn("_browser_origin_ok(request)", routes)
        entry = (ENGINE / '__init__.py').read_text()
        self.assertIn("SMARTSVG_ENABLE_PROJECT_API", entry)
