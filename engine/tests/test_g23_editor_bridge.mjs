import test from 'node:test';
import assert from 'node:assert/strict';
import {createEditorProjectControls,validName} from '../web/js/smartsvg_editor_project_bridge_g23.mjs';
import {encodeDocument} from '../web/js/smartsvg_editor_model_v216.mjs';

const REF=name=>({filename:'ed_'+ 'd'.repeat(24)+'_'+name+'.png',
  subfolder:'SmartSVG_Studio_Editor',type:'output'});
const meta={version:1,width:12,height:9,count:2,source:'a'.repeat(64),
  preview_width:12,preview_height:9,image:REF('image'),
  masks:[REF('mask00'),REF('mask01')]};
const brush=()=>encodeDocument(meta,[{object:1,mode:'add',
  radius:0.01,points:[[0.2,0.3],[0.3,0.4]]}]);

class El {
  constructor(tag){this.tagName=tag;this.textContent='';this.value='';this.children=[];
    this.events={};this.disabled=false;this.attrs={};this.style={};}
  append(...children){this.children.push(...children);}
  addEventListener(t,fn){(this.events[t]??=[]).push(fn);}
  setAttribute(k,v){this.attrs[k]=v;}
  async fire(t){for(const fn of this.events[t]||[])await fn();}
}

function makePanel(){
  globalThis.document={createElement:type=>new El(type)};
  globalThis.window={confirm:()=>true};
  globalThis.FormData=class {
    constructor(){this.entries=[];}
    append(k,v){this.entries.push([k,v]);}
  };
  const calls=[],widget={name:'retouches_json',value:brush()};
  let stored=brush(),allowed=true,callbackCalls=0;
  const node={widgets:[widget],
    inputs:[{name:'image',link:2},{name:'masque_base',link:12}],
    setDirtyCanvas(){}};
  const app={graph:{change(){callbackCalls++;}}};
  const api={
    async fetchApi(route,opts){
      calls.push({route,opts});
      if(!allowed) return {ok:false,json:async()=>({ok:false,error_code:'PROJECT_CHANGED'})};
      if(route.startsWith('/smartsvg/g22/project?'))
        return {ok:true,json:async()=>({ok:true,project:{
          name:'snails',status:'PROJECT_HEALTHY',sha256:'a'.repeat(64),
          document:{width_mm:40}}})};
      if(route.endsWith('/editor/save')){
        stored=opts.body.entries.find(x=>x[0]==='editor_json')[1];
        return {ok:true,json:async()=>({ok:true,result:{strokes_saved:JSON.parse(stored).strokes.length}})};
      }
      if(route.startsWith('/smartsvg/g22/editor?'))
        return {ok:true,json:async()=>({ok:true,session:{
          editor_json:stored,base_masks_persisted:false}})};
      return {ok:false,json:async()=>({ok:false,error_code:'UNKNOWN_ROUTE'})};
    }
  };
  const panel=createEditorProjectControls(api,app,node);
  const [label,name,save,load,status]=panel.root.children;
  name.value='snails';panel.refresh(meta);
  return {panel,label,name,save,load,status,calls,widget,node,
    setStored:next=>{stored=next},
    fail:()=>{allowed=false},countChanges:()=>callbackCalls};
}
test('name validation refuses path tricks and reserved suffixes',()=>{
  for(const n of ['../../secret','C:\\Windows','with spaces','a.previous','a'.repeat(49),'demo_previous'])
    assert.equal(validName(n),false,n);
  assert.equal(validName('snails_24'),true);
});
test('strokes save uses actual V216 JSON and archive revision fingerprint',async()=>{
  const h=makePanel();
  await h.save.fire('click');
  assert.equal(h.calls.length,2);
  assert.match(h.calls[0].route,/\/project\?name=snails$/);
  const req=h.calls[1];
  assert.match(req.route,/\/editor\/save$/);
  assert.equal(req.opts.headers['X-SmartSVG-UI'],'1');
  const values=Object.fromEntries(req.opts.body.entries);
  assert.equal(values.expected_sha256,'a'.repeat(64));
  assert.deepEqual(JSON.parse(values.editor_json),JSON.parse(brush()));
  assert.match(h.status.textContent,/Masques de base externes/);
});
test('load matching source after confirmation updates only historical retouches widget',async()=>{
  const h=makePanel();
  h.widget.value='';
  await h.load.fire('click');
  assert.deepEqual(JSON.parse(h.widget.value),JSON.parse(brush()));
  assert.equal(h.countChanges(),1);
  assert.match(h.status.textContent,/Relancer le workflow/);
});
test('reject mismatching source fingerprint without changing the widget',async()=>{
  const h=makePanel();
  const bad=JSON.parse(brush());bad.source='b'.repeat(64);
  h.setStored(JSON.stringify(bad));
  const old=h.widget.value;
  await h.load.fire('click');
  assert.equal(h.widget.value,old);
  assert.equal(h.countChanges(),0);
});
test('reject source link changes since last node execution',async()=>{
  const h=makePanel();
  h.node.inputs[1].link=99;
  await h.save.fire('click');
  assert.equal(h.calls.length,0);
  assert.match(h.status.textContent,/relancer le nœud/);
});
test('refuse restoring without explicit confirmation',async()=>{
  const h=makePanel(),old=h.widget.value;
  globalThis.window.confirm=()=>false;
  await h.load.fire('click');
  assert.equal(h.widget.value,old);
  assert.equal(h.countChanges(),0);
});
test('failure from API never marks a save as successful',async()=>{
  const h=makePanel();h.fail();
  await h.save.fire('click');
  assert.doesNotMatch(h.status.textContent,/Retouches conservées/);
  assert.equal(h.countChanges(),0);
});
test('callback failure rolls back widget value',async()=>{
  const h=makePanel();
  h.widget.value='';
  h.widget.callback=()=>{throw Error('widget callback rejected')};
  await h.load.fire('click');
  assert.equal(h.widget.value,'');
  assert.equal(h.countChanges(),0);
});
test('no mask source currently loaded disables project actions',()=>{
  const h=makePanel();
  h.panel.refresh(null);
  assert.equal(h.save.disabled,true);
  assert.equal(h.load.disabled,true);
});
