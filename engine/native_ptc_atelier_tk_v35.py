"""W03 Atelier export admission: selected verified Subject and physical width.

This module is UI-side validation only; the native exporter independently
rechecks archive SHA, mask proof, and physical constraints before any write.
"""
from __future__ import annotations

from pathlib import Path
import math
import re
from smartsvg_core.source_preview_v34 import MAX_ENCODED_BYTES

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


def ptc_atelier_action_ready(snapshot, subject, project_path):
    """Enable native PTC inspection independently of the brush's 2048px cap.

    A verified subject must have a usable inspector preview, but the preview
    may be downsampled and is never the source of physical/PPI validation.
    The native read-only inspect rechecks the full V1 archive before export.
    """
    if ptc_preview_request(snapshot, subject, project_path, "100") is None:
        return False
    preview = getattr(subject, "preview", None)
    if preview is None or getattr(preview, "status", None) != "READY_PNG":
        return False
    png = getattr(preview, "png", None)
    return (
        type(png) is bytes
        and 33 <= len(png) <= MAX_ENCODED_BYTES
        and type(getattr(preview, "width_px", None)) is int
        and type(getattr(preview, "height_px", None)) is int
        and preview.width_px > 0 and preview.height_px > 0
    )


def ptc_physical_feedback(request, width_px, height_px):
    """Preflight the native renderer's physical bounds without writing.

    Returns an actionable French message, or None if the geometry is eligible.
    The native renderer remains authoritative for source and mask validation.
    """
    if (type(request) is not dict or
            type(request.get("width_mm")) is not float or
            type(width_px) is not int or type(height_px) is not int or
            width_px <= 0 or height_px <= 0 or
            width_px * height_px > 5_000_000):
        return "Dimensions de source indisponibles ou trop grandes : réexaminer le projet (F5)."
    width_mm = request["width_mm"]
    if not math.isfinite(width_mm) or not 0.01 <= width_mm <= 10000:
        return "Largeur physique invalide : saisir une valeur entre 0,01 et 10 000 mm."
    ppi = width_px * 25.4 / width_mm
    height_mm = height_px * width_mm / width_px
    if ppi > 2400:
        return "Largeur trop petite pour cette image (plus de 2 400 ppp). Augmenter les millimètres."
    if ppi < 1:
        return "Largeur trop grande pour cette image (moins de 1 ppp). Réduire les millimètres."
    if height_mm < 0.01 or height_mm > 10000:
        return "Hauteur calculée hors limites (0,01 à 10 000 mm). Adapter la largeur."
    return None
