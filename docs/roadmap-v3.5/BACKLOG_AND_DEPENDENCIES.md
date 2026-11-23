# SmartSVG V3.5 — Architecture du backlog, dépendances réelles et jalons

> **Complément fonctionnel 18/11 :** appliquer les dépendances et critères de la [contre-expertise F01–F12](CONTRE_EXPERTISE_FONCTIONNELLE_2026_11_18.md#2-défauts-confirmés-à-corriger-en-priorité) aux unités W01/W02/W03/W12/W13 concernées. Le budget de masques V1 est une contrainte pour les grands sujets et planches, distincte de la limite de 32 sujets et du nombre de placements. Examiner les masques recadrés ou tuilés, leur mémoire, la relecture V1 et une migration qualifiée avant tout changement durable. Les améliorations futures et l’étude PDF sont décrites dans la [section dédiée](CONTRE_EXPERTISE_FONCTIONNELLE_2026_11_18.md#5-arbitrages-pour-les-fonctions-futures).

> **Autorité actuelle — 18/11/2026 :** V3.5 est **adoptée** sur `main`. Le pilotage technique et le prochain micro-lot proviennent de [EXECUTION_STATE.json](EXECUTION_STATE.json), `AGENTS.md` et [MASTER_PRIORISE.md](MASTER_PRIORISE.md). Les mentions datées du 13–14 novembre ci-dessous (« V3.4 active », `RUN_STATE.json` ou « CANDIDAT ») sont **des photographies historiques avant promotion**, pas des instructions de reprise valides. Voir la [contre-expertise indépendante](INDEPENDENT_COUNTER_REVIEW_2026_11_18.md).

> **Raccord UX du16novembre : [UXI0–3](UX_INTERACTION_AND_VISUAL_CONTRACT.md).** W01/W02/W13 portent états, libellés et focus ; W02/W03/W13 le premier parcours import→correction→save/reopen→export ; SCN/CST et leurs CP requis les éléments/réglages ; W12/W13/E20 répétition/recherche/finition. Aucun nouveau ticket, moteur, writer ou classement ; D08 précède toujours le gros éditeur, pas les tranches natives utiles. Les18recettes UXI restent proposées, hors437/17SCN/14CST.

> **Pilotage courant — 14/11/2026 :** lire [RUN_STATE.json](RUN_STATE.json) et [EXECUTION_PLAYBOOK.md](EXECUTION_PLAYBOOK.md). Leurs décisions/cursor remplacent les anciennes « prochaines actions » ci-dessous. [Arbitrages transversaux](DECISIONS_TRANSVERSALES.md), [composition persistante](ADR_COMPOSITION_PERSISTENCE.md), [contrat Smart Delivery](SMART_DELIVERY_EXECUTION_CONTRACT.md) et [rapport de campagne](CAMPAIGN_REVIEW_2026_11_14.md) complètent cette photographie. V3.4 reste active ; delta relu ; revue globale en attente.

> **Complément de pilotage du 14 novembre 2026 :** l'[ordre de livraison recommandé](MASTER_PRIORISE.md) précise l'entrée des premières tranches W00–W16, et l'[index priorisé](PRIORITY_INDEX.md) conserve les 80 libellés originaux avec leurs priorités sources. Les unités et critères de ce document restent conservés ; l'ordre ne transforme pas un grand lot en prérequis global et ne renumérote aucun ticket. Les blocages de fin de conception sont suivis dans [COMPLETION_QUEUE.md](COMPLETION_QUEUE.md).

**État : V35-COV-11 / PREMIÈRE CONCEPTION STRUCTURÉE, NON NORMATIVE — 13/11/2026.** La V3.4 reste ACTIVE. Le présent document transforme les inventaires et les arbitrages en unités de livraison ; il **ne remplace pas** les 140 tickets V34 ni leurs critères V3.3. Aucun ticket V35 nouveau n'est déclaré « intégré » du seul fait qu'il est listé ici.

**Sources :** [V3.4 README](../roadmap-v3.4/README.md) et ses 24 lots, [registre V3.4→V3.5](COVERAGE_V34_TO_V35.md), [80 UX](INHERITANCE_REGISTER.md), [437 scénarios](SCENARIOS_V34_INDEX.md), [programme V3.5 #142](https://github.com/frenndak/SmartSVG-Studio/issues/142), [idées et décisions #141](https://github.com/frenndak/SmartSVG-Studio/issues/141), [audit API COV-10C](COV10C_V1_TEXT_EXPORT_PORTS.md), [25 gates](AUTOMATION_QUALITY_CONTRACT.md). HEAD exact main contrôlé via `GET /branches/main` : `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935` au début de la rédaction. L'autorité, les PR et les tests doivent être **revérifiés** au passage suivant.

## 1. Principe de découpage — capacités et interfaces, pas inflation de tickets

Les unités **W00–W16 ci-dessous sont des conteneurs de conception V3.5**, **pas** 17 nouveaux tickets GitHub. Chaque unité doit pointer vers les tickets V34 existants **réellement applicables** ; un ID `V35-xxx` n'est ouvert qu'après examen de non-doublon/DoD et revue. Les exigences originales `S-xxx/R33-xxx`, **y compris G6/G9**, restent contraignantes indépendamment de leur priorité de réalisation.

**États indépendants requis :** `CANDIDATE`, `SPECIFIED`, `REVIEWED`, `DOC_ADOPTED`, `CODE_BRANCH`, `CODE_MAIN`, `WINDOWS_EXPOSED`, `UNIT_PASS_EXACT_SHA`, `WINDOWS_UI_PASS`, `RTX_GPU_PASS`, `DESIGN_SPACE_PASS`, `PHYSICAL_PASS`. Jamais un `TESTED` global vague ; `NOT_RUN/SKIP/UNKNOWN` ≠ PASS. Les statistiques 24/141/140/80/437 désignent un **inventaire**, pas des fonctions terminées.

## 2. Lots de conception, priorités et contrats de sortie

| Unité candidate / priorité | Fonction, utilisateur et valeur | Invariants, ports réels / dépendances | Livrable concret et fermeture de la spécification |
|---|---|---|---|
| **W00 — P0** | Héritage exhaustif et audit anti-perte | Lots V3.4 01–24, V3.3 complet, #134/#141, COV10C ; **431/437 références explicites**, 6 non assignées, 10 G6/G9 sans ticket V34 direct | Matrice de couverture **sémantique**, arbitres de six exceptions et dix obligations, décisions opposées, 25 gates, zéro ambiguïté non signalée |
| **W01 — P0** | **Session Windows native unique** : importer PNG, ouvrir V1, annuler, reprendre sans altérer la source | `NativeAppShell`, `create_native_project`, `ManagedWorkspace`, `project_archive` et `project_recovery` ; pas de second writer | Parcours A réel sur Windows, tests de conflit CAS, crash/pending-backup, sauvegarde/réouverture et absence ComfyUI |
| **W02 — P0** | Atelier réel de sujets, sélection, masques float32, Undo/Redo fiable, outils d'édition | `Subject` et identités, `editor_session_g23` strokes uniquement ; projet V1, cas 32 masques vs 50 sujets | Un même objet/subject ID sur écran, snapshot, undo/replay et export ; aucune sélection démo persistée |
| **W03 — P0** | 4 projections export séparées, géométrie et QA : sticker PTC, Basic Cut, multilayer CUT, SVG éditable | `Artifact.use` V1 n'en autorise que **3 persistées** ; 4e externe ; `run_v211`, `direct_import_v218`, `artifact_qa` ≠ exporteur natif universel | 4 contrats, unités/QA/manifeste, correctifs de parcours, tests réels par axe, aucun alias trompeur |
| **W04 — P0** | Validation de fabrication : CUT, SCORE, DRAW, PRINT, FOIL, profil Explore 5 | Prévol `preflight_template`, contrôles SVG/mm, profil tri-state, manuel Design Space | Coupures statiques vérifiées, Score/Attach guidés ; le gate physique attend le protocole et des mesures |
| **W05 — P1 élevée** | **Smart Delivery SD0** : planifier le pack, typer les fichiers, vérifier sources/sha/licence, sans écrire | `delivery_manifest`, `artifact_qa`, `LoadedProject` ; ne pas confondre JSON historique, archive .smartsvg et futur ZIP | `DeliveryPlan` conceptualisé et fixture multi-format ; refus des fichiers manquants/privés, tests adversariaux |
| **W06 — P1 élevée** | **Smart Delivery SD1/SD2** : ZIP dès UN export réel, interface novice/expert, guide statique hors ligne | Dépend de **W05 et d'au moins UN export W03 validé**, pas des quatre ; chemins Windows/no-clobber/hash/source stable | ZIP relu et vérifié, manifest QA, instructions françaises, confirmation ; aucune promesse DS/physique |
| **W07 — P1** | Smart Cut Advisor : difficulté, microformes, simplification à fidélité contrôlée, options explicables | W03/W04, lots V34 13–15 ; réemployer inspecteur géométrique/cut-path | Diagnostic fidèle/équilibré/facile **sans changer les originaux**, seuils mesurés et prototypes |
| **W08 — P1** | Print Then Cut Assistant + compatibilité Design Space versionnée | W03 au moins PNG, `direct_import_v218`, O-001/002/032 ; calibration dans DS, pas API privée | Guides mm/DPI, alpha/bleed, orientation, contrôle manuel versionné, export non certifiant |
| **W09 — P1 conception ; P2 géométrie automatique** | Smart Weeding : diagnostic puis lignes/boîtes d'échenillage réversibles | W04/W07, prévol topologique, matière/outil UNKNOWN | V1 aperçu sans modification ; lignes de coupe uniquement après protocole géométrique + coupon physique |
| **W10 — P1 G6 hérité** | Typographie/texte dans Atelier : polices, glyphes, licence, conversion en chemins sans perte d'éditabilité projet | Code V1 `editor_v216`/`editor_session_g23` limité aux strokes, sans TextNode implémenté ; cible TextNode/V2 décidée dans ADR_COMPOSITION_PERSISTENCE, aucun ajout caché au writer CAS V1 | Exécuter CP0–6 selon leurs dépendances, puis tests accents/licences/réouverture et 4 outputs ; décision de conception distincte d'adoption et d'implémentation ; **S-036/064/092/R33-028** |
| **W11 — P1 G6 hérité** | Gabarits métiers : étiquette, topper, carte avec édition et reprise | `folded_card/open_tray` sont deux patrons existants, non équivalents aux trois usages G6 | Trois projets distincts, prévol et sauvegarde/réouverture/export, test d'identité ; **S-037** |
| **W12 — P1** | Bibliothèque, séries 12/24/50, CSV, gabarits partageables de base | V34 lots 19/20, workspace stable, cache/reprise/batch, données CSV inertes | Tests uniques/reprise après crash, annotations et licences, pas de duplication de fichiers/sujets |
| **W13 — P1/architecture transverse** | UX mature/accessibilité et arbitrage framework de manière **mesurée** | Tk actuel : shell+Atelier, vérification à 1366×768/DPI 200 %, clavier/focus, packaging | ADR comparatif Tk/Qt/Tauri par latence/cold start/outils disponibles ; migration seulement si blocage prouvé |
| **W14 — P1 pour socle manuel ; P2 pour accélérations** | IA locale facultative : détourage assisté, upscaling conditionnel, OCR guidé ultérieur | `routing_v21121` sans OCR, CPU/manual sans réseau, budgets VRAM, consentement & licences | Catalogue local vérifié, modèle/hash/permissions, tests OOM/race ; aucun téléchargement implicite |
| **W15 — P1 qualité/release** | Windows autonome : installation, mises à jour/rollback, état hors ligne, sauvegarde fiable | W01/W02 ; packaging reproductible, CI exact-head, contrôles de non-régression | Installer réellement utilisable, flux de récupération et refus de corruption ; Windows réel validé |
| **W16 — P2 conservé / R&D** | Diorama 4 plans (S-044/066/099), OCR affiche/couverture (S-021/047), Smart Cost, CSV nom/QR, photos de découpes, multimarque, optimiseur, recettes versionnées et SD3 | G6 composition W10/W11, W03/W04, W12 ; IA W14 seulement pour OCR optionnel ; protos physiques | Fiches séparées de port/contrat/tests et faisabilité. **Exigences G9 restent héritées et conservées** même si leur livraison dépend du jalon adopté ; aucun report silencieux ou abandon |

Pour fermer les raccordements, reprendre les [critères par fonction et recettes de l’Atelier](ATELIER_PARCOURS_ET_RECETTES_UX.md#recettes-de-fermeture-à-reprendre-par-les-chantiers). W01 couvre la miniature et la saisie française. W02/W13 couvre le premier sujet, la protection du brouillon et la réactivité pendant l’enregistrement. W03/W04 raccorde l’action de sortie, ses preuves et le dossier. W07/W12 couvre l’impact d’une correction sur les fichiers et les placements verrouillés. Les autres cartes pointent vers leurs critères dans la même matrice et leurs contrats de référence.

### 2.1. Anti-perte V3.3 explicite

**Dix exigences historiquement sans ticket V34 direct (toutes visibles)** :
- **G6, P1** : `S-036`, `S-037`, `S-064`, `S-092`, `R33-028` → W10/W11 et QA transversale.
- **G9, P2** : `S-021`, `S-044`, `S-047`, `S-066`, `S-099` → W16, avec un port commun OCR et une famille diorama, mais preuves métier distinctes.

**Six recettes TEST→TICKET non explicites** : `T-V34-03-16`, `T-V34-06-22`, `06-24`, `06-25`, `07-16`, `07-25` ; aucune des propositions COV-05B n'est promue comme lien source. La série 431/437 est un *statut de rapprochement textuel*, pas une certification.

## 3. Graphe de dépendance réel (DAG de qualification, non de programmation absolue)

**Studio créatif réversible — [contrat CST](CREATIVE_STUDIO_PRODUCT_CONTRACT.md).** Cinq parcours partagés, pas cinq moteurs : sélection intelligente, recomposition SCN, réglages rééditables, préparation par intention, production répétée. CST0 fixe contrats/fixtures et CP0-CST pour les ressources de recettes ; CST1 raccorde gestes/alertes W02/W13 ; CST2 qualifie un offset physique après transformation du motif puis save/reopen CP0–3 ; CST3 ajoute simplification/protections/variantes W03/W07 ; CST4 réemploie W12/SD. Preview/export externe avant V2 possible, mais pas DoD de réglage durable ainsi ; CP4/5 seulement pour les capacités texte/effets utilisées. D08 benchmark avant gros éditeur conservé, aucune dépendance IA ou SD globale. Les nouvelles recettes CST sont séparées des437historiques et17SCN.

**Parcours transversal ajouté le 15 novembre :** [Décomposer une scène](SCENE_DECOMPOSITION_AND_RELIEF_CONTRACT.md), raffinement B03/B08 et planches/relief. W02 possède extraction et objets, W12 la planche et ses placements, W16 le relief/reconstruction avancés, W14 les fournisseurs optionnels ; W03/W04 gardent exports/prévol. SCN0–5 sont six incréments de ces responsabilités, pas six nouveaux tickets V34. SCN1 aperçu/export externe sans CP2 ; scène/placements rééditables SCN2/3 seulement avec CP0–3 et ressources strictes CP0-SCN ; relief manuel dépend uniquement des capacités utiles CP3–6, sans OCR/texte/3D obligatoires. G9 conserve le prototype quatre plans distinct des planches de pièces libres et du nouveau cas à nombre de plans variable. Aucune fonction n'est déclarée implémentée.

```text
W00 couverture/traçabilité (transverse, pas un gate de code automatique)
W01 projet V1/CAS ─┬─> W02 premier sujet MANUEL (alpha/pinceau/polygone), Undo/reopen
                   ├─> W03 exports typés ─┬─> W04 prévol ──> CAL-CUT SVG réel
                   │                      └─> W08 PTC ────> CAL-PTC distinct
                   ├─> W05 SD0 (plan uniquement, SANS W03)
                   └─> W15a ZIP Alpha versionné (build/test Windows)
W05 SD0 + ≥1 export W03 qualifié ──> W06 SD1 ZIP mono-artefact / SD2 guide
CP0 contrat V2 → CP1 lecture/plan → CP2 migration CAS/recovery → CP3 scène native
                                                            ├─> W10 texte (CP4) → W11 gabarits
                                                            └─> W12 séries persistantes > capacité V1
W07 Cut Advisor : diagnostics sur fixtures W03/W04 ; seuils matiere MESURÉS après CAL-CUT
W09 Weeding : diagnostic non destructif puis coupe seulement après CAL-CUT et W07
W13 benchmark Tk/Qt/Tauri avant le gros éditeur, sans bloquer la tranche Tk utile
W14 IA FACULTATIVE, aucune dépendance W01→W03 vers ComfyUI/GPU
W16 usages avancés indépendants, sous-gates, sans bloquer A1/B1
`````

**Attention :** cette vue décrit les dépendances minimales. **SD0 n'attend aucun export W03** ; seul SD1/W06 requiert au moins un artefact W03 réel, typé, relu et qualifié. Les 4 formats restent obligatoires pour clore **W03**, pas pour démarrer un ZIP mono-artefact en W06. Le développement peut traiter W04, W05, W07, W10 et W13 sur fixtures **en parallèle**. Les seuils de matière/outil/temps sont **UNKNOWN** tant que non mesurés ; la V3.5 n'invente aucune API Cricut.

## 4. Livraison incrémentale et preuves de sortie

Les tranches **A0 → A1 → A2 → B1 → B2 → C** sont détaillées dans [DELIVERY_EXECUTION_PLAN](DELIVERY_EXECUTION_PLAN.md). Elles **ne renumérotent pas** W00–W16 et ne réduisent aucun DoD historique.

- **A0, réconciliation produit** : vérifier W01/W02/W03 existants et clore les PR courantes qualifiées sans refaire les composants fonctionnels ; sujet manuel depuis PNG, brouillon/Undo/reopen et source intacts.
- **A1, Alpha Windows utile** : projet réel et même identité sujet, édition/récupération, **au moins un export typé** déclenché par l'UI, consentement/no-clobber/lecture de retour, build portable traçable et validation sur Windows propre, hors ComfyUI obligatoire. W03 reste ouvert tant que les quatre projections distinctes ne sont pas livrées.
- **A2, preuve Cricut mesurée** : deux sous-gates indépendants CAL-CUT (SVG, taille importée, découpe) et CAL-PTC (PNG imprimé, calibration PTC, écart observé). Relevé matériel avec version/outils/matière, fichier hashé, résultats UNKNOWN/NOT_RUN jusqu'au test réel. Le logiciel peut progresser indépendamment d'un appareil indisponible.
- **B1, premier parcours de livraison** : W05 SD0, W06 ZIP relu dès un export admissible, guide hors ligne, W08 assistant PTC et bibliothèque de base ; pas de fausse certification Cricut.
- **B2, studio avancé** : CP0–CP3 avant scène rééditable, CP4/texte puis W11 gabarits ; quatre sorties W03, séries persistées W12 et leurs tests d'intégrité.
- **C, spécialisations** : W14 IA strictement facultative et W16 sous-tranches ; CPU/manual et confidentialité maintenus.

**Deux dimensions distinctes de « fini » :** (1) livraison produit réellement démontrée par parcours/artefact ; (2) couverture normative et traçabilité V3.3/V3.4/V3.5. Ni une adoption documentaire ni un test CI ne remplace une qualification matérielle.

### W16 décomposé sans nouveaux moteurs ni double propriété

| Sous-tranche | Propriétaire de capacité | Dépendance minimale | Gate propre |
|---|---|---|---|
| W16-SCENE | W02 extraction, W16 recomposition avancée | CP0–3 pour édition durable ; aperçu manuel avant V2 | Source conservée, occultations connues |
| W16-DIORAMA | W16 relief/montage | W03/W04 et scène/positions ; mesures propres | Quatre plans séparés réellement validés |
| W16-OCR | W14 fournisseur OCR ; W16 usages affiches/couvertures | W10 texte si édition durable | Accepter/corriger proposition, licence, provenance |
| W16-COST | W16 calcul ; W12 placements ; W07 géométrie | Dimensions fiables et prix fournis | Estimation identifiée comme indicative |
| W16-PERSONAL | W12 CSV générique ; W16 QR/noms spécifiques | W10/CP requis selon persistance | Séries traçables, pas de champs V1 clandestins |
| W16-ADV | W16 multimarque/optimisation | Profils explicitement inconnus jusqu'aux preuves | R&D, aucun READY machine imaginaire |

Le chemin manuel sans IA doit rester réalisable et testé de bout en bout. Les sous-tranches P2 ne constituent pas des prérequis du jalon A1.

## 5. Modèle de fiche micro-lot, à appliquer dans chaque domaine

Chaque nouveau ticket V35 proposé doit inclure **toutes** ces rubriques :
1. **ID et origine** : fonctions UX A/B/C/D/E, exigence S/R33, ticket(s) V34, scénario(s) T-V34-LL-NN, opportunité #141/O-0xx ; conflit/doublon étudié.
2. **JTBD** novice/expert, parcours “déclenchement → geste → aperçu → correction/Undo → commit → retour → reprise”; code/port/branche/source des limitations.
3. **Autorité** projet `.smartsvg` V1/revision SHA, écritures exclusives CAS, masques float32 et identités, original non modifié, migration V2 explicite.
4. **I/O versionnés** unités/tailles, source d'erreur, capacité UNKNOWN, résultats mutables/non mutables, exploitation des ports existants.
5. **Tests TDD** cas positif, **≥3 négatifs** significatifs, cancel/crash/retry/race/disque plein, rollback, fixture libre, benchmark en conditions réelles.
6. **UX** modes novice/expert, vide/chargement/erreur/conflit/succès, clavier/focus, DPI 200 %, petites tailles et motion réduit.
7. **Qualité et sécurité** licences, données privées, XML/ZIP, chemins, no-clobber, opt-in IA, profil matière, absence de certification implicite.
8. **Preuves** `DOC`, `CODE_MAIN`, `UNIT_PASS`, `WINDOWS_UI`, `RTX_GPU`, `DESIGN_SPACE`, `PHYSICAL` séparés, chaque verdict lié à SHA/log/version/datum.
9. **Effort/risque** estimation qualitative, dépendances minimales, rôle d'équipe, critère d'arrêt, plan de désactivation/rollback.
10. **Prochaine action unique** exécutable par producteur, sans nécessiter que la roadmap entière soit finie.

Une fiche **n'est pas terminée** par la seule répétition de titres ou l'existence d'un module similaire. Exemples : le prévol d'un patron ne satisfait pas « trois gabarits métiers testés » ; un texte dessiné sur PNG ne satisfait pas l'édition typographique ; un `write_delivery` JSON ne satisfait pas Smart Delivery ZIP.

## 6. Politique de revue et passage de témoin

- La tâche horaire V3.5 doit tenir ce document comme **graphe de candidat**, compléter la cartographie ticket→DoD et arbitrer les priorités après lecture des specs source. Elle peut préparer une branche documentaire et des fiches, mais **ne modifie ni main, ni AGENTS, ni la tâche V3.4**, n'ajoute ni PR docs si WIP saturé, ni merge automatisé.
- **Prochaine fiche** : `UX_ARCHITECTURE_AND_WORKFLOWS.md` ; relier les 80 capacités A01–E20 à des parcours d'interface réellement cohérents, sans créer 80 boutons. Puis `QUALITY_TESTS_AND_EVIDENCE.md` ; les axes Windows/RTX/Design Space/coupe physique doivent être écrits avant toute promotion.
- Revue indépendante et contrôles de couverture **24/141/140/80/437**, plus une revue des décisions O-001..O-033/#141, nécessaires pour la V3.5 finale ; aucune prétention `DOC_ADOPTED` avant PR/revue et promotion de gouvernance séparée.
