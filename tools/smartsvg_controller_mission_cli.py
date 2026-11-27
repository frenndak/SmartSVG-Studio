"""Read-only SmartSVG R15.2 mission advice for an existing local checkpoint."""
import argparse
import json
import os
from sqlite3 import Error as SQLiteError

from .smartsvg_controller_missions import MAX_SNAPSHOT_BYTES, MissionError, MissionJournal
from .smartsvg_controller_objectives import Profile, ROLES, SHA, _matches
from .smartsvg_controller_mission_transport import reconcile_mission_snapshots
from .smartsvg_controller_observation import github_get
from .smartsvg_controller_smartsvg_objectives import (
    BACKLOG_PATH, POLICY_PIN, REPOSITORY, SOURCE_PINS,
    observe_smartsvg_mission_resumption,
)

MAX_REVISION_BYTES = 32 * 1024


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--main", required=True, help="expected exact SmartSVG main SHA")
    parser.add_argument("--role", required=True, choices=ROLES)
    state = parser.add_mutually_exclusive_group(required=True)
    state.add_argument("--journal", help="existing local mission SQLite file")
    state.add_argument("--snapshot", help="private mission snapshot; restored to memory only")
    parser.add_argument("--peer-snapshot", help="second private snapshot; conflicts quarantined in memory")
    parser.add_argument("--revisions", required=True,
                        help="caller-observed objective-to-revision JSON map")
    args = parser.parse_args(argv)

    report = {"version": 1, "qualification": "LOCAL_ADVISORY_ONLY",
              "merge_authorized": False, "agent_work_executed": False,
              "role": args.role, "selection": None}
    if not _matches(SHA, args.main):
        report["status"] = "CONTEXT_INPUT_INVALID"
        print(json.dumps(report, sort_keys=True))
        return 2
    report["main"] = args.main
    if args.peer_snapshot and not args.snapshot:
        report["status"] = "SNAPSHOT_PAIR_REQUIRED"
        print(json.dumps(report, sort_keys=True))
        return 2

    try:
        with open(args.revisions, "rb") as source:
            raw = source.read(MAX_REVISION_BYTES + 1)
        if len(raw) > MAX_REVISION_BYTES:
            raise ValueError("revision inventory too large")
        revisions = json.loads(raw)
    except (OSError, RecursionError, ValueError):
        report["status"] = "REVISION_INPUT_INVALID"
        print(json.dumps(report, sort_keys=True))
        return 2

    try:
        journal = MissionJournal(":memory:") if args.snapshot else MissionJournal(
            args.journal, read_only=True)
    except (OSError, RuntimeError, SQLiteError, ValueError):
        report["status"] = "LOCAL_JOURNAL_UNAVAILABLE"
        print(json.dumps(report, sort_keys=True))
        return 2
    try:
        token = os.environ.get("SMARTSVG_GITHUB_READ_TOKEN")
        profile = Profile("smartsvg", REPOSITORY, "main", POLICY_PIN,
                          dict(SOURCE_PINS)[BACKLOG_PATH])
        quarantined = ()
        if args.snapshot:
            try:
                with open(args.snapshot, "rb") as source:
                    payload = source.read(MAX_SNAPSHOT_BYTES + 1)
                if args.peer_snapshot:
                    with open(args.peer_snapshot, "rb") as source:
                        peer = source.read(MAX_SNAPSHOT_BYTES + 1)
                    payload, quarantined = reconcile_mission_snapshots(profile, payload, peer)
                journal.import_snapshot(profile, payload)
            except (OSError, SQLiteError, MissionError):
                report["status"] = "MISSION_SNAPSHOT_UNAVAILABLE"
                print(json.dumps(report, sort_keys=True))
                return 2
        observed = observe_smartsvg_mission_resumption(
            lambda path: github_get(path, token=token), journal, profile,
            args.main, revisions, role=args.role, quarantined=quarantined)
    finally:
        journal.close()

    report["status"] = observed.status
    if args.peer_snapshot:
        report["quarantined_missions"] = list(quarantined)
    if observed.mission_plan is not None:
        selected = observed.mission_plan.selected
        if selected is not None:
            report["selection"] = {
                "objective": selected.objective.objective,
                "action": selected.objective.action,
                "checkpoint_status": selected.checkpoint_status,
            }
    print(json.dumps(report, sort_keys=True))
    return 0 if observed.mission_plan is not None else 2


if __name__ == "__main__":
    raise SystemExit(main())
