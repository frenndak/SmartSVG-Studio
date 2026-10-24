import test from 'node:test';
import assert from 'node:assert/strict';
import {validateMeta,nativeUrl,fitView,clampView,nativeZoom,sourceAt,centerOn} from '../web/js/smartsvg_native_model_v219.mjs';
const token='e'.repeat(24);
const ref=tail=>({filename:`ni_${token}_${tail}.png`,subfolder:'SmartSVG_Studio_Native_V219',type:'output'});
const meta={version:1,width:4500,height:1100,count:2,image:ref('image'),masks:[ref('mask00'),ref('mask01')],
 objects:[{objet:1,alertes:['MICRO_ILOTS'],points:[{type:'ILOT_DETACHE',x:112,y:34,priorite:1,detail:'À vérifier'}]},
          {objet:2,alertes:[],points:[]}]};
test('full native 4500x1100 metadata accepted, with prefixed reverse proxy route',()=>{
 assert.deepEqual(validateMeta({smartsvg_native:[meta]}),meta);
 const url=nativeUrl(meta.image,'https://example.net/proxy/8188/','/proxy/8188/view');
 assert.ok(url.startsWith('https://example.net/proxy/8188/view?'));
 assert.match(url,/SmartSVG_Studio_Native_V219/);
});
test('reject forged paths, swapped sessions and wrong dimensions',()=>{
 assert.equal(validateMeta({smartsvg_native:[{...meta,width:5000001}]}),null);
 assert.equal(validateMeta({smartsvg_native:[{...meta,masks:[ref('mask01'),ref('mask00')]}]}),null);
 assert.equal(validateMeta({smartsvg_native:[{...meta,masks:[ref('mask00'), {...ref('mask01'),filename:'ni_'+('f'.repeat(24))+'_mask01.png'}]}]}),null);
 assert.equal(validateMeta({smartsvg_native:[{...meta,objects:[{...meta.objects[0],points:[{type:'X',x:4500,y:12,detail:'oops'}]},meta.objects[1]]}]}),null);
 assert.equal(nativeUrl({...ref('image'),filename:'../../secret.png'},'https://a/','/view'),null);
});
test('1:1 pixels, zoom anchored to cursor and source coordinates invariant',()=>{
 const v=fitView(4500,1100,900,600);
 assert.ok(v.scale<1);
 const center=[450,300];const sourceBefore=sourceAt(v,...center,4500,1100);
 const n=nativeZoom(v,1,...center,4500,1100,900,600);
 assert.equal(n.scale,1);
 const sourceAfter=sourceAt(n,...center,4500,1100);
 assert.deepEqual(sourceAfter,sourceBefore);
 assert.equal(sourceAt(n,n.x-1,n.y-1,4500,1100),null);
});
test('focusing on native anomaly navigates to actual source pixel',()=>{
 let v=fitView(4500,1100,900,600);
 v=nativeZoom(v,2,450,300,4500,1100,900,600);
 v=centerOn(v,512,334,4500,1100,900,600);
 assert.deepEqual(sourceAt(v,450,300,4500,1100),[512,334]);
});
test('pan is bounded; no serialization changes to masks',()=>{
 let v=fitView(4500,1100,900,600);
 v=clampView({...v,x:100000,y:-100000},4500,1100,900,600);
 assert.ok(v.x<=0);
 assert.ok(v.y>=0);
 assert.throws(()=>centerOn(v,-10,12,4500,1100,900,600));
});
