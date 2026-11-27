import tempfile
import unittest
import sqlite3
from dataclasses import replace
from datetime import datetime,timezone
from pathlib import Path
from hashlib import sha256

from tools.smartsvg_controller_orchestration import Plan, Proposal, reserve_next, routing_incident
from tools.smartsvg_controller_storage import OperationalJournal
from tools.smartsvg_controller_cycle_ingest import CycleObservation, ingest_cycle

NOW=datetime(2026,11,27,tzinfo=timezone.utc)
M,P,H,J=(c*40 for c in "abcd")


def dig(s):
    return sha256(s.encode()).hexdigest()


class CycleIngestionTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path=Path(tmp.name)/"cycles.sqlite"
        self.j=OperationalJournal(self.path,lambda:100)
        self.addCleanup(self.j.close)
        self.p=Proposal(195,H,"B","REVIEW",(),())
        self.plan=Plan(M,P,NOW,(self.p,),1,True,())
        self.r=reserve_next(self.plan,"A",self.j,now=NOW)

    def obs(self,n,outcome="NO_PROGRESS",material=""):
        return CycleObservation(self.r.context_key,routing_incident(self.plan,self.p),"A",
                                dig("run"+str(n)),n,outcome,dig("source"+str(n)),material)

    def ingest(self,o,plan=None,p=None,r=None):
        return ingest_cycle(self.j,plan or self.plan,p or self.p,r or self.r,o)

    def evidence(self):
        return self.j.evidence_for(195,self.p.head,self.plan.main,self.plan.policy_blob,
                                   "CYCLE_OUTCOME")

    def rotate(self,head):
        self.assertTrue(self.j.release("pr:195",self.r.context_key,"A",self.r.fence))
        self.p=replace(self.p,head=head)
        self.plan=replace(self.plan,proposals=(self.p,))
        self.r=reserve_next(self.plan,"A",self.j,now=NOW)

    def test_atomic_evidence_and_both_ledgers_idempotent(self):
        o=self.obs(1,"PROGRESS",dig("artifact"))
        digest=self.ingest(o)
        self.assertEqual(self.ingest(o),digest)
        rows=self.evidence()
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0][0],digest)
        self.assertEqual(rows[0][1].payload["material_digest"],dig("artifact"))
        self.assertEqual(self.j.db.execute("SELECT COUNT(*) FROM cycle").fetchone()[0],1)
        self.assertEqual(self.j.db.execute("SELECT COUNT(*) FROM incident_cycle_v1").fetchone()[0],1)

    def test_conflicting_run_observation_is_not_replayed(self):
        o=self.obs(1)
        self.assertIsNotNone(self.ingest(o))
        self.assertIsNone(self.ingest(replace(o,source_digest=dig("changed"))))
        self.assertIsNone(self.ingest(replace(o,outcome="WAIT_CI")))
        self.assertEqual(len(self.evidence()),1)

    def test_stale_context_or_fence_cannot_write(self):
        old=self.r
        self.rotate(J)
        self.assertIsNone(self.ingest(self.obs(1),r=old))
        self.assertIsNone(self.ingest(self.obs(1),r=replace(self.r,fence=self.r.fence+1)))
        self.assertIsNone(self.ingest(self.obs(1),r=replace(self.r,owner="B")))
        self.assertEqual(self.evidence(),())

    def test_stable_no_progress_across_exact_context_change(self):
        self.assertIsNotNone(self.ingest(self.obs(1)))
        self.rotate(J)
        self.assertIsNotNone(self.ingest(self.obs(2)))
        self.assertEqual(self.j.advise("pr:195",self.r.context_key,"A",
                                      incident=routing_incident(self.plan,self.p)),
                         "CHANGE_STRATEGY")
        self.assertIsNone(self.ingest(self.obs(1)))
        self.assertIsNotNone(self.ingest(self.obs(3)))
        self.assertEqual(self.j.advise("pr:195",self.r.context_key,"A",
                                      incident=routing_incident(self.plan,self.p)),
                         "PROPOSE_HANDOFF_REVIEW")

    def test_new_receipt_same_material_does_not_reset_progress(self):
        material=dig("artifact")
        self.ingest(self.obs(1,"PROGRESS",material))
        self.rotate(J)
        self.ingest(self.obs(2,"PROGRESS",material))
        self.ingest(self.obs(3,"PROGRESS",material))
        self.assertEqual(self.j.advise("pr:195",self.r.context_key,"A",
                                      incident=routing_incident(self.plan,self.p)),
                         "CHANGE_STRATEGY")
        self.ingest(self.obs(4,"PROGRESS",dig("new-artifact")))
        self.assertEqual(self.j.advise("pr:195",self.r.context_key,"A",
                                      incident=routing_incident(self.plan,self.p)),
                         "RESUME_CHECKPOINT")

    def test_legitimate_wait_not_stagnation_and_old_wait_expires(self):
        self.ingest(self.obs(1))
        self.ingest(self.obs(2))
        self.ingest(self.obs(3,"WAIT_CI"))
        self.assertEqual(self.j.advise("pr:195",self.r.context_key,"A",
                                      incident=routing_incident(self.plan,self.p)),
                         "OTHER_ACTIONABLE_WORK")
        self.rotate(J)
        self.assertEqual(self.r.recovery_advice,"CHANGE_STRATEGY")

    def test_malformed_or_unproven_material_rejected(self):
        o=self.obs(1)
        for x in (replace(o,run_digest="raw"),replace(o,source_digest="raw error"),
                  replace(o,ordinal=True),replace(o,outcome="PROGRESS"),
                  replace(o,material_digest=dig("unexpected"))):
            with self.assertRaises(ValueError):
                self.ingest(x)
        self.assertEqual(self.evidence(),())

    def test_legacy_partial_ledger_does_not_manufacture_receipt(self):
        o=self.obs(1)
        self.assertTrue(self.j.record_cycle("pr:195",self.r.context_key,"A",
            self.r.fence,run=o.run_digest,ordinal=o.ordinal,outcome=o.outcome,
            receipt=o.source_digest))
        self.assertIsNone(self.ingest(o))
        self.assertEqual(self.evidence(),())
        self.assertEqual(self.j.db.execute("SELECT COUNT(*) FROM incident_cycle_v1").fetchone()[0],0)

    def test_transaction_rolls_back_on_evidence_write_failure(self):
        self.j.db.execute("""CREATE TRIGGER reject_cycle_evidence BEFORE INSERT ON evidence
            BEGIN SELECT RAISE(ABORT,'fixture'); END""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.ingest(self.obs(1))
        self.assertEqual(self.j.db.execute("SELECT COUNT(*) FROM cycle").fetchone()[0],0)
        self.assertEqual(self.j.db.execute("SELECT COUNT(*) FROM incident_cycle_v1").fetchone()[0],0)
        self.assertEqual(self.j.db.execute("SELECT COUNT(*) FROM cycle_import_v1").fetchone()[0],0)
        self.assertEqual(self.evidence(),())

    def test_reopen_retains_imported_evidence_and_advice(self):
        self.ingest(self.obs(1))
        self.ingest(self.obs(2))
        other=OperationalJournal(self.path,lambda:100)
        try:
            self.assertEqual(other.advise("pr:195",self.r.context_key,"A",
                                         incident=routing_incident(self.plan,self.p)),
                             "CHANGE_STRATEGY")
            self.assertEqual(len(other.evidence_for(195,H,M,P,"CYCLE_OUTCOME")),2)
        finally:
            other.close()

    def test_observation_is_bound_to_its_exact_context_incident_and_role(self):
        o=self.obs(1)
        self.rotate(J)
        self.assertIsNone(self.ingest(o))
        fresh=self.obs(2)
        self.assertIsNone(self.ingest(replace(fresh,incident_key=dig("other"))))
        self.assertIsNone(self.ingest(replace(fresh,role="B")))
        self.assertEqual(self.evidence(),())
        self.assertIsNotNone(self.ingest(fresh))

    def test_source_receipt_cannot_count_as_second_actual_cycle(self):
        first=self.obs(1)
        self.assertIsNotNone(self.ingest(first))
        self.rotate(J)
        second=self.obs(2)
        self.assertIsNone(self.ingest(replace(second,source_digest=first.source_digest)))
        self.assertEqual(self.evidence(),())
        self.assertIsNotNone(self.ingest(second))
        self.assertEqual(self.j.advise("pr:195",self.r.context_key,"A",
                                      incident=routing_incident(self.plan,self.p)),
                         "CHANGE_STRATEGY")

    def test_overflowing_ordinal_and_fence_are_rejected_without_write(self):
        with self.assertRaises(ValueError):
            self.ingest(replace(self.obs(1),ordinal=2**63))
        self.assertIsNone(self.ingest(self.obs(1),r=replace(self.r,fence=2**63)))
        self.assertEqual(self.evidence(),())
