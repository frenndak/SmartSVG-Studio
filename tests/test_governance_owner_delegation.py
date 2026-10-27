"""Owner-authorized interactive integration must never enable scheduled self-merges."""
from pathlib import Path
import unittest

CONTRACT=(Path(__file__).resolve().parents[1]/"AGENTS.md").read_text(encoding="utf-8")

class OwnerDelegationContractTests(unittest.TestCase):
    def test_public_repo_status_and_sensitive_assets(self):
        self.assertIn("intentionally **public**", CONTRACT)
        self.assertNotIn("this private repository", CONTRACT)
        self.assertIn("Do not commit API keys", CONTRACT)
        self.assertIn("licensed media", CONTRACT)

    def test_no_autonomous_scheduled_merge_or_protected_edits(self):
        self.assertIn("Scheduled AI agents must submit **draft PRs only**", CONTRACT)
        self.assertIn("must not approve or merge them autonomously", CONTRACT)
        self.assertIn("scheduled agents remain prohibited from editing protected paths", CONTRACT)
        self.assertIn("Never modify `AGENTS.md`", CONTRACT)

    def test_delegated_live_session_still_requires_evidence(self):
        for phrase in ("live, user-directed ChatGPT session",
                       "documented counter-expertise", "fresh green relevant CI",
                       "current main/HEAD comparison",
                       "reversible integration plan",
                       "no unresolved blockers",
                       "does not manufacture an independent GitHub APPROVED"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, CONTRACT)

    def test_frozen_sources_and_cut_claims_remain_protected(self):
        for fragment in ("docs/ROADMAP_MASTER_v3_2.md",
                         "V21.14.1", "V21.15.2",
                         "actual GPU RTX 3070",
                         "physical cut measurements"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, CONTRACT)

if __name__=="__main__":
    unittest.main()
