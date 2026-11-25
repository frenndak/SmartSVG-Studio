"""W04 SVG publication: consent, CAS, non-overwrite and failure receipts."""
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from smartsvg_core.native_basic_cut_v35 import BasicCutError
from smartsvg_core.native_basic_cut_export_v35 import publish_native_basic_cut_svg
from smartsvg_core.native_first_subject_v35 import NativeFirstSubjectError
from smartsvg_core.native_ptc_export_v35 import NativePTCError

MODULE = "smartsvg_core.native_basic_cut_export_v35"


class NativeBasicCutExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "cut.svg"
        self.data = b'<svg xmlns="http://www.w3.org/2000/svg"/>'
        self.digest = sha256(self.data).hexdigest()
        self.args = dict(project_path="/synthetic/a.smartsvg",
                         expected_sha256="a" * 64,
                         subject_id="subject-" + "b" * 32, width_mm=60,
                         destination_path=str(self.output),
                         expected_svg_sha256=self.digest, confirmed=True)
        self.preview = SimpleNamespace(svg=self.data, svg_sha256=self.digest,
                                       project_sha256="a" * 64,
                                       subject_id=self.args["subject_id"],
                                       width_mm=60, height_mm=40, ring_count=1)

    def mocks(self):
        return patch(MODULE + ".inspect_native_basic_cut_subject",
                     return_value=self.preview)

    def test_consent_and_digest_are_required_before_render(self):
        with self.mocks() as render:
            for changes, code in [
                ({"confirmed": False}, "EXPLICIT_CONFIRMATION_REQUIRED"),
                ({"expected_svg_sha256": "wrong"}, "EXPECTED_PREVIEW_REQUIRED"),
                ({"destination_path": str(self.output.with_suffix(".png"))}, "INVALID_EXPORT_PATH"),
            ]:
                with self.assertRaisesRegex(BasicCutError, code):
                    publish_native_basic_cut_svg(**{**self.args, **changes})
            render.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_preview_change_does_not_publish(self):
        with self.mocks(), patch(MODULE + "._pinned_project") as pinned, patch(
                MODULE + "._publish_posix_pinned") as publish:
            with self.assertRaisesRegex(BasicCutError, "PREVIEW_CHANGED"):
                publish_native_basic_cut_svg(**{**self.args, "expected_svg_sha256": "c" * 64})
            pinned.assert_not_called()
            publish.assert_not_called()

    def test_project_cas_failure_prevents_publication(self):
        with self.mocks(), patch(MODULE + "._pinned_project",
                                 side_effect=NativeFirstSubjectError("PROJECT_CHANGED")), patch(
                MODULE + "._publish_posix_pinned") as publish:
            with self.assertRaisesRegex(BasicCutError, "PROJECT_CHANGED"):
                publish_native_basic_cut_svg(**self.args)
            publish.assert_not_called()

    @unittest.skipUnless(sys.platform.startswith("linux"), "POSIX Linux atomic writer")
    def test_real_writer_no_overwrite_and_identical_retry(self):
        with self.mocks(), patch(MODULE + "._pinned_project", return_value=object()):
            try:
                receipt = publish_native_basic_cut_svg(**self.args)
            except BasicCutError as exc:
                if str(exc) == "ATOMIC_PUBLICATION_UNAVAILABLE":
                    self.skipTest("O_TMPFILE/procfs atomic writer unsupported on runner")
                raise
            self.assertEqual(self.output.read_bytes(), self.data)
            self.assertEqual(receipt["status"], "LOCAL_SVG_RELOADED")
            self.assertFalse(receipt["physical_cut_tested"])
            publish_native_basic_cut_svg(**self.args)
            self.assertEqual(self.output.read_bytes(), self.data)
            self.output.write_bytes(b"other user's work")
            with self.assertRaisesRegex(BasicCutError, "OUTPUT_REQUIRES_REVIEW"):
                publish_native_basic_cut_svg(**self.args)
            self.assertEqual(self.output.read_bytes(), b"other user's work")

    def test_writer_failure_propagates_no_success_receipt(self):
        # Never mutate os.name: pathlib selects its host-specific Path class from it.
        writer = "_publish_windows_locked" if sys.platform == "win32" else "_publish_posix_pinned"
        with self.mocks(), patch(MODULE + "._pinned_project", return_value=object()), patch(
                MODULE + "." + writer,
                side_effect=NativePTCError("OUTPUT_REQUIRES_REVIEW")):
            with self.assertRaisesRegex(BasicCutError, "OUTPUT_REQUIRES_REVIEW"):
                publish_native_basic_cut_svg(**self.args)
            self.assertFalse(self.output.exists())

    def test_unrelated_png_symlink_does_not_invalidate_svg_destination(self):
        sibling = self.output.with_suffix(".png")
        target = Path(self.temp.name) / "elsewhere.png"
        target.write_bytes(b"untouched")
        try:
            sibling.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable on this host: {exc}")
        with self.mocks(), patch(MODULE + "._pinned_project", return_value=object()):
            writer = "_publish_windows_locked" if sys.platform == "win32" else "_publish_posix_pinned"
            with patch(MODULE + "." + writer) as publish:
                publish_native_basic_cut_svg(**self.args)
                publish.assert_called_once()
        self.assertEqual(target.read_bytes(), b"untouched")

    def test_symlink_target_refused_without_render(self):
        target = Path(self.temp.name) / "other.svg"
        target.write_bytes(b"original")
        self.output.symlink_to(target)
        with self.mocks() as render:
            with self.assertRaisesRegex(BasicCutError, "UNSAFE_EXPORT_PATH"):
                publish_native_basic_cut_svg(**self.args)
            render.assert_not_called()
        self.assertEqual(target.read_bytes(), b"original")


if __name__ == "__main__":
    unittest.main()
