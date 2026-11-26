"""Read-only recovery planner linking the durable journal to live reconciliation.

The report is shadow advice. It never dispatches, writes the journal, retries
a merge or grants authority. A prepared intent must be requalified before use.
"""
from .smartsvg_controller_cas import decode, _ref, TERMINAL
from .smartsvg_controller_live_reconcile import Subject, reconcile_live
from .smartsvg_controller_observation import POLICY
from .smartsvg_controller_successor import observe_successor

ACTIONS = {
    "MERGED_G0_PASS": "OBSERVE_COMPLETED_INTEGRATION",
    "G0_FAILED": "REVIEW_REPAIR_OR_REVERT",
    "WAIT_G0": "WAIT_EXACT_MAIN_G0",
    "MAIN_DRIFT": "REQUALIFY_CURRENT_MAIN",
    "NEGATIVE_READBACK": "VERIFY_REQUEST_TERMINALITY",
    "UNKNOWN": "INSPECT_READBACK",
}


def recover(read, get):
    """Inspect a stable journal snapshot, preserving independent work.

    The supplied read callable must validate the pinned journal history.
    A changed journal discards the entire observation. The original policy
    blob is checked at its immutable main commit, not guessed from today.
    """
    report = {
        "journal_ref": None, "generation": None, "intent": None,
        "journal_state": None, "observation": None, "successor": None,
        "action": "INSPECT_JOURNAL", "qualification": "SHADOW_ONLY",
        "merge_authorized": False, "retry_authorized": False,
        "independent_work_blocked": False,
    }
    try:
        ref, raw = read()
        _ref(ref)
        record = decode(raw)
        report.update(journal_ref=ref, generation=record.generation,
                      intent=record.intent, journal_state=record.state)
        if record.state == "IDLE" or record.state in TERMINAL:
            report["action"] = "NO_PENDING_INTENT"
        elif record.state == "PREPARED":
            report["action"] = "REQUALIFY_PREPARED_INTENT"
        else:
            policy = get(f"/contents/{POLICY}?ref={record.main}")
            if policy.get("sha") != record.policy:
                report["action"] = "INSPECT_POLICY_MISMATCH"
            else:
                subject = Subject(record.number, record.head, record.main, record.tree)
                result = reconcile_live(get, subject)
                report["observation"] = result
                report["action"] = ACTIONS.get(result["state"], "INSPECT_READBACK")
                if result["state"] == "MAIN_DRIFT" and result.get("merge_sha"):
                    report["successor"] = observe_successor(get, subject, result)
        if read() != (ref, raw):
            report.update(action="JOURNAL_DRIFT", observation=None, successor=None)
    except Exception as exc:
        # Type only: never expose a token, URL or server response body.
        report.update(action="INSPECT_JOURNAL_OR_READBACK", observation=None, successor=None,
                      error=type(exc).__name__)
    return report
