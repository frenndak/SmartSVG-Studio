"""Read-only subject inspection of one already validated V1 archive."""
from __future__ import annotations

from dataclasses import dataclass

from .mask_binding_g33e import snapshot_mask_bindings
from .source_preview_v34 import MAX_ENCODED_BYTES, SourcePreview, verified_png_preview


@dataclass(frozen=True)
class AtelierSubject:
    subject_id: str
    source_id: str
    mask_id: str
    bbox_px: tuple[int, int, int, int]
    proof_status: str
    preview: SourcePreview


@dataclass(frozen=True)
class AtelierSnapshot:
    project_id: str
    sha256: str
    subjects: tuple[AtelierSubject, ...]


def inspect_atelier_snapshot(project, sha256: str) -> AtelierSnapshot:
    """Use persisted IDs and archive previews, never export float32 pixels."""
    evidence = snapshot_mask_bindings(project) if project.subjects else None
    bindings = {item['mask_id']: item for item in evidence['bindings']} if evidence else {}
    masks = {mask.mask_id: mask for mask in project.masks}
    previews = {}
    remaining = MAX_ENCODED_BYTES
    subjects = []
    for subject in project.subjects:
        mask = masks[subject.mask_id]
        if mask.mask_id not in previews:
            raw = project.resources[project.mask_paths[mask.mask_id]]
            if len(raw) <= remaining:
                preview = verified_png_preview(raw, mask.mask_id, mask.sha256,
                                               mask.width_px, mask.height_px)
                remaining -= len(preview.png)
            else:
                preview = SourcePreview('SOURCE_TOO_LARGE')
            previews[mask.mask_id] = preview
        binding = bindings.get(mask.mask_id)
        proof_status = 'png_only'
        if binding is not None:
            proof_status = (binding['subject_proof_status']
                            if binding['subject_id'] == subject.subject_id else 'unverified')
        subjects.append(AtelierSubject(
            subject.subject_id, subject.source_id, subject.mask_id, subject.bbox_px,
            proof_status, previews[mask.mask_id]))
    return AtelierSnapshot(project.project_id, sha256, tuple(subjects))
