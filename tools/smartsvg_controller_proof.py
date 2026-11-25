"""R15 evidence verification helpers; no GitHub writes or review authentication.

Callers must obtain blobs and log bytes from authenticated GitHub reads.
A matching hash binds bytes, not the trustworthiness of their producer.
"""
from dataclasses import dataclass
from hashlib import sha256
import re

SHA = re.compile(r"[0-9a-f]{40}")
TEST_ID = re.compile(r"[A-Za-z_][A-Za-z0-9_.]*")
LINE = re.compile(
    r"^(?:\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z )?"
    r"(test_[A-Za-z0-9_]+) \(([A-Za-z_][A-Za-z0-9_.]*)\) \.\.\. "
    r"(ok|FAIL|ERROR|skipped(?: .*)?|expected failure|unexpected success)$"
)
MAX_LOG = 16 * 1024 * 1024


@dataclass(frozen=True)
class PinResult:
    matched: bool
    reason: str


def verify_workflow_pin(expected, main_blob, head_blob):
    """Only compare against an explicitly reviewed pin; never auto-trust main."""
    if any(not isinstance(x, str) or SHA.fullmatch(x) is None
           for x in (expected, main_blob, head_blob)):
        return PinResult(False, "MISSING_OR_INVALID_PIN")
    if expected != main_blob:
        return PinResult(False, "MAIN_WORKFLOW_DRIFT")
    if expected != head_blob:
        return PinResult(False, "PR_WORKFLOW_DRIFT")
    return PinResult(True, "MATCHING_REVIEWED_PIN")


@dataclass(frozen=True)
class TestReceipt:
    test_id: str
    status: str
    lines: tuple


@dataclass(frozen=True)
class LogReceipt:
    run_id: int
    attempt: int
    job_id: int
    head: str
    digest: str
    tests: tuple
    qualification: str = "LOG_ONLY"


def parse_test_receipts(log, required, *, head, run_id, attempt, job_id):
    """Parse explicit unittest verbose result lines, not a suite green status.

    Duplicate results are ambiguous even when both say ok. Unrecognized
    formats and missing lines remain UNKNOWN. A job log alone does not
    establish checkout identity, scope, independent review or permission.
    """
    if not isinstance(log, str):
        raise ValueError("log must be text")
    raw = log.encode("utf-8")
    if len(raw) > MAX_LOG:
        raise ValueError("log too large")
    if (not isinstance(head, str) or SHA.fullmatch(head) is None
            or any(type(x) is not int or x < 1 for x in (run_id, attempt, job_id))):
        raise ValueError("invalid log provenance")
    required = tuple(required)
    if (not required or len(required) != len(set(required))
            or any(not isinstance(x, str) or TEST_ID.fullmatch(x) is None
                   or ".test_" not in x for x in required)):
        raise ValueError("invalid test identifiers")
    found = {name: [] for name in required}
    for number, line in enumerate(log.splitlines(), 1):
        m = LINE.fullmatch(line)
        if not m:
            continue
        short, name, outcome = m.groups()
        if name.rsplit(".", 1)[-1] != short or name not in found:
            continue
        status = ("PASS" if outcome == "ok" else
                  "SKIP" if outcome.startswith("skipped") else
                  "FAIL" if outcome in ("FAIL", "ERROR", "unexpected success")
                  else "UNKNOWN")
        found[name].append((number, status))
    receipts = []
    for name, rows in found.items():
        status = rows[0][1] if len(rows) == 1 else "UNKNOWN"
        receipts.append(TestReceipt(name, status, tuple(n for n, _ in rows)))
    return LogReceipt(run_id, attempt, job_id, head, sha256(raw).hexdigest(),
                      tuple(receipts))
