"""Atelier workspace for inspecting the subjects persisted in a V1 project."""
from __future__ import annotations

import base64
from pathlib import Path
import re

from native_image_viewport_v34 import NativeImageViewport
from smartsvg_core.native_brush_history_v34 import inspect_native_brush_history
from smartsvg_core.source_preview_v34 import MAX_ENCODED_BYTES


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

_PROVEN_SUBJECT = re.compile(r'^subject-[0-9a-f]{32}$')
_REVISION = re.compile(r'^[0-9a-f]{64}$')
# Match the read-only Tk brush allocation ceiling; backend checks PNG again.
BRUSH_PREVIEW_MAX_AXIS = 2048


def brush_preview_request(snapshot, subject, project_path):
    """Route only an explicitly proven and revision-pinned subject to G3.3e.

    The existing brush backend must recheck project ownership, current SHA
    and float32 proof. The PNG is a display preview, never a mask index.
    """
    if (snapshot is None or subject is None or type(project_path) is not str
            or not Path(project_path).is_absolute()
            or type(getattr(snapshot, 'sha256', None)) is not str
            or not _REVISION.fullmatch(snapshot.sha256)
            or type(getattr(subject, 'subject_id', None)) is not str
            or not _PROVEN_SUBJECT.fullmatch(subject.subject_id)
            or getattr(subject, 'proof_status', None) != 'verified'
            or getattr(subject, 'preview', None) is None
            or getattr(subject.preview, 'status', None) != 'READY_PNG'
            or type(getattr(subject.preview, 'png', None)) is not bytes
            or not 33 <= len(subject.preview.png) <= MAX_ENCODED_BYTES
            or type(getattr(subject.preview, 'width_px', None)) is not int
            or type(getattr(subject.preview, 'height_px', None)) is not int
            or not 0 < subject.preview.width_px <= BRUSH_PREVIEW_MAX_AXIS
            or not 0 < subject.preview.height_px <= BRUSH_PREVIEW_MAX_AXIS):
        return None
    return {
        'project_path': project_path,
        'expected_sha256': snapshot.sha256,
        'subject_id': subject.subject_id,
        'preview_png': subject.preview.png,
    }


def _admit_subject_catalog(snapshot):
    """Fail closed on incomplete V1 inspection records, before Tk consumes IDs.

    Only the historical inspector's ordered tuple is admitted. A duplicate
    persistent Subject ID must never silently select/overwrite another mask.
    This helper does not inspect, decode or mutate any archive resource.
    """
    if snapshot is None:
        return {}, False
    project_id = getattr(snapshot, 'project_id', None)
    revision = getattr(snapshot, 'sha256', None)
    entries = getattr(snapshot, 'subjects', None)
    if (type(project_id) is not str or not project_id
            or type(revision) is not str or not _REVISION.fullmatch(revision)
            or type(entries) is not tuple):
        return {}, True
    catalog = {}
    for subject in entries:
        sid = getattr(subject, 'subject_id', None)
        # Historical V1 IDs are valid for read-only inspection even when
        # they do not match today's proven float32 Subject ID syntax. The
        # stricter _PROVEN_SUBJECT guard applies only to brush admission.
        if (type(sid) is not str or not sid or sid in catalog):
            return {}, True
        catalog[sid] = subject
    return catalog, False


class NativeAtelierPanel:
    def __init__(self, parent, tk, ttk, *, on_saved=None,
                 history_fn=inspect_native_brush_history):
        self.tk, self.ttk, self.parent = tk, ttk, parent
        self._on_saved = on_saved
        self._history_fn = history_fn
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
        self.history = tk.StringVar()
        ttk.Label(parent, text='Atelier', font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 12))
        ttk.Label(parent, textvariable=self.project, wraplength=640).pack(anchor='w')
        ttk.Label(parent, textvariable=self.history, wraplength=640).pack(anchor='w', pady=(4, 0))
        ttk.Label(parent, text='Sujet enregistré · inspection en lecture seule').pack(anchor='w', pady=(8, 0))
        # In the same row to preserve canvas height on smaller Windows panes.
        navigation = ttk.Frame(parent)
        navigation.pack(fill='x', pady=(3, 8))
        self.previous_button = ttk.Button(
            navigation, text='◀ Préc.', width=9,
            command=self.previous_subject, state='disabled')
        self.previous_button.pack(side='left', padx=(0, 4))
        self.picker = ttk.Combobox(
            navigation, textvariable=self.selection, state='disabled', width=38)
        self.picker.pack(side='left', fill='x', expand=True)
        self.picker.bind('<<ComboboxSelected>>', self.render)
        self.next_button = ttk.Button(
            navigation, text='Suiv. ▶', width=9,
            command=self.next_subject, state='disabled')
        self.next_button.pack(side='left', padx=(4, 0))
        self.subject_position = tk.StringVar(value='')
        ttk.Label(parent, textvariable=self.subject_position).pack(anchor='w')
        ttk.Label(parent, textvariable=self.details, wraplength=640).pack(anchor='w', pady=(0, 8))
        self.brush_button = ttk.Button(
            parent, text='Retoucher ce sujet (aperçu puis sauvegarde)',
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
        self.subjects, invalid_catalog = _admit_subject_catalog(snapshot)
        self.picker.configure(values=tuple(self.subjects),
                              state='readonly' if self.subjects else 'disabled')
        self.selection.set(selected_subject if selected_subject in self.subjects
                           else next(iter(self.subjects), ''))
        self._project_label()
        self._refresh_history(invalid_catalog=invalid_catalog)
        self.render()
        if invalid_catalog:
            self.details.set('Liste des sujets invalide. Réexaminez le projet (F5). '
                             'Aucune retouche disponible ; archive inchangée.')

    def _refresh_history(self, *, invalid_catalog=False):
        """Present the existing V1 journal status without offering a fake action.

        Called only on project load/F5, not on canvas events or subject
        navigation. A stale project or malformed history stays unavailable.
        """
        snapshot = self.snapshot
        revision = getattr(snapshot, 'sha256', None)
        path = self._project_path
        unavailable = ('Historique du pinceau indisponible. '
                       'Réexaminez le projet (F5).')
        if (invalid_catalog or type(path) is not str
                or not Path(path).is_absolute() or type(revision) is not str
                or not _REVISION.fullmatch(revision)):
            self.history.set(unavailable)
            return
        try:
            status = self._history_fn(project_path=path,
                                      expected_sha256=revision)
        except Exception:
            # Never expose an OS path, exception, private stroke or mask data.
            self.history.set(unavailable)
            return
        if (type(status) is not dict or
                status.get('project_sha256') != revision or
                status.get('schema') != 'smartsvg-native-brush-history-status/1' or
                type(status.get('undo_available')) is not bool or
                type(status.get('redo_available')) is not bool or
                status.get('persisted') is not False or
                status.get('cricut_certified') is not False):
            self.history.set(unavailable)
            return
        undo = 'oui' if status['undo_available'] else 'non'
        redo = 'oui' if status['redo_available'] else 'non'
        self.history.set(
            'Journal V1 (lecture seule) · Annulation possible : '
            + undo + ' · Rétablissement possible : ' + redo
            + ' · Commandes non encore raccordées.')

    def _update_navigation(self):
        # Choose the canonical order already returned by the V1 inspector.
        # An unknown selection is not silently mapped to a different subject.
        keys = tuple(self.subjects)
        selected = self.selection.get()
        index = keys.index(selected) if selected in self.subjects else -1
        self.subject_position.set(
            f'Sujet {index + 1} sur {len(keys)} · sélectionner pour inspecter'
            if index >= 0 else ('Aucun sujet sélectionné' if keys else ''))
        self.previous_button.configure(
            state='normal' if index > 0 else 'disabled')
        self.next_button.configure(
            state='normal' if 0 <= index < len(keys) - 1 else 'disabled')

    def _step_subject(self, offset):
        keys = tuple(self.subjects)
        selected = self.selection.get()
        if selected not in self.subjects:
            return False
        index = keys.index(selected) + offset
        if not 0 <= index < len(keys):
            return False
        self.selection.set(keys[index])
        # Same render path as the combobox: closes any stale brush preview.
        self.render()
        return True

    def previous_subject(self):
        return self._step_subject(-1)

    def next_subject(self):
        return self._step_subject(1)

    def _project_label(self):
        # A partial inspector snapshot must not crash the Tk refresh callback.
        snapshot = self.snapshot
        project_id = getattr(snapshot, 'project_id', None)
        revision = getattr(snapshot, 'sha256', None)
        if (type(project_id) is not str or not project_id
                or type(revision) is not str or not _REVISION.fullmatch(revision)):
            self.project.set('Projet indisponible. Réexaminez le projet (F5).'
                             if snapshot is not None else
                             'Ouvrez un projet V1 sain depuis l’espace Projet.')
            return
        self.project.set(f'Projet {project_id} · SHA {revision[:12]}')

    def _on_map(self, _event):
        if self.viewport.original is None:
            self.render()

    def render(self, _event=None):
        self._update_navigation()
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
        # Refuse malformed V1 inspector records before touching Tk images.
        bbox = getattr(subject, 'bbox_px', None)
        preview = getattr(subject, 'preview', None)
        if (type(getattr(subject, 'subject_id', None)) is not str
                or type(getattr(subject, 'source_id', None)) is not str
                or type(getattr(subject, 'mask_id', None)) is not str
                or not isinstance(bbox, (tuple, list)) or len(bbox) != 4
                or any(type(v) is not int or v < 0 for v in bbox)
                or bbox[2] == 0 or bbox[3] == 0
                or preview is None or type(getattr(preview, 'status', None)) is not str):
            self.details.set('Métadonnées du sujet incomplètes. Réexaminez le projet (F5).')
            return
        x, y, width, height = bbox
        info = (f'Sujet {subject.subject_id}\\n'
                f'Source {subject.source_id} · Masque {subject.mask_id}\\n'
                f'Zone dans la source : ({x}, {y}), {width} × {height} px\\n'
                f'{PROOF_LABELS.get(getattr(subject, "proof_status", None), "Liaison de masque non vérifiée")}. ')
        if preview.status != 'READY_PNG':
            reason = MASK_PREVIEW_ERRORS.get(
                preview.status, 'Aperçu indisponible pour ce masque. Réexaminez le projet (F5).')
            self.details.set(info + reason)
            return
        if (type(getattr(preview, 'png', None)) is not bytes
                or not 33 <= len(preview.png) <= MAX_ENCODED_BYTES
                or type(getattr(preview, 'width_px', None)) is not int
                or type(getattr(preview, 'height_px', None)) is not int
                or preview.width_px <= 0 or preview.height_px <= 0):
            self.details.set(info + 'Aperçu invalide. Réexaminez le projet (F5).')
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
        if (getattr(subject, 'proof_status', None) == 'verified' and
                (preview.width_px > BRUSH_PREVIEW_MAX_AXIS or
                 preview.height_px > BRUSH_PREVIEW_MAX_AXIS)):
            self.details.set(
                info + 'Masque inspectable mais trop grand pour la retouche native '
                '(limite : 2 048 px par axe). Aucune modification.')
        elif (self._brush_class is None and
              getattr(subject, 'proof_status', None) == 'verified'):
            self.details.set(
                info + 'Aperçu du masque archivé. '
                'Le pinceau natif sera disponible après son intégration.')
        else:
            self.details.set(info + 'Aperçu du masque archivé.')

    def _brush_saved(self, key, receipt):
        """Forward a real receipt only for the still-active native selection."""
        if (self._on_saved is None or self._brush_key != key or
                self._project_path != key[0] or self.snapshot is None or
                getattr(self.snapshot, 'sha256', None) != key[1] or
                not isinstance(receipt, dict) or
                receipt.get('subject_id') != key[2] or
                receipt.get('persisted') is not True or
                type(receipt.get('project_sha256')) is not str or
                not _REVISION.fullmatch(receipt['project_sha256'])):
            return
        self._on_saved(receipt)

    def open_brush(self):
        """Open a verified V1 Subject draft with an explicit save path."""
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
            dialog.title('Retouche du masque · avant/après et sauvegarde')
            dialog.geometry('560x540')
            panel = self._brush_class(
                dialog, dialog, self.tk, self.ttk,
                on_saved=lambda receipt: self._brush_saved(key, receipt))
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
