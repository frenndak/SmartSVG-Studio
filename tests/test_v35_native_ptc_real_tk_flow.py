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
        payload = b"synthetic png bytes"
        digest = hashlib.sha256(payload).hexdigest()
        # A real Tk PhotoImage needs a valid PNG; use a tiny image created by Tk
        # and avoid any filesystem or export operation during inspection.
        import base64
        png = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/lXcAAAAASUVORK5CYII=")
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


if __name__ == "__main__":
    main()
