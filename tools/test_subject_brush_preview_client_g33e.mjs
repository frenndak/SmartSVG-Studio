#!/usr/bin/env node
/** G3.3e-b2a browser-client contract checks (Node >=18).
 * Run: node --test tools/test_subject_brush_preview_client_g33e.mjs
 * Server-side CRC/dimension checks are covered in Python route tests.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {webcrypto} from 'node:crypto';
if(!globalThis.crypto)globalThis.crypto=webcrypto;
import {requestSubjectBrushPreview,brushPreviewMessage,saveSubjectBrushPreview} from
  '../engine/web/js/smartsvg_subject_brush_preview_g33e.mjs';

const SHA='a'.repeat(64);
const MASK_SHA='e'.repeat(64);
const SOURCE_SHA='f'.repeat(64);
const SUBJECT='subject-'+'d'.repeat(32);
// This fake response is intentionally only a transport contract fixture.
// Real PNG decoding and CRC are validated by the server, not this test.
const PNG64='iVBORw0KGgo'+'A'.repeat(80);
const mask=Object.freeze({
  mask_index:0,mask_id:'base-mask-00',mask_sha256_float32:MASK_SHA,
  subject_id:SUBJECT,subject_ambiguous:false,has_foreground:true,
  subject_proof_status:'verified',
});
function report(){
  return {
    project_name:'subject-project',project_sha256:SHA,source_sha256:SOURCE_SHA,
    width_px:16,height_px:12,expires_at_ms:Date.now()+60_000,
    mask_catalog:{
      project_name:'subject-project',project_sha256:SHA,
      source_sha256:SOURCE_SHA,source_id:'source-original',items:[mask],
    },
  };
}
function fakeApi(mutate){
  let calls=0,fields;
  return {
    get calls(){return calls;},
    get fields(){return fields;},
    async fetchApi(url,options){
      calls++;
      assert.equal(url,'/smartsvg/g22/subject/preview');
      assert.equal(options.method,'POST');
      assert.equal(options.headers['X-SmartSVG-UI'],'1');
      fields=Object.fromEntries(options.body.entries());
      const result={
        command_id:fields.command_id,name:fields.name,
        project_sha256:fields.expected_sha256,
        subject_id:fields.subject_id,mask_id:fields.mask_id,
        base_mask_sha256_float32:fields.mask_sha256_float32,
        source_sha256:fields.source_sha256,
        preview_mask_sha256_float32:'b'.repeat(64),
        dimensions_px:[16,12],changed_pixels:3,
        before_png_base64:PNG64,after_png_base64:PNG64,
        persisted:false,cricut_certified:false,
      };
      return {ok:true,async json(){
        return {ok:true,certified:false,preview:mutate?mutate(result):result};
      }};
    },
  };
}
test('Atelier offers a brush preview only for an explicitly verified Subject',()=>{
  // Execute the actual HTML eligibility predicate, not a duplicated policy.
  // Before this regression, a legacy subject without proof still displayed
  // an enabled preview control although the request client rejects it.
  const html=readFileSync(
    new URL('../engine/web/js/smartsvg_express_atelier_preview.html',import.meta.url),'utf8');
  const marker='    if(!reportAtPaint.identityActionStale&&linkedIdentity&&';
  const start=html.indexOf(marker);
  const end=html.indexOf('){\n      const previewBox',start);
  assert.ok(start>=0&&end>start,'actual Atelier preview gate exists');
  const predicate=html.slice(start+7,end);
  const visible=new Function('reportAtPaint','linkedIdentity',
    'return Boolean('+predicate+');');
  const reportAtPaint={identityActionStale:false,expires_at_ms:Date.now()+60000};
  const base={has_foreground:true,subject_ambiguous:false,
    subject_id:'subject-'+'a'.repeat(32)};
  assert.equal(visible(reportAtPaint,{...base,subject_proof_status:'verified'}),true);
  assert.equal(visible(reportAtPaint,base),false,'missing proof must not offer a dead-end button');
  assert.equal(visible(reportAtPaint,{...base,subject_proof_status:'unbound'}),false);
  assert.equal(visible(reportAtPaint,{...base,subject_proof_status:'ambiguous'}),false);
  assert.equal(visible({...reportAtPaint,identityActionStale:true},
    {...base,subject_proof_status:'verified'}),false);
  assert.equal(visible({...reportAtPaint,expires_at_ms:Date.now()-1},
    {...base,subject_proof_status:'verified'}),false);
});

test('Atelier cleanup never re-enables a preview after Subject proof expiry',()=>{
  // Evaluate the actual ready() function: before this regression, an
  // asynchronous completion re-enabled "Calculer l’aperçu" even after
  // the diagnostic expired (or had no valid expiry timestamp).
  const html=readFileSync(
    new URL('../engine/web/js/smartsvg_express_atelier_preview.html',import.meta.url),'utf8');
  const start=html.indexOf('      const ready=()=>{',
    html.indexOf('let pending=false,abort=null,serial=0;'));
  const end=html.indexOf('      const discardPreview=()=>{',start);
  assert.ok(start>=0&&end>start,'actual Atelier cleanup function exists');
  const actual=html.slice(start,end);
  const run=(expires_at_ms,{stale=false,different=false}={})=>{
    const reportAtPaint={identityActionStale:stale,expires_at_ms};
    const state={
      pending:true,abort:{},calculate:{disabled:true},
      cancel:{disabled:false},before:{hidden:true},after:{hidden:true},
      modeInput:{disabled:true},xInput:{disabled:true},yInput:{disabled:true},
      saveButton:{disabled:true},saving:false,acceptedPreview:null,
      reportAtPaint,realSubjectsData:different?{}:reportAtPaint,
    };
    return new Function(...Object.keys(state),actual+
      'ready();return {disabled:calculate.disabled,cancelled:cancel.disabled};')(
        ...Object.values(state));
  };
  assert.equal(run(Date.now()+60000).disabled,false,'valid proof permits retry');
  assert.equal(run(Date.now()-1000).disabled,true,'expired proof stays disabled');
  assert.equal(run(undefined).disabled,true,'missing expiry stays disabled');
  assert.equal(run(NaN).disabled,true,'invalid expiry stays disabled');
  assert.equal(run(Date.now()+60000,{stale:true}).disabled,true);
  assert.equal(run(Date.now()+60000,{different:true}).disabled,true);
  assert.equal(run(Date.now()-1000).cancelled,true,
    'cleanup also disables cancellation when there is no visible preview');
});

test('valid single-stroke request pins identity and only returns PNGs',async()=>{
  const api=fakeApi();
  const result=await requestSubjectBrushPreview(api,report(),mask);
  assert.equal(api.calls,1);
  assert.equal(Object.keys(api.fields).length,12);
  assert.equal(api.fields.preview_version,'1');
  assert.equal(api.fields.mask_sha256_float32,MASK_SHA);
  assert.equal(api.fields.subject_id,SUBJECT);
  assert.equal(api.fields.points,'[[0.5,0.5]]');
  assert.match(api.fields.command_id,/^[a-f0-9]{32}$/);
  assert.equal(result.persisted,false);
  assert.equal(result.cricutCertified,false);
  assert.equal(result.changedPixels,3);
  assert.match(result.beforeSrc,/^data:image\/png;base64,/);
  assert.equal(result.preview_float32,undefined);
});
test('stale report and unverified subject never call the server',async()=>{
  const api=fakeApi();
  await assert.rejects(
    requestSubjectBrushPreview(api,{...report(),project_sha256:'0'.repeat(64)},mask),
    /PREVIEW_SELECTION_STALE/);
  await assert.rejects(
    requestSubjectBrushPreview(api,report(),{...mask,subject_id:null}),
    /PREVIEW_SELECTION_STALE/);
  assert.equal(api.calls,0);
});
test('invalid proof or empty mask is rejected before any CPU request',async()=>{
  const api=fakeApi();
  for(const changes of [
    {subject_proof_status:'mismatch'},
    {subject_proof_status:'missing'},
    {subject_proof_status:undefined},
    {has_foreground:false},
    {subject_ambiguous:true},
  ]){
    const invalid={...mask,...changes};
    const current=report();
    current.mask_catalog.items=[invalid];
    await assert.rejects(requestSubjectBrushPreview(api,current,invalid),
      /PREVIEW_SELECTION_STALE/);
  }
  assert.equal(api.calls,0);
});
test('selected mask proof diverges from verified catalog: no CPU request',async()=>{
  // A caller may hold a changed selection while the catalog remains valid.
  // Validate both snapshots, not only the catalog entry.
  const api=fakeApi();
  for(const changes of [{has_foreground:false},{subject_ambiguous:true},
                        {subject_proof_status:undefined},
                        {subject_proof_status:'unbound'}]){
    await assert.rejects(
      requestSubjectBrushPreview(api,report(),{...mask,...changes}),
      /PREVIEW_SELECTION_STALE/);
  }
  assert.equal(api.calls,0);
});
test('invalid coordinates and NaN fail before CPU request',async()=>{
  const api=fakeApi();
  for(const points of [[[NaN,0.5]],[[1.01,0.5]],[],[[true,0.5]]]){
    await assert.rejects(requestSubjectBrushPreview(api,report(),mask,{points}),
      /INVALID_PREVIEW_STROKE/);
  }
  assert.equal(api.calls,0);
});
test('wrong float32 mask digest is rejected before preview display',async()=>{
  const api=fakeApi(p=>({...p,base_mask_sha256_float32:'0'.repeat(64)}));
  await assert.rejects(requestSubjectBrushPreview(api,report(),mask),
    /INVALID_PREVIEW_OUTPUT/);
});
test('mismatched late result fails closed without displaying images',async()=>{
  const api=fakeApi(p=>({...p,subject_id:'subject-'+'0'.repeat(32)}));
  await assert.rejects(requestSubjectBrushPreview(api,report(),mask),
    /INVALID_PREVIEW_OUTPUT/);
});
test('late response after proof expiry is rejected before PNG delivery',async()=>{
  const current=report();
  const api=fakeApi(p=>{
    current.expires_at_ms=Date.now()-1;
    return p;
  });
  await assert.rejects(requestSubjectBrushPreview(api,current,mask),
    /PREVIEW_SELECTION_STALE/);
  assert.equal(api.calls,1);
  assert.match(brushPreviewMessage('PREVIEW_SELECTION_STALE'),/modifié/);
});
test('late response after subject proof changes is rejected',async()=>{
  const current=report();
  const api=fakeApi(p=>{
    current.mask_catalog.items=[{
      ...mask,mask_sha256_float32:'0'.repeat(64),
    }];
    return p;
  });
  await assert.rejects(requestSubjectBrushPreview(api,current,mask),
    /PREVIEW_SELECTION_STALE/);
  assert.equal(api.calls,1);
});
test('timeout rejects a nonresponding preview and does not certify output',async()=>{
  const api={fetchApi:()=>new Promise(()=>{})};
  await assert.rejects(
    requestSubjectBrushPreview(api,report(),mask,{timeoutMs:10}),
    /PREVIEW_TIMEOUT/);
});
test('timeout remains PREVIEW_TIMEOUT when fetch rejects on abort',async()=>{
  let aborted=false;
  const api={fetchApi:(_url,{signal})=>new Promise((_resolve,reject)=>{
    signal.addEventListener('abort',()=>{
      aborted=true;
      reject(Error('AbortError'));
    },{once:true});
  })};
  await assert.rejects(
    requestSubjectBrushPreview(api,report(),mask,{timeoutMs:10}),
    /PREVIEW_TIMEOUT/);
  assert.equal(aborted,true,'timeout cancels the underlying HTTP request');
  assert.match(brushPreviewMessage('PREVIEW_TIMEOUT'),/trop long/);
});

test('explicit cancellation discards the late HTTP response',async()=>{
  const controller=new AbortController();
  const api={fetchApi:()=>new Promise(()=>{})};
  const request=requestSubjectBrushPreview(api,report(),mask,{
    signal:controller.signal,timeoutMs:1000,
  });
  controller.abort();
  await assert.rejects(request,/PREVIEW_ABORTED/);
  assert.match(brushPreviewMessage('PREVIEW_ABORTED'),/annulé/);
});


test('Atelier recovers visibly when the preview module cannot load',async()=>{
  // Exercise the actual event handler with a deliberately unavailable module.
  // Previously catch() repeated the failed import, leaving "Calcul CPU en
  // cours" on screen and rejecting the click handler a second time.
  const html=readFileSync(
    new URL('../engine/web/js/smartsvg_express_atelier_preview.html',import.meta.url),'utf8');
  const start=html.indexOf('      let pending=false,abort=null,serial=0;');
  const end=html.indexOf('      previewBox.appendChild(calculate);',start);
  assert.ok(start>=0&&end>start);
  const actual=html.slice(start,end);
  assert.ok(actual.includes('await import("./smartsvg_subject_brush_preview_g33e.mjs")'),
    'preview module import must be exercised');
  const failing=actual.replaceAll(
    './smartsvg_subject_brush_preview_g33e.mjs',
    './__smartsvg_intentionally_missing_preview_module__.mjs');
  const el=()=>({
    hidden:true,disabled:false,src:'',textContent:'',events:{},
    addEventListener(event,handler){(this.events[event]??=[]).push(handler);},
    removeAttribute(key){delete this[key];},
  });
  const ctx={
    modeInput:el(),xInput:el(),yInput:el(),calculate:el(),cancel:el(),saveButton:el(),
    before:el(),after:el(),previewStatus:el(),button:el(),
    reportAtPaint:{identityActionStale:false,expires_at_ms:Date.now()+60000},
    chosenRealSubjects:new Set([1]),item:{numero:1},linkedIdentity:{},
  };
  ctx.realSubjectsData=ctx.reportAtPaint;
  ctx.modeInput.value='add';ctx.xInput.value='50';ctx.yInput.value='50';
  const names=Object.keys(ctx);
  new Function(...names,failing)(...names.map(name=>ctx[name]));
  assert.equal(ctx.calculate.events.click.length,1);
  await ctx.calculate.events.click[0]();
  assert.match(ctx.previewStatus.textContent,/Module de prévisualisation indisponible/);
  assert.match(ctx.previewStatus.textContent,/Aucun changement enregistré/);
  assert.equal(ctx.calculate.disabled,false,'retry is possible after import failure');
  assert.equal(ctx.cancel.disabled,true);
});

test('Atelier preview dismissal and gesture changes never leave stale PNGs visible',()=>{
  // Execute the real UI event-handler block without a browser dependency.
  // A success preview must be dismissible; changing a gesture or subject
  // invalidates displayed images and aborts an in-flight preview.
  const html=readFileSync(
    new URL('../engine/web/js/smartsvg_express_atelier_preview.html',import.meta.url),'utf8');
  const start=html.indexOf('      let pending=false,abort=null,serial=0;');
  const end=html.indexOf('      previewBox.appendChild(calculate);',start);
  assert.ok(start>=0&&end>start,'Atelier preview event handlers found');
  const el=()=>({
    hidden:true,disabled:false,src:'',textContent:'',events:{},
    addEventListener(event,handler){(this.events[event]??=[]).push(handler);},
    removeAttribute(key){delete this[key];},
    fire(event){for(const handler of this.events[event]||[])handler();},
  });
  const ctx={
    modeInput:el(),xInput:el(),yInput:el(),calculate:el(),cancel:el(),saveButton:el(),
    before:el(),after:el(),previewStatus:el(),button:el(),
    reportAtPaint:{identityActionStale:false,expires_at_ms:Date.now()+60000},
    chosenRealSubjects:new Set([1]),item:{numero:1},linkedIdentity:{},
  };
  ctx.realSubjectsData=ctx.reportAtPaint;
  const names=Object.keys(ctx);
  const bind=new Function(...names,html.slice(start,end)+
    '\nreturn {ready,setPending(v){pending=v},setAbort(v){abort=v},getSerial(){return serial}};');
  const ui=bind(...names.map(name=>ctx[name]));
  ctx.before.hidden=false;ctx.after.hidden=false;
  ctx.before.src='data:image/png;base64,old';ctx.after.src='data:image/png;base64,old';
  ui.ready();
  assert.equal(ctx.cancel.disabled,false,'successful preview remains dismissible');
  ctx.modeInput.fire('input');
  assert.equal(ctx.before.hidden,true);
  assert.equal(ctx.after.hidden,true);
  assert.equal(ctx.before.src,undefined);
  assert.equal(ctx.cancel.disabled,true);
  assert.match(ctx.previewStatus.textContent,/Geste modifié/);
  ctx.before.hidden=false;ctx.after.hidden=false;ui.ready();
  ctx.cancel.fire('click');
  assert.equal(ctx.before.hidden,true);
  assert.equal(ctx.cancel.disabled,true);
  ctx.before.hidden=false;ctx.after.hidden=false;ui.ready();
  ctx.xInput.fire('change');
  assert.equal(ctx.after.hidden,true,'coordinate changes invalidate previews');
  let aborted=false;
  ui.setPending(true);ui.setAbort({abort(){aborted=true;}});
  const previousSerial=ui.getSerial();
  ctx.button.fire('click');
  assert.equal(aborted,true,'selection change aborts pending request');
  assert.equal(ui.getSerial(),previousSerial+1,'late result is invalidated');
  assert.equal(ctx.cancel.disabled,true);
});

function saveApi(saveImplementation){
  const preview=fakeApi();let writes=0,fields;
  return {
    get writes(){return writes;},get fields(){return fields;},
    async fetchApi(url,options){
      if(url.endsWith('/preview'))return preview.fetchApi(url,options);
      assert.equal(url,'/smartsvg/g22/subject/save');
      assert.equal(options.headers['X-SmartSVG-UI'],'1');
      writes++;fields=Object.fromEntries(options.body.entries());
      if(saveImplementation)return saveImplementation(fields,options);
      return {ok:true,async json(){return {ok:true,certified:false,result:{
        name:fields.name,command_id:fields.command_id,sha256:'c'.repeat(64),
        status:'subject_brush_saved',persisted:true,cricut_certified:false,
      }}}};
    },
  };
}
test('saving requires a confirmed server preview and sends its exact digest',async()=>{
  const api=saveApi(),current=report();
  const preview=await requestSubjectBrushPreview(api,current,mask);
  await assert.rejects(saveSubjectBrushPreview(api,current,mask,preview),/BRUSH_SAVE_CONFIRMATION_REQUIRED/);
  assert.equal(api.writes,0);
  const result=await saveSubjectBrushPreview(api,current,mask,preview,{confirmed:true});
  assert.equal(api.fields.expected_preview_mask_sha256_float32,'b'.repeat(64));
  assert.equal(api.fields.command_id,preview.commandId);
  assert.equal(api.fields.confirmed,'yes');
  assert.equal(result.persisted,true);assert.equal(result.cricutCertified,false);
  const repeat=await saveSubjectBrushPreview(api,current,mask,preview,{confirmed:true});
  assert.deepEqual(repeat,result);assert.equal(api.writes,1);
});
test('cloned preview or stale proof cannot trigger a save',async()=>{
  const api=saveApi(),current=report();
  const preview=await requestSubjectBrushPreview(api,current,mask);
  await assert.rejects(saveSubjectBrushPreview(api,current,mask,{...preview},{confirmed:true}),/INVALID_BRUSH_SAVE_PREVIEW/);
  current.identityActionStale=true;
  await assert.rejects(saveSubjectBrushPreview(api,current,mask,preview,{confirmed:true}),/PREVIEW_SELECTION_STALE/);
  assert.equal(api.writes,0);
});
test('double-click while saving sends only one write',async()=>{
  let finish;
  const api=saveApi(()=>new Promise(resolve=>{finish=resolve;})),current=report();
  const preview=await requestSubjectBrushPreview(api,current,mask);
  const saving=saveSubjectBrushPreview(api,current,mask,preview,{confirmed:true});
  await assert.rejects(saveSubjectBrushPreview(api,current,mask,preview,{confirmed:true}),/SAVE_BUSY/);
  finish({ok:true,async json(){return {ok:true,certified:false,result:{
    name:current.project_name,command_id:preview.commandId,sha256:'c'.repeat(64),
    status:'subject_brush_saved',persisted:true,cricut_certified:false,
  }}}});
  await saving;assert.equal(api.writes,1);
});
test('save timeout stays unknown and never silently retries',async()=>{
  const api=saveApi(()=>new Promise(()=>{})),current=report();
  const preview=await requestSubjectBrushPreview(api,current,mask);
  await assert.rejects(saveSubjectBrushPreview(api,current,mask,preview,{confirmed:true,timeoutMs:10}),/SAVE_OUTCOME_UNKNOWN/);
  await assert.rejects(saveSubjectBrushPreview(api,current,mask,preview,{confirmed:true}),/SAVE_OUTCOME_UNKNOWN/);
  assert.equal(api.writes,1);
});
test('malformed acknowledgement cannot claim nothing was written',async()=>{
  const api=saveApi(()=>({ok:true,async json(){return {ok:true,result:{persisted:false}};}})),current=report();
  const preview=await requestSubjectBrushPreview(api,current,mask);
  await assert.rejects(saveSubjectBrushPreview(api,current,mask,preview,{confirmed:true}),/SAVE_OUTCOME_UNKNOWN/);
  assert.equal(api.writes,1);
});

test('Atelier save acknowledgement or uncertainty invalidates the old diagnostic and blocks duplicate clicks',async()=>{
  const html=readFileSync(new URL('../engine/web/js/smartsvg_express_atelier_preview.html',import.meta.url),'utf8');
  const start=html.indexOf('      let pending=false,abort=null,serial=0;');
  const end=html.indexOf('      previewBox.appendChild(calculate);',start);
  const actual=html.slice(start,end)
    .replaceAll('await import("./smartsvg_subject_brush_preview_g33e.mjs")','await Promise.resolve(previewModule)')
    .replaceAll('await import("../../scripts/api.js")','await Promise.resolve({api:{}})');
  for(const failed of [false,true]){
    const el=()=>({hidden:false,disabled:false,src:'old',textContent:'',events:{},
      addEventListener(event,handler){(this.events[event]??=[]).push(handler);},
      removeAttribute(key){delete this[key];}});
    let finish,writes=0;
    const current={identityActionStale:false,expires_at_ms:Date.now()+60000};
    const ctx={modeInput:el(),xInput:el(),yInput:el(),calculate:el(),cancel:el(),saveButton:el(),
      before:el(),after:el(),previewStatus:el(),button:el(),reportAtPaint:current,realSubjectsData:current,
      chosenRealSubjects:new Set([1]),item:{numero:1},linkedIdentity:{},
      previewModule:{saveSubjectBrushPreview(_api,_report,_mask,_preview,options){
        writes++;assert.equal(options.confirmed,true);
        return new Promise((resolve,reject)=>{finish=()=>failed?reject(Error('SAVE_OUTCOME_UNKNOWN')):resolve({persisted:true});});
      },brushSaveMessage(){return 'Résultat incertain : vérifier le projet.';}}};
    const bind=new Function(...Object.keys(ctx),actual+';return {setPreview(p){acceptedPreview=p},ready};');
    const ui=bind(...Object.values(ctx));ui.setPreview({canSave:true});ui.ready();
    assert.equal(ctx.saveButton.disabled,false);
    const first=ctx.saveButton.events.click[0]();
    await Promise.resolve();await Promise.resolve();
    await ctx.saveButton.events.click[0]();assert.equal(writes,1);
    finish();await first;
    assert.equal(current.identityActionStale,true);
    assert.equal(ctx.saveButton.disabled,true);assert.equal(ctx.calculate.disabled,true);
    assert.equal(ctx.before.hidden,true);assert.equal(ctx.after.hidden,true);
    assert.match(ctx.previewStatus.textContent,failed?/incertain/:/enregistré/);
  }
});
