import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizeMeta,previewUrl,encodeDocument,decodeDocument} from '../web/js/smartsvg_editor_model_v216.mjs';
const t='abcabcabcabcabcabcabcabc';
const ref=(name)=>({filename:`ed_${t}_${name}.png`,subfolder:'SmartSVG_Studio_Editor',type:'output'});
const meta={version:1,width:800,height:600,count:2,source:'a'.repeat(64),
 preview_width:760,preview_height:570,image:ref('image'),masks:[ref('mask00'),ref('mask01')]};
test('accepted metadata and secure prefixed /view URL',()=>{
 assert.deepEqual(normalizeMeta({smartsvg_editor:[meta]}),meta);
 const result=previewUrl(meta.image,'https://demo.test/proxy/8188/','/proxy/8188/view');
 assert.match(result,/\/proxy\/8188\/view\?/);
 assert.match(result,/subfolder=SmartSVG_Studio_Editor/);
});
test('reject cross-session references, filenames, wrong dimensions and URLs',()=>{
 assert.equal(normalizeMeta({smartsvg_editor:[{...meta,source:'abc'}]}),null);
 assert.equal(normalizeMeta({smartsvg_editor:[{...meta,count:3}]}),null);
 assert.equal(normalizeMeta({smartsvg_editor:[{...meta,masks:[ref('mask00'),ref('mask01'),ref('mask02')] }]}),null);
 assert.equal(normalizeMeta({smartsvg_editor:[{...meta,masks:[ref('mask00'),ref('mask09')] }]}),null);
 assert.equal(normalizeMeta({smartsvg_editor:[{...meta,width:500000000}]}),null);
 assert.equal(previewUrl({...ref('image'),filename:'../../secret.png'},'https://demo.test/','/view'),null);
});
test('document round trips across reload, with real persisted strokes',()=>{
 const marks=[{object:1,mode:'erase',radius:.013,points:[[.25,.5],[.4,.7]]}];
 const encoded=encodeDocument(meta,marks);
 assert.deepEqual(decodeDocument(meta,encoded),marks);
 assert.deepEqual(decodeDocument(meta,''),[]);
 assert.throws(()=>decodeDocument({...meta,source:'b'.repeat(64)},encoded),/source a changé/);
});
test('prevent malformed/oversized strokes and executable injection',()=>{
 assert.throws(()=>encodeDocument(meta,[{object:0,mode:'add',radius:Infinity,points:[[.5,.5]]}]),/invalide/);
 assert.throws(()=>encodeDocument(meta,[{object:0,mode:'add',radius:.05,points:[[-1,.5]]}]),/invalide/);
 assert.throws(()=>encodeDocument(meta,[{object:0,mode:'add',radius:.05,points:[[.5,.5]]}].map(s=>({...s,object:4}))),/invalide/);
 assert.throws(()=>encodeDocument(meta,Array.from({length:401},()=>({object:0,mode:'add',radius:.03,points:[[.1,.1]]}))),/Maximum 400/);
 assert.throws(()=>encodeDocument(meta,[{object:0,mode:'add',radius:.03,points:Array.from({length:1501},()=>[.2,.2])}]),/invalide/);
});
