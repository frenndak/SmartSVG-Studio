"""Bind job log lines to the actual checkout and executed step time windows.

Only for independently retrieved GitHub job logs with matching reviewed workflow
pins. This is observational evidence, not a signature, semantic review, or
authorization. Missing timestamps remain unqualified instead of guessed.
"""
from datetime import datetime, timedelta
import re

from .smartsvg_controller_proof import MAX_LOG, SHA, LogReceipt

STAMP = re.compile(r"^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z) (.*)$")
CHECKOUT = re.compile(r"Run actions/checkout@v[0-9]+")
GIT_HEAD = re.compile(r'\[command\](?:"[^"\r\n]+[\\/]git(?:\.exe)?"|[^\r\n ]*[\\/]git(?:\.exe)?|git(?:\.exe)?) log -1 --format=%H')


def _utc(value):
    if not isinstance(value,str) or not value.endswith("Z"):
        raise ValueError("expected GitHub UTC timestamp")
    return datetime.fromisoformat(value[:-1]+"+00:00")


def _window(step):
    if step.get("status")!="completed" or step.get("conclusion")!="success":
        raise ValueError("step not successful")
    start,end=_utc(step["started_at"]),_utc(step["completed_at"])
    if end<=start:
        raise ValueError("invalid time window")
    return start,end


def _inside(time,window):
    # API bounds are commonly rounded to seconds; exclude the entire first
    # second and final boundary to avoid assigning adjacent step output.
    return time is not None and window[0]+timedelta(seconds=1)<=time<window[1]


def bind_step_log(log,receipt,job,step_number):
    def unknown(reason):
        return {"status":"UNKNOWN","reason":reason}
    try:
        if (not isinstance(log,str) or len(log.encode("utf-8"))>MAX_LOG
                or not isinstance(receipt,LogReceipt) or type(step_number) is not int
                or step_number<1 or not isinstance(job,dict)
                or job.get("id")!=receipt.job_id or job.get("run_id")!=receipt.run_id
                or job.get("run_attempt")!=receipt.attempt or job.get("head_sha")!=receipt.head):
            return unknown("LOG_JOB_IDENTITY_MISMATCH")
        from hashlib import sha256
        if sha256(log.encode("utf-8")).hexdigest()!=receipt.digest:
            return unknown("LOG_DIGEST_MISMATCH")
        steps=job["steps"]
        checkouts=[s for s in steps if CHECKOUT.fullmatch(s.get("name",""))]
        targets=[s for s in steps if s.get("number")==step_number]
        if len(checkouts)!=1 or len(targets)!=1:
            return unknown("AMBIGUOUS_STEP_IDENTITY")
        checkout,target=checkouts[0],targets[0]
        if type(checkout.get("number")) is not int or checkout["number"]>=step_number:
            return unknown("CHECKOUT_STEP_ORDER")
        cw,tw=_window(checkout),_window(target)
        if cw[1]>tw[0]:
            return unknown("OVERLAPPING_STEP_WINDOWS")
        parsed=[]
        for line in log.splitlines():
            m=STAMP.fullmatch(line)
            parsed.append((_utc(m.group(1)),m.group(2)) if m else (None,line))
        checkout_lines=[]
        for i,(time,line) in enumerate(parsed[:-1]):
            if _inside(time,cw) and GIT_HEAD.fullmatch(line):
                observed_time,observed=parsed[i+1]
                if _inside(observed_time,cw) and observed_time>=time and SHA.fullmatch(observed):
                    checkout_lines.append((i+2,observed))
        if len(checkout_lines)!=1 or checkout_lines[0][1]!=receipt.head:
            return unknown("CHECKOUT_SHA_NOT_OBSERVED")
        for test in receipt.tests:
            if (len(test.lines)!=1 or test.status=="UNKNOWN" or
                    type(test.lines[0]) is not int or not 1<=test.lines[0]<=len(parsed)
                    or not _inside(parsed[test.lines[0]-1][0],tw)):
                return unknown("TEST_RESULT_NOT_UNIQUELY_IN_STEP")
        return {"status":"BOUND","reason":"CHECKOUT_SHA_AND_TEST_STEP_OBSERVED",
                "checkout_line":checkout_lines[0][0],"step_number":step_number,
                "qualification":"OBSERVATIONAL_ONLY"}
    except (KeyError,TypeError,ValueError,AttributeError,OverflowError):
        return unknown("STEP_TIMESTAMPS_OR_LOG_UNAVAILABLE")
