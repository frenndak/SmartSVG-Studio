# GLOBAL_REVIEW — verdict indépendant de conception V3.5

**15 novembre 2026 — reviewer `review_v35_global`, lecture seule, aucun sous-agent.**

**Verdict : PRÊTE comme conception exploitable et pour l'étape de préparation de la PR documentaire. Aucun défaut Critical ou Important identifié ; trois Minor d'harmonisation des points d'entrée.** G35-01 à G35-11 et G35-15 sont satisfaits au niveau documentaire, sur les preuves cumulées et les vérifications ci-dessous. Ce verdict ne satisfait pas G35-12/13/14 et ne déclare ni V3.5 ACTIVE ni logiciel livré. V3.4 reste l'autorité du produit.

## 1. Cible exacte et indépendance

| Élément | Référence et limite |
|---|---|
| Dépôt / branche | `frenndak/SmartSVG-Studio`, `roadmap/v3-5-design-candidate-20261112` |
| Candidate examinée | **`6f611a50a6eebf35f843decb87c7f6d1aeb9c6cd`**, 132 fichiers de `docs/roadmap-v3.5`, hors `__pycache__` |
| Empreinte locale du périmètre | SHA256 **`4cd8e14ecba1c21311ae32005efa1b85f379461683d8d082f170cee819fc1ca4`** ; noms de fichiers triés, pour chacun `nom + NUL + octets + NUL` |
| Main observé | `0692f804ad21bd775cd0269dd92dc6e2b1cea01f` ; observation API et comparaison des arbres réalisées par le coordinateur, pas requête distante de ce reviewer |
| Copies lues | `canonical-v35` et `history-work`, répertoires sans métadonnées Git ; aucun `git rev-parse` fictif |
| Correspondance distante | Le coordinateur atteste les 132 blobs locaux identiques à l'arbre distant du SHA figé, les 26 pins source identiques à main et le lot22 `6fa98816ae2a8048471f6625d3c099df171fb0fb` ; aucun changement hors dossier V3.5 dans la publication examinée |
| Action de cette revue | Nouveau rapport seulement ; aucun contrat, registre, curseur, fichier produit, workflow, archive, main ou distant modifié |

Le présent rapport est une **nouvelle pièce après le gel**, donc ne fait pas partie des 132 fichiers ni de leur empreinte. Une avancée horaire a ajouté uniquement `GLOBAL_REVIEW_PRELIMINARY_2026_11_15.md` au commit `9fc6cf489d0a0c0aa179b5e61cf3198c1beff6c2`, selon le coordinateur. Cette fiche de 43 lignes a été lue : son verdict provisoire, ses demandes de preuves et G35-12..14 PENDING sont compatibles avec cette revue finale. Elle n'altère aucun contrat examiné ; ses réserves documentaires sont traitées ici, sans en déduire une autorisation de promotion.

## 2. Méthode, lectures et réemploi des preuves

Lecture directe des contrats principaux : `PROMOTION_CHECKLIST`, `AUTOMATION_QUALITY_CONTRACT`, `MASTER_PRIORISE`, `BACKLOG_AND_DEPENDENCIES`, `UX_ARCHITECTURE_AND_WORKFLOWS`, `QUALITY_TESTS_AND_EVIDENCE`, `ADR_COMPOSITION_PERSISTENCE`, `DECISIONS_TRANSVERSALES`, `SMART_DELIVERY_EXECUTION_CONTRACT`, `EXECUTION_PLAYBOOK`, `RUN_STATE` ; en complément Q04 résolution, Q04G, SC-01, SC-02A/B/C/F2, SC-03B, les tableaux A/B de COV18A2C/2D/3A/3B/3C et les trois dossiers COV18B. SC-02D/E ont été rapprochés sur les lignes à risque ; leur revue individuelle antérieure est réemployée dans la portée indiquée ci-dessous. Les pointeurs et états historiques de README ont été distingués du bandeau courant et du curseur.

Relectures parentes directes ciblées : lot06 §§1–7 (CAS, receipts, epoch, Undo, jobs), lot17 §§2–5 (quatre exports, prévol, PARTIAL, guide), lot20 §§2–5 (autorité, tags, duplication, CSV et reprise), Héritage V3.3 G6/G7/G8/G9 et §40. Leurs conditions complètent les extraits du registre ; les critères parents restent intégralement contraignants. Ce rapport ne revendique pas une nouvelle lecture de chaque paragraphe de tous les lots ni une nouvelle comparaison individuelle de chaque critère/DoD/assertion.

Consommateurs réels lus dans `history-work` : `project_contracts.Artifact` et ses trois usages V1 ; schéma strict de `editor_session_g23.parse_editor_document` ; `ManagedWorkspace.create/list_projects_page/inspect` ; `project_recovery.save_with_recovery/resolve_pending_backup` ; `delivery_v21122.write_delivery`. Constat discriminant : le code V1 fait bien CAS et récupération avec publication primaire avant rotation du backup, mais ne constitue pas le futur receipt de commande. Le JSON historique de livraison n'est pas le ZIP Smart Delivery ; le document de strokes n'est pas un TextNode. La présence de ces fonctions ne vaut pas qualification de leurs parcours Windows.

| Preuve réemployée | Ce qui est admis et vérification de fraîcheur | Ce qui n'en est pas déduit |
|---|---|---|
| `REVIEW_DELTA_RESULT` | Revue bornée des contrats consolidés ; lecture fraîche de l'ADR, D01–D09, SD et playbook dans cette revue | Revue entière du produit ou approbation GitHub |
| `REVIEW_DE_CLOSURE`, `REVIEW_DE_E13_E20`, `REVIEW_DE_RESOLUTION` | 32 décisions individuelles, corrections de tickets/critères, V1≠receipt, portabilité/a11y ; résolution relue et hash identique au rapport de session | 32 fonctionnalités exécutées ; anciens rapprochements erronés promus en sources |
| `OPPORTUNITIES_EXECUTION_RESOLUTION`, `REVIEW_SESSION` | 33 opportunités, huit rejets, 15 groupes ; résolution et SC-02B byte-identiques aux SHA256 de la revue indépendante | Nouveaux moteurs, licences actuelles ou métriques acquises |
| `REVIEW_SOURCE_TRANSFER` | Empreintes SC-02D/E/F1/F2, contrôleur et SC-03B recalculées identiques ; revue antérieure des 259 assertions littérales et 106 oracles corrigés, puis 141 précisions/140 lignes de tickets | Compteur437 comme preuve sémantique, seconde lecture exhaustive de tous paragraphes parents |
| `SOURCE_TRANSFER_REGISTER` | Contrôle frais141/140/26pins ; SHA256 actuel `c637e307e64c835e323d9d0b69b2d854e40a699795dcbe89ceb9f3327b0c8a48`. Retirer uniquement `review_evidence` et remettre `REVIEW_PENDING` reconstruit exactement l'empreinte relue `6c5be2af77b43ea6a3a51fbc3e9e355993f78d82db1128f39834ed5ebe875cb5` | Hash de commit syntaxiquement valide comme attestation du HEAD courant |
| `REVIEW_SOURCE_ACCEPTANCE` | Complément indépendant des six familles contextuelles, avec clauses/tests effectivement lus et limites ; correction OCR W16/CP6 relue ; constat concordant avec les contrats relus ici | Lecture supplémentaire des437assertions par ce reviewer, ni preuve distante indépendante du coordinateur |

Ces preuves cumulées sont **suffisantes pour une clôture de conception** : les sources littérales et clauses parentes restent obligatoires, les écarts réellement trouvés ont une résolution explicite, et les nouvelles frontières risquées ont été confrontées à leurs consommateurs. Elles ne constituent pas une certification sémantique produite par les seuls scripts. L'absence de seconde lecture universelle est déclarée, sans transformer cette limite en exigence de refaire indéfiniment les travaux inchangés.

## 3. Contrôles exécutés dans cette revue

| Commande / contrôle | Résultat réel |
|---|---|
| `python canonical-v35/docs/roadmap-v3.5/verify_source_transfer.py --main-root history-work` | exit0 ; `PASS literal 141 criteria / 140 DoD / 26 pins and references. Semantic and product verdicts are separate.` |
| `python canonical-v35/docs/roadmap-v3.5/verify_priority_register.py --pinned --main-root history-work` | exit0 ; inventaires80UX/15groupes/33opportunités/24lots/141critères/140tickets/437scénarios ; message du contrôleur conserve sémantique OPEN et produit non qualifié |
| `python canonical-v35/docs/roadmap-v3.5/verify_run_state.py` | exit0 ; curseur/dépendances/preuves documentaires cohérents, revue sémantique encore pending dans l'état gelé |
| Empreintes de réemploi | Toutes les empreintes listées ci-dessus concordent ; changement du registre limité aux deux métadonnées reconstruites exactement |
| Liens Markdown locaux | 150 cibles uniques de fichiers existantes, zéro absence, avec résolution des sources historiques dans `history-work` ; ce contrôle ne valide ni ancres ni URL externes |

Les mentions OPEN/pending des contrôleurs sont des limites de leur rôle, pas un échec d'exécution ni un verdict humain contraire. Aucun test produit n'a été exécuté ou ajouté : **Windows/UI/NTFS, CPU/GPU réel, Design Space, impression, coupe/montage, benchmark et observation d'accessibilité : NOT_RUN dans cette revue**. Les essais adversariaux des contrôleurs rapportés dans les revues antérieures ne sont pas revendiqués réexécutés ici.

## 4. Matrice des 25 axes

`PASS conception` signifie : obligation conservée, décision/contrat et preuve de revue suffisants pour préparer l'exécution ; aucun PASS produit implicite. Toutes les lignes s'appliquent ; aucun axe supprimé ou classé N/A pour alléger la revue.

| Axe | Preuve et décision | Verdict / limite pratique |
|---:|---|---|
| 01 — 24 lots | Registre pinned, couverture, SC-02A..F2, SC-03B et revues source ; traitement sans réécriture des lots | **PASS conception** ; pas24lots livrés |
| 02 — 141 critères | Registre littéral contrôlé, précisions individuelles revues, SC-03B et complément contextuel ; parents intégraux conservés | **PASS conception** ; pas de conformité déduite des IDs seuls |
| 03 — 140 tickets | Lignes DoD/dépendances/rollback conservées et contrôlées ; liens314 qualifiés comme planification parfois partielle | **PASS conception** ; ni renumérotation ni propriété exclusive inventée |
| 04 — 80 UX | COV18A2C/2D/3A–C, COV18B1–3, clôture D/E et résolutions ; D01/D02/D07/D08/ADR corrigent les anciennes tables | **PASS conception** ; 80 décisions distinctes, pas80boutons ni80fonctions qualifiées |
| 05 — 437 scénarios | SC-02B/C, D/E/F1/F2 et leurs revues, SC-01 six exceptions ; conservation des assertions/oracles et des axes | **PASS conception** ; 431liens source explicites restent431, six propriétaires candidats acceptés sans faux lien historique |
| 06 — maturité/preuves | RUN_STATE, playbook§4, QA§§1–2 et revues ; DOCUMENTED/REVIEWED distincts CODE_MAIN et axes réels | **PASS conception** ; aucune validation GitHub APPROVED ni qualification externe fabriquée |
| 07 — projet unique | ADR§§1–4, Q04§§3–4, SC-02A/F2, résolution D/E correction6 ; V1 CAS confirmé dans code, CP2 requis pour receipt durable | **PASS conception** ; CP0–6 futurs, un writer par format actif, source/float32/IDs préservés |
| 08 — quatre exports | Lot17§2, ADR§5, SD§2 et C10 ; trois usages Artifact V1 confirmés, multicouche externe distinct | **PASS conception** ; PNG PTC/Basic Cut/CUT multicouche/édition ne sont pas alias |
| 09 — opérations/machine | D02, COV18B, QA DS/physique, guide SD§3 ; capacités tri-state, inventaire matériel séparé | **PASS conception** ; aucune commande machine inventée, contexte/profil à requalifier avant revendication |
| 10 — Express-first | UX huit flux, MASTER rangs1–5 et playbook ; même moteur/session, divulgation progressive, erreurs corrigibles | **PASS conception** ; métriques/observations novice et expert NOT_RUN |
| 11 — canevas/gestes | COV18A, ADR matrices/locks/commandes, D01/D02 ; clic/lasso/pinceau, poignées, clavier, preview et Undo distincts | **PASS conception** ; outils futurs ne sont pas attestés disponibles dans Tk |
| 12 — accessibilité | D08, résolution E10, SC-03B et parent§40 ; petits écrans, 100/125/150/200%, lecteur écran et alternative au drag | **PASS conception** ; vrai parcours Windows/accessibilité à qualifier ; framework incapable reste non qualifié |
| 13 — annulation/reprise | ADR§§3–4/7, D03/D04, SD§4, parent lot06 ; stale, fermeture, crash, CAS, issue UNKNOWN, rollback et reprise ciblée | **PASS conception** ; Undo ne retire ni export ni coupe ; M03 éditorial ci-dessous |
| 14 — IA facultative | D06, résolution D01–12, SC-02B/C ; CPU/manuel, source fiable/licence/version/hash, download/exécution/transfert séparés | **PASS conception** ; hash≠signature, OOM et provenance à éprouver, aucun modèle admis par ce rapport |
| 15 — raster | SC-02C lot12, résolution E15 et QA E2E01 ; alpha/ICC/EXIF/DPI/mm, anti-halo et texture≠CUT, upscale conditionnel | **PASS conception** ; hausse DPI/interpolation n'est pas détail natif acquis |
| 16 — vecteur | COV18A/B, SC-02D lot13 et D01/D02 ; trous/Bézier/mm/XML inerte, optimisation non destructive, changement topologique voulu explicite | **PASS conception** ; budget logiciel5000 injecté≠limite machine, géométrie locale≠coupon |
| 17 — Fabrique/séries/bibliothèque | Q04G/ADR CP6, D03–D05, SC-02E, source G6/G7 ; trois usages, quatre plans, 12/24/50 et CSV avec reprise | **PASS conception** ; index jetable≠tags durables, portabilité demeure due,50placements≠50sujets persistés |
| 18 — Smart Delivery | Contrat SD0–3 relu, quotas, typage4, SHA/readback/no-clobber, privacy et HTML inerte ; code historique JSON confirmé | **PASS conception** ; premier ZIP dès UN export sain, indépendant CP2/V2 et achèvement4exports ; pack atomique, batch PARTIAL honnête |
| 19 — autres évolutions | Résolution des33opportunités/15groupes + revue inchangée ; Advisor/Weeding/PTC/Cost/Feedback/CSV/QR/recettes/profils/optimiseur décidés | **PASS conception** ; huit rejets maintenus ; extensions de recherche ne remplacent pas les obligations héritées |
| 20 — métriques | SC-03B, parent§40, D08 et QA ; p50/p90/max historiques conservés, p95/RSS/VRAM ajoutés, protocoles/corpus/environnement | **PASS conception** ; objectifs et futurs benchmarks, aucun chiffre présenté comme observé |
| 21 — sécurité publique | SD§§1–4, ADR fontes/OCR, D06, résolution E19 ; droits image/police/modèle, copies expurgées, secrets/chemins/médias privés exclus | **PASS conception** ; pas d'audit runtime universel ni revalidation externe des licences par cette revue |
| 22 — gouvernance/WIP | AGENTS/main consulté localement, playbook§5, checklist ; producteur existant distinct et opt-in V34 non transféré automatiquement | **PASS conception** ; quatre PR code DRAFT signalées par coordinateur, G35-12 reste en attente de WIP admissible |
| 23 — anti-doublons | MASTER§§2/7, ADR§1, SD§5, D05 ; réemploi writer/bus/canevas/exporteurs ; préférences bornées hors composition | **PASS conception** ; CP/SD sont tranches, pas tickets/moteurs créés automatiquement |
| 24 — revue/adoption | Présent rapport indépendant, revues cumulées, séquence checklist/playbook et contrôleurs frais | **PASS conception** ; CI PR exact-head, approbation applicable, fusion docs puis gouvernance et handoff restent à faire |
| 25 — optimisation | Réemploi par empreintes vérifiées, corrections explicites et lectures ciblées parentes ; aucun axe effacé | **PASS conception** ; gains de lecture ne valent ni omission des critères ni faux résultat produit |

## 5. Gates séparés G35-01..11 et15

| Gate | Décision finale au SHA figé | Justification et frontière |
|---|---|---|
| G35-01 —24lots | **PASS documentaire** | Couverture/registre et SC-02, parents conservés ; inventaire complété par décisions et revues, pas seul compteur |
| G35-02 —141exigences | **PASS documentaire** | Transfert littéral vérifié, revue individuelle des précisions et complément contextuel ; critères parents intégraux contraignants |
| G35-03 —140tickets | **PASS documentaire** | DoD complets vérifiés et revue reçue ; coordination héritée ne devient pas propriétaire exclusif, aucun ticket renuméroté |
| G35-04 —80UX | **PASS documentaire** | Décisions A/B/C + D/E, corrections ADR/D01–D08 et recettes par parcours ; aucune restriction artificielle à80menus |
| G35-05 —437scénarios | **PASS documentaire** | Revues cumulées des assertions/oracles et source closure ; six absences historiques maintenues avec responsabilité candidate acceptée |
| G35-06 —G6/G9 | **PASS documentaire** | W10 texte/W11 gabarits/W16 OCR-diorama, CP4/CP6 gates distincts ; éditabilité/prototypes par usage/quatre plans non réduits |
| G35-07 —33opportunités | **PASS documentaire** | Résolution et revue indépendante byte-identiques ; huit rejets/15groupes conservés avec priorités/dépendances et coûts qualitatifs |
| G35-08 —architecture | **PASS documentaire** | V1/CAS/float32≠receipt ; migration V2 sur copie CP0–6, quatre sorties, fichier/ZIP atomiques vs batch PARTIAL ; SD précoce indépendant |
| G35-09 —parcours/a11y | **PASS documentaire** | Huit flux et cinq familles critiques, novice/expert/erreurs/Undo/reprise, écran/DPI/lecteur écran ; benchmark W13 futur avant gros éditeur |
| G35-10 —qualité/risques | **PASS documentaire** | Oracles positifs/négatifs/crash/concurrence/reprise et axes de preuve distincts ; seuils historiques préservés, qualifications futures NOT_RUN |
| G35-11 —revue indépendante | **PASS documentaire** | Présente revue transversale avec défauts/limites, lectures parentes/consommateurs et réemploi tracé ; aucun Critical/Important non arbitré détecté |
| G35-15 —source/sécurité | **PASS documentaire dans le diff examiné** | Publication limitée docsV3.5 attestée par coordinateur,26pins+lot22 identiques, clauses de droits/privacy/sécurité relues ; AGENTS/code/workflows/archives/baseline non modifiés par cette revue ni le diff signalé |

**G35-12 reste PENDING** : aucune PR docs intégrée, aucun CI exact-head de cette PR ni approbation propriétaire GitHub n'est attesté ici. Le WIP code courant doit être traité conformément aux règles existantes avant ouverture permise d'une nouvelle PR docs ; la revue de conception peut être close pendant cette attente. **G35-13 et G35-14 restent PENDING** : changement séparé d'autorité puis passation du producteur existant ; aucune fusion horaire automatique ni transfert d'opt-in par renommage.

## 6. Constats et correctifs bornés

**Critical : aucun. Important : aucun.** Les trois constats suivants sont Minor, confiance élevée ; ils concernent des résumés anciens dans les entrées opérationnelles. La hiérarchie de lecture et les décisions postérieures les résolvent déjà, ce qui évite d'en faire un NO-GO architectural. Une harmonisation courte est utile avant le handoff ; ne pas réécrire les sources ni rouvrir les dossiers clos.

| ID / sévérité | Fichier et ligne du SHA figé | Effet concret / plus petit correctif |
|---|---|---|
| M01 —Minor | `MASTER_PRIORISE.md:40` et `BACKLOG_AND_DEPENDENCIES.md:31` | « persistance à décider » / « pas TextNode approuvé » peut relancer une ADR déjà rendue ou mélanger candidate et code existant. Remplacer par renvoi à l'ADR CP0–6 : cible décidée dans la conception, implementation et adoption non acquises ; V1 strokes inchangé. Le bandeau/ADR/playbook empêchent actuellement une contradiction normative. |
| M02 —Minor | `MASTER_PRIORISE.md:42` | « lot50partitionné si moteur32 » est trop court pour distinguer calcul/placements externes et50sujets persistés. Ajouter cette distinction et renvoyer aux packs internes d'un seul projet V2/SC-01/Q04. D03, ADR§4 et SC-02F2 contiennent déjà la règle complète. |
| M03 —Minor | `QUALITY_TESTS_AND_EVIDENCE.md:54`, `:55` et `:68` | E2E04 juxtapose positif V1 et négatifs command_id/replay sans CP2 dans la même ligne ; « dernier projet sain intact » peut se lire comme absence de publication après toute erreur. Ajouter sous-gates V1 versus receipt CP2/V2 et cas primary publié+backup échoué : inspecter primary/receipt/pending, COMMITTED_NEEDS_RECOVERY ou UNKNOWN, aucun retry aveugle. Résolution D/E correction6, lot06, ADR et SC-03B tranchent déjà ce point. |

Ces corrections éditoriales, si publiées après ce rapport, demanderont contrôle du delta et des liens/contrôleurs concernés ; elles ne sont pas réputées appartenir au SHA figé. Aucun correctif n'a été appliqué par le reviewer.

## 7. Comportements examinés mais non jugés ici — declined to judge

| Objet | Motif et conséquence |
|---|---|
| Logiciel Windows réellement utilisable, boutons natifs, exactitude runtime de tous les moteurs | Revue de conception ; lecture de ports discriminants seulement, aucun test produit. CODE_MAIN/WINDOWS_EXPOSED/PASS non attribués. |
| Atomicité Windows/NTFS, GPU/RTX, mesures de qualité/performance, lecteur écran réel | Protocoles et refus attendus examinés ; leur réussite dépend d'exécutions futures sur environnements réels, NOT_RUN. |
| Design Space actuel, capacités matérielles actuelles, coupe/pliage/montage quatre plans | Pas de revalidation externe fabricant ni essai humain ; profils versionnés/UNKNOWN et gates physiques restent obligatoires. |
| Licences actuelles de chaque police/modèle, provenance de tous fichiers futurs | Contrats d'admission/privacy jugés ; droits de révisions réelles à vérifier avant usage/redistribution. Hash seul ne prouve pas l'auteur. |
| Exhaustivité runtime sécurité/secrets de tout le dépôt historique | Diff limité docs et pins/source examinés ; aucune revendication de scan universel. Les données privées/poids/médias non autorisés restent interdits. |
| CI, protection GitHub, approbation propriétaire, résolution des quatre PR code DRAFT | ÉtapeG35-12 distincte, à revalider au HEAD exact ; pas de GitHub APPROVED inventé ni merge effectué. |
| AutoritéV3.5 et prompt de développement modifié | ÉtapesG35-13/14 explicitement hors tâche ; opt-in V34 non transmis automatiquement, V3.4 demeure active. |

La prochaine action de fond est **PROMOTION_DOCS sous ses conditions réelles de WIP/CI/revue**, après enregistrement de ce verdict et contrôle du petit delta éditorial éventuel. L'absence de produit futur n'est pas un défaut de cette conception ; une revendication de livraison ultérieure exigera ses preuves propres.
