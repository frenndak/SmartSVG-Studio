"""G1.2: stable metadata contracts; no image processing or machine certification.

These records are a boundary for the future .smartsvg format, not a reader of
untrusted archives. Actual image bytes/mask pixels must be validated separately.
Existing ComfyUI nodes continue to use their historical input/output APIs.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import re
from pathlib import PurePosixPath
import unicodedata

SCHEMA_VERSION = 'smartsvg-contracts/1'
_MAX_PIXELS = 100_000_000
_MIN_PHYSICAL_MM = 0.01
_MAX_PHYSICAL_MM = 10_000.0
_ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$')
_SHA = re.compile(r'^[0-9a-f]{64}$')
_STATUSES = frozenset({'not_tested', 'passed', 'failed'})
# Windows device names are invalid even with a file extension. Project paths
# must be portable between ComfyUI installations on Windows and POSIX.
_WINDOWS_DEVICE = re.compile(r'^(?:CON|PRN|AUX|NUL|COM[1-9¹²³]|LPT[1-9¹²³]|CONIN\$|CONOUT\$)(?:\..*)?$', re.IGNORECASE)
_WINDOWS_FORBIDDEN = frozenset('<>"|?*')


class RecordError(ValueError):
    """Invalid contract metadata. No processing should start with these records."""


def _identifier(value, field):
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise RecordError(f'{field}: INVALID_ID')


def _digest(value, field):
    if not isinstance(value, str) or not _SHA.fullmatch(value):
        raise RecordError(f'{field}: INVALID_SHA256')


def _size(width, height):
    if (type(width) is not int or type(height) is not int or width <= 0 or
            height <= 0 or width * height > _MAX_PIXELS):
        raise RecordError('INVALID_PIXEL_DIMENSIONS')


def _positive_number(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise RecordError(f'{field}: INVALID_NUMBER')
    # math.isfinite() converts integers to float and raises OverflowError for
    # very large integers supplied by an untrusted project metadata record.
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite or value <= 0:
        raise RecordError(f'{field}: INVALID_NUMBER')


def _identifiers(values, field, *, empty_ok=False):
    if not isinstance(values, (tuple, list)) or (not empty_ok and not values):
        raise RecordError(f'{field}: INVALID_SEQUENCE')
    for value in values:
        _identifier(value, field)
    if len(set(values)) != len(values):
        raise RecordError(f'{field}: DUPLICATE_ID')


@dataclass(frozen=True)
class SourceAsset:
    source_id: str
    sha256: str
    width_px: int
    height_px: int
    color_mode: str = 'RGBA'
    provenance: str = 'unspecified'

    def __post_init__(self):
        _identifier(self.source_id, 'source_id')
        _digest(self.sha256, 'source_sha256')
        _size(self.width_px, self.height_px)
        if self.color_mode not in ('L', 'RGB', 'RGBA'):
            raise RecordError('UNSUPPORTED_SOURCE_COLOR_MODE')
        if not isinstance(self.provenance, str) or len(self.provenance) > 1024:
            raise RecordError('INVALID_PROVENANCE')


@dataclass(frozen=True)
class Mask:
    mask_id: str
    source_id: str
    sha256: str
    width_px: int
    height_px: int
    polarity: str = 'subject_white'
    encoding: str = 'L8'

    def __post_init__(self):
        _identifier(self.mask_id, 'mask_id')
        _identifier(self.source_id, 'source_id')
        _digest(self.sha256, 'mask_sha256')
        _size(self.width_px, self.height_px)
        if self.polarity != 'subject_white' or self.encoding != 'L8':
            raise RecordError('MASK_MUST_BE_L8_SUBJECT_WHITE')


@dataclass(frozen=True)
class Subject:
    subject_id: str
    source_id: str
    mask_id: str
    bbox_px: tuple[int, int, int, int]
    accessory_ids: tuple[str, ...] = ()

    def __post_init__(self):
        for field in ('subject_id', 'source_id', 'mask_id'):
            _identifier(getattr(self, field), field)
        if (not isinstance(self.bbox_px, (tuple, list)) or len(self.bbox_px) != 4 or
            any(type(x) is not int for x in self.bbox_px)):
            raise RecordError('INVALID_BBOX')
        x, y, w, h = self.bbox_px
        if x < 0 or y < 0 or w <= 0 or h <= 0:
            raise RecordError('INVALID_BBOX')
        _identifiers(self.accessory_ids, 'accessory_ids', empty_ok=True)
        if self.subject_id in self.accessory_ids:
            raise RecordError('SELF_ACCESSORY')
        # JSON arrays are accepted at the boundary, but frozen records must
        # not retain mutable references after validation.
        object.__setattr__(self, 'bbox_px', tuple(self.bbox_px))
        object.__setattr__(self, 'accessory_ids', tuple(self.accessory_ids))


@dataclass(frozen=True)
class Artifact:
    artifact_id: str
    subject_ids: tuple[str, ...]
    use: str
    file_path: str
    sha256: str
    width_mm: float
    height_mm: float
    ppi: int | None = None

    def __post_init__(self):
        _identifier(self.artifact_id, 'artifact_id')
        _identifiers(self.subject_ids, 'subject_ids')
        object.__setattr__(self, 'subject_ids', tuple(self.subject_ids))
        _digest(self.sha256, 'artifact_sha256')
        if self.use not in ('print_then_cut_png', 'basic_cut_svg', 'editable_svg'):
            raise RecordError('INVALID_ARTIFACT_USE')
        if not isinstance(self.file_path, str) or '\\' in self.file_path or ':' in self.file_path:
            raise RecordError('INVALID_ARTIFACT_PATH')
        p = PurePosixPath(self.file_path)
        # Common filesystems reject a single component over 255 UTF-8 bytes,
        # even when the full relative path is within the metadata limit.
        if (not self.file_path or p.is_absolute() or '..' in p.parts or '.' in p.parts or
                p.as_posix() != self.file_path or len(self.file_path) > 512 or
                any(char in _WINDOWS_FORBIDDEN or
                    (unicodedata.category(char) in ('Cc', 'Cf', 'Cs', 'Zl', 'Zp') or char == '\u034f' or
                     0xFE00 <= ord(char) <= 0xFE0F or
                     0xE0100 <= ord(char) <= 0xE01EF)
                    for char in self.file_path) or
                any(part.endswith(('.', ' ')) or _WINDOWS_DEVICE.fullmatch(part) or
                    len(part.encode('utf-8')) > 255 for part in p.parts)):
            raise RecordError('INVALID_ARTIFACT_PATH')
        if p.suffix.lower() != ('.png' if self.use == 'print_then_cut_png' else '.svg'):
            raise RecordError('ARTIFACT_EXTENSION_MISMATCH')
        _positive_number(self.width_mm, 'width_mm')
        _positive_number(self.height_mm, 'height_mm')
        # A metadata contract must not accept an effectively zero-length
        # or astronomical SVG/print size. This is a generic sanity limit,
        # not a statement about a particular Cricut model's work area.
        if (not _MIN_PHYSICAL_MM <= self.width_mm <= _MAX_PHYSICAL_MM or
                not _MIN_PHYSICAL_MM <= self.height_mm <= _MAX_PHYSICAL_MM):
            raise RecordError('PHYSICAL_SIZE_OUT_OF_RANGE')
        if self.ppi is not None and (type(self.ppi) is not int or not 72 <= self.ppi <= 2400):
            raise RecordError('INVALID_PPI')
        if self.use == 'print_then_cut_png' and self.ppi is None:
            raise RecordError('PRINT_REQUIRES_EXPLICIT_PPI')
        if self.use == 'print_then_cut_png' and self.ppi is not None:
            width_px = self.width_mm * self.ppi / 25.4
            height_px = self.height_mm * self.ppi / 25.4
            if width_px < 1 or height_px < 1:
                raise RecordError('PRINT_SIZE_BELOW_ONE_PIXEL')
            if width_px * height_px > _MAX_PIXELS:
                raise RecordError('PRINT_PIXEL_BUDGET_EXCEEDED')


@dataclass(frozen=True)
class QAResult:
    artifact_id: str
    visual: str = 'not_tested'
    geometry: str = 'not_tested'
    design_space_import: str = 'not_tested'
    physical_cut: str = 'not_tested'
    import_evidence: str | None = None
    physical_evidence: str | None = None
    environment: str = 'static'

    def __post_init__(self):
        _identifier(self.artifact_id, 'artifact_id')
        for field in ('visual', 'geometry', 'design_space_import', 'physical_cut'):
            status = getattr(self, field)
            if not isinstance(status, str) or status not in _STATUSES:
                raise RecordError(f'{field}: INVALID_STATUS')
        if self.environment not in ('static', 'simulated', 'real'):
            raise RecordError('INVALID_QA_ENVIRONMENT')
        for field, evidence in (('design_space_import', self.import_evidence),
                                ('physical_cut', self.physical_evidence)):
            if evidence is not None and (not isinstance(evidence, str) or not 1 <= len(evidence) <= 512):
                raise RecordError(f'{field}: INVALID_EVIDENCE')
        if self.design_space_import == 'passed' and (self.environment != 'real' or not self.import_evidence):
            raise RecordError('IMPORT_PASS_REQUIRES_REAL_EVIDENCE')
        if self.physical_cut == 'passed' and (self.environment != 'real' or not self.physical_evidence or
                                               self.design_space_import != 'passed'):
            raise RecordError('CUT_PASS_REQUIRES_IMPORT_AND_REAL_EVIDENCE')


def validate_project_records(*, sources, masks, subjects, artifacts, qa_results=()):
    """Check references and geometry across records without changing originals.

    This metadata check does not verify file contents, real import or cuts.
    """
    tables = []
    for name, values, cls, key in (
        ('sources', sources, SourceAsset, 'source_id'),
        ('masks', masks, Mask, 'mask_id'),
        ('subjects', subjects, Subject, 'subject_id'),
        ('artifacts', artifacts, Artifact, 'artifact_id'),
        ('qa_results', qa_results, QAResult, 'artifact_id'),
    ):
        if not isinstance(values, (tuple, list)) or any(not isinstance(x, cls) for x in values):
            raise RecordError(f'{name}: INVALID_RECORD_COLLECTION')
        index = {getattr(x, key): x for x in values}
        if len(index) != len(values):
            raise RecordError(f'{name}: DUPLICATE_ID')
        tables.append(index)
    src, msk, sub, art, qa = tables
    # Artifact names are persisted as portable paths. On case-insensitive file
    # systems two different artifact IDs can refer to the same output file.
    # Reject aliases even when their digests match: each artifact owns one path.
    portable_paths = set()
    required_directories = set()
    for artifact in art.values():
        portable_path = unicodedata.normalize('NFC', artifact.file_path).casefold()
        if portable_path in portable_paths:
            raise RecordError('artifacts: DUPLICATE_FILE_PATH')
        # An artifact owns a regular file, never a directory. Reject a path
        # that is a parent of another file (or is inside an existing file),
        # irrespective of insertion order and portable Unicode/case aliases.
        parts = portable_path.split('/')
        parents = ('/'.join(parts[:i]) for i in range(1, len(parts)))
        if portable_path in required_directories or any(
                parent in portable_paths for parent in parents):
            raise RecordError('artifacts: FILE_DIRECTORY_PATH_CONFLICT')
        portable_paths.add(portable_path)
        required_directories.update(
            '/'.join(parts[:i]) for i in range(1, len(parts)))
    for mask in msk.values():
        source = src.get(mask.source_id)
        if source is None or (mask.width_px, mask.height_px) != (source.width_px, source.height_px):
            raise RecordError('MASK_SOURCE_MISMATCH')
    for subject in sub.values():
        source, mask = src.get(subject.source_id), msk.get(subject.mask_id)
        if source is None or mask is None or mask.source_id != subject.source_id:
            raise RecordError('SUBJECT_SOURCE_MASK_MISMATCH')
        x, y, w, h = subject.bbox_px
        if x + w > source.width_px or y + h > source.height_px:
            raise RecordError('BBOX_OUT_OF_SOURCE')
        if any(a not in sub or sub[a].source_id != subject.source_id for a in subject.accessory_ids):
            raise RecordError('INVALID_ACCESSORY_LINK')
    # Accessory references form a directed graph. A reference cycle
    # (A -> B -> A, or a longer loop) has no meaningful root; future
    # exporters/inspectors may otherwise traverse forever. Validate the
    # graph iteratively so long chains cannot overflow Python recursion.
    incoming = {subject_id: 0 for subject_id in sub}
    for subject in sub.values():
        for accessory_id in subject.accessory_ids:
            incoming[accessory_id] += 1
    ready = [subject_id for subject_id, degree in incoming.items()
             if degree == 0]
    visited = 0
    for subject_id in ready:
        visited += 1
        for accessory_id in sub[subject_id].accessory_ids:
            incoming[accessory_id] -= 1
            if incoming[accessory_id] == 0:
                ready.append(accessory_id)
    if visited != len(sub):
        raise RecordError('CYCLIC_ACCESSORY_LINK')
    for artifact in art.values():
        if any(subject_id not in sub for subject_id in artifact.subject_ids):
            raise RecordError('UNKNOWN_ARTIFACT_SUBJECT')
    if any(key not in art for key in qa):
        raise RecordError('UNKNOWN_QA_ARTIFACT')
    return {'schema_version': SCHEMA_VERSION, 'sources': len(src), 'masks': len(msk),
            'subjects': len(sub), 'artifacts': len(art), 'qa_results': len(qa),
            'verification': 'metadata_only_not_cricut_certification'}


def record_dict(record):
    """JSON-compatible representation; callers own durable serialization."""
    if not isinstance(record, (SourceAsset, Mask, Subject, Artifact, QAResult)):
        raise RecordError('UNSUPPORTED_RECORD_TYPE')
    return asdict(record)
