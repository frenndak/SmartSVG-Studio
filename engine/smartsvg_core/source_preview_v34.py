"""V34-019 native PNG preview selection from an already validated V1 project.

The result contains only a bounded, verified source PNG, never an exported
Cricut artefact. No ComfyUI, Pillow, network, ZIP extraction or filesystem I/O.
The GUI may decode only this bounded result using the local Tk PNG decoder.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import PurePosixPath
import math
import struct

from .project_archive import LoadedProject

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_ENCODED_BYTES = 8 * 1024 * 1024
MAX_DECODED_PIXELS = 5_000_000
MAX_AXIS = 4096
MAX_SCREEN_WIDTH = 480
MAX_SCREEN_HEIGHT = 235


@dataclass(frozen=True)
class SourcePreview:
    status: str
    png: bytes = b""
    source_id: str = ""
    width_px: int = 0
    height_px: int = 0
    subsample: int = 1


def select_source_png(project: LoadedProject) -> SourcePreview:
    """Choose first displayable PNG source; never synthesize, resize or mutate it.

    Accepted input comes from the existing bounded and validated
    `load_project` path. Recheck the selected bytes against source metadata
    before passing them to a native UI decoder.
    """
    if not project.sources:
        return SourcePreview("NO_SOURCE")

    fallback = "SOURCE_FORMAT_UNSUPPORTED"
    for source in project.sources:
        path = project.source_paths.get(source.source_id)
        if not path or PurePosixPath(path).suffix.lower() != ".png":
            continue
        raw = project.resources.get(path)
        result = verified_png_preview(raw, source.source_id, source.sha256,
                                      source.width_px, source.height_px)
        if result.status != "SOURCE_TOO_LARGE":
            return result
        fallback = result.status
    return SourcePreview(fallback)


def verified_png_preview(raw, asset_id, expected_sha256, width_px, height_px):
    """Bound display of a PNG resource from an already validated V1 archive."""
    if raw is None:
        return SourcePreview("SOURCE_MISSING")
    if len(raw) > MAX_ENCODED_BYTES:
        return SourcePreview("SOURCE_TOO_LARGE")
    if (len(raw) < 33 or raw[:8] != PNG_SIGNATURE or
            raw[8:16] != b"\x00\x00\x00\rIHDR"):
        return SourcePreview("SOURCE_INVALID_PNG")
    width, height = struct.unpack(">II", raw[16:24])
    if (not width or not height or width > MAX_AXIS or height > MAX_AXIS or
            width * height > MAX_DECODED_PIXELS):
        return SourcePreview("SOURCE_TOO_LARGE")
    if (width, height) != (width_px, height_px) or sha256(raw).hexdigest() != expected_sha256:
        return SourcePreview("SOURCE_CHANGED")
    factor = max(1, math.ceil(width / MAX_SCREEN_WIDTH),
                 math.ceil(height / MAX_SCREEN_HEIGHT))
    return SourcePreview("READY_PNG", raw, asset_id, width, height, factor)
