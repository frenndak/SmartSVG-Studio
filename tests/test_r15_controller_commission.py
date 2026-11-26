import json
from pathlib import Path
import unittest
from tools.smartsvg_controller_commission import manifests, PROBE_HEAD, PROBE_TESTS

FIXTURE=Path(__file__).with_name("fixtures")/"r15_queue_replay_20261125.json"


class CommissionManifestTests(unittest.TestCase):
    def test_real_replay_routing_and_exact_probe(self):
        snapshot=json.loads(FIXTURE.read_text(encoding="utf-8"))["snapshot"]
        scopes,ci=manifests(snapshot)
        actual={p["number"]:(p["writer"],p["code_only"]) for p in scopes["scopes"]}
        self.assertEqual(actual,{192:("B",True),194:("B",True),195:("A",True),196:("OWNER",False)})
        self.assertEqual(ci["candidates"],[{"number":194,"head":PROBE_HEAD,
            "checks":{"windows_python":PROBE_TESTS}}])

    def test_unknown_branch_and_stale_probe_are_not_guessed(self):
        snapshot=json.loads(FIXTURE.read_text(encoding="utf-8"))["snapshot"]
        p=next(r["pr"] for r in snapshot["candidates"] if r["pr"]["number"]==194)
        p["head"]["sha"]="f"*40
        self.assertEqual(manifests(snapshot)[1]["candidates"],[])
        p["head"]["ref"]="unclassified/example"
        self.assertNotIn(194,{r["number"] for r in manifests(snapshot)[0]["scopes"]})


    def test_historical_writer_names_and_documentary_scope(self):
        snapshot=json.loads(FIXTURE.read_text(encoding="utf-8"))["snapshot"]
        cases={192:"code/v35-b-w05-sd0",194:"code/v35-w04-tests-b",
               195:"code/v35-a-w04-export",196:"governance/r15-promotion"}
        for row in snapshot["candidates"]:
            p=row["pr"]
            p["head"]["ref"]=cases[p["number"]]
        scopes,_=manifests(snapshot)
        self.assertEqual({p["number"]:(p["writer"],p["code_only"]) for p in scopes["scopes"]},
                         {192:("B",True),194:("B",True),195:("A",True),196:("OWNER",False)})

    def test_ambiguous_legacy_role_not_guessed(self):
        snapshot=json.loads(FIXTURE.read_text(encoding="utf-8"))["snapshot"]
        p=next(r["pr"] for r in snapshot["candidates"] if r["pr"]["number"]==194)
        for ref in ("code/v35-a-w04-b","code/v35-w04-tests","code/v35-b"):
            p["head"]["ref"]=ref
            self.assertNotIn(194,{r["number"] for r in manifests(snapshot)[0]["scopes"]})
