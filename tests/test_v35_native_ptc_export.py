"""W03 first native PNG: real V1 Subject, brush replay and non-overwrite export."""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import importlib.util
import os
from unittest.mock import patch
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



@unittest.skipUnless(os.name == "posix", "POSIX dir_fd semantics required")
class PinnedPublisherSafetyTests(unittest.TestCase):
    """Dependency-free Linux gate for W03 TOCTOU, even without NumPy/Pillow."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.parent = Path(self.tmp.name) / "safe"
        self.parent.mkdir()
        self.dest = self.parent / "export.png"
        self.payload = b"complete staged export bytes"
        self.digest = sha256(self.payload).hexdigest()

    def publish(self):
        from smartsvg_core.native_ptc_export_v35 import _publish_posix_pinned
        return _publish_posix_pinned(
            self.dest, self.payload, self.digest,
            os.stat(self.parent, follow_symlinks=False))

    def test_existing_identical_output_is_idempotent_without_stage(self):
        self.publish()
        self.publish()
        self.assertEqual(self.dest.read_bytes(), self.payload)
        self.assertEqual(len(list(self.parent.glob(".smartsvg_ptc_stage_*"))), 1)

    def test_concurrent_different_output_is_never_overwritten(self):
        real_link = os.link
        rival = b"valuable competing user file"
        def compete(src, dst, *args, **kwargs):
            self.dest.write_bytes(rival)
            return real_link(src, dst, *args, **kwargs)
        with patch("smartsvg_core.native_ptc_export_v35.os.link",
                   side_effect=compete):
            with self.assertRaises(NativePTCError) as ctx:
                self.publish()
        self.assertEqual(ctx.exception.code, "OUTPUT_REQUIRES_REVIEW")
        self.assertEqual(self.dest.read_bytes(), rival)
        self.assertEqual(len(list(self.parent.glob(".smartsvg_ptc_stage_*"))), 1)

    def test_parent_swap_during_link_never_writes_replacement(self):
        parked = Path(self.tmp.name) / "parked"
        replacement = Path(self.tmp.name) / "replacement"
        replacement.mkdir()
        swapped = False
        real_link = os.link

        def swap_during_link(src, dst, *args, **kwargs):
            nonlocal swapped
            if not swapped:
                swapped = True
                # Attacker-controlled parent contains a same-named stage.
                (replacement / Path(src).name).write_bytes(b"attacker-controlled")
                self.parent.rename(parked)
                replacement.rename(self.parent)
            return real_link(src, dst, *args, **kwargs)

        try:
            with patch("smartsvg_core.native_ptc_export_v35.os.link",
                       side_effect=swap_during_link):
                with self.assertRaises(NativePTCError) as ctx:
                    self.publish()
            self.assertEqual(ctx.exception.code, "UNSAFE_EXPORT_PATH")
            self.assertFalse(self.dest.exists(), "Published into replacement parent")
        finally:
            if swapped:
                self.parent.rename(replacement)
                parked.rename(self.parent)
        self.assertTrue(swapped)
        self.assertFalse((replacement / "export.png").exists())
        # The pinned original directory may contain a completed hard-link:
        # detection after link returns UNSAFE_EXPORT_PATH, but deleting that
        # entry would risk removing a concurrently substituted user file.
        # The output is retained only in the original, verified directory.
        self.assertEqual(self.dest.read_bytes(), self.payload)
        self.assertEqual(len(list(self.parent.glob(".smartsvg_ptc_stage_*"))), 1)

    def test_no_identity_checked_path_unlink_even_on_failed_publication(self):
        # A stat/unlink pair is racy even when the stat matches our inode:
        # a rival can replace the entry before unlink and lose user data.
        # POSIX publisher must not invoke unlink on either output or stage.
        real_link = os.link
        rival = b"rival output must survive"
        def concurrent_output(src, dst, *args, **kwargs):
            self.dest.write_bytes(rival)
            return real_link(src, dst, *args, **kwargs)
        with patch("smartsvg_core.native_ptc_export_v35.os.unlink",
                   side_effect=AssertionError("unsafe pathname cleanup")):
            with patch("smartsvg_core.native_ptc_export_v35.os.link",
                       side_effect=concurrent_output):
                with self.assertRaises(NativePTCError):
                    self.publish()
        self.assertEqual(self.dest.read_bytes(), rival)
        retained = list(self.parent.glob(".smartsvg_ptc_stage_*"))
        self.assertEqual(len(retained), 1)
        self.assertEqual(retained[0].read_bytes(), self.payload)

    def test_parent_changed_before_open_is_rejected(self):
        from smartsvg_core.native_ptc_export_v35 import _publish_posix_pinned
        original = os.stat(self.parent, follow_symlinks=False)
        parked = Path(self.tmp.name) / "parked"
        replacement = Path(self.tmp.name) / "replacement"
        replacement.mkdir()
        self.parent.rename(parked)
        replacement.rename(self.parent)
        try:
            with self.assertRaises(NativePTCError) as ctx:
                _publish_posix_pinned(self.dest, self.payload, self.digest, original)
            self.assertEqual(ctx.exception.code, "UNSAFE_EXPORT_PATH")
            self.assertFalse(self.dest.exists())
        finally:
            self.parent.rename(replacement)
            parked.rename(self.parent)
        self.assertFalse(self.dest.exists())

    def test_symlinked_parent_rejected(self):
        redirected = Path(self.tmp.name) / "redirected"
        redirected.mkdir()
        alias = Path(self.tmp.name) / "link-parent"
        alias.symlink_to(redirected, target_is_directory=True)
        self.dest = alias / "export.png"
        with self.assertRaises(NativePTCError):
            self.publish()
        self.assertFalse((redirected / "export.png").exists())


@unittest.skipUnless(os.name == "nt", "Windows handle-pinning semantics required")
class WindowsPinnedPublisherTests(unittest.TestCase):
    def test_complete_nonclobber_publication_and_idempotent_rerun(self):
        from smartsvg_core.native_ptc_export_v35 import _publish_windows_locked
        with tempfile.TemporaryDirectory() as root:
            parent = Path(root) / "safe"
            parent.mkdir()
            dest = parent / "export.png"
            payload = b"complete PNG bytes"
            digest = sha256(payload).hexdigest()
            saved = os.stat(parent, follow_symlinks=False)
            _publish_windows_locked(dest, payload, digest, saved)
            self.assertEqual(dest.read_bytes(), payload)
            _publish_windows_locked(dest, payload, digest, saved)
            self.assertEqual(dest.read_bytes(), payload)
            dest.write_bytes(b"user-owned content")
            with self.assertRaises(NativePTCError) as ctx:
                _publish_windows_locked(dest, payload, digest, saved)
            self.assertEqual(ctx.exception.code, "OUTPUT_REQUIRES_REVIEW")
            self.assertEqual(dest.read_bytes(), b"user-owned content")

    def test_parent_rename_is_blocked_during_exclusive_link(self):
        from smartsvg_core.native_ptc_export_v35 import _publish_windows_locked
        with tempfile.TemporaryDirectory() as root:
            parent = Path(root) / "safe"
            parent.mkdir()
            parked = Path(root) / "parked"
            dest = parent / "export.png"
            payload = b"Windows atomically staged bytes"
            digest = sha256(payload).hexdigest()
            real_link = os.link
            blocked = False

            def try_rename_then_link(src, dst, *args, **kwargs):
                nonlocal blocked
                try:
                    parent.rename(parked)
                except OSError:
                    blocked = True
                else:
                    raise AssertionError("Directory was replaceable despite held handles")
                return real_link(src, dst, *args, **kwargs)

            with patch("smartsvg_core.native_ptc_export_v35.os.link",
                       side_effect=try_rename_then_link):
                _publish_windows_locked(
                    dest, payload, digest,
                    os.stat(parent, follow_symlinks=False))
            self.assertTrue(blocked)
            self.assertEqual(dest.read_bytes(), payload)
            self.assertFalse(parked.exists())


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

    @unittest.skipUnless(os.name == "posix", "Deterministic directory-swap test uses POSIX rename")
    def test_directory_swap_during_link_never_publishes_in_replacement(self):
        # Simulate an attacker replacing the verified parent after staging.
        preview = self.preview()
        safe = Path(self.tmp.name) / "safe"
        replacement = Path(self.tmp.name) / "replacement"
        parked = Path(self.tmp.name) / "parked"
        safe.mkdir()
        replacement.mkdir()
        destination = safe / "export.png"
        real_link = os.link
        swapped = False

        def swap_then_link(src, dst, *args, **kwargs):
            nonlocal swapped
            if not swapped:
                swapped = True
                # Give the replacement directory a matching staging name:
                # a pathname-based link must not publish from this directory.
                (replacement / Path(src).name).write_bytes(b"attacker bytes")
                safe.rename(parked)
                replacement.rename(safe)
            return real_link(src, dst, *args, **kwargs)

        try:
            with patch("smartsvg_core.native_ptc_export_v35.os.link", side_effect=swap_then_link):
                with self.assertRaises(NativePTCError):
                    self.publish(preview, destination_path=str(destination))
        finally:
            if swapped:
                safe.rename(replacement)
                parked.rename(safe)
        self.assertTrue(swapped)
        self.assertFalse((replacement / "export.png").exists(),
                         "Export escaped the verified directory during a parent swap")
        self.assertFalse(destination.exists())

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
