#!/usr/bin/env node
/** G3.3e-b2a browser-client contract checks (Node >=18).
 * Run: node --test tools/test_subject_brush_preview_client_g33e.mjs
 * Server-side CRC/dimension checks are covered in Python route tests.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {requestSubjectBrushPreview,brushPreviewMessage} from
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
  subject_id:SUBJECT,subject_ambiguous:false,
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
        source_sha256:fields.source_sha256,
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
test('invalid coordinates and NaN fail before CPU request',async()=>{
  const api=fakeApi();
  for(const points of [[[NaN,0.5]],[[1.01,0.5]],[],[[true,0.5]]]){
    await assert.rejects(requestSubjectBrushPreview(api,report(),mask,{points}),
      /INVALID_PREVIEW_STROKE/);
  }
  assert.equal(api.calls,0);
});
test('mismatched late result fails closed without displaying images',async()=>{
  const api=fakeApi(p=>({...p,subject_id:'subject-'+'0'.repeat(32)}));
  await assert.rejects(requestSubjectBrushPreview(api,report(),mask),
    /INVALID_PREVIEW_OUTPUT/);
});
test('timeout rejects a nonresponding preview and does not certify output',async()=>{
  const api={fetchApi:()=>new Promise(()=>{})};
  await assert.rejects(
    requestSubjectBrushPreview(api,report(),mask,{timeoutMs:10}),
    /PREVIEW_TIMEOUT/);
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
