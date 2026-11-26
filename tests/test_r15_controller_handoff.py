import unittest
import json
from dataclasses import replace
from datetime import datetime, timezone
from tools.smartsvg_controller_handoff import PREFIX, route_checkpoints
from tools.smartsvg_controller_orchestration import Plan, Proposal
from tools.smartsvg_controller_decision import Status
from tools.smartsvg_controller_evidence import StepReceipt

H,M,P = (x*40 for x in "abc")


class DurableHandoffTests(unittest.TestCase):
    def setUp(self):
        self.plan = Plan(M,P,datetime(2026,11,26,16,tzinfo=timezone.utc),
                         (Proposal(195,H,"A","REVIEW",(),(StepReceipt("g0",Status.PASS),)),),
                         1,True,())
        self.value = dict(version=1,number=195,head=H,main=M,policy_blob=P,
                          role="B",verdict="ADVERSE")
        self.comment = dict(id=123,user={"login":"frenndak"},
            issue_url="https://api.github.com/repos/frenndak/SmartSVG-Studio/issues/195",
            created_at="2026-11-26T15:00:00Z",updated_at="2026-11-26T15:00:00Z")
        self.pr = {"number":195,"state":"open","head":{"sha":H,"ref":"a/test",
                   "repo":{"full_name":"frenndak/SmartSVG-Studio"}}}
        self.drift = False

    def get(self,path):
        if path=="/git/commits/"+H:
            return {"sha":H,"committer":{"date":"2026-11-26T14:00:00Z"}}
        if path=="/issues/comments/123":
            return dict(self.comment,body="edited") if self.drift else self.comment
        if path=="/pulls/195":
            return self.pr
        if path=="/git/ref/heads/a/test":
            return {"ref":"refs/heads/a/test","object":{"type":"commit","sha":H}}
        if path=="/branches/main":
            return {"commit":{"sha":M}}
        raise KeyError(path)

    def run_hint(self,extra=()):
        self.comment["body"]="Technical review details\n"+PREFIX+json.dumps(self.value)
        snapshot={"candidates":[{"pr":self.pr,"comments":[self.comment,*extra]}]}
        return route_checkpoints(self.plan,snapshot,self.get)

    def test_adverse_hint_survives_reconstruction_without_authority(self):
        plan, reports = self.run_hint()
        self.assertEqual(plan.proposals[0].action,"VERIFY_FINDING")
        self.assertEqual(reports[0]["qualification"],"UNAUTHENTICATED_ADVISORY_ONLY")
        self.assertNotIn("body",reports[0])
        self.assertEqual(self.run_hint(),(plan,reports))

    def test_favorable_only_qualifies_and_missing_ci_inspects(self):
        self.value["verdict"]="FAVORABLE"
        self.assertEqual(self.run_hint()[0].proposals[0].action,"QUALIFY_ONLY")
        self.plan=replace(self.plan,proposals=(replace(self.plan.proposals[0],
            steps=(StepReceipt("g0",Status.SKIP),)),))
        self.assertEqual(self.run_hint()[0].proposals[0].action,"CI_INSPECT")

    def test_partial_does_not_fake_review_completion(self):
        self.value["verdict"]="PARTIAL"
        plan,reports=self.run_hint()
        self.assertEqual(plan.proposals[0].action,"REVIEW")
        self.assertIn("RESUME_PARTIAL_REVIEW",plan.proposals[0].reasons)

    def test_stale_main_wrong_role_and_edit_are_not_used(self):
        for key,value in (("main","d"*40),("head","d"*40),("role","A")):
            previous=self.value[key]
            self.value[key]=value
            self.assertEqual(self.run_hint(),(self.plan,[]))
            self.value[key]=previous
        self.drift=True
        self.assertEqual(self.run_hint(),(self.plan,[]))

    def test_newer_invalid_marker_does_not_resurrect_old_verdict(self):
        newer=dict(self.comment,id=124,body=PREFIX+"{")
        self.assertEqual(self.run_hint((newer,)),(self.plan,[]))

    def test_raw_failure_is_never_overridden(self):
        self.plan=replace(self.plan,proposals=(replace(self.plan.proposals[0],
            action="FIX_REQUIRED"),))
        self.value["verdict"]="FAVORABLE"
        self.assertEqual(self.run_hint(),(self.plan,[]))

    def test_edited_comment_and_precommit_comment_are_not_used(self):
        self.comment["updated_at"]="2026-11-26T15:10:00Z"
        self.assertEqual(self.run_hint(),(self.plan,[]))
        self.comment["created_at"]=self.comment["updated_at"]="2026-11-26T13:00:00Z"
        self.assertEqual(self.run_hint(),(self.plan,[]))

    def test_changed_or_closed_pr_is_quarantined_not_reviewed_again(self):
        for state, head in (("open","d"*40),("closed",H)):
            self.pr["state"]=state
            self.pr["head"]["sha"]=head
            plan,reports=self.run_hint()
            self.assertEqual(plan.proposals,())
            self.assertEqual(plan.unknown,(195,))
            self.assertFalse(plan.queue_complete)
            self.assertEqual(plan.code_wip,1)
            self.assertEqual(reports,[])

    def test_diverged_branch_is_quarantined(self):
        original=self.get
        def get(path):
            if path=="/git/ref/heads/a/test":
                return {"ref":"refs/heads/a/test","object":{"type":"commit","sha":"d"*40}}
            return original(path)
        self.get=get
        plan,reports=self.run_hint()
        self.assertEqual(plan.proposals,())
        self.assertEqual(plan.unknown,(195,))
        self.assertEqual(reports,[])

    def test_other_candidate_survives_quarantine(self):
        other=replace(self.plan.proposals[0],number=196,action="FIX_REQUIRED")
        self.plan=replace(self.plan,proposals=(*self.plan.proposals,other),code_wip=2)
        self.pr["state"]="closed"
        plan,reports=self.run_hint()
        self.assertEqual(plan.proposals,(other,))
        self.assertEqual(plan.code_wip,2)
        self.assertEqual(plan.unknown,(195,))
        self.assertEqual(reports,[])
