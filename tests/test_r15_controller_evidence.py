import unittest
from copy import deepcopy
from tools.smartsvg_controller_decision import Status
from tools.smartsvg_controller_evidence import SPECS, Work, dispatch, step_receipts

H = "a" * 40

def entry(name):
    path, job, step = SPECS[name]
    return {"run": {"path": path, "head_sha": H, "event": "pull_request",
                    "id": 1, "run_attempt": 2, "status": "completed", "conclusion": "success"},
            "jobs": [{"name": job, "head_sha": H, "run_id": 1, "run_attempt": 2,
                      "id": 3, "status": "completed", "conclusion": "success",
                      "steps": [{"name": step, "number": 4, "status": "completed",
                                 "conclusion": "success"}]}]}

def evidence(runs):
    return next(x for x in step_receipts(H, runs) if x.name == "g0")

class EvidenceTests(unittest.TestCase):
    def test_exact_step_not_test_qualification(self):
        x = evidence([entry("g0")])
        self.assertEqual(x.status, Status.PASS)
        self.assertEqual(x.qualification, "STEP_ONLY")
        self.assertEqual((x.run_id, x.attempt, x.job_id, x.step_number), (1, 2, 3, 4))

    def test_stale_head_attempt_and_event(self):
        for layer, key, value in (("run", "head_sha", "b"*40),
                                  ("run", "event", "push"),
                                  ("job", "run_attempt", 1),
                                  ("job", "head_sha", "b"*40)):
            x = entry("g0")
            target = x["run"] if layer == "run" else x["jobs"][0]
            target[key] = value
            self.assertEqual(evidence([x]).status, Status.UNKNOWN)

    def test_step_skipped_failed_pending_and_cancelled(self):
        for status, conclusion, expected in (
            ("completed", "skipped", Status.SKIP),
            ("completed", "failure", Status.FAIL),
            ("in_progress", None, Status.PENDING),
            ("completed", "cancelled", Status.UNKNOWN)):
            x = entry("g0")
            x["jobs"][0]["steps"][0].update(status=status, conclusion=conclusion)
            self.assertEqual(evidence([x]).status, expected)

    def test_ambiguity_and_parent_failure(self):
        x = entry("g0")
        self.assertEqual(evidence([x, deepcopy(x)]).status, Status.UNKNOWN)
        x["jobs"][0]["steps"] *= 2
        self.assertEqual(evidence([x]).status, Status.UNKNOWN)
        x = entry("g0")
        x["run"]["conclusion"] = "failure"
        self.assertEqual(evidence([x]).status, Status.FAIL)

    def test_role_dispatch(self):
        q = (Work(192, "B", "REVIEW"), Work(195, "A", "REVIEW"),
             Work(194, "B", "FIX_REQUIRED"))
        self.assertEqual(dispatch("A", q, 3), (192, "REVIEW"))
        self.assertEqual(dispatch("B", q, 3), (195, "REVIEW"))
        self.assertEqual(dispatch("B", q[2:], 3), (194, "FIX_REQUIRED"))

    def test_never_merge_or_open_on_unknown_queue(self):
        q = (Work(195, "A", "SHADOW_QUALIFIED"),)
        self.assertEqual(dispatch("A", q, 3), (None, "CHECKPOINT_WAIT"))
        self.assertEqual(dispatch("B", q, 3), (195, "QUALIFY_ONLY"))
        self.assertEqual(dispatch("B", (), 2), (None, "CHECKPOINT_WAIT"))
        self.assertEqual(dispatch("B", (), 2, queue_complete=True), (None, "DEVELOP"))
        self.assertEqual(dispatch("A", (Work(192, "B", "REVIEW", False),), 3),
                         (None, "CHECKPOINT_WAIT"))

    def test_roadmap_rank_breaks_review_tie_not_role_or_action(self):
        q=(Work(192,"B","REVIEW",roadmap_rank=4),
           Work(194,"B","REVIEW",roadmap_rank=3),
           Work(195,"A","FIX_REQUIRED",roadmap_rank=1))
        self.assertEqual(dispatch("A",q,3),(194,"REVIEW"))
        self.assertEqual(dispatch("B",q,3),(None,"CHECKPOINT_WAIT"))

    def test_roadmap_does_not_override_existing_action_priority_or_availability(self):
        q=(Work(192,"B","REVIEW",False,1),Work(194,"B","REVIEW",True,4),
           Work(195,"A","FIX_REQUIRED",True,1))
        self.assertEqual(dispatch("A",q,3),(194,"REVIEW"))
        self.assertEqual(dispatch("A",q[2:],3),(195,"FIX_REQUIRED"))

    def test_unranked_legacy_tie_is_stable(self):
        q=(Work(194,"B","REVIEW"),Work(192,"B","REVIEW"))
        self.assertEqual(dispatch("A",q,3),(192,"REVIEW"))
