"""R15.2 atomic local import of externally verified cycle outcomes.

An independent connector-native verifier must establish the actual run,
material artifact and context before calling this adapter. A digest or a
narrative result alone cannot establish provenance. The local lease is not
a scheduler identity, distributed lock, or GitHub mutation authorization.
"""
from dataclasses import dataclass
from hashlib import sha256

from .smartsvg_controller_evidence import Work, dispatch
from .smartsvg_controller_orchestration import (
    Plan, Proposal, Reservation, _context, routing_incident,
)
from .smartsvg_controller_recovery import DIGEST, OUTCOMES
from .smartsvg_controller_storage import Evidence, OperationalJournal, _encode


@dataclass(frozen=True)
class CycleObservation:
    context_key: str
    incident_key: str
    role: str
    run_digest: str
    ordinal: int
    outcome: str
    source_digest: str
    material_digest: str = ""


def _digest(value):
    return isinstance(value, str) and DIGEST.fullmatch(value) is not None


def _validate_observation(observation):
    if type(observation) is not CycleObservation:
        raise ValueError("invalid cycle observation")
    o = observation
    if (not all(_digest(v) for v in (o.context_key,o.incident_key,o.run_digest))
            or o.role not in ("A","B") or type(o.ordinal) is not int
            or not 1 <= o.ordinal <= 2**63-1
            or not isinstance(o.outcome, str) or o.outcome not in OUTCOMES
            or not _digest(o.source_digest) or not isinstance(o.material_digest, str)
            or (o.outcome == "PROGRESS" and not _digest(o.material_digest))
            or (o.outcome != "PROGRESS" and o.material_digest != "")):
        raise ValueError("invalid observed outcome")
    return o


def _cycle_evidence(plan, proposal, o, context, incident, owner, number):
    payload = {
        "version": 1, "role": owner, "writer": proposal.writer,
        "action": proposal.action, "context_key": context, "incident_key": incident,
        "run_digest": o.run_digest, "ordinal": o.ordinal, "outcome": o.outcome,
        "source_digest": o.source_digest, "material_digest": o.material_digest,
        "qualification": "EXTERNAL_OBSERVATION_IMPORTED_ONLY",
    }
    evidence = Evidence(number,proposal.head,plan.main,plan.policy_blob,
                        "CYCLE_OUTCOME","external-cycle-observer",payload)
    raw = _encode(evidence)
    return raw, sha256(raw).hexdigest()


@dataclass(frozen=True)
class CycleReadback:
    status: str
    evidence_digest: str | None = None
    qualification: str = "LOCAL_READBACK_ONLY"


def read_imported_cycle(journal, plan, proposal, observation):
    """Reconcile an uncertain import from one consistent SQLite read.

    No active lease, clock or write is needed to confirm historical local
    bytes. This is not proof of scheduler provenance or current authority.
    Never infer success from a single ledger or retry an uncertain write.
    """
    if (not isinstance(journal, OperationalJournal) or type(plan) is not Plan
            or type(proposal) is not Proposal):
        raise ValueError("invalid cycle readback input")
    o = _validate_observation(observation)
    if proposal not in plan.proposals:
        return CycleReadback("CONTEXT_MISMATCH")
    number, action = dispatch(o.role, (Work(proposal.number, proposal.writer,
                                            proposal.action),), plan.code_wip)
    context = _context(plan, proposal)
    incident = routing_incident(plan, proposal)
    if (number != proposal.number or not action
            or (o.context_key, o.incident_key) != (context, incident)):
        return CycleReadback("CONTEXT_MISMATCH")
    item = "pr:" + str(number)
    receipt = o.material_digest if o.outcome == "PROGRESS" else o.source_digest
    raw, digest = _cycle_evidence(plan, proposal, o, context, incident, o.role, number)
    # One SELECT gives a consistent view of the exact row, stable row, link,
    # and complete evidence index/raw bytes even during a concurrent commit.
    row = journal.db.execute("""
        SELECT c.ordinal,c.outcome,c.receipt,
               s.context,s.ordinal,s.outcome,s.receipt,
               l.context,l.source,l.evidence_digest,
               e.number,e.head,e.main,e.policy,e.kind,e.raw
        FROM (SELECT 1) anchor
        LEFT JOIN cycle c ON c.item=? AND c.head=? AND c.owner=? AND c.run=?
        LEFT JOIN incident_cycle_v1 s
            ON s.item=? AND s.incident=? AND s.owner=? AND s.run=?
        LEFT JOIN cycle_import_v1 l
            ON l.item=? AND l.incident=? AND l.owner=? AND l.run=?
        LEFT JOIN evidence e ON e.digest=?
        """, (item,context,o.role,o.run_digest,
              item,incident,o.role,o.run_digest,
              item,incident,o.role,o.run_digest,digest)).fetchone()
    expected = (o.ordinal,o.outcome,receipt,
                context,o.ordinal,o.outcome,receipt,
                context,o.source_digest,digest,
                number,proposal.head,plan.main,plan.policy_blob,"CYCLE_OUTCOME",raw)
    if row == expected:
        return CycleReadback("MATCHED", digest)
    if all(value is None for value in row):
        return CycleReadback("ABSENT")
    return CycleReadback("CONFLICT")


def ingest_cycle(journal, plan, proposal, reservation, observation):
    """Bind one observed outcome per actual run/incident to both ledgers.

    Return the exact-context stored evidence digest, or None on stale CAS,
    mismatched reservation or a conflicting prior observation. All three
    writes are atomic. The caller aggregates multiple actions on this
    incident in one real scheduler invocation; it cannot increment the
    stagnation counter several times by changing the action summary.
    """
    if (not isinstance(journal, OperationalJournal) or type(plan) is not Plan
            or type(proposal) is not Proposal or type(reservation) is not Reservation
            or type(observation) is not CycleObservation):
        raise ValueError("invalid cycle adapter input")
    o = _validate_observation(observation)
    if proposal not in plan.proposals or reservation.owner not in ("A","B"):
        return None
    number, action = dispatch(reservation.owner,
        (Work(proposal.number, proposal.writer, proposal.action),), plan.code_wip)
    context = _context(plan, proposal)
    incident = routing_incident(plan, proposal)
    if (number != proposal.number or action != reservation.action
            or reservation.number != proposal.number or reservation.head != proposal.head
            or reservation.context_key != context
            or (o.context_key,o.incident_key,o.role) != (context,incident,reservation.owner)
            or type(reservation.fence) is not int
            or not 1 <= reservation.fence <= 2**63-1):
        return None
    item = "pr:" + str(number)
    owner = reservation.owner
    # Use the stable material fingerprint for PROGRESS, not the new cycle's
    # receipt digest: repeated evidence must not reset the incident streak.
    receipt = o.material_digest if o.outcome == "PROGRESS" else o.source_digest
    raw, digest = _cycle_evidence(plan, proposal, o, context, incident, owner, number)
    key = (item, context, owner)
    stable_key = (item, incident, owner)
    exact_value = (o.ordinal, o.outcome, receipt)
    stable_value = (context, o.ordinal, o.outcome, receipt)
    with journal.transaction():
        lease = journal.db.execute(
            "SELECT 1 FROM work WHERE item=? AND head=? AND owner=? "
            "AND fence=? AND expires>?",
            (*key,reservation.fence,journal.clock())).fetchone()
        if not lease:
            return None
        exact = journal.db.execute(
            "SELECT ordinal,outcome,receipt FROM cycle WHERE item=? AND head=? "
            "AND owner=? AND run=?", (*key,o.run_digest)).fetchone()
        stable = journal.db.execute(
            "SELECT context,ordinal,outcome,receipt FROM incident_cycle_v1 "
            "WHERE item=? AND incident=? AND owner=? AND run=?",
            (*stable_key,o.run_digest)).fetchone()
        stored = journal.db.execute("SELECT raw FROM evidence WHERE digest=?",
                                    (digest,)).fetchone()
        link = journal.db.execute(
            "SELECT context,source,evidence_digest FROM cycle_import_v1 "
            "WHERE item=? AND incident=? AND owner=? AND run=?",
            (*stable_key,o.run_digest)).fetchone()
        if exact is not None or stable is not None or link is not None:
            # Never fill a partially written legacy ledger by assuming that
            # it came from this observation. Reconcile it separately.
            return digest if (exact==exact_value and stable==stable_value
                              and link==(context,o.source_digest,digest)
                              and stored==(raw,)) else None
        if journal.db.execute(
                "SELECT 1 FROM cycle_import_v1 WHERE item=? AND incident=? "
                "AND owner=? AND source=?", (*stable_key,o.source_digest)).fetchone():
            return None
        exact_last = journal.db.execute(
            "SELECT MAX(ordinal) FROM cycle WHERE item=? AND head=? AND owner=?",
            key).fetchone()[0]
        stable_last = journal.db.execute(
            "SELECT MAX(ordinal) FROM incident_cycle_v1 WHERE item=? AND incident=? AND owner=?",
            stable_key).fetchone()[0]
        if any(last is not None and o.ordinal <= last for last in (exact_last,stable_last)):
            return None
        journal.db.execute("INSERT INTO cycle VALUES(?,?,?,?,?,?,?)",
                           (*key,o.run_digest,*exact_value))
        journal.db.execute("INSERT INTO incident_cycle_v1 VALUES(?,?,?,?,?,?,?,?)",
                           (*stable_key,context,
                            o.run_digest,o.ordinal,o.outcome,receipt))
        journal.db.execute("INSERT INTO cycle_import_v1 VALUES(?,?,?,?,?,?,?)",
                           (*stable_key,o.run_digest,context,o.source_digest,digest))
        journal.db.execute("INSERT OR IGNORE INTO evidence VALUES(?,?,?,?,?,?,?)",
                           (digest,number,proposal.head,plan.main,plan.policy_blob,
                            "CYCLE_OUTCOME",raw))
        stored = journal.db.execute("SELECT raw FROM evidence WHERE digest=?",
                                    (digest,)).fetchone()
        if stored != (raw,):
            raise ValueError("cycle evidence identity collision")
        return digest
