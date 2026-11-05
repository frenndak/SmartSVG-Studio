"""V34-132: explicit, bounded same-origin save of an accepted brush preview."""
import asyncio
import importlib.util
import json
from hashlib import sha256
from pathlib import Path
from threading import Event, Lock
import unittest
from unittest.mock import patch
import test_g33e_preview_route as transport
import test_g33e_subject_brush_preview as brush


def fields():
    return [(('save_version' if k=='preview_version' else k),v)
            for k,v in transport.command()] + [
        ('confirmed','yes'), ('expected_preview_mask_sha256_float32','b'*64)]


class BrushSaveRouteTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        transport.PreviewRouteTests.setUp(self)
        self.save_handler = self.routes.handlers[('POST','/smartsvg/g22/subject/save')]

    async def test_origin_confirmation_and_version_refuse_before_worker(self):
        with patch.object(self.workspace,'save_subject_brush') as save:
            cases=[(transport.Request(fields(),header=False),403,'ORIGIN_REJECTED'),
                   (transport.Request(fields(),origin='https://other.example'),403,'ORIGIN_REJECTED'),
                   (transport.Request([(k,'no' if k=='confirmed' else v) for k,v in fields()]),400,'BRUSH_SAVE_CONFIRMATION_REQUIRED'),
                   (transport.Request([(k,'2' if k=='save_version' else v) for k,v in fields()]),400,'INVALID_BRUSH_SAVE_VERSION')]
            for request,status,code in cases:
                response=await self.save_handler(request)
                self.assertEqual(response.status,status)
                self.assertEqual(response.payload['error_code'],code)
            save.assert_not_called()

    async def test_revision_conflict_reports_no_success_and_no_cached_response(self):
        with patch.object(self.workspace,'save_subject_brush',side_effect=
                          self.route_module.WorkspaceError('PROJECT_CHANGED')):
            response=await self.save_handler(transport.Request(fields()))
        self.assertEqual(response.status,409)
        self.assertFalse(response.payload['ok'])
        self.assertEqual(response.headers['Cache-Control'],'no-store')

    async def test_worker_failure_is_not_reported_as_a_safe_retry(self):
        with patch.object(self.workspace,'save_subject_brush',side_effect=
                          self.route_module.WorkspaceError('SAVE_FAILED')):
            response=await self.save_handler(transport.Request(fields()))
        self.assertEqual(response.payload['error_code'],'SAVE_OUTCOME_UNKNOWN')
        self.assertFalse(response.payload['ok'])

    async def test_extra_or_duplicate_fields_refuse_before_save(self):
        with patch.object(self.workspace,'save_subject_brush') as save:
            for pairs,code in (([*fields(),('notes','extra')],'TOO_MANY_FIELDS'),
                               ([*fields(),('confirmed','yes')],'TOO_MANY_FIELDS'),
                               ([*fields()[:-1],('confirmed','yes')],'DUPLICATE_FIELD')):
                response=await self.save_handler(transport.Request(pairs))
                self.assertEqual(response.payload['error_code'],code)
            save.assert_not_called()

    async def test_cancelled_http_write_keeps_slots_until_workers_finish(self):
        started=Event();release=Event();lock=Lock();count=0
        def blocked(name,**kwargs):
            nonlocal count
            with lock:
                count+=1
                if count==2:started.set()
            release.wait(timeout=4)
            return dict(name=name,status='subject_brush_saved',sha256='b'*64,
                        command_id=kwargs['command_id'],persisted=True,cricut_certified=False)
        with patch.object(self.workspace,'save_subject_brush',side_effect=blocked):
            tasks=[asyncio.create_task(self.save_handler(transport.Request(fields()))) for _ in range(2)]
            try:
                self.assertTrue(await asyncio.to_thread(started.wait,2))
                tasks[0].cancel()
                with self.assertRaises(asyncio.CancelledError):await tasks[0]
                overloaded=await self.save_handler(transport.Request(fields()))
                self.assertEqual(overloaded.status,429)
                self.assertEqual(overloaded.payload['error_code'],'PREVIEW_BUSY')
            finally:
                release.set()
                await asyncio.gather(*tasks,return_exceptions=True)

    @unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'),
                         'CPU brush dependencies not installed in stdlib-only G0')
    async def test_real_preview_save_reopen_and_duplicate_ack_preserve_base_resources(self):
        case=brush.SubjectBrushPreviewTests();case.setUp()
        self.addCleanup(case.doCleanups)
        routes=transport.Routes()
        workspace=self.route_module.register_project_routes(routes,case.path.parent.parent)
        handler=routes.handlers[('POST','/smartsvg/g22/subject/save')]
        project,command=case.command()
        revision=sha256(case.path.read_bytes()).hexdigest()
        preview=workspace.preview_subject_brush_readonly('brush-preview',
            expected_sha256=revision,**command)
        request_fields=dict(save_version='1', command_id='a'*32,name='brush-preview',
            expected_sha256=revision,confirmed='yes',
            expected_preview_mask_sha256_float32=preview['preview_mask_sha256_float32'],
            **{k:json.dumps(v) if k=='points' else str(v) for k,v in command.items()})
        response=await handler(transport.Request(request_fields.items()))
        self.assertEqual(response.status,200)
        self.assertTrue(response.payload['result']['persisted'])
        self.assertFalse(response.payload['result']['cricut_certified'])
        from smartsvg_core.project_archive import load_project
        self.assertEqual(load_project(case.path).resources,project.resources)
        saved=case.path.read_bytes()
        response=await handler(transport.Request(request_fields.items()))
        self.assertEqual(response.payload['result']['status'],'subject_brush_already_saved')
        self.assertEqual(case.path.read_bytes(),saved)
