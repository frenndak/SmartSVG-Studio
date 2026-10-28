import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const source=fs.readFileSync(new URL('../web/js/smartsvg_subject_inspector_v21154.js',import.meta.url),'utf8').replace(/^import\s+\{app\}.*;\s*$/m,'').replace(/^import\s+\{api\}.*;\s*$/m,'').replace(/^import\s+\{validProjectName[^;]+;\s*$/m,'');
const png='data:image/png;base64,QUJDRA==';
function fixture(){
  let extension;
  const doc={createElement(tag){
    return {tag,style:{},children:[],attributes:{},events:{},textContent:'',disabled:false,
      append(...x){this.children.push(...x);},replaceChildren(...x){this.children=[...x];},
      setAttribute(k,v){this.attributes[k]=v;},addEventListener(k,fn){this.events[k]=fn;}};
  }};
  vm.runInNewContext(source,{document:doc,app:{registerExtension:x=>extension=x},console});
  const node={comfyClass:'SmartSVGChooseSubjectV21154',widgets:[{name:'numero_sujet',value:1}],
    size:[300,200],addDOMWidget(){},setDirtyCanvas(){}};
  extension.nodeCreated(node);
  return node;
}
const location=(type,box,src)=>({type,bbox_apercu_88px:box,bbox_source_px:src,surface_px:1});
test('subject islands are shown on thumbnails without changing selected mask',()=>{
  const node=fixture();
  const zones=[location('MICRO_FRAGMENT',[12,20,13,21],[40,60,41,61]),
    location('FRAGMENT_SEPARE',[56,32,62,38],[100,90,110,100])];
  node.onExecuted({smartsvg_subjects_v21154:[{selection:1,sujets:[
    {numero:1,image_data:png,codes:['FRAGMENTS_DETACHES'],zones_a_examiner:zones,zones_non_affichees:7},
  ]}]});
  const root=node._ss21154Inspector.root;
  const card=root.children[3].children[0];
  const overlay=card.children[0];
  assert.equal(overlay.tag,'span');
  assert.equal(overlay.children[0].tag,'img');
  assert.equal(overlay.children.length,3);
  assert.match(overlay.children[1].style.cssText,/pointer-events:none/);
  assert.equal(overlay.children[1].attributes['aria-hidden'],'true');
  assert.match(card.attributes['aria-label'],/x40–41, y60–61/);
  assert.match(card.children[3].textContent,/\+7 autre/);
  assert.equal(node.widgets[0].value,1);
});
test('untrusted malformed regions are ignored and never parsed as markup',()=>{
  const node=fixture();
  const zones=[location('MICRO_FRAGMENT',[NaN,-2,500,500],[1,2,3,4]),
    location('FRAGMENT_SEPARE',[1,1,3,4],[1,2,1,7]),
    location('INJECT_HTML',[0,0,88,88],[1,2,3,4])];
  node.onExecuted({smartsvg_subjects_v21154:[{selection:1,sujets:[
    {numero:1,image_data:png,codes:[],zones_a_examiner:zones,zones_non_affichees:-99},
  ]}]});
  const card=node._ss21154Inspector.root.children[3].children[0];
  assert.equal(card.children[0].children.length,1);
  assert.doesNotMatch(card.attributes['aria-label'],/INJECT_HTML/);
  assert.match(card.attributes['aria-label'],/0 zone/);
});
test('pre-V21.15.5 reports retain their selection buttons',()=>{
  const node=fixture();
  node.onExecuted({smartsvg_subjects_v21154:[{selection:1,sujets:[
    {numero:1,image_data:png,codes:[]},
    {numero:2,image_data:png,codes:['TOUCHE_BORD_IMAGE']},
  ]}]});
  const cards=node._ss21154Inspector.root.children[3].children;
  cards[1].events.click();
  assert.equal(node.widgets[0].value,2);
  assert.equal(cards[1].attributes['aria-pressed'],'true');
});
