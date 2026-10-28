import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const page=readFileSync(new URL('../engine/web/js/smartsvg_express_atelier_preview.html',import.meta.url),'utf8');
const script=page.match(/<script>\s*([\s\S]*?)<\/script>/i)?.[1];
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
  const window={location:{protocol:'file:'},addEventListener(){}};
  class MockBroadcastChannel{
    static instances=[];
    constructor(name){this.name=name;this.closed=false;MockBroadcastChannel.instances.push(this);}
    close(){this.closed=true;}
    sendToReceiver(data){this.onmessage?.({data});}
  }
  const timeouts=new Map();let nextTimeout=1;
  const globals={document,window,URL,Image,console,Set,Array,Math,Number,String,
    Object,Promise,BroadcastChannel:MockBroadcastChannel,
    setTimeout:(fn)=>{const id=nextTimeout++;timeouts.set(id,fn);return id;},
    clearTimeout:id=>timeouts.delete(id)};
  vm.runInNewContext(script,globals,{timeout:5000,
    importModuleDynamically:specifier=>{
      if(specifier!=='./smartsvg_subject_handoff_g33.mjs')
        throw Error('Unexpected dynamic import in test '+specifier);
      return import(new URL('../engine/web/js/smartsvg_subject_handoff_g33.mjs',import.meta.url));
    }});
  return {find,steps,navigation,revoked,created,Image,document,
    window,MockBroadcastChannel,timeouts};
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
  const png='data:image/png;base64,QUJDRA==';
  channel.sendToReceiver({kind:'smartsvg:subjects:g33b',version:1,
    selection:1,source_sha256:'a'.repeat(64),width_px:160,height_px:90,count:2,
    sujets:[
      {numero:1,image_data:png,codes:['FRAGMENTS_DETACHES'],
       zones_a_examiner:[{type:'FRAGMENT_SEPARE',bbox_source_px:[1,2,8,10],
         bbox_apercu_88px:[2,3,14,19]}],zones_non_affichees:0},
      {numero:2,image_data:png,codes:['MASQUE_VIDE'],
       zones_a_examiner:[],zones_non_affichees:0}
    ]});
  assert.equal(channel.closed,true);
  assert.equal(b.find('receiveSubjects').disabled,false);
  assert.equal(b.find('realSubjectsGrid').children.length,2);
  assert.match(b.find('realSubjectsStatus').textContent,/Diagnostic G2.6 reçu/);
  assert.match(b.find('realSubjectsSelection').textContent,/1 \/ 2 sujets/);
  const first=b.find('realSubjectsGrid').children[0];
  const button=first.children.find(x=>x.tagName==='button');
  assert.equal(button.attributes['aria-pressed'],'true');
  await button.fire('click');
  assert.match(b.find('realSubjectsSelection').textContent,/0 \/ 2 sujets/);
  // The old fictitious planche remains unchanged.
  assert.equal(b.find('count').textContent,'12 / 12');
  await b.find('clearSubjects').fire('click');
  assert.equal(b.find('realSubjectsGrid').children.length,0);
  assert.match(b.find('realSubjectsStatus').textContent,/Aucun masque ni projet modifié/);
});
test('real subjects receiver explicitly refuses file protocol',async()=>{
  const b=browser();
  await b.find('receiveSubjects').fire('click');
  assert.equal(b.MockBroadcastChannel.instances.length,0);
  assert.match(b.find('realSubjectsStatus').textContent,/ComfyUI sous HTTP local/);
});
