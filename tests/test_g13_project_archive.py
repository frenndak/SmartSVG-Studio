"""Include G1.3 archive tests in the existing private admission CI."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"


def load_tests(loader, standard_tests, pattern):
    if str(ENGINE) not in sys.path:
        sys.path.insert(0, str(ENGINE))
    file = ENGINE / "tests" / "test_project_archive_g13.py"
    spec = spec_from_file_location("smartsvg_g13_archive_tests", file)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return loader.loadTestsFromModule(module)
