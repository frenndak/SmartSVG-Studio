# SmartSVG V3.5 — Checklist de préparation et procédure de promotion contrôlée

**V35-COV-15 — version candidate, 13 novembre 2026.** Concerne la **promotion de la feuille de route documentaire** V3.5, PAS la certification d'un logiciel V3.5 déjà livré. **Statut au moment de la rédaction : NO-GO** ; les gates ci-dessous ne sont pas tous satisfaits. La V3.4 reste la roadmap active tant que la gouvernance `AGENTS.md` n'est pas modifiée séparément et après revue.

**Documents de preuve V3.5** : [README](README.md), [héritage](INHERITANCE_REGISTER.md), [couverture source](COVERAGE_V34_TO_V35.md), [index 437 scénarios](SCENARIOS_V34_INDEX.md), [COV10C ports](COV10C_V1_TEXT_EXPORT_PORTS.md), [backlog et dépendances](BACKLOG_AND_DEPENDENCIES.md), [UX 80 capacités](UX_ARCHITECTURE_AND_WORKFLOWS.md), [plan de tests](QUALITY_TESTS_AND_EVIDENCE.md), [ADR/opportunités](ADR_RISKS_OPPORTUNITIES.md), [règles des 25 critères](AUTOMATION_QUALITY_CONTRACT.md), [journal](PROGRESS.md).

## 1. Ce que signifie « V3.5 prête »

La roadmap V3.5 est **prête à être proposée comme référence de conception et d'exécution** quand chaque obligation héritée a une localisation, une décision explicite, une dépendance réaliste, un contrat, un critère DoD et un test de recette prévu. **Cela ne nécessite pas** que toutes les fonctionnalités P2 soient déjà implémentées, ni que des tests Windows/Design Space/physiques proposés aient réussi. En revanche, cela requiert de **ne jamais prétendre qu'ils ont été exécutés** si ce n'est pas le cas.

**La roadmap est incomplète** si elle se contente de recopier des ID, de multiplier les noms « Smart X », d'ignorer les fonctionnalités héritées G6/G9, d'inventer une limite de Cricut, de déclarer un code existant sans vérification, ou de raccourcir ses tests pour aller plus vite.

## 2. Gates de complétude, chacun à prouver séparément

| Gate | Exigence d'admission | État constaté au 13/11/2026 | Preuve attendue pour PASS documentaire |
|---|---|---|---|
| **G35-01 — 24 lots** | Chaque lot V3.4 01–24 possède traitement V3.5, obligations et sorties préservées | **INDEXÉS / REVUE SÉMANTIQUE OUVERTE** | 24/24 deltas documentés, IDs uniques, arbitrages et renvois |
| **G35-02 — 141 exigences** | Tous les critères **intégraux** V3.3 et dépendances conservés | **141 IDs ; critères individuels pas encore tous contre-expertisés** | 141/141 critères vérifiés contre MASTER/HERITAGE/TRACEABILITY/COVERAGE V3.3 |
| **G35-03 — 140 tickets** | Aucun ticket V34 réduit/renuméroté ; port et DoD vérifiables | **140 IDs ; 314 relations de planification réciproques** | 140/140 tickets avec placement V3.5, critères locaux et statuts distincts |
| **G35-04 — 80 UX** | 80 capacités A01–E20 localisées et **décidées individuellement** avec UX et tests | **80/80 indexées, classées provisoirement ; revue individuelle OUVERTE** | 80/80 décisions contredites/revues, sans 80 boutons, tests UX réels prévus |
| **G35-05 — 437 scénarios** | Assertion de chaque scénario source conservée, liens ticket/exigence vérifiés | **437/437 inventoriés ; 431 liens explicitement cités** | 437/437 revus sémantiquement ; six sans ticket attribués ou exceptions signées |
| **G35-06 — G6/G9** | Dix exigences sans ticket V34 direct reprises **sans perte** | **10/10 identifiées + contrats candidats COV10C ; aucune propriétaire normatif adopté** | chaque exigence avec propriétaire V35 adopté et tests; pas de remplacement par simple template |
| **G35-07 — 33 opportunités** | Conserver choix retenu/rejeté/reporté et auditer nouveaux apports #141 | **33/33 repris en ADR ; comparaison sémantique individuelle OUVERTE** | tableau de non-doublons, raisons de rejet intactes, nouvelles idées priorisées |
| **G35-08 — Architecture** | V1/CAS/Subject/float32 et 4 exports sans régression, slots P1/P2 réalistes | **COV10C + backlog W00–W16 rédigés**, décision UI/texte V1/V2 non rendue | ADR revues, port E/S précis, migration contrôlée, pas de writer doublon |
| **G35-09 — Parcours et accessibilité** | Novice/expert, au moins 5 E2E, clavier/DPI/recovery et UI honnête | **UX candidate rédigée**, benchmarks réels non exécutés | design system/états, tests et DoD UX cohérents avec Tk courant |
| **G35-10 — Qualité et risques** | tests positifs/négatifs/reprise, preuves par axe, 25 contrôles conservés | **Plan écrit, tests produits NON_RUN**, 25 contrôles repris mais pas tous certifiés | tests/fixtures/résultats attendus avec liens à DoD et responsabilités |
| **G35-11 — Adversarial review** | Relecture indépendante transversale, contradictions et pertes closes | **NON EXÉCUTÉE intégralement** | registre des anomalies, changements de décisions, réconciliation, revue signée |
| **G35-12 — Intégration documentaire** | Une PR docs complète (pas code), tests de liens/coverage + approbation propriétaire | **PAS DE PR** ; 3 PR code DRAFT ouvertes #138–140 à la dernière vérification | CI exact-head, revue indépendante, diff des archives = 0, fusion contrôlée |
| **G35-13 — Gouvernance** | Changement d'autorité `AGENTS.md` seulement après G35-01..12 et autorisation dédiée | **NON EFFECTUÉ** | PR distincte approuvée, référence du commit V3.5 adopté, procédure rollback |
| **G35-14 — Handoff du producteur** | La tâche de développement reçoit une nouvelle référence uniquement après G35-13 | **V3.4 ACTIVE**, tâche engineering inchangée | nouveau prompt approuvé et séparation des tâches/traces |
| **G35-15 — Source et sécurité** | Archives V3.3/V3.2, baseline V21.14.1 et données/licences intactes | **AUCUNE MODIFICATION revendiquée** | comparaison Git exact SHA, pas de secrets/artworks/modèles, source publique conservée |

**Règle :** un `INDEXÉS`, `SPECIFIÉS`, `PR DOCS` ou `CI VERTE` ne vaut pas automatiquement `GATE PASS`. La colonne « état » est une photographie candidate à actualiser avec les véritables commits et tests. Aucun pourcentage global de progression ne sera calculé en mélangeant inventaire et fonction livrée.

## 3. Critères techniques bloquants — absence de raccourci

- **Projet** : `smartsvg-project/1` et ses consommateurs/recettes conservés ; source, masques float32, identités, writer CAS, erreurs/reprise sans perte. Un champ JSON libre n'est pas une API texte.
- **Quatre exports** : PNG PTC, SVG Basic Cut, SVG CUT multicouche externe, SVG d'édition, non échangés ni persistés frauduleusement via `Artifact.use`.
- **Cricut** : profil et opérations tri-state, guides DS manuels, limites versionnées, preuves matérielles humaines et aucune interaction machine non documentée.
- **Smart Delivery** : ZIP externe non destructeur, typage, hashes, manifestes, QA, licence/privacy, no-clobber et contrôle après relecture. Le JSON historique `write_delivery` n'est pas le ZIP.
- **Texte/OCR/gabarits/dioramas** : dix exigences conservées avec leurs scénarios métier et priorités héritées, OCR facultatif/non-mutant, police et glyphes vérifiés, prototype diorama 4 plans mesuré selon critère G9.
- **IA** : consentement téléchargement/exécution/transfert, provenance/licences/modèles hash, fallback manuel/CPU et gestion OOM/replay.
- **UX** : 80 capacités conservées individuellement, intégrées aux parcours plutôt qu'aux menus encombrés, modèle accessible de brouillon/Undo, réelle UI Windows.

## 4. Procédure de promotion, ordre strict

1. **Geler un SHA de branche V3.5 pour revue** et lire `main` par `GET /branches/main` ; comparer la branche documentaire aux archives et au dernier état des PR de code.
2. **Vérification intégrité** : nombre et unicité des 24/141/140/80/437/33, existence des documents/ancres/liens, liens bidirectionnels et absence d'IDs orphelins, 25 contrôles documentaires satisfaits/justifiés.
3. **Contre-expertise indépendante** : examiner tous les contrats/critères source et risques de dérive ; documenter les incohérences et les traiter. Les cas sans propriétaire ne disparaissent pas derrière une catégorie.
4. **Vérifier le WIP réel** de PR ; seulement si compatible, ouvrir **une PR documentaire consolidée** sur la branche, DRAFT d'abord, sans toucher aux fichiers protégés. Aucune fusion autonome par agent horaire.
5. **Revue propriétaire** du diff et des gates, CI docs exact-head/non-SKIP, résolution des commentaires ; conserver le lien vers décision/commit de revue.
6. **Fusion de la PR docs selon autorisation et protections applicables**, puis contrôler que main contient exactement ces fichiers et leurs liens. Ne pas annoncer V3.5 ACTIVE au stade de la PR docs.
7. **Micro-PR de gouvernance distincte** dans session propriétaire explicitement autorisée, ciblant `AGENTS.md` et la référence active. Aucune tâche horaire n'est habilitée à faire cette modification automatiquement.
8. **Passation de la tâche de développement V3.4 à V3.5** seulement après preuve de la promotion; conserver un plan de retour à la référence V3.4 si échec et les branches/archives sans perte.
9. **Reprise d'ingénierie** avec tickets et gates V3.5 triés par vertical slices ; les tests Windows/RTX/Design Space/coupe physique sont exécutés par les producteurs autorisés, sans prétendre avoir été réalisés à la promotion documentaire.

## 5. Procédure de refus et rollback

- **G35-01..G35-11 non satisfaits** : rester dans la branche candidate et poursuivre, pas de PR de promotion.
- **PR code WIP saturée** : continuer les micro-fiches sur issue #142/branche dédiée sans créer de PR docs concurrente.
- **CI docs échoue** : conserver V3.4 ACTIVE, corriger sur branche et rejouer exact-head ; pas de réduction des assertions pour « passer ».
- **Divergence avec contrat V1 ou exigence V3.3** : ADR, matrice impact, tests et revue ; si décision impossible, statut `BLOCKED` explicite.
- **AGENTS non approuvé** : V3.4 conserve son autorité, V3.5 n'est que la candidate, même si la PR de documents a été fusionnée.
- **Défaut découvert après promotion** : revenir par PR de gouvernance autorisée à la référence V3.4 en préservant le code et l'historique ; ne pas supprimer les fichiers V3.5.

## 6. Évaluation honnête à cette étape

**Faits documentaires** : 24/141/140/80/437 inventoriés ; 431/437 relations TEST→TICKET explicitement retrouvées, six exceptions ; dix exigences G6/G9 préservées et proposées à un port, non closes ; 33 opportunités archivées dans ADR ; premières fiches UX/backlog/QA présentes. **Ce ne sont pas des validations de produit.**

**Principaux NO-GO restants** : revoir individuellement l'ensemble des critères V3.3 et des 80 UX, qualifier sémantiquement les 437 scénarios (pas uniquement les citations), fermer/acter les six exceptions et dix exigences, arbitrer les 33 opportunités et #141, réaliser contre-expertise indépendante et PR documentaire revue.

**Prochaine action autonome logique** : une fois la checklist publiée, effectuer un audit d'intégrité des documents V3.5 effectivement présents, mettre à jour `README.md`, `PROGRESS.md` et l'issue #142 avec les commits et statuts exacts ; poursuivre les gaps sémantiques au prochain passage horaire. Aucune promotion maintenant.
