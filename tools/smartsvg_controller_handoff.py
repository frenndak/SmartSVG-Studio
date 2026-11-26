"""Durable PR-comment checkpoints for live advisory routing.

Public technical metadata only. Comments survive runner restarts, but the
shared GitHub identity does NOT authenticate an A/B scheduler cycle. A
checkpoint can change what is inspected next, never qualify a review, skip
a test, transfer ownership, authorize a merge or reserve a live worker.
"""
from dataclasses import replace
from datetime import datetime
from hashlib import sha256
from http.client import HTTPException
import json

from .smartsvg_controller_decision import Status
from .smartsvg_controller_observation import ObservationError, branch_observation

PREFIX = "R15_CHECKPOINT_V1 "
MAX_BODY = 32768
MAX_MARKER = 2048
FIELDS = {"version", "number", "head", "main", "policy_blob", "role", "verdict"}
VERDICTS = {"PARTIAL", "ADVERSE", "FAVORABLE"}


class CheckpointContextChanged(ObservationError):
    """Known PR/ref drift is not merely an unusable checkpoint."""


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate checkpoint field")
        result[key] = value
    return result


def _time(value):
    t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.utcoffset() is None:
        raise ValueError("timezone required")
    return t


def _marked(comment):
    body = comment.get("body")
    return isinstance(body, str) and any(
        line.startswith(PREFIX) for line in body.splitlines())


def _checkpoint(plan, p, entry, get):
    # Select the newest marker before validating it: a malformed/edited newer
    # marker must not silently resurrect an older favorable recommendation.
    rows = [c for c in entry["comments"] if _marked(c)
            and (c.get("user") or {}).get("login") == "frenndak"]
    if not rows:
        return None
    if any(type(c.get("id")) is not int or c["id"] < 1 for c in rows):
        return None
    if len({c["id"] for c in rows}) != len(rows):
        return None
    c = max(rows, key=lambda row: row["id"])
    body = c["body"]
    if len(body) > MAX_BODY:
        return None
    lines = [line[len(PREFIX):] for line in body.splitlines()
             if line.startswith(PREFIX)]
    if len(lines) != 1 or len(lines[0]) > MAX_MARKER:
        return None
    v = json.loads(lines[0], object_pairs_hook=_unique)
    if (not isinstance(v, dict) or set(v) != FIELDS
            or type(v["version"]) is not int or v["version"] != 1
            or type(v["number"]) is not int or v["number"] != p.number
            or (v["head"],v["main"],v["policy_blob"]) != (p.head,plan.main,plan.policy_blob)
            or v["role"] != ("B" if p.writer == "A" else "A")
            or v["verdict"] not in VERDICTS):
        return None
    # Immutable-by-convention checkpoint: editing it invalidates the hint.
    if _time(c["created_at"]) != _time(c["updated_at"]):
        return None
    commit = get("/git/commits/" + p.head)
    if (commit.get("sha") != p.head or
            not _time(commit["committer"]["date"]) <= _time(c["created_at"]) <= plan.finished):
        return None
    fresh = get("/issues/comments/" + str(c["id"]))
    keys = ("id","user","issue_url","body","created_at","updated_at")
    if (any(fresh.get(k) != c.get(k) for k in keys)
            or c.get("issue_url") !=
                f"https://api.github.com/repos/frenndak/SmartSVG-Studio/issues/{p.number}"):
        return None
    pr = get("/pulls/" + str(p.number))
    if (pr.get("number") != p.number or pr.get("state") != "open"
            or pr.get("head",{}).get("sha") != p.head
            or branch_observation(get, pr)["status"] != "MATCH"):
        raise CheckpointContextChanged("PR changed during checkpoint readback")
    return {"number":p.number,"head":p.head,"comment_id":c["id"],
            "role":v["role"],"verdict":v["verdict"],
            "comment_digest":sha256(body.encode()).hexdigest(),
            "qualification":"UNAUTHENTICATED_ADVISORY_ONLY"}


def route_checkpoints(plan, snapshot, get):
    """Apply exact-context hints after normal scope/CI/queue checks.

    Do not replace an existing repair/owner/CI/correlated-review action.
    A partial review resumes REVIEW; adverse means VERIFY_FINDING by writer,
    favorable means independent qualification (never SHADOW_QUALIFIED).
    Missing/unreadable hint leaves original routing unchanged.
    """
    entries = {e["pr"]["number"]:e for e in snapshot["candidates"]}
    proposals, reports, invalid = [], [], set()
    for p in plan.proposals:
        hint = None
        if p.action == "REVIEW" and p.writer in ("A","B"):
            try:
                hint = _checkpoint(plan,p,entries[p.number],get)
            except CheckpointContextChanged:
                invalid.add(p.number)
                continue
            except (KeyError, TypeError, ValueError, AttributeError, OSError,
                    OverflowError, HTTPException, ObservationError):
                pass
        if hint is not None:
            reports.append(hint)
            if hint["verdict"] == "ADVERSE":
                p = replace(p,action="VERIFY_FINDING",
                            reasons=(*p.reasons,"DURABLE_ADVERSE_HINT_UNVERIFIED"))
            elif hint["verdict"] == "FAVORABLE":
                missing = tuple(s.name+":"+s.status.value for s in p.steps
                                if s.status is not Status.PASS)
                # B must independently qualify every R13 gate. A remains
                # reviewer for B-owned work with incomplete CI evidence.
                p = replace(p,action="CI_INSPECT" if missing else "QUALIFY_ONLY",
                            reasons=(*p.reasons,"DURABLE_FAVORABLE_HINT_UNVERIFIED",*missing))
            else:
                p = replace(p,reasons=(*p.reasons,"RESUME_PARTIAL_REVIEW"))
        proposals.append(p)
    if (reports or invalid) and get("/branches/main")["commit"]["sha"] != plan.main:
        raise ObservationError("main changed during checkpoint readback")
    unknown = set(plan.unknown) | invalid
    # A quarantined product PR still occupies its original WIP slot.
    return replace(plan,proposals=tuple(proposals),unknown=tuple(sorted(unknown)),
                   queue_complete=plan.queue_complete and not unknown),reports
