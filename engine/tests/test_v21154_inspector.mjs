import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const script=fs.readFileSync(new URL('../web/js/smartsvg_subject_inspector_v21154.js',import.meta.url),'utf8').replace(/^import\s+\{app\}.*;\s*$/m,'').replace(/^import\s+\{api\}.*;\s*$/m,'').replace(/^import\s+\{validProjectName[^;]+;\s*$/m,'');
const png='data:image/png;base64,QUJDRA==';
function setup(){
 let extension;
 const document={createElement(tag){
   return {tag,style:{},children:[],textContent:'',attributes:{},events:{},disabled:false,
     append(...items){this.children.push(...items);},
     replaceChildren(...items){this.children=[...items];},
     setAttribute(key,value){this.attributes[key]=value;},
     addEventListener(key,callback){this.events[key]=callback;}};
 }};
 const app={registerExtension:ext=>{extension=ext;}};
 vm.runInNewContext(script,{document,app,console});
 const node={comfyClass:'SmartSVGChooseSubjectV21154',size:[300,200],widgets:[{name:'numero_sujet',value:1}],
   addDOMWidget(...args){this.args=args;return {};},setDirtyCanvas(){this.dirty=true;}};
 extension.nodeCreated(node);
 return node;
}
test('inspector renders subject-specific warnings and requires a second run',()=>{
 const node=setup();
 const items=[{numero:1,image_data:png,codes:['FRAGMENTS_DETACHES','TOUCHE_BORD_IMAGE']},
              {numero:2,image_data:png,codes:[]},
              {numero:3,image_data:null,codes:['MASQUE_VIDE']}];
 node.onExecuted({smartsvg_subjects_v21154:[{selection:1,sujets:items}]});
 const root=node._ss21154Inspector.root;
 assert.equal(node.args[3].serialize,false);
 assert.equal(root.children[3].children.length,3);
 const [one,two,three]=root.children[3].children;
 assert.match(one.attributes['aria-label'],/Fragments détachés/);
 assert.match(one.attributes['aria-label'],/Touche un bord/);
 assert.equal(three.disabled,true);
 assert.equal(one.attributes['aria-pressed'],'true');
 two.events.click();
 assert.equal(node.widgets[0].value,2);
 assert.equal(one.attributes['aria-pressed'],'false');
 assert.equal(two.attributes['aria-pressed'],'true');
 assert.match(root.children[1].textContent,/Relancer/);
 assert.equal(node.dirty,true);
});
test('external images and unknown codes are never presented as executable content',()=>{
 const node=setup();
 const items=[{numero:1,image_data:'https://example.test/img.png',codes:['ARBITRARY']},
              {numero:2,image_data:'data:image/svg+xml;base64,PHN2Zz4=',codes:['MASQUE_VIDE']},
              {numero:3,image_data:png,codes:['MICRO_FRAGMENTS']}];
 node.onExecuted({smartsvg_subjects_v21154:[{selection:3,sujets:items}]});
 const nodes=node._ss21154Inspector.root.children[3].children;
 assert.equal(nodes.length,3);
 assert.equal(nodes[0].disabled,true);
 assert.equal(nodes[1].disabled,true);
 assert.match(nodes[2].attributes['aria-label'],/Petits îlots/);
});
test('older nodes remain isolated and updates can be missing',()=>{
 const node=setup();node.onExecuted({});
 assert.match(node._ss21154Inspector.root.children[2].textContent,/Aucun diagnostic/);
 let extension;
 vm.runInNewContext(script,{app:{registerExtension:x=>extension=x},console,document:{createElement(){throw Error('unexpected')}}});
 extension.nodeCreated({comfyClass:'SmartSVGChooseSubjectV21131'});
});
