import unittest
from tools.smartsvg_controller_roadmap import roadmap_advice, explicit_lot, PATH, PIN

M="a"*40


class RoadmapPriorityTests(unittest.TestCase):
    def snapshot(self):
        return {"main":{"commit":{"sha":M}},"candidates":[
            {"pr":{"number":192,"title":"feat(v3.5 W05): SD0","head":{"ref":"b/w05-sd0"}}},
            {"pr":{"number":194,"title":"test(v3.5 W04): export","head":{"ref":"b/w04-export"}}},
            {"pr":{"number":195,"title":"feat(v3.5 W04): Atelier","head":{"ref":"a/w04-atelier"}}}]}

    def test_current_queue_order_matches_reviewed_master(self):
        def get(path):
            self.assertEqual(path,f"/contents/{PATH}?ref={M}")
            return {"sha":PIN}
        ranks,report=roadmap_advice(self.snapshot(),get)
        self.assertEqual(ranks,{192:4,194:3,195:3})
        self.assertEqual(report["qualification"],"ADVISORY_ONLY")
        self.assertEqual(report["source_blob"],PIN)

    def test_document_drift_and_read_failure_fall_back(self):
        ranks,report=roadmap_advice(self.snapshot(),lambda p:{"sha":"b"*40})
        self.assertEqual(ranks,{})
        self.assertEqual(report["status"],"ROADMAP_CHANGED")
        def unavailable(p):
            raise OSError("unavailable")
        self.assertEqual(roadmap_advice(self.snapshot(),unavailable)[0],{})

    def test_conflicting_multiple_transverse_or_missing_lot_unranked(self):
        for title,ref in (("W04","b/w05"),("W04 W05","b/w04"),
                          ("W13","a/w13"),("W04","a/export"),("W040","b/w04")):
            self.assertIsNone(explicit_lot({"title":title,"head":{"ref":ref}}))
