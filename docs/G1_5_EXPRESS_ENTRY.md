# SmartSVG Studio — G1.5 : un seul démarrage Express recommandé

**Objectif :** guider la préparation Cricut depuis le nœud déjà existant SmartSVGExpressV21152, sans casser les 186 workflows historiques ni leurs signatures ComfyUI.

**Base de développement :** PR #16 (G1.4) → PR #15 (G1.3) → PR #14 (G1.2), toutes conservées en revue. L'archive originale V21.15.2 et ses manifestes restent inchangés.

## Expérience utilisateur livrée dans ce micro-lot

Un petit panneau additionnel dans le **nœud Express V21.15.2** :

1. Choisir un objectif dans la liste : autocollant individuel, planche de 12 motifs, planche de 24 motifs, carte rectangulaire, Auto prudent.
2. Lire la fiche explicative : ce qui sera conservé, ce qui peut nécessiter un masque et les limites de la découpe.
3. Cliquer « Appliquer le choix au workflow ». Le panneau modifie exclusivement le widget historique **projet**.
4. Relier le port IMAGE, exécuter manuellement dans ComfyUI, consulter les aperçus et contrôles du tableau de bord déjà existant.

L'assistant ne lance pas le graphe, ne choisit pas de matière, ne prétend pas que le SVG est éditable ni que l'import ou la découpe Cricut est validée. Il ne fait pas encore de détourage interactif.

## Contrats techniques

- Modèle pur : engine/web/js/smartsvg_express_start_model_g15.mjs (profil → option historique exacte, validation stricte).
- Panneau facultatif : engine/web/js/smartsvg_express_start_g15.js, chargé par le répertoire WEB_DIRECTORY actuel sans ajout d'endpoint.
- Compatible uniquement avec l'ID SmartSVGExpressV21152. Les anciens IDs et workflows ne sont ni retirés ni renommés.
- L'option est sélectionnée uniquement si le widget existant la contient dans ses options ; sinon échec explicite sans modifier le projet.
- Les ports IMAGE et MASK, IA, dimension mm, PPI et dossier de sortie ne sont jamais réécrits.
- Widget DOM additionnel non sérialisé. Seule la valeur du widget ComfyUI historique est enregistrée.
- Focus, label, bouton accessible au clavier, statut aria-live, tailles compactes et aucun HTML injecté.
- Si le frontend ne prend pas en charge addDOMWidget, l'ancien nœud reste opérationnel.

## Tests de non-régression

engine/tests/test_g15_express_start.mjs :
- correspondance exacte des cinq anciens modes et explications ;
- sélections successives sans modifier les ports ni d'autres widgets ;
- inaction si le choix est déjà actif ;
- refus des anciens IDs et des valeurs invalides ;
- rollback en cas d'erreur de callback ;
- DOM clavier et aria, non-sérialisation ;
- absence de modification des anciens nœuds et repli sur vieux frontend ;
- absence d'actions export et de HTML/script dangereux.

tests/test_g15_express_start.py exécute ces tests Node.js dans le CI d'admission existant et vérifie qu'aucune classe de nœud n'est ajoutée.

**Gate :** tests GitHub sur HEAD exact, empreinte historique V21.15.2, tests CPU et revue du diff. Une vérification réelle de la navigation clavier dans ComfyUI Windows reste indispensable avant validation ergonomique complète.

## Étape suivante (G2.1)

Relier les étapes d'Express à un écran plus autonome « importer → contrôler → exporter », avec états vides, erreur, récupération, visualisation de chaque sujet, et sauvegarde .smartsvg branchée au vrai flux d'édition. Le présent panneau est un prérequis limité, pas cette interface autonome.

## État de preuve

Aucun test RTX 3070, Design Space, découpe Cricut physique ou interaction Windows réelle n'est déclaré. Les images utilisateur ne sont pas ajoutées au dépôt public.
