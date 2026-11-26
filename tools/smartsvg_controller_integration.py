"""Persistent R15 integration rehearsal journal. Never performs a merge.

Only synthetic rehearsal intents are accepted. An external, reviewed adapter
would be needed to use authenticated live evidence; this module deliberately
has no API mutation or permission to invoke one.
"""
from dataclasses import dataclass
import re
from .smartsvg_controller_storage import OperationalJournal
from .smartsvg_controller_preflight import IntegrationSubject, evaluate

SHA = re.compile(r"[0-9a-f]{40}")
DIGEST = re.compile(r"[0-9a-f]{64}")
TERMINAL = frozenset(("QUALIFIED_SIMULATION", "NOT_APPLIED"))


@dataclass(frozen=True)
class Intent:
    cycle: str
    number: int
    head: str
    main: str
    subject_digest: str


@dataclass(frozen=True)
class Observation:
    number: int
    head: str
    main: str
    pr_state: str
    merged: bool | None
    merge_sha: str | None
    merge_parent: str | None
    g0_sha: str | None
    g0_status: str
    source: str = "SYNTHETIC_REHEARSAL"


@dataclass(frozen=True)
class TerminalReceipt:
    cycle: str
    number: int
    head: str
    main: str
    subject_digest: str
    receipt_digest: str
    outcome: str = "REJECTED_BEFORE_APPLY"
    source: str = "SYNTHETIC_TERMINAL_EVENT"


@dataclass(frozen=True)
class Reconciliation:
    state: str
    action: str
    mutation_authorized: bool = False


class IntegrationJournal(OperationalJournal):
    """Local rehearsal of at-most-one attempt per cycle, globally unresolved."""
    def __init__(self, path, clock=None):
        super().__init__(path, clock)
        self.db.execute("""CREATE TABLE IF NOT EXISTS integration_rehearsal(
            cycle TEXT PRIMARY KEY, number INTEGER NOT NULL, head TEXT NOT NULL,
            main TEXT NOT NULL, subject TEXT NOT NULL, state TEXT NOT NULL,
            merge_sha TEXT, CHECK(number > 0))""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS integration_terminal_receipt(
            cycle TEXT PRIMARY KEY, receipt_digest TEXT NOT NULL)""")

    def prepare(self, subject, facts, *, role, now):
        """Derive intent from the subject and a freshly evaluated rehearsal.

        Facts are still synthetic/external inputs, not trusted production
        receipts. A caller cannot substitute an unrelated preflight or intent.
        """
        if not isinstance(subject, IntegrationSubject):
            return False
        preflight = evaluate(subject, facts, role=role, now=now)
        if (preflight.action != "SHADOW_PREFLIGHT_PASS"
                or preflight.merge_authorized is not False
                or len(subject.executor_cycle) > 256):
            return False
        intent = Intent(subject.executor_cycle, subject.number, subject.head,
                        subject.main, preflight.subject_digest)
        with self.transaction():
            if self.db.execute("SELECT 1 FROM integration_rehearsal WHERE cycle=?",
                               (intent.cycle,)).fetchone():
                return False
            if self.db.execute("SELECT 1 FROM integration_rehearsal WHERE state NOT IN (?,?)",
                               tuple(sorted(TERMINAL))).fetchone():
                return False
            self.db.execute("INSERT INTO integration_rehearsal VALUES(?,?,?,?,?,?,NULL)",
                            (intent.cycle,intent.number,intent.head,intent.main,
                             intent.subject_digest,"PREPARED"))
            return True

    def mark_attempt(self, cycle):
        """Record the synthetic dispatch boundary before any simulated response."""
        with self.transaction():
            return self.db.execute(
                "UPDATE integration_rehearsal SET state='AMBIGUOUS' WHERE cycle=? AND state='PREPARED'",
                (cycle,)).rowcount == 1

    def cancel_prepared(self, cycle, *, role):
        """Atomic cancellation only before the synthetic dispatch boundary."""
        if role != "B":
            return False
        with self.transaction():
            return self.db.execute(
                "UPDATE integration_rehearsal SET state='NOT_APPLIED' WHERE cycle=? AND state='PREPARED'",
                (cycle,)).rowcount == 1

    def resolve_negative(self, cycle, observation, terminal_receipt, *, role):
        """Rehearse a separately proved terminal rejection, never infer it.

        The receipt is a simulator input, not an actual server-side guarantee.
        Both the matching negative readback and explicit terminal evidence
        must be present; timeout/404/unchanged branch alone cannot release it.
        """
        if role != "B" or not isinstance(terminal_receipt, TerminalReceipt):
            return False
        with self.transaction():
            row = self.db.execute(
                "SELECT number,head,main,subject,state,merge_sha FROM integration_rehearsal WHERE cycle=?",
                (cycle,)).fetchone()
            if row is None:
                return False
            number,head,main,subject,state,known_sha = row
            if (state != "NEGATIVE_READBACK" or known_sha is not None
                    or terminal_receipt.source != "SYNTHETIC_TERMINAL_EVENT"
                    or terminal_receipt.outcome != "REJECTED_BEFORE_APPLY"
                    or (terminal_receipt.cycle,terminal_receipt.number,terminal_receipt.head,
                        terminal_receipt.main,terminal_receipt.subject_digest) !=
                       (cycle,number,head,main,subject)
                    or not isinstance(terminal_receipt.receipt_digest,str)
                    or DIGEST.fullmatch(terminal_receipt.receipt_digest) is None
                    or observation.source != "SYNTHETIC_REHEARSAL"
                    or type(observation.number) is not int or observation.number != number
                    or observation.head != head or observation.main != main
                    or observation.pr_state != "open" or observation.merged is not False
                    or observation.merge_sha is not None or observation.merge_parent is not None):
                return False
            # Preserve the terminal event receipt alongside the outcome.
            self.db.execute("INSERT INTO integration_terminal_receipt VALUES(?,?)",
                            (cycle,terminal_receipt.receipt_digest))
            self.db.execute("UPDATE integration_rehearsal SET state='NOT_APPLIED' WHERE cycle=?",
                            (cycle,))
            return True

    def status(self, cycle):
        row = self.db.execute(
            "SELECT state,merge_sha FROM integration_rehearsal WHERE cycle=?", (cycle,)).fetchone()
        return tuple(row) if row else None

    def reconcile(self, cycle, observation):
        """Resolve from readback, not from a transport response or retry.

        NOT_APPLIED requires explicit negative evidence and a stable main.
        An observed external main advance is isolated, never reset blindly.
        A failed G0 remains blocked for reviewed repair; no automatic revert.
        """
        with self.transaction():
            row = self.db.execute(
                "SELECT number,head,main,state,merge_sha FROM integration_rehearsal WHERE cycle=?",
                (cycle,)).fetchone()
            if row is None:
                return Reconciliation("UNKNOWN","INSPECT")
            number,head,main,state,known_sha = row
            if state in TERMINAL:
                return Reconciliation(state,"NO_REPEAT")
            if state == "PREPARED":
                return Reconciliation(state,"REHEARSAL_NOT_DISPATCHED")
            if (observation.source != "SYNTHETIC_REHEARSAL" or
                    type(observation.number) is not int or observation.number != number
                    or observation.head != head or not isinstance(observation.main,str)
                    or SHA.fullmatch(observation.main) is None):
                return Reconciliation(state,"READBACK_REQUIRED")
            merge_sha = known_sha
            if (observation.merged is True and observation.pr_state == "closed"
                    and isinstance(observation.merge_sha,str)
                    and SHA.fullmatch(observation.merge_sha) is not None
                    and observation.merge_sha != main
                    and observation.merge_parent == main
                    and (known_sha is None or known_sha == observation.merge_sha)):
                merge_sha = observation.merge_sha
                if observation.main != merge_sha:
                    new, action = "MAIN_DRIFT","REQUALIFY_MAIN"
                elif observation.g0_sha != merge_sha:
                    new, action = "WAIT_G0","OBSERVE_EXACT_MAIN_G0"
                elif observation.g0_status == "PASS":
                    new, action = "QUALIFIED_SIMULATION","NO_REPEAT"
                elif observation.g0_status == "FAIL":
                    new, action = "G0_FAILED","REVIEW_REPAIR_OR_REVERT"
                else:
                    new, action = "WAIT_G0","OBSERVE_EXACT_MAIN_G0"
            elif (state in ("AMBIGUOUS", "NEGATIVE_READBACK") and known_sha is None
                    and observation.pr_state == "open" and observation.merged is False
                    and observation.merge_sha is None and observation.main == main):
                # A negative readback is not proof that an in-flight request
                # cannot apply later. Hold globally; require separate resolution.
                new, action = "NEGATIVE_READBACK","VERIFY_REQUEST_TERMINALITY"
            else:
                return Reconciliation(state,"READBACK_REQUIRED")
            self.db.execute("UPDATE integration_rehearsal SET state=?,merge_sha=? WHERE cycle=?",
                            (new,merge_sha,cycle))
            return Reconciliation(new,action)
