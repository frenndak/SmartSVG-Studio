/** V21.15.5: locate suspicious components; diagnostics only, no mask mutations. */
import {app} from '../../scripts/app.js';
import {api} from '../../scripts/api.js';
import {validProjectName,readProjectRevision,makeProjectLock,matchesProjectLock}
  from './smartsvg_subject_project_gate_g33d.mjs';
const FOCUS_EVENT='smartsvg:mask-focus:v1';
const SHA=/^[a-f0-9]{64}$/;
const CLASS='SmartSVGChooseSubjectV21154';
const LABELS=Object.freeze({
  MASQUE_VIDE:'Masque vide',
  FRAGMENTS_DETACHES:'Fragments détachés',
  MICRO_FRAGMENTS:'Petits îlots à examiner',
  TOUCHE_BORD_IMAGE:'Touche un bord de l’image',
  SILHOUETTE_RECTANGULAIRE:'Contour presque rectangulaire',
  SUJET_TRES_PETIT:'Sujet très petit',
});
const element=(tag,content)=>{
  const e=document.createElement(tag);
  if(content!==undefined)e.textContent=String(content);
  return e;
};
const validPreview=value=>typeof value==='string'&&value.length<700000&&
  /^data:image\/png;base64,[A-Za-z0-9+/]+={0,2}$/.test(value);
const validZone=zone=>{
  const coords=zone?.bbox_apercu_88px;
  const src=zone?.bbox_source_px;
  return (zone?.type==='MICRO_FRAGMENT'||zone?.type==='FRAGMENT_SEPARE')&&
    Array.isArray(coords)&&coords.length===4&&coords.every(n=>Number.isInteger(n)&&n>=0&&n<=88)&&
    coords[2]>=coords[0]&&coords[3]>=coords[1]&&
    Array.isArray(src)&&src.length===4&&src.every(n=>Number.isInteger(n)&&n>=0)&&
    src[2]>src[0]&&src[3]>src[1];
};
const makePreview=(item,zones)=>{
  const preview=element('span');
  preview.style.cssText='display:inline-block;position:relative;width:76px;height:76px;flex-shrink:0';
  const img=element('img');img.width=76;img.height=76;
  img.style.cssText='object-fit:contain;width:76px;height:76px;max-width:100%';
  img.src=item.image_data;img.alt='Aperçu du sujet '+item.numero;
  preview.append(img);
  for(const zone of zones){
    const b=zone.bbox_apercu_88px;
    const ring=element('span');
    const left=Math.max(0,Math.min(73,b[0]*76/88));
    const top=Math.max(0,Math.min(73,b[1]*76/88));
    const width=Math.min(76-left,Math.max(3,(b[2]-b[0])*76/88));
    const height=Math.min(76-top,Math.max(3,(b[3]-b[1])*76/88));
    ring.style.cssText=['position:absolute','pointer-events:none',
      'left:'+left+'px','top:'+top+'px','width:'+width+'px','height:'+height+'px',
      'outline:2px solid #ffce73','background:rgba(255,174,0,.17)','box-sizing:border-box'].join(';');
    ring.setAttribute('aria-hidden','true');
    preview.append(ring);
  }
  return preview;
};

function inspector(node){
 const root=element('section');
 root.style.cssText='padding:10px;color:#edf2f7;background:#1c2731;border:1px solid #53687a;border-radius:9px;font:13px system-ui;max-height:320px;overflow-y:auto';
 const title=element('strong','Inspection des silhouettes');
 const hint=element('p','Exécuter le nœud puis choisir une vignette. Rien n’est découpé automatiquement.');
 hint.setAttribute('role','status');hint.setAttribute('aria-live','polite');
 const summary=element('p','Aucune analyse disponible.');
 const layout=element('div');
 layout.style.cssText='display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px';
 const zoneActions=element('div');
 zoneActions.setAttribute('aria-label','Examiner des fragments dans l’éditeur V21.6');
 const share=element('button','Envoyer le dernier diagnostic vers l’Atelier');
 share.type='button';share.disabled=true;
 share.style.cssText='display:block;margin-top:10px;padding:9px;border:1px solid #68aa9c;background:#12423e;color:white;border-radius:7px;cursor:pointer';
 const confirm=element('button','Confirmer le sujet proposé depuis l’Atelier');
 confirm.type='button';confirm.hidden=true;confirm.disabled=true;
 confirm.style.cssText='margin-top:8px;padding:9px;border:2px solid #ffce73;background:#42351b;color:white;border-radius:7px';
 const projectLabel=element('label','Projet .smartsvg à verrouiller (facultatif, lecture seule)');
 const projectName=element('input');
 projectName.type='text';projectName.maxLength=48;
 projectName.id='smartsvg-g33d-project-'+String(node?.id||'node');
 projectLabel.setAttribute('for',projectName.id);
 projectName.placeholder='Nom du projet existant';
 projectName.setAttribute('aria-label','Nom du projet SmartSVG à vérifier avant confirmation');
 projectName.style.cssText='display:block;max-width:100%;margin:5px 0 8px;padding:7px';
 let latest=null,selectionModule=null,selectionBinding=null,selectionChannel=null;
 let selectionTimer=null,pendingSelection=null,widgetAtProposal=null;
 let thumbnailChoiceVersion=0;
 let confirmationInFlight=false,shareInFlight=false,disposed=false;
 // Read-only requests belong to a particular UI/session lifetime. Abort on
 // rerun, edited project name, expiry and final channel closure.
 let shareReadController=null,confirmReadController=null;
 function dispose(){
   disposed=true;stopSelection();latest=null;
   share.disabled=true;confirm.disabled=true;
 }
 function stopSelection(){
   shareReadController?.abort();shareReadController=null;
   confirmReadController?.abort();confirmReadController=null;
   if(selectionTimer!==null){clearTimeout(selectionTimer);selectionTimer=null;}
   selectionChannel?.close();selectionChannel=null;
   selectionBinding=null;pendingSelection=null;widgetAtProposal=null;
   confirm.hidden=true;confirm.disabled=true;
 }
 projectName.addEventListener('input',()=>{
   stopSelection();
   hint.textContent='Projet modifié : renvoyer le diagnostic avant toute proposition.';
 });
 confirm.addEventListener('click',async()=>{
   if(disposed||confirmationInFlight)return; // ignore double clicks while a callback is pending
   const widget=node.widgets?.find(w=>w.name==='numero_sujet');
   const subject=selectionModule?.validateSelectionProposal(
     pendingSelection,selectionBinding,node,latest);
   if(!widget||subject===null||subject===undefined||
      widget.value!==widgetAtProposal){
     hint.textContent='Proposition périmée : nœud, source, liens ou choix modifiés. Relancer le nœud et renvoyer le diagnostic.';
     stopSelection();return;
   }
   const previous=widget.value;
   const manualChoiceAtConfirm=thumbnailChoiceVersion;
   let assignedByConfirmation=false;
   const readController=new AbortController();
   confirmReadController=readController;
   const reportAtConfirm=latest,bindingAtConfirm=selectionBinding;
   const proposalAtConfirm=pendingSelection;
   confirmationInFlight=true;confirm.disabled=true;share.disabled=true;
   try{
     const projectAtConfirm=bindingAtConfirm?.project_name
       ?{project_name:bindingAtConfirm.project_name,
         project_sha256:bindingAtConfirm.project_sha256}:null;
     if(projectAtConfirm){
       const current=await readProjectRevision(api,projectAtConfirm.project_name,{signal:readController.signal});
       // The awaited GET creates a race with a user's newer widget choice.
       // Never overwrite that choice (or a replacement widget) after returning.
       if(node.widgets?.find(w=>w.name==='numero_sujet')!==widget||
          widget.value!==previous)
         throw Error('SELECTION_CHANGED');
       if(!matchesProjectLock(projectAtConfirm,current,reportAtConfirm)||
          projectName.value.trim()!==projectAtConfirm.project_name||
          selectionBinding!==bindingAtConfirm||
          selectionModule.validateSelectionProposal(
            proposalAtConfirm,bindingAtConfirm,node,reportAtConfirm)!==subject)
         throw Error('PROJECT_CHANGED');
     }
     widget.value=subject;
     assignedByConfirmation=true;
     // ComfyUI widgets are usually synchronous, but a Promise rejection must
     // never be mistaken for a successful subject change.
     await widget.callback?.(subject);
     if(projectAtConfirm){
       const current=await readProjectRevision(api,projectAtConfirm.project_name,{signal:readController.signal});
       if(!matchesProjectLock(projectAtConfirm,current,reportAtConfirm)||
          projectName.value.trim()!==projectAtConfirm.project_name)
         throw Error('PROJECT_CHANGED');
     }
     if(latest!==reportAtConfirm||selectionBinding!==bindingAtConfirm||
        pendingSelection!==proposalAtConfirm||
        node.widgets?.find(w=>w.name==='numero_sujet')!==widget||
        widget.value!==subject||
        selectionModule.validateSelectionProposal(
          proposalAtConfirm,bindingAtConfirm,node,reportAtConfirm)!==subject){
       if(assignedByConfirmation&&thumbnailChoiceVersion===manualChoiceAtConfirm&&
          widget.value===subject)widget.value=previous;
       hint.textContent='Proposition périmée pendant la confirmation ; valeur précédente restaurée si inchangée.';
       return;
     }
     node.setDirtyCanvas?.(true,true);
     node.graph?.setDirtyCanvas?.(true,true);
     hint.textContent='Sujet '+subject+' confirmé dans le nœud. Relancer manuellement le workflow ; masques float32 et fragments conservés.';
   }catch(error){
     // Do not roll back a value we never wrote, or a newer explicit thumbnail choice.
     if(assignedByConfirmation&&thumbnailChoiceVersion===manualChoiceAtConfirm&&
        widget.value===subject)widget.value=previous;
     if(error?.message==='PROJECT_BINDING_ABORTED'){
       // A newer execution or changed project owns the UI message/state.
       // The value is restored above only if this confirmation still owns it.
       return;
     }
     hint.textContent=error?.message==='SELECTION_CHANGED'
       ?'Sélection modifiée pendant la vérification du projet : proposition refusée, votre nouveau choix est conservé.'
       :error?.message==='PROJECT_CHANGED'
       ?'Projet .smartsvg modifié ou incompatible : proposition refusée, valeur précédente restaurée si inchangée.'
       :error?.message==='PROJECT_BINDING_TIMEOUT'
       ?'Délai de vérification du projet dépassé : proposition annulée, valeur précédente conservée si inchangée. Réessayer.'
       :'Échec du changement de sujet ou de la vérification du projet ; valeur précédente restaurée si inchangée.';
   }finally{
     confirmationInFlight=false;stopSelection();share.disabled=disposed||!latest;
   }
 });
 // Deliberately NOT connected to onExecuted: user action is mandatory.
 share.addEventListener('click',async()=>{
   if(disposed)return;
   // A pending widget callback owns the current channel until it settles.
   // Do not replace it: its finally block would otherwise close a new channel.
   if(confirmationInFlight||shareInFlight){
     hint.textContent='Transfert ou confirmation en cours : attendre sa fin avant de renvoyer le diagnostic.';
     return;
   }
   if(!latest)return;
   if(!['http:','https:'].includes(window.location.protocol)||
      typeof BroadcastChannel==='undefined'){
     hint.textContent='Transfert indisponible : ouvrir ComfyUI et l’Atelier sur la même origine HTTP.';
     return;
   }
   shareInFlight=true;share.disabled=true;
   stopSelection();
   const readController=new AbortController();
   shareReadController=readController;
   const sourceAtSend=latest;
   try{
     const {normalizeSubjectInspection,SUBJECT_HANDOFF_CHANNEL}=
       await import('./smartsvg_subject_handoff_g33.mjs');
     selectionModule=await import('./smartsvg_subject_selection_g33c.mjs');
     if(readController.signal.aborted||latest!==sourceAtSend)return; // imports or user input invalidated this transfer
     const msg=normalizeSubjectInspection(latest);
     if(!msg){hint.textContent='Diagnostic incomplet ou trop volumineux : relancer le nœud et réessayer.';return;}
     const requestedProject=projectName.value.trim();
     let projectLock=null;
     if(requestedProject){
       if(!validProjectName(requestedProject)){
         hint.textContent='Nom de projet invalide : aucune proposition envoyée.';return;
       }
       const info=await readProjectRevision(api,requestedProject,{signal:readController.signal});
       if(readController.signal.aborted||latest!==sourceAtSend||projectName.value.trim()!==requestedProject)return;
       projectLock=makeProjectLock(requestedProject,info,msg);
       if(!projectLock){
         hint.textContent='Projet incompatible : révision saine et empreinte IMAGE + masques float32 G2.4 identiques requises.';return;
       }
       Object.assign(msg,projectLock);
     }
     const originalBinding=selectionModule.createSelectionBinding(node,msg);
     if(projectLock&&!originalBinding){
       hint.textContent='Liaison du nœud indisponible : projet non envoyé.';return;
     }
     const binding=originalBinding
       ?Object.freeze({...originalBinding,...(projectLock||{})}):null;
     if(binding){
       msg.node_id=binding.node_id;msg.session_id=binding.session_id;
       msg.expires_at_ms=binding.expires_at_ms;
       selectionBinding=binding;
     }
     if(readController.signal.aborted)return; // never revive a session cancelled during imports or GET
     const channel=new BroadcastChannel(SUBJECT_HANDOFF_CHANNEL);
     if(binding){
       selectionChannel=channel;
       channel.onmessage=event=>{
         if(confirmationInFlight)return;
         const subject=selectionModule.validateSelectionProposal(
           event.data,selectionBinding,node,latest);
         if(subject===null)return;
         const widget=node.widgets?.find(w=>w.name==='numero_sujet');
         if(!widget){
           hint.textContent='Champ numero_sujet introuvable : proposition refusée.';
           stopSelection();return;
         }
         pendingSelection=event.data;widgetAtProposal=widget.value;
         confirm.hidden=false;confirm.disabled=false;
         hint.textContent='L’Atelier propose le sujet '+subject+
           '. Vérifier les accessoires puis cliquer « Confirmer » ici. Aucun calcul automatique.';
       };
       selectionTimer=setTimeout(()=>{
         stopSelection();
         hint.textContent='Proposition expirée (90 s) : renvoyer le diagnostic si nécessaire.';
       },90000);
     }
     try{channel.postMessage(msg);}catch(error){stopSelection();throw error;}
     if(!binding)channel.close();
     hint.textContent=binding
       ?'Diagnostic envoyé'+(projectLock?' avec projet '+projectLock.project_name+' verrouillé à la révision '+projectLock.project_sha256.slice(0,12)+'…':' sans projet lié')+'. Choisir un sujet dans l’Atelier, puis confirmer ici dans les 90 s. Aucune modification automatique.'
       :'Diagnostic envoyé en lecture seule. Liaison indisponible : connecter IMAGE/MASK, identifier le nœud et utiliser un navigateur avec crypto.';
   }catch(error){
     // The input/rerun/expiry already invalidated this transfer. Do not
     // replace the newer status message with a stale request error.
     if(readController.signal.aborted)return;
     stopSelection();
     hint.textContent=error?.message==='PROJECT_BINDING_TIMEOUT'
       ?'Délai de lecture du projet dépassé : aucun sujet envoyé. Réessayer ou laisser le champ projet vide.'
       :'Transfert indisponible ; utiliser l’inspecteur du nœud ComfyUI.';
   }finally{
     if(shareReadController===readController)shareReadController=null;
     shareInFlight=false;
     share.disabled=disposed||confirmationInFlight||!latest;
   }
 });
 root.append(title,hint,summary,layout,zoneActions,share,confirm,
   projectLabel,projectName);
 function update(data){
   if(disposed)return;
   stopSelection();latest=null;share.disabled=true;
   layout.replaceChildren();zoneActions.replaceChildren();
   const entry=data?.smartsvg_subjects_v21154?.[0];
   if(!entry||!Array.isArray(entry.sujets)){
     summary.textContent='Aucun diagnostic disponible : utilisez la sélection numérique.';
     hint.textContent='La sélection et le calcul restent disponibles sans cet inspecteur.';
     return;
   }
   const selected=entry.selection;
   const safeSource=SHA.test(String(entry.source_sha256||''))&&Number.isInteger(entry.width_px)&&entry.width_px>0&&
      Number.isInteger(entry.height_px)&&entry.height_px>0&&Number.isInteger(entry.count)&&entry.count>=1&&entry.count<=32;
   if(safeSource&&Array.isArray(entry.sujets)&&entry.sujets.length===entry.count){
     latest=entry;share.disabled=false;
   }
   let issues=0, shown=0;
   for(const item of entry.sujets.slice(0,32)){
     if(!Number.isInteger(item.numero)||item.numero<1||item.numero>32)continue;
     const warnings=Array.isArray(item.codes)?item.codes.filter(code=>Object.hasOwn(LABELS,code)).slice(0,5):[];
     const zones=Array.isArray(item.zones_a_examiner)?item.zones_a_examiner.filter(validZone).slice(0,12):[];
     const hidden=Number.isInteger(item.zones_non_affichees)&&item.zones_non_affichees>=0?
       Math.min(item.zones_non_affichees,1000000):0;
     if(warnings.length||zones.length||hidden)issues++;
     const canSelect=validPreview(item.image_data) && !warnings.includes('MASQUE_VIDE');
     const button=element('button');button.type='button';
     button.style.cssText='background:#293a48;color:#fff;border:2px solid #607689;border-radius:7px;padding:5px;cursor:pointer;min-height:138px;display:flex;flex-direction:column;align-items:center;gap:4px;';
     const name=element('strong','Sujet '+item.numero);
     const message=warnings.length ? warnings.map(w=>LABELS[w]).join(' · ') : 'Inspection visuelle requise';
     const detail=element('span',message);
     detail.style.cssText='font-size:11px;text-align:center;';
     const locations=zones.slice(0,3).map(z=>{
       const b=z.bbox_source_px;
       return (z.type==='MICRO_FRAGMENT'?'Micro-îlot':'Fragment séparé')+' : x'+b[0]+'–'+b[2]+', y'+b[1]+'–'+b[3];
     });
     const extra=zones.length-Math.min(3,zones.length)+hidden;
     const focus=element('span',locations.join(' · ')+(extra>0?' · +'+extra+' autre(s) zone(s)':''));
     focus.style.cssText='font-size:10px;overflow-wrap:anywhere;text-align:center';
     if(canSelect)button.append(makePreview(item,zones),name,detail,focus);
     else button.append(name,element('span','Aucun aperçu exploitable'),detail,focus);
     button.setAttribute('aria-label','Sujet '+item.numero+' : '+message+'. '+(zones.length+hidden)+
       ' zone(s) localisée(s) à inspecter. '+locations.join('; ')+'. '+
       (canSelect?'Cliquer pour choisir et relancer.':'Non sélectionnable ici.'));
     button.setAttribute('aria-pressed',String(item.numero===selected));
     if(item.numero===selected)button.style.borderColor='#82d8bc';
     if(warnings.length||zones.length)button.style.borderStyle='dashed';
     if(!canSelect){button.disabled=true;button.style.opacity='.65';}
     else button.addEventListener('click',()=>{
       const widget=node.widgets?.find(w=>w.name==='numero_sujet');
       if(!widget){hint.textContent='Champ numero_sujet introuvable : choisir manuellement.';return;}
       // A newer explicit thumbnail choice cancels any older pending
       // inspection/confirmation before the widget is changed.
       thumbnailChoiceVersion++;
       stopSelection();
       widget.value=item.numero;
       for(const b of layout.children){
         b.setAttribute('aria-pressed',String(b===button));
         b.style.borderColor=b===button?'#82d8bc':'#607689';
       }
       hint.textContent=`Sujet ${item.numero} choisi. Relancer le workflow pour appliquer la sélection ; corriger les fragments dans l’éditeur de masques si nécessaire.`;
       node.setDirtyCanvas?.(true,true);
       node.graph?.setDirtyCanvas?.(true,true);
     });
     layout.append(button);shown++;
     // Explicit keyboard-operable request; never applies a brush stroke.
     if(safeSource&&item.numero<=entry.count&&zones.length){
       zoneActions.append(element('strong','Sujet '+item.numero+' — zones à inspecter'));
       zones.forEach((z,idx)=>{
         const focus=element('button','Examiner zone '+(idx+1)+' du sujet '+item.numero+' dans V21.6');
         focus.type='button';
         focus.style.cssText='display:inline-block;margin:3px;padding:6px;border:1px solid #ffce73;color:#fff;background:#42351b;border-radius:5px;cursor:pointer';
         focus.addEventListener('click',()=>{
           const payload={version:1,source_sha256:entry.source_sha256,
             width_px:entry.width_px,height_px:entry.height_px,
             subject:item.numero,bbox_source_px:[...z.bbox_source_px]};
           window.dispatchEvent(new CustomEvent(FOCUS_EVENT,{detail:payload}));
           hint.textContent='Zone transmise aux éditeurs V21.6 de même image et mêmes masques. Confirmer dans l’éditeur ; aucun trait modifié.';
         });
         zoneActions.append(focus);
       });
     }
   }
   summary.textContent=`${shown} sujet(s) affiché(s), ${issues} à examiner. Cadres orange = fragments possibles, jamais supprimés. Aucune validation de découpe.`;
   hint.textContent='Cliquer un sujet puis relancer. Un avertissement demande inspection, pas suppression automatique.';
 }
 return {root,update,dispose};
}
app.registerExtension({name:'smartsvg.studio.subjectinspector.v21154',nodeCreated(node){
 if((node?.comfyClass||node?.type)!==CLASS||node._ss21154Inspector||typeof node.addDOMWidget!=='function')return;
 try{
   const ui=inspector(node);
   node.addDOMWidget('smartsvg_subject_inspector_v21154','smartsvg_inspector',ui.root,
     {serialize:false,hideOnZoom:true,getMinHeight:()=>200,getMaxHeight:()=>380});
   node._ss21154Inspector=ui;
   const previous=node.onExecuted;
   node.onExecuted=function(out){previous?.apply(this,arguments);try{ui.update(out);}catch(error){console.warn('SmartSVG inspection advisory',error);}};
   const previousRemoved=node.onRemoved;
   node.onRemoved=function(...args){
     try{ui.dispose();}finally{return previousRemoved?.apply(this,args);}
   };
   node.size=[Math.max(node.size?.[0]||300,430),Math.max(node.size?.[1]||200,470)];
 }catch(error){console.warn('SmartSVG subject inspector disabled',error);}
}});
