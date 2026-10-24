# SmartSVG — G2.1 : parcours Express guidé dans ComfyUI

**Périmètre exact.** Ce lot combine le panneau de démarrage G1.5 et le contrôle V21.15.2 dans **une seule interface facultative** sur le nœud historique SmartSVGExpressV21152. Il ne prétend pas remplacer le moteur, créer un programme indépendant ou ouvrir des projets .smartsvg.

## Parcours utilisateur

1. **Importer :** relier une image au port ComfyUI IMAGE (les masques facultatifs restent possibles).
2. **Configurer :** choisir Sticker, Planche 12, Planche 24, Carte ou Auto. Cliquer « Appliquer au workflow ». Seul le widget projet historique change.
3. **Lancer :** exécuter manuellement le workflow dans ComfyUI, sans moteur d'exécution ajouté à l'interface.
4. **Vérifier :** lire le verdict du contrôle V21.15.2, l'action requise, la liste bornée des objets et, si disponibles, les aperçus contrôlés via l'API officielle ComfyUI /view.
5. **Retrouver les fichiers :** copier le chemin de sortie pour inspection. Ce bouton **ne télécharge pas** et **n'autorise pas la fabrication** ; les résultats bloqués restent accessibles uniquement comme brouillons de diagnostic.

## Sûreté du verdict

Le modèle de présentation engine/web/js/smartsvg_guide_model_g21.mjs refuse par défaut :
- rapport manquant, malformé ou sans contrôle qualité déclaré ;
- statut inconnu ou « PASS » non prévu au contrat ;
- REVIEW_REQUIRED avec 0 objet ;
- écart entre nombre d'objets et profil explicitement choisi (12 ou 24) ;
- ancien résultat affiché après changement du profil du nœud.

Seuls deux états métiers peuvent apparaître pour des résultats exploitables : **BLOCKED** et **REVIEW_REQUIRED**. REVIEW_REQUIRED ne veut **jamais** dire que Design Space a importé le fichier, ni que la découpe physique est validée.

Le contrôle de cohérence par profil est un **garde de présentation** et ne modifie pas les fichiers de production. Si le backend a généré 12 objets lors d'une planche attendue à 24, le panneau affiche BLOQUÉ, même si son rapport initial demandait seulement une revue.

## Compatibilité et accessibilité

- Le vieux dashboard reste actif pour SmartSVGExpressV2151, mais plus pour SmartSVGExpressV21152 afin d'éviter deux panneaux.
- Le même ID de nœud V21.15.2 est conservé. Aucun port ni entrée ni sortie ne change.
- La sélection est celle du widget ComfyUI historique ; le composant DOM est explicitement non sérialisé.
- Mise en page compacte, contrôles au clavier, label explicite, rôle de statut avec aria-live.
- Écritures via textContent uniquement, sans innerHTML ni route HTTP privée. Les prévisualisations utilisent les refs contraintes du sous-dossier SmartSVG_Studio_Previews et le builder d'URL ComfyUI.
- Pas de fuite automatique des chemins ; bouton de copie sous geste de l'utilisateur.
- Frontend ancien sans addDOMWidget : repli sur le nœud Python précédent.

## Limites et validation

- Les projets .smartsvg et la reprise G1.3/G1.4 sont prêts au niveau backend mais **pas encore reliés** à cette interface. Il n'y a pas encore de boutons « Sauvegarder », « Ouvrir » ou « Restaurer ».
- Les anciens rapports ne prouvent pas cryptographiquement quels paramètres ont été utilisés au démarrage d'une tâche. G2.1 prend l'état des widgets à l'affichage du résultat et invalide les changements postérieurs. La liaison fiable des run IDs et fingerprints est un travail futur.
- Aucune validation réelle sous Windows, aucune IA RTX 3070, aucun import Design Space ni coupe Explore 5 n'a été réalisé par ce lot.
- L'intégration dépend de l'ordre des PR empilées #14 → #15 → #16 → #17 → G2.1. Pas de fusion automatique avant revue.

## Tests

- engine/tests/test_g21_guided_express.mjs : états invalides, blocages, 12/24 motifs, non-certification, changement de profil, prévisualisation sûre, DOM du vrai panneau et isolation des anciens nœuds.
- tests/test_g21_guided_express.py : lance les tests Node.js dans la CI privée, sans modifier les workflows.
- Rejouer aussi test_g15_express_start.mjs, les tests dashboard V21.5.1 et la suite Python G0.

**Prochaine étape G2.2 :** flux d'erreur/récupération guidé et liaison du projet .smartsvg aux actions réelles, sous tests Windows/ComfyUI. Ne pas inventer d'endpoint ou de bouton inerte avant d'avoir un backend exposé de manière sûre.
