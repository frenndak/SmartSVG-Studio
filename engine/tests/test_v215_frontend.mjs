import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { normalizePayload, normalizePreviews, previewUrl } from '../web/js/smartsvg_ui_model.mjs';
const root=path.dirname(fileURLToPath(import.meta.url));

test('empty responses remain inert',()=>{
  assert.equal(normalizePayload(null),null);
  assert.deepEqual(normalizePreviews({}),[]);
});
test('comfy payload decoded',()=>{
  const out=normalizePayload({smartsvg:[{objets_total:24,planches_total:2,alertes_total:3,provenance:'masques externes',
    objets:[{numero:1,largeur_mm:34.9,etat:'A_VERIFIER',alertes:[]}]}]});
  assert.equal(out.objets_total,24);assert.equal(out.planches_total,2);
  assert.equal(out.objets[0].largeur_mm,34.9);
});
test('payload bounded and typed',()=>{
  const out=normalizePayload({smartsvg:[{objets_total:9e99,alertes_total:-4,
    objets:Array.from({length:100},()=>({largeur_mm:NaN,alertes:['a'.repeat(400)]}))}]});
  assert.equal(out.objets_total,0);assert.equal(out.alertes_total,0);
  assert.equal(out.objets.length,32);assert.equal(out.objets[0].alertes[0].length,120);
});
test('arbitrary image URL cannot be used',()=>{
  assert.deepEqual(normalizePreviews({smartsvg_previews:[{filename:'../../private.png',type:'output',subfolder:'SmartSVG_Studio_Previews'}]}),[]);
  assert.equal(previewUrl({filename:'x.svg',type:'output',subfolder:'SmartSVG_Studio_Previews'},'http://localhost:8188'),null);
});
test('server-provided generated filename builds encoded official Comfy view URL',()=>{
  const ref={filename:'qa_global_abcd1234567890.png',subfolder:'SmartSVG_Studio_Previews',type:'output'};
  const target=previewUrl(ref,'http://localhost:8188/path');
  const url=new URL(target);
  assert.equal(url.pathname,'/view');assert.equal(url.searchParams.get('filename'),ref.filename);
});
test('script avoids user-controlled html injection',()=>{
  const code=fs.readFileSync(path.join(root,'../web/js/smartsvg_ui.js'),'utf8');
  assert.match(code,/app\.registerExtension/);
  assert.match(code,/widget\.serialize=false/);
  assert.doesNotMatch(code,/innerHTML|outerHTML|eval\(|new Function\(/);
});
test('frontend registration is scoped only to latest class',()=>{
  const code=fs.readFileSync(path.join(root,'../web/js/smartsvg_ui.js'),'utf8');
  assert.match(code,/SmartSVGExpressV215/);
  assert.match(code,/onExecuted/);
  assert.match(code,/NODE_IDS\.has/);
});
