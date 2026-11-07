"""Atelier workspace for inspecting the subjects persisted in a V1 project."""
from __future__ import annotations

import base64
from dataclasses import replace


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
        self.photo = None
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
        self.image = ttk.Label(parent)
        self.image.pack(anchor='w')
        parent.bind('<Map>', self.render)
        self.load(None)

    def load(self, snapshot):
        self.snapshot = snapshot
        self.subjects = {subject.subject_id: subject for subject in snapshot.subjects} if snapshot else {}
        self.picker.configure(values=tuple(self.subjects),
                              state='readonly' if self.subjects else 'disabled')
        self.selection.set(next(iter(self.subjects), ''))
        self._project_label()
        self.render()

    def notes_saved(self, previous, current):
        # The existing writer verified the new revision and changed only notes.
        if (self.snapshot is not None and self.snapshot.project_id == previous.project_id
                and self.snapshot.sha256 == previous.sha256):
            self.snapshot = replace(self.snapshot, sha256=current.sha256)
            self._project_label()

    def _project_label(self):
        self.project.set(
            f'Projet {self.snapshot.project_id} · SHA {self.snapshot.sha256[:12]}'
            if self.snapshot else 'Ouvrez un projet V1 sain depuis l’espace Projet.')

    def render(self, _event=None):
        self.image.configure(image='')
        self.photo = None
        subject = self.subjects.get(self.selection.get())
        if subject is None:
            self.details.set('Aucun sujet enregistré dans ce projet.' if self.snapshot else '')
            return
        x, y, width, height = subject.bbox_px
        info = (f'Source {subject.source_id} · Masque {subject.mask_id}\n'
                f'Zone dans la source : ({x}, {y}), {width} × {height} px\n'
                f'{PROOF_LABELS[subject.proof_status]}. ')
        preview = subject.preview
        if preview.status != 'READY_PNG':
            self.details.set(info + 'Aperçu indisponible pour ce masque.')
            return
        if not self.parent.winfo_ismapped():
            self.details.set(info)
            return
        try:
            image = self.tk.PhotoImage(data=base64.b64encode(preview.png).decode('ascii'), format='png')
            self.photo = image.subsample(preview.subsample) if preview.subsample > 1 else image
            self.image.configure(image=self.photo)
        except self.tk.TclError:
            self.details.set(info + 'Impossible de décoder l’aperçu du masque.')
            return
        self.details.set(info + f'Aperçu du masque archivé · réduction ×{preview.subsample}.')
