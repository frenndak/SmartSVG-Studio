"""R15.2 descriptive cycle/delivery comparison from verified observations.

The adapter must independently verify scheduler and GitHub provenance.
Opaque digests do not authenticate their sources. No raw scheduler identity,
prompt, log or credential is needed. No action, permission or optimization
is activated by these calculations.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from statistics import median
import re

DIGEST = re.compile(r"[0-9a-f]{64}")
SHA = re.compile(r"[0-9a-f]{40}")
TOKEN = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}")
REPO = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}/[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}")
OUTCOMES = ("PRODUCTIVE", "NO_PROGRESS", "WAIT_ONLY", "EXTERNAL_BLOCKED", "UNKNOWN")
ROLES = ("A", "B")
MIN_COVERAGE_PERCENT = 80
MIN_ELIGIBLE = 20
MIN_WINDOW = timedelta(days=7)
MAX_WINDOW = timedelta(days=31)
MAX_DELIVERIES = 512


def _matches(pattern, value):
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def _utc(value):
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("timezone-aware timestamp required")
    return value.astimezone(timezone.utc)


@dataclass(frozen=True)
class Period:
    project: str
    repository: str
    start: datetime
    end: datetime
    cadence: tuple
    phase: str


@dataclass(frozen=True)
class Cycle:
    scheduled_for: datetime
    role: str
    run_digest: str
    outcome: str
    receipt_digest: str = ""
    artifact_digest: str = ""


@dataclass(frozen=True)
class Delivery:
    number: int
    opened: datetime
    merged: datetime
    head: str
    merge: str
    acceptance_digest: str
    product: bool


@dataclass(frozen=True)
class Summary:
    expected: int
    productive: int
    no_progress: int
    wait_only: int
    external_blocked: int
    unknown: int
    missing: int
    rejected: int
    duplicate_artifacts: int
    delivered: int
    lead_time_hours_median: float | None
    delivery_rejected: int
    qualification: str = "IMPORTED_OBSERVATIONS_ONLY"

    @property
    def known(self):
        return self.productive + self.no_progress + self.wait_only + self.external_blocked

    @property
    def eligible(self):
        return self.productive + self.no_progress

    @property
    def coverage(self):
        return self.known / self.expected if self.expected else None

    @property
    def productive_rate(self):
        return self.productive / self.eligible if self.eligible else None


@dataclass(frozen=True)
class Comparison:
    status: str
    baseline: Summary
    current: Summary
    productive_rate_change_pp: float | None
    reasons: tuple
    qualification: str = "DESCRIPTIVE_ONLY"
    causal_gain_established: bool = False
    optimization_authorized: bool = False


def _period(p):
    if (type(p) is not Period or not _matches(TOKEN, p.project)
            or not _matches(REPO, p.repository) or p.phase not in ("R13", "R15")
            or type(p.cadence) is not tuple or not 1 <= len(p.cadence) <= len(ROLES)):
        raise ValueError("invalid period")
    cadence = {}
    for pair in p.cadence:
        if type(pair) is not tuple or len(pair) != 2:
            raise ValueError("invalid cadence")
        role, minute = pair
        if (role not in ROLES or role in cadence or type(minute) is not int
                or not 0 <= minute <= 59):
            raise ValueError("invalid cadence")
        cadence[role] = minute
    start, end = _utc(p.start), _utc(p.end)
    if (start.minute or start.second or start.microsecond or end.minute
            or end.second or end.microsecond or not timedelta(0) < end-start <= MAX_WINDOW):
        raise ValueError("period must be bounded whole UTC hours")
    slots = set()
    hour = start
    while hour < end:
        for role, minute in cadence.items():
            slots.add((hour + timedelta(minutes=minute), role))
        hour += timedelta(hours=1)
    return start, end, cadence, slots


def _cycle(c):
    if (type(c) is not Cycle or c.role not in ROLES
            or not _matches(DIGEST, c.run_digest) or c.outcome not in OUTCOMES
            or not isinstance(c.receipt_digest, str)
            or not isinstance(c.artifact_digest, str)):
        raise ValueError("invalid cycle")
    if c.outcome == "UNKNOWN":
        if c.artifact_digest or (c.receipt_digest and not _matches(DIGEST,c.receipt_digest)):
            raise ValueError("invalid unknown observation")
    elif not _matches(DIGEST, c.receipt_digest):
        raise ValueError("known outcome requires independently checked receipt")
    if (c.outcome == "PRODUCTIVE" and not _matches(DIGEST,c.artifact_digest)
            or c.outcome != "PRODUCTIVE" and c.artifact_digest != ""):
        raise ValueError("invalid material artifact")
    return (_utc(c.scheduled_for), c.role)


def _deliveries(deliveries, start, end, prior):
    if type(deliveries) is not tuple or len(deliveries) > MAX_DELIVERIES:
        raise ValueError("invalid delivery inventory")
    by_pr = {}
    rejected = 0
    for d in deliveries:
        try:
            if (type(d) is not Delivery or type(d.number) is not int or d.number < 1
                    or type(d.product) is not bool or not _matches(SHA,d.head)
                    or not _matches(SHA,d.merge) or not _matches(DIGEST,d.acceptance_digest)):
                raise ValueError("invalid delivery")
            opened, merged = _utc(d.opened), _utc(d.merged)
            if not opened <= merged or not start <= merged < end:
                raise ValueError("delivery outside comparison period")
        except (ValueError, TypeError, OverflowError):
            rejected += 1
            continue
        # Governance work is explicitly not a delivered product DoD.
        by_pr.setdefault(d.number,set()).add(d)
    valid = []
    for n, rows in by_pr.items():
        if len(rows) != 1:
            rejected += len(rows)
            continue
        d = next(iter(rows))
        if not d.product:
            continue
        if any(identity in prior for identity in
               (("pr", n), ("merge", d.merge), ("receipt", d.acceptance_digest))):
            rejected += 1
            continue
        valid.append(d)
    identity = {}
    for d in valid:
        for kind,value in (("merge",d.merge),("receipt",d.acceptance_digest)):
            identity.setdefault((kind,value),set()).add(d.number)
    conflicted = {n for rows in identity.values() if len(rows)>1 for n in rows}
    kept = [d for d in valid if d.number not in conflicted]
    rejected += len(conflicted)
    durations = [(_utc(d.merged)-_utc(d.opened)).total_seconds()/3600 for d in kept]
    # Retain even conflicting previously observed identities so they cannot
    # be recycled as apparently new deliveries in a later comparison window.
    seen = {(kind, value) for rows in by_pr.values() for d in rows if d.product
            for kind, value in (("pr", d.number), ("merge", d.merge),
                                ("receipt", d.acceptance_digest))}
    return len(kept), median(durations) if durations else None, rejected, seen


def _summarize(period, cycles, deliveries, *, previous_artifacts=(), previous_deliveries=(),
               previous_runs=(), previous_receipts=()):
    start, end, _, slots = _period(period)
    if type(cycles) is not tuple or len(cycles) > len(slots)*4:
        raise ValueError("invalid cycle inventory")
    by_slot, run_slots, receipt_slots = {}, {}, {}
    rejected = 0
    for c in cycles:
        try:
            key = _cycle(c)
            if key not in slots:
                raise ValueError("cycle outside schedule")
        except (ValueError, TypeError, OverflowError):
            rejected += 1
            continue
        by_slot.setdefault(key,set()).add(c)
        run_slots.setdefault(c.run_digest,set()).add(key)
        if c.receipt_digest:
            receipt_slots.setdefault(c.receipt_digest,set()).add(key)
    conflicted = {k for rows in (*run_slots.values(),*receipt_slots.values())
                  if len(rows)>1 for k in rows}
    # A run or receipt belongs to exactly one scheduled cycle, including
    # across periods. Keep the earlier historical observation conservative.
    for identity in previous_runs:
        conflicted.update(run_slots.get(identity, ()))
    for identity in previous_receipts:
        conflicted.update(receipt_slots.get(identity, ()))
    artifacts = set(previous_artifacts)
    counts = {k:0 for k in OUTCOMES}
    duplicates = 0
    for key in sorted(by_slot):
        rows = by_slot[key]
        if key in conflicted or len(rows) != 1:
            counts["UNKNOWN"] += 1
            continue
        c = next(iter(rows))
        if c.outcome == "PRODUCTIVE":
            if c.artifact_digest in artifacts:
                # The repeated artifact does not prove no other work occurred.
                # Do not upgrade a duplicate claim to a measured outcome.
                counts["UNKNOWN"] += 1
                duplicates += 1
                continue
            artifacts.add(c.artifact_digest)
        counts[c.outcome] += 1
    delivered, lead, delivery_rejected, seen_deliveries = _deliveries(
        deliveries,start,end,set(previous_deliveries))
    return (Summary(len(slots),counts["PRODUCTIVE"],counts["NO_PROGRESS"],
                    counts["WAIT_ONLY"],counts["EXTERNAL_BLOCKED"],counts["UNKNOWN"],
                    len(slots)-len(by_slot),rejected,duplicates,delivered,lead,delivery_rejected),
            artifacts,seen_deliveries,set(run_slots),set(receipt_slots))


def summarize(period, cycles=(), deliveries=()):
    """One period, with unknowns and missing slots kept separate."""
    return _summarize(period,cycles,deliveries)[0]


def compare(baseline, current, *, baseline_cycles=(), current_cycles=(),
            baseline_deliveries=(), current_deliveries=()):
    """Only compare matched windows; no causal or adaptive authority."""
    bs,be,bc,_ = _period(baseline)
    cs,ce,cc,_ = _period(current)
    if ((baseline.project,baseline.repository)!=(current.project,current.repository)
            or baseline.phase!="R13" or current.phase!="R15"
            or bc!=cc or be>cs or be-bs!=ce-cs):
        raise ValueError("noncomparable periods")
    a,artifacts,deliveries,runs,receipts = _summarize(
        baseline,baseline_cycles,baseline_deliveries)
    b,_,_,_,_ = _summarize(current,current_cycles,current_deliveries,
                           previous_artifacts=artifacts,previous_deliveries=deliveries,
                           previous_runs=runs,previous_receipts=receipts)
    reasons = []
    if be-bs < MIN_WINDOW:
        reasons.append("WINDOW_TOO_SHORT")
    for label,s in (("BASELINE",a),("CURRENT",b)):
        if 100*s.known < MIN_COVERAGE_PERCENT*s.expected:
            reasons.append(label+"_COVERAGE_INSUFFICIENT")
        if s.eligible < MIN_ELIGIBLE:
            reasons.append(label+"_ELIGIBLE_SAMPLE_INSUFFICIENT")
    if reasons:
        return Comparison("INSUFFICIENT_DATA",a,b,None,tuple(reasons))
    return Comparison("DESCRIPTIVE_COMPARISON",a,b,
                      100*(b.productive_rate-a.productive_rate),())
