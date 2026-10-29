# SmartSVG V3.4 — Dossier de conception en cours

**DRAFT NON NORMATIF.** La [V3.3](../ROADMAP_MASTER_v3_3.md) demeure la roadmap active. Les archives et chemins protégés restent inchangés.

## Livrables
- [Lot 01 : audit du référentiel et du code](01_BASELINE_AUDIT.md)
- [Lot 02 : vision, personas, parcours stickers/boîte, contrats et tests](02_VISION_PARCOURS.md)
- [Lot 03 : architecture, ADR, interfaces, contrat de fabrication et tests](03_ARCHITECTURE_ADR.md)
- [Lot 04 : migration autonome, adaptateurs, dual-run, sécurité et rollback](04_MIGRATION_AUTONOME.md)
- [Annexe 04 : inventaire du dépôt et graphe de dépendances ciblé — exhaustivité encore ouverte](04_DEPENDENCY_INVENTORY.md)
- [Registre d'opportunités et arbitrages](OPPORTUNITIES.md)
- [Index individuel des 141 exigences V3.3](HERITAGE_INDEX.md)
- [Journal des cycles et reprises](PROGRESS.md)
- [Issue de suivi #72](https://github.com/frenndak/SmartSVG-Studio/issues/72)

## Discipline
Chaque cycle doit relire le HEAD et le journal, produire un micro-lot vérifiable et documenter la prochaine étape. Aucun test logiciel, Windows, GPU, Design Space ou Cricut physique n'est présumé réussi. Les quatre sorties historiques restent distinctes : PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche, SVG d'édition. La sémantique des opérations de fabrication est une couche additionnelle, pas un remplacement silencieux. La migration hors ComfyUI est incrémentale et réversible. Aucune fusion autonome ni promotion V3.4.

## Objectif final
Une spécification de développement par tranches verticales, avec contrats d'interface, parcours débutant/expert, schémas, pseudocode, risques, critères d'acceptation, tests, dépendances et traçabilité bidirectionnelle des 141 exigences héritées et des nouveaux tickets V34.