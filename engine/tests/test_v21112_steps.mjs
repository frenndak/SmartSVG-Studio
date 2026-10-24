import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const src=fs.readFileSync(new URL('../web/js/smartsvg_steps_v21112.js',import.meta.url),'utf8');
function setup(id='SmartSVGAutoExpressV21112'){
 let extension;
 const app={registerExtension(x){extension=x}};
 const document={createElement(tag){return {tag,style:{},children:[],textContent:'',append(...xs){this.children.push(...xs)}}}};
 vm.runInNewContext(src.replace(/^import\s+\{app\}.*;\s*$/m,''),{app,document,console});
 const node={comfyClass:id,widgets:[],size:[250,150],addDOMWidget(...args){this.args=args;return {options:{}}}};
 extension.nodeCreated(node);
 return {node,status:node._ss21112Guide.root.children[1],next:node._ss21112Guide.root.children[2]};
}
test('guide visible but never serialized into workflow',()=>{
 const {node,status}=setup();
 assert.ok(node.args);assert.equal(node.args[3].serialize,false);
 assert.match(status.textContent,/Importer/);
});
test('guide distinguishes local cutout, card and failure without false certification',()=>{
 const {node,status,next}=setup();
 node.onExecuted({smartsvg_steps_v21112:[{statut:'CONTROLE_LOCAL_OK_VERIFICATION_VISUELLE',sujets:12,cartes:0,action:'Vérifier dans Design Space'}]});
 assert.match(status.textContent,/12 silhouette/);assert.match(next.textContent,/Design Space/);
 node.onExecuted({smartsvg_steps_v21112:[{statut:'CARTE_RECTANGULAIRE',sujets:0,cartes:1,action:'Carte uniquement'}]});
 assert.match(status.textContent,/rectangulaire/);
 node.onExecuted({});assert.match(status.textContent,/Aucun nouveau résultat/);
});
test('guide ignores legacy nodes and keeps a fallback without browser API dependencies',()=>{
 let extension;const app={registerExtension(x){extension=x}};
 vm.runInNewContext(src.replace(/^import\s+\{app\}.*;\s*$/m,''),{app,document:{createElement(){throw Error('should not run')}},console});
 extension.nodeCreated({comfyClass:'SmartSVGAutoExpressV2111'});
});

test('V21.12.2 latest Express displays guide without extra workflow widgets',()=>{const {node,status}=setup('SmartSVGAutoExpressV21122');assert.equal(node.args[3].serialize,false);assert.match(status.textContent,/Importer/);});
