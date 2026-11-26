"""R15 persistent recovery advice; never changes GitHub writer or merge authority."""
import re
import json
from hashlib import sha256
from .smartsvg_controller_shadow import Journal

DIGEST = re.compile(r"[0-9a-f]{64}")
OUTCOMES = frozenset(("PROGRESS", "NO_PROGRESS", "WAIT_CI", "WAIT_REVIEW", "EXTERNAL"))


def incident_key(project, repository, policy, kind, resource):
    """Stable incident scope, independent of transient HEAD/plan changes.

    Policy or project changes intentionally invalidate the history scope.
    Only technical identifiers are accepted; no error text, secrets or logs.
    This key is not a receipt, a permission or a qualified mission identity.
    """
    token = re.compile(r"[a-z0-9][a-z0-9._:-]{0,127}")
    repo = re.compile(r"[a-z0-9][a-z0-9._-]{0,127}/[a-z0-9][a-z0-9._-]{0,127}")
    if (any(not isinstance(v, str) or token.fullmatch(v) is None
            for v in (project, kind, resource))
            or not isinstance(repository, str) or repo.fullmatch(repository) is None
            or not isinstance(policy, str) or re.fullmatch(r"[0-9a-f]{40}", policy) is None):
        raise ValueError("invalid incident scope")
    return sha256(json.dumps([1, project, repository, policy, kind, resource],
                             separators=(",", ":")).encode()).hexdigest()


def _advice(rows):
    seen = set()
    streak = 0
    last = None
    for outcome, receipt in rows:
        last = outcome
        if outcome == "PROGRESS" and receipt not in seen:
            seen.add(receipt)
            streak = 0
        elif outcome in ("PROGRESS", "NO_PROGRESS"):
            streak += 1
        # A genuine wait neither increments nor resets an existing streak.
    if last in ("WAIT_CI", "WAIT_REVIEW"):
        return "OTHER_ACTIONABLE_WORK"
    if last == "EXTERNAL":
        return "ISOLATE_EXTERNAL_BLOCKER"
    if streak >= 3:
        return "PROPOSE_HANDOFF_REVIEW"
    if streak >= 2:
        return "CHANGE_STRATEGY"
    return "RESUME_CHECKPOINT"


class RecoveryJournal(Journal):
    def __init__(self, path, clock=None):
        if clock is None:
            super().__init__(path)
        else:
            super().__init__(path, clock)
        self.db.execute("""CREATE TABLE IF NOT EXISTS cycle(
            item TEXT NOT NULL, head TEXT NOT NULL, owner TEXT NOT NULL,
            run TEXT NOT NULL, ordinal INTEGER NOT NULL, outcome TEXT NOT NULL,
            receipt TEXT NOT NULL, PRIMARY KEY(item,head,owner,run),
            UNIQUE(item,head,owner,ordinal))""")
        # Local rehearsal history only: no cross-runner lease or scheduler proof.
        self.db.execute("""CREATE TABLE IF NOT EXISTS incident_cycle_v1(
            item TEXT NOT NULL, incident TEXT NOT NULL, owner TEXT NOT NULL,
            context TEXT NOT NULL, run TEXT NOT NULL, ordinal INTEGER NOT NULL,
            outcome TEXT NOT NULL, receipt TEXT NOT NULL,
            PRIMARY KEY(item,incident,owner,run),
            UNIQUE(item,incident,owner,ordinal))""")

    def renew(self, item, head, owner, fence, ttl=300):
        if type(ttl) is not int or not 1 <= ttl <= 3600:
            raise ValueError("invalid ttl")
        with self.transaction():
            now = self.clock()
            result = self.db.execute(
                "UPDATE work SET expires=? WHERE item=? AND head=? AND owner=? "
                "AND fence=? AND expires>?",
                (now + ttl, item, head, owner, fence, now))
            return result.rowcount == 1

    def record_cycle(self, item, head, owner, fence, *, run, ordinal, outcome, receipt=""):
        """Record ordered, externally verified observations, not agent prose.

        PROGRESS requires an evidence digest from a future verifier. Duplicate
        progress evidence is not new work. Waiting does not count as failure.
        """
        if (owner not in ("A", "B") or not isinstance(run, str) or not run
                or len(run) > 128 or type(ordinal) is not int or ordinal < 1
                or outcome not in OUTCOMES or not isinstance(receipt, str)
                or len(receipt) > 256):
            raise ValueError("invalid cycle")
        if outcome == "PROGRESS" and DIGEST.fullmatch(receipt) is None:
            raise ValueError("missing evidence digest")
        with self.transaction():
            lease = self.db.execute(
                "SELECT 1 FROM work WHERE item=? AND head=? AND owner=? AND fence=? AND expires>?",
                (item, head, owner, fence, self.clock())).fetchone()
            if not lease:
                return False
            key = (item, head, owner)
            existing = self.db.execute(
                "SELECT ordinal,outcome,receipt FROM cycle WHERE item=? AND head=? AND owner=? AND run=?",
                (*key, run)).fetchone()
            if existing:
                return existing == (ordinal, outcome, receipt)
            last = self.db.execute(
                "SELECT MAX(ordinal) FROM cycle WHERE item=? AND head=? AND owner=?", key).fetchone()[0]
            if last is not None and ordinal <= last:
                return False
            self.db.execute("INSERT INTO cycle VALUES(?,?,?,?,?,?,?)",
                            (*key, run, ordinal, outcome, receipt))
            return True

    def advise(self, item, head, owner):
        """Return an advisory action. No transfer or lease claim is performed."""
        rows = self.db.execute(
            "SELECT outcome,receipt FROM cycle WHERE item=? AND head=? AND owner=? ORDER BY ordinal",
            (item, head, owner)).fetchall()
        return _advice(rows)

    def record_incident_cycle(self, item, context, owner, fence, *, incident,
                              run, ordinal, outcome, receipt=""):
        """Record externally verified outcomes under a stable incident key.

        The active exact-context local lease is still required for every
        write. Old receipts can inform stagnation only, never requalify a
        new HEAD, transfer ownership, or authorize a GitHub mutation.
        Ordinals must be monotone per incident and role, across contexts.
        A caller must supply independently checked progress evidence; a
        syntactically valid digest alone does not authenticate its origin.
        """
        if (not isinstance(item, str) or not 1 <= len(item) <= 128
                or any(not isinstance(v, str) or DIGEST.fullmatch(v) is None
                       for v in (context, incident))
                or owner not in ("A", "B") or type(fence) is not int or fence < 1
                or not isinstance(run, str) or not 1 <= len(run) <= 128
                or type(ordinal) is not int or ordinal < 1
                or not isinstance(outcome, str) or outcome not in OUTCOMES
                or not isinstance(receipt, str)
                or (receipt != "" and DIGEST.fullmatch(receipt) is None)
                or (outcome == "PROGRESS" and not receipt)):
            raise ValueError("invalid incident cycle")
        with self.transaction():
            lease = self.db.execute(
                "SELECT 1 FROM work WHERE item=? AND head=? AND owner=? "
                "AND fence=? AND expires>?",
                (item, context, owner, fence, self.clock())).fetchone()
            if not lease:
                return False
            key = (item, incident, owner)
            existing = self.db.execute(
                "SELECT context,ordinal,outcome,receipt FROM incident_cycle_v1 "
                "WHERE item=? AND incident=? AND owner=? AND run=?",
                (*key, run)).fetchone()
            if existing:
                return existing == (context, ordinal, outcome, receipt)
            last = self.db.execute(
                "SELECT MAX(ordinal) FROM incident_cycle_v1 "
                "WHERE item=? AND incident=? AND owner=?", key).fetchone()[0]
            if last is not None and ordinal <= last:
                return False
            self.db.execute("INSERT INTO incident_cycle_v1 VALUES(?,?,?,?,?,?,?,?)",
                            (*key, context, run, ordinal, outcome, receipt))
            return True

    def advise_incident(self, item, incident, owner):
        """Continuity advice only; does not expose prior exact-context evidence."""
        if (not isinstance(incident, str) or DIGEST.fullmatch(incident) is None
                or owner not in ("A", "B")):
            raise ValueError("invalid incident identity")
        rows = self.db.execute(
            "SELECT outcome,receipt FROM incident_cycle_v1 "
            "WHERE item=? AND incident=? AND owner=? ORDER BY ordinal",
            (item, incident, owner)).fetchall()
        return _advice(rows)
