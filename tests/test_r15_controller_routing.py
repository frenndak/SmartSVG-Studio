import json
import unittest
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from tools.smartsvg_controller_cli import simulate
from tools.smartsvg_controller_review import TASKS

FIXTURE = Path(__file__).with_name("fixtures") / "r15_queue_replay_20261125.json"


class RoutingTests(unittest.TestCase):
    def setUp(self):
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.snapshot, self.manifest = data["snapshot"], data["manifest"]
        self.now = datetime.fromisoformat(self.snapshot["finished_at"])

    def packet(self, number, verdict="FAVORABLE"):
        p = next(x for x in self.snapshot["candidates"] if x["pr"]["number"] == number)
        scope = next(x for x in self.manifest["scopes"] if x["number"] == number)
        writer = scope["writer"]
        role = "B" if writer == "A" else "A"
        h, m, policy = scope["head"], self.manifest["main"], self.manifest["policy_blob"]
        t0,t1,t2,t3 = ("2026-11-25T16:00:00Z","2026-11-25T17:00:00Z",
                        "2026-11-25T17:01:00Z","2026-11-25T17:02:00Z")
        body = "Synthetic technical review for test only"
        comment = {"id":number,"body":body,"user":{"login":"frenndak"},
                   "issue_url":"https://api.github.com/repos/frenndak/SmartSVG-Studio/issues/"+str(number),
                   "created_at":t2,"updated_at":t2}
        p["comments"] = [comment]
        receipt = {"version":1,"number":number,"head":h,"main":m,
                   "policy_blob":policy,"role":role,"run_id":"review-run",
                   "author_run":"author-run","comment_id":number,
                   "comment_sha256":sha256(body.encode()).hexdigest(),"verdict":verdict}
        scheduler = {"id":TASKS[role],"is_enabled":True,"run_details":{
            "last_run":{"id":"review-run","recorded_status":"completed","started_at":t1,"completed_at":t3},
            "latest_result":{"run_id":"review-run","created_at":t3,"content_truncated":False,
                             "requires_user_action":False,"is_failure_message":False,
                             "content_text":"R15_REVIEW_RECEIPT "+json.dumps(
                                 receipt,sort_keys=True,separators=(",",":"))}}}
        return {"number":number,"head":h,"main":m,"policy_blob":policy,"writer":writer,
                "role":role,"author_run":"author-run","author_completed_at":t0,
                "head_committed_at":t0,"comment_id":number,"scheduler":scheduler}

    def report(self,*packets):
        return simulate(self.snapshot,self.manifest,now=self.now,review_packets=packets)

    def action(self,r,n):
        return next(x["action"] for x in r["candidates"] if x["number"]==n)

    def test_favorable_routes_qualification_not_merge(self):
        r=self.report(self.packet(195))
        self.assertEqual(self.action(r,195),"QUALIFY_ONLY")
        self.assertEqual(r["assignments"]["B"]["action"],"QUALIFY_ONLY")
        self.assertFalse(r["merge_authorized"])
        self.assertEqual(r["review_verification"],"NOT_QUALIFIED")

    def test_missing_cpu_routes_diagnostic_not_retry_or_merge(self):
        r=self.report(self.packet(194))
        self.assertEqual(self.action(r,194),"CI_INSPECT")
        p=next(x for x in r["candidates"] if x["number"]==194)
        self.assertIn("cpu:UNKNOWN",p["reasons"])
        self.assertFalse(r["merge_authorized"])

    def test_adverse_and_partial_are_distinct(self):
        self.assertEqual(self.action(self.report(self.packet(195,"ADVERSE")),195),"VERIFY_FINDING")
        self.assertEqual(self.action(self.report(self.packet(195,"PARTIAL")),195),"REVIEW")

    def test_stale_duplicate_and_missing_comment_never_replaces_review(self):
        p=self.packet(195)
        self.assertEqual(self.action(self.report(p,p),195),"REVIEW")
        p["main"]="f"*40
        self.assertEqual(self.action(self.report(p),195),"REVIEW")
        p=self.packet(195)
        next(x for x in self.snapshot["candidates"] if x["pr"]["number"]==195)["comments"]=[]
        self.assertEqual(self.action(self.report(p),195),"REVIEW")

    def test_ci_failure_not_overridden(self):
        p=self.packet(195)
        row=next(x for x in self.snapshot["candidates"] if x["pr"]["number"]==195)
        row["runs"][0]["run"]["conclusion"]="failure"
        self.assertEqual(self.action(self.report(p),195),"FIX_REQUIRED")
