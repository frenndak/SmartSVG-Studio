/** Explicit native-project history. Never rebind an old mask diagnostic. */
const SHA=/^[a-f0-9]{64}$/,SUBJECT=/^subject-[a-f0-9]{32}$/;
const snapshots=new WeakMap();
function projectName(name){
  if(typeof name!=='string'||!/^[A-Za-z0-9][A-Za-z0-9_-]{0,47}$/.test(name)||name.endsWith('_previous'))
    throw Error('INVALID_PROJECT_NAME');
  return name;
}
export function brushHistoryMessage(code){
  if(code==='SAVE_OUTCOME_UNKNOWN')return 'Résultat incertain : vérifier le projet avant une nouvelle action. La retouche peut avoir été annulée ou rétablie.';
  if(code==='SAVE_BUSY')return 'Une sauvegarde est déjà en cours : attendre son résultat.';
  if(['PROJECT_CHANGED','PROJECT_CHANGED_DURING_SAVE','BRUSH_HISTORY_STALE'].includes(code))
    return 'Le projet a changé : actualiser son historique avant de recommencer.';
  if(code==='PROJECT_NOT_HEALTHY')return 'Vérifier ou récupérer le projet avant de modifier son historique.';
  return 'Historique indisponible : actualiser ou vérifier le projet avant de réessayer.';
}
async function post(api,path,values,{timeoutMs=12000,write=false}={}){
  if(typeof api?.fetchApi!=='function'||!Number.isSafeInteger(timeoutMs)||timeoutMs<1||timeoutMs>15000)
    throw Error('HISTORY_UNAVAILABLE');
  const controller=new AbortController(),form=new FormData();let timer;
  for(const [key,value] of Object.entries(values))form.append(key,value);
  const timeout=new Promise((_,reject)=>{timer=setTimeout(()=>{
    reject(Error(write?'SAVE_OUTCOME_UNKNOWN':'HISTORY_STATUS_TIMEOUT'));controller.abort();
  },timeoutMs);});
  const request=(async()=>{
    const response=await api.fetchApi(path,{method:'POST',headers:{'X-SmartSVG-UI':'1'},
                                          body:form,signal:controller.signal});
    const body=await response.json();
    if(!response.ok||body?.ok!==true){
      const error=Error(typeof body?.error_code==='string'?body.error_code:'HISTORY_UNAVAILABLE');
      error.serverRejection=true;throw error;
    }
    return body;
  })();
  try{return await Promise.race([request,timeout]);}
  catch(error){
    if(error?.serverRejection||error?.message==='HISTORY_STATUS_TIMEOUT')throw error;
    throw Error(write?'SAVE_OUTCOME_UNKNOWN':'HISTORY_STATUS_UNAVAILABLE');
  }finally{clearTimeout(timer);}
}
export async function inspectSubjectBrushHistory(api,name,options={}){
  projectName(name);
  const body=await post(api,'/smartsvg/g22/subject/history/status',{
    name,history_version:'1'},options);
  const h=body.history;
  if(body.certified!==false||!h||h.name!==name||!SHA.test(h.project_sha256||'')||
     h.cricut_certified!==false||typeof h.undo_available!=='boolean'||typeof h.redo_available!=='boolean'||
     (h.undo_available&&!SUBJECT.test(h.undo_subject_id||''))||
     (h.redo_available&&!SUBJECT.test(h.redo_subject_id||'')))throw Error('INVALID_BRUSH_HISTORY_SNAPSHOT');
  const result=Object.freeze({projectName:name,projectSha256:h.project_sha256,
    canUndo:h.undo_available,canRedo:h.redo_available,
    undoSubjectId:h.undo_subject_id,redoSubjectId:h.redo_subject_id,
    undoReason:h.undo_error_code,redoReason:h.redo_error_code,expiresAt:Date.now()+120000});
  snapshots.set(result,{state:'ready',action:null,result:null});return result;
}
export async function changeSubjectBrushHistory(api,snapshot,action,{confirmed=false,timeoutMs=15000}={}){
  if(confirmed!==true)throw Error('BRUSH_HISTORY_CONFIRMATION_REQUIRED');
  const entry=snapshots.get(snapshot);
  if(!entry||!['undo','redo'].includes(action))throw Error('INVALID_BRUSH_HISTORY_SNAPSHOT');
  if(entry.state==='saving')throw Error('SAVE_BUSY');
  if(entry.state==='unknown')throw Error('SAVE_OUTCOME_UNKNOWN');
  if(entry.state==='saved'){
    if(entry.action!==action)throw Error('BRUSH_HISTORY_STALE');
    return entry.result;
  }
  if(Date.now()>=snapshot.expiresAt)throw Error('BRUSH_HISTORY_STALE');
  if(!(action==='undo'?snapshot.canUndo:snapshot.canRedo))throw Error('BRUSH_NOTHING_TO_'+action.toUpperCase());
  if(typeof globalThis.crypto?.getRandomValues!=='function')throw Error('HISTORY_UNAVAILABLE');
  const nonce=new Uint8Array(16);globalThis.crypto.getRandomValues(nonce);
  const id=Array.from(nonce,b=>b.toString(16).padStart(2,'0')).join('');
  entry.state='saving';entry.action=action;
  try{
    const body=await post(api,'/smartsvg/g22/subject/history/apply',{
      name:snapshot.projectName,expected_sha256:snapshot.projectSha256,action,
      command_id:id,confirmed:'yes',history_version:'1'}, {timeoutMs,write:true});
    const r=body.result;
    if(body.certified!==false||!r||r.name!==snapshot.projectName||r.command_id!==id||
       r.action!==action||!SHA.test(r.sha256||'')||r.persisted!==true||r.cricut_certified!==false||
       !['brush_history_'+action,'brush_history_already_applied'].includes(r.status))
      throw Error('SAVE_OUTCOME_UNKNOWN');
    entry.result=Object.freeze({projectSha256:r.sha256,action,persisted:true,cricutCertified:false});
    entry.state='saved';return entry.result;
  }catch(error){entry.state='unknown';throw error;}
}

export function createBrushHistoryControls(api,name,{
  document=globalThis.document,onBeforeWrite=()=>{},onAfterWrite=()=>{},onMessage=()=>{},
}={}){
  projectName(name);
  const element=document.createElement('section');element.setAttribute('aria-label','Historique des retouches du projet');
  const title=document.createElement('p');title.textContent='Projet : '+name;element.appendChild(title);
  const explanation=document.createElement('p');explanation.textContent=
    'Annuler ou rétablir la dernière retouche du projet. Les fichiers déjà exportés sont conservés.';
  element.appendChild(explanation);
  const status=document.createElement('p');status.setAttribute('role','status');status.setAttribute('aria-live','polite');
  const makeButton=label=>{const b=document.createElement('button');b.type='button';b.className='outline';
    b.textContent=label;element.appendChild(b);return b;};
  const undo=makeButton('Annuler la dernière retouche'),redo=makeButton('Rétablir la retouche');
  const reload=makeButton('Actualiser l’historique');element.appendChild(status);
  let alive=true,phase=null,snapshot=null,generation=0;
  const ready=()=>{
    undo.disabled=!alive||!!phase||!snapshot?.canUndo;
    redo.disabled=!alive||!!phase||!snapshot?.canRedo;
    reload.disabled=!alive||!!phase;
  };
  async function refresh(notice=''){
    if(!alive||phase)return;
    const token=++generation;phase='read';ready();status.textContent='Lecture de l’historique du projet…';
    try{
      const result=await inspectSubjectBrushHistory(api,name);
      if(!alive||token!==generation)return;
      snapshot=result;
      const blocked=[result.undoReason,result.redoReason].some(code=>code&&
        !['BRUSH_NOTHING_TO_UNDO','BRUSH_NOTHING_TO_REDO'].includes(code));
      status.textContent=notice||((result.canUndo||result.canRedo)?'Historique actualisé.':
        blocked?'Cet historique nécessite une vérification du projet.':'Aucune retouche annulable ou à rétablir.');
    }catch(error){
      if(!alive||token!==generation)return;
      snapshot=null;status.textContent=notice?notice+' Actualisation de l’historique indisponible.':brushHistoryMessage(error?.message);
    }finally{if(token===generation){phase=null;ready();}}
  }
  async function apply(action){
    if(!alive||phase||!snapshot)return;
    if(!(action==='undo'?snapshot.canUndo:snapshot.canRedo))return;
    const selected=snapshot;phase='write';ready();let started=false,notice='';
    try{
      onBeforeWrite();started=true;
      status.textContent='Enregistrement de la modification en cours…';onMessage(status.textContent);
      await changeSubjectBrushHistory(api,selected,action,{confirmed:true});
      notice=action==='undo'?'Dernière retouche annulée.':'Retouche rétablie.';
      status.textContent=notice;onMessage(notice);
    }catch(error){status.textContent=brushHistoryMessage(error?.message);onMessage(status.textContent);}
    finally{
      snapshot=null;phase=null;
      try{if(started)onAfterWrite();}finally{ready();}
    }
    // Read-only refresh after a known durable acknowledgement permits the
    // opposite action without re-running a ComfyUI node or rebinding masks.
    if(notice&&alive)await refresh(notice);
  }
  undo.addEventListener('click',()=>apply('undo'));redo.addEventListener('click',()=>apply('redo'));
  reload.addEventListener('click',()=>refresh());ready();
  return {element,refresh,
    invalidate(){snapshot=null;generation++;if(phase==='read')phase=null;ready();},
    dispose(){alive=false;generation++;snapshot=null;ready();}};
}
