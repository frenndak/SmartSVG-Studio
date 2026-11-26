"""Shadow correlation of author and reviewer cycles from scheduler readback.

Inputs are imported scheduler metadata and live GitHub reads, not signed
attestations. Never fabricate author cycles from latest narrative output or
commit timestamps. Only explicit matching receipts can yield routing hints.
"""
import json
from hashlib import sha256
from .smartsvg_controller_review import (
    TASKS, PREFIX, MAX_BODY, ReviewContext, correlate_review, _canonical, _time)
from .smartsvg_controller_scheduler import inspect_scheduler, MAX_RESULT_AGE
from .smartsvg_controller_observation import ObservationError, branch_observation

AUTHOR_PREFIX = "R15_AUTHOR_RECEIPT "


def _receipt(task, prefix, captured):
    if task.get("is_enabled") is not True:
        raise ValueError("disabled task")
    detail=task["run_details"]
    run,result=detail["last_run"],detail["latest_result"]
    if (run["recorded_status"]!="completed" or not isinstance(run["id"],str)
            or not run["id"] or result["run_id"]!=run["id"]
            or any(result.get(k) is not False for k in
                   ("content_truncated","requires_user_action","is_failure_message"))):
        raise ValueError("incomplete cycle")
    start,end=_time(run["started_at"]),_time(run["completed_at"])
    created=_time(result["created_at"])
    if not start<=created<=end<=captured or captured-end>MAX_RESULT_AGE:
        raise ValueError("invalid cycle dates")
    if _time(result["completed_at"])!=end:
        raise ValueError("result completion mismatch")
    body=result["content_text"]
    if not isinstance(body,str) or len(body)>MAX_BODY:
        raise ValueError("invalid result")
    lines=[x[len(prefix):] for x in body.splitlines() if x.startswith(prefix)]
    if len(lines)!=1:
        raise ValueError("missing or ambiguous structured receipt")
    value=json.loads(lines[0])
    if not isinstance(value,dict) or _canonical(value)!=lines[0]:
        raise ValueError("noncanonical receipt")
    return value,run,start,end


def _comment(get, entry, number, ident, digest, start, end):
    if type(ident) is not int or ident<1:
        raise ValueError("invalid comment ID")
    matches=[x for x in entry["comments"] if x.get("id")==ident]
    if len(matches)!=1:
        raise ValueError("missing or ambiguous snapshot comment")
    fresh=get("/issues/comments/"+str(ident))
    fields=("id","body","user","issue_url","created_at","updated_at")
    if any(fresh.get(k)!=matches[0].get(k) for k in fields):
        raise ValueError("comment changed")
    if (fresh["user"]["login"]!="frenndak" or fresh["id"]!=ident
            or fresh["issue_url"]!=
               f"https://api.github.com/repos/frenndak/SmartSVG-Studio/issues/{number}"
            or not isinstance(fresh["body"],str) or not fresh["body"].strip()
            or len(fresh["body"])>MAX_BODY
            or sha256(fresh["body"].encode()).hexdigest()!=digest
            or not start<=_time(fresh["created_at"])<=_time(fresh["updated_at"])<=end):
        raise ValueError("invalid comment provenance")
    return fresh


def derive_review_packets(plan,snapshot,scheduler_snapshot,get,*,now):
    """Return legacy routing packets only when both latest cycles correlate.

    Older author cycles are deliberately not reconstructed. A later unrelated
    writer run means the previous author receipt needs a separately preserved
    scheduler observation. No production qualification or mutation.
    """
    inspect_scheduler(scheduler_snapshot,now=now)
    captured=_time(scheduler_snapshot["captured_at"])
    tasks={}
    for role,ident in TASKS.items():
        matches=[a for a in scheduler_snapshot["automations"]
                 if isinstance(a,dict) and a.get("id")==ident]
        if len(matches)==1:
            tasks[role]=matches[0]
    entries={r["pr"]["number"]:r for r in snapshot["candidates"]}
    packets,reports=[],[]
    for p in plan.proposals:
        if p.action!="REVIEW" or p.writer not in TASKS:
            continue
        report={"number":p.number,"head":p.head,"status":"UNKNOWN",
                "reason":"AUTHOR_RECEIPT_UNAVAILABLE","qualification":"IMPORTED_CORRELATION_ONLY"}
        reports.append(report)
        role="B" if p.writer=="A" else "A"
        try:
            author,ar,astart,aend=_receipt(tasks[p.writer],AUTHOR_PREFIX,captured)
            expected={"version":1,"number":p.number,"head":p.head,"main":plan.main,
                      "policy_blob":plan.policy_blob,"role":p.writer,"run_id":ar["id"],
                      "comment_id":author.get("comment_id"),
                      "comment_sha256":author.get("comment_sha256")}
            if author!=expected or type(author.get("version")) is not int or type(author.get("number")) is not int:
                report["reason"]="AUTHOR_CONTEXT_MISMATCH"
                continue
            report["reason"]="AUTHOR_PROVENANCE_UNAVAILABLE"
            commit=get("/git/commits/"+p.head)
            if commit["sha"]!=p.head:
                raise ValueError("commit mismatch")
            committed=_time(commit["committer"]["date"])
            if not astart<=committed<=aend:
                raise ValueError("commit outside author cycle")
            _comment(get,entries[p.number],p.number,author["comment_id"],
                     author["comment_sha256"],astart,aend)
            report["reason"]="REVIEW_RECEIPT_UNAVAILABLE"
            reviewer,rr,rstart,rend=_receipt(tasks[role],PREFIX,captured)
            if rstart<=aend:
                report["reason"]="REVIEW_NOT_LATER_CYCLE"
                continue
            report["reason"]="REVIEW_PROVENANCE_UNAVAILABLE"
            comment=_comment(get,entries[p.number],p.number,reviewer["comment_id"],
                             reviewer["comment_sha256"],rstart,rend)
            ctx=ReviewContext(p.number,p.head,plan.main,plan.policy_blob,p.writer,
                              ar["id"],aend.isoformat(),committed.isoformat())
            verdict=correlate_review(ctx,role,tasks[role],comment)
            if not verdict.status.startswith("CORRELATED_"):
                report["reason"]=verdict.reason
                continue
            pr=get("/pulls/"+str(p.number))
            if (pr.get("number")!=p.number or pr.get("state")!="open"
                    or pr.get("head",{}).get("sha")!=p.head
                    or branch_observation(get,pr)["status"]!="MATCH"):
                report["reason"]="PR_CONTEXT_CHANGED"
                continue
            packets.append({"number":p.number,"head":p.head,"main":plan.main,
                "policy_blob":plan.policy_blob,"writer":p.writer,"role":role,
                "author_run":ar["id"],"author_completed_at":aend.isoformat(),
                "head_committed_at":committed.isoformat(),"comment_id":comment["id"],
                "scheduler":tasks[role]})
            report.update(status=verdict.status,reason="SEMANTIC_REVIEW_STILL_REQUIRED",
                          author_run=ar["id"],review_run=rr["id"],comment_id=comment["id"])
        except (KeyError,TypeError,ValueError,AttributeError,OverflowError,OSError,ObservationError):
            continue
    if get("/branches/main")["commit"]["sha"]!=plan.main:
        raise ObservationError("main changed during scheduler correlation")
    return tuple(packets),reports
