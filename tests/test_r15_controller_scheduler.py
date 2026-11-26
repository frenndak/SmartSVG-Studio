import json
import unittest
from copy import deepcopy
from datetime import datetime, timezone, timedelta

from tools.smartsvg_controller_scheduler import inspect_scheduler
from tools.smartsvg_controller_review import TASKS, PREFIX

NOW=datetime(2026,11,26,1,30,tzinfo=timezone.utc)


def fixture():
    # Shape and timing pattern observed through actual connector peek.
    # Synthetic identifiers/result text; not a historical review receipt.
    tasks=[]
    for role in ("A","B"):
        run={"id":"fixture-"+role,"recorded_status":"completed",
             "scheduled_for":"2026-11-26T01:25:00Z",
             "started_at":"2026-11-26T01:21:34Z","completed_at":"2026-11-26T01:22:05Z"}
        result={"run_id":run["id"],"created_at":"2026-11-26T01:22:05Z",
                "completed_at":run["completed_at"],"content_truncated":False,
                "requires_user_action":False,"is_failure_message":False,
                "content_text":"PRIVATE_RESULT_EXAMPLE"}
        tasks.append({"id":TASKS[role],"is_enabled":True,"prompt":"PRIVATE_PROMPT_EXAMPLE",
                      "run_details":{"last_run":run,"latest_result":result}})
    return {"captured_at":NOW.isoformat(),"automations":tasks}


class SchedulerReadbackTests(unittest.TestCase):
    def test_actual_shape_narrative_is_not_review(self):
        r=inspect_scheduler(fixture(),now=NOW)
        for report in r.values():
            self.assertEqual(report["status"],"COMPLETED")
            self.assertEqual(report["reason"],"NARRATIVE_ONLY")
            self.assertFalse(report["review_qualified"])
            self.assertFalse(report["native_approval"])
        self.assertNotIn("PRIVATE_",json.dumps(r))

    def test_missing_disabled_or_duplicate_task_is_isolated(self):
        f=fixture()
        f["automations"][0]["is_enabled"]=False
        self.assertEqual(inspect_scheduler(f,now=NOW)["A"]["reason"],"TASK_DISABLED_OR_UNKNOWN")
        f["automations"].append(deepcopy(f["automations"][0]))
        self.assertEqual(inspect_scheduler(f,now=NOW)["A"]["reason"],"TASK_AMBIGUOUS")
        self.assertEqual(inspect_scheduler(f,now=NOW)["B"]["reason"],"NARRATIVE_ONLY")

    def test_future_and_stale_capture_rejected(self):
        for delta in (timedelta(seconds=1),timedelta(minutes=-6)):
            f=fixture()
            f["captured_at"]=(NOW+delta).isoformat()
            with self.assertRaises(ValueError):
                inspect_scheduler(f,now=NOW)

    def test_last_result_must_match_latest_run(self):
        f=fixture()
        d=f["automations"][0]["run_details"]
        d["latest_result"]["run_id"]="older"
        self.assertEqual(inspect_scheduler(f,now=NOW)["A"]["reason"],"LATEST_RESULT_MISMATCH")
        d["last_run"]["recorded_status"]="in_progress"
        self.assertEqual(inspect_scheduler(f,now=NOW)["A"]["reason"],"LATEST_CYCLE_NOT_COMPLETED")

    def test_blocked_or_truncated_result(self):
        for flag in ("requires_user_action","is_failure_message","content_truncated"):
            f=fixture()
            f["automations"][0]["run_details"]["latest_result"][flag]=True
            self.assertEqual(inspect_scheduler(f,now=NOW)["A"]["reason"],"RESULT_INCOMPLETE_OR_BLOCKED")

    def test_receipt_present_still_not_correlated(self):
        f=fixture()
        d=f["automations"][0]["run_details"]
        d["latest_result"]["content_text"]=PREFIX+json.dumps({"run_id":d["last_run"]["id"],"role":"A"})
        r=inspect_scheduler(f,now=NOW)["A"]
        self.assertEqual(r["reason"],"RECEIPT_PRESENT_NOT_CORRELATED")
        self.assertFalse(r["review_qualified"])

    def test_cli_report_integration(self):
        from test_r15_controller_cli import inputs
        from tools.smartsvg_controller_cli import simulate
        s,m=inputs(NOW)
        r=simulate(s,m,now=NOW,scheduler_snapshot=fixture())
        self.assertEqual(r["scheduler_verification"],"IMPORTED_METADATA_ONLY")
        self.assertEqual(r["scheduler_reports"]["B"]["reason"],"NARRATIVE_ONLY")
        self.assertFalse(r["merge_authorized"])
        self.assertFalse(r["agent_work_executed"])
