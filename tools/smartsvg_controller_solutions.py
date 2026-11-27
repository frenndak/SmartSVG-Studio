"""R15.2 local incident solution memory, with live compatibility readback.

A solution is a bounded technical strategy record, not a permission, script,
successful current execution or review. Callers must independently establish
past validation and current compatibility. No network or GitHub writes.
"""
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import sqlite3

from .smartsvg_controller_objectives import Profile, _validate_profile, _matches, TOKEN, SHA, DIGEST

MAX_SOLUTIONS = 128
MAX_HISTORY = 32
MAX_RECORD = 8192
STRATEGIES = ("RETRY_READ_ALTERNATE", "INSPECT_INDEPENDENT", "REPAIR_AND_RETEST",
              "RECONCILE_STATE", "PREPARE_FIXTURE", "REQUEST_REVIEW_HANDOFF",
              "WAIT_FOR_CONDITION")


@dataclass(frozen=True)
class Solution:
    profile: Profile
    incident: str
    resource: str
    symptom: str
    diagnosis: str
    strategy: str
    compatibility: str
    validated_revision: str
    validation_digest: str
    prerequisites: tuple = ()
    contraindications: tuple = ()


@dataclass(frozen=True)
class SolutionHint:
    strategy: str
    solution_digest: str
    validated_revision: str
    qualification: str = "REVALIDATE_ADVISORY_ONLY"
    merge_authorized: bool = False
    agent_work_executed: bool = False


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode()


def _scope(profile):
    _validate_profile(profile)
    return sha256(_canonical(asdict(profile))).hexdigest()


def _flags(values):
    return (type(values) is tuple and len(values) <= 32
            and all(_matches(TOKEN, value) for value in values)
            and len(values) == len(set(values)) and values == tuple(sorted(values)))


def _encode(solution):
    if type(solution) is not Solution:
        raise ValueError("invalid solution")
    _validate_profile(solution.profile)
    if (not _matches(DIGEST, solution.incident)
            or not all(_matches(TOKEN, v) for v in
                       (solution.resource, solution.symptom, solution.diagnosis))
            or solution.strategy not in STRATEGIES
            or not _matches(DIGEST, solution.compatibility)
            or not _matches(SHA, solution.validated_revision)
            or not _matches(DIGEST, solution.validation_digest)
            or not _flags(solution.prerequisites) or not _flags(solution.contraindications)
            or set(solution.prerequisites) & set(solution.contraindications)):
        raise ValueError("invalid solution fields")
    raw = _canonical({"version": 1, **asdict(solution)})
    if len(raw) > MAX_RECORD:
        raise ValueError("solution too large")
    return raw, sha256(raw).hexdigest()


def _decode(raw, digest):
    if (type(raw) is not bytes or len(raw) > MAX_RECORD
            or not _matches(DIGEST, digest) or sha256(raw).hexdigest() != digest):
        raise ValueError("solution integrity failure")
    try:
        v = json.loads(raw)
        if type(v) is not dict or type(v.get("version")) is not int or v.pop("version") != 1:
            raise ValueError("invalid solution version")
        v["profile"] = Profile(**v["profile"])
        v["prerequisites"] = tuple(v["prerequisites"])
        v["contraindications"] = tuple(v["contraindications"])
        solution = Solution(**v)
        if _encode(solution) != (raw, digest):
            raise ValueError("noncanonical solution")
        return solution
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("invalid solution bytes") from exc


class SolutionMemory:
    """Immutable, bounded local records; no overwrite or automatic promotion."""

    def __init__(self, path):
        self.db = sqlite3.connect(path, isolation_level=None, timeout=5)
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.execute("""CREATE TABLE IF NOT EXISTS solution_v1(
            scope TEXT NOT NULL, incident TEXT NOT NULL, resource TEXT NOT NULL,
            compatibility TEXT NOT NULL, digest TEXT PRIMARY KEY,
            validation TEXT NOT NULL, raw BLOB NOT NULL,
            UNIQUE(scope, validation))""")
        self.db.execute("""CREATE INDEX IF NOT EXISTS solution_scope_v1
            ON solution_v1(scope, incident, resource, compatibility)""")

    def close(self):
        self.db.close()

    def store(self, solution):
        """Store one independently validated historical solution idempotently.

        The digest's syntax is not evidence provenance. The observer must
        actually validate the method and result before calling this API.
        """
        raw, digest = _encode(solution)
        scope = _scope(solution.profile)
        self.db.execute("BEGIN IMMEDIATE")
        try:
            existing = self.db.execute(
                "SELECT scope,incident,resource,compatibility,validation,raw FROM solution_v1 "
                "WHERE digest=?", (digest,)).fetchone()
            value = (scope, solution.incident, solution.resource, solution.compatibility,
                     solution.validation_digest, raw)
            if existing is not None:
                if existing != value:
                    raise ValueError("solution index mismatch")
            else:
                # A validation receipt cannot be relabeled as another method.
                if self.db.execute("SELECT 1 FROM solution_v1 WHERE scope=? AND validation=?",
                                   (scope, solution.validation_digest)).fetchone():
                    raise ValueError("validation already bound")
                total = self.db.execute("SELECT COUNT(*) FROM solution_v1 WHERE scope=?",
                                        (scope,)).fetchone()[0]
                history = self.db.execute(
                    "SELECT COUNT(*) FROM solution_v1 WHERE scope=? AND incident=? AND resource=?",
                    (scope, solution.incident, solution.resource)).fetchone()[0]
                if total >= MAX_SOLUTIONS or history >= MAX_HISTORY:
                    raise ValueError("solution inventory full; reviewed archival required")
                self.db.execute("INSERT INTO solution_v1 VALUES(?,?,?,?,?,?,?)",
                                (scope, solution.incident, solution.resource, solution.compatibility,
                                 digest, solution.validation_digest, raw))
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        return digest

    def hints(self, profile, incident, resource, compatibility, *, known_present=(),
              known_absent=(), verify):
        """Offer only compatible solutions with freshly confirmed conditions.

        The verifier must re-read a trusted current context, validate the
        historical receipt's applicability and return literal True. Unknown
        conditions, unavailable verification and conflicting observations
        cannot promote a historical solution. Multiple hints are alternatives,
        not an instruction to execute any of them.
        """
        scope = _scope(profile)
        if (not _matches(DIGEST, incident) or not _matches(TOKEN, resource)
                or not _matches(DIGEST, compatibility) or not _flags(known_present)
                or not _flags(known_absent) or set(known_present) & set(known_absent)
                or not callable(verify)):
            raise ValueError("invalid current incident context")
        rows = self.db.execute(
            "SELECT digest,validation,raw FROM solution_v1 WHERE scope=? AND incident=? "
            "AND resource=? AND compatibility=? ORDER BY digest LIMIT ?",
            (scope, incident, resource, compatibility, MAX_HISTORY+1)).fetchall()
        if len(rows) > MAX_HISTORY:
            raise ValueError("solution history exceeds bound")
        result = []
        for digest, validation, raw in rows:
            solution = _decode(raw, digest)
            if ((solution.profile, solution.incident, solution.resource,
                 solution.compatibility, solution.validation_digest) !=
                    (profile, incident, resource, compatibility, validation)):
                raise ValueError("solution index context mismatch")
            if (not set(solution.prerequisites) <= set(known_present)
                    or not set(solution.contraindications) <= set(known_absent)):
                continue
            try:
                applicable = verify(solution)
            except (OSError, ValueError, RuntimeError, LookupError, TypeError):
                # Optional knowledge is not allowed to suppress independent work.
                continue
            if applicable is True:
                result.append(SolutionHint(solution.strategy, digest, solution.validated_revision))
        return tuple(result)
