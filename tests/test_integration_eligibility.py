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


def file_info(filename):
    return {"filename": filename, "status": "modified", "sha": "d" * 40,
            "additions": 1, "deletions": 0, "changes": 1}


def base_snapshot():
    snapshot = {
        "schema": 1,
        "repo": "frenndak/SmartSVG-Studio",
        "main_sha": MAIN,
        "checked_main_sha": MAIN,
        "checked_head_sha": HEAD,
        "checked_base_ref": "main",
        "checked_base_sha": MAIN,
        "pr": {
            "number": 14, "state": "open", "draft": False,
            "mergeable": True, "changed_files": 2,
            "user": {"login": "author"},
            "head": {"sha": HEAD, "ref": "feat/g1-2"},
            "base": {"ref": "main", "sha": MAIN},
        },
        "comparison": {"status": "ahead", "ahead_by": 2, "behind_by": 0},
        "changed_files": [file_info("engine/smartsvg_core/example.py"),
                          file_info("engine/tests/test_example.py")],
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
        "audit_comments": [{"user": {"login": "independent-reviewer"}, "body": ""}],
    }
    snapshot["audit_comments"][0]["body"] = (
        "SMARTSVG_AUDIT_V1\nPR=14\nHEAD=" + HEAD +
        "\nBASE=main@" + MAIN +
        "\nDIFF_SHA256=" + gate.diff_identity(snapshot["changed_files"]) +
        "\nVERDICT=GO_POUR_REVUE_INTEGRATION\n"
    )
    return snapshot


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


    def test_workflow_only_change_needs_g0_not_cpu(self):
        self.data["changed_files"] = [
            file_info(".github/workflows/private-ai-development.yml"),
            file_info("tools/integration_eligibility.py"),
        ]
        self.data["workflow_runs"] = self.data["workflow_runs"][:1]
        self.assertEqual(self.blockers(), [])

    def test_engine_change_still_requires_cpu(self):
        self.data["workflow_runs"] = self.data["workflow_runs"][:1]
        self.assertIn("CI_NOT_SUCCESS:" + gate.REQUIRED[1], self.blockers())

    def test_missing_truncated_or_duplicate_file_list_fails_closed(self):
        self.data["changed_files"] = []
        self.assertIn("CHANGESET_UNVERIFIED", self.blockers())
        self.data["changed_files"] = [{"filename": "tools/helper.py"}]
        self.assertIn("CHANGESET_UNVERIFIED", self.blockers())
        self.data["changed_files"] = [{"filename": "tools/helper.py"},
                                       {"filename": "tools/helper.py"}]
        self.assertIn("CHANGESET_UNVERIFIED", self.blockers())

    def test_newer_pr_failure_rejects_old_dispatch_success(self):
        self.data["workflow_runs"].append({
            "id": 40, "name": gate.REQUIRED[0], "head_sha": HEAD,
            "status": "completed", "conclusion": "failure",
            "created_at": "2026-10-26T07:00:00Z",
            "event": "pull_request", "head_branch": "feat/g1-2",
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


    def test_audit_cannot_be_reused_after_retarget_with_same_head(self):
        receipt = self.data["audit_comments"][0]
        receipt["body"] = receipt["body"].replace(
            "BASE=main@" + MAIN, "BASE=feat/unmerged-parent@" + "c" * 40
        )
        self.assertIn("INDEPENDENT_AUDIT_GO_MISSING", self.blockers())

    def test_audit_cannot_be_reused_for_changed_file_manifest(self):
        self.data["changed_files"][0]["sha"] = "e" * 40
        self.assertIn("INDEPENDENT_AUDIT_GO_MISSING", self.blockers())

    def test_audit_must_be_authored_by_independent_approved_reviewer(self):
        self.data["audit_comments"][0]["user"]["login"] = "author"
        self.assertIn("INDEPENDENT_AUDIT_GO_MISSING", self.blockers())
        self.data["audit_comments"][0]["user"]["login"] = "unknown"
        self.assertIn("INDEPENDENT_AUDIT_GO_MISSING", self.blockers())

    def test_base_retarget_race_or_stale_base_is_rejected(self):
        self.data["checked_base_ref"] = "feat/old-parent"
        self.assertIn("STALE_SNAPSHOT", self.blockers())
        self.data["checked_base_ref"] = "main"
        self.data["pr"]["base"]["sha"] = "c" * 40
        self.assertIn("BASE_SHA_MISMATCH", self.blockers())
        self.assertIn("STALE_SNAPSHOT", self.blockers())

    def test_nul_and_missing_file_sha_fail_closed(self):
        self.data["changed_files"][0]["filename"] = "engine/\\x00evil.py"
        self.assertIn("CHANGESET_UNVERIFIED", self.blockers())
        self.data["changed_files"][0] = file_info("engine/good.py")
        self.data["changed_files"][0]["sha"] = None
        self.assertIn("CHANGESET_UNVERIFIED", self.blockers())

    def test_diff_identity_is_order_independent(self):
        expected = gate.diff_identity(self.data["changed_files"])
        self.data["changed_files"].reverse()
        self.assertEqual(gate.diff_identity(self.data["changed_files"]), expected)
        self.assertEqual(self.blockers(), [])

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
