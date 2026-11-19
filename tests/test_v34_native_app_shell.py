"""Shared native navigation behavior; widget doubles do not qualify rendering."""
import gc
import importlib
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

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
    def delete(self, *_indices): self.content = ''
    def insert(self, _index, value): self.content = value
    def get(self, *_indices): return self.content
    def edit_reset(self): pass
    def pack_forget(self): self.visible = False
    def winfo_ismapped(self): return self.visible
    def focus_set(self): self.focused = True
    def create_image(self, *_args, **_kwargs): pass
    def xview_moveto(self, _fraction): pass
    def yview_moveto(self, _fraction): pass
    def xview_scroll(self, *_args): pass
    def yview_scroll(self, *_args): pass


def create_atelier_project(directory):
    """Build and bind two exact masks using the existing V1 workspace."""
    import struct
    import time
    from smartsvg_core.project_workspace_g22 import ManagedWorkspace
    from test_g33e_persistent_subject_identity import png

    workspace = ManagedWorkspace(directory)
    name = 'atelier-project'
    created = workspace.create(name, png(), profile='Sticker - contour du sujet')
    raw = struct.pack('<24f', 1.0, 0.5, *([0.0] * 20), 0.75, 1.0)
    workspace.save_base_masks(name, raw_float32=raw, shape=[2, 3, 4],
                              image_fingerprint='b' * 64, editor_fingerprint='a' * 64,
                              expected_sha256=created['sha256'])
    ids = {}
    for index in (1, 0):
        state = workspace.inspect(name)
        catalog = state['base_masks']['mask_identity']
        binding = catalog['bindings'][index]
        result = workspace.register_subject_identity(
            name, mask_index=index, mask_id=binding['mask_id'],
            mask_sha256_float32=binding['mask_sha256_float32'],
            source_id=catalog['source_id'], source_sha256='a' * 64,
            expected_sha256=state['sha256'], confirmed=True,
            expires_at_ms=int(time.time() * 1000) + 60_000)
        ids[result['subject_id']] = binding['mask_id']
    return workspace.root / (name + '.smartsvg'), ids


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

    def test_capability_notice_distinguishes_brush_from_unavailable_export(self):
        labels = [widget.options.get('text', '') for widget in LayoutWidget.all_widgets]
        notice = next(text for text in labels if 'Création PNG' in text)
        self.assertIn('retouche', notice.lower())
        self.assertIn('sujets vérifiés', notice.lower())
        self.assertIn('exports', notice.lower())
        self.assertNotIn('Retouche, exports et installation Windows : intégration à venir', notice)

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
    def failed_thread_start(self, prefix):
        from threading import Thread

        real_start = Thread.start

        def start(thread):
            if thread.name.startswith(prefix):
                raise RuntimeError('simulated thread launch failure')
            return real_start(thread)

        return patch.object(Thread, 'start', start)

    def test_failed_notes_start_cannot_save_an_abandoned_draft_on_another_project(self):
        from smartsvg_core.project_archive import load_project

        with tempfile.TemporaryDirectory() as directory:
            left, right = Path(directory) / 'a', Path(directory) / 'b'
            left.mkdir()
            right.mkdir()
            first, _ = create_atelier_project(left)
            second, _ = create_atelier_project(right)
            original = first.read_bytes()

            def scenario(root, state):
                def receive_read():
                    state.jobs.futures[-1].result(timeout=15)
                    root.pending.pop(0)()

                receive_read()
                state.notes.editor.insert('1.0', 'Brouillon abandonné')
                launch_raised = False
                with self.failed_thread_start('smartsvg-notes'):
                    try:
                        state.notes.save()
                    except RuntimeError:
                        launch_raised = True  # Exercise the retry on the baseline, too.
                self.assertIsNone(state.notes.future)
                self.assertEqual(state.notes.editor.get(), 'Brouillon abandonné')
                root.events['<Control-o>'](None)
                receive_read()
                state.notes.editor.insert('1.0', 'Notes du second projet')
                state.notes.save()
                state.notes.future.result(timeout=15)
                self.assertEqual(first.read_bytes(), original)
                self.assertEqual(load_project(second).document['notes'], 'Notes du second projet')
                self.assertFalse(launch_raised)
                root.pending.pop(0)()
                receive_read()

            self.run_desktop(scenario, first_project=str(first), chosen=str(second),
                             discard_notes=lambda **_kwargs: True)

    @unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'),
                         'Real desktop history requires NumPy/Pillow')
    def test_failed_history_start_cannot_undo_another_project_later(self):
        from smartsvg_core.project_archive import load_project

        with tempfile.TemporaryDirectory() as directory:
            left, right = Path(directory) / 'a', Path(directory) / 'b'
            left.mkdir()
            right.mkdir()
            first, first_subject, _ = self.seed_history_project(left)
            second, second_subject, _ = self.seed_history_project(right)
            original = first.read_bytes()

            def scenario(root, state):
                def select_subject(subject):
                    state.jobs.futures[-1].result(timeout=15)
                    root.pending.pop(0)()
                    state.atelier.selection.set(subject)
                    state.atelier.render()

                panel = state.atelier
                panel.parent.after = root.after
                panel._confirm_history_fn = lambda *_args: True
                select_subject(first_subject)
                with self.failed_thread_start('smartsvg-history'):
                    self.assertFalse(panel.undo_brush())
                self.assertFalse(panel.busy)
                root.events['<Control-o>'](None)
                select_subject(second_subject)
                self.assertTrue(panel.undo_brush())
                panel._history_future.result(timeout=15)
                self.assertEqual(first.read_bytes(), original)
                self.assertNotIn('editor_v216', load_project(second).document)
                root.pending.pop(0)()
                select_subject(second_subject)

            self.run_desktop(scenario, first_project=str(first), chosen=str(second))

    def test_failed_recovery_start_cannot_restore_another_project_later(self):
        from smartsvg_core.project_archive import save_project
        from test_v34_native_preview_jobs import fixture_module

        with tempfile.TemporaryDirectory() as directory:
            left, right = Path(directory) / 'a', Path(directory) / 'b'
            left.mkdir()
            right.mkdir()
            first, second = (folder / 'project-test.smartsvg' for folder in (left, right))
            for target in (first, second):
                save_project(target.with_suffix('.previous.smartsvg'), fixture_module.fixture())

            def scenario(root, state):
                def receive_read():
                    state.jobs.futures[-1].result(timeout=15)
                    root.pending.pop(0)()

                receive_read()
                with self.failed_thread_start('smartsvg-recovery'):
                    state.recovery.start()
                self.assertIsNone(state.recovery.future)
                self.assertFalse(first.exists())
                root.events['<Control-o>'](None)
                receive_read()
                state.recovery.start()
                state.recovery.future.result(timeout=15)
                self.assertFalse(first.exists())
                self.assertEqual(second.read_bytes(),
                                 second.with_suffix('.previous.smartsvg').read_bytes())
                root.pending.pop(0)()
                receive_read()

            self.run_desktop(scenario, first_project=str(first), chosen=str(second),
                             discard_notes=lambda **_kwargs: True)

    def run_desktop(self, scenario, *, first_project=None, chosen='', source_choice='', output_choice='', discard_notes=lambda **_: False):
        import standalone_desktop_v34 as desktop
        from native_app_shell_v34 import NativeAppShell
        from smartsvg_core.native_preview_jobs_v34 import LatestOnlyJob
        from native_templates_tk_v34 import TemplatePreviewContent
        LayoutWidget.all_widgets = []
        captured = SimpleNamespace(
            shell=None, jobs=None, template=None, creator=None, notes=None,
            atelier=None, recovery=None, theme=None, lifecycle=[])
        class Root(LayoutWidget):
            def __init__(self):
                super().__init__()
                self.pending, self.protocols = [], {}
            def after(self, _ms, callback): self.pending.append(callback)
            def protocol(self, key, callback): self.protocols[key] = callback
            def mainloop(root): scenario(root, captured)
            def destroy(self):
                captured.lifecycle.append('root.destroy')
                super().destroy()
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
        class Theme:
            def __init__(self, **_kwargs):
                self.shutdown_calls = 0
                captured.theme = self
            def shutdown(self):
                self.shutdown_calls += 1
                captured.lifecycle.append('theme.shutdown')
        class Popup(LayoutWidget):
            def protocol(self, event, callback): self.events[event] = callback
        class Creator(desktop.NativeCreateDialog):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                captured.creator = self
        class Notes(desktop.NativeNotesPanel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                captured.notes = self
        class Atelier(desktop.NativeAtelierPanel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                captured.atelier = self
        class Recovery(desktop.NativeRecoveryPanel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                captured.recovery = self
        class Photo:
            def __init__(self, **kwargs): self.data = kwargs.get('data')
            def subsample(self, _factor): return self
            def width(self): return 4
            def height(self): return 3
        root = Root()
        tk = SimpleNamespace(Tk=lambda: root, Toplevel=Popup, Canvas=LayoutWidget,
            StringVar=Var, TclError=RuntimeError, PhotoImage=Photo, Text=LayoutWidget,
            messagebox=SimpleNamespace(askyesno=lambda _title, _message, **kwargs: discard_notes(**kwargs)),
            filedialog=SimpleNamespace(askopenfilename=lambda **kwargs:
                source_choice if kwargs.get('filetypes') == [('Image PNG', '*.png')] else chosen,
                askdirectory=lambda **kwargs:output_choice),
            ttk=SimpleNamespace(Frame=LayoutWidget, Label=LayoutWidget,
                Button=LayoutWidget, Entry=LayoutWidget, Combobox=LayoutWidget,
                Separator=LayoutWidget))
        with patch.dict(sys.modules, {'tkinter': tk}), \
             patch.object(desktop, 'ArtisanThemePicker', side_effect=Theme) as theme, \
             patch.object(desktop, 'NativeAppShell', Shell), \
             patch.object(desktop, 'LatestOnlyJob', Jobs), \
             patch.object(desktop, 'TemplatePreviewContent', Template), \
             patch.object(desktop, 'NativeAtelierPanel', Atelier), \
             patch.object(desktop, 'NativeRecoveryPanel', Recovery), \
             patch.object(desktop, 'NativeNotesPanel', Notes), \
             patch.object(desktop, 'NativeCreateDialog', Creator):
            self.assertEqual(desktop._start_gui(first_project), 0)
            self.assertEqual(theme.call_count, 1)
            self.assertIs(theme.call_args.kwargs['parent'], captured.shell.pages['appearance'])
        self.assertGreaterEqual(captured.theme.shutdown_calls, 1)
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
            self.assertEqual(
                state.lifecycle[:2], ['theme.shutdown', 'root.destroy'])
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

    def test_home_creation_writes_verifies_and_opens_real_project(self):
        from test_v34_native_preview_jobs import fixture_module
        from smartsvg_core.project_archive import load_project
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'dessin.png'
            source.write_bytes(fixture_module.png())
            def scenario(root, state):
                actions = [widget for widget in LayoutWidget.all_widgets
                           if widget.options.get('text') == 'Créer depuis un PNG…']
                self.assertEqual(len(actions), 2)
                actions[-1].options['command']()
                creator = state.creator
                creator.choose_source(); creator.choose_output()
                creator.start()
                self.assertTrue(creator.busy)
                # Closing/opening a different project cannot cancel the write
                # or let its later result replace a newly selected session.
                root.events['<Control-o>'](None)
                root.protocols['WM_DELETE_WINDOW']()
                self.assertTrue(root.exists)
                self.assertEqual(state.jobs.futures, [])
                creator.future.result(timeout=15)
                while root.pending:
                    root.pending.pop(0)()
                    if state.jobs.futures: state.jobs.futures[-1].result(timeout=15)
                self.assertFalse(creator.busy)
                self.assertFalse(creator.window.winfo_exists())
                self.assertEqual(state.shell.active_page, 'project')
                self.assertEqual(len(state.jobs.futures), 1)
                report, _ = state.jobs.futures[0].result(timeout=15)
                self.assertTrue(report['ok'])
                project = load_project(Path(directory) / 'SmartSVG_Managed_Projects/dessin.smartsvg')
                self.assertEqual(project.resources['sources/source-original.png'], source.read_bytes())
                notices = [widget.options['textvariable'].get() for widget in LayoutWidget.all_widgets
                           if 'textvariable' in widget.options]
                self.assertTrue(any(str(value).startswith('Projet créé, enregistré et relu') for value in notices))
            self.run_desktop(scenario, source_choice=str(source), output_choice=directory)

    def test_creation_waits_until_initial_project_inspection_is_applied(self):
        from test_v34_native_preview_jobs import fixture_module

        with tempfile.TemporaryDirectory() as directory:
            path, _ = create_atelier_project(directory)
            source = Path(directory) / 'nouveau.png'
            source.write_bytes(fixture_module.png())

            def scenario(root, state):
                # The read can be finished in its worker, but its Tk callback
                # has not yet installed the project and notes revision.
                state.jobs.futures[0].result(timeout=15)
                root.events['<Control-n>'](None)
                creator = state.creator
                creator.choose_source()
                creator.choose_output()
                creator.start()
                premature = creator.future
                if premature is not None:
                    premature.result(timeout=15)
                self.assertIsNone(premature)
                self.assertFalse(creator.busy)
                self.assertIn('vérification', creator.status.get().lower())

                root.pending.pop(0)()
                creator.start()
                self.assertTrue(creator.busy)
                creator.future.result(timeout=15)
                root.pending.pop(0)()
                state.jobs.futures[-1].result(timeout=15)
                root.pending.pop(0)()
                self.assertEqual(state.notes.revision.path.name, 'nouveau.smartsvg')

            self.run_desktop(scenario, first_project=str(path),
                             source_choice=str(source), output_choice=directory)

    def test_creation_form_changed_during_brush_confirmation_keeps_draft(self):
        from test_v34_native_preview_jobs import fixture_module

        with tempfile.TemporaryDirectory() as directory:
            path, _ = create_atelier_project(directory)
            source = Path(directory) / 'nouveau.png'
            source.write_bytes(fixture_module.png())
            active = {}

            def change_name(**_kwargs):
                active['creator'].name.set('nouveau-nom')
                return True

            def scenario(root, state):
                state.jobs.futures[0].result(timeout=15)
                root.pending.pop(0)()
                panel = SimpleNamespace(has_draft=True,
                    draft_checkpoint=lambda: ('unchanged',), shutdown=lambda: None)
                dialog = SimpleNamespace(lift=lambda: None, destroy=lambda: None)
                state.atelier._brush_panel, state.atelier._brush_dialog = panel, dialog
                state.atelier._brush_key = (str(path), state.atelier.snapshot.sha256,
                                            state.atelier.selection.get())
                root.events['<Control-n>'](None)
                creator = state.creator
                active['creator'] = creator
                creator.choose_source()
                creator.choose_output()
                creator.start()
                premature = creator.future
                if premature is not None:
                    premature.result(timeout=15)
                self.assertIsNone(premature)
                self.assertIs(state.atelier._brush_panel, panel)
                self.assertEqual(creator.name.get(), 'nouveau-nom')
                self.assertFalse(list((Path(directory) / 'SmartSVG_Managed_Projects')
                                      .glob('nouveau*.smartsvg')))

            self.run_desktop(scenario, first_project=str(path),
                             source_choice=str(source), output_choice=directory,
                             discard_notes=change_name)

    def test_replaced_creation_dialog_keeps_existing_brush_draft(self):
        from test_v34_native_preview_jobs import fixture_module

        with tempfile.TemporaryDirectory() as directory:
            path, _ = create_atelier_project(directory)
            before = path.read_bytes()
            source = Path(directory) / 'nouveau.png'
            source.write_bytes(fixture_module.png())
            active = {}

            def replace_creator(**_kwargs):
                active['creator'].close()
                active['root'].events['<Control-n>'](None)
                return True

            def scenario(root, state):
                state.jobs.futures[0].result(timeout=15)
                root.pending.pop(0)()
                panel = SimpleNamespace(has_draft=True,
                    draft_checkpoint=lambda: ('unchanged',), shutdown=lambda: None)
                dialog = SimpleNamespace(lift=lambda: None, destroy=lambda: None)
                state.atelier._brush_panel, state.atelier._brush_dialog = panel, dialog
                state.atelier._brush_key = (str(path), state.atelier.snapshot.sha256,
                                            state.atelier.selection.get())
                root.events['<Control-n>'](None)
                creator = state.creator
                active.update(root=root, creator=creator)
                creator.choose_source()
                creator.choose_output()
                creator.start()
                # An unfixed implementation may have launched a writer on
                # the destroyed dialog; let it finish before temp cleanup.
                if creator.future is not None:
                    creator.future.result(timeout=15)
                self.assertFalse(creator.window.winfo_exists())
                self.assertIsNot(state.creator, creator)
                self.assertIs(state.atelier._brush_panel, panel)
                self.assertIsNone(creator.future)
                self.assertFalse((Path(directory) /
                    'SmartSVG_Managed_Projects/nouveau.smartsvg').exists())
                self.assertEqual(path.read_bytes(), before)

            self.run_desktop(scenario, first_project=str(path),
                             source_choice=str(source), output_choice=directory,
                             discard_notes=replace_creator)

    def test_new_project_does_not_displace_notes_edited_during_creation(self):
        from test_v34_native_preview_jobs import fixture_module

        for try_save in (False, True):
            with self.subTest(try_save=try_save), tempfile.TemporaryDirectory() as directory:
                path, _ = create_atelier_project(directory)
                before = path.read_bytes()
                source = Path(directory) / 'nouveau.png'
                source.write_bytes(fixture_module.png())

                def scenario(root, state):
                    state.jobs.futures[0].result(timeout=15)
                    root.pending.pop(0)()
                    root.events['<Control-n>'](None)
                    state.creator.choose_source()
                    state.creator.choose_output()
                    state.creator.start()
                    self.assertTrue(state.creator.busy)
                    # Model a callback already queued before the creation
                    # dialog's grab, rather than ordinary pointer typing.
                    state.notes.editor.insert('1.0', 'Note arrivée pendant la création')
                    if try_save:
                        state.notes.save()
                        self.assertIsNone(state.notes.future)
                    state.creator.future.result(timeout=15)
                    root.pending.pop(0)()
                    destination = Path(directory) / 'SmartSVG_Managed_Projects/nouveau.smartsvg'
                    self.assertTrue(destination.exists())
                    self.assertEqual(state.notes.editor.get(), 'Note arrivée pendant la création')
                    self.assertEqual(state.notes.revision.path, path)
                    self.assertEqual(len(state.jobs.futures), 1)
                    self.assertEqual(path.read_bytes(), before)

                self.run_desktop(scenario, first_project=str(path),
                                 source_choice=str(source), output_choice=directory)

    def test_f5_keeps_notes_changed_during_discard_confirmation(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _ = create_atelier_project(directory)
            before = path.read_bytes()
            current_notes = {}

            def confirm_after_edit(**_kwargs):
                editor = current_notes['panel'].editor
                editor.delete('1.0', 'end')
                editor.insert('1.0', 'Note modifiée pendant le dialogue')
                return True

            def scenario(root, state):
                state.jobs.futures[0].result(timeout=15)
                root.pending.pop(0)()
                current_notes['panel'] = state.notes
                state.notes.editor.insert('1.0', 'Première note')
                root.events['<F5>'](None)
                self.assertEqual(state.notes.editor.get(), 'Note modifiée pendant le dialogue')
                self.assertEqual(len(state.jobs.futures), 1)
                self.assertEqual(path.read_bytes(), before)
                root.protocols['WM_DELETE_WINDOW']()

            self.run_desktop(scenario, first_project=str(path),
                             discard_notes=confirm_after_edit)

    def test_project_changes_preserve_notes_edited_during_brush_confirmation(self):
        from test_v34_native_preview_jobs import fixture_module

        for action in ('f5', 'switch', 'close', 'create'):
            for initial_note in ('', 'Note initiale à abandonner'):
                with self.subTest(action=action, initial_note=initial_note), \
                        tempfile.TemporaryDirectory() as directory:
                    path, _ = create_atelier_project(directory)
                    before = path.read_bytes()
                    source = Path(directory) / 'nouveau.png'
                    source.write_bytes(fixture_module.png())
                    notes = {}
                    prompts = []

                    def confirm(**kwargs):
                        prompts.append(kwargs)
                        # The first prompt belongs to the notes only when they
                        # were already dirty. Change the text in the *second*
                        # modal, after the earlier note decision has returned.
                        if not initial_note or len(prompts) == 2:
                            notes['panel'].editor.delete('1.0', 'end')
                            notes['panel'].editor.insert('1.0', 'Nouvelle note à conserver')
                        return True

                    def scenario(root, state):
                        state.jobs.futures[0].result(timeout=15)
                        root.pending.pop(0)()
                        notes['panel'] = state.notes
                        if initial_note:
                            state.notes.editor.insert('1.0', initial_note)
                        panel = SimpleNamespace(
                            has_draft=True, draft_checkpoint=lambda: ('unchanged',),
                            shutdown=lambda: None)
                        dialog = SimpleNamespace(lift=lambda: None, destroy=lambda: None)
                        state.atelier._brush_panel = panel
                        state.atelier._brush_dialog = dialog
                        state.atelier._brush_key = (str(path), state.atelier.snapshot.sha256,
                                                    state.atelier.selection.get())
                        if action == 'f5':
                            root.events['<F5>'](None)
                        elif action == 'switch':
                            root.events['<Control-o>'](None)
                        elif action == 'close':
                            root.protocols['WM_DELETE_WINDOW']()
                        else:
                            root.events['<Control-n>'](None)
                            state.creator.choose_source()
                            state.creator.choose_output()
                            state.creator.start()
                            self.assertIsNone(state.creator.future)
                            self.assertFalse(state.creator.busy)
                            self.assertFalse((Path(directory) /
                                'SmartSVG_Managed_Projects/nouveau.smartsvg').exists())
                        self.assertEqual(state.notes.editor.get(), 'Nouvelle note à conserver')
                        self.assertIs(state.atelier._brush_panel, panel)
                        self.assertEqual(len(state.jobs.futures), 1)
                        self.assertTrue(root.exists)
                        self.assertEqual(path.read_bytes(), before)

                    self.run_desktop(scenario, first_project=str(path),
                                     chosen=str(Path(directory) / 'other.smartsvg'),
                                     source_choice=str(source), output_choice=directory,
                                     discard_notes=confirm)

    def test_f5_preserves_brush_draft_when_discard_is_declined(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _ = create_atelier_project(directory)
            before = path.read_bytes()

            def scenario(root, state):
                state.jobs.futures[0].result(timeout=15)
                root.pending.pop(0)()
                atelier = state.atelier
                panel = SimpleNamespace(has_draft=True, draft_checkpoint=lambda: ('unchanged',),
                                        shutdown=lambda: None)
                dialog = SimpleNamespace(lift=lambda: None, destroy=lambda: None)
                atelier._brush_panel, atelier._brush_dialog = panel, dialog
                subject = atelier.selection.get()
                atelier._brush_key = (str(path), atelier.snapshot.sha256, subject)
                root.events['<F5>'](None)
                self.assertEqual(len(state.jobs.futures), 1)
                self.assertEqual(atelier.selection.get(), subject)
                self.assertIs(atelier._brush_panel, panel)
                self.assertEqual(path.read_bytes(), before)

            self.run_desktop(scenario, first_project=str(path))

    def test_notes_wait_for_brush_draft_and_preserve_both_edits(self):
        from smartsvg_core.project_archive import load_project
        with tempfile.TemporaryDirectory() as directory:
            path, _ = create_atelier_project(directory)
            before = path.read_bytes()

            def scenario(root, state):
                state.jobs.futures[0].result(timeout=15)
                root.pending.pop(0)()
                atelier = state.atelier
                closed = []
                panel = SimpleNamespace(has_draft=True, draft_checkpoint=lambda: ('unchanged',),
                                        shutdown=lambda: closed.append('panel'))
                dialog = SimpleNamespace(lift=lambda: None, destroy=lambda: closed.append('window'))
                atelier._brush_panel, atelier._brush_dialog = panel, dialog
                atelier._brush_key = (str(path), atelier.snapshot.sha256, atelier.selection.get())
                state.notes.editor.insert('1.0', 'Notes à conserver')

                state.notes.save()
                self.assertIsNone(state.notes.future)
                self.assertIs(atelier._brush_panel, panel)
                self.assertEqual(state.notes.editor.get(), 'Notes à conserver')
                self.assertIn('retouche', state.notes.status.get().lower())
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(closed, [])

                # Explicitly abandoning the brush then permits the notes write.
                self.assertTrue(atelier._request_close_brush())
                state.notes.save()
                state.notes.future.result(timeout=15)
                root.pending.pop(0)()
                self.assertEqual(load_project(path).document['notes'], 'Notes à conserver')
                self.assertEqual(closed, ['panel', 'window'])
                # Let the host's asynchronous post-save inspection release
                # its archive handle before the temporary directory is removed.
                state.jobs.futures[-1].result(timeout=15)
                root.pending.pop(0)()

            self.run_desktop(scenario, first_project=str(path), discard_notes=lambda **_: True)

    def test_recovery_cannot_start_while_a_brush_draft_is_open(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _ = create_atelier_project(directory)
            before = path.read_bytes()

            def scenario(root, state):
                state.jobs.futures[0].result(timeout=15)
                root.pending.pop(0)()
                brush = SimpleNamespace(has_draft=True,
                                        draft_checkpoint=lambda: ('unchanged',), shutdown=Mock())
                dialog = SimpleNamespace(lift=Mock(), destroy=Mock())
                state.atelier._brush_panel, state.atelier._brush_dialog = brush, dialog
                apply = Mock(return_value={'status': 'restored_from_previous',
                                           'project_id': path.stem})
                plan = SimpleNamespace(outcome='restored_from_previous',
                                       pending_sha256='missing', previous_sha256='a' * 64,
                                       project_id=path.stem, apply=apply)
                state.recovery.load(plan)
                state.recovery.start()
                self.assertIsNone(state.recovery.future)
                apply.assert_not_called()
                self.assertIn('retouche', state.recovery.status.get().lower())
                self.assertIs(state.atelier._brush_panel, brush)
                self.assertEqual(path.read_bytes(), before)
                self.assertTrue(state.atelier._request_close_brush())
                brush.shutdown.assert_called_once()
                state.recovery.start()
                self.assertIsNotNone(state.recovery.future)
                state.recovery.future.result(timeout=15)
                state.recovery.receive()
                apply.assert_called_once_with(confirmed=True)
                state.jobs.futures[-1].result(timeout=15)
                while root.pending:
                    root.pending.pop(0)()
                root.protocols['WM_DELETE_WINDOW']()

            self.run_desktop(scenario, first_project=str(path),
                             discard_notes=lambda **_: True)

    def test_notes_typed_during_recovery_survive_its_refresh(self):
        from threading import Event
        from smartsvg_core.project_archive import load_project
        from smartsvg_core.project_workspace_g22 import WorkspaceError, save_project_notes

        for external_notes in (None, 'Notes restaurées ailleurs'):
            with self.subTest(external_notes=external_notes), tempfile.TemporaryDirectory() as directory:
                path, _ = create_atelier_project(directory)
                release = Event()

                def scenario(root, state):
                    state.jobs.futures[0].result(timeout=15)
                    root.pending.pop(0)()
                    initial_sha = state.notes.revision.sha256

                    def apply(*, confirmed):
                        self.assertIs(confirmed, True)
                        self.assertTrue(release.wait(timeout=15))
                        if external_notes is not None:
                            save_project_notes(path, path.stem, notes=external_notes,
                                               expected_sha256=initial_sha)
                        return {'status': 'restored_from_previous', 'project_id': path.stem}

                    plan = SimpleNamespace(outcome='restored_from_previous',
                                           pending_sha256='missing', previous_sha256='a' * 64,
                                           project_id=path.stem, apply=apply)
                    state.recovery.load(plan)
                    state.recovery.start()
                    self.assertIsNotNone(state.recovery.future)
                    state.notes.editor.insert('1.0', 'Note saisie pendant la récupération')
                    release.set()
                    state.recovery.future.result(timeout=15)
                    state.recovery.receive()
                    self.assertEqual(state.notes.editor.get(), 'Note saisie pendant la récupération')
                    # Reinspection is asynchronous: a later edit must survive it too.
                    state.notes.editor.delete('1.0', 'end')
                    state.notes.editor.insert('1.0', 'Note modifiée pendant la relecture')
                    state.jobs.futures[-1].result(timeout=15)
                    while root.pending:
                        root.pending.pop(0)()
                    self.assertEqual(state.notes.editor.get(), 'Note modifiée pendant la relecture')
                    if external_notes is None:
                        state.notes.save()
                        state.notes.future.result(timeout=15)
                        root.pending.pop(0)()
                        state.jobs.futures[-1].result(timeout=15)
                        root.pending.pop(0)()
                        self.assertEqual(load_project(path).document['notes'],
                                         'Note modifiée pendant la relecture')
                    else:
                        self.assertEqual(load_project(path).document['notes'], external_notes)
                        self.assertIn('non synchronisée', state.notes.status.get())
                        state.notes.save()
                        with self.assertRaises(WorkspaceError) as failure:
                            state.notes.future.result(timeout=15)
                        self.assertEqual(failure.exception.code, 'PROJECT_CHANGED')
                        root.pending.pop(0)()
                        self.assertEqual(state.notes.editor.get(), 'Note modifiée pendant la relecture')
                        self.assertEqual(load_project(path).document['notes'], external_notes)
                    root.protocols['WM_DELETE_WINDOW']()

                self.run_desktop(scenario, first_project=str(path),
                                 discard_notes=lambda **_: True)

    def test_notes_survive_failed_reinspection_after_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _ = create_atelier_project(directory)

            def scenario(root, state):
                state.jobs.futures[0].result(timeout=15)
                root.pending.pop(0)()
                plan = SimpleNamespace(
                    outcome='restored_from_previous', pending_sha256='missing',
                    previous_sha256='a' * 64, project_id=path.stem,
                    apply=lambda **_kw: {'status': 'restored_from_previous',
                                         'project_id': path.stem})
                state.recovery.load(plan)
                state.recovery.start()
                state.notes.editor.insert('1.0', 'Brouillon à conserver')
                state.recovery.future.result(timeout=15)
                def failed_read(_path):
                    raise OSError('synthetic read failure')
                state.jobs._read = failed_read
                state.recovery.receive()
                with self.assertRaises(OSError):
                    state.jobs.futures[-1].result(timeout=15)
                while root.pending:
                    root.pending.pop(0)()
                self.assertEqual(state.notes.editor.get(), 'Brouillon à conserver')
                self.assertIsNotNone(state.notes.revision)
                root.protocols['WM_DELETE_WINDOW']()

            self.run_desktop(scenario, first_project=str(path),
                             discard_notes=lambda **_: True)

    def test_new_project_creation_asks_before_discarding_brush_draft(self):
        from test_v34_native_preview_jobs import fixture_module
        with tempfile.TemporaryDirectory() as directory:
            path, _ = create_atelier_project(directory)
            before = path.read_bytes()
            source = Path(directory) / 'nouveau.png'
            source.write_bytes(fixture_module.png())
            choices = iter((False, True))
            prompts = []

            def choose(**kwargs):
                prompts.append(kwargs)
                return next(choices)

            def scenario(root, state):
                state.jobs.futures[0].result(timeout=15)
                root.pending.pop(0)()
                atelier = state.atelier
                closed = []
                panel = SimpleNamespace(has_draft=True, draft_checkpoint=lambda: ('unchanged',),
                                        shutdown=lambda: closed.append('panel'))
                dialog = SimpleNamespace(lift=lambda: None, destroy=lambda: closed.append('window'))
                atelier._brush_panel, atelier._brush_dialog = panel, dialog
                atelier._brush_key = (str(path), atelier.snapshot.sha256, atelier.selection.get())
                root.events['<Control-n>'](None)
                creator = state.creator
                creator.choose_source()
                creator.choose_output()
                creator.start()
                destination = Path(directory) / 'SmartSVG_Managed_Projects/nouveau.smartsvg'
                self.assertIsNone(creator.future)
                self.assertFalse(destination.exists())
                self.assertIs(atelier._brush_panel, panel)
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(closed, [])

                creator.start()
                self.assertTrue(creator.busy)
                creator.future.result(timeout=15)
                root.pending.pop(0)()
                self.assertTrue(destination.exists())
                self.assertEqual(closed, ['panel', 'window'])
                self.assertEqual(path.read_bytes(), before)
                self.assertEqual(len(prompts), 2)
                state.jobs.futures[-1].result(timeout=15)
                root.pending.pop(0)()

            self.run_desktop(scenario, first_project=str(path), source_choice=str(source),
                             output_choice=directory, discard_notes=choose)

    def test_brush_cannot_open_while_notes_write_is_in_flight(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _ = create_atelier_project(directory)

            def scenario(root, state):
                state.jobs.futures[0].result(timeout=15)
                root.pending.pop(0)()
                state.notes.editor.insert('1.0', 'Notes en cours')
                state.notes.save()
                self.assertTrue(state.notes.busy)
                atelier = state.atelier
                # A usable brush implementation must not be instantiated against
                # the revision that the notes writer is about to replace.
                with patch.object(atelier, '_brush_class', side_effect=AssertionError('stale brush opened')):
                    self.assertFalse(atelier.open_brush())
                self.assertIsNone(atelier._brush_dialog)
                state.notes.future.result(timeout=15)
                root.pending.pop(0)()
                state.jobs.futures[-1].result(timeout=15)
                root.pending.pop(0)()

            self.run_desktop(scenario, first_project=str(path))

    def test_empty_brush_window_blocks_notes_write_until_it_is_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path, _ = create_atelier_project(directory)
            before = path.read_bytes()

            def scenario(root, state):
                state.jobs.futures[0].result(timeout=15)
                root.pending.pop(0)()
                atelier = state.atelier
                panel = SimpleNamespace(has_draft=False, shutdown=lambda: None)
                dialog = SimpleNamespace(lift=lambda: None, destroy=lambda: None)
                atelier._brush_panel, atelier._brush_dialog = panel, dialog
                state.notes.editor.insert('1.0', 'Notes conservées')
                state.notes.save()
                self.assertIsNone(state.notes.future)
                self.assertIs(atelier._brush_panel, panel)
                self.assertEqual(state.notes.editor.get(), 'Notes conservées')
                self.assertEqual(path.read_bytes(), before)

            self.run_desktop(scenario, first_project=str(path))

    def test_creation_closes_empty_brush_before_starting_writer(self):
        from test_v34_native_preview_jobs import fixture_module
        with tempfile.TemporaryDirectory() as directory:
            path, _ = create_atelier_project(directory)
            source = Path(directory) / 'nouveau.png'
            source.write_bytes(fixture_module.png())

            def scenario(root, state):
                state.jobs.futures[0].result(timeout=15)
                root.pending.pop(0)()
                atelier = state.atelier
                closed = []
                atelier._brush_panel = SimpleNamespace(
                    has_draft=False, shutdown=lambda: closed.append('panel'))
                atelier._brush_dialog = SimpleNamespace(
                    lift=lambda: None, destroy=lambda: closed.append('window'))
                root.events['<Control-n>'](None)
                creator = state.creator
                creator.choose_source()
                creator.choose_output()
                creator.start()
                self.assertTrue(creator.busy)
                self.assertIsNone(atelier._brush_panel)
                self.assertEqual(closed, ['panel', 'window'])
                with patch.object(atelier, '_brush_class', side_effect=AssertionError('brush reopened')):
                    self.assertFalse(atelier.open_brush())
                creator.future.result(timeout=15)
                root.pending.pop(0)()
                state.jobs.futures[-1].result(timeout=15)
                root.pending.pop(0)()

            self.run_desktop(scenario, first_project=str(path), source_choice=str(source),
                             output_choice=directory)

    def test_notes_save_twice_preserves_sources_and_rotates_backup(self):
        from hashlib import sha256
        from test_v34_native_preview_jobs import fixture_module
        from smartsvg_core.project_archive import load_project, save_project
        project = fixture_module.fixture()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / (project.project_id + '.smartsvg')
            backup = path.with_suffix('.previous.smartsvg')
            save_project(path, project)

            def scenario(root, state):
                state.jobs.futures[0].result(timeout=15)
                root.pending.pop(0)()
                notes = state.notes
                for text in ('Découpe\nVersion A', 'Deuxième version'):
                    before = path.read_bytes()
                    reads = len(state.jobs.futures)
                    notes.editor.insert('1.0', text)
                    state.shell.show('factory')
                    state.shell.show('project')
                    self.assertEqual(notes.editor.get(), text)
                    root.events['<F5>'](None)  # declined discard
                    root.protocols['WM_DELETE_WINDOW']()
                    self.assertEqual(notes.editor.events['<Control-o>'](None), 'break')
                    self.assertTrue(root.exists)
                    self.assertEqual(len(state.jobs.futures), reads)
                    self.assertEqual(path.read_bytes(), before)
                    notes.save()
                    future = notes.future
                    notes.save()
                    root.protocols['WM_DELETE_WINDOW']()
                    self.assertIs(notes.future, future)
                    self.assertTrue(root.exists)
                    future.result(timeout=15)
                    root.pending.pop(0)()
                    state.jobs.futures[-1].result(timeout=15)
                    root.pending.pop(0)()
                    saved = load_project(path)
                    self.assertEqual(saved.document['notes'], text)
                    self.assertEqual(saved.resources, project.resources)
                    self.assertEqual(saved.operations[-1], {'kind': 'update_notes', 'notes': text})
                    self.assertEqual(backup.read_bytes(), before)
                    self.assertEqual(notes.revision.sha256, sha256(path.read_bytes()).hexdigest())
                    self.assertIn('enregistrées et relues', notes.status.get())
                root.protocols['WM_DELETE_WINDOW']()
                self.assertFalse(root.exists)

            def keep_draft(*, parent, default):
                self.assertEqual(default, 'no')
                # Native confirmation can run a nested event loop. Re-entry
                # must neither close the window nor start a save.
                parent.protocols['WM_DELETE_WINDOW']()
                notes_button = next(widget for widget in LayoutWidget.all_widgets
                    if widget.options.get('text') == 'Enregistrer les notes')
                notes_button.options['command']()
                self.assertTrue(parent.exists)
                return False
            self.run_desktop(scenario, first_project=str(path), chosen=str(path),
                             discard_notes=keep_draft)

    def test_notes_keep_draft_after_conflict_and_failed_publication(self):
        from test_v34_native_preview_jobs import fixture_module
        from smartsvg_core.project_archive import save_project
        from smartsvg_core import project_recovery
        from smartsvg_core.project_workspace_g22 import WorkspaceError, save_project_notes
        project = fixture_module.fixture()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / (project.project_id + '.smartsvg')
            save_project(path, project)

            def scenario(root, state):
                state.jobs.futures[0].result(timeout=15)
                root.pending.pop(0)()
                notes = state.notes
                notes.editor.insert('1.0', 'Brouillon local')
                before = path.read_bytes()
                with patch.object(project_recovery, 'save_project', side_effect=OSError('disk full')):
                    notes.save()
                    with self.assertRaisesRegex(WorkspaceError, 'SAVE_FAILED'):
                        notes.future.result(timeout=15)
                    root.pending.pop(0)()
                self.assertIn('non confirmée', notes.status.get())
                self.assertEqual(path.read_bytes(), before)
                self.assertFalse(path.with_suffix('.pending-backup.smartsvg').exists())
                save_project_notes(path, project.project_id, notes='Édition externe',
                                   expected_sha256=notes.revision.sha256)
                changed = path.read_bytes()
                notes.save()
                with self.assertRaisesRegex(WorkspaceError, 'PROJECT_CHANGED'):
                    notes.future.result(timeout=15)
                root.pending.pop(0)()
                self.assertIn('modifié ailleurs', notes.status.get())
                self.assertEqual(notes.editor.get(), 'Brouillon local')
                self.assertEqual(path.read_bytes(), changed)

            self.run_desktop(scenario, first_project=str(path))

    def test_recovery_via_sidecar_selection_cancels_or_finalizes_exact_bytes(self):
        from test_v34_native_preview_jobs import fixture_module
        from smartsvg_core.project_archive import save_project

        cases = (
            ('previous', 'missing', 'Restaurer le secours'),
            ('pending-backup', 'missing', 'Récupérer le projet'),
            ('pending-backup', 'new', 'Finaliser la sauvegarde'),
            ('pending-backup', 'same', 'Clore la sauvegarde interrompue'),
        )
        for suffix, primary_state, action in cases:
            with self.subTest(suffix=suffix, primary=primary_state), tempfile.TemporaryDirectory() as directory:
                folder = Path(directory)
                project_id = 'project-test'
                target = folder / (project_id + '.smartsvg')
                selected = target.with_suffix('.' + suffix + '.smartsvg')
                backup = target.with_suffix('.previous.smartsvg')
                save_project(selected, fixture_module.fixture(2))
                old = selected.read_bytes()
                if suffix != 'previous':
                    save_project(backup, fixture_module.fixture(1))
                if primary_state == 'same':
                    target.write_bytes(old)
                if primary_state == 'new':
                    save_project(target, fixture_module.fixture(3))
                previous = backup.read_bytes()
                main = target.read_bytes() if target.exists() else None
                confirmations = []

                def consent(*, parent, default):
                    self.assertEqual(default, 'no')
                    parent.protocols['WM_DELETE_WINDOW']()
                    self.assertTrue(parent.exists)
                    confirmations.append(True)
                    return len(confirmations) == 2

                def scenario(root, state):
                    def drain_read():
                        state.jobs.futures[-1].result(timeout=15)
                        root.pending.pop(0)()
                    root.events['<Control-o>'](None)
                    drain_read()
                    button = next(w for w in LayoutWidget.all_widgets if w.options.get('text') == action)
                    callback = button.options['command']
                    callback()
                    self.assertEqual(root.pending, [])
                    self.assertEqual(selected.read_bytes(), old)
                    self.assertEqual(target.read_bytes() if target.exists() else None, main)
                    callback()
                    callback()
                    root.events['<Control-o>'](None)
                    root.protocols['WM_DELETE_WINDOW']()
                    self.assertTrue(root.exists)
                    self.assertEqual(len(confirmations), 2)
                    self.assertEqual(len(state.jobs.futures), 1)
                    import time
                    deadline = time.monotonic() + 15
                    while len(state.jobs.futures) == 1 and time.monotonic() < deadline:
                        root.pending.pop(0)()
                        time.sleep(0.005)
                    self.assertEqual(len(state.jobs.futures), 2)
                    drain_read()
                    self.assertEqual(target.read_bytes(), main if main is not None else old)
                    self.assertEqual(backup.read_bytes(), old if primary_state == 'new' else previous)
                    self.assertEqual(selected.exists(), suffix == 'previous')
                    self.assertIsNotNone(state.notes.revision)

                self.run_desktop(scenario, chosen=str(selected), discard_notes=consent)

    def test_atelier_selects_real_mask_and_tracks_the_active_project_revision(self):
        import base64
        from smartsvg_core.project_archive import load_project

        with tempfile.TemporaryDirectory() as directory:
            target, ids = create_atelier_project(directory)
            original = target.read_bytes()
            archive = load_project(target)

            def scenario(root, state):
                def receive_project():
                    state.jobs.futures[-1].result(timeout=15)
                    root.pending.pop(0)()

                receive_project()
                atelier = state.atelier
                self.assertIsNone(atelier.viewport.original)  # decoding waits until the Atelier is shown
                root.events['<Control-Key-5>'](None)
                self.assertEqual(state.shell.active_page, 'atelier')
                self.assertEqual(set(atelier.picker.options['values']), set(ids))
                old_revision = atelier.snapshot.sha256
                for subject, mask in ids.items():
                    atelier.selection.set(subject)
                    atelier.picker.events['<<ComboboxSelected>>'](None)
                    self.assertIn('Masque ' + mask, atelier.details.get())
                    self.assertIn('Liaison float32 vérifiée', atelier.details.get())
                    self.assertEqual(base64.b64decode(atelier.viewport.original.data),
                                     archive.resources[archive.mask_paths[mask]])
                self.assertEqual(target.read_bytes(), original)
                selected = atelier.selection.get()
                state.notes.editor.insert('1.0', 'Révision suivante')
                state.notes.save()
                state.notes.future.result(timeout=15)
                root.pending.pop(0)()
                self.assertIsNone(atelier.snapshot)
                state.jobs.futures[-1].result(timeout=15)
                obsolete_refresh = root.pending.pop(0)
                state.notes.editor.insert('1.0', 'Deux sauvegardes consécutives')
                state.notes.save()
                state.notes.future.result(timeout=15)
                root.pending.pop(0)()
                obsolete_refresh()
                self.assertIsNone(atelier.snapshot)
                receive_project()
                self.assertNotEqual(atelier.snapshot.sha256, old_revision)
                self.assertEqual(atelier.snapshot.sha256, state.notes.revision.sha256)
                self.assertEqual(atelier.selection.get(), selected)
                self.assertEqual(load_project(target).resources, archive.resources)
                root.events['<Control-o>'](None)
                self.assertIsNone(atelier.viewport.original)
                self.assertIsNone(atelier.snapshot)
                receive_project()
                self.assertEqual(atelier.picker.options['values'], ())

            self.run_desktop(scenario, first_project=str(target),
                             chosen=str(target.with_name('missing.smartsvg')))

    def test_atelier_distinguishes_long_legacy_subject_ids_sharing_a_mask(self):
        from dataclasses import replace
        from smartsvg_core.project_archive import load_project, save_project
        from smartsvg_core.subject_identity_g33e import BINDINGS_KEY

        with tempfile.TemporaryDirectory() as directory:
            target, _ids = create_atelier_project(directory)
            project = load_project(target)
            document = dict(project.document)
            document.pop(BINDINGS_KEY)
            prefix = 'legacy-' + 'a' * 120
            first, second = prefix + '1', prefix + '2'
            subject = project.subjects[0]
            subjects = tuple(replace(subject, subject_id=key) for key in (first, second))
            save_project(target, replace(project, document=document, subjects=subjects), overwrite=True)
            original = target.read_bytes()

            def scenario(root, state):
                state.jobs.futures[-1].result(timeout=15)
                root.pending.pop(0)()
                root.events['<Control-Key-5>'](None)
                for selected, other in ((first, second), (second, first)):
                    state.atelier.selection.set(selected)
                    state.atelier.picker.events['<<ComboboxSelected>>'](None)
                    details = state.atelier.details.get()
                    self.assertIn(selected, details)
                    self.assertNotIn(other, details)
                    self.assertIn('Masque ' + subject.mask_id, details)
                self.assertEqual(target.read_bytes(), original)

            self.run_desktop(scenario, first_project=str(target))

    def test_atelier_reads_the_archived_subjects_again_after_notes_save(self):
        from dataclasses import replace
        import native_notes_tk_v34 as notes_module
        from smartsvg_core.project_archive import load_project, save_project
        from smartsvg_core.subject_identity_g33e import BINDINGS_KEY

        with tempfile.TemporaryDirectory() as directory:
            target, ids = create_atelier_project(directory)
            save_notes = notes_module.save_project_notes
            kept_id = next(iter(ids))

            def save_with_replacement(*args, **kwargs):
                receipt = save_notes(*args, **kwargs)
                project = load_project(target, expected_sha256=receipt['sha256'])
                document = dict(project.document)
                document[BINDINGS_KEY] = {
                    'version': True,
                    'items': [item for item in document[BINDINGS_KEY]['items']
                              if item['subject_id'] == kept_id],
                }
                replacement = replace(project, document=document, subjects=tuple(
                    subject for subject in project.subjects if subject.subject_id == kept_id))
                saved = save_project(target, replacement, overwrite=True)
                return {**receipt, 'sha256': saved['sha256']}

            def scenario(root, state):
                state.jobs.futures[-1].result(timeout=15)
                root.pending.pop(0)()
                self.assertEqual(set(state.atelier.subjects), set(ids))
                state.notes.editor.insert('1.0', 'Notes enregistrées')
                with patch.object(notes_module, 'save_project_notes', side_effect=save_with_replacement):
                    state.notes.save()
                    state.notes.future.result(timeout=15)
                    root.pending.pop(0)()
                self.assertIsNone(state.atelier.snapshot)
                state.jobs.futures[-1].result(timeout=15)
                root.pending.pop(0)()
                self.assertEqual(state.atelier.snapshot.sha256, state.notes.revision.sha256)
                self.assertEqual(tuple(state.atelier.subjects), (kept_id,))
                self.assertEqual(state.atelier.subjects[kept_id].proof_status, 'unverified')
                self.assertEqual(state.notes.editor.get(), 'Notes enregistrées')

            self.run_desktop(scenario, first_project=str(target))

    def test_native_brush_receipt_refresh_preserves_and_rebases_dirty_notes(self):
        """Real archive CAS change; UI save completion is simulated, not CPU."""
        from smartsvg_core.project_archive import load_project
        from smartsvg_core.project_workspace_g22 import save_project_notes

        with tempfile.TemporaryDirectory() as directory:
            target, ids = create_atelier_project(directory)
            subject_id = next(iter(ids))

            def scenario(root, state):
                state.jobs.futures[-1].result(timeout=15)
                root.pending.pop(0)()
                before = load_project(target)
                original_sha = state.atelier.snapshot.sha256
                state.atelier.selection.set(subject_id)
                state.atelier.render()
                notes = state.notes
                notes.editor.insert('1.0', 'Brouillon maintenu après retouche')
                original_notes = notes.revision.notes
                receipt = save_project_notes(
                    target, target.stem, notes=original_notes,
                    expected_sha256=original_sha)
                self.assertNotEqual(receipt['sha256'], original_sha)
                # Simulate the verified bridge callback after a committed edit.
                state.atelier._on_saved({
                    'subject_id': subject_id, 'persisted': True,
                    'project_sha256': receipt['sha256']})
                self.assertIsNone(state.atelier.snapshot)
                state.jobs.futures[-1].result(timeout=15)
                root.pending.pop(0)()
                self.assertEqual(state.atelier.snapshot.sha256, receipt['sha256'])
                self.assertEqual(state.atelier.selection.get(), subject_id)
                self.assertEqual(notes.editor.get(), 'Brouillon maintenu après retouche')
                self.assertEqual(notes.revision.sha256, receipt['sha256'])
                self.assertIn('conservé', notes.status.get())
                self.assertEqual(load_project(target).resources, before.resources)
                # The draft can now be saved with the new CAS revision.
                notes.save()
                notes.future.result(timeout=15)
                root.pending.pop(0)()
                state.jobs.futures[-1].result(timeout=15)
                root.pending.pop(0)()
                self.assertEqual(load_project(target).document['notes'],
                                 'Brouillon maintenu après retouche')

            self.run_desktop(scenario, first_project=str(target))

    def seed_history_project(self, directory):
        from smartsvg_core.native_subject_preview_v34 import preview_native_subject_stroke
        from smartsvg_core.native_subject_save_v34 import save_native_subject_stroke
        from smartsvg_core.project_archive import load_project
        from hashlib import sha256
        target, ids = create_atelier_project(directory)
        subject = next(iter(ids))
        request = dict(project_path=str(target), expected_sha256=sha256(target.read_bytes()).hexdigest(),
                       subject_id=subject, mode='add', radius=.05, points=[[.5, .5]])
        preview = preview_native_subject_stroke(**request)
        save_native_subject_stroke(
            **request, expected_preview_mask_sha256_float32=preview['preview_mask_sha256_float32'],
            command_id='desktop-history-seed', confirmed=True)
        return target, subject, load_project(target)

    @unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'),
                         'Real desktop history requires NumPy/Pillow')
    def test_history_commands_refresh_real_project_and_preserve_dirty_notes(self):
        from smartsvg_core.project_archive import load_project
        with tempfile.TemporaryDirectory() as directory:
            target, subject, saved = self.seed_history_project(directory)
            def scenario(root, state):
                state.jobs.futures[-1].result(timeout=15); root.pending.pop(0)()
                p = state.atelier
                p.parent.after = root.after  # Tk-frame scheduling in widget double.
                p._confirm_history_fn = lambda *_args: True
                p.selection.set(subject); p.render()
                notes = state.notes
                notes.editor.insert('1.0', 'Notes encore non enregistrées')
                for button, action in ((p.undo_button, 'undo'), (p.redo_button, 'redo')):
                    self.assertEqual(button.options['state'], 'normal')
                    reads = len(state.jobs.futures)
                    button.options['command']()
                    self.assertTrue(p.busy)
                    root.events['<Control-o>'](None)
                    root.events['<F5>'](None)
                    root.protocols['WM_DELETE_WINDOW']()
                    notes.save()
                    self.assertIsNone(notes.future)
                    self.assertTrue(root.exists)
                    self.assertEqual(len(state.jobs.futures), reads)
                    p._history_future.result(timeout=15); root.pending.pop(0)()
                    # Receipt acknowledged, but host reinspection not delivered:
                    # no notes writer can race the pending revision adoption.
                    self.assertTrue(p.history_requires_review)
                    notes.save()
                    self.assertIsNone(notes.future)
                    state.jobs.futures[-1].result(timeout=15); root.pending.pop(0)()
                    self.assertEqual(p.selection.get(), subject)
                    self.assertEqual(notes.editor.get(), 'Notes encore non enregistrées')
                    self.assertEqual(notes.revision.sha256, p.snapshot.sha256)
                    self.assertFalse(p.history_requires_review)
                    if action == 'undo':
                        self.assertNotIn('editor_v216', load_project(target).document)
                self.assertEqual(load_project(target).document['editor_v216'], saved.document['editor_v216'])
                self.assertEqual(load_project(target).resources, saved.resources)
            self.run_desktop(scenario, first_project=str(target), chosen=str(target))

    @unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'),
                         'Real desktop history requires NumPy/Pillow')
    def test_history_host_read_failure_or_mismatch_keeps_notes_write_blocked(self):
        from dataclasses import replace
        for failure in ('reader', 'revision', 'submit'):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as directory:
                target, subject, _ = self.seed_history_project(directory)
                def scenario(root, state):
                    state.jobs.futures[-1].result(timeout=15); root.pending.pop(0)()
                    p, notes = state.atelier, state.notes
                    p.parent.after = root.after
                    p._confirm_history_fn = lambda *_args: True
                    p.selection.set(subject); p.render()
                    notes.editor.insert('1.0', 'Brouillon non perdu après écriture')
                    old_revision = notes.revision
                    before = target.read_bytes()
                    read = state.jobs._read
                    def failed(*_args):
                        raise OSError('/private/reader-failure')
                    def mismatch(path):
                        state_, preview = read(path)
                        state_['atelier_snapshot'] = replace(
                            state_['atelier_snapshot'], sha256='0' * 64)
                        return state_, preview
                    if failure == 'submit':
                        state.jobs.submit = failed
                    else:
                        state.jobs._read = failed if failure == 'reader' else mismatch
                    self.assertTrue(p.undo_brush())
                    p._history_future.result(timeout=15); root.pending.pop(0)()
                    self.assertTrue(p.history_requires_review)
                    notes.save()
                    self.assertIsNone(notes.future)
                    if failure != 'submit':
                        if failure == 'reader':
                            with self.assertRaises(OSError): state.jobs.futures[-1].result(timeout=15)
                        else:
                            state.jobs.futures[-1].result(timeout=15)
                        root.pending.pop(0)()
                    self.assertNotEqual(target.read_bytes(), before)
                    self.assertIsNone(p.snapshot)
                    self.assertTrue(p.history_requires_review)
                    notes.save()
                    self.assertIsNone(notes.future)
                    self.assertEqual(notes.revision, old_revision)
                    self.assertEqual(notes.editor.get(), 'Brouillon non perdu après écriture')
                    self.assertFalse(p.undo_brush())
                    self.assertNotIn('/private/', p.project.get())
                self.run_desktop(scenario, first_project=str(target))

    @unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'),
                         'Real desktop history requires NumPy/Pillow')
    def test_uncertain_history_after_real_commit_keeps_notes_and_blocks_other_writes(self):
        from smartsvg_core.native_brush_history_command_v34 import change_native_brush_history
        with tempfile.TemporaryDirectory() as directory:
            target, subject, _ = self.seed_history_project(directory)
            def scenario(root, state):
                state.jobs.futures[-1].result(timeout=15); root.pending.pop(0)()
                p = state.atelier
                p.parent.after = root.after
                p._confirm_history_fn = lambda *_args: True
                p.selection.set(subject); p.render()
                state.notes.editor.insert('1.0', 'Brouillon à conserver')
                before = target.read_bytes()
                def interrupted(**request):
                    change_native_brush_history(**request)
                    raise OSError('/private/post-commit')
                p._history_change_fn = interrupted
                self.assertTrue(p.undo_brush())
                with self.assertRaises(OSError): p._history_future.result(timeout=15)
                root.pending.pop(0)()
                self.assertNotEqual(target.read_bytes(), before)
                self.assertTrue(p.history_requires_review)
                self.assertIn('non confirmée', p.history.get())
                self.assertNotIn('/private/', p.history.get())
                state.notes.save()
                self.assertIsNone(state.notes.future)
                self.assertEqual(state.notes.editor.get(), 'Brouillon à conserver')
                self.assertFalse(p.undo_brush())
                self.assertEqual(len(state.jobs.futures), 1)
            self.run_desktop(scenario, first_project=str(target))

    def test_native_brush_refresh_does_not_rebase_external_notes_conflict(self):
        from smartsvg_core.project_archive import load_project
        from smartsvg_core.project_workspace_g22 import (
            save_project_notes, WorkspaceError)

        with tempfile.TemporaryDirectory() as directory:
            target, ids = create_atelier_project(directory)
            subject_id = next(iter(ids))

            def scenario(root, state):
                state.jobs.futures[-1].result(timeout=15)
                root.pending.pop(0)()
                notes = state.notes
                notes.editor.insert('1.0', 'Ne pas effacer ce brouillon')
                previous_sha = notes.revision.sha256
                receipt = save_project_notes(
                    target, target.stem, notes='Changement externe',
                    expected_sha256=previous_sha)
                state.atelier._on_saved({
                    'subject_id': subject_id, 'persisted': True,
                    'project_sha256': receipt['sha256']})
                state.jobs.futures[-1].result(timeout=15)
                root.pending.pop(0)()
                self.assertEqual(notes.editor.get(), 'Ne pas effacer ce brouillon')
                self.assertEqual(notes.revision.sha256, previous_sha)
                self.assertIn('non synchronisée', notes.status.get())
                notes.save()
                with self.assertRaisesRegex(WorkspaceError, 'PROJECT_CHANGED'):
                    notes.future.result(timeout=15)
                root.pending.pop(0)()
                self.assertEqual(load_project(target).document['notes'],
                                 'Changement externe')

            self.run_desktop(scenario, first_project=str(target))

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

    def setUp(self):
        # Collect test widget cycles on the Tk thread after root.destroy().
        # Otherwise the next worker can trigger Tcl finalizers off-thread.
        gc.collect()
        self.addCleanup(gc.collect)

    def test_actual_desktop_png_creation_and_reopen(self):
        try:
            import tkinter as tk
            from tkinter import filedialog, ttk
        except ImportError as exc:
            self.skipTest(f'Tkinter unavailable: {exc}')
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest('No graphical Tk session available')
        self.addCleanup(root.destroy)
        import time
        import standalone_desktop_v34 as desktop
        from native_theme_tk_v34 import ArtisanThemePicker
        from test_v34_native_preview_jobs import fixture_module
        from smartsvg_core.project_archive import load_project
        captured = []
        class Creator(desktop.NativeCreateDialog):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                captured.append(self)
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'image.png'
            source.write_bytes(fixture_module.png())
            def theme(**kwargs):
                return ArtisanThemePicker(**kwargs, settings_path=Path(directory) / 'appearance.json')
            def scenario():
                root.update()
                def widgets(parent):
                    for child in parent.winfo_children():
                        yield child
                        yield from widgets(child)
                action = next(widget for widget in widgets(root)
                    if isinstance(widget, ttk.Button) and widget.cget('text') == 'Créer depuis un PNG…'
                    and widget.winfo_viewable())
                action.invoke()
                dialog = captured[0]
                dialog.choose_source(); dialog.choose_output()
                # Long display paths must not push actions/errors out of the
                # minimum-height dialog; original path variables stay intact.
                dialog.window.geometry('660x580')
                long_path = '/very-long-selected-path/'*30
                dialog.source.set(long_path); dialog.output.set(long_path)
                dialog.status.set('PNG invalide ou non pris en charge : choisir un autre fichier avant de continuer.')
                root.update()
                self.assertEqual(dialog.source.get(), long_path)
                for widget in (dialog.create_button, dialog.status_label):
                    self.assertTrue(widget.winfo_viewable())
                    self.assertLessEqual(widget.winfo_rooty()+widget.winfo_height(),
                                         dialog.window.winfo_rooty()+dialog.window.winfo_height())
                dialog.source.set(str(source)); dialog.output.set(directory)
                dialog.create_button.invoke()
                deadline = time.monotonic()+15
                while dialog.busy and time.monotonic()<deadline:
                    root.update(); time.sleep(0.005)
                self.assertFalse(dialog.busy, dialog.status.get())
                self.assertFalse(dialog.window.winfo_exists(), dialog.status.get())
                target = Path(directory) / 'SmartSVG_Managed_Projects/image.smartsvg'
                project = load_project(target)
                self.assertEqual(project.resources['sources/source-original.png'], source.read_bytes())
                self.assertEqual(project.sources[0].provenance, 'manual_native_png_import')
                def visible_values():
                    return [str(root.getvar(widget.cget('textvariable'))) for widget in widgets(root)
                            if isinstance(widget, ttk.Label) and widget.cget('textvariable')]
                deadline = time.monotonic()+15
                while time.monotonic()<deadline:
                    root.update()
                    values = visible_values()
                    if any(value.startswith('Source source-original') for value in values): break
                    time.sleep(0.005)
                self.assertTrue(any(value.startswith('Projet créé, enregistré et relu') for value in values))
                self.assertTrue(any(value.startswith('Projet : image') for value in values))
                self.assertTrue(any(value.startswith('Source source-original') for value in values))
                editor = next(widget for widget in widgets(root) if isinstance(widget, tk.Text))
                save_notes = next(widget for widget in widgets(root)
                    if isinstance(widget, ttk.Button) and widget.cget('text') == 'Enregistrer les notes')
                self.assertTrue(editor.winfo_viewable())
                self.assertTrue(save_notes.winfo_viewable())
                editor.focus_force()
                root.update()
                with patch.object(filedialog, 'askopenfilename', return_value='') as picker:
                    editor.event_generate('<Control-o>')
                    root.update()
                    picker.assert_called_once()
                self.assertEqual(editor.get('1.0', 'end-1c'), '')
                notes = 'À vérifier\nVersion 2'
                editor.insert('1.0', notes)
                original = target.read_bytes()
                save_notes.invoke()
                deadline = time.monotonic()+15
                while time.monotonic()<deadline:
                    root.update()
                    values = visible_values()
                    if (any(value.startswith('Notes enregistrées et relues') for value in values)
                            and any(value.startswith('Source source-original') for value in values)):
                        break
                    time.sleep(0.005)
                self.assertTrue(any(value.startswith('Notes enregistrées et relues')
                                    for value in visible_values()))
                self.assertEqual(load_project(target).document['notes'], notes)
                self.assertEqual(target.with_suffix('.previous.smartsvg').read_bytes(), original)
                target.write_bytes(b'synthetic damaged project')
                recheck = next(widget for widget in widgets(root)
                    if isinstance(widget, ttk.Button) and widget.cget('text') == 'Réexaminer (F5)')
                recheck.invoke()
                deadline = time.monotonic()+15
                restore = None
                while time.monotonic()<deadline:
                    root.update()
                    restore = next((widget for widget in widgets(root)
                        if isinstance(widget, ttk.Button) and widget.cget('text') == 'Restaurer le secours'
                        and widget.winfo_viewable()), None)
                    if restore is not None:
                        break
                    time.sleep(0.005)
                self.assertIsNotNone(restore)
                from tkinter import messagebox
                with patch.object(messagebox, 'askyesno', return_value=True) as confirm:
                    restore.invoke()
                    self.assertEqual(confirm.call_args.kwargs['default'], 'no')
                deadline = time.monotonic()+15
                while time.monotonic()<deadline:
                    root.update()
                    values = visible_values()
                    if (any(value.startswith('Projet restauré depuis') for value in values)
                            and any(value.startswith('Source source-original') for value in values)):
                        break
                    time.sleep(0.005)
                values = visible_values()
                self.assertTrue(any(value.startswith('Projet restauré depuis') for value in values))
                self.assertTrue(any(value.startswith('Source source-original') for value in values))
                self.assertEqual(editor.get('1.0', 'end-1c'), '')
                self.assertEqual(target.read_bytes(), original)
                self.assertEqual(target.with_suffix('.previous.smartsvg').read_bytes(), original)

            with patch.object(tk, 'Tk', return_value=root), \
                 patch.object(root, 'mainloop', side_effect=scenario), \
                 patch.object(filedialog, 'askopenfilename', return_value=str(source)), \
                 patch.object(filedialog, 'askdirectory', return_value=directory), \
                 patch.object(desktop, 'ArtisanThemePicker', side_effect=theme), \
                 patch.object(desktop, 'NativeCreateDialog', Creator):
                self.assertEqual(desktop._start_gui(None), 0)

    def test_actual_atelier_selects_two_archived_subject_masks(self):
        try:
            import tkinter as tk
        except ImportError as exc:
            self.skipTest(f'Tkinter unavailable: {exc}')
        try:
            root = tk.Tk()
        except tk.TclError:
            self.skipTest('No graphical Tk session available')
        self.addCleanup(root.destroy)
        import time
        import standalone_desktop_v34 as desktop
        from native_theme_tk_v34 import ArtisanThemePicker
        captured = []

        class Atelier(desktop.NativeAtelierPanel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                captured.append(self)

        with tempfile.TemporaryDirectory() as directory:
            target, ids = create_atelier_project(directory)
            before = target.read_bytes()

            def theme(**kwargs):
                return ArtisanThemePicker(**kwargs, settings_path=Path(directory) / 'appearance.json')

            def scenario():
                root.geometry('900x650')
                deadline = time.monotonic() + 15
                while not captured[0].subjects and time.monotonic() < deadline:
                    root.update()
                    time.sleep(0.005)
                atelier = captured[0]
                self.assertEqual(set(atelier.subjects), set(ids))
                root.focus_force()
                root.update()
                root.event_generate('<Control-Key-5>')
                root.update()
                self.assertTrue(atelier.picker.winfo_viewable())
                self.assertIsNotNone(atelier.viewport.original)
                for subject, mask in ids.items():
                    atelier.picker.set(subject)
                    atelier.picker.event_generate('<<ComboboxSelected>>')
                    root.update()
                    self.assertIn('Masque ' + mask, atelier.details.get())
                    self.assertEqual((atelier.viewport.original.width(), atelier.viewport.original.height()), (4, 3))
                    self.assertTrue(atelier.viewport.canvas.winfo_viewable())
                    self.assertEqual(atelier.viewport.fit_scale, 1)
                    atelier.viewport.actual_button.invoke()
                    self.assertIs(atelier.viewport.display, atelier.viewport.original)
                    self.assertIsNone(atelier.viewport.fit_scale)
                self.assertEqual(target.read_bytes(), before)

            with patch.object(tk, 'Tk', return_value=root), \
                 patch.object(root, 'mainloop', side_effect=scenario), \
                 patch.object(desktop, 'ArtisanThemePicker', side_effect=theme), \
                 patch.object(desktop, 'NativeAtelierPanel', Atelier):
                self.assertEqual(desktop._start_gui(str(target)), 0)

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
            self.addCleanup(theme.shutdown)
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
