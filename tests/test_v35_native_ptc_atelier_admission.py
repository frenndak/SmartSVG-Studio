"""Focused W03 Atelier native PTC GUI admission regressions."""
from pathlib import Path
from types import SimpleNamespace
import sys
import unittest
import tempfile

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))
from native_ptc_atelier_tk_v35 import ptc_preview_request, ptc_physical_feedback, ptc_atelier_action_ready


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


    def test_ptc_action_ready_large_verified_preview(self):
        # PTC is not a brush operation. At 2049 px, the brush gate rejects
        # the thumbnail, but the native PTC inspector can inspect the source.
        from native_atelier_tk_v34 import brush_preview_request
        self.subject.preview = SimpleNamespace(status="READY_PNG",
                                               png=b"p" * 40,
                                               width_px=2049, height_px=1)
        self.assertIsNone(brush_preview_request(
            self.snapshot, self.subject, self.path))
        self.assertTrue(ptc_atelier_action_ready(
            self.snapshot, self.subject, self.path))

    def test_ptc_action_ready_fails_closed_without_verified_preview(self):
        self.subject.preview = SimpleNamespace(status="READY_PNG",
                                               png=b"p" * 40,
                                               width_px=2049, height_px=1)
        self.assertTrue(ptc_atelier_action_ready(
            self.snapshot, self.subject, self.path))
        self.subject.proof_status = "unverified"
        self.assertFalse(ptc_atelier_action_ready(
            self.snapshot, self.subject, self.path))
        self.subject.proof_status = "verified"
        self.snapshot.sha256 = "invalid"
        self.assertFalse(ptc_atelier_action_ready(
            self.snapshot, self.subject, self.path))
        self.snapshot.sha256 = "a" * 64
        self.subject.preview.status = "SOURCE_CHANGED"
        self.assertFalse(ptc_atelier_action_ready(
            self.snapshot, self.subject, self.path))
        self.subject.preview.status = "READY_PNG"
        self.subject.preview.png = b"tiny"
        self.assertFalse(ptc_atelier_action_ready(
            self.snapshot, self.subject, self.path))
        self.subject.preview.png = b"p" * 40
        self.subject.preview.width_px = True
        self.assertFalse(ptc_atelier_action_ready(
            self.snapshot, self.subject, self.path))


    def test_physical_limits_before_publish(self):
        request = self.request("50")
        self.assertIsNone(ptc_physical_feedback(request, 1000, 1000))
        self.assertIn("2 400 ppp", ptc_physical_feedback(self.request("0,01"), 1000, 1000))
        self.assertIn("moins de 1 ppp", ptc_physical_feedback(self.request("10000"), 100, 100))
        self.assertIn("Hauteur", ptc_physical_feedback(self.request("1000"), 100, 2000))
        self.assertIn("réexaminer", ptc_physical_feedback(request, True, 100))
        self.assertIn("réexaminer", ptc_physical_feedback(request, 5000, 5000))

    def test_open_folder_requires_existing_png_and_explicit_opener(self):
        from native_ptc_dialog_tk_v35 import open_export_folder
        opened = []
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            png = root / "export.png"
            self.assertFalse(open_export_folder(str(png), opened.append))
            self.assertEqual(opened, [])
            png.write_bytes(b"synthetic")
            self.assertTrue(open_export_folder(str(png), opened.append))
            self.assertEqual(opened, [str(root)])
            self.assertFalse(open_export_folder(str(root / "other.svg"), opened.append))
            self.assertFalse(open_export_folder("relative.png", opened.append))
            self.assertEqual(opened, [str(root)])

    def test_relative_project_path_rejected(self):
        self.assertIsNone(ptc_preview_request(
            self.snapshot, self.subject, "relative.smartsvg", "30"))


    def test_dialog_preview_admission_is_read_only(self):
        from native_ptc_dialog_tk_v35 import preview_identity
        self.subject.preview = SimpleNamespace(width_px=1000, height_px=1000)
        request, issue = preview_identity(self.snapshot, self.subject, self.path, "50,25")
        self.assertIsNone(issue)
        self.assertEqual(request["width_mm"], 50.25)
        # The inspector's 1000px thumbnail is not the full-resolution
        # source. The read-only native inspect must decide physical eligibility.
        request, issue = preview_identity(self.snapshot, self.subject, self.path, "0,01")
        self.assertIsNone(issue)
        self.assertEqual(request["width_mm"], 0.01)

    def test_dialog_does_not_infer_source_geometry_from_thumbnail(self):
        from native_ptc_dialog_tk_v35 import preview_identity
        self.subject.preview = SimpleNamespace(width_px=1, height_px=1)
        request, issue = preview_identity(self.snapshot, self.subject, self.path, "100")
        self.assertIsNone(issue)
        self.assertEqual(request["subject_id"], self.subject.subject_id)

    def test_dialog_rejects_stale_or_missing_preview(self):
        from native_ptc_dialog_tk_v35 import preview_identity
        self.assertIsNone(preview_identity(self.snapshot, self.subject, self.path, "50")[0])
        self.subject.preview = SimpleNamespace(width_px=100, height_px=100)
        self.snapshot.sha256 = "invalid"
        request, issue = preview_identity(self.snapshot, self.subject, self.path, "50")
        self.assertIsNone(request)
        self.assertIn("non vérifié", issue)




class PTCDialogTkFlowTests(unittest.TestCase):
    """Exercise real dialog callbacks with a deterministic headless Tk facade."""

    def test_inspect_width_change_during_backend_call_never_enables_publish(self):
        from unittest.mock import patch
        import native_ptc_dialog_tk_v35 as module

        class Variable:
            instances = []
            def __init__(self, value=""):
                self.value = value
                self.traces = []
                Variable.instances.append(self)
            def get(self):
                return self.value
            def set(self, value):
                self.value = value
                for callback in self.traces:
                    callback()
            def trace_add(self, _mode, callback):
                self.traces.append(callback)

        class Widget:
            buttons = {}
            def __init__(self, *_args, **kwargs):
                self.command = kwargs.get("command")
                self.state = kwargs.get("state")
                if "text" in kwargs and self.command:
                    Widget.buttons[kwargs["text"]] = self
            def pack(self, **_kwargs):
                pass
            def configure(self, **kwargs):
                if "state" in kwargs:
                    self.state = kwargs["state"]
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

        tk = SimpleNamespace(Toplevel=Widget, StringVar=Variable,
                             PhotoImage=Widget, TclError=RuntimeError)
        ttk = SimpleNamespace(Frame=Widget, Label=Widget, Entry=Widget, Button=Widget)
        subject = SimpleNamespace(subject_id="subject-" + "b" * 32,
                                  proof_status="verified",
                                  preview=SimpleNamespace(width_px=10, height_px=10))
        snapshot = SimpleNamespace(sha256="a" * 64)
        panel = SimpleNamespace(
            tk=tk, ttk=ttk, _closed=False, busy=False,
            history_requires_review=False, has_open_brush=False,
            parent=Widget(), subjects={subject.subject_id: subject},
            selection=Variable(subject.subject_id),
            _project_path=str(Path.cwd().resolve() / "synthetic.smartsvg"),
            snapshot=snapshot,
        )
        def changing_inspect(**_kwargs):
            Variable.instances[-3].set("200")
            return {"status": "PTC_PREVIEW_READY", "preview_png_rgba": b"png",
                    "output_sha256": "c" * 64, "width_mm": 100,
                    "height_mm": 100, "low_resolution_warning": False}

        # width, status, destination are the last three variables created.
        with patch.object(module, "inspect_native_ptc_png", side_effect=changing_inspect):
            self.assertTrue(module.show_ptc_dialog(panel))
            Widget.buttons["Examiner"].command()
        self.assertEqual(Widget.buttons["Choisir et publier…"].state, "disabled")
        self.assertIn("périmé", Variable.instances[-2].get())
        Widget.buttons["Fermer"].command()
        self.assertEqual(Widget.buttons["Choisir et publier…"].state, "disabled")


    def test_publish_with_queued_width_change_disables_stale_folder_action(self):
        from unittest.mock import patch
        from hashlib import sha256
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
                pass

        tk = SimpleNamespace(Toplevel=Widget, StringVar=Variable,
                             PhotoImage=Widget, TclError=RuntimeError)
        ttk = SimpleNamespace(Frame=Widget, Label=Widget, Entry=Widget, Button=Widget)
        subject = SimpleNamespace(subject_id="subject-" + "b" * 32,
                                  proof_status="verified",
                                  preview=SimpleNamespace(width_px=10, height_px=10))
        snapshot = SimpleNamespace(sha256="a" * 64)
        panel = SimpleNamespace(
            tk=tk, ttk=ttk, _closed=False, busy=False,
            history_requires_review=False, has_open_brush=False,
            parent=Widget(), subjects={subject.subject_id: subject},
            selection=Variable(subject.subject_id),
            _project_path=str(Path.cwd().resolve() / "synthetic.smartsvg"),
            snapshot=snapshot,
        )
        payload = b"synthetic png bytes"
        digest = sha256(payload).hexdigest()
        def preview(**_kwargs):
            return {"status": "PTC_PREVIEW_READY", "preview_png_rgba": payload,
                    "output_sha256": digest, "width_mm": 100,
                    "height_mm": 100, "low_resolution_warning": False}
        with tempfile.TemporaryDirectory() as directory:
            target = str(Path(directory) / "export.png")
            def publish(**_kwargs):
                Path(target).write_bytes(payload)
                # Simulate a queued Tk width callback while native code runs.
                Variable.created[-3].set("200")
                return {"persisted": True}
            with (patch.object(module, "inspect_native_ptc_png", side_effect=preview),
                  patch.object(module, "publish_native_ptc_png", side_effect=publish),
                  patch.object(module.filedialog, "asksaveasfilename", return_value=target),
                  patch.object(module.messagebox, "askyesno", return_value=True)):
                self.assertTrue(module.show_ptc_dialog(panel))
                Widget.buttons["Examiner"].command()
                self.assertEqual(Widget.buttons["Choisir et publier…"].state, "normal")
                Widget.buttons["Choisir et publier…"].command()
            self.assertEqual(Path(target).read_bytes(), payload)
            self.assertEqual(Widget.buttons["Ouvrir le dossier"].state, "disabled")
            self.assertIn("vérifier le fichier", Variable.created[-2].get())
            self.assertEqual(Widget.buttons["Choisir et publier…"].state, "disabled")

if __name__ == "__main__":
    unittest.main()
