"""W03 Atelier export admission: selected verified Subject and physical width.

This module is UI-side validation only; the native exporter independently
rechecks archive SHA, mask proof, and physical constraints before any write.
"""
from __future__ import annotations

from pathlib import Path
import math
import re

_SHA = re.compile(r"^[0-9a-f]{64}$")
_SUBJECT = re.compile(r"^subject-[0-9a-f]{32}$")
_WIDTH = re.compile(r"^(?:[0-9]+)(?:[.,][0-9]{1,4})?$")


def ptc_preview_request(snapshot, subject, project_path, width_text):
    """Return a pinned read-only request, or None without changing UI state.

    Accept French decimal comma; reject exponent, NaN, ambiguous grouping,
    bool, non-verified subjects, and stale/malformed snapshot identifiers.
    """
    if (snapshot is None or subject is None
            or type(project_path) is not str
            or not Path(project_path).is_absolute()
            or type(width_text) is not str
            or not _WIDTH.fullmatch(width_text.strip())
            or type(getattr(snapshot, "sha256", None)) is not str
            or not _SHA.fullmatch(snapshot.sha256)
            or type(getattr(subject, "subject_id", None)) is not str
            or not _SUBJECT.fullmatch(subject.subject_id)
            or getattr(subject, "proof_status", None) != "verified"):
        return None
    try:
        width = float(width_text.strip().replace(",", "."))
    except (ValueError, OverflowError):
        return None
    if not math.isfinite(width) or not 0.01 <= width <= 10000:
        return None
    return {
        "project_path": project_path,
        "expected_sha256": snapshot.sha256,
        "subject_id": subject.subject_id,
        "width_mm": width,
    }
