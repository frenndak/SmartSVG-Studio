"""W04: read-only Basic Cut contours from a verified native V1 Subject.

The pinned native PTC renderer is reused solely to obtain the actual edited
subject alpha, not its output contract. Basic Cut emits vector paths, not PTC.
No file is opened for writing and no project or mask is modified.
"""
from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from .native_basic_cut_v35 import BasicCutError, preview_basic_cut
from .native_ptc_export_v35 import _render, _width_mm

_MAX_BOUNDARY_EDGES = 20000
_MAX_PIXELS = 5_000_000


@dataclass(frozen=True)
class NativeBasicCutSubjectPreview:
    status: str
    project_sha256: str
    subject_id: str
    source_sha256: str
    rendered_mask_sha256: str
    svg: bytes
    svg_sha256: str
    width_mm: float
    height_mm: float
    ring_count: int
    persisted: bool = False
    design_space_import_tested: bool = False
    physical_cut_tested: bool = False


def _mask_rings(alpha):
    """Trace edge-aligned 4-connected alpha silhouettes; refuse ambiguities.

    Each exterior/inner edge is oriented with the opaque pixel on its right.
    Four-way corner contacts are ambiguous in vector topology and rejected.
    """
    import numpy as np

    if alpha.ndim != 2 or not 1 <= alpha.size <= _MAX_PIXELS:
        raise BasicCutError("INVALID_ALPHA_DIMENSIONS")
    filled = alpha >= 128
    if not bool(filled.any()):
        raise BasicCutError("EMPTY_CUT_SILHOUETTE")
    pad = np.pad(filled, ((1, 1), (1, 1)), constant_values=False)
    # Check a small memory budget before materializing Python edge coordinates.
    # A noisy 5-Mpx mask can otherwise allocate millions of vertices first.
    boundaries = (filled & ~pad[:-2, 1:-1],
                  filled & ~pad[1:-1, 2:],
                  filled & ~pad[2:, 1:-1],
                  filled & ~pad[1:-1, :-2])
    if sum(int(np.count_nonzero(edge)) for edge in boundaries) > _MAX_BOUNDARY_EDGES:
        raise BasicCutError("SILHOUETTE_TOO_COMPLEX")
    top, right, bottom, left = (np.argwhere(edge) for edge in boundaries)
    following = {}

    def add(start, end):
        if start in following:
            raise BasicCutError("AMBIGUOUS_CORNER_CONTACT")
        following[start] = end

    for y, x in top:
        add((int(x), int(y)), (int(x) + 1, int(y)))
    for y, x in right:
        add((int(x) + 1, int(y)), (int(x) + 1, int(y) + 1))
    for y, x in bottom:
        add((int(x) + 1, int(y) + 1), (int(x), int(y) + 1))
    for y, x in left:
        add((int(x), int(y) + 1), (int(x), int(y)))

    rings = []
    while following:
        start = min(following)
        current = start
        ring = []
        while True:
            if current not in following:
                raise BasicCutError("OPEN_CUT_CONTOUR")
            ring.append(current)
            current = following.pop(current)
            if current == start:
                break
        # Remove straight intermediate pixel corners, preserving all turns.
        corners = []
        for i, point in enumerate(ring):
            before, after = ring[i - 1], ring[(i + 1) % len(ring)]
            if not (before[0] == point[0] == after[0] or
                    before[1] == point[1] == after[1]):
                corners.append(point)
        if len(corners) < 3:
            raise BasicCutError("DEGENERATE_CUT_CONTOUR")
        signed_twice_area = sum(
            a[0] * b[1] - b[0] * a[1]
            for a, b in zip(corners, corners[1:] + corners[:1]))
        if signed_twice_area == 0:
            raise BasicCutError("DEGENERATE_CUT_CONTOUR")
        rings.append((signed_twice_area, corners))
    # One connected foreground polygon with zero or more enclosed holes.
    outer = [corners for area, corners in rings if area > 0]
    holes = [corners for area, corners in rings if area < 0]
    if len(outer) != 1:
        raise BasicCutError("MULTIPLE_CUT_COMPONENTS")
    if len(rings) > 32 or sum(len(points) for _, points in rings) > 512:
        raise BasicCutError("SILHOUETTE_TOO_COMPLEX")
    # Sorting holes makes SVG output and SHA independent of traversal order.
    return [outer[0], *sorted(holes, key=lambda ring: min(ring))]


def inspect_native_basic_cut_subject(*, project_path, expected_sha256,
                                     subject_id, width_mm):
    """Inspect a verified edited V1 Subject and return an in-memory cut SVG.

    Native _render performs immutable SHA/CAS checks, validates the selected
    float32 mask, checks physical PPI/height and rereads the original PNG.
    Only the corrected alpha is traced. No export or disk write occurs.
    """
    rendered = _render(project_path=project_path, expected_sha256=expected_sha256,
                       subject_id=subject_id, width_mm=width_mm)
    from PIL import Image

    try:
        with Image.open(BytesIO(rendered["png"])) as png:
            # Check the decoder's header before expanding pixel buffers.
            # A highly compressible oversized PNG can otherwise allocate
            # far beyond the Basic Cut 5-Mpx budget before rejection.
            if (png.format != "PNG" or png.mode != "RGBA" or
                    list(png.size) != rendered["dimensions_px"] or
                    png.width * png.height > _MAX_PIXELS):
                raise BasicCutError("INVALID_RENDERED_PNG")
            png.load()
            import numpy as np
            alpha = np.asarray(png.getchannel("A"), dtype=np.uint8)
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        # Corrupt or truncated renderer bytes must fail with the public
        # Basic Cut admission error, not leak a Pillow decoder exception.
        raise BasicCutError("INVALID_RENDERED_PNG") from exc
    rings = _mask_rings(alpha)
    width_px, height_px = rendered["dimensions_px"]
    width = _width_mm(width_mm)
    # Preserve the renderer's physical aspect ratio without rounding
    # the supplied width or silently changing the mask coordinates.
    height = width * height_px / width_px
    scale = width / width_px
    # Map the terminal pixel border exactly to the physical viewBox edge.
    # Otherwise width_px * (width / width_px) can exceed width by one ULP.
    polygons = [tuple((width if x == width_px else x * scale,
                       height if y == height_px else y * scale)
                      for x, y in ring) for ring in rings]
    result = preview_basic_cut(rings=polygons, width_mm=width,
                               height_mm=height)
    return NativeBasicCutSubjectPreview(
        status="BASIC_CUT_PREVIEW_READY", project_sha256=rendered["project_sha256"],
        subject_id=rendered["subject_id"],
        source_sha256=rendered["source_sha256"],
        rendered_mask_sha256=rendered["rendered_mask_sha256"],
        svg=result.svg, svg_sha256=result.sha256,
        width_mm=result.width_mm, height_mm=result.height_mm,
        ring_count=result.ring_count)
