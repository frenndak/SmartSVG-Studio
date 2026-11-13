# Journal de conception — SmartSVG V3.5

## 2026-11-12 — Initialisation contrôlée

- **Version** : V3.5 candidate, non normative ; V3.4 reste la référence des producteurs de code.
- **main de référence historique** : `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`.
- **Branche candidate** : `roadmap/v3-5-design-candidate-20261112`.
- **Issue canonique** : [#142](https://github.com/frenndak/SmartSVG-Studio/issues/142) ; sources #141 (enrichissements, Smart Delivery V1/V2) et #134 (80 UX).
- **Actions réalisées** : lecture de la politique AGENTS et de la promotion V3.4 ; inventaire extraction des tables : 24 lots, 141 exigences, 140 tickets, 80 UX, IDs uniques ; constitution de la nouvelle photographie sans toucher aux sources V3.4.
- **Tests produits** : AUCUN dans cette opération ; aucune certification Windows/GPU/Design Space/coupe physique.
- **Tests d'intégrité documentaire** : dénombrement/exclusivité des IDs V3.4/UX et des liens vers 24 lots contrôlés dans la session de préparation ; traçabilité exhaustive des 437 recettes **ouverte**.
- **Travaux V3.5 restant à faire** : matrice sémantique exigence par exigence, liens aux 437 scénarios, étude des 80 UX, micro-tickets V35 nouveaux, critères d'acceptation E2E, architecture UX, plans de test, ADR, revue et promotion.
- **Prochaine action à portée d'un cycle** : qualifier la méthode d'héritage et les vérifications automatisables, confronter V3.4 à #141 et #134 sans dupliquer le contenu. Reprendre les fiches Smart Delivery SD-V1/SD-V2 déjà publiées, puis SD0/SD1 et l'ensemble des autres fonctions selon les dépendances. Débuter la matrice `COVERAGE_V34_TO_V35.md` sans annoncer 100 % de spécifications rédigées.

**Règle de suivi :** une entrée de journal référence un changement/une preuve réelle. Pas de répétition de statut ni de relecture exhaustive sans cause ; jamais de pass mécanique pour cocher un ID.

## 2026-11-12 — Exécution manuelle immédiate, inventaire exhaustif des 437 scénarios

- **Déclenchement** : demande explicite propriétaire d'exécuter maintenant la tâche horaire V3.5 ; l'exécution a été acceptée sans création d'une tâche supplémentaire ni changement de calendrier. Travail documentaire poursuivi directement dans cette conversation.
- **Référence source** : `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`, 21 documents sources des lots 02 à 22. Les lots 01 et 23/24 ne contiennent pas de nouveaux tableaux T-V34 identifiés.
- **Livrables effectivement créés et commits** :
  - [SCENARIOS_V34_02_08.md](SCENARIOS_V34_02_08.md) : **160 IDs**, commit `a823f0eb0c8311cd57f438ebf1c243937595aa7a`.
  - [SCENARIOS_V34_09_16.md](SCENARIOS_V34_09_16.md) : **208 IDs**, commit `fbd4b1e6c2ab63a6829432279ae4ef71d6c0c1cf`.
  - [SCENARIOS_V34_17_22.md](SCENARIOS_V34_17_22.md) : **69 IDs**, commit `6b2ed78f483ddab8997ba0dbca5f6116cfb7851f`.
  - [SCENARIOS_V34_INDEX.md](SCENARIOS_V34_INDEX.md) : inventaire central 21 lots, commit `fc492941174150fbd560592312dbc69a920c3a61` ; README lié en commit `f637b85c11d938ae2b5d388b1266c7889aea7788`.
- **Contrôles exécutés à l'écriture et relecture** : source IDs de chaque lot vérifiés avec décompte attendu et séquence 01..NN ; relecture des trois documents publiés → **160+208+69 = 437 IDs distincts**, 21 lots représentés, aucun doublon ni trou. SHA du fichier historique et numéro de ligne d'origine conservés ; texte complet de chaque ligne source copié, sans supprimer ses axes de test.
- **État de couverture HONNÊTE** : `INVENTAIRE_ID_ET_TEXTE = 437/437` ; `RATTACHEMENT_SÉMANTIQUE_AUX_EXIGENCES_ET_TICKETS = OUVERT` ; `TESTS PRODUITS EXÉCUTÉS PAR CE PASSAGE = 0`. Les 141 exigences, 140 tickets, 24 lots et 80 UX restent conservés par le registre initial, mais leurs critères détaillés ne sont pas tous requalifiés dans V3.5.
- **Gouvernance** : branche candidate uniquement ; aucune PR documentaire, aucun merge, aucune modification de code, roadmap active V3.4, tâche de développement ou règle AGENTS. Les 25 contrôles anti-perte restent applicables.
- **Prochaine micro-action PRÉCISE** : commencer `COVERAGE_V34_TO_V35.md` en reliant les 437 scénarios à leurs exigences et tickets, **sur preuves sources explicites**, en traitant d'abord les lots 02–04 et les références du lot 23 ; marquer `À RAPPROCHER` chaque relation qui serait inférée du seul numéro de lot. Ne pas recommencer l'inventaire ni annoncer prématurément une conformité V3.5 intégrale.

## 2026-11-12 — Contre-expertise COV-03 / COV-04 : défauts de couverture et première qualification explicite des scénarios

**Motivation :** demande propriétaire de vérification, contre-expertise, corrections, recherche d'erreurs et optimisation des travaux V3.5. Périmètre documentaire seulement ; V3.4 ACTIVE. Sources historiques inspectées sous `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`, V3.3 norme intégrale et lots V3.4 02/03/04/23.

### Constats et corrections concrètes
- [COVERAGE_V34_TO_V35.md](COVERAGE_V34_TO_V35.md) : **141 exigences**, **140 tickets**, **314 liens réciproques**, **0 arête unilatérale**, mais **10 exigences V3.3 sans ticket V34 explicite**, héritées G6/G9 (polices/licences/glyphes, OCR, gabarits métiers, dioramas multi-plans). Commit `5a7d53eb5acc216332cfd85c4cb8ebf3ce7dce62`.
- [COVERAGE_SCENARIOS_02_04.md](COVERAGE_SCENARIOS_02_04.md) : extraction des **19 micro-fiches** et des **52 scénarios des lots 02–04** ; **51/52** ont au moins un ticket source explicite, **1 scénario sans propriétaire direct : T-V34-03-16** (certification de coupe physique). Propriété à arbitrer sans falsifier le lot historique (V34-012/V34-003 candidats). Commit `56587e252a42aa53dc758c97d71d54f78368c47b`.
- [README.md](README.md) : correction de la mention historique des **437 scénarios déjà inventoriés**, lien vers la nouvelle matrice et visibilité explicite des fonctions héritées **texte/typographie/OCR** et **dioramas quatre plans**, sans les déguiser en nouveautés optionnelles. Commit `8d21201af942e50d7282f8f99374fcd1f583bf65`.
- Recettes testées : **aucune**. La vérification réalisée est un contrôle de documents/IDs et de références textuelles ; les tests Windows/RTX/Design Space/physiques restent axes distincts. Le fait de lier 51 scénarios à des tickets ne qualifie pas leurs 51 critères techniques.

### Prochain passage horaire à privilégier
1. Lire COV-03 et COV-04 avant de commencer ; **ne pas refaire** les 437 inventaires ni les 314 liens réciproques.
2. Confronter les exigences G6/G9 complètes aux critères et aux tickets V3.5 ; produire un vrai dossier de rattrapage de 10 obligations sans renuméroter arbitrairement les 140 tickets V34.
3. Continuer **COV-05** sur les lots 05–08 pour la relation explicite `scénario→ticket`, puis les autres lots en conservant le statut `NON_ATTRIBUÉ` lorsqu'il manque une ligne source.
4. Maintenir le développement Windows V3.4 inchangé, la confidentialité des sources et la promotion de gouvernance séparée.

**Conclusion de contre-expertise :** inventaire 24/141/140/80/437 conservé ; liens internes ticket↔exigence **314/314 réciproques**, **10 exigences héritées à raccorder**, scénario→ticket **51/52** sur le sous-ensemble 02–04. Aucun KPI « spécifié / implémenté / testé » gonflé.

## 2026-11-13 — COV-05, lots 05–08 : matrice explicite de planification

- **Livrable :** [COVERAGE_SCENARIOS_05_08.md](COVERAGE_SCENARIOS_05_08.md), commit `f4e005f9703e89e27368db967a3a0884686e223f` sur la branche documentaire uniquement.
- **Source :** quatre blobs historiques V3.4 inchangés (SHA dans le livrable). **108 scénarios** : 20/20 lot 05, 27/30 lot 06, 26/28 lot 07, 30/30 lot 08 avec référence ticket explicite, soit **103/108** ; cinq sans référence explicite : `T-V34-06-22`, `06-24`, `06-25`, `07-16`, `07-25` (préfixe `T-V34-`). Le rapprochement reste une extraction textuelle, à vérifier sémantiquement.
- **Statut :** documentation publiée, aucune PR/merge/code, aucun test exécuté ; couverture historique 24/141/140/80/437 inchangée. Les 10 exigences G6/G9 non rattachées restent ouvertes.
- **Prochaine action unique :** arbitrer les cinq cas sans propriétaire explicite, lire leurs critères source complets et corriger la matrice sans attribution fictive.

## 2026-11-13 — COV-05B : cinq exceptions qualifiées sans faux liens

- **Livrable réel :** [COVERAGE_SCENARIOS_05_08_ARBITRAGE.md](COVERAGE_SCENARIOS_05_08_ARBITRAGE.md), commit `d21e64d74fb2aff2573f6a706cd59a51230a125a` ; branche candidate uniquement.
- **Lecture :** blobs V3.4 lots 06/07 et COV-05 ; cinq scénarios `06-22`, `06-24`, `06-25`, `07-16`, `07-25` rapprochés **sémantiquement en propositions**, non comme liens source explicites. COV-05 reste **103/108 explicites** ; les cinq propositions nécessitent revue. Aucune nouvelle fonction/ticket inventé.
- **Preuves :** documentation uniquement ; 0 test produit, Windows, GPU, Design Space ou coupe physique exécuté. 24 lots / 141 exigences / 140 tickets / 80 UX / 437 scénarios inventoriés restent des comptes d'héritage, pas des certifications ; 10 exigences G6/G9 sans ticket explicite et `T-V34-03-16` ouverts. Les 25 contrôles restent applicables, pas tous certifiés par ce micro-lot.
- **HEAD main :** NON_VÉRIFIÉ de façon autoritative ; la recherche de commits renvoie `aa0ff9e7...` en premier, mais ne garantit pas la tête de branche. Sources 06/07 lues sur main avec blob SHA précis.
- **Prochaine action unique :** COV-06, rapprochement explicite des scénarios 09–12, avec liste des exceptions et contrôle des critères, sans recompiler les 437 scénarios.

## 2026-11-13 — COV-06 : scénarios 09–12, matrice des plages explicites

- **Livrable :** [COVERAGE_SCENARIOS_09_12.md](COVERAGE_SCENARIOS_09_12.md), commit `3ee735d13aab51dc757e5ed3882f5d6ca4ee974b` sur branche candidate ; quatre sources V3.4 lues sur `main` avec blobs identiques au snapshot d'inventaire.
- **Résultat :** 120/120 scénarios (30 par lot) possèdent au moins une référence explicite dans les plages de tests des tickets V34 ; 0 exception textuelle. Les tickets transversaux de corpus couvrant T01..30 ne suffisent **pas** à démontrer un propriétaire fonctionnel ou une spécification testée. Les liens détaillés sont listés un par un ; aucune réécriture des 437 textes sources.
- **Couverture :** 24/141/140/80/437 identifiants historiques conservés, non qualifiés intégralement ; 10 exigences G6/G9 sans ticket explicite, scénario 03-16 et cinq arbitrages 05–08 restent ouverts. COV-06 est une qualification de liens, pas une preuve de tests.
- **Exécution :** 0 test produit, Windows, GPU, Design Space ou coupe physique. Main HEAD exact NON_VÉRIFIÉ ; les blobs source sont vérifiés mais la recherche de commits ne garantit pas la tête de branche. Aucune PR, merge, modification de code/AGENTS ni tâche de développement.
- **Prochaine action unique :** COV-07, scénarios 13–16, établir les liens source explicites et exceptions ; ensuite revenir aux dossiers G6/G9 et à la revue sémantique.


## 2026-11-13 — COV-07 : premier index conservateur lots 13–16

- Livrable : [COVERAGE_SCENARIOS_13_16.md](COVERAGE_SCENARIOS_13_16.md), commit `1414473099a5c0f84f48cfc7e7e934455a3630ba` sur branche candidate seulement.
- Sources lues : lots V3.4 13–16 ; 88 scénarios au total (30+30+18+10). Première extraction **49/88** avec lien textuel reconnu ; **39 NON_ATTRIBUÉ** au sens strict de l'extracteur, et NON 39 absences prouvées de propriétaire. L'extracteur ne reconnaît pas toutes les variantes de plages (`T04..08/09`, `T01..03/15/22`) : ce chiffre est une borne inférieure, pas une couverture validée.
- Contre-expertise : le dossier reste **INACHEVÉ** et nécessite relecture humaine des plages abrégées, en particulier tickets V34-096..128. Ne pas passer à COV-08 avant correction des faux NON_ATTRIBUÉ et audit sémantique. Les 25 contrôles sont conservés comme contrat ; aucune validation exhaustive n'est revendiquée.
- 0 test produit exécuté ; aucune preuve Windows/GPU/Design Space/physique ; aucun code, merge, AGENTS ou tâche modifiés. Main HEAD NON_VÉRIFIÉ (recherche de commits non autoritative). Trois PR code ouvertes #138–140.
- **Prochaine action unique :** COV-07B, parser et contrôler manuellement les plages composées dans les micro-tickets 13–16, rectifier les 88 lignes et publier un arbitrage des exceptions réelles.

## 2026-11-13 — COV-07B : correction des 39 faux NON_ATTRIBUÉ

- Livrable [COVERAGE_SCENARIOS_13_16_CORRECTION.md](COVERAGE_SCENARIOS_13_16_CORRECTION.md), commit `57d1ed427777c2b2242b422691eff3f4fba4b762`. Relecture des plages sources lots 13–16 aux quatre blob SHA inchangés : **88/88 scénarios cités textuellement par au moins un ticket** contre borne inférieure 49/88 dans COV-07. Les plages composées expliquent les 39 faux négatifs ; COV-07 est conservé comme trace historique, non supprimé.
- Ce résultat ne certifie ni adéquation sémantique, ni DoD, ni test exécuté. 10 exigences G6/G9 sans ticket direct et `T-V34-03-16` toujours ouverts ; inventaire 24/141/140/80/437 conservé. 25 contrôles ventilés dans le livrable, aucun changement de code, PR, merge, AGENTS ou tâche. Tests produit et terrain NOT_RUN. Main HEAD NON_VÉRIFIÉ.
- **Prochaine action unique : COV-08, liens explicites scénarios 17–20.**

## 2026-11-13 — COV-08 : rapprochement des lots 17–20

- Livrable : [COVERAGE_SCENARIOS_17_20.md](COVERAGE_SCENARIOS_17_20.md), commit `b8ca24f2c62ad72eb579645be455baa71ccb6011` sur branche candidate.
- Quatre blobs sources V3.4 contrôlés et inchangés par rapport à l'inventaire : **45/45 scénarios** possèdent une référence explicite dans les mappings locaux (13+10+12+10), **0 exception textuelle**. Liens de planification, **pas** qualification sémantique ni tests PASS.
- Décisions : conserver quatre exports distincts et V1 strict, Undo de brouillon distinct du commit, jobs 12/24/50 sans deuxième queue, bibliothèque reconstructible et CSV littéral. Contre-expertise des risques, alternatives rejetées et 25 contrôles documentée.
- Couverture historique 24/141/140/80/437 inchangée ; 10 exigences G6/G9, T-V34-03-16 et cinq arbitrages 05–08 ouverts. Tests produit/Windows/GPU/Design Space/physique NOT_RUN ; main HEAD exact NON_VÉRIFIÉ. Aucun code, PR, merge, AGENTS ou tâche modifiés.
- **Prochaine action unique : COV-09**, rapprochement des 24 scénarios lots 21–22, puis revue sémantique.

## 2026-11-13 — COV-09 : lots 21–22, clôture du rapprochement textuel

- **Livrable :** [COVERAGE_SCENARIOS_21_22.md](COVERAGE_SCENARIOS_21_22.md), commit `3d16b5568c2434ea9318efaf97a7c1e738119283`. Sources V3.4 lots 21/22 lues sur main ; blobs `8700846208315f405b7f60266fabf8181e160ff4` et `6fa98816ae2a8048471f6625d3c099df171fb0fb`, identiques à l'index historique.
- **24/24** scénarios (10+14) ont un ticket V34 explicitement cité ; aucune exception textuelle. Windows/recovery/packaging séparés des tests transversaux et de la certification Design Space/physique. Les 25 critères sont ventilés dans le livrable ; aucune preuve produit n'est créée.
- **Bilan provisoire des rapprochements explicites 02–22 :** 51/52 + 103/108 + 120/120 + 88/88 (après correction COV-07B) + 45/45 + 24/24 = **431/437**, avec **6 sans ticket source direct** (03-16 et cinq 06/07). Les cinq cas COV-05B ont des propositions sémantiques non validées. Les 10 exigences G6/G9 sans ticket explicite restent ouvertes. Ce total ne certifie ni 431 DoD ni 431 tests.
- **Preuves :** documentation seulement ; auto/Windows/GPU/Design Space/physique NOT_RUN. `main@HEAD` NON_VÉRIFIÉ : la recherche de commits n'est pas un endpoint autoritatif de branche. Aucun code, AGENTS, PR, merge ou tâche de développement modifiés.
- **Prochaine action unique :** COV-10, traiter les 10 exigences G6/G9 une à une avec texte et critères source exacts, options de rattachement V3.5 et contre-expertise sans nouveaux tickets V34 fictifs.


## 2026-11-13 — COV-10 : qualification candidate G6/G9

- Livrable : [COV10_G6_G9_SEMANTIC_RECOVERY.md](COV10_G6_G9_SEMANTIC_RECOVERY.md), commit `9b08a7aa0218542304f82f7c311012106d2edd9e` ; branche documentaire seulement.
- Sources V3.3 et V3.4 lot 23 lues sur main, blobs cités dans la fiche. Dix exigences S-021/036/037/044/047/064/066/092/099 et R33-028 examinées individuellement : critères hérités, décisions candidates, architecture texte/OCR/gabarits/diorama, négatifs, rollback, preuves séparées, 25 contrôles ventilés. Aucun ticket V34 fictif ; API réelles et PR restent à examiner.
- Couverture historique 24/141/140/80/437 conservée ; photographie de liens explicites **431/437**, six exceptions ; dix exigences sans ticket V34 direct **toujours ouvertes** en attente de revue et adoption. Tests produit/Windows/GPU/Design Space/physique NOT_RUN. main@HEAD NON_VÉRIFIÉ. Aucun code, merge, AGENTS ou tâche de développement modifiés.
- Prochaine action unique : **COV-10B**, auditer ports code main et PR des dix exigences pour arbitrage technique sans doublons.


## 2026-11-13 — COV-10B : ports réels et propriétaires candidats G6/G9

- **Livrable :** [COV10B_PORTS_AND_G6_G9_OWNERS.md](COV10B_PORTS_AND_G6_G9_OWNERS.md), commit `23e3df23088d95b594c75db14e27b9edbe79feba`, branche documentaire uniquement.
- **Sources vérifiées :** quatre fichiers de code sur main (SHA blobs individuels dans le livrable), recherches de ports typographie/OCR, trois PR code ouvertes #138–140. Les ports `folded_card`, `open_tray`, `preflight_template`, `TemplatePreviewContent` et `NativeAppShell` sont réels, mais ne livrent ni OCR, ni diorama quatre plans, ni exports gabarits. Les PR sont hors G6/G9.
- **Arbitrage :** dix exigences conservées et regroupées en propriétaires **candidats**, sans nouveau ticket V34, moteur concurrent ou modification de la whitelist du prévol. Les API texte/objet/writer/export n'ont pas encore été inspectées exhaustivement ; l'absence de résultat de recherche n'est pas une preuve d'absence de fonctionnalité.
- **Preuves :** audit documentaire uniquement, tests unitaires, UI Windows, GPU, Design Space et coupe physique **NOT_RUN**. main@HEAD **NON_VÉRIFIÉ**. Inventaire 24/141/140/80/437 inchangé, 431/437 liens explicites, six exceptions, dix G6/G9 sans ticket direct encore ouverts. Les 25 contrôles ventilés sans certification fictive.
- **Prochaine action unique : COV-10C**, examiner API V1, texte/objets et exporteurs, puis confirmer ou rejeter les propriétaires candidats avec références exactes.

## 2026-11-13 — COV-10C à COV-15 : consolidation transversale et vérification des inventaires

**Contexte :** continuation demandée par le propriétaire. La tâche horaire V3.5 est active et la roadmap V3.4 reste normative pour le développement. `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935` a été vérifié par le véritable endpoint GitHub `GET /repos/frenndak/SmartSVG-Studio/branches/main`, et non par un tri de commits. Trois PR code DRAFT #138/#139/#140 restent ouvertes à la lecture, aucune PR documentaire supplémentaire créée.

### Fiches, corrections et commits réellement publiés sur la branche candidate

- **Erratum COV-10B** : inversion historique corrigée (**S-037 = gabarits métiers**, **S-064 = licences/typographie**, **R33-028 = glyphes/licences G6–G8**, pas diorama). Commit `f79ca9f3eaa9e46bc0a15ba9edab8fc8b1744ba4`.
- [COV10C_V1_TEXT_EXPORT_PORTS.md](COV10C_V1_TEXT_EXPORT_PORTS.md), commit `5b14ee8d0c51e42d4845b755e9502743f7c23c30` : lecture des API `LoadedProject`, `Artifact`, `ManagedWorkspace`, `editor_v216`, recovery CAS, production historique PNG, prévol/export, QA, `delivery_manifest` et `write_delivery` JSON ; contrats réels vs interfaces *proposées* explicitement distingués. `Artifact.use` V1 = 3 types, mais 4 sorties métier distinctes, SVG multicouche externe.
- [BACKLOG_AND_DEPENDENCIES.md](BACKLOG_AND_DEPENDENCIES.md), commit `4a1cf15a619a4d9d2592abd69246bcb69b0734b1` : **17 unités candidates W00–W16** P0/P1/P2, vrai graphe de dépendances, gates A/B/C, G6/G9 conservés. Ce ne sont pas 17 nouveaux tickets normatifs.
- [UX_ARCHITECTURE_AND_WORKFLOWS.md](UX_ARCHITECTURE_AND_WORKFLOWS.md), commit `06a9a744518879b1edef210a41ec4adec402416e` : **8 parcours UX**, 80 IDs A01–E20 avec intitulés originaux #134, domaines et priorités provisoires ; 30 P0/41 P1/9 P2 candidats, non adoptés et non certifiés.
- [QUALITY_TESTS_AND_EVIDENCE.md](QUALITY_TESTS_AND_EVIDENCE.md), commit `8c275394c919a415924ce19dfccc462968595050` : séparation stricte des preuves DOC/UNIT/Windows UI/GPU/Design Space/physique, cinq parcours E2E, cas adversariaux et récupération ; aucun test produit exécuté par cette opération.
- [ADR_RISKS_OPPORTUNITIES.md](ADR_RISKS_OPPORTUNITIES.md), commit `92b44e3da2452bbeaa5520b88db27850f0efbb46` : neuf ADR candidates, risques, **33/33 opportunités historiques avec décisions/rejets conservés**, premières décisions sur les nouvelles idées #141. Les 33 arbitrages individuels *complets* restent ouverts.
- [PROMOTION_CHECKLIST.md](PROMOTION_CHECKLIST.md), commit `9a4d311d7dfda727b99b39831c5fac7bd0922f63` : **15 gates NO-GO/GO**, revue et PR docs puis modification de gouvernance séparée, aucune promotion automatique.
- [README.md](README.md), commit `a7d1a6883ec167a16ea3d6769bb51e7bcf879d99` : liens vers tous les nouveaux livrables, état honnête des gates encore ouverts.

### Vérifications réellement effectuées

- Relecture des fichiers documentaires publiés : **24/24 lots**, **141/141 exigences**, **140/140 tickets**, **80/80 IDs UX**, **437/437 scénarios historiques distincts**, **33/33 opportunités**, **17/17 unités W00–W16** et **15/15 gates G35** inventoriés. Aucune disparition d'identifiant dans ces inventaires.
- Contrôle des liens relatifs des six documents principaux et du README : **0 cible locale manquante** parmi les liens testés sur la branche.
- La matrice antérieure demeure : **314/314** arêtes réciproques exigence–ticket dans V34, **431/437** références scénarios→tickets explicites; **6** scénarios non reliés explicitement et **10** obligations historiques G6/G9 sans ticket V34 direct restent ouverts.
- Aucune preuve de fonctions 80/80 prêtes à coder, ni de 437 tests PASS. **Tests produit exécutés par cette opération : 0** ; Windows/GPU/Design Space/Cricut PHYSICAL = **NOT_RUN**. Audit de code source et des documents uniquement.
- Aucune modification de `main`, `AGENTS.md`, des archives, des sources produit ni de la tâche horaire de développement. Aucune PR docs ni merge.

### Revue contradictoire et prochaine action précise

**La campagne V3.5 a une PREMIÈRE STRUCTURE DOCUMENTAIRE pour tous les grands domaines, mais pas encore la contre-expertise sémantique complète exigence par exigence. NE PAS PROMOUVOIR.**

1. **Prochaine action unique COV-16** : auditer sans raccourci les **six scénarios sans propriétaire source** et les **dix obligations G6/G9**, confronter leurs critères V3.3 à COV10C/W10/W11/W16, proposer puis faire revoir les propriétaires V35 sans inventer de liens V34.
2. Ensuite **COV-17** : revoir individuellement les **80 IDs UX** et les **33 opportunités O-001..O-033**, rendre une décision argumentée en regard de V34 et de #141, et ne pas masquer les fonctions rejetées.
3. Ensuite **COV-18** : rapprocher sémantiquement les **437** recettes et leur DoD, produire audit indépendant, vérifier l'ensemble des **15 gates** et préparer une PR documentaire **seulement quand WIP et revue le permettent**.

**Règle de relance** : ne pas recompiler une nouvelle fois les 437 identifiants ni recréer COV10C–15. La tâche horaire doit reprendre au premier écart sémantique réel, documenter les preuves exact-head et poursuivre la roadmap entière.

## 2026-11-13 — COV-16 : six scénarios orphelins et dix exigences G6/G9

- **Fiche** : [COV16_EXCEPTIONS_AND_G6_G9_OWNERS.md](COV16_EXCEPTIONS_AND_G6_G9_OWNERS.md), commit `c9ba790dbe327d9c504cdd1f938c1ac64633b0b9`, indexée dans README commit `2f67d6721989d5f7f16470b61ed7f808080d252b`.
- **Arbitrage conservateur** : les six scénarios `03-16,06-22,06-24,06-25,07-16,07-25` ont chacun un propriétaire **candidat** Wxx et un test/DoD proposés ; les **10 obligations G6/G9** sont identifiées une par une et réparties entre W10/W11/W16. Ce ne sont **pas** des tickets V34 rétrospectifs ni des modifications du backlog normatif.
- **État des preuves INCHANGÉ** : **431/437** relations TEST→TICKET explicitement présentes à l'origine, **6/6** rapprochements sémantiques **CANDIDATS** supplémentaires, **10/10** obligations G6/G9 avec route proposée, **0** adoption normative dans cette passe. Aucun test produit, Windows, RTX, Design Space, coupe physique exécuté.
- **Écart prioritaire** : revue contradictoire de l'adéquation propriétaire et du critère complet pour chaque relation, puis décision individuelle des 80 capacités UX et des 33 opportunités. Un mapping initial ne constitue pas une revue qualitative 80/80.
- **Prochaine action unique V35-COV-17** : commencer la revue sémantique **A01–A16 (16 capacités Smart Import/Select/Clean/Color/Vector)** en comparant spécifications V3.3/V3.4, code actuel et parcours UX V3.5 ; décider pour chacune GARDER/RACCORDER/FUSIONNER/REPORTER/REJETER avec raison, API existante, négatifs et DoD. Continuer ensuite B/C/D/E, puis 33 opportunités, sans prétendre que la promotion est prête.


## 2026-11-13 — COV-17A : revue individuelle UX A01–A16

- Livrable [COV17A_UX_A01_A16_SEMANTIC_REVIEW.md](COV17A_UX_A01_A16_SEMANTIC_REVIEW.md), commit `d49fda5a52f05ae60238c10f1357899af7e24dd8` sur branche documentaire. 16 décisions candidates individuelles, propriétaires Wxx, contrats transversaux et au moins trois négatifs par ID, cinq micro-lots TDD et ventilation des 25 critères.
- Limite explicite : rapprochement exact par S/R33/ticket/scénario/DoD et audit approfondi du code A01–A16 non terminés ; 0/16 certifiée prête à coder. Aucun test produit exécuté ; Windows/GPU/Design Space/physique NOT_RUN. Main HEAD NON_VÉRIFIÉ dans ce cycle.
- Inventaire historique 24/141/140/80/437 conservé ; 431/437 liens explicites, six exceptions, dix G6/G9 sans ticket V34 direct toujours ouverts. Aucune modification main, AGENTS, code, PR, merge ou automatisation.
- **Prochaine action unique : COV-17B** — examiner B01–B14 individuellement (objets/calques/texte/OCR), ports V1 et critères exacts, contre-expertise et DoD.

## 2026-11-13 — V35-COV-17A/B/C/D/E : 80 décisions UX candidates contrôlées

**Demande de poursuite propriétaire :** audits A01–E20 réalisés dans la même session après la consolidation COV10C–16, sans réécrire les critères V3.3/V3.4. Les cinq documents reprennent les libellés historiques #134 et documentent pour chaque ID une décision candidate, état du port existant ou limite, critère/DoD et négatifs.

| Dossier candidate UX | IDs contrôlés | Commit GitHub publié |
|---|---:|---|
| [COV17A — image/sélection/vectoriel](COV17A_UX_A01_A16_SEMANTIC_AUDIT.md) | **16/16 A01–A16** | `0bc92965636cc4db269259fcece682ca142dcc4b` |
| [COV17B — objets/calques/texte](COV17B_UX_B01_B14_SEMANTIC_AUDIT.md) | **14/14 B01–B14** | `f41a1c9f6c86a71b6b95bbba432cba38065369c9` |
| [COV17C — Cricut/fabrication](COV17C_UX_C01_C18_SEMANTIC_AUDIT.md) | **18/18 C01–C18** | `1f64a6f399d83ab1d3e1de7e0956aef00d2bc8b1` |
| [COV17D — IA/automatisation](COV17D_UX_D01_D12_SEMANTIC_AUDIT.md) | **12/12 D01–D12** | `2a4c731651338d18c08c1117d303ce32950708ff` |
| [COV17E — application/qualité](COV17E_UX_E01_E20_SEMANTIC_AUDIT.md) | **20/20 E01–E20** | `ecb9d59d9d2816fa49f99db3f829058d6a809351` |

- **Contrôle réellement exécuté** : relecture par GitHub des cinq fichiers, extraction des IDs des tableaux, comparaison à l'univers A01–A16, B01–B14, C01–C18, D01–D12, E01–E20 : **80 lignes, 80 IDs distincts, zéro oublié/dupliqué**, blobs présents. [README](README.md) actualisé commit `8f5196b779222c092af3d2ffc2f5215b53e81ae7`.
- **Réalité technique vérifiée** : `vectorize_flat_art` pour groupes couleurs éditables, `auto_hd` dérivé CPU, `auto_masks` propositions conservatrices, `NativeAtelierPanel` et `NativeImageViewport` Tk, `project_recovery` CAS et `artifact_qa` statique. **Le fait qu'un port existe n'implique pas que le parcours complet est disponible**. Risque explicitement inscrit : `provider_v2112` peut télécharger des poids au premier appel, donc consentement/hashes/licences avant invocation.
- **État honnête** : `UX_DECISIONS_CANDIDATES=80/80` ; `UX_DECISIONS_INDEPENDENTLY_REVIEWED=0/80` dans cette session ; `UX_DOC_ADOPTED=0/80`. Les critères historiques complets/relations exactes tickets et DoD doivent encore être confrontés un par un. **Tests produits de cette session = 0**, Windows UI/RTX/Design Space/physique NOT_RUN.
- **Autres obligations** : 24/141/140/437 inventaires conservés, 431/437 citations scenario→ticket historiques et six arbitrages COV16 **candidats** ; dix exigences G6/G9 ont des responsables **proposés**, pas adop­tés.
- **Gouvernance** : main et code produit inchangés, aucune PR documentaire ni merge, V3.4 normative, automatisations horaires inchangées.
- **Prochaine action UNIQUE : V35-COV-18A** : contre-expertise croisée indépendante des **80 décisions UX candidates** avec 141 critères historiques / 140 tickets / 33 opportunités. Commencer par **A01–A16 et B01–B14**, lier explicitement chaque critère et DoD au contrat existant ou à un delta V3.5, noter `UNASSIGNED` et refuser les doublons. Ensuite C/D/E et revue de promotion de la documentation. **Ne pas recommencer les 5 fiches individuelles**, ajouter leur revue critique et la traçabilité sémantique.

## 2026-11-13 — Coordination avec l'exécution horaire concurrente (COV17A)

La tâche horaire a publié indépendamment [COV17A_UX_A01_A16_SEMANTIC_REVIEW.md](COV17A_UX_A01_A16_SEMANTIC_REVIEW.md), commit `2f71f82641577d2bf1d1635c754a0ab91993471e`, pendant cette campagne de conception. Le fichier est présent et relu. Il s'agit de **la même famille A01–A16** que [COV17A_UX_A01_A16_SEMANTIC_AUDIT.md](COV17A_UX_A01_A16_SEMANTIC_AUDIT.md), mais sous un autre angle. Il ne faut **ni additionner les deux en 32 fonctions**, ni supprimer un audit sans revue contradictoire. Le README pointe désormais vers les deux.

**Règle pour COV-18** : confronter les deux décisions A01–A16, résoudre leurs différences documentées si nécessaire, puis qualifier les 80 IDs contre les 141 exigences, 140 tickets et 33 opportunités. La prochaine tâche horaire doit **reprendre COV-18**, pas recréer COV17B/C/D/E déjà présents. La V3.4 reste ACTIVE, aucun test produit nouveau, PR docs, merge ni promotion.

## 2026-11-13 — COV-18A première contre-expertise croisée A/B

- [COV18A_UX_AB_CROSS_REVIEW.md](COV18A_UX_AB_CROSS_REVIEW.md), commit `df690ac86a43ddedc6498defecbe2df4f10e59dd` : rapprochement contradictoire des deux fiches A01–A16 et du dossier B01–B14. Trois écarts de priorité/scope A04/A08/A16 identifiés et arbitrages candidats documentés; blocage schéma persistant B01/B02/B09 explicité. 30 décisions candidates examinées, 0 certifiée avec liens S/R33/V34/DoD complets.
- 24/141/140/80/437 inventoriés, 431/437 liens historiques, six exceptions et dix exigences G6/G9 conservées. Contrat 25 axes ventilé; tests produit/Windows/GPU/Design Space/coupe physique NOT_RUN. Main HEAD NON_VÉRIFIÉ lors de cette passe; aucun code, AGENTS, PR, merge ni automatisation modifiés.
- **Prochaine action unique COV-18A-1** : établir les liens exacts exigences↔tickets↔scénarios↔DoD pour A01–A16/B01–B14 et confronter A04/A08/A16 aux critères historiques avant certification.

## 2026-11-13 — COV-18A-1 : première tranche traçabilité A/B

- [COV18A1_AB_EXACT_TRACE_FIRST_PASS.md](COV18A1_AB_EXACT_TRACE_FIRST_PASS.md), commit `d5c195f7bb25bc76a9fe944717c32835b158170f` : 10/30 correspondances UX A/B candidates vers exigences S/R33, tickets V34 explicitement cités et tests transversaux du lot 22. Distinction stricte entre lien source exigence↔ticket et association sémantique UX↔exigence proposée ; B09/G6 sans ticket direct maintenu.
- Contre-expertise : A04 sélection ≠ segmentation, A08 interpolation ≠ détail restauré, A12/A15 SVG d'édition ≠ CUT, B04/B09 brouillon ≠ persistance V1 autorisée. Cinq négatifs et reprise prévus, non exécutés.
- Inventaires historiques 24/141/140/80/437 inchangés ; 431/437 liens scénarios↔tickets source et six exceptions inchangés ; **10/30 liens UX candidats de première tranche, 0/30 certifiés**. Tests produits 0 ; Windows/GPU/Design Space/physique NOT_RUN. Main HEAD NON_VÉRIFIÉ par lecture de branche dans cette passe.
- Aucune modification main, AGENTS, code produit, PR, merge ni tâche de développement. **Prochaine action unique COV-18A-1b : compléter les 20 IDs A/B restants avec exigences, tickets, scénarios spécifiques et DoD intégraux, puis revue contradictoire des 30.**


## 2026-11-13 — COV-18A-1b : complément 20/20 associations A/B

- [COV18A1B_AB_TRACE_REMAINING_20.md](COV18A1B_AB_TRACE_REMAINING_20.md), commit `ac6ca2d9547b77d8a3b138a8a3d73f3e3f273039` : 20 IDs A/B supplémentaires rapprochés des points d'entrée S, tickets V34 lorsqu'ils existent et tests transversaux. **10 + 20 = 30/30 IDs A/B candidats, 0/30 certifiés** ; UX→S inféré, critères intégraux, DoD et scénarios locaux encore à confronter.
- Inventaires 24/141/140/80/437, 431/437 liens historiques, six exceptions, dix exigences G6/G9 sans ticket V34 direct inchangés. Contrat 25 axes ventilé dans la fiche ; quatre exports, V1/CAS/float32, tri-state et IA opt-in préservés.
- Aucun test produit/Windows/GPU/Design Space/coupe physique exécuté (NOT_RUN). main@HEAD NON_VÉRIFIÉ ; aucune modification code, AGENTS, PR, merge ou tâche de développement.
- **Prochaine action unique COV-18A-2** : confronter les 30 associations A/B aux critères V3.3 intégraux, DoD V34 et scénarios locaux, avec revue contradictoire avant certification.


## 2026-11-13 — COV-18A-2a : revue hostile de six liens A/B

- [COV18A2A_AB_HOSTILE_SIX.md](COV18A2A_AB_HOSTILE_SIX.md), commit `9021dcb0a86b34ae22b9d45446aa21079124f6ea` : examen indépendant ciblé A02/A03/A04/A08/A12/B09 contre les lignes explicites du lot 23, décisions de non-surinterprétation, contrats de brouillon/CAS, sept négatifs et plan TDD. **6/30 examinés dans cette passe, 0/30 certifiés** ; critères intégraux V3.3, DoD et scénarios locaux encore ouverts.
- Main : dernier SHA retourné par recherche de commits `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`, **HEAD DE BRANCHE NON VÉRIFIÉ** ; PR ouvertes observées #138/#139/#140. Aucun test produit exécuté ; Windows/GPU/Design Space/physique NOT_RUN.
- Inventaires 24/141/140/80/437 conservés ; 431/437 liens historiques explicites, six exceptions et dix exigences G6/G9 sans ticket direct inchangés. Aucun code, AGENTS, PR, merge ou automatisation modifiés.
- **Prochaine action unique COV-18A-2b :** lire critères V3.3 intégraux et DoD locaux exacts des six IDs, associer les scénarios locaux avec lignes et résoudre les écarts avant d'étendre la revue aux 24 autres.


## 2026-11-13 — COV-18A-2b : six critères historiques confrontés

- Livrable [COV18A2B_V33_CRITERIA_SIX.md](COV18A2B_V33_CRITERIA_SIX.md), commit `e1a8bafa1163569625102a370a2c6308944ce7db`. Lecture des sources V3.3 MASTER/TRACEABILITY/HERITAGE et du lot 23 V3.4 : six critères textuels et dépendances pour A02/A03/A04/A08/A12/B09, correction des surinterprétations (12 sujets même ID, rejet des faux sujets, avant/après objectif, quatre profils séparés, pas de substitution de police). Trois protocoles TDD et négatifs ajoutés, non exécutés.
- **Reste ouvert** : DoD complets des tickets locaux et scénarios locaux exacts, puis confrontation des 24 autres A/B. 6/30 critères examinés, **0/30 certifiés**. Univers historiques 24/141/140/80/437 inchangés ; 431/437 liens historiques explicites, six exceptions et dix G6/G9 sans ticket direct.
- Main HEAD de branche NON_VÉRIFIÉ ; recherche de commits renvoie `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935` comme dernier commit indexé, non preuve du HEAD actuel. Tests produits, Windows, GPU, Design Space, physique NOT_RUN. Aucun code, AGENTS, merge, PR ni automatisation modifiés.
- **Prochaine action unique COV-18A-2c** : retrouver DoD et tests locaux des tickets A02/A03/A04/A08/A12/B09 dans les lots V3.4 concernés et consigner les écarts assertion par assertion.

## 2026-11-13 — COV-18A-2c→3b : six DoD, arbitrages et 12 UX supplémentaires

**Reprise manuelle avec autorisation propriétaire :** quatre fiches **nouvellement créées et relues** sur la branche candidate, sans toucher au code produit ni aux archives V3.4.

- [COV18A2C_LOCAL_DOD_SIX.md](COV18A2C_LOCAL_DOD_SIX.md) — commit `7a57ca939f2291393e233fcbae422c34cd7950b7` : **13 micro-fiches V34**, **53 citations** de scénarios locaux correspondant à **52 IDs distincts**, pour A02/A03/A04/A08/A12/B09 ; les références du lot 23 qui manquent dans les micro-fiches sont identifiées sans les effacer.
- [COV18A2D_ARCHITECTURE_ARBITRATION.md](COV18A2D_ARCHITECTURE_ARBITRATION.md) — commit `177232b146b3152e8fd5102a6b7e9cdc18cddef4` : arbitrages S-032/V34-098 (support topologique), R33-006/V34-133 (consommateur UI), S-009/V34-129 (prévol QA externe), et deux risques S-045 (vinyle multi-couleur ≠ DRAW) / S-048 (IA artistique ≠ CPU upscale). Ports V1/éditeur/import/manifeste vérifiés au snapshot `main@aa0ff9e7`.
- [COV18A3A_UX_NEXT_SIX.md](COV18A3A_UX_NEXT_SIX.md) — commit `c89d4af0e0d60b3d6de3471b2d027785bdd2954c` : revue contradictoire de **A01/A05/A06/A07/A09/A10**. Découplages essentiels S-061 (sécurité import ≠ support formats multiples), S-014 (segmentation ≠ matting), S-060 (métriques ≠ pipette/recoloration).
- [COV18A3B_VECTOR_OBJECTS_SIX.md](COV18A3B_VECTOR_OBJECTS_SIX.md) — commit `4bc78cd42c2461d1377e3ae0b6af61caec412924` : revue contradictoire de **A11/A13/A14/A15/A16/B01**, distinction couche couleur/CUT, diagnostics booléens vs outil d'édition, métriques vs IA, objets persistés vs sujet V1.

**Vérification après écriture :** quatre fichiers lus à leur chemin GitHub exact, blobs présents, IDs attendus et statut CANDIDAT/NON NORMATIF confirmés. La vérification du HEAD main exact au moment final de chaque écriture n'est **pas** revendiquée : sources lues au snapshot `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`. Trois PR ouvertes #138/#139/#140 observées au démarrage.

**État honnête :** sur les **30 IDs A01–A16 et B01–B14**, **18/30** ont maintenant reçu cette revue approfondie par sous-lots (6 + 6 + 6), **0/30 certifiés** ; les 30 avaient déjà des décisions candidates de premier niveau. Les autres familles C/D/E gardent leurs 50 décisions candidates, pas 50 certifications. **Aucun test produit, Windows, RTX, Design Space ou coupe physique n'a été exécuté par ces fiches (NOT_RUN)**. Univers 24/141/140/80/437 inventoriés conservé ; 431/437 liens scénarios→tickets historiques, six exceptions et dix exigences G6/G9 sans ticket direct restent à qualifier.

**Prochaine action UNIQUE — COV-18A-3c :** confronter les **12 derniers IDs A/B**, B02–B08 et B10–B14, aux critères intégraux V3.3, tickets et DoD locaux, en deux tranches de six. Préserver les blocages B02/B09/G6 (modèle de calques/texte), puis procéder à la contre-expertise croisée des 50 IDs C/D/E, des 33 opportunités et des gates de promotion. Ne pas recréer COV18A2c–3b ni déclarer V3.5 norme actuelle.
