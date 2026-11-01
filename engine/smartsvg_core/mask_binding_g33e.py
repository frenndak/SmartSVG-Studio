"""G3.3e-a: read-only float32 mask identity evidence for a healthy project.

This is an *ordered snapshot binding*, not a new persistent Subject ID.
The G2.4 archive stores base-mask-00... by tensor position; an explicit
Subject record is the sole authority for an existing stable subject_id.
Never derive subject_id from preview order, 8-bit PNG or a mask digest.
"""
from __future__ import annotations

from hashlib import sha256
import re
import struct

from .mask_snapshot_g24 import SNAPSHOT_KEY, SNAPSHOT_PATH, decode_snapshot
from .subject_identity_g33e import (
    SubjectIdentityError, validated_subject_identity_bindings,
)

_B1_SUBJECT_ID = re.compile(r'^subject-[0-9a-f]{32}$')


def snapshot_mask_bindings(project):
    """Return bounded metadata only; no mask bytes leave the trusted server.

    The caller has already validated the .smartsvg archive, including each
    preview's exact relationship to its float32 snapshot. Decode only the
    bounded G2.4 resource. Never rewrite, quantize or return mask pixels.
    """
    snapshot = project.document.get(SNAPSHOT_KEY)
    if snapshot is None:
        return None
    raw = decode_snapshot(snapshot, project.resources[SNAPSHOT_PATH])
    count, height, width = snapshot['shape']
    stride = width * height * 4
    by_mask = {}
    for subject in project.subjects:
        by_mask.setdefault(subject.mask_id, []).append(subject)
    try:
        proofs = validated_subject_identity_bindings(project)
        proof_schema_valid = True
    except SubjectIdentityError:
        proofs = []
        proof_schema_valid = False
    by_subject_proof = {}
    for proof in proofs:
        by_subject_proof.setdefault(proof["subject_id"], []).append(proof)
    bindings = []
    proof_content_valid = True
    for index in range(count):
        mask = project.masks[index]
        chunk = memoryview(raw)[index * stride:(index + 1) * stride]
        references = by_mask.get(mask.mask_id, ())
        digest = sha256(chunk).hexdigest()
        # A Subject is exposed as persistent only when its authoritative b1
        # proof covers the exact source fingerprint and float32 slice.
        subject = references[0] if len(references) == 1 else None
        proof_status = 'unbound' if not references else 'ambiguous'
        if subject is not None:
            if not _B1_SUBJECT_ID.fullmatch(subject.subject_id):
                # Preserve the frozen G3.3e-a contract for pre-b1 G1.2 records.
                # Only IDs minted by b1 claim the new exact-proof semantics.
                proof_status = 'legacy_subject_record'
            else:
                expected = {
                    'subject_id': subject.subject_id,
                    'source_id': subject.source_id,
                    'source_sha256': snapshot['editor_fingerprint'],
                    'mask_id': mask.mask_id,
                    'mask_sha256_float32': digest,
                }
                candidates = by_subject_proof.get(subject.subject_id, ())
                if not proof_schema_valid:
                    proof_status, subject = 'invalid', None
                elif len(candidates) != 1:
                    proof_status, subject = 'missing', None
                elif candidates[0] != expected:
                    proof_status, subject = 'mismatch', None
                else:
                    proof_status = 'verified'
        if proof_status in ('invalid', 'missing', 'mismatch'):
            proof_content_valid = False
        bindings.append({
            'mask_index': index,
            'mask_id': mask.mask_id,
            'mask_sha256_float32': digest,
            'has_foreground': any(value >= 0.5 for (value,) in struct.iter_unpack('<f', chunk)),
            'subject_id': subject.subject_id if subject else None,
            'accessory_ids': list(subject.accessory_ids) if subject else [],
            'subject_ambiguous': len(references) > 1,
            'subject_proof_status': proof_status,
        })
    return {'version': 1, 'bindings': bindings,
            'source_id': project.sources[0].source_id,
            'identity_kind': 'snapshot_position_plus_float32_digest',
            'subject_proof_schema_valid': proof_schema_valid and proof_content_valid,
            'persistent_subject_ids': all(x['subject_id'] is not None for x in bindings)}
