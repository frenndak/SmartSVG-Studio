# SmartSVG V3.4 — Dossier de conception en cours

**DRAFT NON NORMATIF.** La [V3.3](../ROADMAP_MASTER_v3_3.md) demeure la roadmap active. Les archives et chemins protégés restent inchangés.

## Livrables
- [Lot 01 : audit du référentiel et du code](01_BASELINE_AUDIT.md)
- [Lot 02 : vision, personas, parcours stickers/boîte, contrats et tests](02_VISION_PARCOURS.md)
- [Lot 03 : architecture, ADR, interfaces, contrat de fabrication et tests](03_ARCHITECTURE_ADR.md)
- [Lot 04 : migration autonome, adaptateurs, dual-run, sécurité et rollback](04_MIGRATION_AUTONOME.md)
- [Annexe 04 : inventaire du dépôt et graphe de dépendances ciblé — exhaustivité encore ouverte](04_DEPENDENCY_INVENTORY.md)
- [Lot 05 : schéma .smartsvg, identités, ressources, CAS, migration V1→V2 et 20 tests proposés](05_PROJECT_SCHEMA.md)
- [Lot 06 : bus de commandes, receipts/epochs, Undo/Redo, jobs, concurrence et 30 tests proposés](06_COMMAND_BUS.md)
- [Lot 07 : accueil Importer/Créer/Reprendre, Express, navigation, états UX, accessibilité et 28 tests proposés](07_UX_EXPRESS_NAVIGATION.md)
- [Lot 08 : assistant contextuel facultatif, clarification, préférences locales, sécurité, 30 tests et 9 tickets proposés](08_ASSISTANT_CONTEXTUEL.md)
- [Lot 09 : planificateur sécurisé, catalogue fermé, simulation, consentement et 30 tests proposés](09_PLANIFICATEUR_SECURISÉ.md)
- [Lot 10 : analyse visuelle, masques float32/ROI, sujets/accessoires, lots 12/24/50, QA et 30 tests proposés](10_ANALYSE_VISUELLE.md)
- [Lot 11 : catalogue IA facultatif, licences, téléchargements consentis, GPU/CPU, benchmarks, 30 tests proposés](11_MODELES_IA_LOCAUX.md)
- [Lot 12 : raster, alpha, anti-halo, HD conditionnelle, Print Then Cut, 30 tests et 9 tickets proposés](12_RASTER_PIPELINE.md)
- [Lot 13 : vectorisation, SVG édition vs coupe, courbes, topologie, 30 tests et 10 tickets proposés](13_VECTORISATION_SVG.md)
- [Lot 14 : langage Cut/Score/Draw/Print/Foil, prévol déterministe, transfert guidé, 30 tests et 10 tickets proposés](14_LANGAGE_FABRICATION.md)
- [Lot 15 : profils Explore 5, outils/supports/matières, résolution tri-state, 18 tests et 10 tickets proposés (sans nouvelle capacité)](15_PROFILS_EXPLORE5.md)
- [Registre d'opportunités et arbitrages](OPPORTUNITIES.md)
- [Index individuel des 141 exigences V3.3](HERITAGE_INDEX.md)
- [Journal des cycles et reprises](PROGRESS.md)
- [Issue de suivi #72](https://github.com/frenndak/SmartSVG-Studio/issues/72)

## Discipline
Chaque cycle doit relire le HEAD et le journal, produire un micro-lot vérifiable et documenter la prochaine étape. Aucun test logiciel, Windows, GPU, Design Space ou Cricut physique n'est présumé réussi. Les quatre sorties historiques restent distinctes : PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche, SVG d'édition. La sémantique des opérations de fabrication est une couche additionnelle, pas un remplacement silencieux. La migration hors ComfyUI est incrémentale et réversible. Aucune fusion autonome ni promotion V3.4.

## Objectif final
Une spécification de développement par tranches verticales, avec contrats d'interface, parcours débutant/expert, schémas, pseudocode, risques, critères d'acceptation, tests, dépendances et traçabilité bidirectionnelle des 141 exigences héritées et des nouveaux tickets V34.