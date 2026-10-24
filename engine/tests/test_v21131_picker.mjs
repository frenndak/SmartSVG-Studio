import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';import vm from 'node:vm';
const source=fs.readFileSync(new URL('../web/js/smartsvg_subject_picker_v21131.js',import.meta.url),'utf8').replace(/^import\s+\{app\}.*;\s*$/m,'');
function setup(){
 let extension;
 const app={registerExtension:e=>extension=e};
 const document={createElement(tag){const obj={tag,style:{},children:[],textContent:'',events:{},append(...a){this.children.push(...a);},replaceChildren(...a){this.children=[...a];},addEventListener(k,cb){this.events[k]=cb;}};return obj;}};
 vm.runInNewContext(source,{app,document,console});
 const node={comfyClass:'SmartSVGChooseSubjectV21131',widgets:[{name:'numero_sujet',value:1}],size:[290,200],addDOMWidget(...args){this.args=args;return {}}};
 extension.nodeCreated(node);return node;
}
test('picker uses nonserialized widget and manual re-run',()=>{
 const node=setup();assert.ok(node._ss21131Picker);assert.equal(node.args[3].serialize,false);
 node.onExecuted({smartsvg_subjects_v21131:[{selection:1,sujets:[{numero:1,image_data:'data:image/png;base64,QQ=='},{numero:2,image_data:'data:image/png;base64,QQ=='}]}]});
 const layout=node._ss21131Picker.root.children[2];assert.equal(layout.children.length,2);
 layout.children[1].events.click();assert.equal(node.widgets[0].value,2);
 assert.match(node._ss21131Picker.root.children[1].textContent,/Relancer/);
});
test('picker ignores malformed image urls',()=>{
 const node=setup();node.onExecuted({smartsvg_subjects_v21131:[{selection:1,sujets:[{numero:1,image_data:'https://bad.example/'},{numero:2,image_data:'data:image/png;base64,QQ=='}]}]});
 assert.equal(node._ss21131Picker.root.children[2].children.length,1);
});
test('older selectors are not modified',()=>{
 let ext;vm.runInNewContext(source,{app:{registerExtension:v=>ext=v},console,document:{createElement(){throw Error('unwanted DOM')}}});
 ext.nodeCreated({comfyClass:'SmartSVGChooseSubjectV2113'});
});
