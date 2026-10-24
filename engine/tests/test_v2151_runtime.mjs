import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as model from '../web/js/smartsvg_ui_model_v2151.mjs';
const root=path.dirname(fileURLToPath(import.meta.url));

class StubElement {
  constructor(tag) {
    this.tagName=tag;this.children=[];this.dataset={};this.hidden=false;
    this.className='';this.textContent='';this.style={};this.attributes=new Map();
    this.classList={toggle(){}};this.events=new Map();this.src='';
  }
  append(...items){this.children.push(...items);}
  appendChild(item){this.children.push(item);return item;}
  replaceChildren(...items){this.children=[...items];}
  setAttribute(k,v){this.attributes.set(k,String(v));}
  removeAttribute(k){this.attributes.delete(k);if(k==='src')this.src='';}
  addEventListener(k,fn){this.events.set(k,fn);}
}
let serial=0;
async function extension() {
  let registered=null;
  globalThis.__mockApp={registerExtension(ext){registered=ext;}};
  globalThis.__mockApi={apiURL(path){return '/proxy/8188'+path;}};
  globalThis.__smartsvgModel=model;
  globalThis.window={location:{href:'https://example.org/proxy/8188/'}};
  Object.defineProperty(globalThis,'navigator',{value:{clipboard:{writeText:async value=>value}},configurable:true});
  const head=new StubElement('head');
  globalThis.document={head,getElementById:()=>null,createElement:name=>new StubElement(name)};
  let code=fs.readFileSync(path.join(root,'../web/js/smartsvg_ui_v2151.js'),'utf8');
  code=code.replace('import { app } from "../../scripts/app.js";','const app=globalThis.__mockApp;');
  code=code.replace('import { api } from "../../scripts/api.js";','const api=globalThis.__mockApi;');
  code=code.replace('import { normalizePayload, normalizePreviews, previewUrl } from "./smartsvg_ui_model_v2151.mjs";',
     'const { normalizePayload, normalizePreviews, previewUrl }=globalThis.__smartsvgModel;');
  await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64')+'#run='+String(++serial));
  assert.ok(registered);
  return registered;
}
test('v2151 dashboard proxy-safe preview, lifecycle, and serialisation',async()=>{
  const ext=await extension();
  const node={comfyClass:'SmartSVGExpressV2151',size:[240,100],addDOMWidget(name,type,el,opts){
    this.widget={name,type,root:el,options:opts};return this.widget;
  }};
  ext.nodeCreated(node);
  assert.equal(node.widget.serialize,false);
  assert.equal(node.widget.options.serialize,false);
  assert.ok(node.size[1]>=530);
  const out={smartsvg:[{objets_total:24,planches_total:2,alertes_total:0,
      provenance:'provenance verifiee',action_requise:'Verifier manuellement',
      objets:[{numero:1,largeur_mm:32,etat:'A_VERIFIER',alertes:[],nombre_alertes:0}]}],
    smartsvg_previews:[{filename:'qa_global_12345678901234.png',subfolder:'SmartSVG_Studio_Previews',type:'output'}]};
  node.onExecuted(out);
  const el=node.widget.root;
  const counters=el.children[3];
  assert.equal(counters.children[0].children[0].textContent,'24');
  assert.match(el.children[5].src,/\/proxy\/8188\/view\?/);
  assert.equal(el.children[5].hidden,false);
  node.onExecuted({});
  assert.equal(counters.children[0].children[0].textContent,'—');
  assert.equal(el.children[5].hidden,true);
  assert.equal(el.children[6].children.length,0);
  assert.equal(el.children[4].children.length,0);
});
test('old V21.5 nodes not touched by new frontend',async()=>{
  const ext=await extension();
  const old={comfyClass:'SmartSVGExpressV215'};
  ext.nodeCreated(old);
  assert.equal(old._smartsvgV2151Dashboard,undefined);
});
test('modern frontend without DOM widget degrades without throwing',async()=>{
  const ext=await extension();
  ext.nodeCreated({comfyClass:'SmartSVGExpressV2151'});
});
