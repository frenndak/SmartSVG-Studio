# Roadmap SmartSVG V3.3 Design

## Intention

Produire une révision de planification exhaustive qui conserve toutes les ambitions de la roadmap V3.2, sans réduire, supprimer ni repousser silencieusement une capacité. La V3.3 doit rendre explicites les dépendances, les états de maturité, les preuves attendues et les sujets transversaux afin qu'une fonction ne puisse plus être considérée terminée par la seule présence de code.

## Objectifs

- Conserver intégralement les familles F01 à F15, les jalons G0 à G9 et les tickets S-001 à S-101.
- Séparer vision produit, capacités, parcours, architecture, exécution, validation et preuves.
- Donner à chaque capacité une définition de prêt, une définition de terminé et un chemin de rollback.
- Relier chaque exigence à ses parcours, lots, risques, tests et environnements de validation.
- Couvrir explicitement Windows, ComfyUI, CPU/GPU, Design Space, Cricut, accessibilité, sécurité, migration et récupération.

## Non objectifs

- Modifier ou remplacer silencieusement la V3.2 figée.
- Déclarer une capacité livrée, validée sur GPU ou certifiée Cricut sans preuve.
- Modifier le code produit, les workflows GitHub ou les fichiers de gouvernance protégés.
- Réordonner le projet en supprimant des fonctions : l'ordre indique uniquement les dépendances et les portes de validation.

## Contraintes

- `docs/ROADMAP_MASTER_v3_2.md` et `docs/ROADMAP_FREEZE_v3_2.json` restent bit à bit inchangés.
- Le dépôt est public : aucune donnée utilisateur, œuvre privée, secret, poids de modèle ou média sous licence ne peut être ajouté.
- PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche et SVG d'édition restent quatre contrats distincts.
- Les preuves automatisées, Windows, GPU, Design Space et fabrication physique restent séparées.
- La révision est publiée comme proposition documentaire jusqu'à décision de fusion autorisée ; sa promotion opérationnelle exige ensuite un micro-lot distinct de gouvernance protégée.

## Approches considérées

### Réécrire la V3.2 en place

Rejetée : elle détruirait la traçabilité du gel et contreviendrait au contrat du dépôt.

### Copier la V3.2 et ajouter davantage de prose

Rejetée : le document deviendrait plus long sans garantir qu'une exigence soit reliée à une preuve ou à un responsable.

### Révision maître plus deux registres spécialisés

Retenue : un document maître explique la stratégie et les portes, un registre assure la traçabilité des exigences, et une matrice vérifie les dimensions transversales. Cette séparation conserve un point d'entrée lisible tout en permettant une couverture exhaustive et vérifiable.

## Livrables

- `docs/ROADMAP_MASTER_v3_3.md` : vision, parcours, familles, architecture, vagues, gates et gouvernance.
- `docs/ROADMAP_TRACEABILITY_v3_3.md` : conventions de statut et correspondance complète des exigences historiques et nouvelles.
- `docs/ROADMAP_HERITAGE_v3_3.md` : annexe historique normative complète.
- `docs/ROADMAP_COVERAGE_v3_3.md` : matrices de couverture des formats, environnements, erreurs, accessibilité, persistance, sécurité et preuves.

## Décisions de structure

La V3.3 reprend normativement le contenu historique dans une annexe autonome `docs/ROADMAP_HERITAGE_v3_3.md` ; le registre fournit les 101 dossiers canoniques enrichis. Le fichier V3.2 original et son manifeste restent des archives protégées. Les nouvelles exigences de structuration utilisent les identifiants R33-001 et suivants afin d'éviter toute collision avec S-001 à S-101.

Les états d'implémentation communs sont : `SPECIFIE`, `ARCHITECTURE`, `IMPLEMENTE`, `RACCORDE`, `QUALIFIE`, `STABILISE`. Les preuves AUTO, WINDOWS, DESIGN_SPACE et PHYSIQUE sont quatre dimensions indépendantes, chacune justifiée par un SHA et un environnement ; aucune n'est déduite d'une autre.

Les lots sont organisés par dépendances, pas par abandon : fondations et vérité des données, parcours connecté, fabrication, création, production, extensions avancées, stabilisation. Toutes les familles restent visibles jusqu'à leur gate final.

## Critères d'acceptation documentaire

- Les 15 familles et les 10 jalons historiques sont tous présents et reliés.
- Les tickets S-001 à S-101 sont explicitement conservés par plages et vérifiables dans le registre.
- Les parcours principaux disposent d'une entrée, d'une sortie, d'erreurs et de preuves attendues.
- Les dimensions transversales incluent au minimum installation, migration, concurrence, corruption, disque plein, OOM, confidentialité, accessibilité et validation physique.
- Les trois documents se référencent mutuellement et ne contiennent aucun lien local cassé.
- Aucun fichier protégé n'est modifié.
