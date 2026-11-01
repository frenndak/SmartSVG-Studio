# SmartSVG Studio V3.4 — Lot 14 : langage sémantique de fabrication, opérations et prévol

**DRAFT DE SPÉCIFICATION — 29 octobre 2026.** Références : issue [#72](https://github.com/frenndak/SmartSVG-Studio/issues/72), [PR #73](https://github.com/frenndak/SmartSVG-Studio/pull/73), branche `codex/docs-roadmap-v3-4-campaign`, HEAD d'entrée `528ab0197ddcc1d3defe056d363641ffebcca6cc`, `main@fdbda304beb77d97340a8be4dd5c5e9cefde15f4`. La **V3.3 reste ACTIVE**. **Tout schéma, exemple, algorithme, ticket et test ci-dessous est une proposition NON IMPLÉMENTÉE et NON EXÉCUTÉE.** Les quatre axes de preuve (auto/Windows/Design Space/physique) restent `NON_EXECUTE`.

## 1. Problème, périmètre, état existant et contrats de vérité

**Problème :** un trait SVG ne dit pas s'il faut le découper, le rainurer, le dessiner au stylo, appliquer du foil, ou simplement l'imprimer. Les attributs `stroke`, `fill`, la couleur et le nom de calque ne sont pas des ordres machine. Une boîte requiert au minimum une géométrie de découpe et des lignes de pli distinctes, associées au bon support ; l'Explore 5 exige ensuite de sélectionner les opérations **dans Design Space**, de réaliser **Attacher**, de choisir le matériau et de suivre les changements d'outil. Un dessin complexe peut nécessiter un SVG éditable sans aucune opération de coupe.

**État effectivement lu dans le code de `main` :** `engine/smartsvg_governance/cut_path_preflight.py` réalise un prévol **statique de SVG Basic Cut**, pas un moteur multi-opérations ; `engine/smartsvg_cricut/direct_import_v218.py` prépare un transfert local **Print Then Cut** et ses contrôles, pas une configuration automatique de Design Space ; `engine/smartsvg_core/project_contracts.py` distingue les preuves d'import et de coupe réelle. Les modules de revue SVG du lot 13 inspectent des chemins et leurs rôles ; ils ne produisent pas de commande machine. **Il n'existe pas de FabricationPort V3.4 opérationnel prouvé.**

**Périmètre de ce lot :** modèle `Path → Operation → Tool → Material → Machine`, validation sémantique, conflits, prévol déterministe, présentation novice/expert, transfert guidé non automatisé, deux vertical slices et tests. Le lot 15 qualifiera les profils matériels, 16 la géométrie paramétrique, 17 les artefacts d'export et 18 l'éditeur. **Hors périmètre :** pilote USB/Bluetooth, API privée Design Space, réglages physiques pression/vitesse non mesurés, certification matière, pilotage d'outil, intégration machine réelle.

**Vérités invariantes :**
1. `GUIDE_ONLY` et `OPERATION_PENDING` ne deviennent jamais `CUT` par défaut ; `SCORE` n'est pas un style SVG.
2. Une géométrie est en **mm explicites** dans le projet, avec ID et digest ; aucune taille cachée n'est inférée depuis une photo ou un DPI absent.
3. `PRINT` décrit une image/région raster à imprimer. `PRINT_THEN_CUT` est une **recette composite** `PRINT + CUT` et un contrat d'export PNG, **pas** une opération de trajectoire autonome.
4. L'assignation sémantique n'est **pas transférée automatiquement** par un SVG importé. Le guide Design Space reste obligatoire pour Score/Draw/Foil/Attacher.
5. La compatibilité est un verdict **versionné par combinaison** machine × outil × matière × support × opération, jamais une extrapolation de famille. Une documentation officielle peut attester la compatibilité générale d'un outil, pas un réglage validé pour un papier précis.
6. Un `preflight=PASS` ne signifie ni `DesignSpace=PASS` ni `physical=PASS`. Les quatre sorties historiques restent séparées.
7. `.smartsvg` demeure l'autorité ; un export n'est qu'un artefact externe, non réversible par Undo. V2 est futur et conditionné au writer/migrateur qualifié ; V1 ne reçoit aucun champ nouveau en douce.
8. L'IA peut proposer une intention, **jamais** affecter une opération à un chemin sans revue et confirmation déterministe ; CPU/manuel fonctionnent sans modèle.

## 2. Contre-expertise du lot 13 et ADR-034-17 (PROPOSÉE)

**C14-01 — Rôle de contour ≠ opération.** Le lot 13 introduit `OUTER|HOLE|OPEN_GUIDE` et `CUT_CANDIDATE`. Un `HOLE` fermé est une propriété topologique ; il n'est pas automatiquement une coupe intérieure. Une `OPEN_GUIDE` peut devenir Score/Draw/Foil **sur action explicite**, sinon reste un guide. Le `CUT_CANDIDATE` ne vaut pas `CUT` accepté.

**C14-02 — Contrat historique des opérations.** Les lots 03/09 citent `CUT|SCORE|DRAW|PRINT|FOIL` et parfois `PRINT_THEN_CUT`. **ADR-034-17 :** conserver les cinq valeurs sémantiques `CUT|SCORE|DRAW|PRINT|FOIL` ; placer `PRINT_THEN_CUT` dans `production_intent`/`output_contract`, avec traduction explicite des anciennes propositions (jamais une migration implicite de fichiers existants). L'enveloppe **unique** des commandes est `smartsvg-command/1-draft` du lot 06 ; les exemples `v34.command/0.1/0.2-draft` des lots 03/04 sont des brouillons historiques à réconcilier au lot 23, pas de nouveaux protocoles.

**C14-03 — Limite d'import SVG.** Les 5 000 chemins officiellement mentionnés pour Design Space constituent un **plafond d'import**, pas une promesse de performance ni une autorisation de 5 000 coupes sûres. Les tracés de dessin et de foil peuvent eux aussi compter dans le budget après expansion. Le prévol doit compter les chemins réellement exportés par projection, et vérifier trous, doubles lignes, micro-îlots et recouvrements.

**C14-04 — Fabricabilité.** Une ligne de pli traversant un contour de coupe ou une région imprimée n'est pas nécessairement incorrecte ; seul un conflit métier ou géométrique contextualisé peut bloquer. Les collisions doivent être classées : exactes/duplicatas, croisements, recouvrements tolérés, extrémités proches, multi-opérations sur le même chemin. La décision est **par groupe d'opération et support**, pas un rejet global de tout croisement.

**Alternatives comparées :** (A) encoder les opérations par couleur SVG — REJET (ambigu, fragile à l'import) ; (B) générer un SVG par outil sans modèle canonique — REJET (perte d'identité, d'alignement et d'Undo) ; (C) graphe sémantique canonique + projections par opération + guide Design Space — **RECOMMANDÉ SOUS RÉSERVE DE PROTOTYPE**. Ne pas multiplier les stores ou les writers.

**Dépendances bloquantes :** V34-017/021 bootstrap, V34-025..031 format V2, V34-032..040 commandes/CAS, V34-096..101 vectoriel, V34-012..014 ports. Les profils détaillés et leur versionnement sont au lot 15 ; un profil `UNKNOWN` n'est pas transformé en `SUPPORTED` pour satisfaire un test.

## 3. Parcours novice/expert, wireframes textuels et erreurs

### 3.1 Novice — « boîte carton avec plis »
```text
[Fabrique ▸ Projet : boîte 80 × 50 × 30 mm]    [Projet sauvegardé / brouillon]
[Support : carton déclaré] [Machine : Explore 5] [Outils : lame ✓ | Score ?]
[APERÇU]  contour = CUT (rouge + libellé) | plis = SCORE (bleu pointillé + libellé)
[3 lignes de pli : SCORE proposé, non confirmé] [Confirmer les opérations]
[Prévol : 1 avertissement — outil Score non déclaré] [Choisir outil / Continuer en brouillon]
[Préparer l'export] [Guide Design Space : Importer → Score → Attacher → Vérifier → Faire]
[État final : fichiers exportés ; import et coupe non vérifiés]
```
Le novice ne voit pas un faux bouton « Envoyer à la Cricut ». Si l'outil Score est absent, proposer « Garder le pli comme guide » ou « Reporter la fabrication », **jamais** remplacer silencieusement Score par Cut. Une cote manquante ouvre **une** question ciblée, non un dialogue imposé.

### 3.2 Expert — inspecteur de fabrication
```text
[Projet SHA | révision | matrice capacités @version] [Mode lecture seule si V1 incompatible]
[Arbre objets] id | geometry_digest | rôle | operation | outil | support | matière
[Canevas mm] [Calques CUT/SCORE/DRAW/FOIL/PRINT/GUIDE] [Motif + texte, pas couleur seule]
[Prévol] bloqueurs | avertissements | inconnues | chemins sélectionnables
[Diff opérations avant/après] [Undo] [Recalculer] [Export DRAFT]
[Transfert] checklist Attacher | sélection d'opérations DS | outil | matériau | preuve
```

**États UI :** `EMPTY`, `INTENT_PENDING`, `ASSIGNMENT_PROPOSED`, `REVIEW_REQUIRED`, `PREFLIGHT_BLOCKED`, `PREFLIGHT_WARN`, `PREFLIGHT_PASS_STATIC`, `EXPORTED_UNVERIFIED`, `DS_IMPORTED_UNVERIFIED`, `PHYSICAL_VERIFIED` (dernier uniquement sur preuve explicite). Toute action dangereuse est accessible au clavier, les statuts et motifs ne dépendent pas de la couleur ; Undo ne supprime pas les fichiers déjà exportés. `STALE_PROJECT_SHA` exige relecture du snapshot et nouveau prévol, pas réemploi silencieux.

### 3.3 Cas particuliers et fallback
- **Aucun outil/matière déclaré :** `UNKNOWN` + mode brouillon ; aucune recommandation de réglage de pression.
- **Machine Explore 5 + gravure/débossage/QuickSwap Maker-only :** `KNOWN_UNSUPPORTED` pour les opérations hors catalogue validé, pas de fallback automatique vers une autre opération.
- **Ligne Score non attachée :** avertissement de transfert et guide obligatoire ; le SVG seul n'enregistre pas « Attacher ».
- **Panne CPU/OOM de l'analyse IA :** édition/assignation manuelle reste disponible ; aucune proposition partielle committée.
- **Fichier externe changé, ZIP futur ou preuve obsolète :** refuser publication ou lecture seule selon le contrat V2 ; conserver l'original.
- **Support Smart Material, tapis carte, HTV miroir, foil :** ne pas deviner compatibilité à partir du nom ; `UNKNOWN` tant que la combinaison précise n'est pas documentée au lot 15.
- **Impression A4 :** zone Print Then Cut non rectangulaire ; vérifier dans Design Space avec machine, papier et orientation réels, sans fabriquer de repères de capteur externes.

## 4. Modèle de données et interfaces — SPÉCIFICATION

**Entités futures (non implémentées) :**
- `FabricationPlan`: `schema`, `project_sha256`, `logical_revision`, `source_digest`, `machine_profile_ref`, `material_profile_ref`, `support_ref`, `assignments[]`, `groups[]`, `intent`, `preflight`, `proof_axes`, `provenance`.
- `GeometryRef`: `object_id`, `contour_id?`, `geometry_digest`, `geometry_kind=PATH|RASTER_REGION`, `units=mm`, `closed`, `bbox_mm`, `source_revision`.
- `OperationAssignment`: `assignment_id`, `geometry_ref`, `operation_kind=CUT|SCORE|DRAW|FOIL|PRINT`, `operation_variant` (ex. `BASIC`, `PEN`, `FOIL_TRANSFER`, `RASTER`), `tool_profile_ref?`, `material_profile_ref`, `machine_profile_ref`, `support_ref`, `group_id`, `review_state`, `origin=USER|RULE_PROPOSAL|AI_PROPOSAL`, `confirmed_by_user`.
- `OperationGroup`: `group_id`, `relative_transform_mm`, `attachment_intent=REQUIRES_ATTACH|KEEP_RELATIVE|NONE`, `shared_support_ref`, `assignment_ids[]`. `attachment_intent` est un **rappel**, jamais une commande Design Space transmise.
- `CapabilityVerdict`: `state=KNOWN_SUPPORTED|KNOWN_UNSUPPORTED|UNKNOWN`, `scope`, `source_url`, `source_checked_at`, `profile_version`, `conditions[]`, `confidence_basis=OFFICIAL_DOC|LOCAL_TEST|USER_DECLARED`. Une déclaration utilisateur seule ne vaut pas qualification.
- `PreflightFinding`: `code`, `severity=BLOCKER|WARNING|INFO`, `geometry_ids[]`, `operation_ids[]`, `machine_scope`, `explanation_fr`, `repair_action?`, `rule_version`, `evidence_ref?`.
- `HandoffManifest`: `export_sha256`, `source_project_sha256`, `operation_groups`, `design_space_steps[]`, `external_validation_state`, `unverified_assumptions[]`. Ne contient aucun jeton ni chemin personnel public.

**Contraintes structurelles :** IDs uniques et non recyclés, références résolues, SHA-256 hex de 64 caractères, `logical_revision ≥ 0`, mm positifs/finis, transformations inversibles ou rejetées, ordre des points explicite, quotas de chemins et octets versionnés, aucune référence hors projet autorisée, `PRINT` seulement sur `RASTER_REGION`, `SCORE/DRAW/FOIL` seulement sur géométrie de trait approuvée, `CUT` seulement sur géométrie de coupe qualifiée topologiquement ; une ligne ouverte n'est pas automatiquement rejetée pour DRAW/SCORE/FOIL mais n'est jamais une découpe fermée sûre par défaut.

**Exemple JSON de référence : boîte 2D fictive (NON EXÉCUTÉ ; géométrie réelle à produire au lot 16).**
```json
{
  "schema": "smartsvg-fabrication-plan/1-draft",
  "project_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "logical_revision": 7,
  "source_digest": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "intent": "BOX_SCORE_CUT",
  "units": "mm",
  "machine_profile_ref": "cricut-explore-5@draft",
  "material_profile_ref": "cardstock-unknown@draft",
  "support_ref": "mat-12x12-declared-unverified",
  "assignments": [
    {
      "assignment_id": "op-cut-01",
      "geometry_ref": {"object_id":"box-flat-01","contour_id":"outer-01",
        "geometry_digest":"cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
        "geometry_kind":"PATH","units":"mm","closed":true,
        "bbox_mm":[0,0,140,100],"source_revision":"vec-r3"},
      "operation_kind":"CUT","operation_variant":"BASIC",
      "tool_profile_ref":"fine-point-declared-unverified",
      "material_profile_ref":"cardstock-unknown@draft",
      "machine_profile_ref":"cricut-explore-5@draft",
      "support_ref":"mat-12x12-declared-unverified",
      "group_id":"box-01","review_state":"ACCEPTED",
      "origin":"USER","confirmed_by_user":true
    },
    {
      "assignment_id":"op-score-01",
      "geometry_ref":{"object_id":"box-flat-01","contour_id":"fold-01",
        "geometry_digest":"dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
        "geometry_kind":"PATH","units":"mm","closed":false,
        "bbox_mm":[50,0,50,100],"source_revision":"vec-r3"},
      "operation_kind":"SCORE","operation_variant":"LINE",
      "tool_profile_ref":"explore5-scoring-tool-unconfirmed",
      "material_profile_ref":"cardstock-unknown@draft",
      "machine_profile_ref":"cricut-explore-5@draft",
      "support_ref":"mat-12x12-declared-unverified",
      "group_id":"box-01","review_state":"PROPOSED",
      "origin":"RULE_PROPOSAL","confirmed_by_user":false
    }
  ],
  "groups":[{"group_id":"box-01","assignment_ids":["op-cut-01","op-score-01"],
    "attachment_intent":"REQUIRES_ATTACH","shared_support_ref":"mat-12x12-declared-unverified",
    "relative_transform_mm":[1,0,0,1,0,0]}],
  "preflight":{"state":"WARN","findings":["TOOL_UNCONFIRMED","OPERATION_NOT_ACCEPTED"],
    "rule_version":"fabrication-preflight/1-draft"},
  "proof_axes":{"auto":"NON_EXECUTE","windows":"NON_EXECUTE",
    "design_space":"NON_EXECUTE","physical":"NON_EXECUTE"}
}
```

**Interfaces futures** (noms pressentis, **fichiers inexistants**) :
`FabricationPort.plan(snapshot,operation_intent)->FabricationProposal` ;
`OperationAssignmentPort.validate_and_stage(snapshot,assignments)->CandidateDiff` ;
`CapabilityPort.resolve(machine,tool,material,support,operation,version)->CapabilityVerdict` ;
`GeometryPort.inspect(path_refs,context)->GeometryFindings` ;
`PreflightPort.evaluate(snapshot,assignments,capabilities,export_contract)->PreflightReport` ;
`ExportPort.stage(plan,format)->ArtifactProposal` ;
`ProjectCommandPort.commit(accepted_diff,expected_project_sha256,command_id)->Receipt`.
Les UI/assistant ne parlent qu'aux ports, jamais directement aux writers ou aux modèles IA.

**Commandes via le bus du lot 06 :** `AssignOperation`, `SetFabricationProfile`, `ConfirmIntent`, `Undo`, `Redo` (mutantes après confirmation et CAS) ; `InspectFabrication`, `PreviewOperationPlan`, `ValidatePreflight`, `PrepareHandoff` (lectures ou calculs de proposition). Événements proposés : `fabrication.proposed`, `fabrication.assignment_review_required`, `fabrication.committed`, `fabrication.preflight_completed`, `fabrication.handoff_staged`, `fabrication.stale`. `command_id`/epoch/digest du lot 06 assurent l'idempotence ; aucune seconde enveloppe créée.

## 5. Prévol déterministe, collisions, IA facultative et performance

**Pseudo-algorithme de SPÉCIFICATION — NON EXÉCUTÉ :**
```text
function preflight(snapshot, proposed_assignments, profile_refs, export_contract):
    require snapshot.sha == expected_project_sha256
    assert no duplicate IDs and all geometry digests resolve at snapshot revision
    reject NaN/Inf, invalid mm, unsupported archive schema, unbounded payload
    for each assignment:
        check geometry kind vs operation; reject PRINT on PATH and SCORE on RASTER
        check explicit user acceptance; otherwise REVIEW_REQUIRED
        resolve machine/tool/material/support/operation profile -> SUPPORTED/UNSUPPORTED/UNKNOWN
        UNSUPPORTED => BLOCKER; UNKNOWN => WARNING and never machine-ready
        inspect topology, minimum feature sizes as warnings until material calibration exists
    detect exact duplicate paths and overlapping CUT on same support -> BLOCKER or explicit repair
    detect near-overlaps/crossings -> REVIEW_REQUIRED with object-specific explanation
    verify each group references one coherent support and stable relative mm transform
    if group contains SCORE/DRAW/FOIL + CUT: require handoff step "Select Operation + Attach"
    if PRINT_THEN_CUT intent: require raster+cut association, A4/Letter selected,
        known or UNKNOWN versioned cuttable region; never assume full page is usable
    count paths after projection and report 5000-path import ceiling separately from performance
    return immutable findings, deterministic digest, state PASS/WARN/BLOCKED
```

**Priorités des findings :** `BLOCKER` pour références cassées, géométrie non finie, rôle de coupe impossible, double coupe exacte non résolue, opération officiellement non supportée, profil contradictoire ; `WARNING` pour matériel non déclaré, taille fine non qualifiée, besoin de test coupon, orientation A4 non mesurée, guide Attacher non confirmé ; `INFO` pour instruction de changement d'outil ou suggestion de prévisualisation. `WARN` n'autorise qu'un **export brouillon explicitement non qualifié**. Une erreur bloquante interdit « prêt à fabriquer » et export final de fabrication ; le projet reste éditable.

**Conflits à distinguer :** duplication `CUT/CUT` sur même géométrie, `SCORE/CUT` identiques, chemins de `DRAW` en dehors du support, foil dans une zone de ruban de fixation, plusieurs opérations sur même tracé, supports différents mais groupe commun, chemin ouvert, trou intérieur, îlot fragile, chevauchement voulu pour un montage. Les seuils de distance sont des **paramètres de recette à calibrer**, pas des tolérances universelles.

**Performance à mesurer (objectifs de conception, non benchmarks) :** prévol incrémental sur 50 objets sans revectoriser ; 100 commandes d'assignation puis Undo/Redo sans perte ; invalidation par digest de géométrie, profil et support ; UI sans blocage perceptible sur corpus 12/24/50 ; journal sans médias privés ; calcul CPU déterministe avec version de règle et hash de résultat. Aucun chiffre p95 n'est annoncé comme atteint. Le GPU n'est pas nécessaire au prévol.

**IA facultative :** un modèle local peut proposer `BOX_SCORE_CUT` ou suggérer des plis ; il ne choisit ni épaisseur ni réglage cachés. Toute proposition passe par le catalogue fermé du lot 09, les contrôles du lot 11 et une confirmation explicite. Sans IA : formulaire dimensions, choix d'opérations, prévol et export fonctionnent.

## 6. Deux vertical slices de référence et cas supplémentaires

### A — 12 escargots → stickers
1. Import PNG/JPEG autorisé, original + SHA immuables ; analyse 12 sujets (manuel/CPU ou IA opt-in), IDs stables, masques revus.
2. Taille physique **saisie**, composition planche, PNG Print Then Cut avec alpha/rendu distinct du contour de coupe ; `production_intent=STICKERS_PRINT_THEN_CUT`.
3. `PRINT` sur les pixels ; `CUT` sur les contours acceptés **dans le modèle logique** ; ne pas exporter ces deux rôles comme deux SVG qui seraient automatiquement « Print Then Cut ».
4. Prévol : A4/Letter et orientation, zone de coupe non rectangulaire dépendante de Design Space, collisions/îlots, calibration requise ; pas de repères de capteur inventés.
5. Export PNG + manifeste + guide d'import, sélection de Print Then Cut dans Design Space, confirmation de dimensions et aperçu ; états `EXPORTED_UNVERIFIED` puis preuve externe distincte. **Aucun upload/pilotage automatique**.

### B — boîte carton 80 × 50 × 30 mm → Score + Basic Cut
1. Saisie explicite de dimensions, épaisseur si utile, type de boîte et matière ; si parametric engine du lot 16 absent : `TEMPLATE_NOT_IMPLEMENTED`, pas de faux développé.
2. Génération future d'un patron 2D : chemins fermés de coupe, lignes ouvertes de pli, IDs et digests distincts ; revue des languettes et tolérances.
3. `AssignOperation(CUT)` puis `AssignOperation(SCORE)` avec confirmation ; outil Score Explore 5 et tapis déclarés, profils conditionnels.
4. Prévol : contours fermés, pli distinct, aucune double coupe, placement sur support, groupe d'alignement ; `UNKNOWN` si matériau/outil non qualifié.
5. Export SVG(s) géométriques et **guide explicite** : importer dans Design Space, identifier les plis, régler leur opération sur **Score**, sélectionner les plis + la découpe, **Attacher**, vérifier le tapis et les dimensions, choisir matériau et suivre les demandes de changement d'outil. Un SVG ne transporte pas une instruction Score garantie.
6. Le retour d'expérience réel (import/pli/découpe/mesures) est un **axe de preuve séparé**, non produit par le prévol.

### C — cas de recette complémentaires
- **Pen + Cut :** un trait de dessin reste `DRAW` et non `CUT` ; outil de stylo déclaré, guide Attacher ; le stylo doit être compatible Explore 5, pas supposé à partir de sa couleur.
- **Foil + Cut :** `FOIL` nécessite outil de transfert, feuilles, matière et espace de fixation ; guider la préparation et les changements d'outil ; ne pas garantir un support non testé.
- **HTV/vinyle multicouche :** le miroir est une intention explicite et vérifiée par couche ; aucune inversion automatique à partir de la simple présence de vinyle.
- **Smart Material sans tapis / tapis carte :** profil combiné obligatoire, ne pas inférer que toute matière peut être utilisée sans tapis.
- **Pochoir fragile :** micro-ponts et îlots examinés ; géométrie valide ≠ solidité physique.
- **Line-art depuis dessin couleur :** `DRAW` proposé après revue de traits ; ne pas transformer les aplats de couleur en trajectoires de stylo sans choix.
- **Absence d'IA, OOM, source modifiée :** formulaire/CPU, aucune proposition partielle publiée, recalcul CAS.

## 7. Corpus, tests d'acceptation proposés — TOUS NON_EXECUTE

**Fixtures futures autorisées :** `tests/fixtures/v34_fabrication/{box_score_cut_synthetic,12_snails_synthetic,pen_cut,foil_cut,print_then_cut_a4,duplicate_cut,overlap_score_cut,unsupported_engrave,unknown_profile,missing_tool,smart_material_no_mat,card_mat,htv_mirror,fragile_stencil,50_objects,stale_revision,corrupt_archive,malicious_svg}`. Toutes synthétiques, sans Pokémon ni œuvres personnelles ; créer en PR de code ultérieure. Pour chaque test : SHA du code, version de règles, fixture SHA, environnement, assertion, axe auto/Windows/Design Space/physique indépendant.

| Test | Assertion exacte à implémenter | Axe futur |
|---|---|---|
| T-V34-14-01 | GUIDE_ONLY et CUT_CANDIDATE ne créent aucune assignation CUT sans confirmation | auto |
| T-V34-14-02 | SCORE ouvert accepté comme candidat ; CUT ouvert non sûr bloque la fabrication | auto |
| T-V34-14-03 | IDs, digest, unités mm et références invalides provoquent un refus non mutant | auto |
| T-V34-14-04 | PRINT sur PATH et SCORE sur RASTER_REGION refusés | auto |
| T-V34-14-05 | PRINT_THEN_CUT est recette composite ; ne devient pas une opération de PATH | auto |
| T-V34-14-06 | Compatibilité KNOWN_UNSUPPORTED bloque, UNKNOWN avertit sans promotion | auto |
| T-V34-14-07 | Source officielle datée et version du profil exigées pour KNOWN_SUPPORTED | auto |
| T-V34-14-08 | Une double coupe exacte CUT/CUT sur même support est détectée et localisée | auto |
| T-V34-14-09 | Croisement SCORE/CUT légitime est différencié d'une duplication exacte | auto |
| T-V34-14-10 | Score + Cut sans groupe d'alignement donne avertissement Attacher | auto/UI |
| T-V34-14-11 | Un groupe avec supports différents est refusé sans fusion implicite | auto |
| T-V34-14-12 | Projet boîte : deux types d'opérations et géométries distincts préservés | auto |
| T-V34-14-13 | Le guide d'export boîte inclut Score, Attacher, outil, matériau et contrôle mm | auto/UI |
| T-V34-14-14 | Import réel Design Space : Score choisi et Attach vérifié manuellement | Design Space |
| T-V34-14-15 | Essai carton : mesure pli/coupe et outil/version/matière consignés | physique |
| T-V34-14-16 | Pen + Cut garde DRAW distinct et propose guide Attacher | auto/UI/Design Space |
| T-V34-14-17 | Foil + Cut conserve FOIL et avertit sur support/outil non qualifiés | auto/UI/Design Space |
| T-V34-14-18 | Explore 5 rejette Engrave/Deboss Maker-only sans substitution | auto |
| T-V34-14-19 | A4 Print Then Cut n'utilise pas la pleine page comme zone de coupe | auto/UI |
| T-V34-14-20 | 12 escargots : PNG et contrat Print Then Cut restent distincts du SVG Cut | auto/Design Space |
| T-V34-14-21 | Smart Material sans tapis avec combinaison inconnue reste UNKNOWN | auto/UI |
| T-V34-14-22 | HTV multicouche exige miroir explicite par couche et rapport de décision | auto/UI |
| T-V34-14-23 | Tapis carte non déclaré bloque « prêt machine » sans empêcher brouillon | auto/UI |
| T-V34-14-24 | Pochoir fragile : ponts trop fins signalés sans fausse cote universelle | auto |
| T-V34-14-25 | Undo groupe CUT+SCORE restaure assignations, sans supprimer géométries | auto/Windows |
| T-V34-14-26 | Projet périmé / commande dupliquée : CAS/idempotence, aucun double commit | auto/Windows |
| T-V34-14-27 | 50 objets : prévol sans troncature silencieuse et résultats déterministes | auto/Windows |
| T-V34-14-28 | Mode sans IA / OOM simulé : formulaire manuel et aucun commit partiel | auto/Windows |
| T-V34-14-29 | Interface clavier/lecteur d'écran : opérations, avertissements, correctifs accessibles | UI/Windows |
| T-V34-14-30 | Export final refuse BLOCKED, brouillon WARN étiqueté ; aucun PASS externe inventé | auto/UI |

**Critères d'acceptation du lot d'implémentation futur :** assertions T01..30 exécutées sur fixtures et SHA ; zéro assignation implicite ; zéro confusion `SCORE`/`CUT` ; zéro état `PHYSICAL_VERIFIED` sans preuve matérielle ; prévol réentrant et stable ; transfert manuel explicite ; aucune régression V1/ComfyUI ; rollback et preuves attachés à la PR de code. **Aucun de ces tests n'a été exécuté ici.**

## 8. Micro-tickets futurs V34-106..115 — tous SPECIFIE, aucun code livré

**Definition of Done commune :** implémentation ultérieure sous PR dédiée, schéma et tests automatisés au SHA, contrats d'erreur et UI accessibles, compatibilité V1/anciens nœuds, aucun code distant ni données privées, preuve par axe indépendante, rollback documenté et réellement vérifié. Les chemins `src/smartsvg_app` sont **provisoires**, à décider après spike de bootstrap ; ne pas créer sous `engine/` sans preuve d'isolation de ComfyUI.

| Ticket | Priorité, dépendances héritées et V34 | Livrables FUTURS, tests, preuve, DoD spécifique et rollback |
|---|---|---|
| **V34-106** modèle d'assignation typé | **P0** S-012/030/032/052, R33-008/022, V34-025..031/096/100 ; `src/smartsvg_app/fabrication/model.py`, `tests/fabrication/test_model.py` ; T01..05 ; auto ; DoD géométries/rôles/operations distincts ; rollback projets V1 lecture seule |
| **V34-107** résolveur tri-state des capacités | **P0** S-012/046/085, R33-022/023/034, V34-012/024/106 ; `.../fabrication/capabilities.py`, `tests/fabrication/test_capabilities.py` ; T06/07/18/21/23 ; auto+Windows, DesignSpace/physique séparés ; DoD provenance datée, pas de promotion UNKNOWN ; rollback mode brouillon |
| **V34-108** collisions et géométrie par opération | **P0** S-030/033/034/056, R33-008/022, V34-097/098/106 ; `.../fabrication/operation_geometry.py`, `tests/fabrication/test_conflicts.py` ; T02/08/09/11/24 ; auto ; DoD duplication et croisements distingués ; rollback revue manuelle |
| **V34-109** prévol déterministe et findings | **P0** S-012/029/054/060, R33-008/022/025, V34-036/101/106..108 ; `.../fabrication/preflight.py`, `tests/fabrication/test_preflight.py` ; T03..11/18/19/24/30 ; auto ; DoD PASS/WARN/BLOCKED non confondus avec preuves ; rollback export brouillon uniquement |
| **V34-110** recette Print Then Cut sémantique | **P0** S-007/009/029/070, R33-004/022, V34-007/087..095/106/109 ; `.../fabrication/print_recipe.py`, `tests/fabrication/test_print_recipe.py` ; T05/19/20 ; auto+DesignSpace ultérieur ; DoD PNG raster distinct de CUT et A4 non rectangulaire ; rollback transfert PNG historique |
| **V34-111** manifeste et guide Score+Cut | **P0** S-012/030/085, R33-008/022/023, V34-008/101/106/109 ; `.../fabrication/handoff.py`, `tests/fabrication/test_handoff.py` ; T10/12..15 ; auto+DesignSpace+physique distincts ; DoD étapes Score/Attacher explicites ; rollback SVG Basic Cut seul avec avertissement |
| **V34-112** Pen/Draw + Cut | **P1** S-032/085/093, R33-008/019/022, V34-106/107/109/111 ; `.../fabrication/draw_plan.py`, `tests/fabrication/test_draw.py` ; T04/16/29 ; auto+UI+DesignSpace futur ; DoD DRAW non transformé en CUT ; rollback guide-only |
| **V34-113** Foil + Cut conditionnel | **P1** S-012/085/093, R33-008/022/023, V34-106/107/109/111 ; `.../fabrication/foil_plan.py`, `tests/fabrication/test_foil.py` ; T17/18/23 ; auto+DesignSpace+physique futurs ; DoD outil/support et incertitudes affichés ; rollback FOIL désactivé |
| **V34-114** UI opérations et réparation | **P0** S-067/069/071/077/080, R33-018/019/022, V34-041..049/105/106/109 ; `engine/web/js/v34_fabrication_panel.mjs`, `tests/ui/test_v34_fabrication.spec.mjs` ; T01/10/13/16/17/21..24/29/30 ; UI+Windows ; DoD clavier, diff, actions sûres ; rollback UI historique |
| **V34-115** révision/Undo/jobs/évidence | **P0** S-023/026/042/061/095, R33-005/011/012/013/025, V34-032..040/074/106/109 ; `.../fabrication/command_adapter.py`, `tests/fabrication/test_transactional.py` ; T25..28/30 ; auto+Windows ; DoD CAS, receipts, OOM/stale non mutants ; rollback lecture seule et V1 intact |

**Mapping inverse tests → tickets (tous les tests ont un propriétaire) :** T01..05→106 ; T06/07/18/21/23→107 ; T02/08/09/11/24→108 ; T03..11/18/19/24/30→109 ; T05/19/20→110 ; T10/12..15→111 ; T04/16/29→112 ; T17/18/23→113 ; T01/10/13/16/17/21..24/29/30→114 ; T25..28/30→115. **Mapping inverse global des 141 exigences** encore ouvert, réservé aux lots 23/24 ; aucune exigence historique supprimée.

## 9. Opportunités, arbitrages et limites de ce cycle

- **O-031 — Détection de conflit d'opérations sur un segment partagé (P1 RETENU_POUR_SPEC).** Raffine S-030/085, R33-022, V34-108/109 ; plus ciblé que O-004 (prévisualisation) et O-028 (budget de chemins). Aperçu « Deux opérations sur ce trait → séparer / conserver en guide / revoir » ; T08/09/24 ; aucune déduction depuis couleur.
- **O-032 — Points de contrôle de cohérence après import (P1 RETENU_POUR_SPEC).** Raffine S-012/084, R33-022/034, V34-111/114 ; distinct de O-001 (journal de transfert) : contrôle **des dimensions et de l'alignement Score+Cut dans le canevas Design Space** par checklist guidée, sans lecture automatique de son état. Aperçu « 2 dimensions / 1 groupe Attacher à confirmer » ; T13/14/30.
- **O-033 — Transformer automatiquement tous les pointillés/couleurs en Score (REJETE).** Ambigu pour les décors et tracés de dessin ; risque de coupe involontaire. Alternative : proposition explicite `SCORE_CANDIDATE` suivie de confirmation ; T01/02/30 négatifs, aucun ticket autonome.

**Non-objectifs maintenus :** clone universel de CAO, simulation physique certifiée, inventaire automatique des accessoires possédés, pilote direct Cricut, contournement Design Space, import/export machine opaque, installation IA automatique, ajout de nouvelles opérations Maker-only pour Explore 5. Les profils multi-machines sont différés.

## 10. Auto-contre-expertise et risques ouverts

**Revue inverse :** (1) aucune couleur ne crée une opération ; (2) `PRINT_THEN_CUT` composite et `PRINT` raster, sans altérer les anciens contrats ; (3) `SCORE` ≠ `CUT` et Attach manuel ; (4) `GUIDE_ONLY` jamais fabriqué ; (5) `UNKNOWN` jamais qualifié ; (6) zéro commande machine ; (7) double coupe et conflits localisés ; (8) CAS/Undo et preuves séparées ; (9) 30 tests → tickets → S/R33 ; (10) tout code futur marqué tel quel.

**Risques P0 encore ouverts :** format V2 et durabilité, import autonome sans `engine/__init__.py` ComfyUI, résolution de profils matériels, parité de transformation mm à l'export, QA réelle Design Space/Explore 5, matrice 141→V34→tests. **P1 :** seuils matière et tests coupon, ordre des opérations dépendant de Design Space, alignement après import, UX accessible, coût de validation de 50 objets, disponibilité de l'outil Score/Foil.

**Aucune validation réelle** Windows, GPU RTX 3070, Design Space, impression, rainurage, dessin, foil ou découpe physique. **Prochain lot 15 :** profils Cricut Explore 5, outils/matières/supports, matrice tri-state versionnée, combinaison de capacités et plan de tests réels ; réviser les exemples de profil `@draft` de ce lot avant toute affirmation de compatibilité.

## 11. Sources officielles vérifiées le 29 octobre 2026

1. Cricut, *Cricut Explore 5: How to use the Scoring Tool* : Score choisi dans Design Space, Attacher Score + Cut, changement d'outil sur demande. https://help.cricut.com/hc/en-us/articles/38613473602455-Cricut-Explore-5-How-to-use-the-Scoring-Tool
2. Cricut, *Design Space: Selecting Operation*, **modifié 15/09/2026** : opération sélectionnée dans Design Space, options filtrées selon machine. https://help.cricut.com/hc/en-us/articles/26922998476183-Design-Space-Selecting-Operation
3. Cricut, *How to use Attach in Design Space*, **modifié 02/10/2024** : placement relatif et liaison Score/Draw/Foil avec Cut. https://help.cricut.com/hc/en-us/articles/360009380514-How-to-use-Attach-in-Design-Space
4. Cricut, *Cricut Explore 5: Button functions and loading basics* : pince à outils Fine-Point/Scoring/Deep-Point/Foil, support stylo compatible, changement sur instruction de Design Space. https://help.cricut.com/hc/en-us/articles/38613203748503-Cricut-Explore-5-Button-functions-and-loading-basics
5. Cricut, *All About Cricut Blades and Machine Tools*, **modifié 03/09/2026** : catégories d'outils Explore 5 et outils Maker/QuickSwap distincts. https://help.cricut.com/hc/en-us/articles/360009432294-All-About-Cricut-Blades-and-Machine-Tools
6. Cricut, *How large can I Print Then Cut?*, **modifié 19/08/2026** : zone non rectangulaire, dépendante machine, papier et proportions ; A4 Explore series, sans garantie d'orientation/implantation locale. https://help.cricut.com/hc/en-us/articles/360009429814-How-large-can-I-Print-Then-Cut
7. Cricut, *Which mats can I use with my Cricut machine?*, **modifié 03/09/2026** : tapis Explore 5, tapis cartes, choix selon matière. https://help.cricut.com/hc/en-us/articles/360009373414-Which-mats-can-I-use-with-my-Cricut-machine

**Limites :** ces pages attestent les règles générales publiées à la date indiquée, **pas** l'import d'un fichier SmartSVG ni la qualification physique d'une combinaison matière/outil. Les numéros de version de Design Space, les marges réellement mesurées et les réglages de pression restent inconnus. Aucune licence IA n'est réévaluée au lot 14 car aucune nouvelle dépendance IA n'est proposée ; la matrice du lot 11 reste en attente de qualification par version/hash.
