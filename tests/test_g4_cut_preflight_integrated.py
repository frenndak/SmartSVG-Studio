"""Verify that G4 Basic Cut safeguards are actually present in the G1/G2 stack.

CPU-only, stdlib fixtures avoid mistaking unavailable cv2/Pillow/ComfyUI for
a passing full runtime test. Actual image QA remains a separate runtime gate.
"""
import sys
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ENGINE = Path(__file__).resolve().parents[1] / "engine"
sys.path.insert(0, str(ENGINE))
from smartsvg_governance.cut_path_preflight import inspect_cut_paths, CutPathError


def root(paths):
    return ET.fromstring('<svg xmlns="http://www.w3.org/2000/svg" '
                         'width="40mm" height="20mm" viewBox="0 0 40 20">'
                         + paths + '</svg>')


class CutPreflightIntegratedTests(unittest.TestCase):
    def test_real_subject_outline_requires_human_review(self):
        svg = root('<path d="M1 1 L10 1 L10 10 Z"/>')
        report = inspect_cut_paths(svg)
        self.assertEqual(report["path_elements"], 1)
        self.assertTrue(report["closed_paths_checked"])
        self.assertFalse(report["nonpolygonal_paths_require_visual_review"])

    def test_rejects_empty_open_collinear_hidden_active_and_external(self):
        candidates = [
            '<path d="M1 1 L10 1 L10 10"/>',
            '<path d="M1 1 L10 1 Z"/>',
            '<path d="M1 1 L5 5 L10 10 Z"/>',
            '<path d="M1 1 L10 1 L10 10 Z" transform="scale(2)"/>',
            '<path d="M1 1 L10 1 L10 10 Z" onclick="alert(1)"/>',
            '<image href="https://invalid.example/x.png"/>',
            '<path d=""/>',
            '<rect x="1" y="1" width="10" height="10"/>',
        ]
        for markup in candidates:
            with self.subTest(markup=markup):
                with self.assertRaises(CutPathError):
                    inspect_cut_paths(root(markup))

    def test_curve_is_only_review_candidate_never_physically_certified(self):
        report = inspect_cut_paths(root('<path d="M1 1 C1 5 5 10 10 1 Z"/>'))
        self.assertTrue(report["nonpolygonal_paths_require_visual_review"])
        self.assertNotIn("physical_cut_verified", report)

    def test_malformed_curve_commands_never_pass_basic_cut_preflight(self):
        invalid = [
            'M0 0 C1 2 3 4 Z', 'M0 0 C1 2 3 4 5 Z',
            'M0 0 Q1 2 3 Z', 'M0 0 S1 2 3 Z',
            'M0 0 T1 Z', 'M0 0 H Z', 'M0 0 V Z',
            'M0 0 A2 2 0 0 1 10 Z',
            'M0 0 A2 2 0 2 0 10 10 Z',
            'M0 0 A2 2 0 0 -1 10 10 Z',
            'C1 2 3 4 5 6 M0 0 Z',
            'M0 0 C1 2 3 4 5 6 7 Z',
            'M0 0 L10 0 L10 10 Z 4 5',
            'M0 0 C1 2 3 4 5 6 M0 0 Z Z',
            'M0 0 C1 2 3 4 5 6 Z Z M0 0 Z',
        ]
        for data in invalid:
            with self.subTest(data=data), self.assertRaises(CutPathError):
                inspect_cut_paths(root('<path d="'+data+'"/>'))

    def test_svg_numbers_and_separators_are_ascii_and_not_ambiguous_commas(self):
        invalid = ['M٠ ٠ L١٠ ٠ L١٠ ١٠ Z',
                   'M0 0\u00a0L10 0 L10 10 Z',
                   ',M0 0 L10 0 L10 10 Z',
                   'M0 0,,L10 0 L10 10 Z',
                   'M0 0 L,10 0 L10 10 Z']
        for data in invalid:
            with self.subTest(data=data), self.assertRaises(CutPathError):
                inspect_cut_paths(root('<path d="'+data+'"/>'))

    def test_complete_curves_and_compact_arc_flags_remain_review_candidates(self):
        valid = [
            'M0 0 C0 10 10 10 10 0 Z',
            'm0 0 c0 10 10 10 10 0 s10 -10 20 0 z',
            'M0 0 Q5 10 10 0 T20 0 Z',
            'M0 0 H10 V10 h-10 v-10 Z',
            'M0 0 A5 5 0 0 1 10 10 Z',
            'M0 0 A5 5 0 0110 10 Z',
            'M0 0 A5 5 0 01.5.5 Z',
            'M0 0 C0 10 10 10 10 0 10 -10 20 -10 20 0 Z',
        ]
        for data in valid:
            with self.subTest(data=data):
                svg=root('<path d="'+data+'"/>')
                before=ET.tostring(svg)
                report=inspect_cut_paths(svg)
                self.assertTrue(report['closed_paths_checked'])
                self.assertTrue(report['nonpolygonal_paths_require_visual_review'])
                self.assertEqual(ET.tostring(svg),before)
                self.assertNotIn('physical_cut_verified',report)

    def test_live_quality_gate_is_connected_to_this_preflight(self):
        artifact = (ENGINE / "smartsvg_governance/artifact_qa.py").read_text()
        gate = (ENGINE / "smartsvg_quality/release_gate_v21152.py").read_text()
        self.assertIn("from .cut_path_preflight import inspect_cut_paths", artifact)
        self.assertIn("checked=inspect_cut_paths(root)", artifact)
        self.assertIn("audit_project(project/", gate)


if __name__ == "__main__":
    unittest.main()
