"""G3.3e-b1: explicit persistent G1.2 Subject identity for an exact G2.4 mask.

This module never edits mask pixels or previews. It validates the ordered
float32 snapshot and returns an updated in-memory project; the managed
workspace remains responsible for revision locking and recovery persistence.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import re
import secrets
import struct

from .mask_snapshot_g24 import SNAPSHOT_KEY, SNAPSHOT_PATH, decode_snapshot, MaskSnapshotError
from .project_contracts import Subject
from .project_archive import LoadedProject

_SHA = re.compile(r"^[0-9a-f]{64}$")
_SUBJECT_ID = re.compile(r"^subject-[0-9a-f]{32}$")
_RECORD_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
BINDINGS_KEY = "subject_identity_bindings_g33e_b1"


class SubjectIdentityError(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _subject_id(existing, factory):
    for _ in range(8):
        token = factory()
        candidate = "subject-" + token
        if (isinstance(token, str) and re.fullmatch(r"[0-9a-f]{32}", token)
                and candidate not in existing):
            return candidate
    raise SubjectIdentityError("SUBJECT_ID_COLLISION")


def _validated_bindings(project):
    raw = project.document.get(BINDINGS_KEY)
    if raw is None:
        return []
    if (not isinstance(raw, dict) or set(raw) != {"version", "items"}
            or raw.get("version") != 1 or not isinstance(raw.get("items"), list)
            or len(raw["items"]) > 5000):
        raise SubjectIdentityError("INVALID_SUBJECT_IDENTITY_PROOF")
    subjects = {subject.subject_id: subject for subject in project.subjects}
    items, subject_ids, mask_ids = [], set(), set()
    required = {
        "subject_id", "source_id", "mask_id", "mask_sha256_float32",
    }
    for item in raw["items"]:
        if (not isinstance(item, dict) or set(item) != required
                or not _SUBJECT_ID.fullmatch(str(item.get("subject_id", "")))
                or not _RECORD_ID.fullmatch(str(item.get("source_id", "")))
                or not _RECORD_ID.fullmatch(str(item.get("mask_id", "")))
                or not _SHA.fullmatch(str(item.get("mask_sha256_float32", "")))):
            raise SubjectIdentityError("INVALID_SUBJECT_IDENTITY_PROOF")
        subject = subjects.get(item["subject_id"])
        if (subject is None or subject.source_id != item["source_id"]
                or subject.mask_id != item["mask_id"]
                or item["subject_id"] in subject_ids or item["mask_id"] in mask_ids):
            raise SubjectIdentityError("INVALID_SUBJECT_IDENTITY_PROOF")
        subject_ids.add(item["subject_id"])
        mask_ids.add(item["mask_id"])
        items.append(dict(item))
    return items


def _bbox_float32(chunk, width, height):
    left, top, right, bottom = width, height, -1, -1
    for index, (value,) in enumerate(struct.iter_unpack("<f", chunk)):
        if value >= 0.5:
            x, y = index % width, index // width
            left, top = min(left, x), min(top, y)
            right, bottom = max(right, x), max(bottom, y)
    if right < left or bottom < top:
        raise SubjectIdentityError("MASK_HAS_NO_G26_FOREGROUND")
    return (left, top, right - left + 1, bottom - top + 1)


def register_subject_identity(
    project: LoadedProject, *, mask_index, mask_id, mask_sha256_float32,
    source_id, source_sha256, subject_id_factory=None,
):
    """Create or recognize one persistent Subject from exact float32 evidence.

    Returns updated_project, subject, created. Existing accessories are
    preserved when the exact same Subject is recognized.
    """
    if (type(mask_index) is not int or mask_index < 0
            or not isinstance(mask_id, str)
            or not isinstance(mask_sha256_float32, str)
            or not _SHA.fullmatch(mask_sha256_float32)
            or not isinstance(source_id, str)
            or not isinstance(source_sha256, str)
            or not _SHA.fullmatch(source_sha256)):
        raise SubjectIdentityError("INVALID_SUBJECT_IDENTITY_REQUEST")
    bindings = _validated_bindings(project)
    snapshot = project.document.get(SNAPSHOT_KEY)
    if snapshot is None:
        raise SubjectIdentityError("BASE_MASK_SNAPSHOT_NOT_FOUND")
    if (len(project.sources) != 1 or project.sources[0].source_id != source_id
            or snapshot.get("editor_fingerprint") != source_sha256):
        raise SubjectIdentityError("SUBJECT_SOURCE_MISMATCH")
    try:
        raw = decode_snapshot(snapshot, project.resources[SNAPSHOT_PATH])
    except (KeyError, MaskSnapshotError) as exc:
        raise SubjectIdentityError("INVALID_BASE_MASK_SNAPSHOT") from exc
    count, height, width = snapshot["shape"]
    if mask_index >= count or mask_index >= len(project.masks):
        raise SubjectIdentityError("MASK_INDEX_OUT_OF_RANGE")
    record = project.masks[mask_index]
    if record.mask_id != mask_id or record.source_id != source_id:
        raise SubjectIdentityError("MASK_IDENTITY_MISMATCH")
    stride = width * height * 4
    chunks = [
        memoryview(raw)[index * stride:(index + 1) * stride]
        for index in range(count)
    ]
    digests = [sha256(chunk).hexdigest() for chunk in chunks]
    if digests[mask_index] != mask_sha256_float32:
        raise SubjectIdentityError("MASK_FLOAT32_SHA_MISMATCH")
    if digests.count(mask_sha256_float32) != 1:
        raise SubjectIdentityError("AMBIGUOUS_MASK_CONTENT")
    bbox = _bbox_float32(chunks[mask_index], width, height)

    linked = [subject for subject in project.subjects if subject.mask_id == mask_id]
    if len(linked) > 1:
        raise SubjectIdentityError("AMBIGUOUS_SUBJECT_IDENTITY")
    if linked:
        subject = linked[0]
        if subject.source_id != source_id or subject.bbox_px != bbox:
            raise SubjectIdentityError("SUBJECT_IDENTITY_CONFLICT")
        proof = [item for item in bindings
                 if item["subject_id"] == subject.subject_id]
        if not proof:
            raise SubjectIdentityError("SUBJECT_IDENTITY_PROOF_MISSING")
        expected = {
            "subject_id": subject.subject_id,
            "source_id": source_id,
            "mask_id": mask_id,
            "mask_sha256_float32": mask_sha256_float32,
        }
        if len(proof) != 1 or proof[0] != expected:
            raise SubjectIdentityError("SUBJECT_IDENTITY_PROOF_MISMATCH")
        return project, subject, False
    if any(item["mask_id"] == mask_id for item in bindings):
        raise SubjectIdentityError("SUBJECT_IDENTITY_PROOF_CONFLICT")

    existing = {subject.subject_id for subject in project.subjects}
    factory = subject_id_factory or (lambda: secrets.token_hex(16))
    subject = Subject(
        subject_id=_subject_id(existing, factory),
        source_id=source_id,
        mask_id=mask_id,
        bbox_px=bbox,
    )
    if len(project.operations) >= 4999:
        raise SubjectIdentityError("HISTORY_LIMIT")
    proof = {
        "subject_id": subject.subject_id,
        "source_id": source_id,
        "mask_id": mask_id,
        "mask_sha256_float32": mask_sha256_float32,
    }
    updated = replace(
        project,
        subjects=(*project.subjects, subject),
        document={
            **project.document,
            BINDINGS_KEY: {"version": 1, "items": [*bindings, proof]},
        },
        operations=[*project.operations, {
            "kind": "register_subject_identity_g33e_b1",
            "subject_id": subject.subject_id,
            "source_id": source_id,
            "mask_id": mask_id,
            "mask_sha256_float32": mask_sha256_float32,
        }],
    )
    return updated, subject, True
