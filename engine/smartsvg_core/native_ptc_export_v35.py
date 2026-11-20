"""W03: bounded native Print Then Cut PNG from a verified V1 Subject.

This is an explicit external file export, NOT a V1 archive writer, Design
Space upload, bleed generator, cutting-path certificate or physical cut.
The saved G2.3 editor session is replayed, never silently omitted.
"""
from __future__ import annotations

from contextlib import contextmanager
import secrets
import stat
from hashlib import sha256
from io import BytesIO
import json
import math
import os
from pathlib import Path
import re
import tempfile

from .mask_binding_g33e import snapshot_mask_bindings
from .mask_snapshot_g24 import SNAPSHOT_KEY, SNAPSHOT_PATH, decode_snapshot
from .native_first_subject_v35 import _pinned_project, NativeFirstSubjectError
from .project_contracts import _WINDOWS_DEVICE, _WINDOWS_FORBIDDEN

_SHA = re.compile(r"^[0-9a-f]{64}$")
_SUBJECT = re.compile(r"^subject-[0-9a-f]{32}$")
_MAX_PIXELS = 5_000_000


class NativePTCError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _width_mm(value):
    if type(value) not in (int, float):
        raise NativePTCError("INVALID_PHYSICAL_WIDTH")
    try:
        width = float(value)
    except (OverflowError, ValueError):
        raise NativePTCError("INVALID_PHYSICAL_WIDTH") from None
    if not math.isfinite(width) or not 0.01 <= width <= 10000:
        raise NativePTCError("INVALID_PHYSICAL_WIDTH")
    return width


def _render(*, project_path, expected_sha256, subject_id, width_mm):
    """Compute the real RGBA output in memory; no disk write or archive change."""
    if type(subject_id) is not str or not _SUBJECT.fullmatch(subject_id):
        raise NativePTCError("INVALID_SUBJECT_ID")
    width_mm = _width_mm(width_mm)
    try:
        _, _, project = _pinned_project(project_path, expected_sha256)
        if len(project.sources) != 1:
            raise NativePTCError("SOURCE_NOT_ELIGIBLE")
        source = project.sources[0]
        if source.color_mode != "RGBA":
            raise NativePTCError("SOURCE_RGBA_REQUIRED")
        pixels = source.width_px * source.height_px
        if not 1 <= pixels <= _MAX_PIXELS:
            raise NativePTCError("IMAGE_PIXEL_BUDGET_EXCEEDED")
        catalog = snapshot_mask_bindings(project)
        if (type(catalog) is not dict or
                catalog.get("subject_proof_schema_valid") is not True or
                catalog.get("source_id") != source.source_id):
            raise NativePTCError("SUBJECT_NOT_VERIFIED")
        matches = [row for row in catalog["bindings"]
                   if row.get("subject_id") == subject_id]
        if (len(matches) != 1 or
                matches[0].get("subject_proof_status") != "verified" or
                matches[0].get("subject_ambiguous") is not False or
                matches[0].get("has_foreground") is not True):
            raise NativePTCError("SUBJECT_NOT_VERIFIED")
        snapshot = project.document[SNAPSHOT_KEY]
        raw = decode_snapshot(snapshot, project.resources[SNAPSHOT_PATH])
        count, height, width = snapshot["shape"]
        if (width, height) != (source.width_px, source.height_px):
            raise NativePTCError("SOURCE_SIZE_CHANGED")
        idx = matches[0]["mask_index"]
        if type(idx) is not int or not 0 <= idx < count:
            raise NativePTCError("SUBJECT_NOT_VERIFIED")
        effective_ppi = width * 25.4 / width_mm
        height_mm = height * width_mm / width
        if (not 1 <= effective_ppi <= 2400 or
                not 0.01 <= height_mm <= 10000):
            raise NativePTCError("PHYSICAL_SIZE_NOT_SUPPORTED")
        # The same existing CPU replay as the native brush; never render an
        # old unedited base mask if persisted editor_v216 strokes exist.
        import numpy as np
        from PIL import Image
        from .editor_session_g23 import parse_editor_document
        from smartsvg_editor.strokes import decode, apply_strokes
        base = np.frombuffer(raw, dtype="<f4").reshape(count, height, width)
        base.flags.writeable = False
        corrected = base
        if "editor_v216" in project.document:
            editor, canonical = parse_editor_document(
                json.dumps(project.document["editor_v216"],
                           allow_nan=False, separators=(",", ":")),
                source_dimensions=(width, height))
            if (editor["source"] != snapshot["editor_fingerprint"] or
                    editor["count"] != count):
                raise NativePTCError("EDITOR_SESSION_CHANGED")
            validated = decode(canonical, width=width, height=height,
                               count=count, fingerprint=snapshot["editor_fingerprint"])
            corrected = apply_strokes(base, validated)
        if corrected.shape != base.shape or not np.isfinite(corrected[idx]).all():
            raise NativePTCError("INVALID_RENDERED_MASK")
        selected = corrected[idx]
        if (np.min(selected) < -0.001 or np.max(selected) > 1.001 or
                not np.any(selected >= 0.5)):
            raise NativePTCError("EMPTY_OR_INVALID_CUT_SILHOUETTE")
        alpha = np.clip(np.rint(selected * 255), 0, 255).astype(np.uint8)
        source_png = project.resources[project.source_paths[source.source_id]]
        if sha256(source_png).hexdigest() != source.sha256:
            raise NativePTCError("SOURCE_CHANGED")
        with Image.open(BytesIO(source_png)) as original:
            original.load()
            if (original.format != "PNG" or original.mode != "RGBA" or
                    original.size != (width, height)):
                raise NativePTCError("SOURCE_RGBA_REQUIRED")
            rendered = original.copy()
        # The exact edited subject float32 becomes the final transparency.
        # Multiplying by source alpha again would square semi-transparent
        # source pixels, even with zero retouch: never do that.
        rendered.putalpha(Image.fromarray(alpha, mode="L"))
        output = BytesIO()
        rendered.save(output, format="PNG", dpi=(effective_ppi, effective_ppi))
        png = output.getvalue()
        with Image.open(BytesIO(png)) as verified:
            verified.load()
            dpi = verified.info.get("dpi")
            if (verified.format != "PNG" or verified.mode != "RGBA" or
                    verified.size != (width, height) or dpi is None or
                    abs(dpi[0] - effective_ppi) > 0.1 or
                    abs(dpi[1] - effective_ppi) > 0.1):
                raise NativePTCError("OUTPUT_PNG_VERIFICATION_FAILED")
        thumbnail = rendered.copy()
        thumbnail.thumbnail((280, 280))
        thumbnail_data = BytesIO()
        thumbnail.save(thumbnail_data, format="PNG")
        return {
            "project_sha256": expected_sha256,
            "subject_id": subject_id,
            "source_sha256": source.sha256,
            "rendered_mask_sha256": sha256(alpha.tobytes()).hexdigest(),
            "output_sha256": sha256(png).hexdigest(),
            "dimensions_px": [width, height],
            "width_mm": round(width_mm, 4),
            "height_mm": round(height_mm, 4),
            "effective_ppi": round(effective_ppi, 3),
            "low_resolution_warning": effective_ppi < 150,
            "preview_png_rgba": thumbnail_data.getvalue(),
            "png": png,
        }
    except NativePTCError:
        raise
    except (NativeFirstSubjectError, KeyError, ValueError, TypeError,
            OSError, ImportError, RuntimeError, MemoryError) as exc:
        raise NativePTCError("EXPORT_PREPARATION_UNAVAILABLE") from exc


def inspect_native_ptc_png(*, project_path, expected_sha256, subject_id, width_mm):
    """Read-only preview, fingerprint and physical size before confirmation."""
    result = _render(project_path=project_path, expected_sha256=expected_sha256,
                     subject_id=subject_id, width_mm=width_mm)
    return {
        **{k: v for k, v in result.items() if k != "png"},
        "status": "PTC_PREVIEW_READY",
        "persisted": False,
        "design_space_import_tested": False,
        "physical_cut_tested": False,
    }


def _destination(value):
    if type(value) is not str or not value or len(value) > 4096:
        raise NativePTCError("INVALID_EXPORT_PATH")
    path = Path(value)
    if (not path.is_absolute() or ".." in path.parts or
            path.suffix.lower() != ".png" or
            _WINDOWS_DEVICE.fullmatch(path.name) or
            any(char in _WINDOWS_FORBIDDEN or ord(char) < 32
                for char in path.name) or
            path.name.endswith((".", " "))):
        raise NativePTCError("INVALID_EXPORT_PATH")
    if not path.parent.is_dir():
        raise NativePTCError("EXPORT_DIRECTORY_NOT_FOUND")
    try:
        for part in (path, *path.parents):
            if part.is_symlink():
                raise NativePTCError("UNSAFE_EXPORT_PATH")
    except OSError as exc:
        raise NativePTCError("UNSAFE_EXPORT_PATH") from exc
    return path



def _same_directory_identity(first, second):
    return ((first.st_dev, first.st_ino) ==
            (second.st_dev, second.st_ino))


def _verify_posix_entry(dir_fd, name, expected_sha256):
    """Read only a regular inode in the already opened parent directory."""
    try:
        flags = os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
        fd = os.open(name, flags, dir_fd=dir_fd)
    except FileNotFoundError:
        return False
    except OSError as exc:
        raise NativePTCError("OUTPUT_REQUIRES_REVIEW") from exc
    with os.fdopen(fd, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise NativePTCError("OUTPUT_REQUIRES_REVIEW")
        digest = sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
        if digest.hexdigest() != expected_sha256:
            raise NativePTCError("OUTPUT_REQUIRES_REVIEW")
    return True


def _publish_posix_pinned(dest, data, digest, initial_parent):
    """Pin each path component, stage and link with directory FDs.

    An attacker can rename the visible parent, but cannot redirect a dir_fd-
    relative link to a replacement directory. A changed name invalidates the
    receipt and rolls back only our own newly linked inode in the old parent.
    """
    flags = (os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW |
             getattr(os, "O_CLOEXEC", 0))
    parent_fd = None
    stage = None
    created = False
    accepted = False
    stage_identity = None
    try:
        parent_fd = os.open(dest.anchor, flags)
        for component in dest.parent.parts[1:]:
            new_fd = os.open(component, flags, dir_fd=parent_fd)
            os.close(parent_fd)
            parent_fd = new_fd
        pinned = os.fstat(parent_fd)
        if not _same_directory_identity(initial_parent, pinned):
            raise NativePTCError("UNSAFE_EXPORT_PATH")

        def check_parent():
            try:
                current = os.stat(dest.parent, follow_symlinks=False)
            except OSError as exc:
                raise NativePTCError("UNSAFE_EXPORT_PATH") from exc
            if (not stat.S_ISDIR(current.st_mode) or
                    not _same_directory_identity(current, pinned)):
                raise NativePTCError("UNSAFE_EXPORT_PATH")

        check_parent()
        if _verify_posix_entry(parent_fd, dest.name, digest):
            check_parent()
            return

        stage = ".smartsvg_ptc_stage_" + secrets.token_hex(16) + ".png"
        stage_fd = os.open(
            stage, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW |
            getattr(os, "O_CLOEXEC", 0), 0o600, dir_fd=parent_fd)
        # Record ownership before writes, including errors and disk-full.
        opened_stage = os.fstat(stage_fd)
        stage_identity = (opened_stage.st_dev, opened_stage.st_ino)
        with os.fdopen(stage_fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        stage_stat = os.stat(stage, dir_fd=parent_fd, follow_symlinks=False)
        if (stage_stat.st_dev, stage_stat.st_ino) != stage_identity:
            raise NativePTCError("STAGING_VERIFICATION_FAILED")
        if not _verify_posix_entry(parent_fd, stage, digest):
            raise NativePTCError("STAGING_VERIFICATION_FAILED")
        check_parent()
        try:
            os.link(stage, dest.name, src_dir_fd=parent_fd,
                    dst_dir_fd=parent_fd, follow_symlinks=False)
            created = True
        except FileExistsError:
            if not _verify_posix_entry(parent_fd, dest.name, digest):
                raise NativePTCError("OUTPUT_REQUIRES_REVIEW")
        except OSError as exc:
            raise NativePTCError("ATOMIC_PUBLICATION_UNAVAILABLE") from exc
        check_parent()  # Detect even a swap performed inside os.link itself.
        if not _verify_posix_entry(parent_fd, dest.name, digest):
            raise NativePTCError("OUTPUT_REQUIRES_REVIEW")
        if created:
            try:
                os.fsync(parent_fd)
            except OSError as exc:
                raise NativePTCError("OUTPUT_REQUIRES_REVIEW") from exc
        check_parent()
        accepted = True
    except NativePTCError:
        raise
    except (OSError, ValueError, NotImplementedError) as exc:
        raise NativePTCError("ATOMIC_PUBLICATION_UNAVAILABLE") from exc
    finally:
        if parent_fd is not None:
            # Do not unlink either pathname here. stat(entry) followed by
            # unlink(entry) is NOT an atomic identity-checked removal: a
            # concurrent writer can replace the entry between those calls,
            # causing deletion of a user-owned file. This includes the
            # staging name, even when its original inode was ours.
            #
            # Fail closed: retain uncertain staging / output entries rather
            # than risk data loss. These private-prefix staging files are
            # intentionally left for explicit, user-reviewed housekeeping.
            # A future cleanup needs a platform-specific atomic ownership
            # primitive and its own adversarial regression tests.
            os.close(parent_fd)


@contextmanager
def _pin_windows_directory_chain(parent, initial_parent):
    """Keep every directory component open without FILE_SHARE_DELETE.

    Windows otherwise lacks the POSIX dir_fd APIs. Opened directory handles
    prevent rename/delete through supported Win32 sharing semantics; reject
    junctions/reparse points. Refuse publication if any handle cannot be held.
    """
    import ctypes
    from ctypes import wintypes

    class _FileInfo(ctypes.Structure):
        _fields_ = [
            ("dwFileAttributes", wintypes.DWORD),
            ("ftCreationTime", wintypes.FILETIME),
            ("ftLastAccessTime", wintypes.FILETIME),
            ("ftLastWriteTime", wintypes.FILETIME),
            ("dwVolumeSerialNumber", wintypes.DWORD),
            ("nFileSizeHigh", wintypes.DWORD),
            ("nFileSizeLow", wintypes.DWORD),
            ("nNumberOfLinks", wintypes.DWORD),
            ("nFileIndexHigh", wintypes.DWORD),
            ("nFileIndexLow", wintypes.DWORD),
        ]

    api = ctypes.WinDLL("kernel32", use_last_error=True)
    api.CreateFileW.argtypes = [
        wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD,
        wintypes.LPVOID, wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
    api.CreateFileW.restype = wintypes.HANDLE
    api.GetFileInformationByHandle.argtypes = [
        wintypes.HANDLE, ctypes.POINTER(_FileInfo)]
    api.GetFileInformationByHandle.restype = wintypes.BOOL
    api.CloseHandle.argtypes = [wintypes.HANDLE]
    api.CloseHandle.restype = wintypes.BOOL
    handles = []
    try:
        for folder in (*reversed(parent.parents), parent):
            # FILE_READ_ATTRIBUTES alone (0x80) is metadata-only and does
            # NOT enforce FILE_SHARE_DELETE against renames. Request actual
            # FILE_LIST_DIRECTORY (0x1) plus SYNCHRONIZE/READ_ATTRIBUTES.
            # Without FILE_SHARE_DELETE, Windows must refuse directory
            # rename/delete while this handle is held; our CI exercises it.
            directory_access = 0x00100000 | 0x00000080 | 0x00000001
            handle = api.CreateFileW(
                str(folder), directory_access, 0x1 | 0x2, None, 3,
                0x02000000 | 0x00200000, None)
            if handle in (None, ctypes.c_void_p(-1).value):
                raise NativePTCError("ATOMIC_PUBLICATION_UNAVAILABLE")
            handles.append(handle)
            info = _FileInfo()
            if not api.GetFileInformationByHandle(handle, ctypes.byref(info)):
                raise NativePTCError("ATOMIC_PUBLICATION_UNAVAILABLE")
            if (info.dwFileAttributes & 0x00000400 or  # reparse/junction
                    not info.dwFileAttributes & 0x00000010):
                raise NativePTCError("UNSAFE_EXPORT_PATH")
        current = os.stat(parent, follow_symlinks=False)
        if not _same_directory_identity(initial_parent, current):
            raise NativePTCError("UNSAFE_EXPORT_PATH")
        yield
        current = os.stat(parent, follow_symlinks=False)
        if not _same_directory_identity(initial_parent, current):
            raise NativePTCError("UNSAFE_EXPORT_PATH")
    finally:
        for handle in reversed(handles):
            api.CloseHandle(handle)


def _publish_windows_locked(dest, data, digest, initial_parent):
    """Full staging + exclusive publication while ancestor renames are blocked."""
    with _pin_windows_directory_chain(dest.parent, initial_parent):
        staged = None
        try:
            if dest.is_symlink() or (dest.exists() and
                    (not dest.is_file() or
                     sha256(dest.read_bytes()).hexdigest() != digest)):
                raise NativePTCError("OUTPUT_REQUIRES_REVIEW")
            if not dest.exists():
                fd, raw_path = tempfile.mkstemp(
                    prefix=".smartsvg_ptc_stage_", suffix=".png",
                    dir=str(dest.parent))
                staged = Path(raw_path)
                with os.fdopen(fd, "wb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
                if sha256(staged.read_bytes()).hexdigest() != digest:
                    raise NativePTCError("STAGING_VERIFICATION_FAILED")
                try:
                    os.link(staged, dest)
                except FileExistsError:
                    if (dest.is_symlink() or not dest.is_file() or
                            sha256(dest.read_bytes()).hexdigest() != digest):
                        raise NativePTCError("OUTPUT_REQUIRES_REVIEW") from None
                except OSError as exc:
                    # Windows rename is non-overwriting; POSIX uses dir_fd.
                    try:
                        os.rename(staged, dest)
                        staged = None
                    except FileExistsError:
                        if (dest.is_symlink() or not dest.is_file() or
                                sha256(dest.read_bytes()).hexdigest() != digest):
                            raise NativePTCError("OUTPUT_REQUIRES_REVIEW") from None
                    except OSError as rename_exc:
                        raise NativePTCError(
                            "ATOMIC_PUBLICATION_UNAVAILABLE") from rename_exc
            if (dest.is_symlink() or not dest.is_file() or
                    sha256(dest.read_bytes()).hexdigest() != digest):
                raise NativePTCError("OUTPUT_REQUIRES_REVIEW")
        except NativePTCError:
            raise
        except (OSError, ValueError) as exc:
            raise NativePTCError("OUTPUT_REQUIRES_REVIEW") from exc
        finally:
            if staged is not None:
                staged.unlink(missing_ok=True)


def publish_native_ptc_png(*, project_path, expected_sha256, subject_id,
                           width_mm, destination_path, expected_output_sha256,
                           confirmed=False):
    """Publish a completely staged PNG with the existing non-overwrite writer.

    The .smartsvg project is never mutated. A failed/uncertain receipt must not
    trigger an automatic second publication from the UI.
    """
    if confirmed is not True:
        raise NativePTCError("EXPLICIT_CONFIRMATION_REQUIRED")
    if (type(expected_output_sha256) is not str or
            not _SHA.fullmatch(expected_output_sha256)):
        raise NativePTCError("EXPECTED_PREVIEW_REQUIRED")
    dest = _destination(destination_path)
    # Pin the originally selected directory BEFORE potentially lengthy render.
    # A swap during rendering must never silently select a different parent.
    try:
        initial_parent = os.stat(dest.parent, follow_symlinks=False)
    except OSError as exc:
        raise NativePTCError("UNSAFE_EXPORT_PATH") from exc
    if not stat.S_ISDIR(initial_parent.st_mode):
        raise NativePTCError("UNSAFE_EXPORT_PATH")
    result = _render(project_path=project_path, expected_sha256=expected_sha256,
                     subject_id=subject_id, width_mm=width_mm)
    if result["output_sha256"] != expected_output_sha256:
        raise NativePTCError("PREVIEW_CHANGED")
    # Recheck CAS immediately before publication; unlike a project save, an
    # external exported PNG is a revision-tagged snapshot, not a V1 mutation.
    try:
        _pinned_project(project_path, expected_sha256)
    except NativeFirstSubjectError as exc:
        raise NativePTCError("PROJECT_CHANGED") from exc

    try:
        if os.name == "posix":
            _publish_posix_pinned(
                dest, result["png"], expected_output_sha256, initial_parent)
        elif os.name == "nt":
            _publish_windows_locked(
                dest, result["png"], expected_output_sha256, initial_parent)
        else:
            raise NativePTCError("ATOMIC_PUBLICATION_UNAVAILABLE")
    except NativePTCError:
        raise
    except OSError as exc:
        raise NativePTCError("UNSAFE_EXPORT_PATH") from exc
    try:
        _pinned_project(project_path, expected_sha256)
        still_current = True
    except NativeFirstSubjectError:
        still_current = False
    return {
        "status": "LOCAL_PNG_RELOADED" if still_current else "LOCAL_PNG_REVISION_CHANGED",
        "file_path": str(dest), "sha256": expected_output_sha256,
        "project_sha256": expected_sha256, "subject_id": subject_id,
        "dimensions_px": result["dimensions_px"],
        "width_mm": result["width_mm"], "height_mm": result["height_mm"],
        "effective_ppi": result["effective_ppi"],
        "low_resolution_warning": result["low_resolution_warning"],
        "persisted": True, "project_revision_still_current": still_current,
        "design_space_import_tested": False, "physical_cut_tested": False,
    }
