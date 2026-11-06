"""Explicit native PNG -> V1 creation through the existing managed writer.

No GUI/ComfyUI/server imports, background scheduling, implicit destination,
project migration or existing-project edit. Receipt follows verified readback.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import stat

from .project_archive import ProjectArchiveError, load_project, _file_digest
from .project_workspace_g22 import (
    ManagedWorkspace, WorkspaceError, MAX_IMAGE_BYTES, PROFILES,
    _valid_name, _width, _dpi, _verify_png,
)
from .source_preview_v34 import select_source_png


class NativeCreateError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class NativeCreateReceipt:
    path: str
    sha256: str
    preview_status: str


def _read_source(path):
    if not isinstance(path, (str, Path)) or not str(path):
        raise NativeCreateError('INVALID_SOURCE_PATH')
    source = Path(path)
    if source.suffix.lower() != '.png' or source.is_symlink():
        raise NativeCreateError('INVALID_SOURCE_PATH')
    flags = os.O_RDONLY | getattr(os, 'O_BINARY', 0) | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
    try:
        descriptor = os.open(source, flags)
        with os.fdopen(descriptor, 'rb') as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise NativeCreateError('INVALID_SOURCE_PATH')
            data = stream.read(MAX_IMAGE_BYTES + 1)
        if len(data) > MAX_IMAGE_BYTES:
            raise NativeCreateError('INVALID_IMAGE_BYTES')
        return data
    except OSError as exc:
        raise NativeCreateError('SOURCE_READ_FAILED') from exc


def create_native_project(*, source_path, output_root, name, profile, width_mm, dpi):
    """Create once and verify persisted bytes; never retry uncertain writes."""
    try:
        _valid_name(name)
        # Keep names portable for the intended Windows distribution.
        if name.upper() in {'CON', 'PRN', 'AUX', 'NUL', *('COM'+str(i) for i in range(1, 10)),
                            *('LPT'+str(i) for i in range(1, 10))}:
            raise WorkspaceError('INVALID_PROJECT_NAME')
        if not isinstance(profile, str) or profile not in PROFILES:
            raise WorkspaceError('INVALID_PROFILE')
        width, density = _width(width_mm), _dpi(dpi)
        if (not isinstance(output_root, (str, Path)) or not str(output_root) or
                not Path(output_root).is_absolute()):
            raise NativeCreateError('INVALID_WORKSPACE_ROOT')
        source = _read_source(source_path)
        _verify_png(source)  # reject input before creating a workspace directory
        workspace = ManagedWorkspace(output_root)
        result = workspace.create(name, source, profile=profile, width_mm=width, dpi=density,
                                  source_provenance='manual_native_png_import')
    except WorkspaceError as exc:
        raise NativeCreateError(exc.code) from exc
    except OSError as exc:
        raise NativeCreateError('SAVE_FAILED') from exc
    path = workspace.root / (name + '.smartsvg')
    try:
        project = load_project(path, expected_sha256=result['sha256'])
        asset = project.sources[0]
        if (project.project_id != name or len(project.sources) != 1 or
                project.document.get('profile') != profile or
                project.document.get('width_mm') != width or project.document.get('dpi') != density or
                asset.sha256 != sha256(source).hexdigest() or
                project.resources[project.source_paths[asset.source_id]] != source or
                _file_digest(path) != result['sha256']):
            raise NativeCreateError('CREATE_UNCONFIRMED')
        preview = select_source_png(project)
    except (ProjectArchiveError, OSError, KeyError, IndexError) as exc:
        raise NativeCreateError('CREATE_UNCONFIRMED') from exc
    return NativeCreateReceipt(str(path), result['sha256'], preview.status)
