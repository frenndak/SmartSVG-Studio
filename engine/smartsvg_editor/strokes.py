"""Deterministic, bounded raster replay of portable, normalized brush strokes.

A saved correction is a JSON widget in the ComfyUI workflow, NOT a hidden
server-side mask. It is pinned to original image dimensions and RGB checksum.
Values are aggressively validated before allocating stroke buffers.
"""
from __future__ import annotations
import hashlib
import json
import math
import numpy as np
from PIL import Image, ImageDraw

MAX_DOCUMENT_BYTES = 350_000
MAX_STROKES = 400
MAX_POINTS_PER_STROKE = 1500
MAX_POINTS_TOTAL = 12000
MAX_INSTANCES = 32
MAX_PIXELS = 5_000_000
MAX_TOTAL_MASK_PIXELS = 50_000_000


class StrokeError(ValueError):
    """User-facing correction/geometry mismatch, never silently ignored."""


def source_fingerprint(rgb):
    """Digest of the actual image pixels before edits; only 8-bit normalized RGB."""
    a = np.asarray(rgb)
    if a.ndim != 3 or a.shape[-1] not in (3, 4):
        raise StrokeError('IMAGE RGB/RGBA attendue')
    if a.shape[0] < 1 or a.shape[1] < 1 or a.shape[0] * a.shape[1] > MAX_PIXELS:
        raise StrokeError('Image trop grande pour la retouche (5 Mp maximum)')
    if not np.isfinite(a).all() or np.min(a) < -0.001 or np.max(a) > 1.001:
        raise StrokeError('IMAGE : couleurs hors de 0..1 ou non finies')
    # Include alpha if present: changing transparent boundaries is a source change.
    b = np.ascontiguousarray(np.rint(np.clip(a, 0, 1) * 255).astype(np.uint8))
    return hashlib.sha256(bytes([a.shape[-1]]) + b.tobytes()).hexdigest()


def edit_fingerprint(rgb, masks):
    """Pin a replay to both source pixels and the actual input segmentation.

    An alpha-only edit through ComfyUI's LoadImage is caught through the MASK,
    even if Comfy's IMAGE tensor contains only RGB. Preserve exact base masks
    to guarantee identical pixel output on replay.
    """
    b=np.ascontiguousarray(np.asarray(masks,dtype=np.float32))
    if b.ndim!=3 or b.shape[0]<1 or b.size>MAX_TOTAL_MASK_PIXELS:
        raise StrokeError('Masques source invalides pour empreinte')
    m=hashlib.sha256()
    m.update(source_fingerprint(rgb).encode('ascii'))
    m.update(str(tuple(b.shape)).encode('ascii'))
    m.update(memoryview(b).cast('B'))
    return m.hexdigest()


def _number(v, label, lower=0.0, upper=1.0):
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not lower <= v <= upper:
        raise StrokeError(f'Correction invalide : {label}')
    return float(v)


def decode(document, *, width, height, count, fingerprint):
    """Exact versioned schema. Empty string is an empty edit set.

    Unknown keys disallowed to make corrections portable and unambiguous.
    Geometry/image checks block applying edits to a different drawing.
    """
    if not isinstance(document, str) or len(document.encode('utf-8')) > MAX_DOCUMENT_BYTES:
        raise StrokeError('JSON de retouches trop volumineux (350 Ko maximum)')
    if not document.strip():
        return []
    try:
        doc = json.loads(document, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
    except (ValueError, TypeError) as exc:
        raise StrokeError('JSON de retouches illisible') from exc
    if not isinstance(doc, dict) or set(doc) != {'version','width','height','count','source','strokes'} or type(doc['version']) is not int or doc['version'] != 1:
        raise StrokeError('Format de corrections incompatible : schéma V21.6 requis')
    if any(type(doc[k]) is not int for k in ('width','height','count')):
        raise StrokeError('Dimensions des corrections invalides')
    if (doc['width'], doc['height'], doc['count']) != (width, height, count) or doc['source'] != fingerprint:
        raise StrokeError('Image ou dimensions modifiées : effacer/recréer les retouches avant de poursuivre')
    raw = doc['strokes']
    if not isinstance(raw, list) or len(raw) > MAX_STROKES:
        raise StrokeError('Trop de traits de pinceau (400 maximum)')
    result = []
    points_seen = 0
    for s in raw:
        if not isinstance(s, dict) or set(s) != {'object','mode','radius','points'}:
            raise StrokeError('Trait de pinceau mal formé')
        obj = s['object']
        if type(obj) is not int or not 0 <= obj < count:
            raise StrokeError('Numéro de masque hors limites')
        if s['mode'] not in ('add', 'erase'):
            raise StrokeError('Mode de pinceau inconnu')
        radius = _number(s['radius'], 'rayon', 0.0005, 0.2)
        pts = s['points']
        if not isinstance(pts, list) or not 1 <= len(pts) <= MAX_POINTS_PER_STROKE:
            raise StrokeError('Nombre de points invalide (1..1500)')
        points_seen += len(pts)
        if points_seen > MAX_POINTS_TOTAL:
            raise StrokeError('Trop de points de dessin (12000 maximum)')
        points=[]
        for p in pts:
            if not isinstance(p,list) or len(p)!=2:
                raise StrokeError('Coordonnées de pinceau invalides')
            points.append((_number(p[0],'x'),_number(p[1],'y')))
        result.append({'object':obj,'mode':s['mode'],'radius':radius,'points':points})
    return result


def apply_strokes(base_masks, strokes):
    """Float masks [N,H,W] -> corrected copy, retaining untouched soft values.

    Last stroke wins; raster alpha is binary for manually painted areas.
    Back-end draws onto the original resolution, not the preview resolution.
    """
    base = np.asarray(base_masks)
    if base.ndim!=3 or base.shape[0]<1 or base.shape[0]>MAX_INSTANCES or base.shape[1]*base.shape[2]>MAX_PIXELS or base.size>MAX_TOTAL_MASK_PIXELS:
        raise StrokeError('Masques attendus [1..32,H,W], <= 5 Mp par sujet et <= 50 millions de pixels au total')
    if not np.isfinite(base).all() or base.min()<-.001 or base.max()>1.001:
        raise StrokeError('Masques invalides : valeurs hors de 0..1')
    result = np.ascontiguousarray(base,dtype=np.float32).copy()
    n,h,w = result.shape
    per_object={}
    for stroke in strokes:
        per_object.setdefault(stroke['object'],[]).append(stroke)
    for index,group in per_object.items():
        # One overlay per object; a byte per pixel, not one full mask per stroke.
        overlay=Image.new('L',(w,h),0)
        painter=ImageDraw.Draw(overlay)
        for stroke in group:
            val = 1 if stroke['mode']=='add' else 2
            r = max(1,round(stroke['radius']*min(w,h)))
            pixel_pts=[(round(x*(w-1)), round(y*(h-1))) for x,y in stroke['points']]
            if len(pixel_pts)>1:
                painter.line(pixel_pts,fill=val,width=2*r)
            for x,y in pixel_pts:
                painter.ellipse((x-r,y-r,x+r,y+r),fill=val)
        values=np.asarray(overlay)
        result[index][values==1]=1.0
        result[index][values==2]=0.0
    return result
