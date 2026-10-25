import test from 'node:test';
import assert from 'node:assert/strict';
import {RESUME_STATES, resumeEmpty, resumeLoading, resumeError,
        resumeFromProject} from '../web/js/smartsvg_resume_state_g25.mjs';

const A='a'.repeat(64), B='b'.repeat(64), C='c'.repeat(64);
function base(overrides={}){
  return {name:'escargots',status:'PROJECT_HEALTHY',recoverable:false,
    sha256:A,source_count:1,
    document:{profile:'Planche - 12 images (4x3)',stage:'source_imported_only'},
    ...overrides};
}
function exactMasks(){
  return {exact_float32:true,count:12,dimensions_px:[1500,1000],
    editor_fingerprint:B,source_fingerprint:C,physical_cut_verified:false};
}
function brush(){
  return {available:true,count:12,stroke_count:14,source_fingerprint:B,
    base_masks_persisted:false};
}
test('empty, loading and error are separate nonproduction states',()=>{
  assert.equal(resumeEmpty().state,RESUME_STATES.EMPTY);
  assert.equal(resumeLoading().state,RESUME_STATES.LOADING);
  assert.equal(resumeError().state,RESUME_STATES.ERROR);
  for(const view of [resumeEmpty(),resumeLoading(),resumeError()]){
    assert.equal(view.machineReady,false);
    assert.equal(view.cutVerified,false);
    assert.equal(view.graphRestored,false);
    assert.equal(view.steps.length,4);
  }
});
test('source-only archive has precise remaining steps, no false masking claims',()=>{
  const view=resumeFromProject(base());
  assert.equal(view.state,RESUME_STATES.SOURCE_ONLY);
  assert.equal(view.steps[0].status,'saved');
  assert.equal(view.steps[1].status,'needed');
  assert.equal(view.steps[2].status,'needed');
  assert.equal(view.steps[3].status,'manual');
  assert.equal(view.revision,A);
  assert.equal(view.mayOpenSource,true);
});
test('masks without strokes never imply edits were restored',()=>{
  const view=resumeFromProject(base({base_masks:exactMasks()}));
  assert.equal(view.state,RESUME_STATES.MASKS_ONLY);
  assert.equal(view.steps[1].status,'saved');
  assert.equal(view.steps[2].status,'needed');
  assert.equal(view.cutVerified,false);
});
test('strokes without masks require original bases, not a thumbnail',()=>{
  const view=resumeFromProject(base({editor_session:brush()}));
  assert.equal(view.state,RESUME_STATES.STROKES_ONLY);
  assert.match(view.action,/masques de base identiques/);
  assert.equal(view.steps[1].status,'needed');
  assert.equal(view.steps[2].status,'saved');
});
test('matching exact masks and native V216 strokes still require manual graph',()=>{
  const view=resumeFromProject(base({base_masks:exactMasks(),editor_session:brush()}));
  assert.equal(view.state,RESUME_STATES.COMPLETE_MANUAL);
  assert.deepEqual(view.steps.map(s=>s.status),['saved','saved','saved','manual']);
  assert.match(view.action,/G2.4/);
  assert.equal(view.machineReady,false);
  assert.equal(view.graphRestored,false);
  assert.equal(view.cutVerified,false);
});
test('incompatible fingerprints, subject counts and malformed data fail closed',()=>{
  const scenarios=[
    {base_masks:{...exactMasks(),count:24},editor_session:brush()},
    {base_masks:exactMasks(),editor_session:{...brush(),source_fingerprint:'d'.repeat(64)}},
    {base_masks:exactMasks(),editor_session:{...brush(),stroke_count:500}},
    {base_masks:{exact_float32:true,count:12,dimensions_px:[0,100]},editor_session:brush()},
    {base_masks:{...exactMasks(),exact_float32:false},editor_session:brush()},
  ];
  for(const scenario of scenarios){
    const view=resumeFromProject(base(scenario));
    assert.equal(view.state,RESUME_STATES.INCOMPATIBLE);
    assert.equal(view.mayOpenSource,true);
    assert.equal(view.steps[1].status,'needed');
    assert.equal(view.graphRestored,false);
  }
});
test('recovery only offered with a verified hash and confirmed health flag',()=>{
  const good=resumeFromProject({status:'PROJECT_RECOVERABLE',
    recoverable:true,recovery_sha256:C});
  assert.equal(good.state,RESUME_STATES.RECOVERABLE);
  assert.equal(good.mayRestore,true);
  for(const scenario of [{status:'PROJECT_RECOVERABLE'},
    {status:'PROJECT_RECOVERABLE',recoverable:true,recovery_sha256:'bad'},
    {status:'PROJECT_RECOVERABLE',recoverable:false,recovery_sha256:C}]){
    const view=resumeFromProject(scenario);
    assert.equal(view.state,RESUME_STATES.UNAVAILABLE);
    assert.equal(view.mayRestore,false);
  }
});
test('unknown archive health and malformed summaries never become ready',()=>{
  const scenarios=[null,[],{}, {status:'PROJECT_HEALTHY',sha256:A},
    base({sha256:'invalid'}),base({source_count:0}),base({document:[]}),
    {status:'PROJECT_BROKEN',recoverable:true,recovery_sha256:C}];
  for(const report of scenarios){
    const view=resumeFromProject(report);
    assert.ok([RESUME_STATES.UNKNOWN,RESUME_STATES.UNAVAILABLE].includes(view.state));
    assert.equal(view.mayOpenSource,false);
    assert.equal(view.machineReady,false);
  }
});
test('state model never offers automatic workflow or physical cut',()=>{
  const outputs=[resumeEmpty(),resumeLoading(),resumeError(),
    resumeFromProject(base()),resumeFromProject(base({base_masks:exactMasks(),editor_session:brush()})),
    resumeFromProject({status:'PROJECT_RECOVERABLE',recoverable:true,recovery_sha256:C})];
  for(const output of outputs){
    assert.notEqual(output.state,'READY_FOR_CRICUT');
    assert.equal(output.cutVerified,false);
    assert.equal(output.graphRestored,false);
    assert.equal(output.machineReady,false);
  }
});
