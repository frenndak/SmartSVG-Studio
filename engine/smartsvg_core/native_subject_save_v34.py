"""Explicit native V1 Subject brush save, using the existing G3.3e writer.

This bridge never resolves a float32 tensor index from the UI, never writes
without a literal confirmation, and never accepts a preview from a different
project revision. It is deliberately separate from the read-only Tk draft:
the GUI save command must explicitly call this function in a future lot.
"""
from __future__ import annotations

import re

from .native_subject_preview_v34 import (
    NativeSubjectPreviewError, _SHA, _SUBJECT, _workspace_from_path,
    preview_native_subject_stroke,
)
from .project_workspace_g22 import WorkspaceError

_COMMAND = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")


def save_native_subject_stroke(
    *, project_path, expected_sha256, subject_id, mode, radius, points,
    expected_preview_mask_sha256_float32, command_id, confirmed=False,
):
    """Persist exactly a confirmed, revision-pinned V1 brush gesture.

    The input contains no mask ID/index/source digest. We re-create the
    genuine CPU preview before saving and resolve the subject's proven
    binding through ManagedWorkspace. Its existing save_subject_brush is
    the ONLY writer and checks CAS, preview digest, identity and backups.
    A stale retry intentionally fails closed; callers must reopen the project.
    """
    if confirmed is not True:
        raise NativeSubjectPreviewError("BRUSH_SAVE_CONFIRMATION_REQUIRED")
    if type(expected_sha256) is not str or not _SHA.fullmatch(expected_sha256):
        raise NativeSubjectPreviewError("EXPECTED_REVISION_REQUIRED")
    if type(subject_id) is not str or not _SUBJECT.fullmatch(subject_id):
        raise NativeSubjectPreviewError("INVALID_SUBJECT_ID")
    if (type(expected_preview_mask_sha256_float32) is not str or
            not _SHA.fullmatch(expected_preview_mask_sha256_float32) or
            type(command_id) is not str or not _COMMAND.fullmatch(command_id)):
        raise NativeSubjectPreviewError("INVALID_BRUSH_SAVE_REQUEST")

    workspace, name = _workspace_from_path(project_path)
    # The independent backend validates the CPU result and refuses stale V1.
    preview = preview_native_subject_stroke(
        project_path=project_path, expected_sha256=expected_sha256,
        subject_id=subject_id, mode=mode, radius=radius, points=points)
    if preview["preview_mask_sha256_float32"] != expected_preview_mask_sha256_float32:
        raise NativeSubjectPreviewError("BRUSH_PREVIEW_CHANGED")

    try:
        snapshot = workspace.inspect(name)
        if not isinstance(snapshot, dict) or snapshot.get("status") != "PROJECT_HEALTHY":
            raise NativeSubjectPreviewError("PROJECT_NOT_HEALTHY")
        if snapshot.get("sha256") != expected_sha256:
            raise NativeSubjectPreviewError("PROJECT_CHANGED")
        masks = snapshot.get("base_masks")
        if not isinstance(masks, dict):
            raise NativeSubjectPreviewError("NO_VERIFIED_MASKS")
        catalog = masks.get("mask_identity")
        if (not isinstance(catalog, dict) or
                catalog.get("subject_proof_schema_valid") is not True):
            raise NativeSubjectPreviewError("SUBJECT_NOT_VERIFIED")
        bindings = catalog.get("bindings")
        if (not isinstance(bindings, (list, tuple)) or
                any(type(row) is not dict for row in bindings)):
            raise NativeSubjectPreviewError("SUBJECT_NOT_VERIFIED")
        rows = [row for row in bindings if row.get("subject_id") == subject_id]
        if (len(rows) != 1 or rows[0].get("subject_proof_status") != "verified" or
                rows[0].get("subject_ambiguous") is not False or
                rows[0].get("has_foreground") is not True or
                rows[0].get("mask_id") != preview["mask_id"]):
            raise NativeSubjectPreviewError("SUBJECT_NOT_VERIFIED")
        row = rows[0]

        # This existing method is solely responsible for archive writes,
        # CAS, command receipts, backups and the G3.3e float32 replay.
        saved = workspace.save_subject_brush(
            name, expected_sha256=expected_sha256, subject_id=subject_id,
            mask_id=row["mask_id"],
            mask_sha256_float32=row["mask_sha256_float32"],
            source_id=catalog["source_id"],
            source_sha256=masks["editor_fingerprint"],
            mode=mode, radius=radius, points=points,
            expected_preview_mask_sha256_float32=expected_preview_mask_sha256_float32,
            command_id=command_id, confirmed=True,
        )
    except NativeSubjectPreviewError:
        raise
    except WorkspaceError as exc:
        raise NativeSubjectPreviewError(exc.code) from exc
    except (KeyError, TypeError, ValueError, OSError, RuntimeError) as exc:
        raise NativeSubjectPreviewError("BRUSH_SAVE_UNAVAILABLE") from exc

    if (not isinstance(saved, dict) or
            saved.get("status") not in ("subject_brush_saved",
                                        "subject_brush_already_saved") or
            saved.get("persisted") is not True or
            saved.get("cricut_certified") is not False or
            saved.get("command_id") != command_id or
            type(saved.get("sha256")) is not str or
            not _SHA.fullmatch(saved["sha256"])):
        raise NativeSubjectPreviewError("BRUSH_SAVE_UNAVAILABLE")
    return {
        "status": saved["status"], "project_sha256": saved["sha256"],
        "subject_id": subject_id, "command_id": command_id,
        "persisted": True, "cricut_certified": False,
    }
