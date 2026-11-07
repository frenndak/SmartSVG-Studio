"""Atelier workspace for inspecting the subjects persisted in a V1 project."""
from __future__ import annotations

import base64

from native_image_viewport_v34 import NativeImageViewport


PROOF_LABELS = {
    'verified': 'Liaison float32 vérifiée',
    'legacy_subject_record': 'Liaison float32 historique',
    'unverified': 'Identité float32 non vérifiée pour ce sujet',
    'png_only': 'Masque PNG archivé',
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
                f'{PROOF_LABELS[subject.proof_status]}. ')
        preview = subject.preview
        if preview.status != 'READY_PNG':
            reason = ('Limite de taille des aperçus atteinte.'
                      if preview.status == 'SOURCE_TOO_LARGE' else 'Aperçu indisponible pour ce masque.')
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
