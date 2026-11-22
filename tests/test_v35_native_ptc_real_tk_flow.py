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

if __name__ == "__main__":
    main()
