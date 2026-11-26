import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from threading import Barrier
from tools.smartsvg_controller_storage import Evidence, OperationalJournal

H, M, P = "a"*40, "b"*40, "c"*40
K = "d"*64


class StorageTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "shadow.db"
        self.now = 100
        self.j = OperationalJournal(self.path, lambda: self.now)
        self.addCleanup(self.j.close)
        self.e = Evidence(195, H, M, P, "STEP_ONLY", "job/123", {"status": "PASS"})

    def test_one_active_lease_per_worker_and_per_item(self):
        f = self.j.claim("pr:192", K, "A", 10)
        self.assertIsNotNone(f)
        self.assertIsNone(self.j.claim("pr:195", K, "A"))
        self.assertIsNone(self.j.claim("pr:192", K, "B"))
        self.assertIsNotNone(self.j.claim("pr:195", K, "B"))
        self.assertTrue(self.j.release("pr:192", K, "A", f))
        self.assertIsNotNone(self.j.claim("pr:194", K, "A"))

    def test_expired_lease_does_not_block_worker(self):
        f = self.j.claim("pr:192", K, "A", 1)
        self.now += 1
        self.assertIsNotNone(self.j.claim("pr:195", K, "A"))
        self.assertFalse(self.j.save("pr:192", K, "A", f, "late"))

    def test_same_worker_concurrent_different_items(self):
        barrier = Barrier(2)
        def worker(item):
            j = OperationalJournal(self.path, lambda: self.now)
            try:
                barrier.wait(timeout=5)
                return j.claim(item, K, "A")
            finally:
                j.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            got = list(pool.map(worker, ("pr:192", "pr:195")))
        self.assertEqual(sum(x is not None for x in got), 1)

    def test_deduplication_and_exact_context(self):
        digest = self.j.store_evidence(self.e)
        self.assertEqual(self.j.store_evidence(self.e), digest)
        self.assertEqual(self.j.evidence_for(195,H,M,P,"STEP_ONLY"),
                         ((digest,self.e),))
        self.assertEqual(self.j.evidence_for(195,M,M,P,"STEP_ONLY"), ())
        self.assertEqual(self.j.evidence_for(195,H,H,P,"STEP_ONLY"), ())
        self.assertEqual(self.j.evidence_for(195,H,M,H,"STEP_ONLY"), ())
        self.assertEqual(self.j.evidence_for(195,H,M,P,"LOG_ONLY"), ())

    def test_reopen_preserves_evidence(self):
        digest = self.j.store_evidence(self.e)
        other = OperationalJournal(self.path, lambda: self.now)
        try:
            self.assertEqual(other.evidence_for(195,H,M,P,"STEP_ONLY")[0][0], digest)
        finally:
            other.close()

    def test_tampered_storage_rejected(self):
        digest = self.j.store_evidence(self.e)
        self.j.db.execute("UPDATE evidence SET raw=? WHERE digest=?", (b"bad",digest))
        with self.assertRaises(ValueError):
            self.j.evidence_for(195,H,M,P,"STEP_ONLY")

    def test_invalid_metadata_and_no_merge_receipt_kind(self):
        for e in (replace(self.e, kind="APPROVED"), replace(self.e, head="bad"),
                  replace(self.e, payload={"x":float("nan")}),
                  replace(self.e, payload={"x":"a"*70000})):
            with self.assertRaises(ValueError):
                self.j.store_evidence(e)
