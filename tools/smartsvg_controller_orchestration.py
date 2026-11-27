"""R15 shadow orchestration: raw snapshot -> bounded work advice -> local lease.

No GitHub mutation, agent invocation, review authentication, or merge authority.
An operator-supplied scope is a routing hint, not an authorization receipt.
"""
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
import re

from .smartsvg_controller_decision import Candidate, Check, Context, Status, decide
from .smartsvg_controller_evidence import Work, dispatch, step_receipts

REPO = "frenndak/SmartSVG-Studio"
SHA = re.compile(r"[0-9a-f]{40}")
MAX_AGE = timedelta(minutes=5)
MAX_COLLECTION = timedelta(minutes=15)


@dataclass(frozen=True)
class Scope:
    number: int
    head: str
    writer: str
    code_only: bool


@dataclass(frozen=True)
class Proposal:
    number: int
    head: str
    writer: str
    action: str
    reasons: tuple
    steps: tuple


@dataclass(frozen=True)
class Plan:
    main: str
    policy_blob: str
    finished: datetime
    proposals: tuple
    code_wip: int
    queue_complete: bool
    unknown: tuple


@dataclass(frozen=True)
class Reservation:
    number: int
    action: str
    head: str
    context_key: str
    owner: str
    fence: int
    checkpoint: str
    recovery_advice: str


def _sha(value):
    if not isinstance(value, str) or SHA.fullmatch(value) is None:
        raise ValueError("invalid SHA")
    return value


def _now(now):
    now = datetime.now(timezone.utc) if now is None else now
    if not isinstance(now, datetime) or now.utcoffset() is None:
        raise ValueError("timezone-aware time required")
    return now


def _fresh(finished, now):
    if not timedelta(0) <= now - finished <= MAX_AGE:
        raise ValueError("stale or future observation")


def build_plan(snapshot, scopes, *, now=None):
    """Route only explicitly scoped exact-HEAD candidates; never infer reviews."""
    now = _now(now)
    if snapshot.get("qualification") != "RAW_ONLY":
        raise ValueError("expected raw observation")
    started = _now(datetime.fromisoformat(snapshot["started_at"]))
    finished = _now(datetime.fromisoformat(snapshot["finished_at"]))
    _fresh(finished, now)
    if not timedelta(0) <= finished - started <= MAX_COLLECTION:
        raise ValueError("invalid collection interval")
    main = _sha(snapshot["main"]["commit"]["sha"])
    policy = _sha(snapshot["policy_blob"])
    scope_by_number = {}
    for scope in scopes:
        if (type(scope.number) is not int or scope.number < 1
                or scope.number in scope_by_number or type(scope.code_only) is not bool
                or (scope.code_only and scope.writer not in ("A", "B"))):
            raise ValueError("invalid or duplicate scope")
        _sha(scope.head)
        scope_by_number[scope.number] = scope
    proposals, unknown, seen = [], [], set()
    wip = 0
    # Raw workflow steps cannot qualify a review or a merge.
    ctx = Context(main, policy, False, False, False, False, Status.UNKNOWN, "", True)
    for entry in snapshot["candidates"]:
        pr = entry["pr"]
        n = pr["number"]
        if type(n) is not int or n < 1 or n in seen or pr.get("state") != "open":
            raise ValueError("invalid or duplicate open PR")
        seen.add(n)
        if "collection_error" in entry:
            unknown.append(n)
            wip += 1
            continue
        head = _sha(pr["head"]["sha"])
        scope = scope_by_number.get(n)
        branch = entry.get("branch") or {}
        if (scope is None or scope.head != head
                or branch.get("status") != "MATCH"
                or branch.get("sha") != head):
            unknown.append(n)
            wip += 1  # unknown scope cannot free a slot
            continue
        if not scope.code_only:
            proposals.append(Proposal(n, head, scope.writer, "OWNER_REVIEW", (), ()))
            continue
        wip += 1
        same_repo = (pr.get("head", {}).get("repo", {}).get("full_name") == REPO
                     and pr.get("base", {}).get("repo", {}).get("full_name") == REPO
                     and pr.get("base", {}).get("ref") == "main")
        # This is a deliberately narrow owner identity, not a general verifier.
        author = pr.get("user", {}).get("login") == "frenndak"
        if not same_repo or not author:
            unknown.append(n)
            continue
        steps = step_receipts(head, entry["runs"])
        # A failed step is a repair signal. PASS is not full test evidence.
        failed = tuple(Check(s.name, head, Status.FAIL, False, "")
                       for s in steps if s.status is Status.FAIL)
        candidate = Candidate(n, head, scope.writer, True, True, True,
                              pr.get("draft") is not False, pr.get("mergeable"),
                              None, failed, None)
        decision = decide(ctx, candidate)
        proposals.append(Proposal(n, head, scope.writer, decision.action,
                                  decision.reasons, steps))
    complete = not unknown and seen == set(scope_by_number)
    return Plan(main, policy, finished, tuple(sorted(proposals, key=lambda x: x.number)),
                wip, complete, tuple(sorted(unknown)))


def _context(plan, p):
    raw = json.dumps([plan.main, plan.policy_blob, p.number, p.head, p.writer, p.action],
                     separators=(",", ":")).encode()
    return sha256(raw).hexdigest()


def reserve_next(plan, role, journal, *, now=None, ttl=300, roadmap_ranks=None):
    """Reserve a local advisory PR unit, falling through on lease contention.

    The lease is not a GitHub lock. Re-observe before any real action.
    A new main/policy/head/action cannot reuse the previous checkpoint.
    No new development lease, writer transfer, or merge is performed.
    """
    _fresh(plan.finished, _now(now))
    candidates = {p.number: p for p in plan.proposals}
    ranks = roadmap_ranks or {}
    work = [Work(p.number, p.writer, p.action, roadmap_rank=ranks.get(p.number))
            for p in plan.proposals]
    while work:
        number, action = dispatch(role, work, plan.code_wip, queue_complete=False)
        if number is None:
            break
        p = candidates[number]
        key = _context(plan, p)
        item = "pr:" + str(number)
        fence = journal.claim(item, key, role, ttl)
        if fence is not None:
            return Reservation(number, action, p.head, key, role, fence,
                               journal.checkpoint(item, key) or "",
                               journal.advise(item, key, role))
        work = [w for w in work if w.number != number]
    return None
