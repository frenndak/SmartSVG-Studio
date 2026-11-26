import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from tools.smartsvg_controller_relay import make_checkpoint,read_checkpoint,write_checkpoint,compare_checkpoint


class RelayTests(unittest.TestCase):
    def report(self):
        return {"mode":"LIVE_SHADOW_COMMISSIONING","merge_authorized":False,
                "agent_work_executed":False,"active_leases":0,"main":"a"*40,"policy_blob":"b"*40,
                "assignments":{"A":{"number":192,"head":"c"*40,"action":"REVIEW",
                                    "plan_digest":"d"*64,"private":"never export"},"B":None}}

    def test_disk_roundtrip_and_cross_run(self):
        a=make_checkpoint(self.report(),100,1)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"relay.json"
            write_checkpoint(p,a)
            prior=read_checkpoint(p)
            self.assertNotIn("private",p.read_text())
            self.assertEqual(prior,a)
            fresh=make_checkpoint(self.report(),101,1)
            r=compare_checkpoint(prior,fresh)
            self.assertEqual(r["status"],"PRIOR_RUN_RELAY")
            self.assertEqual(r["roles"]["A"],"SAME_ADVISORY_PLAN")
            self.assertEqual(r["qualification"],"ADVISORY_ONLY")

    def test_same_run_required_and_drift(self):
        a=make_checkpoint(self.report(),100,1)
        self.assertEqual(compare_checkpoint(a,a,require_current=True)["status"],"SAME_RUNNER_RELAY")
        with self.assertRaises(ValueError):
            compare_checkpoint(a,make_checkpoint(self.report(),101,1),require_current=True)
        b=deepcopy(a)
        b["main"]="e"*40
        self.assertEqual(compare_checkpoint(a,b)["roles"]["A"],"CONTEXT_CHANGED")
        b=deepcopy(a)
        b["assignments"]["A"]["plan_digest"]="e"*64
        self.assertEqual(compare_checkpoint(a,b)["roles"]["A"],"PLAN_CHANGED")

    def test_untrusted_extra_fields_and_duplicate_keys_rejected(self):
        a=make_checkpoint(self.report(),100,1)
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"relay.json"
            self.assertIsNone(read_checkpoint(p))
            a["lease"]="not allowed"
            p.write_text(json.dumps(a))
            with self.assertRaises(ValueError):
                read_checkpoint(p)
            p.write_text('{"version":1,"version":1}')
            with self.assertRaises(ValueError):
                read_checkpoint(p)

    def test_no_work_authority_or_active_lease_export(self):
        for key,value in (("merge_authorized",True),("agent_work_executed",True),("active_leases",1)):
            r=self.report()
            r[key]=value
            with self.assertRaises(ValueError):
                make_checkpoint(r,100,1)
        with self.assertRaises(ValueError):
            compare_checkpoint(None,make_checkpoint(self.report(),100,1),require_current=True)
