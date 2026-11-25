import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, replace
from datetime import datetime, timezone, timedelta
from pathlib import Path
from threading import Barrier

from tools.smartsvg_controller_integration import Observation, IntegrationJournal, TerminalReceipt
from tools.smartsvg_controller_preflight import IntegrationSubject, Fact, GATES, requirements, _digest

H,M,N,X = ("a"*40,"b"*40,"c"*40,"d"*40)
NOW = datetime(2026,11,25,18,0,tzinfo=timezone.utc)
S = IntegrationSubject(195,H,M,"e"*40,"A","author","cycle-1","d"*64,
                       ("engine/example.py",),True,True,("test_native.Flow.test_export",))
KEY = _digest(asdict(S))
O = Observation(195,H,N,"closed",True,N,M,N,"PASS")
NEG = replace(O,main=M,pr_state="open",merged=False,merge_sha=None,
              merge_parent=None,g0_sha=None,g0_status="UNKNOWN")
T = TerminalReceipt(S.executor_cycle,195,H,M,KEY,"f"*64)

def facts(subject=S):
    names=GATES | {"ci:"+x for x in requirements(subject)} | {"test:"+t for t in subject.targeted_tests}
    return tuple(Fact(n,_digest(asdict(subject)),"PASS","EXTERNALLY_VERIFIED","e"*64,NOW)
                 for n in sorted(names))

def prepare(j,subject=S,fs=None,role="B",now=NOW):
    return j.prepare(subject,facts(subject) if fs is None else fs,role=role,now=now)


class IntegrationJournalTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/"shadow.db"
        self.j=IntegrationJournal(self.path)
        self.addCleanup(self.j.close)

    def dispatch(self):
        self.assertTrue(prepare(self.j))
        self.assertTrue(self.j.mark_attempt(S.executor_cycle))

    def test_cycle_budget_and_global_unresolved(self):
        self.dispatch()
        self.assertFalse(self.j.mark_attempt(S.executor_cycle))
        self.assertFalse(prepare(self.j))
        self.assertFalse(prepare(self.j,replace(S,executor_cycle="2")))
        r=self.j.reconcile(S.executor_cycle,O)
        self.assertEqual(r.state,"QUALIFIED_SIMULATION")
        self.assertFalse(r.mutation_authorized)
        self.assertFalse(prepare(self.j))
        self.assertTrue(prepare(self.j,replace(S,executor_cycle="2")))

    def test_timeout_negative_readback_is_not_retry_authority(self):
        self.dispatch()
        r=self.j.reconcile(S.executor_cycle,replace(O,main=M,pr_state="open",merged=False,
            merge_sha=None,merge_parent=None,g0_sha=None,g0_status="UNKNOWN"))
        self.assertEqual(r.state,"NEGATIVE_READBACK")
        self.assertFalse(prepare(self.j,replace(S,executor_cycle="2")))
        self.assertEqual(self.j.reconcile(S.executor_cycle,O).state,"QUALIFIED_SIMULATION")

    def test_restart_recovers_ambiguous_attempt(self):
        self.dispatch()
        other=IntegrationJournal(self.path)
        try:
            self.assertEqual(other.status(S.executor_cycle),("AMBIGUOUS",None))
            self.assertEqual(other.reconcile(S.executor_cycle,O).state,"QUALIFIED_SIMULATION")
            self.assertEqual(self.j.status(S.executor_cycle),("QUALIFIED_SIMULATION",N))
        finally:
            other.close()

    def test_wrong_g0_and_failure_and_recovery(self):
        self.dispatch()
        self.assertEqual(self.j.reconcile(S.executor_cycle,replace(O,g0_sha=M)).state,"WAIT_G0")
        self.assertEqual(self.j.reconcile(S.executor_cycle,replace(O,g0_status="FAIL")).state,"G0_FAILED")
        self.assertFalse(prepare(self.j,replace(S,executor_cycle="2")))
        self.assertEqual(self.j.reconcile(S.executor_cycle,O).state,"QUALIFIED_SIMULATION")

    def test_main_drift_and_inconsistent_sha(self):
        self.dispatch()
        self.assertEqual(self.j.reconcile(S.executor_cycle,replace(O,main=X)).state,"MAIN_DRIFT")
        r=self.j.reconcile(S.executor_cycle,replace(O,merge_sha=X,main=X,g0_sha=X))
        self.assertEqual(r.action,"READBACK_REQUIRED")
        self.assertFalse(r.mutation_authorized)

    def test_wrong_role_subject_and_preflight(self):
        self.assertFalse(prepare(self.j,role="A"))
        self.assertFalse(prepare(self.j,replace(S,number=194),fs=facts()))
        self.assertFalse(prepare(self.j,replace(S,head=X),fs=facts()))
        self.assertFalse(prepare(self.j,replace(S,executor_cycle="other"),fs=facts()))
        self.assertFalse(prepare(self.j,fs=tuple(replace(f,status="FAIL") for f in facts())))
        self.assertFalse(prepare(self.j,now=NOW+timedelta(minutes=6)))

    def test_concurrent_prepare_single_winner(self):
        barrier=Barrier(2)
        def worker(cycle):
            j=IntegrationJournal(self.path)
            try:
                barrier.wait(timeout=5)
                return prepare(j,replace(S,executor_cycle=cycle))
            finally:
                j.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results=list(pool.map(worker,("one","two")))
        self.assertEqual(sum(results),1)

    def test_untrusted_or_wrong_subject_readback_no_transition(self):
        self.dispatch()
        for o in (replace(O,number=194),replace(O,head=X),
                  replace(O,merge_parent=X),replace(O,source="LIVE_UNVERIFIED")):
            self.assertEqual(self.j.reconcile(S.executor_cycle,o).state,"AMBIGUOUS")
        self.assertEqual(self.j.status(S.executor_cycle),("AMBIGUOUS",None))

    def test_cancel_before_dispatch_releases_only_new_cycle(self):
        self.assertTrue(prepare(self.j))
        self.assertFalse(self.j.cancel_prepared(S.executor_cycle,role="A"))
        self.assertTrue(self.j.cancel_prepared(S.executor_cycle,role="B"))
        self.assertEqual(self.j.status(S.executor_cycle),("NOT_APPLIED",None))
        self.assertFalse(self.j.mark_attempt(S.executor_cycle))
        self.assertFalse(prepare(self.j))
        self.assertTrue(prepare(self.j,replace(S,executor_cycle="2")))

    def test_terminal_rejection_requires_exact_receipt_and_readback(self):
        self.dispatch()
        self.assertFalse(self.j.cancel_prepared(S.executor_cycle,role="B"))
        self.assertFalse(self.j.resolve_negative(S.executor_cycle,NEG,T,role="B"))
        self.assertEqual(self.j.reconcile(S.executor_cycle,NEG).state,"NEGATIVE_READBACK")
        for t in (replace(T,cycle="other"),replace(T,head=X),
                  replace(T,outcome="TIMEOUT"),replace(T,source="UNVERIFIED"),
                  replace(T,receipt_digest="bad")):
            self.assertFalse(self.j.resolve_negative(S.executor_cycle,NEG,t,role="B"))
        self.assertFalse(self.j.resolve_negative(S.executor_cycle,replace(NEG,main=X),T,role="B"))
        self.assertFalse(self.j.resolve_negative(S.executor_cycle,NEG,T,role="A"))
        self.assertFalse(prepare(self.j,replace(S,executor_cycle="2")))
        self.assertTrue(self.j.resolve_negative(S.executor_cycle,NEG,T,role="B"))
        self.assertEqual(self.j.status(S.executor_cycle),("NOT_APPLIED",None))
        self.assertEqual(self.j.db.execute("SELECT receipt_digest FROM integration_terminal_receipt").fetchone(),(T.receipt_digest,))
        self.assertTrue(prepare(self.j,replace(S,executor_cycle="2")))

    def test_dispatch_and_cancel_race(self):
        self.assertTrue(prepare(self.j))
        barrier=Barrier(2)
        def worker(cancel):
            j=IntegrationJournal(self.path)
            try:
                barrier.wait(timeout=5)
                return j.cancel_prepared(S.executor_cycle,role="B") if cancel else j.mark_attempt(S.executor_cycle)
            finally:
                j.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sum(pool.map(worker,(True,False))),1)
        self.assertIn(self.j.status(S.executor_cycle)[0],("NOT_APPLIED","AMBIGUOUS"))
