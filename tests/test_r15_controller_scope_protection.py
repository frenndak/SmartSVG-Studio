import unittest
from tools.smartsvg_controller_preflight import _valid_path

class ControllerScopeProtectionTests(unittest.TestCase):
    def test_controller_files_require_owner_review(self):
        for path in ("tools/smartsvg_controller_runtime.py",
                     "tools/smartsvg_controller_recovery_record.py",
                     "tests/test_r15_controller_cas.py",
                     "tests/fixtures/r15_queue_replay_20261125.json"):
            with self.subTest(path=path):
                self.assertFalse(_valid_path(path))

    def test_product_code_and_tests_remain_eligible(self):
        for path in ("engine/native_atelier_tk_v34.py",
                     "tests/test_v35_native_basic_cut_export.py",
                     "tools/check_svg.py"):
            with self.subTest(path=path):
                self.assertTrue(_valid_path(path))
