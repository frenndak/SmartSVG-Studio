"""Confirmed native Undo/Redo port over the existing G3.3e history writer.

This is a command boundary, not a Tk control or a second history engine.
The caller pins the project revision AND the subject named in its confirmed
action. A stale retry is refused: reinspection is required after uncertainty.
"""
from __future__ import annotations

import re

from .native_subject_preview_v34 import (
    NativeSubjectPreviewError, _SHA, _SUBJECT, _workspace_from_path,
)
from .project_workspace_g22 import WorkspaceError

_COMMAND = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$')
_ERROR = re.compile(r'^[A-Z][A-Z0-9_]{0,79}$')


def change_native_brush_history(
    *, project_path, expected_sha256, subject_id, action, command_id,
    confirmed=False,
):
    """Apply one explicit action, then verify its receipt against readback.

    Availability comes from the historical workspace, not a UI stack, mask
    index or caller-supplied editor document. The existing writer alone owns
    CAS, journal, recovery and immutable base resources. Errors after calling
    that writer must never be interpreted as evidence of rollback.
    """
    if confirmed is not True:
        raise NativeSubjectPreviewError('BRUSH_HISTORY_CONFIRMATION_REQUIRED')
    if type(expected_sha256) is not str or not _SHA.fullmatch(expected_sha256):
        raise NativeSubjectPreviewError('EXPECTED_REVISION_REQUIRED')
    if type(subject_id) is not str or not _SUBJECT.fullmatch(subject_id):
        raise NativeSubjectPreviewError('INVALID_SUBJECT_ID')
    if (type(action) is not str or action not in ('undo', 'redo') or
            type(command_id) is not str or not _COMMAND.fullmatch(command_id)):
        raise NativeSubjectPreviewError('INVALID_BRUSH_HISTORY_REQUEST')

    workspace, name = _workspace_from_path(project_path)
    try:
        record = workspace.subject_brush_history(name, expected_sha256=expected_sha256)
    except WorkspaceError as exc:
        raise NativeSubjectPreviewError(exc.code) from exc
    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        raise NativeSubjectPreviewError('BRUSH_HISTORY_UNAVAILABLE') from exc
    if (type(record) is not dict or record.get('name') != name or
            record.get('project_sha256') != expected_sha256 or
            record.get('cricut_certified') is not False or
            type(record.get(action + '_available')) is not bool):
        raise NativeSubjectPreviewError('INVALID_BRUSH_HISTORY_STATUS')
    if not record[action + '_available']:
        code = record.get(action + '_error_code')
        if type(code) is not str or not _ERROR.fullmatch(code):
            raise NativeSubjectPreviewError('INVALID_BRUSH_HISTORY_STATUS')
        raise NativeSubjectPreviewError(code)
    if record.get(action + '_subject_id') != subject_id:
        raise NativeSubjectPreviewError('BRUSH_HISTORY_SUBJECT_CHANGED')

    try:
        saved = workspace.change_subject_brush_history(
            name, expected_sha256=expected_sha256, action=action,
            command_id=command_id, confirmed=True)
    except WorkspaceError as exc:
        # The code is preserved for actionable recovery. It is not a claim
        # that the writer left the files untouched (e.g. backup interruption).
        raise NativeSubjectPreviewError(exc.code) from exc
    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        raise NativeSubjectPreviewError('BRUSH_HISTORY_OUTCOME_UNKNOWN') from exc
    if (type(saved) is not dict or saved.get('name') != name or
            saved.get('action') != action or saved.get('command_id') != command_id or
            saved.get('status') not in ('brush_history_' + action, 'brush_history_already_applied') or
            saved.get('persisted') is not True or saved.get('cricut_certified') is not False or
            type(saved.get('sha256')) is not str or not _SHA.fullmatch(saved['sha256']) or
            saved['sha256'] == expected_sha256):
        raise NativeSubjectPreviewError('BRUSH_HISTORY_OUTCOME_UNKNOWN')
    try:
        snapshot = workspace.inspect(name)
    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        raise NativeSubjectPreviewError('BRUSH_HISTORY_OUTCOME_UNKNOWN') from exc
    if (type(snapshot) is not dict or snapshot.get('status') != 'PROJECT_HEALTHY' or
            snapshot.get('sha256') != saved['sha256']):
        raise NativeSubjectPreviewError('BRUSH_HISTORY_OUTCOME_UNKNOWN')
    return {
        'status': saved['status'], 'project_sha256': saved['sha256'],
        'subject_id': subject_id, 'action': action, 'command_id': command_id,
        'persisted': True, 'cricut_certified': False,
    }
