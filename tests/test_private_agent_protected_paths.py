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



class BacklogGateTests(unittest.TestCase):
    """Run the *actual* bash backlog gate extracted from the checked-in workflow."""

    def test_paid_develop_is_deferred_after_four_total_open_prs(self):
        for count, phase, blocked in (
            (0, "develop", False),
            (3, "develop", False),
            (4, "develop", True),
            (16, "develop", True),
            (16, "repair", False),
        ):
            with self.subTest(count=count, phase=phase):
                result, output = self._run_gate(count, phase)
                self.assertEqual(result.returncode, 0, result.stderr)
                if blocked:
                    self.assertEqual(output, "proceed=false\\n")
                    self.assertNotIn("REACHED_NEXT_STAGE", result.stdout)
                else:
                    self.assertEqual(output, "")
                    self.assertIn("REACHED_NEXT_STAGE", result.stdout)

    def test_malformed_open_prs_fail_closed(self):
        result, output = self._run_gate(0, "develop", prs_json="{broken")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("REACHED_NEXT_STAGE", result.stdout)
        self.assertEqual(output, "")

    @staticmethod
    def _run_gate(count, phase, prs_json=None):
        source = WORKFLOW.read_text(encoding="utf-8")
        beginning = '          total_open_prs="$(jq '
        end_marker = '          # WIP=1 among autonomous agent branches'
        start = source.index(beginning)
        end = source.index(end_marker, start)
        snippet = "\\n".join(line[10:] for line in source[start:end].splitlines())
        script = "set -euo pipefail\\n" + snippet + "\\necho REACHED_NEXT_STAGE\\n"
        if prs_json is None:
            prs_json = json.dumps([
                {"number": n + 1, "isDraft": True, "headRefName": "feat/test",
                 "labels": []} for n in range(count)
            ])
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "output.txt"
            output.write_text("")
            result = subprocess.run(
                ["bash", "-c", script], check=False, capture_output=True, text=True,
                env={**os.environ, "phase": phase, "open_prs": prs_json,
                     "GITHUB_OUTPUT": str(output)},
            )
            return result, output.read_text()



if __name__ == "__main__":
    unittest.main()
