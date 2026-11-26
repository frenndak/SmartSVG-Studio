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


def predicted_tree(get, number, head, main):
    """Require exact preview parents, or a proven main ancestor of HEAD."""
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
    return None


def packet(get, route, *, journal=None):
    """One candidate, exact current context, no inferred authorization."""
    result={"version":1,"main":route["main"],"policy_blob":route["policy_blob"],
            "run_id":route["run_id"],"attempt":route["attempt"],
            "controller_head":route["controller_head"],"qualification":"ADVISORY_ONLY",
            "merge_authorized":False,"retry_authorized":False,"status":"UNAVAILABLE"}
    try:
        journal=journal or PilotJournalTransport(get)
        ref,raw=journal.read()
        record=decode(raw)
        result.update(journal_ref=ref,journal_generation=record.generation,
                      journal_state=record.state)
        if record.state not in TERMINAL | {"IDLE"}:
            result["status"]="RECOVERY_REQUIRED"
            return result
        a=route["assignments"]["B"]
        if a is None:
            result["status"]="NO_CANDIDATE"
            return result
        main=_sha(route["main"])
        head=_sha(a["head"])
        number=a["number"]
        if type(number) is not int or number<1:
            return result
        if get("/branches/main")["commit"]["sha"]!=main:
            return result
        if get(f"/contents/{POLICY}?ref={main}")["sha"]!=route["policy_blob"]:
            return result
        pr=get("/pulls/"+str(number))
        scope=inspect_scope(get,number,head=head,main=main)
        if scope.excluded_paths or not pr["head"]["ref"].startswith(("a/","b/","code/v35-")):
            result["status"]="OWNER_REVIEW"
            return result
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
            return result
        result.update(status="OBSERVED",number=number,head=head,
                      path_count=len(scope.files),inventory_digest=scope.inventory_digest,
                      engine_changed=scope.engine_changed,base_matches_main=scope.base_matches_main,
                      draft=pr.get("draft"),mergeable=pr.get("mergeable"),expected_tree=tree,
                      main_g0=dict(asdict(g0),status=g0.status.value),
                      checks=[dict(asdict(s),status=s.status.value) for s in checks])
    except Exception as exc:
        result.update(status="UNAVAILABLE",error=type(exc).__name__)
    result["observed_at"]=datetime.now(timezone.utc).isoformat()
    result["evidence_digest"]=sha256(json.dumps(result,sort_keys=True,separators=(",",":"),
                                               allow_nan=False).encode()).hexdigest()
    return result
