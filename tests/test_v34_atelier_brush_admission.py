"""Regression: malformed archived previews cannot crash native brush admission."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))
from native_atelier_tk_v34 import brush_preview_request


class AtelierBrushAdmissionTests(unittest.TestCase):
    def setUp(self):
        self.snapshot = SimpleNamespace(sha256="a" * 64)
        self.preview = SimpleNamespace(status="READY_PNG", png=b"x" * 40,
                                       width_px=16, height_px=12)
        self.subject = SimpleNamespace(subject_id="subject-" + "b" * 32,
                                       proof_status="verified", preview=self.preview)
        self.path = str(Path.cwd().resolve() / "synthetic.smartsvg")

    def test_verified_subject_routes_to_backend_without_mutation(self):
        request = brush_preview_request(self.snapshot, self.subject, self.path)
        self.assertEqual(request["expected_sha256"], self.snapshot.sha256)
        self.assertEqual(request["subject_id"], self.subject.subject_id)
        self.assertEqual(request["preview_png"], self.preview.png)

    def test_incomplete_snapshot_or_subject_fails_closed(self):
        """Malformed session objects must not crash the Tk event callback."""
        original_snapshot, original_subject = self.snapshot, self.subject
        try:
            for snapshot, subject in (
                (SimpleNamespace(), original_subject),
                (original_snapshot, SimpleNamespace()),
                (original_snapshot, SimpleNamespace(subject_id=original_subject.subject_id)),
                (original_snapshot, SimpleNamespace(subject_id=original_subject.subject_id,
                                                    proof_status="verified")),
            ):
                with self.subTest(snapshot=snapshot, subject=subject):
                    self.assertIsNone(brush_preview_request(snapshot, subject, self.path))
        finally:
            self.snapshot, self.subject = original_snapshot, original_subject

    def test_incomplete_preview_fields_fail_closed(self):
        """Missing metadata in an archived preview must never escape into Tk."""
        original = self.subject.preview
        try:
            for preview in (
                SimpleNamespace(),
                SimpleNamespace(status="READY_PNG"),
                SimpleNamespace(status="READY_PNG", png=b"x" * 40),
                SimpleNamespace(status="READY_PNG", png=b"x" * 40, width_px=16),
                SimpleNamespace(status="READY_PNG", png=b"x" * 40, height_px=12),
            ):
                with self.subTest(preview=vars(preview)):
                    self.subject.preview = preview
                    self.assertIsNone(brush_preview_request(
                        self.snapshot, self.subject, self.path))
        finally:
            self.subject.preview = original

    def test_missing_preview_fails_closed(self):
        self.subject.preview = None
        self.assertIsNone(brush_preview_request(self.snapshot, self.subject, self.path))

    def test_invalid_dimensions_fail_closed_without_exception(self):
        for value in (None, "16", 16.0, True, -1, 0, 2049):
            for axis in ("width_px", "height_px"):
                with self.subTest(value=value, axis=axis):
                    setattr(self.preview, "width_px", 16)
                    setattr(self.preview, "height_px", 12)
                    setattr(self.preview, axis, value)
                    self.assertIsNone(brush_preview_request(
                        self.snapshot, self.subject, self.path))


if __name__ == "__main__":
    unittest.main()
