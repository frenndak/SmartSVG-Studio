"""Read-only Tk viewport for a bounded, already decoded project image."""
from __future__ import annotations

from math import ceil

from smartsvg_core.source_preview_v34 import MAX_SCREEN_HEIGHT, MAX_SCREEN_WIDTH


def fit_factor(width, height, available_width, available_height):
    return max(1, ceil(width / available_width), ceil(height / available_height))


class NativeImageViewport:
    def __init__(self, parent, tk, ttk):
        self.original = self.display = None
        self.fit_scale = None
        self.frame = ttk.Frame(parent)
        controls = ttk.Frame(self.frame)
        controls.pack(anchor='w', pady=(0, 4))
        self.fit_button = ttk.Button(controls, text='Adapter', command=self.fit)
        self.fit_button.pack(side='left')
        self.actual_button = ttk.Button(controls, text='100 %', command=self.actual_size)
        self.actual_button.pack(side='left', padx=6)
        ttk.Label(controls, text='Déplacer : glisser ou utiliser les flèches').pack(side='left')
        self.canvas = tk.Canvas(self.frame, width=MAX_SCREEN_WIDTH, height=MAX_SCREEN_HEIGHT,
                                highlightthickness=1, takefocus=True)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind('<Configure>', self._resize)
        self.canvas.bind('<ButtonPress-1>', self._start_drag)
        self.canvas.bind('<B1-Motion>', lambda event: self.canvas.scan_dragto(event.x, event.y, gain=1))
        for key, axis, direction in (('Left', 'x', -1), ('Right', 'x', 1),
                                     ('Up', 'y', -1), ('Down', 'y', 1)):
            scroll = self.canvas.xview_scroll if axis == 'x' else self.canvas.yview_scroll
            self.canvas.bind(f'<{key}>', lambda _event, step=direction, move=scroll: move(step, 'units'))
        self.load(None)

    def load(self, image):
        self.original = image
        self.fit_scale = None
        if image is None:
            self.frame.pack_forget()
            self._show(None)
            return
        self.fit()
        self.frame.pack(fill='both', expand=True)

    def fit(self):
        if self.original is not None:
            width = self.canvas.winfo_width() - 2
            height = self.canvas.winfo_height() - 2
            factor = fit_factor(self.original.width(), self.original.height(),
                                width if width > 0 else MAX_SCREEN_WIDTH,
                                height if height > 0 else MAX_SCREEN_HEIGHT)
            if factor != self.fit_scale:
                self.fit_scale = factor
                self._show(self.original.subsample(factor) if factor > 1 else self.original)

    def _resize(self, _event):
        if self.fit_scale is not None:
            self.fit()

    def actual_size(self):
        if self.original is not None:
            self.fit_scale = None
            self._show(self.original)

    def _show(self, image):
        self.canvas.delete('all')
        self.display = image
        region = (0, 0, 0, 0)
        if image is not None:
            self.canvas.create_image(0, 0, anchor='nw', image=image)
            region = (0, 0, image.width(), image.height())
        self.canvas.configure(scrollregion=region)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

    def _start_drag(self, event):
        self.canvas.focus_set()
        self.canvas.scan_mark(event.x, event.y)
