"""Shared native navigation behavior; widget doubles do not qualify rendering."""
import importlib
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[1] / 'engine'
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))
from test_v34_native_templates import Var, Widget


class LayoutWidget(Widget):
    all_widgets = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = args[0] if args else None
        self.visible = False
        self.focused = False
        self.pack_options = {}
        self.all_widgets.append(self)
    def pack(self, **kwargs):
        self.visible = True
        self.pack_options = kwargs
    def pack_forget(self): self.visible = False
    def focus_set(self): self.focused = True


class AppShellTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((ENGINE / 'native_app_shell_v34.py').exists(),
                        'The shared standalone application shell is missing')
        self.module = importlib.import_module('native_app_shell_v34')
        LayoutWidget.all_widgets = []
        self.root = LayoutWidget()
        self.tk = SimpleNamespace(StringVar=Var, Canvas=LayoutWidget)
        self.ttk = SimpleNamespace(Frame=LayoutWidget, Label=LayoutWidget,
            Button=LayoutWidget, Separator=LayoutWidget, Entry=LayoutWidget,
            Combobox=LayoutWidget)
        self.shell = self.module.NativeAppShell(self.root, self.tk, self.ttk)
        for key, label in (('home', 'Accueil'), ('project', 'Projet'),
                           ('factory', 'Fabrique'), ('appearance', 'Apparence')):
            self.shell.add_page(key, label)
        self.shell.show('home')

    def test_only_selected_page_is_visible_with_textual_active_marker(self):
        self.assertEqual(self.shell.active_page, 'home')
        self.shell.buttons['factory'].options['command']()
        self.assertEqual(self.shell.active_page, 'factory')
        self.assertEqual([key for key, page in self.shell.pages.items() if page.visible], ['factory'])
        self.assertIn('Fabrique', self.shell.buttons['factory'].options['text'])
        self.assertNotEqual(self.shell.buttons['factory'].options['text'], 'Fabrique')
        self.assertEqual(self.shell.buttons['home'].options['text'], 'Accueil')

    def test_unknown_page_refused_without_hiding_current_or_duplicate_registration(self):
        with self.assertRaises(ValueError): self.shell.show('missing')
        self.assertEqual(self.shell.active_page, 'home')
        self.assertTrue(self.shell.pages['home'].visible)
        with self.assertRaises(ValueError): self.shell.add_page('home', 'Duplicate')
        self.assertEqual(len(self.shell.pages), 4)

    def test_one_hundred_navigation_changes_keep_real_draft_and_do_not_touch_files(self):
        from native_templates_tk_v34 import TemplatePreviewContent
        draft = TemplatePreviewContent(self.shell.pages['factory'], self.tk, self.ttk)
        draft.width.set('90,5')
        draft.calculate()
        proposal = draft.proposal
        before_count = len(LayoutWidget.all_widgets)
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'keep.smartsvg'
            project.write_bytes(b'project remains unchanged')
            with patch.object(Path, 'write_bytes', side_effect=AssertionError('navigation writes')), \
                 patch.object(Path, 'write_text', side_effect=AssertionError('navigation writes')):
                for index in range(100):
                    self.shell.show(('project', 'factory', 'appearance', 'home')[index % 4])
            self.assertEqual(project.read_bytes(), b'project remains unchanged')
            self.assertEqual(len(list(Path(directory).iterdir())), 1)
        self.assertEqual(len(LayoutWidget.all_widgets), before_count)
        self.assertEqual(draft.width.get(), '90,5')
        self.assertIs(draft.proposal, proposal)
        self.assertEqual(proposal['geometry']['bbox_mm'], [0, 0, 150.5, 110])

    def test_shortcuts_switch_workspace_and_return_break_with_focus(self):
        for number, key in enumerate(('home', 'project', 'factory', 'appearance'), 1):
            result = self.root.events[f'<Control-Key-{number}>'](None)
            self.assertEqual(result, 'break')
            self.assertEqual(self.shell.active_page, key)
            self.assertTrue(self.shell.buttons[key].focused)



class DesktopShellIntegrationTests(unittest.TestCase):
    def run_desktop(self, scenario, *, first_project=None, chosen=''):
        import standalone_desktop_v34 as desktop
        from native_app_shell_v34 import NativeAppShell
        from smartsvg_core.native_preview_jobs_v34 import LatestOnlyJob
        from native_templates_tk_v34 import TemplatePreviewContent
        LayoutWidget.all_widgets = []
        captured = SimpleNamespace(shell=None, jobs=None, template=None)
        class Root(LayoutWidget):
            def __init__(self):
                super().__init__()
                self.pending, self.protocols = [], {}
            def after(self, _ms, callback): self.pending.append(callback)
            def protocol(self, key, callback): self.protocols[key] = callback
            def mainloop(root): scenario(root, captured)
        class Shell(NativeAppShell):
            def __init__(self, *args):
                super().__init__(*args)
                captured.shell = self
        class Jobs(LatestOnlyJob):
            def __init__(self, loader):
                super().__init__(loader)
                self.futures, self.closed = [], False
                captured.jobs = self
            def submit(self, path):
                version, future = super().submit(path)
                self.futures.append(future)
                return version, future
            def close(self):
                self.closed = True
                super().close()
        class Template(TemplatePreviewContent):
            def __init__(self, *args):
                super().__init__(*args)
                captured.template = self
        class Photo:
            def __init__(self, **_kwargs): pass
            def subsample(self, _factor): return self
        root = Root()
        tk = SimpleNamespace(Tk=lambda: root, Canvas=LayoutWidget,
            StringVar=Var, TclError=RuntimeError, PhotoImage=Photo,
            filedialog=SimpleNamespace(askopenfilename=lambda **_kwargs: chosen),
            ttk=SimpleNamespace(Frame=LayoutWidget, Label=LayoutWidget,
                Button=LayoutWidget, Entry=LayoutWidget, Combobox=LayoutWidget,
                Separator=LayoutWidget))
        with patch.dict(sys.modules, {'tkinter': tk}), \
             patch.object(desktop, 'ArtisanThemePicker', return_value=object()) as theme, \
             patch.object(desktop, 'NativeAppShell', Shell), \
             patch.object(desktop, 'LatestOnlyJob', Jobs), \
             patch.object(desktop, 'TemplatePreviewContent', Template):
            self.assertEqual(desktop._start_gui(first_project), 0)
            self.assertEqual(theme.call_count, 1)
            self.assertIs(theme.call_args.kwargs['parent'], captured.shell.pages['appearance'])
        self.assertTrue(captured.jobs.closed)
        return root, captured

    def test_home_actions_shortcuts_cancel_and_embedded_template_reuse(self):
        def scenario(root, state):
            self.assertEqual(state.shell.active_page, 'home')
            self.assertEqual(state.jobs.futures, [])
            root.events['<Control-o>'](None)  # dialog cancelled
            self.assertEqual(state.shell.active_page, 'home')
            actions = {widget.options.get('text'): widget.options.get('command')
                       for widget in LayoutWidget.all_widgets if 'command' in widget.options}
            actions['Préparer un gabarit']()
            self.assertEqual(state.shell.active_page, 'factory')
            state.template.width.set('99')
            state.template.calculate()
            proposal = state.template.proposal
            actions['Personnaliser mon espace']()
            self.assertEqual(state.shell.active_page, 'appearance')
            root.events['<Control-Key-3>'](None)
            self.assertIs(state.template.proposal, proposal)
            self.assertEqual(state.jobs.futures, [])
            root.protocols['WM_DELETE_WINDOW']()
            self.assertFalse(root.exists)
        self.run_desktop(scenario)

    def test_startup_project_real_reader_keeps_summary_and_bytes_across_navigation(self):
        from test_v34_native_preview_jobs import fixture_module
        from smartsvg_core.project_archive import save_project
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / 'source.smartsvg'
            save_project(project, fixture_module.fixture())
            before = project.read_bytes()
            def scenario(root, state):
                self.assertEqual(state.shell.active_page, 'project')
                self.assertEqual(len(state.jobs.futures), 1)
                report, preview = state.jobs.futures[0].result(timeout=15)
                self.assertTrue(report['ok'])
                self.assertEqual(preview.status, 'READY_PNG')
                while root.pending:
                    root.pending.pop(0)()
                variables = [widget.options['textvariable'] for widget in LayoutWidget.all_widgets
                             if 'textvariable' in widget.options]
                summary = next(var for var in variables if str(var.get()).startswith('Projet :'))
                original_summary = summary.get()
                for index in range(100):
                    root.events[f'<Control-Key-{index % 4 + 1}>'](None)
                self.assertEqual(summary.get(), original_summary)
                self.assertEqual(len(state.jobs.futures), 1)
                self.assertEqual(project.read_bytes(), before)
                state.shell.buttons['project'].focused = False
                self.assertEqual(root.events['<F5>'](None), 'break')
                self.assertTrue(state.shell.buttons['project'].focused)
                self.assertEqual(state.shell.active_page, 'project')
                self.assertEqual(len(state.jobs.futures), 2)
                state.jobs.futures[-1].result(timeout=15)
            self.run_desktop(scenario, first_project=str(project))
            self.assertEqual(project.read_bytes(), before)

    def test_open_failure_is_visible_and_navigation_does_not_erase_error(self):
        def scenario(root, state):
            self.assertEqual(root.events['<Control-o>'](None), 'break')
            self.assertEqual(state.shell.active_page, 'project')
            state.jobs.futures[-1].result(timeout=15)
            while root.pending:
                root.pending.pop(0)()
            variables = [widget.options['textvariable'] for widget in LayoutWidget.all_widgets
                         if 'textvariable' in widget.options]
            errors = [var for var in variables if 'Aucune modification' in str(var.get())]
            self.assertEqual(len(errors), 1)
            previous = errors[0].get()
            state.shell.show('home')
            state.shell.show('project')
            self.assertEqual(errors[0].get(), previous)
            self.assertEqual(len(state.jobs.futures), 1)
        self.run_desktop(scenario, chosen='/missing.smartsvg')

    def test_reader_closed_even_if_event_loop_raises(self):
        def scenario(_root, _state):
            raise RuntimeError('event loop failed')
        # run_desktop checks normal cleanup itself; record close independently
        # because its normal-return assertion is skipped on this failure path.
        from smartsvg_core.native_preview_jobs_v34 import LatestOnlyJob
        with patch.object(LatestOnlyJob, 'close', autospec=True) as close:
            with self.assertRaisesRegex(RuntimeError, 'event loop failed'):
                self.run_desktop(scenario)
            self.assertTrue(close.called)


class ActualTkShellSmokeTests(unittest.TestCase):
    """Real widget layout smoke when a GUI exists, not full Windows qualification."""
    def test_actual_layout_navigation_and_template_canvas_at_supported_sizes(self):
        try:
            import tkinter as tk
            from tkinter import ttk
        except ImportError as exc:
            self.skipTest(f'Tkinter unavailable: {exc}')
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest('No graphical Tk session available')
        self.addCleanup(root.destroy)
        from native_app_shell_v34 import NativeAppShell
        from native_templates_tk_v34 import TemplatePreviewContent
        from native_theme_tk_v34 import ArtisanThemePicker
        shell = NativeAppShell(root, tk, ttk)
        for key, label in (('home', 'Accueil'), ('project', 'Projet'),
                           ('factory', 'Fabrique'), ('appearance', 'Apparence')):
            shell.add_page(key, label)
        with tempfile.TemporaryDirectory() as directory:
            # A real theme styles and sizes the widgets; never user settings.
            theme = ArtisanThemePicker(root=root, parent=shell.pages['appearance'],
                tk=tk, ttk=ttk, settings_path=Path(directory) / 'appearance.json')
            template = TemplatePreviewContent(shell.pages['factory'], tk, ttk)
            for size in ('900x650', '1100x760', '1280x720'):
                with self.subTest(size=size):
                    root.geometry(size)
                    shell.show('factory')
                    root.update()
                    self.assertGreater(template.canvas.winfo_width(), 48)
                    self.assertGreater(template.canvas.winfo_height(), 48)
                    self.assertEqual(len(template.canvas.find_all()), 13)
                    self.assertLessEqual(template.canvas.winfo_rooty() + template.canvas.winfo_height(),
                                         root.winfo_rooty() + root.winfo_height())
                    for button in shell.buttons.values():
                        self.assertTrue(button.winfo_viewable())
            before = template.proposal
            for index in range(100):
                shell.show(('project', 'factory', 'appearance', 'home')[index % 4])
            root.update()
            self.assertIs(template.proposal, before)
            self.assertFalse(theme.settings_path.exists())

if __name__ == '__main__':
    unittest.main()
