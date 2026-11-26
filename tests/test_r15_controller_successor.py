import unittest
from unittest.mock import patch
from dataclasses import asdict, dataclass
from tools.smartsvg_controller_live_reconcile import Subject
from tools.smartsvg_controller_successor import observe_successor
from tools.smartsvg_controller_decision import Status

H,M,S,N,T,P = (c*40 for c in "abcdef")

@dataclass(frozen=True)
class Receipt:
    status: Status
    job_id: int = 1

class SuccessorTests(unittest.TestCase):
    def setUp(self):
        self.subject=Subject(196,H,M,T)
        self.original={"state":"MAIN_DRIFT","main":N,"merge_sha":S,
                       "subject":asdict(self.subject)}
        self.compare={"status":"ahead","base_commit":{"sha":S},
                      "merge_base_commit":{"sha":S},"ahead_by":1,"behind_by":0}
        self.main=N

    def get(self,path):
        if path.startswith("/compare/"):
            self.assertEqual(path,"/compare/"+S+"..."+N)
            return self.compare.copy()
        if path.startswith("/contents/"):
            self.assertTrue(path.endswith("?ref="+N))
            return {"sha":P}
        if path=="/branches/main":
            return {"commit":{"sha":self.main}}
        raise AssertionError(path)

    def read(self,status=Status.PASS):
        with patch("tools.smartsvg_controller_successor._g0",return_value=Receipt(status)) as g0:
            with patch("tools.smartsvg_controller_successor.reconcile_live",return_value=self.original):
                result=observe_successor(self.get,self.subject,self.original)
            for call in g0.call_args_list:
                self.assertEqual(call.args[1],N)
        self.assertFalse(result["merge_authorized"])
        self.assertFalse(result["retry_authorized"])
        return result

    def test_descendant_with_fresh_g0(self):
        result=self.read()
        self.assertEqual(result["state"],"SUCCESSOR_G0_PASS")
        self.assertEqual(result["policy_blob"],P)
        self.assertEqual(result["g0"]["status"],"PASS")

    def test_failed_and_pending_g0(self):
        self.assertEqual(self.read(Status.FAIL)["state"],"SUCCESSOR_G0_FAILED")
        self.assertEqual(self.read(Status.UNKNOWN)["state"],"SUCCESSOR_G0_WAIT")

    def test_divergence(self):
        self.compare["status"]="diverged"
        self.assertEqual(self.read()["state"],"ANCESTRY_UNPROVED")

    def test_wrong_base_or_behind(self):
        self.compare["base_commit"]={"sha":M}
        self.assertEqual(self.read()["state"],"ANCESTRY_UNPROVED")
        self.compare["base_commit"]={"sha":S}
        self.compare["behind_by"]=1
        self.assertEqual(self.read()["state"],"ANCESTRY_UNPROVED")

    def test_changed_main(self):
        self.main=T
        self.assertEqual(self.read()["state"],"READBACK_DRIFT")

    def test_unknown_merge_not_requalified(self):
        self.original["merge_sha"]=None
        self.assertEqual(self.read()["state"],"UNKNOWN")

    def test_wrong_subject(self):
        self.original["subject"]["number"]=197
        self.assertEqual(self.read()["state"],"UNKNOWN")
