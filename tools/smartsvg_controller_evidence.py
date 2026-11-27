"""R15 shadow step receipts and role-aware dispatch; no mutation or authorization."""
from dataclasses import dataclass
from .smartsvg_controller_decision import Status

# Observed workflow paths and exact step names, not proof of trusted workflow
# contents. Any contract drift must be reviewed rather than fuzzy-matched.
STABILITY = ".github/workflows/stability-qualification.yml"
WINDOWS = "Windows Python 3.11 full regression (no skip of known failures)"
SPECS = {
    "g0": (".github/workflows/g0-admission-tests.yml", "admission",
           "Verify and test admission gate"),
    "preflight": (".github/workflows/public-readonly-preflight.yml", "free-preflight",
                  "Verify exact checkout, immutable baseline and regression tests"),
    "cpu": (".github/workflows/engine-cpu-smoke.yml", "live-engine-cpu",
            "Qualify real G3.3e Subject brush CPU tests (no skips)"),
    "windows_python": (STABILITY, WINDOWS,
                       "Full Python suite on native Windows (with brush CPU dependencies)"),
    "strict_v1_tk_cpu": (STABILITY, WINDOWS,
                         "Strict native V1 to Tk to CPU regression (no skips)"),
}


@dataclass(frozen=True)
class StepReceipt:
    name: str
    status: Status
    run_id: int | None = None
    attempt: int | None = None
    job_id: int | None = None
    step_number: int | None = None
    reason: str = ""
    # A successful step is not proof of no relevant unittest skips,
    # exact checkout content, or reviewed workflow provenance.
    qualification: str = "STEP_ONLY"


def _positive_int(value):
    return type(value) is int and value > 0


def _status(obj):
    if obj.get("status") in ("queued", "in_progress", "waiting", "requested", "pending"):
        return Status.PENDING
    if obj.get("status") != "completed":
        return Status.UNKNOWN
    return {"success": Status.PASS, "failure": Status.FAIL,
            "timed_out": Status.FAIL, "skipped": Status.SKIP,
            "cancelled": Status.UNKNOWN}.get(obj.get("conclusion"), Status.UNKNOWN)


def step_receipts(head, runs, *, event="pull_request"):
    """Normalize exact-head, exact-attempt receipts, rejecting ambiguous matches."""
    out = []
    for name, (path, job_name, step_name) in SPECS.items():
        def missing(reason):
            return StepReceipt(name, Status.UNKNOWN, reason=reason)
        matches = [x for x in runs if x["run"].get("path") == path
                   and x["run"].get("head_sha") == head
                   and x["run"].get("event") == event]
        if len(matches) != 1:
            out.append(missing("MISSING_OR_MULTIPLE_RUNS"))
            continue
        entry = matches[0]
        run = entry["run"]
        rid, attempt = run.get("id"), run.get("run_attempt")
        if not _positive_int(rid) or not _positive_int(attempt):
            out.append(missing("INVALID_RUN_IDENTITY"))
            continue
        if _status(run) is not Status.PASS:
            out.append(StepReceipt(name, _status(run), rid, attempt,
                                   reason="RUN_NOT_SUCCESS"))
            continue
        jobs = [j for j in entry["jobs"] if j.get("name") == job_name]
        if len(jobs) != 1:
            out.append(missing("MISSING_OR_MULTIPLE_JOBS"))
            continue
        job = jobs[0]
        jid = job.get("id")
        if (not _positive_int(jid) or job.get("head_sha") != head
                or not _positive_int(job.get("run_id")) or job["run_id"] != rid
                or not _positive_int(job.get("run_attempt")) or job["run_attempt"] != attempt):
            out.append(missing("JOB_PROVENANCE_MISMATCH"))
            continue
        if _status(job) is not Status.PASS:
            out.append(StepReceipt(name, _status(job), rid, attempt, jid,
                                   reason="JOB_NOT_SUCCESS"))
            continue
        steps = [s for s in job.get("steps", ()) if s.get("name") == step_name]
        if len(steps) != 1 or not _positive_int(steps[0].get("number")):
            out.append(missing("MISSING_OR_MULTIPLE_STEPS"))
            continue
        step = steps[0]
        out.append(StepReceipt(name, _status(step), rid, attempt, jid,
                               step["number"], "EXACT_STEP"))
    return tuple(out)


def only_waiting_on_ci(steps):
    """Recognize a complete inventory where every outstanding check is pending."""
    if len(steps) != len(SPECS) or {step.name for step in steps} != SPECS.keys():
        return False
    return (any(step.status is Status.PENDING for step in steps)
            and all(step.status in (Status.PASS, Status.PENDING)
                    and _positive_int(step.run_id) and _positive_int(step.attempt)
                    for step in steps))


@dataclass(frozen=True)
class Work:
    number: int
    writer: str
    action: str
    # False for work currently reserved by a different live worker.
    available: bool = True
    roadmap_rank: int | None = None
    only_waiting_on_ci: bool = False


def dispatch(role, work, code_wip, *, queue_complete=False):
    """Propose a next action only; never claim a lease or change GitHub."""
    if role not in ("A", "B") or type(code_wip) is not int or code_wip < 0:
        raise ValueError("invalid role or WIP")
    eligible = []
    for w in work:
        if w.available is not True or w.writer not in ("A", "B"):
            continue
        other = w.writer != role
        rank = None
        if w.action == "REVIEW" and other:
            rank = 0
        elif w.action in ("FIX_REQUIRED", "RECONCILE") and not other:
            rank = 1
        elif w.action == "VERIFY_FINDING" and not other:
            rank = 1
        elif w.action in ("SHADOW_QUALIFIED", "QUALIFY_ONLY") and role == "B":
            rank = 2
        elif w.action == "CI_INSPECT":
            # CI inspection is read-only and does not qualify a review or merge.
            # A can inspect B-owned work instead of idling when B is unavailable.
            # Mutating repairs and B-only qualification retain their own gates.
            rank = 5 if w.only_waiting_on_ci else 3
        elif w.action == "INSPECT":
            rank = 4
        if rank is not None:
            # Roadmap only breaks ties within the existing action class.
            lot_rank = w.roadmap_rank if type(w.roadmap_rank) is int and w.roadmap_rank > 0 else 100
            eligible.append((rank, lot_rank, w.number, w.action))
    if eligible:
        _, _, number, action = min(eligible)
        return number, "QUALIFY_ONLY" if action == "SHADOW_QUALIFIED" else action
    if queue_complete is True and code_wip < 3:
        return None, "DEVELOP"
    return None, "CHECKPOINT_WAIT"
