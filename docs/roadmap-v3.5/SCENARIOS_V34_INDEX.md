# SmartSVG V3.5 — Index des 437 scénarios historiques V3.4

> **Inventaire contrôlé le 12 novembre 2026, non normatif.** Sources du commit `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`. Ce registre copie les **identifiants et assertions documentaires**, jamais un résultat de test. Les documents d'inventaire ont été enregistrés sur la branche de conception `roadmap/v3-5-design-candidate-20261112` et relus pour contrôler **437 IDs uniques sur 437, sans trou par lot ni doublon**.
>
> **États rigoureusement distincts :** `SOURCE_INVENTORIÉE` ≠ `LIEN_EXIGENCE_ET_TICKET_QUALIFIÉ` ≠ `TEST_IMPLÉMENTÉ` ≠ `PASS_UNITAIRE` ≠ `PASS_WINDOWS` ≠ `PASS_DESIGN_SPACE` ≠ `PASS_PHYSIQUE`.

## 1. Inventaire et contrôles effectivement réalisés

- 21 tables de recettes (lots 02 à 22) : **437 entrées uniques** `T-V34-LL-NN`, de NN=01 à NN=n sans interruption dans chaque lot ; vérification des identifiants attendus et du nombre de lignes source de chaque lot.
- Lots 01 et 23–24 : aucune table contenant de nouveaux IDs `T-V34-LL-NN` à compter ; ils continuent à contenir des exigences, méthodes, références ou renvois vers des recettes existantes.
- Copies conservant chaque **ligne source intégrale** dans des blocs de texte, associée au chemin du fichier V3.4, au **blob SHA** lu à la source et à son **numéro de ligne**.
- Les textes n'ont pas été paraphrasés dans les inventaires ; ils ne sont ni des critères nouveaux ni des essais réalisés. La vérification est celle d'un **inventaire et de l'unicité**, pas un audit sémantique complet.
- Les fichiers historiques V3.4, les sources de code et `AGENTS.md` n'ont pas été modifiés.

## 2. Sommaire vérifiable lot par lot

| Lot | Scénarios | Intervalle | Fichier historique + SHA blob | Inventaire V3.5 |
|---|---:|---|---|---|
| 02 | 14 | `T-V34-02-01`…`T-V34-02-14` | [02_VISION_PARCOURS.md](../roadmap-v3.4/02_VISION_PARCOURS.md) `9a4297168d95c5f09b8529236865e8f83184fb38` | [SCENARIOS_V34_02_08.md](SCENARIOS_V34_02_08.md) |
| 03 | 16 | `T-V34-03-01`…`T-V34-03-16` | [03_ARCHITECTURE_ADR.md](../roadmap-v3.4/03_ARCHITECTURE_ADR.md) `7a0b0c00f21c02895174d8bd99517ba5a3769482` | [SCENARIOS_V34_02_08.md](SCENARIOS_V34_02_08.md) |
| 04 | 22 | `T-V34-04-01`…`T-V34-04-22` | [04_MIGRATION_AUTONOME.md](../roadmap-v3.4/04_MIGRATION_AUTONOME.md) `272fb820b12a56285152cb3d2bd80c2d6dec9278` | [SCENARIOS_V34_02_08.md](SCENARIOS_V34_02_08.md) |
| 05 | 20 | `T-V34-05-01`…`T-V34-05-20` | [05_PROJECT_SCHEMA.md](../roadmap-v3.4/05_PROJECT_SCHEMA.md) `598a0ba0ec17d2e6035ff8875d3a5ba49a2f702c` | [SCENARIOS_V34_02_08.md](SCENARIOS_V34_02_08.md) |
| 06 | 30 | `T-V34-06-01`…`T-V34-06-30` | [06_COMMAND_BUS.md](../roadmap-v3.4/06_COMMAND_BUS.md) `074879c0729042a77e8addc60b8c9446c176c183` | [SCENARIOS_V34_02_08.md](SCENARIOS_V34_02_08.md) |
| 07 | 28 | `T-V34-07-01`…`T-V34-07-28` | [07_UX_EXPRESS_NAVIGATION.md](../roadmap-v3.4/07_UX_EXPRESS_NAVIGATION.md) `0846d31a7bd3b0c719423ee585e2ab8721dcbb76` | [SCENARIOS_V34_02_08.md](SCENARIOS_V34_02_08.md) |
| 08 | 30 | `T-V34-08-01`…`T-V34-08-30` | [08_ASSISTANT_CONTEXTUEL.md](../roadmap-v3.4/08_ASSISTANT_CONTEXTUEL.md) `e638a1b008aa1206b01eb4f3ef5d7ad2957c351a` | [SCENARIOS_V34_02_08.md](SCENARIOS_V34_02_08.md) |
| 09 | 30 | `T-V34-09-01`…`T-V34-09-30` | [09_PLANIFICATEUR_SECURISÉ.md](../roadmap-v3.4/09_PLANIFICATEUR_SECURISÉ.md) `52e61d658d47570edffb662fc4f8983cf1208512` | [SCENARIOS_V34_09_16.md](SCENARIOS_V34_09_16.md) |
| 10 | 30 | `T-V34-10-01`…`T-V34-10-30` | [10_ANALYSE_VISUELLE.md](../roadmap-v3.4/10_ANALYSE_VISUELLE.md) `9c0b0648a6b3c2790813ff59136fdb0a88df89c0` | [SCENARIOS_V34_09_16.md](SCENARIOS_V34_09_16.md) |
| 11 | 30 | `T-V34-11-01`…`T-V34-11-30` | [11_MODELES_IA_LOCAUX.md](../roadmap-v3.4/11_MODELES_IA_LOCAUX.md) `9a169e3c7db786d6dca1123397b13fcadde6a80e` | [SCENARIOS_V34_09_16.md](SCENARIOS_V34_09_16.md) |
| 12 | 30 | `T-V34-12-01`…`T-V34-12-30` | [12_RASTER_PIPELINE.md](../roadmap-v3.4/12_RASTER_PIPELINE.md) `30424177571a1e5c627cbdb0630c07c63ba344e0` | [SCENARIOS_V34_09_16.md](SCENARIOS_V34_09_16.md) |
| 13 | 30 | `T-V34-13-01`…`T-V34-13-30` | [13_VECTORISATION_SVG.md](../roadmap-v3.4/13_VECTORISATION_SVG.md) `f694c0016e896917084f1d70a642f67316d1cf70` | [SCENARIOS_V34_09_16.md](SCENARIOS_V34_09_16.md) |
| 14 | 30 | `T-V34-14-01`…`T-V34-14-30` | [14_LANGAGE_FABRICATION.md](../roadmap-v3.4/14_LANGAGE_FABRICATION.md) `3b7dd601c6f844f3a3d12b44bc971fc101133367` | [SCENARIOS_V34_09_16.md](SCENARIOS_V34_09_16.md) |
| 15 | 18 | `T-V34-15-01`…`T-V34-15-18` | [15_PROFILS_EXPLORE5.md](../roadmap-v3.4/15_PROFILS_EXPLORE5.md) `19cf7835044936e5cf2a2f894b5a42456c8fa8b4` | [SCENARIOS_V34_09_16.md](SCENARIOS_V34_09_16.md) |
| 16 | 10 | `T-V34-16-01`…`T-V34-16-10` | [16_PATRONS_PARAMETRIQUES.md](../roadmap-v3.4/16_PATRONS_PARAMETRIQUES.md) `562af8bc7ceca562381e08251352dfd5bd6c2b69` | [SCENARIOS_V34_09_16.md](SCENARIOS_V34_09_16.md) |
| 17 | 13 | `T-V34-17-01`…`T-V34-17-13` | [17_EXPORTS_DESIGNSPACE.md](../roadmap-v3.4/17_EXPORTS_DESIGNSPACE.md) `4c13bfe529f672d68a0c66a77c07fcd0068d5170` | [SCENARIOS_V34_17_22.md](SCENARIOS_V34_17_22.md) |
| 18 | 10 | `T-V34-18-01`…`T-V34-18-10` | [18_ATELIER_GRAPHIQUE.md](../roadmap-v3.4/18_ATELIER_GRAPHIQUE.md) `466fd3652524fe71ca9893e2c2e109376b4c6f48` | [SCENARIOS_V34_17_22.md](SCENARIOS_V34_17_22.md) |
| 19 | 12 | `T-V34-19-01`…`T-V34-19-12` | [19_PLANCHES_NESTING.md](../roadmap-v3.4/19_PLANCHES_NESTING.md) `e6ac52be45c79999a2ed043c44ed0c972fa8f007` | [SCENARIOS_V34_17_22.md](SCENARIOS_V34_17_22.md) |
| 20 | 10 | `T-V34-20-01`…`T-V34-20-10` | [20_BIBLIOTHEQUE_VARIANTES_CSV.md](../roadmap-v3.4/20_BIBLIOTHEQUE_VARIANTES_CSV.md) `b58e891ce65edcfa5ccabe46c24968036781e92a` | [SCENARIOS_V34_17_22.md](SCENARIOS_V34_17_22.md) |
| 21 | 10 | `T-V34-21-01`…`T-V34-21-10` | [21_WINDOWS_OFFLINE_RECOVERY.md](../roadmap-v3.4/21_WINDOWS_OFFLINE_RECOVERY.md) `8700846208315f405b7f60266fabf8181e160ff4` | [SCENARIOS_V34_17_22.md](SCENARIOS_V34_17_22.md) |
| 22 | 14 | `T-V34-22-01`…`T-V34-22-14` | [22_VALIDATION_CORPUS_PREUVES.md](../roadmap-v3.4/22_VALIDATION_CORPUS_PREUVES.md) `6fa98816ae2a8048471f6625d3c099df171fb0fb` | [SCENARIOS_V34_17_22.md](SCENARIOS_V34_17_22.md) |
| **TOTAL** | **437** | **437 identifiants uniques** | **21 sources historiques** | **3 inventaires complets** |

## 3. Livrables sources conservés

- [Scénarios 02–08 : 160 entrées](SCENARIOS_V34_02_08.md)
- [Scénarios 09–16 : 208 entrées](SCENARIOS_V34_09_16.md)
- [Scénarios 17–22 : 69 entrées](SCENARIOS_V34_17_22.md)
- [Contrat de contrôle des 25 obligations](AUTOMATION_QUALITY_CONTRACT.md)
- [Méthode de couverture V35-COV-01](COVERAGE_PROTOCOL_V35_COV_01.md)
- [Registre des 24 lots, 141 exigences, 140 tickets et 80 fonctions UX](INHERITANCE_REGISTER.md)

## 4. Qualité de l'inventaire vs travail restant

**FAIT à ce stade :** identifier les 437 lignes originales et les conserver dans V3.5 sans les mélanger à des preuves d'exécution. Les 21 groupes sont consécutifs et sans doublon.

**NON FAIT :**
1. Établir pour CHAQUE scénario la correspondance vérifiée `ID → critères complets V3.3/V3.4 → tickets V34/V35 → test/fonction réel → preuve` ; un renvoi générique au lot 22 n'est pas un contrôle fin.
2. Auditer le sens exact des assertions, les limites Explore 5, les dépendances, la frontière simulateur/Windows/Design Space/physique et les éventuelles contradictions ; corriger par delta V3.5 sans modifier l'historique.
3. Écrire et exécuter les tests produits correspondant aux critères retenus ; cela relève de la tâche de développement, non de la tâche de conception.
4. Évaluer de nouveaux scénarios de V3.5 pour les nouvelles fonctionnalités sans les inclure artificiellement dans les 437 scénarios hérités.

## 5. Prochaine opération de contrôle

Générer la **matrice de rattachement sémantique** `T-V34-LL-NN → V34-xxx / S-xxx / R33-xxx / parcours / preuves` en partant des renvois explicites des sources. Chaque lien doit être justifiable (texte source, section, consommateur, statut), jamais inféré uniquement du numéro de lot. Les liens non démontrés restent `À RAPPROCHER` ; aucune exigence historique ne disparaît du registre initial.

Une fois les 437 cas rapprochés des tickets/critères, passer à la conception des nouvelles capacités V3.5 (Smart Delivery, Smart Cut Advisor, Print Then Cut, Weeding, UX avancée, etc.) selon [#142](https://github.com/frenndak/SmartSVG-Studio/issues/142). Le développement V3.4 continue indépendamment.
