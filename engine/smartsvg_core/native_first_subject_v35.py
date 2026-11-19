"""W02: explicit first native Subject from one verified RGBA PNG alpha channel.

The preview is read-only. Confirmation reopens the exact CAS revision and
recomputes the alpha mask; only existing G2.2/G3.3e writers persist it.
No segmentation, hidden background removal, new archive format or auto-retry.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import re
import struct
import time
import zlib

from .mask_snapshot_g24 import SNAPSHOT_KEY, MAX_VALUES, encode_preview_l8
from .native_subject_preview_v34 import _workspace_from_path, NativeSubjectPreviewError
from .project_archive import load_project, ProjectArchiveError
from .project_workspace_g22 import WorkspaceError, _verify_png

_SHA = re.compile(r"^[0-9a-f]{64}$")
_PNG = b"\x89PNG\r\n\x1a\n"
_MAX_PIXELS = min(MAX_VALUES, 5_000_000)
MAX_MASK_PREVIEW_AXIS = 280


class NativeFirstSubjectError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _pinned_project(project_path, expected_sha256):
    if type(expected_sha256) is not str or not _SHA.fullmatch(expected_sha256):
        raise NativeFirstSubjectError("EXPECTED_REVISION_REQUIRED")
    try:
        workspace, name = _workspace_from_path(project_path)
        state = workspace.inspect(name)
        if state.get("status") != "PROJECT_HEALTHY":
            raise NativeFirstSubjectError("PROJECT_REQUIRES_REVIEW")
        if state.get("sha256") != expected_sha256:
            raise NativeFirstSubjectError("PROJECT_CHANGED")
        project = load_project(workspace._path(name), expected_sha256=expected_sha256)
    except NativeFirstSubjectError:
        raise
    except (NativeSubjectPreviewError, WorkspaceError, ProjectArchiveError,
            OSError, ValueError, TypeError) as exc:
        raise NativeFirstSubjectError("PROJECT_REQUIRES_REVIEW") from exc
    if project.project_id != name or len(project.sources) != 1:
        raise NativeFirstSubjectError("SOURCE_NOT_ELIGIBLE")
    return workspace, name, project


def _rgba_alpha_mask(png):
    """Decode *only* a pre-validated 8-bit non-interlaced RGBA PNG.

    PNG Sub/Up/Average/Paeth filters are reversed on each full RGBA scanline.
    Image bytes are never altered; alpha is normalized into contiguous <f4.
    """
    try:
        width, height, mode = _verify_png(png)
    except WorkspaceError as exc:
        raise NativeFirstSubjectError("INVALID_ARCHIVED_SOURCE") from exc
    if mode != "RGBA":
        raise NativeFirstSubjectError("MANUAL_SELECTION_REQUIRED")
    if width * height > _MAX_PIXELS:
        raise NativeFirstSubjectError("MASK_SNAPSHOT_TOO_LARGE")

    pos, chunks = 8, []
    while pos < len(png):
        length = struct.unpack_from(">I", png, pos)[0]
        kind = png[pos + 4:pos + 8]
        if kind == b"IDAT":
            chunks.append(png[pos + 8:pos + 8 + length])
        pos += length + 12
    stride = width * 4
    needed = height * (stride + 1)
    decoder = zlib.decompressobj()
    try:
        pixels = decoder.decompress(b"".join(chunks), needed + 1)
        if (len(pixels) != needed or not decoder.eof or
                decoder.unconsumed_tail or decoder.unused_data):
            raise ValueError("invalid inflation")
    except (zlib.error, ValueError) as exc:
        raise NativeFirstSubjectError("INVALID_ARCHIVED_SOURCE") from exc

    packed = bytearray(width * height * 4)
    lookup = tuple(struct.pack("<f", level / 255.0) for level in range(256))
    previous = bytearray(stride)
    bbox = [width, height, -1, -1]
    foreground = 0
    transparent = False
    for y in range(height):
        offset = y * (stride + 1)
        predictor = pixels[offset]
        row = bytearray(pixels[offset + 1:offset + 1 + stride])
        if predictor == 1:
            for i in range(4, stride):
                row[i] = (row[i] + row[i - 4]) & 255
        elif predictor == 2:
            for i in range(stride):
                row[i] = (row[i] + previous[i]) & 255
        elif predictor == 3:
            for i in range(stride):
                a = row[i - 4] if i >= 4 else 0
                b = previous[i]
                row[i] = (row[i] + (a + b) // 2) & 255
        elif predictor == 4:
            for i in range(stride):
                a = row[i - 4] if i >= 4 else 0
                b = previous[i]
                c = previous[i - 4] if i >= 4 else 0
                p = a + b - c
                da, db, dc = abs(p - a), abs(p - b), abs(p - c)
                row[i] = (row[i] + (a if da <= db and da <= dc
                                     else b if db <= dc else c)) & 255
        elif predictor != 0:
            raise NativeFirstSubjectError("INVALID_ARCHIVED_SOURCE")
        for x in range(width):
            alpha = row[4 * x + 3]
            if alpha != 255:
                transparent = True
            packed[(y * width + x) * 4:(y * width + x + 1) * 4] = lookup[alpha]
            if alpha >= 128:
                foreground += 1
                bbox[0] = min(bbox[0], x)
                bbox[1] = min(bbox[1], y)
                bbox[2] = max(bbox[2], x)
                bbox[3] = max(bbox[3], y)
        previous = row
    if not transparent or not foreground:
        raise NativeFirstSubjectError("MANUAL_SELECTION_REQUIRED")
    left, top, right, bottom = bbox
    return (bytes(packed), width, height, foreground,
            (left, top, right - left + 1, bottom - top + 1))


def _mask_preview_png(raw, width, height):
    """Bound the thumbnail and retain isolated foreground pixels when reduced."""
    step = (max(width, height) + MAX_MASK_PREVIEW_AXIS - 1) // MAX_MASK_PREVIEW_AXIS
    if step == 1:
        return encode_preview_l8(raw, width, height)
    columns = (width + step - 1) // step
    rows = (height + step - 1) // step
    peaks = [0.] * (columns * rows)
    for index, (opacity,) in enumerate(struct.iter_unpack("<f", raw)):
        y, x = divmod(index, width)
        cell = (y // step) * columns + x // step
        if opacity > peaks[cell]:
            peaks[cell] = opacity
    return encode_preview_l8(struct.pack(f"<{len(peaks)}f", *peaks), columns, rows)


def _candidate(project):
    asset = project.sources[0]
    png = project.resources[project.source_paths[asset.source_id]]
    if sha256(png).hexdigest() != asset.sha256:
        raise NativeFirstSubjectError("SOURCE_CHANGED")
    raw, width, height, foreground, bbox = _rgba_alpha_mask(png)
    if (asset.width_px, asset.height_px) != (width, height):
        raise NativeFirstSubjectError("SOURCE_CHANGED")
    image_digest = sha256(png).hexdigest()
    mask_digest = sha256(raw).hexdigest()
    # Stable, domain-separated native fingerprint, *not* a ComfyUI tensor hash.
    binding_digest = sha256(
        b"smartsvg-native-alpha-v35\x00" +
        bytes.fromhex(image_digest) + bytes.fromhex(mask_digest)).hexdigest()
    return raw, {
        "candidate_sha256": mask_digest,
        "image_fingerprint": image_digest,
        "editor_fingerprint": binding_digest,
        "dimensions_px": [width, height],
        "foreground_pixels": foreground,
        "bbox_px": list(bbox),
        "source_id": asset.source_id,
    }


def _existing_snapshot(project, candidate):
    if project.subjects:
        raise NativeFirstSubjectError("SUBJECT_ALREADY_PRESENT")
    if not project.masks:
        return False
    meta = project.document.get(SNAPSHOT_KEY)
    if (type(meta) is not dict or len(project.masks) != 1 or
            meta.get("shape") != [1, *candidate["dimensions_px"][::-1]] or
            meta.get("sha256_raw") != candidate["candidate_sha256"] or
            meta.get("image_fingerprint") != candidate["image_fingerprint"] or
            meta.get("editor_fingerprint") != candidate["editor_fingerprint"]):
        raise NativeFirstSubjectError("EXISTING_MASK_REQUIRES_REVIEW")
    return True


def inspect_first_alpha_subject(*, project_path, expected_sha256):
    """Return bounded evidence; never expose float32 data or write."""
    _workspace, _name, project = _pinned_project(project_path, expected_sha256)
    raw, candidate = _candidate(project)
    resume = _existing_snapshot(project, candidate)
    return {
        "status": "RESUME_MASK_BINDING" if resume else "ALPHA_PREVIEW_READY",
        "project_sha256": expected_sha256,
        **candidate,
        "mask_preview_png_l8": _mask_preview_png(raw, *candidate["dimensions_px"]),
        "preview_only": True, "persisted": False,
        "selection_kind": "whole_rgba_alpha",
        "manual_confirmation_required": True,
        "cricut_certified": False,
    }


def confirm_first_alpha_subject(*, project_path, expected_sha256,
                                candidate_sha256, confirmed=False):
    """Commit only the explicitly confirmed candidate via existing V1 writers.

    A failure can occur AFTER the mask or subject was written. Never retry
    automatically; a caller must re-inspect and re-confirm the new revision.
    """
    if confirmed is not True:
        raise NativeFirstSubjectError("ALPHA_CONFIRMATION_REQUIRED")
    if type(candidate_sha256) is not str or not _SHA.fullmatch(candidate_sha256):
        raise NativeFirstSubjectError("INVALID_ALPHA_CANDIDATE")
    workspace, name, project = _pinned_project(project_path, expected_sha256)
    raw, candidate = _candidate(project)
    if candidate_sha256 != candidate["candidate_sha256"]:
        raise NativeFirstSubjectError("ALPHA_CANDIDATE_CHANGED")
    resumed = _existing_snapshot(project, candidate)
    current_sha = expected_sha256
    if not resumed:
        try:
            saved = workspace.save_base_masks(
                name, raw_float32=raw,
                shape=[1, *candidate["dimensions_px"][::-1]],
                image_fingerprint=candidate["image_fingerprint"],
                editor_fingerprint=candidate["editor_fingerprint"],
                expected_sha256=current_sha)
            current_sha = saved["sha256"]
        except (WorkspaceError, OSError, KeyError, TypeError, ValueError) as exc:
            raise NativeFirstSubjectError("MASK_PUBLICATION_UNCERTAIN") from exc
    # Phase 1 is durable. Re-inspect exact bytes before an independent phase 2.
    _workspace, _name, persisted = _pinned_project(project_path, current_sha)
    if not _existing_snapshot(persisted, candidate):
        raise NativeFirstSubjectError("MASK_PUBLICATION_UNCERTAIN")
    state = workspace.inspect(name)
    try:
        catalog = state["base_masks"]["mask_identity"]
        if (catalog.get("source_id") != candidate["source_id"] or
                catalog.get("subject_proof_schema_valid") is not True or
                len(catalog["bindings"]) != 1):
            raise NativeFirstSubjectError("MASK_BINDING_UNVERIFIED")
        binding = catalog["bindings"][0]
        if (binding.get("subject_proof_status") != "unbound" or
                binding.get("mask_sha256_float32") != candidate["candidate_sha256"] or
                binding.get("mask_id") != "base-mask-00" or
                binding.get("has_foreground") is not True):
            raise NativeFirstSubjectError("MASK_BINDING_UNVERIFIED")
        bound = workspace.register_subject_identity(
            name, mask_index=0, mask_id=binding["mask_id"],
            mask_sha256_float32=binding["mask_sha256_float32"],
            source_id=catalog["source_id"],
            source_sha256=candidate["editor_fingerprint"],
            expected_sha256=current_sha, confirmed=True,
            expires_at_ms=int(time.time() * 1000) + 60_000)
    except NativeFirstSubjectError:
        raise
    except (WorkspaceError, OSError, KeyError, IndexError, TypeError,
            ValueError) as exc:
        raise NativeFirstSubjectError("SUBJECT_BINDING_OUTCOME_UNCERTAIN") from exc
    _workspace, _name, reopened = _pinned_project(project_path, bound["sha256"])
    if (len(reopened.subjects) != 1 or
            reopened.subjects[0].subject_id != bound["subject_id"] or
            list(reopened.subjects[0].bbox_px) != candidate["bbox_px"]):
        raise NativeFirstSubjectError("SUBJECT_BINDING_OUTCOME_UNCERTAIN")
    return {
        "status": "FIRST_SUBJECT_CREATED",
        "project_sha256": bound["sha256"],
        "subject_id": bound["subject_id"],
        "mask_id": "base-mask-00",
        "persisted": True, "cricut_certified": False,
    }
