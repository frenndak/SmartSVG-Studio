"""R15 read-only CLI: python -m tools.smartsvg_controller_cli --help."""
import argparse
from dataclasses import asdict, replace
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

from .smartsvg_controller_observation import ObservationError, github_get, observe
from .smartsvg_controller_orchestration import Scope, build_plan, reserve_next, _fresh
from .smartsvg_controller_storage import Evidence, OperationalJournal
from .smartsvg_controller_routing import route_review_hints
from .smartsvg_controller_scope import inspect_scope

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


def simulate(snapshot, manifest, *, now=None, review_packets=(), scope_get=None):
    """Use actual orchestration and operational journal, but only in memory.

    No GitHub writes, no scheduler calls, no persistent local writes.
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
    journal = OperationalJournal(":memory:")
    try:
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
        for role in ("A", "B"):
            reservation = reserve_next(plan, role, journal, now=now)
            assignments[role] = ({"number": reservation.number,
                                  "action": reservation.action,
                                  "head": reservation.head,
                                  "recovery_advice": reservation.recovery_advice}
                                 if reservation else None)
        return {"mode": "SHADOW_DRY_RUN", "merge_authorized": False,
                "main": plan.main, "policy_blob": plan.policy_blob,
                "observed_at": plan.finished.isoformat(),
                "code_wip": plan.code_wip, "queue_complete": plan.queue_complete,
                "unknown": plan.unknown, "candidates": candidates,
                "assignments": assignments, "persistent_writes": False,
                "scope_verification": ("OPERATOR_HINT_ONLY" if scope_get is None else
                    "PATHS_ONLY_PARTIAL" if plan.unknown else "PATHS_ONLY"),
                "scope_reports": scope_reports,
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
    args = parser.parse_args(argv)
    try:
        manifest = read_json(args.scopes)
        get = None
        if args.live:
            # Optional existing read token; never print or persist it.
            token = os.environ.get("SMARTSVG_GITHUB_READ_TOKEN")
            get = lambda path: github_get(path, token=token)
            snapshot = observe(get)
        else:
            snapshot = read_json(args.snapshot)
        packets = read_json(args.review_evidence) if args.review_evidence else ()
        report = simulate(snapshot, manifest, review_packets=packets, scope_get=get)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        # Avoid printing raw HTTP bodies, private paths or supplied secrets.
        print(json.dumps({"mode": "SHADOW_DRY_RUN", "merge_authorized": False,
                          "error": type(exc).__name__}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
