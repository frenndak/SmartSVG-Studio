"""Explicit single-flight native project creation; no replaceable write jobs.

All widget access is on Tk's thread. A submitted write is never cancelled or
retried automatically; closing waits for its outcome before destroying Tk.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import re
import unicodedata

from smartsvg_core.native_project_create_v34 import create_native_project, NativeCreateError
from smartsvg_core.project_workspace_g22 import PROFILES


class NativeCreateDialog:
    def __init__(self, root, tk, ttk, filedialog, on_created, *, can_create=None):
        self.root, self.filedialog, self.on_created = root, filedialog, on_created
        self.can_create = can_create
        self.window = tk.Toplevel(root)
        self.window.title('Créer un projet depuis un PNG')
        self.window.geometry('700x620')
        self.window.minsize(660, 580)
        self.window.transient(root)
        self.window.protocol('WM_DELETE_WINDOW', self.close)
        self.source = tk.StringVar(value='')
        self.output = tk.StringVar(value='')
        self.name = tk.StringVar(value='mon_projet')
        self.profile = tk.StringVar(value='Auto - conserver le visuel')
        self.width = tk.StringVar(value='40')
        self.dpi = tk.StringVar(value='300')
        self.status = tk.StringVar(value='Choisir un PNG et un dossier, puis créer le projet.')
        self.future, self.executor = None, None
        self.busy = False
        self._path_traces = []
        self._tcl_error = getattr(tk, 'TclError', RuntimeError)
        self.controls = []
        outer = ttk.Frame(self.window, padding=18)
        outer.pack(fill='both', expand=True)
        # Reserve actions and diagnostic space before the expanding form.
        footer = ttk.Frame(outer)
        footer.pack(side='bottom', fill='x')
        actions = ttk.Frame(footer)
        actions.pack(fill='x')
        self.create_button = self._button(ttk, actions, 'Créer et ouvrir', self.start, side='left')
        ttk.Button(actions, text='Fermer', command=self.close).pack(side='left', padx=8, pady=4)
        self.status_label = ttk.Label(footer, textvariable=self.status, wraplength=610)
        self.status_label.pack(anchor='w', pady=10)
        frame = ttk.Frame(outer)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='Nouveau projet', font=('Segoe UI', 16, 'bold')).pack(anchor='w')
        ttk.Label(frame, text=(
            'Le PNG original est conservé. La création enregistre une archive V1 '
            'dans le sous-dossier SmartSVG_Managed_Projects du dossier choisi. '
            'Aucun détourage, masque ou export n’est généré.'), wraplength=620).pack(anchor='w', pady=(6, 12))
        self._button(ttk, frame, 'Choisir le PNG…', self.choose_source)
        self._path_label(tk, ttk, frame, self.source)
        self._button(ttk, frame, 'Choisir le dossier des projets…', self.choose_output)
        self._path_label(tk, ttk, frame, self.output)
        self._field(ttk, frame, 'Nom (lettres/chiffres, tiret ou _, 48 caractères maximum)', self.name)
        self._field(ttk, frame, 'Intention (réglage initial, sans traitement automatique)', self.profile,
                    values=tuple(sorted(PROFILES)))
        dimensions = ttk.Frame(frame)
        dimensions.pack(fill='x')
        left, right = ttk.Frame(dimensions), ttk.Frame(dimensions)
        left.pack(side='left', fill='x', expand=True)
        right.pack(side='left', fill='x', expand=True)
        self._field(ttk, left, 'Largeur (mm, de 5 à 300)', self.width, width=24)
        self._field(ttk, right, 'Résolution (DPI)', self.dpi, values=('300', '450'), width=18)

    def _path_label(self, tk, ttk, frame, variable):
        display = tk.StringVar(value='')
        def update(*_unused):
            text = ' '.join(variable.get().split())
            display.set(text if len(text) <= 96 else text[:24] + ' … ' + text[-68:])
        self._path_traces.append((variable, variable.trace_add('write', update)))
        update()
        ttk.Label(frame, textvariable=display, wraplength=610).pack(anchor='w', pady=(3, 8))

    def _button(self, ttk, frame, text, command, **pack_options):
        button = ttk.Button(frame, text=text, command=command)
        button.pack(anchor='w', pady=4, **pack_options)
        self.controls.append((button, 'normal'))
        return button

    def _field(self, ttk, frame, label, variable, *, values=None, width=48):
        row = ttk.Frame(frame)
        row.pack(fill='x', pady=4)
        ttk.Label(row, text=label, wraplength=600).pack(anchor='w')
        if values is None:
            widget = ttk.Entry(row, textvariable=variable, width=width)
            normal = 'normal'
        else:
            widget = ttk.Combobox(row, textvariable=variable, values=values, state='readonly', width=width)
            normal = 'readonly'
        widget.pack(anchor='w')
        self.controls.append((widget, normal))

    def choose_source(self):
        if self.busy: return
        chosen = self.filedialog.askopenfilename(parent=self.window,
            title='Choisir une image PNG', filetypes=[('Image PNG', '*.png')])
        if chosen:
            from pathlib import Path
            self.source.set(chosen)
            name = unicodedata.normalize('NFKD', Path(chosen).stem).encode('ascii', 'ignore').decode()
            name = re.sub(r'[^A-Za-z0-9_-]', '-', name).strip('-_')[:48]
            self.name.set(name if name and not name.endswith('_previous') else 'mon_projet')

    def choose_output(self):
        if self.busy: return
        chosen = self.filedialog.askdirectory(parent=self.window,
            title='Dossier qui contiendra vos projets', mustexist=True)
        if chosen: self.output.set(chosen)

    def start(self):
        if self.busy: return
        if not self.source.get() or not self.output.get():
            self.status.set('Choisir un PNG et un dossier de projets avant de continuer.')
            return
        try:
            width = self.width.get().strip().replace(',', '.')
            if len(width) > 64 or self.dpi.get() not in ('300', '450'):
                raise ValueError('invalid dimensions')
            args = dict(source_path=self.source.get(), output_root=self.output.get(),
                name=self.name.get(), profile=self.profile.get(), width_mm=width, dpi=int(self.dpi.get()))
        except (ValueError, TypeError):
            self.status.set('Vérifier la largeur en mm et la résolution (300 ou 450 DPI).')
            return
        if self.can_create is not None and not self.can_create():
            return
        self.window.grab_set()
        self.busy = True
        for widget, _state in self.controls: widget.configure(state='disabled')
        self.status.set('Création et vérification de la sauvegarde en cours…')
        try:
            if self.executor is None:
                self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='smartsvg-create')
            self.future = self.executor.submit(create_native_project, **args)
        except RuntimeError:
            self._error(None)
            return
        self.root.after(50, self._receive)

    def _error(self, error):
        self.window.grab_release()
        self.busy = False
        for widget, state in self.controls: widget.configure(state=state)
        code = error.code if isinstance(error, NativeCreateError) else ''
        messages = {
            'INVALID_PROJECT_NAME': 'Nom invalide : utiliser 1 à 48 lettres/chiffres, tirets ou _, sans nom réservé Windows.',
            'PROJECT_ALREADY_EXISTS': 'Un projet ou secours porte déjà ce nom. Choisir un autre nom ; il est conservé.',
            'INVALID_WIDTH': 'Largeur invalide : choisir une valeur de 5 à 300 mm.',
            'INVALID_DPI': 'Résolution invalide : choisir 300 ou 450 DPI.',
            'INVALID_PROFILE': 'Choisir une intention dans la liste.',
            'INVALID_WORKSPACE_ROOT': 'Dossier indisponible ou non sûr. Choisir un dossier existant.',
            'SOURCE_READ_FAILED': 'PNG illisible : vérifier le fichier et ses droits d’accès.',
            'INVALID_SOURCE_PATH': 'Choisir un fichier PNG local ordinaire, sans lien symbolique.',
        }
        if code == 'IMAGE_TOO_LARGE' or code.startswith(('INVALID_PNG', 'UNSUPPORTED', 'PNG_', 'INVALID_IMAGE', 'INCOMPLETE_PNG')):
            message = 'PNG invalide ou non pris en charge : choisir un PNG 8 bits L, RGB ou RGBA non entrelacé, jusqu’à 12 Mio et 20 millions de pixels.'
        else:
            message = messages.get(code, 'Création non confirmée : vérifier le dossier et les fichiers avant de réessayer. Aucun nouvel essai automatique.')
        self.status.set(message)

    def _receive(self):
        if not self.window.winfo_exists(): return
        if not self.future.done():
            self.root.after(50, self._receive)
            return
        try:
            receipt = self.future.result()
        except Exception as error:
            self._error(error)
            return
        self.busy = False
        self.window.grab_release()
        self.status.set('Projet enregistré et vérifié.')
        try:
            self.on_created(receipt)
        except Exception:
            self.status.set('Projet enregistré et vérifié, mais ouverture non confirmée. Ouvrir son fichier .smartsvg depuis le dossier choisi.')
            return
        self.close()

    def close(self):
        if self.busy:
            self.status.set('Création en cours : attendre son résultat avant de fermer. L’écriture n’est pas annulée.')
            return False
        if self.window.winfo_exists(): self.window.destroy()
        self.shutdown()
        return True

    def shutdown(self):
        if self.executor is not None:
            # On an unexpected main-loop exit, settle the write before exit.
            self.executor.shutdown(wait=True)
            self.executor = None
        traces, self._path_traces = self._path_traces, []
        for variable, handle in traces:
            try:
                variable.trace_remove('write', handle)
            except self._tcl_error:
                # The interpreter may already have been destroyed by the host.
                pass
