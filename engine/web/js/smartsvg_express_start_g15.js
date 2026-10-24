/** G1.5 – Starter for the current ComfyUI Express node. */
import { app } from "../../scripts/app.js";
import { EXPRESS_CLASS, PROFILES, getProfile, chosenProfile,
         applyProfile, explainFailure } from "./smartsvg_express_start_model_g15.mjs";

const EXTENSION_NAME='smartsvg.studio.g15.express.start';

function e(tag, cls='', text=null) {
  const item=document.createElement(tag);
  if (cls) item.className=cls;
  if (text!==null) item.textContent=String(text);
  return item;
}
function styles() {
  if (document.getElementById('smartsvg-g15-start-css')) return;
  const sheet=e('style');sheet.id='smartsvg-g15-start-css';
  sheet.textContent=[
    '.smartsvg-g15{display:flex;flex-direction:column;gap:8px;background:#1c2631;color:#f0f5fd;font:12px/1.5 system-ui,sans-serif;padding:12px;border:1px solid #697b91;border-radius:10px;box-sizing:border-box;min-width:270px}',
    '.smartsvg-g15 *{box-sizing:border-box}',
    '.smartsvg-g15 strong{font-size:14px}',
    '.smartsvg-g15 select,.smartsvg-g15 button{width:100%;min-height:34px;padding:5px 8px;color:#f6f9ff;background:#2e3d4c;border:1px solid #8499b2;border-radius:6px;font:inherit}',
    '.smartsvg-g15 button{background:#265b77;cursor:pointer;font-weight:700}',
    '.smartsvg-g15 button:disabled{cursor:not-allowed;opacity:.6}',
    '.smartsvg-g15 :focus-visible{outline:2px solid #c5edff;outline-offset:2px}',
    '.smartsvg-g15 .details{padding:8px;border-radius:6px;background:#263543}',
    '.smartsvg-g15 .fine{font-size:11px;color:#d1dce8}',
    '.smartsvg-g15 [role=status]{min-height:20px;font-weight:600}',
    '@media(max-width:420px){.smartsvg-g15{min-width:220px;padding:8px}}',
  ].join('\n');
  document.head.appendChild(sheet);
}

function starter(node) {
  styles();
  const root=e('section','smartsvg-g15');
  root.setAttribute('role','region');
  root.setAttribute('aria-label','Démarrage guidé SmartSVG Express');
  const heading=e('strong','', 'Démarrer avec SmartSVG');
  const label=e('label','','1. Que veux-tu préparer ?');
  const select=e('select');
  const selectId='smartsvg-g15-profile-'+String(node.id ?? 'node').replace(/[^0-9a-zA-Z_-]/g,'').slice(0,24);
  select.id=selectId;label.setAttribute('for',selectId);
  for (const p of PROFILES) {
    const option=e('option','',p.label);
    option.value=p.id;select.appendChild(option);
  }
  const intro=e('div','details');
  const help=e('p','fine');
  const output=e('p','fine');
  const next=e('p','fine');
  intro.append(help,output,next);
  const apply=e('button','','Appliquer le choix au workflow');
  apply.type='button';
  const state=e('div');
  state.setAttribute('role','status');
  state.setAttribute('aria-live','polite');
  const notice=e('p','fine',
    '2. Relier IMAGE dans ComfyUI · 3. Exécuter manuellement · 4. Vérifier les exports. Aucune découpe automatique ni validation Cricut.');
  root.append(heading,label,select,intro,apply,state,notice);

  function render() {
    const profile=getProfile(select.value);
    if (!profile) {
      apply.disabled=true;state.textContent='Usage non reconnu.';
      help.textContent='';output.textContent='';next.textContent='';
      return;
    }
    apply.disabled=false;
    help.textContent=profile.help;
    output.textContent='Sortie visée : '+profile.output;
    next.textContent='Après traitement : '+profile.next;
  }
  const initial=chosenProfile(node);
  select.value=(initial || PROFILES[0]).id;
  render();
  select.addEventListener('change',()=>{
    state.textContent='';
    render();
  });
  apply.addEventListener('click',()=>{
    const result=applyProfile(node,select.value);
    state.textContent=result.ok
      ? (result.changed ? 'Choix appliqué. Vérifier le nœud puis lancer manuellement.' : 'Ce choix est déjà actif.')
      : explainFailure(result.reason);
  });
  return root;
}

app.registerExtension({
  name:EXTENSION_NAME,
  nodeCreated(node) {
    if (!node || (node.comfyClass !== EXPRESS_CLASS && node.type !== EXPRESS_CLASS)) return;
    if (node._smartsvgG15Starter || typeof node.addDOMWidget !== 'function') return;
    try {
      const ui=starter(node);
      const widget=node.addDOMWidget('smartsvg_g15_starter','smartsvg_start',ui,{
        serialize:false,hideOnZoom:true,getMinHeight:()=>255,getMaxHeight:()=>430,
      });
      if (!widget) return;
      widget.serialize=false;
      widget.options={...(widget.options||{}),serialize:false};
      node._smartsvgG15Starter=ui;
      node.size=[Math.max(node.size?.[0]||400,400),Math.max(node.size?.[1]||400,590)];
    } catch (err) {
      console.warn('SmartSVG: guided starter unavailable, legacy node retained',err);
    }
  },
});
