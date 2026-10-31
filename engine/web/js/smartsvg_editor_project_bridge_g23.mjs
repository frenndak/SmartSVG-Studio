/** G2.3 — opt-in bridge from the existing V21.6 editor widget to .smartsvg.
 * Only *native strokes* are saved. Original full-res base masks are NOT saved.
 */
import { decodeDocument,encodeDocument } from './smartsvg_editor_model_v216.mjs';

const NAME=/^[A-Za-z0-9][A-Za-z0-9_-]{0,47}$/;
const API_ROOT='/smartsvg/g22';

export function validName(name){
  return typeof name==='string' && NAME.test(name) && !name.endsWith('_previous');
}
export function createEditorProjectControls(api,app,node){
  const el=(tag,text='')=>{
    const item=document.createElement(tag);
    if(text)item.textContent=text;
    return item;
  };
  const root=el('div');root.className='ss216-project';
  const label=el('label','Projet .smartsvg :');
  const field=el('input');field.type='text';field.maxLength=48;field.placeholder='mon_projet';
  field.setAttribute('aria-label','Nom de projet SmartSVG');
  const save=el('button','Enregistrer les retouches');
  const restore=el('button','Recharger les retouches');
  for(const b of [save,restore])b.type='button';
  const message=el('p','Les masques de base doivent rester dans le workflow : seuls les traits seront sauvegardés.');
  message.setAttribute('role','status');message.setAttribute('aria-live','polite');
  const note=(text)=>{message.textContent=text;};
  let meta=null,linksAtRun=null;
  const links=()=>JSON.stringify(
    (Array.isArray(node?.inputs)?node.inputs:[])
      .filter(x=>x?.name==='image'||x?.name==='masque_base')
      .map(x=>[x.name,x.link??null])
  );
  const request=async(route,opts={})=>{
    if(typeof api?.fetchApi!=='function')throw Error('API_INDISPONIBLE');
    const response=await api.fetchApi(API_ROOT+route,opts);
    const data=await response.json();
    if(!response.ok || !data?.ok)throw Error(data?.error_code||'API_INDISPONIBLE');
    return data;
  };
  const post=async(route,parts)=>{
    const form=new FormData();
    for(const [name,value] of Object.entries(parts))form.append(name,value);
    return request(route,{method:'POST',headers:{'X-SmartSVG-UI':'1'},body:form});
  };
  const preflight=()=>{
    const name=field.value.trim();
    if(!validName(name))throw Error('NOM_INVALIDE');
    if(!meta || !linksAtRun || linksAtRun!==links())throw Error('MASQUES_CHANGES');
    const widget=(node.widgets||[]).find(x=>x.name==='retouches_json');
    if(!widget)throw Error('EDITEUR_ABSENT');
    return {name,widget};
  };
  const translate=code=>({
    NOM_INVALIDE:'Nom invalide : utiliser lettres, chiffres, tirets ou soulignements.',
    MASQUES_CHANGES:'Image ou masques modifiés : relancer le nœud avant toute opération.',
    EDITEUR_ABSENT:'Champ de retouches introuvable sur le nœud actuel.',
    PROJECT_CHANGED:'Le projet a évolué : le rouvrir puis réessayer.',
    EDITOR_CHANGED_DURING_SAVE:'Les retouches, la source ou le projet ont changé pendant le contrôle : aucun enregistrement envoyé. Relancer la sauvegarde.',
    EDITOR_CHANGED_DURING_RESTORE:'Le projet, la source ou les retouches ont changé pendant le chargement : aucun rechargement appliqué. Réessayer.',
    INVALID_EDITOR_STROKE:'Retouches invalides : corriger le dessin dans l’éditeur.',
    INCOMPATIBLE_EDITOR_SOURCE:'Dimensions ou empreinte de source différentes.',
    EDITOR_SESSION_NOT_FOUND:'Aucune retouche enregistrée dans ce projet.',
    API_INDISPONIBLE:'Service de projets désactivé ou indisponible.',
  })[code]||'Opération refusée : vérifier le projet, sa source et la connexion ComfyUI.';

  save.addEventListener('click',async()=>{
    try{
      const {name,widget}=preflight();
      const metaAtStart=meta, linksAtStart=linksAtRun, valueAtStart=widget.value;
      const sourceAtStart=meta.source, widthAtStart=meta.width,
            heightAtStart=meta.height, countAtStart=meta.count;
      const unchanged=()=>meta===metaAtStart && linksAtRun===linksAtStart &&
        links()===linksAtStart && field.value.trim()===name &&
        (node.widgets||[]).find(x=>x.name==='retouches_json')===widget &&
        widget.value===valueAtStart && meta.source===sourceAtStart &&
        meta.width===widthAtStart && meta.height===heightAtStart &&
        meta.count===countAtStart;
      const document=widget.value?.trim()
        ? String(widget.value)
        : encodeDocument(meta,[]);
      decodeDocument(meta,document);
      const info=(await request('/project?name='+encodeURIComponent(name))).project;
      // The GET is asynchronous: never overwrite a project with a snapshot
      // from before the user edited the brush, source, links or project name.
      if(!unchanged())throw Error('EDITOR_CHANGED_DURING_SAVE');
      if(info.status!=='PROJECT_HEALTHY'||!info.sha256)
        throw Error('PROJECT_CHANGED');
      if(info.document?.width_mm===undefined)throw Error('PROJECT_CHANGED');
      const result=await post('/editor/save',{name,editor_json:document,
        expected_sha256:info.sha256});
      if(!unchanged()){
        note('Ancien état enregistré. Les modifications récentes restent à sauvegarder.');
        return;
      }
      note('Retouches conservées : '+String(result.result.strokes_saved)+
        ' trait(s). Masques de base externes, aucune découpe certifiée.');
    }catch(error){note(translate(error.message));}
  });
  restore.addEventListener('click',async()=>{
    try{
      const {name,widget}=preflight();
      const metaAtStart=meta, linksAtStart=linksAtRun, valueAtStart=widget.value;
      const sourceAtStart=meta.source, widthAtStart=meta.width,
            heightAtStart=meta.height, countAtStart=meta.count;
      const unchanged=()=>meta===metaAtStart && linksAtRun===linksAtStart &&
        links()===linksAtStart && field.value.trim()===name &&
        (node.widgets||[]).find(x=>x.name==='retouches_json')===widget &&
        widget.value===valueAtStart && meta.source===sourceAtStart &&
        meta.width===widthAtStart && meta.height===heightAtStart &&
        meta.count===countAtStart;
      const session=(await request('/editor?name='+encodeURIComponent(name))).session;
      // Never apply an asynchronous response to a different local editor state.
      if(!unchanged())throw Error('EDITOR_CHANGED_DURING_RESTORE');
      if(!session||session.base_masks_persisted!==false)
        throw Error('SESSION_INCOMPATIBLE');
      // Critical: node model checks exact sha256(image + base masks), dimensions,
      // instance count, points and bounds before displaying a confirmation.
      const validated=decodeDocument(meta,session.editor_json);
      if(typeof window?.confirm!=='function' ||
         !window.confirm('Remplacer les retouches de ce nœud par '+
             validated.length+' trait(s) du projet ?'))return;
      if(!unchanged())throw Error('EDITOR_CHANGED_DURING_RESTORE');
      const previous=widget.value;
      try{
        widget.value=session.editor_json;
        widget.callback?.(session.editor_json);
      }catch(error){widget.value=previous;throw error;}
      app.graph?.change?.();
      node.setDirtyCanvas?.(true,true);
      note('Retouches rechargées. Relancer le workflow pour appliquer les masques corrigés.');
    }catch(error){note(translate(error.message));}
  });
  field.addEventListener('input',()=>{
    note('Choisir un projet existant. Les masques de base ne sont pas inclus.');
  });
  const refresh=nextMeta=>{
    meta=nextMeta||null;
    linksAtRun=meta?links():null;
    save.disabled=!meta;restore.disabled=!meta;
  };
  root.append(label,field,save,restore,message);
  refresh(null);
  return {root,refresh};
}
