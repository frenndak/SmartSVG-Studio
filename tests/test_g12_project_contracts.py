"""Run G1.2 metadata record contract tests in the private admission CI."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"


def load_tests(loader, standard_tests, pattern):
    if str(ENGINE) not in sys.path:
        sys.path.insert(0, str(ENGINE))
    file = ENGINE / "tests" / "test_project_contracts_g12.py"
    spec = spec_from_file_location("smartsvg_g12_contract_tests", file)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return loader.loadTestsFromModule(module)
