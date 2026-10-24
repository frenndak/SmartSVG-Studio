import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as model from '../web/js/smartsvg_ui_model_v2151.mjs';
const root=path.dirname(fileURLToPath(import.meta.url));
const ref={filename:'qa_global_abcd1234567890.png',subfolder:'SmartSVG_Studio_Previews',type:'output'};

test('reverse proxy prefix retained by route builder',()=>{
 const url=model.previewUrl(ref,'https://host.local/comfyui/','/comfyui/view');
 assert.equal(new URL(url).pathname,'/comfyui/view');
 assert.equal(new URL(url).searchParams.get('filename'),ref.filename);
});
test('absolute host route retains gateway prefix',()=>{
 const url=model.previewUrl(ref,'https://host.local/comfyui/','https://host.local/proxy/8188/view');
 assert.equal(new URL(url).pathname,'/proxy/8188/view');
});
test('missing api route fails closed, no guessed URLs',()=>{
 assert.equal(model.previewUrl(ref,'https://host.local/comfyui/'),null);
});
test('arbitrary URL is not a valid ComfyUI preview ref',()=>{
 assert.equal(model.previewUrl({filename:'../../private.png',subfolder:ref.subfolder,type:'output'},'https://host.local','/comfyui/view'),null);
});
test('only bounded preview metadata is exposed',()=>{
 const res=model.normalizePreviews({smartsvg_previews:Array.from({length:90},(_,i)=>({...ref,filename:`qa_global_${String(i).padStart(14,'0')}.png`}))});
 assert.equal(res.length,7);
});
test('new extension imports official ComfyUI API URL builder',()=>{
 const src=fs.readFileSync(path.join(root,'../web/js/smartsvg_ui_v2151.js'),'utf8');
 assert.match(src,/import \{ api \} from "\.\.\/\.\.\/scripts\/api\.js"/);
 assert.match(src,/api\.apiURL\('\/view'\)/);
 assert.doesNotMatch(src,/innerHTML|outerHTML|eval\(|new Function\(/);
});
test('new extension distinguishes current node from historical',()=>{
 const src=fs.readFileSync(path.join(root,'../web/js/smartsvg_ui_v2151.js'),'utf8');
 assert.match(src,/SmartSVGExpressV2151/);
 assert.match(src,/if \(!report\)/);
 assert.match(src,/widget\.options/);
});
