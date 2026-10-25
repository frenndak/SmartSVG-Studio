"""G2.2: a bounded, server-owned .smartsvg project workspace.

This module never accepts absolute user paths, executes SVG, or certifies a
Cricut cut. It is intentionally independent of ComfyUI's HTTP runtime.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json
import struct
import zlib
from pathlib import Path
import re

from .project_archive import LoadedProject, ProjectArchiveError, load_project
from .project_contracts import SourceAsset
from .editor_session_g23 import parse_editor_document, EditorSessionError
from .project_contracts import Mask
from .mask_snapshot_g24 import (
    SNAPSHOT_KEY, SNAPSHOT_PATH, create_snapshot, decode_snapshot,
    encode_preview_l8, MaskSnapshotError,
)
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
            report['sha256']=_sha(path.read_bytes())
            snap=loaded.document.get(SNAPSHOT_KEY)
            if isinstance(snap,dict):
                report['base_masks']={
                    'exact_float32':True,'count':snap['shape'][0],
                    'dimensions_px':[snap['shape'][2],snap['shape'][1]],
                    'editor_fingerprint':snap['editor_fingerprint'],
                    'source_fingerprint':snap['image_fingerprint'],
                    'physical_cut_verified':False,
                }
            session=loaded.document.get('editor_v216')
            if isinstance(session,dict):
                report['editor_session']={
                    'available':True,
                    'count':session.get('count'),
                    'stroke_count':len(session.get('strokes',[])),
                    'source_fingerprint':session.get('source'),
                    'base_masks_persisted':False,
                }
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


    def save_editor_document(self, name, *, editor_json, expected_sha256):
        """Persist V21.6 strokes only; check archive revision inside the lock."""
        path=self._path(name)
        if not isinstance(expected_sha256,str) or not re.fullmatch('[0-9a-f]{64}',expected_sha256):
            raise WorkspaceError('EXPECTED_REVISION_REQUIRED')
        if not path.is_file():
            raise WorkspaceError('PROJECT_NOT_FOUND')
        previous_hash=_sha(path.read_bytes())
        if previous_hash!=expected_sha256:
            raise WorkspaceError('PROJECT_CHANGED')
        try:
            previous=load_project(path)
        except ProjectArchiveError as exc:
            raise WorkspaceError('INVALID_PROJECT_CONTENTS') from exc
        if previous.project_id!=name or len(previous.sources)!=1:
            raise WorkspaceError('PROJECT_ID_MISMATCH')
        src=previous.sources[0]
        try:
            parsed,_=parse_editor_document(
                editor_json,source_dimensions=(src.width_px,src.height_px))
        except EditorSessionError as exc:
            raise WorkspaceError(exc.code) from exc
        snap=previous.document.get(SNAPSHOT_KEY)
        if snap is not None and parsed['source']!=snap['editor_fingerprint']:
            raise WorkspaceError('EDITOR_MASK_SNAPSHOT_MISMATCH')
        document=dict(previous.document)
        document['editor_v216']=parsed
        document['stage']='editor_strokes_saved_base_masks_external'
        if len(previous.operations)>=4999:
            raise WorkspaceError('HISTORY_LIMIT')
        ops=[*previous.operations,{'kind':'save_editor_v216',
                                  'source':parsed['source'],
                                  'stroke_count':len(parsed['strokes'])}]
        updated=replace(previous,document=document,operations=ops)
        try:
            saved=save_with_recovery(path,updated,expected_sha256=previous_hash)
        except RecoveryError as exc:
            raise WorkspaceError(exc.code) from exc
        return {'name':name,'status':'editor_session_saved',
                'sha256':saved['sha256'],
                'strokes_saved':len(parsed['strokes']),
                'base_masks_persisted':False,'certified':False}

    def editor_document(self, name):
        """Retrieve exact strokes for explicit import into a matching V21.6 node."""
        path=self._path(name)
        try:
            project=load_project(path)
        except (ProjectArchiveError,OSError) as exc:
            raise WorkspaceError('INVALID_PROJECT_CONTENTS') from exc
        if project.project_id!=name or len(project.sources)!=1:
            raise WorkspaceError('PROJECT_ID_MISMATCH')
        session=project.document.get('editor_v216')
        if session is None:
            raise WorkspaceError('EDITOR_SESSION_NOT_FOUND')
        try:
            _,canonical=parse_editor_document(json.dumps(
                session,ensure_ascii=False,allow_nan=False),
                source_dimensions=(project.sources[0].width_px,
                                   project.sources[0].height_px))
        except (EditorSessionError,ValueError,TypeError) as exc:
            raise WorkspaceError('CORRUPT_EDITOR_SESSION') from exc
        return {'name':name,'editor_json':canonical,
                'expected_sha256':_sha(path.read_bytes()),
                'base_masks_persisted':False,'certified':False}


    def save_base_masks(self, name, *, raw_float32, shape,
                        image_fingerprint, editor_fingerprint, expected_sha256):
        """Trusted node-only API. Browser routes never accept float mask payloads.

        The caller is responsible for verifying that the IMAGE tensor matches
        the project's original PNG and that editor_fingerprint was computed
        from exactly (IMAGE, raw base MASK). This module checks persistence,
        shapes and all resource consistency independently.
        """
        path=self._path(name)
        if not isinstance(expected_sha256,str) or not re.fullmatch('[0-9a-f]{64}',expected_sha256):
            raise WorkspaceError('EXPECTED_REVISION_REQUIRED')
        if not path.is_file():
            raise WorkspaceError('PROJECT_NOT_FOUND')
        current_sha=_sha(path.read_bytes())
        if current_sha!=expected_sha256:
            raise WorkspaceError('PROJECT_CHANGED')
        try:
            previous=load_project(path)
        except (ProjectArchiveError,OSError) as exc:
            raise WorkspaceError('INVALID_PROJECT_CONTENTS') from exc
        if previous.project_id!=name or len(previous.sources)!=1:
            raise WorkspaceError('PROJECT_ID_MISMATCH')
        try:
            meta,payload=create_snapshot(raw_float32,shape,
                image_fingerprint=image_fingerprint,
                editor_fingerprint=editor_fingerprint)
        except MaskSnapshotError as exc:
            raise WorkspaceError(exc.code) from exc
        src=previous.sources[0]
        count,height,width=meta['shape']
        if (width,height)!=(src.width_px,src.height_px):
            raise WorkspaceError('MASK_SOURCE_SIZE_MISMATCH')
        session=previous.document.get('editor_v216')
        if session and session.get('source')!=editor_fingerprint:
            raise WorkspaceError('EDITOR_MASK_SNAPSHOT_MISMATCH')
        if previous.masks and SNAPSHOT_KEY not in previous.document:
            raise WorkspaceError('EXISTING_MASKS_NOT_OWNED')
        resources={key:value for key,value in previous.resources.items()
                   if key!=SNAPSHOT_PATH and not key.startswith('masks/base-mask-')}
        records=[]
        paths={}
        step=width*height*4
        for i in range(count):
            mask_id=f'base-mask-{i:02d}'
            path_png=f'masks/{mask_id}.png'
            try:
                preview=encode_preview_l8(raw_float32[step*i:step*(i+1)],width,height)
            except MaskSnapshotError as exc:
                raise WorkspaceError(exc.code) from exc
            resources[path_png]=preview
            paths[mask_id]=path_png
            records.append(Mask(mask_id,src.source_id,_sha(preview),width,height))
        resources[SNAPSHOT_PATH]=payload
        document=dict(previous.document)
        document[SNAPSHOT_KEY]=meta
        document['stage']='full_resolution_base_masks_saved'
        if len(previous.operations)>=4999:
            raise WorkspaceError('HISTORY_LIMIT')
        updated=replace(previous,document=document,
            masks=tuple(records),mask_paths=paths,resources=resources,
            operations=[*previous.operations,{
                'kind':'capture_base_masks_float32_v1','count':count,
                'editor_fingerprint':editor_fingerprint}])
        try:
            saved=save_with_recovery(path,updated,expected_sha256=current_sha)
        except RecoveryError as exc:
            raise WorkspaceError(exc.code) from exc
        return {'name':name,'status':'full_resolution_masks_saved',
            'sha256':saved['sha256'],'count':count,
            'base_masks_exact':True,'certified':False}

    def base_masks(self,name,*,expected_sha256):
        """Get lossless float32 mask bytes only for the trusted ComfyUI node."""
        path=self._path(name)
        if not isinstance(expected_sha256,str) or not re.fullmatch('[0-9a-f]{64}',expected_sha256):
            raise WorkspaceError('EXPECTED_REVISION_REQUIRED')
        if not path.is_file():
            raise WorkspaceError('PROJECT_NOT_FOUND')
        if _sha(path.read_bytes())!=expected_sha256:
            raise WorkspaceError('PROJECT_CHANGED')
        try:
            loaded=load_project(path)
        except (ProjectArchiveError,OSError) as exc:
            raise WorkspaceError('INVALID_PROJECT_CONTENTS') from exc
        if loaded.project_id!=name:
            raise WorkspaceError('PROJECT_ID_MISMATCH')
        meta=loaded.document.get(SNAPSHOT_KEY)
        if meta is None:
            raise WorkspaceError('BASE_MASK_SNAPSHOT_NOT_FOUND')
        try:
            raw=decode_snapshot(meta,loaded.resources[SNAPSHOT_PATH])
        except (KeyError,MaskSnapshotError) as exc:
            raise WorkspaceError('INVALID_BASE_MASK_SNAPSHOT') from exc
        return raw,meta.copy()
