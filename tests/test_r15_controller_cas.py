import unittest
from dataclasses import replace
from tools.smartsvg_controller_cas import (
    Record, encode, decode, prepare, transition, persist)

A, B, C, D = (c * 40 for c in "abcd")
E = "e" * 64


class CASTests(unittest.TestCase):
    def setUp(self):
        self.initial = Record()
        self.prepared = prepare(self.initial, number=196, head=A, main=B,
                                tree=C, policy=D, evidence=E)
        self.ref, self.raw = A, encode(self.initial)
        self.stages = 0
        self.advances = 0

    def read(self):
        return self.ref, self.raw

    def stage(self, parent, raw):
        self.assertEqual(parent, A)
        self.stages += 1
        self.pending = raw
        return B

    def advance(self, expected, candidate):
        self.advances += 1
        self.assertEqual((expected, candidate), (A, B))
        self.ref, self.raw = B, self.pending

    def write(self, advance=None, read=None):
        result = persist(read or self.read, self.stage, advance or self.advance,
                         expected=A, previous=self.initial, proposed=self.prepared)
        self.assertFalse(result.merge_authorized)
        self.assertFalse(result.retry_authorized)
        return result

    def test_restart_roundtrip(self):
        self.assertEqual(self.write().state, "APPLIED")
        self.assertEqual(decode(self.read()[1]), self.prepared)
        self.assertEqual(self.write().state, "STALE")
        self.assertEqual((self.stages, self.advances), (1, 1))

    def test_lost_success_response(self):
        def advance(expected, candidate):
            self.advance(expected, candidate)
            raise TimeoutError()
        self.assertEqual(self.write(advance).state, "APPLIED")
        self.assertEqual(self.advances, 1)

    def test_unchanged_ref_after_timeout_is_ambiguous(self):
        def timeout(*args):
            raise TimeoutError()
        self.assertEqual(self.write(timeout).state, "AMBIGUOUS")
        self.assertEqual(self.stages, 1)

    def test_competing_ref_preserved(self):
        def conflict(*args):
            self.ref = C
            self.raw = encode(replace(self.prepared, number=197))
            raise RuntimeError()
        self.assertEqual(self.write(conflict).state, "CONFLICT")
        self.assertEqual(decode(self.raw).number, 197)

    def test_exact_candidate_wrong_bytes_is_ambiguous(self):
        def wrong(*args):
            self.ref = B
        self.assertEqual(self.write(wrong).state, "AMBIGUOUS")

    def test_read_failure_no_write(self):
        def unavailable():
            raise OSError()
        self.assertEqual(self.write(read=unavailable).state, "READ_UNAVAILABLE")
        self.assertEqual(self.stages, 0)

    def test_negative_does_not_release_intent(self):
        attempted = transition(self.prepared, "DISPATCH_UNKNOWN", E)
        negative = transition(attempted, "NEGATIVE_READBACK", E)
        with self.assertRaises(ValueError):
            transition(negative, "CANCELLED_PREPARED", E)
        with self.assertRaises(ValueError):
            prepare(negative, number=197, head=A, main=B, tree=C, policy=D, evidence=E)
        qualified = transition(negative, "QUALIFIED_READBACK", E)
        nxt = prepare(qualified, number=197, head=A, main=B, tree=C, policy=D, evidence=E)
        self.assertEqual((nxt.intent, nxt.generation), (2, 5))

    def test_pre_dispatch_cancel(self):
        cancelled = transition(self.prepared, "CANCELLED_PREPARED", E)
        with self.assertRaises(ValueError):
            transition(cancelled, "DISPATCH_UNKNOWN", E)

    def test_context_mutation_and_noncanonical_bytes(self):
        with self.assertRaises(ValueError):
            persist(self.read, self.stage, self.advance, expected=A,
                    previous=self.initial, proposed=replace(self.prepared, generation=99))
        with self.assertRaises(ValueError):
            decode(encode(self.prepared) + b" ")
        with self.assertRaises(ValueError):
            decode(encode(self.initial).replace(b'"version":1', b'"version":2'))
        self.assertEqual(self.stages, 0)
