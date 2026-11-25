"""Historical reduced real-queue replay, not live qualification."""
from datetime import datetime
import json
from pathlib import Path
import unittest

from tools.smartsvg_controller_cli import simulate

FIXTURE = Path(__file__).with_name("fixtures") / "r15_queue_replay_20261125.json"


class QueueReplayTests(unittest.TestCase):
    def setUp(self):
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.snapshot = data["snapshot"]
        self.manifest = data["manifest"]
        self.now = datetime.fromisoformat(self.snapshot["finished_at"])

    def replay(self):
        return simulate(self.snapshot, self.manifest, now=self.now)

    def test_observed_queue_and_missing_cpu_step(self):
        r = self.replay()
        self.assertEqual(r["code_wip"], 3)
        self.assertTrue(r["queue_complete"])
        self.assertEqual(r["assignments"]["A"]["number"], 192)
        self.assertEqual(r["assignments"]["B"]["number"], 195)
        by_number = {x["number"]: x for x in r["candidates"]}
        for n in (192, 195):
            self.assertEqual(by_number[n]["action"], "REVIEW")
            self.assertEqual({s["status"] for s in by_number[n]["steps"]}, {"PASS"})
        self.assertEqual(by_number[194]["action"], "REVIEW")
        self.assertEqual({s["name"]: s["status"] for s in by_number[194]["steps"]}["cpu"], "UNKNOWN")
        self.assertEqual(by_number[196]["action"], "OWNER_REVIEW")
        self.assertFalse(r["merge_authorized"])
        self.assertFalse(r["persistent_writes"])
        self.assertEqual(r["review_verification"], "NOT_QUALIFIED")

    def test_divergent_governance_does_not_free_slot_or_stop_product(self):
        row = next(x for x in self.snapshot["candidates"] if x["pr"]["number"] == 196)
        row["branch"] = {"status": "DIVERGED", "sha": "f" * 40}
        r = self.replay()
        self.assertEqual(r["unknown"], (196,))
        self.assertFalse(r["queue_complete"])
        self.assertEqual(r["code_wip"], 4)
        self.assertEqual(r["assignments"]["A"]["number"], 192)
        self.assertEqual(r["assignments"]["B"]["number"], 195)
        self.assertFalse(r["merge_authorized"])

    def test_divergent_product_routes_to_next_candidate(self):
        row = next(x for x in self.snapshot["candidates"] if x["pr"]["number"] == 192)
        row["branch"] = {"status": "DIVERGED", "sha": "f" * 40}
        r = self.replay()
        self.assertEqual(r["unknown"], (192,))
        self.assertEqual(r["assignments"]["A"]["number"], 194)
        self.assertEqual(r["assignments"]["B"]["number"], 195)
        self.assertFalse(r["merge_authorized"])
