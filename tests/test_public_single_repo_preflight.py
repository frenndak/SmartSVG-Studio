"""Static security and regression gates for the free, public SmartSVG preflight.

No GitHub API, network, credentials, GPU, or physical machine is needed.
This tests workflow policy, not successful execution on the candidate PR HEAD.
"""
import re
import unittest
from pathlib import Path

WORKFLOW = Path(__file__).resolve().parents[1] / ".github/workflows/public-autonomous-cycle.yml"


def policy_violations(source: str) -> list[str]:
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(message)

    # This workflow must remain a free, read-only *preflight*, not a hidden
    # development agent or an inter-repository dispatcher.
    require(bool(re.search(r"(?m)^permissions:\s*\n\s+contents:\s*read\s*$", source)),
            "GLOBAL_PERMISSIONS_NOT_READ_ONLY")
    require(not re.search(r"(?m)^\s+(?:contents|actions|issues|pull-requests|workflows):\s*write\s*$", source),
            "WRITE_PERMISSION_REQUESTED")
    require(not re.search(r"\b(?:pull_request_target|repository_dispatch|workflow_run|workflow_call)\s*:", source),
            "PRIVILEGED_OR_CROSS_REPO_TRIGGER")
    require(not re.search(
        r"(?i)(?:OPENAI_API_KEY|SMARTSVG_DISPATCH_TOKEN|codex-action|"
        r"repository_dispatch|gh\s+api|curl\s|wget\s|"
        r"secrets\.|\bghp_|\bgithub-script\b)", source),
        "PAID_OR_EXTERNAL_API_REFERENCE")
    require("runs-on: ubuntu-24.04" in source, "RUNNER_NOT_PINNED")
    require("timeout-minutes: 12" in source, "TIMEOUT_MISSING")
    require("persist-credentials: false" in source, "CHECKOUT_CREDENTIALS_PERSISTED")
    # The PR event's default github.sha is a synthetic merge commit. Both
    # checkout and the explicit assertion must use the candidate's HEAD.
    expected_ref = r"\$\{\{\s*github\.event\.pull_request\.head\.sha\s*\|\|\s*github\.sha\s*\}\}"
    require(bool(re.search(r"(?m)^\s+ref:\s*" + expected_ref + r"\s*$", source)),
            "PR_HEAD_NOT_CHECKED_OUT")
    require(bool(re.search(r"(?m)^\s+EXPECTED_HEAD:\s*" + expected_ref + r"\s*$", source)),
            "PR_HEAD_EXPECTATION_MISSING")
    require('actual_head="$(git rev-parse HEAD)"' in source and
            'if [[ "$actual_head" != "$EXPECTED_HEAD" ]]' in source and
            'echo "::error::Checkout SHA mismatch:' in source,
            "EXACT_HEAD_ASSERTION_MISSING")


    schedules = re.findall(r'(?m)^\s+- cron:\s*"([^"]+)"\s*$', source)
    require(schedules == ["5 * * * *", "50 * * * *"], "SCHEDULE_DRIFT")
    # Engine and admission changes must trigger the independent free PR check.
    required_pr_paths = (
        ".github/workflows/**", "engine/**", "tools/**", "tests/**",
        "source-releases/**", ".automation/READY", "AGENTS.md", "README.md",
        "docs/ROADMAP_MASTER_v3_2.md",
    )
    match = re.search(r'(?m)^  pull_request:\s*\n    paths:\s*\n((?:      - [^\n]+\n)+)', source)
    configured_paths = set(re.findall(r'^      - "([^"]+)"$', match.group(1), re.M)) if match else set()
    require(set(required_pr_paths) <= configured_paths, "PR_PATH_COVERAGE_MISSING")
    require('*) echo "::error::Unknown schedule"; exit 1' in source,
            "UNKNOWN_SCHEDULE_NOT_REJECTED")
    require("test -s .automation/READY" in source, "ADMISSION_MARKER_MISSING")
    require(bool(re.search(
        r"[0-9a-f]{64}\s+docs/ROADMAP_MASTER_v3_2\.md'\s*\|\s*sha256sum -c",
        source)), "FROZEN_ROADMAP_HASH_NOT_CHECKED")
    require("verify_source_integrity.py --repo . --archive-only" in source,
            "IMMUTABLE_ARCHIVE_NOT_VERIFIED")
    require("python -m unittest discover -s tests -p 'test_*.py' -q" in source,
            "PYTHON_REGRESSIONS_NOT_RUN")
    require("python -m compileall -q engine tools tests" in source,
            "PYTHON_SYNTAX_NOT_CHECKED")
    return errors


class PublicSingleRepoPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_current_workflow_satisfies_free_read_only_contract(self):
        self.assertEqual(policy_violations(self.workflow), [])

    def test_rejects_paid_secret_or_cross_repository_dispatch(self):
        for addition in (
            "\n      - run: echo ${{ secrets.OPENAI_API_KEY }}\n",
            "\n      - run: gh api repos/frenndak/SmartSVG-Automation/dispatches\n",
            "\n  repository_dispatch:\n",
        ):
            with self.subTest(addition=addition):
                self.assertTrue(policy_violations(self.workflow + addition))

    def test_rejects_write_permission_and_missing_archive_gate(self):
        mutated = self.workflow.replace("contents: read", "contents: write")
        self.assertIn("GLOBAL_PERMISSIONS_NOT_READ_ONLY", policy_violations(mutated))
        mutated = self.workflow.replace(" --archive-only", "")
        self.assertIn("IMMUTABLE_ARCHIVE_NOT_VERIFIED", policy_violations(mutated))

    def test_requires_exact_pr_head_checkout_and_runtime_assertion(self):
        for old, new, expected in (
            ("ref: ${{ github.event.pull_request.head.sha || github.sha }}",
             "ref: ${{ github.sha }}", "PR_HEAD_NOT_CHECKED_OUT"),
            ("EXPECTED_HEAD: ${{ github.event.pull_request.head.sha || github.sha }}",
             "EXPECTED_HEAD: ${{ github.sha }}", "PR_HEAD_EXPECTATION_MISSING"),
            ('if [[ "$actual_head" != "$EXPECTED_HEAD" ]]',
             'if [[ "$actual_head" == "$EXPECTED_HEAD" ]]', "EXACT_HEAD_ASSERTION_MISSING"),
        ):
            with self.subTest(expected=expected):
                self.assertIn(expected, policy_violations(self.workflow.replace(old, new)))

    def test_engine_and_source_changes_must_trigger_pr_preflight(self):
        for path in ("engine/**", "source-releases/**", "AGENTS.md",
                     ".github/workflows/**"):
            with self.subTest(path=path):
                modified = self.workflow.replace(f'      - "{path}"\n', "")
                self.assertIn("PR_PATH_COVERAGE_MISSING", policy_violations(modified))

    def test_rejects_missing_timeout_or_changed_cron(self):
        self.assertIn("TIMEOUT_MISSING", policy_violations(
            self.workflow.replace("timeout-minutes: 12", "timeout-minutes: 0")))
        self.assertIn("SCHEDULE_DRIFT", policy_violations(
            self.workflow.replace('"50 * * * *"', '"30 * * * *"')))


if __name__ == "__main__":
    unittest.main()
