"""V34-128 preview subset: native card/tray drafts using existing geometry.

Widget APIs are supplied by the desktop after its lazy Tk import. No files,
projects, exports, networks, model calls or machine operations are performed.
"""
from __future__ import annotations

from smartsvg_core.template_geometry_v34 import folded_card, open_tray
from smartsvg_core.template_preflight_v34 import preflight_template


class TemplatePreviewContent:
    """Read-only parameter form and nominal CUT/SCORE canvas."""

    def __init__(self, parent, tk, ttk):
        self.proposal = None
        self.kind = tk.StringVar(value='Boîte ouverte')
        self.width = tk.StringVar(value='80')
        self.depth = tk.StringVar(value='50')
        self.wall = tk.StringVar(value='30')
        self.tab = tk.StringVar(value='10')
        self.sheet_width = tk.StringVar(value='')
        self.sheet_height = tk.StringVar(value='')
        self.status = tk.StringVar(value='')
        self.preflight_status = tk.StringVar(value='')
        frame = ttk.Frame(parent, padding=16)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text='Fabrique · aperçu de gabarit',
                  font=('Segoe UI', 15, 'bold')).pack(anchor='w')
        ttk.Label(frame, text='Brouillon géométrique en millimètres, sans export ni modification du projet.',
                  wraplength=620).pack(anchor='w', pady=(5, 10))
        row = ttk.Frame(frame)
        row.pack(fill='x', pady=4)
        ttk.Label(row, text='Modèle', width=35).pack(side='left')
        ttk.Combobox(row, textvariable=self.kind, state='readonly',
                     values=('Boîte ouverte', 'Carte pliée'), width=20).pack(side='left')
        fields = ttk.Frame(frame)
        fields.pack(fill='x')
        fields.columnconfigure(0, weight=1)
        fields.columnconfigure(1, weight=1)
        self.width_label, self.width_entry = self._field(ttk, fields, self.width, 0, 0)
        self.depth_label, self.depth_entry = self._field(ttk, fields, self.depth, 0, 1)
        self.wall_label, self.wall_entry = self._field(ttk, fields, self.wall, 1, 0)
        self.tab_label, self.tab_entry = self._field(ttk, fields, self.tab, 1, 1)
        self.wall_label.configure(text='Hauteur des parois (mm)')
        self.tab_label.configure(text='Largeur des languettes (mm)')
        ttk.Label(frame, text=(
            'Zone utile déclarée (facultatif) : dimensions disponibles en mm. '
            'Ce contrôle ne qualifie pas une machine.'
        ), wraplength=620).pack(anchor='w', pady=(7, 2))
        self.sheet_width_label, self.sheet_width_entry = self._field(
            ttk, fields, self.sheet_width, 2, 0)
        self.sheet_height_label, self.sheet_height_entry = self._field(
            ttk, fields, self.sheet_height, 2, 1)
        self.sheet_width_label.configure(text='Largeur disponible (mm)')
        self.sheet_height_label.configure(text='Hauteur disponible (mm)')
        actions = ttk.Frame(frame)
        actions.pack(fill='x', pady=9)
        ttk.Button(actions, text='Calculer l’aperçu', command=self.calculate).pack(side='left')
        ttk.Button(actions, text='Lancer le prévol', command=self.run_preflight).pack(side='left', padx=10)
        ttk.Label(frame, textvariable=self.status, wraplength=620).pack(anchor='w', pady=5)
        ttk.Label(frame, textvariable=self.preflight_status, wraplength=620).pack(anchor='w', pady=5)
        ttk.Label(frame, text='CUT : trait plein sombre · SCORE : pointillés bleus',
                  wraplength=620).pack(anchor='w', pady=4)
        ttk.Label(frame, text=(
            'Dimensions théoriques, aperçu réduit. Aucun fichier créé. '
            'Dans Design Space, SCORE et Attacher doivent être affectés manuellement. '
            'Machine, outil et matière non qualifiés.'), wraplength=620).pack(anchor='w', pady=5)
        self.canvas = tk.Canvas(frame, width=720, height=320, background='#FFFFFF',
                                highlightthickness=1, highlightbackground='#A0AAA5')
        self.canvas.pack(fill='both', expand=True, pady=6)
        self.canvas.bind('<Configure>', self._redraw)
        for variable in (self.width, self.depth, self.wall, self.tab):
            variable.trace_add('write', self.invalidate)
        for variable in (self.sheet_width, self.sheet_height):
            variable.trace_add('write', self.invalidate_preflight)
        self.kind.trace_add('write', self._mode_changed)
        self._mode_changed()
        self.calculate()

    @staticmethod
    def _field(ttk, parent, variable, row_index, column):
        row = ttk.Frame(parent)
        row.grid(row=row_index, column=column, sticky='ew', padx=(0, 10), pady=3)
        label = ttk.Label(row, wraplength=280)
        label.pack(anchor='w')
        entry = ttk.Entry(row, textvariable=variable, width=20)
        entry.pack(anchor='w')
        return label, entry

    def _mode_changed(self, *_unused):
        card = self.kind.get() == 'Carte pliée'
        self.width_label.configure(text='Largeur de la carte pliée (mm)' if card else 'Largeur du fond (mm)')
        self.depth_label.configure(text='Hauteur de la carte (mm)' if card else 'Profondeur du fond (mm)')
        state = 'disabled' if card else 'normal'
        self.wall_entry.configure(state=state)
        self.tab_entry.configure(state=state)
        self.invalidate()

    def invalidate(self, *_unused):
        self.proposal = None
        self.canvas.delete('all')
        self.status.set('Paramètres modifiés : cliquer sur Calculer l’aperçu.')
        self.preflight_status.set('Prévol indisponible tant que l’aperçu n’est pas recalculé.')

    def invalidate_preflight(self, *_unused):
        # A sheet change invalidates only preflight, not geometry or canvas.
        self.preflight_status.set(
            'Zone utile modifiée : relancer le prévol.'
            if self.proposal is not None else
            'Prévol indisponible tant que l’aperçu n’est pas recalculé.')

    @staticmethod
    def _dimension(variable):
        text = variable.get()
        if not isinstance(text, str) or len(text) > 64:
            raise ValueError('Invalid dimension')
        return float(text.strip().replace(',', '.'))

    def calculate(self):
        self.invalidate()
        try:
            width, depth = self._dimension(self.width), self._dimension(self.depth)
            if self.kind.get() == 'Carte pliée':
                proposal = folded_card(width, depth)
            elif self.kind.get() == 'Boîte ouverte':
                proposal = open_tray(width, depth, self._dimension(self.wall), self._dimension(self.tab))
            else:
                raise ValueError('Unknown template')
        except (ValueError, OverflowError):
            self.status.set('Vérifier les dimensions : nombres positifs, et languette inférieure à la hauteur de paroi.')
            return
        self.proposal = proposal
        geometry = proposal['geometry']
        _, _, width, height = geometry['bbox_mm']
        cuts = sum(path['operation'] == 'CUT' for path in geometry['paths'])
        scores = sum(path['operation'] == 'SCORE' for path in geometry['paths'])
        self.status.set(f'Développé théorique : {width:g} × {height:g} mm · {cuts} tracé(s) CUT · {scores} SCORE.')
        self.preflight_status.set('Prévol statique à lancer avant tout export brouillon.')
        self._redraw()

    def run_preflight(self):
        if self.proposal is None:
            self.preflight_status.set('Recalculer un aperçu valide avant le prévol.')
            return None
        sheet_width = self.sheet_width.get().strip()
        sheet_height = self.sheet_height.get().strip()
        if bool(sheet_width) != bool(sheet_height):
            self.preflight_status.set(
                'Zone utile incomplète : indiquez les deux dimensions en mm '
                'ou laissez les deux champs vides.')
            return None
        usable_sheet = None
        if sheet_width:
            try:
                usable_sheet = (self._dimension(self.sheet_width),
                                self._dimension(self.sheet_height))
            except (ValueError, OverflowError):
                self.preflight_status.set(
                    'Zone utile invalide : utilisez deux dimensions positives en mm.')
                return None
        result = preflight_template(self.proposal, usable_sheet_mm=usable_sheet)
        if result['blocking_codes'] == ['TEMPLATE_BOUNDS_EXCEEDED']:
            self.preflight_status.set(
                'Prévol bloqué : le développé ne tient pas dans la zone utile '
                'déclarée. Adaptez les dimensions ou la disposition.')
        elif result['blocking_codes'] == ['TEMPLATE_SHEET_INVALID']:
            self.preflight_status.set(
                'Zone utile invalide : utilisez deux dimensions positives en mm.')
        elif result['status'] == 'BLOCKED':
            paths = ', '.join(result['path_ids'])
            detail = f' · tracés : {paths}' if paths else ''
            self.preflight_status.set(
                f"Prévol bloqué : {result['blocking_codes'][0]}{detail}.")
        else:
            if usable_sheet is None:
                self.preflight_status.set(
                    'Prévol statique cohérent · zone utile non déclarée ; '
                    'matière, outil, Design Space et fabrication non qualifiés.')
            else:
                self.preflight_status.set(
                    'Prévol : développé dans la zone utile déclarée, '
                    'sans validation machine, matière, Design Space ou découpe.')
        return result

    def _redraw(self, *_unused):
        self.canvas.delete('all')
        if self.proposal is None:
            return
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        width = 720 if width <= 1 else width
        height = 320 if height <= 1 else height
        if width <= 48 or height <= 48:
            return
        x, y, w, h = self.proposal['geometry']['bbox_mm']
        scale = min((width - 48) / w, (height - 48) / h)
        left, top = (width - w * scale) / 2, (height - h * scale) / 2
        for path in self.proposal['geometry']['paths']:
            points = [coordinate for px, py in path['points_mm']
                      for coordinate in (left + (px - x) * scale, top + (py - y) * scale)]
            style = {'fill': '#26322E', 'width': 2}
            if path['operation'] == 'SCORE':
                style.update(fill='#1D5DA8', dash=(6, 4))
            self.canvas.create_line(*points, **style)


class NativeTemplatePreview(TemplatePreviewContent):
    """Compatible popup adapter for callers outside the shared application."""

    def __init__(self, root, tk, ttk):
        self.window = tk.Toplevel(root)
        self.window.title('Fabrique · gabarits carte et boîte (brouillon)')
        self.window.geometry('800x680')
        self.window.minsize(660, 580)
        self.window.transient(root)
        super().__init__(self.window, tk, ttk)


def open_template_preview(current, root, tk, ttk):
    """Reuse a live preview window; a closed one may be created afresh."""
    if current is not None and current.window.winfo_exists():
        current.window.lift()
        return current
    return NativeTemplatePreview(root, tk, ttk)
