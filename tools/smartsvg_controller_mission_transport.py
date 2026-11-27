"""Synchronize advisory mission history through a caller-owned private store.

The caller binds read and replace to one existing private item. Replace must
apply an atomic version precondition and return True on acknowledgment or
False on a definite version conflict. There is no unconditional write.
"""
from contextlib import closing
from dataclasses import dataclass
from http.client import HTTPException
import json
from sqlite3 import Error as SQLiteError

from .smartsvg_controller_missions import MAX_SNAPSHOT_BYTES, MissionError, MissionJournal, _canonical


@dataclass(frozen=True)
class StoredSnapshot:
    version: int | str
    payload: bytes


def _valid_snapshot(observed):
    if type(observed) is not StoredSnapshot or type(observed.payload) is not bytes:
        return False
    version = observed.version
    return (len(observed.payload) <= MAX_SNAPSHOT_BYTES
            and ((type(version) is int and 0 <= version <= 2**63 - 1)
                 or (type(version) is str and 0 < len(version) <= 128)))


def sync_mission_snapshot(profile, outgoing, *, read, replace):
    """Merge compatible histories and verify a single conditional write.

    The result describes the observed persistence outcome only. An uncertain
    acknowledgment is reconciled by readback, never by a second write.
    """
    try:
        with closing(MissionJournal(":memory:")) as journal:
            journal.import_snapshot(profile, outgoing)
            try:
                current = read()
            except (OSError, HTTPException):
                return "STORE_UNAVAILABLE"
            if not _valid_snapshot(current):
                return "STORE_UNAVAILABLE"
            try:
                journal.import_snapshot(profile, current.payload)
            except MissionError:
                return "HISTORY_REJECTED"
            proposed = journal.export_snapshot(profile)
    except (MissionError, SQLiteError, ValueError):
        return "SNAPSHOT_INVALID"
    return _publish(current, proposed, read=read, replace=replace)


def _publish(current, proposed, *, read, replace):
    if proposed == current.payload:
        return "ALREADY_CURRENT"

    try:
        acknowledged = replace(current.version, proposed)
    except (OSError, HTTPException):
        acknowledged = None
    if acknowledged is False:
        return "VERSION_CONFLICT"

    try:
        observed = read()
    except (OSError, HTTPException):
        return "WRITE_UNCONFIRMED"
    if (_valid_snapshot(observed) and observed.version != current.version
            and observed.payload == proposed):
        return "WRITE_VERIFIED"
    return "WRITE_UNCONFIRMED"


@dataclass(frozen=True)
class IndependentSync:
    status: str
    conflicts: tuple = ()
    qualification: str = "LOCAL_ADVISORY_ONLY"


def sync_independent_missions(profile, outgoing, *, read, replace):
    """Persist compatible missions while retaining divergent remote histories.

    Both whole snapshots must first pass the existing strict validation.
    Only conflicting mission histories are excluded from the proposed write;
    the caller must retain its outgoing snapshot and quarantine the listed
    missions until independently reconciled. Nothing here grants ownership
    or makes either divergent history the truth. No write retry is performed.
    """
    try:
        with closing(MissionJournal(":memory:")) as local:
            local.import_snapshot(profile, outgoing)
            local_rows = dict(json.loads(local.export_snapshot(profile))["missions"])
    except (MissionError, SQLiteError, ValueError):
        return IndependentSync("SNAPSHOT_INVALID")

    try:
        current = read()
    except (OSError, HTTPException):
        return IndependentSync("STORE_UNAVAILABLE")
    if not _valid_snapshot(current):
        return IndependentSync("STORE_UNAVAILABLE")

    try:
        with closing(MissionJournal(":memory:")) as remote:
            try:
                remote.import_snapshot(profile, current.payload)
            except MissionError:
                return IndependentSync("HISTORY_REJECTED")
            remote_doc = json.loads(remote.export_snapshot(profile))
            remote_rows = dict(remote_doc["missions"])
            conflicts = []
            compatible = []
            for key, rows in sorted(local_rows.items()):
                stored = remote_rows.get(key, [])
                shared = min(len(stored), len(rows))
                if stored[:shared] != rows[:shared]:
                    conflicts.append(key)
                else:
                    compatible.append([key, rows])
            # Reuse the bounded append-only import, including inventory checks.
            # This deliberately never replaces a conflicting remote history.
            remote.import_snapshot(profile, _canonical({
                "version": 1, "profile": remote_doc["profile"],
                "missions": compatible,
            }))
            proposed = remote.export_snapshot(profile)
    except (MissionError, SQLiteError, ValueError):
        return IndependentSync("SNAPSHOT_INVALID")
    status = _publish(current, proposed, read=read, replace=replace)
    return IndependentSync(status, tuple(conflicts))
