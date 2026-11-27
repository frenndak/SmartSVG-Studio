import unittest
from dataclasses import replace
from tools.smartsvg_controller_objectives import (
    Profile, Objective, Receipt, plan_objectives, next_objective,
)

M, P, R, H, J = (c * 40 for c in "abcde")
PROFILE = Profile("smartsvg", "frenndak/SmartSVG-Studio", "main", P, R)


def objective(key, deps=(), **kwargs):
    fields = dict(key=key, revision=H, role="A", criteria=("proof",),
                  dependencies=deps)
    fields.update(kwargs)
    return Objective(**fields)


def receipt(o, *, status="PASS", executed=True, digest="f"*64, **kwargs):
    fields = dict(profile=PROFILE, main=M, objective=o.key, revision=o.revision,
                  criterion=o.criteria[0], status=status, executed=executed, digest=digest)
    fields.update(kwargs)
    return Receipt(**fields)


class ObjectivePlannerTests(unittest.TestCase):
    def plan(self, *items, receipts=(), profile=PROFILE, main=M):
        return plan_objectives(profile, main, items, receipts)

    def by_key(self, p):
        return {a.objective: a for a in p.objectives}

    def test_exact_executed_receipt_observes_criterion_not_done(self):
        o = objective("one")
        plan = self.plan(o, receipts=(receipt(o),))
        self.assertEqual(plan.objectives[0].action, "CRITERIA_OBSERVED")
        self.assertFalse(plan.merge_authorized)
        self.assertFalse(plan.agent_work_executed)
        self.assertIsNone(next_objective(plan, "A"))

    def test_wrong_project_main_policy_roadmap_revision_or_unexecuted_ignored(self):
        o = objective("one")
        bad = (
            receipt(o, profile=replace(PROFILE, project="other")),
            receipt(o, profile=replace(PROFILE, repository="other/repo")),
            receipt(o, profile=replace(PROFILE, policy_blob=J)),
            receipt(o, profile=replace(PROFILE, roadmap_blob=J)),
            receipt(o, profile=replace(PROFILE, branch="other")),
            receipt(o, main=J), receipt(o, revision=J),
            receipt(o, executed=False),
        )
        plan = self.plan(o, receipts=bad)
        self.assertEqual(plan.ignored_receipts, len(bad))
        self.assertEqual(next_objective(plan, "A").action, "VERIFY_CRITERION")

    def test_wait_does_not_stop_independent_work(self):
        a, b, c = objective("a"), objective("b", ("a",)), objective("c")
        p = self.plan(a, b, c, receipts=(receipt(a, status="WAIT", executed=False),))
        self.assertEqual(self.by_key(p)["a"].action, "WAIT_EVIDENCE")
        self.assertEqual(self.by_key(p)["b"].action, "WAIT_DEPENDENCY")
        self.assertEqual(next_objective(p, "A").objective, "c")

    def test_preparation_explicit_and_not_qualification(self):
        a = objective("a", role="B")
        b = objective("b", ("a",), preparation_allowed=True)
        p = self.plan(a, b, receipts=(receipt(b),))
        self.assertEqual(next_objective(p, "A").action, "PREPARE_INDEPENDENT")
        self.assertEqual(next_objective(p, "B").objective, "a")
        p = self.plan(a, b, receipts=(receipt(a, digest="a"*64), receipt(b)))
        self.assertEqual(self.by_key(p)["b"].action, "CRITERIA_OBSERVED")

    def test_cycle_and_unknown_block_only_affected_descendants(self):
        items = (objective("a", ("b",)), objective("b", ("a",)),
                 objective("c", ("a",)), objective("d", ("missing",)),
                 objective("e", ("d",)), objective("healthy"))
        p = self.plan(*items)
        rows = self.by_key(p)
        self.assertEqual(rows["a"].blockers, ("DEPENDENCY_CYCLE",))
        self.assertEqual(rows["b"].blockers, ("DEPENDENCY_CYCLE",))
        self.assertEqual(rows["c"].blockers, ("BLOCKED:a",))
        self.assertEqual(rows["d"].blockers, ("UNKNOWN:missing",))
        self.assertEqual(rows["e"].blockers, ("BLOCKED:d",))
        self.assertEqual(next_objective(p, "A").objective, "healthy")

    def test_self_cycle_isolated(self):
        p = self.plan(objective("a", ("a",)), objective("b"))
        self.assertEqual(self.by_key(p)["a"].action, "BLOCKED_GRAPH")
        self.assertEqual(next_objective(p, "A").objective, "b")

    def test_failed_criterion_preferred_over_unknown(self):
        a, b = objective("a"), objective("b")
        p = self.plan(a, b, receipts=(receipt(b, status="FAIL"),))
        self.assertEqual(next_objective(p, "A").objective, "b")
        self.assertEqual(next_objective(p, "A").action, "REPAIR_CRITERION")

    def test_conflicting_or_cross_criterion_receipts_not_pass(self):
        a = objective("a", criteria=("one", "two"))
        first = receipt(a)
        reused = receipt(a, criterion="two")
        p = self.plan(a, receipts=(first, reused))
        self.assertEqual(next_objective(p, "A").criteria, ("one", "two"))
        conflict = receipt(a, status="FAIL", digest="a"*64)
        p = self.plan(a, receipts=(first, conflict))
        self.assertEqual(next_objective(p, "A").criteria, ("one", "two"))

    def test_critical_path_and_age_rank_within_action_class(self):
        a, b, c = objective("a"), objective("b"), objective("c", ("b",))
        self.assertEqual(next_objective(self.plan(a,b,c), "A").objective, "b")
        old = replace(a, age=20)
        self.assertEqual(next_objective(self.plan(old,b,c), "A").objective, "a")

    def test_role_separation_and_input_order_independence(self):
        a, b = objective("a"), objective("b", role="B")
        p = self.plan(a,b)
        self.assertEqual(p, self.plan(b,a))
        self.assertEqual(next_objective(p,"A").objective,"a")
        self.assertEqual(next_objective(p,"B").objective,"b")

    def test_duplicate_or_malformed_inventory_rejected(self):
        a = objective("a")
        for items in ((a,a), (replace(a,criteria=()),),
                      (replace(a,priority=True),),
                      (replace(a,role="OWNER"),),
                      (replace(a,dependencies=("b","b")),)):
            with self.subTest(items=items), self.assertRaises(ValueError):
                self.plan(*items)
        with self.assertRaises(ValueError):
            self.plan(a, profile=replace(PROFILE,version=True))

    def test_synthetic_second_profile_does_not_reuse_evidence(self):
        a = objective("a")
        second = Profile("synthetic", "sample/second", "trunk", P, R)
        p = self.plan(a, profile=second, receipts=(receipt(a),))
        self.assertEqual(p.ignored_receipts, 1)
        self.assertEqual(next_objective(p,"A").action,"VERIFY_CRITERION")
        p = self.plan(a, profile=second, receipts=(receipt(a,profile=second),))
        self.assertEqual(p.objectives[0].action,"CRITERIA_OBSERVED")
