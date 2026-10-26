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
                    self.assertEqual(output, "proceed=false\n")
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
        snippet = "\n".join(line[10:] for line in source[start:end].splitlines())
        script = "set -euo pipefail\n" + snippet + "\necho REACHED_NEXT_STAGE\n"
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



class PaidBudgetGateTests(unittest.TestCase):
    """Exercise the actual no-cost Bash gate before any paid API step."""

    @staticmethod
    def _run_gate(budget="10", cap="2", count="1", api_fail=False, attempt="1"):
        source = WORKFLOW.read_text(encoding="utf-8")
        start = source.index("      - name: Require explicit paid budget and daily run cap")
        end = source.index("      - name: Require the private OpenAI API secret", start)
        step = source[start:end]
        script = "\n".join(
            line[10:] for line in step.split("        run: |\n", 1)[1].splitlines()
        ) + "\n"
        with tempfile.TemporaryDirectory() as tmp:
            fake_gh = Path(tmp) / "gh"
            fake_gh.write_text(
                "#!/usr/bin/env bash\n"
                '[[ "$1" == "api" ]] || exit 7\n'
                '[[ "$2" == repos/frenndak/SmartSVG-Studio/actions/workflows/private-ai-development.yml/runs?created=* ]] || exit 7\n'
                '[[ "${FAKE_API_FAIL:-0}" != 1 ]] || exit 8\n'
                "printf '{\"total_count\":%s}\\n' \"${FAKE_RUN_COUNT:-1}\"\n"
            )
            fake_gh.chmod(0o755)
            return subprocess.run(
                ["bash", "-c", script], capture_output=True, text=True,
                env={**os.environ, "PATH": tmp + os.pathsep + os.environ["PATH"],
                     "MONTHLY_API_BUDGET_USD": budget,
                     "MAX_PAID_RUNS_PER_DAY": cap,
                     "FAKE_RUN_COUNT": count,
                     "GITHUB_RUN_ATTEMPT": attempt,
                     "FAKE_API_FAIL": "1" if api_fail else "0"},
                check=False,
            )

    def test_configured_budget_and_in_quota_run_pass(self):
        result = self._run_gate(budget="12.50", cap="2", count="2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Budget admission", result.stdout)

    def test_missing_invalid_or_zero_budget_fails_closed(self):
        for budget in ("", "0", "-1", "invalid", "12.999"):
            with self.subTest(budget=budget):
                self.assertNotEqual(self._run_gate(budget=budget).returncode, 0)

    def test_missing_invalid_or_excessive_run_cap_fails_closed(self):
        for cap in ("", "0", "25", "abc", "01"):
            with self.subTest(cap=cap):
                self.assertNotEqual(self._run_gate(cap=cap).returncode, 0)

    def test_over_quota_or_unverified_github_count_fails_closed(self):
        for count in ("3", "101", "null", '"broken"'):
            with self.subTest(count=count):
                self.assertNotEqual(self._run_gate(cap="2", count=count).returncode, 0)
        self.assertNotEqual(self._run_gate(api_fail=True).returncode, 0)

    def test_paid_workflow_retries_never_consume_extra_api_quota(self):
        # GitHub reruns increment GITHUB_RUN_ATTEMPT, not total_count.
        # No attempt other than the first may reach the paid action.
        for attempt in ("", "2", "3", "01", "not-a-number"):
            with self.subTest(attempt=attempt):
                result = self._run_gate(budget="10", cap="24", count="1",
                                        attempt=attempt)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Paid workflow reruns are prohibited", result.stdout)

    def test_budget_gate_precedes_secret_and_paid_action(self):
        source = WORKFLOW.read_text(encoding="utf-8")
        self.assertLess(source.index("Require explicit paid budget and daily run cap"),
                        source.index("Require the private OpenAI API secret"))
        self.assertLess(source.index("Require explicit paid budget and daily run cap"),
                        source.index("uses: openai/codex-action@v1"))


if __name__ == "__main__":
    unittest.main()
