"""R15 routing service: live advisory work allocation, independent of probe PRs.

No mutation, dispatch, permission, review verdict or merge authority. Existing
agent contracts remain effective. The transport is a reduced public JSON line.
"""
import json
import os
from pathlib import Path
import tempfile

from .smartsvg_controller_cli import simulate
from .smartsvg_controller_commission import manifests
from .smartsvg_controller_observation import observe, github_get, ObservationError, QueueChanged
from .smartsvg_controller_relay import validate

PREFIX="R15_ROUTE_V1 "


def envelope(report,run_id,attempt,controller_head):
    if (report.get("merge_authorized") is not False
            or report.get("agent_work_executed") is not False
            or report.get("final_queue_readback")!="ADVISORY"):
        raise ValueError("not live advisory routing")
    rows={}
    for role in ("A","B"):
        row=report["assignments"][role]
        rows[role]=None if row is None else {k:row[k] for k in
                                             ("number","head","action","plan_digest")}
    checkpoint=validate({"version":1,"run_id":run_id,"attempt":attempt,"main":report["main"],
                         "policy_blob":report["policy_blob"],"assignments":rows})
    from .smartsvg_controller_relay import SHA
    if not isinstance(controller_head,str) or SHA.fullmatch(controller_head) is None:
        raise ValueError("invalid controller identity")
    from .smartsvg_controller_capacity import development_advice
    checkpoint["development_advice"] = development_advice(report)
    if "roadmap_advice" in report:
        checkpoint["roadmap_advice"] = report["roadmap_advice"]
    # Keep the version-1 assignment shape intact. Recovery is a separate
    # bounded hint, not a new review, dispatch or integration authority.
    allowed = ("CHANGE_STRATEGY", "PROPOSE_HANDOFF_REVIEW",
               "OTHER_ACTIONABLE_WORK", "ISOLATE_EXTERNAL_BLOCKER")
    hints = {}
    for role in ("A", "B"):
        row = report["assignments"][role]
        if row is not None and row.get("recovery_advice") in allowed:
            hints[role] = {"number": rows[role]["number"], "head": rows[role]["head"],
                           "action": rows[role]["action"],
                           "advice": row["recovery_advice"],
                           "qualification": "LOCAL_ADVISORY_ONLY"}
    return dict(checkpoint,controller_head=controller_head,observed_at=report["observed_at"],
                queue_complete=report["queue_complete"],code_wip=report["code_wip"],
                unknown=list(report["unknown"]),qualification="ADVISORY_ONLY",
                merge_authorized=False,agent_work_executed=False,
                checkpoint_hints=report.get("checkpoint_reports", []),
                recovery_hints=hints)


def route(get,journal_path,*,run_id,attempt,controller_head,require_main=False):
    # One bounded restart of a read-only observation on known PR churn.
    # Never reuse partial evidence; main drift and other errors still fail.
    restarted=False
    try:
        snapshot=observe(get)
    except QueueChanged:
        restarted=True
        snapshot=observe(get)
    if require_main and snapshot["main"]["commit"]["sha"]!=controller_head:
        raise ObservationError("controller checkout is no longer main")
    scopes,_=manifests(snapshot)
    # No fixed test probe. A closed or changed #194 must not stop routing.
    from .smartsvg_controller_roadmap import roadmap_advice
    ranks, advice = roadmap_advice(snapshot,get)
    report=simulate(snapshot,scopes,scope_get=get,journal_path=journal_path,
                    durable_checkpoints=True,roadmap_ranks=ranks)
    report["roadmap_advice"] = advice
    if require_main and report["main"]!=controller_head:
        raise ObservationError("routing main drift")
    result=envelope(report,run_id,attempt,controller_head)
    result["observation_restarted"]=restarted
    return result


def main():
    try:
        token=os.environ.get("SMARTSVG_GITHUB_READ_TOKEN")
        with tempfile.TemporaryDirectory(prefix="r15-route-") as tmp:
            result=route(lambda path:github_get(path,token=token),Path(tmp)/"routing.sqlite",
                         run_id=int(os.environ["GITHUB_RUN_ID"]),
                         attempt=int(os.environ["GITHUB_RUN_ATTEMPT"]),
                         controller_head=os.environ["EXPECTED_HEAD"],
                         require_main=os.environ.get("R15_REQUIRE_MAIN")=="1")
        print(PREFIX+json.dumps(result,sort_keys=True,separators=(",",":"),allow_nan=False))
        if os.environ.get("R15_REQUIRE_MAIN")=="1":
            from .smartsvg_controller_pilot import packet
            try:
                advice=packet(lambda path:github_get(path,token=token),result)
                print("R15B_PILOT_V1 "+json.dumps(advice,sort_keys=True,separators=(",",":"),allow_nan=False))
            except Exception:
                # Optional advice must not invalidate a successful A route.
                print("R15B_PILOT_UNAVAILABLE")
        return 0
    except Exception as exc:
        print(json.dumps({"mode":"R15_ROUTING","error":type(exc).__name__,
                          "merge_authorized":False}))
        return 2


if __name__=="__main__":
    raise SystemExit(main())
