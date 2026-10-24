"""G2.2 optional ComfyUI HTTP bridge; default OFF.

Requires the existing ComfyUI authentication / same-origin boundary.
All client path-like values are reduced to whitelisted project names;
never read/write arbitrary files requested by a browser.
"""
from __future__ import annotations

import os
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
               'expected_recovery_sha256','confirmed'}
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
        limit = MAX_IMAGE_BYTES if key == 'image' and image else 2000
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

    return workspace
