# V35-COV-01 — Protocole de couverture sans perte et qualification des preuves

**Statut : SPÉCIFIÉ, NON NORMATIF, NON EXÉCUTÉ.** Référence observée : main@`aa0ff9e7d0c53dba3fdc429c02c6198736cfe935` ; dernier commit main examiné : `engine/native_image_viewport_v34.py`, `tests/test_v34_native_image_viewport.py`. Source : issue #142, #134, #141 ; AGENTS.md et politique V3.4 priment. Cette fiche définit une méthode de contrôle ; elle **ne prouve pas** encore la couverture sémantique.

## Décision et valeur

**V35-COV-01, P0 — GARDER / AMÉLIORER** le registre d'héritage, sans réécrire les 24 lots ni générer 437 nouveaux tests. JTBD novice : « Quand une fonctionnalité m'est promise, je veux savoir si je peux réellement l'utiliser sous Windows. » JTBD expert : « Quand un ticket est déclaré terminé, je veux remonter aux critères, à l'artefact, au test et à la preuve matérielle éventuelle. » Contre-avis : un tableau de bord autonome ferait doublon avec le backlog ; **refus** d'un second store et d'un nouveau statut global « terminé ». Le premier livrable est une matrice documentaire contrôlable, pas une interface supplémentaire.

## Inventaire attendu et invariants

| Famille | Univers canonique attendu | Contrôle obligatoire | État actuel de qualification |
|---|---|---|---|
| Lots | 01..24, 24 uniques | chemin + SHA source + décision V35 individuelle | À rapprocher |
| Exigences | S-001..S-101 et R33-001..R33-040, 141 uniques | texte et DoD historiques, liens V34/V35 sans perte | À rapprocher |
| Tickets | V34-001..V34-140, 140 uniques | propriétaire/lot, dépendances, DoD et preuve distincte | À rapprocher |
| UX | A01..A16, B01..B14, C01..C18, D01..D12, E01..E20, 80 uniques | description originale #134, décision et localisation V35 | À rapprocher ; 80 audités historiquement, 0 certifié codable historiquement |
| Recettes | 437 scénarios documentés | extraire l'identifiant **réel** ou la clé source stable (fichier SHA + section + ordinal), conserver le texte, joindre exigences/tickets et preuve | **0/437 individuellement qualifiés dans cette fiche** |
| Opportunités | O-001..O-033 et #141 | décision, contre-avis, doublons, liens consommateurs | À rapprocher |

Le dénombrement est une **assertion à vérifier**, pas un résultat. Tout doublon, trou de séquence, source manquante, critère altéré ou lien sans cible est `COVERAGE_BLOCKED`, jamais « PASS ». Une exigence peut alimenter plusieurs tickets, et un ticket plusieurs recettes : exiger une relation explicite, **pas** une bijection artificielle entre univers différents. Contrôler l'unicité *à l'intérieur* de chaque univers et les liens bidirectionnels vérifiables.

## Schéma documentaire proposé (aucune API existante affirmée)

Une ligne canonique par ID : `{source_family,source_id,source_path,source_blob_sha,source_anchor,original_criterion,decision_v35,target_section,ticket_ids,recipe_keys,proof_refs,review_state}`. `original_criterion` est une référence au texte immuable, jamais une paraphrase substitutive. Une recette sans ID source reçoit une clé documentaire déterministe `source_blob_sha:heading:ordinal` ; une modification du blob déclenche réconciliation, jamais réutilisation silencieuse. `proof_refs` est un ensemble typé `{axis,commit_sha,workflow_or_manual_log,result,date,environment}`, où `axis` est CODE_MAIN, CODE_BRANCHE, WINDOWS_UI, UNIT_NON_SKIP, GPU, DESIGN_SPACE, PHYSICAL_CUT ou DOCUMENTARY. `result` = PASS/FAIL/SKIP/NOT_RUN/UNKNOWN ; UNKNOWN et SKIP ne deviennent pas PASS.

La source de vérité reste les fichiers V3.3/V3.4 et GitHub. Le tableau V3.5 est une **vue de traçabilité**, non un writer projet, un moteur d'export ou un registre de certification. Le .smartsvg V1, SHA/CAS, Subject et masques float32 sont intangibles ; les quatre contrats PNG Print Then Cut / SVG Basic Cut / SVG CUT multicouche / SVG éditable restent séparés. Une ligne de traçabilité ne modifie ni projet ni artefact.

## Parcours utilisateur et états

**Novice :** dans le suivi produit, recherche « exporter sticker » → voit le contrat PNG PTC, son état Windows réel et « non vérifié dans Design Space » → consulte la recette et le blocage → revient au projet sans modifier ses données. **Expert :** filtre les tickets par `CODE_MAIN` sans `WINDOWS_UI`, ouvre le commit, vérifie le test exact-SHA, signale une preuve périmée, puis requalifie la ligne. Ce suivi peut d'abord être une page Markdown accessible ; aucun canevas ni poignées ne sont requis. États : NON INDEXÉ → INDEXÉ → LIÉ → REVU ; preuve absente = NON VÉRIFIÉ, lien cassé = ERREUR ; retour arrière = restauration de la révision documentaire par Git, jamais modification de l'historique source. Libellés lisibles, liens clavier, focus visible, pas de couleur seule ; tester affichage à 1366×768 et DPI 200 % avant toute future UI.

## Recettes de qualification PROPOSÉES, non exécutées

**Positif :** fixtures documentaires synthétiques avec 2 exigences, 2 tickets, 3 recettes et relations multiples ; importer deux fois → mêmes clés, mêmes liens, aucune duplication ; contrôler les deux sens des relations. **N1 :** ID répété avec critère différent → erreur bloquante. **N2 :** recette orpheline ou ancre déplacée → rapport de trou et aucun 437/437. **N3 :** preuve de test PASS sur ancien SHA ou SKIP → statut NON VÉRIFIÉ pour le HEAD actuel. **N4 :** deux contrats SVG CUT et SVG éditable confondus → violation bloquante. **N5 :** source historique modifiée → alerte, ne pas normaliser silencieusement. **Crash/annulation :** préparation en brouillon sur branche, aucun changement de sources ; publication atomique Git par commit distinct ; un conflit de branche impose relecture et nouvelle revue, sans force-push. Tests Windows UI / GPU / Design Space / coupe physique : **NOT_RUN**, non applicables à la validation *du seul registre documentaire*, mais restent obligatoires pour certifier leurs fonctionnalités consommatrices.

**Mesures futures :** temps de retrouver une exigence et son test, proportion de liens cassés, erreurs de classement et temps de correction, mesurés sur tâches réelles novice/expert ; aucun résultat observé ici.

## Micro-lots TDD et DoD

1. Extraire les 24 lots et leurs SHA, puis 141 exigences/critères complets ; contrôler unicité et stabilité.
2. Extraire les 140 tickets et leurs DoD, lier à chaque exigence pertinente ; conserver les exigences sans ticket comme lacunes explicites.
3. Inventorier **chaque** scénario parmi les 437 dans son fichier source, dédupliquer seulement sur identité vérifiée, préserver chaque recette même si redondante.
4. Confronter les 80 descriptions #134 et les 33 opportunités, établir décisions et contre-avis, raccorder #141.
5. Produire `COVERAGE_V34_TO_V35.md` avec références sources exactes, puis contre-relecture indépendante des 25 contrôles.
6. Ajouter preuves exact-SHA au fur et à mesure des tests réels, sans convertir documentation en qualification.

**DoD documentaire :** 24/24, 141/141, 140/140, 80/80 et 437/437 **effectivement réconciliés**, aucun lien orphelin non signalé, aucune perte de DoD, revue hostile et contrôle 25/25. **DoD produit :** indépendant et non satisfait par cette fiche. Aucun code, PR, merge, nouvelle dépendance, changement de gouvernance ou tâche n'est autorisé par ce document.

## Contrat de qualité R3 — 25 axes

01–05 : inventaires explicitement ouverts ; 06 : états disjoints ; 07–09 : invariants projet/exports/opérations maintenus ; 10–12 : UX de lecture et accessibilité, canevas/poignées **N/A** pour matrice documentaire ; 13 : concurrence/rollback Git ; 14–17 : IA/raster/vecteur/Fabrique **N/A au moteur de matrice**, mais obligations conservées pour consommateurs ; 18–19 : Delivery et autres opportunités indexées, pas re-spécifiées ; 20 : métriques proposées non mesurées ; 21 : aucune donnée privée ; 22 : branche docs uniquement ; 23 : aucun store/engine nouveau ; 24 : adoption conditionnée à revue ; 25 : cette fiche résout la fausse bijection et l'identité des 437 recettes sans raccourcir les obligations.

**Prochaine fiche unique :** extraction vérifiable et réconciliation des 437 scénarios V3.4 (sources, clés stables, liens tickets/exigences), puis publication de la première tranche réelle de matrice.