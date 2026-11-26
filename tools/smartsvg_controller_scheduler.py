"""R15 scheduler readback adapter for the actual automation peek schema.

A connector-native caller can export the independently read task summaries
and capture time. Python has no scheduler API credential or connector access.
Imported metadata is advisory: never synthesize approval or authorship from
the latest result, task status, timestamps, prose, or task identifiers.
"""
from datetime import datetime, timedelta
from hashlib import sha256
import json
from .smartsvg_controller_review import TASKS, PREFIX, MAX_BODY, _time

MAX_CAPTURE_AGE = timedelta(minutes=5)
MAX_RESULT_AGE = timedelta(hours=3)


def inspect_scheduler(snapshot, *, now):
    """Return redacted latest-cycle diagnostics, without raw result or prompt."""
    if (not isinstance(snapshot,dict) or set(snapshot)!={"captured_at","automations"}
            or not isinstance(snapshot["automations"],list)
            or len(snapshot["automations"])>20
            or not isinstance(now,datetime) or now.utcoffset() is None):
        raise ValueError("invalid scheduler snapshot")
    captured=_time(snapshot["captured_at"])
    if not timedelta(0)<=now-captured<=MAX_CAPTURE_AGE:
        raise ValueError("scheduler capture stale or future")
    reports={}
    for role,task_id in TASKS.items():
        report={"status":"UNKNOWN","reason":"TASK_MISSING",
                "qualification":"IMPORTED_METADATA_ONLY",
                "review_qualified":False,"native_approval":False}
        reports[role]=report
        matches=[a for a in snapshot["automations"] if isinstance(a,dict) and a.get("id")==task_id]
        if len(matches)!=1:
            if matches:
                report["reason"]="TASK_AMBIGUOUS"
            continue
        a=matches[0]
        if a.get("is_enabled") is not True:
            report["reason"]="TASK_DISABLED_OR_UNKNOWN"
            continue
        try:
            detail=a["run_details"]
            run,result=detail["last_run"],detail["latest_result"]
            state=run["recorded_status"]
            if state not in ("in_progress","completed","failed","no_update"):
                raise ValueError("unknown run state")
            start=_time(run["started_at"])
            scheduled=_time(run["scheduled_for"])
            if (not isinstance(run["id"],str) or not 1<=len(run["id"])<=128
                    or start>captured):
                raise ValueError("invalid run identity")
            report["status"]=state.upper()
            report["run_id"]=run["id"]
            report["scheduled_for"]=scheduled.isoformat()
            if state!="completed":
                report["reason"]="LATEST_CYCLE_NOT_COMPLETED"
                continue
            end=_time(run["completed_at"])
            if not start<=end<=captured:
                raise ValueError("invalid cycle time")
            report["completed_at"]=end.isoformat()
            if captured-end>MAX_RESULT_AGE:
                report["reason"]="LATEST_CYCLE_STALE"
                continue
            if not isinstance(result,dict) or result.get("run_id")!=run["id"]:
                report["reason"]="LATEST_RESULT_MISMATCH"
                continue
            if (result.get("requires_user_action") is not False
                    or result.get("is_failure_message") is not False
                    or result.get("content_truncated") is not False):
                report["reason"]="RESULT_INCOMPLETE_OR_BLOCKED"
                continue
            created=_time(result["created_at"])
            if not start<=created<=end or _time(result["completed_at"])!=end:
                raise ValueError("result time mismatch")
            body=result["content_text"]
            if not isinstance(body,str) or not body.strip() or len(body)>MAX_BODY:
                raise ValueError("invalid result body")
            report["result_digest"]=sha256(body.encode()).hexdigest()
            receipts=[line[len(PREFIX):] for line in body.splitlines() if line.startswith(PREFIX)]
            handoffs=[line for line in body.splitlines() if line.startswith("R15_HANDOFF ")]
            authors=[line for line in body.splitlines() if line.startswith("R15_AUTHOR_RECEIPT ")]
            if len(receipts)+len(handoffs)+len(authors)>1:
                report["reason"]="AMBIGUOUS_STRUCTURED_RECEIPT"
            elif handoffs or authors:
                report["reason"]="RECEIPT_PRESENT_NOT_CORRELATED"
            elif not receipts:
                report["reason"]="NARRATIVE_ONLY"
            elif len(receipts)!=1:
                report["reason"]="AMBIGUOUS_STRUCTURED_RECEIPT"
            else:
                receipt=json.loads(receipts[0])
                if not isinstance(receipt,dict) or receipt.get("run_id")!=run["id"] or receipt.get("role")!=role:
                    report["reason"]="RECEIPT_IDENTITY_MISMATCH"
                else:
                    # Requires independent author-cycle + GitHub comment + semantic checks.
                    report["reason"]="RECEIPT_PRESENT_NOT_CORRELATED"
        except (KeyError,TypeError,ValueError,AttributeError,OverflowError):
            report["status"]="UNKNOWN"
            report["reason"]="MALFORMED_READBACK"
            report.pop("result_digest",None)
    return reports
