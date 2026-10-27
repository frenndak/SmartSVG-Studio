"""G2.4: exact float32 base-mask snapshots plus deterministic full-res L8 previews.

The float32 resource preserves soft-mask pixels bit for bit. PNG previews are
separate for human inspection; never use them for deterministic V21.6 replay.
Pure Python standard library to keep G0 admission independent from numpy/torch.
"""
from __future__ import annotations

from array import array
from hashlib import sha256
import math
import struct
import sys
import zlib

SNAPSHOT_PATH='snapshots/base_masks_float32_v1.zlib'
SNAPSHOT_KEY='base_masks_f32_v1'
MAX_VALUES=8_000_000
PNG_HEADER=b'\x89PNG\r\n\x1a\n'


class MaskSnapshotError(ValueError):
    def __init__(self,code):
        self.code=code
        super().__init__(code)


def _floats(blob, count):
    if type(blob) is not bytes or len(blob)!=count*4:
        raise MaskSnapshotError('INVALID_MASK_FLOAT32_BYTES')
    a=array('f')
    if a.itemsize != 4:
        raise MaskSnapshotError('UNSUPPORTED_FLOAT32_PLATFORM')
    a.frombytes(blob)
    if sys.byteorder!='little':
        a.byteswap()
    for value in a:
        if not math.isfinite(value) or not -0.001<=value<=1.001:
            raise MaskSnapshotError('INVALID_MASK_FLOAT32_RANGE')
    return a


def encode_preview_l8(raw, width, height):
    """Pack canonical full-resolution grayscale PNG; no downsampling."""
    if type(width) is not int or type(height) is not int or width<1 or height<1:
        raise MaskSnapshotError('INVALID_MASK_SHAPE')
    a=_floats(raw,width*height)
    def chunk(name,payload):
        return struct.pack('>I',len(payload))+name+payload+struct.pack(
            '>I',zlib.crc32(name+payload)&0xffffffff)
    # Exactly the same quantization policy as the V21.6 preview engine.
    px=bytes(max(0,min(255,round(max(0,min(1,v))*255))) for v in a)
    rows=b''.join(b'\0'+px[y*width:(y+1)*width] for y in range(height))
    header=struct.pack('>IIBBBBB',width,height,8,0,0,0,0)
    return PNG_HEADER+chunk(b'IHDR',header)+chunk(b'IDAT',zlib.compress(rows,6))+chunk(b'IEND',b'')


def create_snapshot(raw, shape, *, image_fingerprint, editor_fingerprint):
    """Create strict bounded metadata & compressed bytes from contiguous <f4."""
    if (not isinstance(shape,(list,tuple)) or len(shape)!=3 or
        any(type(x) is not int or x<1 for x in shape)):
        raise MaskSnapshotError('INVALID_MASK_SHAPE')
    count,height,width=shape
    if count>32 or count*height*width>MAX_VALUES or width*height>5_000_000:
        raise MaskSnapshotError('MASK_SNAPSHOT_TOO_LARGE')
    for digest in (image_fingerprint,editor_fingerprint):
        if not isinstance(digest,str) or len(digest)!=64 or any(
            c not in '0123456789abcdef' for c in digest):
            raise MaskSnapshotError('INVALID_MASK_FINGERPRINT')
    _floats(raw,count*height*width)
    compressed=zlib.compress(raw,6)
    meta={
        'version':1,'resource':SNAPSHOT_PATH,'shape':[count,height,width],
        'sha256_raw':sha256(raw).hexdigest(),
        'image_fingerprint':image_fingerprint,
        'editor_fingerprint':editor_fingerprint,
        'base_masks_exact':True,'cricut_certified':False,
    }
    return meta,compressed


def decode_snapshot(meta,compressed):
    """Validate and decompress once with hard upper bound and no trailing bytes."""
    if not isinstance(meta,dict) or set(meta)!={
        'version','resource','shape','sha256_raw','image_fingerprint',
        'editor_fingerprint','base_masks_exact','cricut_certified'}:
        raise MaskSnapshotError('INVALID_MASK_SNAPSHOT_SCHEMA')
    if type(meta['version']) is not int or meta['version']!=1 or meta['resource']!=SNAPSHOT_PATH:
        raise MaskSnapshotError('INVALID_MASK_SNAPSHOT_SCHEMA')
    shape=meta['shape']
    if (not isinstance(shape,list) or len(shape)!=3 or
        any(type(x) is not int or x<1 for x in shape)):
        raise MaskSnapshotError('INVALID_MASK_SHAPE')
    count,height,width=shape
    if count>32 or width*height>5_000_000 or count*height*width>MAX_VALUES:
        raise MaskSnapshotError('MASK_SNAPSHOT_TOO_LARGE')
    if meta['base_masks_exact'] is not True or meta['cricut_certified'] is not False:
        raise MaskSnapshotError('INVALID_MASK_SNAPSHOT_SCHEMA')
    for field in ('sha256_raw','image_fingerprint','editor_fingerprint'):
        item=meta[field]
        if not isinstance(item,str) or len(item)!=64 or any(
            ch not in '0123456789abcdef' for ch in item):
            raise MaskSnapshotError('INVALID_MASK_FINGERPRINT')
    if type(compressed) is not bytes or not compressed or len(compressed)>64*1024*1024:
        raise MaskSnapshotError('INVALID_MASK_COMPRESSED_BYTES')
    try:
        decompressor=zlib.decompressobj()
        raw=decompressor.decompress(compressed,count*height*width*4+1)
        if (len(raw)!=count*height*width*4 or not decompressor.eof or
            decompressor.unconsumed_tail or decompressor.unused_data):
            raise MaskSnapshotError('MASK_SNAPSHOT_ZLIB_INVALID')
    except zlib.error as exc:
        raise MaskSnapshotError('MASK_SNAPSHOT_ZLIB_INVALID') from exc
    if sha256(raw).hexdigest()!=meta['sha256_raw']:
        raise MaskSnapshotError('MASK_SNAPSHOT_SHA_MISMATCH')
    _floats(raw,count*height*width)
    return raw


def validate_archive_snapshot(project):
    """Called from G1.3 archive admission for every load and every save."""
    meta=project.document.get(SNAPSHOT_KEY) if isinstance(project.document,dict) else None
    if meta is None:
        return ()
    if not isinstance(meta,dict) or not isinstance(meta.get('shape'),list) or len(meta['shape'])!=3:
        raise MaskSnapshotError('INVALID_MASK_SNAPSHOT_SCHEMA')
    count,height,width=meta['shape']
    if type(count) is not int or not 1<=count<=32:
        raise MaskSnapshotError('INVALID_MASK_SHAPE')
    if len(project.sources)!=1 or not isinstance(project.sources[0].source_id,str):
        raise MaskSnapshotError('MASK_SNAPSHOT_REQUIRES_SINGLE_SOURCE')
    if (project.sources[0].width_px,project.sources[0].height_px)!=(width,height):
        raise MaskSnapshotError('MASK_SOURCE_SIZE_MISMATCH')
    if len(project.masks)!=count or len(project.mask_paths)!=count:
        raise MaskSnapshotError('MASK_SNAPSHOT_PREVIEW_COUNT')
    compressed=project.resources.get(SNAPSHOT_PATH)
    raw=decode_snapshot(meta,compressed)
    mask_bytes=width*height*4
    from hashlib import sha256 as hash256
    for i in range(count):
        record=project.masks[i]
        mask_id=f'base-mask-{i:02d}'
        path=f'masks/{mask_id}.png'
        if record.mask_id!=mask_id or record.source_id!=project.sources[0].source_id or (
            record.width_px,record.height_px)!=(width,height) or project.mask_paths.get(mask_id)!=path:
            raise MaskSnapshotError('MASK_SNAPSHOT_PREVIEW_ID_MISMATCH')
        expected=encode_preview_l8(raw[i*mask_bytes:(i+1)*mask_bytes],width,height)
        actual=project.resources.get(path)
        if actual!=expected or hash256(expected).hexdigest()!=record.sha256:
            raise MaskSnapshotError('MASK_SNAPSHOT_PREVIEW_MISMATCH')
    return (SNAPSHOT_PATH,)
