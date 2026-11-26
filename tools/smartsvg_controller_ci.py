"""R15 advisory CI evidence composition, not a trusted verifier.

Read workflow blob identities and current run/job metadata through a caller
supplied GET source. Explicit operator pins and imported logs are untrusted
until independently reviewed and authenticated. Never emit EXTERNALLY_VERIFIED
facts, infer exact checkout from head_sha, or promote a log to a merge gate.
"""
from .smartsvg_controller_evidence import SPECS, step_receipts
from .smartsvg_controller_decision import Status
from .smartsvg_controller_observation import ObservationError, branch_observation
from .smartsvg_controller_proof import SHA, TEST_ID, verify_workflow_pin, parse_test_receipts

from .smartsvg_controller_step_log import bind_step_log

MAX_TARGETS = 64


def inspect_ci(plan, manifest, get, logs=(), *, log_get=None):
    if (not isinstance(manifest, dict) or set(manifest) != {"main","policy_blob","pins","candidates"}
            or (manifest["main"],manifest["policy_blob"]) != (plan.main,plan.policy_blob)
            or not isinstance(manifest["pins"],dict)
            or any(k not in {v[0] for v in SPECS.values()} or not isinstance(v,str)
                   or SHA.fullmatch(v) is None for k,v in manifest["pins"].items())
            or not isinstance(manifest["candidates"],list) or len(manifest["candidates"])>100
            or not isinstance(logs,(list,tuple)) or len(logs)>100
            or (log_get is not None and logs)):
        raise ValueError("invalid CI manifest")
    proposals={p.number:p for p in plan.proposals}
    seen=set()
    reports=[]
    cache={}
    log_cache={}
    def blob(path,ref):
        key=(path,ref)
        if key not in cache:
            cache[key]=get("/contents/"+path+"?ref="+ref)["sha"]
        return cache[key]
    for row in manifest["candidates"]:
        if (not isinstance(row,dict) or set(row)!={"number","head","checks"}
                or type(row["number"]) is not int or row["number"] in seen
                or not isinstance(row["checks"],dict)
                or not row["checks"] or any(k not in SPECS for k in row["checks"])):
            raise ValueError("invalid CI candidate")
        number=row["number"]
        seen.add(number)
        p=proposals.get(number)
        if p is None or p.head != row["head"] or p.writer not in ("A","B"):
            continue
        if sum(len(v) if isinstance(v,list) else MAX_TARGETS+1 for v in row["checks"].values())>MAX_TARGETS:
            raise ValueError("too many targeted tests")
        for name,targets in sorted(row["checks"].items()):
            if (not isinstance(targets,list) or any(not isinstance(t,str) or
                    TEST_ID.fullmatch(t) is None or ".test_" not in t or len(t)>512 for t in targets)
                    or len(set(targets))!=len(targets)):
                raise ValueError("invalid targeted test list")
            path,_,_=SPECS[name]
            step=next((s for s in p.steps if s.name==name),None)
            report={"number":number,"head":p.head,"check":name,"qualification":"ADVISORY_ONLY",
                    "status":"UNKNOWN","reason":"MISSING_STEP","tests":[]}
            reports.append(report)
            if step is None:
                continue
            report["observed_step_status"]=step.status.value
            try:
                pin=verify_workflow_pin(manifest["pins"].get(path),
                                        blob(path,plan.main),blob(path,p.head))
                report["pin_status"]=pin.reason
                if not pin.matched:
                    report["reason"]="WORKFLOW_PIN_NOT_MATCHED"
                    continue
                if step.status is not Status.PASS:
                    report["reason"]="STEP_NOT_PASS"
                    continue
                run=get("/actions/runs/"+str(step.run_id))
                job=get("/actions/jobs/"+str(step.job_id))
                current=next(s for s in step_receipts(p.head,[{"run":run,"jobs":[job]}]) if s.name==name)
                if current!=step or current.status is not Status.PASS:
                    report["reason"]="RUN_JOB_OR_ATTEMPT_CHANGED"
                    continue
                report["status"]="STEP_MATCHED"
                report["reason"]="CHECKOUT_AND_LOG_ORIGIN_NOT_QUALIFIED"
                report["run_id"],report["attempt"],report["job_id"]=step.run_id,step.attempt,step.job_id
                if not targets:
                    continue
                if log_get is not None:
                    log_key=(step.run_id,step.attempt,step.job_id,p.head)
                    if log_key not in log_cache:
                        log_cache[log_key]=log_get(step.job_id)
                    log=log_cache[log_key]
                    # A rerun can begin while downloading. Revalidate current
                    # metadata after the bytes have arrived.
                    latest_run=get("/actions/runs/"+str(step.run_id))
                    latest_job=get("/actions/jobs/"+str(step.job_id))
                    latest=next(s for s in step_receipts(p.head,[{"run":latest_run,
                        "jobs":[latest_job]}]) if s.name==name)
                    if latest!=step:
                        report["status"]="UNKNOWN"
                        report["reason"]="ATTEMPT_CHANGED_DURING_LOG_READ"
                        continue
                    source="GITHUB_JOB_LOG"
                else:
                    packets=[x for x in logs if isinstance(x,dict) and x.get("job_id")==step.job_id
                             and x.get("run_id")==step.run_id and x.get("attempt")==step.attempt
                             and x.get("head")==p.head]
                    if len(packets)!=1:
                        report["reason"]="IMPORTED_LOG_MISSING_OR_AMBIGUOUS"
                        continue
                    log=packets[0]["log"]
                    source="IMPORTED_LOG"
                receipt=parse_test_receipts(log,targets,head=p.head,
                    run_id=step.run_id,attempt=step.attempt,job_id=step.job_id)
                report["tests"]=[{"test_id":t.test_id,"status":t.status,"lines":list(t.lines)}
                                 for t in receipt.tests]
                report["log_digest"]=receipt.digest
                report["log_source"]=source
                if log_get is not None:
                    report["step_binding"]=bind_step_log(log,receipt,latest_job,
                                                         step.step_number)
                report["reason"]=("GITHUB_LOG_ONLY_STEP_AND_CHECKOUT_NOT_QUALIFIED"
                                  if log_get is not None else "IMPORTED_LOG_ONLY_NOT_AUTHENTICATED")
            except Exception as exc:
                report["status"]="UNKNOWN"
                report["reason"]="CI_READ_OR_PARSE_UNAVAILABLE"
                report["error"]=type(exc).__name__
        # A later branch change invalidates all observations for this PR.
        try:
            pr=get("/pulls/"+str(number))
            stable=(pr.get("number")==number and pr.get("state")=="open"
                    and pr.get("head",{}).get("sha")==p.head
                    and branch_observation(get,pr)["status"]=="MATCH")
        except Exception:
            stable=False
        if not stable:
            for report in reports:
                if report["number"]==number:
                    report.update(status="UNKNOWN",reason="PR_CONTEXT_CHANGED",tests=[])
                    report.pop("log_digest",None)
                    report.pop("log_source",None)
                    report.pop("step_binding",None)
    if get("/branches/main")["commit"]["sha"]!=plan.main:
        raise ObservationError("main changed during CI inspection")
    return reports
