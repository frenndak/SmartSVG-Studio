import test from 'node:test';
import assert from 'node:assert/strict';
import {editorDraftStore} from '../web/js/smartsvg_editor_draft_g28.mjs';
const ref=name=>({filename:'ed_'+'c'.repeat(24)+'_'+name+'.png',
  type:'output',subfolder:'SmartSVG_Studio_Editor'});
const meta={
  version:1,width:64,height:32,count:2,source:'a'.repeat(64),
  preview_width:64,preview_height:32,image:ref('image'),
  masks:[ref('mask00'),ref('mask01')]
};
const stroke=({object=0,mode='add'}={})=>
  ({object,mode,radius:0.02,points:[[0.1,0.2],[0.3,0.4]]});
const fakeStorage=()=>new class{
 constructor(){this.data=new Map();}
 getItem(key){return this.data.get(key)||null;}
 setItem(key,val){this.data.set(key,val);}
 removeItem(key){this.data.delete(key);}
}();

test('crash reopens identical source and object slots from an automatic draft',()=>{
  const storage=fakeStorage(),clock=()=>500000000;
  const writer=editorDraftStore(storage,meta,14,clock);
  assert.equal(writer.enabled,true);
  assert.equal(writer.save([stroke(),stroke({object:1,mode:'erase'})]),true);
  const reader=editorDraftStore(storage,{...meta},14,clock);
  assert.deepEqual(reader.load(),[stroke(),stroke({object:1,mode:'erase'})]);
  assert.ok(writer.key.includes(meta.source));
  const raw=storage.getItem(writer.key);
  const envelope=JSON.parse(raw);
  assert.equal(envelope.document.includes('"points"'),true);
  assert.equal(raw.includes('"image"'),false,'do not store image bytes or output URL');
});

test('unrelated node/source, old draft, invalid JSON and changed dimensions are rejected',()=>{
  const storage=fakeStorage(),t=1000000000;
  const original=editorDraftStore(storage,meta,14,()=>t);
  assert.equal(original.save([stroke()]),true);
  assert.equal(editorDraftStore(storage,meta,15,()=>t).load(),null);
  assert.equal(editorDraftStore(storage,{...meta,source:'b'.repeat(64)},14,()=>t).load(),null);
  assert.equal(editorDraftStore(storage,{...meta,width:128},14,()=>t).load(),null);
  assert.equal(editorDraftStore(storage,meta,14,()=>t+8*86400000).load(),null);
  assert.equal(storage.getItem(original.key),null,'expired draft erased');
  storage.setItem(original.key,'{not-json');
  assert.equal(original.load(),null);
  assert.equal(storage.getItem(original.key),null);
});

test('explicit discard, empty history and hostile strokes do not preserve invalid drafts',()=>{
  const storage=fakeStorage(),draft=editorDraftStore(storage,meta,3,()=>100000);
  assert.equal(draft.save([stroke()]),true);
  assert.equal(draft.save([]),true);
  assert.equal(draft.load(),null);
  assert.equal(draft.save([{object:9,mode:'add',radius:0.02,points:[[0.1,0.3]]}]),false);
  assert.equal(draft.save([stroke()]),true);
  assert.equal(draft.clear(),true);
  assert.equal(draft.load(),null);
});

test('disabled storage and quota failures never prevent editor action',()=>{
  const quota={getItem(){return null;},setItem(){throw Error('QuotaExceededError');},
    removeItem(){throw Error('SecurityError');}};
  const limited=editorDraftStore(quota,meta,11,()=>10000);
  assert.equal(limited.enabled,true);
  assert.equal(limited.save([stroke()]),false);
  assert.equal(limited.clear(),false);
  const denied=editorDraftStore(null,meta,11);
  assert.equal(denied.enabled,false);
  assert.equal(denied.load(),null);
  assert.equal(denied.save([stroke()]),false);
  assert.equal(denied.clear(),false);
});
test('stale or malformed recovery envelopes are cleared instead of being applied',()=>{
  const storage=fakeStorage(),draft=editorDraftStore(storage,meta,5,()=>2000000);
  draft.save([stroke()]);
  const raw=JSON.parse(storage.getItem(draft.key));
  raw.count=999;
  storage.setItem(draft.key,JSON.stringify(raw));
  assert.equal(draft.load(),null);
  assert.equal(storage.getItem(draft.key),null);
  draft.save([stroke()]);
  const wrong=JSON.parse(storage.getItem(draft.key));
  wrong.document=wrong.document.replace('"source":"'+meta.source+'"',
    '"source":"'+('f'.repeat(64))+'"');
  storage.setItem(draft.key,JSON.stringify(wrong));
  assert.equal(draft.load(),null);
  assert.equal(storage.getItem(draft.key),null);
});
