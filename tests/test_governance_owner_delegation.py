"""Enforce owner-directed autonomous-merge scope and the fail-closed opt-in.

These regression tests intentionally protect the owner delegation and explicit V3.5 adoption from
silent policy downgrades. Scheduled agents MUST NOT autonomously change these
governance/security tests (see docs/AUTONOMOUS_INTEGRATION_POLICY_V34.md).
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
READY = (ROOT / ".automation" / "READY").read_text(encoding="utf-8")
POLICY = (ROOT / "docs" / "AUTONOMOUS_INTEGRATION_POLICY_V35.md").read_text(encoding="utf-8")
G0 = (ROOT / ".github" / "workflows" / "g0-admission-tests.yml").read_text(encoding="utf-8")


class OwnerDelegationContractTests(unittest.TestCase):
    def test_public_repo_status_and_sensitive_assets(self):
        self.assertIn("intentionally **public**", CONTRACT)
        self.assertNotIn("this private repository", CONTRACT)
        self.assertIn("Do not commit API keys", CONTRACT)
        self.assertIn("licensed media", CONTRACT)

    def test_both_sources_require_explicit_opt_in(self):
        self.assertIn("AUTONOMOUS_MERGE_V35=ENABLED", CONTRACT)
        self.assertEqual(READY.splitlines().count("AUTONOMOUS_MERGE_V35=ENABLED"), 1)
        self.assertIn("docs/AUTONOMOUS_INTEGRATION_POLICY_V35.md", CONTRACT)
        self.assertIn("docs/AUTONOMOUS_INTEGRATION_POLICY_V35.md", READY)
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

    def test_legacy_opt_in_is_disabled_without_erasing_source_provenance(self):
        self.assertEqual(READY.splitlines().count("AUTONOMOUS_MERGE_V34=DISABLED"), 1)
        self.assertNotIn("AUTONOMOUS_MERGE_V34=ENABLED", READY.splitlines())
        import importlib.util
        helper = ROOT / "docs/roadmap-v3.5/git_blob_provenance.py"
        spec = importlib.util.spec_from_file_location("v35_gov_blob", helper)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        blob = module.file_blob(ROOT / "docs" / "AUTONOMOUS_INTEGRATION_POLICY_V34.md")
        self.assertEqual(blob, "dd7784b17d44814dbf657b52f652980c4d494f49")

    def test_adoption_has_one_execution_cursor_and_preserves_inherited_scope(self):
        import json
        state = json.loads((ROOT / "docs/roadmap-v3.5/EXECUTION_STATE.json").read_text())
        self.assertIn("Governing roadmap: **V3.5**", CONTRACT)
        self.assertEqual(state["active_roadmap"], "3.5")
        self.assertEqual(state["next_action"], "RECONCILE_EXISTING_CODE_WIP")
        self.assertEqual(state["documentary_pr"], 146)
        self.assertEqual(state["inherited_counts"], {"lots": 24, "criteria": 141, "tickets": 140, "ux": 80, "scenarios": 437})
        self.assertEqual(state["qualification_inferred_by_adoption"], False)
        self.assertTrue(state["handoff"]["producer"]["expected_is_enabled"])
        self.assertFalse(state["handoff"]["design"]["expected_is_enabled"])
        self.assertIn("Design task is PAUSED by owner instruction", CONTRACT)
        self.assertIn("later independent scheduled review cycle remains mandatory", CONTRACT)
        import hashlib
        for name, expected_role in (("producer", "single code producer with bounded integration"), ("design", "read-only improvement and quality review")):
            handoff = state["handoff"][name]
            contract = ROOT / "docs/roadmap-v3.5" / handoff["contract"]
            self.assertEqual(hashlib.sha256(contract.read_text(encoding="utf-8").encode("utf-8")).hexdigest(), handoff["contract_sha256"])
            self.assertRegex(handoff["bootstrap_sha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(handoff["role"], expected_role)
        snapshot = json.loads((ROOT / "docs/roadmap-v3.5/RUN_STATE.json").read_text())
        self.assertEqual(snapshot["record_role"], "SEALED_PRE_ADOPTION_CANDIDATE_SNAPSHOT")
        self.assertEqual(snapshot["current_state_after_promotion"], "EXECUTION_STATE.json")
        for name in ("MASTER_PRIORISE.md", "EXECUTION_PLAYBOOK.md", "CREATIVE_STUDIO_PRODUCT_CONTRACT.md", "SCENE_DECOMPOSITION_AND_RELIEF_CONTRACT.md", "UX_INTERACTION_AND_VISUAL_CONTRACT.md"):
            self.assertTrue((ROOT / "docs/roadmap-v3.5" / name).is_file(), name)
        decision = (ROOT / "docs/ROADMAP_PROMOTION_v3_5.md").read_text()
        self.assertIn("rollback", decision)
        self.assertIn(state["adopted_design_commit"], decision)
        self.assertIn("DRAFT-only", POLICY)

    def test_explicit_prompt_guard_and_no_second_producer(self):
        self.assertIn("producer prompt must target V3.5", CONTRACT)
        self.assertIn("not an opt-in created by renaming V34", CONTRACT)
        self.assertIn("must not write an old candidate branch", CONTRACT)
        self.assertIn("No widening of paths", CONTRACT)
        for name in ("AGENTS.md", ".automation/**", ".github/**", "docs/**", "source-releases/**"):
            self.assertIn(name, POLICY)


if __name__ == "__main__":
    unittest.main()
