"""V34-132: read-only native bridge from a proven V1 Subject to the existing brush.

The UI supplies a managed project path, its exact observed SHA-256 and a
persistent subject_id. It never chooses a tensor index, a mask file or a
float32 digest. Reuse the G2.2 workspace admission/revision checks and
G3.3e brush; do not create a writer, save a gesture or publish an export.
"""
from __future__ import annotations

from pathlib import Path
import re

from .project_workspace_g22 import ManagedWorkspace, WorkspaceError, NAME


_SHA = re.compile(r"^[0-9a-f]{64}$")
_SUBJECT = re.compile(r"^subject-[0-9a-f]{32}$")
_MANAGED_DIRECTORY = "SmartSVG_Managed_Projects"


class NativeSubjectPreviewError(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _workspace_from_path(project_path):
    """Admit existing managed V1 files only, without creating directories."""
    if not isinstance(project_path, (str, Path)) or not str(project_path):
        raise NativeSubjectPreviewError("INVALID_PROJECT_PATH")
    try:
        path = Path(project_path)
        if (not path.is_absolute() or ".." in path.parts
                or path.suffix != ".smartsvg" or
                path.parent.name != _MANAGED_DIRECTORY or
                not NAME.fullmatch(path.stem) or
                path.is_symlink() or path.parent.is_symlink() or
                path.parent.parent.is_symlink() or
                not path.parent.is_dir() or not path.parent.parent.is_dir() or
                not path.is_file()):
            raise NativeSubjectPreviewError("UNMANAGED_PROJECT")
        # Check the *whole* path, not only its final two parent directories.
        # On Windows a junction (or a more distant symlink) can redirect a
        # syntactically managed path to another tree without appearing as a
        # symlink on the project, managed folder or immediate workspace root.
        # Path.resolve(strict=True) resolves reparse points without writing.
        if path.resolve(strict=True) != path.absolute():
            raise NativeSubjectPreviewError("UNMANAGED_PROJECT")
        workspace = ManagedWorkspace(path.parent.parent)
        if workspace.root != path.parent or workspace._path(path.stem) != path:
            raise NativeSubjectPreviewError("UNMANAGED_PROJECT")
        return workspace, path.stem
    except NativeSubjectPreviewError:
        raise
    except (OSError, ValueError, TypeError, RuntimeError, WorkspaceError) as exc:
        raise NativeSubjectPreviewError("INVALID_PROJECT_PATH") from exc


def preview_native_subject_stroke(
    *, project_path, expected_sha256, subject_id, mode, radius, points,
):
    """Preview one Add/Erase stroke on the actual proven Subject.

    Result is UI-safe: only two PNG L8 previews, bounded metadata and
    revision/identity. In particular neither replay float32 nor editor
    document escapes. The managed backend checks the revision before and
    after CPU processing; old UI generations must still be discarded by
    the caller if the user switches projects during asynchronous work.
    """
    if type(expected_sha256) is not str or not _SHA.fullmatch(expected_sha256):
        raise NativeSubjectPreviewError("EXPECTED_REVISION_REQUIRED")
    if type(subject_id) is not str or not _SUBJECT.fullmatch(subject_id):
        raise NativeSubjectPreviewError("INVALID_SUBJECT_ID")

    workspace, name = _workspace_from_path(project_path)
    try:
        snapshot = workspace.inspect(name)
        if snapshot.get("status") != "PROJECT_HEALTHY":
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
        matches = [
            row for row in catalog.get("bindings", ())
            if row.get("subject_id") == subject_id
        ]
        if (len(matches) != 1 or
                matches[0].get("subject_proof_status") != "verified" or
                matches[0].get("subject_ambiguous") is not False or
                matches[0].get("has_foreground") is not True):
            raise NativeSubjectPreviewError("SUBJECT_NOT_VERIFIED")
        match = matches[0]
        result = workspace.preview_subject_brush_readonly(
            name, expected_sha256=expected_sha256,
            subject_id=subject_id, mask_id=match["mask_id"],
            mask_sha256_float32=match["mask_sha256_float32"],
            source_id=catalog["source_id"],
            source_sha256=masks["editor_fingerprint"],
            mode=mode, radius=radius, points=points,
        )
        # Whitelist UI output even if the underlying backend gains internal
        # fields later. Never leak exact float32 pixels or the editor session.
        if (result.get("project_sha256") != expected_sha256 or
                result.get("subject_id") != subject_id or
                result.get("mask_id") != match["mask_id"] or
                result.get("persisted") is not False):
            raise NativeSubjectPreviewError("PREVIEW_IDENTITY_CHANGED")
        return {
            "project_sha256": expected_sha256,
            "subject_id": subject_id,
            "mask_id": match["mask_id"],
            "before_png_l8": result["before_png_l8"],
            "after_png_l8": result["after_png_l8"],
            "changed_pixels": result["changed_pixels"],
            "dimensions_px": result["dimensions_px"],
            "preview_mask_sha256_float32": result["preview_mask_sha256_float32"],
            "persisted": False,
            "cricut_certified": False,
        }
    except NativeSubjectPreviewError:
        raise
    except WorkspaceError as exc:
        raise NativeSubjectPreviewError(exc.code) from exc
    except (OSError, KeyError, TypeError, ValueError) as exc:
        raise NativeSubjectPreviewError("PREVIEW_UNAVAILABLE") from exc
