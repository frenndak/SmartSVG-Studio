/** G2.2 browser controls for managed .smartsvg files.
 * Never reads arbitrary server files, never queues a graph, and never
 * claims reopening a .smartsvg restores the editor/IMAGE connection.
 */
import { projectReadiness } from './smartsvg_express_ux_g25.mjs';

export const PROJECT_NAME=/^[A-Za-z0-9][A-Za-z0-9_-]{0,47}$/;
const BYTES_LIMIT=12*1024*1024;
const ROOT='/smartsvg/g22';

export function validProjectName(value){
  return typeof value==='string' && PROJECT_NAME.test(value) && !value.endsWith('_previous');
}
export function projectError(code){
  const map={
    INVALID_PROJECT_NAME:'Nom invalide : lettres, chiffres, tirets et soulignements (48 maximum).',
    PROJECT_ALREADY_EXISTS:'Ce nom est déjà utilisé. Ouvrir ce projet ou choisir un autre nom.',
    INVALID_PNG:'PNG illisible : choisir un fichier PNG valide.',
    INVALID_IMAGE_MODE:'PNG non compatible : utiliser RVB ou niveaux de gris.',
    REQUEST_TOO_LARGE:'Image trop volumineuse (12 Mo maximum).',
    PROJECT_CHANGED:'Le projet a été modifié : le rouvrir avant d’enregistrer.',
    BACKUP_CONFLICT:'Le secours existant est incompatible ou endommagé : aucune donnée écrasée.',
    NOT_RECOVERABLE:'Aucune sauvegarde valide ne peut être restaurée.',
    RECOVERY_SNAPSHOT_CHANGED:'La sauvegarde précédente a changé : recommencer l’inspection.',
    SAVE_FAILED:'Écriture refusée : contrôler le dossier ou les permissions.',
    ORIGIN_REJECTED:'Requête refusée : utiliser cette interface depuis ComfyUI.',
  };
  return map[code]||'Opération indisponible. Vérifier que le module de projets G2.2 est activé dans ComfyUI.';
}

export function createProjectPanel(api, currentSettings, ownerId='default'){
  const el=(tag,text='')=>{
    const item=document.createElement(tag);
    if(text)item.textContent=text;
    return item;
  };
  const root=el('section');
  root.setAttribute('aria-label','Projet SmartSVG sauvegarde et récupération');
  root.className='details';
  const title=el('strong','Projet .smartsvg · Sauvegarde locale');
  const label=el('label','Nom du projet');
  const name=el('input');name.type='text';name.maxLength=48;
  name.placeholder='exemple_escargots';
  const inputId='smartsvg-g22-name-'+String(ownerId).replace(/[^a-zA-Z0-9_-]/g,'').slice(0,30);
  name.id=inputId;label.setAttribute('for',inputId);
  const fileLabel=el('label','PNG original à enregistrer dans le projet');
  const file=el('input');file.type='file';file.accept='image/png';
  const noteLabel=el('label','Notes du projet (facultatif)');
  const notes=el('textarea');notes.maxLength=1500;notes.rows=2;
  const actions=el('div');actions.className='toolbar';
  const status=el('p');status.setAttribute('role','status');
  status.setAttribute('aria-live','polite');
  const details=el('p');details.className='fine';
  const readiness=el('p');readiness.className='fine';
  readiness.textContent='État du projet : aucune archive ouverte.';
  const source=el('img');source.className='preview';source.hidden=true;
  source.alt='Source conservée dans le projet, sans validation de découpe';
  const hint=el('p','Sauvegarde : sélectionner explicitement un PNG local. Ouvrir réaffiche sa source et ses notes, mais ne restaure pas encore les retouches ni le graphe ComfyUI.');
  hint.className='fine';
  let loaded=null,pending=false;
  const actionButtons=[];
  const discard=()=>{
    loaded=null;
    saveNotes.disabled=true;restore.disabled=true;
    source.hidden=true;source.removeAttribute('src');
    readiness.textContent='Projet à réinspecter avant toute modification.';
  };
  const action=(text,handler)=>{
    const button=el('button',text);button.type='button';
    button.addEventListener('click',async()=>{
      if(pending)return;
      pending=true;
      root.setAttribute('aria-busy','true');
      for(const b of actionButtons)b.disabled=true;
      try{await handler();}
      finally{
        pending=false;
        root.setAttribute('aria-busy','false');
        for(const b of actionButtons)b.disabled=false;
        saveNotes.disabled=!loaded?.sha256;
        restore.disabled=!loaded?.recoverable;
      }
    });
    actions.appendChild(button);
    actionButtons.push(button);
    return button;
  };
  const show=(text)=>{status.textContent=text;};
  const nameValue=()=>name.value?.trim()||'';
  const request=async(route,options={})=>{
    if(typeof api?.fetchApi!=='function')throw Error('PROJECT_API_UNAVAILABLE');
    const response=await api.fetchApi(ROOT+route,options);
    let body;
    try{body=await response.json();}catch{throw Error('PROJECT_API_UNAVAILABLE');}
    if(!response.ok || !body?.ok)throw Error(body?.error_code||'PROJECT_API_UNAVAILABLE');
    return body;
  };
  const form=(fields)=>{
    const data=new FormData();
    for(const [key,value] of Object.entries(fields))data.append(key,value);
    return data;
  };
  const post=(route,fields)=>request(route,{
    method:'POST',headers:{'X-SmartSVG-UI':'1'},body:form(fields),
  });
  const inspect=async()=>{
    const n=nameValue();
    if(!validProjectName(n))throw Error('INVALID_PROJECT_NAME');
    const result=await request('/project?name='+encodeURIComponent(n));
    if(nameValue()!==n)throw Error('PROJECT_SELECTION_CHANGED');
    loaded=result.project;
    const level=projectReadiness(loaded);
    readiness.textContent=level.title+' — '+level.detail;
    details.textContent='Statut : '+loaded.status+
      (loaded.document ? ' · '+String(loaded.document.width_mm)+' mm · '+String(loaded.document.dpi)+' ppp' : '')+
      (loaded.sha256 ? ' · SHA-256 révision (à copier dans le nœud G2.4) : '+loaded.sha256 : '')+
      (loaded.base_masks ? ' · '+String(loaded.base_masks.count)+' masque(s) float32 intacts' : '')+
      ' · découpe non certifiée';
    if(loaded.document && typeof loaded.document.notes==='string')
      notes.value=loaded.document.notes;
    source.hidden=true;source.removeAttribute('src');
    if(loaded.status==='PROJECT_HEALTHY'){
      source.src=api.apiURL(ROOT+'/source?name='+encodeURIComponent(n));
      source.hidden=false;
      source.onerror=()=>{source.hidden=true;source.removeAttribute('src');};
    }
    restore.disabled=!loaded.recoverable;
    saveNotes.disabled=!loaded.sha256;
    return loaded;
  };
  const save=action('Créer projet depuis PNG',async()=>{
    try{
      const n=nameValue(),chosen=file.files?.[0];
      if(!validProjectName(n))throw Error('INVALID_PROJECT_NAME');
      if(!chosen||chosen.size>BYTES_LIMIT||chosen.size<40||
         !/\.png$/i.test(chosen.name))throw Error('INVALID_PNG');
      const config=currentSettings();
      show('Enregistrement en cours…');
      await post('/create',{name:n,image:chosen,profile:config.profile,
        width_mm:String(config.width_mm),dpi:String(config.dpi),notes:notes.value||''});
      await inspect();show('Projet créé. Source PNG conservée ; découpe non certifiée.');
    }catch(err){show(projectError(err.message));}
  });
  const open=action('Ouvrir et inspecter',async()=>{
    try{
      show('Ouverture et vérification du projet en cours…');
      await inspect();show('Projet inspecté. Lire son état avant de reprendre.');
    }
    catch(err){discard();show(projectError(err.message));}
  });
  const saveNotes=action('Enregistrer les notes',async()=>{
    try{
      if(!loaded?.sha256)throw Error('PROJECT_CHANGED');
      await post('/notes',{name:nameValue(),notes:notes.value||'',expected_sha256:loaded.sha256});
      await inspect();show('Notes enregistrées. Sauvegarde précédente conservée.');
    }catch(err){
      if(['PROJECT_CHANGED','PROJECT_CHANGED_DURING_SAVE'].includes(err.message))discard();
      show(projectError(err.message));
    }
  });
  const restore=action('Restaurer le secours',async()=>{
    try{
      if(!loaded?.recoverable||!loaded.recovery_sha256)throw Error('NOT_RECOVERABLE');
      if(typeof window?.confirm!=='function'||!window.confirm(
        'Restaurer la précédente version vérifiée du projet ? Le fichier corrompu actuel sera remplacé.'))return;
      await post('/restore',{name:nameValue(),
        expected_recovery_sha256:loaded.recovery_sha256,confirmed:'yes'});
      await inspect();show('Version précédente restaurée après confirmation.');
    }catch(err){show(projectError(err.message));}
  });
  saveNotes.disabled=true;restore.disabled=true;
  name.addEventListener('input',()=>{
    discard();details.textContent='';
  });
  root.append(title,label,name,fileLabel,file,noteLabel,notes,
    actions,status,readiness,details,source,hint);
  return root;
}
