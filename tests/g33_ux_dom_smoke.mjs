import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import * as handoff from '../engine/web/js/smartsvg_subject_handoff_g33.mjs';
import * as selection from '../engine/web/js/smartsvg_subject_selection_g33c.mjs';
import * as identity from '../engine/web/js/smartsvg_subject_identity_g33e.mjs';

const page=readFileSync(new URL('../engine/web/js/smartsvg_express_atelier_preview.html',import.meta.url),'utf8');
const script=page.match(/<script>\s*([\s\S]*?)<\/script>/i)?.[1];
const vmScript=script?.replace(
  'await import("./smartsvg_subject_handoff_g33.mjs")',
  'await Promise.resolve(globalThis.__g33Handoff)'
).replace(
  'await import("./smartsvg_subject_selection_g33c.mjs")',
  'await Promise.resolve(globalThis.__g33Selection)'
).replace(
  'await import("./smartsvg_subject_identity_g33e.mjs")',
  'await Promise.resolve(globalThis.__g33Identity)'
).replaceAll(
  'import("../../scripts/api.js")',
  'Promise.resolve({api:globalThis.__g33Api})'
);
assert.ok(script,'single inline G3 atelier script required');

function browser(){
  class Element{
    constructor(tag='div',id=''){
      this.tagName=tag;this.id=id;this.value='';this.dataset={};this.listeners={};
      this.attributes={};this.children=[];this.files=[];
      this.type='';this.disabled=false;this.hidden=false;this.className='';
      this.style={setProperty(){}};
      this._textContent='';
    }
    set textContent(value){this._textContent=String(value);}
    get textContent(){return this._textContent;}
    set innerHTML(value){this._innerHTML=value;}
    get innerHTML(){return this._innerHTML||'';}
    setAttribute(k,v){this.attributes[k]=String(v);}
    removeAttribute(k){delete this.attributes[k];}
    addEventListener(type,fn){(this.listeners[type]??=[]).push(fn);}
    replaceChildren(...items){this.children=[...items];}
    appendChild(item){this.children.push(item);}
    append(...items){this.children.push(...items);}
    scrollIntoView(){}
    click(){this.fire('click');}
    async fire(type,event={}){for(const cb of this.listeners[type]??[])await cb(event);}
  }
  const store=new Map();
  const find=id=>store.get(id)||(store.set(id,new Element('div',id)),store.get(id));
  const ids=['file','uploadButton','realContourButton','realProjectButton','realContourHost',
    'realProjectHost','realContourMount','realProjectMount','sheet','uploaded','empty',
    'notification','count','selInfo','stageBadge','statePill','sizeNote','artboardNote',
    'width','dpi','stageTitle','stageSubtitle','actionTitle','actionDesc','modeHint',
    'next','all','none','alternate','resetSelect','demo','zoomLabel','artboardWrap','dropZone',
    'zoomIn','zoomOut','zoomFit','fileInfo','receiveSubjects','clearSubjects',
    'realSubjectsGrid','realSubjectsStatus','realSubjectsSelection','realSubjectsHost'];
  for(const id of ids)find(id);
  find('width').value='40';
  for(const id of ['uploaded','empty','realProjectHost','realContourHost'])find(id).hidden=true;
  const steps=['source','clean','subjects','retouch','cut','export'].map(step=>{
    const el=new Element('button');el.dataset.step=step;return el;
  });
  const navigation=['source','subjects','retouch','cut','export'].map(view=>{
    const el=new Element('button');el.dataset.view=view;return el;
  });
  const modeInput=new Element('input');modeInput.value='cut';
  const document={
    getElementById:find,
    createElement:tag=>new Element(tag),
    querySelectorAll:sel=>sel==='[data-step]'?steps:
      sel==='[data-view]'?navigation:
      sel==='input[name="mode"]'?[modeInput]:[],
    querySelector:sel=>sel==='input[name="mode"]:checked'?modeInput:null,
  };
  const revoked=[],created=[];
  const URL={createObjectURL(file){const url='blob:smartsvg-'+created.length;created.push([url,file]);return url;},
    revokeObjectURL(url){revoked.push(url);}};
  class Image {
    static pending=[];
    constructor(){this.naturalWidth=0;this.naturalHeight=0;Image.pending.push(this);}
    set src(v){this._src=v;}
    get src(){return this._src;}
    load(w=300,h=200){this.naturalWidth=w;this.naturalHeight=h;this.onload?.();}
    fail(){this.onerror?.();}
  }
  const confirmations=[];
  const window={location:{protocol:'file:'},addEventListener(){},
    confirm(message){confirmations.push(message);return true;}};
  class MockBroadcastChannel{
    static instances=[];
    constructor(name){this.name=name;this.closed=false;this.posted=[];MockBroadcastChannel.instances.push(this);}
    postMessage(value){this.posted.push(value);}
    close(){this.closed=true;}
    sendToReceiver(data){this.onmessage?.({data});}
  }
  const timeouts=new Map();let nextTimeout=1;
  let simulatedNow=Date.now();
  class SimulatedDate extends Date {static now(){return simulatedNow;}}
  const apiCalls=[];
  const api={fetchApi:async(route,options)=>{
    apiCalls.push({route,options});
    return {ok:true,json:async()=>({ok:true,result:{
      name:'subjects',status:'subject_identity_created',
      subject_id:'subject-'+ 'e'.repeat(32),mask_id:'base-mask-00',
      bbox_px:[0,0,160,90],sha256:'f'.repeat(64),
      previous_available:true,certified:false,
    }})};
  }};
  class FormData{constructor(){this.rows=[];}append(key,value){this.rows.push([key,value]);}}
  const globals={document,window,URL,Image,console,Set,Array,Math,Number,String,Date:SimulatedDate,
    Object,Promise,FormData,AbortController,BroadcastChannel:MockBroadcastChannel,
    __g33Handoff:handoff,__g33Selection:selection,__g33Identity:identity,__g33Api:api,
    setTimeout:(fn)=>{const id=nextTimeout++;timeouts.set(id,fn);return id;},
    clearTimeout:id=>timeouts.delete(id)};
  vm.runInNewContext(vmScript,globals,{timeout:5000});
  return {find,steps,navigation,revoked,created,Image,document,
    window,confirmations,apiCalls,api,MockBroadcastChannel,timeouts,
    advance:ms=>{simulatedNow+=ms;}};
}
const file=(name,type='image/png',size=1000)=>({name,type,size});

test('six-step navigation exposes retouches on compact displays and advances to cut',async()=>{
  const b=browser();
  assert.equal(b.steps.length,6);
  await b.steps[3].fire('click');
  assert.equal(b.find('stageTitle').textContent,'Retouches des masques');
  assert.equal(b.steps[3].attributes['aria-current'],'step');
  await b.find('next').fire('click');
  assert.equal(b.find('stageTitle').textContent,'Contours & découpe');
});
test('resetting selection does not wipe a previously loaded file',async()=>{
  const b=browser();
  await b.find('none').fire('click');
  assert.equal(b.find('count').textContent,'0 / 12');
  await b.find('resetSelect').fire('click');
  assert.equal(b.find('count').textContent,'12 / 12');
  b.find('file').files=[file('test-1.png')];
  await b.find('file').fire('change',{target:b.find('file')});
  b.Image.pending.at(-1).load();
  assert.match(b.find('fileInfo').textContent,/test-1\.png/);
  assert.equal(b.find('all').disabled,true);
  assert.equal(b.find('resetSelect').disabled,true);
  await b.find('resetSelect').fire('click');
  assert.match(b.find('fileInfo').textContent,/test-1\.png/);
  await b.find('demo').fire('click');
  assert.equal(b.find('count').textContent,'12 / 12');
  assert.equal(b.find('fileInfo').textContent.includes('Démo chargée'),true);
});
test('late onload never overwrites newer image; rejected oversized image keeps old',async()=>{
  const b=browser();
  const input=b.find('file');
  input.files=[file('older.png')];
  await input.fire('change',{target:input});
  const older=b.Image.pending.at(-1);
  input.files=[file('newer.png')];
  await input.fire('change',{target:input});
  const newer=b.Image.pending.at(-1);
  older.load();
  assert.doesNotMatch(b.find('fileInfo').textContent,/older\.png/);
  newer.load(1200,800);
  assert.match(b.find('fileInfo').textContent,/newer\.png/);
  assert.ok(b.revoked.includes('blob:smartsvg-0'));
  input.files=[file('giant.png')];
  await input.fire('change',{target:input});
  b.Image.pending.at(-1).load(12000,8000);
  assert.match(b.find('fileInfo').textContent,/newer\.png/);
  assert.ok(b.revoked.includes('blob:smartsvg-2'));
  assert.match(b.find('notification').textContent,/20 millions de pixels/);
});
test('invalid replacement invalidates outstanding decode and stale errors stay silent',async()=>{
  const b=browser(),input=b.find('file');
  input.files=[file('pending.png')];
  await input.fire('change',{target:input});
  const pending=b.Image.pending.at(-1);
  input.files=[file('bad.txt','text/plain')];
  await input.fire('change',{target:input});
  const msg=b.find('notification').textContent;
  pending.fail();
  assert.equal(b.find('notification').textContent,msg);
  assert.ok(b.revoked.includes('blob:smartsvg-0'));
});
test('real ComfyUI panels are explicitly unavailable on file:// but UI stays interactive',async()=>{
  const b=browser();
  await b.find('realProjectButton').fire('click');
  assert.match(b.find('notification').textContent,/page servie depuis ComfyUI/);
  assert.equal(b.find('realProjectHost').hidden,true);
  await b.find('realContourButton').fire('click');
  assert.match(b.find('notification').textContent,/ComfyUI/);
  await b.find('none').fire('click');
  assert.equal(b.find('count').textContent,'0 / 12');
});

test('explicit real subject reception displays verified G2.6 content and stays non-destructive',async()=>{
  const b=browser();
  b.window.location.protocol='http:';
  await b.find('receiveSubjects').fire('click');
  assert.equal(b.MockBroadcastChannel.instances.length,1);
  const channel=b.MockBroadcastChannel.instances[0];
  assert.equal(b.find('receiveSubjects').disabled,true);
  channel.sendToReceiver({kind:'foreign-plugin',sujets:[]});
  assert.equal(b.find('realSubjectsGrid').children.length,0);
  const png='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAAD0lEQVR42mNgGAUMDAwMAAEIAAEoUqMqAAAAAElFTkSuQmCC';
  channel.sendToReceiver({kind:'smartsvg:subjects:g33b',version:1,
    selection:1,source_sha256:'a'.repeat(64),width_px:160,height_px:90,count:2,
    sujets:[
      {numero:1,image_data:png,codes:['FRAGMENTS_DETACHES'],
       zones_a_examiner:[
         {type:'FRAGMENT_SEPARE',bbox_source_px:[1,2,8,10],
           bbox_apercu_88px:[2,3,14,19]},
         {type:'MICRO_FRAGMENT',bbox_source_px:[10,11,14,15],
           bbox_apercu_88px:[20,21,24,25]}
       ],zones_non_affichees:0},
      {numero:2,image_data:png,codes:['MASQUE_VIDE'],
       zones_a_examiner:[],zones_non_affichees:0}
    ]});
  assert.equal(channel.closed,true);
  assert.equal(b.find('receiveSubjects').disabled,false);
  assert.equal(b.find('realSubjectsGrid').children.length,2);
  assert.match(b.find('realSubjectsStatus').textContent,/Diagnostic G2.6 reçu/);
  assert.match(b.find('realSubjectsSelection').textContent,/1 \/ 2 sujets/);
  const first=b.find('realSubjectsGrid').children[0];
  const details=first.children.find(x=>x.tagName==='details');
  const zoneButtons=details.children.filter(x=>x.tagName==='button');
  const rings=first.children.find(x=>x.className==='thumb-wrap').children.slice(1);
  assert.equal(zoneButtons.length,2);
  assert.equal(zoneButtons[0].attributes['aria-pressed'],'false');
  await zoneButtons[0].fire('click');
  assert.equal(zoneButtons[0].attributes['aria-pressed'],'true');
  assert.equal(rings[0].attributes['data-active'],'true');
  assert.match(b.find('realFragmentStatus').textContent,/pixels source \[1, 2, 8, 10\]/);
  await zoneButtons[1].fire('click');
  assert.equal(zoneButtons[0].attributes['aria-pressed'],'false');
  assert.equal(zoneButtons[1].attributes['aria-pressed'],'true');
  assert.equal(rings[0].attributes['data-active'],'false');
  assert.equal(rings[1].attributes['data-active'],'true');
  assert.match(b.find('realFragmentStatus').textContent,/Micro-fragment/);
  assert.match(b.find('realFragmentStatus').textContent,/sans modification des masques/);
  const button=first.children.find(x=>x.tagName==='button');
  assert.equal(button.attributes['aria-pressed'],'true');
  await button.fire('click');
  assert.match(b.find('realSubjectsSelection').textContent,/0 \/ 2 sujets/);
  // The old fictitious planche remains unchanged.
  assert.equal(b.find('count').textContent,'12 / 12');
  await b.find('clearSubjects').fire('click');
  assert.equal(b.find('realSubjectsGrid').children.length,0);
  assert.equal(b.find('realFragmentStatus').textContent,'');
  assert.match(b.find('realSubjectsStatus').textContent,/Aucun masque ni projet modifié/);
});
test('real subjects receiver explicitly refuses file protocol',async()=>{
  const b=browser();
  await b.find('receiveSubjects').fire('click');
  assert.equal(b.MockBroadcastChannel.instances.length,0);
  assert.match(b.find('realSubjectsStatus').textContent,/ComfyUI sous HTTP local/);
});

test('bound G2.6 report proposes one subject to node, never applies a mask',async()=>{
  const b=browser();b.window.location.protocol='http:';
  await b.find('receiveSubjects').fire('click');
  const receive=b.MockBroadcastChannel.instances[0];
  const png='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAgAAAAICAYAAADED76LAAAAD0lEQVR42mNgGAUMDAwMAAEIAAEoUqMqAAAAAElFTkSuQmCC';
  const report={kind:'smartsvg:subjects:g33b',version:1,
    node_id:17,session_id:'4'.repeat(32),expires_at_ms:Date.now()+90_000,selection:1,
    source_sha256:'a'.repeat(64),width_px:160,height_px:90,count:2,
    sujets:[
      {numero:1,image_data:png,codes:['FRAGMENTS_DETACHES'],
       zones_a_examiner:[{type:'FRAGMENT_SEPARE',bbox_source_px:[1,2,8,10],
         bbox_apercu_88px:[2,3,14,19]}],zones_non_affichees:0},
      {numero:2,image_data:null,codes:['MASQUE_VIDE'],
       zones_a_examiner:[],zones_non_affichees:0}
    ]};
  receive.sendToReceiver(report);
  const card=b.find('realSubjectsGrid').children[0];
  const proposals=card.children.filter(x=>x.tagName==='button');
  assert.equal(proposals.length,2,'one local selection and one explicit proposal');
  assert.equal(b.find('realSubjectsGrid').children[1].children.filter(x=>x.tagName==='button').length,1);
  await proposals[1].fire('click');
  assert.equal(b.MockBroadcastChannel.instances.length,2);
  const outbound=b.MockBroadcastChannel.instances[1];
  assert.equal(outbound.closed,true);
  assert.equal(outbound.posted.length,1);
  assert.equal(outbound.posted[0].node_id,17);
  assert.equal(outbound.posted[0].session_id,'4'.repeat(32));
  assert.equal(outbound.posted[0].subject,1);
  assert.match(b.find('realSubjectsStatus').textContent,/Confirmer dans ComfyUI/);
  assert.match(b.find('realSubjectsSelection').textContent,/1 \/ 2/);
  await b.find('clearSubjects').fire('click');
  await proposals[1].fire('click');
  assert.equal(b.MockBroadcastChannel.instances.length,2,'stale card must not send');
  assert.match(b.find('realSubjectsStatus').textContent,/Rapport remplacé/);
  assert.equal(b.find('count').textContent,'12 / 12','demo remains isolated');
});

test('Atelier expires proposal controls, even when the real PNG thumbnails stay visible',async()=>{
 const b=browser();b.window.location.protocol='http:';
 await b.find('receiveSubjects').fire('click');
 const report={kind:'smartsvg:subjects:g33b',version:1,
   node_id:17,session_id:'4'.repeat(32),expires_at_ms:Date.now()+90_000,selection:1,
   source_sha256:'a'.repeat(64),width_px:160,height_px:90,count:1,
   sujets:[{numero:1,image_data:null,codes:[],
     zones_a_examiner:[],zones_non_affichees:0}]};
 b.MockBroadcastChannel.instances[0].sendToReceiver(report);
 const first=b.find('realSubjectsGrid').children[0];
 const proposal=first.children.filter(x=>x.tagName==='button')[1];
 assert.ok(proposal,'fresh report has proposal action');
 const callbacks=[...b.timeouts.values()];
 assert.equal(callbacks.length,1,'one actual session expiration callback');
 b.advance(90_100);
 callbacks[0]();
 assert.match(b.find('realSubjectsStatus').textContent,/expirée/);
 assert.equal(b.find('realSubjectsGrid').children.length,1,'genuine thumbnail remains available');
 assert.equal(b.find('realSubjectsGrid').children[0].children.filter(x=>x.tagName==='button').length,1,
   'propose control is no longer rendered');
 await proposal.fire('click'); // stale detached button cannot send
 assert.equal(b.MockBroadcastChannel.instances.length,1);
 assert.match(b.find('realSubjectsStatus').textContent,/Session expirée/);
});


test('verified project mask offers one confirmed persistent identity write',async()=>{
 const b=browser();b.window.location.protocol='http:';
 await b.find('receiveSubjects').fire('click');
 const report={kind:'smartsvg:subjects:g33b',version:1,
  node_id:17,session_id:'4'.repeat(32),expires_at_ms:Date.now()+90_000,selection:1,
  source_sha256:'a'.repeat(64),width_px:160,height_px:90,count:1,
  project_name:'subjects',project_sha256:'b'.repeat(64),
  mask_catalog:{version:1,project_name:'subjects',project_sha256:'b'.repeat(64),
   source_sha256:'a'.repeat(64),source_id:'source-original',
   width_px:160,height_px:90,count:1,items:[{
    mask_index:0,mask_id:'base-mask-00',mask_sha256_float32:'c'.repeat(64),
    has_foreground:true,subject_id:null,accessory_ids:[],subject_ambiguous:false,
   }]},
  sujets:[{numero:1,image_data:null,codes:[],zones_a_examiner:[],zones_non_affichees:0}]};
 b.MockBroadcastChannel.instances[0].sendToReceiver(report);
 const card=b.find('realSubjectsGrid').children[0];
 const register=card.children.find(x=>x.tagName==='button'&&
   /Enregistrer l’identité/.test(x.textContent));
 assert.ok(register,'verified mask without Subject exposes explicit registration');
 const first=register.fire('click'),second=register.fire('click');
 await Promise.all([first,second]);
 assert.equal(b.confirmations.length,1,'double click cannot request two confirmations');
 assert.equal(b.apiCalls.length,1,'double click cannot issue two writes');
 assert.equal(b.apiCalls[0].route,'/smartsvg/g22/subject/identity');
 assert.match(b.find('realSubjectsStatus').textContent,/subject-e{32}/);
 assert.match(b.find('realSubjectsStatus').textContent,/révision f{12}/);
 assert.equal(register.disabled,true,'old revision cannot be written again');
 const oldProposal=card.children.find(x=>x.tagName==='button'&&
   /Proposer le sujet/.test(x.textContent));
 assert.equal(oldProposal.disabled,true,'project revision changed: stale proposal is disabled');
 await oldProposal.fire('click');
 assert.equal(b.MockBroadcastChannel.instances.length,1,
   'no stale proposal can be sent after a successful identity write');
});


test('timeout and cancellation copy does not claim that the server did not commit',()=>{
 assert.doesNotMatch(page,/aucune identité confirmée/i);
 assert.match(page,/état du projet.*vérifier/i);
});

function registrationReport(){
 return {kind:'smartsvg:subjects:g33b',version:1,
  node_id:17,session_id:'4'.repeat(32),expires_at_ms:Date.now()+90_000,selection:1,
  source_sha256:'a'.repeat(64),width_px:160,height_px:90,count:2,
  project_name:'subjects',project_sha256:'b'.repeat(64),
  mask_catalog:{version:1,project_name:'subjects',project_sha256:'b'.repeat(64),
   source_sha256:'a'.repeat(64),source_id:'source-original',
   width_px:160,height_px:90,count:2,items:[0,1].map(i=>({
    mask_index:i,mask_id:'base-mask-'+String(i).padStart(2,'0'),
    mask_sha256_float32:(i?'d':'c').repeat(64),
    has_foreground:true,subject_id:null,accessory_ids:[],subject_ambiguous:false,
   }))},
  sujets:[1,2].map(numero=>({numero,image_data:null,codes:[],
   zones_a_examiner:[],zones_non_affichees:0}))};
}

test('writing one subject seals other stale subject actions until new inspection',async()=>{
 const b=browser();b.window.location.protocol='http:';
 await b.find('receiveSubjects').fire('click');
 b.MockBroadcastChannel.instances[0].sendToReceiver(registrationReport());
 const cards=b.find('realSubjectsGrid').children;
 const writes=cards.map(card=>card.children.find(x=>x.tagName==='button'&&
   /Enregistrer l’identité/.test(x.textContent)));
 assert.equal(writes.length,2);
 await writes[0].fire('click');
 assert.equal(b.apiCalls.length,1);
 assert.equal(writes[1].disabled,true,'second subject uses a now-obsolete project SHA');
 await writes[1].fire('click');
 assert.equal(b.apiCalls.length,1,'second stale write cannot reach server');
 assert.match(b.find('realSubjectsStatus').textContent,/Diagnostic périmé/);
});

test('uncertain write response seals registration controls pending reinspection',async()=>{
 const b=browser();b.window.location.protocol='http:';
 b.api.fetchApi=async(route,options)=>{
   b.apiCalls.push({route,options});
   throw Error('SUBJECT_IDENTITY_TIMEOUT');
 };
 await b.find('receiveSubjects').fire('click');
 b.MockBroadcastChannel.instances[0].sendToReceiver(registrationReport());
 const card=b.find('realSubjectsGrid').children[0];
 const button=card.children.find(x=>x.tagName==='button'&&
   /Enregistrer l’identité/.test(x.textContent));
 await button.fire('click');
 assert.equal(b.apiCalls.length,1);
 assert.equal(button.disabled,true,'timeout may mean server committed: no retry on stale revision');
 assert.match(b.find('realSubjectsStatus').textContent,/état du projet à vérifier/);
 await button.fire('click');
 assert.equal(b.apiCalls.length,1);
});
