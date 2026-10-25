import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {STEPS,expressStep,projectReadiness,screenMode}
  from '../web/js/smartsvg_express_ux_g25.mjs';
import {createProjectPanel} from '../web/js/smartsvg_project_panel_g22.mjs';

const F='a'.repeat(64), G='b'.repeat(64);
function project(mask=null,strokes=null){
  return {status:'PROJECT_HEALTHY',name:'escargots',sha256:F,
    document:{width_mm:40,dpi:300,notes:'Garder les contours'},
    ...(mask?{base_masks:mask}:{}),...(strokes?{editor_session:strokes}:{})};
}
const mask={exact_float32:true,count:12,editor_fingerprint:F};
const strokes={available:true,count:12,source_fingerprint:F,stroke_count:8};

test('four distinct steps and actionable guidance, no fabricated auto-execution',()=>{
  assert.deepEqual(STEPS.map(s=>s.id),['SOURCE','PROFILE','RUN','CHECK']);
  assert.equal(expressStep({}).index,0);
  assert.equal(expressStep({imageConnected:true}).index,1);
  assert.equal(expressStep({imageConnected:true,profileApplied:true}).index,2);
  assert.equal(expressStep({imageConnected:true,profileApplied:true,loading:true}).state,'LOADING');
  assert.equal(expressStep({imageConnected:true,profileApplied:true,resultState:'STALE'}).index,2);
  for(const state of ['BLOCKED','REVIEW','INVALID']){
    const s=expressStep({imageConnected:true,profileApplied:true,resultState:state});
    assert.equal(s.index,3);
    assert.notEqual(s.state,'READY_TO_CUT');
  }
});
test('layout model covers desktop targets and invalid dimensions',()=>{
  assert.equal(screenMode(1366,768),'compact');
  assert.equal(screenMode(1920,1080),'comfortable');
  assert.equal(screenMode(420,780),'compact');
  assert.equal(screenMode(NaN,1080),'compact');
});
test('project state requires actual masks and fingerprint matching',()=>{
  assert.equal(projectReadiness(null).state,'MISSING');
  assert.equal(projectReadiness({status:'PROJECT_RECOVERABLE'}).state,'RECOVERABLE');
  assert.equal(projectReadiness({status:'PROJECT_CORRUPT'}).state,'ERROR');
  assert.equal(projectReadiness(project()).state,'SOURCE_ONLY');
  assert.equal(projectReadiness(project(null,strokes)).state,'STROKES_ONLY');
  assert.equal(projectReadiness(project(mask)).state,'MASKS_ONLY');
  assert.equal(projectReadiness(project(mask,strokes)).state,'RESTORABLE_MANUALLY');
  assert.equal(projectReadiness(project(mask,{...strokes,count:24})).state,'CONFLICT');
  assert.equal(projectReadiness(project(mask,{...strokes,source_fingerprint:G})).state,'CONFLICT');
  assert.equal(projectReadiness(project({...mask,exact_float32:false},strokes)).state,'ERROR');
  assert.equal(projectReadiness(project({...mask,editor_fingerprint:'invalid'},strokes)).state,'ERROR');
});
test('no project status claims physical Cricut cut or automatic graph restoration',()=>{
  for(const p of [null,project(),project(mask),project(mask,strokes),
                    {status:'PROJECT_RECOVERABLE'},project(mask,{...strokes,count:20})]){
    const r=projectReadiness(p);
    assert.doesNotMatch(r.title,/prêt.*Cricut|découpe certifiée/i);
    assert.ok(r.detail.length>20);
  }
});

class Element {
  constructor(tag){this.tagName=tag;this.children=[];this.textContent='';this.attrs={};
    this.value='';this.disabled=false;this.hidden=false;this.src='';this.events={};
    this.type='';this.files=[];this.className='';this.dataset={};}
  append(...items){this.children.push(...items);if(this.tagName==='select'&&!this.value&&this.children[0])this.value=this.children[0].value;}
  appendChild(x){this.children.push(x);return x;}
  addEventListener(k,callback){(this.events[k]??=[]).push(callback);}
  setAttribute(k,v){this.attrs[k]=v;}
  removeAttribute(k){delete this.attrs[k];if(k==='src')this.src='';}
  async fire(k){for(const fn of this.events[k]||[])await fn({target:this});}
}
const descendants=e=>[e,...e.children.flatMap(descendants)];
test('panel displays accurate project readiness, cannot send concurrent inspection requests',async()=>{
  globalThis.document={createElement:tag=>new Element(tag)};
  const calls=[];
  let release;
  const gate=new Promise(resolve=>release=resolve);
  const api={
    apiURL:x=>'/proxy/8188'+x,
    async fetchApi(url,opts){
      calls.push(url);
      await gate;
      return {ok:true,json:async()=>({ok:true,project:project(mask,strokes)})};
    }
  };
  const ui=createProjectPanel(api,()=>({profile:'Sticker - contour du sujet',
                                     width_mm:40,dpi:300}),55);
  const elements=descendants(ui);
  const input=elements.find(e=>e.tagName==='input'&&e.type==='text');
  const buttons=elements.filter(e=>e.tagName==='button');
  assert.equal(input.id,'smartsvg-g22-name-55');
  input.value='escargots';
  const pending=buttons[1].fire('click');
  assert.equal(ui.attrs['aria-busy'],'true');
  assert.ok(buttons.every(x=>x.disabled));
  await buttons[1].fire('click'); // deliberately forced event while disabled
  assert.equal(calls.length,1);
  release();
  await pending;
  assert.equal(ui.attrs['aria-busy'],'false');
  const contents=elements.map(x=>String(x.textContent)).join(' ');
  assert.match(contents,/Source, masques et traits cohérents/);
  assert.match(contents,/ne se reconnecte pas automatiquement/);
  assert.equal(buttons[2].disabled,false);
  assert.equal(buttons[3].disabled,true);
});
test('stale project selection invalidates controls and disallows last-project writes',async()=>{
  globalThis.document={createElement:tag=>new Element(tag)};
  const api={apiURL:x=>x,
    fetchApi:async()=>({ok:true,json:async()=>({ok:true,project:project(mask,strokes)})})};
  const ui=createProjectPanel(api,()=>({profile:'Auto - conserver le visuel',
                                    width_mm:40,dpi:300}),99);
  const nodes=descendants(ui), input=nodes.find(e=>e.type==='text'),
        buttons=nodes.filter(e=>e.tagName==='button');
  input.value='escargots';await buttons[1].fire('click');
  assert.equal(buttons[2].disabled,false);
  input.value='autre';await input.fire('input');
  assert.equal(buttons[2].disabled,true);
  assert.equal(buttons[3].disabled,true);
});
test('G2.5 has real semantic disclosure and responsive CSS without fake export control',()=>{
  const src=fs.readFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)),
        '../web/js/smartsvg_express_start_g15.js'),'utf8');
  assert.match(src,/e\('details','details'\)/);
  assert.match(src,/e\('summary'/);
  assert.match(src,/72dvh/);
  assert.match(src,/max-height:800px/);
  assert.match(src,/aria-current/);
  assert.doesNotMatch(src,/queuePrompt|app\.queuePrompt|innerHTML/);
});


test('actual Express panel updates 4-step guidance when IMAGE link changes before execution',async()=>{
  const {default:fs2}=await import('node:fs');
  const presets=await import('../web/js/smartsvg_express_start_model_g15.mjs');
  const guide=await import('../web/js/smartsvg_guide_model_g21.mjs');
  const ux=await import('../web/js/smartsvg_express_ux_g25.mjs');
  const {previewUrl}=await import('../web/js/smartsvg_ui_model_v2151.mjs');
  let extension=null;
  globalThis.__ssApp={registerExtension:e=>{extension=e;}};
  globalThis.__ssApi={apiURL:path=>'/proxy/8188'+path};
  globalThis.__ssModel=presets;
  globalThis.__ssGuide=guide;
  globalThis.__ssPreviewUrl=previewUrl;
  globalThis.__ssProjectPanel={createProjectPanel:()=>new Element('section')};
  globalThis.__ssUx=ux;
  globalThis.window={innerWidth:1366,innerHeight:768,
    location:{href:'https://example.invalid/proxy/8188/'}};
  globalThis.document={
    head:new Element('head'),getElementById:()=>null,
    createElement:tag=>new Element(tag)
  };
  let source=fs2.readFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)),
    '../web/js/smartsvg_express_start_g15.js'),'utf8');
  source=source.replace('import { app } from "../../scripts/app.js";',
    'const app=globalThis.__ssApp;');
  source=source.replace('import { api } from "../../scripts/api.js";',
    'const api=globalThis.__ssApi;');
  source=source.replace(/import \{ EXPRESS_CLASS, PROFILES, getProfile, chosenProfile,\s*applyProfile, explainFailure \} from "\.\/smartsvg_express_start_model_g15\.mjs";/,
    'const {EXPRESS_CLASS,PROFILES,getProfile,chosenProfile,applyProfile,explainFailure}=globalThis.__ssModel;');
  source=source.replace('import { evaluateOutput, emptyState, statusForDisplay, STATES, configurationSignature } from "./smartsvg_guide_model_g21.mjs";',
    'const {evaluateOutput,emptyState,statusForDisplay,STATES,configurationSignature}=globalThis.__ssGuide;');
  source=source.replace('import { previewUrl } from "./smartsvg_ui_model_v2151.mjs";',
    'const previewUrl=globalThis.__ssPreviewUrl;');
  source=source.replace('import { createProjectPanel } from "./smartsvg_project_panel_g22.mjs";',
    'const {createProjectPanel}=globalThis.__ssProjectPanel;');
  source=source.replace('import { STEPS, expressStep, screenMode } from "./smartsvg_express_ux_g25.mjs";',
    'const {STEPS,expressStep,screenMode}=globalThis.__ssUx;');
  await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64')+'#g25');
  assert.ok(extension);
  const node={
    comfyClass:presets.EXPRESS_CLASS,id:25,size:[420,480],
    widgets:[{name:'projet',value:presets.getProfile('auto').project,
      options:{values:presets.PROFILES.map(p=>p.project)}}],
    inputs:[{name:'image',link:null},{name:'masques_objets',link:null}],
    setDirtyCanvas(){this.repaintCount=(this.repaintCount||0)+1;},
    addDOMWidget(name,type,root,options){
      this.ui=root;return {name,type,options};
    },
  };
  extension.nodeCreated(node);
  assert.ok(node.ui);
  assert.equal(node.ui.dataset.screen,'compact');
  const steps=descendants(node.ui).find(el=>el.className==='steps');
  assert.equal(steps.children[0].attrs['aria-current'],'step');
  const before=node.repaintCount;
  node.inputs[0].link=33;
  node.onDrawForeground();
  assert.equal(steps.children[2].attrs['aria-current'],'step');
  const refreshed=node.repaintCount;
  assert.ok(refreshed>before);
  node.onDrawForeground();
  assert.equal(node.repaintCount,refreshed,'unchanged signature must not redraw repeatedly');
  const selected=descendants(node.ui).find(el=>el.tagName==='select');
  selected.value='sticker';await selected.fire('change');
  assert.equal(steps.children[1].attrs['aria-current'],'step');
  const apply=descendants(node.ui).find(el=>el.tagName==='button');
  await apply.fire('click');
  assert.equal(steps.children[2].attrs['aria-current'],'step');
  node.onExecuted({});
  assert.equal(steps.children[3].attrs['aria-current'],'step');
  assert.equal(descendants(node.ui).some(el=>el.textContent.includes('aucune validation Cricut')),true);
});
