"""V34-018/025: bounded native PNG -> V1 creation, independent of ComfyUI.

The trusted output root is supplied by the caller, never by image metadata.
No GUI, network, weights, or implicit recovery is performed here.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from .project_workspace_g22 import ManagedWorkspace, MAX_IMAGE_BYTES, WorkspaceError
from .project_archive import load_project


def create_native_png_project(trusted_output_root, name, source_path, *,
                              profile="Auto - conserver le visuel",
                              width_mm=40, dpi=300):
    """Create a new managed V1 archive and verify it can be reopened.

    Refuse symlink input and source changes during reading. Never overwrite an
    existing project. The writer owns validation, atomic save and recovery.
    """
    source = Path(source_path)
    if source.is_symlink() or not source.is_file():
        raise WorkspaceError("INVALID_SOURCE_PATH")
    before = source.stat()
    if before.st_size > MAX_IMAGE_BYTES:
        raise WorkspaceError("INVALID_IMAGE_BYTES")
    data = source.read_bytes()
    after = source.stat()
    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns):
        raise WorkspaceError("SOURCE_CHANGED")
    if sha256(data).digest() != _file_digest(source):
        raise WorkspaceError("SOURCE_CHANGED")
    workspace = ManagedWorkspace(trusted_output_root)
    result = workspace.create(name, data, profile=profile,
                              width_mm=width_mm, dpi=dpi)
    archive = workspace._path(name)
    # Verify actual persisted bytes, not only the writer's receipt.
    if _file_digest(archive).hex() != result["sha256"]:
        raise WorkspaceError("ARCHIVE_CHANGED")
    loaded = load_project(archive)
    if (loaded.project_id != name or len(loaded.sources) != 1 or
            loaded.sources[0].sha256 != sha256(data).hexdigest()):
        raise WorkspaceError("ARCHIVE_VERIFICATION_FAILED")
    return {"archive": str(archive), "sha256": result["sha256"],
            "source_sha256": sha256(data).hexdigest(),
            "status": "created", "cricut_certified": False}


def _file_digest(path):
    digest = sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.digest()
