"""G1.3 portable .smartsvg ZIP projects with bounded, fail-closed loading.

This is a byte-preserving *project* format, not a Cricut-compatible export.
No archives are extracted to disk and no external references are followed.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from io import BytesIO
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import struct
import tempfile
import unicodedata
import zipfile
import zlib
import xml.etree.ElementTree as ET

from .project_contracts import (
    Artifact, Mask, QAResult, SourceAsset, Subject, RecordError,
    record_dict, validate_project_records, _WINDOWS_DEVICE, _WINDOWS_FORBIDDEN,
)

SCHEMA_VERSION = 'smartsvg-project/1'
MAX_ENTRIES = 256
MAX_MEMBER_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
MAX_ARCHIVE_BYTES = 280 * 1024 * 1024
MAX_JSON_BYTES = 4 * 1024 * 1024
JSON_FILES = ('document.json', 'operations.json', 'sources.json', 'masks.json',
              'subjects.json', 'artifacts.json', 'proofs/qa_results.json')
VALID_ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$')
PNG_MAGIC = b'\x89PNG\r\n\x1a\n'


class ProjectArchiveError(ValueError):
    """Untrusted project was rejected or atomic persistence failed."""


@dataclass(frozen=True)
class LoadedProject:
    project_id: str
    app_version: str
    sources: tuple[SourceAsset, ...]
    masks: tuple[Mask, ...]
    subjects: tuple[Subject, ...]
    artifacts: tuple[Artifact, ...]
    qa_results: tuple[QAResult, ...]
    document: dict
    operations: list
    resources: dict[str, bytes]
    source_paths: dict[str, str]
    mask_paths: dict[str, str]


def _digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def _safe_path(path: str) -> str:
    """Portable path aligned with G1.2: accept safe visible Unicode and spaces.

    Validate on both save and load, without extracting ZIP members to disk.
    """
    if (not isinstance(path, str) or not path or len(path) > 512 or
            '\\' in path or ':' in path):
        raise ProjectArchiveError('UNSAFE_ARCHIVE_PATH')
    p = PurePosixPath(path)
    parts = path.split('/')
    if (p.is_absolute() or p.as_posix() != path or
            any(part in ('', '.', '..') for part in parts) or
            any(char in _WINDOWS_FORBIDDEN or
                unicodedata.category(char) in ('Cc', 'Cf', 'Cs', 'Zl', 'Zp')
                or char == '\u034f' or
                0xFE00 <= ord(char) <= 0xFE0F or
                0xE0100 <= ord(char) <= 0xE01EF
                for char in path) or
            any(part.endswith(('.', ' ')) or
                _WINDOWS_DEVICE.fullmatch(part) or
                len(part.encode('utf-8')) > 255 for part in parts)):
        raise ProjectArchiveError('UNSAFE_ARCHIVE_PATH')
    return path


def _object_pairs(pairs):
    data = {}
    for k, v in pairs:
        if k in data:
            raise ProjectArchiveError('DUPLICATE_JSON_KEY')
        data[k] = v
    return data


def _reject_constant(_):
    raise ProjectArchiveError('NONFINITE_JSON_NUMBER')


def _check_json_structure(value, depth=0):
    # Avoid recursively hostile documents accepted by JSON but unusable in the UI.
    if depth > 32:
        raise ProjectArchiveError('JSON_NESTING_TOO_DEEP')
    if isinstance(value, dict):
        if len(value) > 50000:
            raise ProjectArchiveError('JSON_TOO_MANY_FIELDS')
        for key, item in value.items():
            if not isinstance(key, str) or len(key) > 512:
                raise ProjectArchiveError('INVALID_JSON_KEY')
            _check_json_structure(item, depth + 1)
    elif isinstance(value, list):
        if len(value) > 50000:
            raise ProjectArchiveError('JSON_TOO_MANY_ITEMS')
        for item in value:
            _check_json_structure(item, depth + 1)
    elif not (value is None or isinstance(value, (str, bool, int, float))):
        raise ProjectArchiveError('INVALID_JSON_TYPE')


def _json_bytes(value) -> bytes:
    _check_json_structure(value)
    try:
        encoded = json.dumps(value, allow_nan=False, sort_keys=True,
                             separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise ProjectArchiveError('INVALID_JSON_DATA') from exc
    if len(encoded) > MAX_JSON_BYTES:
        raise ProjectArchiveError('JSON_TOO_LARGE')
    return encoded


def _parse_json(data: bytes):
    if len(data) > MAX_JSON_BYTES:
        raise ProjectArchiveError('JSON_TOO_LARGE')
    try:
        value = json.loads(data.decode('utf-8'), object_pairs_hook=_object_pairs,
                           parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ProjectArchiveError('INVALID_JSON_DATA') from exc
    _json_bytes(value)  # normalizes bounds and non-finite validation
    return value


def _png_size(data: bytes, *, grayscale: bool) -> tuple[int, int]:
    if len(data) < 33 or not data.startswith(PNG_MAGIC):
        raise ProjectArchiveError('INVALID_PNG_HEADER')
    if data[12:16] != b'IHDR' or struct.unpack('>I', data[8:12])[0] != 13:
        raise ProjectArchiveError('INVALID_PNG_HEADER')
    if zlib.crc32(data[12:29]) & 0xffffffff != struct.unpack('>I', data[29:33])[0]:
        raise ProjectArchiveError('PNG_IHDR_CRC_FAILED')
    w, h, depth, color, compression, filtering, interlace = struct.unpack('>IIBBBBB', data[16:29])
    if not w or not h or w * h > 100_000_000 or (compression, filtering) != (0, 0):
        raise ProjectArchiveError('INVALID_PNG_DIMENSIONS')
    if grayscale and (depth, color, interlace) != (8, 0, 0):
        raise ProjectArchiveError('MASK_NOT_L8_PNG')
    return w, h


def _jpeg_source_info(data: bytes) -> tuple[tuple[int, int], str]:
    """Validate bounded JPEG marker structure and infer L/RGB from the frame.

    This checks SOI/SOF/SOS/EOI, segment bounds, and scan marker escaping.
    It does not entropy-decode pixels or apply EXIF orientation.
    """
    if not data.startswith(b'\xff\xd8'):
        raise ProjectArchiveError('INVALID_JPEG')
    offset = 2
    dimensions = None
    color_mode = None
    scan_found = False
    in_scan = False
    sof_markers = {0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7,
                   0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf}
    while offset < len(data):
        if in_scan:
            # Compressed data can contain FF00 stuffing and RST0..RST7;
            # neither is a new JPEG segment. Progressive JPEG may contain
            # multiple scans with tables between them.
            while offset < len(data):
                if data[offset] != 0xff:
                    offset += 1
                    continue
                end = offset + 1
                while end < len(data) and data[end] == 0xff:
                    end += 1
                if end >= len(data):
                    break
                marker = data[end]
                if marker == 0 or 0xd0 <= marker <= 0xd7:
                    offset = end + 1
                    continue
                offset = end - 1
                in_scan = False
                break
            if in_scan:
                break
        if data[offset] != 0xff:
            raise ProjectArchiveError('INVALID_JPEG_MARKER')
        while offset < len(data) and data[offset] == 0xff:
            offset += 1
        if offset >= len(data):
            break
        marker = data[offset]
        offset += 1
        if marker == 0xd9:  # EOI must finish the file, after real scan data
            if dimensions and scan_found and offset == len(data):
                return dimensions, color_mode
            raise ProjectArchiveError('INVALID_JPEG_END')
        if marker in (0xd8, 0x00, 0x01) or 0xd0 <= marker <= 0xd7:
            raise ProjectArchiveError('INVALID_JPEG_MARKER')
        if offset + 2 > len(data):
            break
        segment_size = int.from_bytes(data[offset:offset + 2], 'big')
        if segment_size < 2 or offset + segment_size > len(data):
            raise ProjectArchiveError('INVALID_JPEG_SEGMENT')
        if marker in sof_markers:
            if dimensions is not None or segment_size < 8:
                raise ProjectArchiveError('INVALID_JPEG_FRAME')
            precision = data[offset + 2]
            height = int.from_bytes(data[offset + 3:offset + 5], 'big')
            width = int.from_bytes(data[offset + 5:offset + 7], 'big')
            components = data[offset + 7]
            # Four-component CMYK and >8-bit JPEG require an explicit
            # conversion; G1.2 only represents L, RGB or RGBA accurately.
            if (precision != 8 or not width or not height or
                    width * height > 100_000_000 or components not in (1, 3) or
                    segment_size != 8 + 3 * components):
                raise ProjectArchiveError('UNSUPPORTED_JPEG_FRAME')
            dimensions = (width, height)
            color_mode = 'L' if components == 1 else 'RGB'
        if marker == 0xda:  # Start of Scan
            if (dimensions is None or segment_size < 6 or
                    segment_size != 6 + 2 * data[offset + 2]):
                raise ProjectArchiveError('INVALID_JPEG_SCAN')
            scan_found = True
            in_scan = True
        offset += segment_size
    raise ProjectArchiveError('INCOMPLETE_JPEG')


def _source_dimensions(path: str, data: bytes) -> tuple[int, int]:
    suffix = PurePosixPath(path).suffix.lower()
    if suffix == '.png':
        return _png_size(data, grayscale=False)
    if suffix in ('.jpg', '.jpeg'):
        return _jpeg_source_info(data)[0]
    if suffix == '.webp':
        # RIFF is a chunked container. The header alone is not enough: the
        # declared RIFF length must cover the whole resource, every chunk
        # must fit and static images must contain a frame chunk. This remains
        # a structural preflight, NOT a compressed-pixel decoder.
        if (len(data) < 26 or data[:4] != b'RIFF' or data[8:12] != b'WEBP'
                or int.from_bytes(data[4:8], 'little') != len(data) - 8):
            raise ProjectArchiveError('INVALID_WEBP_HEADER')
        chunks = []
        offset = 12
        while offset < len(data):
            if len(data) - offset < 8:
                raise ProjectArchiveError('INVALID_WEBP_CHUNK')
            kind = data[offset:offset + 4]
            size = int.from_bytes(data[offset + 4:offset + 8], 'little')
            end = offset + 8 + size
            padded_end = end + (size & 1)
            if size > MAX_MEMBER_BYTES or padded_end > len(data):
                raise ProjectArchiveError('INVALID_WEBP_CHUNK')
            if size & 1 and data[end] != 0:
                raise ProjectArchiveError('INVALID_WEBP_PADDING')
            chunks.append((kind, data[offset + 8:end]))
            offset = padded_end
        if not chunks or offset != len(data):
            raise ProjectArchiveError('INVALID_WEBP_CHUNK')
        mode, payload = chunks[0]
        kinds = [kind for kind, _ in chunks]
        if b'ANIM' in kinds or b'ANMF' in kinds:
            raise ProjectArchiveError('ANIMATED_WEBP_UNSUPPORTED')
        if mode == b'VP8X':
            if (len(payload) != 10 or
                    not any(kind in (b'VP8 ', b'VP8L') for kind in kinds[1:])):
                raise ProjectArchiveError('INVALID_WEBP_FRAME')
            return (1 + int.from_bytes(payload[4:7], 'little'),
                    1 + int.from_bytes(payload[7:10], 'little'))
        if mode == b'VP8 ':
            if len(payload) < 10 or payload[3:6] != b'\x9d\x01\x2a':
                raise ProjectArchiveError('INVALID_WEBP_FRAME')
            return (int.from_bytes(payload[6:8], 'little') & 0x3fff,
                    int.from_bytes(payload[8:10], 'little') & 0x3fff)
        if mode == b'VP8L':
            if len(payload) < 5 or payload[0] != 0x2f or payload[4] & 0xe0:
                raise ProjectArchiveError('INVALID_WEBP_FRAME')
            b0, b1, b2, b3 = payload[1:5]
            return (1 + b0 + ((b1 & 0x3f) << 8),
                    1 + (b1 >> 6) + (b2 << 2) + ((b3 & 0x0f) << 10))
        raise ProjectArchiveError('UNSUPPORTED_WEBP_HEADER')
    raise ProjectArchiveError('UNSUPPORTED_SOURCE_IMAGE_TYPE')



def _webp_color_mode(data: bytes) -> str:
    """Validate alpha declarations without pretending to decode WebP pixels.

    Called only after _source_dimensions has checked RIFF/chunk bounds.
    Ambiguous extended containers fail closed pending full pixel decoding.
    """
    chunks = []
    offset = 12
    while offset < len(data):
        kind = data[offset:offset + 4]
        size = int.from_bytes(data[offset + 4:offset + 8], 'little')
        chunks.append((kind, data[offset + 8:offset + 8 + size]))
        offset += 8 + size + (size & 1)
    kind, payload = chunks[0]
    if kind == b'VP8L':
        return 'RGBA' if payload[4] & 0x10 else 'RGB'
    if kind == b'VP8 ':
        return 'RGB'
    if kind != b'VP8X':
        raise ProjectArchiveError('UNSUPPORTED_WEBP_HEADER')
    flags = payload[0]
    if flags & ~0x3e or flags & 0x02 or payload[1:4] != bytes(3):
        raise ProjectArchiveError('UNSUPPORTED_WEBP_EXTENDED_FLAGS')
    frames = [(name, frame) for name, frame in chunks[1:]
              if name in (b'VP8 ', b'VP8L')]
    alpha = [part for name, part in chunks[1:] if name == b'ALPH']
    if len(frames) != 1 or len(alpha) > 1:
        raise ProjectArchiveError('INVALID_WEBP_FRAME')
    frame_kind, frame = frames[0]
    if frame_kind == b'VP8L':
        if alpha or len(frame) < 5 or frame[0] != 0x2f or frame[4] & 0xe0:
            raise ProjectArchiveError('INVALID_WEBP_ALPHA')
        b0, b1, b2, b3 = frame[1:5]
        dimensions = (1 + b0 + ((b1 & 0x3f) << 8),
                      1 + (b1 >> 6) + (b2 << 2) + ((b3 & 0x0f) << 10))
        frame_has_alpha = bool(frame[4] & 0x10)
    else:
        if len(frame) < 10 or frame[3:6] != bytes.fromhex('9d012a'):
            raise ProjectArchiveError('INVALID_WEBP_FRAME')
        dimensions = (int.from_bytes(frame[6:8], 'little') & 0x3fff,
                      int.from_bytes(frame[8:10], 'little') & 0x3fff)
        frame_has_alpha = bool(alpha)
    canvas = (1 + int.from_bytes(payload[4:7], 'little'),
              1 + int.from_bytes(payload[7:10], 'little'))
    if dimensions != canvas or not all(dimensions):
        raise ProjectArchiveError('WEBP_FRAME_CANVAS_MISMATCH')
    if bool(flags & 0x10) != frame_has_alpha:
        raise ProjectArchiveError('WEBP_ALPHA_FLAG_MISMATCH')
    return 'RGBA' if frame_has_alpha else 'RGB'


def _verify_png_pixels(data: bytes, width: int, height: int, *, grayscale: bool):
    """Bounded complete scanline validation for both masks and PNG sources.

    Do not trust just IHDR: checksums, IDAT decompression, scanline count and
    PNG filter bytes must be verified before accepting a durable project.
    """
    if _png_size(data, grayscale=grayscale) != (width, height):
        raise ProjectArchiveError(
            'MASK_PNG_SIZE_MISMATCH' if grayscale else 'SOURCE_PIXEL_DIMENSIONS_MISMATCH')
    if grayscale:
        channels = 1
        problem = 'MASK'
    else:
        # G1.2 records only L/RGB/RGBA. Other PNG layouts (indexed, 16-bit,
        # interlaced) must be explicitly normalized by the importer.
        if data[24] != 8 or data[28] != 0 or data[25] not in (0, 2, 6):
            raise ProjectArchiveError('UNSUPPORTED_SOURCE_PNG_LAYOUT')
        channels = {0: 1, 2: 3, 6: 4}[data[25]]
        problem = 'SOURCE'
    pos, idat, got_end = 8, [], False
    seen_ihdr = False
    seen_plte = False
    idat_closed = False
    while pos < len(data):
        if pos + 12 > len(data):
            raise ProjectArchiveError('TRUNCATED_PNG')
        size = struct.unpack('>I', data[pos:pos + 4])[0]
        if size > MAX_MEMBER_BYTES or pos + 12 + size > len(data):
            raise ProjectArchiveError('INVALID_PNG_CHUNK_SIZE')
        kind = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + size]
        crc = struct.unpack('>I', data[pos + 8 + size:pos + 12 + size])[0]
        if zlib.crc32(kind + payload) & 0xffffffff != crc:
            raise ProjectArchiveError('PNG_CRC_FAILED')
        # PNG chunk names are ASCII letters. Bit 5 of the third byte is
        # reserved and must be zero; an unknown CRITICAL chunk cannot be
        # ignored because it may change how pixels should be interpreted.
        if (any(not (65 <= ch <= 90 or 97 <= ch <= 122) for ch in kind)
                or not 65 <= kind[2] <= 90):
            raise ProjectArchiveError('INVALID_PNG_CHUNK_TYPE')
        pos += size + 12
        if kind == b'IHDR':
            if seen_ihdr or pos != 33:
                raise ProjectArchiveError('DUPLICATE_PNG_IHDR')
            seen_ihdr = True
        elif kind == b'PLTE':
            if (seen_plte or idat or data[25] == 0 or
                    size == 0 or size > 768 or size % 3):
                raise ProjectArchiveError('INVALID_PNG_PLTE')
            seen_plte = True
        elif kind == b'tRNS':
            # Transparency in an L8 mask makes its subject-white pixels
            # semantically ambiguous: grayscale 255 can decode as alpha=0.
            # Likewise L/RGB sources with tRNS are effectively LA/RGBA
            # although SourceAsset advertises an opaque color_mode. RGBA
            # files must not contain tRNS at all under PNG's chunk rules.
            # Never strip this chunk silently: require explicit conversion.
            raise ProjectArchiveError('PNG_UNDECLARED_TRANSPARENCY')
        elif kind == b'IDAT':
            if idat_closed or not seen_ihdr:
                raise ProjectArchiveError('NONCONTIGUOUS_PNG_IDAT')
            idat.append(payload)
        elif kind == b'IEND':
            if size != 0:
                raise ProjectArchiveError('INVALID_PNG_IEND')
            got_end = True
            break
        else:
            if idat:
                idat_closed = True
            if kind[0] & 0x20 == 0:
                raise ProjectArchiveError('UNKNOWN_CRITICAL_PNG_CHUNK')
    if not got_end or not idat or pos != len(data):
        raise ProjectArchiveError('INCOMPLETE_' + problem + '_PNG')
    row_size = width * channels + 1
    expected = height * row_size
    if expected > MAX_TOTAL_BYTES:
        raise ProjectArchiveError(problem + '_DECOMPRESSION_TOO_LARGE')
    try:
        decoder = zlib.decompressobj()
        uncompressed = decoder.decompress(b''.join(idat), expected + 1)
        if (len(uncompressed) != expected or decoder.unconsumed_tail or
                not decoder.eof or decoder.unused_data):
            raise ProjectArchiveError('INVALID_' + problem + '_PNG_PIXELS')
    except zlib.error as exc:
        raise ProjectArchiveError('INVALID_' + problem + '_PNG_PIXELS') from exc
    if any(uncompressed[y * row_size] > 4 for y in range(height)):
        raise ProjectArchiveError('INVALID_' + problem + '_PNG_FILTER')



# Conservative non-executing artifact admission; not a Design Space guarantee.
_SVG_NS = 'http://www.w3.org/2000/svg'
_SVG_TAGS = {'svg', 'g', 'path', 'rect', 'circle', 'ellipse', 'polygon',
             'polyline', 'line', 'defs', 'clipPath', 'mask', 'linearGradient',
             'radialGradient', 'stop', 'title', 'desc', 'text', 'tspan', 'metadata'}
_SVG_STYLES = {'fill', 'stroke', 'stroke-width', 'opacity', 'fill-opacity',
               'stroke-opacity', 'stroke-linecap', 'stroke-linejoin',
               'stroke-dasharray', 'stroke-dashoffset', 'display', 'visibility',
               'fill-rule', 'clip-rule'}


def _verify_svg_artifact(data: bytes):
    if len(data) > 4 * 1024 * 1024:
        raise ProjectArchiveError('SVG_ARTIFACT_TOO_LARGE')
    if re.search(rb'<!\s*(?:DOCTYPE|ENTITY)\b', data, re.I):
        raise ProjectArchiveError('SVG_DTD_OR_ENTITY')
    root, count, depth = None, 0, 0
    try:
        for event, node in ET.iterparse(BytesIO(data), events=('start', 'end', 'pi')):
            if event == 'pi':
                raise ProjectArchiveError('SVG_PROCESSING_INSTRUCTION')
            if event == 'end':
                depth -= 1
                continue
            if root is None:
                root = node
            count += 1
            depth += 1
            if count > 20000 or depth > 64:
                raise ProjectArchiveError('SVG_COMPLEXITY_LIMIT')
            if node.tag not in {f'{{{_SVG_NS}}}{tag}' for tag in _SVG_TAGS}:
                raise ProjectArchiveError('SVG_ACTIVE_OR_FOREIGN_ELEMENT')
            for key, value in node.attrib.items():
                name = key.split('}', 1)[-1].lower()
                if (name.startswith('on') or name in ('href', 'src', 'base')
                        or (key.startswith('{') and
                            not key.startswith(f'{{{_SVG_NS}}}') and
                            key != '{http://www.w3.org/XML/1998/namespace}space')):
                    raise ProjectArchiveError('SVG_ACTIVE_ATTRIBUTE')
                low = value.lower()
                if ('\\' in value or any(x in low for x in
                        ('url(', 'javascript:', 'data:', '@import', 'expression(',
                         'http://', 'https://', '/*', '*/'))):
                    raise ProjectArchiveError('SVG_EXTERNAL_REFERENCE')
                if name == 'style':
                    for decl in value.split(';'):
                        if not decl.strip():
                            continue
                        if ':' not in decl:
                            raise ProjectArchiveError('SVG_UNSUPPORTED_STYLE')
                        prop, val = decl.split(':', 1)
                        if (prop.strip().lower() not in _SVG_STYLES or
                                not re.fullmatch(r'[a-zA-Z0-9#.,+\- %]*', val.strip())):
                            raise ProjectArchiveError('SVG_UNSUPPORTED_STYLE')
    except (ET.ParseError, UnicodeError) as exc:
        raise ProjectArchiveError('INVALID_SVG_XML') from exc
    if root is None or root.tag != f'{{{_SVG_NS}}}svg':
        raise ProjectArchiveError('NOT_SVG_ARTIFACT')


def _verify_artifact_bytes(data: bytes, artifact: Artifact):
    if artifact.use == 'print_then_cut_png':
        width, height = _png_size(data, grayscale=False)
        if (abs(width - artifact.width_mm * artifact.ppi / 25.4) > 0.51 or
                abs(height - artifact.height_mm * artifact.ppi / 25.4) > 0.51):
            raise ProjectArchiveError('PRINT_ARTIFACT_PIXEL_DIMENSIONS_MISMATCH')
        _verify_png_pixels(data, width, height, grayscale=False)
    elif artifact.use in ('basic_cut_svg', 'editable_svg'):
        _verify_svg_artifact(data)
    else:
        raise ProjectArchiveError('UNKNOWN_ARTIFACT_USE')


def _verify_mask_png(data: bytes, width: int, height: int):
    _verify_png_pixels(data, width, height, grayscale=True)


def _record_list(data, cls):
    if not isinstance(data, list):
        raise ProjectArchiveError('INVALID_RECORD_LIST')
    try:
        records = []
        for row in data:
            if not isinstance(row, dict):
                raise ProjectArchiveError('INVALID_RECORD_FIELDS')
            values = dict(row)
            # JSON arrays must round-trip to the immutable record field types.
            if cls is Subject:
                for field in ('bbox_px', 'accessory_ids'):
                    if field in values and isinstance(values[field], list):
                        values[field] = tuple(values[field])
            if cls is Artifact and isinstance(values.get('subject_ids'), list):
                values['subject_ids'] = tuple(values['subject_ids'])
            records.append(cls(**values))
        return tuple(records)
    except (TypeError, ValueError, KeyError) as exc:
        raise ProjectArchiveError('INVALID_RECORD_FIELDS') from exc


def _validate_bundle(project: LoadedProject):
    if not isinstance(project.project_id, str) or not VALID_ID.fullmatch(project.project_id):
        raise ProjectArchiveError('INVALID_PROJECT_ID')
    if not isinstance(project.app_version, str) or not 1 <= len(project.app_version) <= 64:
        raise ProjectArchiveError('INVALID_APP_VERSION')
    try:
        validate_project_records(sources=project.sources, masks=project.masks,
                                 subjects=project.subjects, artifacts=project.artifacts,
                                 qa_results=project.qa_results)
    except RecordError as exc:
        raise ProjectArchiveError(f'RECORDS_INVALID: {exc}') from exc
    if not isinstance(project.document, dict) or not isinstance(project.operations, list):
        raise ProjectArchiveError('INVALID_DOCUMENT_OR_OPERATIONS')
    if len(project.operations) > 5000:
        raise ProjectArchiveError('TOO_MANY_OPERATIONS')
    _json_bytes(project.document)
    _json_bytes(project.operations)

    # Untrusted LoadedProject instances may be constructed directly by the UI
    # or an adapter. Reject malformed path/resource mappings with a stable
    # archive error before accessing .get(), iterating, or writing to disk.
    if not isinstance(project.source_paths, dict):
        raise ProjectArchiveError('INVALID_SOURCE_PATH_MAP')
    if not isinstance(project.mask_paths, dict):
        raise ProjectArchiveError('INVALID_MASK_PATH_MAP')
    if not isinstance(project.resources, dict):
        raise ProjectArchiveError('INVALID_RESOURCE_MAP')

    expected = {}
    for source in project.sources:
        path = project.source_paths.get(source.source_id)
        if not isinstance(path, str) or not path.startswith('sources/'):
            raise ProjectArchiveError('MISSING_SOURCE_PATH')
        _safe_path(path)
        if PurePosixPath(path).suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
            raise ProjectArchiveError('INVALID_SOURCE_EXTENSION')
        # Two source IDs sharing one ZIP member would silently overwrite the
        # earlier expected resource, making the archive identity ambiguous.
        if path in expected:
            raise ProjectArchiveError('RESOURCE_PATH_COLLISION')
        expected[path] = ('source', source)
    for mask in project.masks:
        path = project.mask_paths.get(mask.mask_id)
        # G1.2 mask identifiers are stable logical keys, not ZIP filenames.
        # Values such as 'mask:01' and 'CON' are valid IDs but unsafe on
        # Windows. Persist them under independently chosen portable names.
        if (not isinstance(path, str) or not path.startswith('masks/') or
                len(path.split('/')) != 2 or not path.endswith('.png') or
                len(path) <= len('masks/.png')):
            raise ProjectArchiveError('INVALID_MASK_PATH')
        _safe_path(path)
        if path in expected:
            raise ProjectArchiveError('RESOURCE_PATH_COLLISION')
        expected[path] = ('mask', mask)
    for artifact in project.artifacts:
        path = _safe_path(artifact.file_path)
        if path in expected:
            raise ProjectArchiveError('RESOURCE_PATH_COLLISION')
        expected[path] = ('artifact', artifact)
    # G2.4 backward-compatible attachment: exactly declared full-resolution
    # mask snapshot supplement, validated before any disk mutation. The
    # upstream G1.3 security checks must also cover these ZIP resource paths.
    try:
        from .mask_snapshot_g24 import validate_archive_snapshot, MaskSnapshotError
        mask_extras = validate_archive_snapshot(project)
    except MaskSnapshotError as exc:
        raise ProjectArchiveError('MASK_SNAPSHOT_INVALID: '+exc.code) from exc
    for snapshot_path in mask_extras:
        _safe_path(snapshot_path)
        if snapshot_path in expected:
            raise ProjectArchiveError('RESOURCE_PATH_COLLISION')
        expected[snapshot_path]=('snapshot', None)
    if set(project.source_paths) != {x.source_id for x in project.sources}:
        raise ProjectArchiveError('UNKNOWN_SOURCE_PATH')
    if set(project.mask_paths) != {x.mask_id for x in project.masks}:
        raise ProjectArchiveError('UNKNOWN_MASK_PATH')
    if set(project.resources) != set(expected):
        raise ProjectArchiveError('RESOURCE_SET_MISMATCH')
    portable_resources = [unicodedata.normalize('NFC', p).casefold() for p in expected]
    if len(set(portable_resources)) != len(expected):
        raise ProjectArchiveError('CASE_COLLIDING_RESOURCE_PATHS')
    # Prevent file/directory conflicts both among resources and against the
    # mandatory ZIP metadata. ZIP readers may extract or display these paths
    # differently on Windows, macOS or case-insensitive filesystems.
    portable_metadata = {unicodedata.normalize('NFC', p).casefold()
                         for p in (*JSON_FILES, 'manifest.json')}
    if portable_metadata.intersection(portable_resources):
        raise ProjectArchiveError('RESERVED_ARCHIVE_RESOURCE_PATH')
    portable_all = set(portable_resources) | portable_metadata
    for path_name in portable_all:
        segments = path_name.split('/')
        if any('/'.join(segments[:index]) in portable_all
               for index in range(1, len(segments))):
            raise ProjectArchiveError('ARCHIVE_FILE_DIRECTORY_PATH_CONFLICT')
    total = 0
    for path, (kind, rec) in expected.items():
        data = project.resources[path]
        if not isinstance(data, bytes) or not data or len(data) > MAX_MEMBER_BYTES:
            raise ProjectArchiveError('INVALID_RESOURCE_BYTES')
        if kind != 'snapshot' and _digest(data) != rec.sha256:
            raise ProjectArchiveError('RESOURCE_SHA256_MISMATCH')
        # G2.4 snapshot compressed bytes + decoded float32 digest are checked
        # by validate_archive_snapshot; ZIP manifest independently hashes bytes.
        if kind == 'source':
            suffix = PurePosixPath(path).suffix.lower()
            if suffix in ('.jpg', '.jpeg'):
                dims, actual_mode = _jpeg_source_info(data)
            elif suffix == '.webp':
                dims = _source_dimensions(path, data)
                actual_mode = _webp_color_mode(data)
            else:
                dims, actual_mode = _source_dimensions(path, data), None
            if dims != (rec.width_px, rec.height_px):
                raise ProjectArchiveError('SOURCE_PIXEL_DIMENSIONS_MISMATCH')
            if actual_mode is not None and rec.color_mode != actual_mode:
                raise ProjectArchiveError('SOURCE_COLOR_MODE_MISMATCH')
            if suffix == '.png':
                # SourceAsset.color_mode is an explicit contract, not a hint:
                # an RGBA label on opaque/RGB bytes can silently mislead
                # mask creation and downstream transparency diagnostics.
                # Indexed and grayscale+alpha PNGs must be normalized before
                # admission because the G1.2 metadata has no matching mode.
                actual_mode = {0: 'L', 2: 'RGB', 6: 'RGBA'}.get(data[25])
                if actual_mode is None:
                    raise ProjectArchiveError('UNSUPPORTED_SOURCE_PNG_COLOR_TYPE')
                if rec.color_mode != actual_mode:
                    raise ProjectArchiveError('SOURCE_COLOR_MODE_MISMATCH')
                _verify_png_pixels(data, rec.width_px, rec.height_px,
                                   grayscale=False)
        elif kind == 'mask':
            _verify_mask_png(data, rec.width_px, rec.height_px)
        elif kind == 'artifact':
            _verify_artifact_bytes(data, rec)
        total += len(data)
    if total > MAX_TOTAL_BYTES:
        raise ProjectArchiveError('RESOURCES_TOO_LARGE')


def _record_json(record):
    """Encode documented typed tuple fields as JSON arrays, explicitly.

    Scene and operation JSON are stricter: arbitrary tuples are rejected to
    prevent silent changes after reopening a project.
    """
    row = record_dict(record)
    if isinstance(record, Subject):
        row['bbox_px'] = list(record.bbox_px)
        row['accessory_ids'] = list(record.accessory_ids)
    elif isinstance(record, Artifact):
        row['subject_ids'] = list(record.subject_ids)
    return row


def _payload(project: LoadedProject):
    _validate_bundle(project)
    files = {
        'document.json': _json_bytes(project.document),
        'operations.json': _json_bytes(project.operations),
        'sources.json': _json_bytes([_record_json(x) for x in project.sources]),
        'masks.json': _json_bytes([_record_json(x) for x in project.masks]),
        'subjects.json': _json_bytes([_record_json(x) for x in project.subjects]),
        'artifacts.json': _json_bytes([_record_json(x) for x in project.artifacts]),
        'proofs/qa_results.json': _json_bytes([_record_json(x) for x in project.qa_results]),
    }
    files.update(project.resources)
    if len(files) + 1 > MAX_ENTRIES or sum(map(len, files.values())) > MAX_TOTAL_BYTES:
        raise ProjectArchiveError('ARCHIVE_BUDGET_EXCEEDED')
    manifest = {
        'schema_version': SCHEMA_VERSION, 'project_id': project.project_id,
        'app_version': project.app_version,
        'source_paths': project.source_paths, 'mask_paths': project.mask_paths,
        'entries': {p: {'sha256': _digest(content), 'size_bytes': len(content)}
                    for p, content in sorted(files.items())}
    }
    files['manifest.json'] = _json_bytes(manifest)
    return files


def save_project(path, project: LoadedProject, *, overwrite: bool = False):
    """Durable write: validate -> temp ZIP -> readback -> fsync -> atomic rename."""
    destination = Path(path)
    if destination.suffix.lower() != '.smartsvg' or not destination.parent.is_dir():
        raise ProjectArchiveError('INVALID_PROJECT_DESTINATION')
    if destination.is_symlink() or (destination.exists() and not overwrite):
        raise ProjectArchiveError('DESTINATION_EXISTS_OR_UNSAFE')
    files = _payload(project)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(prefix='.smartsvg-', suffix='.tmp',
                                         dir=destination.parent, delete=False) as handle:
            tmp = Path(handle.name)
        with zipfile.ZipFile(tmp, 'w', compression=zipfile.ZIP_DEFLATED,
                             compresslevel=6, allowZip64=False) as out:
            for name, content in sorted(files.items()):
                out.writestr(name, content)
        with open(tmp, 'rb') as handle:
            os.fsync(handle.fileno())
        recovered = load_project(tmp)
        if recovered.project_id != project.project_id:
            raise ProjectArchiveError('READBACK_PROJECT_MISMATCH')
        if not overwrite:
            os.link(tmp, destination)  # no-clobber creation on same filesystem
            tmp.unlink()
            tmp = None
        else:
            if destination.is_symlink():
                raise ProjectArchiveError('DESTINATION_EXISTS_OR_UNSAFE')
            os.replace(tmp, destination)
            tmp = None
        # Directory fsync is best-effort; not available on all Windows filesystems.
        try:
            fd = os.open(destination.parent, os.O_RDONLY)
            try:
                os.fsync(fd)
            finally:
                os.close(fd)
        except (OSError, ValueError):
            pass
    except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
        raise ProjectArchiveError('PROJECT_SAVE_FAILED') from exc
    finally:
        if tmp is not None:
            tmp.unlink(missing_ok=True)
    return {'path': str(destination), 'sha256': _digest(destination.read_bytes()),
            'schema_version': SCHEMA_VERSION, 'cut_verified': False}


def load_project(path) -> LoadedProject:
    """Read untrusted project without extracting or executing any content."""
    source_path = Path(path)
    if not source_path.is_file() or source_path.stat().st_size > MAX_ARCHIVE_BYTES:
        raise ProjectArchiveError('ARCHIVE_MISSING_OR_TOO_LARGE')
    try:
        with zipfile.ZipFile(source_path, 'r') as src:
            infos = src.infolist()
            if not infos or len(infos) > MAX_ENTRIES:
                raise ProjectArchiveError('INVALID_ENTRY_COUNT')
            seen, total = set(), 0
            for info in infos:
                name = _safe_path(info.filename)
                portable_name = unicodedata.normalize('NFC', name).casefold()
                if portable_name in seen:
                    raise ProjectArchiveError('DUPLICATE_ARCHIVE_PATH')
                seen.add(portable_name)
                mode = (info.external_attr >> 16) & 0xffff
                if (info.is_dir() or (stat.S_IFMT(mode) not in (0, stat.S_IFREG)) or
                        info.flag_bits & 1 or info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)):
                    raise ProjectArchiveError('UNSAFE_ZIP_ENTRY')
                if info.file_size > MAX_MEMBER_BYTES or (info.file_size and
                     info.file_size / max(info.compress_size, 1) > 2000):
                    raise ProjectArchiveError('ZIP_BOMB_OR_OVERSIZED_MEMBER')
                total += info.file_size
                if total > MAX_TOTAL_BYTES:
                    raise ProjectArchiveError('ARCHIVE_BUDGET_EXCEEDED')
            if 'manifest.json' not in src.namelist():
                raise ProjectArchiveError('MISSING_MANIFEST')
            def read(name):
                info = src.getinfo(name)
                with src.open(info) as f:
                    data = f.read(min(info.file_size, MAX_MEMBER_BYTES) + 1)
                if len(data) != info.file_size:
                    raise ProjectArchiveError('ZIP_MEMBER_SIZE_MISMATCH')
                return data
            manifest = _parse_json(read('manifest.json'))
            if not isinstance(manifest, dict) or manifest.get('schema_version') != SCHEMA_VERSION:
                raise ProjectArchiveError('UNSUPPORTED_PROJECT_SCHEMA')
            entries = manifest.get('entries')
            if not isinstance(entries, dict) or set(entries) != set(src.namelist()) - {'manifest.json'}:
                raise ProjectArchiveError('UNDECLARED_OR_MISSING_ENTRY')
            if not set(JSON_FILES) <= set(entries):
                raise ProjectArchiveError('REQUIRED_PROJECT_JSON_MISSING')
            payload = {}
            for name in entries:
                _safe_path(name)
                entry = entries[name]
                if (not isinstance(entry, dict) or set(entry) != {'sha256', 'size_bytes'} or
                        not isinstance(entry['size_bytes'], int) or isinstance(entry['size_bytes'], bool) or
                        entry['size_bytes'] < 0):
                    raise ProjectArchiveError('INVALID_MANIFEST_ENTRY')
                data = read(name)
                if entry['size_bytes'] != len(data) or entry['sha256'] != _digest(data):
                    raise ProjectArchiveError('MANIFEST_CONTENT_MISMATCH')
                payload[name] = data
            def records(name, cls):
                return _record_list(_parse_json(payload[name]), cls)
            data = LoadedProject(
                project_id=manifest.get('project_id'), app_version=manifest.get('app_version'),
                sources=records('sources.json', SourceAsset),
                masks=records('masks.json', Mask),
                subjects=records('subjects.json', Subject),
                artifacts=records('artifacts.json', Artifact),
                qa_results=records('proofs/qa_results.json', QAResult),
                document=_parse_json(payload['document.json']),
                operations=_parse_json(payload['operations.json']),
                resources={k: v for k, v in payload.items() if k not in JSON_FILES},
                source_paths=manifest.get('source_paths'),
                mask_paths=manifest.get('mask_paths'),
            )
            _validate_bundle(data)
            return data
    except (OSError, EOFError, KeyError, TypeError, AttributeError, IndexError,
            ValueError, zipfile.BadZipFile, zipfile.LargeZipFile, RuntimeError) as exc:
        if isinstance(exc, ProjectArchiveError):
            raise
        raise ProjectArchiveError('CORRUPT_OR_UNSUPPORTED_ARCHIVE') from exc
