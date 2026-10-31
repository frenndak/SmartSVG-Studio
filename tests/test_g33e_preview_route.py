"""G3.3e-b2a: read-only HTTP preview boundary, no ComfyUI or aiohttp needed.

V3.3 #71: browser opt-in, same-origin, bounded command, pinned Subject,
non-persistent PNG previews; CPU replay correctness is tested separately.
"""
import asyncio
import base64
from importlib.util import module_from_spec, spec_from_file_location
import json
import struct
import zlib
from pathlib import Path
import sys
import tempfile
from threading import Event, Lock
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[1] / 'engine'
PNG = b'\x89PNG\r\n\x1a\n'
SHA = 'a' * 64


def png(width=16, height=12, *, shade=128, color=0):
    channels = {0:1, 2:3}[color]
    def chunk(kind, data):
        return (struct.pack('>I',len(data)) + kind + data
                + struct.pack('>I',zlib.crc32(kind+data)&0xffffffff))
    header = struct.pack('>IIBBBBB',width,height,8,color,0,0,0)
    rows = (b'\x00'+bytes([shade])*(width*channels))*height
    return (PNG+chunk(b'IHDR',header)+chunk(b'IDAT',zlib.compress(rows))
            + chunk(b'IEND',b''))


BEFORE = png(shade=30)
AFTER = png(shade=210)


class Web:
    @staticmethod
    def json_response(payload, status=200, headers=None):
        return SimpleNamespace(payload=payload, status=status, headers=headers)


class Routes:
    def __init__(self):
        self.handlers = {}

    def get(self, path):
        return self._register('GET', path)

    def post(self, path):
        return self._register('POST', path)

    def _register(self, method, path):
        def register(fn):
            self.handlers[(method, path)] = fn
            return fn
        return register


class Part:
    def __init__(self, name, value):
        self.name = name
        self.data = str(value).encode('utf-8')
        self.done = False

    async def read_chunk(self, size=65536):
        if self.done:
            return b''
        self.done = True
        return self.data


class Reader:
    def __init__(self, pairs):
        self.parts = [Part(k, v) for k, v in pairs]

    async def next(self):
        return self.parts.pop(0) if self.parts else None


class Request:
    def __init__(self, pairs, *, origin='http://localhost:8188',
                 header=True):
        self.pairs = list(pairs)
        self.content_length = 1500
        self.headers = {'Host':'localhost:8188', 'Origin':origin}
        if header:
            self.headers['X-SmartSVG-UI'] = '1'

    async def multipart(self):
        return Reader(self.pairs)


def command():
    return [
        ('preview_version','1'),
        ('command_id','c'*32),
        ('name','subject-project'),
        ('expected_sha256',SHA),
        ('subject_id','subject-'+'d'*32),
        ('mask_id','base-mask-00'),
        ('mask_sha256_float32','e'*64),
        ('source_id','source-original'),
        ('source_sha256','f'*64),
        ('mode','add'),
        ('radius','0.05'),
        ('points',json.dumps([[0.5,0.5]])),
    ]


class PreviewRouteTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        package = 'smartsvg_preview_route_test_pkg'
        pkg = ModuleType(package)
        pkg.__path__ = [str(ENGINE)]
        self.modules = patch.dict(
            sys.modules, {package:pkg, 'aiohttp':SimpleNamespace(web=Web)})
        self.modules.start()
        self.addCleanup(self.modules.stop)
        spec = spec_from_file_location(package+'.project_routes_g22',
                                       ENGINE/'project_routes_g22.py')
        module = module_from_spec(spec)
        spec.loader.exec_module(module)
        self.routes = Routes()
        self.workspace = module.register_project_routes(
            self.routes, self.temp.name)
        self.handler = self.routes.handlers[
            ('POST','/smartsvg/g22/subject/preview')]

    async def test_success_is_opt_in_and_png_only_with_pinned_metadata(self):
        before = BEFORE
        after = AFTER
        result = {
            'name':'subject-project', 'project_sha256':SHA,
            'subject_id':'subject-'+'d'*32, 'mask_id':'base-mask-00',
            'source_sha256':'f'*64, 'dimensions_px':[16,12],
            'changed_pixels':3, 'before_png_l8':before,
            'after_png_l8':after,
            'preview_float32':b'SECRET_FLOAT32',
            'unrecognized_internal_field':b'NEVER_EXPORT',
        }
        with patch.object(self.workspace, 'preview_subject_brush_readonly',
                          return_value=result) as replay:
            response = await self.handler(Request(command()))
        self.assertEqual(response.status,200)
        self.assertEqual(response.headers['Cache-Control'],'no-store')
        self.assertEqual(response.payload['ok'],True)
        self.assertEqual(response.payload['certified'],False)
        payload = response.payload['preview']
        self.assertEqual(payload['command_id'],'c'*32)
        self.assertEqual(payload['project_sha256'],SHA)
        self.assertEqual(base64.b64decode(payload['before_png_base64']),before)
        self.assertEqual(base64.b64decode(payload['after_png_base64']),after)
        self.assertEqual(payload['persisted'],False)
        self.assertEqual(payload['cricut_certified'],False)
        self.assertNotIn('preview_float32',str(payload))
        self.assertNotIn('unrecognized_internal_field',str(payload))
        self.assertNotIn('SECRET_FLOAT32',str(response.payload))
        replay.assert_called_once()
        args,kwargs = replay.call_args
        self.assertEqual(args,('subject-project',))
        self.assertEqual(kwargs['expected_sha256'],SHA)
        self.assertEqual(kwargs['points'],[[0.5,0.5]])

    async def test_origin_header_and_malformed_commands_fail_before_cpu(self):
        with patch.object(self.workspace,'preview_subject_brush_readonly') as replay:
            for request,code,status in [
                (Request(command(),header=False),'ORIGIN_REJECTED',403),
                (Request(command(),origin='https://other.example'),
                 'ORIGIN_REJECTED',403),
                (Request([*command()[:-1],('points','not-json')]),
                 'INVALID_PREVIEW_REQUEST',400),
                (Request([*command()[:-2],('points','[]'),('points','[]')]),
                 'DUPLICATE_FIELD',400),
                (Request([(k,'2' if k=='preview_version' else v)
                          for k,v in command()]),
                 'INVALID_PREVIEW_VERSION',400),
                (Request([(k,'not-a-command' if k=='command_id' else v)
                          for k,v in command()]),
                 'INVALID_PREVIEW_COMMAND_ID',400),
                (Request([(k,'[]' if k=='points' else v)
                          for k,v in command()]),
                 'INVALID_PREVIEW_STROKE',400),
                (Request([(k,json.dumps([[0.5,0.5]]*65) if k=='points' else v)
                          for k,v in command()]),
                 'INVALID_PREVIEW_STROKE',400),
            ]:
                with self.subTest(code=code):
                    response=await self.handler(request)
                    self.assertEqual(response.status,status)
                    self.assertEqual(response.payload['error_code'],code)
                    self.assertEqual(response.headers['Cache-Control'],'no-store')
            replay.assert_not_called()

    async def test_cpu_preview_concurrency_is_bounded_without_leaking_slots(self):
        entered, release = Event(), Event()
        lock = Lock()
        active = 0
        def slow(*_args, **_kwargs):
            nonlocal active
            with lock:
                active += 1
                if active == 2:
                    entered.set()
            release.wait(3)
            return {
                'name':'subject-project','project_sha256':SHA,
                'subject_id':'subject-'+'d'*32,'mask_id':'base-mask-00',
                'source_sha256':'f'*64,'dimensions_px':[16,12],
                'changed_pixels':1,'before_png_l8':BEFORE,
                'after_png_l8':AFTER,
            }
        with patch.object(self.workspace,'preview_subject_brush_readonly',
                          side_effect=slow) as replay:
            first = asyncio.create_task(self.handler(Request(command())))
            second = asyncio.create_task(self.handler(Request(command())))
            try:
                self.assertTrue(await asyncio.to_thread(entered.wait,2),
                                'two CPU preview workers did not start')
                third = await self.handler(Request(command()))
                self.assertEqual(third.status,429)
                self.assertEqual(third.payload['error_code'],'PREVIEW_BUSY')
                self.assertEqual(replay.call_count,2)
            finally:
                release.set()
                results = await asyncio.gather(first,second,
                                               return_exceptions=True)
            self.assertEqual([r.status for r in results],[200,200])

    async def test_conflict_runtime_failure_and_non_png_fail_closed(self):
        from importlib import import_module
        error = import_module('smartsvg_preview_route_test_pkg.smartsvg_core.project_workspace_g22').WorkspaceError
        with patch.object(self.workspace,'preview_subject_brush_readonly',
                          side_effect=error('PROJECT_CHANGED')):
            response=await self.handler(Request(command()))
            self.assertEqual(response.status,409)
            self.assertEqual(response.payload['error_code'],'PROJECT_CHANGED')
        with patch.object(self.workspace,'preview_subject_brush_readonly',
                          side_effect=error('BRUSH_RUNTIME_UNAVAILABLE')):
            response=await self.handler(Request(command()))
            self.assertEqual(response.status,503)
            self.assertEqual(response.payload['error_code'],'BRUSH_RUNTIME_UNAVAILABLE')
        with patch.object(self.workspace,'preview_subject_brush_readonly',
                          return_value={'dimensions_px':[16,12],
                                        'before_png_l8':b'not-png',
                                        'after_png_l8':AFTER}):
            response=await self.handler(Request(command()))
            self.assertEqual(response.status,400)
            self.assertEqual(response.payload['error_code'],'INVALID_PREVIEW_OUTPUT')


    async def test_preview_png_integrity_dimensions_and_grayscale_fail_closed(self):
        # A PNG signature alone is insufficient: reject corrupted CRC,
        # truncated pixels, mismatched sizes and non-L8 formats.
        bad_crc = bytearray(BEFORE)
        bad_crc[-1] ^= 1
        cases = [
            ('truncated', BEFORE[:-1], AFTER),
            ('bad_crc', bytes(bad_crc), AFTER),
            ('wrong_dimensions', png(width=15), AFTER),
            ('rgb_not_l8', png(color=2), AFTER),
            ('trailing_bytes', BEFORE + b'extra', AFTER),
            ('invalid_after', BEFORE, AFTER[:-3]),
        ]
        for label, before, after in cases:
            with self.subTest(label=label), patch.object(
                    self.workspace, 'preview_subject_brush_readonly',
                    return_value={
                        'dimensions_px':[16,12],
                        'before_png_l8':before, 'after_png_l8':after,
                    }) as replay:
                response = await self.handler(Request(command()))
                self.assertEqual(response.status,400)
                self.assertEqual(response.payload['error_code'],
                                 'INVALID_PREVIEW_OUTPUT')
                self.assertEqual(response.headers['Cache-Control'],'no-store')
                replay.assert_called_once()


    async def test_preview_rejects_mismatched_identity_and_invalid_change_counts(self):
        # A late or faulty CPU result must not be labelled as the selected
        # Subject/revision. The HTTP boundary must fail closed before PNG
        # base64 is sent, even when both preview PNGs are structurally valid.
        valid = {
            'name':'subject-project','project_sha256':SHA,
            'subject_id':'subject-'+'d'*32,'mask_id':'base-mask-00',
            'source_sha256':'f'*64,'dimensions_px':[16,12],
            'changed_pixels':3,'before_png_l8':BEFORE,'after_png_l8':AFTER,
        }
        cases = [
            ('project', {'name':'another-project'}),
            ('revision', {'project_sha256':'b'*64}),
            ('subject', {'subject_id':'subject-'+'e'*32}),
            ('mask', {'mask_id':'base-mask-01'}),
            ('source', {'source_sha256':'e'*64}),
            ('missing_subject', {'subject_id':None}),
            ('negative_count', {'changed_pixels':-1}),
            ('oversized_count', {'changed_pixels':193}),
            ('bool_count', {'changed_pixels':True}),
            ('float_count', {'changed_pixels':1.5}),
        ]
        for label, change in cases:
            with self.subTest(label=label), patch.object(
                    self.workspace,'preview_subject_brush_readonly',
                    return_value={**valid, **change}) as replay:
                response=await self.handler(Request(command()))
                self.assertEqual(response.status,400)
                self.assertEqual(response.payload['error_code'],
                                 'INVALID_PREVIEW_OUTPUT')
                self.assertNotIn('preview',response.payload)
                self.assertEqual(response.headers['Cache-Control'],'no-store')
                replay.assert_called_once()


if __name__ == '__main__':
    unittest.main()
