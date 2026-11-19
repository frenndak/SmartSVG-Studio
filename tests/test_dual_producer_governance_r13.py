"""R13 owner-governance regression tests; never auto-merge edits to this file.

These assertions verify textual authorization consistency, not scheduler activation,
actual cross-review independence, CI success, or access to Windows/Cricut hardware.
"""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
AGENTS = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
READY = (ROOT / ".automation/READY").read_text(encoding="utf-8")
POLICY = (ROOT / "docs/AUTONOMOUS_INTEGRATION_POLICY_V35.md").read_text(encoding="utf-8")
CONTRACT = (ROOT / "docs/roadmap-v3.5/DUAL_PRODUCER_R13_CONTRACT.md").read_text(encoding="utf-8")
STATE = json.loads((ROOT / "docs/roadmap-v3.5/EXECUTION_STATE.json").read_text(encoding="utf-8"))


class DualProducerR13OwnerGovernanceTests(unittest.TestCase):
    def test_explicit_and_unique_owner_markers(self):
        for marker in (
            "AUTONOMOUS_MERGE_V34=DISABLED",
            "AUTONOMOUS_MERGE_V35=ENABLED",
            "DUAL_PRODUCER_V35=AUTHORIZED",
            "R13_MERGE_EXECUTOR=AGENT_B",
        ):
            with self.subTest(marker=marker):
                self.assertEqual(READY.splitlines().count(marker), 1)
                self.assertIn(marker, AGENTS)
        self.assertNotIn("AUTONOMOUS_MERGE_V34=ENABLED", READY.splitlines())
        self.assertNotIn("DUAL_PRODUCER_V35=ENABLED", READY.splitlines())

    def test_one_merge_executor_and_two_scheduled_roles(self):
        self.assertIn("Only B executes squash merges", AGENTS)
        self.assertIn("unique exécuteur", POLICY)
        self.assertIn("ne fusionne plus après passation R13", POLICY)
        self.assertIn("Un agent ne peut être seul réviseur de son propre correctif", POLICY)
        self.assertIn("même identité GitHub", CONTRACT)
        handoff = STATE["handoff"]["r13"]
        self.assertEqual(handoff["producer_a_task_id"], "6ae27963fd848191a1053dfc486e8eb4")
        self.assertIsNone(handoff["producer_b_task_id"])
        self.assertEqual(handoff["merge_executor"], "B_ONLY_AFTER_VERIFIED_HANDOFF")
        self.assertEqual(handoff["initial_code_wip_max"], 3)
        self.assertEqual(handoff["merges_per_b_cycle_max"], 1)

    def test_fail_closed_activation_and_preserved_code_only_scope(self):
        for fragment in (
            "NO_MERGE", "DRAFT-only", "expected_head_sha", "G0",
            "post-merge", "writer", "HEAD",
        ):
            with self.subTest(fragment=fragment):
                self.assertTrue(fragment in CONTRACT or fragment in POLICY)
        for excluded in (
            "AGENTS.md", ".automation/**", ".github/**", "docs/**",
            "source-releases/**", "engine/requirements.txt",
            "tests/test_governance_owner_delegation.py",
            "tests/test_dual_producer_governance_r13.py",
        ):
            with self.subTest(excluded=excluded):
                self.assertIn(excluded, POLICY)
        self.assertEqual(STATE["handoff"]["r13"]["missing_handoff_policy"], "DRAFT_ONLY")
        self.assertEqual(STATE["inherited_counts"], {
            "lots": 24, "criteria": 141, "tickets": 140, "ux": 80, "scenarios": 437
        })


if __name__ == "__main__":
    unittest.main()
