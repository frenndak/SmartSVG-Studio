"""Read-only native V1 brush Undo/Redo availability; no second history writer.

This is a future Atelier UI boundary, not an Undo/Redo button or operation.
It reuses the existing ManagedWorkspace journal and refuses untrusted or
stale revisions. Return only bounded status metadata, never editor pixels.
"""
from __future__ import annotations

import re

from .native_subject_preview_v34 import (
    NativeSubjectPreviewError, _SHA, _SUBJECT, _workspace_from_path,
)
from .project_workspace_g22 import WorkspaceError


_ERROR = re.compile(r"^[A-Z][A-Z0-9_]{0,79}$")


def inspect_native_brush_history(*, project_path, expected_sha256):
    """Inspect Undo/Redo for exactly one healthy managed V1 project revision.

    A caller must refresh after an archive save or external change. This
    function never attempts replay, journal mutation or implicit recovery.
    Neither a caller-provided mask index nor an editor document is accepted.
    """
    if type(expected_sha256) is not str or not _SHA.fullmatch(expected_sha256):
        raise NativeSubjectPreviewError("EXPECTED_REVISION_REQUIRED")

    workspace, name = _workspace_from_path(project_path)
    try:
        record = workspace.subject_brush_history(
            name, expected_sha256=expected_sha256)
    except WorkspaceError as exc:
        raise NativeSubjectPreviewError(exc.code) from exc
    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        raise NativeSubjectPreviewError("BRUSH_HISTORY_UNAVAILABLE") from exc

    if (type(record) is not dict or record.get("name") != name
            or record.get("project_sha256") != expected_sha256
            or record.get("cricut_certified") is not False):
        raise NativeSubjectPreviewError("INVALID_BRUSH_HISTORY_STATUS")

    out = {
        "schema": "smartsvg-native-brush-history-status/1",
        "project_sha256": expected_sha256,
        "undo_available": False,
        "redo_available": False,
        "persisted": False,
        "cricut_certified": False,
    }
    for action in ("undo", "redo"):
        available = record.get(action + "_available")
        if type(available) is not bool:
            raise NativeSubjectPreviewError("INVALID_BRUSH_HISTORY_STATUS")
        out[action + "_available"] = available
        if available:
            subject_id = record.get(action + "_subject_id")
            if type(subject_id) is not str or not _SUBJECT.fullmatch(subject_id):
                raise NativeSubjectPreviewError("INVALID_BRUSH_HISTORY_STATUS")
            out[action + "_subject_id"] = subject_id
        else:
            code = record.get(action + "_error_code")
            if type(code) is not str or not _ERROR.fullmatch(code):
                raise NativeSubjectPreviewError("INVALID_BRUSH_HISTORY_STATUS")
            out[action + "_reason"] = code
    return out
