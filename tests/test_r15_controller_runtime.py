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

    def test_isolation_diagnostics_are_reduced_and_do_not_release_wip(self):
        snapshot={"main":{"commit":{"sha":H}},"policy_blob":P,"candidates":[
            {"pr":{"number":195},"collection_error":"PermissionError"},
            {"pr":{"number":196},"collection_error":"secret raw detail"},
            {"pr":{"number":198},"collection_error":"TypeError"},
        ]}
        report=self.report()
        report.update(unknown=[195,196],queue_complete=False,code_wip=3)
        with patch("tools.smartsvg_controller_runtime.observe",return_value=snapshot), patch(
                "tools.smartsvg_controller_runtime.simulate",return_value=report):
            result=route(object(),"fixture",run_id=10,attempt=1,controller_head=H)
        self.assertEqual(result["candidate_failures"],[
            {"number":195,"reason":"READ_UNAVAILABLE"},
            {"number":196,"reason":"UNCLASSIFIED"}])
        self.assertNotIn("secret raw detail",str(result))
        self.assertEqual(result["development_advice"]["available_slots"],0)
        self.assertEqual(result["assignments"]["A"]["number"],197)
        self.assertFalse(result["merge_authorized"])

    def test_no_probe_dependency_even_when_queue_is_empty(self):
        snapshot={"main":{"commit":{"sha":H}},"policy_blob":P,"candidates":[]}
        report=self.report()
        report["assignments"]["A"]=None
        report["code_wip"]=0
        with patch("tools.smartsvg_controller_runtime.observe",return_value=snapshot), patch(
                "tools.smartsvg_controller_runtime.simulate",return_value=report) as simulate:
            r=route(object(),"fixture",run_id=10,attempt=1,controller_head=C)
            self.assertEqual(r["assignments"],{"A":None,"B":None})
            self.assertEqual(r["candidate_failures"],[])
            self.assertNotIn("ci_manifest",simulate.call_args.kwargs)
            self.assertEqual(simulate.call_args.args[1]["scopes"],[])

    def test_recovery_hint_survives_public_envelope_without_authority(self):
        for advice in ("CHANGE_STRATEGY", "PROPOSE_HANDOFF_REVIEW",
                       "OTHER_ACTIONABLE_WORK", "ISOLATE_EXTERNAL_BLOCKER"):
            report=self.report()
            report["assignments"]["A"]["recovery_advice"]=advice
            result=envelope(report,10,1,C)
            self.assertEqual(result["recovery_hints"], {"A":{
                "number":197,"head":H,"action":"REVIEW","advice":advice,
                "qualification":"LOCAL_ADVISORY_ONLY"}})
            self.assertNotIn("recovery_advice",result["assignments"]["A"])
            self.assertFalse(result["merge_authorized"])
            self.assertFalse(result["agent_work_executed"])

    def test_recovery_hint_omits_unknown_or_normal_values(self):
        for value in (None, "RESUME_CHECKPOINT", "raw error or secret", [], 42):
            report=self.report()
            report["assignments"]["A"]["recovery_advice"]=value
            result=envelope(report,10,1,C)
            self.assertEqual(result["recovery_hints"],{})
            self.assertNotIn("recovery_advice",result["assignments"]["A"])

    def test_nonlive_or_mutation_authority_refused(self):
        for key,value in (("merge_authorized",True),("agent_work_executed",True),
                          ("final_queue_readback","NOT_REQUESTED")):
            r=self.report()
            r[key]=value
            with self.assertRaises(ValueError):
                envelope(r,10,1,C)


    def test_operational_route_rejects_old_controller_checkout(self):
        from tools.smartsvg_controller_observation import ObservationError
        snapshot={"main":{"commit":{"sha":H}},"policy_blob":P,"candidates":[]}
        with patch("tools.smartsvg_controller_runtime.observe",return_value=snapshot), patch(
                "tools.smartsvg_controller_runtime.simulate") as simulate:
            with self.assertRaises(ObservationError):
                route(object(),"fixture",run_id=10,attempt=1,controller_head=C,require_main=True)
            simulate.assert_not_called()

    def test_operational_route_binds_controller_to_fresh_main(self):
        snapshot={"main":{"commit":{"sha":H}},"policy_blob":P,"candidates":[]}
        report=self.report()
        with patch("tools.smartsvg_controller_runtime.observe",return_value=snapshot), patch(
                "tools.smartsvg_controller_runtime.simulate",return_value=report):
            result=route(object(),"fixture",run_id=10,attempt=1,controller_head=H,require_main=True)
            self.assertEqual(result["main"],result["controller_head"])
            self.assertFalse(result["merge_authorized"])

    def test_new_work_capacity_never_double_allocates_last_slot(self):
        report=self.report()
        report["assignments"]={"A":None,"B":None}
        report["code_wip"]=2
        result=envelope(report,10,1,C)
        advice=result["development_advice"]
        self.assertEqual(advice["available_slots"],1)
        self.assertEqual(advice["roles"],["A"])
        self.assertEqual(advice["qualification"],"ADVISORY_ONLY")
        self.assertEqual(result["assignments"],{"A":None,"B":None})
        self.assertFalse(result["merge_authorized"])

    def test_capacity_can_suggest_b_when_a_has_review(self):
        report=self.report()
        report["code_wip"]=2
        self.assertEqual(envelope(report,10,1,C)["development_advice"]["roles"],["B"])

    def test_capacity_both_idle_with_two_slots(self):
        report=self.report()
        report["assignments"]={"A":None,"B":None}
        self.assertEqual(envelope(report,10,1,C)["development_advice"]["roles"],["A","B"])

    def test_capacity_not_granted_for_unknown_or_full_queue(self):
        for complete,unknown,wip,reason in ((False,[],0,"QUEUE_INCOMPLETE"),
                (True,[197],0,"QUEUE_INCOMPLETE"),(True,[],3,"WIP_FULL")):
            report=self.report()
            report.update(queue_complete=complete,unknown=unknown,code_wip=wip)
            result=envelope(report,10,1,C)["development_advice"]
            self.assertEqual(result["roles"],[])
            self.assertEqual(result["reason"],reason)

    def test_truncated_optional_roadmap_preserves_assignments(self):
        from http.client import IncompleteRead
        from tools.smartsvg_controller_roadmap import PATH

        report = self.report()
        snapshot = {"main": {"commit": {"sha": report["main"]}},
                    "policy_blob": report["policy_blob"], "candidates": []}

        def short_read(path):
            self.assertEqual(path, f"/contents/{PATH}?ref={report['main']}")
            raise IncompleteRead(b"partial body")

        with patch("tools.smartsvg_controller_runtime.observe", return_value=snapshot), patch(
                "tools.smartsvg_controller_runtime.simulate", return_value=report):
            result = route(short_read, "unused", run_id=1, attempt=1,
                           controller_head=report["main"], require_main=True)
        self.assertEqual(result["assignments"]["A"]["number"], 197)
        self.assertEqual(result["roadmap_advice"]["status"], "UNAVAILABLE")
        self.assertFalse(result["merge_authorized"])
        self.assertNotIn("partial body", str(result))

    def test_existing_assignments_retained(self):
        report=self.report()
        report["assignments"]["B"]={"number":198,"head":H,"action":"REVIEW","plan_digest":"e"*64}
        result=envelope(report,10,1,C)
        self.assertEqual(result["development_advice"]["roles"],[])
        self.assertEqual(result["assignments"]["B"]["number"],198)

    def test_queue_churn_restarts_once_with_new_snapshot(self):
        from tools.smartsvg_controller_observation import QueueChanged
        snapshot={"main":{"commit":{"sha":H}},"policy_blob":P,"candidates":[]}
        report=self.report()
        with patch("tools.smartsvg_controller_runtime.observe",
                   side_effect=[QueueChanged("queue drift"),snapshot]) as observe, patch(
                "tools.smartsvg_controller_runtime.simulate",return_value=report) as simulate:
            result=route(object(),"fixture",run_id=10,attempt=1,controller_head=H,require_main=True)
            self.assertTrue(result["observation_restarted"])
            self.assertEqual(observe.call_count,2)
            self.assertIs(simulate.call_args.args[0],snapshot)
            self.assertFalse(result["merge_authorized"])

    def test_queue_churn_restart_bounded_and_other_errors_not_retried(self):
        from tools.smartsvg_controller_observation import QueueChanged, ObservationError
        for error,count in ((QueueChanged("queue drift"),2),(ObservationError("main drift"),1)):
            with patch("tools.smartsvg_controller_runtime.observe",side_effect=error) as observe, patch(
                    "tools.smartsvg_controller_runtime.simulate") as simulate:
                with self.assertRaises(type(error)):
                    route(object(),"fixture",run_id=10,attempt=1,controller_head=H)
                self.assertEqual(observe.call_count,count)
                simulate.assert_not_called()


    def test_failed_route_emits_recovery_diagnostic_but_still_fails(self):
        import os
        import io
        from contextlib import redirect_stdout
        from tools.smartsvg_controller_runtime import main
        from tools.smartsvg_controller_observation import ObservationError
        env={"R15_REQUIRE_MAIN":"1","GITHUB_RUN_ID":"10","GITHUB_RUN_ATTEMPT":"1",
             "EXPECTED_HEAD":H}
        out=io.StringIO()
        with patch.dict(os.environ,env), patch(
                "tools.smartsvg_controller_runtime.route",side_effect=ObservationError("drift")), patch(
                "tools.smartsvg_controller_pilot.recovery_only_packet",return_value={
                    "qualification":"FAILED_ROUTE_DIAGNOSTIC_ONLY","merge_authorized":False,
                    "retry_authorized":False}) as recovery, redirect_stdout(out):
            self.assertEqual(main(),2)
            recovery.assert_called_once()
        self.assertIn("R15B_RECOVERY_DIAGNOSTIC_V1 ",out.getvalue())
        self.assertNotIn("R15_ROUTE_V1 ",out.getvalue())
        self.assertNotIn("R15B_PILOT_V1 ",out.getvalue())
