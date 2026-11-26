import unittest
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import json
from tools.smartsvg_controller_review import TASKS, ReviewContext, correlate_review

H, M, P = "a"*40, "b"*40, "c"*40
T0, T1, T2, T3 = ("2026-11-25T12:00:00Z", "2026-11-25T13:00:00Z",
                  "2026-11-25T13:01:00Z", "2026-11-25T13:02:00Z")
CTX = ReviewContext(195, H, M, P, "A", "author-run", T0, T0)


def fixture(verdict="FAVORABLE"):
    c = {"id": 123, "user": {"login": "frenndak"}, "body": "Technical evidence",
         "issue_url": "https://api.github.com/repos/frenndak/SmartSVG-Studio/issues/195",
         "created_at": T2, "updated_at": T2}
    receipt = {"version": 1, "number": 195, "head": H, "main": M,
               "policy_blob": P, "role": "B", "run_id": "review-run",
               "author_run": "author-run", "comment_id": 123, "verdict": verdict,
               "comment_sha256": sha256(c["body"].encode()).hexdigest()}
    s = {"id": TASKS["B"], "is_enabled": True, "run_details": {
        "last_run": {"id": "review-run", "recorded_status": "completed",
                     "started_at": T1, "completed_at": T3},
        "latest_result": {"run_id": "review-run", "created_at": T3,
                          "content_truncated": False, "requires_user_action": False,
                          "is_failure_message": False,
                          "content_text": "R15_REVIEW_RECEIPT " + json.dumps(
                              receipt, sort_keys=True, separators=(",", ":"))}}}
    return s, c


class ReviewTests(unittest.TestCase):
    def test_correlation_never_native_approval(self):
        for verdict in ("FAVORABLE", "ADVERSE", "PARTIAL"):
            r = correlate_review(CTX, "B", *fixture(verdict))
            self.assertEqual(r.status, "CORRELATED_" + verdict)
            self.assertFalse(r.native_approval)

    def test_shared_identity_alone_and_wrong_task_rejected(self):
        s, c = fixture()
        s["id"] = TASKS["A"]
        self.assertEqual(correlate_review(CTX, "B", s, c).status, "UNKNOWN")
        s, c = fixture()
        s["run_details"]["latest_result"]["content_text"] = "Agent B APPROVED"
        self.assertEqual(correlate_review(CTX, "B", s, c).status, "UNKNOWN")

    def test_head_main_policy_and_same_writer_invalid(self):
        for ctx in (replace(CTX, head=M), replace(CTX, main=H),
                    replace(CTX, policy_blob=H), replace(CTX, writer="B")):
            self.assertEqual(correlate_review(ctx, "B", *fixture()).status, "UNKNOWN")

    def test_later_cycle_required(self):
        for ctx in (replace(CTX, author_completed_at=T1),
                    replace(CTX, author_run="review-run"),
                    replace(CTX, head_committed_at=T2)):
            self.assertEqual(correlate_review(ctx, "B", *fixture()).status, "UNKNOWN")

    def test_comment_tampering_edit_and_wrong_pr(self):
        for key, value in (("body", "different evidence"), ("updated_at", "2026-11-26T13:02:00Z"),
                           ("issue_url", "https://api.github.com/repos/frenndak/SmartSVG-Studio/issues/192")):
            s, c = fixture()
            c[key] = value
            self.assertEqual(correlate_review(CTX, "B", s, c).status, "UNKNOWN")

    def test_failure_truncation_and_duplicate_receipt(self):
        for key in ("content_truncated", "requires_user_action", "is_failure_message"):
            s, c = fixture()
            s["run_details"]["latest_result"][key] = True
            self.assertEqual(correlate_review(CTX, "B", s, c).status, "UNKNOWN")
        s, c = fixture()
        r = s["run_details"]["latest_result"]
        r["content_text"] += "\n" + r["content_text"]
        self.assertEqual(correlate_review(CTX, "B", s, c).status, "UNKNOWN")

    def test_malformed_inputs_never_approve(self):
        self.assertEqual(correlate_review(CTX, "B", {}, {}).status, "UNKNOWN")
        self.assertEqual(correlate_review(CTX, "B", *fixture("APPROVED")).status, "UNKNOWN")
