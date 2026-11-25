import unittest
from dataclasses import replace
from tools.smartsvg_controller_decision import (
    Candidate, Check, Context, Decision, REQUIRED, Review, Status,
    choose_work, decide,
)

H, M, P = "a"*40, "b"*40, "c"*40

class DecisionTests(unittest.TestCase):
    def setUp(self):
        self.ctx = Context(M, P, True, True, True, True, Status.PASS, M, True)
        checks = tuple(Check(k, H, Status.PASS, True, "run/" + k)
                       for k in sorted(REQUIRED))
        self.pr = Candidate(195, H, "A", True, True, True, False, True,
                            False, checks, Review(H, M, "B", True, True, "review/1"))
    def action(self, pr=None, ctx=None):
        return decide(ctx or self.ctx, pr or self.pr).action
    def test_qualified_is_shadow_only(self):
        self.assertEqual(decide(self.ctx, self.pr),
                         Decision("SHADOW_QUALIFIED", ("NOT_AUTHORIZATION",)))
    def test_head_and_main_changes_invalidate_review(self):
        self.assertEqual(self.action(replace(self.pr, head="d"*40)), "REVIEW")
        self.assertEqual(self.action(ctx=replace(self.ctx, main="d"*40)), "REVIEW")
    def test_same_writer_and_same_cycle_rejected(self):
        for review in (replace(self.pr.review, reviewer="A"),
                       replace(self.pr.review, later_cycle=False)):
            self.assertEqual(self.action(replace(self.pr, review=review)), "REVIEW")
    def test_ci_skip_unknown_pending_unexecuted_and_stale_not_pass(self):
        for check in (replace(self.pr.checks[0], status=Status.SKIP),
                      replace(self.pr.checks[0], status=Status.UNKNOWN),
                      replace(self.pr.checks[0], status=Status.PENDING),
                      replace(self.pr.checks[0], executed=False),
                      replace(self.pr.checks[0], head="d"*40),
                      replace(self.pr.checks[0], receipt="")):
            self.assertEqual(self.action(replace(self.pr,
                checks=(check,) + self.pr.checks[1:])), "CI_REQUIRED")
    def test_ci_failure_and_adverse_review_prioritized(self):
        check = replace(self.pr.checks[0], status=Status.FAIL)
        self.assertEqual(self.action(replace(self.pr, review=None,
            checks=(check,) + self.pr.checks[1:])), "FIX_REQUIRED")
        self.assertEqual(self.action(replace(self.pr,
            review=replace(self.pr.review, favorable=False))), "FIX_REQUIRED")
    def test_mutable_merge_gates_fail_closed(self):
        for field in ("authority_verified", "scheduler_verified", "rules_verified",
                      "required_approval_satisfied"):
            self.assertEqual(self.action(ctx=replace(self.ctx, **{field: False})), "NO_MERGE")
        for status in (Status.PENDING, Status.FAIL, Status.SKIP, Status.UNKNOWN):
            self.assertEqual(self.action(ctx=replace(self.ctx, main_g0=status)), "NO_MERGE")
        self.assertEqual(self.action(ctx=replace(self.ctx, main_g0_sha=H)), "NO_MERGE")
        for pr in (replace(self.pr, mergeable=None), replace(self.pr, draft=True),
                   replace(self.pr, unresolved=None)):
            self.assertEqual(self.action(pr), "NO_MERGE")
    def test_scope_and_ambiguous_evidence(self):
        self.assertEqual(self.action(replace(self.pr, code_only=False)), "OWNER_REVIEW")
        self.assertEqual(self.action(replace(self.pr, same_repo=False)), "INSPECT")
        self.assertEqual(self.action(replace(self.pr, checks=self.pr.checks+
                                            (self.pr.checks[0],))), "INSPECT")
    def test_unknown_authority_does_not_stop_review(self):
        self.assertEqual(self.action(replace(self.pr, review=None),
                         replace(self.ctx, authority_verified=False)), "REVIEW")
    def test_wip_never_blocks_existing_review(self):
        queue = ((192, Decision("CI_REQUIRED")), (195, Decision("REVIEW")))
        self.assertEqual(choose_work(queue, 3), (195, "REVIEW"))
        self.assertEqual(choose_work(queue[:1], 3), (None, "CHECKPOINT_WAIT"))
        self.assertEqual(choose_work(queue[:1], 2), (None, "DEVELOP"))
