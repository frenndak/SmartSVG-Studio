"""Actual Tk widget smoke for W03; skips where no graphical display exists.

Unlike callback fakes, these tests construct real Tk/Ttk widgets and invoke
the actual buttons. They do not validate Cricut hardware or Design Space.
"""
import hashlib
import sys
import tempfile
import tkinter as tk
from pathlib import Path
from types import SimpleNamespace
from tkinter import ttk
from unittest import TestCase, main
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))
import native_ptc_dialog_tk_v35 as ptc


def descendants(widget):
    for child in widget.winfo_children():
        yield child
        yield from descendants(child)


class RealTkPTCFlow(TestCase):
    def setUp(self):
        try:
            self.root = tk.Tk()
        except tk.TclError as exc:
            self.skipTest("Tk display unavailable: " + str(exc))
        self.root.withdraw()
        subject_id = "subject-" + "b" * 32
        subject = SimpleNamespace(subject_id=subject_id, proof_status="verified",
                                  preview=SimpleNamespace(width_px=10, height_px=10))
        self.panel = SimpleNamespace(
            tk=tk, ttk=ttk, parent=self.root, _closed=False, busy=False,
            history_requires_review=False, has_open_brush=False,
            subjects={subject_id: subject}, selection=tk.StringVar(value=subject_id),
            _project_path=str(Path.cwd().resolve() / "synthetic.smartsvg"),
            snapshot=SimpleNamespace(sha256="a" * 64))

    def tearDown(self):
        if hasattr(self, "root"):
            try:
                self.root.destroy()
            except tk.TclError:
                pass

    def buttons(self):
        return {w.cget("text"): w for w in descendants(self.root)
                if isinstance(w, ttk.Button)}


    def test_real_atelier_action_allows_large_ptc_without_brush(self):
        """Actual Tk action state: PTC >2048px works, brush stays disabled."""
        import struct
        import zlib
        from native_atelier_tk_v34 import NativeAtelierPanel

        width_px = 2049
        def chunk(tag, data):
            return (struct.pack(">I", len(data)) + tag + data +
                    struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))
        png = (bytes.fromhex("89504e470d0a1a0a") +
               chunk(b"IHDR", struct.pack(">IIBBBBB", width_px, 1, 8, 6, 0, 0, 0)) +
               chunk(b"IDAT", zlib.compress(b"\x00" + b"\x00\x00\x00\xff" * width_px)) +
               chunk(b"IEND", b""))
        sid = "subject-" + "b" * 32
        subject = SimpleNamespace(
            subject_id=sid, source_id="source-1", mask_id="mask-1",
            proof_status="verified", bbox_px=(0, 0, width_px, 1),
            preview=SimpleNamespace(status="READY_PNG", png=png,
                                    width_px=width_px, height_px=1))
        panel = NativeAtelierPanel.__new__(NativeAtelierPanel)
        panel.tk, panel.ttk = tk, ttk
        panel.parent = ttk.Frame(self.root)  # Unmapped: no heavyweight canvas draw.
        panel.snapshot = SimpleNamespace(sha256="a" * 64)
        panel.subjects = {sid: subject}
        panel.selection = tk.StringVar(value=sid)
        panel._project_path = str(Path.cwd().resolve() / "synthetic.smartsvg")
        panel._brush_key = panel._brush_dialog = panel._brush_panel = None
        panel._brush_class = object()
        panel.viewport = SimpleNamespace(load=lambda *_args: None)
        panel.details = tk.StringVar()
        panel._closed = False
        panel._update_navigation = lambda: None
        panel._update_history_controls = lambda: None
        panel.brush_button = ttk.Button(self.root, state="disabled")
        panel.ptc_button = ttk.Button(self.root, state="disabled")
        with patch.object(ptc, "publish_native_ptc_png") as publish:
            panel.render()
            self.assertEqual(str(panel.brush_button.cget("state")), "disabled")
            self.assertEqual(str(panel.ptc_button.cget("state")), "normal")
            publish.assert_not_called()
            self.assertTrue(panel.open_ptc())
            self.root.update()
            publish.assert_not_called()
            buttons = self.buttons()
            self.assertEqual(str(buttons["Choisir et publier…"].cget("state")),
                             "disabled")
            buttons["Fermer"].invoke()
            self.root.update()
            publish.assert_not_called()

    def test_real_export_buttons_follow_brush_and_history_transitions(self):
        """Both actual Ttk export controls follow non-render write transitions."""
        from concurrent.futures import Future
        from native_atelier_tk_v34 import NativeAtelierPanel

        class BrushFixture:
            # Isolate brush engine only; actual open/close and widget state.
            def __init__(self, *args, **kwargs):
                self._identity = None
                self.has_draft = False

            def load(self, **kwargs):
                self._identity = kwargs

            def shutdown(self):
                pass

        sid = self.panel.selection.get()
        subject = SimpleNamespace(
            subject_id=sid, proof_status="verified",
            preview=SimpleNamespace(status="READY_PNG", png=b"x" * 33,
                                    width_px=10, height_px=10))
        panel = NativeAtelierPanel.__new__(NativeAtelierPanel)
        panel.tk, panel.ttk, panel.parent = tk, ttk, self.root
        panel.snapshot = self.panel.snapshot
        panel.subjects = {sid: subject}
        panel.selection = self.panel.selection
        panel._project_path = self.panel._project_path
        panel._brush_key = panel._brush_dialog = panel._brush_panel = None
        panel._brush_class = BrushFixture
        panel._closed = False
        panel._history_confirming = panel._history_needs_review = False
        panel._history_future = None
        panel._history_generation = 0
        panel._history_status = {"project_sha256": panel.snapshot.sha256,
                                 "undo_available": True, "undo_subject_id": sid}
        panel._on_saved = lambda _receipt: None
        panel.ptc_button = ttk.Button(self.root, state="disabled")
        panel.basic_cut_button = ttk.Button(self.root, state="disabled")

        def states():
            return tuple(str(b.cget("state")) for b in
                         (panel.ptc_button, panel.basic_cut_button))

        panel._update_history_controls()
        self.assertEqual(states(), ("normal", "normal"))
        try:
            self.assertTrue(panel.open_brush())
            self.assertEqual(states(), ("disabled", "disabled"))
            self.assertTrue(panel._request_close_brush())
            self.assertEqual(states(), ("normal", "normal"))

            observed = []
            def cancel_history(*args):
                observed.append(states())
                return False

            panel._confirm_history_fn = cancel_history
            self.assertFalse(panel.undo_brush())
            self.assertEqual(observed, [("disabled", "disabled")])
            self.assertEqual(states(), ("normal", "normal"))

            panel._history_future = Future()
            panel._update_history_controls()
            self.assertEqual(states(), ("disabled", "disabled"))
            panel._history_future = None
            panel._history_needs_review = True
            panel._update_history_controls()
            self.assertEqual(states(), ("disabled", "disabled"))
            panel._history_needs_review = False
            panel._update_history_controls()
            self.assertEqual(states(), ("normal", "normal"))
        finally:
            panel._close_brush()

    def test_real_widgets_no_implicit_export_and_cancel(self):
        with patch.object(ptc, "publish_native_ptc_png") as publish:
            self.assertTrue(ptc.show_ptc_dialog(self.panel))
            self.root.update()
            buttons = self.buttons()
            self.assertEqual(str(buttons["Choisir et publier…"].cget("state")), "disabled")
            self.assertEqual(str(buttons["Ouvrir le dossier"].cget("state")), "disabled")
            publish.assert_not_called()
            buttons["Fermer"].invoke()
            self.root.update()
            self.assertFalse(any(isinstance(w, tk.Toplevel) for w in descendants(self.root)))
            publish.assert_not_called()

    def test_real_widgets_inspect_then_cancel_destination(self):
        # Generate a CRC-correct 1x1 RGBA PNG accepted by native Windows Tk.
        # The preview digest must describe the actual preview payload.
        import struct
        import zlib
        def chunk(tag, data):
            return (struct.pack(">I", len(data)) + tag + data +
                    struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))
        png = (b"\x89PNG\r\n\x1a\n" +
               chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)) +
               chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00\xff")) +
               chunk(b"IEND", b""))
        digest = hashlib.sha256(png).hexdigest()
        def inspect(**_kwargs):
            return dict(status="PTC_PREVIEW_READY", preview_png_rgba=png,
                        output_sha256=digest, width_mm=100, height_mm=100,
                        low_resolution_warning=False)
        with (patch.object(ptc, "inspect_native_ptc_png", side_effect=inspect),
              patch.object(ptc, "publish_native_ptc_png") as publish,
              patch.object(ptc.filedialog, "asksaveasfilename", return_value="")):
            self.assertTrue(ptc.show_ptc_dialog(self.panel))
            self.root.update()
            self.buttons()["Examiner"].invoke()
            self.root.update()
            self.assertEqual(str(self.buttons()["Choisir et publier…"].cget("state")), "normal")
            self.buttons()["Choisir et publier…"].invoke()
            self.root.update()
            publish.assert_not_called()
            self.assertEqual(str(self.buttons()["Ouvrir le dossier"].cget("state")), "disabled")


    def _valid_inspection(self):
        import struct
        import zlib
        def chunk(tag, data):
            return (struct.pack(">I", len(data)) + tag + data +
                    struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))
        png = (bytes.fromhex("89504e470d0a1a0a") +
               chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0)) +
               chunk(b"IDAT", zlib.compress(bytes.fromhex("00ff0000ff"))) +
               chunk(b"IEND", b""))
        return dict(status="PTC_PREVIEW_READY", preview_png_rgba=png,
                    output_sha256=hashlib.sha256(png).hexdigest(),
                    width_mm=100, height_mm=100, low_resolution_warning=False)


    def test_native_save_dialog_failure_keeps_preview_and_allows_retry(self):
        inspection = self._valid_inspection()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "retry.png"
            with (patch.object(ptc, "inspect_native_ptc_png", return_value=inspection),
                  patch.object(ptc, "publish_native_ptc_png") as publisher,
                  patch.object(ptc.filedialog, "asksaveasfilename",
                               side_effect=[tk.TclError("dialog unavailable"), str(target)]),
                  patch.object(ptc.messagebox, "askyesno", return_value=False)):
                self.assertTrue(ptc.show_ptc_dialog(self.panel))
                self.root.update()
                self.buttons()["Examiner"].invoke()
                self.root.update()
                self.buttons()["Choisir et publier…"].invoke()
                self.root.update()
                publisher.assert_not_called()
                self.assertFalse(target.exists())
                self.assertEqual(str(self.buttons()["Choisir et publier…"].cget("state")),
                                 "normal")
                self.buttons()["Choisir et publier…"].invoke()
                self.root.update()
                publisher.assert_not_called()
                self.assertFalse(target.exists())

    def test_native_confirmation_failure_never_publishes_and_recovers(self):
        inspection = self._valid_inspection()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "retry.png"
            with (patch.object(ptc, "inspect_native_ptc_png", return_value=inspection),
                  patch.object(ptc, "publish_native_ptc_png") as publisher,
                  patch.object(ptc.filedialog, "asksaveasfilename",
                               return_value=str(target)),
                  patch.object(ptc.messagebox, "askyesno",
                               side_effect=[OSError("dialog unavailable"), False])):
                self.assertTrue(ptc.show_ptc_dialog(self.panel))
                self.root.update()
                self.buttons()["Examiner"].invoke()
                self.root.update()
                self.buttons()["Choisir et publier…"].invoke()
                self.root.update()
                publisher.assert_not_called()
                self.assertFalse(target.exists())
                self.assertEqual(str(self.buttons()["Choisir et publier…"].cget("state")),
                                 "normal")
                self.buttons()["Choisir et publier…"].invoke()
                self.root.update()
                publisher.assert_not_called()
                self.assertFalse(target.exists())

    def test_queued_close_during_failed_save_dialog_destroys_window(self):
        inspection = self._valid_inspection()
        def fail_with_queued_close(**_kwargs):
            dialog = next(w for w in self.root.winfo_children()
                          if isinstance(w, tk.Toplevel))
            dialog.tk.call(dialog.protocol("WM_DELETE_WINDOW"))
            self.assertTrue(dialog.winfo_exists())
            raise tk.TclError("native save failed")
        with (patch.object(ptc, "inspect_native_ptc_png", return_value=inspection),
              patch.object(ptc, "publish_native_ptc_png") as publisher,
              patch.object(ptc.filedialog, "asksaveasfilename",
                           side_effect=fail_with_queued_close)):
            self.assertTrue(ptc.show_ptc_dialog(self.panel))
            self.root.update()
            self.buttons()["Examiner"].invoke()
            self.root.update()
            self.buttons()["Choisir et publier…"].invoke()
            self.root.update()
            self.assertFalse(any(isinstance(w, tk.Toplevel)
                                 for w in descendants(self.root)))
            publisher.assert_not_called()

    def test_queued_close_during_failed_confirmation_destroys_window(self):
        inspection = self._valid_inspection()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "never-published.png"
            def fail_with_queued_close(*_args, **_kwargs):
                dialog = next(w for w in self.root.winfo_children()
                              if isinstance(w, tk.Toplevel))
                dialog.tk.call(dialog.protocol("WM_DELETE_WINDOW"))
                self.assertTrue(dialog.winfo_exists())
                raise OSError("native confirmation failed")
            with (patch.object(ptc, "inspect_native_ptc_png", return_value=inspection),
                  patch.object(ptc, "publish_native_ptc_png") as publisher,
                  patch.object(ptc.filedialog, "asksaveasfilename",
                               return_value=str(target)),
                  patch.object(ptc.messagebox, "askyesno",
                               side_effect=fail_with_queued_close)):
                self.assertTrue(ptc.show_ptc_dialog(self.panel))
                self.root.update()
                self.buttons()["Examiner"].invoke()
                self.root.update()
                self.buttons()["Choisir et publier…"].invoke()
                self.root.update()
                self.assertFalse(any(isinstance(w, tk.Toplevel)
                                     for w in descendants(self.root)))
                publisher.assert_not_called()
                self.assertFalse(target.exists())

    def test_real_widgets_existing_destination_never_publishes(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "existing.png"
            target.write_bytes(b"original must survive")
            with (patch.object(ptc, "inspect_native_ptc_png",
                               return_value=self._valid_inspection()),
                  patch.object(ptc, "publish_native_ptc_png") as publish,
                  patch.object(ptc.filedialog, "asksaveasfilename",
                               return_value=str(target)),
                  patch.object(ptc.messagebox, "askyesno") as confirm):
                self.assertTrue(ptc.show_ptc_dialog(self.panel))
                self.root.update()
                self.buttons()["Examiner"].invoke()
                self.root.update()
                self.buttons()["Choisir et publier…"].invoke()
                self.root.update()
                self.assertEqual(target.read_bytes(), b"original must survive")
                confirm.assert_not_called()
                publish.assert_not_called()
                self.assertEqual(str(self.buttons()["Ouvrir le dossier"].cget("state")),
                                 "disabled")

    def test_real_widgets_stale_selection_after_confirmation_never_publishes(self):
        def change_selection(*_args, **_kwargs):
            self.panel.selection.set("subject-" + "c" * 32)
            return True
        with (patch.object(ptc, "inspect_native_ptc_png",
                           return_value=self._valid_inspection()),
              patch.object(ptc, "publish_native_ptc_png") as publish,
              patch.object(ptc.filedialog, "asksaveasfilename",
                           return_value=str(Path(tempfile.gettempdir()) /
                                            "smartsvg-w03-stale-test.png")),
              patch.object(ptc.messagebox, "askyesno",
                           side_effect=change_selection)):
            self.assertTrue(ptc.show_ptc_dialog(self.panel))
            self.root.update()
            self.buttons()["Examiner"].invoke()
            self.root.update()
            self.buttons()["Choisir et publier…"].invoke()
            self.root.update()
            publish.assert_not_called()
            self.assertEqual(str(self.buttons()["Ouvrir le dossier"].cget("state")),
                             "disabled")


    def test_real_widgets_successful_publication_requires_readback(self):
        inspection = self._valid_inspection()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "published.png"
            def publish(**kwargs):
                self.assertTrue(kwargs["confirmed"])
                self.assertEqual(kwargs["expected_output_sha256"], inspection["output_sha256"])
                target.write_bytes(inspection["preview_png_rgba"])
                return dict(persisted=True, project_revision_still_current=True,
                            status="LOCAL_PNG_PUBLISHED")
            with (patch.object(ptc, "inspect_native_ptc_png", return_value=inspection),
                  patch.object(ptc, "publish_native_ptc_png", side_effect=publish) as publisher,
                  patch.object(ptc.filedialog, "asksaveasfilename", return_value=str(target)),
                  patch.object(ptc.messagebox, "askyesno", return_value=True)):
                self.assertTrue(ptc.show_ptc_dialog(self.panel))
                self.root.update()
                self.assertFalse(target.exists())
                self.buttons()["Examiner"].invoke()
                self.root.update()
                self.assertFalse(target.exists())
                self.buttons()["Choisir et publier…"].invoke()
                self.root.update()
                publisher.assert_called_once()
                self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(),
                                 inspection["output_sha256"])
                self.assertEqual(str(self.buttons()["Ouvrir le dossier"].cget("state")),
                                 "normal")

    def test_real_widgets_mismatched_readback_blocks_folder(self):
        inspection = self._valid_inspection()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "changed.png"
            def publish(**_kwargs):
                target.write_bytes(b"unexpected content after native publication")
                return dict(persisted=True, project_revision_still_current=True,
                            status="LOCAL_PNG_PUBLISHED")
            with (patch.object(ptc, "inspect_native_ptc_png", return_value=inspection),
                  patch.object(ptc, "publish_native_ptc_png", side_effect=publish) as publisher,
                  patch.object(ptc.filedialog, "asksaveasfilename", return_value=str(target)),
                  patch.object(ptc.messagebox, "askyesno", return_value=True)):
                self.assertTrue(ptc.show_ptc_dialog(self.panel))
                self.root.update()
                self.buttons()["Examiner"].invoke()
                self.root.update()
                self.buttons()["Choisir et publier…"].invoke()
                self.root.update()
                publisher.assert_called_once()
                self.assertTrue(target.exists())
                self.assertEqual(str(self.buttons()["Ouvrir le dossier"].cget("state")),
                                 "disabled")

    def _cut_inspection(self):
        from smartsvg_core.native_basic_cut_v35 import preview_basic_cut
        raw = preview_basic_cut(rings=[[(0, 0), (100, 0), (100, 80), (0, 80)],
                                       [(30, 20), (60, 20), (60, 40), (30, 40)]],
                                width_mm=100, height_mm=80)
        return SimpleNamespace(status="BASIC_CUT_PREVIEW_READY",
                               project_sha256=self.panel.snapshot.sha256,
                               subject_id=self.panel.selection.get(),
                               svg=raw.svg, svg_sha256=raw.sha256,
                               width_mm=100., height_mm=80., ring_count=2)

    def test_basic_cut_real_widgets_preview_confirm_and_readback(self):
        inspection = self._cut_inspection()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "published.svg"
            def publish(**kwargs):
                self.assertIs(kwargs["confirmed"], True)
                self.assertEqual(kwargs["expected_svg_sha256"], inspection.svg_sha256)
                target.write_bytes(inspection.svg)
                return dict(persisted=True, project_revision_still_current=True,
                            status="LOCAL_SVG_RELOADED")
            with (patch.object(ptc, "inspect_native_basic_cut_subject", return_value=inspection),
                  patch.object(ptc, "publish_native_basic_cut_svg", side_effect=publish) as publisher,
                  patch.object(ptc, "publish_native_ptc_png") as png_publisher,
                  patch.object(ptc.filedialog, "asksaveasfilename", return_value=str(target)),
                  patch.object(ptc.messagebox, "askyesno", return_value=True)):
                self.assertTrue(ptc.show_basic_cut_dialog(self.panel))
                self.root.update()
                self.assertEqual(str(self.buttons()["Choisir et publier…"].cget("state")), "disabled")
                self.buttons()["Examiner"].invoke()
                self.root.update()
                canvases = [w for w in descendants(self.root) if isinstance(w, tk.Canvas)]
                self.assertEqual(len(canvases), 1)
                self.assertEqual(len(canvases[0].find_all()), 2)
                self.assertFalse(target.exists())
                self.buttons()["Choisir et publier…"].invoke()
                self.root.update()
                publisher.assert_called_once()
                png_publisher.assert_not_called()
                self.assertEqual(target.read_bytes(), inspection.svg)
                self.assertEqual(str(self.buttons()["Ouvrir le dossier"].cget("state")), "normal")

    def test_basic_cut_stale_selection_during_consent_never_publishes(self):
        inspection = self._cut_inspection()
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "stale.svg"
            def stale(*args, **kwargs):
                self.panel.selection.set("subject-" + "c" * 32)
                return True
            with (patch.object(ptc, "inspect_native_basic_cut_subject", return_value=inspection),
                  patch.object(ptc, "publish_native_basic_cut_svg") as publisher,
                  patch.object(ptc.filedialog, "asksaveasfilename", return_value=str(target)),
                  patch.object(ptc.messagebox, "askyesno", side_effect=stale)):
                self.assertTrue(ptc.show_basic_cut_dialog(self.panel))
                self.root.update()
                self.buttons()["Examiner"].invoke()
                self.buttons()["Choisir et publier…"].invoke()
                publisher.assert_not_called()
                self.assertFalse(target.exists())

    def test_basic_cut_complex_contour_has_actionable_feedback(self):
        from smartsvg_core.native_basic_cut_v35 import BasicCutError
        with (patch.object(ptc, "inspect_native_basic_cut_subject",
                           side_effect=BasicCutError("SILHOUETTE_TOO_COMPLEX")),
              patch.object(ptc, "publish_native_basic_cut_svg") as publisher):
            self.assertTrue(ptc.show_basic_cut_dialog(self.panel))
            self.root.update()
            self.buttons()["Examiner"].invoke()
            labels = [w for w in descendants(self.root) if isinstance(w, ttk.Label)]
            messages = [str(w.getvar(w.cget("textvariable"))) for w in labels
                        if w.cget("textvariable")]
            self.assertTrue(any("simplifiez la silhouette" in msg for msg in messages))
            self.assertEqual(str(self.buttons()["Choisir et publier…"].cget("state")), "disabled")
            publisher.assert_not_called()

    def test_basic_cut_invalid_preview_and_cancel_do_not_publish(self):
        inspection = self._cut_inspection()
        inspection.svg_sha256 = "0" * 64
        with (patch.object(ptc, "inspect_native_basic_cut_subject", return_value=inspection),
              patch.object(ptc, "publish_native_basic_cut_svg") as publisher):
            self.assertTrue(ptc.show_basic_cut_dialog(self.panel))
            self.root.update()
            self.buttons()["Examiner"].invoke()
            self.assertEqual(str(self.buttons()["Choisir et publier…"].cget("state")), "disabled")
            self.buttons()["Fermer"].invoke()
            publisher.assert_not_called()

if __name__ == "__main__":
    main()
