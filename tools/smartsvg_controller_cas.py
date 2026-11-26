"""Public-metadata-only durable CAS rehearsal. Never authorizes a merge.

Transport contract: read() returns (ref SHA, canonical state bytes);
stage(parent, bytes) creates a single-parent commit off-ref;
advance(expected, candidate) uses a non-forced ref update.
All transports must pin a dedicated journal branch, never main.
A failed/unknown advance is reconciled by exact ref and state readback.
"""
from dataclasses import asdict, dataclass, replace
import json
import re

SHA = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"[0-9a-f]{64}")
TERMINAL = frozenset(("CANCELLED_PREPARED", "QUALIFIED_READBACK"))
OBSERVED = frozenset(("DISPATCH_UNKNOWN", "NEGATIVE_READBACK", "WAIT_G0",
                      "G0_FAILED", "MAIN_DRIFT", "QUALIFIED_READBACK"))
STATES = TERMINAL | OBSERVED | {"IDLE", "PREPARED"}


@dataclass(frozen=True)
class Record:
    generation: int = 0
    intent: int = 0
    state: str = "IDLE"
    number: int = 0
    head: str = ""
    main: str = ""
    tree: str = ""
    policy: str = ""
    evidence: str = ""


def valid(record):
    if (not isinstance(record, Record)
            or type(record.generation) is not int or record.generation < 0
            or type(record.intent) is not int or not 0 <= record.intent <= record.generation
            or not isinstance(record.state, str) or record.state not in STATES
            or type(record.number) is not int):
        raise ValueError("invalid record")
    if record.state == "IDLE":
        if record != Record():
            raise ValueError("invalid genesis")
    elif (record.intent < 1 or record.number < 1
          or any(not isinstance(x, str) or SHA.fullmatch(x) is None
                 for x in (record.head, record.main, record.tree, record.policy))
          or not isinstance(record.evidence, str)
          or DIGEST.fullmatch(record.evidence) is None):
        raise ValueError("invalid context")
    return record


def encode(record):
    return (json.dumps(dict(version=1, **asdict(valid(record))),
                       sort_keys=True, separators=(",", ":"), allow_nan=False)
            + "\n").encode("ascii")


def decode(raw):
    if not isinstance(raw, bytes) or len(raw) > 2048:
        raise ValueError("invalid state bytes")
    data = json.loads(raw)
    if not isinstance(data, dict) or type(data.pop("version", None)) is not int:
        raise ValueError("invalid schema")
    # Canonical encoding also rejects duplicate keys and unsupported versions.
    record = valid(Record(**data))
    if encode(record) != raw:
        raise ValueError("noncanonical state")
    return record


def prepare(previous, *, number, head, main, tree, policy, evidence):
    valid(previous)
    if previous.state not in TERMINAL | {"IDLE"}:
        raise ValueError("unresolved intent")
    return valid(Record(previous.generation + 1, previous.intent + 1,
                        "PREPARED", number, head, main, tree, policy, evidence))


def transition(previous, state, evidence):
    valid(previous)
    if previous.state == "PREPARED":
        allowed = {"DISPATCH_UNKNOWN", "CANCELLED_PREPARED"}
    elif previous.state in OBSERVED - TERMINAL:
        # A negative readback or timeout is not a terminal rejection.
        allowed = OBSERVED - {"DISPATCH_UNKNOWN"}
    else:
        allowed = set()
    if state not in allowed:
        raise ValueError("illegal transition")
    return valid(replace(previous, generation=previous.generation + 1,
                         state=state, evidence=evidence))


@dataclass(frozen=True)
class Result:
    state: str
    candidate: str | None = None
    observed: str | None = None
    merge_authorized: bool = False
    retry_authorized: bool = False


def _ref(value):
    if not isinstance(value, str) or SHA.fullmatch(value) is None:
        raise ValueError("invalid ref")
    return value


def persist(read, stage, advance, *, expected, previous, proposed):
    """CAS one valid transition. No retry, force push or merge API here.

    APPLIED means exact candidate and bytes were observed. It is not
    integration evidence. CONFLICT means another ref was observed, not
    terminality of an unrelated merge request. Ambiguity requires readback.
    """
    _ref(expected)
    before, after = encode(previous), encode(proposed)
    if proposed.intent == previous.intent + 1:
        check = prepare(previous, number=proposed.number, head=proposed.head,
                        main=proposed.main, tree=proposed.tree,
                        policy=proposed.policy, evidence=proposed.evidence)
    else:
        check = transition(previous, proposed.state, proposed.evidence)
    if proposed != check:
        raise ValueError("invalid proposed transition")
    try:
        ref, raw = read()
        _ref(ref)
        decode(raw)
    except Exception:
        return Result("READ_UNAVAILABLE")
    if ref != expected or raw != before:
        return Result("STALE", observed=ref)
    try:
        candidate = _ref(stage(expected, after))
        if candidate == expected:
            raise ValueError("stage did not create a commit")
    except Exception:
        return Result("STAGE_UNAVAILABLE")
    try:
        advance(expected, candidate)
    except Exception:
        # A transport failure can occur after the ref was updated.
        pass
    try:
        ref, raw = read()
        _ref(ref)
        decode(raw)
    except Exception:
        return Result("AMBIGUOUS", candidate)
    if ref == candidate:
        return Result("APPLIED" if raw == after else "AMBIGUOUS", candidate, ref)
    if ref == expected:
        return Result("AMBIGUOUS", candidate, ref)
    return Result("CONFLICT", candidate, ref)
