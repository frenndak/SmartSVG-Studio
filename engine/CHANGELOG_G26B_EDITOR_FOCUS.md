# SmartSVG — G2.6b · Inspecteur V21.15.5 vers éditeur V21.6

## Fonction
L'inspecteur ajoute, pour chaque zone signalée, un bouton clavier « Examiner zone ». Il transmet uniquement en mémoire un **intent de zoom** contenant l'empreinte SHA-256 exacte de l'image **et de tous ses masques de base**, les dimensions, l'index du sujet (1-based) et la bbox source.

Le nœud **SmartSVGMaskEditorV216** n'accepte cette demande que si l'empreinte produite par son moteur V21.6 et toutes les dimensions correspondent. Il affiche une action de confirmation dans son panneau. Après confirmation, il ouvre le bon masque en **mode déplacer** et centre la région signalée. L'utilisateur doit choisir explicitement Ajouter/Retirer ; annuler/rétablir et l'enregistrement existants restent inchangés.

Aucun événement externe, modification de masque, nouveau coup de pinceau, export, sauvegarde ou découpe n'est déclenché par le clic dans l'inspecteur. Les demandes expirent dès que l'éditeur reçoit un autre état de source. Le listener est libéré à la suppression du nœud.

## Dépendances
PR #27 (inspecteur V21.15.5), elle-même dépendante de #26. Ne pas réutiliser ce lot directement sur la baseline sans les PR parentes.

## Tests
- Tests purs Node.js des empreintes divergentes, index, bornes, NaN, coordonnées et cadrage.
- Suite des **15 scripts JavaScript** en environnement local de développement : PASS ; adaptations de mocks du test historique V21.6.
- Tests Python ciblés des inspecteurs V21.15.4/V21.15.5 : **15 PASS**.
- Une tentative de la **suite Python complète** de cette branche n'a pas abouti dans la fenêtre d'exécution disponible : résultat global **NON VALIDÉ**.
- CI GitHub G0/CPU requise sur le HEAD ; écran ComfyUI réel, GPU, Design Space et découpe physique non vérifiés.

## Garanties
Pas de nouvelle route réseau, pas de transmission de masques au serveur lors du clic (événement JavaScript local), aucune modification du format `.smartsvg`, aucun changement de ports ou noms de nœuds. Aucune certification « prêt Cricut ».

## Rollback
Réinitialiser `node_v21154.py`, `web/js/smartsvg_subject_inspector_v21154.js`, `web/js/smartsvg_editor_v216.js`, `tests/test_v216_runtime.mjs` sur le commit parent G2.6a ; retirer `web/js/smartsvg_mask_focus_v21156.mjs`, `tests/test_v21156_mask_focus.mjs` et cette note. L'archive source V21.15.2 et la roadmap v3.2 ne sont pas touchées.
