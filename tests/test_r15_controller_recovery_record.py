import unittest
from copy import deepcopy
from unittest.mock import patch
from tools.smartsvg_controller_cas import Record, prepare, transition, encode, Result
from tools.smartsvg_controller_recovery_record import reconcile_and_record
from tools.smartsvg_controller_observation import POLICY
from tools.smartsvg_controller_evidence import SPECS

A,B,C,D,F=(x*40 for x in "abcdf")
E="e"*64


class Journal:
    def __init__(self,record):
        self.record=record
        self.ref=A
        self.calls=0
        self.outcome="APPLIED"

    def read(self):
        return self.ref,encode(self.record)

    def write(self,ref,previous,proposed):
        self.calls+=1
        if (ref,encode(previous))!=self.read():
            raise ValueError("stale")
        if self.outcome=="APPLIED":
            self.record=proposed
            self.ref=F
        return Result(self.outcome,F,self.ref)


class RecoveryRecordTests(unittest.TestCase):
    def setUp(self):
        self.prepared=prepare(Record(),number=196,head=A,main=B,tree=C,policy=D,evidence=E)
        self.journal=Journal(transition(self.prepared,"DISPATCH_UNKNOWN",E))
        self.workflow=C
        self.policy=D

    def observation(self,state):
        r=self.journal.record
        return {"journal_ref":self.journal.ref,"generation":r.generation,"intent":r.intent,
                "journal_state":r.state,"action":"OBSERVE",
                "observation":{"state":state,"main":F,"merge_sha":F,"g0":{"status":"PASS"}},
                "successor":None}

    def get(self,path):
        if path.startswith(f"/contents/{POLICY}?"):
            return {"sha":self.policy}
        if path==f"/contents/{SPECS['g0'][0]}?ref={B}":
            return {"sha":C}
        if path==f"/contents/{SPECS['g0'][0]}?ref={F}":
            return {"sha":self.workflow}
        raise AssertionError(path)

    def run_state(self,state):
        with patch("tools.smartsvg_controller_recovery_record.recover",
                   return_value=self.observation(state)):
            r=reconcile_and_record(self.journal,self.get)
        self.assertFalse(r["merge_authorized"])
        self.assertFalse(r["retry_authorized"])
        self.assertFalse(r["independent_work_blocked"])
        return r

    def test_positive_readback_and_restart(self):
        self.assertEqual(self.run_state("MERGED_G0_PASS")["status"],"OBSERVATION_RECORDED")
        self.assertEqual(self.journal.record.state,"QUALIFIED_READBACK")
        self.assertEqual(self.run_state("MERGED_G0_PASS")["status"],"NO_OBSERVATION_WRITE")
        self.assertEqual(self.journal.calls,1)

    def test_workflow_or_policy_change_never_terminal(self):
        self.workflow=F
        self.assertEqual(self.run_state("MERGED_G0_PASS")["status"],"POLICY_OR_G0_CHANGED")
        self.workflow=C
        self.policy=F
        self.assertEqual(self.run_state("MERGED_G0_PASS")["status"],"POLICY_OR_G0_CHANGED")
        self.assertEqual(self.journal.calls,0)

    def test_negative_and_same_observation_dedup(self):
        self.assertEqual(self.run_state("NEGATIVE_READBACK")["status"],"OBSERVATION_RECORDED")
        self.assertEqual(self.journal.record.state,"NEGATIVE_READBACK")
        self.assertEqual(self.run_state("NEGATIVE_READBACK")["status"],"ALREADY_RECORDED")
        self.assertEqual(self.journal.calls,1)

    def test_wait_failure_and_main_drift_never_terminal(self):
        for state in ("WAIT_G0","G0_FAILED","MAIN_DRIFT"):
            self.assertEqual(self.run_state(state)["status"],"OBSERVATION_RECORDED")
            self.assertEqual(self.journal.record.state,state)

    def test_unknown_prepared_and_ambiguous_write(self):
        self.assertEqual(self.run_state("UNKNOWN")["status"],"READBACK_UNAVAILABLE")
        self.journal.outcome="AMBIGUOUS"
        self.assertEqual(self.run_state("MERGED_G0_PASS")["status"],"JOURNAL_AMBIGUOUS")
        self.assertEqual(self.journal.calls,1)
        self.assertEqual(self.journal.record.state,"DISPATCH_UNKNOWN")
        self.journal.record=self.prepared
        self.assertEqual(self.run_state("MERGED_G0_PASS")["status"],"NO_OBSERVATION_WRITE")
        self.assertEqual(self.journal.calls,1)

    def test_observation_drift_before_cas(self):
        before=self.observation("MERGED_G0_PASS")
        after=deepcopy(before)
        after["observation"]["state"]="WAIT_G0"
        with patch("tools.smartsvg_controller_recovery_record.recover",side_effect=[before,after]):
            r=reconcile_and_record(self.journal,self.get)
        self.assertEqual(r["status"],"OBSERVATION_CHANGED")
        self.assertEqual(self.journal.calls,0)
