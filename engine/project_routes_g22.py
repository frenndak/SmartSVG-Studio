"""G2.2 optional ComfyUI HTTP bridge; default OFF.

Requires the existing ComfyUI authentication / same-origin boundary.
All client path-like values are reduced to whitelisted project names;
never read/write arbitrary files requested by a browser.
"""
from __future__ import annotations

import asyncio
import base64
import json
import os
import re
from urllib.parse import urlsplit

from .smartsvg_core.project_workspace_g22 import ManagedWorkspace, WorkspaceError, MAX_IMAGE_BYTES


def _browser_origin_ok(request):
    # A custom header is necessary (cross-site HTML forms cannot set it).
    if request.headers.get('X-SmartSVG-UI') != '1':
        return False
    origin = request.headers.get('Origin')
    if origin:
        parsed = urlsplit(origin)
        if parsed.scheme not in ('http', 'https') or parsed.netloc.lower() != request.headers.get('Host', '').lower():
            return False
    return True


async def _multipart_fields(request, *, image=False):
    if request.content_length is not None and request.content_length > MAX_IMAGE_BYTES + 65536:
        raise WorkspaceError('REQUEST_TOO_LARGE')
    reader = await request.multipart()
    fields = {}
    allowed = {'name','profile','width_mm','dpi','notes','expected_sha256',
               'expected_recovery_sha256','expected_pending_sha256',
               'expected_primary_sha256','expected_previous_sha256',
               'confirmed','editor_json','source_id','source_sha256',
               'mask_index','mask_id','mask_sha256_float32','expires_at_ms',
               'subject_id','mode','radius','points','preview_version',
               'command_id'}
    total = 0
    for _ in range(12):
        part = await reader.next()
        if part is None:
            break
        key = part.name
        if key not in allowed and key != 'image':
            raise WorkspaceError('UNKNOWN_FIELD')
        if key in fields:
            raise WorkspaceError('DUPLICATE_FIELD')
        limit = MAX_IMAGE_BYTES if key == 'image' and image else (350000 if key == 'editor_json' else (4096 if key == 'points' else 2000))
        if key == 'image' and not image:
            raise WorkspaceError('UNEXPECTED_IMAGE')
        chunks = []
        length = 0
        while True:
            block = await part.read_chunk(size=65536)
            if not block:
                break
            length += len(block)
            total += len(block)
            if length > limit or total > MAX_IMAGE_BYTES+65536:
                raise WorkspaceError('REQUEST_TOO_LARGE')
            chunks.append(block)
        data = b''.join(chunks)
        if key != 'image':
            try:
                fields[key] = data.decode('utf-8')
            except UnicodeDecodeError as exc:
                raise WorkspaceError('INVALID_FIELD_ENCODING') from exc
        else:
            fields[key] = data
    if await reader.next() is not None:
        raise WorkspaceError('TOO_MANY_FIELDS')
    return fields


def register_project_routes(routes, trusted_output_root):
    """Register narrow ComfyUI routes (called only after opt-in at load time)."""
    from aiohttp import web

    workspace = ManagedWorkspace(trusted_output_root)
    prefix = '/smartsvg/g22'

    def json_error(code, status=400):
        return web.json_response({'ok':False,'error_code':code,
                                  'certified':False},status=status)

    @routes.get(prefix+'/projects')
    async def projects(request):
        return web.json_response({'ok':True,'projects':workspace.list_projects(),
                                  'certified':False})

    @routes.get(prefix+'/project')
    async def project(request):
        try:
            return web.json_response({'ok':True,
                 'project':workspace.inspect(request.query.get('name')),'certified':False})
        except (WorkspaceError, ValueError) as exc:
            return json_error(getattr(exc,'code','INVALID_PROJECT'),404)

    @routes.get(prefix+'/source')
    async def source(request):
        try:
            image = workspace.source_png(request.query.get('name'))
            return web.Response(body=image,content_type='image/png',
                headers={'Cache-Control':'no-store','X-Content-Type-Options':'nosniff'})
        except (WorkspaceError, ValueError, OSError, KeyError) as exc:
            return json_error(getattr(exc,'code','SOURCE_UNAVAILABLE'),404)

    @routes.post(prefix+'/create')
    async def create(request):
        if not _browser_origin_ok(request):
            return json_error('ORIGIN_REJECTED',403)
        try:
            fields=await _multipart_fields(request,image=True)
            result=workspace.create(
                fields.get('name'),fields.get('image'),
                profile=fields.get('profile'),
                width_mm=fields.get('width_mm','40'),
                dpi=int(fields.get('dpi','300')),
                notes=fields.get('notes',''))
            return web.json_response({'ok':True,'result':result,'certified':False})
        except (WorkspaceError, ValueError, TypeError) as exc:
            return json_error(getattr(exc,'code','INVALID_REQUEST'))

    @routes.post(prefix+'/notes')
    async def notes(request):
        if not _browser_origin_ok(request):
            return json_error('ORIGIN_REJECTED',403)
        try:
            fields=await _multipart_fields(request)
            result=workspace.update_notes(fields.get('name'),
                notes=fields.get('notes',''),
                expected_sha256=fields.get('expected_sha256'))
            return web.json_response({'ok':True,'result':result,'certified':False})
        except (WorkspaceError, ValueError) as exc:
            return json_error(getattr(exc,'code','INVALID_REQUEST'))

    @routes.post(prefix+'/restore')
    async def restore(request):
        if not _browser_origin_ok(request):
            return json_error('ORIGIN_REJECTED',403)
        try:
            fields=await _multipart_fields(request)
            result=workspace.restore(
                fields.get('name'),
                expected_recovery_sha256=fields.get('expected_recovery_sha256'),
                confirmed=fields.get('confirmed')=='yes')
            return web.json_response({'ok':True,'result':result,'certified':False})
        except (WorkspaceError, ValueError) as exc:
            return json_error(getattr(exc,'code','INVALID_REQUEST'))

    @routes.post(prefix+'/resolve-pending')
    async def resolve_pending(request):
        if not _browser_origin_ok(request):
            return json_error('ORIGIN_REJECTED',403)
        try:
            fields=await _multipart_fields(request)
            result=workspace.resolve_pending(fields.get('name'),
                expected_pending_sha256=fields.get('expected_pending_sha256'),
                expected_primary_sha256=fields.get('expected_primary_sha256'),
                expected_previous_sha256=fields.get('expected_previous_sha256'),
                confirmed=fields.get('confirmed')=='yes')
            return web.json_response({'ok':True,'result':result,'certified':False},
                                     headers={'Cache-Control':'no-store'})
        except (WorkspaceError,ValueError) as exc:
            return json_error(getattr(exc,'code','INVALID_REQUEST'))

    @routes.post(prefix+'/subject/identity')
    async def subject_identity(request):
        if not _browser_origin_ok(request):
            return json_error('ORIGIN_REJECTED',403)
        try:
            fields=await _multipart_fields(request)
            result=workspace.register_subject_identity(
                fields.get('name'),
                mask_index=int(fields.get('mask_index','')),
                mask_id=fields.get('mask_id'),
                mask_sha256_float32=fields.get('mask_sha256_float32'),
                source_id=fields.get('source_id'),
                source_sha256=fields.get('source_sha256'),
                expected_sha256=fields.get('expected_sha256'),
                confirmed=fields.get('confirmed')=='yes',
                expires_at_ms=int(fields.get('expires_at_ms','')))
            return web.json_response(
                {'ok':True,'result':result,'certified':False},
                headers={'Cache-Control':'no-store'})
        except (WorkspaceError,ValueError,TypeError) as exc:
            return json_error(getattr(exc,'code','INVALID_SUBJECT_IDENTITY_REQUEST'))

    @routes.post(prefix+'/subject/preview')
    async def subject_preview(request):
        """G3.3e-b2a: opt-in, read-only CPU preview; never save or queue ComfyUI.

        PNGs are transported as base64 only; exact float32 and archive bytes
        never cross this HTTP boundary. The command_id lets the client discard
        stale responses; it is not a persistence or deduplication token.
        """
        headers = {'Cache-Control':'no-store',
                   'X-Content-Type-Options':'nosniff'}
        def error(code, status=400):
            return web.json_response(
                {'ok':False,'error_code':code,'certified':False},
                status=status,headers=headers)
        if not _browser_origin_ok(request):
            return error('ORIGIN_REJECTED',403)
        try:
            fields = await _multipart_fields(request)
            if fields.get('preview_version') != '1':
                raise WorkspaceError('INVALID_PREVIEW_VERSION')
            command_id = fields.get('command_id')
            if (type(command_id) is not str or
                    re.fullmatch(r'[0-9a-f]{32}',command_id) is None):
                raise WorkspaceError('INVALID_PREVIEW_COMMAND_ID')
            points = json.loads(fields.get('points',''))
            if not isinstance(points,list) or not 1 <= len(points) <= 64:
                raise WorkspaceError('INVALID_PREVIEW_STROKE')
            radius = float(fields.get('radius',''))
            # CPU replay is isolated from the async event loop and bounded
            # by the existing G2.4 snapshot and G2.3 single-stroke limits.
            # Timeout cancels delivery, not the already-running read-only CPU
            # thread. No state is ever persisted by this route.
            preview = await asyncio.wait_for(asyncio.to_thread(
                workspace.preview_subject_brush_readonly,
                fields.get('name'),
                expected_sha256=fields.get('expected_sha256'),
                subject_id=fields.get('subject_id'),
                mask_id=fields.get('mask_id'),
                mask_sha256_float32=fields.get('mask_sha256_float32'),
                source_id=fields.get('source_id'),
                source_sha256=fields.get('source_sha256'),
                mode=fields.get('mode'),radius=radius,points=points,
            ),timeout=15)
            before, after = preview['before_png_l8'], preview['after_png_l8']
            signature = b'\x89PNG\r\n\x1a\n'
            if any(type(blob) is not bytes or
                   not blob.startswith(signature) or
                   len(blob)>12*1024*1024 for blob in (before,after)):
                raise WorkspaceError('INVALID_PREVIEW_OUTPUT')
            result = {
                'command_id':command_id,
                'name':preview['name'],
                'project_sha256':preview['project_sha256'],
                'subject_id':preview['subject_id'],
                'mask_id':preview['mask_id'],
                'source_sha256':preview['source_sha256'],
                'dimensions_px':preview['dimensions_px'],
                'changed_pixels':preview['changed_pixels'],
                'before_png_base64':base64.b64encode(before).decode('ascii'),
                'after_png_base64':base64.b64encode(after).decode('ascii'),
                'persisted':False,'cricut_certified':False,
            }
            return web.json_response(
                {'ok':True,'preview':result,'certified':False},
                headers=headers)
        except asyncio.TimeoutError:
            return error('PREVIEW_TIMEOUT',504)
        except (WorkspaceError,ValueError,TypeError,KeyError,
                RecursionError,OverflowError) as exc:
            code = getattr(exc,'code','INVALID_PREVIEW_REQUEST')
            status = (409 if code in ('PROJECT_CHANGED',
                       'PROJECT_CHANGED_DURING_PREVIEW',
                       'PROJECT_NOT_HEALTHY') else
                      503 if code == 'BRUSH_RUNTIME_UNAVAILABLE' else 400)
            return error(code,status)

    @routes.get(prefix+'/editor')
    async def editor(request):
        try:
            session=workspace.editor_document(request.query.get('name'))
            return web.json_response({'ok':True,'session':session,'certified':False},
                                     headers={'Cache-Control':'no-store'})
        except (WorkspaceError,ValueError) as exc:
            return json_error(getattr(exc,'code','EDITOR_SESSION_UNAVAILABLE'),404)

    @routes.post(prefix+'/editor/save')
    async def save_editor(request):
        if not _browser_origin_ok(request):
            return json_error('ORIGIN_REJECTED',403)
        try:
            fields=await _multipart_fields(request)
            result=workspace.save_editor_document(
                fields.get('name'),editor_json=fields.get('editor_json'),
                expected_sha256=fields.get('expected_sha256'))
            return web.json_response({'ok':True,'result':result,'certified':False})
        except (WorkspaceError,ValueError) as exc:
            return json_error(getattr(exc,'code','INVALID_EDITOR_REQUEST'))

    return workspace
