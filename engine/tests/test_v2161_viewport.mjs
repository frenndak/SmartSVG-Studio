import test from 'node:test';
import assert from 'node:assert/strict';
import {fitView,constrainView,zoomView,moveView,viewToUV,VIEW_LIMITS,strokeSpacing} from '../web/js/smartsvg_editor_model_v216.mjs';
const approx=(a,b)=>assert.ok(Math.abs(a-b)<0.00001,`${a} != ${b}`);
test('fit scales wide landscape preview without losing any part of the image',()=>{
 const v=fitView(760,570,420,400);
 approx(v.scale,420/760);approx(v.x,0);
 assert.ok(v.y>0);assert.ok(v.y+570*v.scale<400);
});
test('fit scales tall sheets and centers horizontally',()=>{
 const v=fitView(400,760,800,300);
 approx(v.scale,300/760);approx(v.y,0);assert.ok(v.x>0);
});
test('zoom respects the exact cursor pivot in image space',()=>{
 const dims=[760,570,400,300],v=fitView(...dims);
 const px=110,py=145;
 const before=viewToUV(v,px,py,760,570);
 const next=zoomView(v,v.scale*2,px,py,...dims);
 const after=viewToUV(next,px,py,760,570);
 assert.deepEqual(before,after);
});
test('panning clamps without allowing sheets to disappear',()=>{
 const dims=[760,570,400,300],v=zoomView(fitView(...dims),3,200,150,...dims);
 const a=moveView(v,1e6,1e6,...dims);
 assert.equal(a.x,0);assert.equal(a.y,0);
 const b=moveView(v,-1e6,-1e6,...dims);
 approx(b.x,400-760*b.scale);approx(b.y,300-570*b.scale);
});
test('a sheet smaller than the frame stays centered, including after attempts to pan',()=>{
 const v=constrainView({scale:.5,x:999,y:-999},400,300,800,600);
 approx(v.x,300);approx(v.y,225);
 assert.deepEqual(moveView(v,1000,-1000,400,300,800,600),v);
});
test('normalized coordinates stable across zoom and valid for native replay',()=>{
 const v=zoomView(fitView(760,570,760,570),4,380,285,760,570,760,570);
 assert.deepEqual(viewToUV(v,380,285,760,570),[.5,.5]);
 assert.deepEqual(viewToUV(v,99999,99999,760,570),null);
 assert.deepEqual(viewToUV(v,99999,99999,760,570,true),[1,1]);
});
test('upper and lower limits are enforced and untrusted viewport values rejected',()=>{
 let v=zoomView({scale:1,x:0,y:0},1e9,0,0,760,570,760,570);
 assert.equal(v.scale,VIEW_LIMITS.maxScale);
 v=zoomView(v,.00001,0,0,760,570,760,570);
 assert.equal(v.scale,VIEW_LIMITS.minScale);
 assert.throws(()=>fitView(760,570,0,500),/Géométrie/);
 assert.throws(()=>constrainView({scale:1,x:NaN,y:0},760,570,400,300),/Géométrie/);
 assert.throws(()=>zoomView({scale:1,x:0,y:0},NaN,0,0,760,570,400,300),/Zoom/);
 assert.throws(()=>moveView({scale:1,x:0,y:0},Infinity,0,760,570,400,300),/Déplacement/);
});

test('magnified brush samples enough points for fine edge tracing',()=>{
 assert.equal(strokeSpacing(1),1.2);
 assert.ok(strokeSpacing(8)<.2);
 assert.ok(strokeSpacing(16)<.1);
 assert.throws(()=>strokeSpacing(0),/Grossissement/);
});
