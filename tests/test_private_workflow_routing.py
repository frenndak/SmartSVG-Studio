"""Regression tests for autonomous PR scoping in the private runner.

Tests use synthetic GitHub CLI metadata only; no token, repository access or AI API.
"""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "private-ai-development.yml"


class PrivateAgentRoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = WORKFLOW.read_text(encoding="utf-8")
        match = re.search(r"""auto_prs="\$\(jq '([^']+)' <<< "\$open_prs"\)""", cls.source)
        if not match:
            raise AssertionError("No explicit agent-only PR filter in private runner")
        cls.jq_query = match.group(1)

    @unittest.skipUnless(shutil.which("jq"), "jq is required by the GitHub runner")
    def test_human_and_bootstrap_prs_do_not_block_agent_development(self):
        input_prs = [
            {"headRefName": "bootstrap/v21-15-2-100", "isDraft": True},
            {"headRefName": "ops/manual-review", "isDraft": True},
        ]
        self.assertEqual(self._filter(input_prs), [])

    @unittest.skipUnless(shutil.which("jq"), "jq is required by the GitHub runner")
    def test_repair_targets_only_single_autonomous_branch(self):
        input_prs = [
            {"headRefName": "ops/manual-review", "isDraft": True},
            {"headRefName": "smartsvg/auto-123", "isDraft": True},
        ]
        self.assertEqual(self._filter(input_prs), [input_prs[1]])

    @unittest.skipUnless(shutil.which("jq"), "jq is required by the GitHub runner")
    def test_multiple_autonomous_prs_count_as_conflict(self):
        input_prs = [
            {"headRefName": "smartsvg/auto-123", "isDraft": True},
            {"headRefName": "smartsvg/auto-456", "isDraft": True},
            {"headRefName": "bootstrap/source", "isDraft": True},
        ]
        self.assertEqual(len(self._filter(input_prs)), 2)
        self.assertIn('[[ "$count" == "1" && "$phase" == "repair" ]]', self.source)

    def test_provenance_gate_and_no_auto_merge_remain(self):
        for required in (
            ".automation/READY",
            "docs/IMPORT_V21_15_2.json",
            "engine/INSTALLATION_MANIFEST_V21_15_2.json",
            "internal_manifest_hashes_verified",
            "gh pr create",
            "--draft --base main",
        ):
            self.assertIn(required, self.source)
        self.assertNotIn("gh pr merge", self.source)

    def test_github_token_candidates_receive_explicit_branch_ci(self):
        # GitHub may hold pull_request CI created with GITHUB_TOKEN for
        # approval. Explicit workflow_dispatch has different event semantics.
        self.assertIn("actions: write", self.source)
        self.assertIn("gh workflow run g0-admission-tests.yml", self.source)
        self.assertIn("gh workflow run engine-cpu-smoke.yml", self.source)
        self.assertEqual(self.source.count('--ref "$BRANCH"'), 2)
        self.assertIn('git diff --quiet HEAD^ HEAD -- engine/', self.source)

    def test_manual_default_is_preflight_only(self):
        self.assertIn('execute:', self.source)
        self.assertIn('default: false', self.source)
        self.assertIn("inputs.execute == true", self.source)
        self.assertIn("github.event_name == 'workflow_dispatch'", self.source)
        self.assertIn("python tools/verify_source_integrity.py --repo . --archive-only", self.source)

    def test_one_shot_repair_requires_reviewer_label(self):
        self.assertIn('repair_requested="$(jq', self.source)
        self.assertIn('"smartsvg:repair" or .name == "bug"', self.source)
        self.assertIn('[[ "$repair_requested" != "true" ]]', self.source)
        self.assertIn('Claim reviewer repair request before any API cost', self.source)
        self.assertIn('gh pr edit "$PR_NUMBER"', self.source)
        self.assertIn('--remove-label "$REPAIR_LABEL"', self.source)
        self.assertIn('Require the private OpenAI API secret', self.source)

    @classmethod
    def _filter(cls, prs):
        completed = subprocess.run(
            ["jq", cls.jq_query],
            input=json.dumps(prs),
            text=True,
            capture_output=True,
            check=True,
        )
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
