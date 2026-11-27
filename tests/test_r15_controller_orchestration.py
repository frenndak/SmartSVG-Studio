import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from tools.smartsvg_controller_orchestration import Scope, build_plan, reserve_next
from tools.smartsvg_controller_recovery import RecoveryJournal

NOW = datetime(2026, 11, 25, 15, 0, tzinfo=timezone.utc)
M, P, H, J, K = (c * 40 for c in "abcde")
REPO = "frenndak/SmartSVG-Studio"


def row(n, head):
    return {"pr": {"number": n, "state": "open", "head": {"sha": head,
            "repo": {"full_name": REPO}}, "base": {"ref": "main",
            "repo": {"full_name": REPO}}, "user": {"login": "frenndak"},
            "draft": False, "mergeable": True}, "branch": {"status": "MATCH", "sha": head}, "runs": [],
            "comments": [{"body": "APPROVED by A"}], "reviews": []}


def snapshot():
    return {"qualification": "RAW_ONLY", "started_at": NOW.isoformat(),
            "finished_at": NOW.isoformat(), "main": {"commit": {"sha": M}},
            "policy_blob": P, "candidates": [row(192, H), row(195, J), row(196, K)]}


SCOPES = (Scope(192, H, "B", True), Scope(195, J, "A", True),
          Scope(196, K, "OWNER", False))


class OrchestrationTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.j = RecoveryJournal(Path(tmp.name) / "state.db", lambda: 100)
        self.addCleanup(self.j.close)

    def plan(self, data=None, scopes=SCOPES, now=NOW):
        return build_plan(data or snapshot(), scopes, now=now)

    def test_real_module_routing_and_scope(self):
        p = self.plan()
        self.assertTrue(p.queue_complete)
        self.assertEqual(p.code_wip, 2)
        self.assertEqual([x.action for x in p.proposals],
                         ["REVIEW", "REVIEW", "OWNER_REVIEW"])
        a = reserve_next(p, "A", self.j, now=NOW)
        b = reserve_next(p, "B", self.j, now=NOW)
        self.assertEqual((a.number, b.number), (192, 195))
        self.assertEqual(a.recovery_advice, "RESUME_CHECKPOINT")
        self.assertIsNone(reserve_next(p, "A", self.j, now=NOW))

    def test_resume_and_policy_change_invalidation(self):
        p = self.plan()
        a = reserve_next(p, "A", self.j, now=NOW)
        args = ("pr:192", a.context_key, "A", a.fence)
        self.assertTrue(self.j.save(*args, "consumer inspected"))
        self.assertTrue(self.j.release(*args))
        b = reserve_next(p, "A", self.j, now=NOW)
        self.assertEqual(b.checkpoint, "consumer inspected")
        self.j.release("pr:192", b.context_key, "A", b.fence)
        d = snapshot()
        d["policy_blob"] = J
        c = reserve_next(self.plan(d), "A", self.j, now=NOW)
        self.assertNotEqual(c.context_key, a.context_key)
        self.assertEqual(c.checkpoint, "")

    def test_pending_ci_yields_to_independent_inspection_but_remains_available(self):
        from dataclasses import replace
        from tools.smartsvg_controller_evidence import SPECS, StepReceipt, Status

        original = self.plan()
        steps = tuple(StepReceipt(name, Status.PENDING if name == "g0" else Status.PASS,
                                  run_id=1, attempt=1) for name in SPECS)
        waiting = replace(original.proposals[0], action="CI_INSPECT", steps=steps)
        independent = replace(original.proposals[1], action="INSPECT")
        plan = replace(original, proposals=(waiting, independent), code_wip=3)
        first = reserve_next(plan, "A", self.j, now=NOW, roadmap_ranks={waiting.number: 1})
        second = reserve_next(plan, "B", self.j, now=NOW)
        self.assertEqual((first.number, first.action), (independent.number, "INSPECT"))
        self.assertEqual((second.number, second.action), (waiting.number, "CI_INSPECT"))

    def test_mixed_or_incomplete_ci_remains_a_diagnostic_priority(self):
        from dataclasses import replace
        from tools.smartsvg_controller_evidence import SPECS, StepReceipt, Status

        original = self.plan()
        pending = tuple(StepReceipt(name, Status.PENDING, run_id=1, attempt=1)
                        for name in SPECS)
        cases = [pending[:-1], (*pending[:-1], pending[0]),
                 (replace(pending[0], run_id=None), *pending[1:]),
                 (replace(pending[0], attempt=0), *pending[1:])]
        for status in (Status.UNKNOWN, Status.SKIP, Status.FAIL):
            cases.append((replace(pending[0], status=status), *pending[1:]))
        for steps in cases:
            with self.subTest(steps=steps):
                diagnostic = replace(original.proposals[0], action="CI_INSPECT", steps=steps)
                other = replace(original.proposals[1], action="INSPECT")
                plan = replace(original, proposals=(diagnostic, other))
                choice = reserve_next(plan, "A", self.j, now=NOW)
                self.assertEqual((choice.number, choice.action), (diagnostic.number, "CI_INSPECT"))
                self.j.release("pr:" + str(choice.number), choice.context_key, "A", choice.fence)

    def test_contention_falls_through(self):
        d = snapshot()
        d["candidates"].append(row(194, K))
        p = self.plan(d, SCOPES + (Scope(194, K, "B", True),))
        a = reserve_next(p, "A", self.j, now=NOW)
        b = reserve_next(p, "A", self.j, now=NOW)
        self.assertEqual((a.number, b.number), (192, 194))

    def test_unknown_and_changed_head_not_dispatched(self):
        p = self.plan(scopes=SCOPES[1:])
        self.assertFalse(p.queue_complete)
        self.assertEqual(p.unknown, (192,))
        self.assertEqual(p.code_wip, 2)
        self.assertIsNone(reserve_next(p, "A", self.j, now=NOW))
        d = snapshot()
        d["candidates"][0]["pr"]["head"]["sha"] = K
        self.assertIn(192, self.plan(d).unknown)

    def test_stale_future_and_duplicate_rejected(self):
        for delta in (timedelta(minutes=6), timedelta(seconds=-1)):
            with self.assertRaises(ValueError):
                self.plan(now=NOW + delta)
        with self.assertRaises(ValueError):
            reserve_next(self.plan(), "A", self.j, now=NOW + timedelta(minutes=6))
        with self.assertRaises(ValueError):
            self.plan(scopes=SCOPES + (SCOPES[0],))

    def test_failed_step_own_writer_not_cross_review(self):
        d = snapshot()
        d["candidates"][0]["runs"] = [{"run": {
            "path": ".github/workflows/g0-admission-tests.yml", "head_sha": H,
            "event": "pull_request", "id": 1, "run_attempt": 1,
            "status": "completed", "conclusion": "failure"}, "jobs": []}]
        p = self.plan(d)
        self.assertEqual(p.proposals[0].action, "FIX_REQUIRED")
        self.assertIsNone(reserve_next(p, "A", self.j, now=NOW))
        b = reserve_next(p, "B", self.j, now=NOW)
        self.assertEqual(b.number, 195)  # cross review first
        b2 = reserve_next(p, "B", self.j, now=NOW)
        self.assertEqual((b2.number, b2.action), (192, "FIX_REQUIRED"))

    def test_divergent_branch_does_not_block_other_pr(self):
        d = snapshot()
        d["candidates"][0]["branch"] = {"status": "DIVERGED", "sha": K}
        p = self.plan(d)
        self.assertIn(192, p.unknown)
        self.assertFalse(p.queue_complete)
        self.assertIsNone(reserve_next(p, "A", self.j, now=NOW))
        b = reserve_next(p, "B", self.j, now=NOW)
        self.assertEqual(b.number, 195)

    def test_stagnation_routes_independent_work_after_head_change(self):
        from dataclasses import replace
        from tools.smartsvg_controller_orchestration import routing_incident

        plan = self.plan()
        first = reserve_next(plan, "A", self.j, now=NOW)
        proposal = plan.proposals[0]
        for n in (1, 2):
            self.assertTrue(self.j.record_incident_cycle(
                "pr:192", first.context_key, "A", first.fence,
                incident=routing_incident(plan, proposal), run=str(n),
                ordinal=n, outcome="NO_PROGRESS"))
        self.j.release("pr:192", first.context_key, "A", first.fence)
        changed = replace(proposal, head=K)
        other = replace(proposal, number=194)
        plan = replace(plan, proposals=(changed, other))
        alternative = reserve_next(plan, "A", self.j, now=NOW)
        self.assertEqual(alternative.number, 194)
        # With that alternative reserved, the original PR remains actionable.
        fallback = reserve_next(plan, "A", self.j, now=NOW)
        self.assertEqual((fallback.number, fallback.recovery_advice), (192, "CHANGE_STRATEGY"))
        self.assertNotEqual(first.context_key, fallback.context_key)
        self.assertEqual(fallback.checkpoint, "")
        self.j.release("pr:192", fallback.context_key, "A", fallback.fence)
        fresh = reserve_next(replace(plan, policy_blob=H), "A", self.j, now=NOW)
        self.assertEqual((fresh.number, fresh.recovery_advice), (192, "RESUME_CHECKPOINT"))

    def test_wait_is_local_to_current_context_and_never_transfers_writer(self):
        from dataclasses import replace
        plan = self.plan()
        first = reserve_next(plan, "A", self.j, now=NOW)
        args = ("pr:192", first.context_key, "A", first.fence)
        self.j.record_cycle(*args, run="wait", ordinal=1, outcome="WAIT_CI")
        self.j.release(*args)
        own_review = replace(plan.proposals[0], number=198, writer="A")
        other = replace(plan.proposals[0], number=194)
        plan = replace(plan, proposals=(plan.proposals[0], own_review, other))
        alternative = reserve_next(plan, "A", self.j, now=NOW)
        self.assertEqual(alternative.number, 194)
        waiting = reserve_next(plan, "A", self.j, now=NOW)
        self.assertEqual((waiting.number, waiting.recovery_advice), (192, "OTHER_ACTIONABLE_WORK"))
        self.j.release("pr:192", waiting.context_key, "A", waiting.fence)
        changed = replace(plan.proposals[0], head=K)
        resumed = reserve_next(replace(plan, proposals=(changed, own_review)), "A", self.j, now=NOW)
        self.assertEqual((resumed.number, resumed.recovery_advice), (192, "RESUME_CHECKPOINT"))
