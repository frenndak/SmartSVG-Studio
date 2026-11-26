import json
import unittest
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from tools.smartsvg_controller_exchange import AUTHOR_PREFIX, derive_review_packets
from tools.smartsvg_controller_review import PREFIX, TASKS, _canonical
from tools.smartsvg_controller_orchestration import build_plan, Scope
from tools.smartsvg_controller_routing import route_review_hints

FIXTURE=Path(__file__).with_name("fixtures")/"r15_queue_replay_20261125.json"


class ExchangeTests(unittest.TestCase):
    def setUp(self):
        data=json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.snapshot=data["snapshot"]
        self.now=datetime.fromisoformat(self.snapshot["finished_at"])
        self.plan=build_plan(self.snapshot,tuple(Scope(**s) for s in data["manifest"]["scopes"]),now=self.now)
        self.pr=next(x for x in self.snapshot["candidates"] if x["pr"]["number"]==195)
        self.p=next(x for x in self.plan.proposals if x.number==195)
        common={"version":1,"number":195,"head":self.p.head,"main":self.plan.main,
                "policy_blob":self.plan.policy_blob}
        self.tasks=[]
        self.comments={}
        for role,ident,start,end,when,prefix in (
            ("A",701,"2026-11-25T16:00:00Z","2026-11-25T16:05:00Z","2026-11-25T16:03:00Z",AUTHOR_PREFIX),
            ("B",702,"2026-11-25T17:00:00Z","2026-11-25T17:02:00Z","2026-11-25T17:01:00Z",PREFIX)):
            body="fixture only "+role
            comment={"id":ident,"body":body,"user":{"login":"frenndak"},
                     "issue_url":"https://api.github.com/repos/frenndak/SmartSVG-Studio/issues/195",
                     "created_at":when,"updated_at":when}
            self.comments[ident]=comment
            receipt=dict(common,role=role,run_id="run-"+role,comment_id=ident,
                         comment_sha256=sha256(body.encode()).hexdigest())
            if role=="B":
                receipt.update(author_run="run-A",verdict="FAVORABLE")
            self.tasks.append({"id":TASKS[role],"is_enabled":True,"run_details":{
                "last_run":{"id":"run-"+role,"recorded_status":"completed","scheduled_for":start,
                            "started_at":start,"completed_at":end},
                "latest_result":{"run_id":"run-"+role,"created_at":end,"completed_at":end,
                                 "content_truncated":False,"requires_user_action":False,
                                 "is_failure_message":False,"content_text":prefix+_canonical(receipt)}}})
        self.pr["comments"]=list(self.comments.values())
        self.scheduler={"captured_at":self.now.isoformat(),"automations":self.tasks}

    def get(self,path):
        if path=="/git/commits/"+self.p.head:
            return {"sha":self.p.head,"committer":{"date":"2026-11-25T16:02:00Z"}}
        if path.startswith("/issues/comments/"):
            return deepcopy(self.comments[int(path.rsplit("/",1)[1])])
        if path=="/pulls/195":
            return self.pr["pr"]
        if path=="/git/ref/heads/"+self.pr["pr"]["head"]["ref"]:
            return {"ref":"refs/heads/"+self.pr["pr"]["head"]["ref"],
                    "object":{"type":"commit","sha":self.p.head}}
        if path=="/branches/main":
            return {"commit":{"sha":self.plan.main}}
        raise KeyError(path)

    def derive(self,get=None):
        return derive_review_packets(self.plan,self.snapshot,self.scheduler,get or self.get,now=self.now)

    def test_two_explicit_cycles_route_advisory_only(self):
        packets,reports=self.derive()
        self.assertEqual(len(packets),1)
        r=next(x for x in reports if x["number"]==195)
        self.assertEqual(r["status"],"CORRELATED_FAVORABLE")
        self.assertEqual(r["qualification"],"IMPORTED_CORRELATION_ONLY")
        p=next(x for x in route_review_hints(self.plan,self.snapshot,packets).proposals if x.number==195)
        self.assertEqual(p.action,"QUALIFY_ONLY")

    def test_narrative_author_cannot_be_invented(self):
        self.tasks[0]["run_details"]["latest_result"]["content_text"]="Work completed"
        packets,reports=self.derive()
        self.assertEqual(packets,())
        self.assertEqual(next(x for x in reports if x["number"]==195)["reason"],"AUTHOR_RECEIPT_UNAVAILABLE")

    def test_edited_review_comment_invalidates(self):
        def get(path):
            value=self.get(path)
            if path=="/issues/comments/702":
                value["body"]="changed"
            return value
        self.assertEqual(self.derive(get)[0],())

    def test_commit_outside_author_cycle_invalidates(self):
        def get(path):
            value=self.get(path)
            if path.startswith("/git/commits/"):
                value["committer"]["date"]="2026-11-25T15:00:00Z"
            return value
        self.assertEqual(self.derive(get)[0],())

    def test_wrong_author_cycle_identity_invalidates(self):
        r=self.tasks[1]["run_details"]["latest_result"]
        receipt=json.loads(r["content_text"][len(PREFIX):])
        receipt["author_run"]="other"
        r["content_text"]=PREFIX+_canonical(receipt)
        self.assertEqual(self.derive()[0],())

    def test_branch_drift_invalidates(self):
        def get(path):
            value=self.get(path)
            if path.startswith("/git/ref/"):
                value["object"]["sha"]="f"*40
            return value
        self.assertEqual(self.derive(get)[0],())
