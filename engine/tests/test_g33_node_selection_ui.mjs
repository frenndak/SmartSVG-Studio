import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as handoff from '../web/js/smartsvg_subject_handoff_g33.mjs';
import * as selection from '../web/js/smartsvg_subject_selection_g33c.mjs';

const original=fs.readFileSync(new URL('../web/js/smartsvg_subject_inspector_v21154.js',import.meta.url),'utf8');
const script=original
 .replace("import {app} from '../../scripts/app.js';","const app=globalThis.__app;")
 .replace("await import('./smartsvg_subject_handoff_g33.mjs')","await Promise.resolve(globalThis.__handoff)")
 .replace("await import('./smartsvg_subject_selection_g33c.mjs')","await Promise.resolve(globalThis.__selection)");
const png='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAAD0lEQVR42mNgGAUMDAwMAAEIAAEoUqMqAAAAAElFTkSuQmCC';
const report=()=>({smartsvg_subjects_v21154:[{
 source_sha256:'a'.repeat(64),width_px:160,height_px:90,count:2,selection:1,
 sujets:[
  {numero:1,image_data:png,codes:[],zones_a_examiner:[],zones_non_affichees:0},
  {numero:2,image_data:png,codes:['FRAGMENTS_DETACHES'],
   zones_a_examiner:[{type:'FRAGMENT_SEPARE',bbox_source_px:[1,2,8,10],
     bbox_apercu_88px:[2,3,14,19]}],zones_non_affichees:0}
 ]}]});
function setup(){
 class Element{
  constructor(tag){this.tagName=tag;this.children=[];this.style={};this.attributes={};
   this.listeners={};this.hidden=false;this.disabled=false;this.value='';this.textContent='';}
  append(...xs){this.children.push(...xs);}
  replaceChildren(...xs){this.children=[...xs];}
  addEventListener(name,cb){(this.listeners[name]??=[]).push(cb);}
  async fire(name){for(const cb of this.listeners[name]??[])await cb();}
  setAttribute(k,v){this.attributes[k]=String(v);}
 }
 const document={createElement:tag=>new Element(tag)};
 let extension=null,root=null;
 const app={registerExtension(e){extension=e;}};
 const channels=[];
 class BroadcastChannel{
  constructor(name){this.name=name;this.closed=false;this.sent=[];channels.push(this);}
  postMessage(data){this.sent.push(data);}
  close(){this.closed=true;}
  receive(data){this.onmessage?.({data});}
 }
 const random={getRandomValues(bytes){bytes.fill(0x42);return bytes;}};
 const timers=new Map();
 let timer=0;
 const context={__app:app,__handoff:handoff,
  __selection:{...selection,createSelectionBinding:(n,r)=>selection.createSelectionBinding(n,r,random)},
  document,window:{location:{protocol:'http:'}},BroadcastChannel,
  setTimeout:fn=>{const id=++timer;timers.set(id,fn);return id;},
  clearTimeout:id=>timers.delete(id),console,CustomEvent:class{}};
 vm.runInNewContext(script,context,{timeout:5000});
 const node={id:17,comfyClass:'SmartSVGChooseSubjectV21154',
  inputs:[{name:'image',link:3},{name:'masques_objets',link:4}],
  widgets:[{name:'numero_sujet',value:1}],size:[300,200],
  addDOMWidget(_name,_type,element){root=element;},
  setDirtyCanvas(){},graph:{setDirtyCanvas(){}}};
 extension.nodeCreated(node);
 assert.ok(root,'real inspector is attached to source node');
 const hint=root.children[1],share=root.children[5],confirm=root.children[6];
 return {node,root,hint,share,confirm,channels,timers};
}
test('source node changes widget only after its own explicit confirmation',async()=>{
 const s=setup();s.node.onExecuted(report());
 assert.equal(s.share.disabled,false);
 await s.share.fire('click');
 assert.equal(s.channels.length,1);
 const c=s.channels[0],sent=c.sent[0];
 assert.equal(sent.node_id,17);assert.equal(sent.session_id,'42'.repeat(16));
 const proposal=selection.makeSelectionProposal(sent,2);
 assert.ok(proposal);
 c.receive(proposal);
 assert.equal(s.confirm.hidden,false);
 assert.equal(s.node.widgets[0].value,1,'proposal must not write');
 await s.confirm.fire('click');
 assert.equal(s.node.widgets[0].value,2);
 assert.equal(c.closed,true);
 assert.match(s.hint.textContent,/Relancer manuellement/);
 assert.equal(s.node.inputs[1].link,4,'float32 mask connection untouched');
});
test('detached link or stale rerun invalidates pending confirmation',async()=>{
 const s=setup();s.node.onExecuted(report());await s.share.fire('click');
 const c=s.channels[0];
 c.receive(selection.makeSelectionProposal(c.sent[0],2));
 s.node.inputs[1].link=null;
 await s.confirm.fire('click');
 assert.equal(s.node.widgets[0].value,1);
 assert.match(s.hint.textContent,/périmée/);
 const t=setup();t.node.onExecuted(report());await t.share.fire('click');
 const old=t.channels[0];
 old.receive(selection.makeSelectionProposal(old.sent[0],2));
 t.node.onExecuted(report());
 assert.equal(old.closed,true);
 await t.confirm.fire('click');
 assert.equal(t.node.widgets[0].value,1);
});
test('missing widget and callback failure never leave a false committed choice',async()=>{
 const s=setup();s.node.onExecuted(report());await s.share.fire('click');
 const c=s.channels[0];s.node.widgets=[];
 c.receive(selection.makeSelectionProposal(c.sent[0],2));
 assert.equal(s.confirm.hidden,true);
 const t=setup();t.node.onExecuted(report());await t.share.fire('click');
 const d=t.channels[0];d.receive(selection.makeSelectionProposal(d.sent[0],2));
 t.node.widgets[0].callback=()=>{throw Error('mock failure');};
 await t.confirm.fire('click');
 assert.equal(t.node.widgets[0].value,1);
 assert.match(t.hint.textContent,/restaurée/);
});
