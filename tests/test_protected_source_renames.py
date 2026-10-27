"""Regression tests for the private agent protected-path gate.

Run with: python -m unittest discover -s tests -p 'test_*.py'
"""
import fnmatch
import json
import os
import re
import subprocess
import tempfile
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





class ProtectedPathRenameTests(unittest.TestCase):
    """Exercise the real staged-path check against actual git rename detection."""

    @staticmethod
    def _run_staged_check(old_path, new_path):
        source = WORKFLOW.read_text(encoding="utf-8")
        start = source.index("          while IFS= read -r -d '' path; do")
        end = source.index("\n", source.index("          done < <(git diff", start))
        snippet = "\n".join(line[10:] for line in source[start:end].splitlines())
        script = "set -euo pipefail\n" + snippet + "\necho ADMITTED\n"

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            old_file = root / old_path
            old_file.parent.mkdir(parents=True, exist_ok=True)
            old_file.write_text("synthetic test data\n", encoding="utf-8")

            def git(*args):
                subprocess.run(["git", *args], cwd=tmp, check=True,
                               capture_output=True, text=True)

            git("init", "-q")
            git("config", "user.email", "smartsvg-test@example.invalid")
            git("config", "user.name", "SmartSVG regression test")
            git("add", ".")
            git("commit", "-qm", "synthetic baseline")
            (root / new_path).parent.mkdir(parents=True, exist_ok=True)
            git("mv", old_path, new_path)
            return subprocess.run(["bash", "-c", script], cwd=tmp,
                                  capture_output=True, text=True, check=False)

    def test_protected_source_renamed_into_unprotected_path_is_blocked(self):
        for protected in (
            "docs/ROADMAP_MASTER_v3_2.md",
            "docs/SOURCE_V21_15_2_PROVENANCE.json",
            "source-releases/source.zip",
            ".automation/READY",
        ):
            with self.subTest(source=protected):
                result = self._run_staged_check(protected, "engine/renamed.txt")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("Protected path edited: " + protected, result.stdout)

    def test_safe_rename_remains_allowed(self):
        result = self._run_staged_check("engine/old.py", "engine/new.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ADMITTED", result.stdout)


if __name__=="__main__":
    unittest.main()
