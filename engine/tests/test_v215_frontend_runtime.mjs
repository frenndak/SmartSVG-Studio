import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as model from '../web/js/smartsvg_ui_model.mjs';
const root=path.dirname(fileURLToPath(import.meta.url));

class StubElement {
  constructor(tag) {
    this.tagName=tag;this.children=[];this.dataset={};this.hidden=false;
    this.className='';this.textContent='';this.style={};this.attributes=new Map();
    this.classList={toggle(name,enabled){}};this.events=new Map();
  }
  append(...items){this.children.push(...items);}
  appendChild(item){this.children.push(item);return item;}
  replaceChildren(...items){this.children=[...items];}
  setAttribute(k,v){this.attributes.set(k,String(v));}
  removeAttribute(k){this.attributes.delete(k);}
  addEventListener(k,fn){this.events.set(k,fn);}
}

let loadCount=0;
async function loadExtension() {
  let registered=null;
  globalThis.__mockApp={registerExtension(ext){registered=ext;}};
  globalThis.__smartsvgTestModel=model;
  globalThis.window={location:{href:'http://localhost:8188/'}};
  Object.defineProperty(globalThis,"navigator",{value:{clipboard:{writeText:async value=>value}},configurable:true});
  const styleHolder=new StubElement('head');
  globalThis.document={head:styleHolder,getElementById:()=>null,createElement:name=>new StubElement(name)};
  let code=fs.readFileSync(path.join(root,'../web/js/smartsvg_ui.js'),'utf8');
  code=code.replace('import { app } from "../../scripts/app.js";', 'const app=globalThis.__mockApp;');
  code=code.replace('import { normalizePayload, normalizePreviews, previewUrl } from "./smartsvg_ui_model.mjs";',
    'const { normalizePayload, normalizePreviews, previewUrl }=globalThis.__smartsvgTestModel;');
  await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64')+'#run='+String(++loadCount));
  assert.ok(registered);
  return registered;
}

test('new node gets functional non-serializable dashboard',async()=>{
  const extension=await loadExtension();
  const node={comfyClass:'SmartSVGExpressV215',size:[280,100],addDOMWidget(name,type,root,options){
    const widget={name,type,root,options};this.widget=widget;return widget;}};
  extension.nodeCreated(node);
  assert.ok(node._smartsvgV215Dashboard);
  assert.equal(node.widget.serialize,false);
  assert.equal(node.widget.options.serialize,false);
  assert.ok(node.size[0]>=400);
  node.onExecuted({smartsvg:[{objets_total:24,planches_total:2,alertes_total:1,
    provenance:'Masques test',action_requise:'Vérifier dans Cricut',
    objets:[{numero:1,largeur_mm:33.5,etat:'RISQUE_ELEVE',nombre_alertes:1,alertes:['Contour incomplet']}]}],
    smartsvg_previews:[{filename:'qa_global_abc12345678900.png',type:'output',subfolder:'SmartSVG_Studio_Previews'}]});
  const element=node.widget.root;
  const counts=element.children[3];
  assert.equal(counts.children[0].children[0].textContent,'24');
  assert.equal(counts.children[1].children[0].textContent,'2');
  assert.equal(element.children[6].children.length,1);
  assert.equal(element.children[5].hidden,false);
  assert.ok(element.children[5].src.includes('/view?'));
});

test('old node is not modified and old browser API degrades safely',async()=>{
  const extension=await loadExtension();
  const old={comfyClass:'SmartSVGExpressV214'};
  extension.nodeCreated(old);
  assert.equal(old._smartsvgV215Dashboard,undefined);
  const modern={comfyClass:'SmartSVGExpressV215'};
  extension.nodeCreated(modern);
  assert.equal(modern._smartsvgV215Dashboard,undefined);
});
