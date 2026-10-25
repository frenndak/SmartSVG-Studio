"""G2.3: strict contract for native SmartSVGMaskEditorV216 brush sessions.

A stroke session is only applicable to the *same* V21.6 source-plus-base-mask
fingerprint. This module does not claim to persist full-resolution base masks.
"""
from __future__ import annotations

import json
import math
import re

HEX_SHA=re.compile(r'^[0-9a-f]{64}$')
MAX_BYTES=350000
MAX_STROKES=400
MAX_POINTS_PER_STROKE=1500
MAX_POINTS_TOTAL=12000


class EditorSessionError(ValueError):
    def __init__(self, code):
        self.code=code
        super().__init__(code)


def _unique_pairs(items):
    result={}
    for key,value in items:
        if key in result:
            raise EditorSessionError('DUPLICATE_EDITOR_FIELD')
        result[key]=value
    return result


def _reject_constant(_):
    raise EditorSessionError('INVALID_EDITOR_NUMBER')


def _number(value,low,high):
    return type(value) in (int,float) and math.isfinite(value) and low <= value <= high


def parse_editor_document(value, *, source_dimensions):
    """Validate the V21.6 JSON document without reinterpretation of brush ops."""
    if type(value) is not str or len(value.encode('utf-8')) > MAX_BYTES:
        raise EditorSessionError('INVALID_EDITOR_SIZE')
    try:
        doc=json.loads(value,object_pairs_hook=_unique_pairs,parse_constant=_reject_constant)
    except (ValueError,TypeError,RecursionError) as exc:
        if isinstance(exc,EditorSessionError):
            raise
        raise EditorSessionError('INVALID_EDITOR_JSON') from exc
    if not isinstance(doc,dict) or set(doc)!={'version','width','height','count','source','strokes'}:
        raise EditorSessionError('INVALID_EDITOR_SCHEMA')
    width,height=source_dimensions
    if (type(doc['version']) is not int or doc['version']!=1 or
        type(doc['width']) is not int or doc['width']!=width or
        type(doc['height']) is not int or doc['height']!=height or
        type(doc['count']) is not int or not 1<=doc['count']<=32 or
        width*height>5_000_000 or
        not isinstance(doc['source'],str) or not HEX_SHA.fullmatch(doc['source'])):
        raise EditorSessionError('INCOMPATIBLE_EDITOR_SOURCE')
    strokes=doc['strokes']
    if not isinstance(strokes,list) or len(strokes)>MAX_STROKES:
        raise EditorSessionError('INVALID_EDITOR_STROKES')
    points_total=0
    for stroke in strokes:
        if not isinstance(stroke,dict) or set(stroke)!={'object','mode','radius','points'}:
            raise EditorSessionError('INVALID_EDITOR_STROKE')
        if (type(stroke['object']) is not int or not 0<=stroke['object']<doc['count'] or
            stroke['mode'] not in ('add','erase') or
            not _number(stroke['radius'],0.0005,0.2) or
            not isinstance(stroke['points'],list) or
            not 1<=len(stroke['points'])<=MAX_POINTS_PER_STROKE):
            raise EditorSessionError('INVALID_EDITOR_STROKE')
        points_total+=len(stroke['points'])
        if points_total>MAX_POINTS_TOTAL:
            raise EditorSessionError('TOO_MANY_EDITOR_POINTS')
        for point in stroke['points']:
            if not isinstance(point,list) or len(point)!=2 or not all(
                _number(coordinate,0,1) for coordinate in point
            ):
                raise EditorSessionError('INVALID_EDITOR_POINT')
    # Round-trip canonical content; the GUI still checks its own source
    # fingerprint (image + base masks) on apply, not just PNG dimensions.
    canonical=json.dumps(doc,ensure_ascii=False,allow_nan=False,
                         sort_keys=True,separators=(',',':'))
    if len(canonical.encode('utf-8'))>MAX_BYTES:
        raise EditorSessionError('INVALID_EDITOR_SIZE')
    return doc,canonical
