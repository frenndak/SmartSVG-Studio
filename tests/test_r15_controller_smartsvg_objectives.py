import unittest
from dataclasses import replace
from hashlib import sha256
from tools.smartsvg_controller_objectives import Profile, Receipt, plan_objectives
from tools.smartsvg_controller_smartsvg_objectives import (
    REPOSITORY, POLICY_PATH, POLICY_PIN, BACKLOG_PATH, SOURCE_PINS, SLICES,
    observe_smartsvg_objectives,
)

M = "a"*40
P = Profile("smartsvg",REPOSITORY,"main",POLICY_PIN,dict(SOURCE_PINS)[BACKLOG_PATH])
REVISIONS = {row[0]: M for row in SLICES}


def source(path):
    if path == "/branches/main":
        return {"commit":{"sha":M}}
    for name,pin in ((POLICY_PATH,POLICY_PIN),*SOURCE_PINS):
        if path == f"/contents/{name}?ref={M}":
            return {"sha":pin}
    raise AssertionError(path)


def rows(result):
    return {o.key:o for o in result.objectives}


def pass_receipts(o):
    return tuple(Receipt(P,M,o.key,o.revision,c,"PASS",True,
                         sha256((o.key+":"+c).encode()).hexdigest()) for c in o.criteria)


class SmartSVGObjectiveAdapterTests(unittest.TestCase):
    def observe(self, revisions=REVISIONS, get=source, profile=P):
        return observe_smartsvg_objectives(get,profile,M,revisions)

    def test_exact_pins_and_partial_graph_not_authority(self):
        r=self.observe()
        self.assertEqual(r.status,"OBSERVED_PARTIAL_GRAPH")
        self.assertEqual(len(r.objectives),len(SLICES))
        self.assertEqual(r.missing_revisions,())
        self.assertIn("CAL-CUT",r.unmapped)
        self.assertIn("W15-release",r.unmapped)
        self.assertFalse(r.merge_authorized)
        self.assertFalse(r.agent_work_executed)
        plan=plan_objectives(P,M,r.objectives)
        self.assertFalse(any(a.action=="BLOCKED_GRAPH" for a in plan.objectives))
        self.assertFalse(any(a.action=="CRITERIA_OBSERVED" for a in plan.objectives))

    def test_sd0_a_independent_and_sd1_only_one_export_proof(self):
        o=rows(self.observe())
        self.assertEqual(o["W05-SD0-A"].dependencies,())
        self.assertIn("W03-ONE-TYPED-EXPORT",o["W06-SD1-A"].dependencies)
        self.assertNotIn("W03-BASIC-CUT-BACKEND",o["W06-SD1-A"].dependencies)
        self.assertNotIn("W03-PTC-BACKEND",o["W06-SD1-A"].dependencies)
        self.assertNotIn("W03-ONE-TYPED-EXPORT",o["W08-PTC-ASSISTANT"].dependencies)
        self.assertEqual(o["W08-PTC-ASSISTANT"].dependencies,("W03-PTC-BACKEND",))

    def test_one_export_is_explicit_receipt_not_automatically_inferred(self):
        o=rows(self.observe())
        proof=pass_receipts(o["W01-V1-CORE"])+pass_receipts(o["W03-BASIC-CUT-BACKEND"])
        plan=plan_objectives(P,M,tuple(o.values()),proof)
        actions={a.objective:a.action for a in plan.objectives}
        self.assertEqual(actions["W03-BASIC-CUT-BACKEND"],"CRITERIA_OBSERVED")
        self.assertEqual(actions["W03-ONE-TYPED-EXPORT"],"VERIFY_CRITERION")
        self.assertEqual(actions["W06-SD1-A"],"WAIT_DEPENDENCY")
        proof+=pass_receipts(o["W03-ONE-TYPED-EXPORT"])
        plan=plan_objectives(P,M,tuple(o.values()),proof)
        actions={a.objective:a.action for a in plan.objectives}
        self.assertEqual(actions["W03-ONE-TYPED-EXPORT"],"CRITERIA_OBSERVED")
        self.assertEqual(actions["W08-PTC-ASSISTANT"],"WAIT_DEPENDENCY")

    def test_missing_revision_blocks_only_affected_nodes(self):
        r=self.observe({k:v for k,v in REVISIONS.items() if k!="W01-V1-CORE"})
        self.assertEqual(r.missing_revisions,("W01-V1-CORE",))
        plan=plan_objectives(P,M,r.objectives)
        actions={a.objective:a.action for a in plan.objectives}
        self.assertEqual(actions["W02-MANUAL-SUBJECT"],"BLOCKED_GRAPH")
        self.assertEqual(actions["W05-SD0-A"],"VERIFY_CRITERION")
        self.assertEqual(actions["W13-ACCESSIBILITY"],"VERIFY_CRITERION")

    def test_source_or_policy_change_disables_only_optional_adapter(self):
        for name,_ in ((POLICY_PATH,POLICY_PIN),*SOURCE_PINS):
            def changed(path):
                if path==f"/contents/{name}?ref={M}":
                    return {"sha":"b"*40}
                return source(path)
            result=self.observe(get=changed)
            self.assertEqual(result.status,"SOURCE_REVIEW_REQUIRED")
            self.assertEqual(result.objectives,())
        self.assertEqual(self.observe(profile=replace(P,policy_blob="b"*40)).status,
                         "SOURCE_REVIEW_REQUIRED")

    def test_main_drift_or_optional_transport_failure_never_produces_graph(self):
        calls=0
        def drift(path):
            nonlocal calls
            if path=="/branches/main":
                calls+=1
                if calls==2:
                    return {"commit":{"sha":"b"*40}}
            return source(path)
        self.assertEqual(self.observe(get=drift).status,"CONTEXT_CHANGED")
        def failed(path):
            raise OSError("private response")
        r=self.observe(get=failed)
        self.assertEqual(r.status,"UNAVAILABLE")
        self.assertEqual(r.objectives,())
        self.assertNotIn("private response",str(r))

    def test_wrong_project_and_unrecognized_revision_refused(self):
        r=self.observe(profile=replace(P,project="synthetic"))
        self.assertEqual(r.status,"PROFILE_MISMATCH")
        self.assertEqual(self.observe({**REVISIONS,"invented":M}).status,
                         "REVISION_INPUT_INVALID")
        self.assertEqual(self.observe({"W01-V1-CORE":"not-sha"}).status,
                         "REVISION_INPUT_INVALID")
