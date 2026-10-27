import test from 'node:test';
import assert from 'node:assert/strict';
import {inspectCutSvg,selectedSvg,REVIEW_MESSAGES,CutReviewError}
  from '../web/js/smartsvg_cut_review_model_g27.mjs';
import {createCutReviewPanel}
  from '../web/js/smartsvg_cut_review_panel_g27.mjs';
const NS='http://www.w3.org/2000/svg';
const sample=(a='M1 1L10 1L10 10Z',b='M20 2L30 2L30 12Z')=>
  '<svg xmlns="'+NS+'" width="40mm" height="20mm" viewBox="0 0 40 20">'+
  '<path id="escargot1" d="'+a+'"/><path id="escargot2" d="'+b+'"/></svg>';
function xmlDocument(src){
  // Minimal deterministic DOMParser fixture: enough to exercise the validator
  // without depending on a browser library in public CPU CI.
  const rootTag=src.match(/^<svg\b([^>]*)>/)?.[1]||'';
  const attrs=text=>Array.from(text.matchAll(/([:\w-]+)="([^"]*)"/g))
    .map(([,name,value])=>({name,value,namespaceURI:name==='xmlns'?'http://www.w3.org/2000/xmlns/':null}));
  const obj=(tag,raw)=>{
    const at=attrs(raw);
    return {localName:tag,namespaceURI:NS,attributes:at,children:[],
      getAttribute:name=>at.find(a=>a.name===name)?.value||null};
  };
  const paths=Array.from(src.matchAll(/<(path|script|g|image)\b([^>]*)\/?>/g),m=>obj(m[1],m[2]));
  const root=obj('svg',rootTag);
  root.getElementsByTagName=()=>paths;
  return {documentElement:root};
}
const inspect=(src)=>inspectCutSvg(src,{parseXml:xmlDocument});

test('two editable contours are individually selectable and safely serialized',()=>{
  const v=inspect(sample());
  assert.equal(v.paths.length,2);
  assert.equal(v.width_mm,40);
  assert.deepEqual(v.viewBox,[0,0,40,20]);
  assert.equal(v.verified,false);
  const out=selectedSvg(v,[2]);
  assert.match(out,/width="40mm"/);
  assert.match(out,/id="contour-1"/);
  assert.match(out,/M20 2L30 2L30 12Z/);
  assert.doesNotMatch(out,/escargot1|M1 1L10/);
  assert.equal((out.match(/<path /g)||[]).length,1);
  assert.throws(()=>selectedSvg(v,[2,2]),/INVALID_SELECTION/);
  assert.throws(()=>selectedSvg(v,[]),/INVALID_SELECTION/);
});

test('rejects active XML, external content, transformations and unsupported geometry',()=>{
  for(const src of [
    '<!DOCTYPE svg [<!ENTITY x "evil">]>'+sample(),
    '<?xml-stylesheet href="https://example.invalid/x.css"?>'+sample(),
    sample().replace('<path', '<script/> <path'),
    sample().replace('id="escargot1"', 'transform="scale(100)"'),
    sample().replace('<path', '<image href="https://example.invalid/p.svg"/> <path'),
    sample().replace('40mm', '40px'),
    sample().replace('viewBox="0 0 40 20"', 'viewBox="0 0 40 60"'),
    sample('M1 1L10 1L10 10','M20 2L30 2L30 12Z'),
    sample('M1 1L10 1L10 10Z','M1 1L10 1L10 10Z').replace('id="escargot2"','id="escargot1"'),
    sample().replace('<path', '<rect width="100"/> <path'),
  ]){
    assert.throws(()=>inspect(src),CutReviewError,'bad SVG should not be considered as a cut-preview candidate');
  }
});
test('refuses oversize inputs, path injection, >64 contours and malformed attributes',()=>{
  assert.throws(()=>inspect('x'.repeat(800000)),/SVG_TOO_LARGE/);
  assert.throws(()=>inspect(sample('M0 0L1 1Z" onload="alert(1)','M1 1L2 2Z')),/UNSUPPORTED_SVG_ATTRIBUTE|UNSUPPORTED_PATH/);
  assert.throws(()=>inspect(sample().replace('M1 1L10 1L10 10Z','M0 0 L1e999 2 Z')),/INVALID_PATH_COORDINATE/);
  assert.throws(()=>selectedSvg({width_mm:40,height_mm:20,viewBox:[0,0,40,20],
    paths:[{d:'M0 0" onclick="evil()'}]},[1]),/UNSUPPORTED_PATH/);
  assert.ok(REVIEW_MESSAGES.UNSUPPORTED_SVG_ELEMENT.length>20);
});

class Element{
  constructor(tag){this.tagName=tag;this.children=[];this.attrs={};this.events={};
    this.type='';this.value='';this.disabled=false;this.hidden=false;this.className='';
    this.style={};this.files=[];this.checked=false;this.width=720;this.height=420;
    this.textContent='';this.id='';this.href='';this.download='';}
  append(...kids){this.children.push(...kids);}
  appendChild(kid){this.children.push(kid);}
  replaceChildren(...kids){this.children=[...kids];}
  setAttribute(k,v){this.attrs[k]=v;}
  addEventListener(type,fn){(this.events[type]??=[]).push(fn);}
  getContext(){return {setTransform(){},clearRect(){},fillRect(){},stroke(){},
    set fillStyle(x){},set strokeStyle(x){},set lineWidth(x){}};}
  async fire(k,evt={}){for(const fn of this.events[k]||[])await fn(evt);}
}
const walk=root=>[root,...root.children.flatMap(walk)];
test('local panel handles 2 subjects and never uploads a SVG or auto-queues ComfyUI',async()=>{
  globalThis.document={createElement:tag=>new Element(tag)};
  globalThis.Path2D=class{constructor(d){this.path=d;}};
  globalThis.DOMParser=class{parseFromString(xml){return xmlDocument(xml);}};
  const panel=createCutReviewPanel(33);
  const children=walk(panel),input=children.find(e=>e.type==='file');
  const canvas=children.find(e=>e.tagName==='canvas');
  const buttons=children.filter(e=>e.tagName==='button');
  assert.equal(input.id,'smartsvg-g27-svg-33');
  input.files=[{name:'escargots.svg',size:sample().length,text:async()=>sample()}];
  await input.fire('change');
  assert.equal(canvas.hidden,false);
  const checks=walk(panel).filter(e=>e.type==='checkbox');
  assert.equal(checks.length,2);
  assert.equal(checks.every(e=>e.checked),true);
  checks[0].checked=false;await checks[0].fire('change');
  assert.equal(walk(panel).filter(e=>e.type==='checkbox').filter(e=>e.checked).length,1);
  await buttons[1].fire('click');
  assert.equal(buttons[2].disabled,true,'no selection must disable local download');
  assert.equal(panel.attrs['aria-label'],'Aperçu et choix manuel des chemins de découpe');
  assert.match(walk(panel).map(x=>x.textContent).join(' '),/aucune certification de découpe/);
});
test('older async SVG read cannot overwrite a newer file choice',async()=>{
  globalThis.document={createElement:tag=>new Element(tag)};
  globalThis.DOMParser=class{parseFromString(xml){return xmlDocument(xml);}};
  globalThis.Path2D=class{};
  const panel=createCutReviewPanel('stale'),input=walk(panel).find(e=>e.type==='file');
  let finish;
  const old=new Promise(resolve=>finish=resolve);
  input.files=[{name:'old.svg',size:300,text:()=>old}];
  const pending=input.fire('change');
  input.files=[{name:'new.svg',size:300,text:async()=>sample()}];
  await input.fire('change');
  finish(sample('M0 0L2 2Z','M3 3L4 4Z'));
  await pending;
  assert.match(walk(panel).find(e=>e.attrs.role==='status').textContent,/2\/2 contour/);
});
