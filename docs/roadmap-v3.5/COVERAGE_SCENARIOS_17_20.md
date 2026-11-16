# COV-08 — Scénarios et tickets des lots 17–20

13/11/2026. CANDIDAT, documentaire, non normatif. Sources lues sur main : lots 17–20, blobs identiques aux sources indexées (17: 4c13bfe529f672d68a0c66a77c07fcd0068d5170 ; 18: 466fd3652524fe71ca9893e2c2e109376b4c6f48 ; 19: e6ac52be45c79999a2ed043c44ed0c972fa8f007 ; 20: b58e891ce65edcfa5ccabe46c24968036781e92a). Descriptions intégrales préservées dans SCENARIOS_V34_17_22.md. Ces liens sont les mappings locaux explicitement documentés, pas des preuves de tests.

| Scénario | Tickets cités | Qualification |
|---|---|---|
| T-V34-17-01 | V34-129 | PLANIFICATION_EXPLICITE |
| T-V34-17-02 | V34-129, V34-130 | PLANIFICATION_EXPLICITE |
| T-V34-17-03 | V34-129 | PLANIFICATION_EXPLICITE |
| T-V34-17-04 | V34-129 | PLANIFICATION_EXPLICITE |
| T-V34-17-05 | V34-129 | PLANIFICATION_EXPLICITE |
| T-V34-17-06 | V34-130 | PLANIFICATION_EXPLICITE |
| T-V34-17-07 | V34-131 | PLANIFICATION_EXPLICITE |
| T-V34-17-08 | V34-131 | PLANIFICATION_EXPLICITE |
| T-V34-17-09 | V34-130 | PLANIFICATION_EXPLICITE |
| T-V34-17-10 | V34-130 | PLANIFICATION_EXPLICITE |
| T-V34-17-11 | V34-129, V34-130, V34-131 | PLANIFICATION_EXPLICITE |
| T-V34-17-12 | V34-130 | PLANIFICATION_EXPLICITE |
| T-V34-17-13 | V34-131 | PLANIFICATION_EXPLICITE |
| T-V34-18-01 | V34-041, V34-132 | PLANIFICATION_EXPLICITE |
| T-V34-18-02 | V34-132 | PLANIFICATION_EXPLICITE |
| T-V34-18-03 | V34-132 | PLANIFICATION_EXPLICITE |
| T-V34-18-04 | V34-132 | PLANIFICATION_EXPLICITE |
| T-V34-18-05 | V34-041, V34-132 | PLANIFICATION_EXPLICITE |
| T-V34-18-06 | V34-035, V34-038 | PLANIFICATION_EXPLICITE |
| T-V34-18-07 | V34-133 | PLANIFICATION_EXPLICITE |
| T-V34-18-08 | V34-133 | PLANIFICATION_EXPLICITE |
| T-V34-18-09 | V34-045, V34-133 | PLANIFICATION_EXPLICITE |
| T-V34-18-10 | V34-044, V34-132 | PLANIFICATION_EXPLICITE |
| T-V34-19-01 | V34-134 | PLANIFICATION_EXPLICITE |
| T-V34-19-02 | V34-134 | PLANIFICATION_EXPLICITE |
| T-V34-19-03 | V34-135 | PLANIFICATION_EXPLICITE |
| T-V34-19-04 | V34-134 | PLANIFICATION_EXPLICITE |
| T-V34-19-05 | V34-134 | PLANIFICATION_EXPLICITE |
| T-V34-19-06 | V34-134 | PLANIFICATION_EXPLICITE |
| T-V34-19-07 | V34-134 | PLANIFICATION_EXPLICITE |
| T-V34-19-08 | V34-135 | PLANIFICATION_EXPLICITE |
| T-V34-19-09 | V34-135 | PLANIFICATION_EXPLICITE |
| T-V34-19-10 | V34-135 | PLANIFICATION_EXPLICITE |
| T-V34-19-11 | V34-135 | PLANIFICATION_EXPLICITE |
| T-V34-19-12 | V34-135 | PLANIFICATION_EXPLICITE |
| T-V34-20-01 | V34-136 | PLANIFICATION_EXPLICITE |
| T-V34-20-02 | V34-136 | PLANIFICATION_EXPLICITE |
| T-V34-20-03 | V34-136 | PLANIFICATION_EXPLICITE |
| T-V34-20-04 | V34-137 | PLANIFICATION_EXPLICITE |
| T-V34-20-05 | V34-137 | PLANIFICATION_EXPLICITE |
| T-V34-20-06 | V34-137 | PLANIFICATION_EXPLICITE |
| T-V34-20-07 | V34-138 | PLANIFICATION_EXPLICITE |
| T-V34-20-08 | V34-138 | PLANIFICATION_EXPLICITE |
| T-V34-20-09 | V34-138 | PLANIFICATION_EXPLICITE |
| T-V34-20-10 | V34-138 | PLANIFICATION_EXPLICITE |

## Contre-expertise

**45/45** scénarios possèdent un lien de planification explicite dans les mappings des lots (13+10+12+10). Zéro exception textuelle. Cela ne prouve ni propriété métier exclusive, ni DoD sémantiquement complet, ni test exécuté. Les références source 17 T01..13, 18 T01..10, 19 T01..12, 20 T01..10 sont maintenues sans renumérotation.

- Lot 17 : GARDER et AMÉLIORER les quatre sorties distinctes : PNG Print Then Cut, SVG Basic Cut, SVG CUT multicouche, SVG d'édition. Multicouche reste externe et ne devient pas une nouvelle valeur Artifact.use V1. Smart Delivery est un raffinement de la publication, pas un second exporteur. Refus de confondre SVG éditable et CUT.
- Lot 18 : GARDER la sélection par subject_id, les masques float32 A/B, le preview non mutant et Undo de brouillon distinct d'Undo durable sous CAS. Refus de déduire l'identité de l'ordre des vignettes ou de créer un second store.
- Lot 19 : AMÉLIORER le job borné 12/24/50 et le cache dérivé SHA, avec reprise après 17/50 et zéro doublon. Refus de stocker 50 masques actifs dans le V1 ou de dupliquer la queue.
- Lot 20 : GARDER le catalogue reconstructible, clone à nouveau project_id, CSV littéral sans exécution, IDs par ligne. Métadonnées portables seulement après round-trip writer qualifié. Refus de reconstruire le projet depuis une miniature.

Risques non résolus : T-V34-17-11..13 demandent essais Design Space/physiques ; T-V34-18-03..06 exigent préservation masque, Undo et concurrence ; T-V34-19-09..11 exigent panne, mémoire et reprise ; T-V34-20-03/05/08/09 exigent symlink hostile, conflit de clone, CSV hostile et reprise. Aucune de ces validations n'a été exécutée ici.

## Audit des 25 contrôles

01–06 : 45 IDs et références textuelles contrôlés ; 24 lots, 141 exigences, 140 tickets, 80 UX, 437 scénarios restent inventoriés historiquement, sans certification intégrale. HEAD main exact NON_VÉRIFIÉ.
07–09 : projet V1/SHA/CAS/float32, quatre exports et opérations CUT/SCORE préservés, non testés.
10–12 : UX, focus, clavier, 1366×768/DPI 200 % préservés comme exigences ; N/A pour qualification documentaire, tests Windows NOT_RUN.
13 : crash, concurrence, annulation et rollback conservés ; tests NOT_RUN.
14–16 : IA/raster/vecteur non modifiés ; N/A pour cette extraction textuelle, aucune certification technique.
17 : planches, bibliothèque et CSV couverts par 22 scénarios ; E2E NOT_RUN.
18–19 : Smart Delivery et propositions #141 raccordés comme raffinements ; arbitrage exhaustif des opportunités encore ouvert.
20–21 : performances à mesurer, confidentialité/licences conservées, aucun média privé introduit.
22–25 : branche candidate seulement, aucun code, merge, AGENTS ni tâche modifiés ; contrôle anti-doublon effectué ; aucune promotion ; audit limité à COV-08.

Statuts produit : TEST_UNITÉ_PASS_NON_SKIP, TEST_UI_WINDOWS_PASS, GPU_PASS, DESIGN_SPACE_PASS, COUPE_PHYSIQUE_PASS = NOT_RUN. Dix exigences G6/G9 sans ticket direct, T-V34-03-16 et cinq arbitrages 05–08 toujours ouverts.

**Prochaine action unique : COV-09, scénarios lots 21–22 (24 IDs), puis revue sémantique des exceptions.**
