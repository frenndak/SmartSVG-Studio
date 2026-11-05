"""Local native-history status and explicit Undo/Redo transport."""
import importlib.util
from hashlib import sha256
import unittest
from unittest.mock import patch
import test_g33e_preview_route as transport
import test_g33e_brush_history as history


def status_fields():
    return [('history_version','1'),('name','subject-project')]


def apply_fields():
    return [*status_fields(),('expected_sha256','a'*64),('action','undo'),
            ('command_id','c'*32),('confirmed','yes')]


class BrushHistoryRouteTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        transport.PreviewRouteTests.setUp(self)
        self.status_handler=self.routes.handlers[('POST','/smartsvg/g22/subject/history/status')]
        self.apply_handler=self.routes.handlers[('POST','/smartsvg/g22/subject/history/apply')]

    async def test_origin_version_confirmation_and_action_are_checked_before_writer(self):
        with patch.object(self.workspace,'change_subject_brush_history') as writer:
            for request,code,status in (
                (transport.Request(apply_fields(),header=False),'ORIGIN_REJECTED',403),
                (transport.Request(apply_fields(),origin='https://other.example'),'ORIGIN_REJECTED',403),
                (transport.Request([(k,'2' if k=='history_version' else v) for k,v in apply_fields()]),'INVALID_BRUSH_HISTORY_VERSION',400),
                (transport.Request([(k,'no' if k=='confirmed' else v) for k,v in apply_fields()]),'BRUSH_HISTORY_CONFIRMATION_REQUIRED',400),
                (transport.Request([(k,'delete' if k=='action' else v) for k,v in apply_fields()]),'INVALID_BRUSH_HISTORY_REQUEST',400)):
                response=await self.apply_handler(request)
                self.assertEqual(response.status,status);self.assertEqual(response.payload['error_code'],code)
            writer.assert_not_called()

    async def test_status_is_explicit_readonly_and_pins_current_revision(self):
        expected=dict(name='subject-project',project_sha256='b'*64,
                      undo_available=False,redo_available=False,cricut_certified=False)
        with patch.object(self.workspace,'inspect',return_value={'status':'PROJECT_HEALTHY','sha256':'b'*64}),\
             patch.object(self.workspace,'subject_brush_history',return_value=expected) as read,\
             patch.object(self.workspace,'change_subject_brush_history') as write:
            response=await self.status_handler(transport.Request(status_fields()))
        self.assertEqual(response.payload['history'],expected)
        self.assertEqual(response.headers['Cache-Control'],'no-store')
        read.assert_called_once_with('subject-project',expected_sha256='b'*64)
        write.assert_not_called()

    async def test_uncertain_write_is_not_a_cancellation_or_a_success(self):
        with patch.object(self.workspace,'change_subject_brush_history',side_effect=
                          self.route_module.WorkspaceError('SAVE_FAILED')):
            response=await self.apply_handler(transport.Request(apply_fields()))
        self.assertEqual(response.payload['error_code'],'SAVE_OUTCOME_UNKNOWN')
        self.assertFalse(response.payload['ok'])

    async def test_revision_conflict_is_explicit(self):
        with patch.object(self.workspace,'change_subject_brush_history',side_effect=
                          self.route_module.WorkspaceError('PROJECT_CHANGED')):
            response=await self.apply_handler(transport.Request(apply_fields()))
        self.assertEqual(response.status,409);self.assertFalse(response.payload['ok'])

    @unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'),
                         'CPU brush dependencies not installed in stdlib-only G0')
    async def test_real_native_status_undo_redo_without_new_comfyui_report(self):
        case=history.BrushHistoryTests();case.setUp();self.addCleanup(case.doCleanups)
        original=case.rendered();case.save();edited=case.rendered()
        routes=transport.Routes()
        self.route_module.register_project_routes(routes,case.path.parent.parent)
        status=routes.handlers[('POST','/smartsvg/g22/subject/history/status')]
        apply=routes.handlers[('POST','/smartsvg/g22/subject/history/apply')]
        for index,action in enumerate(('undo','redo')):
            response=await status(transport.Request([('name','brush-preview'),('history_version','1')]))
            snapshot=response.payload['history']
            self.assertTrue(snapshot[action+'_available'])
            response=await apply(transport.Request(dict(name='brush-preview',history_version='1',
                expected_sha256=snapshot['project_sha256'],action=action,
                command_id=str(index)*32,confirmed='yes').items()))
            self.assertTrue(response.payload['result']['persisted'])
            self.assertFalse(response.payload['result']['cricut_certified'])
            self.assertEqual(case.rendered(),original if action=='undo' else edited)
