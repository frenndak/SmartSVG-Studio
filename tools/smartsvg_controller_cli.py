"""R15 read-only CLI: python -m tools.smartsvg_controller_cli --help."""
import argparse
from dataclasses import asdict, replace
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

from .smartsvg_controller_observation import ObservationError, github_get, observe
from .smartsvg_controller_orchestration import Scope, build_plan, reserve_next, _fresh
from .smartsvg_controller_storage import Evidence, OperationalJournal
from .smartsvg_controller_routing import route_review_hints
from .smartsvg_controller_scope import inspect_scope
from .smartsvg_controller_ci import inspect_ci
from .smartsvg_controller_log_transport import github_job_log

MAX_INPUT = 32 * 1024 * 1024


def read_json(path):
    with Path(path).open("rb") as f:
        raw = f.read(MAX_INPUT + 1)
    if len(raw) > MAX_INPUT:
        raise ValueError("input exceeds size bound")
    def unique(pairs):
        obj = {}
        for k, v in pairs:
            if k in obj:
                raise ValueError("duplicate JSON key")
            obj[k] = v
        return obj
    return json.loads(raw, object_pairs_hook=unique)


def scopes_from_manifest(manifest, snapshot):
    """Require an explicit operator routing manifest for the observed context."""
    if not isinstance(manifest, dict) or set(manifest) != {"main", "policy_blob", "scopes"}:
        raise ValueError("invalid scope manifest")
    if (manifest["main"] != snapshot["main"]["commit"]["sha"]
            or manifest["policy_blob"] != snapshot["policy_blob"]):
        raise ValueError("scope manifest context changed")
    if not isinstance(manifest["scopes"], list):
        raise ValueError("invalid scope list")
    return tuple(Scope(**row) for row in manifest["scopes"])


def inspect_plan_scopes(plan, get):
    """Refine operator hints using fresh, count-checked path inventories.

    A path inventory may narrow a candidate's scope but cannot authorize it,
    prove semantic completeness, or exempt a test from required runtime CI.
    A local read failure quarantines only that candidate. Main drift invalidates
    the whole observation. Never release a conservative WIP slot on failure.
    """
    reports = []
    proposals = []
    unknown = set(plan.unknown)
    wip = plan.code_wip
    for p in plan.proposals:
        try:
            scope = inspect_scope(get, p.number, head=p.head, main=plan.main)
        except Exception as exc:
            unknown.add(p.number)
            if p.action == "OWNER_REVIEW":
                wip += 1
            reports.append({"number": p.number, "head": p.head,
                            "qualification": "UNAVAILABLE",
                            "error": type(exc).__name__})
            continue
        reports.append({"number": p.number, "head": p.head,
                        "qualification": scope.qualification,
                        "inventory_digest": scope.inventory_digest,
                        "file_count": len(scope.files),
                        "excluded_count": len(scope.excluded_paths),
                        "engine_changed": scope.engine_changed,
                        "base_matches_main": scope.base_matches_main})
        if scope.excluded_paths:
            p = replace(p, action="OWNER_REVIEW", writer="OWNER",
                        reasons=("EXCLUDED_PATH_IN_INVENTORY",))
        # An older base is not a conflict or a reason to repeat CI blindly.
        # Keep the existing task and disclose the context mismatch.
        if not scope.base_matches_main:
            p = replace(p, reasons=(*p.reasons, "BASE_CONTEXT_REQUIRES_REVIEW"))
        proposals.append(p)
    if get("/branches/main")["commit"]["sha"] != plan.main:
        raise ObservationError("main changed during path inspection")
    return (replace(plan, proposals=tuple(proposals), unknown=tuple(sorted(unknown)),
                    code_wip=wip, queue_complete=plan.queue_complete and not unknown),
            reports)


def simulate(snapshot, manifest, *, now=None, review_packets=(), scope_get=None,
             ci_manifest=None, ci_logs=(), ci_log_get=None, journal_path=None):
    """Run a read-only advisory rehearsal; optional dedicated local SQLite.

    No GitHub writes or scheduler calls. Persistent mode stores only reduced
    evidence and advisory plan fingerprints, not completed agent work.
    No raw comments, logs, credentials, checkpoints or bodies in output.
    """
    explicit_now = now
    now = now or datetime.now(timezone.utc)
    scopes = scopes_from_manifest(manifest, snapshot)
    plan = build_plan(snapshot, scopes, now=now)
    scope_reports = []
    if scope_get is not None:
        plan, scope_reports = inspect_plan_scopes(plan, scope_get)
        now = explicit_now or datetime.now(timezone.utc)
        _fresh(plan.finished, now)
    plan = route_review_hints(plan, snapshot, review_packets)
    # Review hints may replace reasons. Preserve path-derived base context
    # as an explicit reminder, without making it a false conflict.
    old_bases = {r["number"] for r in scope_reports
                 if r.get("base_matches_main") is False}
    plan = replace(plan, proposals=tuple(
        replace(p, reasons=(*p.reasons, "BASE_CONTEXT_REQUIRES_REVIEW"))
        if p.number in old_bases and "BASE_CONTEXT_REQUIRES_REVIEW" not in p.reasons
        else p for p in plan.proposals))
    ci_reports = []
    if ci_manifest is not None:
        if scope_get is None:
            raise ValueError("CI manifest requires live metadata source")
        ci_reports = inspect_ci(plan, ci_manifest, scope_get, ci_logs, log_get=ci_log_get)
        now = explicit_now or datetime.now(timezone.utc)
        _fresh(plan.finished, now)
    elif ci_logs or ci_log_get is not None:
        raise ValueError("logs require CI manifest")
    persistent = journal_path is not None
    if persistent and (not str(journal_path) or str(journal_path) == ":memory:"):
        raise ValueError("dedicated persistent journal path required")
    journal = OperationalJournal(str(journal_path) if persistent else ":memory:")
    try:
        for report in ci_reports:
            report["receipt_digest"] = journal.store_evidence(Evidence(
                report["number"], report["head"], plan.main, plan.policy_blob,
                "LOG_ONLY", "ci-inspection", dict(report)))
        for report in scope_reports:
            if report["qualification"] == "PATHS_ONLY":
                report["receipt_digest"] = journal.store_evidence(Evidence(
                    report["number"], report["head"], plan.main, plan.policy_blob,
                    "SCOPE_OBSERVATION", "github-pr-files", dict(report)))
        candidates = []
        for p in plan.proposals:
            steps = []
            for step in p.steps:
                data = asdict(step)
                data["status"] = step.status.value
                source = "run:{}/attempt:{}/job:{}/step:{}".format(
                    step.run_id, step.attempt, step.job_id, step.step_number)
                # Missing or ambiguous step observations are not positive proof.
                digest = journal.store_evidence(Evidence(
                    p.number, p.head, plan.main, plan.policy_blob,
                    "STEP_ONLY", source, data))
                steps.append({"name": step.name, "status": step.status.value,
                              "reason": step.reason, "digest": digest})
            candidates.append({"number": p.number, "head": p.head, "writer": p.writer,
                               "action": p.action, "reasons": p.reasons, "steps": steps})
        assignments = {}
        held = []
        try:
            for role in ("A", "B"):
                reservation = reserve_next(plan, role, journal, now=now)
                assignments[role] = None
                if reservation is None:
                    continue
                held.append(reservation)
                assignment = {"number": reservation.number, "action": reservation.action,
                              "head": reservation.head,
                              "recovery_advice": reservation.recovery_advice}
                if persistent:
                    # A plan fingerprint only: not a review, completed task,
                    # execution receipt, or authority to skip verification.
                    material = [reservation.context_key,
                        next(c for c in candidates if c["number"] == reservation.number),
                        [r for r in scope_reports if r["number"] == reservation.number],
                        [r for r in ci_reports if r["number"] == reservation.number]]
                    digest = sha256(json.dumps(material,sort_keys=True,separators=(",",":"),
                        ensure_ascii=True,allow_nan=False).encode()).hexdigest()
                    checkpoint = "SHADOW_PLAN_V1:" + digest
                    assignment["same_plan_as_previous"] = reservation.checkpoint == checkpoint
                    assignment["plan_digest"] = digest
                    if not journal.save("pr:"+str(reservation.number), reservation.context_key,
                                        role,reservation.fence,checkpoint):
                        raise ObservationError("rehearsal lease expired")
                assignments[role] = assignment
        finally:
            # Retain both reservations until planning finishes, avoiding
            # duplicate allocation within a rehearsal. Never retain a lease
            # after normal completion because no agent action was dispatched.
            for reservation in held:
                journal.release("pr:"+str(reservation.number),reservation.context_key,
                                reservation.owner,reservation.fence)
        return {"mode": "SHADOW_PERSISTENT_REHEARSAL" if persistent else "SHADOW_DRY_RUN",
                "merge_authorized": False,
                "main": plan.main, "policy_blob": plan.policy_blob,
                "observed_at": plan.finished.isoformat(),
                "code_wip": plan.code_wip, "queue_complete": plan.queue_complete,
                "unknown": plan.unknown, "candidates": candidates,
                "assignments": assignments, "persistent_writes": persistent,
                "agent_work_executed": False,
                "scope_verification": ("OPERATOR_HINT_ONLY" if scope_get is None else
                    "PATHS_ONLY_PARTIAL" if plan.unknown else "PATHS_ONLY"),
                "scope_reports": scope_reports,
                "ci_reports": ci_reports,
                "ci_verification": "ADVISORY_ONLY" if ci_manifest is not None else "NOT_REQUESTED",
                "review_verification": "NOT_QUALIFIED"}
    finally:
        journal.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--snapshot", help="recent raw observation JSON")
    source.add_argument("--live", action="store_true", help="read GitHub REST only")
    parser.add_argument("--scopes", required=True, help="explicit routing manifest JSON")
    parser.add_argument("--review-evidence", help="optional external review packets; routing hints only")
    parser.add_argument("--ci-manifest", help="explicit workflow pins and targeted test inventory; live only")
    logs_source = parser.add_mutually_exclusive_group()
    logs_source.add_argument("--ci-logs", help="optional imported job log packets, not authenticated")
    logs_source.add_argument("--fetch-ci-logs", action="store_true", help="read actual GitHub job logs, live only")
    parser.add_argument("--journal", help="optional dedicated local SQLite rehearsal file")
    args = parser.parse_args(argv)
    try:
        if args.fetch_ci_logs and (not args.live or not args.ci_manifest):
            raise ValueError("live CI manifest required for log fetch")
        manifest = read_json(args.scopes)
        get = None
        log_get = None
        if args.live:
            # Optional existing read token; never print or persist it.
            token = os.environ.get("SMARTSVG_GITHUB_READ_TOKEN")
            get = lambda path: github_get(path, token=token)
            snapshot = observe(get)
            if args.fetch_ci_logs:
                log_get = lambda job_id: github_job_log(job_id, token=token)
        else:
            snapshot = read_json(args.snapshot)
        packets = read_json(args.review_evidence) if args.review_evidence else ()
        ci = read_json(args.ci_manifest) if args.ci_manifest else None
        logs = read_json(args.ci_logs) if args.ci_logs else ()
        report = simulate(snapshot, manifest, review_packets=packets, scope_get=get,
                          ci_manifest=ci, ci_logs=logs, ci_log_get=log_get,
                          journal_path=args.journal)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        # Avoid printing raw HTTP bodies, private paths or supplied secrets.
        print(json.dumps({"mode": "SHADOW_DRY_RUN", "merge_authorized": False,
                          "error": type(exc).__name__}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
