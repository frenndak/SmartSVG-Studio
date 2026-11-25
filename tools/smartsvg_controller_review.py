"""R15 cross-review correlation, shadow only.

The scheduler readback must be obtained independently of the PR comment.
This is a correlation protocol, not a signature, native GitHub approval,
or proof that the technical analysis was correct.
"""
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import re

TASKS = {
    "A": "6ae27963fd848191a1053dfc486e8eb4",
    "B": "Automation_d020c270de78819198e9ab503ec7fb6e",
}
SHA = re.compile(r"[0-9a-f]{40}")
PREFIX = "R15_REVIEW_RECEIPT "
MAX_BODY = 65536


@dataclass(frozen=True)
class ReviewContext:
    number: int
    head: str
    main: str
    policy_blob: str
    writer: str
    # Trusted external observation of the latest author cycle and exact HEAD.
    author_run: str
    author_completed_at: str
    head_committed_at: str


@dataclass(frozen=True)
class Correlation:
    status: str
    reason: str
    native_approval: bool = False


def _time(value):
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.utcoffset() is None:
        raise ValueError("timezone required")
    return dt


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def correlate_review(context, role, scheduler, comment):
    """Correlate explicit final receipt with actual completed scheduler cycle.

    Inputs must come from independently fetched trusted sources. No parsing
    free-form claims, no approval synthesis, no extrapolation to another SHA.
    A positive correlation remains advisory, subject to semantic review and
    mutable GitHub gates. Legacy/unstructured receipts require manual review.
    """
    def reject(reason):
        return Correlation("UNKNOWN", reason)

    try:
        if (role not in TASKS or context.writer not in TASKS or role == context.writer
                or type(context.number) is not int or context.number < 1
                or any(SHA.fullmatch(s) is None for s in
                       (context.head, context.main, context.policy_blob))):
            return reject("INVALID_CONTEXT")
        if scheduler["id"] != TASKS[role] or scheduler.get("is_enabled") is not True:
            return reject("TASK_IDENTITY")
        detail = scheduler["run_details"]
        run, result = detail["last_run"], detail["latest_result"]
        if (run["recorded_status"] != "completed" or not run["id"]
                or run["id"] == context.author_run or result["run_id"] != run["id"]
                or result.get("requires_user_action") is not False
                or result.get("is_failure_message") is not False
                or result.get("content_truncated") is not False):
            return reject("INVALID_OR_INCOMPLETE_CYCLE")
        start, end = _time(run["started_at"]), _time(run["completed_at"])
        if (not context.author_run or start <= _time(context.author_completed_at)
                or start <= _time(context.head_committed_at) or end < start
                or _time(result["created_at"]) < start
                or _time(result["created_at"]) > end):
            return reject("NOT_LATER_CYCLE")
        body = comment["body"]
        if (not isinstance(body, str) or not body.strip() or len(body) > MAX_BODY
                or comment["user"]["login"] != "frenndak"
                or type(comment["id"]) is not int or comment["id"] < 1
                or comment["issue_url"] !=
                f"https://api.github.com/repos/frenndak/SmartSVG-Studio/issues/{context.number}"):
            return reject("COMMENT_IDENTITY")
        created, updated = _time(comment["created_at"]), _time(comment["updated_at"])
        if not start <= created <= updated <= end:
            return reject("COMMENT_OUTSIDE_CYCLE_OR_EDITED")
        text = result["content_text"]
        if not isinstance(text, str) or len(text) > MAX_BODY:
            return reject("INVALID_RESULT")
        lines = [line[len(PREFIX):] for line in text.splitlines()
                 if line.startswith(PREFIX)]
        if len(lines) != 1:
            return reject("MISSING_OR_AMBIGUOUS_STRUCTURED_RECEIPT")
        receipt = json.loads(lines[0])
        if not isinstance(receipt, dict) or _canonical(receipt) != lines[0]:
            return reject("NONCANONICAL_RECEIPT")
        verdict = receipt.get("verdict")
        expected = {
            "version": 1, "number": context.number, "head": context.head,
            "main": context.main, "policy_blob": context.policy_blob,
            "role": role, "run_id": run["id"], "author_run": context.author_run,
            "comment_id": comment["id"], "comment_sha256": sha256(body.encode()).hexdigest(),
            "verdict": verdict,
        }
        if receipt != expected or type(receipt.get("version")) is not int or type(receipt.get("number")) is not int or type(receipt.get("comment_id")) is not int:
            return reject("RECEIPT_CONTEXT_MISMATCH")
        if verdict not in ("FAVORABLE", "ADVERSE", "PARTIAL"):
            return reject("INVALID_VERDICT")
        return Correlation("CORRELATED_" + verdict, "SEMANTIC_REVIEW_STILL_REQUIRED")
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError):
        return reject("MALFORMED_EVIDENCE")
