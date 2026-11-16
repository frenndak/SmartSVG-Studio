"""Native history controls: explicit commands, async outcomes and no fake success."""
from concurrent.futures import Future
from pathlib import Path
from types import SimpleNamespace
import importlib.util
import sys
import time
import unittest

ENGINE = Path(__file__).resolve().parents[1] / 'engine'
sys.path.insert(0, str(ENGINE)) if str(ENGINE) not in sys.path else None
from native_atelier_tk_v34 import NativeAtelierPanel

SUBJECT = 'subject-' + 'a' * 32
OTHER = 'subject-' + 'b' * 32


class Cell:
    def __init__(self, value=''): self.value = value
    def get(self): return self.value
    def set(self, value): self.value = value


class Button:
    def __init__(self): self.state = 'disabled'
    def configure(self, **kwargs): self.state = kwargs.get('state', self.state)


class Worker:
    def __init__(self): self.calls = []; self.future = Future()
    def submit(self, fn, **kwargs):
        self.calls.append((fn, kwargs))
        return self.future
    def shutdown(self, **kwargs): pass


def status(revision='a' * 64, action='undo', subject=SUBJECT):
    return dict(schema='smartsvg-native-brush-history-status/1',
                project_sha256=revision, undo_available=action == 'undo',
                redo_available=action == 'redo',
                **{action + '_subject_id': subject},
                persisted=False, cricut_certified=False)


class NativeHistoryActionTests(unittest.TestCase):
    def setUp(self):
        p = self.panel = NativeAtelierPanel.__new__(NativeAtelierPanel)
        self.scheduled, self.receipts = [], []
        p.parent = SimpleNamespace(after=lambda _ms, fn: self.scheduled.append(fn))
        p.tk = SimpleNamespace(TclError=RuntimeError)
        p.snapshot = SimpleNamespace(project_id='example', sha256='a' * 64)
        p._project_path = str(Path.cwd() / 'example.smartsvg')
        p.subjects = {SUBJECT: SimpleNamespace(subject_id=SUBJECT, proof_status='verified')}
        p.selection = Cell(SUBJECT)
        p.subject_position = Cell()
        p.history, p.project, p.details = Cell(), Cell(), Cell()
        p.undo_button, p.redo_button, p.brush_button = Button(), Button(), Button()
        p.picker, p.previous_button, p.next_button = Button(), Button(), Button()
        p._brush_class = None
        p._brush_panel = p._brush_dialog = p._brush_key = None
        p._closed = p._history_confirming = p._history_needs_review = False
        p._history_generation = 0
        p._history_future = p._history_pending = p._history_status = None
        p._history_worker = Worker()
        p._history_fn = lambda **kw: status()
        p._history_change_fn = lambda **kw: None
        p._confirm_history_fn = lambda *_args: True
        p._can_history = lambda: True
        p._on_saved = self.receipts.append
        p._refresh_history()

    def receipt(self, **changes):
        request = self.panel._history_worker.calls[-1][1]
        result = dict(status='brush_history_' + request['action'],
                      project_sha256='c' * 64, subject_id=SUBJECT,
                      action=request['action'], command_id=request['command_id'],
                      persisted=True, cricut_certified=False)
        result.update(changes)
        return result

    def finish(self, receipt=None, error=None):
        future = self.panel._history_worker.future
        future.set_exception(error) if error else future.set_result(receipt)
        self.scheduled.pop(0)()

    def test_confirmed_undo_is_async_unique_and_delivers_only_verified_receipt(self):
        self.assertTrue(self.panel.undo_brush())
        self.assertTrue(self.panel.busy)
        self.assertEqual(self.receipts, [])
        self.assertEqual(self.panel.undo_button.state, 'disabled')
        self.assertFalse(self.panel.undo_brush())
        self.assertEqual(len(self.panel._history_worker.calls), 1)
        request = self.panel._history_worker.calls[0][1]
        self.assertEqual(request['expected_sha256'], 'a' * 64)
        self.assertEqual(request['subject_id'], SUBJECT)
        self.assertIs(request['confirmed'], True)
        self.finish(self.receipt())
        self.assertFalse(self.panel.busy)
        self.assertEqual(len(self.receipts), 1)
        # Until the host actually re-inspects, an old CAS can never be reused.
        self.assertTrue(self.panel.history_requires_review)
        self.assertFalse(self.panel.undo_brush())

    def test_non_boolean_or_declined_confirmation_never_submits(self):
        for answer in (False, None, 1, 'yes', object()):
            with self.subTest(answer=repr(answer)):
                self.panel._confirm_history_fn = lambda *_args: answer
                self.assertFalse(self.panel.undo_brush())
                self.assertFalse(self.panel.busy)
        self.assertEqual(self.panel._history_worker.calls, [])

    def test_changed_selection_revision_or_generation_during_modal_never_submits(self):
        for kind in ('subject', 'revision', 'generation', 'closed'):
            with self.subTest(kind=kind):
                self.setUp()
                def change(*_args):
                    if kind == 'subject': self.panel.selection.set(OTHER)
                    elif kind == 'revision': self.panel.snapshot.sha256 = 'b' * 64
                    elif kind == 'closed': self.panel._closed = True
                    else: self.panel._history_generation += 1
                    return True
                self.panel._confirm_history_fn = change
                self.assertFalse(self.panel.undo_brush())
                self.assertEqual(self.panel._history_worker.calls, [])

    def test_other_subject_unverified_source_or_open_brush_is_not_actionable(self):
        for kind in ('other', 'unverified', 'brush', 'writer', 'callback'):
            with self.subTest(kind=kind):
                self.setUp()
                if kind == 'other': self.panel.selection.set(OTHER)
                elif kind == 'unverified': self.panel.subjects[SUBJECT].proof_status = 'unverified'
                elif kind == 'brush': self.panel._brush_dialog = object()
                elif kind == 'writer': self.panel._can_history = lambda: False
                else: self.panel._on_saved = None
                self.assertFalse(self.panel.undo_brush())
                self.assertEqual(self.panel._history_worker.calls, [])

    def test_redo_uses_its_own_verified_target_and_action(self):
        self.panel._history_fn = lambda **kw: status(action='redo')
        self.panel._refresh_history()
        self.assertFalse(self.panel.undo_brush())
        self.assertTrue(self.panel.redo_brush())
        self.assertEqual(self.panel._history_worker.calls[0][1]['action'], 'redo')
        self.finish(self.receipt())
        self.assertEqual(self.receipts[0]['action'], 'redo')

    def test_failed_or_forged_result_blocks_writes_without_claiming_success(self):
        for kind in ('exception', 'project', 'subject', 'action', 'command', 'persisted', 'certified'):
            with self.subTest(kind=kind):
                self.setUp(); self.panel.undo_brush()
                if kind == 'exception': self.finish(error=OSError('/private/project'))
                else:
                    changes = {'project': {'project_sha256': 'a' * 64},
                               'subject': {'subject_id': OTHER},
                               'action': {'action': 'redo'},
                               'command': {'command_id': 'other'},
                               'persisted': {'persisted': 1},
                               'certified': {'cricut_certified': True}}[kind]
                    self.finish(self.receipt(**changes))
                self.assertEqual(self.receipts, [])
                self.assertTrue(self.panel.history_requires_review)
                self.assertFalse(self.panel.busy)
                self.assertFalse(self.panel.undo_brush())
                self.assertIn('non confirmée', self.panel.history.get())
                self.assertNotIn('/private/', self.panel.history.get())

    def test_result_from_old_generation_does_not_refresh_new_context(self):
        self.panel.undo_brush()
        self.panel._history_generation += 1
        self.panel._project_path = str(Path.cwd() / 'another.smartsvg')
        self.panel.snapshot = SimpleNamespace(sha256='d' * 64)
        self.panel.history.set('nouveau projet')
        self.finish(self.receipt())
        self.assertEqual(self.receipts, [])
        self.assertEqual(self.panel.history.get(), 'nouveau projet')
        self.assertFalse(self.panel.busy)

    def test_changed_subject_after_submission_requires_same_project_reinspection(self):
        self.panel.undo_brush()
        self.panel.selection.set(OTHER)
        self.finish(self.receipt())
        self.assertEqual(self.receipts, [])
        self.assertTrue(self.panel.history_requires_review)
        self.assertIn('Réexaminez', self.panel.history.get())

    def test_queued_completion_after_shutdown_never_touches_destroyed_widgets(self):
        self.panel.undo_brush(); self.panel.shutdown()
        self.panel.history.set = lambda value: self.fail('destroyed widget')
        self.finish(self.receipt())
        self.assertEqual(self.receipts, [])

    def test_confirmation_exception_and_executor_rejection_never_write(self):
        def fail(*_args, **_kwargs): raise RuntimeError('/private/failure')
        self.panel._confirm_history_fn = fail
        self.assertFalse(self.panel.undo_brush())
        self.assertEqual(self.panel._history_worker.calls, [])
        self.panel._confirm_history_fn = lambda *_args: True
        self.panel._history_worker.submit = fail
        self.assertFalse(self.panel.undo_brush())
        self.assertFalse(self.panel.busy)
        self.assertEqual(self.scheduled, [])
        self.assertNotIn('/private/', self.panel.history.get())

    def test_saved_receipt_but_host_failure_never_announces_rollback(self):
        def failed(_receipt): raise RuntimeError('/private/failure')
        self.panel._on_saved = failed
        self.panel.undo_brush(); self.finish(self.receipt())
        self.assertIn('enregistrée', self.panel.history.get())
        self.assertIn('actualisation indisponible', self.panel.history.get())
        self.assertTrue(self.panel.history_requires_review)


HAS_CPU = bool(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'))


@unittest.skipUnless(HAS_CPU, 'Real history UI round trip needs NumPy/Pillow')
class NativeHistoryCPUActionTests(unittest.TestCase):
    def setUp(self):
        from concurrent.futures import ThreadPoolExecutor
        from hashlib import sha256
        from test_v34_native_subject_preview import NativeSubjectPreviewTests
        from smartsvg_core.native_subject_preview_v34 import preview_native_subject_stroke
        from smartsvg_core.native_subject_save_v34 import save_native_subject_stroke
        from smartsvg_core.native_brush_history_v34 import inspect_native_brush_history
        from smartsvg_core.native_brush_history_command_v34 import change_native_brush_history
        from smartsvg_core.project_archive import load_project
        NativeSubjectPreviewTests.setUp(self)
        self.workspace.update_notes(self.name, notes='Notes conservées', expected_sha256=self.sha)
        self.sha = sha256(self.path.read_bytes()).hexdigest()
        self.original = load_project(self.path)
        command = dict(project_path=str(self.path), expected_sha256=self.sha,
                       subject_id=self.subject_id, mode='add', radius=.05, points=[[.5, .5]])
        preview = preview_native_subject_stroke(**command)
        saved = save_native_subject_stroke(
            **command, expected_preview_mask_sha256_float32=preview['preview_mask_sha256_float32'],
            command_id='history-ui-seed', confirmed=True)
        self.sha = saved['project_sha256']
        self.saved = load_project(self.path)
        self.export = self.path.parent / 'already-exported.svg'
        self.export.write_bytes(b'<svg/>')
        NativeHistoryActionTests.setUp(self)
        p = self.panel
        p._project_path = str(self.path)
        p.selection.set(self.subject_id)
        p._history_fn = inspect_native_brush_history
        p._history_change_fn = change_native_brush_history
        p._history_worker = ThreadPoolExecutor(max_workers=1)
        self.addCleanup(p.shutdown)
        p._on_saved = self.reopen
        self.reopen(None)

    def reopen(self, receipt):
        from hashlib import sha256
        from smartsvg_core.project_archive import load_project
        from smartsvg_core.native_atelier_v34 import inspect_atelier_snapshot
        if receipt is not None: self.receipts.append(receipt)
        p = self.panel
        p._history_generation += 1
        p._history_needs_review = False
        p.snapshot = inspect_atelier_snapshot(load_project(self.path), sha256(self.path.read_bytes()).hexdigest())
        p.subjects = {x.subject_id: x for x in p.snapshot.subjects}
        p._refresh_history()

    def finish_real_command(self):
        self.panel._history_future.result(timeout=15)
        self.scheduled.pop(0)()

    def test_real_cpu_undo_redo_via_controller_reopens_and_preserves_resources(self):
        from smartsvg_core.project_archive import load_project
        before = self.path.read_bytes()
        self.assertEqual(self.panel.undo_button.state, 'normal')
        self.assertTrue(self.panel.undo_brush())
        self.finish_real_command()
        self.assertNotIn('editor_v216', load_project(self.path).document)
        self.assertEqual(self.path.with_suffix('.previous.smartsvg').read_bytes(), before)
        self.assertEqual(self.panel.redo_button.state, 'normal')
        self.assertTrue(self.panel.redo_brush())
        self.finish_real_command()
        reopened = load_project(self.path)
        self.assertEqual(reopened.document['editor_v216'], self.saved.document['editor_v216'])
        self.assertEqual(reopened.resources, self.original.resources)
        self.assertEqual(reopened.masks, self.original.masks)
        self.assertEqual(reopened.subjects, self.original.subjects)
        self.assertEqual(reopened.document['notes'], 'Notes conservées')
        self.assertEqual(self.export.read_bytes(), b'<svg/>')
        self.assertEqual([x['action'] for x in self.receipts], ['undo', 'redo'])

    def test_actual_tk_buttons_drive_real_cpu_history_and_reopen(self):
        import tkinter as tk
        from tkinter import ttk
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest('No graphical Tk session available')
        self.addCleanup(root.destroy)
        root.withdraw()
        previous = self.panel
        panel = NativeAtelierPanel(root, tk, ttk,
                                  on_saved=self.reopen,
                                  confirm_history_fn=lambda *_args: True)
        self.panel = panel
        self.addCleanup(panel.shutdown)
        panel.load(previous.snapshot, selected_subject=self.subject_id,
                   project_path=str(self.path))
        # Host reinspection is the same real archive reader; update actual widgets.
        def reload(receipt):
            from smartsvg_core.project_archive import load_project
            from smartsvg_core.native_atelier_v34 import inspect_atelier_snapshot
            self.receipts.append(receipt)
            panel.load(inspect_atelier_snapshot(load_project(self.path), receipt['project_sha256']),
                       selected_subject=self.subject_id, project_path=str(self.path))
        panel._on_saved = reload
        for button, action in ((panel.undo_button, 'undo'), (panel.redo_button, 'redo')):
            self.assertEqual(str(button.cget('state')), 'normal')
            button.invoke()
            self.assertTrue(panel.busy)
            deadline = time.monotonic() + 15
            while panel.busy and time.monotonic() < deadline:
                root.update()
                time.sleep(.01)
            self.assertFalse(panel.busy)
            self.assertEqual(self.receipts[-1]['action'], action)
        self.assertEqual(self.export.read_bytes(), b'<svg/>')

    def test_real_cas_history_finishes_after_shutdown_without_late_ui_update(self):
        from threading import Event, Thread
        from smartsvg_core.project_archive import load_project
        from smartsvg_core.native_brush_history_v34 import inspect_native_brush_history

        panel = self.panel
        entered, release, closed = Event(), Event(), Event()
        writer = panel._history_change_fn
        before = self.path.read_bytes()
        def delayed_writer(**request):
            entered.set()
            if not release.wait(10):
                raise AssertionError('test did not release confirmed writer')
            return writer(**request)
        panel._history_change_fn = delayed_writer
        self.assertTrue(panel.undo_brush())
        future = panel._history_future
        try:
            self.assertTrue(entered.wait(3))
            closer = Thread(target=lambda: (panel.shutdown(), closed.set()), daemon=True)
            closer.start()
            self.assertTrue(closed.wait(1), 'shutdown waited for confirmed disk write')
            self.assertFalse(future.cancelled())
            # Simulate delivery to an already destroyed UI: no status or host
            # callback may run, although the confirmed CAS command must finish.
            panel.history.set = lambda _value: self.fail('late UI status update')
            release.set()
            receipt = future.result(timeout=15)
            self.scheduled.pop(0)()
            self.assertEqual(self.receipts, [])
            self.assertTrue(receipt['persisted'])
            reopened = load_project(self.path)
            self.assertNotIn('editor_v216', reopened.document)
            self.assertEqual(reopened.resources, self.original.resources)
            self.assertEqual(reopened.subjects, self.original.subjects)
            self.assertEqual(reopened.masks, self.original.masks)
            self.assertEqual(reopened.document['notes'], 'Notes conservées')
            self.assertEqual(self.path.with_suffix('.previous.smartsvg').read_bytes(), before)
            self.assertTrue(inspect_native_brush_history(
                project_path=str(self.path),
                expected_sha256=receipt['project_sha256'])['redo_available'])
            self.assertEqual(self.export.read_bytes(), b'<svg/>')
        finally:
            release.set()
            future.result(timeout=15)

    def test_real_tk_full_panel_teardown_finishes_cas_and_reopens_safely(self):
        """Teardown API during a write; the desktop close guard is separate."""
        import tkinter as tk
        from tkinter import ttk
        from threading import Event, Timer
        from smartsvg_core.project_archive import load_project
        from smartsvg_core.native_brush_history_command_v34 import change_native_brush_history
        from smartsvg_core.native_brush_history_v34 import inspect_native_brush_history

        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest('No graphical Tk session available')
        def destroy_root():
            try:
                root.destroy()
            except tk.TclError:
                pass  # The test deliberately destroys this interpreter first.
        self.addCleanup(destroy_root)
        root.geometry('900x650')
        entered, release = Event(), Event()
        callbacks, errors = [], []
        root.report_callback_exception = lambda *args: errors.append(args)
        def delayed_writer(**request):
            entered.set()
            if not release.wait(10):
                raise AssertionError('test did not release confirmed writer')
            return change_native_brush_history(**request)
        panel = NativeAtelierPanel(
            root, tk, ttk, on_saved=callbacks.append,
            history_change_fn=delayed_writer, confirm_history_fn=lambda *_args: True)
        self.addCleanup(panel.shutdown)
        panel.load(self.panel.snapshot, selected_subject=self.subject_id,
                   project_path=str(self.path))
        root.update()
        self.assertTrue(panel.undo_button.winfo_viewable())
        # Exercise the real brush-dialog lifecycle first: history actions are
        # unavailable until that actual child panel has been closed.
        self.assertTrue(panel.open_brush())
        brush, dialog = panel._brush_panel, panel._brush_dialog
        root.update()
        self.assertFalse(panel.undo_brush())
        panel._close_brush()
        self.assertTrue(brush._closed)
        self.assertFalse(dialog.winfo_exists())
        panel.undo_button.invoke()
        future = panel._history_future
        self.assertIsNotNone(future)
        # A watchdog releases the writer even if a regressed shutdown waits.
        watchdog = Timer(3, release.set)
        watchdog.start()
        before = self.path.read_bytes()
        try:
            self.assertTrue(entered.wait(3))
            root.after(0, panel.shutdown)
            root.after(1, root.quit)
            started = time.monotonic()
            root.mainloop()
            self.assertLess(time.monotonic() - started, 1.5)
            self.assertTrue(panel._closed)
            self.assertFalse(future.cancelled())
            self.assertFalse(future.done())
            root.destroy()
            release.set()
            receipt = future.result(timeout=15)
            # Explicitly deliver stale callbacks after the real widgets died.
            panel._receive_history()
            brush._draw()
            self.assertEqual(callbacks, [])
            self.assertEqual(errors, [])
            reopened = load_project(self.path)
            self.assertNotIn('editor_v216', reopened.document)
            self.assertEqual(reopened.resources, self.original.resources)
            self.assertEqual(reopened.masks, self.original.masks)
            self.assertEqual(reopened.subjects, self.original.subjects)
            self.assertEqual(reopened.document['notes'], 'Notes conservées')
            self.assertEqual(self.path.with_suffix('.previous.smartsvg').read_bytes(), before)
            self.assertTrue(inspect_native_brush_history(
                project_path=str(self.path),
                expected_sha256=receipt['project_sha256'])['redo_available'])
            self.assertEqual(self.export.read_bytes(), b'<svg/>')
        finally:
            release.set()
            watchdog.cancel()
            future.result(timeout=15)


if __name__ == '__main__':
    unittest.main()
