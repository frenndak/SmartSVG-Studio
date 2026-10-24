import test from 'node:test';
import assert from 'node:assert/strict';
import {validProjectName,createProjectPanel,projectError} from '../web/js/smartsvg_project_panel_g22.mjs';

class Element {
  constructor(tag){
    this.tagName=tag;this.children=[];this.textContent='';this.value='';
    this.disabled=false;this.hidden=false;this.type='';this.src='';
    this.attrs={};this.events={};this.files=[];
  }
  append(...items){this.children.push(...items);}
  appendChild(item){this.children.push(item);return item;}
  setAttribute(name,value){this.attrs[name]=value;}
  removeAttribute(name){delete this.attrs[name];if(name==='src')this.src='';}
  addEventListener(type,callback){(this.events[type]??=[]).push(callback);}
  async trigger(type){for(const cb of this.events[type]||[])await cb({target:this});}
}
function all(el){return [el,...el.children.flatMap(all)]}
const makeResponse=(data,status=200)=>({
  ok:status>=200&&status<300,json:async()=>data,
});
function harness(){
  let main={
    name:'snails',status:'PROJECT_HEALTHY',sha256:'a'.repeat(64),
    recoverable:false,
    document:{profile:'Planche - 12 images (4x3)',width_mm:40,dpi:300,
      notes:'départ',stage:'source_imported_only'},
  };
  const calls=[];
  const api={
    apiURL:route=>'/proxy/8188'+route,
    async fetchApi(route,options){
      calls.push({route,options});
      if(route.startsWith('/smartsvg/g22/project?'))return makeResponse({ok:true,project:main});
      if(route.endsWith('/create')){
        return makeResponse({ok:true,result:{name:'snails',status:'created'}});
      }
      if(route.endsWith('/notes')){
        main={...main,sha256:'b'.repeat(64),document:{...main.document,notes:'nouveau'}};
        return makeResponse({ok:true,result:{status:'updated'}});
      }
      if(route.endsWith('/mask') && options?.method==='POST'){
        main={...main,sha256:'d'.repeat(64),subjects:[{subject_id:'sujet_01',bbox_px:[2,3,5,4]}],mask_count:1};
        return makeResponse({ok:true,result:{status:'mask_saved',certified:false}});
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
  const inputs=els.filter(x=>x.tagName==='input');
  const maskFile=inputs.filter(x=>x.type==='file')[1];
  const subject=inputs.filter(x=>x.type==='text')[1];
  const maskPreview=els.filter(x=>x.tagName==='img')[1];
  const notes=els.find(x=>x.tagName==='textarea');
  const preview=els.find(x=>x.tagName==='img');
  const status=els.find(x=>x.attrs.role==='status');
  return {root,buttons,name,file,notes,preview,maskPreview,maskFile,subject,status,calls,
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
  assert.equal(h.buttons[4].disabled,true);
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


test('subject mask upload uses fresh revision and does not mutate the graph',async()=>{
  const h=harness();h.name.value='snails';
  await h.buttons[1].trigger('click');
  assert.equal(h.buttons[4].disabled,false);
  const mask={name:'mask.png',size:240,type:'image/png'};
  h.subject.value='sujet_01';
  h.maskFile.files=[mask];
  await h.buttons[4].trigger('click');
  const action=h.calls.find(x=>x.route==='/smartsvg/g22/mask' && x.options?.method==='POST');
  assert.ok(action);
  const fields=action.options.body.rows;
  assert.equal(fields.find(x=>x[0]==='subject_id')[1],'sujet_01');
  assert.equal(fields.find(x=>x[0]==='mask')[1],mask);
  assert.equal(fields.find(x=>x[0]==='expected_sha256')[1],'a'.repeat(64));
  assert.equal(action.options.headers['X-SmartSVG-UI'],'1');
  assert.match(h.status.textContent,/non certifiée/);
  assert.match(h.maskPreview.src,/\/proxy\/8188\/smartsvg\/g22\/mask\?name=snails&subject_id=sujet_01/);
});

test('invalid subject mask name or file never sends a request',async()=>{
  const h=harness();h.name.value='snails';
  await h.buttons[1].trigger('click');
  const original=h.calls.length;
  h.subject.value='../secrets';h.maskFile.files=[{name:'mask.png',size:200}];
  await h.buttons[4].trigger('click');
  assert.equal(h.calls.length,original);
  assert.match(h.status.textContent,/Identifiant/);
  h.subject.value='sujet_01';h.maskFile.files=[{name:'mask.svg',size:200}];
  await h.buttons[4].trigger('click');
  assert.equal(h.calls.length,original);
  assert.match(h.status.textContent,/PNG/);
});
