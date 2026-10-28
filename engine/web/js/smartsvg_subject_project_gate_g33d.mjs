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

/** GET-only G2.2 project inspection; failures must never silently fall back
 * to an unbound proposal after the user requested a project lock.
 */
export async function readProjectRevision(api,name){
 if(!validProjectName(name)||typeof api?.fetchApi!=='function')
   throw Error('PROJECT_BINDING_UNAVAILABLE');
 const response=await api.fetchApi('/smartsvg/g22/project?name='+encodeURIComponent(name));
 if(!response?.ok)throw Error('PROJECT_BINDING_UNAVAILABLE');
 const body=await response.json();
 if(body?.ok!==true||!body.project)throw Error('PROJECT_BINDING_UNAVAILABLE');
 return body.project;
}
