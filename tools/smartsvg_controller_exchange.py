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
from .smartsvg_controller_storage import Evidence

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


def _author_context(plan,p,author,run_id):
    expected={"version":1,"number":p.number,"head":p.head,"main":plan.main,
              "policy_blob":plan.policy_blob,"role":p.writer,"run_id":run_id,
              "comment_id":author.get("comment_id"),
              "comment_sha256":author.get("comment_sha256")}
    return (author==expected and type(author.get("version")) is int
            and type(author.get("number")) is int)


def _verify_author(plan,p,entry,get,author,run_id,start,end):
    if not _author_context(plan,p,author,run_id):
        raise ValueError("author context mismatch")
    commit=get("/git/commits/"+p.head)
    if commit["sha"]!=p.head:
        raise ValueError("commit mismatch")
    committed=_time(commit["committer"]["date"])
    if not start<=committed<=end:
        raise ValueError("commit outside author cycle")
    _comment(get,entry,p.number,author["comment_id"],author["comment_sha256"],start,end)
    return committed


def _archive_payload(author,run,start,end,committed):
    return {"receipt":author,"run_id":run["id"],"started_at":start.isoformat(),
            "completed_at":end.isoformat(),"committed_at":committed.isoformat(),
            "qualification":"IMPORTED_AUTHOR_CYCLE_ONLY"}


def _historical_author(journal,plan,p,entry,get,run_id,captured):
    rows=journal.evidence_for(p.number,p.head,plan.main,plan.policy_blob,"AUTHOR_CYCLE")
    matches=[e.payload for _,e in rows if e.payload.get("run_id")==run_id]
    if len(matches)!=1:
        raise ValueError("missing or conflicting author history")
    data=matches[0]
    if data.get("qualification")!="IMPORTED_AUTHOR_CYCLE_ONLY":
        raise ValueError("invalid historical source")
    start,end=_time(data["started_at"]),_time(data["completed_at"])
    if not start<=end<=captured:
        raise ValueError("invalid historical dates")
    committed=_verify_author(plan,p,entry,get,data["receipt"],run_id,start,end)
    if committed!=_time(data["committed_at"]):
        raise ValueError("historical commit mismatch")
    return data,end,committed


def derive_review_packets(plan,snapshot,scheduler_snapshot,get,*,now,journal=None):
    """Correlate current reviewer with explicit current or preserved author cycle.

    Historical receipts are imported advisory observations, not signed proof.
    The exact context and live author comment are checked again on every use.
    No narrative reconstruction, production qualification or mutation.
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
        if p.writer not in TASKS:
            continue
        report={"number":p.number,"head":p.head,"status":"UNKNOWN",
                "reason":"AUTHOR_RECEIPT_UNAVAILABLE","qualification":"IMPORTED_CORRELATION_ONLY"}
        reports.append(report)
        role="B" if p.writer=="A" else "A"
        live_author=None
        try:
            author,ar,astart,aend=_receipt(tasks[p.writer],AUTHOR_PREFIX,captured)
            if not _author_context(plan,p,author,ar["id"]):
                report["reason"]="AUTHOR_CONTEXT_MISMATCH"
                raise ValueError("author context mismatch")
            report["reason"]="AUTHOR_PROVENANCE_UNAVAILABLE"
            committed=_verify_author(plan,p,entries[p.number],get,author,ar["id"],astart,aend)
            live_author=_archive_payload(author,ar,astart,aend,committed)
            report["author_source"]="LATEST_CYCLE"
            if journal is not None:
                report["author_archive_digest"]=journal.store_evidence(Evidence(
                    p.number,p.head,plan.main,plan.policy_blob,"AUTHOR_CYCLE",
                    "scheduler-import:"+p.writer,live_author))
            report["reason"]="REVIEW_RECEIPT_UNAVAILABLE"
        except (KeyError,TypeError,ValueError,AttributeError,OverflowError,OSError,ObservationError):
            live_author=None
        if p.action!="REVIEW":
            continue
        try:
            reviewer,rr,rstart,rend=_receipt(tasks[role],PREFIX,captured)
            author_run=reviewer.get("author_run")
            if not isinstance(author_run,str) or not author_run:
                raise ValueError("missing author run")
            # A current failed author readback must not be bypassed by history.
            writer=tasks[p.writer]
            if writer.get("is_enabled") is not True:
                raise ValueError("writer disabled")
            latest_id=writer["run_details"]["last_run"]["id"]
            if live_author is not None and live_author["run_id"]==author_run:
                if journal is not None:
                    # Detect conflicting copies of the same cycle even when current.
                    _,aend,committed=_historical_author(journal,plan,p,
                        entries[p.number],get,author_run,captured)
                else:
                    aend=_time(live_author["completed_at"])
                    committed=_time(live_author["committed_at"])
            elif journal is not None and latest_id!=author_run:
                report["reason"]="AUTHOR_HISTORY_UNAVAILABLE"
                data,aend,committed=_historical_author(journal,plan,p,
                    entries[p.number],get,author_run,captured)
                report["author_source"]="PRESERVED_CYCLE"
            else:
                continue
            if rstart<=aend:
                report["reason"]="REVIEW_NOT_LATER_CYCLE"
                continue
            report["reason"]="REVIEW_PROVENANCE_UNAVAILABLE"
            comment=_comment(get,entries[p.number],p.number,reviewer["comment_id"],
                             reviewer["comment_sha256"],rstart,rend)
            ctx=ReviewContext(p.number,p.head,plan.main,plan.policy_blob,p.writer,
                              author_run,aend.isoformat(),committed.isoformat())
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
                "author_run":author_run,"author_completed_at":aend.isoformat(),
                "head_committed_at":committed.isoformat(),"comment_id":comment["id"],
                "scheduler":tasks[role]})
            report.update(status=verdict.status,reason="SEMANTIC_REVIEW_STILL_REQUIRED",
                          author_run=author_run,review_run=rr["id"],comment_id=comment["id"])
        except (KeyError,TypeError,ValueError,AttributeError,OverflowError,OSError,ObservationError):
            continue
    if get("/branches/main")["commit"]["sha"]!=plan.main:
        raise ObservationError("main changed during scheduler correlation")
    return tuple(packets),reports
