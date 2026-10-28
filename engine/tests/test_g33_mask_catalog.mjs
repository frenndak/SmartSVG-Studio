import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {makeVerifiedMaskCatalog,normalizeMaskCatalog,maskForSubject}
  from '../web/js/smartsvg_mask_link_g33e.mjs';
import {normalizeSubjectInspection}
  from '../web/js/smartsvg_subject_handoff_g33.mjs';
import {makeSelectionProposal}
  from '../web/js/smartsvg_subject_selection_g33c.mjs';

const source='a'.repeat(64),rev='b'.repeat(64);
const sha0='c'.repeat(64),sha1='d'.repeat(64);
const rows=()=>[
 {mask_index:0,mask_id:'base-mask-00',mask_sha256_float32:sha0,
  has_foreground:true,subject_id:null,accessory_ids:[],subject_ambiguous:false},
 {mask_index:1,mask_id:'base-mask-01',mask_sha256_float32:sha1,
  has_foreground:true,subject_id:null,accessory_ids:[],subject_ambiguous:false}
];
const project=()=>({name:'mes_sujets',status:'PROJECT_HEALTHY',sha256:rev,
 base_masks:{exact_float32:true,count:2,dimensions_px:[160,90],
  editor_fingerprint:source,
  mask_identity:{version:1,source_id:'source-01',
    identity_kind:'snapshot_position_plus_float32_digest',
    persistent_subject_ids:false,bindings:rows()}}});
const report=()=>({project_name:'mes_sujets',project_sha256:rev,
 source_sha256:source,width_px:160,height_px:90,count:2,selection:1,
 node_id:17,session_id:'4'.repeat(32),expires_at_ms:Date.now()+90_000,
 sujets:[1,2].map(numero=>({numero,image_data:null,codes:[],
  zones_a_examiner:[],zones_non_affichees:0}))});
const clone=value=>structuredClone(value);

test('ordered float32 catalog binds real mask IDs without inventing persistent subject IDs',()=>{
 const catalog=makeVerifiedMaskCatalog(project(),report());
 assert.ok(catalog);
 assert.equal(catalog.project_sha256,rev);
 assert.equal(catalog.source_sha256,source);
 assert.equal(catalog.source_id,'source-01');
 assert.deepEqual(catalog.items.map(r=>r.mask_id),['base-mask-00','base-mask-01']);
 assert.equal(maskForSubject(catalog,1).mask_sha256_float32,sha0);
 assert.equal(maskForSubject(catalog,2).mask_sha256_float32,sha1);
 assert.equal(maskForSubject(catalog,3),null);
 assert.equal(catalog.items[0].subject_id,null);
 assert.deepEqual(normalizeMaskCatalog(catalog,report()),catalog);
 assert.deepEqual(normalizeMaskCatalog(clone(catalog),report()),catalog);
});

test('real archived subject ID is forwarded, never synthesized from index or preview',()=>{
 const data=project();
 data.base_masks.mask_identity.bindings[0].subject_id='real-subject-01';
 const result=makeVerifiedMaskCatalog(data,report());
 assert.equal(result.items[0].subject_id,'real-subject-01');
 assert.equal(result.items[1].subject_id,null);
});

test('bound diagnostics preserve catalog across untrusted normalization without changing selection payload',()=>{
 const raw=report(),catalog=makeVerifiedMaskCatalog(project(),raw);
 const first=normalizeSubjectInspection({...raw,mask_catalog:catalog});
 assert.ok(first);
 assert.deepEqual(first.mask_catalog,catalog);
 assert.deepEqual(normalizeSubjectInspection(first),first,'normalizer idempotent');
 const proposal=makeSelectionProposal(first,2);
 assert.ok(proposal);
 assert.equal(proposal.subject,2);
 assert.equal(proposal.project_sha256,rev);
 assert.equal(proposal.mask_catalog,undefined,'proposals carry session+revision, not mask bytes');
});

test('fail closed on duplicate, empty, reordered, unsupported or ambiguous float32 bindings',()=>{
 const cases=[];
 const a=project();a.base_masks.mask_identity.bindings[1].mask_sha256_float32=sha0;cases.push(a);
 const b=project();b.base_masks.mask_identity.bindings[0].has_foreground=false;cases.push(b);
 const c=project();c.base_masks.mask_identity.bindings.reverse();cases.push(c);
 const d=project();d.base_masks.mask_identity.bindings[0].mask_id='base-mask-01';cases.push(d);
 const e=project();e.base_masks.mask_identity.bindings[0].subject_ambiguous=true;cases.push(e);
 const f=project();f.base_masks.mask_identity.bindings[0].mask_sha256_float32='bad';cases.push(f);
 const g=project();g.base_masks.mask_identity.bindings[0].accessory_ids=['phantom'];cases.push(g);
 const h=project();h.base_masks.mask_identity.bindings[0].subject_id='same';
 h.base_masks.mask_identity.bindings[1].subject_id='same';cases.push(h);
 const i=project();i.base_masks.mask_identity.bindings[1].mask_index=0;cases.push(i);
 for(const bad of cases)assert.equal(makeVerifiedMaskCatalog(bad,report()),null);
});

test('report, session, project revision and source fingerprint cannot be silently mismatched',()=>{
 const valid=makeVerifiedMaskCatalog(project(),report());
 for(const bad of [
  {...report(),project_sha256:'e'.repeat(64)},
  {...report(),source_sha256:'e'.repeat(64)},
  {...report(),count:1},
  {...report(),height_px:91},
  {...report(),project_name:'foreign'}
 ])assert.equal(normalizeMaskCatalog(valid,bad),null);
 const changed=project();changed.sha256='e'.repeat(64);
 assert.equal(makeVerifiedMaskCatalog(changed,report()),null);
 const malformed=clone(valid);malformed.items[0].mask_sha256_float32='invalid';
 assert.equal(normalizeSubjectInspection({...report(),mask_catalog:malformed}),null);
 assert.equal(normalizeSubjectInspection({...report(),mask_catalog:valid,
   project_sha256:undefined}),null);
 assert.equal(normalizeSubjectInspection({...report(),mask_catalog:valid,
   expires_at_ms:Date.now()-1}),null);
});

test('historical projects remain inspectable but have no fictitious per-mask catalog',()=>{
 const old=project();delete old.base_masks.mask_identity;
 assert.equal(makeVerifiedMaskCatalog(old,report()),null);
 const normalized=normalizeSubjectInspection(report());
 assert.ok(normalized);
 assert.equal(normalized.mask_catalog,undefined);
 assert.equal(maskForSubject(null,1),null);
});

test('Atelier communicates provenance and absence of a stable subject identity, no mask writes',()=>{
 const html=fs.readFileSync(new URL('../web/js/smartsvg_express_atelier_preview.html',import.meta.url),'utf8');
 const node=fs.readFileSync(new URL('../web/js/smartsvg_subject_inspector_v21154.js',import.meta.url),'utf8');
 assert.match(html,/mask_sha256_float32/);
 assert.match(html,/Identité de sujet durable absente/);
 assert.match(html,/Identité du masque non vérifiée/);
 assert.match(node,/makeVerifiedMaskCatalog\(info,msg\)/);
 assert.match(node,/Correspondance des masques ambiguë ou invalide/);
 assert.doesNotMatch(html,/queuePrompt\(|localStorage\(|sessionStorage\(/);
});
