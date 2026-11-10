"""Atelier workspace for inspecting the subjects persisted in a V1 project."""
from __future__ import annotations

import base64
from pathlib import Path
import re

from native_image_viewport_v34 import NativeImageViewport


PROOF_LABELS = {
    'verified': 'Liaison float32 vérifiée',
    'legacy_subject_record': 'Liaison float32 historique',
    'unverified': 'Identité float32 non vérifiée pour ce sujet',
    'png_only': 'Masque PNG archivé',
}

# Read-only, actionable feedback. Never expose file-system paths or attempt repair.
MASK_PREVIEW_ERRORS = {
    'SOURCE_TOO_LARGE': 'Masque trop volumineux pour l’aperçu sécurisé. L’archive reste intacte.',
    'SOURCE_MISSING': 'Ressource du masque absente. Réexaminez le projet (F5) et vérifiez ses sauvegardes.',
    'SOURCE_INVALID_PNG': 'PNG du masque invalide. Réexaminez le projet (F5) avant toute modification.',
    'SOURCE_CHANGED': 'Le masque ne correspond pas aux dimensions ou à l’empreinte attendues. Réexaminez le projet (F5).',
}

_PROVEN_SUBJECT = re.compile(r'^subject-[0-9a-f]{32}    def __init__(self, parent, tk, ttk):
        self.tk, self.ttk, self.parent = tk, ttk, parent
        self.snapshot = None
        self.subjects = {}
        self._project_path = None
        self._brush_dialog = self._brush_panel = self._brush_key = None
        # The G3.3e brush is delivered separately; no duplicated engine.
        try:
            from native_brush_draft_tk_v34 import NativeBrushDraftPanel
        except ImportError:
            self._brush_class = None
        else:
            self._brush_class = NativeBrushDraftPanel
        self.project = tk.StringVar()
        self.selection = tk.StringVar()
        self.details = tk.StringVar()
        ttk.Label(parent, text='Atelier', font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 12))
        ttk.Label(parent, textvariable=self.project, wraplength=640).pack(anchor='w')
        ttk.Label(parent, text='Sujet enregistré · inspection en lecture seule').pack(anchor='w', pady=(8, 0))
        self.picker = ttk.Combobox(parent, textvariable=self.selection, state='disabled', width=52)
        self.picker.pack(anchor='w', fill='x', pady=(3, 8))
        self.picker.bind('<<ComboboxSelected>>', self.render)
        ttk.Label(parent, textvariable=self.details, wraplength=640).pack(anchor='w', pady=(0, 8))
        self.brush_button = ttk.Button(
            parent, text='Retoucher ce sujet (aperçu non enregistré)',
            command=self.open_brush, state='disabled')
        self.brush_button.pack(anchor='w', pady=(0, 8))
        self.viewport = NativeImageViewport(parent, tk, ttk)
        parent.bind('<Map>', self._on_map)
        self.load(None)

    def load(self, snapshot, *, selected_subject=None, project_path=None):
        # Refresh/recovery/switch invalidates all outstanding CPU brush work.
        self._close_brush()
        self._project_path = project_path
        self.snapshot = snapshot
        self.subjects = {subject.subject_id: subject for subject in snapshot.subjects} if snapshot else {}
        self.picker.configure(values=tuple(self.subjects),
                              state='readonly' if self.subjects else 'disabled')
        self.selection.set(selected_subject if selected_subject in self.subjects
                           else next(iter(self.subjects), ''))
        self._project_label()
        self.render()

    def _project_label(self):
        self.project.set(
            f'Projet {self.snapshot.project_id} · SHA {self.snapshot.sha256[:12]}'
            if self.snapshot else 'Ouvrez un projet V1 sain depuis l’espace Projet.')

    def _on_map(self, _event):
        if self.viewport.original is None:
            self.render()

    def render(self, _event=None):
        subject = self.subjects.get(self.selection.get())
        request = brush_preview_request(
            self.snapshot, subject, getattr(self, '_project_path', None))
        key = ((request['project_path'], request['expected_sha256'],
                request['subject_id']) if request else None)
        if getattr(self, '_brush_key', None) is not None and key != self._brush_key:
            self._close_brush()
        button = getattr(self, 'brush_button', None)
        if button is not None:
            button.configure(state='normal' if request is not None
                             and self._brush_class is not None else 'disabled')
        self.viewport.load(None)
        if subject is None:
            self.details.set('Aucun sujet enregistré dans ce projet.' if self.snapshot else '')
            return
        x, y, width, height = subject.bbox_px
        info = (f'Sujet {subject.subject_id}\n'
                f'Source {subject.source_id} · Masque {subject.mask_id}\n'
                f'Zone dans la source : ({x}, {y}), {width} × {height} px\n'
                f'{PROOF_LABELS.get(subject.proof_status, "Liaison de masque non vérifiée")}. ')
        preview = subject.preview
        if preview.status != 'READY_PNG':
            reason = MASK_PREVIEW_ERRORS.get(
                preview.status, 'Aperçu indisponible pour ce masque. Réexaminez le projet (F5).')
            self.details.set(info + reason)
            return
        if not self.parent.winfo_ismapped():
            self.details.set(info)
            return
        try:
            image = self.tk.PhotoImage(data=base64.b64encode(preview.png).decode('ascii'), format='png')
            self.viewport.load(image)
        except self.tk.TclError:
            self.viewport.load(None)
            self.details.set(info + 'Impossible de décoder l’aperçu du masque.')
            return
        self.details.set(info + 'Aperçu du masque archivé.')
)
_REVISION = re.compile(r'^[0-9a-f]{64}    def __init__(self, parent, tk, ttk):
        self.tk, self.parent = tk, parent
        self.snapshot = None
        self.subjects = {}
        self.project = tk.StringVar()
        self.selection = tk.StringVar()
        self.details = tk.StringVar()
        ttk.Label(parent, text='Atelier', font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 12))
        ttk.Label(parent, textvariable=self.project, wraplength=640).pack(anchor='w')
        ttk.Label(parent, text='Sujet enregistré · inspection en lecture seule').pack(anchor='w', pady=(8, 0))
        self.picker = ttk.Combobox(parent, textvariable=self.selection, state='disabled', width=52)
        self.picker.pack(anchor='w', fill='x', pady=(3, 8))
        self.picker.bind('<<ComboboxSelected>>', self.render)
        ttk.Label(parent, textvariable=self.details, wraplength=640).pack(anchor='w', pady=(0, 8))
        self.viewport = NativeImageViewport(parent, tk, ttk)
        parent.bind('<Map>', self._on_map)
        self.load(None)

    def load(self, snapshot, *, selected_subject=None):
        self.snapshot = snapshot
        self.subjects = {subject.subject_id: subject for subject in snapshot.subjects} if snapshot else {}
        self.picker.configure(values=tuple(self.subjects),
                              state='readonly' if self.subjects else 'disabled')
        self.selection.set(selected_subject if selected_subject in self.subjects
                           else next(iter(self.subjects), ''))
        self._project_label()
        self.render()

    def _project_label(self):
        self.project.set(
            f'Projet {self.snapshot.project_id} · SHA {self.snapshot.sha256[:12]}'
            if self.snapshot else 'Ouvrez un projet V1 sain depuis l’espace Projet.')

    def _on_map(self, _event):
        if self.viewport.original is None:
            self.render()

    def render(self, _event=None):
        self.viewport.load(None)
        subject = self.subjects.get(self.selection.get())
        if subject is None:
            self.details.set('Aucun sujet enregistré dans ce projet.' if self.snapshot else '')
            return
        x, y, width, height = subject.bbox_px
        info = (f'Sujet {subject.subject_id}\n'
                f'Source {subject.source_id} · Masque {subject.mask_id}\n'
                f'Zone dans la source : ({x}, {y}), {width} × {height} px\n'
                f'{PROOF_LABELS.get(subject.proof_status, "Liaison de masque non vérifiée")}. ')
        preview = subject.preview
        if preview.status != 'READY_PNG':
            reason = MASK_PREVIEW_ERRORS.get(
                preview.status, 'Aperçu indisponible pour ce masque. Réexaminez le projet (F5).')
            self.details.set(info + reason)
            return
        if not self.parent.winfo_ismapped():
            self.details.set(info)
            return
        try:
            image = self.tk.PhotoImage(data=base64.b64encode(preview.png).decode('ascii'), format='png')
            self.viewport.load(image)
        except self.tk.TclError:
            self.viewport.load(None)
            self.details.set(info + 'Impossible de décoder l’aperçu du masque.')
            return
        self.details.set(info + 'Aperçu du masque archivé.')
)


def brush_preview_request(snapshot, subject, project_path):
    """Route only an explicitly proven and revision-pinned subject to G3.3e.

    The existing brush backend must recheck project ownership, current SHA
    and float32 proof. The PNG is a display preview, never a mask index.
    """
    if (snapshot is None or subject is None or type(project_path) is not str
            or not Path(project_path).is_absolute()
            or type(snapshot.sha256) is not str
            or not _REVISION.fullmatch(snapshot.sha256)
            or type(subject.subject_id) is not str
            or not _PROVEN_SUBJECT.fullmatch(subject.subject_id)
            or subject.proof_status != 'verified'
            or subject.preview.status != 'READY_PNG'
            or type(subject.preview.png) is not bytes):
        return None
    return {
        'project_path': project_path,
        'expected_sha256': snapshot.sha256,
        'subject_id': subject.subject_id,
        'preview_png': subject.preview.png,
    }


class NativeAtelierPanel:
    def __init__(self, parent, tk, ttk):
        self.tk, self.parent = tk, parent
        self.snapshot = None
        self.subjects = {}
        self.project = tk.StringVar()
        self.selection = tk.StringVar()
        self.details = tk.StringVar()
        ttk.Label(parent, text='Atelier', font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 12))
        ttk.Label(parent, textvariable=self.project, wraplength=640).pack(anchor='w')
        ttk.Label(parent, text='Sujet enregistré · inspection en lecture seule').pack(anchor='w', pady=(8, 0))
        self.picker = ttk.Combobox(parent, textvariable=self.selection, state='disabled', width=52)
        self.picker.pack(anchor='w', fill='x', pady=(3, 8))
        self.picker.bind('<<ComboboxSelected>>', self.render)
        ttk.Label(parent, textvariable=self.details, wraplength=640).pack(anchor='w', pady=(0, 8))
        self.viewport = NativeImageViewport(parent, tk, ttk)
        parent.bind('<Map>', self._on_map)
        self.load(None)

    def load(self, snapshot, *, selected_subject=None):
        self.snapshot = snapshot
        self.subjects = {subject.subject_id: subject for subject in snapshot.subjects} if snapshot else {}
        self.picker.configure(values=tuple(self.subjects),
                              state='readonly' if self.subjects else 'disabled')
        self.selection.set(selected_subject if selected_subject in self.subjects
                           else next(iter(self.subjects), ''))
        self._project_label()
        self.render()

    def _project_label(self):
        self.project.set(
            f'Projet {self.snapshot.project_id} · SHA {self.snapshot.sha256[:12]}'
            if self.snapshot else 'Ouvrez un projet V1 sain depuis l’espace Projet.')

    def _on_map(self, _event):
        if self.viewport.original is None:
            self.render()

    def render(self, _event=None):
        self.viewport.load(None)
        subject = self.subjects.get(self.selection.get())
        if subject is None:
            self.details.set('Aucun sujet enregistré dans ce projet.' if self.snapshot else '')
            return
        x, y, width, height = subject.bbox_px
        info = (f'Sujet {subject.subject_id}\n'
                f'Source {subject.source_id} · Masque {subject.mask_id}\n'
                f'Zone dans la source : ({x}, {y}), {width} × {height} px\n'
                f'{PROOF_LABELS.get(subject.proof_status, "Liaison de masque non vérifiée")}. ')
        preview = subject.preview
        if preview.status != 'READY_PNG':
            reason = MASK_PREVIEW_ERRORS.get(
                preview.status, 'Aperçu indisponible pour ce masque. Réexaminez le projet (F5).')
            self.details.set(info + reason)
            return
        if not self.parent.winfo_ismapped():
            self.details.set(info)
            return
        try:
            image = self.tk.PhotoImage(data=base64.b64encode(preview.png).decode('ascii'), format='png')
            self.viewport.load(image)
        except self.tk.TclError:
            self.viewport.load(None)
            self.details.set(info + 'Impossible de décoder l’aperçu du masque.')
            return
        self.details.set(info + 'Aperçu du masque archivé.')

    def open_brush(self):
        """Open a read-only comparison draft for this exact subject revision."""
        request = brush_preview_request(
            self.snapshot, self.subjects.get(self.selection.get()),
            self._project_path)
        if request is None or self._brush_class is None:
            return False
        key = (request['project_path'], request['expected_sha256'],
               request['subject_id'])
        if self._brush_dialog is not None and self._brush_key == key:
            self._brush_dialog.lift()
            return True
        self._close_brush()
        dialog = None
        panel = None
        try:
            dialog = self.tk.Toplevel(self.parent)
            dialog.title('Retouche du masque · aperçu uniquement')
            dialog.geometry('560x540')
            panel = self._brush_class(dialog, dialog, self.tk, self.ttk)
            panel.load(**request)
            if panel._identity is None:
                raise ValueError('BRUSH_IDENTITY_REFUSED')
        except (self.tk.TclError, ValueError):
            if panel is not None:
                panel.shutdown()
            if dialog is not None:
                dialog.destroy()
            self.details.set(
                'Retouche indisponible : réexaminez ce sujet (F5). '
                'Le projet reste intact.')
            return False
        self._brush_dialog, self._brush_panel, self._brush_key = dialog, panel, key
        dialog.protocol('WM_DELETE_WINDOW', self._close_brush)
        return True

    def _close_brush(self):
        panel = getattr(self, '_brush_panel', None)
        dialog = getattr(self, '_brush_dialog', None)
        self._brush_panel = self._brush_dialog = self._brush_key = None
        if panel is not None:
            panel.shutdown()
        if dialog is not None:
            try:
                dialog.destroy()
            except self.tk.TclError:
                pass  # The parent root has already been destroyed.

    def shutdown(self):
        self._close_brush()
