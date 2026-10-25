/** G2.5 — pure UI recovery-state model over a validated G2.2/G2.4 report.
 * A complete archive is NOT a restored ComfyUI graph or a verified Cricut cut.
 * Incomplete, contradictory or unrecognized reports always fail closed.
 */
const SHA=/^[0-9a-f]{64}$/;
const STATES=Object.freeze({
  EMPTY:'EMPTY', LOADING:'LOADING', ERROR:'ERROR', RECOVERABLE:'RECOVERABLE',
  UNAVAILABLE:'UNAVAILABLE', UNKNOWN:'UNKNOWN', SOURCE_ONLY:'SOURCE_ONLY',
  STROKES_ONLY:'STROKES_ONLY', MASKS_ONLY:'MASKS_ONLY',
  COMPLETE_MANUAL:'COMPLETE_MANUAL', INCOMPATIBLE:'INCOMPATIBLE'
});
export {STATES as RESUME_STATES};

const step=(id,label,status,help)=>({id,label,status,help});
const steps=(source,masks,strokes)=>[
  step('source','Image originale',source?'saved':'needed',
    source?'PNG source conservé dans le projet.':'Importer et vérifier le PNG source.'),
  step('masks','Masques de base exacts',masks?'saved':'needed',
    masks?'Valeurs float32 sauvegardées sans perte.':'Capturer les vrais MASK avec le nœud G2.4, pas les miniatures.'),
  step('strokes','Retouches V21.6',strokes?'saved':'needed',
    strokes?'Coups de pinceau enregistrés.':'Enregistrer les retouches dans le projet depuis l’éditeur V21.6.'),
  step('workflow','Connexions ComfyUI','manual',
    'Le graphe ne se reconnecte pas automatiquement. Vérifier IMAGE/MASK, puis relancer manuellement.')
];
const result=(state,title,action,{source=false,masks=false,strokes=false,
  revision=null,restore=false}={})=>({
  state,title,action,steps:steps(source,masks,strokes),
  revision,mayRestore:restore,mayOpenSource:source,
  machineReady:false,cutVerified:false,graphRestored:false
});
export function resumeEmpty(){
  return result(STATES.EMPTY,'Aucun projet chargé',
    'Saisir un nom puis choisir « Ouvrir et inspecter ».');
}
export function resumeLoading(){
  return result(STATES.LOADING,'Lecture et contrôle du projet…',
    'Attendre la réponse du dossier local SmartSVG.');
}
export function resumeError(){
  return result(STATES.ERROR,'Ouverture indisponible',
    'Vérifier le nom, les droits ComfyUI et l’activation du service projets.');
}

export function resumeFromProject(report){
  if(!report || typeof report!=='object' || Array.isArray(report))
    return result(STATES.UNKNOWN,'Rapport manquant',
      'Réinspecter le projet ; aucune restauration autorisée.');
  if(report.status==='PROJECT_RECOVERABLE'){
    const verified=report.recoverable===true && SHA.test(report.recovery_sha256||'');
    return result(verified?STATES.RECOVERABLE:STATES.UNAVAILABLE,
      verified?'Secours disponible — confirmation requise':'Secours non vérifié',
      verified?'Utiliser « Restaurer le secours » puis ouvrir à nouveau.':
        'Ne pas tenter de réouverture ; vérifier la sauvegarde.',
      {restore:verified});
  }
  if(report.status!=='PROJECT_HEALTHY')
    return result(STATES.UNAVAILABLE,'Projet indisponible ou corrompu',
      'Inspecter le dossier ou la sauvegarde précédente sans écraser le projet.');
  if(!SHA.test(report.sha256||'') || !report.document ||
     typeof report.document!=='object' || Array.isArray(report.document) ||
     report.source_count!==1 ||
     typeof report.document.profile!=='string' || !report.document.profile ||
     typeof report.document.stage!=='string' || !report.document.stage)
    return result(STATES.UNKNOWN,'Informations de projet incomplètes',
      'Réinspecter l’archive avant toute reprise.');
  const source=true;
  const mask=report.base_masks;
  const editor=report.editor_session;
  const masks=!!(mask && mask.exact_float32===true &&
    Number.isSafeInteger(mask.count) && mask.count>=1 && mask.count<=32 &&
    Array.isArray(mask.dimensions_px) && mask.dimensions_px.length===2 &&
    mask.dimensions_px.every(x=>Number.isSafeInteger(x)&&x>0) &&
    SHA.test(mask.editor_fingerprint||'') &&
    SHA.test(mask.source_fingerprint||''));
  const strokes=!!(editor && editor.available===true &&
    Number.isSafeInteger(editor.count) && editor.count>=1 && editor.count<=32 &&
    Number.isSafeInteger(editor.stroke_count) && editor.stroke_count>=0 &&
    editor.stroke_count<=400 && SHA.test(editor.source_fingerprint||''));
  const rev=report.sha256;
  // A malformed presence of either section must not be treated as absence.
  if((mask && !masks)||(editor && !strokes) ||
     (masks && strokes && (mask.count!==editor.count ||
       mask.editor_fingerprint!==editor.source_fingerprint)))
    return result(STATES.INCOMPATIBLE,'Données de reprise incohérentes',
      'Ne rien importer. Contrôler les empreintes et versions de masques/retouches.',
      {source,revision:rev});
  if(masks && strokes)
    return result(STATES.COMPLETE_MANUAL,'Source, masques et retouches conservés',
      'Raccorder l’IMAGE au nœud G2.4, restaurer les MASK, puis charger les retouches dans V21.6. Vérifier avant export.',
      {source,masks,strokes,revision:rev});
  if(masks)
    return result(STATES.MASKS_ONLY,'Source et masques conservés',
      'Restaurer les MASK via G2.4, puis ajouter ou recharger les retouches dans V21.6.',
      {source,masks,revision:rev});
  if(strokes)
    return result(STATES.STROKES_ONLY,'Source et retouches, masques manquants',
      'Retrouver les masques de base identiques avant d’appliquer les retouches.',
      {source,strokes,revision:rev});
  return result(STATES.SOURCE_ONLY,'Image originale sauvegardée',
    'Relier le PNG à ComfyUI puis enregistrer les masques et les retouches.',
    {source,revision:rev});
}
