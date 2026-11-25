import contextlib
import io
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.smartsvg_controller_cli import main, read_json, simulate

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
                     "draft":False,"mergeable":True},"runs":[],
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
