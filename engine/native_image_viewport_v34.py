"""Read-only Tk viewport for a bounded, already decoded project image."""
from __future__ import annotations

from math import ceil

from smartsvg_core.source_preview_v34 import MAX_SCREEN_HEIGHT, MAX_SCREEN_WIDTH


def fit_factor(width, height, available_width, available_height):
    """Fit valid image pixels even while Tk reports a zero-size canvas.

    During initial layout/minimization Tk can transiently report 0 for a
    viewport dimension. Treat that dimension as one pixel rather than
    dividing by zero or enlarging the source. Invalid image sizes are not
    displayable and must be rejected explicitly.
    """
    if width <= 0 or height <= 0:
        raise ValueError('image dimensions must be positive')
    return max(1, ceil(width / max(1, available_width)),
               ceil(height / max(1, available_height)))


class NativeImageViewport:
    def __init__(self, parent, tk, ttk):
        self.original = self.display = None
        self.fit_scale = None
        self.auto_fit = True
        self.frame = ttk.Frame(parent)
        controls = ttk.Frame(self.frame)
        controls.pack(anchor='w', pady=(0, 4))
        self.fit_button = ttk.Button(controls, text='Adapter', command=self.fit)
        self.fit_button.pack(side='left')
        self.actual_button = ttk.Button(controls, text='100 %', command=self.actual_size)
        self.actual_button.pack(side='left', padx=6)
        self.zoom_in_button = ttk.Button(controls, text='Zoom +', command=self.zoom_in)
        self.zoom_in_button.pack(side='left', padx=(0, 4))
        self.zoom_out_button = ttk.Button(controls, text='Zoom −', command=self.zoom_out)
        self.zoom_out_button.pack(side='left', padx=(0, 6))
        # Avoid a wide single-row toolbar in a narrow Atelier pane.
        ttk.Label(self.frame, text='Glisser/flèches : déplacer · +/− : zoom · Home : adapter · 0 : 100 %',
                  wraplength=460).pack(anchor='w', pady=(0, 4))
        self.canvas = tk.Canvas(self.frame, width=MAX_SCREEN_WIDTH, height=MAX_SCREEN_HEIGHT,
                                highlightthickness=1, takefocus=True)
        self.canvas.pack(fill='both', expand=True)
        self.canvas.bind('<Configure>', self._resize)
        self.canvas.bind('<ButtonPress-1>', self._start_drag)
        self.canvas.bind('<B1-Motion>', lambda event: self.canvas.scan_dragto(event.x, event.y, gain=1))
        for shortcut in ('<plus>', '<KP_Add>'):
            self.canvas.bind(shortcut, self._zoom_in_key)
        for shortcut in ('<minus>', '<KP_Subtract>'):
            self.canvas.bind(shortcut, self._zoom_out_key)
        self.canvas.bind('<Home>', self._fit_key)
        self.canvas.bind('<Key-0>', self._actual_size_key)
        for key, axis, direction in (('Left', 'x', -1), ('Right', 'x', 1),
                                     ('Up', 'y', -1), ('Down', 'y', 1)):
            scroll = self.canvas.xview_scroll if axis == 'x' else self.canvas.yview_scroll
            self.canvas.bind(f'<{key}>', lambda _event, step=direction, move=scroll: move(step, 'units'))
        self.load(None)

    def load(self, image):
        self.original = image
        self.fit_scale = None
        self.auto_fit = True
        if image is None:
            self.frame.pack_forget()
            self._show(None, reset_view=True)
            return
        self.fit()
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.frame.pack(fill='both', expand=True)

    def _set_scale(self, factor):
        if self.original is None or factor == self.fit_scale:
            return
        self.fit_scale = factor
        self._show(self.original.subsample(factor) if factor > 1 else self.original)

    def fit(self):
        if self.original is None:
            return
        self.auto_fit = True
        width = self.canvas.winfo_width() - 2
        height = self.canvas.winfo_height() - 2
        # Preserve a previously computed fit while Tk is temporarily
        # unmapped/minimized. Refit on the next valid Configure event.
        # Initial loading still uses the bounded fallback below.
        if (width <= 0 or height <= 0) and self.fit_scale is not None:
            return
        factor = fit_factor(self.original.width(), self.original.height(),
                            width if width > 0 else MAX_SCREEN_WIDTH,
                            height if height > 0 else MAX_SCREEN_HEIGHT)
        self._set_scale(factor)

    def _resize(self, _event):
        if self.auto_fit:
            self.fit()

    def actual_size(self):
        if self.original is not None:
            self.auto_fit = False
            # Preserve the existing "100 %" state contract: fit_scale is
            # None when the original image is displayed unscaled.
            self.fit_scale = None
            self._show(self.original)

    def zoom_in(self):
        if self.original is not None:
            self.auto_fit = False
            self._set_scale(max(1, (self.fit_scale or 1) - 1))

    def zoom_out(self):
        if self.original is not None:
            self.auto_fit = False
            current = self.fit_scale or 1
            # A bounded integer subsample keeps Tk image allocation within
            # the already-validated original image; never enlarge pixels.
            ceiling = max(32, current)
            self._set_scale(min(current + 1, ceiling))

    def _zoom_in_key(self, _event):
        self.zoom_in()
        return 'break'

    def _zoom_out_key(self, _event):
        self.zoom_out()
        return 'break'

    def _fit_key(self, _event):
        self.fit()
        return 'break'

    def _actual_size_key(self, _event):
        self.actual_size()
        return 'break'

    def _show(self, image, reset_view=False):
        # Preserve the image-relative viewport centre when changing scale.
        # Loading a different image explicitly resets the view instead.
        previous = None
        if not reset_view and self.display is not None:
            x0, x1 = self.canvas.xview()
            y0, y1 = self.canvas.yview()
            previous = ((x0 + x1) / 2, (y0 + y1) / 2)
        self.canvas.delete('all')
        self.display = image
        region = (0, 0, 0, 0)
        if image is not None:
            self.canvas.create_image(0, 0, anchor='nw', image=image)
            region = (0, 0, image.width(), image.height())
        self.canvas.configure(scrollregion=region)
        if previous is None or image is None:
            self.canvas.xview_moveto(0)
            self.canvas.yview_moveto(0)
        else:
            x0, x1 = self.canvas.xview()
            y0, y1 = self.canvas.yview()
            self.canvas.xview_moveto(max(0, previous[0] - (x1 - x0) / 2))
            self.canvas.yview_moveto(max(0, previous[1] - (y1 - y0) / 2))

    def _start_drag(self, event):
        self.canvas.focus_set()
        self.canvas.scan_mark(event.x, event.y)
