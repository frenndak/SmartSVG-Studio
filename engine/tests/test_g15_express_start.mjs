import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {EXPRESS_CLASS,PROFILES,getProfile,applyProfile,chosenProfile,explainFailure} from '../web/js/smartsvg_express_start_model_g15.mjs';

const root=path.dirname(fileURLToPath(import.meta.url));
const presets=[
  'Auto - conserver le visuel','Sticker - contour du sujet',
  'Planche - 24 images (6x4)','Planche - 12 images (4x3)',
  'Carte - visuel rectangulaire'
];
function node(){
  return {comfyClass:EXPRESS_CLASS,id:9,widgets:[
    {name:'dossier_sortie',value:'C:/Users/Test/Exports'},
    {name:'projet',value:presets[0],options:{values:[...presets]}},
    {name:'largeur_mm',value:40},{name:'qualite_ppp',value:'300'},
    {name:'ia_locale',value:'Desactivee'}
  ],inputs:[{name:'image',link:21},{name:'masques_objets',link:72}]};
}
test('task choices map exactly to the five historical options',()=>{
  assert.equal(PROFILES.length,5);
  assert.deepEqual(new Set(PROFILES.map(p=>p.project)),new Set(presets));
  assert.equal(new Set(PROFILES.map(p=>p.id)).size,5);
  for (const p of PROFILES) {
    assert.ok(p.help.length>30);
    assert.match(p.next,/Design Space|vérifier|Vérifier/);
    assert.equal(getProfile(p.id),p);
  }
  assert.equal(getProfile('unknown'),null);
});
test('profiles only update projet, without touching import links, AI, size or output path',()=>{
  const n=node(),before=JSON.stringify(n.inputs);
  for(const id of ['sticker','sheet12','sheet24','card','auto']){
    const result=applyProfile(n,id);
    assert.equal(result.ok,true);
    assert.equal(n.widgets.find(w=>w.name==='projet').value,getProfile(id).project);
    assert.equal(n.widgets.find(w=>w.name==='largeur_mm').value,40);
    assert.equal(n.widgets.find(w=>w.name==='ia_locale').value,'Desactivee');
    assert.equal(n.widgets.find(w=>w.name==='dossier_sortie').value,'C:/Users/Test/Exports');
    assert.equal(JSON.stringify(n.inputs),before);
    assert.equal(chosenProfile(n).id,id);
  }
});
test('idempotent preset does not callback or mark graph dirty',()=>{
  const n=node();let calls=0;
  n.widgets[1].callback=()=>calls++;
  let dirty=0;n.setDirtyCanvas=()=>dirty++;
  const result=applyProfile(n,'auto');
  assert.equal(result.ok,true);assert.equal(result.changed,false);
  assert.equal(calls,0);assert.equal(dirty,0);
});
test('wrong legacy node IDs and missing option metadata fail closed',()=>{
  const n=node();
  n.comfyClass='SmartSVGExpressV211';
  assert.equal(applyProfile(n,'sticker').reason,'NOEUD_NON_COMPATIBLE');
  n.comfyClass=EXPRESS_CLASS;
  n.widgets[1].options={values:['arbitrary']};
  assert.equal(applyProfile(n,'sticker').reason,'OPTIONS_INCOMPATIBLES');
  assert.equal(n.widgets[1].value,presets[0]);
  assert.equal(applyProfile(n,'nonsense').reason,'CHOIX_INCONNU');
});
test('rejected widget callbacks restore original choice',()=>{
  const n=node(),widget=n.widgets[1];
  widget.callback=()=>{throw Error('frontend refused')};
  assert.equal(applyProfile(n,'sheet12').reason,'MISE_A_JOUR_REFUSEE');
  assert.equal(widget.value,presets[0]);
  assert.match(explainFailure('MISE_A_JOUR_REFUSEE'),/conservés/);
});

class Element {
  constructor(tag){
    this.tagName=tag;this.children=[];this.value='';this.dataset={};this.events={};
    this.textContent='';this.options={};this.attributes={};this.style={};this.disabled=false;this.hidden=false;this.src='';
  }
  append(...parts){this.children.push(...parts);if(this.tagName==='select' && !this.value && this.children.length)this.value=this.children[0].value;}
  appendChild(part){this.append(part);return part;}
  replaceChildren(...parts){this.children=[...parts];}
  removeAttribute(name){delete this.attributes[name];if(name==='src')this.src='';}
  setAttribute(name,value){this.attributes[name]=value;}
  addEventListener(name,handler){this.events[name]=handler;}
  query() {return this.children;}
  invoke(name) {this.events[name]?.({target:this});}
}
function flatten(el){return [el,...el.children.flatMap(flatten)]}
let serial=0;
async function extension(){
  let ext=null;
  globalThis.__ssApp={registerExtension(x){ext=x;}};
  globalThis.__ssModel={EXPRESS_CLASS,PROFILES,getProfile,chosenProfile,applyProfile,explainFailure};
  globalThis.__ssApi={apiURL:route=>'/comfy'+route};
  globalThis.__ssGuide={evaluateOutput:()=>({state:'EMPTY'}),emptyState:()=>({state:'EMPTY',report:null,previews:[],action:'',explanation:''}),statusForDisplay:()=>'',STATES:{}};
  globalThis.__ssPreviewUrl=()=>null;
  const head=new Element('head');
  globalThis.document={head,getElementById:()=>null,createElement:t=>new Element(t)};
  let code=fs.readFileSync(path.join(root,'../web/js/smartsvg_express_start_g15.js'),'utf8');
  code=code.replace('import { app } from "../../scripts/app.js";','const app=globalThis.__ssApp;');
  code=code.replace('import { api } from "../../scripts/api.js";','const api=globalThis.__ssApi;');
  code=code.replace('import { evaluateOutput, emptyState, statusForDisplay, STATES } from "./smartsvg_guide_model_g21.mjs";',
                    'const {evaluateOutput,emptyState,statusForDisplay,STATES}=globalThis.__ssGuide;');
  code=code.replace('import { previewUrl } from "./smartsvg_ui_model_v2151.mjs";',
                    'const previewUrl=globalThis.__ssPreviewUrl;');
  code=code.replace(/import \{ EXPRESS_CLASS, PROFILES, getProfile, chosenProfile,\s*applyProfile, explainFailure \} from "\.\/smartsvg_express_start_model_g15\.mjs";/,
                    'const {EXPRESS_CLASS,PROFILES,getProfile,chosenProfile,applyProfile,explainFailure}=globalThis.__ssModel;');
  await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64')+'#'+(++serial));
  assert.ok(ext);
  return ext;
}
test('frontend node widget does not serialize, remains keyboard accessible, and updates actual widget',async()=>{
  const ext=await extension(),n=node();
  n.addDOMWidget=function(name,type,ui,options){this.extra={name,type,ui,options};return this.extra;};
  ext.nodeCreated(n);
  assert.ok(n.extra);assert.equal(n.extra.options.serialize,false);
  const all=flatten(n.extra.ui);
  const s=all.find(e=>e.tagName==='select'),b=all.find(e=>e.tagName==='button');
  assert.ok(s);assert.ok(b);assert.equal(b.type,'button');
  assert.equal(all.some(e=>e.attributes.role==='status' && e.attributes['aria-live']==='polite'),true);
  assert.equal(s.value,'auto');
  s.value='sheet12';s.invoke('change');
  b.invoke('click');
  assert.equal(n.widgets[1].value,'Planche - 12 images (4x3)');
  assert.equal(n.extra.serialize,false);
  assert.equal(n._smartsvgG15Starter,n.extra.ui);
  ext.nodeCreated(n);assert.equal(n.extra.ui,n._smartsvgG15Starter);
});
test('unrelated nodes or frontends without DOM widgets are not touched',async()=>{
  const ext=await extension();
  const old={comfyClass:'SmartSVGExpressV211',addDOMWidget(){throw Error('must not call')}};
  ext.nodeCreated(old);assert.equal(old._smartsvgG15Starter,undefined);
  const bare={comfyClass:EXPRESS_CLASS};ext.nodeCreated(bare);
  assert.equal(bare._smartsvgG15Starter,undefined);
});
test('frontend has no direct export or unsafe browser code paths',()=>{
  const code=fs.readFileSync(path.join(root,'../web/js/smartsvg_express_start_g15.js'),'utf8');
  assert.doesNotMatch(code,/innerHTML|outerHTML|eval\(|new Function\(|fetch\(|localStorage|sessionStorage|queuePrompt|app\.queue/);
  assert.match(code,/serialize:false/);
  assert.match(code,/role','status/);
});
