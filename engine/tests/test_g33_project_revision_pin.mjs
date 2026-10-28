import test from 'node:test';
import assert from 'node:assert/strict';
import {validProjectName,validProjectLock,makeProjectLock,
  matchesProjectLock,readProjectRevision}
  from '../web/js/smartsvg_subject_project_gate_g33d.mjs';
import {makeSelectionProposal,validateSelectionProposal}
  from '../web/js/smartsvg_subject_selection_g33c.mjs';
import {normalizeSubjectInspection} from '../web/js/smartsvg_subject_handoff_g33.mjs';

const source='a'.repeat(64),revision='b'.repeat(64);
const report=()=>({source_sha256:source,width_px:160,height_px:90,
  count:2,selection:1,sujets:[
    {numero:1,codes:[],zones_a_examiner:[],zones_non_affichees:0},
    {numero:2,codes:['FRAGMENTS_DETACHES'],zones_a_examiner:[],zones_non_affichees:0}
  ]});
const project=()=>({name:'mes_sujets',status:'PROJECT_HEALTHY',sha256:revision,
  base_masks:{exact_float32:true,editor_fingerprint:source,
    count:2,dimensions_px:[160,90]}});
const binding=()=>({node_id:17,session_id:'c'.repeat(32),
  expires_at_ms:Date.now()+60_000,source_sha256:source,
  width_px:160,height_px:90,count:2,links:JSON.stringify([3,4])});
const node=()=>({id:17,inputs:[{name:'image',link:3},{name:'masques_objets',link:4}]});

test('project lock requires healthy matching G2.4 full-resolution float32 fingerprint',()=>{
 const lock=makeProjectLock('mes_sujets',project(),report());
 assert.deepEqual({...lock},{project_name:'mes_sujets',project_sha256:revision});
 assert.equal(matchesProjectLock(lock,project(),report()),true);
 assert.equal(matchesProjectLock(lock,{...project(),sha256:'d'.repeat(64)},report()),false);
 const invalid=[
  {...project(),name:'other'},
  {...project(),status:'PROJECT_RECOVERABLE'},
  {...project(),sha256:'bad'},
  {...project(),base_masks:undefined},
  {...project(),base_masks:{...project().base_masks,exact_float32:false}},
  {...project(),base_masks:{...project().base_masks,editor_fingerprint:'e'.repeat(64)}},
  {...project(),base_masks:{...project().base_masks,count:1}},
  {...project(),base_masks:{...project().base_masks,dimensions_px:[160,91]}}
 ];
 for(const p of invalid)assert.equal(makeProjectLock('mes_sujets',p,report()),null);
 assert.equal(makeProjectLock('mes_sujets',project(),{...report(),source_sha256:'bad'}),null);
 for(const n of ['','../private','x_previous','échec','x'.repeat(49)]){
   assert.equal(validProjectName(n),false);
 }
 assert.equal(validProjectName('mes_sujets'),true);
 assert.equal(validProjectLock({project_name:'mes_sujets',project_sha256:'bad'}),false);
});

test('read-only project API fails closed on missing, invalid and failed responses',async()=>{
 const seen=[];
 const api={fetchApi:async path=>{
   seen.push(path);return {ok:true,json:async()=>({ok:true,project:project()})};
 }};
 assert.deepEqual(await readProjectRevision(api,'mes_sujets'),project());
 assert.deepEqual(seen,['/smartsvg/g22/project?name=mes_sujets']);
 await assert.rejects(readProjectRevision(api,'../escape'));
 await assert.rejects(readProjectRevision(null,'mes_sujets'));
 await assert.rejects(readProjectRevision({fetchApi:async()=>({ok:false})},'mes_sujets'));
 await assert.rejects(readProjectRevision({fetchApi:async()=>({
   ok:true,json:async()=>({ok:false})})},'mes_sujets'));
});

test('project pin survives handoff and cannot be stripped or forged in proposal',()=>{
 const lock=makeProjectLock('mes_sujets',project(),report());
 const activeBinding=binding();
 const bound={...report(),...activeBinding,...lock};
 const normalized=normalizeSubjectInspection(bound);
 assert.equal(normalized.project_name,'mes_sujets');
 assert.equal(normalized.project_sha256,revision);
 const proposal=makeSelectionProposal(normalized,2);
 assert.equal(proposal.project_sha256,revision);
 assert.equal(validateSelectionProposal(
   proposal,{...activeBinding,...lock},node(),report()),2);
 for(const bad of [
   {...proposal,project_sha256:'d'.repeat(64)},
   {...proposal,project_name:'other'},
   {...proposal,project_sha256:undefined},
   {...proposal,project_name:undefined}
 ]){
   assert.equal(validateSelectionProposal(bad,{...binding(),...lock},node(),report()),null);
 }
 assert.equal(normalizeSubjectInspection({...bound,project_sha256:undefined}),null);
 assert.equal(normalizeSubjectInspection({...report(),...lock}),null,
   'a project lock without an active source node is never executable');
 assert.equal(makeSelectionProposal({...normalized,project_sha256:'bad'},2),null);
 assert.equal(makeSelectionProposal({...normalized,project_name:undefined},2),null);
 assert.equal(makeSelectionProposal({...report(),...binding()},2).project_name,undefined,
   'legacy unbound workflow remains available');
});

test('project GET timeout aborts a hung request and a hung JSON decoder',async()=>{
 let firstSignal;
 const hung={fetchApi:(_route,options)=>{
   firstSignal=options.signal;
   return new Promise(()=>{});
 }};
 await assert.rejects(readProjectRevision(hung,'mes_sujets',{timeoutMs:15}),
   {message:'PROJECT_BINDING_TIMEOUT'});
 assert.equal(firstSignal.aborted,true,'abort is requested even if fetch ignores it');
 let secondSignal;
 const stalledBody={fetchApi:async(_route,options)=>{
   secondSignal=options.signal;
   return {ok:true,json:()=>new Promise(()=>{})};
 }};
 await assert.rejects(readProjectRevision(stalledBody,'mes_sujets',{timeoutMs:15}),
   {message:'PROJECT_BINDING_TIMEOUT'});
 assert.equal(secondSignal.aborted,true,'JSON parsing is also time-bounded');
});

test('external cancellation rejects a stale inspection and does not issue a late GET',async()=>{
 const cancelled=new AbortController();
 cancelled.abort();
 let calls=0;
 const api={fetchApi:(_route,options)=>{
   calls++;
   assert.equal(options.signal.aborted,false);
   return new Promise(()=>{});
 }};
 await assert.rejects(readProjectRevision(api,'mes_sujets',
   {signal:cancelled.signal,timeoutMs:100}),{message:'PROJECT_BINDING_ABORTED'});
 assert.equal(calls,0,'already cancelled inspection must not issue a GET');
 const current=new AbortController();
 const pending=readProjectRevision(api,'mes_sujets',
   {signal:current.signal,timeoutMs:100});
 assert.equal(calls,1);
 current.abort();
 await assert.rejects(pending,{message:'PROJECT_BINDING_ABORTED'});
 await assert.rejects(readProjectRevision(api,'mes_sujets',{timeoutMs:0}),
   {message:'PROJECT_BINDING_UNAVAILABLE'});
 assert.equal(calls,1,'invalid timeout must not issue a GET');
});
