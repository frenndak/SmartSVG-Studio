import unittest
from copy import deepcopy
from tools.smartsvg_controller_step_log import bind_step_log
from tools.smartsvg_controller_proof import parse_test_receipts

H="a"*40
TEST="test_example.Example.test_export"


class StepLogTests(unittest.TestCase):
    def setUp(self):
        self.log=(
            '2026-11-25T03:52:46.1607895Z [command]"C:\\Program Files\\Git\\bin\\git.exe" log -1 --format=%H\n'
            '2026-11-25T03:52:46.3327943Z '+H+'\n'
            '2026-11-25T03:54:46.4374273Z test_export ('+TEST+') ... ok\n')
        self.job={"id":3,"run_id":2,"run_attempt":1,"head_sha":H,"steps":[
            {"number":2,"name":"Run actions/checkout@v4","status":"completed","conclusion":"success",
             "started_at":"2026-11-25T03:52:35Z","completed_at":"2026-11-25T03:52:47Z"},
            {"number":6,"name":"Full Python suite","status":"completed","conclusion":"success",
             "started_at":"2026-11-25T03:53:07Z","completed_at":"2026-11-25T03:55:37Z"}]}

    def report(self,log=None,job=None):
        log=self.log if log is None else log
        receipt=parse_test_receipts(log,[TEST],head=H,run_id=2,attempt=1,job_id=3)
        return bind_step_log(log,receipt,self.job if job is None else job,6)

    def test_exact_checkout_and_step_bound(self):
        r=self.report()
        self.assertEqual(r["status"],"BOUND")
        self.assertEqual(r["checkout_line"],2)
        self.assertEqual(r["qualification"],"OBSERVATIONAL_ONLY")

    def test_wrong_checkout_is_not_qualified(self):
        self.assertEqual(self.report(self.log.replace(H,"b"*40))["reason"],
                         "CHECKOUT_SHA_NOT_OBSERVED")

    def test_test_outside_step_or_duplicate_is_not_qualified(self):
        for log in (self.log.replace("03:54:46","03:56:46"),
                    self.log+self.log.splitlines()[-1]+"\n",
                    self.log.replace("03:54:46.4374273","03:53:07.1000000")):
            self.assertEqual(self.report(log)["reason"],"TEST_RESULT_NOT_UNIQUELY_IN_STEP")

    def test_missing_window_and_wrong_attempt(self):
        j=deepcopy(self.job)
        j["steps"][1].pop("started_at")
        self.assertEqual(self.report(job=j)["status"],"UNKNOWN")
        j=deepcopy(self.job)
        j["run_attempt"]=2
        self.assertEqual(self.report(job=j)["reason"],"LOG_JOB_IDENTITY_MISMATCH")
