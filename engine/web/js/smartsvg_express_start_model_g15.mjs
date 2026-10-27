/** G1.5: pure, no-I/O recommendation model for the *existing* Express node.
 * Does not add ComfyUI ports, replace nodes, execute the graph, or certify a cut.
 */
export const EXPRESS_CLASS = 'SmartSVGExpressV21152';
export const PROFILES = Object.freeze([
  Object.freeze({
    id:'sticker',label:'Autocollant individuel',
    project:'Sticker - contour du sujet',
    help:'Relier une image au port IMAGE. Fond blanc simple : détourage heuristique possible ; photo complexe : fournir un masque ou vérifier le contour.',
    next:'Exécuter puis inspecter les contours, les millimètres et les avertissements. Importer le PNG dans Design Space comme impression puis découpe.',
    output:'PNG Print Then Cut (sous réserve de vérification)',expected:1
  }),
  Object.freeze({
    id:'sheet12',label:'Planche de 12 motifs',
    project:'Planche - 12 images (4x3)',
    help:'Relier une planche contenant 12 motifs à IMAGE. Chaque silhouette doit être contrôlée séparément ; la présence d’une grille ne suffit pas.',
    next:'Examiner les 12 masques, corriger les cadres parasites, vérifier la place sur le papier dans Design Space.',
    output:'Planche PNG Print Then Cut (revue obligatoire)',expected:12
  }),
  Object.freeze({
    id:'sheet24',label:'Planche de 24 motifs',
    project:'Planche - 24 images (6x4)',
    help:'Relier une planche de 24 motifs à IMAGE. Les illustrations sur fond sombre ou complexe peuvent nécessiter des masques manuels.',
    next:'Examiner les 24 objets, les petits îlots alpha et la taille réelle avant d’importer dans Design Space.',
    output:'Planche PNG Print Then Cut (revue obligatoire)',expected:24
  }),
  Object.freeze({
    id:'card',label:'Carte / visuel rectangulaire',
    project:'Carte - visuel rectangulaire',
    help:'Conserver le visuel entier avec une coupe rectangulaire. Ce mode ne détourera pas un personnage.',
    next:'Vérifier les dimensions et sélectionner la bonne opération dans Design Space.',
    output:'Carte rectangulaire, pas un sticker détouré',expected:1
  }),
  Object.freeze({
    id:'auto',label:'Détection prudente',
    project:'Auto - conserver le visuel',
    help:'Conserver le comportement historique Auto lorsque le type de création n’est pas encore connu.',
    next:'Vérifier les objets et le format retenu. Aucune découpe ne peut être présumée correcte.',
    output:'Sortie déterminée par le moteur historique (à contrôler)',expected:null
  })
]);

export function getProfile(id) {
  return PROFILES.find(p=>p.id === id) || null;
}

export function chosenProfile(node) {
  const project = node?.widgets?.find(w=>w?.name === 'projet')?.value;
  return PROFILES.find(p=>p.project === project) || null;
}

export function applyProfile(node, id) {
  const profile = getProfile(id);
  if (!profile) return {ok:false,reason:'CHOIX_INCONNU'};
  if (node?.comfyClass !== EXPRESS_CLASS && node?.type !== EXPRESS_CLASS)
    return {ok:false,reason:'NOEUD_NON_COMPATIBLE'};
  const widget=node?.widgets?.find(w=>w?.name === 'projet');
  const values=widget?.options?.values;
  if (!widget || !Array.isArray(values) || !values.includes(profile.project))
    return {ok:false,reason:'OPTIONS_INCOMPATIBLES'};
  // The normal ComfyUI widget is the only serialized state: no hidden duplicate
  // project profile or browser storage. Never touch the IMAGE/MASK connections.
  const previous=widget.value;
  if (previous === profile.project) return {ok:true,changed:false,profile};
  widget.value=profile.project;
  try {
    if (typeof widget.callback === 'function')
      widget.callback(profile.project, node, widget);
  } catch {
    widget.value=previous;  // no half-applied preset if a custom frontend rejects it
    return {ok:false,reason:'MISE_A_JOUR_REFUSEE'};
  }
  node.setDirtyCanvas?.(true,true);
  return {ok:true,changed:true,profile};
}

export function explainFailure(code) {
  switch(code) {
    case 'CHOIX_INCONNU': return 'Choix non reconnu : sélectionner un usage proposé.';
    case 'NOEUD_NON_COMPATIBLE': return 'Cet assistant est réservé au nœud Express V21.15.2.';
    case 'OPTIONS_INCOMPATIBLES': return 'Options du workflow différentes : aucun paramètre modifié.';
    case 'MISE_A_JOUR_REFUSEE': return 'Le préréglage a été refusé : paramètres précédents conservés.';
    default: return 'Choisir un usage avant de lancer le workflow.';
  }
}
