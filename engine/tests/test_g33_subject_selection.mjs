import test from 'node:test';
import assert from 'node:assert/strict';
import {createSelectionBinding,linkedMaskInputs,makeSelectionProposal,
 validateSelectionProposal,newSessionId} from '../web/js/smartsvg_subject_selection_g33c.mjs';
const sha='a'.repeat(64);
const node=()=>({id:17,inputs:[{name:'image',link:3},
 {name:'masques_objets',link:4}],widgets:[{name:'numero_sujet',value:1}]});
const report=()=>({source_sha256:sha,width_px:160,height_px:90,count:2,
 sujets:[{numero:1,codes:['FRAGMENTS_DETACHES'],zones_a_examiner:[
   {type:'FRAGMENT_SEPARE',bbox_source_px:[1,2,8,10]}]},
   {numero:2,codes:['MASQUE_VIDE'],zones_a_examiner:[]}]});
const random={getRandomValues(bytes){bytes.fill(0x42);return bytes;}};
test('proposal is explicit, source+node+session pinned, non-destructive',()=>{
 const n=node(),r=report(),b=createSelectionBinding(n,r,random);
 assert.equal(b.node_id,17);assert.equal(b.session_id,'42'.repeat(16));
 const p=makeSelectionProposal({...r,...b},1);
 assert.equal(validateSelectionProposal(p,b,n,r),1);
 assert.equal(p.subject,1);
 assert.equal(r.sujets[0].zones_a_examiner.length,1,'detached accessory retained');
 assert.equal(n.widgets[0].value,1,'validator never writes node');
 assert.equal(makeSelectionProposal({...r,...b},2),null,'empty mask not selectable');
 assert.equal(makeSelectionProposal({...r,...b},3),null);
});
test('stale source, session, node, missing name/id and detached links fail closed',()=>{
 const n=node(),r=report(),b=createSelectionBinding(n,r,random);
 const p=makeSelectionProposal({...r,...b},1);
 const variants=[
  {...p,source_sha256:'b'.repeat(64)},
  {...p,session_id:'c'.repeat(32)},
  {...p,node_id:18},{...p,node_id:undefined},
  {...p,subject:0},{...p,subject:3},
  {...p,count:3},{...p,width_px:161},{...p,kind:'other'},
 ];
 for(const bad of variants)assert.equal(validateSelectionProposal(bad,b,n,r),null);
 assert.equal(validateSelectionProposal(p,b,n,{...r,source_sha256:'b'.repeat(64)}),null);
 assert.equal(validateSelectionProposal(p,b,{...n,id:18},r),null);
 assert.equal(validateSelectionProposal(p,b,{...n,inputs:[{name:'image',link:3}]},r),null);
 assert.equal(validateSelectionProposal(p,b,{...n,inputs:[{name:'image',link:3},{name:'masques_objets',link:null}]},r),null);
 assert.equal(validateSelectionProposal(p,b,{...n,inputs:[{name:'image',link:3},{name:'masques_objets',link:9}]},r),null);
 assert.equal(createSelectionBinding({...n,id:null},r,random),null);
 assert.equal(createSelectionBinding({...n,inputs:[]},r,random),null);
 assert.equal(linkedMaskInputs({...n,inputs:[{name:'image',link:3}]}),null);
 assert.equal(createSelectionBinding(n,r,{}),null,'no secure random = read-only');
 assert.equal(newSessionId({}),null);
});
