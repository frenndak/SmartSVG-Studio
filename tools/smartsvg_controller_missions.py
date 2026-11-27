"""R15.2 local mission checkpoint journal.

Append-only, bounded, exact-context and CAS checked. It does not authenticate
a scheduler, reserve a GitHub branch or qualify a mission for integration.
The live adapter and operational transport remain separate work.
"""
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import sqlite3
from contextlib import contextmanager

from .smartsvg_controller_objectives import (
    Advice, Profile, Objective, _validate_profile, _validate_objective,
    _matches, plan_objectives, ROLES, TOKEN, SHA, DIGEST,
)

MAX_EVENTS = 256
MAX_MISSIONS = 128
MAX_RECORD = 8192
STATES = ("PLANNED", "ACTIVE", "WAITING", "BLOCKED_LOCAL", "REVIEW", "CANCELLED")
TRANSITIONS = {
    "PLANNED": ("ACTIVE", "WAITING", "BLOCKED_LOCAL", "CANCELLED"),
    "ACTIVE": ("ACTIVE", "WAITING", "BLOCKED_LOCAL", "REVIEW", "CANCELLED"),
    "WAITING": ("ACTIVE", "WAITING", "BLOCKED_LOCAL", "CANCELLED"),
    "BLOCKED_LOCAL": ("ACTIVE", "WAITING", "BLOCKED_LOCAL", "CANCELLED"),
    "REVIEW": ("ACTIVE", "WAITING", "BLOCKED_LOCAL", "REVIEW", "CANCELLED"),
    "CANCELLED": (),
}


class MissionError(ValueError):
    pass


@dataclass(frozen=True)
class Checkpoint:
    profile: Profile
    objective: Objective
    main: str
    generation: int
    state: str
    next_action: str
    evidence: str
    predecessor: str
    digest: str
    qualification: str = "LOCAL_ADVISORY_ONLY"


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def _scope(profile):
    _validate_profile(profile)
    return sha256(_canonical(asdict(profile))).hexdigest()


def _material(profile, objective, main, generation, state, next_action, evidence, predecessor):
    _validate_profile(profile)
    _validate_objective(objective)
    if (not _matches(SHA, main) or type(generation) is not int
            or not 1 <= generation <= MAX_EVENTS or state not in STATES
            or not _matches(TOKEN, next_action)
            or not isinstance(evidence, str)
            or (evidence != "" and not _matches(DIGEST, evidence))
            or not isinstance(predecessor, str)
            or (generation == 1 and predecessor != "")
            or (generation > 1 and not _matches(DIGEST, predecessor))):
        raise MissionError("invalid checkpoint")
    return {"version": 1, "profile": asdict(profile), "objective": asdict(objective),
            "main": main, "generation": generation, "state": state,
            "next_action": next_action, "evidence": evidence, "predecessor": predecessor}


def _record(material):
    raw = _canonical(material)
    if len(raw) > MAX_RECORD:
        raise MissionError("checkpoint too large")
    return raw, sha256(raw).hexdigest()


def _decode(raw, digest):
    if type(raw) is not bytes or len(raw) > MAX_RECORD or not _matches(DIGEST, digest):
        raise MissionError("invalid checkpoint bytes")
    if sha256(raw).hexdigest() != digest:
        raise MissionError("checkpoint digest mismatch")
    try:
        m = json.loads(raw)
        if type(m) is not dict or m.get("version") != 1:
            raise MissionError("invalid checkpoint version")
        profile = Profile(**m["profile"])
        obj = dict(m["objective"])
        obj["criteria"] = tuple(obj["criteria"])
        obj["dependencies"] = tuple(obj["dependencies"])
        objective = Objective(**obj)
        args = (profile, objective, m["main"], m["generation"], m["state"],
                m["next_action"], m["evidence"], m["predecessor"])
        if _record(_material(*args)) != (raw, digest):
            raise MissionError("noncanonical checkpoint")
        return Checkpoint(*args, digest)
    except (KeyError, TypeError, ValueError, AttributeError) as exc:
        raise MissionError("invalid checkpoint") from exc


class MissionJournal:
    """Local SQLite only, distinct from the live integration intent journal."""

    def __init__(self, path):
        self.db = sqlite3.connect(path, isolation_level=None, timeout=5)
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.execute("""CREATE TABLE IF NOT EXISTS mission_checkpoint_v1(
            scope TEXT NOT NULL, mission TEXT NOT NULL, generation INTEGER NOT NULL,
            digest TEXT NOT NULL, raw BLOB NOT NULL,
            PRIMARY KEY(scope, mission, generation),
            UNIQUE(scope, mission, digest))""")

    def close(self):
        self.db.close()

    @contextmanager
    def _transaction(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    def _history(self, profile, key):
        scope = _scope(profile)
        if not _matches(TOKEN, key):
            raise MissionError("invalid mission key")
        rows = self.db.execute(
            "SELECT generation,digest,raw FROM mission_checkpoint_v1 "
            "WHERE scope=? AND mission=? ORDER BY generation LIMIT ?",
            (scope, key, MAX_EVENTS + 1)).fetchall()
        if len(rows) > MAX_EVENTS:
            raise MissionError("mission history exceeds bound")
        result = []
        seen_evidence = set()
        for expected, (generation, digest, raw) in enumerate(rows, 1):
            c = _decode(raw, digest)
            if (generation != expected or c.generation != expected
                    or c.profile != profile or c.objective.key != key
                    or c.predecessor != (result[-1].digest if result else "")):
                raise MissionError("mission history mismatch")
            if not result:
                if c.state != "PLANNED" or c.evidence:
                    raise MissionError("invalid mission genesis")
            else:
                prev = result[-1]
                if prev.state == "CANCELLED":
                    raise MissionError("mission already cancelled")
                # Mission identity and writer are not transferable by context drift.
                if (prev.objective.role != c.objective.role
                        or prev.objective.criteria != c.objective.criteria
                        or prev.objective.dependencies != c.objective.dependencies
                        or prev.objective.preparation_allowed != c.objective.preparation_allowed):
                    raise MissionError("mission contract changed")
                drift = prev.main != c.main or prev.objective.revision != c.objective.revision
                if drift:
                    if c.state != "PLANNED" or c.evidence:
                        raise MissionError("stale evidence in new context")
                elif (c.objective != prev.objective
                      or c.state not in TRANSITIONS[prev.state] or not c.evidence):
                    raise MissionError("invalid mission transition")
            if c.evidence:
                if c.evidence in seen_evidence:
                    raise MissionError("duplicate mission evidence in history")
                seen_evidence.add(c.evidence)
            result.append(c)
        return tuple(result)

    def history(self, profile, key):
        """Immutable local record history, not an execution receipt."""
        return self._history(profile, key)

    def latest(self, profile, key):
        history = self._history(profile, key)
        return history[-1] if history else None

    def _append(self, profile, objective, main, generation, state, next_action,
                evidence, predecessor):
        material = _material(profile, objective, main, generation, state,
                             next_action, evidence, predecessor)
        raw, digest = _record(material)
        self.db.execute("INSERT INTO mission_checkpoint_v1 VALUES(?,?,?,?,?)",
                        (_scope(profile), objective.key, generation, digest, raw))
        return _decode(raw, digest)

    def create(self, profile, objective, main, *, next_action="VERIFY_CRITERION"):
        """Create one explicit mission; never invent a PR, owner or work proof."""
        _validate_objective(objective)
        with self._transaction():
            if self._history(profile, objective.key):
                raise MissionError("mission already exists")
            count = self.db.execute(
                "SELECT COUNT(DISTINCT mission) FROM mission_checkpoint_v1 WHERE scope=?",
                (_scope(profile),)).fetchone()[0]
            if count >= MAX_MISSIONS:
                raise MissionError("mission inventory full")
            return self._append(profile, objective, main, 1, "PLANNED", next_action, "", "")

    def advance(self, profile, key, *, expected_generation, expected_digest,
                main, revision, role, state, next_action, evidence):
        """Append a bounded advisory outcome under the current exact context.

        Evidence must come from an external verifier. A digest's syntax does
        not authenticate it. VERIFIED/INTEGRATED/DONE are intentionally not
        writable until their live acceptance adapter is qualified.
        """
        with self._transaction():
            history = self._history(profile, key)
            prev = history[-1] if history else None
            if (prev is None or type(expected_generation) is not int
                    or prev.generation != expected_generation
                    or prev.digest != expected_digest):
                return None
            if (main != prev.main or revision != prev.objective.revision
                    or role != prev.objective.role):
                return None
            if state not in TRANSITIONS[prev.state] or not _matches(DIGEST, evidence):
                raise MissionError("unsupported mission transition")
            # Retrying a transport operation with the same previous CAS fails.
            # Reusing an earlier evidence digest also cannot manufacture progress.
            if any(c.evidence == evidence for c in history):
                raise MissionError("duplicate mission evidence")
            return self._append(profile, prev.objective, main, prev.generation + 1,
                                state, next_action, evidence, prev.digest)

    def recontextualize(self, profile, objective, main, *, expected_generation,
                        expected_digest, next_action="VERIFY_CRITERION"):
        """Preserve old history while explicitly invalidating a changed context."""
        _validate_objective(objective)
        with self._transaction():
            prev = self.latest(profile, objective.key)
            if (prev is None or type(expected_generation) is not int
                    or prev.generation != expected_generation
                    or prev.digest != expected_digest):
                return None
            if prev.state == "CANCELLED":
                raise MissionError("mission already cancelled")
            if (prev.objective.role != objective.role
                    or prev.objective.criteria != objective.criteria
                    or prev.objective.dependencies != objective.dependencies
                    or prev.objective.preparation_allowed != objective.preparation_allowed):
                raise MissionError("new mission contract required")
            if prev.main == main and prev.objective.revision == objective.revision:
                raise MissionError("context unchanged")
            return self._append(profile, objective, main, prev.generation + 1,
                                "PLANNED", next_action, "", prev.digest)


@dataclass(frozen=True)
class MissionAdvice:
    objective: Advice
    checkpoint_status: str
    checkpoint: Checkpoint | None = None


@dataclass(frozen=True)
class MissionResumePlan:
    missions: tuple
    selected: MissionAdvice | None
    ignored_receipts: int
    qualification: str = "LOCAL_ADVISORY_ONLY"


def plan_mission_resumption(journal, profile, main, objectives, *, role, receipts=()):
    """Choose a useful objective from fresh evidence and exact local checkpoints.

    The checkpoint is context for resuming work. Only freshly evaluated
    objective advice can be selected. Resuming a held or stale mission
    requires a separately observed outcome and an explicit journal update.
    This read does not claim a mission or transfer a writer.
    """
    if role not in ROLES:
        raise MissionError("invalid mission role")
    plan = plan_objectives(profile, main, objectives, receipts)
    by_key = {objective.key: objective for objective in objectives}
    missions = []
    for advice in plan.objectives:
        if advice.role != role:
            continue
        objective = by_key[advice.objective]
        try:
            checkpoint = journal.latest(profile, objective.key)
        except MissionError:
            missions.append(MissionAdvice(advice, "UNREADABLE"))
            continue
        if checkpoint is None:
            missions.append(MissionAdvice(advice, "NEW"))
            continue
        saved = checkpoint.objective
        if (checkpoint.main != main or saved.revision != objective.revision
                or saved.role != objective.role or saved.criteria != objective.criteria
                or saved.dependencies != objective.dependencies
                or saved.preparation_allowed != objective.preparation_allowed):
            missions.append(MissionAdvice(advice, "STALE_CONTEXT"))
            continue
        missions.append(MissionAdvice(advice, checkpoint.state, checkpoint))

    selected = next((mission for mission in missions
                     if mission.checkpoint_status in ("NEW", "PLANNED", "ACTIVE")
                     and mission.objective.action in ("REPAIR_CRITERION",
                                                      "VERIFY_CRITERION",
                                                      "PREPARE_INDEPENDENT")), None)
    return MissionResumePlan(tuple(missions), selected, plan.ignored_receipts)
