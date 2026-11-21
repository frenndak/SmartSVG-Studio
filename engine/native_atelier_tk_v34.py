"""Atelier workspace for inspecting the subjects persisted in a V1 project."""
from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
from uuid import uuid4

from native_image_viewport_v34 import NativeImageViewport
from smartsvg_core.native_brush_history_v34 import inspect_native_brush_history
from smartsvg_core.native_brush_history_command_v34 import change_native_brush_history
from smartsvg_core.native_write_jobs_v35 import tracked_native_write
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
                 history_fn=inspect_native_brush_history,
                 history_change_fn=change_native_brush_history,
                 confirm_history_fn=None, can_history=None,
                 on_create_first_subject=None):
        self.tk, self.ttk, self.parent = tk, ttk, parent
        self._on_saved = on_saved
        self._on_create_first_subject = on_create_first_subject
        self._history_fn = history_fn
        self._history_change_fn = history_change_fn
        self._confirm_history_fn = confirm_history_fn
        self._can_history = can_history
        self._history_status = self._history_future = self._history_pending = None
        self._history_confirming = self._history_needs_review = self._closed = False
        self._history_generation = 0
        # One outstanding confirmed command, using the existing writer only.
        # Unlike read-only previews, a running mutation is never cancelled as stale.
        self._history_worker = None
        self.snapshot = None
        self.subjects = {}
        self._project_path = None
        self._brush_dialog = self._brush_panel = self._brush_key = None
        self._brush_close_confirming = False
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
        self.first_subject_status = tk.StringVar(value='')
        ttk.Label(parent, text='Atelier', font=('Segoe UI', 16, 'bold')).pack(anchor='w', pady=(0, 12))
        ttk.Label(parent, textvariable=self.project, wraplength=640).pack(anchor='w')
        ttk.Label(parent, textvariable=self.history, wraplength=640).pack(anchor='w', pady=(4, 0))
        history_actions = ttk.Frame(parent)
        history_actions.pack(fill='x', pady=(4, 4))
        self.undo_button = ttk.Button(history_actions, text='Annuler la retouche',
                                      command=self.undo_brush, state='disabled')
        self.undo_button.pack(side='left', padx=(0, 6))
        self.redo_button = ttk.Button(history_actions, text='Rétablir la retouche',
                                      command=self.redo_brush, state='disabled')
        self.redo_button.pack(side='left')
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
        self.picker.bind('<<ComboboxSelected>>', self._pick_subject)
        # Scoped to the subject picker: do not steal shortcuts from brush editing.
        self.picker.bind('<Alt-Left>', self._previous_subject_key)
        self.picker.bind('<Alt-Right>', self._next_subject_key)
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
        self.first_subject_button = ttk.Button(
            parent, text='Créer le premier sujet (PNG transparent)…',
            command=self.create_first_subject, state='disabled')
        self.first_subject_button.pack(anchor='w', pady=(0, 4))
        ttk.Label(parent, textvariable=self.first_subject_status,
                  wraplength=640).pack(anchor='w', pady=(0, 8))
        self.viewport = NativeImageViewport(parent, tk, ttk)
        parent.bind('<Map>', self._on_map)
        self.load(None)

    def load(self, snapshot, *, selected_subject=None, project_path=None,
             require_history_review=False):
        if self._closed:
            return
        self._history_generation += 1
        # A previous project's creation feedback must not follow another file.
        self.first_subject_status.set('')
        # A committed command remains write-blocked while its host asynchronously
        # verifies the receipt. Only a correlated snapshot may clear that latch.
        self._history_needs_review = require_history_review is True
        # Refresh/recovery/switch invalidates all outstanding CPU brush work.
        self._close_brush()
        self._project_path = project_path
        self.snapshot = snapshot
        self.subjects, invalid_catalog = _admit_subject_catalog(snapshot)
        self._first_subject_catalog_invalid = invalid_catalog
        self.picker.configure(values=tuple(self.subjects),
                              state='readonly' if self.subjects else 'disabled')
        self.selection.set(selected_subject if selected_subject in self.subjects
                           else next(iter(self.subjects), ''))
        self._project_label()
        self._refresh_history(invalid_catalog=invalid_catalog)
        self._update_first_subject_button(invalid_catalog=invalid_catalog)
        self.render()
        if invalid_catalog:
            self.details.set('Liste des sujets invalide. Réexaminez le projet (F5). '
                             'Aucune retouche disponible ; archive inchangée.')

    def _update_first_subject_button(self, *, invalid_catalog=False):
        snapshot = self.snapshot
        revision = getattr(snapshot, 'sha256', None)
        available = (self._on_create_first_subject is not None and
                     not getattr(self, '_first_subject_catalog_invalid', False) and
                     snapshot is not None and not invalid_catalog and
                     not self.subjects and not self.busy and
                     not self.history_requires_review and
                     not self.has_open_brush and
                     type(revision) is str and _REVISION.fullmatch(revision) and
                     type(self._project_path) is str and
                     Path(self._project_path).is_absolute())
        self.first_subject_button.configure(
            state='normal' if available else 'disabled')
        return bool(available)

    def create_first_subject(self):
        if not self._update_first_subject_button():
            return False
        return self._on_create_first_subject(self.snapshot, self._project_path) is True

    def _refresh_history(self, *, invalid_catalog=False):
        """Present the existing V1 journal status without offering a fake action.

        Called only on project load/F5, not on canvas events or subject
        navigation. A stale project or malformed history stays unavailable.
        """
        self._history_status = None
        self._update_history_controls()
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
                status.get('cricut_certified') is not False or
                any(type(status.get(action + '_subject_id')) is not str
                    or not _PROVEN_SUBJECT.fullmatch(status[action + '_subject_id'])
                    for action in ('undo', 'redo')
                    if status[action + '_available'])):
            self.history.set(unavailable)
            return
        undo = 'oui' if status['undo_available'] else 'non'
        redo = 'oui' if status['redo_available'] else 'non'
        self._history_status = {key: status[key] for key in (
            'project_sha256', 'undo_available', 'redo_available',
            'undo_subject_id', 'redo_subject_id') if key in status}
        self.history.set(
            'Historique du pinceau · Annulation possible : '
            + undo + ' · Rétablissement possible : ' + redo
            + ' · Choisissez le sujet concerné ; fermez sa fenêtre de retouche.')
        self._update_history_controls()

    @property
    def busy(self):
        return (getattr(self, '_history_confirming', False) or
                getattr(self, '_history_future', None) is not None)

    @property
    def history_requires_review(self):
        return getattr(self, '_history_needs_review', False)

    @property
    def has_open_brush(self):
        """Even an empty panel could receive a gesture during a notes write."""
        return (getattr(self, '_brush_panel', None) is not None or
                getattr(self, '_brush_dialog', None) is not None)

    def _history_request(self, action):
        if (action not in ('undo', 'redo') or getattr(self, '_closed', False)
                or self.history_requires_review or self.busy
                or getattr(self, '_brush_dialog', None) is not None
                or not callable(getattr(self, '_on_saved', None))):
            return None
        status = getattr(self, '_history_status', None)
        selection = getattr(self, 'selection', None)
        sid = selection.get() if selection is not None else None
        subject = getattr(self, 'subjects', {}).get(sid)
        revision = getattr(self.snapshot, 'sha256', None)
        path = self._project_path
        if (type(status) is not dict or type(path) is not str
                or not Path(path).is_absolute() or type(revision) is not str
                or not _REVISION.fullmatch(revision)
                or status.get('project_sha256') != revision
                or status.get(action + '_available') is not True
                or type(sid) is not str or not _PROVEN_SUBJECT.fullmatch(sid)
                or status.get(action + '_subject_id') != sid
                or getattr(subject, 'subject_id', None) != sid
                or getattr(subject, 'proof_status', None) != 'verified'):
            return None
        return dict(project_path=path, expected_sha256=revision,
                    subject_id=sid, action=action)

    def _history_allowed(self):
        guard = getattr(self, '_can_history', None)
        try:
            return guard is None or guard() is True
        except Exception:
            return False

    def _update_history_controls(self):
        if getattr(self, '_closed', False):
            return
        for action in ('undo', 'redo'):
            button = getattr(self, action + '_button', None)
            if button is not None:
                button.configure(state='normal' if self._history_request(action)
                                 and self._history_allowed() else 'disabled')
        button = getattr(self, 'brush_button', None)
        if button is not None:
            selection = getattr(self, 'selection', None)
            subject = getattr(self, 'subjects', {}).get(
                selection.get() if selection is not None else None)
            request = brush_preview_request(self.snapshot, subject, self._project_path)
            button.configure(state='normal' if not self.busy
                             and not self.history_requires_review
                             and request is not None
                             and getattr(self, '_brush_class', None) is not None
                             else 'disabled')

    def undo_brush(self):
        return self._change_history('undo')

    def redo_brush(self):
        return self._change_history('redo')

    def _change_history(self, action):
        request = self._history_request(action)
        if request is None or not self._history_allowed():
            return False
        generation = self._history_generation
        confirm = self._confirm_history_fn
        if confirm is None:
            from tkinter import messagebox
            confirm = lambda operation, _sid: messagebox.askyesno(
                'Annuler la retouche' if operation == 'undo' else 'Rétablir la retouche',
                'Modifier le masque du sujet sélectionné dans ce projet ? '
                'Les fichiers déjà exportés seront conservés.',
                parent=self.parent, default='no')
        self._history_confirming = True
        self._update_history_controls()
        try:
            accepted = confirm(action, request['subject_id']) is True
        except Exception:
            accepted = False
        finally:
            self._history_confirming = False
        if self._closed:
            return False
        # Modal callbacks may switch selection, reload even the same revision,
        # start another writer or destroy this panel. Recheck before submit.
        if (not accepted or self._history_generation != generation
                or self._history_request(action) != request
                or not self._history_allowed()):
            self._update_history_controls()
            return False
        command = dict(request, command_id='native-history-' + uuid4().hex,
                       confirmed=True)
        try:
            if self._history_worker is None:
                self._history_worker = ThreadPoolExecutor(
                    max_workers=1, thread_name_prefix='smartsvg-history')
            with tracked_native_write(self._history_worker, self._history_change_fn,
                                      **command) as future:
                self._history_future = future
                self._history_pending = (generation, request, command['command_id'])
                self.parent.after(50, self._receive_history)
        except Exception:
            self._history_future = self._history_pending = None
            worker, self._history_worker = self._history_worker, None
            if worker is not None:
                worker.shutdown(wait=False, cancel_futures=True)
            self.history.set('Commande indisponible. Réexaminez le projet (F5).')
            self._update_history_controls()
            return False
        self.history.set('Modification du pinceau en cours…')
        self._update_history_controls()
        self._update_navigation()
        return True

    def _receive_history(self):
        if self._closed or self._history_future is None:
            return
        if not self._history_future.done():
            self.parent.after(50, self._receive_history)
            return
        future, self._history_future = self._history_future, None
        pending, self._history_pending = self._history_pending, None
        generation, request, command_id = pending
        # Completion belongs to its captured context, never a new project.
        current = (self._history_generation == generation
                   and self._project_path == request['project_path']
                   and getattr(self.snapshot, 'sha256', None) == request['expected_sha256']
                   and self.selection.get() == request['subject_id'])
        if not current:
            if (self._project_path == request['project_path']
                    and getattr(self.snapshot, 'sha256', None) == request['expected_sha256']):
                self._history_status = None
                self._history_needs_review = True
                self.history.set('Révision modifiée pendant la commande. '
                                 'Réexaminez le projet (F5).')
            self._update_history_controls()
            self._update_navigation()
            return
        self._history_status = None
        self._history_needs_review = True
        viewport = getattr(self, 'viewport', None)
        if viewport is not None:
            viewport.load(None)
        self._update_history_controls()
        try:
            receipt = future.result()
            if (type(receipt) is not dict or receipt.get('persisted') is not True
                    or receipt.get('cricut_certified') is not False
                    or receipt.get('action') != request['action']
                    or receipt.get('subject_id') != request['subject_id']
                    or receipt.get('command_id') != command_id
                    or receipt.get('status') not in ('brush_history_' + request['action'],
                                                    'brush_history_already_applied')
                    or type(receipt.get('project_sha256')) is not str
                    or not _REVISION.fullmatch(receipt['project_sha256'])
                    or receipt['project_sha256'] == request['expected_sha256']):
                raise ValueError('UNCERTAIN_HISTORY_RECEIPT')
        except Exception:
            self.history.set('Modification non confirmée. Réexaminez le projet (F5) '
                             'avant une nouvelle écriture ; notes locales conservées.')
            return
        self.history.set('Modification enregistrée ; actualisation du projet…')
        try:
            # Same verified host reinspection/rebase path as a brush save.
            self._on_saved(receipt)
        except Exception:
            if not self._closed and self._history_generation == generation:
                self.history.set('Modification enregistrée ; actualisation indisponible. '
                                 'Réexaminez le projet (F5).')

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
            state='normal' if index > 0 and not self.busy else 'disabled')
        self.next_button.configure(
            state='normal' if 0 <= index < len(keys) - 1 and not self.busy else 'disabled')
        picker = getattr(self, 'picker', None)
        if picker is not None:
            picker.configure(state='readonly' if keys and not self.busy else 'disabled')

    def _step_subject(self, offset):
        if self.busy:
            return False
        keys = tuple(self.subjects)
        selected = self.selection.get()
        if selected not in self.subjects:
            return False
        index = keys.index(selected) + offset
        if not 0 <= index < len(keys):
            return False
        return self._select_subject(keys[index])

    def _pick_subject(self, _event=None):
        return self._select_subject(self.selection.get())

    def _select_subject(self, subject_id):
        # A queued Tk event must not navigate while a background operation
        # has disabled the picker; preserve the current draft and selection.
        if getattr(self, 'busy', False):
            brush_key = getattr(self, '_brush_key', None)
            if brush_key is not None and brush_key[2] in self.subjects:
                self.selection.set(brush_key[2])
            return False
        brush_key = getattr(self, '_brush_key', None)
        # A stale/foreign combobox value is never a valid selection. Keep an
        # open draft on its original subject without prompting to discard it.
        if subject_id not in self.subjects:
            if brush_key is not None and brush_key[2] in self.subjects:
                self.selection.set(brush_key[2])
            return False
        if brush_key is not None and subject_id != brush_key[2]:
            # The picker updates its variable before dispatching the event.
            # Restore the active target before the modal confirmation.
            self.selection.set(brush_key[2])
            if not self._request_close_brush():
                return False
        self.selection.set(subject_id)
        self.render()
        return True

    def _previous_subject_key(self, _event=None):
        self.previous_subject()
        return 'break'

    def _next_subject_key(self, _event=None):
        self.next_subject()
        return 'break'

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
        self._update_history_controls()
        if self.history_requires_review:
            self.viewport.load(None)
            self.details.set('Révision à vérifier : réexaminez le projet (F5).')
            return
        subject = self.subjects.get(self.selection.get())
        request = brush_preview_request(
            self.snapshot, subject, getattr(self, '_project_path', None))
        key = ((request['project_path'], request['expected_sha256'],
                request['subject_id']) if request else None)
        if getattr(self, '_brush_key', None) is not None and key != self._brush_key:
            self._close_brush()
        button = getattr(self, 'brush_button', None)
        if button is not None:
            button.configure(state='normal' if not self.busy and request is not None
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
        info = (f'Sujet {subject.subject_id}\n'
                f'Source {subject.source_id} · Masque {subject.mask_id}\n'
                f'Zone dans la source : ({x}, {y}), {width} × {height} px\n'
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
        if self._closed or self.busy or self.history_requires_review:
            return False
        if not self._history_allowed():
            self.details.set('Terminez l’écriture du projet avant d’ouvrir une retouche.')
            return False
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
        if not self._request_close_brush():
            return False
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
        self._update_history_controls()
        dialog.protocol('WM_DELETE_WINDOW', self._request_close_brush)
        return True

    def can_leave_brush(self):
        """Ask before discarding work, without closing the active panel."""
        if getattr(self, '_brush_close_confirming', False):
            return False
        panel = getattr(self, '_brush_panel', None)
        if panel is None or not panel.has_draft:
            return True
        from tkinter import messagebox

        try:
            checkpoint = panel.draft_checkpoint()
        except Exception:
            # Without a snapshot the confirmation cannot be tied to the work
            # that will be discarded, so keep the panel open.
            return False
        dialog = self._brush_dialog
        self._brush_close_confirming = True
        try:
            confirmed = messagebox.askyesno(
                'Retouche non enregistrée',
                'Abandonner le brouillon du sujet actif ?',
                detail='Choisissez Non pour revenir à la retouche.',
                parent=dialog, default='no')
            if self._brush_panel is not panel:
                return False
            if confirmed is True and checkpoint != panel.draft_checkpoint():
                panel.status.set(
                    'Brouillon modifié pendant la confirmation : rien n’a été effacé.')
                dialog.lift()
                return False
            if not confirmed:
                dialog.lift()
            return confirmed is True
        except Exception:
            return False
        finally:
            self._brush_close_confirming = False

    def _request_close_brush(self):
        if not self.can_leave_brush():
            return False
        self._close_brush()
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
        self._update_history_controls()

    def shutdown(self):
        if self._closed:
            return
        self._closed = True
        self._history_generation += 1
        self._close_brush()
        # A confirmed writer must finish, but closing Tk must not wait for disk I/O.
        # cancel_futures only cancels work that has not started; running work
        # keeps its own request and cannot update a closed panel.
        if self._history_worker is not None:
            self._history_worker.shutdown(wait=False, cancel_futures=True)
