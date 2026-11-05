/** G3.3e-b2a: one read-only Subject brush preview from a pinned G3.3e report.
 * No project writes, no ComfyUI queue and no float32 bytes cross this boundary.
 * A late response is never an authority for the current UI selection.
 */
const SHA=/^[a-f0-9]{64}$/;
const SUBJECT=/^subject-[a-f0-9]{32}$/;
const PROJECT=/^[A-Za-z0-9][A-Za-z0-9_-]{0,47}$/;
const PNG64=/^[A-Za-z0-9+/]+={0,2}$/;
const MAX_PNG64=4*Math.ceil((12*1024*1024)/3);
const acceptedPreviews=new WeakMap();

/** Map a pointer over object-fit:contain, object-position:center to source0..1.
 * The preview image must have no border/padding. Letterbox clicks are ignored.
 */
export function brushPointFromPreview(rect,width,height,clientX,clientY){
  if(!rect||![rect.left,rect.top,rect.width,rect.height,clientX,clientY].every(
      v=>typeof v==='number'&&Number.isFinite(v))||
     !Number.isSafeInteger(width)||!Number.isSafeInteger(height)||width<1||height<1||
     width*height>5_000_000||rect.width<=0||rect.height<=0)return null;
  const scale=Math.min(rect.width/width,rect.height/height);
  const drawnWidth=width*scale,drawnHeight=height*scale;
  const left=rect.left+(rect.width-drawnWidth)/2,top=rect.top+(rect.height-drawnHeight)/2;
  const x=(clientX-left)/drawnWidth,y=(clientY-top)/drawnHeight;
  if(![left,top,drawnWidth,drawnHeight,x,y].every(Number.isFinite)||
     drawnWidth<=0||drawnHeight<=0||x<0||x>1||y<0||y>1)return null;
  return [x,y];
}

/** Choose a point only. Preview calculation and persistence stay explicit. */
export function bindBrushPointPicker(image,{width,height,isCurrent,getPoint,onPoint,onKeyboardFocus=()=>{},clickEnabled=true}){
  let disposed=false;
  image.tabIndex=0;image.setAttribute('role','button');
  image.setAttribute('aria-label',(image.alt||'Aperçu du masque')+
    ' : choisir le point au clic ou avec les flèches ; Entrée pour les coordonnées.');
  image.title='Cliquer pour placer le point ; flèches ou champs de coordonnées au clavier.';
  const available=()=>!disposed&&!image.hidden&&isCurrent();
  image.addEventListener('click',event=>{
    if(!available()||(event.button!==undefined&&event.button!==0))return;
    if(event.detail===0){onKeyboardFocus('x');return;}
    if(!clickEnabled)return;
    const point=brushPointFromPreview(image.getBoundingClientRect(),width,height,event.clientX,event.clientY);
    if(point)onPoint(point);
  });
  image.addEventListener('keydown',event=>{
    if(!available())return;
    if(event.key==='Enter'||event.key===' '){event.preventDefault();onKeyboardFocus('x');return;}
    const delta={ArrowLeft:[-0.01,0],ArrowRight:[0.01,0],ArrowUp:[0,-0.01],ArrowDown:[0,0.01]}[event.key];
    if(!delta)return;
    const point=getPoint();
    if(!Array.isArray(point)||point.length!==2||point.some(v=>
       typeof v!=='number'||!Number.isFinite(v)||v<0||v>1))return;
    event.preventDefault();
    onPoint(point.map((value,index)=>Math.min(1,Math.max(0,value+delta[index]))));
    onKeyboardFocus(delta[0]?'x':'y');
  });
  return ()=>{disposed=true;image.tabIndex=-1;image.setAttribute('aria-disabled','true');};
}

/** Collect one bounded native stroke. Never calls the preview API or writer.
 * Leaving the drawable image, losing capture/focus or changing geometry cancels
 * the whole incomplete gesture. Returned function cancels without committing.
 */
export function bindBrushStrokePicker(image,{
  width,height,isCurrent,getPoint,onPoint,onKeyboardFocus=()=>{},
  onStrokeStart=()=>{},onStrokeProgress=()=>{},onStroke,onStrokeCancel=()=>{},
}){
  let active=null;
  const available=()=>!image.hidden&&isCurrent();
  bindBrushPointPicker(image,{width,height,isCurrent:()=>!active&&available(),
    getPoint,onPoint,onKeyboardFocus,clickEnabled:false});
  image.draggable=false;image.style.touchAction='none';image.style.userSelect='none';
  image.setAttribute('aria-label',(image.alt||'Aperçu du masque')+
    ' : tracer en maintenant le pointeur ; Échap annule ; flèches ou Entrée pour un point au clavier.');
  image.title='Maintenir et tracer ; Échap annule. Coordonnées disponibles au clavier.';
  const release=stroke=>{try{image.releasePointerCapture(stroke.id);}catch{ /* already released */ }};
  const cancel=(reason='BRUSH_CANCELLED')=>{
    if(!active)return;
    const stroke=active;active=null;release(stroke);onStrokeCancel(reason);
  };
  const append=event=>{
    const rect=image.getBoundingClientRect();
    if(!available()||['left','top','width','height'].some(key=>rect[key]!==active.rect[key])){
      cancel('BRUSH_CONTEXT_CHANGED');return false;
    }
    const point=brushPointFromPreview(rect,width,height,event.clientX,event.clientY);
    if(!point){cancel('BRUSH_OUTSIDE_IMAGE');return false;}
    const last=active.points.at(-1);
    if(last&&point[0]===last[0]&&point[1]===last[1])return true;
    if(active.points.length>=1500){cancel('BRUSH_POINT_LIMIT');return false;}
    active.points.push(point);onStrokeProgress(active.points.map(p=>[...p]));return true;
  };
  image.addEventListener('pointerdown',event=>{
    if(active||!available()||event.button!==0||event.isPrimary===false||
       !Number.isSafeInteger(event.pointerId)||event.pointerId<0)return;
    const rect=image.getBoundingClientRect();
    const point=brushPointFromPreview(rect,width,height,event.clientX,event.clientY);
    if(!point)return;
    try{image.setPointerCapture(event.pointerId);}catch{return;}
    active={id:event.pointerId,rect:{left:rect.left,top:rect.top,width:rect.width,height:rect.height},points:[point]};
    event.preventDefault();image.focus({preventScroll:true});onStrokeStart();
    onStrokeProgress([[...point]]);
  });
  image.addEventListener('pointermove',event=>{
    if(!active||event.pointerId!==active.id)return;
    event.preventDefault();
    if((event.buttons&1)===0){cancel();return;}
    append(event);
  });
  image.addEventListener('pointerup',event=>{
    if(!active||event.pointerId!==active.id)return;
    event.preventDefault();
    if(!append(event))return;
    const stroke=active;active=null;release(stroke);
    onStroke(stroke.points.map(p=>[...p]));
  });
  for(const type of ['pointercancel','lostpointercapture'])image.addEventListener(type,event=>{
    if(active&&event.pointerId===active.id)cancel();
  });
  image.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&active){event.preventDefault();cancel();}
  });
  image.addEventListener('blur',()=>cancel());
  image.addEventListener('dragstart',event=>event.preventDefault());
  return ()=>cancel();
}

export function brushSaveMessage(code){
  if(code==='SAVE_OUTCOME_UNKNOWN')return 'Résultat de sauvegarde incertain : vérifier le projet avant de recommencer. Le geste peut être enregistré.';
  if(code==='SAVE_BUSY')return 'Enregistrement déjà en cours.';
  if(code==='PROJECT_CHANGED'||code==='PROJECT_CHANGED_DURING_SAVE')return 'Projet modifié : recevoir un nouveau diagnostic avant de réessayer.';
  return 'Enregistrement non confirmé : vérifier le projet et actualiser le diagnostic avant de réessayer.';
}

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
     linked.subject_proof_status!=='verified'||
     mask.subject_proof_status!=='verified'||
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
     p.base_mask_sha256_float32!==command.mask_sha256_float32||
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
  const result=Object.freeze({
    beforeSrc:'data:image/png;base64,'+p.before_png_base64,
    afterSrc:'data:image/png;base64,'+p.after_png_base64,
    changedPixels:p.changed_pixels,
    commandId,
    projectSha256:p.project_sha256,
    subjectId:p.subject_id,
    persisted:false,cricutCertified:false,
    canSave:SHA.test(p.preview_mask_sha256_float32||''),
  });
  if(result.canSave)acceptedPreviews.set(result,{
    command:Object.freeze({...command}),commandId,
    digest:p.preview_mask_sha256_float32,state:'ready',result:null,
  });
  return result;
}

/** Explicit write after preview. A lost acknowledgement is an unknown outcome,
 * never an assertion that a pending server-side write was cancelled. */
export async function saveSubjectBrushPreview(api,report,mask,preview,{
  confirmed=false,timeoutMs=15000,
}={}){
  if(confirmed!==true)throw Error('BRUSH_SAVE_CONFIRMATION_REQUIRED');
  const accepted=acceptedPreviews.get(preview);
  if(!accepted||typeof api?.fetchApi!=='function'||!Number.isSafeInteger(timeoutMs)||
     timeoutMs<1||timeoutMs>15000)throw Error('INVALID_BRUSH_SAVE_PREVIEW');
  if(accepted.state==='saving')throw Error('SAVE_BUSY');
  if(accepted.state==='saved')return accepted.result;
  if(accepted.state==='unknown')throw Error('SAVE_OUTCOME_UNKNOWN');
  const command=accepted.command;
  const current=validatedCommand(report,mask,{
    mode:command.mode,radius:Number(command.radius),points:JSON.parse(command.points),
  });
  if(Object.keys(command).some(key=>current[key]!==command[key]))
    throw Error('PREVIEW_SELECTION_STALE');
  const form=new FormData();
  for(const [key,value] of Object.entries({...command,
    save_version:'1',command_id:accepted.commandId,confirmed:'yes',
    expected_preview_mask_sha256_float32:accepted.digest,
  }))form.append(key,value);
  accepted.state='saving';
  const controller=new AbortController();let timer;
  const timeout=new Promise((_,reject)=>{
    timer=setTimeout(()=>{reject(Error('SAVE_OUTCOME_UNKNOWN'));controller.abort();},timeoutMs);
  });
  const request=(async()=>{
    const response=await api.fetchApi('/smartsvg/g22/subject/save',{
      method:'POST',headers:{'X-SmartSVG-UI':'1'},body:form,signal:controller.signal,
    });
    const body=await response.json();
    if(!response.ok||body?.ok!==true)throw Error(body?.error_code||'SAVE_OUTCOME_UNKNOWN');
    const r=body.result;
    if(body.certified!==false||!r||r.name!==command.name||
       r.command_id!==accepted.commandId||!SHA.test(r.sha256||'')||
       !['subject_brush_saved','subject_brush_already_saved'].includes(r.status)||
       r.persisted!==true||r.cricut_certified!==false)
      throw Error('SAVE_OUTCOME_UNKNOWN');
    return Object.freeze({projectSha256:r.sha256,status:r.status,
                          persisted:true,cricutCertified:false});
  })();
  try{
    const result=await Promise.race([request,timeout]);
    accepted.state='saved';accepted.result=result;return result;
  }catch(error){
    accepted.state='unknown';
    // Only explicit server rejection codes retain their more specific label.
    if(['PROJECT_CHANGED','PROJECT_CHANGED_DURING_SAVE','PROJECT_NOT_HEALTHY',
        'BRUSH_PREVIEW_CHANGED','BRUSH_SESSION_LIMIT','PREVIEW_BUSY',
        'INVALID_SUBJECT_PROOF','SUBJECT_NOT_VERIFIED'].includes(error?.message))throw error;
    throw Error('SAVE_OUTCOME_UNKNOWN');
  }finally{clearTimeout(timer);}
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
