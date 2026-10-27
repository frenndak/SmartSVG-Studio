import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import * as model from '../web/js/smartsvg_editor_model_v216.mjs';
import {editorDraftStore} from '../web/js/smartsvg_editor_draft_g28.mjs';
const base=path.dirname(fileURLToPath(import.meta.url));
class Context{
 save(){}restore(){}clearRect(){}drawImage(){}beginPath(){}moveTo(){}lineTo(){}stroke(){}arc(){}fill(){}
 getImageData(x,y,w,h){return {data:new Uint8ClampedArray(w*h*4)};}
 putImageData(){}
}
class Dom{
 constructor(tag){this.tagName=tag;this.children=[];this.events={};this.attributes={};this.style={};
 this.classList={toggle(){}};this.value='';this.textContent='';this.disabled=false;this.size=[];this.ctx=new Context();}
 append(...x){this.children.push(...x);}
 appendChild(x){this.children.push(x);return x;}
 addEventListener(t,fn){this.events[t]=fn;}
 setAttribute(k,v){this.attributes[k]=v;}
 getBoundingClientRect(){return {left:0,top:0,width:760,height:570};}
 setPointerCapture(){}
 getContext(){return this.ctx;}
 focus(){}
 remove(){this.removed=true;}
 fire(t,x={}){if(this.events[t])this.events[t](x);}
}
class FakeImage {set src(value){this.uri=value;queueMicrotask(()=>this.onload?.());}}
let serial=0;
async function extension(){
 let ext;
 globalThis.__mockApp={registerExtension(n){ext=n;},graph:{change(){}}};
 globalThis.__mockApi={apiURL(s){return '/proxy/8188'+s;}};
 globalThis.__model=model;
 globalThis.__draftModel={editorDraftStore};
 globalThis.__g23Bridge={createEditorProjectControls:()=>({root:new Dom('div'),refresh(){}})};
 globalThis.window={location:{href:'https://test.example/proxy/8188/'}};
 globalThis.Image=FakeImage;
 let style=null;
 const documentEvents={};
 const doc={head:new Dom('head'),body:new Dom('body'),events:documentEvents,
 getElementById(id){return style?.id===id?style:null;},
 createElement(tag){const d=new Dom(tag);if(tag==='style')style=d;return d;},
 addEventListener(t,fn){documentEvents[t]=fn;},removeEventListener(t){delete documentEvents[t];}};
 globalThis.document=doc;
 let src=fs.readFileSync(path.join(base,'../web/js/smartsvg_editor_v216.js'),'utf8');
 src=src.replace("import { app } from '../../scripts/app.js';","const app=globalThis.__mockApp;");
 src=src.replace("import { createEditorProjectControls } from './smartsvg_editor_project_bridge_g23.mjs';",
                 'const {createEditorProjectControls}=globalThis.__g23Bridge;');
 src=src.replace("import { editorDraftStore } from './smartsvg_editor_draft_g28.mjs';",
                 'const {editorDraftStore}=globalThis.__draftModel;');
 src=src.replace("import { api } from '../../scripts/api.js';","const api=globalThis.__mockApi;");
 src=src.replace(/import \{ normalizeMeta,[\s\S]*?\} from '\.\/smartsvg_editor_model_v216\.mjs';/,
 'const { normalizeMeta, previewUrl, encodeDocument, decodeDocument, LIMITS, fitView, constrainView, zoomView, moveView, viewToUV, strokeSpacing }=globalThis.__model;');
 await import('data:text/javascript;base64,'+Buffer.from(src).toString('base64')+'#'+(++serial));
 assert.ok(ext);return {ext,doc};
}
const ref=name=>({filename:`ed_${'d'.repeat(24)}_${name}.png`,subfolder:'SmartSVG_Studio_Editor',type:'output'});
const sample={smartsvg_editor:[{version:1,width:760,height:570,count:1,source:'a'.repeat(64),
 preview_width:760,preview_height:570,image:ref('image'),masks:[ref('mask00')] }]};
const tick=async()=>{await Promise.resolve();await Promise.resolve();await Promise.resolve();};
test('new editor persists modifications to real workflow widget, and does not serialize display',async()=>{
 const {ext,doc}=await extension();
 const textWidget={name:'retouches_json',value:''};
 const node={comfyClass:'SmartSVGMaskEditorV216',widgets:[textWidget],size:[200,100],
 addDOMWidget(name,type,root,options){this.dashboard={name,type,root,options};return this.dashboard;},setDirtyCanvas(){}};
 ext.nodeCreated(node);
 assert.equal(node.dashboard.serialize,false);
 assert.equal(node.dashboard.options.serialize,false);
 assert.ok(node.size[1]>=315);
 node.onExecuted(sample);
 assert.equal(node._smartsvgV216Editor.trigger.disabled,false);
 node._smartsvgV216Editor.trigger.fire('click');
 node._smartsvgV216Editor.trigger.fire('click'); // second click must not duplicate the modal
 await tick();
 const overlay=doc.body.children.at(-1);
 assert.ok(overlay);
 assert.equal(doc.body.children.length,1);
 assert.equal(node._smartsvgV216ModalOpen,true);
 const panel=overlay.children[0],controls=panel.children[1],toolbar=panel.children[2],viewport=panel.children[3],buttons=panel.children[5];
 const canvas=viewport.children[0];
 assert.equal(canvas.tagName,'canvas');
 assert.equal(viewport.attributes.role,'application');
 assert.equal(canvas.style.width,'760px');
 await tick();
 viewport.fire('pointerdown',{button:0,pointerId:1,clientX:380,clientY:285,preventDefault(){}});
 viewport.fire('pointermove',{pointerId:1,clientX:400,clientY:305,preventDefault(){}});
 viewport.fire('pointerup',{pointerId:1,preventDefault(){}});
 // Zoom must not alter the persisted normalized stroke geometry.
 toolbar.children[1].fire('click');
 assert.ok(parseFloat(canvas.style.width)>760);
 controls.children[4].fire('click'); // pan mode
 const left=parseFloat(canvas.style.left);
 viewport.fire('pointerdown',{button:0,pointerId:9,clientX:380,clientY:285,preventDefault(){}});
 viewport.fire('pointermove',{pointerId:9,clientX:420,clientY:285,preventDefault(){}});
 viewport.fire('pointerup',{pointerId:9,preventDefault(){}});
 assert.ok(parseFloat(canvas.style.left)>left);
 toolbar.children[2].fire('click');
 assert.equal(canvas.style.width,'760px');
 buttons.children[0].fire('click');
 const payload=JSON.parse(textWidget.value);
 assert.equal(payload.version,1);
 assert.equal(payload.strokes.length,1);
 assert.equal(payload.strokes[0].mode,'add');
 assert.equal(payload.strokes[0].object,0);
 assert.equal(payload.source,'a'.repeat(64));
 assert.equal(overlay.removed,true);
 assert.equal(node._smartsvgV216ModalOpen,false);
 // Clear previous UI result if onExecuted receives no valid payload.
 node.onExecuted({});
 assert.equal(node._smartsvgV216Editor.trigger.disabled,true);
 // User can explicitly reset corrections even if the image/source changed.
 node.dashboard.root.children[1].fire('click');
 assert.equal(textWidget.value,'');
});
test('legacy nodes remain unaffected; browser without DOM widget degrades',async()=>{
 const {ext}=await extension();
 const older={comfyClass:'SmartSVGExpressV2151'};ext.nodeCreated(older);
 assert.equal(older._smartsvgV216Editor,undefined);
 const noWidget={comfyClass:'SmartSVGMaskEditorV216'};ext.nodeCreated(noWidget);
 assert.equal(noWidget._smartsvgV216Editor,undefined);
});

test('zoomed brush maps to the same native coordinates; pan and zoom never become strokes',async()=>{
 const {ext,doc}=await extension();
 const field={name:'retouches_json',value:''};
 const node={comfyClass:'SmartSVGMaskEditorV216',widgets:[field],size:[350,315],
 addDOMWidget(name,type,root,options){return {name,type,root,options};},setDirtyCanvas(){}};
 ext.nodeCreated(node);node.onExecuted(sample);
 node._smartsvgV216Editor.trigger.fire('click');await tick();
 const panel=doc.body.children.at(-1).children[0],controls=panel.children[1],toolbar=panel.children[2],viewport=panel.children[3];
 const canvas=viewport.children[0];
 await tick();
 const initLeft=parseFloat(canvas.style.left);
 viewport.fire('wheel',{deltaY:-240,clientX:380,clientY:285,preventDefault(){}});
 assert.ok(parseFloat(canvas.style.width)>760);
 controls.children[4].fire('click');
 viewport.fire('pointerdown',{pointerId:55,button:0,clientX:380,clientY:285,preventDefault(){}});
 viewport.fire('pointermove',{pointerId:55,clientX:400,clientY:285,preventDefault(){}});
 viewport.fire('pointerup',{pointerId:55,preventDefault(){}});
 assert.notEqual(parseFloat(canvas.style.left),initLeft);
 controls.children[2].fire('click'); // back to add
 toolbar.children[2].fire('click'); // fit
 viewport.fire('pointerdown',{pointerId:77,button:0,clientX:380,clientY:285,preventDefault(){}});
 viewport.fire('pointerup',{pointerId:77,preventDefault(){}});
 assert.equal(controls.children[6].disabled,false);
 assert.equal(controls.children[7].disabled,true);
 // Ctrl+Z and Ctrl+Shift+Z are intercepted only while the editor is open.
 doc.events.keydown({key:'z',ctrlKey:true,shiftKey:false,preventDefault(){},stopPropagation(){}});
 assert.equal(controls.children[6].disabled,true);
 doc.events.keydown({key:'z',ctrlKey:true,shiftKey:true,preventDefault(){},stopPropagation(){}});
 assert.equal(controls.children[6].disabled,false);
 const save=panel.children[5].children[0];save.fire('click');
 const strokes=JSON.parse(field.value).strokes;
 assert.equal(strokes.length,1);
 assert.deepEqual(strokes[0].points,[[.5,.5]]);
 assert.equal(doc.events.keydown,undefined); // listeners cleaned up on close
 // Reopening loads and preserves the serialized modifications.
 node._smartsvgV216Editor.trigger.fire('click');await tick();
 const reopened=doc.body.children.at(-1),second=reopened.children[0];
 assert.equal(second.children[1].children[6].disabled,false);
 second.children[5].children[1].fire('click');
});

test('a cancelled stroke and multi-point pan do not change the saved workflow',async()=>{
 const {ext,doc}=await extension();
 const field={name:'retouches_json',value:''};
 const node={comfyClass:'SmartSVGMaskEditorV216',widgets:[field],size:[350,315],
 addDOMWidget(){return {options:{}};},setDirtyCanvas(){}};
 ext.nodeCreated(node);node.onExecuted(sample);node._smartsvgV216Editor.trigger.fire('click');await tick();await tick();
 const panel=doc.body.children.at(-1).children[0],controls=panel.children[1],viewport=panel.children[3];
 viewport.fire('pointerdown',{pointerId:2,button:0,clientX:300,clientY:200,preventDefault(){}});
 viewport.fire('pointercancel',{pointerId:2});
 controls.children[4].fire('click');
 viewport.fire('pointerdown',{pointerId:3,button:0,clientX:300,clientY:200,preventDefault(){}});
 viewport.fire('pointermove',{pointerId:3,clientX:400,clientY:300,preventDefault(){}});
 viewport.fire('pointerup',{pointerId:3,preventDefault(){}});
 panel.children[5].children[0].fire('click');
 assert.equal(JSON.parse(field.value).strokes.length,0);
});
