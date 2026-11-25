"""Persistent R15 integration rehearsal journal. Never performs a merge.

Only synthetic rehearsal intents are accepted. An external, reviewed adapter
would be needed to use authenticated live evidence; this module deliberately
has no API mutation or permission to invoke one.
"""
from dataclasses import dataclass
import re
from .smartsvg_controller_storage import OperationalJournal

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

    def prepare(self, intent, preflight, *, role):
        if (role != "B" or type(intent.number) is not int or intent.number < 1
                or not isinstance(intent.cycle, str) or not 1 <= len(intent.cycle) <= 256
                or any(not isinstance(v, str) or SHA.fullmatch(v) is None
                       for v in (intent.head, intent.main))
                or not isinstance(intent.subject_digest, str)
                or DIGEST.fullmatch(intent.subject_digest) is None
                or preflight.action != "SHADOW_PREFLIGHT_PASS"
                or preflight.subject_digest != intent.subject_digest
                or preflight.merge_authorized is not False):
            return False
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
            elif (state == "AMBIGUOUS" and known_sha is None
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
