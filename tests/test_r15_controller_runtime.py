import unittest
from unittest.mock import patch
from tools.smartsvg_controller_runtime import envelope,route

H="a"*40
P="b"*40
C="c"*40


class RuntimeRoutingTests(unittest.TestCase):
    def report(self):
        return {"main":H,"policy_blob":P,"observed_at":"2026-11-26T03:00:00+00:00",
                "queue_complete":True,"code_wip":1,"unknown":[],
                "merge_authorized":False,"agent_work_executed":False,
                "final_queue_readback":"ADVISORY",
                "assignments":{"A":{"number":197,"head":H,"action":"REVIEW",
                                    "plan_digest":"d"*64,"raw":"excluded"},"B":None}}

    def test_public_envelope_contains_only_reduced_routing(self):
        r=envelope(self.report(),10,1,C)
        self.assertEqual(r["assignments"]["A"]["number"],197)
        self.assertNotIn("raw",r["assignments"]["A"])
        self.assertEqual(r["controller_head"],C)
        self.assertFalse(r["merge_authorized"])
        self.assertFalse(r["agent_work_executed"])

    def test_no_probe_dependency_even_when_queue_is_empty(self):
        snapshot={"main":{"commit":{"sha":H}},"policy_blob":P,"candidates":[]}
        report=self.report()
        report["assignments"]["A"]=None
        report["code_wip"]=0
        with patch("tools.smartsvg_controller_runtime.observe",return_value=snapshot), patch(
                "tools.smartsvg_controller_runtime.simulate",return_value=report) as simulate:
            r=route(object(),"fixture",run_id=10,attempt=1,controller_head=C)
            self.assertEqual(r["assignments"],{"A":None,"B":None})
            self.assertNotIn("ci_manifest",simulate.call_args.kwargs)
            self.assertEqual(simulate.call_args.args[1]["scopes"],[])

    def test_nonlive_or_mutation_authority_refused(self):
        for key,value in (("merge_authorized",True),("agent_work_executed",True),
                          ("final_queue_readback","NOT_REQUESTED")):
            r=self.report()
            r[key]=value
            with self.assertRaises(ValueError):
                envelope(r,10,1,C)
