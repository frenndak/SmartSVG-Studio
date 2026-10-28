/** G3.3d-a: read-only, opt-in revision pin for an existing .smartsvg project.
 * The G2.4 editor fingerprint covers the original IMAGE and exact float32
 * base masks. Never infer this identity from the PNG archive SHA alone.
 * No project write, mask conversion, local storage or ComfyUI queue operation.
 */
const SHA=/^[a-f0-9]{64}$/;
const NAME=/^[A-Za-z0-9][A-Za-z0-9_-]{0,47}$/;
export const validProjectName=name=>typeof name==='string'&&NAME.test(name)&&
  !name.endsWith('_previous');

export function validProjectLock(lock){
 return !!lock&&validProjectName(lock.project_name)&&
   typeof lock.project_sha256==='string'&&SHA.test(lock.project_sha256);
}

/** Project inspection is the only read authority. The name and revision
 * are NOT proof of a matching source without a G2.4 float32 snapshot.
 */
export function makeProjectLock(name,project,report){
 const masks=project?.base_masks;
 if(!validProjectName(name)||project?.name!==name||
    project?.status!=='PROJECT_HEALTHY'||!SHA.test(String(project.sha256||''))||
    masks?.exact_float32!==true||
    !SHA.test(String(report?.source_sha256||''))||
    masks.editor_fingerprint!==report.source_sha256||
    !Number.isSafeInteger(report?.width_px)||report.width_px<=0||
    !Number.isSafeInteger(report?.height_px)||report.height_px<=0||
    !Number.isSafeInteger(report?.count)||report.count<1||report.count>32||
    masks.count!==report.count||
    !Array.isArray(masks.dimensions_px)||masks.dimensions_px.length!==2||
    masks.dimensions_px[0]!==report.width_px||
    masks.dimensions_px[1]!==report.height_px)return null;
 return Object.freeze({project_name:name,project_sha256:project.sha256});
}
export function matchesProjectLock(lock,project,report){
 if(!validProjectLock(lock))return false;
 const current=makeProjectLock(lock.project_name,project,report);
 return !!current&&current.project_sha256===lock.project_sha256;
}

/** GET-only G2.2 project inspection. A hung fetch OR response.json() must
 * not keep the ComfyUI selection locked indefinitely. Abort is best-effort:
 * Promise.race also fails closed if an API implementation ignores the signal.
 * Never silently fall back to an unbound proposal after a requested pin.
 */
export async function readProjectRevision(api,name,{timeoutMs=8000,signal}={}){
 if(!validProjectName(name)||typeof api?.fetchApi!=='function'||
    !Number.isSafeInteger(timeoutMs)||timeoutMs<1||timeoutMs>30000)
   throw Error('PROJECT_BINDING_UNAVAILABLE');
 if(signal?.aborted)throw Error('PROJECT_BINDING_ABORTED');
 const controller=new AbortController();
 let timeoutId,abortListener;
 const timeout=new Promise((_,reject)=>{
   timeoutId=setTimeout(()=>{
     reject(Error('PROJECT_BINDING_TIMEOUT'));
     controller.abort();
   },timeoutMs);
 });
 const cancelled=signal?new Promise((_,reject)=>{
   abortListener=()=>{
     reject(Error('PROJECT_BINDING_ABORTED'));
     controller.abort();
   };
   signal.addEventListener('abort',abortListener,{once:true});
   if(signal.aborted)abortListener();
 }):null;
 const request=(async()=>{
   const response=await api.fetchApi(
     '/smartsvg/g22/project?name='+encodeURIComponent(name),
     {signal:controller.signal});
   if(!response?.ok)throw Error('PROJECT_BINDING_UNAVAILABLE');
   const body=await response.json();
   if(body?.ok!==true||!body.project)throw Error('PROJECT_BINDING_UNAVAILABLE');
   return body.project;
 })();
 try{
   return await Promise.race(cancelled?[request,timeout,cancelled]:[request,timeout]);
 }finally{
   clearTimeout(timeoutId);
   if(abortListener)signal.removeEventListener('abort',abortListener);
 }
}
