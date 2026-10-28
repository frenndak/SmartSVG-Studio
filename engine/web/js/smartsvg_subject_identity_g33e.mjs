/** G3.3e-b1: explicit, revision-pinned registration of one persistent Subject.
 * Only verified metadata crosses the browser boundary; float32 bytes stay server-side.
 */
import {normalizeMaskCatalog} from './smartsvg_mask_link_g33e.mjs';

const SHA=/^[a-f0-9]{64}$/;
const SUBJECT=/^subject-[a-f0-9]{32}$/;
const positive=value=>Number.isSafeInteger(value)&&value>0;

function exactMask(report,mask){
 const catalog=normalizeMaskCatalog(report?.mask_catalog,report);
 if(!catalog||!mask||!Number.isSafeInteger(mask.mask_index))return null;
 const item=catalog.items[mask.mask_index];
 if(!item||item.mask_id!==mask.mask_id||
    item.mask_sha256_float32!==mask.mask_sha256_float32||
    item.subject_id!==null||item.subject_ambiguous!==false)return null;
 return {catalog,item};
}

function validResult(result,report,item){
 if(!result||!['subject_identity_created','subject_identity_exists'].includes(result.status)||
    result.name!==report.project_name||!SUBJECT.test(String(result.subject_id||''))||
    result.mask_id!==item.mask_id||!SHA.test(String(result.sha256||''))||
    !Array.isArray(result.bbox_px)||result.bbox_px.length!==4||
    !result.bbox_px.every(Number.isSafeInteger))return false;
 const [x,y,width,height]=result.bbox_px;
 return x>=0&&y>=0&&width>0&&height>0&&
   x+width<=report.width_px&&y+height<=report.height_px&&
   result.certified===false;
}

export async function registerPersistentSubject(api,report,mask,{
 confirmed=false,timeoutMs=8000,signal,
}={}){
 const verified=exactMask(report,mask);
 if(confirmed!==true||!verified||typeof api?.fetchApi!=='function'||
    !Number.isSafeInteger(report?.expires_at_ms)||
    Date.now()>=report.expires_at_ms||
    !Number.isSafeInteger(timeoutMs)||timeoutMs<1||timeoutMs>30000)
   throw Error('SUBJECT_IDENTITY_UNAVAILABLE');
 if(signal?.aborted)throw Error('SUBJECT_IDENTITY_ABORTED');
 const {catalog,item}=verified;
 const form=new FormData();
 for(const [key,value] of Object.entries({
  name:report.project_name,
  expected_sha256:report.project_sha256,
  source_id:catalog.source_id,
  source_sha256:report.source_sha256,
  mask_index:String(item.mask_index),
  mask_id:item.mask_id,
  mask_sha256_float32:item.mask_sha256_float32,
  expires_at_ms:String(report.expires_at_ms),
  confirmed:'yes',
 }))form.append(key,value);

 const controller=new AbortController();
 let timeoutId,abortListener;
 const timeout=new Promise((_,reject)=>{
  timeoutId=setTimeout(()=>{
   controller.abort();
   reject(Error('SUBJECT_IDENTITY_TIMEOUT'));
  },timeoutMs);
 });
 const cancelled=signal?new Promise((_,reject)=>{
  abortListener=()=>{
   controller.abort();
   reject(Error('SUBJECT_IDENTITY_ABORTED'));
  };
  signal.addEventListener('abort',abortListener,{once:true});
  if(signal.aborted)abortListener();
 }):null;
 const request=(async()=>{
  const response=await api.fetchApi('/smartsvg/g22/subject/identity',{
   method:'POST',headers:{'X-SmartSVG-UI':'1'},body:form,signal:controller.signal,
  });
  let body;
  try{body=await response.json();}catch{throw Error('SUBJECT_IDENTITY_INVALID_RESPONSE');}
  if(!response?.ok||body?.ok!==true)
   throw Error(body?.error_code||'SUBJECT_IDENTITY_UNAVAILABLE');
  if(!validResult(body.result,report,item))
   throw Error('SUBJECT_IDENTITY_INVALID_RESPONSE');
  return body.result;
 })();
 try{
  return await Promise.race(cancelled?[request,timeout,cancelled]:[request,timeout]);
 }finally{
  clearTimeout(timeoutId);
  if(abortListener)signal.removeEventListener('abort',abortListener);
 }
}
