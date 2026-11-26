"""Connect live recovery to the isolated, durable R15-B shadow journal.

Only observed states are persisted; never dispatch, retry or authorize a
merge. The transport is the pinned shadow branch, not a production lock.
A terminal positive readback additionally requires unchanged policy and
G0 workflow content between the original and observed main.
"""
import json
from hashlib import sha256
from .smartsvg_controller_cas import decode, transition, TERMINAL
from .smartsvg_controller_observation import POLICY, _sha
from .smartsvg_controller_evidence import SPECS
from .smartsvg_controller_recovery_plan import recover

MAPPING = {"MERGED_G0_PASS":"QUALIFIED_READBACK", "WAIT_G0":"WAIT_G0",
           "G0_FAILED":"G0_FAILED", "MAIN_DRIFT":"MAIN_DRIFT",
           "NEGATIVE_READBACK":"NEGATIVE_READBACK"}


def reconcile_and_record(journal, get):
    """CAS at most one observation from the current pinned shadow state.

    Failed or ambiguous journal writes are never retried in this call.
    A prepared intent is not dispatched here. A successor main remains
    MAIN_DRIFT even when ancestry and its own G0 are observed.
    """
    report={"status":"INSPECT_JOURNAL","journal_ref":None,"journal_state":None,
            "observation":None,"write":None,"merge_authorized":False,
            "retry_authorized":False,"independent_work_blocked":False}
    try:
        ref, raw=journal.read()
        record=decode(raw)
        report.update(journal_ref=ref,journal_state=record.state)
        if record.state in TERMINAL | {"IDLE","PREPARED"}:
            report["status"]="NO_OBSERVATION_WRITE"
            return report
        observed=recover(journal.read,get)
        report["observation"]=observed
        if (observed.get("journal_ref")!=ref
                or observed.get("generation")!=record.generation
                or observed.get("intent")!=record.intent
                or observed.get("journal_state")!=record.state):
            report["status"]="JOURNAL_CONTEXT_CHANGED"
            return report
        observation=observed.get("observation")
        if not observation or observed.get("action") in ("JOURNAL_DRIFT","INSPECT_JOURNAL_OR_READBACK"):
            report["status"]="READBACK_UNAVAILABLE"
            return report
        target=MAPPING.get(observation.get("state"))
        if target is None:
            report["status"]="READBACK_UNAVAILABLE"
            return report
        proof={"observation":observation,"successor":observed.get("successor")}
        if target=="QUALIFIED_READBACK":
            main=_sha(observation["main"])
            if main!=observation.get("merge_sha") or observation.get("g0",{}).get("status")!="PASS":
                report["status"]="G0_CONTEXT_UNPROVED"
                return report
            path=SPECS["g0"][0]
            original_workflow=_sha(get(f"/contents/{path}?ref={record.main}")["sha"])
            current_workflow=_sha(get(f"/contents/{path}?ref={main}")["sha"])
            current_policy=_sha(get(f"/contents/{POLICY}?ref={main}")["sha"])
            if original_workflow!=current_workflow or current_policy!=record.policy:
                report["status"]="POLICY_OR_G0_CHANGED"
                return report
            proof.update(policy=current_policy,g0_workflow=current_workflow)
        evidence=sha256(json.dumps(proof,sort_keys=True,separators=(",",":"),
                                   allow_nan=False).encode()).hexdigest()
        if journal.read()!=(ref,raw):
            report["status"]="JOURNAL_CONTEXT_CHANGED"
            return report
        # A second fresh recovery prevents persisting a known intervening
        # PR/main/CI change. This is still not a distributed GitHub lock.
        if recover(journal.read,get)!=observed:
            report["status"]="OBSERVATION_CHANGED"
            return report
        if record.state==target and record.evidence==evidence:
            report["status"]="ALREADY_RECORDED"
            return report
        proposed=transition(record,target,evidence)
        result=journal.write(ref,record,proposed)
        report["write"]={"state":result.state,"candidate":result.candidate,
                         "observed":result.observed}
        report["status"]="OBSERVATION_RECORDED" if result.state=="APPLIED" else "JOURNAL_"+result.state
        return report
    except Exception:
        report["status"]="INSPECT_JOURNAL_OR_READBACK"
        return report
