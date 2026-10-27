import test from 'node:test';
import assert from 'node:assert/strict';
import {validatedFocus,centerFocusView} from '../web/js/smartsvg_mask_focus_v21156.mjs';
const sha='a'.repeat(64);
const meta={version:1,source:sha,width:200,height:100,count:4};
const good={version:1,source_sha256:sha,width_px:200,height_px:100,subject:2,bbox_source_px:[40,10,60,30]};
test('accepts only exact, bounded source and mask fingerprint',()=>{
 assert.equal(validatedFocus(good,meta).subject,2);
 assert.deepEqual([...validatedFocus(good,meta).box],[40,10,60,30]);
 for (const fragment of [{source_sha256:'b'.repeat(64)}, {subject:5},{subject:0},
   {width_px:300},{height_px:101},{bbox_source_px:[1,2,300,5]},
   {bbox_source_px:[1,2,1,5]}, {bbox_source_px:[1,2,NaN,5]},
   {bbox_source_px:'javascript:alert(1)'},{version:2}]) {
   assert.equal(validatedFocus({...good,...fragment},meta),null,JSON.stringify(fragment));
 }
});
test('centers source rect at expected magnification without editing mask',()=>{
 const view=centerFocusView(good.bbox_source_px,200,100,400,200,800,400);
 assert.equal(view.scale,5);
 assert.equal(view.x,400-100*5);
 assert.equal(view.y,200-40*5);
});
test('invalid zoom geometry fails closed',()=>{
 for(const b of [[20,30,10,40],null, [0,0,0,0]])assert.throws(()=>centerFocusView(b,200,100,400,200,800,400));
});
