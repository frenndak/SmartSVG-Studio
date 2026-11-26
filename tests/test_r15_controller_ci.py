import json
import unittest
from datetime import datetime
from pathlib import Path

from tools.smartsvg_controller_ci import inspect_ci
from tools.smartsvg_controller_observation import ObservationError
from tools.smartsvg_controller_orchestration import Scope, build_plan

FIXTURE=Path(__file__).with_name("fixtures")/"r15_queue_replay_20261125.json"
PIN="a"*40
PATH=".github/workflows/stability-qualification.yml"
TEST="test_example.Example.test_export"


class CICompositionTests(unittest.TestCase):
    def setUp(self):
        data=json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.snapshot=data["snapshot"]
        self.plan=build_plan(self.snapshot,tuple(Scope(**s) for s in data["manifest"]["scopes"]),
            now=datetime.fromisoformat(self.snapshot["finished_at"]))
        self.entry=next(x for x in self.snapshot["candidates"] if x["pr"]["number"]==195)
        self.pr=self.entry["pr"]
        self.run=next(x for x in self.entry["runs"] if x["run"]["path"]==PATH)
        self.job=self.run["jobs"][0]
        self.manifest={"main":self.plan.main,"policy_blob":self.plan.policy_blob,
            "pins":{PATH:PIN},"candidates":[{"number":195,"head":self.pr["head"]["sha"],
                                            "checks":{"windows_python":[TEST]}}]}
        self.packet={"head":self.pr["head"]["sha"],"run_id":self.run["run"]["id"],
            "attempt":1,"job_id":self.job["id"],"log":"test_export ("+TEST+") ... ok"}

    def source(self,path):
        if path.startswith("/contents/"):
            return {"sha":PIN}
        if path=="/actions/runs/"+str(self.run["run"]["id"]):
            return self.run["run"]
        if path=="/actions/jobs/"+str(self.job["id"]):
            return self.job
        if path=="/pulls/195":
            return self.pr
        if path=="/git/ref/heads/"+self.pr["head"]["ref"]:
            return {"ref":"refs/heads/"+self.pr["head"]["ref"],
                    "object":{"type":"commit","sha":self.pr["head"]["sha"]}}
        if path=="/branches/main":
            return {"commit":{"sha":self.plan.main}}
        raise AssertionError(path)

    def report(self,source=None,logs=None):
        return inspect_ci(self.plan,self.manifest,source or self.source,
                          [self.packet] if logs is None else logs)[0]

    def test_matching_pin_step_and_log_still_advisory(self):
        r=self.report()
        self.assertEqual(r["status"],"STEP_MATCHED")
        self.assertEqual(r["tests"][0]["status"],"PASS")
        self.assertEqual(r["qualification"],"ADVISORY_ONLY")
        self.assertEqual(r["reason"],"IMPORTED_LOG_ONLY_NOT_AUTHENTICATED")
        self.assertNotIn(self.packet["log"],json.dumps(r))

    def test_pin_mismatch_and_missing_pin(self):
        self.manifest["pins"][PATH]="b"*40
        self.assertEqual(self.report()["reason"],"WORKFLOW_PIN_NOT_MATCHED")
        self.manifest["pins"]={}
        self.assertEqual(self.report()["reason"],"WORKFLOW_PIN_NOT_MATCHED")

    def test_rerun_attempt_invalidates_step(self):
        def get(path):
            value=self.source(path)
            if path.startswith("/actions/runs/"):
                return dict(value,run_attempt=2)
            return value
        self.assertEqual(self.report(get)["reason"],"RUN_JOB_OR_ATTEMPT_CHANGED")

    def test_log_duplicate_or_wrong_attempt_not_accepted(self):
        for logs in ([self.packet,self.packet],[dict(self.packet,attempt=2)],[]):
            self.assertEqual(self.report(logs=logs)["reason"],"IMPORTED_LOG_MISSING_OR_AMBIGUOUS")

    def test_skipped_test_not_pass(self):
        packet=dict(self.packet,log="test_export ("+TEST+") ... skipped 'fixture'")
        self.assertEqual(self.report(logs=[packet])["tests"][0]["status"],"SKIP")

    def test_branch_drift_and_main_drift(self):
        def get(path):
            value=self.source(path)
            if path.startswith("/git/ref/"):
                value["object"]["sha"]="f"*40
            return value
        self.assertEqual(self.report(get)["reason"],"PR_CONTEXT_CHANGED")
        def main_changed(path):
            if path=="/branches/main":
                return {"commit":{"sha":"f"*40}}
            return self.source(path)
        with self.assertRaises(ObservationError):
            self.report(main_changed)

    def test_stale_manifest_and_duplicate_candidate_rejected(self):
        self.manifest["candidates"].append(self.manifest["candidates"][0])
        with self.assertRaises(ValueError):
            self.report()
        self.manifest["candidates"].pop()
        self.manifest["main"]="f"*40
        with self.assertRaises(ValueError):
            self.report()
