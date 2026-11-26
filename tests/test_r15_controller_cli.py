import contextlib
import io
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.smartsvg_controller_cli import main, read_json, simulate
from tools.smartsvg_controller_observation import ObservationError

NOW = datetime(2026, 11, 25, 15, 0, tzinfo=timezone.utc)
M, P, H, J, K = (c*40 for c in "abcde")
REPO = "frenndak/SmartSVG-Studio"


def inputs(now=NOW):
    rows = []
    scopes = []
    for n, head, writer, code in ((192,H,"B",True),(195,J,"A",True),
                                    (196,K,"OWNER",False)):
        rows.append({"pr":{"number":n,"state":"open","head":{"sha":head,
                     "repo":{"full_name":REPO}},"base":{"ref":"main",
                     "repo":{"full_name":REPO}},"user":{"login":"frenndak"},
                     "draft":False,"mergeable":True},"branch":{"status":"MATCH","sha":head},"runs":[],
                     "comments":[{"body":"SECRET_EXAMPLE_DO_NOT_PRINT"}],"reviews":[]})
        scopes.append({"number":n,"head":head,"writer":writer,"code_only":code})
    snapshot = {"qualification":"RAW_ONLY","started_at":now.isoformat(),
                "finished_at":now.isoformat(),"main":{"commit":{"sha":M}},
                "policy_blob":P,"candidates":rows}
    return snapshot, {"main":M,"policy_blob":P,"scopes":scopes}


class CliTests(unittest.TestCase):
    def test_simulation_real_modules_and_no_output_leak(self):
        s,m = inputs()
        r = simulate(s,m,now=NOW)
        self.assertEqual(r["assignments"]["A"]["number"],192)
        self.assertEqual(r["assignments"]["B"]["number"],195)
        self.assertEqual(r["code_wip"],2)
        self.assertFalse(r["merge_authorized"])
        self.assertFalse(r["persistent_writes"])
        self.assertEqual(r["candidates"][2]["action"],"OWNER_REVIEW")
        self.assertNotIn("SECRET_EXAMPLE_DO_NOT_PRINT",json.dumps(r))
        self.assertEqual(len(r["candidates"][0]["steps"][0]["digest"]),64)

    def test_changed_context_and_stale_snapshot_rejected(self):
        s,m = inputs()
        m["policy_blob"] = H
        with self.assertRaises(ValueError):
            simulate(s,m,now=NOW)
        s,m = inputs()
        with self.assertRaises(ValueError):
            simulate(s,m,now=NOW+timedelta(minutes=6))

    def test_unknown_scope_not_assigned(self):
        s,m = inputs()
        m["scopes"].pop(0)
        r = simulate(s,m,now=NOW)
        self.assertIsNone(r["assignments"]["A"])
        self.assertFalse(r["queue_complete"])
        self.assertEqual(r["unknown"],(192,))

    def test_cli_offline_and_no_network(self):
        s,m = inputs(datetime.now(timezone.utc))
        with tempfile.TemporaryDirectory() as tmp:
            a,b = Path(tmp)/"snapshot.json", Path(tmp)/"scopes.json"
            a.write_text(json.dumps(s),encoding="utf-8")
            b.write_text(json.dumps(m),encoding="utf-8")
            out = io.StringIO()
            with patch("tools.smartsvg_controller_cli.observe",
                       side_effect=AssertionError("network forbidden")), contextlib.redirect_stdout(out):
                self.assertEqual(main(["--snapshot",str(a),"--scopes",str(b)]),0)
            self.assertEqual(json.loads(out.getvalue())["mode"],"SHADOW_DRY_RUN")
            self.assertEqual({p.name for p in Path(tmp).iterdir()},
                             {"snapshot.json","scopes.json"})

    def test_duplicate_input_and_redacted_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)/"private-test.json"
            p.write_text('{"x":1,"x":2}',encoding="utf-8")
            with self.assertRaises(ValueError):
                read_json(p)
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(main(["--snapshot",str(p),"--scopes",str(p)]),2)
            self.assertFalse(json.loads(err.getvalue())["merge_authorized"])
            self.assertNotIn(str(p),err.getvalue())


def scope_source(snapshot, *, bad=(), old=(), excluded=()):
    """Synthetic REST source; no actual GitHub reads in these tests."""
    rows = {r["pr"]["number"]: r["pr"] for r in snapshot["candidates"]}
    def get(path):
        if path == "/branches/main":
            return {"commit": {"sha": M}}
        if path.startswith("/pulls?state=open"):
            return [dict(pr,id=n) for n,pr in rows.items()]
        if path.startswith("/actions/runs?"):
            head=path.split("head_sha=",1)[1].split("&",1)[0]
            entries=next(r["runs"] for r in snapshot["candidates"] if r["pr"]["head"]["sha"]==head)
            runs=[entry["run"] for entry in entries]
            return {"total_count":len(runs),"workflow_runs":runs}
        if path.startswith("/actions/runs/") and "/jobs?" in path:
            rid=int(path.split("/")[3])
            jobs=next(entry["jobs"] for r in snapshot["candidates"] for entry in r["runs"]
                      if entry["run"]["id"]==rid)
            return {"total_count":len(jobs),"jobs":jobs}
        if path.startswith("/git/ref/heads/scope/"):
            n = int(path.rsplit("/",1)[1])
            return {"ref": "refs/heads/scope/"+str(n),
                    "object": {"type":"commit","sha":rows[n]["head"]["sha"]}}
        if path.startswith("/pulls/"):
            n = int(path.split("/")[2])
            if n in bad:
                raise PermissionError("fixture missing")
            if "/files?" in path:
                name = ("docs/policy.md" if n in excluded or n == 196
                        else "engine/native.py" if n == 195 else "tests/test_x.py")
                return [{"filename":name,"status":"modified","sha":P,"patch":"@@ fixture"}]
            pr = json.loads(json.dumps(rows[n]))
            pr["head"]["ref"] = "scope/"+str(n)
            pr["base"]["sha"] = K if n in old else M
            pr["changed_files"] = 1
            return pr
        raise AssertionError(path)
    return get


class LiveScopeWiringTests(unittest.TestCase):
    def test_live_paths_can_narrow_but_not_authorize(self):
        s,m = inputs()
        r = simulate(s,m,now=NOW,scope_get=scope_source(s,excluded=(192,)))
        by = {x["number"]:x for x in r["candidates"]}
        self.assertEqual(by[192]["action"],"OWNER_REVIEW")
        self.assertIsNone(r["assignments"]["A"])
        self.assertEqual(r["assignments"]["B"]["number"],195)
        self.assertEqual(r["scope_verification"],"PATHS_ONLY")
        self.assertFalse(r["merge_authorized"])
        self.assertEqual(r["code_wip"],2)
        self.assertTrue(all(len(x["receipt_digest"])==64 for x in r["scope_reports"]))

    def test_one_unavailable_inventory_keeps_other_work(self):
        s,m = inputs()
        r = simulate(s,m,now=NOW,scope_get=scope_source(s,bad=(192,)))
        self.assertEqual(r["unknown"],(192,))
        self.assertEqual(r["scope_verification"],"PATHS_ONLY_PARTIAL")
        self.assertFalse(r["queue_complete"])
        self.assertEqual(r["code_wip"],2)
        self.assertEqual(r["assignments"]["B"]["number"],195)
        self.assertFalse(r["merge_authorized"])

    def test_owner_inventory_failure_does_not_free_capacity(self):
        s,m = inputs()
        r = simulate(s,m,now=NOW,scope_get=scope_source(s,bad=(196,)))
        self.assertEqual(r["code_wip"],3)
        self.assertEqual(r["unknown"],(196,))
        self.assertFalse(r["queue_complete"])

    def test_old_base_is_explicit_and_not_a_false_conflict(self):
        s,m = inputs()
        r = simulate(s,m,now=NOW,scope_get=scope_source(s,old=(192,)))
        p=next(x for x in r["candidates"] if x["number"]==192)
        self.assertEqual(p["action"],"REVIEW")
        self.assertIn("BASE_CONTEXT_REQUIRES_REVIEW",p["reasons"])
        self.assertFalse(next(x for x in r["scope_reports"] if x["number"]==192)["base_matches_main"])

    def test_main_drift_fails_entire_observation(self):
        s,m=inputs()
        src=scope_source(s)
        calls=0
        def get(path):
            nonlocal calls
            if path=="/branches/main":
                calls+=1
                if calls>=7:
                    return {"commit":{"sha":K}}
            return src(path)
        with self.assertRaises(ObservationError):
            simulate(s,m,now=NOW,scope_get=get)


class PersistentRehearsalTests(unittest.TestCase):
    def test_reopen_recognizes_same_plan_and_keeps_evidence(self):
        from tools.smartsvg_controller_storage import OperationalJournal
        s,m=inputs()
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"shadow.sqlite"
            first=simulate(s,m,now=NOW,journal_path=path)
            second=simulate(s,m,now=NOW,journal_path=path)
            self.assertEqual(second["mode"],"SHADOW_PERSISTENT_REHEARSAL")
            self.assertTrue(second["persistent_writes"])
            self.assertFalse(second["agent_work_executed"])
            self.assertFalse(second["merge_authorized"])
            for role in ("A","B"):
                self.assertFalse(first["assignments"][role]["same_plan_as_previous"])
                self.assertTrue(second["assignments"][role]["same_plan_as_previous"])
                self.assertEqual(first["assignments"][role]["plan_digest"],
                                 second["assignments"][role]["plan_digest"])
            j=OperationalJournal(path)
            try:
                self.assertEqual(len(j.evidence_for(192,H,M,P,"STEP_ONLY")),5)
                self.assertEqual(j.db.execute("SELECT COUNT(*) FROM work WHERE expires>0").fetchone()[0],0)
            finally:
                j.close()

    def test_changed_head_does_not_reuse_checkpoint(self):
        s,m=inputs()
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"shadow.sqlite"
            simulate(s,m,now=NOW,journal_path=path)
            s["candidates"][0]["pr"]["head"]["sha"]=K
            s["candidates"][0]["branch"]["sha"]=K
            m["scopes"][0]["head"]=K
            r=simulate(s,m,now=NOW,journal_path=path)
            self.assertFalse(r["assignments"]["A"]["same_plan_as_previous"])
            self.assertTrue(r["assignments"]["B"]["same_plan_as_previous"])

    def test_live_scope_receipts_persist_and_deduplicate(self):
        from tools.smartsvg_controller_storage import OperationalJournal
        s,m=inputs()
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"shadow.sqlite"
            one=simulate(s,m,now=NOW,scope_get=scope_source(s),journal_path=path)
            two=simulate(s,m,now=NOW,scope_get=scope_source(s),journal_path=path)
            self.assertTrue(two["assignments"]["A"]["same_plan_as_previous"])
            self.assertEqual(one["scope_reports"],two["scope_reports"])
            j=OperationalJournal(path)
            try:
                self.assertEqual(len(j.evidence_for(192,H,M,P,"SCOPE_OBSERVATION")),1)
            finally:
                j.close()

    def test_existing_active_lease_not_stolen(self):
        from tools.smartsvg_controller_storage import OperationalJournal
        s,m=inputs()
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"shadow.sqlite"
            j=OperationalJournal(path)
            try:
                fence=j.claim("pr:192","f"*64,"A",300)
                self.assertIsNotNone(fence)
                r=simulate(s,m,now=NOW,journal_path=path)
                self.assertIsNone(r["assignments"]["A"])
                self.assertEqual(r["assignments"]["B"]["number"],195)
                self.assertTrue(j.release("pr:192","f"*64,"A",fence))
            finally:
                j.close()

    def test_cli_explicit_persistent_file(self):
        s,m=inputs(datetime.now(timezone.utc))
        with tempfile.TemporaryDirectory() as tmp:
            a,b,db=Path(tmp)/"snapshot.json",Path(tmp)/"scopes.json",Path(tmp)/"shadow.sqlite"
            a.write_text(json.dumps(s),encoding="utf-8")
            b.write_text(json.dumps(m),encoding="utf-8")
            out=io.StringIO()
            with contextlib.redirect_stdout(out):
                self.assertEqual(main(["--snapshot",str(a),"--scopes",str(b),"--journal",str(db)]),0)
            self.assertTrue(db.is_file())
            self.assertFalse(json.loads(out.getvalue())["merge_authorized"])


class FinalReadbackTests(unittest.TestCase):
    def test_head_change_after_inventory_is_quarantined(self):
        s,m=inputs()
        source=scope_source(s)
        def get(path):
            result=source(path)
            if path.startswith("/pulls?state=open"):
                result=json.loads(json.dumps(result))
                result[0]["head"]["sha"]=K
            return result
        r=simulate(s,m,now=NOW,scope_get=get)
        self.assertEqual(r["unknown"],(192,))
        self.assertFalse(r["queue_complete"])
        self.assertIsNone(r["assignments"]["A"])
        self.assertEqual(r["assignments"]["B"]["number"],195)
        old=next(x for x in r["scope_reports"] if x["number"]==192)
        self.assertEqual(old["qualification"],"INVALIDATED")
        self.assertNotIn("receipt_digest",old)

    def test_new_and_closed_pr_do_not_release_capacity(self):
        s,m=inputs()
        source=scope_source(s)
        def get(path):
            result=source(path)
            if path.startswith("/pulls?state=open"):
                return [pr for pr in result if pr["number"]!=192]+[
                    {"id":197,"number":197,"head":{"sha":K}}]
            return result
        r=simulate(s,m,now=NOW,scope_get=get)
        self.assertEqual(r["unknown"],(192,197))
        self.assertEqual(r["code_wip"],3)
        self.assertEqual(r["assignments"]["B"]["number"],195)

    def test_branch_moves_during_final_detail_read(self):
        s,m=inputs()
        source=scope_source(s)
        final=False
        def get(path):
            nonlocal final
            result=source(path)
            if path.startswith("/pulls?state=open"):
                final=True
            if final and path=="/git/ref/heads/scope/192":
                result["object"]["sha"]=K
            return result
        r=simulate(s,m,now=NOW,scope_get=get)
        self.assertEqual(r["unknown"],(192,))
        self.assertIsNone(r["assignments"]["A"])
        self.assertEqual(r["assignments"]["B"]["number"],195)

    def test_ci_context_change_cannot_leave_assignment(self):
        s,m=inputs()
        reports=[{"number":192,"head":H,"check":"g0","reason":"PR_CONTEXT_CHANGED",
                  "qualification":"ADVISORY_ONLY","status":"UNKNOWN","tests":[]}]
        with patch("tools.smartsvg_controller_cli.inspect_ci",return_value=reports):
            r=simulate(s,m,now=NOW,scope_get=scope_source(s),ci_manifest={})
        self.assertEqual(r["unknown"],(192,))
        self.assertIsNone(r["assignments"]["A"])
        self.assertEqual(r["ci_reports"][0]["reason"],"FINAL_QUEUE_CONTEXT_CHANGED")
        self.assertNotIn("receipt_digest",r["ci_reports"][0])

    def test_ci_attempt_change_replaces_stale_steps_with_inspection(self):
        s,m=inputs()
        reports=[{"number":192,"head":H,"check":"g0","reason":"RUN_JOB_OR_ATTEMPT_CHANGED",
                  "qualification":"ADVISORY_ONLY","status":"UNKNOWN","tests":[]}]
        with patch("tools.smartsvg_controller_cli.inspect_ci",return_value=reports):
            r=simulate(s,m,now=NOW,scope_get=scope_source(s),ci_manifest={})
        p=next(x for x in r["candidates"] if x["number"]==192)
        self.assertEqual(p["action"],"INSPECT")
        self.assertEqual(p["steps"],[])
        self.assertIn("CI_ATTEMPT_CHANGED",p["reasons"])
        self.assertFalse(r["merge_authorized"])


class FinalCIReadbackTests(unittest.TestCase):
    def failed_snapshot(self):
        s,m=inputs()
        run={"id":123,"path":".github/workflows/g0-admission-tests.yml",
             "head_sha":H,"event":"pull_request","run_attempt":1,
             "status":"completed","conclusion":"failure"}
        s["candidates"][0]["runs"]=[{"run":run,"jobs":[]}]
        return s,m,run

    def test_unchanged_failure_remains_repair(self):
        s,m,run=self.failed_snapshot()
        r=simulate(s,m,now=NOW,scope_get=scope_source(s))
        self.assertEqual(next(p for p in r["candidates"] if p["number"]==192)["action"],
                         "FIX_REQUIRED")

    def test_failed_attempt_now_queued_is_not_repaired_again(self):
        s,m,run=self.failed_snapshot()
        source=scope_source(s)
        def get(path):
            if path.startswith("/actions/runs?head_sha="+H):
                return {"total_count":1,"workflow_runs":[dict(run,run_attempt=2,
                         status="queued",conclusion=None)]}
            return source(path)
        r=simulate(s,m,now=NOW,scope_get=get)
        p=next(p for p in r["candidates"] if p["number"]==192)
        self.assertEqual(p["action"],"INSPECT")
        self.assertEqual(p["steps"],[])
        self.assertIn("CI_ATTEMPT_CHANGED",p["reasons"])
        self.assertEqual(r["assignments"]["B"]["number"],195)

    def test_new_run_after_missing_observation_invalidates_plan(self):
        s,m,run=self.failed_snapshot()
        s["candidates"][0]["runs"]=[]
        source=scope_source(s)
        def get(path):
            if path.startswith("/actions/runs?head_sha="+H):
                return {"total_count":1,"workflow_runs":[run]}
            return source(path)
        r=simulate(s,m,now=NOW,scope_get=get)
        self.assertEqual(next(p for p in r["candidates"] if p["number"]==192)["action"],"INSPECT")

    def test_unavailable_ci_does_not_block_independent_work(self):
        s,m,run=self.failed_snapshot()
        source=scope_source(s)
        def get(path):
            if path.startswith("/actions/runs?head_sha="+H):
                raise PermissionError("unavailable")
            return source(path)
        r=simulate(s,m,now=NOW,scope_get=get)
        p=next(p for p in r["candidates"] if p["number"]==192)
        self.assertEqual(p["reasons"],("CI_READBACK_UNAVAILABLE",))
        self.assertEqual(p["steps"],[])
        self.assertEqual(r["assignments"]["B"]["number"],195)
