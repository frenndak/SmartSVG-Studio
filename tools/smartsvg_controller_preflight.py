"""Deterministic R15 integration preflight. No mutation or authorization.

This consumes explicit, externally verified evidence contracts, not raw
collector output or review hints. The caller must authenticate every receipt
and determine semantic scope/applicability. No adapter may infer VERIFIED
from a comment, a green workflow, a hash alone, or a self-declared flag.
"""
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from hashlib import sha256
import json
import re

SHA = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"[0-9a-f]{64}")
MAX_AGE = timedelta(minutes=5)
GATES = frozenset(("authority", "scheduler", "same_repo_author", "scope_complete",
                   "semantic_review", "threads_clear", "effective_rules",
                   "external_approval", "mergeable", "non_draft",
                   "rollback", "main_g0", "cycle_budget"))
CHECKS = frozenset(("g0", "preflight", "cpu", "windows_python", "strict_v1_tk_cpu"))
STATUSES = frozenset(("PASS", "FAIL", "SKIP", "PENDING", "UNKNOWN"))
FORBIDDEN = frozenset(("tools/verify_source_integrity.py",
    "tools/validate_release_archive.py", "tools/import_release_archive.py",
    "tools/verify_v21152_manifest.py", "tests/test_governance_owner_delegation.py",
    "tests/test_dual_producer_governance_r13.py", "tests/test_release_archive_gate.py",
    "tests/test_release_import.py", "tests/test_v21152_manifest.py",
    "tests/test_private_workflow_routing.py", "engine/requirements.txt"))


@dataclass(frozen=True)
class IntegrationSubject:
    number: int
    head: str
    main: str
    policy_blob: str
    writer: str
    author_cycle: str
    executor_cycle: str
    diff_digest: str
    paths: tuple
    cpu_relevant: bool
    windows_relevant: bool
    targeted_tests: tuple


@dataclass(frozen=True)
class Fact:
    name: str
    subject_digest: str
    status: str
    qualification: str
    receipt_digest: str
    observed_at: datetime


@dataclass(frozen=True)
class Preflight:
    action: str
    reasons: tuple
    subject_digest: str
    merge_authorized: bool = False


def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def _valid_path(path):
    if (not isinstance(path, str) or "\\" in path or
            any(p in ("", ".", "..") for p in path.split("/"))):
        return False
    return (path.startswith(("engine/", "tests/", "tools/", "examples/synthetic/"))
            and path not in FORBIDDEN
            and not path.lower().endswith((".zip", ".exe", ".dll", ".bin", ".whl"))
            and path.rsplit("/", 1)[-1].lower() not in
            ("requirements.txt", "package-lock.json", "pyproject.toml", "setup.py"))


def requirements(subject):
    """Compute minimum CI checks; semantic applicability remains external.

    Engine changes always require CPU. Tests/tools-only changes need explicit
    targeted tests; CPU/Windows applicability must be reviewed, not guessed.
    """
    names = {"g0", "preflight"}
    if subject.cpu_relevant or any(p.startswith("engine/") for p in subject.paths):
        names.add("cpu")
    if subject.windows_relevant:
        names.update(("windows_python", "strict_v1_tk_cpu"))
    return frozenset(names)


def evaluate(subject, facts, *, role, now):
    """Return advisory preflight only; never call a GitHub mutation."""
    if (not isinstance(now, datetime) or now.utcoffset() is None
            or type(subject.number) is not int or subject.number < 1
            or any(not isinstance(x, str) or SHA.fullmatch(x) is None
                   for x in (subject.head, subject.main, subject.policy_blob))
            or not isinstance(subject.diff_digest, str)
            or DIGEST.fullmatch(subject.diff_digest) is None
            or subject.writer not in ("A", "B")
            or type(subject.cpu_relevant) is not bool
            or type(subject.windows_relevant) is not bool
            or not isinstance(subject.paths, tuple) or not subject.paths
            or any(not isinstance(p, str) for p in subject.paths)
            or len(set(subject.paths)) != len(subject.paths)
            or not isinstance(subject.targeted_tests, tuple)
            or not subject.targeted_tests
            or any(not isinstance(t, str) or not t or len(t)>512
                   for t in subject.targeted_tests)
            or len(set(subject.targeted_tests)) != len(subject.targeted_tests)):
        return Preflight("INSPECT", ("INVALID_SUBJECT",), "")
    key = _digest(asdict(subject))
    def result(action, *reasons):
        return Preflight(action, reasons, key)
    if not all(_valid_path(p) for p in subject.paths):
        return result("OWNER_REVIEW", "EXCLUDED_PATH")
    if role != "B":
        return result("NO_MERGE", "B_ONLY")
    if (not isinstance(subject.author_cycle, str) or not subject.author_cycle
            or not isinstance(subject.executor_cycle, str) or not subject.executor_cycle
            or subject.author_cycle == subject.executor_cycle):
        return result("NO_MERGE", "DISTINCT_CYCLE_REQUIRED")
    required = GATES | {"ci:" + x for x in requirements(subject)} | {
        "test:" + x for x in subject.targeted_tests}
    by_name = {}
    for f in facts:
        if f.name not in required:
            continue
        if f.name in by_name:
            return result("INSPECT", "DUPLICATE_FACT:" + f.name)
        by_name[f.name] = f
    invalid, failed, waiting = [], [], []
    for name in sorted(required):
        f = by_name.get(name)
        if (f is None or f.subject_digest != key
                or f.qualification != "EXTERNALLY_VERIFIED"
                or not isinstance(f.receipt_digest, str)
                or DIGEST.fullmatch(f.receipt_digest) is None
                or not isinstance(f.observed_at, datetime)
                or f.observed_at.utcoffset() is None
                or not timedelta(0) <= now-f.observed_at <= MAX_AGE
                or f.status not in STATUSES):
            invalid.append(name)
        elif f.status == "FAIL":
            failed.append(name)
        elif f.status != "PASS":
            waiting.append(name + ":" + f.status)
    if failed:
        return result("BLOCKED", *failed, *invalid, *waiting)
    if invalid or waiting:
        return result("EVIDENCE_REQUIRED", *invalid, *waiting)
    return result("SHADOW_PREFLIGHT_PASS", "NOT_AUTHORIZATION", "FRESH_RECHECK_REQUIRED")
