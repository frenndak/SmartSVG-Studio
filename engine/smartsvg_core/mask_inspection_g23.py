"""G2.3: validate user-supplied L8 masks and measure actual nonzero silhouettes.

This is not vector tracing and is NOT a Cricut cut-quality certification.
8-bit non-interlaced grayscale PNG only; fail closed for unsupported layouts.
No Pillow, scripts, source file reads, or arbitrary filesystem paths.
"""
from __future__ import annotations

import struct
import zlib

from .project_workspace_g22 import WorkspaceError, MAX_IMAGE_BYTES, MAX_PIXELS

MAGIC = b'\x89PNG\r\n\x1a\n'


def _paeth(a, b, c):
    p = a + b - c
    da, db, dc = abs(p - a), abs(p - b), abs(p - c)
    return a if da <= db and da <= dc else b if db <= dc else c


def inspect_l8_mask(data: bytes, width: int, height: int) -> dict:
    """Returns bbox [x,y,w,h] and pixel count. Pixel >=128 is foreground.

    Iterates all actual pixels; a source-size PNG with a fake IHDR, bad CRC,
    truncated IDAT, invalid filters, empty or full-frame mask is refused.
    """
    if (not isinstance(data, bytes) or len(data) < 50 or
            len(data) > MAX_IMAGE_BYTES or not data.startswith(MAGIC) or
            type(width) is not int or type(height) is not int or
            width < 1 or height < 1 or width * height > MAX_PIXELS):
        raise WorkspaceError('INVALID_MASK_PNG')
    cursor, started, ended, seen_data, after_data = 8, False, False, False, False
    chunks = []
    while cursor < len(data):
        if cursor + 12 > len(data):
            raise WorkspaceError('INVALID_MASK_PNG')
        size = struct.unpack('>I', data[cursor:cursor + 4])[0]
        if size > MAX_IMAGE_BYTES or cursor + size + 12 > len(data):
            raise WorkspaceError('INVALID_MASK_PNG')
        tag = data[cursor + 4:cursor + 8]
        chunk = data[cursor + 8:cursor + 8 + size]
        expected_crc = struct.unpack('>I', data[cursor + 8 + size:cursor + 12 + size])[0]
        if zlib.crc32(tag + chunk) & 0xffffffff != expected_crc:
            raise WorkspaceError('MASK_PNG_CRC_FAILED')
        cursor += 12 + size
        if not started and tag != b'IHDR':
            raise WorkspaceError('INVALID_MASK_PNG')
        if tag == b'IHDR':
            if started or size != 13:
                raise WorkspaceError('INVALID_MASK_PNG')
            w, h, depth, color, comp, filtering, interlace = struct.unpack('>IIBBBBB', chunk)
            if (w, h) != (width, height):
                raise WorkspaceError('MASK_DIMENSIONS_MISMATCH')
            if (depth, color, comp, filtering, interlace) != (8, 0, 0, 0, 0):
                raise WorkspaceError('MASK_NOT_L8')
            started = True
        elif tag == b'IDAT':
            if after_data:
                raise WorkspaceError('INVALID_MASK_PNG')
            seen_data = True
            chunks.append(chunk)
        elif tag == b'IEND':
            if not seen_data or size != 0 or cursor != len(data):
                raise WorkspaceError('INVALID_MASK_PNG')
            ended = True
            break
        else:
            if seen_data:
                after_data = True
            # Safe to ignore ancillary chunks; unknown critical chunks rejected.
            if tag != b'PLTE' and tag and 65 <= tag[0] <= 90:
                raise WorkspaceError('UNSUPPORTED_MASK_CHUNK')
    if not ended or not seen_data:
        raise WorkspaceError('INVALID_MASK_PNG')
    expected = height * (width + 1)
    if expected > MAX_PIXELS + height:
        raise WorkspaceError('MASK_PIXELS_TOO_LARGE')
    try:
        decoder = zlib.decompressobj()
        raw = decoder.decompress(b''.join(chunks), expected + 1)
        if (len(raw) != expected or not decoder.eof or
                decoder.unused_data or decoder.unconsumed_tail):
            raise WorkspaceError('INVALID_MASK_PIXELS')
    except zlib.error as exc:
        raise WorkspaceError('INVALID_MASK_PIXELS') from exc

    previous = bytearray(width)
    left, top, right, bottom = width, height, -1, -1
    selected = 0
    for y in range(height):
        start = y * (width + 1)
        filt = raw[start]
        values = bytearray(raw[start + 1:start + 1 + width])
        if filt > 4:
            raise WorkspaceError('INVALID_MASK_FILTER')
        for x in range(width):
            a = values[x - 1] if x else 0
            b = previous[x]
            c = previous[x - 1] if x else 0
            if filt == 1:
                values[x] = (values[x] + a) & 255
            elif filt == 2:
                values[x] = (values[x] + b) & 255
            elif filt == 3:
                values[x] = (values[x] + ((a + b) // 2)) & 255
            elif filt == 4:
                values[x] = (values[x] + _paeth(a, b, c)) & 255
            if values[x] >= 128:
                selected += 1
                left = min(left, x)
                right = max(right, x)
                top = min(top, y)
                bottom = max(bottom, y)
        previous = values
    if selected == 0:
        raise WorkspaceError('MASK_EMPTY')
    if selected == width * height:
        raise WorkspaceError('MASK_FULL_FRAME')
    return {'bbox_px': (left, top, right - left + 1, bottom - top + 1),
            'selected_pixels': selected, 'width_px': width, 'height_px': height,
            'cut_certified': False}
