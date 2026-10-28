import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {
 normalizeSubjectInspection,SUBJECT_HANDOFF_CHANNEL,SUBJECT_HANDOFF_KIND,
 SUBJECT_WARNING_LABELS
} from '../web/js/smartsvg_subject_handoff_g33.mjs';
const png='data:image/png;base64,QUJDRA==';
const source='a'.repeat(64);
const item=(numero)=>({numero,image_data:png,codes:[],
 zones_a_examiner:[],zones_non_affichees:0,etat:'INSPECTION_VISUELLE_REQUISE'});
const sample=()=>({selection:1,source_sha256:source,width_px:160,height_px:90,
 count:2,sujets:[item(1),item(2)]});

test('real G2.6 payload is reconstituted with source fingerprint and no certified flag',()=>{
 const r=normalizeSubjectInspection(sample());
 assert.equal(r.kind,SUBJECT_HANDOFF_KIND);
 assert.equal(r.count,2);
 assert.equal(r.source_sha256,source);
 assert.equal(r.sujets[0].image_data,png);
 assert.equal(r.modifications_automatiques,false);
 assert.equal(r.decoupe_certifiee,false);
 assert.ok(SUBJECT_HANDOFF_CHANNEL.startsWith('smartsvg:'));
 assert.deepEqual(normalizeSubjectInspection(r),r);
});
test('data from other tools, unknown codes or external images is rejected',()=>{
 const cases=[
  {...sample(),kind:'other:event'},
  {...sample(),version:99},
  {...sample(),source_sha256:'bad'},
  {...sample(),width_px:0},
  {...sample(),height_px:100000},
  {...sample(),count:33},
  {...sample(),sujets:[item(1),item(1)]},
  {...sample(),sujets:[item(1)]},
  {...sample(),sujets:[{...item(1),image_data:'https://evil.example/pixel'},item(2)]},
  {...sample(),sujets:[{...item(1),image_data:'data:image/svg+xml;base64,PHN2Zz4='},item(2)]},
  {...sample(),sujets:[{...item(1),codes:['<script>']},item(2)]},
 ];
 for(const c of cases)assert.equal(normalizeSubjectInspection(c),null);
});
test('highlight zones must be valid source+tile coordinates, with bounded count',()=>{
 const raw=sample();
 raw.sujets[1]={...item(2),codes:['FRAGMENTS_DETACHES'],
  zones_a_examiner:[{type:'FRAGMENT_SEPARE',bbox_source_px:[1,2,6,8],
  bbox_apercu_88px:[0,1,5,7]}],zones_non_affichees:1};
 const result=normalizeSubjectInspection(raw);
 assert.equal(result.sujets[1].zones_a_examiner[0].bbox_source_px[2],6);
 assert.equal(result.sujets[1].codes[0],'FRAGMENTS_DETACHES');
 assert.equal(SUBJECT_WARNING_LABELS.FRAGMENTS_DETACHES,'Fragments détachés');
 for(const bad of [
  {type:'FRAGMENT_SEPARE',bbox_source_px:[0,0,1000,5],bbox_apercu_88px:[0,0,88,88]},
  {type:'FRAGMENT_SEPARE',bbox_source_px:[1,1,1,5],bbox_apercu_88px:[0,0,88,88]},
  {type:'FRAGMENT_SEPARE',bbox_source_px:[1,2,6,8],bbox_apercu_88px:[0,0,99,88]},
  {type:'CLICK',bbox_source_px:[1,2,6,8],bbox_apercu_88px:[0,0,88,88]},
 ]){
  const invalid=sample();invalid.sujets[0].zones_a_examiner=[bad];
  assert.equal(normalizeSubjectInspection(invalid),null);
 }
});
test('payload is bounded by subjects, thumbnail size and aggregate media',()=>{
 const many={...sample(),count:32,sujets:Array.from({length:32},(_,i)=>item(i+1))};
 assert.equal(normalizeSubjectInspection(many).count,32);
 many.count=33;many.sujets.push(item(33));
 assert.equal(normalizeSubjectInspection(many),null);
 const huge=sample();huge.sujets[0].image_data='data:image/png;base64,'+'A'.repeat(700000);
 assert.equal(normalizeSubjectInspection(huge),null);
 const all=sample();all.sujets=Array.from({length:15},(_,i)=>({
  ...item(i+1),image_data:'data:image/png;base64,'+'A'.repeat(400000)}));
 all.count=15;
 assert.equal(normalizeSubjectInspection(all),null,'reject excessive same-origin media handoff');
});
test('UI explicitly handles only opt-in sender+receiver; no hidden compute or persistence',()=>{
 const sender=fs.readFileSync(new URL('../web/js/smartsvg_subject_inspector_v21154.js',import.meta.url),'utf8');
 const atelier=fs.readFileSync(new URL('../web/js/smartsvg_express_atelier_preview.html',import.meta.url),'utf8');
 assert.match(sender,/Envoyer le dernier diagnostic vers l’Atelier/);
 assert.match(sender,/share\.addEventListener\('click'/);
 assert.match(sender,/normalizeSubjectInspection\(latest\)/);
 assert.match(atelier,/id="receiveSubjects"/);
 assert.match(atelier,/id="realSubjectsGrid"/);
 assert.match(atelier,/id="clearSubjects"/);
 assert.match(atelier,/\$\("receiveSubjects"\)\.addEventListener\("click"/);
 assert.match(atelier,/stopSubjectReceive\(\)/);
 assert.match(atelier,/aucune modification du nœud/);
 assert.doesNotMatch(atelier,/queuePrompt|localStorage|sessionStorage|XMLHttpRequest/);
 assert.doesNotMatch(sender,/localStorage|sessionStorage|queuePrompt/);
});
