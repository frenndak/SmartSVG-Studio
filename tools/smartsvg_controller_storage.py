"""Operational shadow storage; local evidence is not a merge authorization."""
from dataclasses import dataclass
from hashlib import sha256
import json
import math
import re
from .smartsvg_controller_recovery import RecoveryJournal

SHA = re.compile(r"[0-9a-f]{40}")
KEY = re.compile(r"[0-9a-f]{64}")
KINDS = frozenset(("STEP_ONLY", "LOG_ONLY", "REVIEW_CORRELATION", "SCOPE_OBSERVATION"))
MAX_PAYLOAD = 65536


@dataclass(frozen=True)
class Evidence:
    number: int
    head: str
    main: str
    policy_blob: str
    kind: str
    source: str
    payload: dict


def _encode(e):
    if (type(e.number) is not int or e.number < 1
            or any(not isinstance(s, str) or SHA.fullmatch(s) is None
                   for s in (e.head, e.main, e.policy_blob))
            or e.kind not in KINDS
            or not isinstance(e.source, str) or not 1 <= len(e.source) <= 512
            or not isinstance(e.payload, dict)):
        raise ValueError("invalid evidence context")
    # Evidence metadata only. Do not store credentials, raw logs or source files.
    def validate(value, depth=0):
        if depth > 8:
            raise ValueError("evidence nesting too deep")
        if isinstance(value, dict):
            for k, v in value.items():
                if not isinstance(k, str):
                    raise ValueError("non-string evidence key")
                validate(v, depth + 1)
        elif isinstance(value, list):
            for v in value:
                validate(v, depth + 1)
        elif value is not None and type(value) not in (str, int, float, bool):
            raise ValueError("non-JSON evidence value")
    validate(e.payload)
    raw = json.dumps([e.number, e.head, e.main, e.policy_blob, e.kind,
                      e.source, e.payload], sort_keys=True, separators=(",", ":"),
                     ensure_ascii=True, allow_nan=False).encode()
    if len(raw) > MAX_PAYLOAD:
        raise ValueError("evidence metadata too large")
    return raw


class OperationalJournal(RecoveryJournal):
    """Dedicated operational shadow DB. All workers must use this class.

    SQLite serializes competing claims. An active lease is never revoked by
    a different HEAD or new plan; wait for release/expiry. These are local
    advisory leases, not GitHub branch locks or distributed permissions.
    """
    def __init__(self, path, clock=None):
        super().__init__(path, clock)
        self.db.execute("""CREATE TABLE IF NOT EXISTS evidence(
            digest TEXT PRIMARY KEY, number INTEGER NOT NULL,
            head TEXT NOT NULL, main TEXT NOT NULL, policy TEXT NOT NULL,
            kind TEXT NOT NULL, raw BLOB NOT NULL)""")
        self.db.execute("""CREATE INDEX IF NOT EXISTS evidence_context
            ON evidence(number,head,main,policy,kind)""")

    def claim(self, item, head, owner, ttl=300):
        if (owner not in ("A", "B") or not isinstance(item, str) or not item
                or not isinstance(head, str) or KEY.fullmatch(head) is None
                or type(ttl) is not int or not 1 <= ttl <= 3600):
            raise ValueError("invalid operational lease")
        with self.transaction():
            now = self.clock()
            if not math.isfinite(now) or now <= 0:
                raise ValueError("invalid clock")
            if self.db.execute("SELECT 1 FROM work WHERE owner=? AND expires>?",
                               (owner, now)).fetchone():
                return None
            row = self.db.execute(
                "SELECT head,fence,expires,checkpoint FROM work WHERE item=?",
                (item,)).fetchone()
            if row and row[2] > now:
                return None
            fence = row[1] + 1 if row else 1
            checkpoint = row[3] if row and row[0] == head else ""
            self.db.execute(
                "INSERT INTO work VALUES(?,?,?,?,?,?) ON CONFLICT(item) DO UPDATE SET "
                "head=excluded.head,owner=excluded.owner,fence=excluded.fence,"
                "expires=excluded.expires,checkpoint=excluded.checkpoint",
                (item, head, owner, fence, now + ttl, checkpoint))
            return fence

    def store_evidence(self, evidence):
        raw = _encode(evidence)
        digest = sha256(raw).hexdigest()
        with self.transaction():
            self.db.execute("INSERT OR IGNORE INTO evidence VALUES(?,?,?,?,?,?,?)",
                            (digest, evidence.number, evidence.head, evidence.main,
                             evidence.policy_blob, evidence.kind, raw))
            stored = self.db.execute("SELECT raw FROM evidence WHERE digest=?",
                                     (digest,)).fetchone()[0]
            if stored != raw:
                raise ValueError("evidence identity collision")
        return digest

    def evidence_for(self, number, head, main, policy, kind):
        """Return exact-context evidence, never promote to a qualified verdict."""
        rows = self.db.execute(
            "SELECT digest,raw FROM evidence WHERE number=? AND head=? AND main=? "
            "AND policy=? AND kind=? ORDER BY digest",
            (number, head, main, policy, kind)).fetchall()
        result = []
        for digest, raw in rows:
            if sha256(raw).hexdigest() != digest:
                raise ValueError("evidence digest mismatch")
            n, h, m, p, k, source, payload = json.loads(raw)
            if (n, h, m, p, k) != (number, head, main, policy, kind):
                raise ValueError("evidence context mismatch")
            result.append((digest, Evidence(n, h, m, p, k, source, payload)))
        return tuple(result)
