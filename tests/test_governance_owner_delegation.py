"""Enforce owner-directed autonomous-merge scope and the fail-closed opt-in.

These regression tests intentionally protect the V3.4 owner delegation from
silent policy downgrades. Scheduled agents MUST NOT autonomously change these
governance/security tests (see docs/AUTONOMOUS_INTEGRATION_POLICY_V34.md).
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
READY = (ROOT / ".automation" / "READY").read_text(encoding="utf-8")
POLICY = (ROOT / "docs" / "AUTONOMOUS_INTEGRATION_POLICY_V34.md").read_text(encoding="utf-8")
G0 = (ROOT / ".github" / "workflows" / "g0-admission-tests.yml").read_text(encoding="utf-8")


class OwnerDelegationContractTests(unittest.TestCase):
    def test_public_repo_status_and_sensitive_assets(self):
        self.assertIn("intentionally **public**", CONTRACT)
        self.assertNotIn("this private repository", CONTRACT)
        self.assertIn("Do not commit API keys", CONTRACT)
        self.assertIn("licensed media", CONTRACT)

    def test_both_sources_require_explicit_opt_in(self):
        self.assertIn("AUTONOMOUS_MERGE_V34=ENABLED", CONTRACT)
        self.assertEqual(READY.splitlines().count("AUTONOMOUS_MERGE_V34=ENABLED"), 1)
        self.assertIn("docs/AUTONOMOUS_INTEGRATION_POLICY_V34.md", CONTRACT)
        self.assertIn("docs/AUTONOMOUS_INTEGRATION_POLICY_V34.md", READY)
        self.assertIn("DRAFT-only", CONTRACT)
        self.assertIn("DRAFT-only", READY)

    def test_code_only_scope_and_protected_files(self):
        for fragment in (
            "engine/**", "tests/**", "tools/**", "examples/synthetic/**",
            "AGENTS.md", ".automation/**", ".github/**", "docs/**",
            "source-releases/**", "engine/requirements.txt",
            "tests/test_governance_owner_delegation.py",
            "tests/test_release_archive_gate.py",
            "MANUAL_GOVERNANCE_REVIEW",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, POLICY)
        self.assertIn("Never modify `AGENTS.md`", CONTRACT)
        self.assertIn("No scheduled agent may autonomously change", CONTRACT)

    def test_fresh_candidate_checks_and_independent_cycle(self):
        for fragment in (
            "Cycle A", "Cycle B", "une PR", "expected_head_sha",
            "squash", "G0 Admission Tests", "Public read-only preflight",
            "Live Engine CPU Smoke", "SKIPPED",
            "NEEDS_CI", "FIX_REQUIRED", "BLOCKED_GITHUB_PROTECTION",
            "post-merge", "main", "NO_MERGE", "P0/P1",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, POLICY)

    def test_no_bypass_and_no_fabricated_review(self):
        for fragment in (
            "GitHub APPROVED", "branch protections", "admin bypass",
            "force-push", "G2-G9", "ComfyUI", "Cricut",
        ):
            with self.subTest(fragment=fragment):
                self.assertTrue(fragment in POLICY or fragment in CONTRACT or fragment in READY)
        self.assertIn("No simulated independent GitHub APPROVED review", READY)
        self.assertIn("No scheduled modification to AGENTS.md", READY)
        self.assertIn("owner-authorized micro-PR in a live session", CONTRACT)

    def test_source_admission_provenance_remains_immutable(self):
        for fragment in (
            "9369656f0216cebb6dccce0d0155bffa16d8c384da6a984bf848cdd8aa003c54",
            "651 internal manifest SHA-256",
            "876 Python unittest passed",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, READY)
        for fragment in (
            "docs/ROADMAP_MASTER_v3_2.md",
            "V21.14.1", "V21.15.2",
            "actual GPU RTX 3070", "physical cut measurements",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CONTRACT)

    def test_g0_has_exact_head_ci_on_all_prs_and_main_pushes(self):
        self.assertIn("  pull_request:\n", G0)
        self.assertIn("  push:\n    branches: [main]", G0)
        self.assertNotIn("    paths:", G0)
        self.assertIn("github.event.pull_request.head.sha || github.sha", G0)
        self.assertIn("EXPECTED_HEAD", G0)
        self.assertIn('test "$(git rev-parse HEAD)" = "$EXPECTED_HEAD"', G0)
        self.assertIn("contents: read", G0)
        self.assertIn("persist-credentials: false", G0)


if __name__ == "__main__":
    unittest.main()
