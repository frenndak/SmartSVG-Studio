"""W03 dialog regression: cancellation, collision, stale selection and readback.

Headless Tk callback tests; not a substitute for interactive Windows qualification.
"""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))
import native_ptc_dialog_tk_v35 as module


class Variable:
    created = []
    def __init__(self, value=""):
        self.value, self.callbacks = value, []
        Variable.created.append(self)
    def get(self):
        return self.value
    def set(self, value):
        self.value = value
        for callback in self.callbacks:
            callback()
    def trace_add(self, _mode, callback):
        self.callbacks.append(callback)


class Widget:
    buttons = {}
    def __init__(self, *_args, **kwargs):
        self.command = kwargs.get("command")
        self.state = kwargs.get("state")
        self.destroyed = False
        if self.command is not None:
            Widget.buttons[kwargs.get("text")] = self
    def pack(self, **_kwargs):
        pass
    def configure(self, **kwargs):
        self.state = kwargs.get("state", self.state)
    def title(self, *_args):
        pass
    def transient(self, *_args):
        pass
    def geometry(self, *_args):
        pass
    def protocol(self, *_args):
        pass
    def destroy(self):
        self.destroyed = True


class DialogSafetyTests(unittest.TestCase):
    def setUp(self):
        Variable.created.clear()
        Widget.buttons.clear()
        tk = SimpleNamespace(Toplevel=Widget, StringVar=Variable,
                             PhotoImage=Widget, TclError=RuntimeError)
        ttk = SimpleNamespace(Frame=Widget, Label=Widget, Entry=Widget, Button=Widget)
        self.subject = SimpleNamespace(
            subject_id="subject-" + "b" * 32, proof_status="verified",
            preview=SimpleNamespace(width_px=10, height_px=10))
        self.panel = SimpleNamespace(
            tk=tk, ttk=ttk, _closed=False, busy=False,
            history_requires_review=False, has_open_brush=False,
            parent=Widget(), subjects={self.subject.subject_id: self.subject},
            selection=Variable(self.subject.subject_id),
            _project_path=str(Path.cwd().resolve() / "synthetic.smartsvg"),
            snapshot=SimpleNamespace(sha256="a" * 64))
        self.payload = b"synthetic png bytes"
        self.digest = hashlib.sha256(self.payload).hexdigest()

    def open_and_inspect(self):
        self.assertTrue(module.show_ptc_dialog(self.panel))
        Widget.buttons["Examiner"].command()
        self.assertEqual(Widget.buttons["Choisir et publier…"].state, "normal")

    def inspector(self, **_kwargs):
        return dict(status="PTC_PREVIEW_READY", preview_png_rgba=self.payload,
                    output_sha256=self.digest, width_mm=100,
                    height_mm=100, low_resolution_warning=False)

    def test_cancel_destination_never_publishes(self):
        with (patch.object(module, "inspect_native_ptc_png", side_effect=self.inspector),
              patch.object(module, "publish_native_ptc_png") as publisher,
              patch.object(module.filedialog, "asksaveasfilename", return_value="")):
            self.open_and_inspect()
            Widget.buttons["Choisir et publier…"].command()
            publisher.assert_not_called()
            self.assertEqual(Widget.buttons["Ouvrir le dossier"].state, "disabled")

    def test_declined_confirmation_never_publishes(self):
        with tempfile.TemporaryDirectory() as folder:
            target = str(Path(folder) / "new.png")
            with (patch.object(module, "inspect_native_ptc_png", side_effect=self.inspector),
                  patch.object(module, "publish_native_ptc_png") as publisher,
                  patch.object(module.filedialog, "asksaveasfilename", return_value=target),
                  patch.object(module.messagebox, "askyesno", return_value=False)):
                self.open_and_inspect()
                Widget.buttons["Choisir et publier…"].command()
                publisher.assert_not_called()
                self.assertFalse(Path(target).exists())

    def test_existing_destination_never_confirms_or_overwrites(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "existing.png"
            target.write_bytes(b"original")
            with (patch.object(module, "inspect_native_ptc_png", side_effect=self.inspector),
                  patch.object(module, "publish_native_ptc_png") as publisher,
                  patch.object(module.filedialog, "asksaveasfilename", return_value=str(target)),
                  patch.object(module.messagebox, "askyesno") as confirmation):
                self.open_and_inspect()
                Widget.buttons["Choisir et publier…"].command()
                confirmation.assert_not_called()
                publisher.assert_not_called()
                self.assertEqual(target.read_bytes(), b"original")

    def test_stale_selection_after_confirmation_never_publishes(self):
        with tempfile.TemporaryDirectory() as folder:
            target = str(Path(folder) / "new.png")
            def change_selection(*_args, **_kwargs):
                self.panel.selection.set("subject-" + "c" * 32)
                return True
            with (patch.object(module, "inspect_native_ptc_png", side_effect=self.inspector),
                  patch.object(module, "publish_native_ptc_png") as publisher,
                  patch.object(module.filedialog, "asksaveasfilename", return_value=target),
                  patch.object(module.messagebox, "askyesno", side_effect=change_selection)):
                self.open_and_inspect()
                Widget.buttons["Choisir et publier…"].command()
                publisher.assert_not_called()
                self.assertFalse(Path(target).exists())

    def test_verified_readback_enables_folder_only_on_digest_match(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "new.png"
            def publisher(**kwargs):
                self.assertTrue(kwargs["confirmed"])
                self.assertEqual(kwargs["expected_output_sha256"], self.digest)
                target.write_bytes(self.payload)
                return {"persisted": True}
            with (patch.object(module, "inspect_native_ptc_png", side_effect=self.inspector),
                  patch.object(module, "publish_native_ptc_png", side_effect=publisher),
                  patch.object(module.filedialog, "asksaveasfilename", return_value=str(target)),
                  patch.object(module.messagebox, "askyesno", return_value=True)):
                self.open_and_inspect()
                Widget.buttons["Choisir et publier…"].command()
                self.assertEqual(target.read_bytes(), self.payload)
                self.assertEqual(Widget.buttons["Ouvrir le dossier"].state, "normal")

    def test_bad_readback_never_enables_folder(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "new.png"
            def publisher(**_kwargs):
                target.write_bytes(b"corrupt")
                return {"persisted": True}
            with (patch.object(module, "inspect_native_ptc_png", side_effect=self.inspector),
                  patch.object(module, "publish_native_ptc_png", side_effect=publisher),
                  patch.object(module.filedialog, "asksaveasfilename", return_value=str(target)),
                  patch.object(module.messagebox, "askyesno", return_value=True)):
                self.open_and_inspect()
                Widget.buttons["Choisir et publier…"].command()
                self.assertEqual(Widget.buttons["Ouvrir le dossier"].state, "disabled")
                self.assertIn("Relecture différente", Variable.created[-2].get())


if __name__ == "__main__":
    unittest.main()
