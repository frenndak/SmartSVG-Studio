import test from 'node:test';
import assert from 'node:assert/strict';
import {createEditorProjectControls} from '../web/js/smartsvg_editor_project_bridge_g23.mjs';
import {encodeDocument} from '../web/js/smartsvg_editor_model_v216.mjs';

// G2.3 / R33-004: use the production handlers, not a model of the race.
const REF=name=>({filename:'ed_'+ 'd'.repeat(24)+'_'+name+'.png',
  subfolder:'SmartSVG_Studio_Editor',type:'output'});
const meta={version:1,width:12,height:9,count:2,source:'a'.repeat(64),
  preview_width:12,preview_height:9,image:REF('image'),
  masks:[REF('mask00'),REF('mask01')]};
const documentAt=u=>encodeDocument(meta,[{object:1,mode:'add',
  radius:0.01,points:[[u,0.3]]}]);

class Element {
  constructor(tag){this.tagName=tag;this.children=[];this.events={};
    this.textContent='';this.value='';this.disabled=false;}
  append(...children){this.children.push(...children);}
  addEventListener(type,fn){(this.events[type]??=[]).push(fn);}
  setAttribute(){}
  async fire(type){for(const fn of this.events[type]??[])await fn();}
}
function makePanel(stage='get'){
  globalThis.document={createElement:tag=>new Element(tag)};
  globalThis.FormData=class {
    constructor(){this.entries=[];}
    append(key,value){this.entries.push([key,value]);}
  };
  globalThis.window={confirm:()=>true};
  let release;
  const gate=new Promise(resolve=>{release=resolve;});
  const calls=[],widget={name:'retouches_json',value:documentAt(0.2)};
  const node={widgets:[widget],
    inputs:[{name:'image',link:2},{name:'masque_base',link:12}],
    setDirtyCanvas(){}};
  const api={async fetchApi(route,opts){
    calls.push({route,opts});
    if(route.includes('/project?')){
      if(stage==='get')await gate;
      return {ok:true,json:async()=>({ok:true,project:{
        status:'PROJECT_HEALTHY',sha256:'a'.repeat(64),
        document:{width_mm:40}}})};
    }
    if(route.includes('/editor?')){
      if(stage==='restore')await gate;
      return {ok:true,json:async()=>({ok:true,session:{
        base_masks_persisted:false,editor_json:documentAt(0.4)}})};
    }
    if(route.endsWith('/editor/save')){
      if(stage==='post')await gate;
      return {ok:true,json:async()=>({ok:true,result:{strokes_saved:1}})};
    }
    throw Error('Unexpected route: '+route);
  }};
  const panel=createEditorProjectControls(api,{graph:{}},node);
  const [,name,save,restore,status]=panel.root.children;
  name.value='snails';
  panel.refresh(meta);
  return {panel,name,save,restore,status,calls,widget,node,release};
}
const posts=h=>h.calls.filter(x=>x.route.endsWith('/editor/save'));
async function untilPost(h){
  for(let i=0;i<20&&posts(h).length===0;i++)await Promise.resolve();
  assert.equal(posts(h).length,1,'POST must have started before editing');
}

test('unchanged editor save posts once and reports success',async()=>{
  const h=makePanel('none');
  await h.save.fire('click');
  assert.equal(posts(h).length,1);
  assert.equal(Object.fromEntries(posts(h)[0].opts.body.entries).editor_json,
    documentAt(0.2));
  assert.match(h.status.textContent,/Retouches conservées/);
});
test('edit during asynchronous project inspection prevents stale POST',async()=>{
  const h=makePanel();
  const pending=h.save.fire('click');
  assert.equal(h.calls.length,1);
  h.widget.value=documentAt(0.7);
  h.release();await pending;
  assert.equal(posts(h).length,0);
  assert.equal(h.widget.value,documentAt(0.7));
  assert.match(h.status.textContent,/aucun enregistrement envoyé/);
});
test('project name, input links or refreshed source invalidate pending save',async()=>{
  for(const changed of ['name','links','source']){
    const h=makePanel();
    const pending=h.save.fire('click');
    assert.equal(h.calls.length,1);
    if(changed==='name')h.name.value='another_project';
    if(changed==='links')h.node.inputs[1].link=99;
    if(changed==='source')h.panel.refresh({...meta,source:'b'.repeat(64)});
    h.release();await pending;
    assert.equal(posts(h).length,0,changed);
    assert.match(h.status.textContent,/aucun enregistrement envoyé/,changed);
  }
});
test('edits during POST are not falsely reported as the current saved state',async()=>{
  const h=makePanel('post');
  const pending=h.save.fire('click');
  await untilPost(h);
  h.widget.value=documentAt(0.7);
  h.release();await pending;
  assert.equal(posts(h).length,1);
  assert.equal(h.widget.value,documentAt(0.7));
  assert.match(h.status.textContent,/Ancien état enregistré/);
  assert.match(h.status.textContent,/modifications récentes restent à sauvegarder/);
});

test('unchanged restore applies the validated session',async()=>{
  const h=makePanel('none');
  await h.restore.fire('click');
  assert.equal(h.widget.value,documentAt(0.4));
  assert.match(h.status.textContent,/Retouches rechargées/);
});
test('asynchronous restore cannot overwrite edits or switch projects',async()=>{
  for(const changed of ['widget','name','links','source']){
    const h=makePanel('restore');
    const pending=h.restore.fire('click');
    assert.equal(h.calls.length,1,changed);
    if(changed==='widget')h.widget.value=documentAt(0.7);
    if(changed==='name')h.name.value='another_project';
    if(changed==='links')h.node.inputs[1].link=99;
    if(changed==='source')h.panel.refresh({...meta,source:'b'.repeat(64)});
    const expected=h.widget.value;
    h.release();await pending;
    assert.equal(h.widget.value,expected,changed);
    assert.match(h.status.textContent,/aucun rechargement appliqué/,changed);
  }
});
test('restore refuses edits made during the confirmation callback',async()=>{
  const h=makePanel('none');
  globalThis.window.confirm=()=>{h.widget.value=documentAt(0.8);return true;};
  await h.restore.fire('click');
  assert.equal(h.widget.value,documentAt(0.8));
  assert.match(h.status.textContent,/aucun rechargement appliqué/);
});
