"""G2.7 browser-free UI regression gate for local cut contour selection."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "engine"

class CutReviewG27Tests(unittest.TestCase):
    def test_local_svg_cut_review_node(self):
        node = shutil.which("node")
        if node is None:
            self.skipTest("Node.js is unavailable")
        process = subprocess.run(
            [node, "--test", str(ENGINE / "tests" / "test_g27_cut_review.mjs")],
            cwd=ROOT, text=True, capture_output=True, timeout=50,
        )
        self.assertEqual(process.returncode, 0,
                         process.stdout[-10000:] + process.stderr[-5000:])

    def test_reviewer_wired_into_existing_express_without_queue_or_auto_cut(self):
        project=(ENGINE/"web/js/smartsvg_project_panel_g22.mjs").read_text(encoding="utf-8")
        review=(ENGINE/"web/js/smartsvg_cut_review_panel_g27.mjs").read_text(encoding="utf-8")
        model=(ENGINE/"web/js/smartsvg_cut_review_model_g27.mjs").read_text(encoding="utf-8")
        self.assertIn("createCutReviewPanel(ownerId)", project)
        self.assertIn("inspectCutSvg(text)", review)
        self.assertIn("selectedSvg(review", review)
        self.assertNotIn("innerHTML", review)
        self.assertNotIn("queuePrompt", review)
        self.assertNotIn("fetchApi", review)
        self.assertNotIn("eval(", model)

if __name__ == "__main__":
    unittest.main()
