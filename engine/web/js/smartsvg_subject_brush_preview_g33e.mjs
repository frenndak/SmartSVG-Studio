/** G3.3e-b2a: one read-only Subject brush preview from a pinned G3.3e report.
 * No project writes, no ComfyUI queue and no float32 bytes cross this boundary.
 * A late response is never an authority for the current UI selection.
 */
const SHA=/^[a-f0-9]{64}$/;
const SUBJECT=/^subject-[a-f0-9]{32}$/;
const PROJECT=/^[A-Za-z0-9][A-Za-z0-9_-]{0,47}$/;
const PNG64=/^[A-Za-z0-9+/]+={0,2}$/;
const MAX_PNG64=4*Math.ceil((12*1024*1024)/3);

export const BRUSH_PREVIEW_MESSAGES=Object.freeze({
  PREVIEW_ABORTED:'Aperçu annulé : aucun masque enregistré.',
  PREVIEW_SELECTION_STALE:'Diagnostic ou sujet modifié pendant le calcul : actualiser les sujets avant de réessayer.',
  PREVIEW_TIMEOUT:'Aperçu trop long : réessayer sur un sujet plus petit.',
  PREVIEW_BUSY:'Deux aperçus sont déjà calculés : réessayer dans un instant.',
  PROJECT_CHANGED:'Projet modifié : actualiser les sujets avant de réessayer.',
  PROJECT_CHANGED_DURING_PREVIEW:'Projet modifié pendant le calcul : actualiser les sujets.',
  PROJECT_NOT_HEALTHY:'Projet à vérifier ou à récupérer avant une retouche.',
  INVALID_SUBJECT_PROOF:'Identité du sujet non vérifiée : actualiser le diagnostic.',
  SUBJECT_NOT_VERIFIED:'Sujet non vérifié : enregistrer son identité avant la retouche.',
  BRUSH_RUNTIME_UNAVAILABLE:'Moteur de pinceau indisponible : vérifier NumPy et Pillow.',
  INVALID_PREVIEW_OUTPUT:'Réponse de prévisualisation incohérente : rien n’a été enregistré.',
});
export function brushPreviewMessage(code){
  return BRUSH_PREVIEW_MESSAGES[code]||
    'Aperçu indisponible : actualiser le diagnostic. Aucune modification enregistrée.';
}

function validatedCommand(report,mask,{mode,radius,points}){
  const catalog=report?.mask_catalog;
  const idx=mask?.mask_index;
  const linked=Number.isSafeInteger(idx)?catalog?.items?.[idx]:null;
  if(report?.identityActionStale===true||!PROJECT.test(report?.project_name||'')||
     report.project_name.endsWith('_previous')||
     !SHA.test(report.project_sha256||'')||
     !SHA.test(report.source_sha256||'')||
     !catalog||catalog.project_name!==report.project_name||
     catalog.project_sha256!==report.project_sha256||
     catalog.source_sha256!==report.source_sha256||
     typeof catalog.source_id!=='string'||catalog.source_id.length>128||
     !/^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$/.test(catalog.source_id)||
     !linked||linked.mask_index!==idx||
     linked.mask_id!=='base-mask-'+String(idx).padStart(2,'0')||
     linked.mask_id!==mask.mask_id||
     linked.mask_sha256_float32!==mask.mask_sha256_float32||
     linked.subject_id!==mask.subject_id||
     !SUBJECT.test(mask.subject_id||'')||
     !SHA.test(mask.mask_sha256_float32||'')||
     linked.subject_ambiguous!==false||linked.has_foreground!==true||
     mask.subject_ambiguous!==false||mask.has_foreground!==true||
     (linked.subject_proof_status!==undefined&&linked.subject_proof_status!=='verified')||
     (mask.subject_proof_status!==undefined&&mask.subject_proof_status!=='verified')||
     !Number.isSafeInteger(report.expires_at_ms)||
     Date.now()>=report.expires_at_ms)
    throw Error('PREVIEW_SELECTION_STALE');
  if(!['add','erase'].includes(mode)||
     typeof radius!=='number'||!Number.isFinite(radius)||
     radius<0.0005||radius>0.2||
     !Array.isArray(points)||points.length<1||points.length>64||
     points.some(p=>!Array.isArray(p)||p.length!==2||
       p.some(v=>typeof v!=='number'||!Number.isFinite(v)||v<0||v>1)))
    throw Error('INVALID_PREVIEW_STROKE');
  return {
    name:report.project_name,expected_sha256:report.project_sha256,
    subject_id:mask.subject_id,mask_id:mask.mask_id,
    mask_sha256_float32:mask.mask_sha256_float32,
    source_id:catalog.source_id,source_sha256:report.source_sha256,
    mode,radius:String(radius),points:JSON.stringify(points),
  };
}

function validatedResponse(body,command,commandId,report){
  const p=body?.preview;
  if(body?.ok!==true||body?.certified!==false||!p||
     p.command_id!==commandId||p.name!==command.name||
     p.project_sha256!==command.expected_sha256||
     p.subject_id!==command.subject_id||p.mask_id!==command.mask_id||
     p.source_sha256!==command.source_sha256||
     p.persisted!==false||p.cricut_certified!==false||
     !Array.isArray(p.dimensions_px)||p.dimensions_px.length!==2||
     p.dimensions_px.some(n=>!Number.isSafeInteger(n)||n<1)||
     p.dimensions_px[0]!==report.width_px||
     p.dimensions_px[1]!==report.height_px||
     !Number.isSafeInteger(p.changed_pixels)||p.changed_pixels<0||
     p.changed_pixels>p.dimensions_px[0]*p.dimensions_px[1])
    throw Error('INVALID_PREVIEW_OUTPUT');
  for(const field of ['before_png_base64','after_png_base64']){
    const value=p[field];
    if(typeof value!=='string'||value.length<44||
       value.length>MAX_PNG64||!PNG64.test(value)||
       !value.startsWith('iVBORw0KGgo'))
      throw Error('INVALID_PREVIEW_OUTPUT');
  }
  return Object.freeze({
    beforeSrc:'data:image/png;base64,'+p.before_png_base64,
    afterSrc:'data:image/png;base64,'+p.after_png_base64,
    changedPixels:p.changed_pixels,
    commandId,
    projectSha256:p.project_sha256,
    subjectId:p.subject_id,
    persisted:false,cricutCertified:false,
  });
}

/** Request a single explicit gesture. Abort/timeout prevent late UI delivery.
 * The server may finish its read-only CPU work after an HTTP cancellation.
 */
export async function requestSubjectBrushPreview(api,report,mask,{
  mode='add',radius=0.05,points=[[0.5,0.5]],timeoutMs=12000,signal,
}={}){
  if(typeof api?.fetchApi!=='function'||
     !Number.isSafeInteger(timeoutMs)||timeoutMs<1||timeoutMs>15000)
    throw Error('PREVIEW_UNAVAILABLE');
  if(signal?.aborted)throw Error('PREVIEW_ABORTED');
  const command=validatedCommand(report,mask,{mode,radius,points});
  // getRandomValues is available even on non-secure HTTP LAN origins,
  // unlike randomUUID() (secure contexts only). Never use Math.random().
  if(typeof globalThis.crypto?.getRandomValues!=='function')
    throw Error('PREVIEW_UNAVAILABLE');
  const nonce=new Uint8Array(16);
  globalThis.crypto.getRandomValues(nonce);
  const commandId=Array.from(nonce,b=>b.toString(16).padStart(2,'0')).join('');
  const form=new FormData();
  for(const [key,value] of Object.entries({
    preview_version:'1',command_id:commandId,...command,
  }))form.append(key,value);
  const controller=new AbortController();
  let timer,abortListener;
  const timeout=new Promise((_,reject)=>{
    timer=setTimeout(()=>{
      // Settle the timeout first: aborting fetch can synchronously reject
      // with AbortError, otherwise masking the recoverable timeout reason.
      reject(Error('PREVIEW_TIMEOUT'));
      controller.abort();
    },timeoutMs);
  });
  const cancelled=signal?new Promise((_,reject)=>{
    abortListener=()=>{
      controller.abort();
      reject(Error('PREVIEW_ABORTED'));
    };
    signal.addEventListener('abort',abortListener,{once:true});
    if(signal.aborted)abortListener();
  }):null;
  const request=(async()=>{
    const response=await api.fetchApi('/smartsvg/g22/subject/preview',{
      method:'POST',headers:{'X-SmartSVG-UI':'1'},
      body:form,signal:controller.signal,
    });
    let body;
    try{body=await response.json();}
    catch{throw Error('INVALID_PREVIEW_OUTPUT');}
    if(!response.ok||body?.ok!==true)
      throw Error(body?.error_code||'PREVIEW_UNAVAILABLE');
    // The report and mask can be mutated while the HTTP request is pending.
    // Recheck the full selection proof and its expiry before delivering PNGs.
    // A successful server response is not authority for a stale browser state.
    const stillCurrent=validatedCommand(report,mask,{mode,radius,points});
    if(Object.keys(command).some(key=>stillCurrent[key]!==command[key]))
      throw Error('PREVIEW_SELECTION_STALE');
    return validatedResponse(body,command,commandId,report);
  })();
  try{
    return await Promise.race(cancelled?[request,timeout,cancelled]:[request,timeout]);
  }catch(error){
    if(controller.signal.aborted&&signal?.aborted)
      throw Error('PREVIEW_ABORTED');
    throw error;
  }finally{
    clearTimeout(timer);
    if(abortListener)signal.removeEventListener('abort',abortListener);
  }
}
