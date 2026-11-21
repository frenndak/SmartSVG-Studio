"""Focused W03 Atelier native PTC GUI admission regressions."""
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))
from native_ptc_atelier_tk_v35 import ptc_preview_request


class PTCAtelierAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = SimpleNamespace(sha256="a" * 64)
        self.subject = SimpleNamespace(subject_id="subject-" + "b" * 32,
                                       proof_status="verified")
        self.path = str(Path.cwd().resolve() / "synthetic.smartsvg")

    def request(self, width="50,25"):
        return ptc_preview_request(self.snapshot, self.subject, self.path, width)

    def test_french_decimal_and_pinned_identity(self):
        self.assertEqual(self.request(), {
            "project_path": self.path,
            "expected_sha256": "a" * 64,
            "subject_id": "subject-" + "b" * 32,
            "width_mm": 50.25,
        })

    def test_invalid_physical_width_never_admitted(self):
        for width in ("", "0", "0,001", "-1", "10001", "NaN", "inf",
                      "1e3", "1 000", "1,2,3", "1.12345", "1/2", True):
            with self.subTest(width=width):
                self.assertIsNone(self.request(width))

    def test_stale_or_unverified_subject_never_admitted(self):
        self.subject.proof_status = "legacy_subject_record"
        self.assertIsNone(self.request())
        self.subject.proof_status = "verified"
        self.snapshot.sha256 = "not-a-sha"
        self.assertIsNone(self.request())
        self.snapshot.sha256 = "a" * 64
        self.subject.subject_id = "subject-invalid"
        self.assertIsNone(self.request())

    def test_relative_project_path_rejected(self):
        self.assertIsNone(ptc_preview_request(
            self.snapshot, self.subject, "relative.smartsvg", "30"))


if __name__ == "__main__":
    unittest.main()
