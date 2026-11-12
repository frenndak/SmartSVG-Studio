"""Native Atelier V1 brush-history display: pinned, read-only, fail-closed."""
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from native_atelier_tk_v34 import NativeAtelierPanel


class Cell:
    def __init__(self):
        self.value = ""

    def set(self, value):
        self.value = value

    def get(self):
        return self.value


class AtelierHistoryStatusTests(unittest.TestCase):
    def setUp(self):
        self.panel = NativeAtelierPanel.__new__(NativeAtelierPanel)
        self.panel.snapshot = SimpleNamespace(sha256="a" * 64)
        self.panel._project_path = str(Path.cwd() / "synthetic.smartsvg")
        self.panel.history = Cell()
        self.calls = []

        def inspect(**kwargs):
            self.calls.append(kwargs)
            return {
                "schema": "smartsvg-native-brush-history-status/1",
                "project_sha256": "a" * 64,
                "undo_available": True,
                "redo_available": False,
                "persisted": False,
                "cricut_certified": False,
                "internal_private_path": "/private/never-render",
            }
        self.panel._history_fn = inspect

    def test_pinned_status_is_visible_without_private_metadata_or_write(self):
        self.panel._refresh_history()
        message = self.panel.history.get()
        self.assertIn("lecture seule", message)
        self.assertIn("Annulation possible : oui", message)
        self.assertIn("Rétablissement possible : non", message)
        self.assertIn("non encore raccordées", message)
        self.assertNotIn("/private/", message)
        self.assertEqual(self.calls, [{
            "project_path": self.panel._project_path,
            "expected_sha256": "a" * 64,
        }])

    def test_invalid_catalog_path_and_revision_never_call_history(self):
        for path, revision, invalid in (
            ("synthetic.smartsvg", "a" * 64, False),
            (self.panel._project_path, "bad", False),
            (self.panel._project_path, "a" * 64, True),
            (None, "a" * 64, False),
        ):
            with self.subTest(path=path, revision=revision, invalid=invalid):
                self.panel._project_path = path
                self.panel.snapshot = SimpleNamespace(sha256=revision)
                self.panel._refresh_history(invalid_catalog=invalid)
                self.assertIn("indisponible", self.panel.history.get())
        self.assertEqual(self.calls, [])

    def test_stale_untrusted_or_failed_history_never_claims_undo(self):
        for result in (
            None, {}, {"schema": "forged"},
            {
                "schema": "smartsvg-native-brush-history-status/1",
                "project_sha256": "b" * 64,
                "undo_available": True, "redo_available": True,
                "persisted": False,
            },
            {
                "schema": "smartsvg-native-brush-history-status/1",
                "project_sha256": "a" * 64,
                "undo_available": 1, "redo_available": False,
                "persisted": False,
            },
        ):
            with self.subTest(result=result):
                self.panel._history_fn = lambda **kwargs: result
                self.panel._refresh_history()
                self.assertIn("indisponible", self.panel.history.get())
                self.assertNotIn("possible : oui", self.panel.history.get())
        def failed(**kwargs):
            raise RuntimeError("/home/private/client.smartsvg")
        self.panel._history_fn = failed
        self.panel._refresh_history()
        self.assertIn("indisponible", self.panel.history.get())
        self.assertNotIn("/home", self.panel.history.get())

    def test_forged_cricut_certification_fails_closed(self):
        valid = {
            "schema": "smartsvg-native-brush-history-status/1",
            "project_sha256": "a" * 64,
            "undo_available": True,
            "redo_available": False,
            "persisted": False,
        }
        for certification in (True, None, "false", 0):
            with self.subTest(certification=certification):
                self.panel._history_fn = lambda **kwargs: {
                    **valid, "cricut_certified": certification,
                }
                self.panel._refresh_history()
                self.assertIn("indisponible", self.panel.history.get())
                self.assertNotIn("Annulation possible : oui", self.panel.history.get())
        self.panel._history_fn = lambda **kwargs: valid
        self.panel._refresh_history()
        self.assertIn("indisponible", self.panel.history.get())

    def test_real_tk_healthy_v1_journal_read_is_non_destructive(self):
        import tkinter as tk
        from tkinter import ttk
        from smartsvg_core.project_workspace_g22 import ManagedWorkspace
        from smartsvg_core.native_atelier_v34 import AtelierSnapshot
        from test_v34_native_subject_preview import _png

        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("No graphical Tk session available")
        self.addCleanup(root.destroy)
        root.withdraw()
        with tempfile.TemporaryDirectory() as directory:
            workspace = ManagedWorkspace(directory)
            created = workspace.create(
                "history-ui", _png(), profile="Sticker - contour du sujet")
            project = workspace.root / "history-ui.smartsvg"
            before = project.read_bytes()
            panel = NativeAtelierPanel(root, tk, ttk)
            self.addCleanup(panel.shutdown)
            panel.load(AtelierSnapshot("history-ui", created["sha256"], ()),
                       project_path=str(project))
            message = panel.history.get()
            self.assertIn("lecture seule", message)
            self.assertIn("Annulation possible : non", message)
            self.assertIn("Rétablissement possible : non", message)
            self.assertEqual(project.read_bytes(), before)
            panel.load(None)
            self.assertIn("indisponible", panel.history.get())
            self.assertEqual(project.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
