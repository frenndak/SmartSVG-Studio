import unittest
from tools.smartsvg_controller_proof import parse_test_receipts, verify_workflow_pin

H, P, Q = "a"*40, "b"*40, "c"*40
A = "test_native.Flow.test_export"
B = "test_native.Flow.test_stale"

def row(name, status):
    return ("2026-11-25T05:07:31.9888558Z " + name.rsplit(".", 1)[-1]
            + " (" + name + ") ... " + status + "\r\n")

def parse(log, required=(A, B)):
    return parse_test_receipts(log, required, head=H, run_id=1, attempt=2, job_id=3)

class ProofTests(unittest.TestCase):
    def test_pin_drift_and_unknown(self):
        self.assertTrue(verify_workflow_pin(P, P, P).matched)
        self.assertEqual(verify_workflow_pin(P, Q, P).reason, "MAIN_WORKFLOW_DRIFT")
        self.assertEqual(verify_workflow_pin(P, P, Q).reason, "PR_WORKFLOW_DRIFT")
        self.assertFalse(verify_workflow_pin(None, P, P).matched)

    def test_verbose_results_and_digest(self):
        r = parse(row(A, "ok") + row(B, "ok") + "OK (skipped=12)")
        self.assertEqual([t.status for t in r.tests], ["PASS", "PASS"])
        self.assertEqual(r.tests[1].lines, (2,))
        self.assertEqual((r.head, r.run_id, r.attempt, r.job_id), (H, 1, 2, 3))
        self.assertEqual(len(r.digest), 64)
        self.assertEqual(r.qualification, "LOG_ONLY")

    def test_skipped_and_failed_are_not_pass(self):
        for status, expected in (("skipped 'no Tk'", "SKIP"), ("FAIL", "FAIL"),
                                 ("ERROR", "FAIL"), ("expected failure", "UNKNOWN")):
            self.assertEqual(parse(row(A, status)).tests[0].status, expected)

    def test_missing_duplicate_and_summary_not_proof(self):
        self.assertEqual([t.status for t in parse("Ran 100 tests\nOK").tests],
                         ["UNKNOWN", "UNKNOWN"])
        r = parse(row(A, "ok") + row(A, "ok") + row(B, "ok"))
        self.assertEqual(r.tests[0].status, "UNKNOWN")
        self.assertEqual(r.tests[0].lines, (1, 2))
        self.assertEqual(r.tests[1].status, "PASS")

    def test_similar_test_names_do_not_match(self):
        r = parse(row("other.Flow.test_export", "ok") + row(A + "_extra", "ok"))
        self.assertEqual(r.tests[0].status, "UNKNOWN")

    def test_invalid_provenance_and_identifiers(self):
        with self.assertRaises(ValueError):
            parse_test_receipts("", (A,), head="bad", run_id=1, attempt=1, job_id=1)
        with self.assertRaises(ValueError):
            parse("", (A, A))
        with self.assertRaises(ValueError):
            parse("", ())

    def test_docstring_two_line_result(self):
        header = row(A, "ok").replace(" ... ok", "")
        desc = "2026-11-25T05:07:32.0000000Z Both export controls follow state. ... ok\n"
        r = parse(header + desc + row(B, "ok"))
        self.assertEqual(r.tests[0].status, "PASS")
        self.assertEqual(r.tests[0].lines, (1,2))
        self.assertEqual(r.tests[1].lines, (3,))
        self.assertEqual(parse(header+desc.replace("... ok", "... skipped 'no Tk'")).tests[0].status,"SKIP")

    def test_docstring_missing_or_other_test_is_not_pass(self):
        header = row(A,"ok").replace(" ... ok","")
        self.assertEqual(parse(header+row(B,"ok")).tests[0].status,"UNKNOWN")
        self.assertEqual(parse(header+"unrelated output\n... ok\n").tests[0].status,"UNKNOWN")
        self.assertEqual(parse(header+row(A,"ok")).tests[0].status,"UNKNOWN")

    def test_docstring_duplicate_and_failure(self):
        header = row(A,"ok").replace(" ... ok","")
        desc = "Actual Tk transition. ... ok\n"
        self.assertEqual(parse(header+desc+header+desc).tests[0].status,"UNKNOWN")
        self.assertEqual(parse(header+desc.replace("... ok","... FAIL")).tests[0].status,"FAIL")
