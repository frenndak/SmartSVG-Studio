# SmartSVG Studio V3.4 — Lot 05 : projet .smartsvg, identités, ressources, révisions et migrations

**DRAFT de conception — 29 octobre 2026.** Statut : `SPECIFIE`, aucune modification du moteur. Base du code lue : `main@fdbda304beb77d97340a8be4dd5c5e9cefde15f4` ; branche de préparation `codex/docs-roadmap-v3-4-campaign`, PR #73, issue #72. **V3.3 reste la seule roadmap active.** Les JSON ci-dessous sont des **contrats proposés**, pas des archives déjà produites ou testées. Aucun essai Windows, GPU, Design Space ou Cricut n'est revendiqué.

## 1. Problème, objectifs, limites et contre-expertise du cycle 04

L'atelier autonome doit ouvrir les projets existants sans perte, conserver source originale, masques float32, IDs de sujets, accessoires, opérations et preuves, puis enrichir le document de géométrie de fabrication, de commandes annulables et de ressources de planches. Une nouvelle interface ne doit ni créer une seconde vérité ni réécrire silencieusement les archives historiques.

**État réel constaté dans le code, et non fonctionnalité V3.4 déjà disponible :**
- `engine/smartsvg_core/project_archive.py` : `SCHEMA_VERSION='smartsvg-project/1'` ; ZIP contrôlé ; `MAX_ENTRIES=256` ; `MAX_MEMBER_BYTES=64 MiB` ; `MAX_TOTAL_BYTES=256 MiB` ; `MAX_ARCHIVE_BYTES=280 MiB` ; `MAX_JSON_BYTES=4 MiB` **par fichier JSON** ; profondeur JSON ≤32 ; opérations ≤5 000. Entrées JSON obligatoires : `document.json`, `operations.json`, `sources.json`, `masks.json`, `subjects.json`, `artifacts.json`, `proofs/qa_results.json`. Les ressources sont strictement déclarées et vérifiées ; **ajouter arbitrairement un membre ZIP V3.4 est rejeté** (`RESOURCE_SET_MISMATCH`).
- `LoadedProject` ne possède pas de champ de révision numérique ni de journal de commandes idempotentes ; `ManagedWorkspace` expose le **SHA-256 des octets du fichier .smartsvg** comme révision CAS, et un dossier géré. `project_recovery.py` utilise verrou OS, fichier `.pending-backup.smartsvg` et `.previous.smartsvg` avec résolution explicite.
- `SourceAsset` conserve `source_id`, SHA-256, dimensions, mode couleur et provenance ; `Mask` est une **prévisualisation L8** ; `mask_snapshot_g24.py` garde l'autorité float32 ordonnée avec maximum 32 masques **pour une seule source**. `subject_identity_g33e.py` lie explicitement un `subject-<32 hex>` au masque exact et à l'empreinte float32, sans dérivation par ordre ou digest. `editor_session_g23.py` limite les coups de pinceau à 400 et 12 000 points au total.
- `Artifact.use` V1 n'admet que `print_then_cut_png`, `basic_cut_svg` et `editable_svg` ; ne **pas** lui injecter silencieusement `score`, `foil`, `multilayer` ou un chemin inconnu. Les **quatre contrats métier de sortie V3.3** restent distincts, même si le type `Artifact` V1 ne les représente pas tous nativement.
- La migration M1/M2 du lot 04 n'est pas implémentée ; le bootstrap Python autonome reste bloqué par l'import `engine/__init__.py`, et le graphe AST/ESM exhaustif reste ouvert (V34-017). **Aucune nouvelle API d'archive n'est supposée existante.**

**Correction du lot précédent :** remplacer l'expression imprécise « version de projet V34 » par trois axes distincts : `archive_schema` (format ZIP et règles), `document_schema` (modèle d'édition et fabrication), `app_version` (logiciel). Le SHA du fichier reste la révision CAS existante ; un `logical_revision` monotone est seulement **proposé pour V2**, sans l'inventer pour V1. Le futur journal ne peut pas être considéré idempotent par la seule présence d'`operations.json`.

## 2. ADR-034-06 — Politique de compatibilité : V1 strict + V2 explicite (PROPOSÉ)

| Option | Avantage | Risque / décision |
|---|---|---|
| A — Tout enregistrer dans `document.json` V1 | Ancien chargeur peut lire des clés JSON additionnelles de taille bornée ; chemin court pour **métadonnées légères** | Risque de perte de sémantique si ancien client réécrit ; **autoriser seulement en expérimentation contrôlée** avec validation aller-retour, jamais pour ressources ou nouvelles opérations certifiées |
| B — Injecter de nouveaux fichiers ZIP dans V1 | Facilité apparente | **REJET** : `_validate_bundle` exige ensemble exact de ressources |
| C — Format `smartsvg-project/2` avec migrateur explicite | Contrats de ressources et journal évolutifs ; rejet sûr par ancien lecteur | Coût d'un nouveau lecteur/écrivain et de tests de sécurité ; **CIBLE RECOMMANDÉE**, après spike et gates |
| D — Projet JSON parallèle à .smartsvg | Aucun | **REJET** : double source de vérité et révisions concurrentes |

**Décision :** préserver les archives V1 inchangées ; ouverture en lecture seule possible dans la nouvelle interface. Toute écriture native sur V1 est limitée aux opérations **déjà réellement prises en charge par l'ancien writer** et à ses contrôles ; aucune conversion implicite. Pour les fonctions V34 nécessitant nouvelles ressources, faire **Enregistrer une copie migrée** vers V2 lorsque le writer V2 sera implémenté et qualifié. Le fichier V1 reste intact. Le chargeur V1 doit continuer à refuser V2 par `UNSUPPORTED_PROJECT_SCHEMA` ; l'interface affiche « version plus récente, ouvrir en lecture seule si possible » sans tenter de downgrade. Un lecteur V2 doit prendre en charge V1 via adaptateur, sans modifier le disque lors de l'ouverture.

**Invariant absolu :** un projet canonique à la fois. Les index de bibliothèque, caches de miniatures, prévisualisations, exports et rapports ne deviennent pas des autorités de projet. Un sidecar de secours est une sauvegarde transactionnelle, pas un second document éditable.

## 3. Schéma logique canonique V2 proposé (ne pas confondre avec le ZIP V1)

```json
{
  "archive_schema": "smartsvg-project/2-draft",
  "document_schema": "smartsvg-document/2-draft",
  "project_id": "boite-demo-01",
  "app_version": "v3.4-draft",
  "logical_revision": 4,
  "parent_revision_digest": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "sources": [
    {"source_id":"source-original","sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","width_px":1200,"height_px":900,"color_mode":"RGBA","resource_ref":"sources/source-original.png","immutable":true}
  ],
  "subjects": [
    {"subject_id":"subject-0123456789abcdef0123456789abcdef","source_id":"source-original","mask_ref":"mask-pack-001:0","identity_proof_ref":"proof-subject-001","accessory_ids":[]}
  ],
  "objects": [
    {"object_id":"object-001","subject_id":"subject-0123456789abcdef0123456789abcdef","geometry_ref":"geometry/outline-001.svg","operation_ref":"operation-001","transform_mm":[1,0,0,1,0,0]}
  ],
  "manufacturing": {
    "operations":[{"operation_id":"operation-001","kind":"CUT","tool_profile_id":null,"material_profile_id":null,"machine_profile_id":"cricut-explore-5-unverified","verification":"PROFILE_REQUIRED"}],
    "dimension_policy":{"units":"mm","physical_dimensions_confirmed":false}
  },
  "resource_manifest":[{"path":"sources/source-original.png","sha256":"bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb","media_type":"image/png","role":"ORIGINAL","size_bytes":123456}],
  "command_log":{"format":"smartsvg-commands/1-draft","checkpoint_ref":null,"recent_receipts":[]},
  "proof_axes":{"auto":"NON_EXECUTE","windows":"NON_EXECUTE","design_space":"NON_EXECUTE","physical":"NON_EXECUTE"}
}
```

**Exemple purement illustratif, pas un manifeste ZIP V2 final :** les chemins `geometry/outline-001.svg`, `mask-pack-001` et `proof-subject-001` sont des références **à résoudre ou rejeter** lors de la validation ; ils ne désignent pas des ressources existantes dans cet exemple. Les champs `null` signifient « inconnu » et interdisent un prévol qualifié, pas « choisir automatiquement ». `verification` concerne le **profil de fabrication**, pas les preuves V3.3. L'extension doit définir un JSON Schema discriminé avant code ; les clés inconnues requises sont bloquantes, les extensions facultatives versionnées et conservées octet-à-octet ou refusées en écriture.

### 3.1. Identités, références et provenance

| Type | Autorité / contrainte | Comportement lors d'une migration |
|---|---|---|
| `project_id` | Identifiant logique existant, stable, non dérivé du nom de fichier | Inchangé lors de migration ; « Dupliquer » crée nouvel ID avec provenance explicite |
| `source_id` + SHA | Octets de source historique immuables | Reproduire octets et digest **sans réencodage** ; pas de substitution par preview |
| `mask_id` / `mask_ref` | ID et ressource du masque ; float32 est autorité G2.4 | Préserver l'ordre et les digests existants ; V2 autorise packs partitionnés **seulement après nouveau contrat et tests** |
| `subject_id` | ID G3.3e persistant si preuve exacte valide | Préserver sans re-générer ; si preuve absente ou incohérente, marquer `IDENTITY_REVIEW_REQUIRED` ; aucune association par similarité visuelle |
| `accessory_ids` | Liens explicites, sans auto-déduction | Vérifier références et absence de cycles avant commit |
| `object_id` | Futur ID d'objet de scène, indépendant du sujet | Créé à l'acceptation d'une transformation ; stable à l'undo/redo |
| `operation_id` | Futur identifiant d'opération typée Cut/Score/Draw/Print/Foil | Référence explicite, jamais déduite d'un simple trait SVG |
| `artifact_id` | Sortie dérivée, type de sortie distinct | Les artefacts historiques V1 sont préservés ; les nouveaux types passent par contrat V2 |
| `command_id` | Identité d'une intention validée, non de la source | Unique par projet + digest canonique de payload ; persistance atomique requise |
| `resource_ref` | Chemin POSIX interne vérifié, sans chemin absolu | Refus traversal, symlink, collisions Unicode/casse, MIME/extension trompeuse |

**Split/merge :** un sujet scindé ne donne pas silencieusement son ID à l'un des enfants ; créer de nouveaux IDs et un `lineage` explicite, garder l'ancien sujet dans l'historique. Une retouche de masque qui change les octets invalide la preuve d'identité exacte jusqu'à réconciliation contrôlée ; elle ne doit pas être maquillée en preuve « vérifiée ». Une édition purement graphique sans changement de masque conserve l'ID.

### 3.2. V1 et limites de volume

Les 50 sujets ne sont **pas** sérialisables comme un unique snapshot G2.4 V1 : 32 masques maximum et une source. Le V2 devra permettre une segmentation en packs vérifiables, par exemple 2 packs de 25, sans casser les relations d'ID ni imposer un traitement GPU unique. Les bornes ZIP V1 ne sont **pas** automatiquement relevées ; un budget V2 sera décidé après benchmark de mémoire, décompression et récupération. **Pas de stockage des poids IA, caches de rendu ou images personnelles dans un dépôt public.**

Les miniatures et dérivés régénérables sont en cache externe local (reconstructible), jamais autorité ; les ressources nécessaires à l'édition reproductible sont dans l'archive V2 avec digest, ou le projet est marqué explicitement `NON_PORTABLE` et l'utilisateur doit choisir de les intégrer avant partage. Pas de référence silencieuse vers un chemin privé absolu.

## 4. Machine d'états, commandes et protocole déterministe

### 4.1. Parcours débutant et expert (wireframes textuels)

**Novice :**
```text
[Reprendre un projet .smartsvg]  [État : compatible / migration nécessaire]
[Projet original conservé] [Créer une copie compatible V3.4] [Plus tard]
[Contrôle : sources OK | masques OK | IDs OK | place disque ?]
[Différences avant/après] [Migrer la copie] [Ouvrir dans Atelier]
[Échec ? Retour au projet original] [Rapport local sans données privées]
```

**Expert :**
```text
[Inspecteur] archive_schema | document_schema | SHA fichier | revision logique
[Entrées ZIP + SHA] [IDs/lineage] [Snapshots float32] [Command receipts]
[Dry-run] [Détail des changements] [Validation budget/sécurité]
[Exporter rapport expurgé] [Rejouer corpus synthétique] [Rollback]
```

L'interface ne présente jamais « Migration réussie » avant lecture et comparaison du fichier V2 publié. Si le migrateur n'est pas installé, elle affiche **Lecture seule V1** et garde le projet intact. Pas de boîte de dialogue IA obligatoire.

### 4.2. Contrats de commande/événement (à harmoniser au cycle 06)

- `InspectProject` : lecture non mutante, retourne `archive_schema`, `file_sha256`, `compatibility` et diagnostics expurgés ; événements `ProjectInspected` / `PROJECT_CORRUPT`.
- `PlanMigration` : calcule un plan **sans écrire** ; préserve les empreintes des ressources, estime l'espace disque, détecte types inconnus, collisions et preuves de sujet manquantes ; événements `MigrationPlanReady` / `MIGRATION_BLOCKED`.
- `MigrateCopy` : exige `expected_project_sha256`, destination neuve sûre et confirmation ; lit et valide V1, construit V2, publie atomiquement, relit et compare ; événements `MigrationCommitted` ou `MigrationFailed`. Ne touche jamais V1.
- `OpenReadOnly` : consultation d'un format futur non pris en charge **seulement** si un lecteur explicitement sûr existe ; sinon `UNSUPPORTED_PROJECT_SCHEMA`.
- `ApplyCommand` : sous writer unique, compare le SHA avant toute mutation ; rejette `STALE_PROJECT_SHA` ; exige la conservation des receipts et des preuves ; événement `ProjectCommitted` seulement après fsync/lecture de contrôle.
- `RestorePrevious` / `ResolvePendingRecovery` : confirmation explicite et SHA des sidecars ; aucune restauration automatique silencieuse.

**Pseudo-code de spécification (non exécuté) :**
```text
plan = inspect_v1_without_writing(path)
assert plan.source_sha256 == SHA256(source_bytes)
assert all(identity_proofs_are_verified_or_flagged(plan))
if plan.has_unsupported_required_data: return MIGRATION_BLOCKED
if plan.archive_budget_exceeded or plan.disk_space_unconfirmed: return MIGRATION_BLOCKED
under_single_project_lock:
    assert SHA256(v1_archive_bytes) == expected_project_sha256
    build_v2_in_new_temporary_destination(plan)
    validate_v2_schema_and_all_resource_digests()
    assert preserve_v1_source_bytes_and_stable_ids()
    publish_new_destination_atomically_without_overwriting_v1()
    reopen_and_verify_v2_against_plan()
return new_project_sha256, source_sha256_unchanged, migration_report
```

**Ordre des effets :** vérifier → proposer → confirmer → calculer sur snapshot → verrou + CAS → écrire copie temporaire → relire → publier → notifier. Une annulation avant publication laisse V1 inchangé et supprime le temporaire sûr ; une coupure après publication nécessite une inspection déterministe de la destination, pas une seconde migration aveugle. Un échec de fsync, un disque plein ou un fichier en lecture seule bloque l'opération, avec récupération explicite.

### 4.3. Révision, undo et idempotence

- **V1 :** `file_sha256` de l'archive entière = CAS ; aucune notion de compteur garanti. Un export dérivé ne change pas le SHA du projet.
- **V2 (proposé) :** `logical_revision` entier non négatif, incrémenté uniquement après commit durable ; `parent_revision_digest` + SHA archive relient l'historique ; ne pas exiger égalité entre digest du contenu et SHA des octets ZIP (compression et métadonnées peuvent différer).
- **Idempotence :** `command_id` + empreinte de payload canonique + résultat durable dans **la même transaction que la mutation** ; même ID/même payload renvoie le résultat déjà enregistré ; même ID/payload différent → `COMMAND_ID_CONFLICT`. Ne pas enregistrer le succès uniquement en RAM. Une compaction du journal doit garder une preuve d'ancrage et un registre de receipts suffisants ; si l'ID a expiré, **refuser une reprise ambiguë** plutôt que risquer une seconde mutation. Politique de rétention à arbitrer au cycle 06.
- **Undo/redo :** historique de commandes/snapshots versionnés, pas réécriture du masque source ; rollback d'un groupe d'opérations doit être transactionnel. Les anciens `operations.json` sont des données héritées, **pas** des receipts idempotents.
- **Jobs :** calcul IA/CPU hors verrou avec SHA épinglé ; avant acceptation comparer SHA source et identité des objets ; résultat périmé isolé, jamais appliqué à un projet plus récent.

## 5. Sécurité, licences, confidentialité, limites et erreurs

| Situation | Décision/fallback |
|---|---|
| ZIP hostile (traversal, doublons casse/NFC, bombes, membres inconnus, symlink) | Rejeter avant extraction et écriture ; aucune extraction aveugle |
| Archive V1 à 5 000 opérations ou près des budgets | Lecture possible si valide ; refuser mutation V1 dépassant les bornes ; proposer migration V2 seulement si validée |
| Ancien client réécrit une extension V34 inconnue | Interdire édition en V1 enrichi non qualifié ; préférer copie V2 ; test aller-retour exigé |
| Sujet avec preuve float32 manquante ou divergente | Ouvrir en lecture seule ou isoler sujet ; jamais rebind automatique |
| Deux sessions, SHA obsolète, disque plein, destination symlink | Échec contrôlé, pas de « last writer wins », aucun écrasement |
| Source originale manquante ou digest erroné | `SOURCE_INTEGRITY_FAILED`, bloquer fabrication et migration |
| IA absente, modèle non licencié, OOM | Aucune dépendance à l'IA pour ouvrir/migrer ; manuel/CPU, aucun téléchargement |
| Projet reçu d'un tiers | Aucun code embarqué exécuté, aucune URL ou chemin local suivi automatiquement ; rapports expurgés |
| Document futur plus récent | Refus explicite ou lecteur limité sécurisé, pas de downgrade silencieux |
| Partage d'un projet | Rapport des ressources externes manquantes ; aucun chemin privé ou cache involontairement embarqué |

**Licences :** le format projet ne transporte pas les poids de modèles ; conserver seulement ID/version, provenance et licence **déclarée non vérifiée** tant qu'une source officielle datée n'a pas été contrôlée. Les créations importées conservent leurs métadonnées de provenance sans publier de médias tiers dans le dépôt. Pas d'appel réseau nécessaire pour la migration.

**Performances cibles à mesurer, pas garanties :** ouvrir V1 petit projet ≤2 s sur SSD Windows ; plan de migration sans écriture ≤3 s hors gros médias ; UI réactive pendant hashing/validation ; pic RAM ≤2× budget d'archive sur corpus standard ; 50 sujets sans OOM sur profil CPU. Les cibles sont provisoires, dépendantes du matériel et des tailles ; elles doivent être ajustées par benchmarks reproductibles. Aucun GPU requis pour la migration.

## 6. Scénarios verticaux et cas limites

**A — 12 escargots → stickers :** conserver `source-original` et son SHA ; chaque masque reçoit un ID explicite, le sujet ne devient stable qu'après preuve ; placement A4 est un artefact dérivé avec dimensions en mm **confirmées**. Un réagencement n'altère ni l'original ni les masques. Export PNG Print Then Cut ≠ source vectorielle éditable. Si profil A4 inconnu, prévol « vérification externe nécessaire ».

**B — boîte carton → Score + Basic Cut :** aucun masque n'est obligatoire pour une création paramétrique ; le modèle V2 doit accepter un document purement géométrique. Chaque chemin de pli possède `operation_ref=SCORE` et chaque bord `CUT` ; le profil machine/outils/matière peut rester `INCONNU` jusqu'à validation. Export SVG + manifeste de consignes ; dans Design Space, configurer Score et Attacher manuellement. Le SVG n'est pas une commande machine.

**C — 50 sujets :** deux packs de 25 proposés à titre d'exemple de partition V2 ; ne pas injecter 50 masques dans le snapshot V1 limité à 32. Vérifier collisions, IDs et budget par pack, plus la cohérence globale de la planche.

**D — ancien projet G2.2/G2.4/G3.3e :** un projet V1 avec strokes `editor_v216`, masques float32, bindings d'identité et sidecars est ouvert sans mutation. Migration ne convertit jamais float32 en L8, ne réordonne pas les masques et ne change pas `subject_id`. Si une preuve n'est pas vérifiable, ne pas prétendre à une migration qualifiée.

## 7. Tests de recette spécifiés (aucun exécuté)

Chaque test devra avoir fixture synthétique/licite, commande exacte, SHA du code et résultat enregistré. Les axes de preuve restent indépendants : `auto` / `windows` / `design_space` / `physical` = `NON_EXECUTE` ici.

| ID | Assertion vérifiable | Axe futur |
|---|---|---|
| T-V34-05-01 | V1 valide ouvert sans écriture ; SHA archive identique avant/après | auto, Windows |
| T-V34-05-02 | Source PNG/JPEG/WebP conservée octet pour octet, digest identique après V1→V2 | auto |
| T-V34-05-03 | 12 IDs sujet G3.3e et preuves exactes préservés ; aucun ID réattribué | auto |
| T-V34-05-04 | Snapshot float32 round-trip bit-identique ; preview L8 ne devient jamais autorité | auto |
| T-V34-05-05 | V1 avec nouveau membre ZIP non déclaré rejeté, sans écriture | auto |
| T-V34-05-06 | ZIP traversal, collisions NFC/casse, symlink, bombes et double JSON key rejetés | auto |
| T-V34-05-07 | V1 au-delà de 256 entrées / 64 MiB membre / 256 MiB total / 4 MiB JSON rejeté | auto |
| T-V34-05-08 | V1 5 000 opérations reste lisible si valide ; mutation supplémentaire refusée | auto |
| T-V34-05-09 | Ancien chargeur V1 rejette V2 avec code explicite, sans corruption | auto |
| T-V34-05-10 | PlanMigration produit un diff déterministe et ne crée aucun fichier | auto |
| T-V34-05-11 | MigrateCopy n'écrase jamais V1 ; SHA original identique après succès et échec | auto, Windows |
| T-V34-05-12 | Coupure à chaque point de publication : soit aucune copie, soit V2 relisible ; V1 intact | auto, Windows |
| T-V34-05-13 | Deux écrivains et SHA périmé → un seul commit ; second `STALE_PROJECT_SHA` | auto, Windows |
| T-V34-05-14 | Retry même command_id/payload → un seul commit ; payload différent → conflit | auto, Windows |
| T-V34-05-15 | Job IA terminé après changement de projet → proposition isolée, zéro mutation | auto |
| T-V34-05-16 | Masque modifié avec preuve d'identité ancienne → `IDENTITY_REVIEW_REQUIRED` | auto |
| T-V34-05-17 | 50 sujets partitionnés : IDs uniques, aucun pack >32, aucune fuite de source | auto, Windows |
| T-V34-05-18 | Projet sans image, boîte Score/Cut : opérations typées persistées et prévol bloqué si profil inconnu | auto, Design Space |
| T-V34-05-19 | Export Print Then Cut ne modifie ni archive ni révision ; dimensions non confirmées → avertissement | auto, Design Space |
| T-V34-05-20 | Refus modèle IA/réseau et OOM : migration/lecture manuelles fonctionnent, aucun téléchargement | auto, Windows |

**Corpus futur pressenti (absent du dépôt) :** `tests/fixtures/v34_projects/{legacy_g22,legacy_g24,legacy_g33e,source_jpeg,source_webp,stale_sha,zip_bomb,case_collision,unknown_v2,mask_32,mask_50,box_score_cut,crash_pending,full_disk,readonly,duplicate_command}`. Produire des fixtures synthétiques et le manifeste de droits ; aucun média utilisateur/copyright dans le dépôt public.

**Preuves de terrain :** tests de lecture/migration V1/V2 : auto+Windows requis ; Design Space/physique **NON_APPLICABLE uniquement si justifié pour la migration elle-même**. Pour les scénarios sticker et boîte, la qualification d'export et fabrication est un gate distinct et demeure `NON_EXECUTE`, jamais déduite de la validité ZIP.

## 8. Backlog de micro-tickets proposés (nouveaux IDs uniques)

| Ticket / priorité | Dépendances héritées et V34 | Livrables/fichiers FUTURS (absents) | Test exact / preuve / Definition of Done |
|---|---|---|---|
| **V34-025 P0** Inventaire contractuel V1 et golden corpus | S-023, S-024, S-052, S-053, S-061 ; R33-001, R33-009 ; V34-001, V34-017 | `docs/roadmap-v3.4/specs/ARCHIVE_V1_CONTRACT.md`, `tests/fixtures/v34_projects/` | T-V34-05-01,05..08 ; auto ; DoD : contraintes réelles et SHA des fixtures répertoriés, zéro modification V1 |
| **V34-026 P0** Schéma V2 et validation stricte | S-052, S-053, S-061 ; R33-003, R33-008, R33-009 ; V34-011, V34-012 | `docs/roadmap-v3.4/schemas/project_v2.schema.json`, futur `engine/smartsvg_core/project_archive_v2.py` | T-V34-05-05..09,18 ; auto ; DoD : nouveaux types explicites, ancien lecteur refuse V2, aucun chemin hostile accepté |
| **V34-027 P0** Migrateur dry-run/copie et rollback | S-053, S-095 ; R33-009, R33-013 ; V34-018, V34-022 | `docs/roadmap-v3.4/specs/MIGRATION_V1_V2.md`, futur `engine/smartsvg_app/project_migrator.py` | T-V34-05-01..04,10..12 ; auto+Windows ; DoD : source V1 inchangée et V2 relue après publication, rollback vérifiable |
| **V34-028 P0** Identités et packs de masques V2 | S-023, S-028, S-052 ; R33-004..006 ; V34-012, V34-018 | `docs/roadmap-v3.4/specs/IDENTITIES_AND_MASK_PACKS.md`, futur `engine/smartsvg_core/mask_pack_v2.py` | T-V34-05-03,04,16,17 ; auto+Windows ; DoD : preuves float32 exactes, IDs stables, partition 50 sans dépasser V1 |
| **V34-029 P0** Révision/CAS, receipts et compaction | S-026, S-053, S-095 ; R33-004, R33-011..014 ; V34-013, V34-022 | `docs/roadmap-v3.4/specs/REVISION_AND_RECEIPTS.md`, futur `engine/smartsvg_app/command_journal.py` | T-V34-05-13..15 ; auto+Windows ; DoD : crash/retry non duplicateur, IDs expirés refusés, transaction atomique |
| **V34-030 P1** Inspecteur de projet et erreurs accessibles | S-069, S-074, S-084 ; R33-015 ; V34-024 | `docs/roadmap-v3.4/specs/PROJECT_INSPECTOR_UX.md`, futur `engine/web/js/smartsvg_project_inspector_v34.mjs` | T-V34-05-10,11,16,20 ; UI+Windows ; DoD : novice/expert, source non altérée, rapport expurgé et fallback manuel |
| **V34-031 P1** Portabilité et budget de ressources | S-017, S-041, S-042, S-061 ; R33-010, R33-013, R33-015 ; V34-025, V34-026 | `docs/roadmap-v3.4/specs/PROJECT_PORTABILITY.md`, futur `engine/smartsvg_app/resource_budget.py` | T-V34-05-02,06,07,17,19 ; auto+Windows ; DoD : aucun chemin absolu, cache reconstructible, diagnostics avant dépassement |

**Mapping bidirectionnel partiel du lot :** S-023/024/052/053/061/095 et R33-003/004/005/006/009/011/012/013/014/015 sont reliés ci-dessus aux tickets et tests ; les 141 exigences V3.3 restent présentes dans `HERITAGE_INDEX.md`. **La matrice bidirectionnelle exhaustive reste à produire** : absence de ligne ici ≠ exigence abandonnée. Aucun ticket ne passe à `IMPLEMENTE` par ce document.

## 9. Contre-expertise croisée, risques ouverts et décision

**Contrôles de conception :**
1. Format V1 strict vs V2 explicite : **résolu en proposition** ; pas de membres ZIP arbitraires dans V1.
2. `file_sha256` existant vs compteur logique futur : **distingués** ; pas de faux compteur V1.
3. 50 sujets vs snapshot 32 et source unique : **blocage V1 reconnu**, packs V2 à prototyper.
4. Identité G3.3e : ne pas utiliser SHA de preview L8 ou ordre pour reconstruire l'ID ; preuve float32 obligatoire.
5. Recovery : conserver sidecars et verrou existants ; aucune deuxième autorité.
6. Archive/ressources : limites de taille, profondeur, sécurité ZIP et format Artifact V1 non contournés.
7. Compatibilité fabrication : Score reste opération sémantique, non une ligne SVG auto-transmise.
8. Migration IA : zéro modèle requis, zéro réseau sans consentement.

**Questions ouvertes :** budget V2 exact (à mesurer), modèle de receipts compacts (cycle 06), choix de packaging natif (spike V34-019), protocole de sauvegarde atomique Windows V2, politique de partage/licence, mécanisme de reprise de projet si un futur client est plus récent, schéma JSON formel et preuve de round-trip avec corpus. **NO-GO pour déclarer V2 compatible ou migrateur opérationnel avant tests.**

**Décision :** conserver V1 comme base historique et proposer V2 opt-in à migration transactionnelle, sans modifier le moteur dans cette campagne. **Prochain micro-lot 06 :** bus de commandes, undo/redo, transactions, idempotence, gestion des jobs et concurrence, en prenant le SHA/CAS V1 et les receipts V2 de ce lot comme contraintes à qualifier.
