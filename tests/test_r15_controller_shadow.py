import tempfile
import unittest
from pathlib import Path
from tools.smartsvg_controller_shadow import Journal

class ShadowJournalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.now = 100
        self.path = Path(self.tmp.name) / "state.db"
        self.a = Journal(self.path, lambda: self.now)
        self.b = Journal(self.path, lambda: self.now)
        self.addCleanup(self.a.close)
        self.addCleanup(self.b.close)
    def test_claim_is_exclusive_and_expired_writer_fenced(self):
        first = self.a.claim("195", "sha1", "A", 10)
        self.assertIsNone(self.b.claim("195", "sha1", "B"))
        self.assertTrue(self.a.save("195", "sha1", "A", first, "file 1 done"))
        self.now += 10
        second = self.b.claim("195", "sha1", "B")
        self.assertGreater(second, first)
        self.assertFalse(self.a.save("195", "sha1", "A", first, "stale"))
        self.assertFalse(self.a.release("195", "sha1", "A", first))
        self.assertEqual(self.b.checkpoint("195", "sha1"), "file 1 done")
    def test_new_head_invalidates_checkpoint(self):
        fence = self.a.claim("195", "sha1", "A")
        self.a.save("195", "sha1", "A", fence, "old")
        self.assertTrue(self.a.release("195", "sha1", "A", fence))
        self.b.claim("195", "sha2", "B")
        self.assertEqual(self.b.checkpoint("195", "sha2"), "")
        self.assertIsNone(self.a.checkpoint("195", "sha1"))
    def test_restart_preserves_checkpoint(self):
        f = self.a.claim("192", "sha1", "A")
        self.a.save("192", "sha1", "A", f, "next consumer")
        self.a.release("192", "sha1", "A", f)
        c = Journal(self.path, lambda: self.now)
        try:
            c.claim("192", "sha1", "B")
            self.assertEqual(c.checkpoint("192", "sha1"), "next consumer")
        finally:
            c.close()
    def test_invalid_ttl_and_expired_write(self):
        with self.assertRaises(ValueError):
            self.a.claim("195", "sha", "A", 0)
        f = self.a.claim("195", "sha", "A", 1)
        self.now += 1
        self.assertFalse(self.a.save("195", "sha", "A", f, "late"))
