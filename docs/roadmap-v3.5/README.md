# SmartSVG Studio V3.5 — consolidation et livraison du logiciel autonome

**Révision : 13 novembre 2026, Europe/Paris. Statut : PROPOSITION de travail.**
Base examinée : `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`, arbre `e84c7d7dbcbcd9a78a4da28f1e127ec6591d1f54`.

Ce dossier prépare la V3.5 demandée par le propriétaire. Il ne prétend pas qu'une V3.5 existante a été retrouvée : aucune n'a été identifiée dans les fichiers de main, la recherche de PR ou les documents recherchés pendant cette session. [AGENTS.md](../../AGENTS.md) désigne encore la V3.4 comme référence active. Son remplacement doit faire l'objet d'une révision d'autorité explicite, distincte et vérifiée. Ce dossier peut servir immédiatement à préparer les micro-lots compatibles avec cette référence.

## Résultat visé

Une application Windows utilisable sans ComfyUI obligatoire : importer une image, identifier ou corriger un sujet, enregistrer et reprendre son travail, préparer la fabrication, contrôler les sorties et les retrouver dans un dossier choisi. Le chemin manuel/CPU reste utilisable sans modèle ni téléchargement. L'interface Express présente les décisions nécessaires à l'objectif choisi ; l'Atelier donne accès aux réglages avancés et aux calques.

**Les 141 exigences héritées et les 140 tickets V34 restent conservés.** Les 15 tranches V35 sont un ordre de réalisation et des critères de livraison complémentaires, pas 15 nouveaux tickets remplaçant le backlog. Leurs liens sont des liens de planification : aucune couverture fonctionnelle n'en est déduite. Les critères normatifs des sources V3.3/V3.4 restent exigibles dans leur intégralité.

## Documents utilisables

- [État vérifié, écarts et travaux déjà ouverts](01_ETAT_ET_ECARTS.md).
- [15 tranches, critères d'acceptation et parcours de recette](02_EXECUTION.md).
- [Premier micro-lot d'historique natif, prêt à implémenter](03_PROCHAIN_MICROLOT.md).
- [Vérifications effectuées et point de reprise](04_VERIFICATION_ET_REPRISE.md).
- [Backlog structuré : 141 exigences, 140 tickets, dépendances et points de reprise](backlog.json).
- [Contrôleur reproductible de traçabilité](../../tools/verify_roadmap_v35.py).
- [Spécification V3.4 conservée](../roadmap-v3.4/README.md) et [matrice héritée complète](../roadmap-v3.4/23_TRACEABILITE_BACKLOG.md).

## Choix de réalisation

**Choix retenu pour cette proposition : raccordement incrémental du bureau Tk existant aux moteurs existants.** Il préserve les archives et permet de livrer un parcours complet à chaque incrément.

| Option examinée | Apport | Coût / décision |
|---|---|---|
| Raccorder Tk aux services déjà présents | Réutilise sauvegarde, historique, géométrie et contrats ; résultat rapidement vérifiable | Retenue ; mesurer ensuite les limites du canevas |
| Refaire immédiatement l'interface dans un autre framework | Peut améliorer les possibilités graphiques | Double migration, packaging et parité à démontrer ; aucune réécriture imposée ici |
| Finir tous les moteurs avant leur raccordement | Travaux algorithmiques indépendants possibles | Ne rend pas le logiciel utilisable ; les moteurs continuent en parallèle des parcours natifs |

Le choix de Tk est une décision de cette proposition, pas une affirmation que toutes les exigences graphiques y sont déjà satisfaites. Un changement de framework exige des mesures, une ADR et une migration réversible. Ni un bus universel, ni un format V2, ni un assistant, ni un GPU ne sont des prérequis artificiels aux raccordements V1 déjà possibles.

## Ordre de travail

1. Réconcilier les PR #138–140 avec main et leurs preuves avant de modifier leurs mêmes surfaces.
2. Historique natif : disponibilité en lecture seule (#139) puis commandes Annuler/Rétablir sur les services G3.3e existants.
3. Export natif PNG puis Basic Cut, chacun avec réouverture, prévol, provenance et récupération ; multicouche/édition livrés séparément.
4. Calques/propriétés, raster, gabarits, planches et bibliothèque en tranches indépendantes quand leurs dépendances utiles sont disponibles.
5. Installation, tests Windows et qualification terrain progressifs ; ne pas attendre la fin de toute la roadmap pour tester un parcours livré.

Le graphe dans `backlog.json` exprime les dépendances de planification entre tranches, pas une interdiction de travailler sur une fonction indépendante à l'intérieur d'une tranche. Les priorités de chaque ticket historique restent celles de son document source.

## Mesurer l'avancement

Pour chaque critère, suivre séparément : **spécifié → code présent → raccordé au bureau → vérifié automatiquement → vérifié sous Windows → qualifié pour l'usage réel**. Ces états ne s'impliquent pas mutuellement et ne s'additionnent pas en un pourcentage global.

Une preuve contient : critère, révision exacte, commande ou protocole, environnement, résultat, artefact/journal, limites et date. Un test planifié reste `NON_EXECUTE`. Un ancien PASS est une preuve historique de son SHA ; une déclaration sans preuve reste `NON_VERIFIE`. `NON_APPLICABLE` demande une justification par critère, jamais par famille entière.

La sortie du contrôleur de ce dossier est une preuve **documentaire**. Elle ne qualifie ni les fonctions de l'application, ni Windows, ni la RTX 3070, ni Design Space, ni la découpe Explore 5. Aucune nouvelle réussite produit n'est déclarée par cette proposition.

## Contrats maintenus

| Usage | Fichier / propriété à vérifier |
|---|---|
| Print Then Cut | PNG transparent, densité et dimensions explicites, guide d'import et contrôle de l'échelle |
| Basic Cut | SVG de chemins de coupe, unités mm, viewBox et topologie contrôlés |
| Cut multicouche | SVG avec séparation et cohérence des couches ; ordre de fabrication explicite |
| Édition vectorielle | SVG avec géométrie effectivement éditable ; fidélité et limites annoncées |

Un contour vectorisé n'invente pas les calques du dessin. CUT, SCORE, DRAW, PRINT et FOIL ne sont pas interchangeables. Les opérations et outils non qualifiés doivent être indiqués comme tels. Le transfert Design Space est guidé et explicite ; aucun pilotage direct de Cricut ni import automatique non démontré n'est promis.

## Conservation, sécurité et périmètre

Projet unique, IDs de sujets stables, masques float32 comme autorité, originaux conservés, CAS et writers existants, aucune sauvegarde implicite au changement de vue. Conserver anciens IDs/ports ComfyUI et les quatre contrats de sortie. Ne pas placer photos privées, médias tiers, poids de modèles ou secrets dans ce dépôt public. Conserver les limites mémoire et ZIP ; 50 sujets ne signifient pas un tenseur unique de 50 masques lorsque le moteur est limité à 32.

Cette proposition n'altère ni les archives historiques, ni AGENTS, ni les workflows, ni les marqueurs d'automatisation. Les éventuels changements de dépendances, de packaging ou d'autorité seront isolés et vérifiés dans leur propre micro-PR. Aucun déploiement, publication de binaire ou changement de tâche planifiée ne résulte de ce dossier.
