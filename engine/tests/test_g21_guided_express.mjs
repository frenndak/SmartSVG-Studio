import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as guide from '../web/js/smartsvg_guide_model_g21.mjs';
import * as starter from '../web/js/smartsvg_express_start_model_g15.mjs';
import {previewUrl} from '../web/js/smartsvg_ui_model_v2151.mjs';

const root=path.dirname(fileURLToPath(import.meta.url));
const options=starter.PROFILES.map(p=>p.project);
const image={filename:'qa_global_12345678901234.png',subfolder:'SmartSVG_Studio_Previews',type:'output'};
function output(state='REVIEW_REQUIRED',count=12) {
  return {smartsvg:[{
    etat_prevol:state,controle_qualite_disponible:true,
    objets_total:count,alertes_total:2,planches_total:1,
    action_requise:'Vérifier les contours avant découpe.',
    provenance:'Masques détectés sans IA',chemin_sortie:'/tmp/smartsvg-exports',
    objets:[{numero:1,largeur_mm:40,etat:'A_VERIFIER',nombre_alertes:1,
      alertes:['La marge doit être vérifiée']}]
  }],smartsvg_previews:[image]};
}
function node(){
  return {comfyClass:starter.EXPRESS_CLASS,id:24,size:[350,220],
    widgets:[{name:'projet',value:options[0],options:{values:[...options]}},
      {name:'largeur_mm',value:40},{name:'ia_locale',value:'Desactivee'},
      {name:'dossier_sortie',value:'C:/Out'}],
    inputs:[{name:'image',link:23},{name:'masques_objets',link:null}],
    setDirtyCanvas(){}};
}
test('missing or malformed report fails closed, never certifies a cut',()=>{
  for(const item of [{},{smartsvg:[{}]},
    {smartsvg:[{etat_prevol:'PASS',objets_total:12,action_requise:'OK',controle_qualite_disponible:true}]},
    {smartsvg:[{etat_prevol:'REVIEW_REQUIRED',objets_total:12,action_requise:'OK'}]},
    {smartsvg:[{etat_prevol:'REVIEW_REQUIRED',objets_total:0,action_requise:'OK',controle_qualite_disponible:true}]}]){
    const state=guide.evaluateOutput(item);
    assert.equal(state.state,'INVALID');
    assert.equal(state.report,null);
    assert.equal(state.previews.length,0);
    assert.equal(state.mayCopy,false);
    assert.equal(state.verifiedPhysicalCut,false);
  }
});
test('blocked QA is never upgraded based on candidate silhouettes',()=>{
  const result=guide.evaluateOutput(output('BLOCKED'));
  assert.equal(result.state,'BLOCKED');
  assert.match(result.explanation,/bloqué/i);
  assert.equal(result.verifiedPhysicalCut,false);
  assert.equal(result.previews.length,1);
  assert.equal(result.mayCopy,true); // debug only
});
test('plausible candidates remain REVIEW, never machine-ready',()=>{
  const result=guide.evaluateOutput(output());
  assert.equal(result.state,'REVIEW');
  assert.match(result.action,/Vérifier/);
  assert.equal(result.report.objets_total,12);
  assert.equal(result.report.objets.length,1);
  assert.equal(result.verifiedPhysicalCut,false);
});
test('wrong 12 / 24 subject count forces BLOCKED even when engine says review',()=>{
  for(const expectedObjects of [12,24]){
    const result=guide.evaluateOutput(output('REVIEW_REQUIRED',expectedObjects-1),{expectedObjects});
    assert.equal(result.state,'BLOCKED');
    assert.match(result.explanation,/incohérent/i);
  }
});
test('changing profile invalidates the previous execution and hides file location',()=>{
  const result=guide.evaluateOutput(output(),{
    projectAtRun:options[1],currentProject:options[2]
  });
  assert.equal(result.state,'STALE');
  assert.equal(result.report,null);
  assert.equal(result.mayCopy,false);
  assert.equal(result.previews.length,0);
});
test('malicious preview URI fails reference filter',()=>{
  const malicious={...image,filename:'../../secrets.png'};
  const data=output();data.smartsvg_previews=[malicious];
  const result=guide.evaluateOutput(data);
  assert.equal(result.previews.length,0);
  assert.equal(previewUrl(malicious,'https://host/comfy','/comfy/view'),null);
});
test('pure state text is always conservative',()=>{
  for(const value of Object.values(guide.STATES)){
    assert.ok(guide.statusForDisplay(value).length>8);
    assert.notEqual(guide.statusForDisplay(value),'PRÊT POUR CRICUT');
  }
  assert.equal(guide.emptyState().verifiedPhysicalCut,false);
});

class El {
  constructor(tag){
    this.tagName=tag;this.children=[];this.dataset={};this.attrs={};
    this.textContent='';this.className='';this.value='';this.hidden=false;
    this.style={};this.events={};this.disabled=false;this.src='';
  }
  append(...items){
    this.children.push(...items);
    if(this.tagName==='select'&&!this.value&&this.children[0])this.value=this.children[0].value;
  }
  appendChild(x){this.append(x);return x;}
  replaceChildren(...items){this.children=[...items];}
  removeAttribute(name){delete this.attrs[name];if(name==='src')this.src='';}
  setAttribute(key,value){this.attrs[key]=String(value);}
  addEventListener(type,cb){(this.events[type]??=[]).push(cb);}
  fire(type){for(const handler of this.events[type]||[])handler({target:this});}
}
function elements(element){return [element,...element.children.flatMap(elements)]}
let sequence=0;
async function loadExtension() {
  let registered;
  globalThis.__ssApp={registerExtension(ext){registered=ext;}};
  globalThis.__ssApi={apiURL:p=>'/proxy/8188'+p};
  globalThis.__ssModel=starter;
  globalThis.__ssGuide=guide;
  globalThis.__ssPreviewUrl=previewUrl;
  globalThis.document={head:new El('head'),getElementById:()=>null,createElement:name=>new El(name)};
  globalThis.window={location:{href:'https://host.example/proxy/8188/'}};
  Object.defineProperty(globalThis,'navigator',
    {value:{clipboard:{writeText:async v=>{globalThis.__lastCopied=v;}}},
      configurable:true});
  let code=fs.readFileSync(path.join(root,'../web/js/smartsvg_express_start_g15.js'),'utf8');
  code=code.replace('import { app } from "../../scripts/app.js";','const app=globalThis.__ssApp;')
    .replace('import { api } from "../../scripts/api.js";','const api=globalThis.__ssApi;')
    .replace(/import \{ EXPRESS_CLASS, PROFILES, getProfile, chosenProfile,\s*applyProfile, explainFailure \} from "\.\/smartsvg_express_start_model_g15\.mjs";/,
      'const {EXPRESS_CLASS,PROFILES,getProfile,chosenProfile,applyProfile,explainFailure}=globalThis.__ssModel;')
    .replace('import { evaluateOutput, emptyState, statusForDisplay, STATES } from "./smartsvg_guide_model_g21.mjs";',
      'const {evaluateOutput,emptyState,statusForDisplay,STATES}=globalThis.__ssGuide;')
    .replace('import { previewUrl } from "./smartsvg_ui_model_v2151.mjs";',
      'const previewUrl=globalThis.__ssPreviewUrl;');
  await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64')+'#'+(++sequence));
  assert.ok(registered);
  return registered;
}
test('unified ComfyUI panel renders real review then clears on stale settings and bad report',async()=>{
  const extension=await loadExtension(),n=node();
  n.addDOMWidget=function(name,type,ui,options){
    this.widget={name,type,root:ui,options};return this.widget;
  };
  let callbacks=0;n.onExecuted=()=>{callbacks++;};
  extension.nodeCreated(n);
  assert.equal(n.widget.options.serialize,false);
  assert.equal(n.widget.serialize,false);
  const root=n.widget.root,all=elements(root);
  const select=all.find(x=>x.tagName==='select');
  const apply=all.find(x=>x.tagName==='button');
  const result=all.find(x=>x.attrs['aria-label']==='Contrôle du dernier traitement SmartSVG');
  assert.ok(select&&apply&&result);
  assert.equal(result.dataset.state,'EMPTY');
  assert.equal(all.some(x=>x.attrs['aria-live']==='polite'),true);
  assert.ok(root.attrs.role==='region');
  assert.ok(root.children.length<14);
  const source=output('REVIEW_REQUIRED',12);
  n.widgets[0].value=starter.getProfile('sheet12').project; // choose 12-sheet BEFORE run
  n.onExecuted(source);
  assert.equal(callbacks,1);
  assert.equal(result.dataset.state,'REVIEW');
  const preview=elements(result).find(x=>x.tagName==='img');
  assert.match(preview.src,/\/proxy\/8188\/view\?/);
  assert.equal(preview.hidden,false);
  assert.equal(elements(result).some(x=>x.textContent.includes('Aucun résultat vérifié')),false);
  select.value='sheet24';select.fire('change');apply.fire('click');
  assert.equal(n.widgets[0].value,options[2]);
  assert.equal(result.dataset.state,'STALE');
  assert.equal(preview.hidden,true);
  n.onExecuted({});
  assert.equal(result.dataset.state,'INVALID');
  assert.equal(preview.src,'');
  assert.equal(callbacks,2);
});
test('blocked output on sheet with missing subject count remains blocked',async()=>{
  const extension=await loadExtension(),n=node();
  n.widgets[0].value=options[2]; // 24 subjects
  n.addDOMWidget=function(a,b,c,d){this.widget={root:c,options:d};return this.widget;};
  extension.nodeCreated(n);
  n.onExecuted(output('REVIEW_REQUIRED',12));
  const result=elements(n.widget.root).find(x=>x.attrs['aria-label']==='Contrôle du dernier traitement SmartSVG');
  assert.equal(result.dataset.state,'BLOCKED');
  assert.equal(elements(result).some(x=>String(x.textContent).includes('incohérent')),true);
});
test('legacy dashboard no longer stacks on V21.15.2',()=>{
  const old=fs.readFileSync(path.join(root,'../web/js/smartsvg_ui_v2151.js'),'utf8');
  assert.match(old,/new Set\(\["SmartSVGExpressV2151"\]\)/);
  assert.doesNotMatch(old,/new Set\(\["SmartSVGExpressV2151", "SmartSVGExpressV21152"\]\)/);
});
test('guide never uses unsafe insertion, local file APIs or queue shortcuts',()=>{
  const src=fs.readFileSync(path.join(root,'../web/js/smartsvg_express_start_g15.js'),'utf8');
  assert.doesNotMatch(src,/innerHTML|outerHTML|eval\(|new Function\(|fetch\(|localStorage|sessionStorage|queuePrompt|app\.queue|window\.open/);
  assert.match(src,/serialize:false/);
  assert.match(src,/api\.apiURL\('\/view'\)/);
});
