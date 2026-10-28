/** G3.3c-b — voluntary subject proposal, bound to the last G2.6 execution.
 * This module never touches masks, projects, the ComfyUI queue or storage.
 * A proposal requires a second, explicit confirmation inside the source node.
 * Same-origin extensions can spoof BroadcastChannel: this is NOT authentication.
 */
export const SUBJECT_SELECTION_KIND='smartsvg:subject-selection:g33c:v1';
const SHA=/^[a-f0-9]{64}$/;
const SESSION=/^[a-f0-9]{32}$/;
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
export function createSelectionBinding(node,report,cryptoProvider=globalThis.crypto){
  const links=linkedMaskInputs(node);
  const session_id=newSessionId(cryptoProvider);
  if(!links||!session_id||!positive(node?.id)||
     !SHA.test(String(report?.source_sha256||''))||
     !positive(report?.count)||report.count>32||
     !positive(report?.width_px)||!positive(report?.height_px)||
     !Array.isArray(report?.sujets)||report.sujets.length!==report.count)return null;
  return Object.freeze({node_id:node.id,session_id,
    source_sha256:report.source_sha256,
    width_px:report.width_px,height_px:report.height_px,
    count:report.count,links});
}
export function makeSelectionProposal(report,subject){
  if(!report||!positive(report.node_id)||!SESSION.test(String(report.session_id||''))||
     !SHA.test(String(report.source_sha256||''))||
     !positive(report.count)||report.count>32||
     !positive(subject)||subject>report.count||
     !Array.isArray(report.sujets)||
     !report.sujets.some(s=>s.numero===subject&&!s.codes?.includes('MASQUE_VIDE')))
    return null;
  return {kind:SUBJECT_SELECTION_KIND,version:1,
    node_id:report.node_id,session_id:report.session_id,
    source_sha256:report.source_sha256,width_px:report.width_px,
    height_px:report.height_px,count:report.count,subject};
}
/** Return the selected 1-based index only when all identities still match. */
export function validateSelectionProposal(request,binding,node,latest){
  if(!request||request.kind!==SUBJECT_SELECTION_KIND||request.version!==1||
     !binding||!latest||!positive(node?.id)||node.id!==binding.node_id||
     linkedMaskInputs(node)!==binding.links||
     !SESSION.test(String(binding.session_id||''))||
     request.node_id!==binding.node_id||
     request.session_id!==binding.session_id||
     request.source_sha256!==binding.source_sha256||
     latest.source_sha256!==binding.source_sha256||
     request.width_px!==binding.width_px||
     request.height_px!==binding.height_px||
     request.count!==binding.count||
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
