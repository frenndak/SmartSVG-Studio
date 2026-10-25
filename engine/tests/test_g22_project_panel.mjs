import test from 'node:test';
import assert from 'node:assert/strict';
import {validProjectName,createProjectPanel,projectError} from '../web/js/smartsvg_project_panel_g22.mjs';

class Element {
  constructor(tag){
    this.tagName=tag;this.children=[];this.textContent='';this.value='';
    this.disabled=false;this.hidden=false;this.type='';this.src='';this.dataset={};this.style={};
    this.attrs={};this.events={};this.files=[];
  }
  append(...items){this.children.push(...items);}
  appendChild(item){this.children.push(item);return item;}
  replaceChildren(...items){this.children=[...items];}
  setAttribute(name,value){this.attrs[name]=value;}
  removeAttribute(name){delete this.attrs[name];if(name==='src')this.src='';}
  addEventListener(type,callback){(this.events[type]??=[]).push(callback);}
  async trigger(type){for(const cb of this.events[type]||[])await cb({target:this});}
}
function all(el){return [el,...el.children.flatMap(all)]}
const makeResponse=(data,status=200)=>({
  ok:status>=200&&status<300,json:async()=>data,
});
function harness(options={}){
  let main={
    name:'snails',status:'PROJECT_HEALTHY',sha256:'a'.repeat(64),
    source_count:1,recoverable:false,
    document:{profile:'Planche - 12 images (4x3)',width_mm:40,dpi:300,
      notes:'départ',stage:'source_imported_only'},
  };
  const calls=[];
  const api={
    apiURL:route=>'/proxy/8188'+route,
    async fetchApi(route,options){
      calls.push({route,options});
      if(route.startsWith('/smartsvg/g22/project?')){
        if(options.inspectGate)await options.inspectGate();
        return makeResponse({ok:true,project:main});
      }
      if(route.endsWith('/create')){
        return makeResponse({ok:true,result:{name:'snails',status:'created'}});
      }
      if(route.endsWith('/notes')){
        main={...main,sha256:'b'.repeat(64),document:{...main.document,notes:'nouveau'}};
        return makeResponse({ok:true,result:{status:'updated'}});
      }
      if(route.endsWith('/restore')){
        main={...main,status:'PROJECT_HEALTHY',recoverable:false,sha256:'c'.repeat(64)};
        return makeResponse({ok:true,result:{status:'restored_from_previous'}});
      }
      return makeResponse({ok:false,error_code:'INVALID_PROJECT_NAME'},400);
    }
  };
  globalThis.document={createElement:type=>new Element(type)};
  globalThis.window={confirm:()=>true};
  Object.defineProperty(globalThis,'navigator',{configurable:true,value:{clipboard:{writeText:async()=>{}}}});
  globalThis.FormData=class{
    constructor(){this.rows=[];}
    append(k,v){this.rows.push([k,v]);}
  };
  const root=createProjectPanel(api,()=>({profile:'Planche - 12 images (4x3)',
    width_mm:40,dpi:300}));
  const els=all(root);
  const buttons=els.filter(x=>x.tagName==='button');
  const name=els.find(x=>x.tagName==='input'&&x.type==='text');
  const file=els.find(x=>x.tagName==='input'&&x.type==='file');
  const notes=els.find(x=>x.tagName==='textarea');
  const preview=els.find(x=>x.tagName==='img');
  const status=els.find(x=>x.attrs.role==='status');
  const resume=els.find(x=>x.tagName==='details');
  const revision=els.find(x=>x.attrs['aria-label']==='Empreinte de projet à copier dans le nœud G2.4');
  return {root,buttons,name,file,notes,preview,status,resume,revision,calls,
    setMain:value=>{main=value},getMain:()=>main};
}
test('project names never permit traversal, separators, or reserved names',()=>{
  for(const name of ['../a','/etc/passwd','C:\\x','a.b','a/b','', 'école',
                     'a'.repeat(49),'foo_previous'])
    assert.equal(validProjectName(name),false,name);
  for(const name of ['Snails12','x_a-4','A'])
    assert.equal(validProjectName(name),true,name);
});
test('creation uses chosen local PNG, historical settings and custom CSRF header',async()=>{
  const h=harness();
  assert.equal(h.buttons.length,5);
  assert.equal(h.buttons[2].disabled,true);
  assert.equal(h.buttons[3].disabled,true);
  h.name.value='snails';
  const file={name:'image.png',size:100,type:'image/png'};
  h.file.files=[file];
  await h.buttons[0].trigger('click');
  assert.equal(h.calls[0].route,'/smartsvg/g22/create');
  assert.equal(h.calls[0].options.method,'POST');
  assert.equal(h.calls[0].options.headers['X-SmartSVG-UI'],'1');
  assert.equal(h.calls[0].options.body.rows.find(x=>x[0]==='image')[1],file);
  assert.equal(h.calls[0].options.body.rows.find(x=>x[0]==='profile')[1],
               'Planche - 12 images (4x3)');
  assert.equal(h.calls[1].route,'/smartsvg/g22/project?name=snails');
  assert.equal(h.preview.src,'/proxy/8188/smartsvg/g22/source?name=snails');
  assert.equal(h.buttons[2].disabled,false);
  assert.equal(h.buttons[3].disabled,true);
  assert.match(h.status.textContent,/non certifiée/);
});
test('saving notes preserves expected revision hash and does not alter png',async()=>{
  const h=harness();h.name.value='snails';
  await h.buttons[1].trigger('click');
  h.notes.value='nouveau';
  await h.buttons[2].trigger('click');
  const post=h.calls.find(x=>x.route.endsWith('/notes'));
  assert.equal(post.options.body.rows.find(x=>x[0]==='expected_sha256')[1],'a'.repeat(64));
  assert.equal(h.getMain().document.notes,'nouveau');
  assert.match(h.status.textContent,/Notes enregistrées/);
});
test('recovery is blocked unless confirmed in browser and carries fresh fingerprint',async()=>{
  const h=harness();
  h.name.value='snails';
  h.setMain({...h.getMain(),status:'PROJECT_RECOVERABLE',
    sha256:undefined,recoverable:true,recovery_sha256:'b'.repeat(64),document:undefined});
  await h.buttons[1].trigger('click');
  assert.equal(h.buttons[3].disabled,false);
  globalThis.window.confirm=()=>false;
  await h.buttons[3].trigger('click');
  assert.equal(h.calls.some(x=>x.route.endsWith('/restore')),false);
  globalThis.window.confirm=()=>true;
  await h.buttons[3].trigger('click');
  const req=h.calls.find(x=>x.route.endsWith('/restore'));
  assert.equal(req.options.body.rows.find(x=>x[0]==='expected_recovery_sha256')[1],'b'.repeat(64));
  assert.equal(req.options.body.rows.find(x=>x[0]==='confirmed')[1],'yes');
});
test('invalid project name does not call backend',async()=>{
  const h=harness();h.name.value='../private';
  await h.buttons[1].trigger('click');
  assert.equal(h.calls.length,0);
  assert.match(h.status.textContent,/Nom invalide/);
});
test('no direct queue/automatic workflow mutation in project controls',()=>{
  const h=harness();
  assert.equal(h.root.attrs['aria-label'],'Projet SmartSVG sauvegarde et récupération');
  assert.ok(projectError('BACKUP_CONFLICT').includes('aucune donnée'));
  assert.ok(all(h.root).some(el=>el.textContent.includes('ne restaure pas encore')));
});

test('guided steps explicitly distinguish full mask snapshots and brush corrections',async()=>{
  const h=harness();
  assert.equal(h.resume.dataset.state,'EMPTY');
  h.name.value='snails';
  await h.buttons[1].trigger('click');
  assert.equal(h.resume.dataset.state,'SOURCE_ONLY');
  assert.equal(h.revision.value,'a'.repeat(64));
  assert.equal(h.resume.open,false);
  const list=all(h.resume).filter(x=>x.tagName==='li');
  assert.equal(list.length,4);
  assert.match(list[1].textContent,/à compléter/);
  assert.match(list[3].textContent,/manuel/);
  h.setMain({...h.getMain(),base_masks:{
    exact_float32:true,count:2,dimensions_px:[12,9],
    editor_fingerprint:'b'.repeat(64),
    source_fingerprint:'c'.repeat(64)},
    editor_session:{available:true,count:2,stroke_count:3,
      source_fingerprint:'b'.repeat(64)}});
  await h.buttons[1].trigger('click');
  assert.equal(h.resume.dataset.state,'COMPLETE_MANUAL');
  assert.equal(h.resume.open,true);
  assert.match(all(h.resume).find(x=>x.attrs.role==='status').textContent,/Aucune découpe Cricut certifiée/);
});
test('recovery states are explicit and guarded by verified fallback fingerprint',async()=>{
  const h=harness();
  h.name.value='snails';
  h.setMain({name:'snails',status:'PROJECT_RECOVERABLE',
    recoverable:true,recovery_sha256:'d'.repeat(64)});
  await h.buttons[1].trigger('click');
  assert.equal(h.resume.dataset.state,'RECOVERABLE');
  assert.equal(h.resume.open,true);
  assert.equal(h.buttons[3].disabled,false);
  assert.equal(h.buttons[4].disabled,true);
  h.setMain({name:'snails',status:'PROJECT_RECOVERABLE',
    recoverable:true,recovery_sha256:'not-sha'});
  await h.buttons[1].trigger('click');
  assert.equal(h.resume.dataset.state,'UNAVAILABLE');
  assert.equal(h.buttons[3].disabled,true);
});
test('copy project revision uses an explicit click and is disabled without inspection',async()=>{
  const h=harness();
  assert.equal(h.buttons[4].disabled,true);
  h.name.value='snails';
  await h.buttons[1].trigger('click');
  assert.equal(h.buttons[4].disabled,false);
  let copied=null;
  Object.defineProperty(globalThis,'navigator',{configurable:true,value:{
    clipboard:{writeText:async s=>{copied=s;}}
  }});
  await h.buttons[4].trigger('click');
  assert.equal(copied,'a'.repeat(64));
  h.name.value='new_project';await h.name.trigger('input');
  assert.equal(h.buttons[4].disabled,true);
  assert.equal(h.resume.dataset.state,'EMPTY');
  assert.equal(h.revision.value,'');
});
test('server refusal never leaves a usable revision after an unsuccessful inspection',async()=>{
  const h=harness();
  h.name.value='../invalid';
  await h.buttons[1].trigger('click');
  assert.equal(h.resume.dataset.state,'ERROR');
  assert.equal(h.buttons[3].disabled,true);
  assert.equal(h.buttons[4].disabled,true);
  assert.equal(h.preview.hidden,true);
});

test('changing name during an async inspection never repaints the wrong project',async()=>{
  let release;
  const gate=new Promise(resolve=>{release=resolve});
  const h=harness({inspectGate:()=>gate});
  h.name.value='snails';
  const pending=h.buttons[1].trigger('click');
  assert.equal(h.resume.dataset.state,'LOADING');
  h.name.value='another';await h.name.trigger('input');
  assert.equal(h.resume.dataset.state,'EMPTY');
  release();await pending;
  assert.equal(h.resume.dataset.state,'EMPTY');
  assert.equal(h.buttons[2].disabled,true);
  assert.equal(h.buttons[4].disabled,true);
  assert.equal(h.preview.hidden,true);
  assert.equal(h.revision.value,'');
});
