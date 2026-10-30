"""G3.3e-b2a (core slice): one read-only brush preview for a proven G1.2 Subject.

This is an in-memory primitive, NOT an HTTP endpoint or a save operation.
The caller must load a healthy archive and enforce project revision/CAS before
and after calling it. UI, cancellation and late-result guards are separate.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re

from .mask_binding_g33e import snapshot_mask_bindings
from .mask_snapshot_g24 import (
    SNAPSHOT_KEY, SNAPSHOT_PATH, MaskSnapshotError, decode_snapshot,
    encode_preview_l8,
)
from .subject_identity_g33e import SubjectIdentityError

_SUBJECT_ID = re.compile(r"^subject-[0-9a-f]{32}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")
MAX_PREVIEW_POINTS = 64


class SubjectBrushPreviewError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def preview_subject_brush(
    project, *, subject_id, mask_id, mask_sha256_float32,
    source_id, source_sha256, mode, radius, points,
):
    """Preview ONE add/erase stroke; never alter project, resources or base float32.

    Return internal-only immutable float32 bytes plus before/after L8 PNG
    previews. Never send preview_float32 to a browser as an archive authority.
    A caller must separately pin and recheck the on-disk .smartsvg revision.
    """
    if (not isinstance(subject_id, str) or not _SUBJECT_ID.fullmatch(subject_id)
            or not isinstance(mask_id, str)
            or not isinstance(mask_sha256_float32, str)
            or not _SHA.fullmatch(mask_sha256_float32)
            or not isinstance(source_id, str)
            or not isinstance(source_sha256, str)
            or not _SHA.fullmatch(source_sha256)):
        raise SubjectBrushPreviewError("INVALID_PREVIEW_IDENTITY")
    if (mode not in ("add", "erase") or type(mode) is not str
            or not isinstance(points, list)
            or not 1 <= len(points) <= MAX_PREVIEW_POINTS):
        raise SubjectBrushPreviewError("INVALID_PREVIEW_STROKE")
    # Reuse the G3.3e-a/b1 proof validator: mask indices are NEVER subject IDs.
    try:
        catalog = snapshot_mask_bindings(project)
    except (KeyError, TypeError, ValueError, MaskSnapshotError,
            SubjectIdentityError) as exc:
        raise SubjectBrushPreviewError("INVALID_SUBJECT_PROOF") from exc
    if (not catalog or catalog["subject_proof_schema_valid"] is not True
            or catalog["source_id"] != source_id):
        raise SubjectBrushPreviewError("INVALID_SUBJECT_PROOF")
    matches = [item for item in catalog["bindings"]
               if item["subject_id"] == subject_id]
    if len(matches) != 1:
        raise SubjectBrushPreviewError("SUBJECT_NOT_VERIFIED")
    item = matches[0]
    if (item["subject_proof_status"] != "verified"
            or item["subject_ambiguous"] is not False
            or item["mask_id"] != mask_id
            or item["mask_sha256_float32"] != mask_sha256_float32
            or item["has_foreground"] is not True):
        raise SubjectBrushPreviewError("SUBJECT_PROOF_MISMATCH")
    snapshot = project.document.get(SNAPSHOT_KEY)
    if not isinstance(snapshot, dict) or snapshot.get("editor_fingerprint") != source_sha256:
        raise SubjectBrushPreviewError("SUBJECT_SOURCE_MISMATCH")
    try:
        raw = decode_snapshot(snapshot, project.resources[SNAPSHOT_PATH])
    except (KeyError, TypeError, ValueError, MaskSnapshotError) as exc:
        raise SubjectBrushPreviewError("INVALID_BASE_MASK_SNAPSHOT") from exc
    count, height, width = snapshot["shape"]
    index = item["mask_index"]
    if type(index) is not int or not 0 <= index < count:
        raise SubjectBrushPreviewError("MASK_INDEX_OUT_OF_RANGE")
    stride = height * width * 4
    before_bytes = raw[index * stride:(index + 1) * stride]
    if sha256(before_bytes).hexdigest() != mask_sha256_float32:
        raise SubjectBrushPreviewError("MASK_FLOAT32_SHA_MISMATCH")
    command = {
        "version": 1, "width": width, "height": height,
        "count": count, "source": source_sha256,
        "strokes": [{"object": index, "mode": mode,
                     "radius": radius, "points": points}],
    }
    # Admission/preflight deliberately use stdlib only. Load the existing
    # CPU replay dependencies only when a real preview is requested.
    try:
        import numpy as np
        from smartsvg_editor.strokes import StrokeError, apply_strokes, decode
    except ImportError as exc:
        raise SubjectBrushPreviewError("BRUSH_RUNTIME_UNAVAILABLE") from exc
    try:
        validated = decode(json.dumps(command, allow_nan=False),
                           width=width, height=height, count=count,
                           fingerprint=source_sha256)
        # The G2.4 snapshot is little-endian float32. The replay engine
        # copies it; the original buffer and all other subjects stay intact.
        base = np.frombuffer(raw, dtype="<f4").reshape(count, height, width)
        base.flags.writeable = False
        corrected = apply_strokes(base, validated)
    except (StrokeError, TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise SubjectBrushPreviewError("INVALID_PREVIEW_STROKE") from exc
    if not np.array_equal(corrected[:index], base[:index]) or not np.array_equal(
            corrected[index + 1:], base[index + 1:]):
        raise SubjectBrushPreviewError("PREVIEW_TOUCHED_OTHER_SUBJECT")
    after_bytes = np.ascontiguousarray(corrected[index], dtype="<f4").tobytes()
    changed = int(np.count_nonzero(corrected[index] != base[index]))
    return {
        "subject_id": subject_id,
        "mask_id": mask_id,
        "source_sha256": source_sha256,
        "base_mask_sha256_float32": mask_sha256_float32,
        "preview_mask_sha256_float32": sha256(after_bytes).hexdigest(),
        "dimensions_px": [width, height],
        "changed_pixels": changed,
        "before_png_l8": encode_preview_l8(before_bytes, width, height),
        "after_png_l8": encode_preview_l8(after_bytes, width, height),
        "preview_float32": after_bytes,
        "cricut_certified": False,
        "persisted": False,
    }
