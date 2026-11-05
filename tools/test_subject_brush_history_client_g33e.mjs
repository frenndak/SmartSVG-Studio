import test from 'node:test';
import assert from 'node:assert/strict';
import {webcrypto} from 'node:crypto';
if(!globalThis.crypto)globalThis.crypto=webcrypto;
import {inspectSubjectBrushHistory,changeSubjectBrushHistory,createBrushHistoryControls} from
  '../engine/web/js/smartsvg_subject_brush_history_g33e.mjs';

const SHA='a'.repeat(64),SUBJECT='subject-'+'d'.repeat(32);
function api(write){
  let writes=0,fields;
  return {get writes(){return writes;},get fields(){return fields;},
    async fetchApi(url,options){
      assert.equal(options.headers['X-SmartSVG-UI'],'1');
      const values=Object.fromEntries(options.body.entries());
      if(url.endsWith('/status'))return {ok:true,async json(){return {ok:true,certified:false,history:{
        name:values.name,project_sha256:SHA,undo_available:true,redo_available:false,
        undo_subject_id:SUBJECT,redo_error_code:'BRUSH_NOTHING_TO_REDO',cricut_certified:false,
      }}}};
      assert.equal(url,'/smartsvg/g22/subject/history/apply');writes++;fields=values;
      if(write)return write(values);
      return {ok:true,async json(){return {ok:true,certified:false,result:{
        name:values.name,sha256:'b'.repeat(64),action:values.action,command_id:values.command_id,
        status:'brush_history_'+values.action,persisted:true,cricut_certified:false,
      }}}};
    }};
}

test('native history read is explicit and an action uses that pinned revision',async()=>{
  const transport=api(),snapshot=await inspectSubjectBrushHistory(transport,'brush-project');
  assert.equal(transport.writes,0);assert.equal(snapshot.canUndo,true);
  await assert.rejects(changeSubjectBrushHistory(transport,snapshot,'undo'),/BRUSH_HISTORY_CONFIRMATION_REQUIRED/);
  const result=await changeSubjectBrushHistory(transport,snapshot,'undo',{confirmed:true});
  assert.equal(transport.fields.expected_sha256,SHA);assert.equal(transport.fields.confirmed,'yes');
  assert.equal(result.persisted,true);assert.equal(result.cricutCertified,false);
  await changeSubjectBrushHistory(transport,snapshot,'undo',{confirmed:true});
  assert.equal(transport.writes,1);
});
test('forged, unavailable, or consumed snapshot cannot mutate history',async()=>{
  const transport=api(),snapshot=await inspectSubjectBrushHistory(transport,'brush-project');
  await assert.rejects(changeSubjectBrushHistory(transport,{...snapshot},'undo',{confirmed:true}),/INVALID_BRUSH_HISTORY_SNAPSHOT/);
  await assert.rejects(changeSubjectBrushHistory(transport,snapshot,'redo',{confirmed:true}),/BRUSH_NOTHING_TO_REDO/);
  assert.equal(transport.writes,0);
  await changeSubjectBrushHistory(transport,snapshot,'undo',{confirmed:true});
  await assert.rejects(changeSubjectBrushHistory(transport,snapshot,'redo',{confirmed:true}),/BRUSH_HISTORY_STALE/);
});
test('double click permits one command and timeout remains an unknown write outcome',async()=>{
  let finish;
  const transport=api(()=>new Promise(resolve=>{finish=resolve;}));
  const snapshot=await inspectSubjectBrushHistory(transport,'brush-project');
  const first=changeSubjectBrushHistory(transport,snapshot,'undo',{confirmed:true,timeoutMs:10});
  await assert.rejects(changeSubjectBrushHistory(transport,snapshot,'undo',{confirmed:true}),/SAVE_BUSY/);
  await assert.rejects(first,/SAVE_OUTCOME_UNKNOWN/);
  await assert.rejects(changeSubjectBrushHistory(transport,snapshot,'undo',{confirmed:true}),/SAVE_OUTCOME_UNKNOWN/);
  assert.equal(transport.writes,1);
  finish({ok:true,async json(){return {ok:true};}});
});

function document(){
  return {createElement(tag){return {tagName:tag,disabled:false,textContent:'',children:[],events:{},
    setAttribute(){},appendChild(node){this.children.push(node);},
    addEventListener(type,fn){this.events[type]=fn;}};}};
}
test('history controls bracket a write and retain an honest unknown-outcome status',async()=>{
  const transport=api(()=>{throw Error('connection lost');});
  let begins=0,ends=0;const messages=[];
  const controls=createBrushHistoryControls(transport,'brush-project',{
    document:document(),onBeforeWrite(){begins++;},onAfterWrite(){ends++;},onMessage(m){messages.push(m);},
  });
  await controls.refresh();
  const buttons=controls.element.children.filter(x=>x.tagName==='button');
  const undo=buttons.find(x=>/Annuler/.test(x.textContent));
  const redo=buttons.find(x=>/Rétablir/.test(x.textContent));
  assert.equal(undo.disabled,false);assert.equal(redo.disabled,true);
  await undo.events.click();
  assert.equal(begins,1);assert.equal(ends,1);assert.equal(undo.disabled,true);
  assert.match(messages.at(-1),/incertain/);
  await undo.events.click();assert.equal(transport.writes,1);
});
test('disposing a history control prevents a detached action',async()=>{
  const transport=api();const controls=createBrushHistoryControls(transport,'brush-project',{document:document()});
  await controls.refresh();controls.dispose();
  const undo=controls.element.children.find(x=>x.tagName==='button'&&/Annuler/.test(x.textContent));
  await undo.events.click();assert.equal(transport.writes,0);assert.equal(undo.disabled,true);
});

test('known durable undo refreshes native status and enables redo without a ComfyUI report',async()=>{
  let undone=false,writes=0,reads=0;
  const transport={async fetchApi(url,{body}){
    const fields=Object.fromEntries(body.entries());
    if(url.endsWith('/status')){
      reads++;return {ok:true,async json(){return {ok:true,certified:false,history:{
        name:fields.name,project_sha256:undone?'b'.repeat(64):SHA,
        undo_available:!undone,redo_available:undone,
        undo_subject_id:SUBJECT,redo_subject_id:SUBJECT,cricut_certified:false,
      }}}};
    }
    writes++;undone=fields.action==='undo';
    return {ok:true,async json(){return {ok:true,certified:false,result:{name:fields.name,
      action:fields.action,command_id:fields.command_id,sha256:undone?'b'.repeat(64):SHA,
      status:'brush_history_'+fields.action,persisted:true,cricut_certified:false,
    }}}};
  }};
  let begins=0,ends=0;
  const controls=createBrushHistoryControls(transport,'brush-project',{
    document:document(),onBeforeWrite(){begins++;},onAfterWrite(){ends++;}});
  await controls.refresh();
  const undo=controls.element.children.find(x=>x.tagName==='button'&&/Annuler/.test(x.textContent));
  const redo=controls.element.children.find(x=>x.tagName==='button'&&/Rétablir/.test(x.textContent));
  await undo.events.click();assert.equal(undo.disabled,true);assert.equal(redo.disabled,false);
  await redo.events.click();assert.equal(undo.disabled,false);assert.equal(redo.disabled,true);
  assert.equal(writes,2);assert.equal(reads,3);assert.equal(begins,2);assert.equal(ends,2);
});
