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

    def test_invalid_ci_identity_is_neither_progress_nor_an_actionable_wait(self):
        for field, value in (("run", 0), ("job", -1), ("step", 0),
                             ("job_run", True), ("job_attempt", True)):
            for status in ("completed", "in_progress"):
                with self.subTest(field=field, value=value, status=status):
                    packet = entry("g0")
                    run, job = packet["run"], packet["jobs"][0]
                    run["run_attempt"] = job["run_attempt"] = 1
                    step = job["steps"][0]
                    if field == "run":
                        run.update(id=value, status=status)
                        job["run_id"] = value
                    elif field == "step":
                        step.update(number=value, status=status)
                    else:
                        key = {"job": "id", "job_run": "run_id", "job_attempt": "run_attempt"}[field]
                        job.update({key: value, "status": status})
                    receipt = evidence([packet])
                    self.assertEqual(receipt.status, Status.UNKNOWN)
                    self.assertIsNone(receipt.step_number)

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

    def test_ci_inspection_is_read_only_for_either_role(self):
        for writer in ("A", "B"):
            q = (Work(195, writer, "CI_INSPECT"),)
            for role in ("A", "B"):
                with self.subTest(writer=writer, role=role):
                    self.assertEqual(dispatch(role, q, 3), (195, "CI_INSPECT"))

    def test_local_block_preserves_independent_ci_at_full_wip(self):
        q = (Work(192, "B", "REVIEW", available=False),
             Work(193, "B", "CI_INSPECT"),
             Work(194, "B", "FIX_REQUIRED"))
        self.assertEqual(dispatch("A", q, 3), (193, "CI_INSPECT"))

    def test_ci_fallback_does_not_change_mutation_or_qualification_roles(self):
        for action in ("FIX_REQUIRED", "RECONCILE", "VERIFY_FINDING",
                       "QUALIFY_ONLY", "SHADOW_QUALIFIED"):
            self.assertEqual(dispatch("A", (Work(195, "B", action),), 3),
                             (None, "CHECKPOINT_WAIT"))
        self.assertEqual(dispatch("A", (Work(195, "B", "CI_INSPECT", False),), 2),
                         (None, "CHECKPOINT_WAIT"))
        self.assertEqual(dispatch("A", (), 3, queue_complete=True),
                         (None, "CHECKPOINT_WAIT"))

    def test_cross_role_ci_preserves_review_and_repair_priority(self):
        q = (Work(192, "B", "CI_INSPECT", roadmap_rank=1),
             Work(193, "A", "FIX_REQUIRED", roadmap_rank=4),
             Work(194, "B", "REVIEW", roadmap_rank=5))
        self.assertEqual(dispatch("A", q, 3), (194, "REVIEW"))
        self.assertEqual(dispatch("A", q[:2], 3), (193, "FIX_REQUIRED"))
