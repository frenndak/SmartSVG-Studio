"""R15 commissioning: real read-only GitHub rehearsal, no scheduler or merge.

The current workflow pin and probe case are explicitly selected for commissioning.
Branch prefixes are routing hints only, never writer authorization.
"""
import json
import os
from pathlib import Path
import re
import tempfile

from .smartsvg_controller_cli import simulate
from .smartsvg_controller_observation import github_get, observe, ObservationError
from .smartsvg_controller_log_transport import github_job_log
from .smartsvg_controller_storage import OperationalJournal

REPO="frenndak/SmartSVG-Studio"
PROBE_HEAD="fa292605d6edf7bc3bed454fac252694240b2a29"
PROBE_TESTS=[
    "test_v35_native_basic_cut_export.RealNativeBasicCutPublicationTests.test_real_project_preview_publish_reopen_and_retry",
    "test_v35_native_basic_cut_export.RealNativeBasicCutPublicationTests.test_real_project_negative_consent_digest_revision_and_collision",
]
PINS={".github/workflows/stability-qualification.yml":
      "41d17675dc6f41cd4138bac4250f8073490b62fe"}


def manifests(snapshot):
    context={"main":snapshot["main"]["commit"]["sha"],"policy_blob":snapshot["policy_blob"]}
    scopes=[]
    probes=[]
    for row in snapshot["candidates"]:
        p=row["pr"]
        head=p["head"]
        if ((head.get("repo") or {}).get("full_name")!=REPO
                or (p.get("base",{}).get("repo") or {}).get("full_name")!=REPO
                or p["base"].get("ref")!="main"
                or p.get("user",{}).get("login")!="frenndak"):
            continue
        ref=head.get("ref","")
        if not isinstance(ref,str):
            continue
        if ref.startswith("owner/"):
            writer,code="OWNER",False
        elif re.fullmatch(r"[ab]/[a-zA-Z0-9._/-]+",ref):
            writer,code=ref[0].upper(),True
        else:
            continue
        scopes.append({"number":p["number"],"head":head["sha"],"writer":writer,"code_only":code})
        if p["number"]==194 and head["sha"]==PROBE_HEAD and writer=="B":
            probes.append({"number":194,"head":PROBE_HEAD,
                           "checks":{"windows_python":list(PROBE_TESTS)}})
    return dict(context,scopes=scopes),dict(context,pins=dict(PINS),candidates=probes)


def commission(get,log_get,journal_path):
    snapshot=observe(get)
    scopes,ci=manifests(snapshot)
    report=simulate(snapshot,scopes,scope_get=get,ci_manifest=ci,
                    ci_log_get=log_get,journal_path=journal_path)
    if (report["merge_authorized"] is not False or report["agent_work_executed"] is not False
            or report["persistent_writes"] is not True):
        raise ObservationError("unexpected rehearsal authority")
    # Reopen the DB rather than treating successful insertion as persistence proof.
    j=OperationalJournal(journal_path)
    try:
        evidence_count=0
        for p in report["candidates"]:
            for kind in ("STEP_ONLY","SCOPE_OBSERVATION","LOG_ONLY"):
                evidence_count+=len(j.evidence_for(p["number"],p["head"],report["main"],
                                                   report["policy_blob"],kind))
        active=j.db.execute("SELECT COUNT(*) FROM work WHERE expires>0").fetchone()[0]
    finally:
        j.close()
    if active:
        raise ObservationError("rehearsal lease retained")
    probe=next((r for r in report["ci_reports"] if r["number"]==194
                and r["head"]==PROBE_HEAD and r["check"]=="windows_python"),None)
    log_pass=bool(probe and probe.get("log_source")=="GITHUB_JOB_LOG"
                  and len(probe["tests"])==len(PROBE_TESTS)
                  and {t["test_id"] for t in probe["tests"]}==set(PROBE_TESTS)
                  and all(t["status"]=="PASS" for t in probe["tests"]))
    return {"mode":"LIVE_SHADOW_COMMISSIONING","main":report["main"],
            "policy_blob":report["policy_blob"],"queue_complete":report["queue_complete"],
            "unknown":report["unknown"],"code_wip":report["code_wip"],
            "assignments":report["assignments"],"scope_reports":report["scope_reports"],
            "ci_probe":probe,"probe_status":"PASS" if log_pass else "NOT_QUALIFIED",
            "reopened_evidence_count":evidence_count,"active_leases":active,
            "scheduler_verified":False,"merge_authorized":False,
            "agent_work_executed":False,"persistent_across_runners":False}


def main():
    token=os.environ.get("SMARTSVG_GITHUB_READ_TOKEN")
    try:
        with tempfile.TemporaryDirectory(prefix="r15-commission-") as tmp:
            report=commission(lambda path:github_get(path,token=token),
                lambda job:github_job_log(job,token=token),Path(tmp)/"rehearsal.sqlite")
        print(json.dumps(report,sort_keys=True,indent=2))
        # A green commissioning check means an actual targeted log was parsed
        # and evidence reopened, not merely that the CLI returned JSON.
        return 0 if report["probe_status"]=="PASS" and report["reopened_evidence_count"]>0 else 1
    except Exception as exc:
        print(json.dumps({"mode":"LIVE_SHADOW_COMMISSIONING","error":type(exc).__name__,
                          "merge_authorized":False}))
        return 2


if __name__=="__main__":
    raise SystemExit(main())
