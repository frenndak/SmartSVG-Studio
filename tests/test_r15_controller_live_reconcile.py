import unittest
from copy import deepcopy
from tools.smartsvg_controller_live_reconcile import Subject, reconcile_live
from tools.smartsvg_controller_evidence import SPECS

H="a"*40
M="b"*40
S="c"*40
T="d"*40
R="frenndak/SmartSVG-Studio"


class LiveReconcileTests(unittest.TestCase):
    def setUp(self):
        self.subject=Subject(196,H,M,T)
        self.main=S
        self.pr={"number":196,"head":{"sha":H,"repo":{"full_name":R}},
                 "base":{"ref":"main","repo":{"full_name":R}},"user":{"login":"frenndak"},
                 "state":"closed","merged":True,"merge_commit_sha":S}
        self.commit={"sha":S,"parents":[{"sha":M}],"tree":{"sha":T}}
        path,name,step=SPECS["g0"]
        self.run={"id":1,"head_sha":S,"head_branch":"main","event":"push","path":path,
                  "run_attempt":1,"status":"completed","conclusion":"success"}
        self.job={"id":2,"run_id":1,"run_attempt":1,"head_sha":S,"name":name,
                  "status":"completed","conclusion":"success",
                  "steps":[{"number":5,"name":step,"status":"completed","conclusion":"success"}]}

    def get(self,path):
        if path=="/branches/main":
            return {"commit":{"sha":self.main}}
        if path=="/pulls/196":
            return deepcopy(self.pr)
        if path=="/git/commits/"+S:
            return deepcopy(self.commit)
        if path.startswith("/actions/runs?"):
            return {"total_count":1,"workflow_runs":[deepcopy(self.run)]}
        if path.startswith("/actions/runs/1/attempts/1/jobs?"):
            return {"total_count":1,"jobs":[deepcopy(self.job)]}
        raise AssertionError(path)

    def read(self):
        result=reconcile_live(self.get,self.subject)
        self.assertFalse(result["merge_authorized"])
        self.assertFalse(result["retry_authorized"])
        return result

    def test_exact_squash_and_g0(self):
        r=self.read()
        self.assertEqual(r["state"],"MERGED_G0_PASS")
        self.assertEqual(r["g0"]["job_id"],2)
        self.assertEqual(r["merge_sha"],S)
        self.assertEqual(self.read()["digest"],r["digest"])

    def test_pending_failure_and_skip_never_pass(self):
        self.run["status"]="in_progress"
        self.run["conclusion"]=None
        self.assertEqual(self.read()["state"],"WAIT_G0")
        self.run.update(status="completed",conclusion="failure")
        self.assertEqual(self.read()["state"],"G0_FAILED")
        self.run["conclusion"]="success"
        self.job["steps"][0]["conclusion"]="skipped"
        self.assertEqual(self.read()["state"],"WAIT_G0")

    def test_open_pr_no_retry_even_on_unchanged_main(self):
        self.main=M
        self.pr.update(state="open",merged=False,merge_commit_sha=None)
        self.assertEqual(self.read()["state"],"NEGATIVE_READBACK")
        self.main=T
        self.assertEqual(self.read()["state"],"MAIN_DRIFT")

    def test_tree_parent_and_identity_mismatch(self):
        self.commit["tree"]["sha"]="e"*40
        self.assertEqual(self.read()["reason"],"EXPECTED_TREE_MISMATCH")
        self.commit["tree"]["sha"]=T
        self.commit["parents"].append({"sha":H})
        self.assertEqual(self.read()["reason"],"SQUASH_PARENT_MISMATCH")
        self.pr["head"]["sha"]=T
        self.assertEqual(self.read()["state"],"UNKNOWN")

    def test_later_main_does_not_reuse_g0(self):
        self.main=T
        r=self.read()
        self.assertEqual(r["state"],"MAIN_DRIFT")
        self.assertIsNone(r["g0"])

    def test_attempt_drift_on_second_read(self):
        base=self.get
        count=0
        def get(path):
            nonlocal count
            if path.startswith("/actions/runs?"):
                count+=1
                if count==2:
                    self.run["run_attempt"]=2
                    self.run["status"]="in_progress"
            return base(path)
        r=reconcile_live(get,self.subject)
        self.assertEqual(r["state"],"UNKNOWN")
        self.assertFalse(r["retry_authorized"])
