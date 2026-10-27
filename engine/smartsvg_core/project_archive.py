"""G1.3 portable .smartsvg ZIP projects with bounded, fail-closed loading.

This is a byte-preserving *project* format, not a Cricut-compatible export.
No archives are extracted to disk and no external references are followed.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import stat
import struct
import tempfile
import zipfile
import zlib

from .project_contracts import (
    Artifact, Mask, QAResult, SourceAsset, Subject, RecordError,
    record_dict, validate_project_records,
)

SCHEMA_VERSION = 'smartsvg-project/1'
MAX_ENTRIES = 256
MAX_MEMBER_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 256 * 1024 * 1024
MAX_ARCHIVE_BYTES = 280 * 1024 * 1024
MAX_JSON_BYTES = 4 * 1024 * 1024
JSON_FILES = ('document.json', 'operations.json', 'sources.json', 'masks.json',
              'subjects.json', 'artifacts.json', 'proofs/qa_results.json')
SAFE_NAME = re.compile(r'^[A-Za-z0-9_.\-/]+$')
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
    if (not isinstance(path, str) or len(path) > 512 or not SAFE_NAME.fullmatch(path)
            or '\\' in path or ':' in path or '//' in path):
        raise ProjectArchiveError('UNSAFE_ARCHIVE_PATH')
    parts = PurePosixPath(path).parts
    if (not parts or PurePosixPath(path).is_absolute() or
            any(p in ('.', '..') for p in path.split('/')) or
            path != PurePosixPath(path).as_posix() or path.endswith('/')):
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


def _source_dimensions(path: str, data: bytes) -> tuple[int, int]:
    suffix = PurePosixPath(path).suffix.lower()
    if suffix == '.png':
        return _png_size(data, grayscale=False)
    if suffix in ('.jpg', '.jpeg'):
        if not data.startswith(b'\xff\xd8'):
            raise ProjectArchiveError('INVALID_JPEG')
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xff:
                raise ProjectArchiveError('INVALID_JPEG')
            while i < len(data) and data[i] == 0xff:
                i += 1
            if i >= len(data):
                break
            marker = data[i]
            i += 1
            if marker == 0xd9:
                break
            if marker in (0xd8, 0x01, *range(0xd0, 0xd8)):
                continue
            if i + 2 > len(data):
                break
            segment = struct.unpack('>H', data[i:i + 2])[0]
            if segment < 2 or i + segment > len(data):
                raise ProjectArchiveError('INVALID_JPEG')
            if marker in (0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7,
                          0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf):
                if segment < 7:
                    raise ProjectArchiveError('INVALID_JPEG')
                h, w = struct.unpack('>HH', data[i + 3:i + 7])
                return w, h
            i += segment
        raise ProjectArchiveError('JPEG_DIMENSIONS_NOT_FOUND')
    if suffix == '.webp':
        if len(data) < 30 or data[:4] != b'RIFF' or data[8:12] != b'WEBP':
            raise ProjectArchiveError('INVALID_WEBP_HEADER')
        mode = data[12:16]
        if mode == b'VP8X':
            return (1 + int.from_bytes(data[24:27], 'little'),
                    1 + int.from_bytes(data[27:30], 'little'))
        if mode == b'VP8 ' and data[23:26] == b'\x9d\x01\x2a':
            return (int.from_bytes(data[26:28], 'little') & 0x3fff,
                    int.from_bytes(data[28:30], 'little') & 0x3fff)
        if mode == b'VP8L' and data[20] == 0x2f:
            b0, b1, b2, b3 = data[21:25]
            return (1 + b0 + ((b1 & 0x3f) << 8),
                    1 + (b1 >> 6) + (b2 << 2) + ((b3 & 0x0f) << 10))
        raise ProjectArchiveError('UNSUPPORTED_WEBP_HEADER')
    raise ProjectArchiveError('UNSUPPORTED_SOURCE_IMAGE_TYPE')


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
        pos += size + 12
        if kind == b'IDAT':
            idat.append(payload)
        if kind == b'IEND':
            if size != 0:
                raise ProjectArchiveError('INVALID_PNG_IEND')
            got_end = True
            break
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
        if path != f'masks/{mask.mask_id}.png':
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
    if set(project.source_paths) != {x.source_id for x in project.sources}:
        raise ProjectArchiveError('UNKNOWN_SOURCE_PATH')
    if set(project.mask_paths) != {x.mask_id for x in project.masks}:
        raise ProjectArchiveError('UNKNOWN_MASK_PATH')
    if set(project.resources) != set(expected):
        raise ProjectArchiveError('RESOURCE_SET_MISMATCH')
    if len({p.casefold() for p in expected}) != len(expected):
        raise ProjectArchiveError('CASE_COLLIDING_RESOURCE_PATHS')
    total = 0
    for path, (kind, rec) in expected.items():
        data = project.resources[path]
        if not isinstance(data, bytes) or not data or len(data) > MAX_MEMBER_BYTES:
            raise ProjectArchiveError('INVALID_RESOURCE_BYTES')
        if _digest(data) != rec.sha256:
            raise ProjectArchiveError('RESOURCE_SHA256_MISMATCH')
        if kind == 'source':
            dims = _source_dimensions(path, data)
            if dims != (rec.width_px, rec.height_px):
                raise ProjectArchiveError('SOURCE_PIXEL_DIMENSIONS_MISMATCH')
            if PurePosixPath(path).suffix.lower() == '.png':
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
                if name.casefold() in seen:
                    raise ProjectArchiveError('DUPLICATE_ARCHIVE_PATH')
                seen.add(name.casefold())
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
