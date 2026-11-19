"""W03: bounded native Print Then Cut PNG from a verified V1 Subject.

This is an explicit external file export, NOT a V1 archive writer, Design
Space upload, bleed generator, cutting-path certificate or physical cut.
The saved G2.3 editor session is replayed, never silently omitted.
"""
from __future__ import annotations

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

    staged = None
    try:
        from smartsvg_cricut.direct_import_v218 import _copy_atomic
        fd, raw_path = tempfile.mkstemp(
            prefix=".smartsvg_ptc_stage_", suffix=".png", dir=str(dest.parent))
        staged = Path(raw_path)
        with os.fdopen(fd, "wb") as stream:
            stream.write(result["png"])
            stream.flush()
            os.fsync(stream.fileno())
        if sha256(staged.read_bytes()).hexdigest() != expected_output_sha256:
            raise NativePTCError("STAGING_VERIFICATION_FAILED")
        _copy_atomic(staged, dest)
        if (not dest.is_file() or dest.is_symlink() or
                sha256(dest.read_bytes()).hexdigest() != expected_output_sha256):
            raise NativePTCError("OUTPUT_REQUIRES_REVIEW")
    except NativePTCError:
        raise
    except (OSError, ValueError, ImportError) as exc:
        # A failed publication may have happened: do not claim rollback.
        raise NativePTCError("OUTPUT_REQUIRES_REVIEW") from exc
    finally:
        if staged is not None:
            staged.unlink(missing_ok=True)
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
