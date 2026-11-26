"""R15 shadow decisions: pure, read-only, never an authorization to merge."""
from dataclasses import dataclass
from enum import Enum
import re

_SHA = re.compile(r"[0-9a-f]{40}")
REQUIRED = frozenset(("g0", "preflight", "cpu", "windows_python", "strict_v1_tk_cpu"))

class Status(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    PENDING = "PENDING"
    UNKNOWN = "UNKNOWN"

@dataclass(frozen=True)
class Check:
    name: str
    head: str
    status: Status
    executed: bool
    receipt: str

@dataclass(frozen=True)
class Review:
    head: str
    main: str
    reviewer: str
    later_cycle: bool
    favorable: bool
    receipt: str

@dataclass(frozen=True)
class Candidate:
    number: int
    head: str
    writer: str
    code_only: bool
    same_repo: bool
    authorized_author: bool
    draft: bool
    mergeable: bool | None
    unresolved: bool | None
    checks: tuple[Check, ...] = ()
    review: Review | None = None

@dataclass(frozen=True)
class Context:
    main: str
    policy_blob: str
    authority_verified: bool
    scheduler_verified: bool
    rules_verified: bool
    required_approval_satisfied: bool
    main_g0: Status
    main_g0_sha: str
    observation_complete: bool

@dataclass(frozen=True)
class Decision:
    action: str
    reasons: tuple[str, ...] = ()

def _sha(value):
    return isinstance(value, str) and _SHA.fullmatch(value) is not None

def decide(context: Context, candidate: Candidate) -> Decision:
    """Conservative shadow classifier. No network, mutations, or approval claims.

    Context is supplied by a future verified adapter, not inferred from prose.
    Main changes invalidate review context here; an explicit requalification
    adapter can later establish a new review-context receipt without re-review.
    """
    def result(action, *reasons):
        return Decision(action, reasons)

    if candidate.code_only is False:
        return result("OWNER_REVIEW", "OUTSIDE_CODE_SCOPE")
    if not (context.observation_complete is True and
            all(_sha(s) for s in (context.main, context.policy_blob, candidate.head)) and
            candidate.writer in ("A", "B") and
            candidate.code_only is True and candidate.same_repo is True and
            candidate.authorized_author is True):
        return result("INSPECT", "INCOMPLETE_OR_UNVERIFIED_IDENTITY")
    if candidate.unresolved is True:
        return result("FIX_REQUIRED", "UNRESOLVED_FINDING")
    by_name = {}
    for check in candidate.checks:
        if check.head != candidate.head or check.name not in REQUIRED:
            continue
        if check.name in by_name:
            return result("INSPECT", "AMBIGUOUS_CHECK:" + check.name)
        by_name[check.name] = check
    failed = sorted(k for k, v in by_name.items() if v.status is Status.FAIL)
    if failed:
        return result("FIX_REQUIRED", *failed)
    review = candidate.review
    if (review is not None and review.head == candidate.head and
            review.main == context.main and review.reviewer in ("A", "B") and
            review.reviewer != candidate.writer and review.later_cycle is True and
            review.receipt and review.favorable is False):
        return result("FIX_REQUIRED", "ADVERSE_REVIEW")
    valid_review = (review is not None and review.head == candidate.head and
                    review.main == context.main and review.reviewer in ("A", "B") and
                    review.reviewer != candidate.writer and review.later_cycle is True and
                    review.favorable is True and bool(review.receipt))
    if not valid_review:
        return result("REVIEW", "MISSING_EXACT_CONTEXT_CROSS_REVIEW")
    missing = sorted(k for k in REQUIRED if k not in by_name or
                     by_name[k].status is not Status.PASS or
                     by_name[k].executed is not True or not by_name[k].receipt)
    if missing:
        return result("CI_REQUIRED", *missing)
    if candidate.mergeable is False:
        return result("RECONCILE", "MERGE_CONFLICT_OR_REFUSAL")
    reasons = []
    for name, value in (
        ("AUTHORITY", context.authority_verified),
        ("SCHEDULER", context.scheduler_verified),
        ("RULES", context.rules_verified),
        ("REQUIRED_APPROVAL", context.required_approval_satisfied),
        ("MERGEABILITY", candidate.mergeable),
        ("NO_UNRESOLVED_FINDINGS", candidate.unresolved is False),
        ("NON_DRAFT", candidate.draft is False),
        ("EXACT_MAIN_G0", context.main_g0 is Status.PASS and
         context.main_g0_sha == context.main),
    ):
        if value is not True:
            reasons.append(name)
    if reasons:
        return result("NO_MERGE", *reasons)
    return result("SHADOW_QUALIFIED", "NOT_AUTHORIZATION")

def choose_work(decisions: tuple[tuple[int, Decision], ...], code_wip: int):
    """Prioritize repair/review over waiting, independently of gate availability."""
    if type(code_wip) is not int or code_wip < 0:
        raise ValueError("invalid WIP")
    priority = {"FIX_REQUIRED": 0, "RECONCILE": 1, "REVIEW": 2,
                "SHADOW_QUALIFIED": 3, "INSPECT": 4}
    actionable = [(priority[d.action], n, d) for n, d in decisions
                  if d.action in priority]
    if actionable:
        _, n, d = min(actionable, key=lambda v: (v[0], v[1]))
        return n, d.action
    return None, "DEVELOP" if code_wip < 3 else "CHECKPOINT_WAIT"
