"""R15 experimental local shadow journal. No GitHub writes or merge authority."""
import sqlite3
import time
from contextlib import contextmanager

class Journal:
    def __init__(self, path, clock=time.time):
        self.clock = clock
        self.db = sqlite3.connect(path, isolation_level=None, timeout=5)
        self.db.execute("PRAGMA busy_timeout=5000")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS work(
          item TEXT PRIMARY KEY, head TEXT NOT NULL, owner TEXT NOT NULL,
          fence INTEGER NOT NULL, expires REAL NOT NULL, checkpoint TEXT NOT NULL
        );
        """)
    @contextmanager
    def transaction(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
    def close(self):
        self.db.close()
    def claim(self, item, head, owner, ttl=300):
        """Return a new fencing token, or None if already leased."""
        if not all(isinstance(v, str) and v for v in (item, head, owner)):
            raise ValueError("missing identity")
        if type(ttl) is not int or not 1 <= ttl <= 3600:
            raise ValueError("invalid ttl")
        with self.transaction():
            now = self.clock()
            row = self.db.execute(
                "SELECT head,fence,expires,checkpoint FROM work WHERE item=?", (item,)
            ).fetchone()
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
    def save(self, item, head, owner, fence, checkpoint):
        """Reject expired, replaced or wrong-HEAD writers atomically."""
        if not isinstance(checkpoint, str) or len(checkpoint) > 65536:
            raise ValueError("invalid checkpoint")
        with self.transaction():
            result = self.db.execute(
                "UPDATE work SET checkpoint=? WHERE item=? AND head=? AND owner=? "
                "AND fence=? AND expires>?",
                (checkpoint, item, head, owner, fence, self.clock()))
            return result.rowcount == 1
    def release(self, item, head, owner, fence):
        with self.transaction():
            result = self.db.execute(
                "UPDATE work SET expires=0 WHERE item=? AND head=? AND owner=? "
                "AND fence=? AND expires>?",
                (item, head, owner, fence, self.clock()))
            return result.rowcount == 1
    def checkpoint(self, item, head):
        row = self.db.execute(
            "SELECT checkpoint FROM work WHERE item=? AND head=?", (item, head)
        ).fetchone()
        return row[0] if row else None
