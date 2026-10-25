"""G2.3 bounded editable mask checkpoint in a managed project.

Stores one L8 PNG mask and explicit reversible operation metadata.
This is a checkpoint, not a restored ComfyUI graph or physical-cut proof.
"""
from dataclasses import replace
from hashlib import sha256
from io import BytesIO
import struct
import zlib

from .project_archive import load_project
from .project_contracts import Mask
from .project_recovery import save_with_recovery, RecoveryError
from .project_workspace_g22 import WorkspaceError, _sha, _valid_name, MAX_IMAGE_BYTES


def _mask_png(data, expected_size):
    if not isinstance(data, bytes) or len(data) > MAX_IMAGE_BYTES or len(data) < 60:
        raise WorkspaceError('INVALID_MASK_BYTES')
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise WorkspaceError('INVALID_MASK_PNG')
    if data[12:16] != b'IHDR' or data[8:12] != b'\x00\x00\x00\r':
        raise WorkspaceError('INVALID_MASK_PNG')
    w,h,depth,color,comp,filt,interlace=struct.unpack('>IIBBBBB',data[16:29])
    if (w,h)!=expected_size or (depth,color,comp,filt,interlace)!=(8,0,0,0):
        raise WorkspaceError('MASK_DIMENSIONS_OR_MODE')
    pos=8
    compressed=[]
    seen_idat=False
    finished=False
    while pos<len(data):
        if pos+12>len(data):
            raise WorkspaceError('INVALID_MASK_PNG')
        size=int.from_bytes(data[pos:pos+4],'big')
        if size>MAX_IMAGE_BYTES or pos+12+size>len(data):
            raise WorkspaceError('INVALID_MASK_PNG')
        tag=data[pos+4:pos+8]
        chunk=data[pos+8:pos+8+size]
        crc=int.from_bytes(data[pos+8+size:pos+12+size],'big')
        if zlib.crc32(tag+chunk)&0xffffffff!=crc:
            raise WorkspaceError('MASK_CRC_FAILED')
        pos+=12+size
        if tag==b'IDAT':
            compressed.append(chunk)
            seen_idat=True
        elif tag==b'IEND':
            if size or pos!=len(data):
                raise WorkspaceError('INVALID_MASK_PNG')
            finished=True
        elif tag not in (b'IHDR',b'PLTE',b'tEXt',b'iTXt',b'zTXt',b'pHYs'):
            raise WorkspaceError('UNSUPPORTED_MASK_CHUNK')
    if not seen_idat or not finished:
        raise WorkspaceError('INVALID_MASK_PNG')
    expected=h*(1+w)
    try:
        decompressor=zlib.decompressobj()
        raw=decompressor.decompress(b''.join(compressed),expected+1)
        if len(raw)!=expected or not decompressor.eof or decompressor.unused_data or decompressor.unconsumed_tail:
            raise WorkspaceError('INVALID_MASK_PIXELS')
    except zlib.error as exc:
        raise WorkspaceError('INVALID_MASK_PIXELS') from exc
    if any(raw[i]>4 for i in range(0,len(raw),w+1)):
        raise WorkspaceError('INVALID_MASK_FILTER')
    return w,h


def checkpoint_mask(workspace, name, mask_png, *, expected_sha256, polarity='white_subject'):
    """Save a validated mask while retaining the original PNG and previous archive."""
    path=workspace._path(name)
    if polarity!='white_subject':
        raise WorkspaceError('INVALID_MASK_POLARITY')
    if not isinstance(expected_sha256,str) or len(expected_sha256)!=64:
        raise WorkspaceError('EXPECTED_REVISION_REQUIRED')
    if not path.is_file():
        raise WorkspaceError('PROJECT_NOT_FOUND')
    if _sha(path.read_bytes())!=expected_sha256:
        raise WorkspaceError('PROJECT_CHANGED')
    current=load_project(path)
    if current.project_id!=name or len(current.sources)!=1:
        raise WorkspaceError('INVALID_PROJECT_CONTENTS')
    source=current.sources[0]
    _mask_png(mask_png,(source.width_px,source.height_px))
    digest=sha256(mask_png).hexdigest()
    mask_id='working-mask'
    mask_path='masks/working-mask.png'
    if current.masks and (len(current.masks)!=1 or current.masks[0].mask_id!=mask_id):
        raise WorkspaceError('UNSUPPORTED_MASK_LAYOUT')
    if len(current.operations)>=4999:
        raise WorkspaceError('HISTORY_LIMIT')
    new_mask=Mask(mask_id=mask_id,source_id=source.source_id,sha256=digest,
                  width_px=source.width_px,height_px=source.height_px,
                  polarity=polarity)
    resources=dict(current.resources)
    resources[mask_path]=mask_png
    updated=replace(current,masks=(new_mask,),resources=resources,
                    mask_paths={mask_id:mask_path},
                    operations=[*current.operations,{
                        'kind':'mask_checkpoint','mask_id':mask_id,
                        'sha256':digest,'polarity':polarity}])
    try:
        saved=save_with_recovery(path,updated,expected_sha256=expected_sha256)
    except RecoveryError as exc:
        raise WorkspaceError(exc.code) from exc
    return {'name':name,'status':'mask_checkpoint_saved','sha256':saved['sha256'],
            'mask_sha256':digest,'previous_available':saved['previous_available'],
            'certified':False}


def load_mask(workspace,name):
    path=workspace._path(name)
    project=load_project(path)
    if project.project_id!=name:
        raise WorkspaceError('PROJECT_ID_MISMATCH')
    if not project.masks:
        raise WorkspaceError('MASK_NOT_FOUND')
    if len(project.masks)!=1 or project.masks[0].mask_id!='working-mask':
        raise WorkspaceError('UNSUPPORTED_MASK_LAYOUT')
    return project.resources[project.mask_paths['working-mask']]
