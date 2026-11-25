import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from threading import Barrier

from tools.smartsvg_controller_integration import Intent, Observation, IntegrationJournal
from tools.smartsvg_controller_preflight import Preflight

H,M,N,X = ("a"*40,"b"*40,"c"*40,"d"*40)
KEY = "e"*64
I = Intent("cycle-1",195,H,M,KEY)
P = Preflight("SHADOW_PREFLIGHT_PASS",("NOT_AUTHORIZATION",),KEY)
O = Observation(195,H,N,"closed",True,N,M,N,"PASS")


class IntegrationJournalTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/"shadow.db"
        self.j=IntegrationJournal(self.path)
        self.addCleanup(self.j.close)

    def dispatch(self):
        self.assertTrue(self.j.prepare(I,P,role="B"))
        self.assertTrue(self.j.mark_attempt(I.cycle))

    def test_cycle_budget_and_global_unresolved(self):
        self.dispatch()
        self.assertFalse(self.j.mark_attempt(I.cycle))
        self.assertFalse(self.j.prepare(I,P,role="B"))
        self.assertFalse(self.j.prepare(replace(I,cycle="2"),P,role="B"))
        r=self.j.reconcile(I.cycle,O)
        self.assertEqual(r.state,"QUALIFIED_SIMULATION")
        self.assertFalse(r.mutation_authorized)
        self.assertFalse(self.j.prepare(I,P,role="B"))
        self.assertTrue(self.j.prepare(replace(I,cycle="2"),P,role="B"))

    def test_timeout_negative_readback_is_not_retry_authority(self):
        self.dispatch()
        r=self.j.reconcile(I.cycle,replace(O,main=M,pr_state="open",merged=False,
            merge_sha=None,merge_parent=None,g0_sha=None,g0_status="UNKNOWN"))
        self.assertEqual(r.state,"NEGATIVE_READBACK")
        self.assertFalse(self.j.prepare(replace(I,cycle="2"),P,role="B"))
        self.assertEqual(self.j.reconcile(I.cycle,O).state,"QUALIFIED_SIMULATION")

    def test_restart_recovers_ambiguous_attempt(self):
        self.dispatch()
        other=IntegrationJournal(self.path)
        try:
            self.assertEqual(other.status(I.cycle),("AMBIGUOUS",None))
            self.assertEqual(other.reconcile(I.cycle,O).state,"QUALIFIED_SIMULATION")
            self.assertEqual(self.j.status(I.cycle),("QUALIFIED_SIMULATION",N))
        finally:
            other.close()

    def test_wrong_g0_and_failure_and_recovery(self):
        self.dispatch()
        self.assertEqual(self.j.reconcile(I.cycle,replace(O,g0_sha=M)).state,"WAIT_G0")
        self.assertEqual(self.j.reconcile(I.cycle,replace(O,g0_status="FAIL")).state,"G0_FAILED")
        self.assertFalse(self.j.prepare(replace(I,cycle="2"),P,role="B"))
        self.assertEqual(self.j.reconcile(I.cycle,O).state,"QUALIFIED_SIMULATION")

    def test_main_drift_and_inconsistent_sha(self):
        self.dispatch()
        self.assertEqual(self.j.reconcile(I.cycle,replace(O,main=X)).state,"MAIN_DRIFT")
        r=self.j.reconcile(I.cycle,replace(O,merge_sha=X,main=X,g0_sha=X))
        self.assertEqual(r.action,"READBACK_REQUIRED")
        self.assertFalse(r.mutation_authorized)

    def test_wrong_role_subject_and_preflight(self):
        self.assertFalse(self.j.prepare(I,P,role="A"))
        self.assertFalse(self.j.prepare(I,replace(P,subject_digest="f"*64),role="B"))
        self.assertFalse(self.j.prepare(I,replace(P,action="BLOCKED"),role="B"))
        self.assertFalse(self.j.prepare(I,replace(P,merge_authorized=True),role="B"))

    def test_concurrent_prepare_single_winner(self):
        barrier=Barrier(2)
        def worker(cycle):
            j=IntegrationJournal(self.path)
            try:
                barrier.wait(timeout=5)
                return j.prepare(replace(I,cycle=cycle),P,role="B")
            finally:
                j.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(worker,("one","two")))
        self.assertEqual(sum(results),1)

    def test_untrusted_or_wrong_subject_readback_no_transition(self):
        self.dispatch()
        for o in (replace(O,number=194),replace(O,head=X),
                  replace(O,merge_parent=X),replace(O,source="LIVE_UNVERIFIED")):
            self.assertEqual(self.j.reconcile(I.cycle,o).state,"AMBIGUOUS")
        self.assertEqual(self.j.status(I.cycle),("AMBIGUOUS",None))
