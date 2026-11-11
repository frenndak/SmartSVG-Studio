"""V34-132/133 native *read-only* brush draft for an archived proven Subject.

This panel is deliberately standalone until the Atelier PR and the verified
bridge have landed together. A UI gesture yields normalized image coordinates;
the existing G3.3e engine alone resolves subject identity, validates float32
and computes before/after PNG previews. No archive writes, export, or Undo
claims. All Tk objects are confined to the UI thread.
"""
from __future__ import annotations

import base64
from uuid import uuid4
from math import ceil, isfinite
from pathlib import Path
import re
import struct

from smartsvg_core.native_preview_jobs_v34 import LatestOnlyJob
from smartsvg_core.native_subject_preview_v34 import preview_native_subject_stroke
from smartsvg_core.native_subject_save_v34 import save_native_subject_stroke
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


def matching_preview_dimensions(source, before, after):
    """Reject a mismatched CPU comparison before publishing or saving it.

    A before/after image with different geometry can visually misrepresent
    the mask being committed, even when each PNG is individually bounded.
    """
    if not all(bounded_tk_png(png) for png in (source, before, after)):
        return False
    def dimensions(png):
        return struct.unpack_from('>II', png, 16)
    return dimensions(source) == dimensions(before) == dimensions(after)


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
    def __init__(self, root, parent, tk, ttk, *, preview_fn=preview_native_subject_stroke,
                 save_fn=save_native_subject_stroke, confirm_fn=None, on_saved=None):
        self.root, self.tk = root, tk
        self._save_fn = save_fn
        self._confirm_fn = confirm_fn
        self._on_saved = on_saved
        self._closed = False
        self._token = 0
        self._job = LatestOnlyJob(lambda request: preview_fn(**request))
        self._identity = None
        self._identity_png = None
        self._image = self._display = None
        self._result_images = None
        self._verified_save_request = None
        self._inflight_request = None
        self._save_pending = False
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
        self.mode_picker.bind('<<ComboboxSelected>>', self._parameter_changed)
        ttk.Label(controls, text='Rayon :').pack(side='left')
        self.radius_picker = ttk.Combobox(
            controls, textvariable=self.radius, state='readonly',
            values=_RADII, width=7)
        self.radius_picker.pack(side='left', padx=4)
        self.radius_picker.bind('<<ComboboxSelected>>', self._parameter_changed)
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
        self.save_button = ttk.Button(
            actions, text='Enregistrer…', command=self.save)
        self.save_button.pack(side='left', padx=4)
        ttk.Label(parent, textvariable=self.status,
                  wraplength=530).pack(anchor='w', pady=(5, 0))
        self._controls()

    def _controls(self):
        active = self._identity is not None and not self._closed
        self.mode_picker.configure(state='readonly' if active and not self._save_pending else 'disabled')
        self.radius_picker.configure(state='readonly' if active and not self._save_pending else 'disabled')
        self.preview_button.configure(
            state='normal' if active and bool(self._points)
            and not self._overflow and not self._busy and not self._save_pending else 'disabled')
        self.discard_button.configure(
            state='normal' if active and not self._save_pending and (self._points or self._result_images)
            else 'disabled')
        self.save_button.configure(
            state='normal' if active and not self._busy and not self._save_pending
            and self._result_images is not None
            and self._verified_save_request is not None else 'disabled')
        for button in (self.before_button, self.after_button):
            button.configure(
                state='normal' if active and self._result_images is not None else 'disabled')

    def load(self, *, project_path=None, expected_sha256=None,
             subject_id=None, preview_png=None):
        """Reset selection and invalidate every outstanding CPU result."""
        self._token += 1
        self._identity, self._image, self._result_images = None, None, None
        self._identity_png = None
        self._verified_save_request = None
        self._inflight_request = None
        self._save_pending = False
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
        self._identity_png = preview_png
        self._identity = (project_path, expected_sha256, subject_id)
        self.status.set('Dessinez sur le masque, puis calculez l’aperçu. Aucune sauvegarde.')
        self._draw()
        self._controls()

    def _draw(self, _event=None):
        # Configure events may be queued while the parent window is closing.
        if self._closed:
            return
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
        if (self._closed or self._identity is None or self._busy or self._save_pending or
                self._result_images is not None):
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
        if (self._closed or self._identity is None or self._busy or self._save_pending or
                normalized_mask_point(event.x, event.y, self._box) is None):
            # A click in the letterbox is not a new stroke; keep the last
            # comparison and in-flight request intact.
            return
        self._verified_save_request = None
        self._token += 1  # invalidate any previous asynchronous reply
        self._busy = False
        self._result_images = None
        self._points = []
        self._overflow = False
        self.canvas.focus_set()
        self._append(event.x, event.y)

    def _drag(self, event):
        self._append(event.x, event.y)

    def _parameter_changed(self, _event=None):
        """Invalidate a result computed with an older mode or radius."""
        if self._closed or self._identity is None or self._save_pending:
            return
        self._verified_save_request = None
        self._inflight_request = None
        self._token += 1  # ignore an in-flight result from the old settings
        self._busy = False
        self._result_images = None
        self._variant = 'after'
        self.status.set('Pinceau modifié : recalculez l’aperçu avant/après.')
        self._draw()
        self._controls()

    def _release(self, _event):
        # A queued release can arrive after the parent Tk widget was destroyed.
        if not self._closed:
            self._controls()

    def preview(self):
        if (self._closed or self._identity is None or not self._points
                or self._overflow or self._busy or self._save_pending or
                self.mode.get() not in _MODES or self.radius.get() not in _RADII):
            return False
        project_path, expected_sha256, subject_id = self._identity
        payload = {
            'project_path': project_path, 'expected_sha256': expected_sha256,
            'subject_id': subject_id, 'mode': _MODES[self.mode.get()],
            'radius': float(self.radius.get()),
            'points': [point[:] for point in self._points],
        }
        self._verified_save_request = None
        # Pin exactly the gesture submitted to the CPU worker. No later UI
        # event may promote a different gesture to a saveable preview.
        self._inflight_request = (
            self._identity, payload['mode'], payload['radius'],
            tuple(tuple(point) for point in payload['points']))
        self._token += 1
        token = self._token
        self._busy = True
        self._controls()
        self.status.set('Calcul de la retouche en lecture seule…')
        try:
            version, future = self._job.submit(payload)
        except RuntimeError:
            self._busy = False
            self._inflight_request = None
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
            bound = self._inflight_request
            if (bound is None or bound[0] != self._identity or
                    bound[1] != _MODES.get(self.mode.get()) or
                    self.radius.get() not in _RADII or
                    bound[2] != float(self.radius.get()) or
                    bound[3] != tuple(tuple(point) for point in self._points)):
                raise ValueError('STALE_STROKE')
            result = future.result()
            if (result['subject_id'] != self._identity[2] or
                    result['project_sha256'] != self._identity[1] or
                    result['persisted'] is not False):
                raise ValueError('STALE_PREVIEW')
            # Validate the displayed count before publishing any preview images.
            # A malformed backend result must not crash the Tk callback after
            # the exception handler has completed.
            if (type(result.get('changed_pixels')) is not int or
                    result['changed_pixels'] < 0):
                raise ValueError('INVALID_CHANGED_PIXELS')
            digest = result.get('preview_mask_sha256_float32')
            if type(digest) is not str or not _SHA.fullmatch(digest):
                raise ValueError('INVALID_CPU_PREVIEW_DIGEST')
            if not matching_preview_dimensions(
                    self._identity_png, result['before_png_l8'],
                    result['after_png_l8']):
                raise ValueError('PREVIEW_GEOMETRY_MISMATCH')
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
            self._inflight_request = None
            self._verified_save_request = None
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
        # Preserve the immutable CPU command with its verified preview digest.
        # A later save button must reuse this command, not rebuild points from
        # potentially changed controls or a new subject selection.
        self._verified_save_request = (
            result['preview_mask_sha256_float32'], token, bound)
        self._inflight_request = None
        self._result_images = photos
        self._variant = 'after'
        self._draw()
        self.status.set(
            f"Aperçu calculé · {result['changed_pixels']} pixel(s) modifié(s). "
            "Non enregistré : aucune écriture dans le projet.")
        self._controls()

    def save(self):
        """Explicit confirmation; only the proven historical writer may persist."""
        if (self._closed or self._busy or self._save_pending or
                self._identity is None or self._result_images is None or
                self._verified_save_request is None):
            return False
        digest, token, bound = self._verified_save_request
        if (token != self._token or bound[0] != self._identity or
                bound[1] != _MODES.get(self.mode.get()) or
                self.radius.get() not in _RADII or
                bound[2] != float(self.radius.get()) or
                bound[3] != tuple(tuple(p) for p in self._points)):
            self._verified_save_request = None
            self.status.set('Aperçu périmé : recalculez avant d’enregistrer.')
            self._controls()
            return False
        from tkinter import messagebox
        confirm = self._confirm_fn or (
            lambda: messagebox.askyesno(
                'Confirmer la retouche',
                'Enregistrer cette retouche dans le projet V1 ? '
                'Une sauvegarde précédente sera conservée.',
                parent=self.root))
        # A confirmation can dispatch nested Tk events. Recheck every proof
        # after the dialog returns, before any call to the writer.
        try:
            accepted = confirm() is True
        except Exception:
            accepted = False
        if not accepted or self._closed or token != self._token or (
                digest, token, bound) != self._verified_save_request:
            return False
        self._save_pending = True
        self._controls()
        self.status.set('Enregistrement confirmé · vérification du projet…')
        project_path, revision, subject_id = bound[0]
        try:
            result = self._save_fn(
                project_path=project_path, expected_sha256=revision,
                subject_id=subject_id, mode=bound[1], radius=bound[2],
                points=[list(p) for p in bound[3]],
                expected_preview_mask_sha256_float32=digest,
                command_id='native-' + uuid4().hex, confirmed=True)
            if (type(result) is not dict or
                    result.get('persisted') is not True or
                    result.get('subject_id') != subject_id or
                    result.get('status') not in
                    ('subject_brush_saved', 'subject_brush_already_saved') or
                    type(result.get('project_sha256')) is not str or
                    not _SHA.fullmatch(result['project_sha256'])):
                raise ValueError('UNCERTAIN_SAVE_RECEIPT')
        except Exception as exc:
            # A failed receipt is NOT evidence that the archive was unchanged.
            # Discard the stale preview; require a new F5 inspection.
            self._token += 1
            self._verified_save_request = None
            self._result_images = None
            self._identity = None
            self._save_pending = False
            code = getattr(exc, 'code', '')
            self.status.set(
                'Projet modifié ailleurs : réexaminez-le (F5).' if
                code == 'PROJECT_CHANGED' else
                'Enregistrement non confirmé : réexaminez le projet (F5) '
                'avant toute nouvelle retouche.')
            if not self._closed:
                self._draw()
                self._controls()
            return False
        # Invalidate this entire panel, including any pending CPU result.
        self._token += 1
        self._verified_save_request = None
        self._result_images = None
        self._identity = None
        self._save_pending = False
        if not self._closed:
            self.status.set('Retouche enregistrée. Réexaminez le projet (F5).')
            self._draw()
            self._controls()
            if self._on_saved is not None:
                try:
                    self._on_saved(result)
                except Exception:
                    # The archive is already committed; never imply rollback.
                    self.status.set(
                        'Retouche enregistrée ; actualisation indisponible. '
                        'Réexaminez le projet (F5).')
        return True

    def show(self, variant):
        if (not self._closed and self._result_images is not None
                and variant in ('before', 'after')):
            self._variant = variant
            self._draw()

    def discard(self):
        if self._closed or self._save_pending:
            return
        self._token += 1
        self._busy = False
        self._points = []
        self._overflow = False
        self._result_images = None
        self._verified_save_request = None
        self._inflight_request = None
        self._variant = 'after'
        self.status.set('Brouillon abandonné. Le projet n’a pas été modifié.')
        self._draw()
        self._controls()

    def shutdown(self):
        if not self._closed:
            self._closed = True
            self._token += 1
            self._inflight_request = None
            self._verified_save_request = None
            self._job.close()
