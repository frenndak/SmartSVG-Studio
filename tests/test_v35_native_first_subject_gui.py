"""W02 Tk first alpha subject: approval, stale contexts and real desktop wiring."""
from concurrent.futures import Future
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[1] / "engine"
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))

from native_first_subject_tk_v35 import NativeFirstSubjectFlow, show_first_subject_confirmation
from smartsvg_core.native_first_subject_v35 import NativeFirstSubjectError
from smartsvg_core.native_first_subject_v35 import (
    inspect_first_alpha_subject, confirm_first_alpha_subject,
)
from smartsvg_core.project_archive import load_project
from smartsvg_core.project_workspace_g22 import ManagedWorkspace
from test_v35_native_first_subject import png
from test_v34_native_app_shell import DesktopShellIntegrationTests


class Root:
    def __init__(self):
        self.pending = []

    def after(self, _delay, callback):
        self.pending.append(callback)

    def tick(self):
        assert self.pending, "no Tk callback"
        self.pending.pop(0)()


class DeferredExecutor:
    def __init__(self, **kwargs):
        self.tasks = []
        self.closed = False

    def submit(self, callback):
        future = Future()
        self.tasks.append((callback, future))
        return future

    def execute(self):
        callback, future = self.tasks.pop(0)
        try:
            future.set_result(callback())
        except BaseException as exc:
            future.set_exception(exc)

    def shutdown(self, **kwargs):
        self.closed = True


class FakeMessagebox:
    def __init__(self, answer=True, during=None):
        self.answer, self.during = answer, during
        self.calls = []

    def askyesno(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        if self.during:
            self.during()
        return self.answer


class FirstSubjectTkFlowTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = str(Path(temp.name).resolve() / "alpha.smartsvg")
        self.sha = "a" * 64
        self.candidate = "b" * 64
        self.status = []
        self.saved = []
        self.state = {"guard": True, "note": "unchanged"}
        self.root = Root()
        self.dialog = FakeMessagebox()
        self.pool = DeferredExecutor()
        self.writes = []
        self.preview = {
            "status": "ALPHA_PREVIEW_READY",
            "project_sha256": self.sha,
            "candidate_sha256": self.candidate,
            "preview_only": True,
            "persisted": False,
            "manual_confirmation_required": True,
            "selection_kind": "whole_rgba_alpha",
            "cricut_certified": False,
            "dimensions_px": [6, 5],
        }
        self.receipt = {
            "status": "FIRST_SUBJECT_CREATED",
            "project_sha256": "c" * 64,
            "subject_id": "subject-" + "d" * 32,
            "persisted": True,
        }

    def make(self, inspect=None, confirm=None):
        def write(**kwargs):
            self.writes.append(kwargs)
            return self.receipt
        self.flow = NativeFirstSubjectFlow(
            self.root,
            guard=lambda path, sha: (self.state["guard"] and
                                     path == self.path and sha == self.sha),
            checkpoint=lambda: self.state["note"],
            confirm_preview=self.dialog.askyesno,
            on_saved=self.saved.append, on_status=self.status.append,
            inspect_fn=inspect or (lambda **_: self.preview),
            confirm_fn=confirm or write,
            executor_factory=lambda **_: self.pool)
        self.addCleanup(self.flow.shutdown)
        return self.flow

    def inspect_done(self):
        self.pool.execute()
        self.root.tick()

    def test_explicit_yes_persists_once_and_refuses_reentrant_start(self):
        flow = self.make()
        self.assertTrue(flow.start(project_path=self.path, expected_sha256=self.sha))
        self.assertFalse(flow.start(project_path=self.path, expected_sha256=self.sha))
        self.assertEqual(self.writes, [])
        self.inspect_done()
        self.assertTrue(flow.busy)
        self.assertEqual(len(self.dialog.calls), 1)
        self.assertEqual(self.writes, [])
        self.pool.execute()
        self.root.tick()
        self.assertFalse(flow.busy)
        self.assertEqual(self.saved, [self.receipt])
        self.assertEqual(len(self.writes), 1)
        self.assertIs(self.writes[0]["confirmed"], True)
        self.assertEqual(self.writes[0]["expected_sha256"], self.sha)
        self.assertEqual(self.writes[0]["candidate_sha256"], self.candidate)

    def test_decline_cannot_run_writer(self):
        self.dialog.answer = False
        flow = self.make()
        self.assertTrue(flow.start(project_path=self.path, expected_sha256=self.sha))
        self.inspect_done()
        self.assertEqual(self.writes, [])
        self.assertFalse(flow.busy)
        self.assertFalse(flow.requires_review)
        self.assertEqual(self.saved, [])

    def test_modal_note_edit_invalidates_confirmation_without_discard(self):
        self.dialog.during = lambda: self.state.update(note="edited in dialog")
        flow = self.make()
        flow.start(project_path=self.path, expected_sha256=self.sha)
        self.inspect_done()
        self.assertEqual(self.state["note"], "edited in dialog")
        self.assertFalse(flow.busy)
        self.assertEqual(self.writes, [])
        self.assertEqual(self.saved, [])
        self.assertIn("modifié", self.status[-1])

    def test_revoked_project_and_malformed_preview_never_write(self):
        flow = self.make()
        flow.start(project_path=self.path, expected_sha256=self.sha)
        self.state["guard"] = False
        self.inspect_done()
        self.assertFalse(flow.busy)
        self.assertFalse(self.dialog.calls)
        self.assertEqual(self.writes, [])
        self.state["guard"] = True
        flow.start(project_path=self.path, expected_sha256=self.sha)
        self.preview["candidate_sha256"] = "invalid"
        self.inspect_done()
        self.assertEqual(self.writes, [])
        self.assertEqual(len(self.dialog.calls), 0)

    def test_write_ack_lost_marks_uncertain_without_retry(self):
        def lost(**kwargs):
            self.writes.append(kwargs)
            raise NativeFirstSubjectError("SUBJECT_BINDING_OUTCOME_UNCERTAIN")
        flow = self.make(confirm=lost)
        flow.start(project_path=self.path, expected_sha256=self.sha)
        self.inspect_done()
        self.pool.execute()
        self.root.tick()
        self.assertEqual(len(self.writes), 1)
        self.assertTrue(flow.requires_review)
        self.assertFalse(flow.start(project_path=self.path, expected_sha256=self.sha))
        flow.acknowledge_reinspection(self.path, healthy=False)
        self.assertTrue(flow.requires_review)
        flow.acknowledge_reinspection(self.path, healthy=True)
        self.assertFalse(flow.requires_review)

    def test_unverified_receipt_does_not_refresh_ui(self):
        self.receipt["persisted"] = False
        flow = self.make()
        flow.start(project_path=self.path, expected_sha256=self.sha)
        self.inspect_done()
        self.pool.execute()
        self.root.tick()
        self.assertTrue(flow.requires_review)
        self.assertEqual(self.saved, [])

    def test_submit_rejection_fails_closed_and_does_not_retry(self):
        pool = self.pool
        def reject(_):
            raise RuntimeError("worker offline")
        pool.submit = reject
        flow = self.make()
        self.assertFalse(flow.start(project_path=self.path, expected_sha256=self.sha))
        self.assertFalse(flow.busy)
        self.assertEqual(self.writes, [])
        self.assertEqual(self.saved, [])

    def test_shutdown_cannot_deliver_result_to_destroyed_widgets(self):
        flow = self.make()
        flow.start(project_path=self.path, expected_sha256=self.sha)
        before = len(self.status)
        flow.shutdown()
        self.pool.execute()
        self.root.tick()
        self.assertEqual(len(self.status), before)
        self.assertEqual(self.saved, [])

    def test_failed_completion_poll_does_not_persist_first_subject(self):
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as directory:
            workspace = ManagedWorkspace(directory)
            created = workspace.create(
                "alpha-no-poll", png(), profile="Sticker - contour du sujet",
                source_provenance="manual_native_png_import")
            path = workspace.root / "alpha-no-poll.smartsvg"
            self.path = str(path)
            self.sha = created["sha256"]
            before = path.read_bytes()
            flow = self.make(inspect=inspect_first_alpha_subject,
                             confirm=confirm_first_alpha_subject)
            self.assertTrue(flow.start(project_path=self.path, expected_sha256=self.sha))

            self.pool.execute()  # Real read-only alpha proposal completed.
            poll_failed = False
            with patch.object(self.root, "after", side_effect=RuntimeError("poll unavailable")):
                try:
                    self.root.tick()  # Confirmation succeeds; scheduling the write poll fails.
                except RuntimeError:
                    poll_failed = True
            self.assertEqual(len(self.dialog.calls), 1)
            self.pool.execute()  # A queued worker may have survived the failure.
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(load_project(path).subjects, ())
            self.assertFalse(poll_failed)
            self.assertFalse(flow.busy)
            self.assertEqual(self.saved, [])


class VisualFirstSubjectConfirmationTests(unittest.TestCase):
    def test_preview_renders_before_cancel_or_explicit_confirmation(self):
        import tkinter as tk
        from tkinter import ttk

        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest("No graphical Tk session available")
        self.addCleanup(root.destroy)
        with tempfile.TemporaryDirectory() as directory:
            workspace = ManagedWorkspace(directory)
            created = workspace.create(
                "mask-preview", png(), profile="Sticker - contour du sujet")
            path = workspace.root / "mask-preview.smartsvg"
            proposal = inspect_first_alpha_subject(
                project_path=str(path), expected_sha256=created["sha256"])

            def descendants(widget):
                for child in widget.winfo_children():
                    yield child
                    yield from descendants(child)

            for label, expected in (("Annuler", False), ("Créer le sujet", True)):
                observed = []
                deadline = time.monotonic() + 4

                def click():
                    window = root.grab_current()
                    if window is None:
                        if time.monotonic() < deadline:
                            root.after(20, click)
                        else:
                            for child in root.winfo_children():
                                child.destroy()
                        return
                    widgets = list(descendants(window))
                    observed.append(any(isinstance(child, ttk.Label) and
                                        child.cget("image") and child.winfo_viewable()
                                        for child in widgets))
                    for child in widgets:
                        if isinstance(child, ttk.Button) and child.cget("text") == label:
                            child.invoke()
                            return
                    window.destroy()

                root.after(20, click)
                self.assertIs(show_first_subject_confirmation(root, tk, ttk, proposal), expected)
                self.assertEqual(observed, [True])
            self.assertEqual(load_project(path).subjects, ())


class RealDesktopFirstSubjectTests(unittest.TestCase):
    def run_desktop(self, scenario, path):
        with patch("standalone_desktop_v34.show_first_subject_confirmation",
                   return_value=True) as confirmation:
            DesktopShellIntegrationTests().run_desktop(
                scenario, first_project=str(path), discard_notes=lambda **_: True)
        self.assertGreaterEqual(confirmation.call_count, 1)
        for call in confirmation.call_args_list:
            self.assertTrue(call.args[3]["mask_preview_png_l8"].startswith(b"\x89PNG"))

    def test_first_subject_write_can_recover_interrupted_backup_without_losing_notes(self):
        from unittest.mock import patch
        from smartsvg_core import project_recovery

        with tempfile.TemporaryDirectory() as directory:
            workspace = ManagedWorkspace(directory)
            workspace.create("alpha-interrupted", png(), profile="Sticker - contour du sujet")
            path = workspace.root / "alpha-interrupted.smartsvg"
            real_copy = project_recovery._atomic_copy
            errors = []
            receive = NativeFirstSubjectFlow._receive

            def fail_rotation(source, destination, **checks):
                if destination == path.with_suffix(".previous.smartsvg"):
                    raise OSError("synthetic backup rotation failure")
                return real_copy(source, destination, **checks)

            def record_result(flow, phase, generation, future):
                if future.done() and (error := future.exception()) is not None:
                    while error is not None:
                        errors.append(repr(error))
                        error = error.__cause__
                receive(flow, phase, generation, future)

            def scenario(root, state):
                def pump_until(predicate):
                    deadline = time.monotonic() + 10
                    while not predicate():
                        if time.monotonic() >= deadline:
                            self.fail(
                                f"Subject: {state.atelier.first_subject_status.get()!r}. "
                                f"Recovery: {state.recovery.status.get()!r}. "
                                f"Atelier: {state.atelier.project.get()!r}. "
                                f"Worker errors: {errors!r}.")
                        if root.pending:
                            root.pending.pop(0)()
                        # The simulated scheduler runs every callback immediately.
                        # Yield between polls so ZIP I/O can progress on Windows.
                        time.sleep(0.005)

                state.jobs.futures[-1].result(timeout=10)
                root.pending.pop(0)()
                state.notes.editor.insert("1.0", "Note à préserver")
                with patch.object(project_recovery, "_atomic_copy", side_effect=fail_rotation):
                    self.assertTrue(state.atelier.create_first_subject())
                    pump_until(lambda: "peut-être effectuée" in state.atelier.first_subject_status.get())
                pending = path.with_suffix(".pending-backup.smartsvg")
                self.assertTrue(pending.is_file())
                staged = pending.read_bytes()
                partially_saved = path.read_bytes()
                self.assertEqual(len(load_project(path).masks), 1)
                self.assertEqual(load_project(path).subjects, ())
                root.events["<F5>"](None)
                pump_until(lambda: state.recovery.plan is not None)
                self.assertEqual(state.recovery.plan.outcome, "pending_backup_finalized")
                self.assertEqual(state.notes.editor.get(), "Note à préserver")
                state.recovery.start()
                self.assertIsNotNone(state.recovery.future)
                pump_until(lambda: state.atelier.snapshot is not None)
                self.assertFalse(pending.exists())
                self.assertEqual(path.read_bytes(), partially_saved)
                self.assertEqual(path.with_suffix(".previous.smartsvg").read_bytes(), staged)
                self.assertEqual(state.notes.editor.get(), "Note à préserver")
                self.assertTrue(state.atelier.create_first_subject())
                pump_until(lambda: state.atelier.snapshot is not None and
                           len(state.atelier.snapshot.subjects) == 1)
                self.assertEqual(state.notes.editor.get(), "Note à préserver")

            with patch.object(NativeFirstSubjectFlow, "_receive", record_result):
                self.run_desktop(scenario, path)

    def test_verified_first_subject_with_failed_host_reread_keeps_notes_and_reports_write(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = ManagedWorkspace(directory)
            workspace.create("alpha-read-fail", png(), profile="Sticker - contour du sujet")
            path = workspace.root / "alpha-read-fail.smartsvg"

            def scenario(root, state):
                state.jobs.futures[-1].result(timeout=10)
                root.pending.pop(0)()
                state.notes.editor.insert("1.0", "Note locale")
                original_loader = state.jobs._read

                def fail_read(_path):
                    raise OSError("synthetic host read failure")

                state.jobs._read = fail_read
                self.assertTrue(state.atelier.create_first_subject())
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    if root.pending:
                        root.pending.pop(0)()
                    if len(state.jobs.futures) == 2 and not root.pending:
                        break
                    time.sleep(0.005)
                self.assertEqual(len(load_project(path).subjects), 1)
                self.assertIn("enregistré", state.atelier.first_subject_status.get())
                self.assertIn("relecture", state.atelier.first_subject_status.get())
                self.assertEqual(state.notes.editor.get(), "Note locale")
                state.jobs._read = original_loader
                root.events["<F5>"](None)
                state.jobs.futures[-1].result(timeout=10)
                root.pending.pop(0)()
                self.assertEqual(state.notes.editor.get(), "Note locale")
                state.notes.save()
                self.assertIsNotNone(state.notes.future)
                state.notes.future.result(timeout=10)
                root.pending.pop(0)()
                state.jobs.futures[-1].result(timeout=10)
                root.pending.pop(0)()
                self.assertEqual(load_project(path).document["notes"], "Note locale")

            self.run_desktop(scenario, path)

    def test_real_png_creates_subject_from_atelier_button_and_reopens(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = ManagedWorkspace(directory)
            source = png()
            created = workspace.create(
                "alpha-gui", source, profile="Sticker - contour du sujet",
                source_provenance="manual_native_png_import")
            path = workspace.root / "alpha-gui.smartsvg"
            before = load_project(path, expected_sha256=created["sha256"])
            self.assertEqual(len(before.subjects), 0)

            def scenario(root, state):
                # Read the active V1 archive via the actual desktop host.
                state.jobs.futures[-1].result(timeout=20)
                root.pending.pop(0)()
                panel = state.atelier
                self.assertEqual(panel.first_subject_button.options["state"], "normal")
                self.assertTrue(panel.create_first_subject())
                self.assertFalse(panel.create_first_subject())
                self.assertIsNone(panel.snapshot.subjects[0] if panel.snapshot.subjects else None)
                deadline = time.monotonic() + 30
                while time.monotonic() < deadline:
                    if root.pending:
                        root.pending.pop(0)()
                    else:
                        time.sleep(0.005)
                    if panel.snapshot is not None and len(panel.snapshot.subjects) == 1:
                        break
                else:
                    self.fail("native Subject was not visible after verified reread")
                self.assertEqual(len(panel.snapshot.subjects), 1)
                self.assertEqual(panel.snapshot.subjects[0].proof_status, "verified")
                self.assertEqual(panel.first_subject_button.options["state"], "disabled")
                self.assertEqual(panel.selection.get(), panel.snapshot.subjects[0].subject_id)
                reopened = load_project(path)
                self.assertEqual(reopened.sources, before.sources)
                source_id = before.sources[0].source_id
                source_path = before.source_paths[source_id]
                self.assertEqual(reopened.resources[source_path],
                                 before.resources[source_path])
                self.assertEqual(len(reopened.masks), 1)
                self.assertTrue(panel.brush_button.options["state"] == "normal")

            self.run_desktop(scenario, path)
            self.assertEqual(len(load_project(path).subjects), 1)


if __name__ == "__main__":
    unittest.main()
