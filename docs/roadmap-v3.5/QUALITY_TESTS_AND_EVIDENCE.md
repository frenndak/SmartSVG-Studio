# SmartSVG V3.5 — Plan de qualité, 437 scénarios hérités et chaîne de preuves

**Statut : V35-COV-13 / CONTRAT DE QUALIFICATION CANDIDAT, NON NORMATIF (13 novembre 2026).** Ce document décrit comment démontrer les critères et relever les défauts avant une promotion V3.5. Il **ne signifie pas** que les tests sont codés, exécutés ou PASS. La V3.4 reste active et les critères V3.3 complets sont conservés.

**Dépendances** : [index 437 scénarios](SCENARIOS_V34_INDEX.md), [couverture 141 exigences et 140 tickets](COVERAGE_V34_TO_V35.md), [couverture explicite 02–22](COVERAGE_SCENARIOS_21_22.md), [rattrapage G6/G9](COV10C_V1_TEXT_EXPORT_PORTS.md), [80 capacités UX](UX_ARCHITECTURE_AND_WORKFLOWS.md), [backlog W00–W16](BACKLOG_AND_DEPENDENCIES.md), [25 invariants](AUTOMATION_QUALITY_CONTRACT.md).

## 1. Interdiction de la fausse complétude

**Univers d'héritage identifié** : 24 lots, 141 exigences, 140 tickets, 80 fonctions UX et **437 IDs T-V34** avec assertions sources et SHA. Ils ne décrivent pas 437 tests Python. La revue du rattachement textuel `TEST→TICKET` atteint **431/437** ; **6** ne disposent pas d'un ticket cité explicitement et ne peuvent pas être déduits d'un numéro de lot :
`T-V34-03-16`, `T-V34-06-22`, `T-V34-06-24`, `T-V34-06-25`, `T-V34-07-16`, `T-V34-07-25`.

**Autre trou de traçabilité** : dix exigences originales G6/G9 n'ont pas de ticket V34 direct : `S-021,S-036,S-037,S-044,S-047,S-064,S-066,S-092,S-099,R33-028`. Elles restent exigibles par leur critère V3.3 ; la documentation COV10C propose des ports, pas des tickets attribués ni du code livré.

Pour chaque ID, imposer des champs **indépendants** :
- `source_id`, `source_blob_sha`, `original_assertion`, `owner_ticket_refs`, `source_relation_type` (EXPLICIT / REVIEWED_INFERRED / UNASSIGNED), `normative_requirement_refs`, `code_locator`, `test_locator`, `fixture_id`, `environment`, `commit_sha`, `run_id`, `verdict`, `proof_files`, `reviewer`.
- `verdict` par AXE = `NOT_RUN` / `SKIP` / `PASS` / `FAIL` / `UNKNOWN`; aucun verdict global « OK » inféré d'un PDF ou d'une pull request.
- `source_relation_type=EXPLICIT` ne prouve pas la conformité de la fonction, seulement la citation d'un ticket dans une spécification de tests.
- Un **nouveau scénario V35** reçoit un ID V35 séparé et n'est jamais compté dans les 437 historiques pour gonfler la couverture.

## 2. Matrice des axes de qualification

| Axe | Ce qui est vérifié par de vraies preuves | Éléments minimum et interdictions |
|---|---|---|
| **DOC_SOURCE** | Les 24 lots/141 critères/140 tickets/80 UX/437 recettes et les nouvelles décisions restent traçables et cohérents | source blob SHA, règle de projection, test d'unicité, revue contradictoire ; ne pas prétendre à la qualification Windows |
| **UNIT/STATIC** | XML/PNG/ZIP/JSON, typage, unités, invariants géométriques, CAS, absence d'effets réseau | code SHA, test complet, fixture/source hash, logs PASS non-SKIP ; CI générique non ciblée ne couvre pas une fonctionnalité |
| **NATIVE_INTEGRATION** | PNG→.smartsvg→ouvrir/éditer/enregistrer/reprendre→export | Windows runner réel, version OS/Python/libs, logs, captures et artefacts, projet initial/final hash ; ne pas confondre mock Tk et UX réelle |
| **WINDOWS_UI** | clavier/focus/1366×768/DPI 200 %, Undo/Redo, panneaux et messages FR, état vide, pan/zoom, annulation | vrai Tk sous Windows et actions utilisateur identifiées ; pas de validation à partir d'une maquette ou screenshot statique |
| **CPU/GPU_LOCAL** | traitement CPU, modèle facultatif consentit, VRAM/latence/état OOM et récupération | CPU Windows, GPU exact (RTX si disponible), modèle/version/licence/hash, seed quand applicable, source/fixture ; résultat GPU simulé distingué |
| **DESIGN_SPACE** | import réel PNG PTC, dimensions, type opération Score/Draw/Foil, Attacher, version et choix machine | version Design Space, langue, captures autorisées et opérateur, dimensions attendues/observées ; jamais automatique via export SVG |
| **PHYSICAL_CUT** | coupe sur Explore 5 réelle : matériau/mat/outil, décalage, dimensions et montage | protocole signé par opérateur, photos librement partageables, mesures mm, retour d'échec, coupon daté ; CI ne peut pas créer un PASS physique |
| **DELIVERY** | ZIP externe cohérent, manifeste, QA, confidentialité et invariance projet | intégrité avant/pendant/après, archive relue, SHA membres, no-clobber, taille streaming, succès par fichier ; PDF/HTML guide n'est pas certificat |
| **INSTALLER/RECOVERY** | installateur hors ligne, dépendances/absence ComfyUI, restauration, mise à jour/rollback | VM Windows propre ou poste test, version/build/hashes, données conservées, test corruption/crash/read-only ; un ZIP source n'est pas un installateur |

## 3. Cinq familles de tests E2E — oracles et cas adversariaux

### E2E-01 — Sticker : import → nettoyage → PNG Print Then Cut
- **Positif** : image synthétique PNG RGBA, source SHA enregistré, sujets stables, bords contrôlés, export PNG avec dimensions mm/ppi et transparence, réouverture inchangée.
- **Négatifs** : PNG tronqué ou mal orienté EXIF ; alpha rectangulaire trompeur ; 11 sujets réellement confirmés sur 12 demandés ; qualité DPI inconnue ; image hors budget ; action annulée ; destination en lecture seule.
- **Preuve** : unit+Windows pour application et export ; Design Space versionné/Print Then Cut réel indépendant ; coupon physique uniquement après protocole.

### E2E-02 — Vectoriel : contour Basic Cut / multicouche / SVG éditable
- **Positif** : silhouettes synthétiques avec trou interne et deux couches, chemins fermés pour CUT, unités mm/viewBox et groupe éditable séparés, QA typée par contrat.
- **Négatifs** : SVG DTD/entité/script/ref externe ; chemins ouverts/confondus ; nœuds doublés et microformes ; multicouche stocké sous `editable_svg` V1 (doit être rejeté) ; `SCORE` dérivé d'une couleur (refus).
- **Preuve** : quatre types de sortie sont bien différents ; tests géométriques et comparaison du rendu ; les deux tests machine restent distincts.

### E2E-03 — Fabrique : patron CUT+SCORE → guide → coupon réel
- **Positif** : `folded_card/open_tray` déjà présents, paramètres mm vérifiés, séparation des chemins et guide Score/Attacher, QA prévol.
- **Négatifs** : zéro/NaN/inf mm, fente dégénérée, matériau inconnu, prévol obsolète après édition, outil incompatible, export interrompu.
- **G6/G9 distincts** : trois gabarits métier (étiquette/topper/carte) et diorama **4 plans**, aucun ne peut être qualifié en réutilisant seulement la recette `open_tray`. Prototype et montage physique obligatoires là où critère historique le demande.

### E2E-04 — Projet, session, texte, Undo et récupération
- **Positif** : `.smartsvg` V1 créé depuis PNG, SHA figé, sujet/masque et brouillon Undo, commit CAS, réouverture et état cohérent ; texte G6 seulement après contrat et port réels.
- **Négatifs** : relecture SHA devenu périmé ; double `command_id` différent ; same command after crash ; pending backup ; fonte manquante/licence interdite ; OCR refusé ou absent ; résultat IA tardif.
- **Preuve** : chaque fichier initial/final hash, snapshot, journal recovery et test Windows exact-head. Le document `editor_v216` actuel n'accepte que les strokes; une entrée texte libre n'est pas un test de texte valide.

### E2E-05 — Planche, bibliothèque, CSV, Smart Delivery
- **Positif** : 12/24/50 instances et batch/reprise sans duplication; SHA et identités conservés ; ZIP depuis au moins un export réel sain avec liste, manifest typé, SHA et guide statique hors ligne.
- **Négatifs** : dépasser `MAX_MASKS=32` sur un seul lot; CSV dangereux/formule/chemin absolu; batch échoué au milieu; destination ZIP existante; symlink/jonction, fichier changé en cours de copie, source privée involontaire, zip-bomb/collision Unicode.
- **Preuve** : rapport par tâche/page, tests mémoire/latence, ZIP décompressé vérifié, copie du projet inchangée, jamais de faux import Cricut.

## 4. Matrice d'échec système et de récupération

| Injection | Comportement obligatoire | Ce qu'il ne faut surtout pas revendiquer |
|---|---|---|
| Fichier projet corrompu/ZIP traversal | Rejet, aucun écrasement, diagnostic sans chemin privé | « Réparé » par une lecture partielle ou faux succès |
| SAVE interrompue/disque plein | Dernier projet sain intact, dossier recovery explicite | Commit validé sur simple retour UI |
| Modification concurrente du projet | Refus CAS, réinspection et confirmation explicite | Réapplication silencieuse à un SHA différent |
| GPU OOM / modèle absent | Projet et brouillon intacts, repli manuel/CPU, consentement | Équivalence qualité IA non démontrée |
| Preview asynchrone périmée | Ignorée sans mutation, nouvelle preview stable | Ancien masque/export présenté comme courant |
| ZIP Smart Delivery concurrent | Publication exclusive ou échec fermé, aucune archive écrasée | ZIP complet si un membre manque |
| SVG importable local mais illisible par Design Space | Signaler `DS_NOT_RUN/FAIL`, préserver export et avertissements | Compatibilité Explore 5 garantie |
| Police absente / glyphes non disponibles | Alerte de différence, retour au texte source, pas de chemin perdu | Substitution ou conversion transparente garantie |
| Matériau inconnu | `UNKNOWN` et guide, pas `READY_TO_CUT` | Preuve physique de coupe issue du prévol |
| Mise à jour Windows ratée | Restaurer version de l'application, archives V1 intacts | Absence de régression basée sur seul test Linux |

## 5. Procédure reproductible de collecte et de revue

1. **Capturer le commit SHA exact depuis `/branches/main`**, pas seulement une recherche de commits. Pour PR, `head.sha` doit être celui du job. Noter date, système, librairies, hardware, source fixture.
2. Déclarer les tests prévus et le véritable périmètre couvert. Pour chaque test, joindre logs/digest, assertion attendue, résultat, contexte. Distinguer runner Windows, GUI réelle, GPU et hardware physique.
3. Construire une table `exigence → (ticket V34 ou justification héritage G6/G9) → recette historique ou V35 → test réel → résultat par axe`. Les liens manquants restent `UNASSIGNED`, non réécrits silencieusement.
4. Mettre en quarantaine tout changement de schéma V1, autorité de writer, contrôle ZIP, profil machine ou dépendance de packaging tant qu'une revue autorisée/ADR n'a pas validé le périmètre. Refuser les suites de tests contournées par `skip` opportuniste.
5. Rejouer les recettes négatives ciblées sur les fichiers modifiés, puis le sous-ensemble transverse de non-régression V3.3. Si un test ne peut pas tourner, indiquer `NOT_RUN`, raison et plan concret.
6. Revoir les preuves physiquement hors CI pour la Cricut ; ne publier que captures/photos autorisées, aucune pièce privée ni licence commerciale dans le dépôt public.
7. Ne promouvoir qu'après tableau des échecs/décisions, revue contradictoire et preuve exact-head. Un `PASS` d'une version antérieure/branche différente ne constitue pas le PASS du SHA fusionné.

## 6. Critères de clôture du plan documentaire V3.5

**Pour déclarer les docs V3.5 prêtes à promotion :**
- [ ] **141/141 exigences** conservées avec critères V3.3 intégrals et décision V3.5 justifiée ; **140/140 tickets** reliés et zéro DoD affaibli.
- [ ] **24/24 lots** V3.4 traités, **80/80 UX** avec décisions individuelles, **437/437 scénarios** avec leur provenance et relation revendiquée exacte ou exception justifiée.
- [ ] Les **six scénarios sans ticket source direct** et les **dix G6/G9** sont explicitement résolus, rattachés ou inscrits comme obligations ouvertes avec propriétaires V35 adoptables.
- [ ] Les nouveautés P0/P1/P2 #141, Smart Delivery, Cut Advisor, Weeding, PTC, Cost, OCR/diorama, recette/CSV et multi-machines ont toutes une fiche de décision, tests et dépendances ; les P2 peuvent être non livrées **mais jamais effacées**.
- [ ] Architecture/UX/V1/export/QA/AI/Windows ont des DoD et gates négatifs ; enregistrement de tout refus ou arbitrage hostile.
- [ ] Documents `README`, `INHERITANCE_REGISTER`, `BACKLOG_AND_DEPENDENCIES`, `UX_ARCHITECTURE_AND_WORKFLOWS`, `QUALITY_TESTS_AND_EVIDENCE`, `ADR_RISKS_OPPORTUNITIES`, `PROMOTION_CHECKLIST` cohérents et référencés.
- [ ] Une PR documentaire consolidée est revue et sa CI documentaire exécutée ; le changement de norme `AGENTS.md` est un acte **séparé** explicitement autorisé. Les trois PR code ouvertes ne sont pas bloquées.

**Attention :** la qualification produit complète pourra continuer après la **promotion de la roadmap**, puisque celle-ci reste un plan d'exécution. La promotion documentaire ne promet pas que la V3.5 du logiciel est déjà publiée.

**Prochaine action** : rédiger `ADR_RISKS_OPPORTUNITIES.md` et `PROMOTION_CHECKLIST.md`, puis effectuer une réconciliation indépendante de ce plan avec les 25 invariants et les tables ID sources.
