"""G2.2 project persistence and browser controls, via existing admission CI."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from dataclasses import replace
from types import ModuleType, SimpleNamespace
from unittest.mock import patch
import struct
import zlib
import tempfile
import shutil
import subprocess
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'engine'


def load_tests(loader, standard_tests, pattern):
    if str(ENGINE) not in sys.path:
        sys.path.insert(0,str(ENGINE))
    path=ENGINE/'tests'/'test_project_workspace_g22.py'
    spec=spec_from_file_location('smartsvg_g22_workspace_tests',path)
    module=module_from_spec(spec)
    spec.loader.exec_module(module)
    result=loader.loadTestsFromModule(module)
    result.addTests(loader.loadTestsFromTestCase(ProjectPanelJSTests))
    result.addTests(loader.loadTestsFromTestCase(RoutePendingIntegrationTests))
    return result


class ProjectPanelJSTests(unittest.TestCase):
    def test_project_panel_node_js(self):
        node=shutil.which('node')
        if not node:
            self.skipTest('Node.js unavailable')
        r=subprocess.run([node,'--test',str(ENGINE/'tests'/'test_g22_project_panel.mjs')],
            cwd=ROOT,capture_output=True,text=True,timeout=35)
        self.assertEqual(r.returncode,0,r.stdout[-7000:]+r.stderr[-5000:])

    def test_optional_endpoints_not_registered_unconditionally(self):
        entry=(ENGINE/'__init__.py').read_text()
        self.assertIn("SMARTSVG_ENABLE_PROJECT_API",entry)
        self.assertIn("== '1'",entry)
        routes=(ENGINE/'project_routes_g22.py').read_text()
        self.assertIn("X-SmartSVG-UI",routes)
        self.assertIn("@routes.post(prefix+'/resolve-pending')",routes)
        self.assertIn("expected_pending_sha256=fields.get('expected_pending_sha256')",routes)
        self.assertIn("confirmed=fields.get('confirmed')=='yes'",routes)
        self.assertNotIn('os.system',routes)

class RoutePendingIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_confirmed_pending_route_rejects_origin_and_stale_hash(self):
        # Execute the actual route handler + real managed archive, with a
        # minimal aiohttp response stand-in (no ComfyUI or network required).
        from importlib.util import module_from_spec, spec_from_file_location
        import sys
        package='smartsvg_route_test_pkg'
        pkg=ModuleType(package)
        pkg.__path__=[str(ENGINE)]
        class Web:
            @staticmethod
            def json_response(payload, status=200, headers=None):
                return SimpleNamespace(payload=payload,status=status)
        class Routes:
            def __init__(self): self.handlers={}
            def get(self,path):
                def register(fn): self.handlers[('GET',path)]=fn; return fn
                return register
            def post(self,path):
                def register(fn): self.handlers[('POST',path)]=fn; return fn
                return register
        class Part:
            def __init__(self,name,value):
                self.name=name;self.value=str(value).encode('utf-8');self.done=False
            async def read_chunk(self,size=65536):
                if self.done:return b''
                self.done=True;return self.value
        class Reader:
            def __init__(self,fields):self.parts=[Part(k,v) for k,v in fields.items()]
            async def next(self):
                return self.parts.pop(0) if self.parts else None
        class Request:
            def __init__(self,fields,origin='http://localhost:8188',header=True):
                self.fields=fields;self.content_length=500
                self.headers={'Host':'localhost:8188','Origin':origin}
                if header:self.headers['X-SmartSVG-UI']='1'
            async def multipart(self):return Reader(self.fields)
        with patch.dict(sys.modules,{package:pkg,'aiohttp':SimpleNamespace(web=Web)}):
            spec=spec_from_file_location(package+'.project_routes_g22',
                                         ENGINE/'project_routes_g22.py')
            module=module_from_spec(spec)
            spec.loader.exec_module(module)
            with tempfile.TemporaryDirectory() as temp:
                routes=Routes()
                workspace=module.register_project_routes(routes,temp)
                def chunk(tag,payload):
                    return (struct.pack('>I',len(payload))+tag+payload+
                            struct.pack('>I',zlib.crc32(tag+payload)&0xffffffff))
                png=(b'\\x89PNG\\r\\n\\x1a\\n'+
                     chunk(b'IHDR',struct.pack('>IIBBBBB',8,6,8,6,0,0,0))+
                     chunk(b'IDAT',zlib.compress((b'\\x00'+b'\\x44'*32)*6))+
                     chunk(b'IEND',b''))
                workspace.create('snails',png,profile='Sticker - contour du sujet')
                first=workspace.inspect('snails')
                workspace.update_notes('snails',notes='v2',
                                       expected_sha256=first['sha256'])
                path=workspace.root/'snails.smartsvg'
                pending=workspace.root/'snails.pending-backup.smartsvg'
                previous=workspace.root/'snails.previous.smartsvg'
                old_backup=previous.read_bytes()
                shutil.copyfile(path,pending)
                from importlib import import_module
                archive=import_module(package+'.smartsvg_core.project_archive')
                current=archive.load_project(path)
                archive.save_project(path,replace(current,document={
                    **current.document,'notes':'v3'}),overwrite=True)
                state=workspace.inspect('snails')
                self.assertTrue(state['pending_resolution_available'])
                fields={'name':'snails','confirmed':'yes',
                        'expected_pending_sha256':state['pending_sha256'],
                        'expected_primary_sha256':state['primary_sha256'],
                        'expected_previous_sha256':state['previous_sha256']}
                handler=routes.handlers[('POST','/smartsvg/g22/resolve-pending')]
                blocked=await handler(Request(fields,origin='https://other.example'))
                self.assertEqual(blocked.status,403)
                blocked=await handler(Request(fields,header=False))
                self.assertEqual(blocked.status,403)
                blocked=await handler(Request({**fields,'confirmed':'no'}))
                self.assertEqual(blocked.payload['error_code'],
                                 'RECOVERY_CONFIRMATION_REQUIRED')
                blocked=await handler(Request({
                    **fields,'expected_primary_sha256':'0'*64}))
                self.assertEqual(blocked.payload['error_code'],
                                 'RECOVERY_SNAPSHOT_CHANGED')
                self.assertEqual(previous.read_bytes(),old_backup)
                self.assertTrue(pending.exists())
                result=await handler(Request(fields))
                self.assertEqual(result.status,200)
                self.assertEqual(result.payload['result']['status'],
                                 'pending_backup_finalized')
                self.assertFalse(pending.exists())
                self.assertEqual(archive.load_project(previous).document['notes'],'v2')
                self.assertEqual(archive.load_project(path).document['notes'],'v3')
