"""V34-035/038: persistent native-session Undo/Redo, no base pixel mutation."""
from dataclasses import replace
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'engine'))
import test_g33e_brush_composition as composition
from smartsvg_core.project_archive import load_project,save_project
from smartsvg_core.project_workspace_g22 import ManagedWorkspace,WorkspaceError
from smartsvg_core import project_recovery


@unittest.skipUnless(importlib.util.find_spec('numpy') and importlib.util.find_spec('PIL'),
                     'CPU brush dependencies not installed in stdlib-only G0')
class BrushHistoryTests(unittest.TestCase):
    def setUp(self):
        composition.BrushCompositionTests.setUp(self)

    def gesture(self,index=0,**changes):
        return composition.BrushCompositionTests.gesture(self,index,**changes)

    def save(self,**kwargs):
        return composition.BrushCompositionTests.save(self,**kwargs)

    def change(self,history_action,command_id,**changes):
        request=dict(expected_sha256=sha256(self.path.read_bytes()).hexdigest(),
                     action=history_action,command_id=command_id,confirmed=True)
        request.update(changes)
        return self.workspace.change_subject_brush_history('brush-preview',**request),request

    def files(self):
        return {p.name:p.read_bytes() for p in self.path.parent.iterdir()}

    def rendered(self):
        import numpy as np
        from smartsvg_editor.strokes import apply_strokes
        project=load_project(self.path)
        revision=sha256(self.path.read_bytes()).hexdigest()
        raw,meta=self.workspace.base_masks('brush-preview',expected_sha256=revision)
        return apply_strokes(np.frombuffer(raw,dtype='<f4').reshape(meta['shape']),
                            project.document.get('editor_v216',{}).get('strokes',[])).tobytes()

    def status(self):
        return self.workspace.subject_brush_history('brush-preview',
            expected_sha256=sha256(self.path.read_bytes()).hexdigest())

    def test_undo_redo_survive_reopen_and_restore_exact_float32_render(self):
        original=load_project(self.path);raw_before=self.rendered()
        self.save(points=[[0.8,0.8]])
        rendered_first=self.rendered()
        self.save(command_id='second',index=1,mode='erase',points=[[0.125,0.18]])
        rendered_second=self.rendered()
        self.assertTrue(self.status()['undo_available'])
        undone,_=self.change('undo','undo-2')
        self.assertEqual(self.rendered(),rendered_first)
        self.assertTrue(undone['persisted']);self.assertFalse(undone['cricut_certified'])
        self.workspace=ManagedWorkspace(self.path.parent.parent)
        self.change('undo','undo-1')
        self.assertEqual(self.rendered(),raw_before)
        self.assertNotIn('editor_v216',load_project(self.path).document)
        self.assertFalse(self.status()['undo_available']);self.assertTrue(self.status()['redo_available'])
        self.change('redo','redo-1');self.assertEqual(self.rendered(),rendered_first)
        self.change('redo','redo-2');self.assertEqual(self.rendered(),rendered_second)
        reopened=load_project(self.path)
        self.assertEqual(reopened.resources,original.resources)
        self.assertEqual(reopened.subjects,original.subjects)
        self.assertEqual(reopened.masks,original.masks)
        self.assertEqual(len([op for op in reopened.operations if op.get('kind')=='subject_brush_history_g33e_v1']),4)

    def test_continuous_stroke_reopens_and_undo_redo_restore_exact_pixels(self):
        import numpy as np
        original=load_project(self.path)
        before=self.rendered()
        points=[[0.1,0.8],[0.5,0.8],[0.9,0.8]]
        self.save(mode='add',radius=0.05,points=points)
        reopened=load_project(self.path)
        self.assertEqual(reopened.document['editor_v216']['strokes'][-1]['points'],points)
        rendered=self.rendered()
        old=np.frombuffer(before,dtype='<f4').reshape(2,12,16)
        new=np.frombuffer(rendered,dtype='<f4').reshape(2,12,16)
        # The horizontal line at source row 9 fills intermediate pixels too.
        self.assertTrue(np.all(new[0,9,2:15]==1))
        self.assertEqual(new[0,0,0].tobytes(),old[0,0,0].tobytes())
        self.assertEqual(new[1].tobytes(),old[1].tobytes())
        self.workspace=ManagedWorkspace(self.path.parent.parent)
        self.change('undo','undo-continuous');self.assertEqual(self.rendered(),before)
        self.change('redo','redo-continuous');self.assertEqual(self.rendered(),rendered)
        self.assertEqual(load_project(self.path).resources,original.resources)

    def test_new_edit_after_undo_clears_redo_without_deleting_audit(self):
        self.save();self.save(command_id='second',mode='erase')
        self.change('undo','undo-2')
        count=len(load_project(self.path).operations)
        self.save(command_id='branch',points=[[0.8,0.8]])
        self.assertFalse(self.status()['redo_available'])
        before=self.files()
        with self.assertRaisesRegex(WorkspaceError,'BRUSH_NOTHING_TO_REDO'):
            self.change('redo','invalid-redo')
        self.assertEqual(self.files(),before)
        self.assertEqual(len(load_project(self.path).operations),count+1)

    def test_notes_are_retained_and_exports_are_not_removed_by_undo(self):
        self.save()
        self.workspace.update_notes('brush-preview',notes='keep these notes',
            expected_sha256=sha256(self.path.read_bytes()).hexdigest())
        export=self.path.parent/'already-exported.svg';export.write_text('<svg/>')
        self.change('undo','with-notes')
        self.assertEqual(load_project(self.path).document['notes'],'keep these notes')
        self.assertEqual(export.read_text(),'<svg/>')

    def test_identical_retry_is_readonly_and_command_id_cannot_change_action(self):
        self.save();saved,request=self.change('undo','one-id')
        before=self.files()
        retry=self.workspace.change_subject_brush_history('brush-preview',**request)
        self.assertEqual(retry['status'],'brush_history_already_applied')
        self.assertEqual(retry['sha256'],saved['sha256']);self.assertEqual(self.files(),before)
        with self.assertRaisesRegex(WorkspaceError,'BRUSH_COMMAND_ID_REUSED'):
            self.workspace.change_subject_brush_history('brush-preview',**{**request,'action':'redo'})
        self.assertEqual(self.files(),before)

    def test_confirmation_stale_revision_and_empty_history_never_write(self):
        before=self.files()
        for changes,error in (({'confirmed':False},'BRUSH_HISTORY_CONFIRMATION_REQUIRED'),
                              ({'confirmed':1},'BRUSH_HISTORY_CONFIRMATION_REQUIRED'),
                              ({'expected_sha256':'f'*64},'PROJECT_CHANGED'),
                              ({'action':'delete'},'INVALID_BRUSH_HISTORY_REQUEST'),
                              ({},'BRUSH_NOTHING_TO_UNDO')):
            with self.subTest(changes=changes),self.assertRaisesRegex(WorkspaceError,error):
                self.change('undo','test-command',**changes)
            self.assertEqual(self.files(),before)

    def test_native_editor_replacement_is_a_history_boundary(self):
        self.save()
        project=load_project(self.path)
        session={**project.document['editor_v216'],'strokes':[]}
        self.workspace.save_editor_document('brush-preview',editor_json=json.dumps(session),
            expected_sha256=sha256(self.path.read_bytes()).hexdigest())
        self.assertFalse(self.status()['undo_available'])
        with self.assertRaisesRegex(WorkspaceError,'BRUSH_NOTHING_TO_UNDO'):
            self.change('undo','after-native')

    def test_direct_native_editor_drift_is_rejected_without_writes(self):
        self.save()
        project=load_project(self.path)
        save_project(self.path,replace(project,document={**project.document,
            'editor_v216':{**project.document['editor_v216'],'strokes':[]}}),overwrite=True)
        before=self.files()
        with self.assertRaisesRegex(WorkspaceError,'BRUSH_HISTORY_CHANGED'):
            self.change('undo','after-drift')
        self.assertEqual(self.files(),before)

    def test_pending_recovery_and_write_failure_keep_recovery_contract(self):
        self.save();before=self.files()
        with patch.object(project_recovery,'save_project',side_effect=OSError('disk full')):
            with self.assertRaisesRegex(WorkspaceError,'SAVE_FAILED'):
                self.change('undo','disk-full')
        self.assertEqual(self.files(),before)

    def test_legacy_compact_receipt_can_be_undone_and_redone_without_migration(self):
        self.save()
        project=load_project(self.path)
        receipt={**project.operations[-1],'kind':'save_subject_brush_g33e_b2b2'}
        for key in ('previous_editor_sha256','source_sha256','base_mask_sha256_float32','base_snapshot_sha256'):
            receipt.pop(key)
        save_project(self.path,replace(project,operations=[*project.operations[:-1],receipt]),overwrite=True)
        rendered=self.rendered()
        self.change('undo','legacy-undo')
        self.assertNotIn('editor_v216',load_project(self.path).document)
        self.change('redo','legacy-redo')
        self.assertEqual(self.rendered(),rendered)

    def test_malformed_recorded_stroke_is_rejected_without_writes(self):
        self.save(index=1)
        project=load_project(self.path)
        receipt={**project.operations[-1],'stroke':{
            **project.operations[-1]['stroke'],'object':True}}
        save_project(self.path,replace(project,operations=[*project.operations[:-1],receipt]),overwrite=True)
        before=self.files()
        with self.assertRaisesRegex(WorkspaceError,'INVALID_BRUSH_HISTORY'):
            self.change('undo','malformed')
        self.assertEqual(self.files(),before)

    def test_history_command_id_cannot_be_reused_as_a_new_brush_gesture(self):
        self.save();self.change('undo','shared-id')
        before=self.files()
        with self.assertRaisesRegex(WorkspaceError,'BRUSH_COMMAND_ID_REUSED'):
            self.save(command_id='shared-id')
        self.assertEqual(self.files(),before)

    def test_pending_recovery_refuses_history_change(self):
        self.save()
        self.path.with_name('brush-preview.pending-backup.smartsvg').write_bytes(self.path.read_bytes())
        before=self.files()
        with self.assertRaisesRegex(WorkspaceError,'PROJECT_NOT_HEALTHY'):
            self.change('undo','pending')
        self.assertEqual(self.files(),before)

    def test_altered_base_context_is_rejected_without_writes(self):
        self.save();project=load_project(self.path)
        for field in ('source_sha256','base_mask_sha256_float32','base_snapshot_sha256'):
            with self.subTest(field=field):
                receipt={**project.operations[-1],field:'f'*64}
                save_project(self.path,replace(project,operations=[*project.operations[:-1],receipt]),overwrite=True)
                before=self.files()
                with self.assertRaisesRegex(WorkspaceError,'BRUSH_HISTORY_SOURCE_CHANGED'):
                    self.change('undo','bad-context')
                self.assertEqual(self.files(),before)

    def test_concurrent_notes_change_wins_over_history_cas(self):
        self.save()
        from smartsvg_core import project_workspace_g22 as module
        original=module.save_with_recovery;fired=False
        revision=sha256(self.path.read_bytes()).hexdigest()
        def concurrent(path,project,**kwargs):
            nonlocal fired
            if not fired:
                fired=True
                self.workspace.update_notes('brush-preview',notes='concurrent',expected_sha256=revision)
            return original(path,project,**kwargs)
        with patch.object(module,'save_with_recovery',side_effect=concurrent):
            with self.assertRaisesRegex(WorkspaceError,'PROJECT_CHANGED_DURING_SAVE'):
                self.change('undo','concurrent-undo')
        project=load_project(self.path)
        self.assertEqual(project.document['notes'],'concurrent')
        self.assertEqual(len(project.document['editor_v216']['strokes']),1)


if __name__=='__main__':unittest.main()
