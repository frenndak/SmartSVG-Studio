import tempfile
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from tools.smartsvg_controller_recovery import RecoveryJournal


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
