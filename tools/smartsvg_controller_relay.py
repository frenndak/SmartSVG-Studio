"""Portable public-metadata checkpoint for R15 shadow commissioning only.

No SQLite file, raw logs, comments, scheduler results, credentials, or leases
cross runner boundaries. Cache/artifact input is untrusted and cannot select
work, seed authoritative evidence, grant permission, or skip live observation.
The current freshly calculated plan is always the source of assignments.
"""
import json
from pathlib import Path
import re
import os
import tempfile

SHA=re.compile(r"[0-9a-f]{40}")
DIGEST=re.compile(r"[0-9a-f]{64}")
ACTIONS=frozenset(("REVIEW","FIX_REQUIRED","RECONCILE","INSPECT","VERIFY_FINDING",
                   "CI_INSPECT","QUALIFY_ONLY","SHADOW_QUALIFIED"))
MAX_BYTES=8192


def validate(value):
    if (not isinstance(value,dict) or set(value)!={"version","run_id","attempt","main","policy_blob","assignments"}
            or type(value["version"]) is not int or value["version"]!=1
            or any(type(value[k]) is not int or value[k]<1 for k in ("run_id","attempt"))
            or any(not isinstance(value[k],str) or SHA.fullmatch(value[k]) is None
                   for k in ("main","policy_blob"))
            or not isinstance(value["assignments"],dict) or set(value["assignments"])!={"A","B"}):
        raise ValueError("invalid relay envelope")
    numbers=set()
    for row in value["assignments"].values():
        if row is None:
            continue
        if (not isinstance(row,dict) or set(row)!={"number","head","action","plan_digest"}
                or type(row["number"]) is not int or row["number"]<1
                or row["number"] in numbers or row["action"] not in ACTIONS
                or not isinstance(row["head"],str) or SHA.fullmatch(row["head"]) is None
                or not isinstance(row["plan_digest"],str) or DIGEST.fullmatch(row["plan_digest"]) is None):
            raise ValueError("invalid relay assignment")
        numbers.add(row["number"])
    return value


def make_checkpoint(report,run_id,attempt):
    if (report.get("mode")!="LIVE_SHADOW_COMMISSIONING" or report.get("merge_authorized") is not False
            or report.get("agent_work_executed") is not False or report.get("active_leases")!=0):
        raise ValueError("not a completed shadow rehearsal")
    rows={}
    for role in ("A","B"):
        row=report["assignments"][role]
        rows[role]=None if row is None else {k:row[k] for k in
                                             ("number","head","action","plan_digest")}
    return validate({"version":1,"run_id":run_id,"attempt":attempt,"main":report["main"],
                     "policy_blob":report["policy_blob"],"assignments":rows})


def _unique(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError("duplicate relay key")
        result[key]=value
    return result


def read_checkpoint(path):
    if path is None:
        return None
    try:
        with Path(path).open("rb") as f:
            raw=f.read(MAX_BYTES+1)
    except FileNotFoundError:
        return None
    if len(raw)>MAX_BYTES:
        raise ValueError("relay too large")
    return validate(json.loads(raw,object_pairs_hook=_unique))


def write_checkpoint(path,value):
    raw=json.dumps(validate(value),sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    path=Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=".relay-",dir=path.parent)
    try:
        with os.fdopen(fd,"wb") as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def compare_checkpoint(prior,current,*,require_current=False):
    validate(current)
    if prior is None:
        if require_current:
            raise ValueError("same-run relay missing")
        return {"status":"NO_PRIOR_CHECKPOINT","qualification":"ADVISORY_ONLY"}
    validate(prior)
    same_run=(prior["run_id"],prior["attempt"])==(current["run_id"],current["attempt"])
    if require_current and not same_run:
        raise ValueError("same-run relay identity mismatch")
    same_context=(prior["main"],prior["policy_blob"])==(current["main"],current["policy_blob"])
    roles={}
    for role in ("A","B"):
        before,after=prior["assignments"][role],current["assignments"][role]
        roles[role]=("CONTEXT_CHANGED" if not same_context else
                     "NO_ASSIGNMENT" if before is None and after is None else
                     "SAME_ADVISORY_PLAN" if before==after else "PLAN_CHANGED")
    return {"status":"SAME_RUNNER_RELAY" if same_run else "PRIOR_RUN_RELAY",
            "prior_run_id":prior["run_id"],"prior_attempt":prior["attempt"],
            "qualification":"ADVISORY_ONLY","same_context":same_context,"roles":roles}
