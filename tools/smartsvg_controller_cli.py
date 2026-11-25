"""R15 read-only CLI: python -m tools.smartsvg_controller_cli --help."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

from .smartsvg_controller_observation import github_get, observe
from .smartsvg_controller_orchestration import Scope, build_plan, reserve_next
from .smartsvg_controller_storage import Evidence, OperationalJournal

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


def simulate(snapshot, manifest, *, now=None):
    """Use actual orchestration and operational journal, but only in memory.

    No GitHub writes, no scheduler calls, no persistent local writes.
    No raw comments, logs, credentials, checkpoints or bodies in output.
    """
    now = now or datetime.now(timezone.utc)
    scopes = scopes_from_manifest(manifest, snapshot)
    plan = build_plan(snapshot, scopes, now=now)
    journal = OperationalJournal(":memory:")
    try:
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
                "scope_verification": "OPERATOR_HINT_ONLY",
                "review_verification": "NOT_QUALIFIED"}
    finally:
        journal.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--snapshot", help="recent raw observation JSON")
    source.add_argument("--live", action="store_true", help="read GitHub REST only")
    parser.add_argument("--scopes", required=True, help="explicit routing manifest JSON")
    args = parser.parse_args(argv)
    try:
        manifest = read_json(args.scopes)
        if args.live:
            # Optional existing read token; never print or persist it.
            token = os.environ.get("SMARTSVG_GITHUB_READ_TOKEN")
            snapshot = observe(lambda path: github_get(path, token=token))
        else:
            snapshot = read_json(args.snapshot)
        report = simulate(snapshot, manifest)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        # Avoid printing raw HTTP bodies, private paths or supplied secrets.
        print(json.dumps({"mode": "SHADOW_DRY_RUN", "merge_authorized": False,
                          "error": type(exc).__name__}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
