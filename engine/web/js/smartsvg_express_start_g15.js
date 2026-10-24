/** G2.1: one guided panel on existing SmartSVGExpressV21152.
 * No new node class, API endpoint, hidden widget serialization, or auto-queue.
 */
import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { EXPRESS_CLASS, PROFILES, getProfile, chosenProfile,
         applyProfile, explainFailure } from "./smartsvg_express_start_model_g15.mjs";
import { evaluateOutput, emptyState, statusForDisplay, STATES, configurationSignature } from "./smartsvg_guide_model_g21.mjs";
import { previewUrl } from "./smartsvg_ui_model_v2151.mjs";
import { createProjectPanel } from "./smartsvg_project_panel_g22.mjs";

const EXTENSION_NAME='smartsvg.studio.g21.express.guide';

function e(tag, cls='', text=null) {
  const item=document.createElement(tag);
  if(cls)item.className=cls;
  if(text!==null)item.textContent=String(text);
  return item;
}
function button(label,click) {
  const b=e('button','',label);
  b.type='button';
  b.addEventListener('click',click);
  return b;
}
function styles() {
  if(document.getElementById('smartsvg-g21-guide-css'))return;
  const style=e('style');
  style.id='smartsvg-g21-guide-css';
  style.textContent=[
    '.smartsvg-g15{display:flex;flex-direction:column;gap:7px;background:#1c2631;color:#f0f5fd;font:12px/1.5 system-ui,sans-serif;padding:11px;border:1px solid #697b91;border-radius:10px;box-sizing:border-box;min-width:260px}',
    '.smartsvg-g15 *{box-sizing:border-box}',
    '.smartsvg-g15 strong{font-size:14px}',
    '.smartsvg-g15 select,.smartsvg-g15 button{width:100%;min-height:32px;padding:5px 8px;color:#f6f9ff;background:#2e3d4c;border:1px solid #8499b2;border-radius:6px;font:inherit}',
    '.smartsvg-g15 button{background:#265b77;cursor:pointer;font-weight:650}',
    '.smartsvg-g15 button:disabled{cursor:not-allowed;opacity:.65}',
    '.smartsvg-g15 :focus-visible{outline:2px solid #c5edff;outline-offset:2px}',
    '.smartsvg-g15 .details{padding:8px;border-radius:6px;background:#263543}',
    '.smartsvg-g15 .fine{font-size:11px;color:#d1dce8}',
    '.smartsvg-g15 [role=status]{min-height:20px;font-weight:600}',
    '.smartsvg-g15 .steps{display:flex;gap:5px;flex-wrap:wrap}',
    '.smartsvg-g15 .steps span{border:1px solid #657b91;border-radius:6px;padding:3px 5px;font-size:10px}',
    '.smartsvg-g15 .result{border:1px solid #60758b;border-radius:7px;padding:8px;display:flex;flex-direction:column;gap:5px}',
    '.smartsvg-g15 .result[data-state=BLOCKED],.smartsvg-g15 .result[data-state=INVALID]{border-color:#ea8b83}',
    '.smartsvg-g15 .result[data-state=REVIEW]{border-color:#f1d18e}',
    '.smartsvg-g15 .cards{max-height:110px;overflow-y:auto;display:flex;flex-direction:column;gap:3px}',
    '.smartsvg-g15 .cards p{margin:0;padding:4px;background:#273a4b;border-radius:4px}',
    '.smartsvg-g15 .preview{width:100%;max-height:135px;object-fit:contain;background:white;border-radius:5px}',
    '.smartsvg-g15 .toolbar{display:flex;flex-wrap:wrap;gap:5px}',
    '.smartsvg-g15 .toolbar button{width:auto;flex:1 1 120px}',
    '.smartsvg-g15 .compact{margin:2px 0}',
    '@media(max-width:420px){.smartsvg-g15{min-width:220px;padding:8px}}',
  ].join('\n');
  document.head.appendChild(style);
}

function starter(node){
  styles();
  const root=e('section','smartsvg-g15');
  root.setAttribute('role','region');
  root.setAttribute('aria-label','SmartSVG : importer, contrôler puis retrouver les exports');
  const heading=e('strong','','SmartSVG · Express guidé');
  const phases=e('div','steps');
  for(const label of ['1 Importer','2 Configurer','3 Lancer','4 Vérifier'])
    phases.appendChild(e('span','',label));
  const label=e('label','','Quel type de création ?');
  const select=e('select');
  const id='smartsvg-g21-profile-'+String(node.id??'node').replace(/[^0-9a-zA-Z_-]/g,'').slice(0,24);
  select.id=id;label.setAttribute('for',id);
  for(const profile of PROFILES){
    const option=e('option','',profile.label);option.value=profile.id;
    select.appendChild(option);
  }
  const intro=e('div','details'),help=e('p','fine compact'),output=e('p','fine compact'),
        next=e('p','fine compact');
  intro.append(help,output,next);
  const apply=e('button','','Appliquer au workflow');
  apply.type='button';
  const state=e('div');
  state.setAttribute('role','status');state.setAttribute('aria-live','polite');
  const notice=e('p','fine compact',
    'Relier IMAGE dans ComfyUI, puis lancer le workflow manuellement. Aucune validation de découpe n’est automatique.');
  const result=e('div','result');
  result.setAttribute('aria-label','Contrôle du dernier traitement SmartSVG');
  const verdict=e('strong'),description=e('p','fine compact'),
        counter=e('p','fine compact'),todo=e('p','fine compact');
  const cards=e('div','cards'),toolbar=e('div','toolbar');
  const preview=e('img','preview');
  preview.alt='Aperçu de contrôle SmartSVG non certifié';preview.hidden=true;
  result.append(verdict,description,counter,cards,toolbar,preview,todo);
  root.append(heading,phases,label,select,intro,apply,state,notice,result);
  // G2.2: explicit local PNG selection. This does NOT reconnect ComfyUI IMAGE.
  root.appendChild(createProjectPanel(api,()=> {
    const value=name=>node.widgets?.find(w=>w?.name===name)?.value;
    return {profile:value('projet'),
      width_mm:Number(value('largeur_mm')??40),
      dpi:Number(value('qualite_ppp')??300)};
  }));

  let latest=emptyState(),projectAtRun=null,hasRun=false,staleSinceRun=false;

  function renderProfile(){
    const profile=getProfile(select.value);
    if(!profile){
      apply.disabled=true;help.textContent='';output.textContent='';next.textContent='';
      state.textContent='Type de création inconnu.';return;
    }
    apply.disabled=false;
    help.textContent=profile.help;
    output.textContent='Format visé : '+profile.output;
    next.textContent='Ensuite : '+profile.next;
  }
  function show(index, refs){
    const reference=refs[index];
    if(!reference)return;
    let url=null;
    try{url=previewUrl(reference,window.location.href,api.apiURL('/view'));}
    catch{return;}
    if(!url)return;
    preview.src=url;preview.hidden=false;
    preview.onerror=()=>{preview.hidden=true;preview.removeAttribute('src');};
  }
  function paint(){
    // The old output loses validity when the underlying ComfyUI project choice changes.
    if(hasRun && configurationSignature(node)!==projectAtRun)staleSinceRun=true;
    const visible=hasRun
      ? evaluateOutput(latest,{projectAtRun,
          currentProject:staleSinceRun?'configuration-changed':configurationSignature(node),
          expectedObjects:chosenProfile(node)?.expected??null})
      : emptyState();
    result.dataset.state=visible.state;
    verdict.textContent=statusForDisplay(visible.state);
    description.textContent=visible.explanation;
    todo.textContent=visible.action;
    const report=visible.report;
    counter.textContent=report?
      String(report.objets_total)+' objet(s) · '+String(report.alertes_total)+' alerte(s) · '+
        String(report.planches_total)+' planche(s)'
      : 'Aucun résultat vérifié à utiliser.';
    cards.replaceChildren();toolbar.replaceChildren();
    preview.hidden=true;preview.removeAttribute('src');
    if(report){
      for(const item of report.objets){
        const card=e('p','fine',
          'Objet '+String(item.numero)+' · '+(item.largeur_mm??'?')+
          ' mm · '+String(item.nombre_alertes)+' alerte(s) · '+item.etat);
        if(item.alertes.length)card.appendChild(e('span','fine',' · '+item.alertes.join(' ; ')));
        cards.appendChild(card);
      }
      visible.previews.forEach((ref,index)=>{
        toolbar.appendChild(button(index===0?'Aperçu global':'Aperçu '+index,
          ()=>show(index,visible.previews)));
      });
      if(visible.previews.length)show(0,visible.previews);
      if(visible.mayCopy){
        toolbar.appendChild(button(visible.state===STATES.BLOCKED ?
          'Copier dossier de brouillons (non validés)' : 'Copier dossier de résultats',()=>{
          if(typeof navigator==='undefined' || !navigator.clipboard?.writeText){
            state.textContent='Copie non disponible dans ce navigateur.';return;
          }
          void navigator.clipboard.writeText(visible.filePath).then(()=>{
            state.textContent='Chemin copié. Vérifier les fichiers avant découpe.';
          }).catch(()=>{state.textContent='Copie refusée ; consulter le rapport du nœud.';});
        }));
      }
    }
    node.setDirtyCanvas?.(true,true);
  }
  const initial=chosenProfile(node);
  select.value=(initial||PROFILES[0]).id;
  renderProfile();
  select.addEventListener('change',()=>{state.textContent='';renderProfile();});
  // Attach the handler to a real button once. Other G1.5 API expectations remain.
  apply.addEventListener('click',()=>{
    const changed=applyProfile(node,select.value);
    state.textContent=changed.ok
      ? (changed.changed?'Choix appliqué ; relancer le workflow pour un nouveau contrôle.':
         'Choix déjà actif. Lancer le workflow si nécessaire.')
      : explainFailure(changed.reason);
    paint();
  });
  paint();
  return {root,updateResult(output){
    projectAtRun=configurationSignature(node);
    latest=output;hasRun=true;staleSinceRun=false;
    state.textContent='';
    paint();
  },refreshIfStale(){
    if(hasRun && !staleSinceRun && configurationSignature(node)!==projectAtRun){
      staleSinceRun=true;paint();
    }
  }};
}

app.registerExtension({
  name:EXTENSION_NAME,
  nodeCreated(node){
    if(!node || (node.comfyClass!==EXPRESS_CLASS && node.type!==EXPRESS_CLASS))return;
    if(node._smartsvgG15Starter || typeof node.addDOMWidget!=='function')return;
    try{
      const panel=starter(node);
      const widget=node.addDOMWidget('smartsvg_g15_starter','smartsvg_start',
        panel.root,{serialize:false,hideOnZoom:true,getMinHeight:()=>340,getMaxHeight:()=>680});
      if(!widget)return;
      widget.serialize=false;
      widget.options={...(widget.options||{}),serialize:false};
      node._smartsvgG15Starter=panel.root;
      node.size=[Math.max(node.size?.[0]||400,420),Math.max(node.size?.[1]||400,700)];
      const old=node.onExecuted;
      node.onExecuted=function(output){
        old?.apply(this,arguments);
        try{panel.updateResult(output);}
        catch(err){console.warn('SmartSVG guide rendering unavailable',err);}
      };
      // Also detect changes to old ComfyUI widgets made outside this panel.
      const oldForeground=node.onDrawForeground;
      node.onDrawForeground=function(){
        const result=oldForeground?.apply(this,arguments);
        try{panel.refreshIfStale();}catch(err){
          console.warn('SmartSVG stale check unavailable',err);
        }
        return result;
      };
    }catch(err){
      console.warn('SmartSVG guided panel unavailable; Python node remains operational',err);
    }
  }
});
