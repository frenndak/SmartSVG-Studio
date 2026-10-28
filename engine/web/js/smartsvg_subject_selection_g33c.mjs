/** G3.3c-b — voluntary subject proposal, bound to the last G2.6 execution.
 * This module never touches masks, projects, the ComfyUI queue or storage.
 * A proposal requires a second, explicit confirmation inside the source node.
 * Same-origin extensions can spoof BroadcastChannel: this is NOT authentication.
 */
import {validProjectLock} from './smartsvg_subject_project_gate_g33d.mjs';
export const SUBJECT_SELECTION_KIND='smartsvg:subject-selection:g33c:v1';
const SHA=/^[a-f0-9]{64}$/;
const SESSION=/^[a-f0-9]{32}$/;
export const SUBJECT_SESSION_LIFETIME_MS=90_000;
const validExpiry=x=>Number.isSafeInteger(x)&&x>0;
const positive=n=>Number.isSafeInteger(n)&&n>0;
export function linkedMaskInputs(node){
  const inputs=Array.isArray(node?.inputs)?node.inputs:[];
  const image=inputs.find(x=>x?.name==='image');
  const masks=inputs.find(x=>x?.name==='masques_objets');
  if(!Number.isSafeInteger(image?.link)||image.link<0||
     !Number.isSafeInteger(masks?.link)||masks.link<0)return null;
  return JSON.stringify([image.link,masks.link]);
}
export function newSessionId(cryptoProvider=globalThis.crypto){
  if(typeof cryptoProvider?.getRandomValues!=='function')return null;
  try{
    const bytes=new Uint8Array(16);
    cryptoProvider.getRandomValues(bytes);
    return [...bytes].map(x=>x.toString(16).padStart(2,'0')).join('');
  }catch{return null;}
}
export function createSelectionBinding(node,report,cryptoProvider=globalThis.crypto,now=Date.now()){
  const links=linkedMaskInputs(node);
  const session_id=newSessionId(cryptoProvider);
  if(!links||!session_id||!validExpiry(now)||
     now>Number.MAX_SAFE_INTEGER-SUBJECT_SESSION_LIFETIME_MS||!positive(node?.id)||
     !SHA.test(String(report?.source_sha256||''))||
     !positive(report?.count)||report.count>32||
     !positive(report?.width_px)||!positive(report?.height_px)||
     !Array.isArray(report?.sujets)||report.sujets.length!==report.count)return null;
  return Object.freeze({node_id:node.id,session_id,
    expires_at_ms:now+SUBJECT_SESSION_LIFETIME_MS,
    source_sha256:report.source_sha256,
    width_px:report.width_px,height_px:report.height_px,
    count:report.count,links});
}
export function makeSelectionProposal(report,subject){
  const hasProject=report?.project_name!==undefined||
    report?.project_sha256!==undefined;
  if(hasProject&&!validProjectLock(report))return null;
  if(!report||!positive(report.node_id)||!SESSION.test(String(report.session_id||''))||
     !validExpiry(report.expires_at_ms)||Date.now()>=report.expires_at_ms||
     !SHA.test(String(report.source_sha256||''))||
     !positive(report.count)||report.count>32||
     !positive(subject)||subject>report.count||
     !Array.isArray(report.sujets)||
     !report.sujets.some(s=>s.numero===subject&&!s.codes?.includes('MASQUE_VIDE')))
    return null;
  return {kind:SUBJECT_SELECTION_KIND,version:1,
    node_id:report.node_id,session_id:report.session_id,
    expires_at_ms:report.expires_at_ms,
    source_sha256:report.source_sha256,width_px:report.width_px,
    height_px:report.height_px,count:report.count,subject,
    ...(hasProject?{project_name:report.project_name,
      project_sha256:report.project_sha256}:{})};
}
/** Return the selected 1-based index only when all identities still match. */
export function validateSelectionProposal(request,binding,node,latest){
  if(!request||request.kind!==SUBJECT_SELECTION_KIND||request.version!==1||
     !binding||!latest||!positive(node?.id)||node.id!==binding.node_id||
     linkedMaskInputs(node)!==binding.links||
     !SESSION.test(String(binding.session_id||''))||
     !validExpiry(binding.expires_at_ms)||Date.now()>=binding.expires_at_ms||
     request.expires_at_ms!==binding.expires_at_ms||
     request.node_id!==binding.node_id||
     request.session_id!==binding.session_id||
     request.source_sha256!==binding.source_sha256||
     latest.source_sha256!==binding.source_sha256||
     request.width_px!==binding.width_px||
     request.height_px!==binding.height_px||
     request.count!==binding.count||
     // A project-bound session cannot be downgraded to an unbound proposal.
     request.project_name!==binding.project_name||
     request.project_sha256!==binding.project_sha256||
     ((binding.project_name!==undefined||binding.project_sha256!==undefined)&&
       !validProjectLock(binding))||
     latest.width_px!==binding.width_px||
     latest.height_px!==binding.height_px||
     latest.count!==binding.count)return null;
  const subject=request.subject;
  if(!positive(subject)||subject>binding.count||
     !Array.isArray(latest.sujets)||
     !latest.sujets.some(s=>s.numero===subject&&!s.codes?.includes('MASQUE_VIDE')))
    return null;
  return subject;
}
