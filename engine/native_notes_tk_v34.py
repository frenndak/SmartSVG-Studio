"""Explicit, revision-bound V1 notes edits in the native project workspace."""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from smartsvg_core.project_workspace_g22 import MAX_NOTE_LENGTH, save_project_notes


@dataclass(frozen=True)
class NotesRevision:
    path: Path
    project_id: str
    sha256: str
    notes: str


class NativeNotesPanel:
    def __init__(self, root, parent, tk, ttk, messagebox, *, on_saved=None):
        self.root = root
        self.messagebox = messagebox
        self.on_saved = on_saved
        self.revision = None
        self.future = None
        self.confirming_discard = False
        self.worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix='smartsvg-notes')
        self.status = tk.StringVar()
        ttk.Label(parent, text=f'Notes du projet · {MAX_NOTE_LENGTH} caractères max.').pack(anchor='w')
        self.editor = tk.Text(parent, height=3, width=40, wrap='word', undo=True,
                              font='TkDefaultFont')
        self.editor.pack(fill='x', pady=(2, 4))
        actions = ttk.Frame(parent)
        actions.pack(fill='x')
        self.button = ttk.Button(actions, text='Enregistrer les notes', command=self.save)
        self.button.pack(side='left', padx=(0, 8))
        ttk.Label(actions, textvariable=self.status, wraplength=440).pack(side='left')
        self.load(None)

    @property
    def busy(self):
        return self.future is not None

    def load(self, revision):
        self.revision = revision
        self.editor.configure(state='normal')
        self.editor.delete('1.0', 'end')
        if revision is not None:
            self.editor.insert('1.0', revision.notes)
        self.editor.edit_reset()
        self._enable(revision is not None)
        self.status.set('' if revision is not None else 'Notes en lecture seule ou projet indisponible.')

    def _enable(self, editable):
        state = 'normal' if editable else 'disabled'
        self.editor.configure(state=state)
        self.button.configure(state=state)

    def _draft(self):
        return self.editor.get('1.0', 'end-1c')

    def can_leave(self):
        if self.busy:
            self.status.set('Sauvegarde en cours. Attendez son résultat.')
            return False
        if self.confirming_discard:
            return False
        if self.revision is None or self._draft() == self.revision.notes:
            return True
        self.confirming_discard = True
        try:
            return self.messagebox.askyesno('Notes non enregistrées',
                'Abandonner les modifications apportées aux notes ?',
                parent=self.root, default='no')
        finally:
            self.confirming_discard = False

    def save(self):
        if self.busy or self.confirming_discard or self.revision is None:
            return
        draft = self._draft()
        revision = self.revision
        if draft == revision.notes:
            self.status.set('Notes déjà enregistrées.')
            return
        if len(draft) > MAX_NOTE_LENGTH:
            self.status.set(f'Réduisez les notes à {MAX_NOTE_LENGTH} caractères.')
            return
        self._enable(False)
        self.status.set('Enregistrement en cours…')
        self.future = self.worker.submit(save_project_notes, revision.path, revision.project_id,
                                         notes=draft, expected_sha256=revision.sha256)
        self.root.after(50, lambda: self._receive(revision, draft))

    def _receive(self, revision, draft):
        if not self.future.done():
            self.root.after(50, lambda: self._receive(revision, draft))
            return
        future, self.future = self.future, None
        self._enable(True)
        try:
            receipt = future.result()
        except Exception as exc:
            code = getattr(exc, 'code', '')
            messages = {
                'PROJECT_CHANGED': 'Projet modifié ailleurs. Copiez le brouillon avant de réexaminer.',
                'PROJECT_CHANGED_DURING_SAVE': 'Projet modifié ailleurs. Copiez le brouillon avant de réexaminer.',
                'PROJECT_NOT_FOUND': 'Projet introuvable. Le brouillon reste ouvert.',
                'PENDING_BACKUP_REVIEW_REQUIRED': 'Une sauvegarde de secours doit être examinée. Brouillon conservé.',
                'BACKUP_CONFLICT': 'Le fichier de secours est incompatible. Brouillon conservé.',
                'HISTORY_LIMIT': 'Historique plein. Brouillon conservé.',
                'PROJECT_LOCKED': 'Projet occupé. Vous pouvez réessayer.',
            }
            self.status.set(messages.get(code, 'Sauvegarde non confirmée. Brouillon conservé.'))
            return
        self.revision = NotesRevision(revision.path, revision.project_id, receipt['sha256'], draft)
        self.status.set('Notes enregistrées et relues · SHA ' + receipt['sha256'][:12])
        if self.on_saved is not None:
            self.on_saved(revision, self.revision)

    def shutdown(self):
        self.worker.shutdown(wait=True)
