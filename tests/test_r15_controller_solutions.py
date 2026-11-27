import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from tools.smartsvg_controller_objectives import Profile
from tools.smartsvg_controller_solutions import Solution, SolutionMemory

PROFILE = Profile("smartsvg","frenndak/SmartSVG-Studio","main","a"*40,"b"*40)
INCIDENT, COMPAT, RECEIPT = (c*64 for c in "cde")
SOLUTION = Solution(PROFILE, INCIDENT, "pr:195", "truncated-read", "transport-failure",
                    "RETRY_READ_ALTERNATE", COMPAT, "f"*40, RECEIPT,
                    ("alternate-read-supported",), ("write-result-unknown",))


class SolutionMemoryTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name)/"solutions.sqlite"
        self.m = SolutionMemory(self.path)
        self.addCleanup(self.m.close)

    def hints(self, **kwargs):
        args = dict(profile=PROFILE, incident=INCIDENT, resource="pr:195",
                    compatibility=COMPAT, known_present=("alternate-read-supported",),
                    known_absent=("write-result-unknown",), verify=lambda s: True)
        args.update(kwargs)
        return self.m.hints(**args)

    def test_validated_solution_reopens_as_advice_not_authority(self):
        digest=self.m.store(SOLUTION)
        self.assertEqual(self.m.store(SOLUTION),digest)
        other=SolutionMemory(self.path)
        try:
            hints=other.hints(PROFILE,INCIDENT,"pr:195",COMPAT,
                             known_present=("alternate-read-supported",),
                             known_absent=("write-result-unknown",),verify=lambda s: True)
            self.assertEqual(len(hints),1)
            self.assertEqual(hints[0].solution_digest,digest)
            self.assertEqual(hints[0].qualification,"REVALIDATE_ADVISORY_ONLY")
            self.assertFalse(hints[0].merge_authorized)
            self.assertFalse(hints[0].agent_work_executed)
        finally:
            other.close()

    def test_unknown_prerequisite_or_contraindication_is_not_compatible(self):
        self.m.store(SOLUTION)
        self.assertEqual(self.hints(known_present=()),())
        self.assertEqual(self.hints(known_absent=()),())
        self.assertEqual(self.hints(known_present=("alternate-read-supported","write-result-unknown"),
                                    known_absent=()),())
        with self.assertRaises(ValueError):
            self.hints(known_present=("alternate-read-supported","write-result-unknown"))

    def test_verifier_must_revalidate_and_return_literal_true(self):
        self.m.store(SOLUTION)
        for value in (False,None,1,"PASS"):
            self.assertEqual(self.hints(verify=lambda s: value),())
        def unavailable(s):
            raise OSError("private error")
        self.assertEqual(self.hints(verify=unavailable),())

    def test_incompatible_project_policy_roadmap_resource_or_revision_signature(self):
        self.m.store(SOLUTION)
        for profile in (replace(PROFILE,project="second"),
                        replace(PROFILE,repository="sample/second"),
                        replace(PROFILE,policy_blob="c"*40),
                        replace(PROFILE,roadmap_blob="c"*40),
                        replace(PROFILE,branch="other")):
            self.assertEqual(self.hints(profile=profile),())
        self.assertEqual(self.hints(incident="f"*64),())
        self.assertEqual(self.hints(resource="pr:196"),())
        self.assertEqual(self.hints(compatibility="f"*64),())

    def test_validation_receipt_cannot_be_relabeled(self):
        self.m.store(SOLUTION)
        with self.assertRaises(ValueError):
            self.m.store(replace(SOLUTION,strategy="RECONCILE_STATE"))
        self.assertEqual(len(self.hints()),1)

    def test_alternative_solutions_are_separately_revalidated(self):
        self.m.store(SOLUTION)
        other=replace(SOLUTION,strategy="INSPECT_INDEPENDENT",validation_digest="f"*64)
        self.m.store(other)
        self.assertEqual(len(self.hints()),2)
        result=self.hints(verify=lambda s: s.strategy=="INSPECT_INDEPENDENT")
        self.assertEqual([h.strategy for h in result],["INSPECT_INDEPENDENT"])

    def test_invalid_strategy_raw_data_and_conflicting_conditions_rejected(self):
        for s in (replace(SOLUTION,strategy="MERGE"),
                  replace(SOLUTION,strategy="RETRY_UNKNOWN_WRITE"),
                  replace(SOLUTION,diagnosis="raw HTTP response with secret"),
                  replace(SOLUTION,validation_digest="raw"),
                  replace(SOLUTION,prerequisites=("write-result-unknown",)),
                  replace(SOLUTION,prerequisites=("z","a"))):
            with self.subTest(s=s), self.assertRaises(ValueError):
                self.m.store(s)
        self.assertEqual(self.hints(),())

    def test_corrupted_blob_or_index_is_not_reused(self):
        digest=self.m.store(SOLUTION)
        self.m.db.execute("UPDATE solution_v1 SET validation=? WHERE digest=?",("f"*64,digest))
        with self.assertRaises(ValueError):
            self.hints()
        self.m.db.execute("UPDATE solution_v1 SET validation=?,raw=? WHERE digest=?",
                          (RECEIPT,b"corrupted",digest))
        with self.assertRaises(ValueError):
            self.hints()

    def test_bounded_history_rejects_without_overwriting_old_solution(self):
        with patch("tools.smartsvg_controller_solutions.MAX_HISTORY",1):
            digest=self.m.store(SOLUTION)
            with self.assertRaises(ValueError):
                self.m.store(replace(SOLUTION,validation_digest="f"*64))
            self.assertEqual(self.hints()[0].solution_digest,digest)
