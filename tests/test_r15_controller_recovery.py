import tempfile
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from tools.smartsvg_controller_recovery import RecoveryJournal, incident_key


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "journal.db"
        self.now = 100
        self.j = RecoveryJournal(self.path, lambda: self.now)
        self.addCleanup(self.j.close)
        self.f = self.j.claim("195", "head", "B", 10)

    def record(self, n, outcome, receipt="", run=None):
        return self.j.record_cycle("195", "head", "B", self.f,
            run=run or str(n), ordinal=n, outcome=outcome, receipt=receipt)

    def advice(self):
        return self.j.advise("195", "head", "B")

    def test_renew_and_stale_fencing(self):
        self.now = 105
        self.assertTrue(self.j.renew("195", "head", "B", self.f, 10))
        self.now = 111
        self.assertIsNone(self.j.claim("195", "head", "A"))
        self.now = 115
        self.assertFalse(self.j.renew("195", "head", "B", self.f))
        self.assertFalse(self.record(1, "NO_PROGRESS"))
        self.assertGreater(self.j.claim("195", "head", "A"), self.f)

    def test_stagnation_and_progress_reset(self):
        for n in (1, 2, 3):
            self.assertTrue(self.record(n, "NO_PROGRESS"))
        self.assertEqual(self.advice(), "PROPOSE_HANDOFF_REVIEW")
        self.assertTrue(self.record(4, "PROGRESS", "a"*64))
        self.assertEqual(self.advice(), "RESUME_CHECKPOINT")

    def test_repeat_evidence_does_not_reset(self):
        for n in (1, 2, 3):
            self.record(n, "PROGRESS", "a"*64)
        self.assertEqual(self.advice(), "CHANGE_STRATEGY")
        self.record(4, "PROGRESS", "a"*64)
        self.assertEqual(self.advice(), "PROPOSE_HANDOFF_REVIEW")

    def test_idempotence_and_order(self):
        self.assertTrue(self.record(2, "NO_PROGRESS"))
        self.assertTrue(self.record(2, "NO_PROGRESS"))
        self.assertFalse(self.record(2, "WAIT_CI"))
        self.assertFalse(self.record(1, "NO_PROGRESS"))
        self.assertEqual(self.advice(), "RESUME_CHECKPOINT")

    def test_wait_and_external_are_not_stagnation(self):
        self.record(1, "NO_PROGRESS")
        self.record(2, "WAIT_CI")
        self.assertEqual(self.advice(), "OTHER_ACTIONABLE_WORK")
        self.record(3, "NO_PROGRESS")
        self.assertEqual(self.advice(), "CHANGE_STRATEGY")
        self.record(4, "EXTERNAL", "permission denied")
        self.assertEqual(self.advice(), "ISOLATE_EXTERNAL_BLOCKER")

    def test_persistence_and_head_isolation(self):
        self.record(1, "NO_PROGRESS")
        self.record(2, "NO_PROGRESS")
        other = RecoveryJournal(self.path, lambda: self.now)
        try:
            self.assertEqual(other.advise("195", "head", "B"), "CHANGE_STRATEGY")
            self.assertEqual(other.advise("195", "new", "B"), "RESUME_CHECKPOINT")
        finally:
            other.close()

    def test_concurrent_claim_has_single_winner(self):
        barrier = Barrier(2)
        def worker(role):
            j = RecoveryJournal(self.path, lambda: self.now)
            try:
                barrier.wait(timeout=5)
                return j.claim("194", "head", role)
            finally:
                j.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(worker, ("A", "B")))
        self.assertEqual(sum(x is not None for x in results), 1)

    def test_progress_requires_digest(self):
        with self.assertRaises(ValueError):
            self.record(1, "PROGRESS", "status report")


class StableIncidentTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "incidents.db"
        self.j = RecoveryJournal(self.path, lambda: 100)
        self.addCleanup(self.j.close)
        self.scope = incident_key("smartsvg", "frenndak/smartsvg-studio",
                                  "a"*40, "ci-failure", "pr:195")
        self.item = "pr:195"
        self.context = "b"*64
        self.fence = self.j.claim(self.item, self.context, "B")

    def record(self, n, outcome, receipt="", **changes):
        args = dict(incident=self.scope, run=str(n), ordinal=n,
                    outcome=outcome, receipt=receipt)
        args.update(changes)
        return self.j.record_incident_cycle(
            self.item, self.context, "B", self.fence, **args)

    def rotate(self, new):
        self.assertTrue(self.j.release(self.item, self.context, "B", self.fence))
        self.context = new
        self.fence = self.j.claim(self.item, self.context, "B")

    def advice(self):
        return self.j.advise_incident(self.item, self.scope, "B")

    def test_head_change_without_progress_does_not_reset_stagnation(self):
        self.assertTrue(self.record(1, "NO_PROGRESS"))
        self.rotate("c"*64)
        self.assertTrue(self.record(2, "NO_PROGRESS"))
        self.assertEqual(self.advice(), "CHANGE_STRATEGY")
        self.rotate("d"*64)
        self.assertTrue(self.record(3, "NO_PROGRESS"))
        self.assertEqual(self.advice(), "PROPOSE_HANDOFF_REVIEW")
        self.assertEqual(self.j.advise(self.item, self.context, "B"),
                         "RESUME_CHECKPOINT")

    def test_duplicate_receipt_across_contexts_is_not_progress(self):
        self.assertTrue(self.record(1, "PROGRESS", "e"*64))
        self.rotate("c"*64)
        self.assertTrue(self.record(2, "PROGRESS", "e"*64))
        self.assertTrue(self.record(3, "PROGRESS", "e"*64))
        self.assertEqual(self.advice(), "CHANGE_STRATEGY")
        self.assertTrue(self.record(4, "PROGRESS", "f"*64))
        self.assertEqual(self.advice(), "RESUME_CHECKPOINT")

    def test_wait_does_not_count_and_history_survives_reopen(self):
        self.record(1, "NO_PROGRESS")
        self.rotate("c"*64)
        self.record(2, "WAIT_CI")
        self.assertEqual(self.advice(), "OTHER_ACTIONABLE_WORK")
        self.record(3, "NO_PROGRESS")
        other = RecoveryJournal(self.path, lambda: 100)
        try:
            self.assertEqual(other.advise_incident(self.item, self.scope, "B"),
                             "CHANGE_STRATEGY")
        finally:
            other.close()

    def test_scope_isolates_project_policy_kind_resource_and_role(self):
        self.record(1, "NO_PROGRESS")
        self.record(2, "NO_PROGRESS")
        for scope in (
                incident_key("other", "frenndak/smartsvg-studio", "a"*40,
                             "ci-failure", "pr:195"),
                incident_key("smartsvg", "frenndak/other", "a"*40,
                             "ci-failure", "pr:195"),
                incident_key("smartsvg", "frenndak/smartsvg-studio", "b"*40,
                             "ci-failure", "pr:195"),
                incident_key("smartsvg", "frenndak/smartsvg-studio", "a"*40,
                             "review", "pr:195"),
                incident_key("smartsvg", "frenndak/smartsvg-studio", "a"*40,
                             "ci-failure", "pr:196")):
            self.assertNotEqual(scope, self.scope)
            self.assertEqual(self.j.advise_incident(self.item, scope, "B"),
                             "RESUME_CHECKPOINT")
        self.assertEqual(self.j.advise_incident(self.item, self.scope, "A"),
                         "RESUME_CHECKPOINT")

    def test_stale_fence_duplicate_run_and_invalid_receipt_rejected(self):
        self.assertTrue(self.record(1, "NO_PROGRESS"))
        self.assertTrue(self.record(1, "NO_PROGRESS"))
        old_context, old_fence = self.context, self.fence
        self.rotate("c"*64)
        self.assertFalse(self.j.record_incident_cycle(
            self.item, old_context, "B", old_fence, incident=self.scope,
            run="2", ordinal=2, outcome="NO_PROGRESS"))
        self.assertFalse(self.record(2, "NO_PROGRESS", run="1"))
        self.assertFalse(self.record(1, "NO_PROGRESS", run="new"))
        with self.assertRaises(ValueError):
            self.record(2, "PROGRESS", "not a receipt")
        with self.assertRaises(ValueError):
            self.record(2, "EXTERNAL", "raw error")
        self.assertTrue(self.record(2, "NO_PROGRESS"))
        self.assertEqual(self.advice(), "CHANGE_STRATEGY")

    def test_invalid_scope_refused(self):
        with self.assertRaises(ValueError):
            incident_key("smartsvg", "frenndak/smartsvg-studio",
                         "a"*40, "raw message with spaces", "pr:195")

    def test_new_exact_progress_supersedes_old_stagnation_for_routing(self):
        self.record(1, "NO_PROGRESS")
        self.record(2, "NO_PROGRESS")
        self.rotate("c"*64)
        args = (self.item, self.context, "B")
        self.assertEqual(self.j.advise(*args, incident=self.scope), "CHANGE_STRATEGY")
        self.assertTrue(self.j.record_cycle(*args, self.fence, run="fresh", ordinal=1,
                                            outcome="PROGRESS", receipt="e"*64))
        self.assertEqual(self.j.advise(*args, incident=self.scope), "RESUME_CHECKPOINT")

    def test_exact_no_progress_cannot_hide_stable_stagnation(self):
        self.record(1, "NO_PROGRESS")
        self.record(2, "NO_PROGRESS")
        self.rotate("c"*64)
        args = (self.item, self.context, "B")
        self.assertTrue(self.j.record_cycle(*args, self.fence, run="new",
                                            ordinal=1, outcome="NO_PROGRESS"))
        self.assertEqual(self.j.advise(*args, incident=self.scope), "CHANGE_STRATEGY")

    def test_old_wait_expires_but_does_not_erase_stagnation(self):
        self.record(1, "NO_PROGRESS")
        self.record(2, "NO_PROGRESS")
        self.record(3, "WAIT_CI")
        args = (self.item, self.context, "B")
        self.assertEqual(self.j.advise(*args, incident=self.scope), "OTHER_ACTIONABLE_WORK")
        self.rotate("c"*64)
        self.assertEqual(self.j.advise(self.item, self.context, "B", incident=self.scope),
                         "CHANGE_STRATEGY")

    def test_old_external_blocker_expires_without_erasing_streak(self):
        self.record(1, "NO_PROGRESS")
        self.record(2, "NO_PROGRESS")
        self.record(3, "NO_PROGRESS")
        self.record(4, "EXTERNAL", "e"*64)
        self.assertEqual(self.j.advise(self.item, self.context, "B", incident=self.scope),
                         "ISOLATE_EXTERNAL_BLOCKER")
        self.rotate("c"*64)
        self.assertEqual(self.j.advise(self.item, self.context, "B", incident=self.scope),
                         "PROPOSE_HANDOFF_REVIEW")

    def test_overlapping_histories_are_not_summed(self):
        self.record(1, "NO_PROGRESS")
        args = (self.item, self.context, "B")
        self.assertTrue(self.j.record_cycle(*args, self.fence, run="1",
                                            ordinal=1, outcome="NO_PROGRESS"))
        self.assertEqual(self.j.advise(*args, incident=self.scope), "RESUME_CHECKPOINT")

    def test_current_wait_has_priority_over_old_stagnation(self):
        self.record(1, "NO_PROGRESS")
        self.record(2, "NO_PROGRESS")
        self.rotate("c"*64)
        args = (self.item, self.context, "B")
        self.assertTrue(self.j.record_cycle(*args, self.fence, run="wait",
                                            ordinal=1, outcome="WAIT_REVIEW"))
        self.assertEqual(self.j.advise(*args, incident=self.scope), "OTHER_ACTIONABLE_WORK")
