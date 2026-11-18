"""V34-132/133 native *read-only* brush draft for an archived proven Subject.

This panel is deliberately standalone until the Atelier PR and the verified
bridge have landed together. A UI gesture yields normalized image coordinates;
the existing G3.3e engine alone resolves subject identity, validates float32
and computes before/after PNG previews. Draft-point undo/redo is UI-local; no
persisted history, export, or archive-write claim is made. All Tk objects are
confined to the UI thread.
"""
from __future__ import annotations

import base64
from copy import deepcopy
from uuid import uuid4
from math import ceil, isfinite
from pathlib import Path
import re
import struct

from smartsvg_core.subject_brush_preview_g33e import (
    MAX_PREVIEW_POINTS as MAX_GESTURE_SEGMENT_POINTS,
    MAX_PREVIEW_POINTS_TOTAL as MAX_DRAFT_POINTS_TOTAL,
)
from smartsvg_core.native_preview_jobs_v34 import LatestOnlyJob
from smartsvg_core.native_subject_preview_v34 import (
    preview_native_subject_stroke, preview_native_subject_strokes,
)
from smartsvg_core.native_subject_save_v34 import (
    save_native_subject_stroke, save_native_subject_strokes,
)
from smartsvg_core.source_preview_v34 import MAX_ENCODED_BYTES


_SHA = re.compile(r"^[0-9a-f]{64}$")
_SUBJECT = re.compile(r"^subject-[0-9a-f]{32}$")
MAX_GESTURE_POINTS = MAX_DRAFT_POINTS_TOTAL
MAX_DRAFT_STROKES = 16
_MODES = {"Ajouter": "add", "Effacer": "erase"}
_RADII = ("0.02", "0.05", "0.10")
_PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def dispatch_preview_request(single_fn, many_fn, request):
    """Keep the historical one-stroke call shape while routing batches."""
    strokes = request['strokes']
    identity = {key: request[key] for key in (
        'project_path', 'expected_sha256', 'subject_id')}
    if len(strokes) == 1:
        return single_fn(**identity, **strokes[0])
    return many_fn(**identity, strokes=strokes)


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
                 preview_many_fn=preview_native_subject_strokes,
                 save_fn=save_native_subject_stroke,
                 save_many_fn=save_native_subject_strokes,
                 confirm_fn=None, on_saved=None):
        self.root, self.tk = root, tk
        self._save_fn = save_fn
        self._save_many_fn = save_many_fn
        self._confirm_fn = confirm_fn
        self._on_saved = on_saved
        self._closed = False
        self._token = 0
        self._job = LatestOnlyJob(
            lambda request: dispatch_preview_request(
                preview_fn, preview_many_fn, request))
        self._identity = None
        self._recovery_identity = None
        self._identity_png = None
        self._image = self._display = None
        self._result_images = None
        self._verified_save_request = None
        self._inflight_request = None
        self._save_pending = False
        self._discard_confirming = False
        self._box = None
        self._points = []
        self._stroke_style = None
        self._strokes = []
        self._redo_points = []
        self._redo_strokes = []
        self._overflow = False
        self._busy = False
        self._drag_active = False
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
            parent, width=480, height=260, highlightthickness=1,
            takefocus=True)
        self.canvas.pack(fill='both', expand=True, pady=(4, 6))
        self.canvas.bind('<Configure>', self._draw)
        self.canvas.bind('<ButtonPress-1>', self._press)
        self.canvas.bind('<B1-Motion>', self._drag)
        self.canvas.bind('<ButtonRelease-1>', self._release)
        self.canvas.bind('<Control-z>', self._undo_draft_key)
        self.canvas.bind('<Control-y>', self._redo_draft_key)
        self.canvas.bind('<Escape>', self._discard_draft_key)
        actions = ttk.Frame(parent)
        actions.pack(fill='x')
        preview_actions = ttk.Frame(actions)
        preview_actions.pack(fill='x')
        draft_actions = ttk.Frame(actions)
        draft_actions.pack(fill='x', pady=(4, 0))
        zone_actions = ttk.Frame(actions)
        zone_actions.pack(fill='x', pady=(4, 0))
        self.preview_button = ttk.Button(
            preview_actions, text='Calculer avant/après', command=self.preview)
        self.preview_button.pack(side='left', padx=(0, 4))
        self.before_button = ttk.Button(
            preview_actions, text='Avant', command=lambda: self.show('before'))
        self.before_button.pack(side='left', padx=4)
        self.after_button = ttk.Button(
            preview_actions, text='Après', command=lambda: self.show('after'))
        self.after_button.pack(side='left', padx=4)
        self.undo_button = ttk.Button(
            draft_actions, text='Annuler le dernier point', command=self.undo_draft_point)
        self.undo_button.pack(side='left', padx=(0, 4))
        self.redo_button = ttk.Button(
            draft_actions, text='Rétablir le point', command=self.redo_draft_point)
        self.redo_button.pack(side='left', padx=4)
        self.discard_button = ttk.Button(
            draft_actions, text='Effacer le brouillon', command=self.request_discard)
        self.discard_button.pack(side='left', padx=4)
        self.save_button = ttk.Button(
            draft_actions, text='Enregistrer…', command=self.save)
        self.save_button.pack(side='left', padx=4)
        self.add_zone_button = ttk.Button(
            zone_actions, text='Ajouter cette zone', command=self.add_draft_zone)
        self.add_zone_button.pack(side='left', padx=(0, 4))
        self.remove_zone_button = ttk.Button(
            zone_actions, text='Retirer la derniere zone',
            command=self.remove_last_draft_zone)
        self.remove_zone_button.pack(side='left', padx=4)
        self.restore_zone_button = ttk.Button(
            zone_actions, text='Retablir la zone',
            command=self.restore_last_draft_zone)
        self.restore_zone_button.pack(side='left', padx=4)
        ttk.Label(parent, textvariable=self.status,
                  wraplength=530).pack(anchor='w', pady=(5, 0))
        self._controls()

    def _controls(self):
        active = self._identity is not None and not self._closed
        recoverable = (getattr(self, '_recovery_identity', None) is not None
                       and not self._closed)
        self.mode_picker.configure(state='readonly' if active and not self._save_pending else 'disabled')
        self.radius_picker.configure(state='readonly' if active and not self._save_pending else 'disabled')
        has_draft = bool(self._points or self._strokes)
        self.preview_button.configure(
            state='normal' if (active or recoverable) and has_draft
            and not self._overflow and not self._busy and not self._save_pending else 'disabled',
            text='Vérifier et recalculer' if recoverable else 'Calculer avant/après')
        self.undo_button.configure(
            state='normal' if active and bool(self._points) and not self._busy
            and not self._save_pending and self._result_images is None else 'disabled')
        self.redo_button.configure(
            state='normal' if active and bool(self._redo_points) and not self._busy
            and not self._save_pending and self._result_images is None else 'disabled')
        self.discard_button.configure(
            state='normal' if (active or recoverable) and not self._save_pending and (
                self._points or self._strokes or self._redo_points or
                self._redo_strokes or self._result_images)
            else 'disabled')
        self.save_button.configure(
            state='normal' if active and not self._busy and not self._save_pending
            and self._result_images is not None
            and self._verified_save_request is not None else 'disabled')
        self.add_zone_button.configure(
            state='normal' if active and bool(self._points) and not self._overflow
            and len(self._strokes) < MAX_DRAFT_STROKES and not self._busy
            and not self._save_pending and self._result_images is None else 'disabled')
        self.remove_zone_button.configure(
            state='normal' if active and bool(self._strokes) and not self._points
            and not self._redo_points
            and not self._busy and not self._save_pending
            and self._result_images is None else 'disabled')
        self.restore_zone_button.configure(
            state='normal' if active and bool(self._redo_strokes)
            and not self._points and not self._redo_points
            and len(self._strokes) < MAX_DRAFT_STROKES and not self._busy
            and not self._save_pending and self._result_images is None else 'disabled')
        for button in (self.before_button, self.after_button):
            button.configure(
                state='normal' if active and self._result_images is not None else 'disabled')

    def load(self, *, project_path=None, expected_sha256=None,
             subject_id=None, preview_png=None):
        """Reset selection and invalidate every outstanding CPU result."""
        self._token += 1
        self._identity, self._image, self._result_images = None, None, None
        self._recovery_identity = None
        self._identity_png = None
        self._verified_save_request = None
        self._inflight_request = None
        self._save_pending = False
        self._points = []
        self._stroke_style = None
        self._strokes = []
        self._redo_points = []
        self._redo_strokes = []
        self._box = None
        self._overflow = self._busy = False
        self._drag_active = False
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
        if self._variant == 'after' and self._result_images is None:
            for stroke in self._strokes:
                self._draw_stroke(left, top, display, stroke['points'], '#6b7280')
            self._draw_stroke(left, top, display, self._points, '#2473ad')

    def _draw_stroke(self, left, top, display, points, colour):
        if points:
            screen = [(left + x * display.width(), top + y * display.height())
                      for x, y in points]
            if len(screen) == 1:
                x, y = screen[0]
                self.canvas.create_oval(x-2, y-2, x+2, y+2, outline=colour)
            else:
                self.canvas.create_line(
                    *[value for xy in screen for value in xy], fill=colour,
                    width=2)

    def _append(self, x, y):
        if (self._closed or self._identity is None or self._busy or self._save_pending or
                self._result_images is not None):
            return
        if not self._points and self._draft_segment_count() >= MAX_DRAFT_STROKES:
            self.status.set(
                f'Limite de {MAX_DRAFT_STROKES} parties pour le calcul : '
                'enregistrez ou retirez une zone.')
            self._controls()
            return
        point = normalized_mask_point(x, y, self._box)
        if point is None or (self._points and point == self._points[-1]):
            return
        if len(self._points) >= MAX_GESTURE_POINTS:
            self._overflow = True
            self.status.set('Geste interrompu : limite du brouillon atteinte.')
            self._controls()
            return
        segments, points = self._draft_budget(current_size=len(self._points) + 1)
        if segments > MAX_DRAFT_STROKES or points > MAX_DRAFT_POINTS_TOTAL:
            self._overflow = bool(self._points)
            self.status.set(
                f'Geste interrompu : limite de {MAX_DRAFT_POINTS_TOTAL} points '
                f'ou {MAX_DRAFT_STROKES} segments atteinte. '
                'Corrigez ou annulez le geste avant de recalculer.')
            self._controls()
            return
        if not self._points:
            # Capture the settings at the start of this gesture. Subsequent
            # picker changes apply to the next gesture, not to this one.
            mode, radius = self.mode.get(), self.radius.get()
            if mode not in _MODES or radius not in _RADII:
                self.status.set('Choisissez un mode et un rayon valides.')
                self._controls()
                return
            self._stroke_style = (_MODES[mode], float(radius))
        self._redo_points = []
        self._redo_strokes = []
        self._points.append(point)
        self.status.set(f'{len(self._points)} point(s) · brouillon non enregistré.')
        self._controls()
        self._draw()

    def _press(self, event):
        if self._closed:
            return
        self._drag_active = False
        if (self._identity is None or self._busy or self._save_pending or
                normalized_mask_point(event.x, event.y, self._box) is None):
            # A click in the letterbox is not a new stroke; keep the last
            # comparison and in-flight request intact.
            return
        if self._overflow:
            self.status.set('Geste trop long : corrigez-le avant de dessiner une autre zone.')
            return
        if self._draft_point_count() >= MAX_DRAFT_POINTS_TOTAL:
            self.status.set(
                f'{MAX_DRAFT_POINTS_TOTAL} points maximum : calculez ou retirez une zone.')
            return
        if self._draft_segment_count() >= MAX_DRAFT_STROKES:
            self.status.set(
                f'Limite de {MAX_DRAFT_STROKES} parties pour le calcul : '
                'calculez ou retirez une zone.')
            return
        if self._points and (self.mode.get() not in _MODES or self.radius.get() not in _RADII):
            self.status.set('Choisissez un mode et un rayon valides avant de continuer.')
            return
        self._variant = 'after'
        if self._points:
            # Freeze the previous gesture before starting another one. A
            # comparison must be recalculated for the expanded draft.
            self._result_images = None
            if not self.add_draft_zone():
                return
        self._verified_save_request = None
        self._token += 1  # invalidate any previous asynchronous reply
        self._busy = False
        self._result_images = None
        self._points = []
        self._redo_points = []
        self._overflow = False
        self._drag_active = True
        self.canvas.focus_set()
        self._append(event.x, event.y)

    def _drag(self, event):
        if getattr(self, '_drag_active', False):
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
        self._redo_points = []
        self._variant = 'after'
        self.status.set(
            'Réglages appliqués au prochain geste. Recalculez l’aperçu.'
            if self._points and getattr(self, '_stroke_style', None) is not None
            else 'Pinceau modifié : recalculez l’aperçu avant/après.')
        self._draw()
        self._controls()

    def _release(self, _event):
        # A queued release can arrive after the parent Tk widget was destroyed.
        if not self._closed:
            self._drag_active = False
            self._controls()

    def undo_draft_point(self):
        """Remove one uncommitted point and invalidate every older preview proof."""
        if (self._closed or self._identity is None or self._busy or
                self._save_pending or self._result_images is not None or
                not self._points):
            return False
        self._token += 1
        self._redo_points.append(self._points.pop())
        self._overflow = False
        self._verified_save_request = None
        self._inflight_request = None
        self._variant = 'after'
        count = len(self._points)
        self.status.set(
            f'{count} point(s) · dernier point annulé · brouillon non enregistré.')
        self._draw()
        self._controls()
        return True

    def _undo_draft_key(self, _event=None):
        return 'break' if (self.undo_draft_point() or
                           self.remove_last_draft_zone()) else None

    def redo_draft_point(self):
        """Restore one locally undone point without touching persisted history."""
        if (self._closed or self._identity is None or self._busy or
                self._save_pending or self._result_images is not None or
                not self._redo_points or len(self._points) >= MAX_GESTURE_POINTS):
            return False
        segments, points = self._draft_budget(current_size=len(self._points) + 1)
        if segments > MAX_DRAFT_STROKES or points > MAX_DRAFT_POINTS_TOTAL:
            self.status.set(
                f'Limite de {MAX_DRAFT_POINTS_TOTAL} points ou '
                f'{MAX_DRAFT_STROKES} parties pour le calcul.')
            return False
        self._token += 1
        self._points.append(self._redo_points.pop())
        self._overflow = False
        self._verified_save_request = None
        self._inflight_request = None
        self._variant = 'after'
        count = len(self._points)
        self.status.set(
            f'{count} point(s) · point rétabli · brouillon non enregistré.')
        self._draw()
        self._controls()
        return True

    def _redo_draft_key(self, _event=None):
        return 'break' if (self.redo_draft_point() or
                           self.restore_last_draft_zone()) else None

    @staticmethod
    def _segment_cost(size):
        if size <= 0:
            return 0, 0
        segments = 1 + max(0, (size - 2) // (MAX_GESTURE_SEGMENT_POINTS - 1))
        return segments, size + segments - 1

    def _draft_budget(self, *, current_size=None):
        sizes = [len(stroke['points']) for stroke in self._strokes]
        sizes.append(len(self._points) if current_size is None else current_size)
        costs = [self._segment_cost(size) for size in sizes]
        return sum(cost[0] for cost in costs), sum(cost[1] for cost in costs)

    def _draft_point_count(self):
        return self._draft_budget()[1]

    def _draft_segment_count(self):
        return self._draft_budget()[0]

    def _current_stroke_style(self):
        style = getattr(self, '_stroke_style', None)
        return style if style is not None else (
            _MODES[self.mode.get()], float(self.radius.get()))

    def _draft_strokes(self):
        strokes = [{
            'mode': stroke['mode'], 'radius': stroke['radius'],
            'points': [point[:] for point in stroke['points']],
        } for stroke in self._strokes]
        if self._points:
            mode, radius = self._current_stroke_style()
            strokes.append({
                'mode': mode,
                'radius': radius,
                'points': [point[:] for point in self._points],
            })
        # The engine accepts at most 64 points per segment. Split a longer
        # logical gesture at shared endpoints so no line segment is lost.
        # Adjacent segments remain in one confirmed grouped history command.
        split = []
        for stroke in strokes:
            points = stroke['points']
            start = 0
            while start < len(points):
                part = points[start:start + MAX_GESTURE_SEGMENT_POINTS]
                split.append({**stroke, 'points': part})
                if start + MAX_GESTURE_SEGMENT_POINTS >= len(points):
                    break
                start += MAX_GESTURE_SEGMENT_POINTS - 1
        return split

    @staticmethod
    def _freeze_strokes(strokes):
        return tuple((stroke['mode'], stroke['radius'],
                      tuple(tuple(point) for point in stroke['points']))
                     for stroke in strokes)

    def _bound_request(self, strokes):
        frozen = self._freeze_strokes(strokes)
        identity = self._identity or getattr(self, '_recovery_identity', None)
        if not self._strokes and len(strokes) == 1:
            mode, radius, points = frozen[0]
            return identity, mode, radius, points
        return identity, 'draft', len(strokes) > 1, frozen

    @staticmethod
    def _bound_strokes(bound):
        frozen = ((bound[1], bound[2], bound[3]),) if bound[1] != 'draft' else bound[3]
        return [{'mode': mode, 'radius': radius,
                 'points': [list(point) for point in points]}
                for mode, radius, points in frozen]

    def _bound_matches(self, bound):
        identity = self._identity or getattr(self, '_recovery_identity', None)
        if identity is None or bound[0] != identity:
            return False
        try:
            return self._freeze_strokes(self._draft_strokes()) == self._freeze_strokes(
                self._bound_strokes(bound))
        except (KeyError, TypeError, ValueError):
            return False

    def add_draft_zone(self):
        """Freeze the current local stroke and open a fresh editable zone."""
        if (self._closed or self._identity is None or self._busy or
                self._save_pending or self._result_images is not None or
                not self._points or self._overflow):
            return False
        if (self._draft_point_count() > MAX_DRAFT_POINTS_TOTAL or
                self._draft_segment_count() > MAX_DRAFT_STROKES):
            self.status.set(
                f'Limite de {MAX_DRAFT_POINTS_TOTAL} points ou '
                f'{MAX_DRAFT_STROKES} parties pour le calcul.')
            return False
        if len(self._strokes) >= MAX_DRAFT_STROKES:
            self.status.set(
                f'{MAX_DRAFT_STROKES} zones maximum : calculez ou effacez le brouillon.')
            self._controls()
            return False
        if self.mode.get() not in _MODES or self.radius.get() not in _RADII:
            self.status.set('Mode ou rayon invalide : zone non ajoutée.')
            self._controls()
            return False
        self._strokes.append({
            'mode': self._current_stroke_style()[0],
            'radius': self._current_stroke_style()[1],
            'points': [point[:] for point in self._points],
        })
        self._points = []
        self._stroke_style = None
        self._redo_points = []
        self._redo_strokes = []
        self._token += 1
        self._verified_save_request = None
        self._inflight_request = None
        self.status.set(
            f'{len(self._strokes)} zone(s) prete(s) - dessinez la suivante ou calculez.')
        self._draw()
        self._controls()
        return True

    def remove_last_draft_zone(self):
        """Remove one frozen local zone; persisted history remains untouched."""
        if (self._closed or self._identity is None or self._busy or
                self._save_pending or self._result_images is not None or
                self._points or self._redo_points or not self._strokes):
            return False
        stroke = self._strokes.pop()
        self._redo_strokes.append({
            'mode': stroke['mode'], 'radius': stroke['radius'],
            'points': [point[:] for point in stroke['points']],
        })
        self._token += 1
        self._verified_save_request = None
        self._inflight_request = None
        self.status.set(
            f'{len(self._strokes)} zone(s) prete(s) - derniere zone retiree.')
        self._draw()
        self._controls()
        return True

    def restore_last_draft_zone(self):
        """Restore one locally removed zone without touching project history."""
        if (self._closed or self._identity is None or self._busy or
                self._save_pending or self._result_images is not None or
                self._points or self._redo_points or not self._redo_strokes or
                len(self._strokes) >= MAX_DRAFT_STROKES):
            return False
        added_segments, added_points = self._segment_cost(len(self._redo_strokes[-1]['points']))
        if (self._draft_point_count() + added_points > MAX_DRAFT_POINTS_TOTAL or
                self._draft_segment_count() + added_segments > MAX_DRAFT_STROKES):
            self.status.set(
                f'Limite de {MAX_DRAFT_POINTS_TOTAL} points ou '
                f'{MAX_DRAFT_STROKES} parties pour le calcul.')
            return False
        stroke = self._redo_strokes.pop()
        self._strokes.append({
            'mode': stroke['mode'], 'radius': stroke['radius'],
            'points': [point[:] for point in stroke['points']],
        })
        self._token += 1
        self._verified_save_request = None
        self._inflight_request = None
        self.status.set(
            f'{len(self._strokes)} zone(s) prete(s) - zone retablie.')
        self._draw()
        self._controls()
        return True

    def preview(self):
        identity = self._identity or getattr(self, '_recovery_identity', None)
        if (self._closed or identity is None or not (self._points or self._strokes)
                or self._overflow or self._busy or self._save_pending or
                self.mode.get() not in _MODES or self.radius.get() not in _RADII):
            return False
        if (self._draft_point_count() > MAX_DRAFT_POINTS_TOTAL or
                self._draft_segment_count() > MAX_DRAFT_STROKES):
            self.status.set(
                f'Limite de {MAX_DRAFT_POINTS_TOTAL} points ou '
                f'{MAX_DRAFT_STROKES} parties pour le calcul.')
            self._controls()
            return False
        project_path, expected_sha256, subject_id = identity
        strokes = self._draft_strokes()
        payload = {
            'project_path': project_path, 'expected_sha256': expected_sha256,
            'subject_id': subject_id, 'strokes': strokes,
        }
        self._verified_save_request = None
        # Pin exactly the gesture submitted to the CPU worker. No later UI
        # event may promote a different gesture to a saveable preview.
        self._inflight_request = self._bound_request(strokes)
        self._token += 1
        token = self._token
        self._busy = True
        self._controls()
        self.status.set('Vérification du projet et recalcul en lecture seule…'
                        if self._identity is None else
                        'Calcul de la retouche en lecture seule…')
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
            if bound is None or not self._bound_matches(bound):
                raise ValueError('STALE_STROKE')
            result = future.result()
            if (result['subject_id'] != bound[0][2] or
                    result['project_sha256'] != bound[0][1] or
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
                self.status.set('Projet modifié : brouillon conservé. Réexaminez-le (F5).')
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
        if self._identity is None:
            # Only an exact-revision, subject-bound read-only preview can
            # restore write eligibility after an uncertain save. The writer
            # still performs CAS and requires a new explicit confirmation.
            self._identity = self._recovery_identity
            self._recovery_identity = None
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
        if token != self._token or not self._bound_matches(bound):
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
        strokes = self._bound_strokes(bound)
        try:
            request = dict(
                project_path=project_path, expected_sha256=revision,
                subject_id=subject_id,
                expected_preview_mask_sha256_float32=digest,
                command_id='native-' + uuid4().hex, confirmed=True)
            if len(strokes) == 1:
                result = self._save_fn(**request, **strokes[0])
                statuses = ('subject_brush_saved', 'subject_brush_already_saved')
            else:
                result = self._save_many_fn(**request, strokes=strokes)
                statuses = ('subject_brushes_saved', 'subject_brushes_already_saved')
            if (type(result) is not dict or
                    result.get('persisted') is not True or
                    result.get('subject_id') != subject_id or
                    result.get('status') not in statuses or
                    type(result.get('project_sha256')) is not str or
                    not _SHA.fullmatch(result['project_sha256'])):
                raise ValueError('UNCERTAIN_SAVE_RECEIPT')
        except Exception as exc:
            # A failed receipt is NOT evidence that the archive was unchanged.
            # Invalidate authority and proof, but keep the local draft visible
            # until the user explicitly chooses to abandon it. Never retry a
            # possibly committed command against an unverified revision.
            self._token += 1
            self._verified_save_request = None
            self._result_images = None
            self._recovery_identity = bound[0]
            self._identity = None
            self._variant = 'after'
            self._save_pending = False
            code = getattr(exc, 'code', '')
            self.status.set(
                'Projet modifié ailleurs. Brouillon conservé ; réexaminez-le (F5).' if
                code == 'PROJECT_CHANGED' else
                'Enregistrement non confirmé. Brouillon conservé ; vérifiez et '
                'recalculez, ou réexaminez le projet (F5).')
            if not self._closed:
                self._draw()
                self._controls()
            return False
        # Invalidate this entire panel, including any pending CPU result.
        self._token += 1
        self._verified_save_request = None
        self._result_images = None
        self._identity = None
        self._recovery_identity = None
        self._points = []
        self._stroke_style = None
        self._strokes = []
        self._redo_points = []
        self._redo_strokes = []
        self._overflow = False
        self._drag_active = False
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

    @property
    def has_draft(self):
        return bool(self._points or self._strokes or
                    self._redo_points or self._redo_strokes)

    def _discard_draft_key(self, _event=None):
        # Escape cancels the current gesture only. Earlier completed zones and
        # their redo history remain part of the local, uncommitted draft.
        if (self._closed or self._save_pending or
                not getattr(self, '_drag_active', False) or
                not (self._points or self._redo_points)):
            return None
        self._token += 1
        self._busy = False
        self._points = []
        self._stroke_style = None
        self._redo_points = []
        self._overflow = False
        self._drag_active = False
        self._result_images = None
        self._verified_save_request = None
        self._inflight_request = None
        self._variant = 'after'
        self.status.set('Geste annulé. Les autres zones du brouillon sont conservées.')
        self._draw()
        self._controls()
        return 'break'

    def request_discard(self):
        """Ask before the UI irreversibly discards all local gesture history."""
        if (self._closed or self._save_pending or not self.has_draft or
                getattr(self, '_discard_confirming', False)):
            return False
        from tkinter import messagebox

        token = self._token
        draft = deepcopy((self._points, self._strokes,
                          self._redo_points, self._redo_strokes))
        self._discard_confirming = True
        try:
            accepted = messagebox.askyesno(
                'Effacer le brouillon ?',
                'Effacer toutes les zones et leur historique local ?',
                detail='Cette action ne peut pas être annulée. Si le dernier '
                       'enregistrement est incertain, vérifiez aussi le projet.',
                parent=self.root, default='no')
        except Exception:
            return False
        finally:
            self._discard_confirming = False
        # A modal Tk dialog can dispatch nested callbacks. Never discard work
        # that changed while the user was answering about an older draft.
        if accepted is not True or self._closed or self._save_pending:
            return False
        if token != self._token or draft != (
                self._points, self._strokes, self._redo_points, self._redo_strokes):
            self.status.set('Brouillon modifié pendant la confirmation : rien n’a été effacé.')
            return False
        return self.discard()

    def discard(self):
        if self._closed or self._save_pending:
            return False
        uncertain = getattr(self, '_recovery_identity', None) is not None
        self._token += 1
        self._busy = False
        self._points = []
        self._stroke_style = None
        self._strokes = []
        self._redo_points = []
        self._redo_strokes = []
        self._overflow = False
        self._drag_active = False
        self._result_images = None
        self._verified_save_request = None
        self._inflight_request = None
        self._variant = 'after'
        self._recovery_identity = None
        self.status.set('Brouillon abandonné. Vérifiez l’enregistrement du projet (F5).'
                        if uncertain else
                        'Brouillon abandonné. Le projet n’a pas été modifié.')
        self._draw()
        self._controls()
        return True

    def shutdown(self):
        if not self._closed:
            self._closed = True
            self._token += 1
            self._inflight_request = None
            self._verified_save_request = None
            self._job.close()
