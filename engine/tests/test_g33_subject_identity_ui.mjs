import test from 'node:test';
import assert from 'node:assert/strict';
import {registerPersistentSubject} from '../web/js/smartsvg_subject_identity_g33e.mjs';

const sha=n=>String(n).repeat(64);
function report(){
 return {
  project_name:'subjects',project_sha256:sha('a'),source_sha256:sha('b'),
  width_px:4,height_px:3,count:2,expires_at_ms:Date.now()+60_000,
  mask_catalog:{
   version:1,project_name:'subjects',project_sha256:sha('a'),
   source_sha256:sha('b'),source_id:'source-original',width_px:4,height_px:3,count:2,
   items:[
    {mask_index:0,mask_id:'base-mask-00',mask_sha256_float32:sha('c'),
     has_foreground:true,subject_id:null,accessory_ids:[],subject_ambiguous:false},
    {mask_index:1,mask_id:'base-mask-01',mask_sha256_float32:sha('d'),
     has_foreground:true,subject_id:null,accessory_ids:[],subject_ambiguous:false},
   ],
  },
 };
}
class FormData {
 constructor(){this.rows=[];}
 append(key,value){this.rows.push([key,value]);}
}
globalThis.FormData=FormData;

test('explicit registration posts only pinned metadata and returns durable identity',async()=>{
 const calls=[];
 const api={fetchApi:async(route,options)=>{
  calls.push({route,options});
  return {ok:true,json:async()=>({ok:true,result:{
   name:'subjects',status:'subject_identity_created',
   subject_id:'subject-'+ 'e'.repeat(32),mask_id:'base-mask-00',
   bbox_px:[1,0,3,2],sha256:sha('f'),previous_available:true,certified:false,
  }})};
 }};
 const value=report(),mask=value.mask_catalog.items[0];
 const result=await registerPersistentSubject(api,value,mask,{confirmed:true,timeoutMs:1000});
 assert.equal(result.subject_id,'subject-'+ 'e'.repeat(32));
 assert.equal(result.sha256,sha('f'));
 assert.equal(calls.length,1);
 assert.equal(calls[0].route,'/smartsvg/g22/subject/identity');
 assert.equal(calls[0].options.method,'POST');
 assert.equal(calls[0].options.headers['X-SmartSVG-UI'],'1');
 const fields=Object.fromEntries(calls[0].options.body.rows);
 assert.deepEqual(fields,{
  name:'subjects',expected_sha256:sha('a'),source_id:'source-original',
  source_sha256:sha('b'),mask_index:'0',mask_id:'base-mask-00',
  mask_sha256_float32:sha('c'),expires_at_ms:String(value.expires_at_ms),
  confirmed:'yes',
 });
 assert.equal('raw_float32' in fields,false);
});

test('invalid, expired, already identified or unconfirmed reports never write',async()=>{
 let calls=0;
 const api={fetchApi:async()=>{calls++;throw Error('unexpected');}};
 const base=report(),mask=base.mask_catalog.items[0];
 for(const [value,item,options] of [
  [base,mask,{confirmed:false}],
  [{...base,expires_at_ms:Date.now()-1},mask,{confirmed:true}],
  [{...base,project_sha256:sha('9')},mask,{confirmed:true}],
  [base,{...mask,mask_sha256_float32:sha('9')},{confirmed:true}],
  [base,{...mask,subject_id:'subject-'+ '1'.repeat(32)},{confirmed:true}],
 ]){
  await assert.rejects(registerPersistentSubject(api,value,item,options));
 }
 assert.equal(calls,0);
});

test('hung request times out and external cancellation wins over late response',async()=>{
 let signal;
 const api={fetchApi:(_route,options)=>{
  signal=options.signal;return new Promise(()=>{});
 }};
 const value=report(),mask=value.mask_catalog.items[0];
 await assert.rejects(
  registerPersistentSubject(api,value,mask,{confirmed:true,timeoutMs:15}),
  {message:'SUBJECT_IDENTITY_TIMEOUT'});
 assert.equal(signal.aborted,true);
 const controller=new AbortController();
 const pending=registerPersistentSubject(api,value,mask,{
  confirmed:true,timeoutMs:1000,signal:controller.signal});
 controller.abort();
 await assert.rejects(pending,{message:'SUBJECT_IDENTITY_ABORTED'});
});

test('malformed success response fails closed',async()=>{
 const api={fetchApi:async()=>({ok:true,json:async()=>({ok:true,result:{
  status:'subject_identity_created',subject_id:'base-mask-00',
  mask_id:'base-mask-00',bbox_px:[0,0,4,3],sha256:sha('f'),
 }})})};
 const value=report();
 await assert.rejects(registerPersistentSubject(
  api,value,value.mask_catalog.items[0],{confirmed:true}),{
   message:'SUBJECT_IDENTITY_INVALID_RESPONSE'});
});
