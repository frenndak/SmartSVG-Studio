"""W03 first native PNG: real V1 Subject, brush replay and non-overwrite export."""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from smartsvg_core.native_first_subject_v35 import (
    inspect_first_alpha_subject, confirm_first_alpha_subject)
from smartsvg_core.native_ptc_export_v35 import (
    NativePTCError, inspect_native_ptc_png, publish_native_ptc_png)
from smartsvg_core.project_archive import load_project
from smartsvg_core.project_workspace_g22 import ManagedWorkspace
from test_v35_native_first_subject import png
from test_v34_native_subject_preview import NativeSubjectPreviewTests
from smartsvg_core.native_subject_preview_v34 import preview_native_subject_stroke
from smartsvg_core.native_subject_save_v34 import save_native_subject_stroke

HAS_CPU = all(importlib.util.find_spec(lib) for lib in ("numpy", "PIL"))


class PTCValidationTests(unittest.TestCase):
    def test_explicit_confirmation_and_width_refusals_are_dependency_free(self):
        request = dict(
            project_path="/missing.smartsvg", expected_sha256="a" * 64,
            subject_id="subject-" + "b" * 32, width_mm=10,
            destination_path="/tmp/out.png", expected_output_sha256="c" * 64)
        with self.assertRaises(NativePTCError) as ctx:
            publish_native_ptc_png(**request)
        self.assertEqual(ctx.exception.code, "EXPLICIT_CONFIRMATION_REQUIRED")
        for value in (True, False, 0, -2, 0.0, float("nan"),
                      float("inf"), "10,5", 10001):
            with self.subTest(width=value):
                with self.assertRaises(NativePTCError) as ctx:
                    inspect_native_ptc_png(
                        project_path="/missing.smartsvg",
                        expected_sha256="a" * 64,
                        subject_id=request["subject_id"], width_mm=value)
                self.assertEqual(ctx.exception.code, "INVALID_PHYSICAL_WIDTH")


@unittest.skipUnless(HAS_CPU, "Full real PNG export needs existing NumPy/Pillow runtime")
class FirstNativePTCTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.workspace = ManagedWorkspace(self.tmp.name)
        self.name = "native-ptc"
        self.original = png()
        created = self.workspace.create(
            self.name, self.original, profile="Sticker - contour du sujet",
            source_provenance="manual_native_png_import")
        self.path = self.workspace.root / (self.name + ".smartsvg")
        alpha = inspect_first_alpha_subject(
            project_path=str(self.path), expected_sha256=created["sha256"])
        committed = confirm_first_alpha_subject(
            project_path=str(self.path), expected_sha256=created["sha256"],
            candidate_sha256=alpha["candidate_sha256"], confirmed=True)
        self.sha = committed["project_sha256"]
        self.subject = committed["subject_id"]
        self.destination = Path(self.tmp.name) / "Première création PTC.png"
        self.request = dict(
            project_path=str(self.path), expected_sha256=self.sha,
            subject_id=self.subject, width_mm=1.0)

    def preview(self):
        return inspect_native_ptc_png(**self.request)

    def publish(self, preview, **changes):
        args = dict(self.request)
        args.update(destination_path=str(self.destination),
                    expected_output_sha256=preview["output_sha256"],
                    confirmed=True)
        args.update(changes)
        return publish_native_ptc_png(**args)

    def test_preview_is_read_only_and_keeps_128_alpha_without_squaring(self):
        before = self.path.read_bytes()
        preview = self.preview()
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(preview["status"], "PTC_PREVIEW_READY")
        self.assertIs(preview["persisted"], False)
        self.assertEqual(preview["dimensions_px"], [6, 5])
        self.assertNotIn("png", preview)
        self.assertFalse(preview["design_space_import_tested"])
        self.assertFalse(self.destination.exists())
        from PIL import Image
        with Image.open(BytesIO(preview["preview_png_rgba"])) as im:
            im.load()
            self.assertEqual(im.mode, "RGBA")
            self.assertEqual(im.size, (6, 5))
            self.assertEqual(im.getpixel((3, 3))[3], 128)
            self.assertEqual(im.getpixel((3, 3))[:3], (33, 53, 70))

    def test_real_external_png_written_reopened_and_project_unchanged(self):
        preview = self.preview()
        before = self.path.read_bytes()
        receipt = self.publish(preview)
        self.assertEqual(receipt["status"], "LOCAL_PNG_RELOADED")
        self.assertEqual(receipt["file_path"], str(self.destination))
        self.assertTrue(receipt["project_revision_still_current"])
        self.assertEqual(sha256(self.destination.read_bytes()).hexdigest(),
                         preview["output_sha256"])
        self.assertEqual(self.path.read_bytes(), before)
        project = load_project(self.path, expected_sha256=self.sha)
        self.assertEqual(
            project.resources[project.source_paths[project.sources[0].source_id]],
            self.original)
        from PIL import Image
        with Image.open(self.destination) as im:
            im.load()
            self.assertEqual(im.size, (6, 5))
            self.assertEqual(im.mode, "RGBA")
            self.assertAlmostEqual(im.info["dpi"][0], 152.4, delta=0.1)
            self.assertEqual(im.getpixel((3, 3))[3], 128)
        self.assertFalse(receipt["physical_cut_tested"])
        # Same content can be safely re-requested; no overwrite of other bytes.
        same = self.publish(preview)
        self.assertEqual(same["sha256"], receipt["sha256"])

    def test_negative_consent_candidate_and_existing_file_preservation(self):
        preview = self.preview()
        for approved in (False, "yes", 1, None):
            with self.subTest(confirmed=approved):
                with self.assertRaises(NativePTCError) as ctx:
                    self.publish(preview, confirmed=approved)
                self.assertEqual(ctx.exception.code,
                                 "EXPLICIT_CONFIRMATION_REQUIRED")
        with self.assertRaises(NativePTCError) as ctx:
            self.publish(preview, expected_output_sha256="0" * 64)
        self.assertEqual(ctx.exception.code, "PREVIEW_CHANGED")
        self.assertFalse(self.destination.exists())
        self.destination.write_bytes(b"Important user file: never overwrite")
        with self.assertRaises(NativePTCError) as ctx:
            self.publish(preview)
        self.assertEqual(ctx.exception.code, "OUTPUT_REQUIRES_REVIEW")
        self.assertEqual(self.destination.read_bytes(),
                         b"Important user file: never overwrite")

    def test_revision_stale_and_unmanaged_target_never_publish(self):
        preview = self.preview()
        self.workspace.update_notes(
            self.name, notes="Une note concurrente", expected_sha256=self.sha)
        with self.assertRaises(NativePTCError):
            self.publish(preview)
        self.assertFalse(self.destination.exists())
        self.assertEqual(load_project(self.path).document["notes"],
                         "Une note concurrente")


@unittest.skipUnless(HAS_CPU, "Existing real brush replay needs NumPy/Pillow")
class PersistedBrushPTCTests(unittest.TestCase):
    def setUp(self):
        fixture = NativeSubjectPreviewTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        self.fixture = fixture

    def test_real_saved_brush_changes_export_alpha_without_touching_source(self):
        fixture = self.fixture
        args = dict(
            project_path=str(fixture.path), expected_sha256=fixture.sha,
            subject_id=fixture.subject_id, width_mm=1.8)
        before = inspect_native_ptc_png(**args)
        source_before = load_project(fixture.path).resources.copy()
        stroke = preview_native_subject_stroke(**fixture.command())
        saved = save_native_subject_stroke(
            **fixture.command(),
            expected_preview_mask_sha256_float32=stroke["preview_mask_sha256_float32"],
            command_id="w03-verify-stroke-export", confirmed=True)
        self.assertEqual(saved["status"], "subject_brush_saved")
        args["expected_sha256"] = saved["project_sha256"]
        after = inspect_native_ptc_png(**args)
        self.assertNotEqual(before["rendered_mask_sha256"],
                            after["rendered_mask_sha256"])
        self.assertNotEqual(before["output_sha256"], after["output_sha256"])
        self.assertEqual(load_project(fixture.path).resources, source_before)
        self.assertEqual(len(load_project(fixture.path).subjects), 1)


if __name__ == "__main__":
    unittest.main()
