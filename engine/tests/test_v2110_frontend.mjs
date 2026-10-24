import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as model from '../web/js/smartsvg_unified_model_v2110.mjs';
const root=path.dirname(fileURLToPath(import.meta.url));
const token='f'.repeat(24);
const ref=s=>({filename:`ni_${token}_${s}.png`,subfolder:'SmartSVG_Studio_Native_V219',type:'output'});
const source='a'.repeat(64);
const sample={smartsvg_unified:[{
 version:1,width:180,height:120,count:2,source,quality:'a_verifier',image:ref('image'),
 masks:[ref('mask00'),ref('mask01')],objects:[
 {objet:1,etat:'a_verifier',alertes:['BORD_IMAGE'],points:[{x:90,y:50,type:'BORD_IMAGE',detail:'Vérifier',priorite:1}]},
 {objet:2,etat:'ok',alertes:[],points:[]},
 ]}]};
const m=sample.smartsvg_unified[0];

class Context{static readbacks=0;setTransform(){}clearRect(){}drawImage(){}beginPath(){}moveTo(){}lineTo(){}stroke(){}arc(){}fill(){}fillRect(){}fillText(){}save(){}restore(){}
 getImageData(_x,_y,w,h){Context.readbacks++;return {data:new Uint8ClampedArray(w*h*4)};}putImageData(){} }
class Dom{
 constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.events={};this.style={};this.attrs={};this.disabled=false;this.value='';this.ctx=new Context();this.classList={toggle(){}};}
 set textContent(t){this.txt=String(t);this.children=[];}get textContent(){return this.txt||'';}
 append(...x){this.children.push(...x);}appendChild(x){this.children.push(x);return x;}
 replaceChildren(...x){this.children=[...x];}addEventListener(k,f){this.events[k]=f;}removeEventListener(k){delete this.events[k];}
 setAttribute(k,v){this.attrs[k]=v;}getBoundingClientRect(){return {left:0,top:0,width:700,height:450};}
 getContext(){return this.ctx;}setPointerCapture(){}focus(){}remove(){this.removed=true;}
 click(){this.fire('click');}fire(name,e={}){this.events[name]?.(e);}
}
class FakeImage{
 naturalWidth=180;naturalHeight=120;
 set src(url){this.url=url;queueMicrotask(()=>this.onload?.());}
}
async function install(){
 let extension;let style=null;
 globalThis.__app={registerExtension(v){extension=v;},graph:{change(){}}};
 globalThis.__api={apiURL(path){return '/proxy/8188'+path;}};
 globalThis.__model=model;
 globalThis.window={location:{href:'https://test.example/proxy/8188/'},devicePixelRatio:1};
 globalThis.Image=FakeImage;
 globalThis.requestAnimationFrame=fn=>queueMicrotask(fn);
 globalThis.document={head:new Dom('head'),body:new Dom('body'),getElementById(id){return style?.id===id?style:null;},
 createElement(tag){const e=new Dom(tag);if(tag==='style')style=e;return e;}};
 let code=fs.readFileSync(path.join(root,'../web/js/smartsvg_unified_v2110.js'),'utf8');
 code=code.replace("import {app} from '../../scripts/app.js';",'const app=globalThis.__app;')
          .replace("import {api} from '../../scripts/api.js';",'const api=globalThis.__api;')
          .replace(/import \{validateUnified,[\s\S]*?\} from '\.\/smartsvg_unified_model_v2110\.mjs';/,
                'const {validateUnified,nativeUrl,fitView,clampView,nativeZoom,sourceAt,centerOn,LIMITS,serialize,deserialize,positionUV}=globalThis.__model;');
 await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64')+'#v2110');
 assert.ok(extension);return extension;
}
async function settle(){for(let i=0;i<16;i++)await Promise.resolve();}

test('unified schema and exact save / read / fingerprint and proxy',()=>{
 assert.equal(model.validateUnified(sample),m);
 assert.equal(model.validateUnified({smartsvg_unified:[{...m,source:'../secret'}]}),null);
 const url=model.nativeUrl(m.image,'https://test.example/proxy/8188/','/proxy/8188/view');
 assert.match(url,/proxy\/8188\/view/);assert.match(url,/subfolder=SmartSVG_Studio_Native_V219/);
 const s=[{object:0,mode:'erase',radius:.012,points:[[.5,.5]]}];
 const txt=model.serialize(m,s);assert.deepEqual(model.deserialize(m,txt),s);
 assert.throws(()=>model.deserialize({...m,source:'b'.repeat(64)},txt),/incompatibles/);
 assert.throws(()=>model.serialize(m,[{...s[0],object:2}]),/hors limites/);
 assert.throws(()=>model.serialize(m,[{...s[0],points:[[NaN,.2]]}]),/invalides/);
 assert.deepEqual(model.positionUV({scale:1,x:0,y:0},90,60,180,120),[.5,.5]);
});

test('unified modal draws native source, edits, saves widget; stale output closes UI',async()=>{
 const ext=await install(),field={name:'retouches_json',value:'',callback(){this.called=true;}};
 const node={comfyClass:'SmartSVGUnifiedEditorV2110',size:[100,100],widgets:[field],
 addDOMWidget(name,type,element,options){this.widget={name,type,element,options};return this.widget;},setDirtyCanvas(){}};
 ext.nodeCreated({comfyClass:'SmartSVGMaskEditorV216'});ext.nodeCreated(node);
 assert.equal(node.widget.serialize,false);assert.equal(node.widget.options.serialize,false);
 node.onExecuted(sample);assert.equal(node._ss2110Button.disabled,false);
 node._ss2110Button.fire('click');node._ss2110Button.fire('click');await settle();
 const modal=document.body.children.at(-1),panel=modal.children[0];
 assert.equal(document.body.children.length,1);assert.equal(modal.className,'ss2110-modal');
 const tools=panel.children[1],nav=panel.children[2],viewport=panel.children[3],actions=panel.children[7];
 assert.equal(viewport.attrs.role,'application');assert.equal(viewport.children[0].width,700);
 assert.match(nav.children[4].textContent,/Zoom/);
 const initial=Context.readbacks;assert.ok(initial>=1);
 viewport.fire('pointerdown',{button:0,pointerId:7,clientX:350,clientY:225,preventDefault(){}});
 viewport.fire('pointermove',{pointerId:7,clientX:390,clientY:255});
 await settle();assert.equal(Context.readbacks,initial,'brush drag must use cached QA raster');
 viewport.fire('pointerup',{pointerId:7});await settle();
 assert.equal(Context.readbacks,initial+1,'committed edit must refresh mask raster exactly once');
 assert.equal(actions.children[0].disabled,false);
 nav.children[1].fire('click');await settle();
 assert.equal(Context.readbacks,initial+2,'zoom must refresh mask once');
 assert.match(nav.children[4].textContent,/Zoom/);
 actions.children[0].fire('click');
 assert.equal(field.called,true);
 const doc=JSON.parse(field.value);assert.equal(doc.strokes.length,1);
 assert.equal(doc.strokes[0].object,0);
 assert.equal(node._ss2110Open,false);
 node.onExecuted(sample);node._ss2110Button.fire('click');await settle();
 const reopened=document.body.children.at(-1);
 assert.equal(reopened.children[0].children[6].textContent.includes('trait(s)'),true);
 // A ComfyUI execution during an unsaved edit must keep an in-memory draft
 // for the same image/segmentation instead of silently losing it.
 const pendingViewport=reopened.children[0].children[3];
 pendingViewport.fire('pointerdown',{button:0,pointerId:17,clientX:310,clientY:180,preventDefault(){}});
 pendingViewport.fire('pointerup',{pointerId:17});await settle();
 node.onExecuted(sample);
 assert.equal(reopened.removed,true);
 assert.match(node.widget.element.children[1].textContent,/BROUILLON/);
 node._ss2110Button.fire('click');await settle();
 const recovered=document.body.children.at(-1);
 assert.match(recovered.children[0].children[6].textContent,/retouches non validées/);
 recovered.children[0].children[7].children[0].fire('click');
 assert.equal(JSON.parse(field.value).strokes.length,2);
 assert.equal(node._ss2110Draft,null);
 // A new execution closes stale native views and cannot reuse old pointers.
 node.onExecuted(sample);assert.equal(reopened.removed,true);assert.equal(node._ss2110Open,false);
 // Unsaved drawing must not be silently discarded with Escape or backdrop click.
 node.onExecuted(sample);node._ss2110Button.fire('click');await settle();
 const pending=document.body.children.at(-1),vp=pending.children[0].children[3];
 vp.fire('pointerdown',{button:0,pointerId:9,clientX:350,clientY:225,preventDefault(){}});
 vp.fire('pointerup',{pointerId:9});await settle();
 let prompts=0;window.confirm=()=>{prompts++;return false;};
 pending.fire('keydown',{key:'Escape',preventDefault(){}});
 assert.equal(pending.removed,undefined);assert.equal(prompts,1);
 window.confirm=()=>true;pending.fire('keydown',{key:'Escape',preventDefault(){}});
 assert.equal(pending.removed,true);
 node.onExecuted({});assert.equal(node._ss2110Button.disabled,true);
 node.onRemoved();assert.equal(node._ss2110Meta,null);
 // Failure in the ComfyUI widget callback cannot leave a half-written edit document.
 const field2={name:'retouches_json',value:'',callback(){throw Error('échec contrôlé');}};
 const node2={comfyClass:'SmartSVGUnifiedEditorV2110',size:[340,290],widgets:[field2],
   addDOMWidget(_n,_t,el,options){return {options};},setDirtyCanvas(){}};
 ext.nodeCreated(node2);node2.onExecuted(sample);node2._ss2110Button.fire('click');await settle();
 const failing=document.body.children.at(-1),fpanel=failing.children[0];
 fpanel.children[7].children[0].fire('click');
 assert.equal(field2.value,'');assert.equal(failing.removed,undefined);
 assert.match(fpanel.children[5].textContent,/échec contrôlé/);
 fpanel.children[7].children[1].fire('click');node2.onRemoved();
});
