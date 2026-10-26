"""No actual GitHub writes: test the exact-head, conservative PR integration gate."""
import copy
import importlib.util
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "integration_eligibility",
    Path(__file__).resolve().parents[1] / "tools" / "integration_eligibility.py",
)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)
HEAD = "a" * 40
MAIN = "b" * 40


def base_snapshot():
    return {
        "schema": 1,
        "repo": "frenndak/SmartSVG-Studio",
        "main_sha": MAIN,
        "checked_main_sha": MAIN,
        "checked_head_sha": HEAD,
        "pr": {
            "number": 14, "state": "open", "draft": False,
            "mergeable": True,
            "user": {"login": "author"},
            "head": {"sha": HEAD, "ref": "feat/g1-2"},
            "base": {"ref": "main", "sha": MAIN},
        },
        "comparison": {"status": "ahead", "ahead_by": 2, "behind_by": 0},
        "workflow_runs": [
            {"id": 10, "name": name, "head_sha": HEAD, "status": "completed",
             "conclusion": "success", "created_at": "2026-10-26T06:00:00Z", "run_attempt": 1,
             "event": "workflow_dispatch", "head_branch": "feat/g1-2"}
            for name in gate.REQUIRED
        ],
        "reviews": [{
            "state": "APPROVED", "commit_id": HEAD,
            "submitted_at": "2026-10-26T06:10:00Z",
            "user": {"login": "independent-reviewer", "type": "User"},
        }],
        "audit_comments": [{"body": "SMARTSVG_AUDIT_V1\nPR=14\nHEAD=" + HEAD +
                            "\nVERDICT=GO_POUR_REVUE_INTEGRATION\n"}],
    }


class IntegrationGateTests(unittest.TestCase):
    def setUp(self):
        self.data = base_snapshot()

    def blockers(self):
        return gate.assess(self.data)["blockers"]

    def test_eligible_still_does_not_authorize_automatic_merge(self):
        decision = gate.assess(self.data)
        self.assertEqual(decision["status"], "ELIGIBLE_FOR_MAINTAINER_MERGE_REVIEW")
        self.assertFalse(decision["automatic_merge_allowed"])

    def test_draft_never_eligible(self):
        self.data["pr"]["draft"] = True
        self.assertIn("PR_DRAFT", self.blockers())

    def test_stacked_branch_cannot_skip_parent(self):
        self.data["pr"]["base"]["ref"] = "feat/g1-1"
        self.assertIn("STACK_PARENT_PENDING", self.blockers())

    def test_main_drift_and_conflict_block(self):
        self.data["comparison"]["behind_by"] = 1
        self.data["pr"]["mergeable"] = None
        self.assertIn("MAIN_ANCESTRY_UNPROVEN", self.blockers())
        self.assertIn("MERGEABILITY_UNKNOWN_OR_FALSE", self.blockers())

    def test_pending_newer_run_overrides_success(self):
        self.data["workflow_runs"].append({
            "id": 20, "name": gate.REQUIRED[0], "head_sha": HEAD,
            "status": "in_progress", "conclusion": None,
            "created_at": "2026-10-26T06:40:00Z", "run_attempt": 1,
            "event": "workflow_dispatch", "head_branch": "feat/g1-2",
        })
        self.assertIn("CI_NOT_SUCCESS:" + gate.REQUIRED[0], self.blockers())

    def test_pr_merge_ref_ci_is_not_direct_branch_proof(self):
        for run in self.data["workflow_runs"]:
            run["event"] = "pull_request"
        self.assertIn("CI_NOT_SUCCESS:" + gate.REQUIRED[0], self.blockers())
        self.assertIn("CI_NOT_SUCCESS:" + gate.REQUIRED[1], self.blockers())

    def test_wrong_checked_out_branch_does_not_count(self):
        self.data["workflow_runs"][0]["head_branch"] = "main"
        self.assertIn("CI_NOT_SUCCESS:" + gate.REQUIRED[0], self.blockers())

    def test_later_no_go_revokes_earlier_go(self):
        self.data["audit_comments"].append({"body": (
            "SMARTSVG_AUDIT_V1\nPR=14\nHEAD=" + HEAD +
            "\nVERDICT=NO_GO\n")})
        self.assertIn("INDEPENDENT_AUDIT_GO_MISSING", self.blockers())

    def test_failure_and_wrong_head_do_not_count_as_success(self):
        self.data["workflow_runs"][1]["head_sha"] = "c" * 40
        self.assertIn("CI_NOT_SUCCESS:" + gate.REQUIRED[1], self.blockers())

    def test_review_stale_or_from_author_not_approval(self):
        self.data["reviews"][0]["commit_id"] = "c" * 40
        self.assertIn("INDEPENDENT_GITHUB_APPROVAL_MISSING", self.blockers())
        self.data["reviews"][0]["commit_id"] = HEAD
        self.data["reviews"][0]["user"]["login"] = "author"
        self.assertIn("INDEPENDENT_GITHUB_APPROVAL_MISSING", self.blockers())

    def test_changes_requested_supersedes_approval(self):
        reviewer = self.data["reviews"][0]["user"]
        self.data["reviews"].append({
            "state": "CHANGES_REQUESTED", "commit_id": HEAD,
            "user": reviewer, "submitted_at": "2026-10-26T06:15:00Z",
        })
        self.assertIn("UNRESOLVED_CHANGE_REQUEST", self.blockers())
        self.assertIn("INDEPENDENT_GITHUB_APPROVAL_MISSING", self.blockers())

    def test_audit_no_go_or_outdated_sha(self):
        self.data["audit_comments"][0]["body"] = (
            "SMARTSVG_AUDIT_V1\nPR=14\nHEAD=" + "c" * 40 +
            "\nVERDICT=GO_POUR_REVUE_INTEGRATION")
        self.assertIn("INDEPENDENT_AUDIT_GO_MISSING", self.blockers())

    def test_stale_snapshot_rejected(self):
        self.data["checked_head_sha"] = "d" * 40
        self.assertIn("STALE_SNAPSHOT", self.blockers())

    def test_wrong_repo_or_malformed_identity(self):
        self.data["repo"] = "wrong-owner/wrong-repo"
        self.assertIn("REPO_MISMATCH", self.blockers())
        self.data["pr"]["head"]["sha"] = "not-a-sha"
        self.assertIn("IDENTITY_INVALID", self.blockers())

    def test_snapshots_are_not_mutated(self):
        original = copy.deepcopy(self.data)
        gate.assess(self.data)
        self.assertEqual(self.data, original)


if __name__ == "__main__":
    unittest.main()
