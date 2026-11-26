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
from .smartsvg_controller_observation import observe, github_get, ObservationError
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
    return dict(checkpoint,controller_head=controller_head,observed_at=report["observed_at"],
                queue_complete=report["queue_complete"],code_wip=report["code_wip"],
                unknown=list(report["unknown"]),qualification="ADVISORY_ONLY",
                merge_authorized=False,agent_work_executed=False)


def route(get,journal_path,*,run_id,attempt,controller_head,require_main=False):
    snapshot=observe(get)
    if require_main and snapshot["main"]["commit"]["sha"]!=controller_head:
        raise ObservationError("controller checkout is no longer main")
    scopes,_=manifests(snapshot)
    # No fixed test probe. A closed or changed #194 must not stop routing.
    report=simulate(snapshot,scopes,scope_get=get,journal_path=journal_path)
    if require_main and report["main"]!=controller_head:
        raise ObservationError("routing main drift")
    return envelope(report,run_id,attempt,controller_head)


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
        return 0
    except Exception as exc:
        print(json.dumps({"mode":"R15_ROUTING","error":type(exc).__name__,
                          "merge_authorized":False}))
        return 2


if __name__=="__main__":
    raise SystemExit(main())
