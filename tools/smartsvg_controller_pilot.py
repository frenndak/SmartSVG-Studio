"""Reduced read-only candidate packet for the existing R13 executor.

No semantic verdict, scheduler authentication, mutation, or authorization.
A packet can be consumed without scanning every historical CI log again.
Only the existing B executor may act under the separately reviewed policy.
"""
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
import json

from .smartsvg_controller_cas import decode, TERMINAL
from .smartsvg_controller_git_journal import PilotJournalTransport
from .smartsvg_controller_observation import _sha, POLICY, branch_observation
from .smartsvg_controller_scope import inspect_scope
from .smartsvg_controller_cli import recheck_candidate_ci
from .smartsvg_controller_orchestration import Proposal
from .smartsvg_controller_live_reconcile import _g0
from .smartsvg_controller_tree import disjoint_tree
from .smartsvg_controller_recovery_plan import recover


def predicted_tree(get, number, head, main):
    """Exact preview, ancestor, or conservative verified disjoint tree."""
    try:
        compare=get("/compare/"+main+"..."+head)
        if (compare.get("status")=="ahead" and compare["base_commit"]["sha"]==main
                and compare["merge_base_commit"]["sha"]==main
                and compare.get("behind_by")==0 and type(compare.get("ahead_by")) is int
                and compare["ahead_by"]>0):
            commit=get("/git/commits/"+head)
            if commit.get("sha")==head:
                return _sha(commit["tree"]["sha"])
    except Exception:
        pass
    try:
        ref=get("/git/ref/pull/"+str(number)+"/merge")
        if (ref.get("ref")!="refs/pull/"+str(number)+"/merge"
                or ref["object"]["type"]!="commit"):
            return None
        sha=_sha(ref["object"]["sha"])
        commit=get("/git/commits/"+sha)
        if commit.get("sha")==sha and [x["sha"] for x in commit["parents"]]==[main,head]:
            return _sha(commit["tree"]["sha"])
    except Exception:
        pass
    return disjoint_tree(get,main,head)


def packet(get, route, *, journal=None):
    """One candidate, exact current context, no inferred authorization."""
    result={"version":1,"main":route["main"],"policy_blob":route["policy_blob"],
            "run_id":route["run_id"],"attempt":route["attempt"],
            "controller_head":route["controller_head"],"qualification":"ADVISORY_ONLY",
            "merge_authorized":False,"retry_authorized":False,"status":"UNAVAILABLE"}
    _observe(get, route, journal, result)
    result["observed_at"]=datetime.now(timezone.utc).isoformat()
    result["evidence_digest"]=sha256(json.dumps(result,sort_keys=True,separators=(",",":"),
                                               allow_nan=False).encode()).hexdigest()
    return result


def _observe(get, route, journal, result):
    try:
        journal=journal or PilotJournalTransport(get)
        ref,raw=journal.read()
        record=decode(raw)
        result.update(journal_ref=ref,journal_generation=record.generation,
                      journal_state=record.state)
        if record.state == "QUALIFIED_READBACK":
            result["status"]="PILOT_COMPLETE"
            return
        if record.state not in TERMINAL | {"IDLE"}:
            # The pending intent takes precedence over the next candidate.
            # Reuse the existing read-only recovery planner, never its writer.
            result["status"]="RECOVERY_REQUIRED"
            advice=recover(journal.read,get)
            if ((advice.get("journal_ref"),advice.get("generation"),
                 advice.get("intent"),advice.get("journal_state")) !=
                (ref,record.generation,record.intent,record.state)
                    or journal.read()!=(ref,raw)
                    or advice.get("action")=="JOURNAL_DRIFT"):
                result["status"]="CONTEXT_CHANGED"
                return
            result["recovery"]=advice
            return
        a=route["assignments"]["B"]
        if a is None:
            result["status"]="NO_CANDIDATE"
            return
        main=_sha(route["main"])
        head=_sha(a["head"])
        number=a["number"]
        if type(number) is not int or number<1:
            return
        if get("/branches/main")["commit"]["sha"]!=main:
            return
        if get(f"/contents/{POLICY}?ref={main}")["sha"]!=route["policy_blob"]:
            return
        pr=get("/pulls/"+str(number))
        scope=inspect_scope(get,number,head=head,main=main)
        if scope.excluded_paths or not pr["head"]["ref"].startswith(("a/","b/","code/v35-")):
            result["status"]="OWNER_REVIEW"
            return
        proposal=Proposal(number,head,"A",a["action"],(),())
        checks=recheck_candidate_ci(proposal,get)
        g0=_g0(get,main)
        tree=predicted_tree(get,number,head,main)
        def identity(x):
            return (x.get("number"),x.get("state"),x.get("draft"),
                    x.get("mergeable"),x.get("head",{}).get("sha"),
                    x.get("base",{}).get("sha"))
        latest=get("/pulls/"+str(number))
        if (identity(pr)!=identity(latest) or branch_observation(get,latest)["status"]!="MATCH"
                or recheck_candidate_ci(proposal,get)!=checks or _g0(get,main)!=g0
                or predicted_tree(get,number,head,main)!=tree
                or journal.read()!=(ref,raw) or get("/branches/main")["commit"]["sha"]!=main):
            result["status"]="CONTEXT_CHANGED"
            return
        result.update(status="OBSERVED",number=number,head=head,
                      path_count=len(scope.files),inventory_digest=scope.inventory_digest,
                      engine_changed=scope.engine_changed,base_matches_main=scope.base_matches_main,
                      draft=pr.get("draft"),mergeable=pr.get("mergeable"),expected_tree=tree,
                      main_g0=dict(asdict(g0),status=g0.status.value),
                      checks=[dict(asdict(s),status=s.status.value) for s in checks])
    except Exception as exc:
        result.update(status="UNAVAILABLE",error=type(exc).__name__)


def recovery_only_packet(get, *, run_id, attempt, controller_head, journal=None):
    """Independent diagnostic after route failure, never a qualified route.

    Read only the live main/policy and pinned journal/recovery subject. Do not
    select any new candidate or turn a failed routing job into a success.
    """
    main=_sha(controller_head)
    if get("/branches/main")["commit"]["sha"]!=main:
        return None
    policy=_sha(get(f"/contents/{POLICY}?ref={main}")["sha"])
    route={"main":main,"policy_blob":policy,"run_id":run_id,"attempt":attempt,
           "controller_head":main,"assignments":{"B":None}}
    result=packet(get,route,journal=journal)
    if (result["status"]!="RECOVERY_REQUIRED"
            or "recovery" not in result
            or get("/branches/main")["commit"]["sha"]!=main):
        return None
    result.pop("evidence_digest")
    result["qualification"]="FAILED_ROUTE_DIAGNOSTIC_ONLY"
    result["evidence_digest"]=sha256(json.dumps(result,sort_keys=True,
        separators=(",",":"),allow_nan=False).encode()).hexdigest()
    return result
