"""Durable brush Undo/Redo over native V21.6 strokes and the existing journal.

Base float32 resources never change: removing/reinstating a saved command
changes only its native replay session. No second history store or PNG inverse.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json
import re

from .editor_session_g23 import parse_editor_document, EditorSessionError
from .mask_binding_g33e import snapshot_mask_bindings
from .mask_snapshot_g24 import SNAPSHOT_KEY
from .project_archive import _payload

SAVE_KINDS=frozenset(('save_subject_brush_g33e_b2b1','save_subject_brush_g33e_b2b2',
                      'save_subject_brush_g33e_b2b3'))
HISTORY_KIND='subject_brush_history_g33e_v1'
_SHA=re.compile(r'^[0-9a-f]{64}$')


class BrushHistoryError(ValueError):
    def __init__(self,code):
        self.code=code
        super().__init__(code)


def editor_digest(session):
    return sha256(json.dumps(session,allow_nan=False,sort_keys=True,
                             separators=(',',':')).encode()).hexdigest()


def logical_digest(project):
    return sha256(_payload(project)['manifest.json']).hexdigest()


def _session(project):
    if 'editor_v216' not in project.document:
        return None
    try:
        if len(project.sources)!=1:
            raise ValueError('one source required')
        src=project.sources[0]
        doc,_=parse_editor_document(json.dumps(project.document['editor_v216'],
            allow_nan=False,separators=(',',':')),source_dimensions=(src.width_px,src.height_px))
        snapshot=project.document[SNAPSHOT_KEY]
        if doc['source']!=snapshot['editor_fingerprint'] or doc['count']!=snapshot['shape'][0]:
            raise ValueError('source mismatch')
        return doc
    except (KeyError,TypeError,ValueError,OverflowError,RecursionError) as exc:
        raise BrushHistoryError('INVALID_SAVED_EDITOR_SESSION') from exc


def _journal(project):
    """Reconstruct command stacks. Native editor imports form a new boundary."""
    undo,redo=[],[]
    expected=None
    ids=set()
    for index,op in enumerate(project.operations):
        if type(op) is not dict:
            raise BrushHistoryError('INVALID_BRUSH_HISTORY')
        kind=op.get('kind')
        if type(kind) is not str:
            raise BrushHistoryError('INVALID_BRUSH_HISTORY')
        if kind in SAVE_KINDS or kind==HISTORY_KIND:
            command_id=op.get('command_id')
            if type(command_id) is not str or command_id in ids:
                raise BrushHistoryError('INVALID_BRUSH_HISTORY')
            ids.add(command_id)
        if kind in SAVE_KINDS:
            if kind=='save_subject_brush_g33e_b2b1':
                # This earliest receipt does not say whether an empty editor
                # existed before the command. Keep its audit, do not invent Undo.
                undo.clear();redo.clear();expected=editor_digest(op.get('editor_v216'))
                continue
            digest=op.get('editor_sha256')
            if (type(digest) is not str or not _SHA.fullmatch(digest) or
                    type(op.get('stroke')) is not dict or
                    type(op.get('previous_editor_present')) is not bool):
                raise BrushHistoryError('INVALID_BRUSH_HISTORY')
            if kind=='save_subject_brush_g33e_b2b3':
                previous=op.get('previous_editor_sha256')
                if type(previous) is not str or not _SHA.fullmatch(previous):
                    raise BrushHistoryError('INVALID_BRUSH_HISTORY')
                if expected is not None and previous!=expected:
                    # A writer outside this journal supplied a new native
                    # baseline. Only commands after that baseline can be undone.
                    undo.clear();redo.clear()
            undo.append((index,op));redo.clear();expected=digest
        elif kind==HISTORY_KIND:
            action=op.get('action')
            source,destination=(undo,redo) if action=='undo' else (redo,undo)
            if (action not in ('undo','redo') or not source or
                    source[-1][1]['command_id']!=op.get('target_command_id') or
                    type(op.get('editor_sha256')) is not str or
                    not _SHA.fullmatch(op['editor_sha256'])):
                raise BrushHistoryError('INVALID_BRUSH_HISTORY')
            destination.append(source.pop());expected=op['editor_sha256']
        elif kind in ('save_editor_v216','capture_base_masks_float32_v1'):
            undo.clear();redo.clear();expected=None
    session=_session(project)
    if expected is not None and editor_digest(session)!=expected:
        raise BrushHistoryError('BRUSH_HISTORY_CHANGED')
    return session,undo,redo


def plan_history_change(project,action):
    """Return a verified native document and target receipt; no I/O or mutation."""
    if action not in ('undo','redo'):
        raise BrushHistoryError('INVALID_BRUSH_HISTORY_REQUEST')
    session,undo,redo=_journal(project)
    stack=undo if action=='undo' else redo
    if not stack:
        raise BrushHistoryError('BRUSH_NOTHING_TO_'+action.upper())
    index,target=stack[-1]
    try:
        snapshot=project.document[SNAPSHOT_KEY]
        catalog=snapshot_mask_bindings(project)
        bindings=[item for item in catalog['bindings']
                  if item['subject_id']==target.get('subject_id')]
        if (catalog['subject_proof_schema_valid'] is not True or len(bindings)!=1 or
                bindings[0]['subject_proof_status']!='verified' or
                bindings[0]['subject_ambiguous'] is not False or
                bindings[0]['mask_id']!=target.get('mask_id') or
                target['stroke'].get('object')!=bindings[0]['mask_index']):
            raise ValueError('proof mismatch')
        if target['kind']=='save_subject_brush_g33e_b2b3':
            if (snapshot['sha256_raw']!=target.get('base_snapshot_sha256') or
                    snapshot['editor_fingerprint']!=target.get('source_sha256') or
                    bindings[0]['mask_sha256_float32']!=target.get('base_mask_sha256_float32')):
                raise ValueError('base changed')
    except (KeyError,TypeError,ValueError,IndexError) as exc:
        raise BrushHistoryError('BRUSH_HISTORY_SOURCE_CHANGED') from exc
    count,height,width=snapshot['shape']
    template=dict(version=1,width=width,height=height,count=count,
                  source=snapshot['editor_fingerprint'],strokes=[])
    try:
        parse_editor_document(json.dumps({**template,'strokes':[target['stroke']]},
            allow_nan=False,separators=(',',':')),source_dimensions=(width,height))
    except (EditorSessionError,TypeError,ValueError,OverflowError,RecursionError) as exc:
        raise BrushHistoryError('INVALID_BRUSH_HISTORY') from exc
    if action=='undo':
        if session is None or not session['strokes'] or session['strokes'][-1]!=target['stroke']:
            raise BrushHistoryError('BRUSH_HISTORY_CHANGED')
        next_session={**session,'strokes':session['strokes'][:-1]}
        if not next_session['strokes'] and target['previous_editor_present'] is False:
            next_session=None
    else:
        next_session={**(session or template),'strokes':[
            *(session or template)['strokes'],target['stroke']]}
    try:
        if next_session is not None:
            next_session,_=parse_editor_document(json.dumps(next_session,allow_nan=False,
                separators=(',',':')),source_dimensions=(width,height))
    except (EditorSessionError,TypeError,ValueError,OverflowError,RecursionError) as exc:
        raise BrushHistoryError('INVALID_BRUSH_HISTORY') from exc
    expected=target.get('previous_editor_sha256') if action=='undo' else target['editor_sha256']
    if expected is not None and editor_digest(next_session)!=expected:
        raise BrushHistoryError('BRUSH_HISTORY_CHANGED')
    document={**project.document}
    if next_session is None:
        document.pop('editor_v216',None)
    else:
        document['editor_v216']=next_session
    if target['kind']=='save_subject_brush_g33e_b2b2':
        # Older compact receipts have no base-context fields. Qualify them
        # against their original full logical state before allowing reversal.
        after_document=project.document if action=='undo' else document
        if logical_digest(replace(project,document=after_document,
                                  operations=project.operations[:index]))!=target.get('result_state_sha256'):
            raise BrushHistoryError('BRUSH_HISTORY_CHANGED')
    return document,target
