# SmartSVG Studio V3.4 — Lot 10 : analyse visuelle, sujets, accessoires et masques

**DRAFT DE SPÉCIFICATION — 29 octobre 2026.** V3.3 reste ACTIVE ; aucun code V3.4, modèle, test Windows/GPU/Design Space ou découpe physique n'est réputé exécuté. Branche documentaire `codex/docs-roadmap-v3-4-campaign`, PR draft #73, issue #72. Base main observée : `fdbda304beb77d97340a8be4dd5c5e9cefde15f4` ; HEAD documentaire avant lot : `6fc5bf4c801e17507e134a7d05c8cf9623d25cb7`.

## 1. Résultat métier, non-objectifs et état réel

**Besoin :** après import d'une planche de 12 escargots, d'une photo smartphone, d'une illustration complexe ou d'un dessin contenant plusieurs accessoires, proposer **des sujets distincts, inspectables et corrigeables** sans déduire arbitrairement « sujet principal », dimensions physiques, identité persistante ou qualité de découpe. Le même contrat doit préparer des lots de 12/24/50, même si la capacité de traitement V21.11 existante est inférieure.

**Réel lu sur main (ne pas confondre avec la proposition) :**
- `engine/smartsvg_ai/auto_masks_v2111.py` : entrée RGB/RGBA `uint8`, **5 000 000 pixels maximum**, **32 masques** maximum, budget `MAX_TOTAL=50_000_000` éléments pour le moteur ; alpha externe ComfyUI inversé (`MASK=1-alpha`), détection alpha/composants et illustration sur fond blanc, refus rectangle, masque trop petit/plein, >32 îlots, bords signalés ; masque accepté = **proposition**, pas preuve sémantique.
- `engine/smartsvg_ai/provider_v2112.py` : adaptateur **ComfyUI** RMBG/SAM2, contrat de nœud inspecté mais modèles susceptibles d'être téléchargés à l'exécution ; sortie limitée à **12 masques**, retour OOM fail-closed ; `available()` ne prouve aucune inférence. Ne jamais appeler le fournisseur par défaut sans contrôle de réseau/poids.
- `engine/smartsvg_core/mask_snapshot_g24.py` : snapshot float32 exact **32 masques max**, **8 000 000 valeurs** cumulées et 5 MP/image ; aperçu PNG L8 dérivé et non autorité. Exemple : 12 masques pleine image à 2 MP = **24 M valeurs**, donc **incompatibles avec ce snapshot** même si le moteur de proposition V21.11 peut les produire.
- `engine/smartsvg_core/subject_identity_g33e.py` et `mask_binding_g33e.py` : IDs persistants uniquement via `Subject` et preuve explicite liée au digest **float32 exact** + source ; l'ordre de preview, un PNG 8 bits ou une empreinte de masque **ne fabriquent pas** un `subject_id`. Les masques legacy ambigus restent non certifiés.
- `engine/smartsvg_core/contracts.py` : choix Express historiques dont 12/24 planches, mais pas moteur multi-sujets V3.4 ; la maquette `engine/web/js/smartsvg_express_atelier_preview.html` affiche 12 escargots **fictifs**. Aucun test réel de segmentation de ces exemples n'est revendiqué.

**Héritage directement relié :** S-005/006/007/008/014/018/023/027/028/050/058/062/070/071/073/074/079/080/093/095 ; R33-003/004/005/006/007/011/012/014/016/017/019/020/024/025/026/030/031/033/034/036/037. Les **141** exigences de V3.3 restent intégralement conservées par `HERITAGE_INDEX.md` ; ce lot n'affirme pas avoir terminé la matrice inverse globale.

**Non-objectifs :** OCR complet, upscale, choix de modèles et licences définitives (lots 11–12), vectorisation (13), placement physique (19), compatibilité certifiée Explore 5 (15–17), envoi de fichiers à une IA cloud, segmentation automatique universelle, 50 masques full-frame en RAM ou dans un seul snapshot V1.

## 2. Contre-expertise du lot 09 et ADR-034-13 (proposée)

**Contradiction du lot 09 corrigée :** `AcceptSubjectsBatch` est **une commande atomique d'acceptation de propositions déjà matérialisées et valides**, pas une commande qui lance l'inférence ni une promesse qu'un `MAX_MASKS=32` acceptera 50 masques. `PlanExport` est refusé/conditionné si sujets non acceptés ; une proposition `SubjectProposal` n'est ni un `Subject` persistant, ni une permission de fabrication. Le digest de masque ne suffit pas à fabriquer une identité. Le planificateur n'a jamais accès aux pixels ni à une API d'installation de modèle.

**ADR-034-13 : séparer Analyse → Propositions → Revue → Commit**, avec autorité unique du projet et moteur déterministe de validation :
- **A — 50 masques pleine image en un tenseur** : simple à brancher, mais explosion mémoire, limites 32/8 M et ZIP ; **REJET**.
- **B — recadrages/ROI bornés + manifeste par sujet + traitement par lots** : réutilise V21.11 pour les petits cas et permet 50 propositions **au total** sans exiger 50 masques simultanés ; **RECOMMANDÉ comme architecture à prototyper**. Nécessite schéma V2 explicite, preuve par ressource, tests de recomposition et migrations.
- **C — IA sémantique obligatoire** : trop coûteuse, non déterministe, licences et VRAM non vérifiées ; **REJET comme prérequis**. IA locale facultative, chargée seulement après consentement.
- **D — segmentation purement manuelle** : **fallback P0** toujours disponible, pas solution unique pour les planches répétitives.

**Invariant :** l'original immuable est l'autorité des pixels ; la représentation canonique d'analyse est une vue dérivée orientée avec transformation enregistrée ; le masque float32 révisé est l'autorité de retouche ; le PNG L8 et le SVG restent des dérivés. Aucun `bbox`, centre de gravité ou ordre d'affichage ne devient une cote réelle.

## 3. Parcours et UX — novice/expert

**Novice, planche 12 escargots :** Importer → aperçu de la source orientée → choisir « Mes 12 escargots » → analyse sans IA si possible → cartes de propositions avec surbrillance croisée → corriger/fusionner/séparer les zones et associer les accessoires → confirmer **12 sujets** → enregistrer un lot atomique → passer à Atelier/Print Then Cut. Si aucun sujet n'est fiable : « Sélectionner au pinceau / détourer manuellement » ; jamais « 12 trouvés » sur la seule maquette.

**Expert, photo smartphone / illustration dense :** afficher orientation EXIF, ICC et transformée, source/masque/coupe en vues distinctes, masque float32 à 100 % et coordonnées source, rapports d'îlots/chevauchements, provenance méthode/ressource, statut `UNKNOWN` ou `NEEDS_REVIEW`, job et snapshot épinglés. Une suggestion « accessoire de tel sujet » est réversible et n'est pas une vérité sémantique.

~~~text
[SmartSVG / Atelier] [Source immuable] [Sans IA ▾] [12 propositions · 0 acceptée]
┌ Source / Zoom 100 % ───────────────┬ Sujets à vérifier ──────────────────┐
│ [Original | Masque | Superposition]│ 01 Escargot ?  [Voir] [✓] [Corriger]│
│ survol/sélection synchronisés      │ 02 Escargot ?  [Voir] [✓] [Corriger]│
│ [Contours suspects: 3]            │ 03 Fleur ?     [Lier à 02] [Séparer]│
│ [Pinceau + / -] [Annuler]          │ …  [Voir 12] [Filtres: suspects]     │
└────────────────────────────────────┴─────────────────────────────────────┘
[⚠ 2 zones touchent le bord] [Revoir] [Tout sélectionner = pas tout accepter]
[Confirmer les sujets vérifiés] [Reprendre plus tard] [Passer en manuel]
~~~

~~~text
[Expert / Analyse] Source SHA / orientation EXIF / ICC / 4032×3024 avant dérivation
Job j10-1 [CPU][READY] | snapshot pinned r7 | backend RULE/LOCAL/MANUAL
Propositions: 12; ACCEPTABLE 9, NEEDS_REVIEW 2, BLOCKED 1
ROI source: x,y,w,h ; transformée canonique→source ; float32 SHA ; overlap
[Comparer 2 versions] [Inspecter îlots] [Exporter rapport local expurgé]
[Réviser masque] [Accepter sélection explicite] [Rejeter] [Rejouer job]
~~~

**États UI** : EMPTY, SOURCE_LOADING, SOURCE_READY, ANALYZING, PROPOSALS_READY, NEEDS_REVIEW, PARTIAL, BLOCKED, ACCEPTING, SAVED_CONFIRMED, STALE, CANCELLED, RECOVERY_REQUIRED. `SAVED_CONFIRMED` uniquement après receipt durable (lot 06) ; `PARTIAL` concerne les **résultats du job**, jamais un demi-commit de sujets.

**Accessibilité :** sélection sujet↔vignette↔calque par même ID de proposition, clavier et libellés sans couleur, navigation liste/zoom indépendante, messages FR « Masque trop proche du bord — corriger » avec focus sur zone, pas de confirmation cachée ; mode expert n'ôte pas les gates.

## 4. Contrats, coordonnées, identités et persistance (PROPOSITION)

### 4.1 AnalyseRequest / ProposalManifest (exemples JSON de spécification, non exécutés)

~~~json
{
  "contract": "v34.analysis-request/0.1-draft",
  "request_id": "analysis-10-001",
  "project_id": "demo-escargots",
  "source_id": "source-01",
  "source_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "expected_project_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "expected_logical_revision": 7,
  "job_id": "job-10-001",
  "mode": "RULES_FIRST",
  "ai_consent": "NONE",
  "expected_subject_count": 12,
  "max_proposals_total": 50,
  "canonical_view": {"orientation_applied": true, "width_px": 1200, "height_px": 900, "color_space": "sRGB", "transform_id": "view-transform-01"},
  "budget": {"max_active_masks": 4, "max_concurrent_gpu_jobs": 1, "network_allowed": false}
}
~~~

~~~json
{
  "contract": "v34.subject-proposals/0.1-draft",
  "job_id": "job-10-001",
  "source_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "base_project_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "canonical_transform_id": "view-transform-01",
  "status": "PARTIAL",
  "proposals": [
    {
      "proposal_id": "proposal-job10-001",
      "roi_px": {"x": 100, "y": 120, "width": 180, "height": 200},
      "mask_ref": "cache/job-10-001/mask-001.f32",
      "mask_sha256_float32": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
      "method": "RULE_ALPHA",
      "review_state": "NEEDS_REVIEW",
      "warnings": ["EDGE_TOUCH"],
      "suggested_parent_proposal_id": null,
      "semantic_label": null,
      "semantic_confidence": null
    }
  ],
  "items_total": 12,
  "items_completed": 1,
  "items_failed": 0,
  "receipt": null
}
~~~

**Contraintes obligatoires :**
- `source_sha256` = octets originaux, jamais dérivé ; `canonical_transform_id` versionné et déterministe ; EXIF 1..8 et profil ICC explicités ; l'orientation de l'image et celle des masques ne doivent jamais diverger. Transformation inverse définie et testée, y compris miroir.
- `proposal_id` unique par job, **éphémère** ; `subject_id` créé uniquement au commit par `SubjectPort` à partir d'un masque validé et d'une preuve d'identité canonique. `mask_ref` = identifiant de ressource **locale sandbox**, non chemin arbitraire accepté du client ; digest sur float32 canonique `<f4`, forme/dimensions et espace coordonnées inclus dans l'enveloppe de preuve.
- `roi_px` demi-ouvert dans l'espace de la vue orientée, entiers >=0, strictement inclus dans source, taille >0 ; pixels hors ROI **explicitement nuls** pour la recomposition ; soft-mask float32 borné [0,1] fini, sans NaN, vérification des strides, canaux, finitude et ordre des axes.
- `semantic_label` facultatif et **non autoritaire** ; `semantic_confidence` null si non calibrée ; aucune « certitude » numérique déduite de la géométrie. `review_state` = PROPOSED/NEEDS_REVIEW/BLOCKED/ACCEPTED/REJECTED ; ACCEPTED seulement via commande humaine et receipt.
- Relations d'accessoires : lien explicite `parent_proposal_id` + `relation_kind` (ATTACHED/SEPARATE/UNKNOWN) ; ne pas fusionner les pixels lors d'une simple association. Plusieurs propositions peuvent se recouvrir : calculer le conflit et demander un arbitrage.
- `max_proposals_total=50` est **objectif d'orchestration**, pas capacité V21.11 ni G2.4 ; le manifeste V2 est futur et **ne doit pas être sérialisé dans un archive V1 non compatible**. Les contraintes d'archive V1 restent applicables tant que migration V2 n'est pas qualifiée.
- Provenance obligatoire : moteur et version, paramètres, digest du modèle si IA consentie, provenance de chaque masque, source/transformée, `job_spec_digest`, état de revue, warnings et preuves séparées. Pas de nom de fichier personnel dans les logs publics.

### 4.2 Ports et événements (fichiers FUTURS, non présents)

`ImageIntakePort.inspect(source_ref)->SourceInspection` ; `CanonicalViewPort.derive(source, orientation, color_profile)->ViewRef` ; `AnalysisPort.propose(AnalysisRequest)->JobRef` ; `MaskValidationPort.validate(ProposalRef)->QualityReport` ; `ProposalStorePort.list(job_id)->ProposalManifest` ; `SubjectPort.accept_batch(proposal_ids, expected_sha, epoch)->CommitReceipt` ; `MaskEditorPort.revise(proposal_id, brush_ops)->RevisionRef`. Tous les ports consomment des IDs/digests, pas des chemins ou objets Python sérialisés sans validation.

Événements : SourceInspected, AnalysisQueued, ProposalReady, ProposalNeedsReview, ProposalRejected, AnalysisPartial, AnalysisFailed, AnalysisCancelled, AnalysisStale, ProposalRevisionCreated, SubjectsBatchAccepted, RecoveryRequired. Chaque événement inclut `event_id`, `job_id`, `project_id`, `source_sha256`, `expected_project_sha256`, `logical_revision`, `epoch`, `event_seq`, `contract_version` ; les abonnés ignorent doublons et événements périmés. L'UI ne déduit pas `COMMITTED` d'un événement de job.

**Frontières :** Intake→Analysis sans mutation ; Analysis→ProposalStore éphémère à quota ; MaskValidation déterministe ; correction par CommandPort/éditeur ; AcceptSubjectsBatch via **writer unique** et receipt durable du lot 06. Le planificateur lot 09 ne peut qu'invoquer le catalogue fermé et ne voit pas le disque/les poids du fournisseur. Aucun accès réseau sans consentement distinct.

## 5. Déroulé déterministe, cas limites et mémoire

~~~python
# PSEUDOCODE DE SPÉCIFICATION, NON EXÉCUTÉ
def propose_subjects(request, snapshot, resources, budget):
    assert request.source_sha256 == snapshot.source_sha256
    view = canonicalize_once_without_modifying_source(resources.source)
    validate_transform_and_dimensions(view, request.canonical_view)
    for tile in bounded_partition(view, budget):
        candidates = rules_alpha_flat_artwork_or_manual(tile)
        if request.ai_consent == "EXPLICIT_LOCAL_MODEL" and installed_model_is_verified():
            candidates += optional_local_provider(tile, network=False, unload_after=True)
        for candidate in candidates:
            report = validate_float32_roi(candidate, view, budget)
            yield isolated_proposal_or_typed_rejection(report)
    return immutable_manifest_with_per_item_status()

def accept_verified_batch(manifest, selected_ids, snapshot, epoch):
    assert all(proposal_is_reviewed_and_valid(i) for i in selected_ids)
    assert all(proposal_source_transform_and_digest_match(i) for i in selected_ids)
    assert manifest.base_project_sha256 == snapshot.sha256
    return CommandPort.submit_atomic("AcceptSubjectsBatch", selected_ids, epoch)
~~~

**Pipeline :** 1) admission hostile de fichier (décompression/tailles/ICC/EXIF) → 2) dérivation orientée immuable → 3) analyse de type source (alpha déjà présent, dessin fond uniforme, photo) → 4) règles déterministes, avec refus plutôt que rectangle arbitraire → 5) option IA locale installée/consentie seulement → 6) validation par ROI (aire, îlots, trou, contact bord, inversion alpha, saturation, couverture, overlaps, masque vide/plein, dimensions) → 7) revue humaine et corrections non destructives → 8) acceptation atomique sur snapshot/epoch épinglé → 9) persistence V2 si gate passé ou refus motivé/fallback manuel V1.

**Découpage en tuiles :** l'image canonique garde des coordonnées globales ; halo de tuiles documenté et retiré à la fusion ; dédoublonner par intersection/identité de pixels sous seuils mesurés ; si un sujet chevauche une frontière, le reconstituer avant de proposer ou marquer `CROSSES_TILE_BOUNDARY` ; ne jamais créer deux sujets identiques. Les seuils IoU, min-area et distance d'accessoire sont des **paramètres de benchmark**, pas des vérités universelles. Ne pas masquer les échecs par un simple top-12 tronqué.

**Budget :** un `MAX_TOTAL=50_000_000` du moteur V21.11 ne garantit ni 50 sujets ni stockage de 50 masques ; fixer un **budget en octets** pour chaque phase, allocation paresseuse de ROI, libération et cache digest, tests d'injection OOM. 50 sujets peuvent exiger plusieurs jobs ; chaque job possède résultats individuels et reprise sans duplication. Si 5 MP dépassés, proposer preview réduite **pour diagnostic seulement** puis traitement borné sur source/tuiles si prototypé ; ne pas prétendre que la réduction garantit le détail de coupe.

**Règles de sécurité et fallback :** image corrompue/bombe de décompression → refus ; ICC/EXIF invalides → diagnostic, orientation manuelle explicite si nécessaire ; alpha opaque ou inversé → ne pas valider comme découpe ; modèle absent/VRAM OOM → aucune installation ni connexion automatique, retour manuel/CPU ; photo à fond chargé → pas de masque rectangulaire silencieux ; dessin complexe (type Pokémon) → conserver accessoires et petits détails, sans publier d'images protégées ; 2 sessions → CAS/epoch, aucun écrasement ; disque plein → conserver original et dernière version saine, reprise explicite ; refus d'un masque n'efface jamais les autres propositions.

**Undo/Redo :** retouches de masque et liaisons d'accessoires = commandes réversibles versionnées ; les jobs/propositions temporaires peuvent être annulés mais ne sont pas des mutations projet ; acceptation groupée = un receipt/une étape Undo logique. Après changement du masque, digest de preuve invalide → recalcul/revue, ne pas conserver un badge VERIFIED périmé.

## 6. Deux vertical slices et séparation fabrication

**A — 12 escargots → stickers :** source 1200×900 synthétique autorisée, 12 motifs disjoints + un accessoire détaché → proposition 12 sujets **réels** par règles si possible, sinon correction manuelle → 12 IDs de proposition et masques float32 inspectables → contrôle accessoire, masques touchant bord et doublons → acceptation atomique des sujets vérifiés → choix explicite largeur 40 mm → **PNG Print Then Cut** avec alpha/résolution et prévol ultérieurs (lots 12/17/19). Import Design Space comme image imprimable et flux Print Then Cut ; **pas de marques capteur PDF produites par SmartSVG**. Les 12 exemples UI G3.2 ne sont pas un résultat d'inférence.

**B — boîte carton → Score + Basic Cut :** aucun sujet raster n'est nécessaire à une boîte paramétrique créée à partir de cotes saisies ; le moteur de lot 16 doit produire les chemins CUT et SCORE distincts. Si un logo photo est ajouté, son masque passe par le présent lot, sans transformer les lignes de pli en contours de segmentation. Dans Design Space, SCORE et Attacher restent des gestes explicites ; aucune certification de matière/outil, aucun pilotage machine.

**C — 24/50 sujets :** corpus synthétique à 24 et 50 symboles, variantes chevauchées/tuilées ; analyse partielle et reprises, pas plus de 4 masques ROI actifs dans le budget illustratif ; rapport par objet (réussi, ambigu, rejeté, non traité), aucun sujet perdu silencieusement. V1 peut rester limité ; la capacité 50 est **conditionnelle à V2/benchmarks**, non une propriété actuelle.

## 7. Corpus de référence et métriques de qualification (tous FUTURS)

Fixtures à **créer sans œuvres tierces** : C10-A 12 escargots vectoriels dessinés par nous et rendus en PNG avec masques vérité terrain ; C10-B 24 symboles + 4 accessoires ; C10-C 50 symboles répartis sur tuiles ; C10-D photo smartphone synthétique avec EXIF 1..8, miroir et ICC ; C10-E fond texturé, ombres et transparence ; C10-F illustration dense avec yeux/traits et régions blanches encloses ; C10-G masque rectangle, vide, plein, inversé, NaN et dimensions H/W permutées ; C10-H source >5 MP et budget 8 M float32 dépassé ; C10-I doublons/overlap et sujet traversant tuile ; C10-J jobs concurrents, crash/OOM et changement de SHA ; C10-K texte EXIF/nom de fichier hostile ; C10-L source avec licences non autorisées (ne pas stocker, test de rejet métadonnées). Les exemples sont **spécifications de fixtures**, pas des fichiers présents.

Métriques à mesurer : recall/precision de sujets, IoU par sujet **après appariement optimal et exclusion des sujets ambigus explicitée**, conservation d'accessoires, taux de faux sujets, nombre de masques nécessitant correction, temps utilisateur pour corriger, p50/p95 latence CPU/IA, pic RAM/VRAM et octets sur disque, collisions/doublons, taux de réouverture/Undo fidèle. Objectifs initiaux à éprouver : 12/12 sujets sur C10-A et 0 acceptation silencieuse ; 0 perte de sujet sur C10-C **dans le manifeste**, même si certaines propositions sont BLOCKED ; aucune divergence de coordonnées EXIF sur C10-D ; 0 mutation sur crash/OOM/STALE. Les seuils IoU/latence/VRAM ne seront figés **qu'après baseline et protocole** ; ne pas inventer de benchmark.

**Preuves séparées** : AUTO = assertions Python/JS sur SHA testé ; WINDOWS = UI + mémoire/latence sur environnement réel ; GPU = RTX 3070 8 Go, modèle/version/hash/licence et journaux réels ; DESIGN_SPACE = import/résultat documenté, pas inféré des masques ; PHYSIQUE = découpe réelle Explore 5, matériau/outils/profil, mesure et approbation humaine. Pour le lot 10, seuls des **tests documentaires** sont effectués ; tous les tests ci-dessous restent NON_EXECUTE.

## 8. Tests d'acceptation à implémenter (30 IDs, tous NON_EXECUTE)

| ID | Assertion attendue | Preuve |
|---|---|---|
| T-V34-10-01 | EXIF 1..8 donne vue et masque même orientation, transformation inverse exacte | auto |
| T-V34-10-02 | SHA de source originale inchangé après diagnostic et retouche | auto |
| T-V34-10-03 | ICC absent/corrompu est signalé ; aucune correction couleur non tracée | auto |
| T-V34-10-04 | Image corrompue/bombe de décompression refusée avant allocation | auto sécurité |
| T-V34-10-05 | Alpha RGBA et LoadImage MASK concurrents → refus ambigu | auto |
| T-V34-10-06 | Alpha opaque/vide ne produit aucun sujet « certifié » | auto |
| T-V34-10-07 | Fond blanc non uniforme/photo → règles refusent rectangle arbitraire | auto |
| T-V34-10-08 | Source H/W permutées, NaN/Inf, shape/strides invalides → rejet | auto |
| T-V34-10-09 | ROI hors limites, chevauchement halo non résolu → BLOCKED | auto |
| T-V34-10-10 | 12 escargots synthétiques : 12 propositions réelles, IDs uniques | auto |
| T-V34-10-11 | 24 sujets : aucune troncature silencieuse au top-12 du provider legacy | auto |
| T-V34-10-12 | 50 sujets : résultats par objet et reprise, 0 perte silencieuse | auto |
| T-V34-10-13 | 12×2 MP excède snapshot V1 8 M ; refus ou V2 explicite, jamais V1 invalide | auto |
| T-V34-10-14 | Un sujet traversant 2 tuiles est recomposé ou bloqué, jamais dupliqué | auto |
| T-V34-10-15 | Chevauchements/îlots/accessoires sont signalés avec régions précises | auto |
| T-V34-10-16 | Un masque touchant bord n'est pas auto-accepté sans revue | auto |
| T-V34-10-17 | Digest exact float32, forme et transformation vérifiés avant acceptation | auto |
| T-V34-10-18 | IDs persistants viennent du SubjectPort/receipt, jamais d'index ou PNG | auto |
| T-V34-10-19 | Une correction invalide le digest de preuve antérieur | auto |
| T-V34-10-20 | Accessoire lié/séparé par commande réversible, pixels non fusionnés | auto + UI |
| T-V34-10-21 | Job interrompu/OOM : rapport PARTIAL, aucun commit, reprise sans doublon | auto + Windows |
| T-V34-10-22 | Réponse tardive sur SHA/epoch modifiés : STALE, 0 mutation | auto |
| T-V34-10-23 | Double clic AcceptSubjectsBatch = une transaction/receipt | auto + Windows |
| T-V34-10-24 | Modèle absent/refus de téléchargement : CPU/manual sans réseau | auto sécurité |
| T-V34-10-25 | Nom/EXIF/OCR hostile ne déclenche ni commande ni réseau | auto sécurité |
| T-V34-10-26 | Novice sélectionne/rejette/corrige 12 propositions sans sujet fantôme | UI |
| T-V34-10-27 | Expert inspecte masque float32/coordonnées/rapport sans faux badge QUALIFIE | UI |
| T-V34-10-28 | Clavier seul, lecteur d'écran et zoom 100 % couvrent revue + correction | Windows UX |
| T-V34-10-29 | Benchmark p50/p95 CPU/RAM/VRAM + qualité par corpus/version, sans PASS fictif | Windows + GPU |
| T-V34-10-30 | Export aval garde PNG Print Then Cut distinct du SVG Cut ; contrôle Design Space et physique NON_EXECUTE tant qu'absence de preuve | auto + DesignSpace + physique |

## 9. Micro-tickets V34-068..077 — futurs, priorité, DoD et rollback

**Definition of Done commune (FUTURE) :** contrat versionné, tests nommés réellement exécutés sur SHA de code exact, preuves auto/Windows/GPU/DesignSpace/physique distinctes, gestion d'erreurs et d'annulation, aucune fuite de média, rétrocompatibilité V1, rollback vers voie manuelle/legacy, documentation du budget et de la provenance. État actuel de chaque ticket : **SPECIFIE**, pas IMPLEMENTE/RACCORDE/QUALIFIE/STABILISE. Chemins cités ci-dessous = **fichiers pressentis, non créés**.

| Ticket | Priorité / dépendances | Livrables futurs ; tests et preuve exacte ; rollback |
|---|---|---|
| **V34-068** Admission source + vue canonique | **P0** S-006/050/061, R33-004/024/026, V34-025/041 ; `engine/smartsvg_app/vision/intake.py`, `tests/vision/test_intake.py` ; T-V34-10-01..04, SHA source/EXIF/ICC, auto sécurité ; DoD orientation sans mutation ; rollback import manuel validé |
| **V34-069** Stratégie règles alpha/dessin et fallback | **P0** S-007/014, R33-006/007, V34-017/050/059 ; `engine/smartsvg_app/vision/rule_proposer.py` ; T-V34-10-05..08, auto ; DoD aucune silhouette rectangle inventée ; rollback outils de sélection manuelle |
| **V34-070** ROI/tuiles et manifeste de 12/24/50 | **P0** S-018/062, R33-011/026/031, V34-025..031/032..040 ; `engine/smartsvg_app/vision/roi_manifest.py` ; T-V34-10-09..14, auto + mémoire Windows ; DoD pas de troncature et respect V1/V2 ; rollback limite legacy explicitée |
| **V34-071** QA masques déterministe + conflits | **P0** S-007/014/071/073, R33-006/034, V34-012/062 ; `engine/smartsvg_app/vision/mask_qa.py` ; T-V34-10-15..17, auto ; DoD rapports reproductibles et faux badges interdits ; rollback revue manuelle obligatoire |
| **V34-072** Preuve d'identité et AcceptSubjectsBatch | **P0** S-023/028, R33-004/005/014, V34-025/029/032..040/061/063 ; `engine/smartsvg_app/vision/subject_commit.py` ; T-V34-10-17..19/22/23, auto + Windows ; DoD SubjectPort+receipt atomique ; rollback acceptation unitaire existante |
| **V34-073** Relations accessoires réversibles (O-019) | **P1** S-028/070/080, R33-006/019, V34-036/045/071/072 ; `engine/smartsvg_app/vision/accessory_links.py` ; T-V34-10-15/20, auto + UI ; DoD relation explicite, Undo exact ; rollback associations manuelles sans fusion |
| **V34-074** Jobs partiels, annulation et OOM | **P0** S-027/062/095, R33-011/012/017/025/030, V34-017/032..040/070 ; `engine/smartsvg_app/vision/analysis_jobs.py` ; T-V34-10-11/12/21/22/24, auto + Windows/GPU ; DoD pas de doublon ni téléchargement implicite ; rollback CPU/manual |
| **V34-075** Revue novice/expert accessible | **P0** S-070/071/073/079/080, R33-018/019/020/033, V34-041..049/050..058/071 ; `engine/web/js/v34_subject_review.mjs` ; T-V34-10-16/26..28, UI + Windows UX ; DoD navigation croisée sans ID fictif ; rollback liste de propositions textuelle |
| **V34-076** Inspection pixel 1:1 et échantillonnage (O-020) | **P1** S-015/073/079, R33-017/019, V34-071/075 ; `engine/web/js/v34_mask_inspector.mjs` ; T-V34-10-15/16/27/28, UI + auto ; DoD inspecter bords sans modifier le masque ; rollback zoom/avant-après existant |
| **V34-077** Corpus et recette de segmentation | **P0** S-005/006/050/058/093, R33-016/017/024/034/037, V34-068..076 ; `tests/fixtures/v34_vision_synthetic/`, `tests/vision/test_vision_e2e.py` ; T-V34-10-01..30, auto/Windows/GPU, DesignSpace/physique **séparés** ; DoD corpus/hash/rapport comparatif + limites documentées ; rollback pas de promotion des capacités |

**Mapping inverse du lot :** T01..04→068 ; T05..08→069 ; T09..14→070 ; T15..17→071 ; T17..19/22/23→072 ; T20→073 ; T11/12/21/22/24→074 ; T16/26..28→075 ; T15/16/27/28→076 ; T01..30→077. Chaque ticket cite ses S/R33 ; aucun ticket n'annule une exigence historique. Consolidation exhaustive de la matrice 141→V34→tests prévue lots 23/24.

## 10. Opportunités du cycle et risques ouverts

**O-019 P1** revue explicite des **relations** accessoires (au-delà de S-028 qui demande leur conservation) ; **O-020 P1** inspection pixel 1:1 et échantillonnage des bords pour réduire les erreurs de masques acceptés ; **O-021 REJET** envoi silencieux d'images à une API cloud pour « améliorer » la reconnaissance. Détails, alternatives, UX, scores et tests dans `OPPORTUNITIES.md` ; aucun nouveau P0 artificiel.

**Risques P0 à traiter avant implémentation :** ROI V2 et preuve float32 sans casser le schéma V1 ; qualité des masques sur photos réelles ; `MAX_MASKS=32` vs 50 et `MAX_VALUES=8 M` vs 12 masques de 2 MP ; orientation/ICC ; budget RAM et libération GPU ; identité d'accessoires et corrections ; limites des sources protégées et licences de modèles ; tests Windows/RTX 3070 ; matrice inverse 141 héritées. Décisions en attente : stratégie V2 ROI et seuils de fusion/IoU après prototype, choix fournisseur et licences au lot 11, benchmarks réels.

## 11. Sources vérifiées le 29 octobre 2026 et limites

- Code source `main` : `auto_masks_v2111.py`, `provider_v2112.py`, `mask_snapshot_g24.py`, `subject_identity_g33e.py`, `mask_binding_g33e.py`, `contracts.py` ; AGENTS.md, README, maître/traceability/coverage/heritage/audit V3.3, ETAT_ACTUEL, lot 09 et issue #72.
- Cricut officiel, **How to upload images into Design Space**, édité 30 mars 2026 : https://help.cricut.com/hc/en-us/articles/360009556313-How-to-upload-images-into-Design-Space ; distingue raster et SVG et avertit des imports SVG > 5 000 chemins. Cette documentation **ne qualifie pas nos masques**.
- Cricut officiel, **Comment Imprimer puis découper**, édité 15 mai 2025 : https://help.cricut.com/hc/fr/articles/360009387274-Comment-Imprimer-puis-d%C3%A9couper-dans-Design-Space ; aplatir/flux Print Then Cut dans Design Space, pas de PDF de repères externes.
- Pillow officiel, **ImageOps.exif_transpose**, documentation stable consultée le 29 octobre 2026 : https://pillow.readthedocs.io/en/stable/reference/ImageOps.html#PIL.ImageOps.exif_transpose ; API exacte et version installée **à vérifier** lors des spikes Windows.
- **Aucune licence de Florence-2/SAM2/BiRefNet/RMBG/Real-ESRGAN qualifiée ici** : inventaire de versions, hash, usage commercial et VRAM au lot 11 ; aucune installation ni téléchargement en cycle 10.

## 12. Auto-relecture documentaire (pas des tests produit)

Vérifier avant clôture : (1) tous les 30 tests ont un ticket et des assertions ; (2) 10 tickets V34-068..077 uniques ; (3) 141 exigences historiques inchangées ; (4) pas de confusion 50 sujets vs 50 masques V1 ; (5) aucune action IA sans consentement ni transfert automatique Cricut ; (6) aucun chemin protégé modifié ; (7) les fichiers proposés restent marqués FUTURS. Les résultats réellement observés doivent être inscrits dans `PROGRESS.md` après relecture GitHub.
