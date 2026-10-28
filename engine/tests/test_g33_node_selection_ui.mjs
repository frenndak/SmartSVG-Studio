import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import * as handoff from '../web/js/smartsvg_subject_handoff_g33.mjs';
import * as selection from '../web/js/smartsvg_subject_selection_g33c.mjs';
import * as projectGate from '../web/js/smartsvg_subject_project_gate_g33d.mjs';

const original=fs.readFileSync(new URL('../web/js/smartsvg_subject_inspector_v21154.js',import.meta.url),'utf8');
const script=original
 .replace("import {app} from '../../scripts/app.js';","const app=globalThis.__app;")
 .replace("import {api} from '../../scripts/api.js';","const api=globalThis.__api;")
 .replace(/import\s+\{validProjectName,readProjectRevision,makeProjectLock,matchesProjectLock\}\s+from '\.\/smartsvg_subject_project_gate_g33d\.mjs';/,
   "const {validProjectName,readProjectRevision,makeProjectLock,matchesProjectLock}=globalThis.__project;")
 .replace("await import('./smartsvg_subject_handoff_g33.mjs')","await Promise.resolve(globalThis.__handoff)")
 .replace("await import('./smartsvg_subject_selection_g33c.mjs')","await Promise.resolve(globalThis.__selection)");
const png='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAAD0lEQVR42mNgGAUMDAwMAAEIAAEoUqMqAAAAAElFTkSuQmCC';
const report=()=>({smartsvg_subjects_v21154:[{
 source_sha256:'a'.repeat(64),width_px:160,height_px:90,count:2,selection:1,
 sujets:[
  {numero:1,image_data:png,codes:[],zones_a_examiner:[],zones_non_affichees:0},
  {numero:2,image_data:png,codes:['FRAGMENTS_DETACHES'],
   zones_a_examiner:[{type:'FRAGMENT_SEPARE',bbox_source_px:[1,2,8,10],
     bbox_apercu_88px:[2,3,14,19]}],zones_non_affichees:0}
 ]}]});
function setup({projectReader,handoffProvider}={}){
 class Element{
  constructor(tag){this.tagName=tag;this.children=[];this.style={};this.attributes={};
   this.listeners={};this.hidden=false;this.disabled=false;this.value='';this.textContent='';}
  append(...xs){this.children.push(...xs);}
  replaceChildren(...xs){this.children=[...xs];}
  addEventListener(name,cb){(this.listeners[name]??=[]).push(cb);}
  async fire(name){for(const cb of this.listeners[name]??[])await cb();}
  setAttribute(k,v){this.attributes[k]=String(v);}
 }
 const document={createElement:tag=>new Element(tag)};
 let extension=null,root=null;
 const app={registerExtension(e){extension=e;}};
 const channels=[];
 class BroadcastChannel{
  constructor(name){this.name=name;this.closed=false;this.sent=[];channels.push(this);}
  postMessage(data){this.sent.push(data);}
  close(){this.closed=true;}
  receive(data){this.onmessage?.({data});}
 }
 const random={getRandomValues(bytes){bytes.fill(0x42);return bytes;}};
 let projectState={name:'mes_sujets',status:'PROJECT_HEALTHY',sha256:'b'.repeat(64),
   base_masks:{exact_float32:true,editor_fingerprint:'a'.repeat(64),
     count:2,dimensions_px:[160,90]}};
 const requests=[];
 const api={fetchApi:async route=>{
   requests.push(route);
   return {ok:true,json:async()=>({ok:true,project:projectState})};
 }};
 const timers=new Map();
 let timer=0;
 const context={__app:app,__api:api,__project:projectReader?{...projectGate,readProjectRevision:projectReader}:projectGate,__handoff:handoffProvider||handoff,
  __selection:{...selection,createSelectionBinding:(n,r)=>selection.createSelectionBinding(n,r,random)},
  document,window:{location:{protocol:'http:'}},BroadcastChannel,AbortController,
  setTimeout:fn=>{const id=++timer;timers.set(id,fn);return id;},
  clearTimeout:id=>timers.delete(id),console,CustomEvent:class{}};
 vm.runInNewContext(script,context,{timeout:5000});
 const node={id:17,comfyClass:'SmartSVGChooseSubjectV21154',
  inputs:[{name:'image',link:3},{name:'masques_objets',link:4}],
  widgets:[{name:'numero_sujet',value:1}],size:[300,200],
  addDOMWidget(_name,_type,element){root=element;},
  setDirtyCanvas(){},graph:{setDirtyCanvas(){}}};
 extension.nodeCreated(node);
 assert.ok(root,'real inspector is attached to source node');
 const hint=root.children[1],share=root.children[5],confirm=root.children[6];
 return {node,root,hint,share,confirm,channels,timers,api,
   projectName:root.children[8],requests,setProject:next=>{projectState=next;},
   getProject:()=>projectState};
}
test('source node changes widget only after its own explicit confirmation',async()=>{
 const s=setup();s.node.onExecuted(report());
 assert.equal(s.share.disabled,false);
 await s.share.fire('click');
 assert.equal(s.channels.length,1);
 const c=s.channels[0],sent=c.sent[0];
 assert.equal(sent.node_id,17);assert.equal(sent.session_id,'42'.repeat(16));
 const proposal=selection.makeSelectionProposal(sent,2);
 assert.ok(proposal);
 c.receive(proposal);
 assert.equal(s.confirm.hidden,false);
 assert.equal(s.node.widgets[0].value,1,'proposal must not write');
 await s.confirm.fire('click');
 assert.equal(s.node.widgets[0].value,2);
 assert.equal(c.closed,true);
 assert.match(s.hint.textContent,/Relancer manuellement/);
 assert.equal(s.node.inputs[1].link,4,'float32 mask connection untouched');
});
test('detached link or stale rerun invalidates pending confirmation',async()=>{
 const s=setup();s.node.onExecuted(report());await s.share.fire('click');
 const c=s.channels[0];
 c.receive(selection.makeSelectionProposal(c.sent[0],2));
 s.node.inputs[1].link=null;
 await s.confirm.fire('click');
 assert.equal(s.node.widgets[0].value,1);
 assert.match(s.hint.textContent,/périmée/);
 const t=setup();t.node.onExecuted(report());await t.share.fire('click');
 const old=t.channels[0];
 old.receive(selection.makeSelectionProposal(old.sent[0],2));
 t.node.onExecuted(report());
 assert.equal(old.closed,true);
 await t.confirm.fire('click');
 assert.equal(t.node.widgets[0].value,1);
});
test('missing widget and callback failure never leave a false committed choice',async()=>{
 const s=setup();s.node.onExecuted(report());await s.share.fire('click');
 const c=s.channels[0];s.node.widgets=[];
 c.receive(selection.makeSelectionProposal(c.sent[0],2));
 assert.equal(s.confirm.hidden,true);
 const t=setup();t.node.onExecuted(report());await t.share.fire('click');
 const d=t.channels[0];d.receive(selection.makeSelectionProposal(d.sent[0],2));
 t.node.widgets[0].callback=()=>{throw Error('mock failure');};
 await t.confirm.fire('click');
 assert.equal(t.node.widgets[0].value,1);
 assert.match(t.hint.textContent,/restaurée/);
});

test('async widget rejection rolls back and ignores duplicate confirmations',async()=>{
 const s=setup();s.node.onExecuted(report());await s.share.fire('click');
 const channel=s.channels[0];
 channel.receive(selection.makeSelectionProposal(channel.sent[0],2));
 let rejectLater;
 s.node.widgets[0].callback=()=>new Promise((_,reject)=>{rejectLater=reject;});
 const attempt=s.confirm.fire('click');
 assert.equal(s.node.widgets[0].value,2,'temporary widget update before callback settlement');
 assert.equal(s.confirm.disabled,true,'confirmation locked while callback is pending');
 await s.confirm.fire('click');
 rejectLater(new Error('synthetic async rejection'));
 await attempt;
 assert.equal(s.node.widgets[0].value,1,'rejected callback must restore old value');
 assert.match(s.hint.textContent,/restaurée/);
 assert.equal(channel.closed,true);
});

test('async widget resolution commits only if the source report remains current',async()=>{
 const s=setup();s.node.onExecuted(report());await s.share.fire('click');
 const channel=s.channels[0];
 channel.receive(selection.makeSelectionProposal(channel.sent[0],2));
 let resolveLater;
 s.node.widgets[0].callback=()=>new Promise(resolve=>{resolveLater=resolve;});
 const attempt=s.confirm.fire('click');
 s.node.onExecuted(report()); // same fingerprint, but a distinct execution invalidates the proposal
 resolveLater();
 await attempt;
 assert.equal(s.node.widgets[0].value,1,'stale asynchronous confirmation must roll back');
 assert.match(s.hint.textContent,/périmée/);
 assert.equal(channel.closed,true);
 assert.equal(s.share.disabled,false,'fresh report is still available');
});

test('async widget resolution on unchanged source completes normally',async()=>{
 const s=setup();s.node.onExecuted(report());await s.share.fire('click');
 const channel=s.channels[0];
 channel.receive(selection.makeSelectionProposal(channel.sent[0],2));
 s.node.widgets[0].callback=async()=>{};
 await s.confirm.fire('click');
 assert.equal(s.node.widgets[0].value,2);
 assert.match(s.hint.textContent,/Relancer manuellement/);
 assert.equal(channel.closed,true);
});

test('re-share during async confirmation cannot close a later fresh channel',async()=>{
 const s=setup();s.node.onExecuted(report());await s.share.fire('click');
 const first=s.channels[0];
 first.receive(selection.makeSelectionProposal(first.sent[0],2));
 let resolveLater;
 s.node.widgets[0].callback=()=>new Promise(resolve=>{resolveLater=resolve;});
 const attempt=s.confirm.fire('click');
 assert.equal(s.share.disabled,true,'re-share button locked while callback pending');
 await s.share.fire('click'); // force handler despite disabled, as stale DOM events can be queued
 assert.equal(s.channels.length,1,'reentrant share must not replace channel');
 assert.equal(first.closed,false,'old confirmation retains its channel');
 s.node.onExecuted(report()); // a fresh report arrives while old callback is unresolved
 await s.share.fire('click'); // update() may re-enable button, handler must still reject
 assert.equal(s.channels.length,1,'fresh execution cannot bypass confirmation guard');
 resolveLater();await attempt;
 assert.equal(s.node.widgets[0].value,1,'stale old confirmation rolled back');
 assert.equal(first.closed,true);
 assert.equal(s.share.disabled,false,'sharing re-enabled after old callback settles');
 await s.share.fire('click');
 assert.equal(s.channels.length,2,'fresh share works after pending confirmation');
 const second=s.channels[1];
 assert.equal(second.closed,false,'new channel remains open');
 second.receive(selection.makeSelectionProposal(second.sent[0],2));
 s.node.widgets[0].callback=async()=>{};
 await s.confirm.fire('click');
 assert.equal(s.node.widgets[0].value,2,'fresh proposal can be confirmed');
 assert.equal(second.closed,true);
});

test('concurrent send clicks do not open two independent sessions',async()=>{
 const s=setup();s.node.onExecuted(report());
 const first=s.share.fire('click'),second=s.share.fire('click');
 await Promise.all([first,second]);
 assert.equal(s.channels.length,1,'even before dynamic imports resolve, one session is permitted');
 assert.equal(s.channels[0].sent.length,1);
 assert.ok(s.channels[0].sent[0].expires_at_ms>Date.now());
 assert.equal(s.share.disabled,false);
});
test('source node expiration closes channel and invalidates later proposals',async()=>{
 const s=setup();s.node.onExecuted(report());await s.share.fire('click');
 const channel=s.channels[0];
 assert.equal(s.timers.size,1);
 const timer=[...s.timers.values()][0];timer();
 assert.equal(channel.closed,true);
 assert.equal(s.confirm.hidden,true);
 channel.receive(selection.makeSelectionProposal(channel.sent[0],2));
 assert.equal(s.confirm.hidden,true,'expired node never offers confirmation');
});

test('opt-in .smartsvg pin is read-only and rechecked before and after confirmation',async()=>{
 const s=setup();s.node.onExecuted(report());
 s.projectName.value='mes_sujets';
 await s.share.fire('click');
 assert.equal(s.channels.length,1);
 const sent=s.channels[0].sent[0];
 assert.equal(sent.project_name,'mes_sujets');
 assert.equal(sent.project_sha256,'b'.repeat(64));
 assert.equal(s.requests.length,1,'share inspects archive without writing');
 const proposal=selection.makeSelectionProposal(sent,2);
 assert.equal(proposal.project_sha256,sent.project_sha256);
 s.channels[0].receive(proposal);
 await s.confirm.fire('click');
 assert.equal(s.node.widgets[0].value,2);
 assert.equal(s.requests.length,3,'confirmation rechecks before and after callback');
 assert.ok(s.requests.every(x=>x==='/smartsvg/g22/project?name=mes_sujets'));
});
test('project mismatch or unavailable project never silently sends an unbound proposal',async()=>{
 const s=setup();s.node.onExecuted(report());
 s.projectName.value='mes_sujets';
 s.setProject({...s.getProject(),base_masks:{...s.getProject().base_masks,
   editor_fingerprint:'e'.repeat(64)}});
 await s.share.fire('click');
 assert.equal(s.channels.length,0);
 assert.match(s.hint.textContent,/incompatible/);
 const t=setup();t.node.onExecuted(report());t.projectName.value='../bad';
 await t.share.fire('click');
 assert.equal(t.channels.length,0);
 assert.match(t.hint.textContent,/invalide/);
});
test('changed project revision before confirmation refuses subject without changing widget',async()=>{
 const s=setup();s.node.onExecuted(report());s.projectName.value='mes_sujets';
 await s.share.fire('click');const channel=s.channels[0];
 channel.receive(selection.makeSelectionProposal(channel.sent[0],2));
 s.setProject({...s.getProject(),sha256:'d'.repeat(64)});
 await s.confirm.fire('click');
 assert.equal(s.node.widgets[0].value,1);
 assert.match(s.hint.textContent,/Projet .smartsvg modifié/);
 assert.equal(channel.closed,true);
});
test('project revision changed while widget callback awaits rolls back unchanged value',async()=>{
 const s=setup();s.node.onExecuted(report());s.projectName.value='mes_sujets';
 await s.share.fire('click');const channel=s.channels[0];
 channel.receive(selection.makeSelectionProposal(channel.sent[0],2));
 let resolveLater,signalCallbackEntered;
 const callbackEntered=new Promise(resolve=>{signalCallbackEntered=resolve;});
 s.node.widgets[0].callback=()=>{
   signalCallbackEntered();
   return new Promise(resolve=>{resolveLater=resolve;});
 };
 const pending=s.confirm.fire('click');
 await callbackEntered;
 assert.equal(typeof resolveLater,'function');
 s.setProject({...s.getProject(),sha256:'d'.repeat(64)});
 resolveLater();await pending;
 assert.equal(s.node.widgets[0].value,1);
 assert.match(s.hint.textContent,/Projet .smartsvg modifié/);
 assert.equal(channel.closed,true);
});

test('pinned confirmation never overwrites a newer valid numeric subject during a pending GET',async()=>{
 const s=setup(),r=report(),entry=r.smartsvg_subjects_v21154[0];
 entry.count=3;
 entry.sujets.push({...entry.sujets[0],numero:3});
 s.setProject({...s.getProject(),base_masks:{...s.getProject().base_masks,count:3}});
 s.node.onExecuted(r);s.projectName.value='mes_sujets';
 await s.share.fire('click');
 const channel=s.channels[0];
 channel.receive(selection.makeSelectionProposal(channel.sent[0],2));
 let enterGet,finishGet;
 const getStarted=new Promise(resolve=>{enterGet=resolve;});
 s.api.fetchApi=route=>{
   s.requests.push(route);enterGet();
   return new Promise(resolve=>{
     finishGet=()=>resolve({ok:true,json:async()=>({ok:true,project:s.getProject()})});
   });
 };
 let callbacks=0;
 s.node.widgets[0].callback=()=>{callbacks++;};
 const pending=s.confirm.fire('click');
 await getStarted;
 assert.equal(s.node.widgets[0].value,1,'GET has not updated the widget');
 s.node.widgets[0].value=3; // newer explicit numeric user choice
 finishGet();
 await pending;
 assert.equal(s.node.widgets[0].value,3,'newer user choice must win');
 assert.equal(callbacks,0,'obsolete proposal must not invoke callback');
 assert.equal(s.requests.length,2,'no post-callback read on refused proposal');
 assert.equal(channel.closed,true);
 assert.match(s.hint.textContent,/Sélection modifiée.*nouveau choix est conservé/);
 assert.equal(s.share.disabled,false,'user can retry');
});

test('pinned confirmation rejects widget replacement during a pending project GET',async()=>{
 const s=setup();s.node.onExecuted(report());s.projectName.value='mes_sujets';
 await s.share.fire('click');const channel=s.channels[0];
 channel.receive(selection.makeSelectionProposal(channel.sent[0],2));
 let enterGet,finishGet;
 const getStarted=new Promise(resolve=>{enterGet=resolve;});
 s.api.fetchApi=route=>{
   s.requests.push(route);enterGet();
   return new Promise(resolve=>{
     finishGet=()=>resolve({ok:true,json:async()=>({ok:true,project:s.getProject()})});
   });
 };
 const previousWidget=s.node.widgets[0];
 let callbacks=0;previousWidget.callback=()=>{callbacks++;};
 const pending=s.confirm.fire('click');
 await getStarted;
 s.node.widgets[0]={name:'numero_sujet',value:1};
 finishGet();await pending;
 assert.equal(s.node.widgets[0].value,1,'replacement widget untouched');
 assert.equal(previousWidget.value,1,'detached widget untouched');
 assert.equal(callbacks,0);
 assert.equal(channel.closed,true);
 assert.match(s.hint.textContent,/Sélection modifiée/);
});

test('a hung project GET fails closed without sending a subject and allows retry',async()=>{
 const s=setup({projectReader:(api,name)=>projectGate.readProjectRevision(
   api,name,{timeoutMs:15})});
 s.node.onExecuted(report());s.projectName.value='mes_sujets';
 s.api.fetchApi=()=>new Promise(()=>{});
 await s.share.fire('click');
 assert.equal(s.channels.length,0,'no proposal sent from a stalled project inspection');
 assert.equal(s.node.widgets[0].value,1,'subject is unchanged');
 assert.equal(s.share.disabled,false,'user can retry after timeout');
 assert.match(s.hint.textContent,/Délai de lecture du projet dépassé/);
});

test('a hung revision recheck cancels confirmation and preserves the previous subject',async()=>{
 const s=setup({projectReader:(api,name)=>projectGate.readProjectRevision(
   api,name,{timeoutMs:15})});
 s.node.onExecuted(report());s.projectName.value='mes_sujets';
 await s.share.fire('click');
 const channel=s.channels[0];
 channel.receive(selection.makeSelectionProposal(channel.sent[0],2));
 s.api.fetchApi=()=>new Promise(()=>{});
 await s.confirm.fire('click');
 assert.equal(s.node.widgets[0].value,1,'no subject write after stalled GET');
 assert.equal(channel.closed,true,'stale proposal channel is closed');
 assert.equal(s.share.disabled,false,'user can retry');
 assert.match(s.hint.textContent,/Délai de vérification du projet dépassé/);
});

test('editing project during stalled share aborts its GET and preserves newer guidance',async()=>{
 let started,signal;
 const entered=new Promise(resolve=>{started=resolve;});
 const reader=(_api,_name,options)=>{
   signal=options.signal;started();
   return new Promise((_resolve,reject)=>{
     options.signal.addEventListener('abort',()=>reject(Error('PROJECT_BINDING_ABORTED')),{once:true});
   });
 };
 const s=setup({projectReader:reader});s.node.onExecuted(report());
 s.projectName.value='mes_sujets';
 const pending=s.share.fire('click');
 await entered;
 assert.equal(signal.aborted,false);
 s.projectName.value='autre_projet';
 await s.projectName.fire('input');
 await pending;
 assert.equal(signal.aborted,true,'input change cancels a read immediately');
 assert.equal(s.channels.length,0,'no stale diagnostic is transmitted');
 assert.equal(s.share.disabled,false,'sharing can be retried');
 assert.match(s.hint.textContent,/Projet modifié : renvoyer le diagnostic/);
});

test('new execution aborts stalled confirmation GET and retains usable UI',async()=>{
 let reads=0,entered,signal;
 const started=new Promise(resolve=>{entered=resolve;});
 let s;
 const reader=(_api,_name,options)=>{
   if(++reads===1)return Promise.resolve(s.getProject());
   signal=options.signal;entered();
   return new Promise((_resolve,reject)=>{
     options.signal.addEventListener('abort',()=>reject(Error('PROJECT_BINDING_ABORTED')),{once:true});
   });
 };
 s=setup({projectReader:reader});s.node.onExecuted(report());
 s.projectName.value='mes_sujets';await s.share.fire('click');
 const channel=s.channels[0];channel.receive(selection.makeSelectionProposal(channel.sent[0],2));
 const pending=s.confirm.fire('click');
 await started;
 s.node.onExecuted(report()); // a new execution takes ownership of the UI
 await pending;
 assert.equal(signal.aborted,true);
 assert.equal(s.node.widgets[0].value,1,'no stale confirmation committed');
 assert.equal(channel.closed,true,'previous proposal channel invalidated');
 assert.equal(s.share.disabled,false,'new diagnostic can be shared');
 assert.doesNotMatch(s.hint.textContent,/Échec du changement de sujet/,'old abort must not hide fresh status');
});

test('expiry during stalled confirmation aborts its project GET and leaves no dangling proposal',async()=>{
 let reads=0,entered,signal,s;
 const started=new Promise(resolve=>{entered=resolve;});
 const reader=(_api,_name,options)=>{
   if(++reads===1)return Promise.resolve(s.getProject());
   signal=options.signal;entered();
   return new Promise((_resolve,reject)=>{
     options.signal.addEventListener('abort',()=>reject(Error('PROJECT_BINDING_ABORTED')),{once:true});
   });
 };
 s=setup({projectReader:reader});s.node.onExecuted(report());
 s.projectName.value='mes_sujets';await s.share.fire('click');
 const channel=s.channels[0];channel.receive(selection.makeSelectionProposal(channel.sent[0],2));
 const expire=[...s.timers.values()][0];
 const pending=s.confirm.fire('click');
 await started;expire();await pending;
 assert.equal(signal.aborted,true);
 assert.equal(s.node.widgets[0].value,1);
 assert.equal(channel.closed,true);
 assert.equal(s.confirm.hidden,true);
 assert.match(s.hint.textContent,/Proposition expirée/);
});

test('removing source node aborts pending share and seals detached inspector',async()=>{
 let signal,entered;
 const started=new Promise(resolve=>{entered=resolve;});
 const reader=(_api,_name,opts)=>{
   signal=opts.signal;entered();
   return new Promise((_resolve,reject)=>{
     signal.addEventListener('abort',()=>reject(Error('PROJECT_BINDING_ABORTED')),{once:true});
   });
 };
 const s=setup({projectReader:reader});s.node.onExecuted(report());
 s.projectName.value='mes_sujets';
 const pending=s.share.fire('click');await started;
 s.node.onRemoved();
 await pending;
 assert.equal(signal.aborted,true);
 assert.equal(s.channels.length,0,'detached node cannot broadcast stale subjects');
 assert.equal(s.share.disabled,true,'removed inspector must remain disabled');
 s.node.onExecuted(report());
 assert.equal(s.share.disabled,true,'late execution cannot revive detached UI');
 await s.share.fire('click');
 assert.equal(s.channels.length,0,'detached UI never shares again');
});

test('removing source node cancels pinned confirmation without changing the widget',async()=>{
 let count=0,entered,signal,s;
 const started=new Promise(resolve=>{entered=resolve;});
 const reader=(_api,_name,opts)=>{
   if(++count===1)return Promise.resolve(s.getProject());
   signal=opts.signal;entered();
   return new Promise((_resolve,reject)=>{
     signal.addEventListener('abort',()=>reject(Error('PROJECT_BINDING_ABORTED')),{once:true});
   });
 };
 s=setup({projectReader:reader});s.node.onExecuted(report());s.projectName.value='mes_sujets';
 await s.share.fire('click');
 const channel=s.channels[0];
 channel.receive(selection.makeSelectionProposal(channel.sent[0],2));
 const pending=s.confirm.fire('click');await started;
 s.node.onRemoved();await pending;
 assert.equal(signal.aborted,true);
 assert.equal(s.node.widgets[0].value,1);
 assert.equal(channel.closed,true);
 assert.equal(s.share.disabled,true);
 assert.equal(s.confirm.disabled,true);
});

test('editing a pinned project to blank during module import cannot send an unbound report',async()=>{
 let releaseImport;
 const importReady=new Promise(resolve=>{releaseImport=resolve;});
 const s=setup({handoffProvider:importReady});
 s.node.onExecuted(report());s.projectName.value='mes_sujets';
 const pending=s.share.fire('click');
 // The dynamic import has not resolved; invalidate this session by clearing pin.
 s.projectName.value='';
 await s.projectName.fire('input');
 releaseImport(handoff);
 await pending;
 assert.equal(s.channels.length,0,'cancelled pinned transfer must not downgrade to unbound');
 assert.equal(s.share.disabled,false,'new explicit send is possible');
 assert.match(s.hint.textContent,/Projet modifié/);
});
