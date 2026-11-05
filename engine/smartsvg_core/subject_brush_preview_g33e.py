"""G3.3e-b2a (core slice): one read-only brush preview for a proven G1.2 Subject.

This is an in-memory primitive, NOT an HTTP endpoint or a save operation.
The caller must load a healthy archive and enforce project revision/CAS before
and after calling it. UI, cancellation and late-result guards are separate.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re

from .editor_session_g23 import EditorSessionError, parse_editor_document
from .mask_binding_g33e import snapshot_mask_bindings
from .mask_snapshot_g24 import (
    SNAPSHOT_KEY, SNAPSHOT_PATH, MaskSnapshotError, decode_snapshot,
    encode_preview_l8,
)
from .subject_identity_g33e import SubjectIdentityError

_SUBJECT_ID = re.compile(r"^subject-[0-9a-f]{32}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")
MAX_PREVIEW_POINTS = 64


def _other_masks_bit_identical(raw, masks, target_index, stride):
    """Reject any non-target float32 byte change, including signed zero.

    Numeric equality is insufficient for G2.4 snapshots: +0.0 and -0.0
    compare equal as floats but are different persisted IEEE-754 payloads.
    Iterate one mask at a time to avoid allocating a second full snapshot.
    """
    for index, candidate in enumerate(masks):
        if index != target_index and candidate != raw[index * stride:(index + 1) * stride]:
            return False
    return True


class SubjectBrushPreviewError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def preview_subject_brush(
    project, *, subject_id, mask_id, mask_sha256_float32,
    source_id, source_sha256, mode, radius, points,
):
    """Preview ONE add/erase stroke after saved strokes; never alter the base.

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
    # Validate the same G2.3 stroke contract before importing optional CPU
    # dependencies. Invalid user gestures must not be reported as a missing
    # NumPy/Pillow runtime, and G0 can exercise these failures with stdlib.
    try:
        editor, canonical = parse_editor_document(
            json.dumps(command, allow_nan=False),
            source_dimensions=(width, height),
        )
    except (EditorSessionError, TypeError, ValueError, OverflowError,
            RecursionError) as exc:
        raise SubjectBrushPreviewError("INVALID_PREVIEW_STROKE") from exc
    session = project.document.get('editor_v216')
    if session is not None:
        try:
            previous, _ = parse_editor_document(
                json.dumps(session, allow_nan=False), source_dimensions=(width, height))
            if previous['source'] != source_sha256 or previous['count'] != count:
                raise EditorSessionError('INCOMPATIBLE_EDITOR_SOURCE')
        except (EditorSessionError, TypeError, ValueError, OverflowError, RecursionError) as exc:
            raise SubjectBrushPreviewError('INVALID_SAVED_EDITOR_SESSION') from exc
        try:
            editor, canonical = parse_editor_document(json.dumps({
                **editor, 'strokes': [*previous['strokes'], *editor['strokes']]
            }, allow_nan=False), source_dimensions=(width, height))
        except (EditorSessionError, TypeError, ValueError, OverflowError, RecursionError) as exc:
            raise SubjectBrushPreviewError('BRUSH_SESSION_LIMIT') from exc
    try:
        import numpy as np
        from smartsvg_editor.strokes import StrokeError, apply_strokes, decode
    except ImportError as exc:
        raise SubjectBrushPreviewError("BRUSH_RUNTIME_UNAVAILABLE") from exc
    try:
        validated = decode(canonical,
                           width=width, height=height, count=count,
                           fingerprint=source_sha256)
        # The G2.4 snapshot is little-endian float32. The replay engine
        # copies it; the original buffer and all other subjects stay intact.
        base = np.frombuffer(raw, dtype="<f4").reshape(count, height, width)
        base.flags.writeable = False
        # Reuse the native replay for BOTH the saved state and the new gesture.
        before = apply_strokes(base, validated[:-1]) if len(validated) > 1 else base
        corrected = apply_strokes(before, validated[-1:])
    except (StrokeError, TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise SubjectBrushPreviewError("INVALID_PREVIEW_STROKE") from exc
    # Compare raw IEEE-754 payloads, not numerical values: np.array_equal
    # would accept a change from +0.0 to -0.0 in an untouched Subject.
    # Keep the G2.4 byte-for-byte invariant without copying every mask at once.
    if (corrected.shape != base.shape or corrected.dtype != base.dtype or
            not _other_masks_bit_identical(
                memoryview(before).cast('B'),
                (corrected[i].tobytes(order="C") for i in range(count)),
                index, stride)):
        raise SubjectBrushPreviewError("PREVIEW_TOUCHED_OTHER_SUBJECT")
    after_bytes = np.ascontiguousarray(corrected[index], dtype="<f4").tobytes()
    before_bytes = before[index].tobytes(order='C')
    changed = int(np.count_nonzero(corrected[index] != before[index]))
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
        "editor_document": editor,  # internal-only writer input, never UI authority
        "cricut_certified": False,
        "persisted": False,
    }
