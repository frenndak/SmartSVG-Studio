import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from tools.smartsvg_controller_objectives import Profile, Objective
from tools.smartsvg_controller_missions import MissionJournal, MissionError

M, P, R, H, J = (c * 40 for c in "abcde")
PROFILE = Profile("smartsvg", "frenndak/SmartSVG-Studio", "main", P, R)
OBJECTIVE = Objective("mission-one", H, "A", ("proof",))
E = "a"*64


class MissionJournalTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / "missions.sqlite"
        self.j = MissionJournal(self.path)
        self.addCleanup(self.j.close)
        self.first = self.j.create(PROFILE, OBJECTIVE, M)

    def advance(self, prev, **changes):
        kw = dict(expected_generation=prev.generation, expected_digest=prev.digest,
                  main=prev.main, revision=prev.objective.revision,
                  role=prev.objective.role, state="ACTIVE", next_action="IMPLEMENT",
                  evidence=E)
        kw.update(changes)
        return self.j.advance(PROFILE, OBJECTIVE.key, **kw)

    def test_create_and_resume_after_reopen(self):
        a = self.advance(self.first)
        b = self.advance(a, state="REVIEW", next_action="CROSS_REVIEW", evidence="b"*64)
        other = MissionJournal(self.path)
        try:
            self.assertEqual(other.latest(PROFILE, OBJECTIVE.key), b)
            self.assertEqual(other.history(PROFILE, OBJECTIVE.key), (self.first,a,b))
            self.assertEqual(b.predecessor, a.digest)
            self.assertEqual(b.qualification, "LOCAL_ADVISORY_ONLY")
        finally:
            other.close()

    def test_stale_cas_and_wrong_context_do_not_write(self):
        a = self.advance(self.first)
        self.assertIsNone(self.advance(self.first))
        for kw in (dict(main=J),dict(revision=J),dict(role="B"),
                   dict(expected_generation=True),dict(expected_digest="b"*64)):
            self.assertIsNone(self.advance(a, **kw))
        self.assertEqual(self.j.latest(PROFILE,OBJECTIVE.key),a)

    def test_context_change_invalidates_evidence_but_preserves_history(self):
        a = self.advance(self.first)
        changed = replace(OBJECTIVE, revision=J)
        b = self.j.recontextualize(PROFILE, changed, M,
             expected_generation=a.generation, expected_digest=a.digest)
        self.assertEqual(b.state,"PLANNED")
        self.assertEqual(b.evidence,"")
        self.assertEqual(self.j.history(PROFILE,OBJECTIVE.key),(self.first,a,b))
        self.assertIsNone(self.advance(a,state="REVIEW",evidence="b"*64))
        with self.assertRaises(MissionError):
            self.advance(b,evidence=E)
        self.assertIsNotNone(self.advance(b,evidence="b"*64))

    def test_main_drift_requires_new_checkpoint(self):
        a = self.advance(self.first)
        b = self.j.recontextualize(PROFILE,OBJECTIVE,J,
             expected_generation=a.generation,expected_digest=a.digest)
        self.assertEqual((b.main,b.state,b.evidence),(J,"PLANNED",""))

    def test_project_policy_and_roadmap_are_isolated(self):
        for p in (replace(PROFILE,project="other"),replace(PROFILE,repository="other/repo"),
                  replace(PROFILE,policy_blob=J),replace(PROFILE,roadmap_blob=J)):
            self.assertIsNone(self.j.latest(p,OBJECTIVE.key))
            c = self.j.create(p,OBJECTIVE,M)
            self.assertNotEqual(c.digest,self.first.digest)
        self.assertEqual(self.j.latest(PROFILE,OBJECTIVE.key),self.first)

    def test_writer_or_acceptance_contract_cannot_change_in_place(self):
        for o in (replace(OBJECTIVE,role="B"),replace(OBJECTIVE,criteria=("new",)),
                  replace(OBJECTIVE,dependencies=("dep",)),
                  replace(OBJECTIVE,preparation_allowed=True)):
            with self.assertRaises(MissionError):
                self.j.recontextualize(PROFILE,o,J,expected_generation=1,
                                       expected_digest=self.first.digest)
        self.assertEqual(self.j.latest(PROFILE,OBJECTIVE.key),self.first)

    def test_no_unqualified_done_or_integration(self):
        for state in ("VERIFIED","INTEGRATED","DONE","REVIEW"):
            with self.assertRaises(MissionError):
                self.advance(self.first,state=state)
        with self.assertRaises(MissionError):
            self.advance(self.first,evidence="raw error")
        self.assertEqual(self.j.latest(PROFILE,OBJECTIVE.key),self.first)

    def test_duplicate_evidence_cannot_create_new_progress(self):
        a = self.advance(self.first)
        with self.assertRaises(MissionError):
            self.advance(a)
        self.assertEqual(self.j.latest(PROFILE,OBJECTIVE.key),a)

    def test_wait_and_cancel_are_local_to_one_mission(self):
        a = self.advance(self.first,state="WAITING")
        b = self.advance(a,state="CANCELLED",evidence="b"*64)
        with self.assertRaises(MissionError):
            self.advance(b,evidence="c"*64)
        o = replace(OBJECTIVE,key="independent")
        c = self.j.create(PROFILE,o,M)
        self.assertEqual(c.state,"PLANNED")
        self.assertEqual(self.j.latest(PROFILE,OBJECTIVE.key),b)

    def test_tampered_history_is_not_reused(self):
        self.advance(self.first)
        self.j.db.execute("UPDATE mission_checkpoint_v1 SET raw=? WHERE generation=1",
                          (b"corrupt",))
        with self.assertRaises(MissionError):
            self.j.latest(PROFILE,OBJECTIVE.key)

    def test_competing_exact_cas_has_single_winner(self):
        barrier = Barrier(2)
        def worker(digest):
            other = MissionJournal(self.path)
            try:
                barrier.wait(timeout=5)
                return other.advance(PROFILE,OBJECTIVE.key,expected_generation=1,
                    expected_digest=self.first.digest,main=M,revision=H,role="A",
                    state="ACTIVE",next_action="IMPLEMENT",evidence=digest)
            finally:
                other.close()
        with ThreadPoolExecutor(max_workers=2) as pool:
            result = list(pool.map(worker,("b"*64,"c"*64)))
        self.assertEqual(sum(x is not None for x in result),1)
        self.assertEqual(self.j.latest(PROFILE,OBJECTIVE.key).generation,2)

    def test_duplicate_mission_and_unchanged_context_rejected(self):
        with self.assertRaises(MissionError):
            self.j.create(PROFILE,OBJECTIVE,M)
        with self.assertRaises(MissionError):
            self.j.recontextualize(PROFILE,OBJECTIVE,M,expected_generation=1,
                                   expected_digest=self.first.digest)
