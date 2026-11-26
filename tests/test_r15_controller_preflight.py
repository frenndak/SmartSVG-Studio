import unittest
from dataclasses import asdict, replace
from datetime import datetime, timedelta, timezone

from tools.smartsvg_controller_preflight import (
    IntegrationSubject, Fact, GATES, evaluate, requirements, _digest)

NOW = datetime(2026, 11, 25, 18, 0, tzinfo=timezone.utc)
S = IntegrationSubject(195,"a"*40,"b"*40,"c"*40,"A","writer","later",
                       "d"*64,("engine/native_atelier.py","tests/test_native.py"),
                       False,True,("test_native.Flow.test_export",))

def facts(s=S):
    names = GATES | {"ci:"+x for x in requirements(s)} | {"test:"+t for t in s.targeted_tests}
    return tuple(Fact(n,_digest(asdict(s)),"PASS","EXTERNALLY_VERIFIED","e"*64,NOW)
                 for n in sorted(names))

def run(s=S, fs=None, role="B"):
    return evaluate(s, facts(s) if fs is None else fs, role=role, now=NOW)


class IntegrationPreflightTests(unittest.TestCase):
    def test_pass_is_never_authority(self):
        r=run()
        self.assertEqual(r.action,"SHADOW_PREFLIGHT_PASS")
        self.assertFalse(r.merge_authorized)
        self.assertIn("FRESH_RECHECK_REQUIRED",r.reasons)

    def test_cpu_applicability_and_test_only(self):
        self.assertIn("cpu", requirements(S))
        s=replace(S, paths=("tests/test_native.py",),windows_relevant=True)
        self.assertNotIn("cpu",requirements(s))
        self.assertIn("windows_python",requirements(s))
        self.assertEqual(run(s).action,"SHADOW_PREFLIGHT_PASS")
        self.assertIn("cpu",requirements(replace(s,cpu_relevant=True)))

    def test_required_test_missing_or_skipped(self):
        f=tuple(x for x in facts() if not x.name.startswith("test:"))
        self.assertEqual(run(fs=f).action,"EVIDENCE_REQUIRED")
        f=tuple(replace(x,status="SKIP") if x.name.startswith("test:") else x for x in facts())
        self.assertEqual(run(fs=f).action,"EVIDENCE_REQUIRED")
        self.assertTrue(any(x.endswith(":SKIP") for x in run(fs=f).reasons))

    def test_raw_step_and_ambiguous_receipts(self):
        f=facts()
        raw=tuple(replace(x,qualification="STEP_ONLY") if x.name=="ci:g0" else x for x in f)
        self.assertEqual(run(fs=raw).action,"EVIDENCE_REQUIRED")
        self.assertEqual(run(fs=f+(f[0],)).action,"INSPECT")

    def test_main_head_policy_diff_and_cycle_changes_invalidate(self):
        for s in (replace(S,main="f"*40),replace(S,head="f"*40),
                  replace(S,policy_blob="f"*40),replace(S,diff_digest="f"*64),
                  replace(S,executor_cycle="new-cycle")):
            self.assertEqual(run(s,facts()).action,"EVIDENCE_REQUIRED")

    def test_role_same_cycle_and_excluded_paths(self):
        self.assertEqual(run(role="A").action,"NO_MERGE")
        self.assertEqual(run(replace(S,executor_cycle=S.author_cycle)).action,"NO_MERGE")
        for path in ("docs/policy.md","tools/verify_source_integrity.py","engine/../docs/a"):
            self.assertEqual(run(replace(S,paths=(path,))).action,"OWNER_REVIEW")

    def test_stale_future_and_failed_gate(self):
        for delta in (timedelta(minutes=-6),timedelta(seconds=1)):
            f=tuple(replace(x,observed_at=NOW+delta) if x.name=="main_g0" else x for x in facts())
            self.assertEqual(run(fs=f).action,"EVIDENCE_REQUIRED")
        for name in ("main_g0","cycle_budget","external_approval","threads_clear"):
            f=tuple(replace(x,status="FAIL") if x.name==name else x for x in facts())
            self.assertEqual(run(fs=f).action,"BLOCKED")
            self.assertFalse(run(fs=f).merge_authorized)

    def test_empty_targeted_tests_refused(self):
        self.assertEqual(run(replace(S,targeted_tests=())).action,"INSPECT")
