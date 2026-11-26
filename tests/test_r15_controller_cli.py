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
