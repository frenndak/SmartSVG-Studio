/** G2.1 — pure conservative guide state. Never authorizes Cricut production.
 * The real engine still owns export; this module only reads bounded UI metadata.
 */
import {normalizePayload, normalizePreviews} from './smartsvg_ui_model_v2151.mjs';

const MAX_PATH=420;
export const STATES=Object.freeze({
  EMPTY:'EMPTY',INVALID:'INVALID',BLOCKED:'BLOCKED',
  REVIEW:'REVIEW',STALE:'STALE'
});
const EMPTY_MESSAGE='Importer une image, choisir le projet puis lancer le workflow manuellement.';
const INVALID_MESSAGE='Aucun rapport de contrôle exploitable pour cette exécution. Ne pas découper ce résultat.';

/** Observable ComfyUI configuration, no image pixels or private paths exposed.
 * Used for conservative stale-output invalidation after UI edits.
 */
export function configurationSignature(node){
  const names=['projet','largeur_mm','qualite_ppp','ia_locale','dossier_sortie'];
  const widgets=names.map(name=>{
    const value=node?.widgets?.find(w=>w?.name===name)?.value;
    return [name,typeof value==='string' ? value.slice(0,512) :
      (typeof value==='number' && Number.isFinite(value) ? value : null)];
  });
  const inputs=(Array.isArray(node?.inputs)?node.inputs:[])
    .filter(x=>x?.name==='image'||x?.name==='masques_objets')
    .map(x=>[x.name,x.link??null]);
  return JSON.stringify({widgets,inputs});
}

export function evaluateOutput(output,{projectAtRun=null,currentProject=null,expectedObjects=null}={}){
  const raw=Array.isArray(output?.smartsvg) ? output.smartsvg[0] : null;
  // Unknown states, malformed object counts or missing QA must fail closed.
  if(!raw || typeof raw!=='object' || Array.isArray(raw) ||
     !['BLOCKED','REVIEW_REQUIRED'].includes(raw.etat_prevol) ||
     !Number.isSafeInteger(raw.objets_total) || raw.objets_total<0 ||
     typeof raw.action_requise!=='string' ||
     raw.action_requise.trim().length===0 ||
     raw.controle_qualite_disponible!==true ||
     (raw.etat_prevol==='REVIEW_REQUIRED' && raw.objets_total===0)){
    return {state:STATES.INVALID,headline:'Résultat indisponible ou incomplet',
      explanation:INVALID_MESSAGE,action:'Relancer le contrôle après avoir vérifié les entrées.',
      report:null,previews:[],filePath:null,mayCopy:false,verifiedPhysicalCut:false};
  }
  // A profile change after a result invalidates the previous review.
  if(projectAtRun!==null && currentProject!==null && projectAtRun!==currentProject){
    return {state:STATES.STALE,headline:'Résultat obsolète après modification des paramètres',
      explanation:'Le projet, les dimensions, le mode IA ou les connexions ont changé depuis le dernier résultat.',
      action:'Relancer le workflow et vérifier les nouvelles sorties.',
      report:null,previews:[],filePath:null,mayCopy:false,verifiedPhysicalCut:false};
  }
  const report=normalizePayload(output);
  if(!report) {
    return {state:STATES.INVALID,headline:'Rapport illisible',
      explanation:INVALID_MESSAGE,action:'Relancer le traitement.',
      report:null,previews:[],filePath:null,mayCopy:false,verifiedPhysicalCut:false};
  }
  const countMismatch=Number.isSafeInteger(expectedObjects) && expectedObjects>0 && raw.objets_total!==expectedObjects;
  const blocked=raw.etat_prevol==='BLOCKED'||countMismatch;
  const explanation=countMismatch
    ? '⛔ Nombre de sujets incohérent : '+String(raw.objets_total)+' détecté(s), '+String(expectedObjects)+' attendu(s).'
    : blocked
    ? '⛔ Précontrôle bloqué : ces contours ne doivent pas être considérés comme prêts à découper.'
    : '⚠️ Silhouettes candidates : contrôle visuel et import Design Space obligatoires.';
  return {
    state:blocked?STATES.BLOCKED:STATES.REVIEW,
    headline:blocked?'Précontrôle bloqué':'Contrôle manuel indispensable',
    explanation,
    action:report.action_requise || 'Vérifier les dimensions et les contours dans Design Space.',
    report,previews:normalizePreviews(output),
    // A blocked export can still be opened for diagnostics, never as production-ready.
    filePath:report.chemin_sortie?.slice(0,MAX_PATH)||null,
    mayCopy:!!report.chemin_sortie,
    verifiedPhysicalCut:false
  };
}
export function emptyState(){
  return {state:STATES.EMPTY,headline:'Aucun traitement affiché',
    explanation:EMPTY_MESSAGE,
    action:'Relier le port IMAGE puis exécuter dans ComfyUI.',
    report:null,previews:[],filePath:null,mayCopy:false,verifiedPhysicalCut:false};
}
export function statusForDisplay(state){
  if(state===STATES.BLOCKED) return 'BLOQUÉ · aucune validation Cricut';
  if(state===STATES.REVIEW) return 'À VÉRIFIER · aucune validation Cricut';
  if(state===STATES.STALE) return 'PÉRIMÉ · relancer le traitement';
  if(state===STATES.INVALID) return 'ERREUR · aucun export approuvé';
  return 'EN ATTENTE · importer et exécuter';
}
