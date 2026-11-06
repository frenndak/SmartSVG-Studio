"""Native creation UI callbacks with real writes, fakes only at widget boundary."""
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[1] / 'engine'
if str(ENGINE) not in sys.path: sys.path.insert(0, str(ENGINE))
from test_v34_native_templates import Var, Widget
from test_v34_native_app_shell import LayoutWidget
from test_v34_native_preview_jobs import fixture_module
from smartsvg_core.project_archive import load_project


class CreatorWidget(LayoutWidget):
    def protocol(self, key, callback): self.events[key] = callback


class NativeCreateUITests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ENGINE / 'native_create_tk_v34.py').exists(), 'Native creation form missing')
        import native_create_tk_v34
        self.module = native_create_tk_v34
        self.tk = SimpleNamespace(Toplevel=CreatorWidget, StringVar=Var)
        self.ttk = SimpleNamespace(Frame=CreatorWidget, Label=CreatorWidget,
            Button=CreatorWidget, Entry=CreatorWidget, Combobox=CreatorWidget)
        self.pending = []
        self.root = SimpleNamespace(after=lambda _ms, callback: self.pending.append(callback))
        self.receipts = []
        self.dialog = self.module.NativeCreateDialog(self.root, self.tk, self.ttk,
            SimpleNamespace(askopenfilename=lambda **_kwargs:'', askdirectory=lambda **_kwargs:''),
            self.receipts.append)
        self.addCleanup(self.dialog.shutdown)

    def drain(self):
        if self.dialog.future is not None:
            try: self.dialog.future.result(timeout=15)
            except Exception: pass  # callback, not the test, must expose the error
        while self.pending: self.pending.pop(0)()

    def test_cancelled_dialogs_and_close_never_create_any_files(self):
        with tempfile.TemporaryDirectory() as directory:
            self.dialog.choose_source()
            self.dialog.choose_output()
            self.assertEqual(self.dialog.source.get(), '')
            self.assertEqual(self.dialog.output.get(), '')
            self.assertTrue(self.dialog.close())
            self.assertEqual(list(Path(directory).iterdir()), [])
            self.assertEqual(self.receipts, [])

    def test_actual_png_creation_and_readback_emits_one_verified_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'image.png'
            source.write_bytes(fixture_module.png())
            self.dialog.source.set(str(source))
            self.dialog.output.set(directory)
            self.dialog.name.set('creation')
            self.dialog.width.set('28,5')
            self.dialog.dpi.set('450')
            self.dialog.start()
            self.drain()
            self.assertEqual(len(self.receipts), 1)
            project = load_project(self.receipts[0].path)
            self.assertEqual(project.document['width_mm'], 28.5)
            self.assertEqual(project.document['dpi'], 450)
            self.assertEqual(project.sources[0].provenance, 'manual_native_png_import')
            self.assertFalse(self.dialog.window.winfo_exists())

    def test_double_activation_does_not_queue_or_cancel_a_write_and_close_waits(self):
        from concurrent.futures import Future
        executor = SimpleNamespace(submit=lambda *args, **kwargs: pending,
                                   shutdown=lambda **kwargs:None)
        pending = Future()
        self.dialog.source.set('/source.png')
        self.dialog.output.set('/chosen')
        self.dialog.name.set('creation')
        with patch.object(self.module, 'ThreadPoolExecutor', return_value=executor):
            with patch.object(executor, 'submit', wraps=executor.submit) as submit:
                self.dialog.start()
                self.dialog.start()
                self.assertEqual(submit.call_count, 1)
                self.assertFalse(self.dialog.close())
                self.assertTrue(self.dialog.window.winfo_exists())
                self.assertFalse(pending.cancelled())
                pending.set_exception(ValueError('failure'))
                self.drain()
        self.assertFalse(self.dialog.busy)
        self.assertEqual(self.receipts, [])
        self.assertIn('non confirmée', self.dialog.status.get())
        self.assertTrue(self.dialog.close())

    def test_validation_and_error_are_actionable_and_original_project_stays_selected(self):
        self.dialog.start()
        self.assertIsNone(self.dialog.future)
        self.assertIn('Choisir', self.dialog.status.get())
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'bad.png'
            source.write_bytes(b'broken')
            self.dialog.source.set(str(source)); self.dialog.output.set(directory)
            self.dialog.start(); self.drain()
            self.assertEqual(self.receipts, [])
            self.assertFalse(list(Path(directory).rglob('*.smartsvg')))
            self.assertEqual(self.dialog.create_button.options['state'], 'normal')
            self.assertIn('PNG', self.dialog.status.get())


if __name__ == '__main__': unittest.main()
