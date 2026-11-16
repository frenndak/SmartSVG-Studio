# GLOBAL_REVIEW — revue contradictoire de promotion documentaire (15/11/2026)

**Périmètre :** revue de conception V3.5 seulement. V3.4 demeure active. Base de lecture : RUN_STATE (GLOBAL_REVIEW READY), PROMOTION_CHECKLIST, AUTOMATION_QUALITY_CONTRACT, PROGRESS, REVIEW_SOURCE_TRANSFER et acceptation SOURCE_CLOSURE. Main : AGENTS.md consulté, référence V3.4 confirmée ; SHA de HEAD main et HEAD candidate à authentifier avant verdict définitif. Aucun test produit exécuté dans cette revue.

## Décision indépendante et portée

**Verdict provisoire : REVIEW_PENDING / NO-GO promotion.** SOURCE_CLOSURE est acceptée au niveau documentaire par ses revues cumulées, mais son acceptation ne transfère aucune autorité. Les 24 lots, 141 critères, 140 DoD, 80 capacités et 437 assertions sont inventoriés selon les rapports sources ; les validations exhaustives par outils au HEAD exact n'ont pas été réexécutées ici. Ne pas convertir ces compteurs en PASS de code, Windows, GPU, Design Space ou découpe physique.

## Gates G35 (décision de cette passe)

| Gate | Appréciation | Vérification encore exigée |
|---|---|---|
| 01–03 héritage | DOCUMENTED, revue de sources cumulée | vérifier au SHA gelé le graphe 24/141/140 et les DoD complets |
| 04 UX80 | DOCUMENTED, REVIEW_DE rapporté DONE | vérifier les 80 décisions individuelles et les cinq parcours |
| 05 scénarios437 | DOCUMENTED, SOURCE_CLOSURE rapporté DONE | confirmer 437 assertions, six exceptions et absence de PASS inventé |
| 06 G6/G9 | CANDIDATE_OWNER_ACCEPTED | dix exigences, six exceptions, W16 OCR/CP6, tests futurs préservés |
| 07 opportunités | DOCUMENTED | 33 décisions, huit rejets, 15 groupes et #141 sans doublon |
| 08 architecture | REVIEW_PENDING | V1/CAS/float32, V2 explicite, receipts séparés, quatre sorties distinctes |
| 09 UX/a11y | REVIEW_PENDING | clavier/focus/DPI200 %, 1366×768, Undo/recovery, E2E novice/expert |
| 10 qualité | REVIEW_PENDING | oracles positifs, ≥3 négatifs, crash/concurrence, matrice PASS/FAIL/SKIP/NOT_RUN |
| 11 adversarial | REVIEW_PENDING | revue indépendante transversale au HEAD exact et contradictions arbitrées |
| 12 PR docs | PENDING | WIP PR réévalué, diff limité docs, CI exact-head et revue |
| 13 gouvernance | PENDING | PR séparée AGENTS après fusion documentaire autorisée |
| 14 passation | PENDING | producteur existant seulement après autorité V3.5 sur main |
| 15 source/sécurité | REVIEW_PENDING | diff archives/AGENTS/code/workflows nul, licences, secrets, médias |

## Contrôle des 25 axes — couverture de revue, pas certification

01–05 : inventaires hérités à revalider par scripts au SHA ; 06 : statuts indépendants ; 07–09 : invariants V1, quatre exports, tri-state machines ; 10–13 : UX, clavier/DPI, Undo, crash et concurrence ; 14–17 : IA opt-in, raster/ICC, vecteur/topologie, batch/Fabrique ; 18–19 : Smart Delivery et opportunités ; 20 : mesures non inventées ; 21 : sécurité et licences ; 22 : branche/WIP/autorité ; 23 : anti-doublons ; 24 : promotion séparée ; 25 : aucune suppression de contrôle par compression. **Tous les axes sont applicables à la revue globale**, mais leur mention ne vaut pas vérification complète : ceux qui requièrent relecture exhaustive/CI restent REVIEW_PENDING. Aucun N/A arbitraire.

## Contre-expertise hostile : cinq risques à empêcher

1. Un index exact peut cacher un critère parent amputé : comparer texte source, clause parente, DoD et consommateur, pas seulement IDs.
2. CAS du projet V1 ne prouve pas l'atomicité du ZIP ou des receipts CP2/V2 ; séparer installation modèle, publication export et mutation projet.
3. Un SVG éditable n'est ni SVG CUT multicouche ni Basic Cut ; PNG PTC ne constitue pas une certification machine.
4. Une recette future Design Space/Explore 5 ne peut être marquée PASS par un test unitaire ou par une maquette UI.
5. Un commit de branche candidate n'autorise ni auto-merge docs, ni transfert d'opt-in V3.4, ni modification du producteur.

## Conditions d'un verdict favorable

Geler HEAD candidat et HEAD main ; exécuter les contrôleurs de priorité, curseur et transfert source sur un checkout cohérent ; relever les résultats réels et les 25 axes avec preuves ; comparer archives et fichiers protégés ; confronter les ports et PR code au HEAD ; obtenir contre-revue indépendante du présent verdict et corriger ses constats. **Ne pas promouvoir** si une contradiction majeure ou un contrôle documentaire non exécuté demeure. Une fois G35-01..11 et15 validés, préparer la PR docs sans la fusionner ; G35-12..14 suivent séparément.

**Prochaine action unique :** GLOBAL_REVIEW-EVIDENCE — geler les deux HEAD, exécuter les vérificateurs documentaires et consigner leurs résultats exacts, puis rendre le verdict G35-01..11/15.
