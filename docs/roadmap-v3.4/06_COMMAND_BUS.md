# SmartSVG Studio V3.4 — Lot 06 : commandes, historique, transactions, jobs et concurrence

**PROPOSITION DOCUMENTAIRE — 29 octobre 2026.** Cycle 06/24 ; référence active : V3.3, 141 exigences. Base main relue : fdbda304beb77d97340a8be4dd5c5e9cefde15f4 ; branche documentaire PR #73, issue #72 ; HEAD avant lot : 1b58db515973061e6ecdd5d099fe793d30a0aaa1. Tous les types, chemins, événements et tests ci-dessous sont **SPÉCIFIÉS**, non implémentés. Aucune preuve Windows, RTX 3070, Design Space ou physique.

## 1. Besoin, état réel, frontières et revue critique du lot 05

**Besoin :** les modes Express/Atelier/Fabrique/Vectoriel/Bibliothèque/Expert et l'assistant facultatif doivent partager **un projet canonique**, des commandes atomiques et un historique cohérent. Un glisser de pinceau, l'acceptation de 12 sujets, une assignation SCORE, un job de segmentation ou une fermeture brutale ne doivent jamais perdre une source ni appliquer deux fois une action.

**Code réel lu sur main :**
- engine/smartsvg_core/project_workspace_g22.py : ManagedWorkspace.update_notes, save_editor_document, save_base_masks, register_subject_identity utilisent un SHA-256 du fichier .smartsvg attendu, puis save_with_recovery ; plusieurs opérations construisent un nouvel objet LoadedProject **avant** l'acquisition du verrou d'écriture. Le CAS est recontrôlé **dans** save_with_recovery, ce qui évite la publication d'un snapshot obsolète, mais **ne fournit ni bus générique ni receipt durable**.
- engine/smartsvg_core/project_recovery.py : verrou OS non bloquant (msvcrt sous Windows, fcntl ailleurs), copie temporaire fsync, .pending-backup.smartsvg et .previous.smartsvg ; si le primaire est publié mais la rotation du secours échoue, l'appel peut signaler SAVE_FAILED tandis que la mutation est déjà durable. Le sidecar pending doit alors être résolu explicitement. **Cette ambiguïté succès/erreur est critique pour les retries.**
- engine/smartsvg_core/project_archive.py : archive V1 smartsvg-project/1, opérations historiques plafonnées à 5 000, ZIP validé, save_project relu avant publication ; ces opérations ne sont **pas** un journal de commandes idempotentes. engine/smartsvg_core/editor_session_g23.py limite une session à 400 strokes et 12 000 points ; engine/smartsvg_core/mask_snapshot_g24.py conserve les masques float32 exacts ; engine/smartsvg_core/subject_identity_g33e.py exige une preuve liée au masque.
- Lot 05 : V2 proposé, migration en copie, logical_revision distinct du SHA du fichier, receipts et packs encore à concevoir. **Correction** : ne pas stocker le SHA final du ZIP dans une receipt contenue dans ce même ZIP (circularité) ; ne pas supposer qu'un succès HTTP perdu signifie échec de commit.

**Non-objectifs du lot :** aucun code, aucune API de pilotage Cricut, aucune commande de fabrication envoyée à Design Space, aucune écriture dans V1 non prévue par ses writers, aucun modèle IA téléchargé, aucune garantie de fsync Windows sans essais. Les exports et les découpes physiques sont des effets **externes** et ne sont pas annulables par Undo.

## 2. ADR-034-07 — Un seul writer, calcul spéculatif hors verrou, CAS sous verrou (PROPOSÉ)

**Options :** (A) store UI comme autorité — REJET : plusieurs interfaces ; (B) base SQLite parallèle au .smartsvg — REJET comme autorité : double vérité ; (C) mutations sérialisées du document V2 dans un ZIP unique, reçus et historique inclus — **RECOMMANDÉ**, sous réserve du spike de performance/atomicité ; (D) événements en mémoire uniquement — REJET : crash après commit avant réponse.

**Pipeline de commit :**
1. Authentifier/autoriser l'acteur local, valider version, taille, schéma discriminé et politique de permissions ; aucune entrée d'IA ne saute cette validation.
2. Lire un snapshot immuable du projet, son SHA-256 archive et son logical_revision ; préparer la transformation déterministe et les ressources temporaires **hors verrou**. Les données volumineuses (masques) restent en fichiers temporaires privés contrôlés, non publiés.
3. Acquérir le **verrou OS du projet** ; lire et valider l'archive courante et les sidecars. Résoudre d'abord une éventuelle ambiguïté de commit (voir §4), sans effacer le pending.
4. Vérifier **d'abord** le receipt durable de command_id/epoch (pour traiter le retry après accusé perdu) ; même payload => réponse REPLAYED, payload différent => COMMAND_ID_CONFLICT ; epoch clôturée => COMMAND_EPOCH_CLOSED. **Ensuite** vérifier expected_project_sha256, logical_revision, dépendances d'identité et empreintes de ressources.
5. Si CAS périmé, rejeter STALE_PROJECT_SHA sans écriture, sauf éventuel recalcul explicitement demandé par l'utilisateur. Ne jamais faire de last-writer-wins ni rebind de sujet à partir de l'ordre des masques.
6. Appliquer le groupe atomique sur une copie du modèle ; valider invariants métier, topologie, références, budgets, provenance et limites du format ; produire la nouvelle archive **avec** mutation, receipt, historique et métadonnées d'événement dans **la même publication**.
7. Écrire temp sur le **même volume** ; fsync et relecture complète, publier selon un protocole V2 à qualifier par crash-injection Windows, conserver sidecars de récupération ; relire la publication avant de déclarer le commit confirmé. Ne pas réutiliser aveuglément le writer V1 pour un V2.
8. Calculer le **SHA final de l'archive publiée après publication** ; répondre avec SHA, logical_revision et état de récupération ; diffuser l'événement aux vues **après** commit. L'événement peut être redélivré, le store UI déduplique event_id ; en cas de trou, recharger le snapshot canonique.

**Ordre des validations sous verrou :** identité du projet et epoch → receipt/idempotence → CAS → préconditions métier → publication. Une erreur d'autorisation reste bloquante même pour un replay ; la réponse REPLAYED ne divulgue pas les détails d'une commande d'un autre acteur.

**Invariant :** l'archive V2 publiée est l'unique source de vérité. Sidecars, file de jobs, caches, UI et exports n'ont jamais le droit de devenir des auteurs concurrents du document. Une transaction peut regrouper plusieurs commandes (ex. 12 sujets), mais une seule révision est publiée.

## 3. Contrats de données et bus de commandes — SPÉCIFICATION

### 3.1 Enveloppe JSON proposée

~~~json
{
  "contract": "smartsvg-command/1-draft",
  "project_id": "boite-demo-01",
  "command_epoch": 2,
  "command_id": "e2-018fe9a8-0001",
  "actor": {"kind": "USER", "session_id": "session-local-01"},
  "expected_project_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "expected_logical_revision": 7,
  "kind": "AssignOperation",
  "payload": {
    "object_ids": ["fold-01", "fold-02"],
    "operation_kind": "SCORE",
    "profile_ref": null
  },
  "preconditions": [{"ref": "geometry/fold-01", "sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"}],
  "request_origin": "ATELIER"
}
~~~

**Contraintes :** command_epoch entier >=0, logical_revision entier >=0, SHA hex minuscule 64 caractères, command_id unique dans l'epoch et lié à celle-ci, session_id opaque local, actor.kind USER/SYSTEM/ASSISTANT_PROPOSAL. Les commandes mutantes de l'assistant sont **interdites** tant qu'une action utilisateur explicite n'a pas transformé la proposition en commande USER autorisée. Payload validé par JSON Schema discriminé, profondeur/volume bornés, nombres finis et unités mm explicites ; clés obligatoires inconnues = refus. Les chemins internes sont des références sûres, jamais des chemins absolus.

**Catalogue minimal proposé :** ImportSource, ConfirmIntent, AcceptSubjectsBatch, EditMaskStrokeGroup, SetObjectTransform, AssignOperation, SetFabricationProfile, CreateParametricTemplate, Undo, Redo, CommitCheckpoint, SaveProjectCopy. Les commandes de consultation/planification (Inspect, Preview, PlanExport, RequestJob, CancelJob) n'incrémentent pas la révision. MigrateCopy est une transaction **sur une destination neuve**, non un Undo du projet original. Toute commande de fabrication agit sur des opérations sémantiques ; AssignOperation(SCORE) ne transmet rien à la machine.

**Événements :** CommandCommitted, CommandReplayed, CommandRejected, UndoCommitted, RedoCommitted, CheckpointCommitted, JobProposed, JobStale, JobCancelled, RecoveryRequired, SnapshotChanged. event_id stable dérivé de project_id + logical_revision + command_id + kind (digest canonique), jamais d'un timestamp seul. Un événement est une **notification** ; le consommateur doit relire l'autorité si l'ordre manque. Aucun événement n'est une preuve Cricut.

### 3.2 Receipt durable, état, sans circularité

~~~json
{
  "command_epoch": 2,
  "command_id": "e2-018fe9a8-0001",
  "payload_sha256": "cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc",
  "actor_scope": "local-session-scope",
  "outcome": "COMMITTED",
  "logical_revision": 8,
  "state_digest": "dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd",
  "result_ref": "receipts/result-0008.json",
  "event_id": "event-project-0008",
  "timestamp_utc": "2026-10-29T03:53:00Z"
}
~~~

Le payload_sha256 porte sur une **sérialisation canonique définie et versionnée** de kind + payload + preconditions + project_id + epoch ; exclure champs de transport variables et sérialisation ZIP. state_digest porte sur le modèle logique canonique **hors receipt/ZIP**, et ne vaut ni SHA du ZIP ni preuve physique. L'horodatage est indicatif, non un critère d'unicité. Le result_ref ne peut référencer que des données bornées embarquées dans le manifeste validé. Le SHA du ZIP publié est calculé **après** publication et retourné dans la réponse, sans le réinjecter dans la même archive.

**États de réponse :** COMMITTED, REPLAYED, REJECTED, COMMITTED_NEEDS_RECOVERY, UNKNOWN_AFTER_INTERRUPTION. Ne pas convertir automatiquement UNKNOWN en « échec sans effet ». Les erreurs de type PROJECT_LOCKED, STALE_PROJECT_SHA, COMMAND_ID_CONFLICT, COMMAND_EPOCH_CLOSED, RECEIPT_CAPACITY_EXCEEDED, IDENTITY_REVIEW_REQUIRED, PROJECT_RECOVERY_REQUIRED, DISK_FULL, READ_ONLY, INVALID_OPERATION sont des codes à spécifier/mapper, **pas** des erreurs déjà disponibles en V1.

## 4. ADR-034-08 — Idempotence, compaction et crash recovery (PROPOSÉ)

**Problème insoluble par un simple TTL :** effacer un receipt puis accepter le même command_id peut rejouer une modification. Le journal V2 ne doit **jamais** supprimer des IDs anciens et les accepter silencieusement.

**Stratégie proposée : epoch clôturable + receipts bornés.** Un projet stocke command_epoch_active, closed_epoch_before et les receipts de l'epoch active ; chaque commande porte explicitement l'epoch. Un checkpoint atomique augmente l'epoch, clôture toutes les anciennes, conserve une empreinte d'ancrage de l'historique et le snapshot, puis peut compacter les anciens receipts. Toute requête avec epoch < active est **rejetée COMMAND_EPOCH_CLOSED**, même si son command_id a disparu ; jamais « probablement nouveau ». Un client doit recharger epoch + SHA avant de créer une nouvelle commande ; un retry ancien n'est jamais réétiqueté automatiquement avec une nouvelle epoch. Les IDs nouveaux incluent le préfixe d'epoch et sont créés localement sans ambiguïté. Limite initiale **proposée à mesurer** : 2 000 receipts par epoch et 10 MiB de métadonnées de receipts ; au plafond, bloquer les mutations et proposer un checkpoint explicite, sans effacer les preuves ni forcer une compaction silencieuse. Une commande de checkpoint a elle-même un receipt durable dans la nouvelle epoch, avec liaison à l'ancienne ; tester crash entre les deux.

**Historique Undo distinct de l'index de receipts.** Clôturer une epoch n'efface pas automatiquement les inverses nécessaires à Undo. Les snapshots/patchs de l'historique sont bornés par quota distinct, la rétention est affichée, et toute purge est explicitement consentie. Si le budget V2 n'est pas suffisant, proposer « enregistrer une copie / checkpoint avec perte d'ancien Undo annoncée » plutôt qu'un dépassement ZIP silencieux. Ne jamais garantir un Undo illimité.

**Ambiguïté observée dans V1 :** publication primaire réussie + échec rotation previous => SAVE_FAILED possible avec pending encore présent. Pour V2, après exception, inspecter **sous verrou** primaire/pending et rechercher le receipt. Si primaire valide et receipt présent : répondre COMMITTED_NEEDS_RECOVERY, **interdire toute nouvelle mutation** jusqu'à résolution explicite du pending ; si primaire identique à l'ancien et receipt absent : REJECTED sans effet ; si état indécidable : UNKNOWN_AFTER_INTERRUPTION + inspecteur/récupération, jamais retry aveugle. Une lecture seule et l'export d'un rapport expurgé restent possibles si sûrs. Ne pas supprimer le pending automatiquement.

**Idempotence ≠ exactly-once réseau :** seul l'effet sur l'archive peut être appliqué au plus une fois par command_id/epoch ; livraison d'événements et appels UI peuvent être répétés. Les exports de fichiers externes et opérations physiques sont exclus de cette garantie, avec manifestes de provenance distincts.

## 5. ADR-034-09 — Undo/Redo transactionnels, non destructifs (PROPOSÉ)

**Option A :** inverser seulement les commandes à partir de paramètres → risque de perte pour masques float32 et évolution d'algorithme. **Option B :** snapshot complet à chaque geste → coûts ZIP/RAM excessifs. **Option C recommandée :** journal de commandes typées + patches avant/après sur ressources modifiées (références content-addressed) + checkpoints bornés, testés en round-trip bit-à-bit pour les masques. Ne pas utiliser la preview L8 comme inverse du float32.

**Règles :** un groupe de coups de pinceau forme **une unité d'Undo** après validation ; les gestes intermédiaires ne sont pas des commits durables indépendants. Une commande Undo crée une **nouvelle révision**, conserve une entrée historique de compensation et remet exactement les ressources/assignations du groupe précédent ; Redo réapplique un patch vérifié. Toute nouvelle édition après Undo invalide la branche Redo, mais pas les preuves d'audit. Les objets et IDs restent stables sauf split/merge explicitement modélisé. Après Undo d'un masque, recalculer/vérifier les preuves float32/subject_id ; ne jamais présenter une preuve périmée comme validée. Annuler AssignOperation(SCORE) restaure l'assignation antérieure sans effacer le chemin géométrique. Un groupe avec CUT et SCORE doit être restauré **en entier**.

**Interdictions :** Undo ne supprime ni impression, ni export déjà remis à Design Space, ni découpe physique ; le guide UI le dit explicitement. Un Undo sur révision périmée => STALE_PROJECT_SHA, pas de fusion implicite. Pour une action IA, seule l'acceptation utilisateur est annulable ; une proposition non acceptée ne modifie pas le projet.

**Quotas à mesurer :** 100 groupes récents conservés par défaut, et budget de patches configurable dans les bornes de V2 ; ces chiffres sont **hypothèses**, pas capacités testées. Au dépassement, proposer checkpoint, export de copie ou refus sûr, jamais écrasement silencieux.

## 6. Jobs CPU/GPU, concurrence, annulation et reprise

**Machine d'états proposée :** QUEUED → RUNNING → PROPOSAL_READY → ACCEPTED/REJECTED ; branches CANCEL_REQUESTED → CANCELLED ou COMPLETED_BEFORE_CANCEL ; FAILED_RECOVERABLE, FAILED_FINAL, STALE, INTERRUPTED. Le passage RUNNING→CANCEL_REQUESTED n'implique pas arrêt immédiat ; un résultat tardif est ignoré si token de génération révoqué. Un job n'est **jamais** un writer de projet.

**JobSpec minimal :** job_id, project_id, pinned_project_sha256, pinned_logical_revision, input_resource_sha256[], model_id/version/licence_status (ou MANUAL), provider/runtime, requested_operation, generation_token, resource_budget, output_contract, consent_flags. Sortie : ProposalBundle avec digest des ressources temporaires, TTL local, provenance et diagnostics, jamais une archive canonique. Ne pas empiler deux modèles sur RTX 3070 8 Go sans budget vérifié ; OOM => unload/fallback CPU/manuel, **aucune** modification de projet. Aucun téléchargement de modèle implicite.

**Ordonnancement :** file bornée, priorité interactive > batch, fairness pour les jobs longs, budget CPU/RAM/VRAM par fournisseur, backpressure ; estimation p95 à mesurer. L'annulation libère les ressources temporaires quand le worker confirme son arrêt, sans effacer les ressources déjà validées du projet. Une reprise après crash relit snapshot/ressources, **ne réexécute jamais silencieusement** une IA non déterministe ou un téléchargement ; demande un nouveau lancement explicite, et un job_id de reprise lié à la tentative précédente.

**Conflit à l'acceptation :** si pinned SHA ou empreinte d'objet a changé, proposition STALE, aucune mutation. Proposer comparer/relancer sur la nouvelle révision ou copier le résultat dans un brouillon **isolé**, sans rebind automatique d'identité. Si le projet est inchangé, l'acceptation passe par le CommandPort normal et reçoit receipt/Undo. Deux fenêtres concurrentes lisent le même snapshot ; un seul CAS peut publier ; la seconde voit un message compréhensible « projet modifié ailleurs » et recharge après choix utilisateur.

**Exemples :** 12 escargots : détection/masques proposés par job, validation utilisateur, AcceptSubjectsBatch atomique, 12 IDs/proofs contrôlés ; réarrangement de planche = commande distincte, export PNG non mutant. Boîte : génération paramétrique déterministe, groupe AssignOperation(CUT/SCORE), Undo restaure l'ensemble ; Design Space exige toujours sélection manuelle Score et Attacher. 50 sujets : lots de calcul avec propositions partielles, jamais 50 masques injectés dans un snapshot V1 limité à 32 ; consolidation V2 uniquement après validation des packs.

## 7. UX novice/expert, accessibilité et messages

**Novice — Express/Atelier :**
~~~text
[Projet : enregistré r8] [Annuler ↶] [Rétablir ↷] [Historique ▾]
[Image/planche] [Aperçu avant/après] [12 sujets proposés — Confirmer]
[Analyse en cours : Annuler le calcul] [Continuer manuellement]
[Conflit : ce projet a changé] [Comparer] [Recharger] [Conserver mon brouillon]
[Récupération nécessaire] [Inspecter les sauvegardes] [Ne rien écraser]
~~~

**Expert — panneau partagé :**
~~~text
Project: file_sha256 | logical_revision | epoch | pending/previous
Command: id | payload_digest | actor | receipt | undo_group | event_id
Jobs: pinned_sha | provider | resource_budget | state | stale_reason
[Diff de groupe] [Rejouer un test synthétique] [Exporter rapport expurgé]
~~~

**Comportement :** mêmes commandes dans toutes les vues, raccourcis clavier et libellés FR, focus conservé après Undo, progression non bloquante, bouton d'annulation distinct de Undo, confirmations seulement si elles changent le résultat. Aucun succès visuel avant confirmation durable. Prévisualiser l'inverse d'un groupe ne modifie pas l'archive ; une vue d'historique ne garantit pas l'Undo d'un export externe. L'assistant propose des actions, ne clique pas à la place de l'utilisateur.

## 8. Sécurité, quotas, performances, rollback

**Menaces :** payload JSON malformé, double clé, NaN/Inf, path traversal, archive ZIP hostile, session usurpée, commande rejouée, requête périmée, symlink de sidecar, échec de fsync, corruption d'un patch, fuite de média dans diagnostic, GPU OOM, téléchargement non consenti. Validateurs déterministes fail-closed ; autorisations côté moteur et adaptateur ; origine locale vérifiée ; aucune exécution de script ou URL contenue dans un projet. Le bus n'expose pas directement le ManagedWorkspace sur un serveur HTTP non authentifié. Un modèle IA n'est pas une autorité.

**Cibles de benchmark proposées (non mesurées) :** 100 mutations légères p95 <150 ms pour réponse UI *optimiste de prévisualisation* ; commit durable chronométré séparément et jamais présenté comme déjà fini ; annulation visuelle <250 ms ; aucune attente GPU sur thread UI ; tests d'au moins 100 points d'injection de crash aux étapes préparation, lock, temp, fsync, rename, relecture, backup, receipt, émission événement. Mesurer CPU, RAM, disque et Windows NTFS ; ne pas promettre les mêmes propriétés sur lecteurs réseau/exFAT.

**Rollback :** désactiver le CommandPort V2, garder V1 en lecture/écriture historique selon ses writers existants, ouvrir V2 en lecture seule si lecteur sûr disponible ; aucun downgrade silencieux. Les copies V1 et archives gelées restent inchangées. La perte de l'UI native n'empêche pas d'utiliser le transport ComfyUI historique. Un projet V2 jamais validé ne peut pas être étiqueté STABILISE.

## 9. Recette proposée — TOUS TESTS NON EXECUTES

Chaque test devra préciser fixture synthétique autorisée, commit, OS, mode, journal des assertions et preuve. Axes indépendants : auto / Windows / DesignSpace / physique ; le test de commandes ne vaut pas essai machine.

| Test | Assertion exacte | Axe futur |
|---|---|---|
| T-V34-06-01 | même command_id, epoch, payload après perte d'ACK → 1 seule révision et réponse REPLAYED | auto, Windows |
| T-V34-06-02 | même ID et payload différent → COMMAND_ID_CONFLICT, SHA inchangé | auto |
| T-V34-06-03 | retry d'une commande déjà commitée avec ancien expected SHA → REPLAYED, pas STALE | auto |
| T-V34-06-04 | commande inconnue avec ancien expected SHA → STALE_PROJECT_SHA, aucune écriture | auto, Windows |
| T-V34-06-05 | 2 writers concurrents → exactement 1 commit, second refus CAS | auto, Windows |
| T-V34-06-06 | publication réussie + échec backup → receipt présent, COMMITTED_NEEDS_RECOVERY, pending conservé | auto, Windows |
| T-V34-06-07 | publication absente + erreur → receipt absent, SHA inchangé, pas de faux succès | auto |
| T-V34-06-08 | état indécidable après crash → UNKNOWN_AFTER_INTERRUPTION, aucune répétition automatique | auto, Windows |
| T-V34-06-09 | checkpoint ferme epoch N ; commande N tardive refusée même sans receipt | auto |
| T-V34-06-10 | checkpoint interrompu ne produit jamais une epoch active ambiguë après inspection | auto, Windows |
| T-V34-06-11 | plafond de receipts atteint → RECEIPT_CAPACITY_EXCEEDED sans suppression silencieuse | auto |
| T-V34-06-12 | digest logique indépendant du SHA ZIP ; receipt ne contient pas de SHA ZIP autoréférent | auto |
| T-V34-06-13 | Undo/Redo 1 stroke float32 → bytes identiques avant/après round-trip | auto |
| T-V34-06-14 | Undo groupe CUT+SCORE restaure toutes assignations, aucun chemin perdu | auto |
| T-V34-06-15 | nouvelle édition après Undo invalide Redo sans supprimer la piste d'audit | auto |
| T-V34-06-16 | Undo d'un masque modifié invalide/revalide explicitement preuves sujet | auto |
| T-V34-06-17 | job IA r8 fini après commit r9 → STALE, 0 mutation | auto, Windows |
| T-V34-06-18 | CancelJob pendant RUNNING puis résultat tardif → proposition non acceptée | auto |
| T-V34-06-19 | OOM GPU simulé → job FAILED_RECOVERABLE, archive et original inchangés | auto, Windows |
| T-V34-06-20 | reprise après crash ne télécharge/rejoue pas modèle IA sans consentement | auto, Windows |
| T-V34-06-21 | 12 sujets acceptés en un groupe : 12 IDs valides ou 0 ; Undo groupé | auto |
| T-V34-06-22 | 50 sujets partitionnés en packs V2 : aucun pack V1 >32, aucun doublon ID | auto |
| T-V34-06-23 | émission événement interrompue → rechargement UI reconstruit r+1 sans double effet | UI, Windows |
| T-V34-06-24 | Score/Draw/Print ne se transforment jamais en CUT lors de Undo/Redo | auto, DesignSpace (plus tard) |
| T-V34-06-25 | rapport expurgé n'expose ni chemin privé ni média/poids IA | auto, Windows |
| T-V34-06-26 | deux interfaces reçoivent même état canonique, et perte d'événement déclenche resync | UI, Windows |
| T-V34-06-27 | tentative assistant sans confirmation utilisateur → aucune commande mutante | auto, UI |
| T-V34-06-28 | disque plein, lecture seule, symlink et ZIP hostile → aucun projet source détruit | auto, Windows |

**Corpus futur, non présent :** tests/fixtures/v34_commands/{lost_ack,duplicate_id,stale_cas,dual_writer,pending_backup,checkpoint_crash,epoch_closed,receipt_limit,float32_undo,score_cut_undo,job_stale,job_cancel,oom_simulated,12_subjects,50_subjects,malicious_archive,full_disk}. Fixtures générées sans médias protégés. Pour la fabrication physique : tests de commandes **NON_APPLICABLE** si justifié, mais tests des exports Score/Print Then Cut restent **NON_EXECUTE** tant que Design Space/Explore 5 n'ont pas été utilisés.

## 10. Micro-tickets de conception V34-032 à V34-040

Chaque DoD exige tests **effectivement exécutés** sur les axes annoncés lors de l'implémentation future ; l'état actuel de tous ces tickets est **SPECIFIE**, non IMPLEMENTE.

| Ticket / priorité | Dépendances historiques et V34 | Livrables FUTURS, non existants | Tests / preuve / DoD / rollback |
|---|---|---|---|
| **V34-032 P0** Contrats de commandes et validateurs | S-003, S-008, S-053 ; R33-003..005 ; V34-011,013,026 | docs/roadmap-v3.4/schemas/command_v1.schema.json ; futur engine/smartsvg_app/command_contracts.py | T-V34-06-02,04,12,27 ; auto ; DoD : schéma strict, aucune écriture IA directe ; rollback bus désactivé |
| **V34-033 P0** Writer unique CAS et publication | S-026, S-053, S-095 ; R33-009,013,014 ; V34-022,027,029 | docs/roadmap-v3.4/specs/WRITER_TRANSACTION.md ; futur engine/smartsvg_app/project_writer_v2.py | T-V34-06-04..08,28 ; auto+Windows ; DoD : un commit au plus, pending récupérable ; rollback V1 historique |
| **V34-034 P0** Receipts/epoch/compaction | S-053, S-095 ; R33-011,012,014 ; V34-013,029 | docs/roadmap-v3.4/specs/RECEIPTS_EPOCH.md ; futur engine/smartsvg_app/receipt_store.py | T-V34-06-01..03,09..12 ; auto+Windows ; DoD : aucun retry ancien réappliqué ; rollback refuser mutations V2 |
| **V34-035 P0** Undo/Redo patches float32 | S-008, S-023, S-052 ; R33-004,006 ; V34-028,032 | docs/roadmap-v3.4/specs/UNDO_HISTORY.md ; futur engine/smartsvg_app/history.py | T-V34-06-13..16,21 ; auto ; DoD : bit-identité float32, groupes atomiques ; rollback lecture seule historique |
| **V34-036 P0** Orchestrateur jobs et garde-fous | S-027, S-028, S-070 ; R33-005,007,011,012,017 ; V34-016,021,023 | docs/roadmap-v3.4/specs/JOBS.md ; futur engine/smartsvg_app/job_scheduler.py | T-V34-06-17..20,27 ; auto+Windows, RTX après équipement ; DoD : aucun worker n'écrit le projet ; rollback manuel/CPU |
| **V34-037 P0** Reconnexion UI et événements | S-067, S-069, S-074 ; R33-003,014,019 ; V34-015,024,032 | docs/roadmap-v3.4/specs/EVENTS.md ; futur engine/smartsvg_app/event_port.py | T-V34-06-23,26 ; UI+Windows ; DoD : perte/rejeu d'événement sans divergence ; rollback rechargement complet |
| **V34-038 P1** Historique groupé et aperçu d'Undo | S-008, S-071, S-074 ; R33-019 ; V34-035,037 | docs/roadmap-v3.4/specs/HISTORY_UX.md ; futur engine/web/js/smartsvg_history_v34.mjs | T-V34-06-13..15,23 ; UI+Windows ; DoD : geste unique réversible, pas de faux Undo physique ; rollback UI sans timeline |
| **V34-039 P1** Boîte de réception des propositions périmées | S-027, S-028, S-069 ; R33-005,007 ; V34-036,037 | docs/roadmap-v3.4/specs/PROPOSAL_INBOX.md ; futur engine/web/js/smartsvg_proposal_inbox_v34.mjs | T-V34-06-17,18,20,27 ; UI+Windows ; DoD : comparer/relancer, zéro rebind automatique ; rollback abandon sûr |
| **V34-040 P0** Banc de crash et concurrence | S-053, S-095 ; R33-009,011..014 ; V34-025,027,033,034 | docs/roadmap-v3.4/specs/CRASH_MATRIX.md ; futur tests/test_v34_transactions.py | T-V34-06-01..12,23,28 ; auto+Windows ; DoD : preuves horodatées, 100 points d'injection, pas de corruption ; rollback NO-GO writer V2 |

**Traçabilité partielle explicitée :** S-003/008/023/026/027/028/052/053/067/069/070/071/074/095 et R33-003..007/009/011..014/017/019 sont liés aux tickets/tests ci-dessus ; le registre historique HERITAGE_INDEX.md conserve les 141 lignes. La matrice inverse **141 → tickets/tests ou justification** reste à finaliser au cycle 23 ; absence de lien dans ce lot n'est pas suppression.

## 11. Auto-contre-expertise, décisions et prochain lot

**Incohérences détectées et résolues en proposition :**
1. Cycle 03 attendait expected_revision numérique ; V1 réel n'a que le SHA : le bus exige expected_project_sha256, et n'ajoute expected_logical_revision qu'en V2.
2. Cycle 05 suggérait receipts compacts sans stratégie d'expiration : epoch clôturée empêche la réexécution après compaction ; **politique à éprouver** sur migration et copies.
3. Un SHA final du ZIP dans son propre receipt est circulaire : remplacer par state_digest logique + SHA retourné après publication.
4. SAVE_FAILED historique peut masquer un commit durable : introduire COMMITTED_NEEDS_RECOVERY et UNKNOWN_AFTER_INTERRUPTION, sans retry aveugle.
5. Undo par simple inverse algébrique perdrait les float32 : patches exacts et vérification de preuve sujet.
6. Un job n'est pas une commande de mutation : résultats isolés jusqu'à Accept... avec CAS ; une IA locale n'a pas d'accès writer.
7. Un export/une coupe réelle ne peuvent pas être « annulés » par une transaction locale.
8. Une promesse d'atomicité Windows sans crash-injection serait infondée : gate Windows encore ouvert.

**Questions ouvertes / spikes obligatoires :** sérialisation canonique et hashing stable entre runtimes ; bornes V2 et coût des patches ; stratégie de publication/backup sous Windows, antivirus et disque réseau ; sémantique des epochs après duplication/migration ; capacité d'un UI à se resynchroniser ; quotas GPU et OOM ; traitement 50 sujets ; démonstration réelle du bus via tests. L'architecture est **proposée**, non approuvée. Aucun test n'a été exécuté durant la rédaction.

**Prochain micro-lot 07 :** accueil Importer/Créer/Reprendre, Express et navigation ; utiliser le bus commun pour concevoir les états UI, confirmations, raccourcis, récupération, sans créer un second store ni masquer les conflits.
