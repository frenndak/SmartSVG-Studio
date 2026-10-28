"""G3.3e-a: read-only float32 mask identity evidence for a healthy project.

This is an *ordered snapshot binding*, not a new persistent Subject ID.
The G2.4 archive stores base-mask-00... by tensor position; an explicit
Subject record is the sole authority for an existing stable subject_id.
Never derive subject_id from preview order, 8-bit PNG or a mask digest.
"""
from __future__ import annotations

from hashlib import sha256
import struct

from .mask_snapshot_g24 import SNAPSHOT_KEY, SNAPSHOT_PATH, decode_snapshot


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
    bindings = []
    for index in range(count):
        mask = project.masks[index]
        chunk = memoryview(raw)[index * stride:(index + 1) * stride]
        references = by_mask.get(mask.mask_id, ())
        # A project can contain Subject records, but two Subjects may point to
        # the same Mask. That is not a unique identity for this binding.
        subject = references[0] if len(references) == 1 else None
        bindings.append({
            'mask_index': index,
            'mask_id': mask.mask_id,
            'mask_sha256_float32': sha256(chunk).hexdigest(),
            'has_foreground': any(value > 0 for (value,) in struct.iter_unpack('<f', chunk)),
            'subject_id': subject.subject_id if subject else None,
            'accessory_ids': list(subject.accessory_ids) if subject else [],
            'subject_ambiguous': len(references) > 1,
        })
    return {'version': 1, 'bindings': bindings,
            'source_id': project.sources[0].source_id,
            'identity_kind': 'snapshot_position_plus_float32_digest',
            'persistent_subject_ids': all(x['subject_id'] is not None for x in bindings)}
