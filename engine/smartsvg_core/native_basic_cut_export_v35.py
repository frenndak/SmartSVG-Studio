"""W04: explicit, revision-pinned local SVG Basic Cut publication.

Uses the verified native Subject vector preview and the established PTC
no-overwrite, pinned-directory, atomic writer. Does not modify the V1 archive.
"""
from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import re
import stat

from .native_basic_cut_subject_v35 import inspect_native_basic_cut_subject
from .native_basic_cut_v35 import BasicCutError
from .native_first_subject_v35 import _pinned_project, NativeFirstSubjectError
from .native_ptc_export_v35 import (
    NativePTCError, _destination, _publish_posix_pinned,
    _publish_windows_locked,
)

_SHA = re.compile(r"^[0-9a-f]{64}$")


def _svg_destination(value):
    if type(value) is not str or not value or len(value) > 4096:
        raise BasicCutError("INVALID_EXPORT_PATH")
    path = Path(value)
    if path.suffix.lower() != ".svg":
        raise BasicCutError("INVALID_EXPORT_PATH")
    # The existing PTC path validator enforces absolute paths, Windows device
    # names, forbidden characters, parent existence and ancestor symlinks.
    try:
        _destination(str(path.with_suffix(".png")))
    except NativePTCError as exc:
        raise BasicCutError(str(exc)) from exc
    try:
        if path.is_symlink():
            raise BasicCutError("UNSAFE_EXPORT_PATH")
    except OSError as exc:
        raise BasicCutError("UNSAFE_EXPORT_PATH") from exc
    return path


def publish_native_basic_cut_svg(*, project_path, expected_sha256,
                                 subject_id, width_mm, destination_path,
                                 expected_svg_sha256, confirmed=False):
    """Publish only the exact confirmed preview; never replace other bytes.

    A failed or uncertain publication must be reviewed, not blindly retried.
    The native preview performs Subject, source, mask and project SHA checks.
    """
    if confirmed is not True:
        raise BasicCutError("EXPLICIT_CONFIRMATION_REQUIRED")
    if type(expected_svg_sha256) is not str or not _SHA.fullmatch(expected_svg_sha256):
        raise BasicCutError("EXPECTED_PREVIEW_REQUIRED")
    dest = _svg_destination(destination_path)
    try:
        initial_parent = os.stat(dest.parent, follow_symlinks=False)
        if not stat.S_ISDIR(initial_parent.st_mode):
            raise BasicCutError("UNSAFE_EXPORT_PATH")
    except OSError as exc:
        raise BasicCutError("UNSAFE_EXPORT_PATH") from exc
    preview = inspect_native_basic_cut_subject(
        project_path=project_path, expected_sha256=expected_sha256,
        subject_id=subject_id, width_mm=width_mm)
    if preview.svg_sha256 != expected_svg_sha256 or sha256(preview.svg).hexdigest() != expected_svg_sha256:
        raise BasicCutError("PREVIEW_CHANGED")
    try:
        _pinned_project(project_path, expected_sha256)
    except NativeFirstSubjectError as exc:
        raise BasicCutError("PROJECT_CHANGED") from exc
    try:
        if os.name == "posix":
            _publish_posix_pinned(dest, preview.svg, expected_svg_sha256, initial_parent)
        elif os.name == "nt":
            _publish_windows_locked(dest, preview.svg, expected_svg_sha256, initial_parent)
        else:
            raise BasicCutError("ATOMIC_PUBLICATION_UNAVAILABLE")
    except NativePTCError as exc:
        raise BasicCutError(str(exc)) from exc
    try:
        _pinned_project(project_path, expected_sha256)
        current = True
    except NativeFirstSubjectError:
        current = False
    return {
        "status": "LOCAL_SVG_RELOADED" if current else "LOCAL_SVG_REVISION_CHANGED",
        "file_path": str(dest), "sha256": expected_svg_sha256,
        "project_sha256": preview.project_sha256,
        "subject_id": preview.subject_id, "width_mm": preview.width_mm,
        "height_mm": preview.height_mm, "ring_count": preview.ring_count,
        "persisted": True, "project_revision_still_current": current,
        "design_space_import_tested": False, "physical_cut_tested": False,
    }
