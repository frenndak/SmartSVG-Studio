"""Regression tests for the private agent protected-path gate.

Run with: python -m unittest discover -s tests -p 'test_*.py'
"""
import fnmatch
import re
import unittest
from pathlib import Path


WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/private-ai-development.yml"


def protected_patterns():
    source = WORKFLOW.read_text(encoding="utf-8")
    match = re.search(r'(?m)^\s*case "\$path" in\s*\n\s*([^\n]+)\)\s*\n\s*echo "::error::Protected path edited: \$path"', source)
    if not match:
        raise AssertionError("Cannot locate the fail-closed protected-path case arm")
    return match.group(1).strip().split("|")


class ProtectedPathGateTests(unittest.TestCase):
    def test_immutable_archive_and_provenance_are_rejected(self):
        patterns = protected_patterns()
        for path in (
            "source-releases/ComfyUI_SmartSVG_Studio_V21_15_2_Installation.zip",
            "source-releases/nested/original.zip",
            "docs/SOURCE_V21_15_2_PROVENANCE.json",
            "docs/ROADMAP_MASTER_v3_2.md",
            ".automation/READY",
        ):
            with self.subTest(path=path):
                self.assertTrue(any(fnmatch.fnmatchcase(path, p) for p in patterns), path)

    def test_engine_changes_remain_allowed(self):
        patterns = protected_patterns()
        for path in ("engine/SmartSVG/nodes.py", "engine/README.md", "tests/test_svg_geometry.py"):
            with self.subTest(path=path):
                self.assertFalse(any(fnmatch.fnmatchcase(path, p) for p in patterns), path)


if __name__ == "__main__":
    unittest.main()
