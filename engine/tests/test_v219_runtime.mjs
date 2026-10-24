import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as model from '../web/js/smartsvg_native_model_v219.mjs';
class Context{setTransform(){}clearRect(){}drawImage(){}putImageData(){}beginPath(){}arc(){}stroke(){}fillRect(){}fillText(){}
 getImageData(x,y,w,h){return {data:new Uint8ClampedArray(w*h*4)};}}
class Dom{
 constructor(tag){this.tagName=tag.toUpperCase();this.children=[];this.events={};this.style={};this.attrs={};this.disabled=false;this.value='';this.width=0;this.height=0;this.ctx=new Context();}
 set textContent(v){this.txt=String(v);this.children=[];}get textContent(){return this.txt||'';}
 append(...elements){this.children.push(...elements);}appendChild(v){this.children.push(v);return v;}
 replaceChildren(...elements){this.children=[...elements];}
 addEventListener(name,callback){this.events[name]=callback;}
 setAttribute(k,v){this.attrs[k]=v;}
 getBoundingClientRect(){return {left:0,top:0,width:700,height:450};}
 setPointerCapture(){}getContext(){return this.ctx;}focus(){}remove(){this.removed=true;}
 fire(name,e={}){this.events[name]?.(e);}
}
class FakeImage{
 naturalWidth=450;naturalHeight=300;
 set src(url){this.url=url;queueMicrotask(()=>this.onload?.());}
}
async function install(){
 let ext;
 globalThis.__mockApp={registerExtension(v){ext=v;}};
 globalThis.__mockApi={apiURL(route){return '/comfyui'+route;}};
 globalThis.__model=model;
 globalThis.Image=FakeImage;
 globalThis.window={location:{href:'https://foo.test/comfyui/'},devicePixelRatio:1};
 globalThis.requestAnimationFrame=cb=>queueMicrotask(cb);
 let style=null;
 globalThis.document={head:new Dom('head'),body:new Dom('body'),
 getElementById(id){return style?.id===id?style:null;},
 createElement(tag){const x=new Dom(tag);if(tag==='style')style=x;return x;}};
 let code=fs.readFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)),'../web/js/smartsvg_native_v219.js'),'utf8');
 code=code.replace("import {app} from '../../scripts/app.js';",'const app=globalThis.__mockApp;')
          .replace("import {api} from '../../scripts/api.js';",'const api=globalThis.__mockApi;')
          .replace(/import \{validateMeta,[\s\S]*?\} from '\.\/smartsvg_native_model_v219\.mjs';/,
                   'const {validateMeta,nativeUrl,fitView,clampView,nativeZoom,sourceAt,centerOn}=globalThis.__model;');
 await import('data:text/javascript;base64,'+Buffer.from(code).toString('base64')+'#test');
 assert.ok(ext);
 return ext;
}
const token='0'.repeat(24);
const ref=k=>({filename:`ni_${token}_${k}.png`,subfolder:'SmartSVG_Studio_Native_V219',type:'output'});
const payload={smartsvg_native:[{version:1,width:450,height:300,count:2,image:ref('image'),masks:[ref('mask00'),ref('mask01')],
 objects:[{objet:1,etat:'a_verifier',alertes:['ILOT'],points:[{type:'ILOT_DETACHE',x:50,y:60,detail:'Examiner',priorite:1}]},
          {objet:2,etat:'ok',alertes:[],points:[]}]}]};
const tick=async()=>{for(let i=0;i<12;i++)await Promise.resolve();};
test('frontend attaches non serialized viewer, loads full size and never changes workflow',async()=>{
 const ext=await install();const old={comfyClass:'SmartSVGMaskEditorV216'};ext.nodeCreated(old);assert.equal(old._smartsvg219Hook,undefined);
 const node={comfyClass:'SmartSVGNativeInspectorV219',size:[200,100],setDirtyCanvas(){},
 addDOMWidget(name,type,root,options){this.widget={name,type,root,options};}};
 ext.nodeCreated(node);assert.equal(node.widget.options.serialize,false);
 node.onExecuted(payload);assert.equal(node._smartsvg219Button.disabled,false);
 node._smartsvg219Button.fire('click');await tick();
 const overlay=document.body.children.at(-1),panel=overlay.children[0];
 assert.ok(overlay);assert.equal(overlay.className,'ss219-modal');
 assert.equal(node._smartsvg219Open,true);
 const controls=panel.children[1],viewport=panel.children[2];
 assert.equal(viewport.attrs.role,'application');
 assert.equal(viewport.children[0].width,700);
 // Changing selected subject loads only the new mask; never modifies source or fabrication MASK.
 controls.children[1].value='1';controls.children[1].fire('change');await tick();
 assert.match(panel.children[4].textContent,/Sujet 2/);
 controls.children[4].fire('click');await tick(); // native 100%
 assert.match(controls.children[6].textContent,/100 %/);
 // New workflow execution must not leave a stale earlier inspection visible.
 node.onExecuted(payload);assert.equal(node._smartsvg219Open,false);
 assert.equal(overlay.removed,true);assert.equal(node._smartsvg219Button.disabled,false);
 node._smartsvg219Button.fire('click');await tick();
 const second=document.body.children.at(-1);
 second.children[0].children.at(-1).fire('click');assert.equal(node._smartsvg219Open,false);
 node.onExecuted({});assert.equal(node._smartsvg219Button.disabled,true);
 // Concurrent new execution before the async image load completes: no stale overlay.
 node.onExecuted(payload);const before=document.body.children.length;
 node._smartsvg219Button.fire('click');node.onExecuted(payload);await tick();
 assert.equal(document.body.children.length,before);
 assert.equal(node._smartsvg219Open,false);
 node.onRemoved();assert.equal(node._smartsvg219Meta,null);
});
