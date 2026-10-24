"""G2.2: a bounded, server-owned .smartsvg project workspace.

This module never accepts absolute user paths, executes SVG, or certifies a
Cricut cut. It is intentionally independent of ComfyUI's HTTP runtime.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import struct
import zlib
from pathlib import Path
import re

from .project_archive import LoadedProject, ProjectArchiveError, load_project
from .project_contracts import SourceAsset, Mask, Subject
from .project_recovery import (
    RecoveryError, inspect_project, recover_previous, save_with_recovery,
)

NAME = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,47}$')
PROFILES = frozenset({
    'Auto - conserver le visuel', 'Sticker - contour du sujet',
    'Planche - 24 images (6x4)', 'Planche - 12 images (4x3)',
    'Carte - visuel rectangulaire',
})
MAX_IMAGE_BYTES = 12 * 1024 * 1024
MAX_PIXELS = 20_000_000
MAX_NOTE_LENGTH = 1500


class WorkspaceError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def _sha(data):
    return sha256(data).hexdigest()


def _valid_name(name):
    if not isinstance(name, str) or not NAME.fullmatch(name) or name.endswith('_previous'):
        raise WorkspaceError('INVALID_PROJECT_NAME')
    return name


def _width(value):
    if isinstance(value, bool):
        raise WorkspaceError('INVALID_WIDTH')
    try:
        numeric = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise WorkspaceError('INVALID_WIDTH') from exc
    if not 5 <= numeric <= 300:
        raise WorkspaceError('INVALID_WIDTH')
    return numeric


def _dpi(value):
    if type(value) is not int or value not in (300, 450):
        raise WorkspaceError('INVALID_DPI')
    return value


def _notes(value):
    if not isinstance(value, str) or len(value) > MAX_NOTE_LENGTH:
        raise WorkspaceError('INVALID_NOTES')
    return value


def _verify_png(data):
    """Decode a bounded, non-interlaced L/RGB/RGBA 8-bit PNG, including CRC.

    Only the source bytes are preserved. No unsafe image metadata or Python
    objects are deserialized. Incompatible variants fail explicitly.
    """
    if not isinstance(data, bytes) or not 40 <= len(data) <= MAX_IMAGE_BYTES:
        raise WorkspaceError('INVALID_IMAGE_BYTES')
    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise WorkspaceError('INVALID_PNG')
    pos, width, height, channels, mode = 8, 0, 0, None, None
    seen_header, seen_data, seen_end, data_ended = False, False, False, False
    fragments = []
    while pos < len(data):
        if pos + 12 > len(data):
            raise WorkspaceError('INVALID_PNG')
        count = struct.unpack('>I', data[pos:pos + 4])[0]
        if count > MAX_IMAGE_BYTES or pos + 12 + count > len(data):
            raise WorkspaceError('INVALID_PNG')
        kind = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + count]
        expected_crc = struct.unpack('>I', data[pos + 8 + count:pos + 12 + count])[0]
        if zlib.crc32(kind + payload) & 0xffffffff != expected_crc:
            raise WorkspaceError('PNG_CRC_FAILED')
        pos += 12 + count
        if not seen_header and kind != b'IHDR':
            raise WorkspaceError('INVALID_PNG')
        if kind == b'IHDR':
            if seen_header or count != 13:
                raise WorkspaceError('INVALID_PNG')
            width, height, depth, color, compression, filtering, interlace = struct.unpack(
                '>IIBBBBB', payload)
            if width < 1 or height < 1 or width * height > MAX_PIXELS:
                raise WorkspaceError('IMAGE_TOO_LARGE')
            if (depth, compression, filtering, interlace) != (8, 0, 0, 0):
                raise WorkspaceError('UNSUPPORTED_PNG_VARIANT')
            values = {0:(1, 'L'), 2:(3, 'RGB'), 6:(4, 'RGBA')}
            if color not in values:
                raise WorkspaceError('INVALID_IMAGE_MODE')
            channels, mode = values[color]
            seen_header = True
        elif kind == b'IDAT':
            if data_ended:
                raise WorkspaceError('INVALID_PNG')
            seen_data = True
            fragments.append(payload)
        elif kind == b'IEND':
            if not seen_data or count != 0 or pos != len(data):
                raise WorkspaceError('INVALID_PNG')
            seen_end = True
            break
        else:
            if seen_data:
                data_ended = True
            if not kind or (65 <= kind[0] <= 90):
                # Unknown critical chunks cannot be safely decoded.
                if kind != b'PLTE':
                    raise WorkspaceError('UNSUPPORTED_PNG_CHUNK')
    if not seen_end or not seen_data:
        raise WorkspaceError('INVALID_PNG')
    expected = height * (1 + width * channels)
    if expected > 90_000_000:
        raise WorkspaceError('IMAGE_TOO_LARGE')
    try:
        decoder = zlib.decompressobj()
        pixels = decoder.decompress(b''.join(fragments), expected + 1)
        if (len(pixels) != expected or not decoder.eof or
                decoder.unused_data or decoder.unconsumed_tail):
            raise WorkspaceError('INVALID_PNG_PIXELS')
    except zlib.error as exc:
        raise WorkspaceError('INVALID_PNG_PIXELS') from exc
    row = 1 + width * channels
    if any(pixels[offset] > 4 for offset in range(0, expected, row)):
        raise WorkspaceError('INVALID_PNG_FILTER')
    return width, height, mode


class ManagedWorkspace:
    def __init__(self, trusted_output_root):
        base = Path(trusted_output_root)
        if base.is_symlink() or not base.is_dir():
            raise WorkspaceError('INVALID_WORKSPACE_ROOT')
        root = base / 'SmartSVG_Managed_Projects'
        if root.is_symlink():
            raise WorkspaceError('INVALID_WORKSPACE_ROOT')
        root.mkdir(exist_ok=True)
        if not root.is_dir() or root.is_symlink():
            raise WorkspaceError('INVALID_WORKSPACE_ROOT')
        self.root = root

    def _path(self, name):
        _valid_name(name)
        file = self.root / (name + '.smartsvg')
        if file.is_symlink() or file.with_name(name + '.previous.smartsvg').is_symlink():
            raise WorkspaceError('UNSAFE_PROJECT_PATH')
        return file

    def create(self, name, source_png, *, profile, width_mm=40, dpi=300, notes=''):
        path = self._path(name)
        if path.exists() or path.with_name(name + '.previous.smartsvg').exists():
            raise WorkspaceError('PROJECT_ALREADY_EXISTS')
        if profile not in PROFILES:
            raise WorkspaceError('INVALID_PROFILE')
        mm, ppi, note = _width(width_mm), _dpi(dpi), _notes(notes)
        w, h, mode = _verify_png(source_png)
        digest = _sha(source_png)
        project = LoadedProject(
            project_id=name, app_version='g2.2-preview',
            sources=(SourceAsset('source-original', digest, w, h, mode,
                                 'manual_browser_png_import'),),
            masks=(), subjects=(), artifacts=(), qa_results=(),
            document={'profile':profile, 'width_mm':mm, 'dpi':ppi,
                      'notes':note, 'stage':'source_imported_only',
                      'cricut_certified':False},
            operations=[], resources={'sources/source-original.png':source_png},
            source_paths={'source-original':'sources/source-original.png'},
            mask_paths={},
        )
        try:
            saved = save_with_recovery(path, project)
        except (RecoveryError, ProjectArchiveError) as exc:
            raise WorkspaceError('SAVE_FAILED') from exc
        return {'name':name, 'status':'created', 'sha256':saved['sha256'],
                'source_dimensions_px':[w,h], 'certified':False}

    def list_projects(self):
        results=[]
        names=set()
        for entry in self.root.glob('*.smartsvg'):
            if entry.is_symlink():
                continue
            name=entry.name
            if name.endswith('.previous.smartsvg'):
                name=name[:-len('.previous.smartsvg')]
            elif name.endswith('.smartsvg'):
                name=name[:-len('.smartsvg')]
            else:
                continue
            if NAME.fullmatch(name) and not name.endswith('_previous'):
                names.add(name)
        for name in sorted(names)[:100]:
            results.append(self.inspect(name))
        return results

    def inspect(self, name):
        path=self._path(name)
        health=inspect_project(path)
        report={'name':name,'status':health.status,
                'primary':health.primary,'previous':health.previous,
                'recoverable':health.status=='PROJECT_RECOVERABLE',
                'certified':False,'message_fr':health.message_fr,
                'action_fr':health.action_fr}
        if health.status=='PROJECT_HEALTHY':
            loaded=load_project(path)
            report['document']={k:loaded.document.get(k) for k in
                ('profile','width_mm','dpi','notes','stage')}
            report['source_count']=len(loaded.sources)
            report['operations_count']=len(loaded.operations)
            report['subjects']=[{'subject_id':s.subject_id,'bbox_px':list(s.bbox_px),
                                 'mask_id':s.mask_id} for s in loaded.subjects[:32]]
            report['mask_count']=len(loaded.masks)
            report['sha256']=_sha(path.read_bytes())
        if health.status=='PROJECT_RECOVERABLE':
            previous=path.with_name(path.stem+'.previous.smartsvg')
            # An explicit restore request must carry a fingerprint of this snapshot.
            report['recovery_sha256']=_sha(previous.read_bytes())
        return report

    def update_notes(self, name, *, notes, expected_sha256):
        path=self._path(name)
        if not isinstance(expected_sha256,str) or len(expected_sha256)!=64:
            raise WorkspaceError('EXPECTED_REVISION_REQUIRED')
        if not path.is_file():
            raise WorkspaceError('PROJECT_NOT_FOUND')
        before=_sha(path.read_bytes())
        if before != expected_sha256:
            raise WorkspaceError('PROJECT_CHANGED')
        current=load_project(path)
        if current.project_id!=name:
            raise WorkspaceError('PROJECT_ID_MISMATCH')
        note=_notes(notes)
        modified=dict(current.document)
        modified['notes']=note
        if len(current.operations)>=4999:
            raise WorkspaceError('HISTORY_LIMIT')
        updated=replace(current,document=modified,
                        operations=[*current.operations,{'kind':'update_notes','notes':note}])
        try:
            result=save_with_recovery(path,updated,expected_sha256=before)
        except RecoveryError as exc:
            raise WorkspaceError(exc.code) from exc
        return {'name':name,'status':'updated','sha256':result['sha256'],
                'previous_available':result['previous_available'],'certified':False}

    def restore(self, name, *, expected_recovery_sha256, confirmed=False):
        path=self._path(name)
        if confirmed is not True:
            raise WorkspaceError('RESTORE_CONFIRMATION_REQUIRED')
        before=self.inspect(name)
        if not before['recoverable']:
            raise WorkspaceError('NOT_RECOVERABLE')
        if (not isinstance(expected_recovery_sha256,str) or
                before['recovery_sha256']!=expected_recovery_sha256):
            raise WorkspaceError('RECOVERY_SNAPSHOT_CHANGED')
        try:
            result=recover_previous(path,confirmed=True)
        except RecoveryError as exc:
            raise WorkspaceError(exc.code) from exc
        return {'name':name,'status':result['status'],
                'certified':False}

    def source_png(self, name):
        path=self._path(name)
        loaded=load_project(path)
        if loaded.project_id!=name or len(loaded.sources)!=1:
            raise WorkspaceError('INVALID_PROJECT_CONTENTS')
        path_id=loaded.source_paths[loaded.sources[0].source_id]
        if not path_id.endswith('.png'):
            raise WorkspaceError('SOURCE_NOT_PNG')
        return loaded.resources[path_id]


    def put_subject_mask(self, name, *, subject_id, mask_png, expected_sha256):
        """Atomically insert/replace one subject mask, leaving source untouched.

        Captures an audit entry and a single previous entire project snapshot.
        This does NOT create Cricut-ready geometry or replayable brush strokes.
        """
        from .mask_inspection_g23 import inspect_l8_mask

        path = self._path(name)
        if not isinstance(subject_id, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,47}', subject_id):
            raise WorkspaceError('INVALID_SUBJECT_ID')
        if not isinstance(expected_sha256, str) or not re.fullmatch('[0-9a-f]{64}', expected_sha256):
            raise WorkspaceError('EXPECTED_REVISION_REQUIRED')
        if not path.is_file():
            raise WorkspaceError('PROJECT_NOT_FOUND')
        before = _sha(path.read_bytes())
        if before != expected_sha256:
            raise WorkspaceError('PROJECT_CHANGED')
        project = load_project(path)
        if (project.project_id != name or len(project.sources) != 1 or
                project.artifacts or project.qa_results):
            raise WorkspaceError('PROJECT_EDIT_NOT_SUPPORTED')
        if project.document.get('stage') not in ('source_imported_only', 'subject_masks_available'):
            raise WorkspaceError('PROJECT_EDIT_NOT_SUPPORTED')
        if len(project.operations) >= 4999:
            raise WorkspaceError('HISTORY_LIMIT')
        source = project.sources[0]
        details = inspect_l8_mask(mask_png, source.width_px, source.height_px)
        old = next((m for m in project.masks if m.mask_id == 'mask-' + subject_id), None)
        if old is None and len(project.subjects) >= 32:
            raise WorkspaceError('TOO_MANY_SUBJECTS')
        if any(s.subject_id == subject_id and s.mask_id != 'mask-' + subject_id for s in project.subjects):
            raise WorkspaceError('SUBJECT_ID_CONFLICT')
        digest = _sha(mask_png)
        if old and old.sha256 == digest:
            raise WorkspaceError('MASK_UNCHANGED')
        mask = Mask('mask-' + subject_id, source.source_id, digest,
                    source.width_px, source.height_px)
        subject = Subject(subject_id, source.source_id, mask.mask_id, details['bbox_px'])
        masks = tuple(m for m in project.masks if m.mask_id != mask.mask_id) + (mask,)
        subjects = tuple(s for s in project.subjects if s.subject_id != subject_id) + (subject,)
        paths = dict(project.mask_paths)
        resource_path = 'masks/' + mask.mask_id + '.png'
        paths[mask.mask_id] = resource_path
        resources = dict(project.resources)
        resources[resource_path] = mask_png
        document = dict(project.document)
        document['stage'] = 'subject_masks_available'
        document['cricut_certified'] = False
        operation = {'kind': 'replace_subject_mask' if old else 'add_subject_mask',
                     'subject_id': subject_id,
                     'new_sha256': digest,
                     'previous_sha256': old.sha256 if old else None,
                     'bbox_px': list(details['bbox_px']),
                     'cut_certified': False}
        updated = replace(project, masks=masks, subjects=subjects, mask_paths=paths,
                          resources=resources, document=document,
                          operations=[*project.operations, operation])
        try:
            result = save_with_recovery(path, updated, expected_sha256=before)
        except RecoveryError as exc:
            raise WorkspaceError(exc.code) from exc
        return {'name': name, 'status': 'mask_saved',
                'subject_id': subject_id, 'bbox_px': list(details['bbox_px']),
                'selected_pixels': details['selected_pixels'],
                'sha256': result['sha256'], 'mask_sha256': digest,
                'previous_available': result['previous_available'],
                'certified': False}

    def subject_mask_png(self, name, subject_id):
        """Retrieve only an already registered L8 mask, never an arbitrary path."""
        path = self._path(name)
        if not isinstance(subject_id, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,47}', subject_id):
            raise WorkspaceError('INVALID_SUBJECT_ID')
        project = load_project(path)
        if project.project_id != name:
            raise WorkspaceError('PROJECT_ID_MISMATCH')
        subject = next((s for s in project.subjects if s.subject_id == subject_id), None)
        if subject is None:
            raise WorkspaceError('SUBJECT_NOT_FOUND')
        resource_path = project.mask_paths.get(subject.mask_id)
        if not resource_path or resource_path not in project.resources:
            raise WorkspaceError('MASK_NOT_FOUND')
        return project.resources[resource_path]
