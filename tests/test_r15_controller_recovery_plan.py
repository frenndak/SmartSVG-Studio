import unittest
from unittest.mock import patch
from tools.smartsvg_controller_cas import Record, prepare, transition, encode
from tools.smartsvg_controller_recovery_plan import recover
from tools.smartsvg_controller_observation import POLICY

A,B,C,D = (c*40 for c in "abcd")
E = "e"*64


class RecoveryPlanTests(unittest.TestCase):
    def setUp(self):
        self.initial = Record()
        self.prepared = prepare(self.initial, number=196, head=A, main=B,
                                tree=C, policy=D, evidence=E)
        self.record = transition(self.prepared, "DISPATCH_UNKNOWN", E)
        self.reads = 0

    def read(self):
        self.reads += 1
        return A, encode(self.record)

    def get(self, path):
        self.assertEqual(path, f"/contents/{POLICY}?ref={B}")
        return {"sha":D}

    def check(self, report, action):
        self.assertEqual(report["action"], action)
        self.assertFalse(report["merge_authorized"])
        self.assertFalse(report["retry_authorized"])
        self.assertFalse(report["independent_work_blocked"])

    def test_idle_terminal_prepared_need_no_github_read(self):
        for record, action in (
            (self.initial, "NO_PENDING_INTENT"),
            (self.prepared, "REQUALIFY_PREPARED_INTENT"),
            (transition(self.prepared,"CANCELLED_PREPARED",E), "NO_PENDING_INTENT"),
        ):
            self.record = record
            with patch("tools.smartsvg_controller_recovery_plan.reconcile_live") as live:
                self.check(recover(self.read, None), action)
                live.assert_not_called()

    def test_exact_context_for_all_observations(self):
        for state, action in (
            ("MERGED_G0_PASS","OBSERVE_COMPLETED_INTEGRATION"),
            ("NEGATIVE_READBACK","VERIFY_REQUEST_TERMINALITY"),
            ("WAIT_G0","WAIT_EXACT_MAIN_G0"),
            ("G0_FAILED","REVIEW_REPAIR_OR_REVERT"),
            ("MAIN_DRIFT","REQUALIFY_CURRENT_MAIN"),
            ("UNKNOWN","INSPECT_READBACK"),
        ):
            with patch("tools.smartsvg_controller_recovery_plan.reconcile_live",
                       return_value={"state":state}) as live:
                report = recover(self.read,self.get)
                self.check(report,action)
                subject = live.call_args.args[1]
                self.assertEqual((subject.number,subject.head,subject.prior_main,
                                  subject.expected_tree),(196,A,B,C))
                self.assertEqual(report["observation"]["state"],state)

    def test_policy_mismatch_no_reconciliation(self):
        with patch("tools.smartsvg_controller_recovery_plan.reconcile_live") as live:
            self.check(recover(self.read,lambda _:{"sha":A}),"INSPECT_POLICY_MISMATCH")
            live.assert_not_called()

    def test_journal_changes_during_observation(self):
        def read():
            self.reads += 1
            return (A if self.reads==1 else B),encode(self.record)
        with patch("tools.smartsvg_controller_recovery_plan.reconcile_live",
                   return_value={"state":"MERGED_G0_PASS"}):
            result=recover(read,self.get)
        self.check(result,"JOURNAL_DRIFT")
        self.assertIsNone(result["observation"])

    def test_unavailable_journal(self):
        def unavailable():
            raise OSError()
        self.check(recover(unavailable,self.get),"INSPECT_JOURNAL_OR_READBACK")

    def test_invalid_bytes(self):
        self.check(recover(lambda:(A,b"not json"),self.get),"INSPECT_JOURNAL_OR_READBACK")
