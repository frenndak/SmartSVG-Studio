"""G2.2: a bounded, server-owned .smartsvg project workspace.

This module never accepts absolute user paths, executes SVG, or certifies a
Cricut cut. It is intentionally independent of ComfyUI's HTTP runtime.
"""
from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import re

from PIL import Image, UnidentifiedImageError

from .project_archive import LoadedProject, ProjectArchiveError, load_project
from .project_contracts import SourceAsset
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
    if not isinstance(data, bytes) or not 40 <= len(data) <= MAX_IMAGE_BYTES:
        raise WorkspaceError('INVALID_IMAGE_BYTES')
    try:
        with Image.open(BytesIO(data)) as im:
            if im.format != 'PNG' or im.mode not in ('L', 'RGB', 'RGBA'):
                raise WorkspaceError('INVALID_IMAGE_MODE')
            w, h = im.size
            if w <= 0 or h <= 0 or w*h > MAX_PIXELS:
                raise WorkspaceError('IMAGE_TOO_LARGE')
            mode = im.mode
            im.verify()
        # Decode for completeness rather than trusting a valid-looking IHDR.
        with Image.open(BytesIO(data)) as im:
            im.load()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        if isinstance(exc, WorkspaceError):
            raise
        raise WorkspaceError('INVALID_PNG') from exc
    return w, h, mode


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
