"""V34-132/133 native *read-only* brush draft for an archived proven Subject.

This panel is deliberately standalone until the Atelier PR and the verified
bridge have landed together. A UI gesture yields normalized image coordinates;
the existing G3.3e engine alone resolves subject identity, validates float32
and computes before/after PNG previews. No archive writes, export, or Undo
claims. All Tk objects are confined to the UI thread.
"""
from __future__ import annotations

import base64
from math import ceil, isfinite
from pathlib import Path
import re
import struct

from smartsvg_core.native_preview_jobs_v34 import LatestOnlyJob
from smartsvg_core.native_subject_preview_v34 import preview_native_subject_stroke
from smartsvg_core.source_preview_v34 import MAX_ENCODED_BYTES


_SHA = re.compile(r"^[0-9a-f]{64}$")
_SUBJECT = re.compile(r"^subject-[0-9a-f]{32}$")
MAX_GESTURE_POINTS = 64
_MODES = {"Ajouter": "add", "Effacer": "erase"}
_RADII = ("0.02", "0.05", "0.10")
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def bounded_tk_png(raw):
    """Reject compressed dimension bombs before Tk allocates a PhotoImage.

    Source previews are already archive-verified and backend results are
    trusted encodings, but Tk still needs an independent allocation bound.
    This is a strict preflight, not an alternative PNG authenticity check.
    """
    if (type(raw) is not bytes or not 33 <= len(raw) <= MAX_ENCODED_BYTES or
            raw[:8] != _PNG_SIGNATURE or raw[12:16] != b'IHDR' or
            struct.unpack_from('>I', raw, 8)[0] != 13):
        return False
    width, height = struct.unpack_from('>II', raw, 16)
    return 0 < width <= 2048 and 0 < height <= 2048


def normalized_mask_point(x, y, image_box):
    """Map a point from a letterboxed Tk image to a normalized source point.

    The rectangle is (left, top, displayed_width, displayed_height), with
    exclusive right/bottom edges. Black margins and invalid geometry reject
    the gesture rather than painting the wrong pixel or silently clipping.
    """
    if (type(image_box) not in (tuple, list) or len(image_box) != 4 or
            not all(type(v) in (int, float) and isfinite(v)
                    for v in (x, y, *image_box))):
        return None
    left, top, width, height = image_box
    if width <= 0 or height <= 0 or not (
            left <= x < left + width and top <= y < top + height):
        return None
    return [(x - left) / width, (y - top) / height]


class NativeBrushDraftPanel:
    def __init__(self, root, parent, tk, ttk, *, preview_fn=preview_native_subject_stroke):
        self.root, self.tk = root, tk
        self._closed = False
        self._token = 0
        self._job = LatestOnlyJob(lambda request: preview_fn(**request))
        self._identity = None
        self._image = self._display = None
        self._result_images = None
        self._box = None
        self._points = []
        self._overflow = False
        self._busy = False
        self._variant = 'after'
        self.mode = tk.StringVar(value='Ajouter')
        self.radius = tk.StringVar(value='0.05')
        self.status = tk.StringVar(value='Choisissez un sujet float32 vérifié.')
        ttk.Label(parent, text='Retouche · brouillon non enregistré',
                  font=('Segoe UI', 12, 'bold')).pack(anchor='w', pady=(8, 4))
        controls = ttk.Frame(parent)
        controls.pack(fill='x', pady=(0, 4))
        ttk.Label(controls, text='Pinceau :').pack(side='left')
        self.mode_picker = ttk.Combobox(
            controls, textvariable=self.mode, state='readonly',
            values=tuple(_MODES), width=10)
        self.mode_picker.pack(side='left', padx=(4, 8))
        ttk.Label(controls, text='Rayon :').pack(side='left')
        self.radius_picker = ttk.Combobox(
            controls, textvariable=self.radius, state='readonly',
            values=_RADII, width=7)
        self.radius_picker.pack(side='left', padx=4)
        self.canvas = tk.Canvas(
            parent, width=480, height=320, highlightthickness=1,
            takefocus=True)
        self.canvas.pack(fill='both', expand=True, pady=(4, 6))
        self.canvas.bind('<Configure>', self._draw)
        self.canvas.bind('<ButtonPress-1>', self._press)
        self.canvas.bind('<B1-Motion>', self._drag)
        self.canvas.bind('<ButtonRelease-1>', self._release)
        actions = ttk.Frame(parent)
        actions.pack(fill='x')
        self.preview_button = ttk.Button(
            actions, text='Calculer avant/après', command=self.preview)
        self.preview_button.pack(side='left', padx=(0, 4))
        self.before_button = ttk.Button(
            actions, text='Avant', command=lambda: self.show('before'))
        self.before_button.pack(side='left', padx=4)
        self.after_button = ttk.Button(
            actions, text='Après', command=lambda: self.show('after'))
        self.after_button.pack(side='left', padx=4)
        self.discard_button = ttk.Button(
            actions, text='Effacer le brouillon', command=self.discard)
        self.discard_button.pack(side='left', padx=4)
        ttk.Label(parent, textvariable=self.status,
                  wraplength=530).pack(anchor='w', pady=(5, 0))
        self._controls()

    def _controls(self):
        active = self._identity is not None and not self._closed
        self.mode_picker.configure(state='readonly' if active else 'disabled')
        self.radius_picker.configure(state='readonly' if active else 'disabled')
        self.preview_button.configure(
            state='normal' if active and bool(self._points)
            and not self._overflow and not self._busy else 'disabled')
        self.discard_button.configure(
            state='normal' if active and (self._points or self._result_images)
            else 'disabled')
        for button in (self.before_button, self.after_button):
            button.configure(
                state='normal' if self._result_images is not None else 'disabled')

    def load(self, *, project_path=None, expected_sha256=None,
             subject_id=None, preview_png=None):
        """Reset selection and invalidate every outstanding CPU result."""
        self._token += 1
        self._identity, self._image, self._result_images = None, None, None
        self._points = []
        self._box = None
        self._overflow = self._busy = False
        self._variant = 'after'
        if self._closed:
            return
        if (type(project_path) is not str or
                not Path(project_path).is_absolute() or
                type(expected_sha256) is not str or
                not _SHA.fullmatch(expected_sha256) or
                type(subject_id) is not str or
                not _SUBJECT.fullmatch(subject_id) or
                not bounded_tk_png(preview_png)):
            self.status.set('Sujet absent ou non vérifié : retouche indisponible.')
            self._draw()
            self._controls()
            return
        try:
            photo = self.tk.PhotoImage(
                master=self.root, data=base64.b64encode(preview_png).decode('ascii'),
                format='png')
            if not 0 < photo.width() <= 2048 or not 0 < photo.height() <= 2048:
                raise ValueError('UNBOUNDED_PREVIEW')
        except (self.tk.TclError, ValueError):
            self.status.set('PNG du masque non décodable : retouche refusée.')
            self._draw()
            self._controls()
            return
        self._image = photo
        self._identity = (project_path, expected_sha256, subject_id)
        self.status.set('Dessinez sur le masque, puis calculez l’aperçu. Aucune sauvegarde.')
        self._draw()
        self._controls()

    def _draw(self, _event=None):
        self.canvas.delete('all')
        self._box, self._display = None, None
        image = (self._result_images or {}).get(self._variant, self._image)
        if image is None:
            return
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        if width <= 1:
            width = 480
        if height <= 1:
            height = 320
        factor = max(1, ceil(image.width() / width), ceil(image.height() / height))
        display = image.subsample(factor) if factor > 1 else image
        left, top = max(0, (width - display.width()) // 2), max(
            0, (height - display.height()) // 2)
        self._box, self._display = (left, top, display.width(), display.height()), display
        self.canvas.create_image(left, top, anchor='nw', image=display)
        if self._points and self._variant == 'after' and self._result_images is None:
            screen = [(left + x * display.width(), top + y * display.height())
                      for x, y in self._points]
            if len(screen) == 1:
                x, y = screen[0]
                self.canvas.create_oval(x-2, y-2, x+2, y+2, outline='#2473ad')
            else:
                self.canvas.create_line(
                    *[value for xy in screen for value in xy], fill='#2473ad',
                    width=2)

    def _append(self, x, y):
        if self._identity is None or self._result_images is not None:
            return
        point = normalized_mask_point(x, y, self._box)
        if point is None or (self._points and point == self._points[-1]):
            return
        if len(self._points) >= MAX_GESTURE_POINTS:
            self._overflow = True
            self.status.set('Geste trop long (64 points maximum) : effacez le brouillon.')
            self._controls()
            return
        self._points.append(point)
        self.status.set(f'{len(self._points)} point(s) · brouillon non enregistré.')
        self._controls()
        self._draw()

    def _press(self, event):
        if self._identity is None:
            return
        self._token += 1  # invalidate any previous asynchronous reply
        self._busy = False
        self._result_images = None
        self._points = []
        self._overflow = False
        self.canvas.focus_set()
        self._append(event.x, event.y)

    def _drag(self, event):
        self._append(event.x, event.y)

    def _release(self, _event):
        self._controls()

    def preview(self):
        if (self._closed or self._identity is None or not self._points
                or self._overflow or self._busy or
                self.mode.get() not in _MODES or self.radius.get() not in _RADII):
            return False
        project_path, expected_sha256, subject_id = self._identity
        payload = {
            'project_path': project_path, 'expected_sha256': expected_sha256,
            'subject_id': subject_id, 'mode': _MODES[self.mode.get()],
            'radius': float(self.radius.get()),
            'points': [point[:] for point in self._points],
        }
        self._token += 1
        token = self._token
        self._busy = True
        self._controls()
        self.status.set('Calcul de la retouche en lecture seule…')
        try:
            version, future = self._job.submit(payload)
        except RuntimeError:
            self._busy = False
            self.status.set('Aperçu indisponible : le panneau est fermé.')
            self._controls()
            return False
        self.root.after(50, lambda: self._receive(token, version, future))
        return True

    def _receive(self, token, version, future):
        if (self._closed or token != self._token or
                not self._job.current(version)):
            return
        if not future.done():
            self.root.after(50, lambda: self._receive(token, version, future))
            return
        self._busy = False
        try:
            result = future.result()
            if (result['subject_id'] != self._identity[2] or
                    result['project_sha256'] != self._identity[1] or
                    result['persisted'] is not False):
                raise ValueError('STALE_PREVIEW')
            photos = {}
            for variant in ('before', 'after'):
                raw = result[variant + '_png_l8']
                if not bounded_tk_png(raw):
                    raise ValueError('INVALID_PREVIEW_PNG')
                photo = self.tk.PhotoImage(
                    master=self.root, data=base64.b64encode(raw).decode('ascii'),
                    format='png')
                if (not 0 < photo.width() <= 2048 or
                        not 0 < photo.height() <= 2048):
                    raise ValueError('INVALID_PREVIEW_DIMENSIONS')
                photos[variant] = photo
        except (Exception,) as exc:
            # Only a stable code is displayed. A backend exception may contain
            # filesystem paths or private project data; never show str(exc).
            code = getattr(exc, 'code', '')
            if code in ('PROJECT_CHANGED', 'PROJECT_CHANGED_DURING_PREVIEW'):
                self.status.set('Projet modifié ailleurs : réexaminez-le (F5).')
            elif code in ('SUBJECT_NOT_VERIFIED', 'SUBJECT_PROOF_MISMATCH',
                          'INVALID_SUBJECT_PROOF'):
                self.status.set('Identité du sujet non vérifiée : aucune retouche.')
            elif code == 'BRUSH_RUNTIME_UNAVAILABLE':
                self.status.set('Moteur CPU indisponible (NumPy/Pillow).')
            else:
                self.status.set('Aperçu refusé. Corrigez le geste ou réexaminez le projet.')
            self._controls()
            return
        self._result_images = photos
        self._variant = 'after'
        self._draw()
        self.status.set(
            f"Aperçu calculé · {result['changed_pixels']} pixel(s) modifié(s). "
            "Non enregistré : aucune écriture dans le projet.")
        self._controls()

    def show(self, variant):
        if self._result_images is not None and variant in ('before', 'after'):
            self._variant = variant
            self._draw()

    def discard(self):
        self._token += 1
        self._busy = False
        self._points = []
        self._overflow = False
        self._result_images = None
        self._variant = 'after'
        self.status.set('Brouillon abandonné. Le projet n’a pas été modifié.')
        self._draw()
        self._controls()

    def shutdown(self):
        if not self._closed:
            self._closed = True
            self._token += 1
            self._job.close()
