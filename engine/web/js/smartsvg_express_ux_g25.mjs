/** G2.5: one source of truth for user-facing Express steps and project readiness.
 * View models only; they do not execute ComfyUI, mutate a graph, or approve a cut.
 */
export const STEPS=Object.freeze([
  Object.freeze({id:'SOURCE',short:'Image',label:'1 · Image source'}),
  Object.freeze({id:'PROFILE',short:'Création',label:'2 · Création'}),
  Object.freeze({id:'RUN',short:'Traitement',label:'3 · Traitement'}),
  Object.freeze({id:'CHECK',short:'Contrôle',label:'4 · Contrôle'}),
]);

export function expressStep({imageConnected=false,profileApplied=false,
                            resultState='EMPTY',loading=false}={}){
  if(!imageConnected)return {index:0,state:'SOURCE_REQUIRED',
    explanation:'Relier une image au port IMAGE du nœud avant de lancer le traitement.'};
  if(!profileApplied)return {index:1,state:'PROFILE_REQUIRED',
    explanation:'Appliquer le type de création au workflow avant de lancer le traitement.'};
  if(loading)return {index:2,state:'LOADING',
    explanation:'Traitement en cours. Les résultats ne sont pas encore validés.'};
  if(['BLOCKED','REVIEW','INVALID'].includes(resultState))return {
    index:3,state:resultState,
    explanation:resultState==='REVIEW'
      ?'Revoir les contours et les dimensions avant Design Space.'
      :'Corriger le contrôle signalé avant toute découpe.'
  };
  return {index:2,state:resultState==='STALE'?'STALE':'WAITING',
    explanation:resultState==='STALE'
      ?'Les paramètres ont changé : relancer pour actualiser le résultat.'
      :'Lancer manuellement ComfyUI puis inspecter le contrôle de sortie.'};
}

/** Conservative project-status gates; never labels a saved archive as Cricut-ready. */
export function projectReadiness(info){
  if(!info||info.status==='PROJECT_MISSING')return {
    state:'MISSING',title:'Projet non disponible',
    detail:'Créer le projet à partir d’un PNG original.',recoverable:false};
  if(info.status==='PROJECT_RECOVERABLE')return {
    state:'RECOVERABLE',title:'Version précédente récupérable',
    detail:'Le projet actuel est absent ou corrompu. Examiner le secours et confirmer sa restauration.',
    recoverable:true};
  if(info.status!=='PROJECT_HEALTHY')return {
    state:'ERROR',title:'Projet indisponible',
    detail:'L’archive est illisible ou non vérifiée. Ne pas relancer la découpe.',
    recoverable:false};
  if(!info.sha256||!(/^[a-f0-9]{64}$/).test(info.sha256))return {
    state:'ERROR',title:'Empreinte de révision manquante',
    detail:'Réinspecter le projet avant d’effectuer une opération.',recoverable:false};

  const masks=info.base_masks,session=info.editor_session;
  if(!masks)return {
    state:session?'STROKES_ONLY':'SOURCE_ONLY',
    title:session?'Traits sauvegardés, masques absents':'Source enregistrée',
    detail:session
      ?'Les retouches sont conservées mais les masques exacts manquent : reprendre avec les masques d’origine.'
      :'Capturer les masques de base avec le nœud G2.4 pour poursuivre.',
    recoverable:false};
  if(!masks.exact_float32||!Number.isInteger(masks.count)||masks.count<1 ||
     !(/^[a-f0-9]{64}$/).test(masks.editor_fingerprint||''))return {
    state:'ERROR',title:'Masques non vérifiés',
    detail:'Réinspecter les masques et leurs empreintes. Aucune reprise automatique.',
    recoverable:false};
  if(!session)return {
    state:'MASKS_ONLY',title:'Masques exacts enregistrés',
    detail:'Les masques float32 sont conservés ; aucune retouche V21.6 n’a encore été enregistrée.',
    recoverable:false};
  if(session.source_fingerprint!==masks.editor_fingerprint ||
     session.count!==masks.count)return {
    state:'CONFLICT',title:'Masques et retouches incompatibles',
    detail:'Empreintes ou nombre de sujets différents. Ne pas restaurer automatiquement les traits.',
    recoverable:false};
  return {
    state:'RESTORABLE_MANUALLY',title:'Source, masques et traits cohérents',
    detail:'Reprise possible via les nœuds ComfyUI G2.4 et V21.6. Le graphe ne se reconnecte pas automatiquement.',
    recoverable:false};
}

/** Model 1366×768 and 1920×1080 desktop targets without claiming browser QA. */
export function screenMode(width,height){
  if(!Number.isFinite(width)||!Number.isFinite(height)||width<=0||height<=0)
    return 'compact';
  return width>=1550&&height>=850?'comfortable': 'compact';
}
