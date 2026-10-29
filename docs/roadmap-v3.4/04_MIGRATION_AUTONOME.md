# SmartSVG V3.4 — Lot 04 : migration incrémentale vers runtime autonome et adaptateur ComfyUI

**DRAFT de spécification, 29 octobre 2026 ; aucune implémentation.** Roadmap **active** : V3.3, 141 exigences conservées. Base `main@fdbda304beb77d97340a8be4dd5c5e9cefde15f4`. PR documentaire #73, branche `codex/docs-roadmap-v3-4-campaign`. Annexe de dépendances : [04_DEPENDENCY_INVENTORY.md](04_DEPENDENCY_INVENTORY.md). Le code historique, les archives, les workflows et les planifications ne sont pas modifiés.

## 1. Problème et résultat vérifiable

**Aujourd'hui, vérifié par lecture de code :** `ManagedWorkspace` et le format `smartsvg-project/1` sont relativement indépendants de ComfyUI, mais `engine/__init__.py` charge la chaîne historique des nœuds ; la passerelle `project_routes_g22.py` dépend d'`aiohttp` et du serveur ComfyUI ; plusieurs fournisseurs IA accèdent à `nodes.NODE_CLASS_MAPPINGS`. L'Atelier HTML possède des imports de l'API ComfyUI et des échanges `BroadcastChannel`. L'interface 12 escargots est encore une démonstration ; les modèles locaux et les résultats Windows/Cricut ne sont pas qualifiés.

**Résultat V3.4 attendu :** même `.smartsvg` et mêmes identifiants/ressources via une façade applicative unique, avec deux transports : `ComfyUITransport` conservant les workflows historiques et `NativeTransport` pour un exécutable local utilisable sans serveur ComfyUI. Les moteurs déterministes sont réutilisés ; IA facultative, aucun téléchargement implicite, original immuable. **L'existence du port ne prouve pas sa disponibilité réelle.**

**Non-objectifs de ce lot :** coder l'application, choisir définitivement Qt/Tauri, changer les nœuds ou leurs ports, migrer automatiquement les projets, garantir des performances RTX 3070, piloter Design Space ou la machine, déclarer un modèle IA licencié.

## 2. Contre-expertise explicite du lot 03 — ADR-034-01 à 04

| ADR | Décision maintenue | Correction / condition avant implémentation |
|---|---|---|
| 034-01 autorité unique | **CONSERVER** `ManagedWorkspace` et archive `.smartsvg` | Révision historique = **SHA-256 du fichier** ; `expected_revision: number` du lot 03 n'est pas encore un compteur persistant. Utiliser `expected_project_sha256` comme CAS initial ; compteur monotone facultatif **seulement après migration**. |
| 034-02 fabrication typée | **CONSERVER** géométrie ≠ opération | Contrat minimal stable entre transports ; Score demeure intention, pas opération automatiquement reconnue par Design Space ; la compatibilité outil/matière reste `UNKNOWN` jusqu'au profil validé. |
| 034-03 choix UI différé | **CONSERVER** comparaison par spikes | Ne pas confondre HTML autonome `file://` et UI ComfyUI. Prototype Qt/PySide6 vs Tauri+Python doit mesurer startup, taille, maintenance, IPC, accessibilité, packaging Windows, reprise, sécurité. |
| 034-04 IA non autoritaire | **CONSERVER** propositions réversibles | Tout fournisseur doit déclarer `requires_comfyui`, `network_side_effects`, `model_id`, `licence_status` et `can_run_cpu`; appel bloqué sans consentement réseau et sans licence qualifiée. |

**Incohérence résolue en conception :** `project_archive.py` n'a pas de compteur de révision durable universel ; le `CommandEnvelope` du cycle 03 est amendé par le présent lot (et sera consolidé aux cycles 05–06). Il ne faut pas prétendre que la V3.3 stocke déjà des événements idempotents.

## 3. Alternatives et arbitrage ADR-034-05 (PROPOSÉ)

| Option | Bénéfice | Coût/risque | Décision |
|---|---|---|---|
| Réécriture intégrale en application de bureau | Cohérence théorique | Régressions, perte de contrats et d'historique, gros lot invérifiable | **REJET** |
| Deux applications avec projets copiés/synchronisés | Prototypage facile | Double autorité, conflits et masques divergents | **REJET** |
| **Strangler / ports et adaptateurs** autour du noyau existant | Parité testable, rollback par capacité, maintien des anciens nœuds | Façade et tests dual-run à concevoir | **RECOMMANDÉ sous gates** |
| Exposer `project_routes_g22` tel quel sur localhost | Réutilisation immédiate de l'UI | GET non authentifiés par SmartSVG, héritage ComfyUI, surface réseau | **INTERDIT en natif sans durcissement** |

**Décision conditionnelle :** `ProjectAuthority` reste unique et sérialise toutes les mutations ; la façade n'exécute aucun code tiers directement. `NativeTransport` est en priorité **IPC/in-process** à privilèges minimaux ; un service HTTP local ne sera accepté qu'après un spike sécurité, liaison loopback explicite et authentification GET/POST. Les deux transports ne doivent pas écrire simultanément le même fichier sans verrou et CAS communs.

## 4. Frontières, ports et composants futurs

```text
Desktop UI (Express/Atelier/Fabrique/...) ─┐
                                            ├── TransportPort.dispatch(CommandEnvelope)
Historical ComfyUI nodes / UI ─────────────┘             │
                                  ApplicationFacade (validation, permissions, job registry)
                                                         │
                            ProjectPort (unique writer, CAS SHA, recovery, snapshots)
                                                         │
                      LoadedProject smartsvg-project/1 + future versioned extensions
                              │             │              │
                         ComputePort    AIProviderPort   ExportPort
                        CPU/determin.  optional         derived only
                              └────── proposals + provenance ──────┘
```

**Fichiers existants à réutiliser (ne pas les remplacer par copie) :** `engine/smartsvg_core/{project_contracts,project_archive,project_workspace_g22,project_recovery,mask_snapshot_g24,subject_identity_g33e,mask_binding_g33e,editor_session_g23}.py` ; `engine/project_routes_g22.py` reste historique ; `engine/smartsvg_ai/{auto_masks_v2111,provider_v2112}.py` sont à séparer en algorithmes et providers. `engine/smartsvg_vector/layers_v2113.py` contient une fonction de sauvegarde dépendante de `folder_paths` : l'export natif utilisera un port de destination sûre.

**Fichiers futurs proposés (n'existent pas) :**
- `engine/smartsvg_app/contracts.py` : schémas de commandes/résultats et erreurs stables ;
- `engine/smartsvg_app/facade.py` : orchestration et permissions ;
- `engine/smartsvg_app/project_port.py` : adaptateur `ManagedWorkspace`, révision SHA et recovery ;
- `engine/smartsvg_app/adapters/native_transport.py` : transport IPC local ;
- `engine/smartsvg_app/adapters/comfy_transport.py` : wrapper conservateur des nœuds/routes existants ;
- `engine/smartsvg_app/jobs.py` : planificateur de calculs non mutateurs, snapshots épinglés ;
- `engine/smartsvg_app/providers.py` : sélection de fournisseurs, aucun modèle par défaut ;
- `engine/smartsvg_app/exports.py` : dérivation de sorties et manifeste ;
- `tools/architecture/build_import_graph.py` : futur audit d'imports à SHA épinglé ;
- `tests/v34/test_transport_parity.py`, `test_native_bootstrap.py`, `test_migration_rollback.py`, `test_security_boundary.py` : tests futurs, **non créés**.

Ces noms sont des **interfaces pressenties** : le cycle 05 peut préciser le schéma sans autoriser l'implémentation.

## 5. Contrat d'appel commun (spécification JSON)

```json
{
  "contract": "v34.command/0.2-draft",
  "command_id": "cmd-0042",
  "project_id": "demo-local-01",
  "expected_project_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "actor": "user",
  "operation": "ProposeMasks",
  "payload": {"source_id":"source-original","mode":"MANUAL","requested_subjects":12},
  "capabilities": {"allow_network":false,"allow_model_install":false},
  "job": {"cancel_token":"cancel-0042","deadline_ms":30000}
}
```

**Contraintes de validation :** `command_id` et `project_id` syntaxiquement bornés ; SHA-256 64 hexadécimaux du fichier existant pour toute mutation ; `expected_project_sha256=null` admis seulement pour création explicite ; `actor` et `operation` en énumérations, payload validé par schéma discriminé ; limites taille, profondeur, nombre d'objets, délai et quotas. Un assistant ne peut émettre que `Propose*` ; `Apply*` requiert validation utilisateur/permissions. Aucune chaîne de chemin arbitraire ni code exécutable dans payload.

**Réponse commune :**
```json
{
  "contract":"v34.result/0.2-draft",
  "command_id":"cmd-0042",
  "state":"PROPOSED",
  "project_sha256_before":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "project_sha256_after":null,
  "proposal_ref":"memory:job-0042",
  "error":null,
  "proof_axes":{"auto":"NON_EXECUTE","windows":"NON_EXECUTE","design_space":"NON_EXECUTE","physical":"NON_EXECUTE"}
}
```

Les références `memory:` sont temporaires et **ne sont pas** des chemins de fichier. Le résultat calculé n'est durable qu'après acceptation et commit dans le projet ; les preuves V3.3 ne sont jamais promues automatiquement. Les champs `proof_axes` sont de **métadonnées de conception** et ne remplacent pas les registres de preuves réels.

**Erreurs contractuelles :** `STALE_PROJECT_SHA`, `COMMAND_ID_CONFLICT`, `UNAUTHORIZED`, `COMFYUI_UNAVAILABLE`, `MODEL_CONSENT_REQUIRED`, `MODEL_LICENSE_UNVERIFIED`, `MODEL_UNAVAILABLE`, `GPU_OOM`, `CANCELLED`, `TIMEOUT`, `ARCHIVE_BUDGET_EXCEEDED`, `PENDING_BACKUP_REVIEW_REQUIRED`, `EXPORT_NOT_QUALIFIED`, `OPERATION_UNSUPPORTED`. Toute erreur possède `code`, `message_fr`, `recoverable`, `suggested_action` et `details_redacted`.

### 5.1. Commandes et événements

| Commande | Effet autorisé | Événement / cas d'erreur |
|---|---|---|
| `OpenProject` | lecture snapshot sans écriture | `ProjectOpened`, `PROJECT_CORRUPT` |
| `ProposeMasks` | calcul hors verrou ; manuel/CPU/IA facultative | `ProposalReady`, `MODEL_UNAVAILABLE`, `GPU_OOM` |
| `AcceptMask` | vérification SHA source, masque float32 et CAS sous verrou | `ProjectCommitted`, `STALE_PROJECT_SHA` |
| `AssignOperation` | nouvelle assignation typée, non inférée du SVG | `ProjectCommitted`, `OPERATION_UNSUPPORTED` |
| `PrepareExport` | artefact dérivé + manifeste, sans mutation de l'original | `ExportPrepared`, `EXPORT_NOT_QUALIFIED` |
| `CancelJob` | marque annulation ; worker libéré selon contrat | `JobCancelled`, `ALREADY_COMMITTED` |
| `ResolvePendingRecovery` | intervention explicite avec SHA des sidecars | `RecoveryResolved`, `PENDING_BACKUP_REVIEW_REQUIRED` |

**États du job :** `QUEUED → RUNNING → PROPOSED → ACCEPTED → COMMITTING → COMMITTED` ; sorties terminales `CANCELLED/FAILED/STALE`. Les propositions ne changent pas `.smartsvg`. Les événements sont publiés **après** commit durable, jamais avant.

**Idempotence à définir au cycle 06 :** même `command_id` + empreinte de payload identique → un seul commit et même réponse après redémarrage ; même ID et payload différent → conflit. La persistance du journal doit être atomique avec le commit, **pas un cache mémoire**. La limite actuelle de 5 000 opérations impose une politique de compaction/migration, jamais un effacement silencieux de provenance.

## 6. Parcours UX novice, expert et erreurs

### Novice A — 12 escargots → stickers, sans ComfyUI

```text
[SmartSVG]  Importer | Créer | Reprendre
[Image 12 escargots]  [But : Autocollants] [Modifier le but]
[Sujets : 12 proposés / confirmer] [Corriger un sujet] [Continuer]
[IA locale : non nécessaire / modèle absent] [Continuer sans IA]
[Dimensions physiques : à confirmer] [Prévisualiser la planche]
[Prévol : zone A4 à vérifier dans Design Space] [Exporter brouillon PNG]
[Guide de transfert] [Enregistrer .smartsvg] [Annuler]
```

**Déroulé :** `Open/Import` → source conservée avec SHA → segmentation manuelle/déterministe ou proposition IA facultative → confirmer les masques et IDs → définir dimensions en mm → layout indicatif selon profil connu → export PNG Print Then Cut + guide, **jamais** marque de capteur inventée. Aucun changement de nœud ou d'onglet imposé. En cas de modèle absent, afficher l'option manuelle ; en cas d'export interrompu, projet inchangé et brouillon récupérable.

### Novice B — boîte carton Score + Basic Cut

```text
[Créer une boîte] [Longueur ?] [Largeur ?] [Hauteur ?] [Carton/épaisseur ?]
[Patron 2D]  Découpe : CUT (x) | Plis : SCORE (y)
[Outil de rainage déclaré ? NON] [Vérifier compatibilité] [Prévol]
[Enregistrer .smartsvg] [Exporter brouillon SVG + instructions]
[Dans Design Space : définir Score / Attacher / vérifier outil]
```

Le `NativeTransport` ne peut pas transformer un chemin SVG en opération Score reconnue automatiquement. Si dimensions/outil inconnus, pas de promesse de fabrication ; l'utilisateur conserve le patron comme brouillon.

### Expert — comparaison ancien/nouveau

```text
[Projet source SHA] [Transport: NATIVE | COMFYUI | DUAL-RUN (diagnostic)]
[Calcul CPU/IA] [Provider + version + licence] [Diff visuel/numérique]
[Masques f32] [IDs] [Géométrie] [Profil] [Manifestes] [Journaux expurgés]
[Accepter proposition] [Annuler] [Exporter rapport privé]
```

**Dual-run est un outil de qualification facultatif**, non un bouton grand public qui exécute silencieusement deux inférences coûteuses. L'utilisateur choisit explicitement l'usage de ComfyUI, la consommation GPU et tout téléchargement.

### Erreurs et fallback

- **ComfyUI absent :** transport natif continue ; anciens workflows non exécutés, mais non modifiés.
- **GPU OOM :** capturer code, libérer ressources si sûr, proposer réduction d'image/CPU/manuelle ; aucun commit de proposition partielle.
- **Projet obsolète :** comparer SHA avant acceptation ; afficher `STALE_PROJECT_SHA` et proposer recalcul, sans écraser les modifications récentes.
- **Crash entre écriture et ACK :** à la reprise, relire archive + journal durable et renvoyer le résultat déjà commis ; jamais deuxième mutation.
- **`.pending-backup.smartsvg` présent :** bloquer mutation et demander résolution explicite ; ne pas purger automatiquement.
- **Projet ZIP futur/invalide :** lecture seule ou refus contrôlé, conserver octets originaux ; pas de « réparation » silencieuse.

## 7. Stratégie de migration par vertical slices (sans big-bang)

| Étape | Périmètre | Gate de passage et preuve requise | Rollback |
|---|---|---|---|
| **M0 Baseline** | SHA, archive V21.15.2, workflows et contrats des 4 sorties ; corpus synthétique légal | Diff Git et checks de non-modification, tests G0 existants sur environnement autorisé | Ne rien changer |
| **M1 ProjectPort** | ouvrir/inspecter/sauvegarder projet `smartsvg-project/1` sans importer les nœuds | 10 projets anciens, source SHA et IDs inchangés, 100 fautes injectées sans perte ; auto + Windows | Désactiver nouveau port ; historique intact |
| **M2 Native read-only** | UI autonome ouvre un projet, montre sources/sujets, aucune écriture | import smoke sans `nodes/server/folder_paths`, UX novice et accessibilité, aucune requête réseau | Retour à UI ComfyUI |
| **M3 CPU/manual** | proposition de masques manuels et vectorisation déterministe via ports | dual-run sur corpus synthétique ; qualité géométrique et masques selon seuils explicites ; CPU/Windows | Route ancienne ; proposition non appliquée |
| **M4 Native writer/export** | commandes CAS, masques f32, opérations typées, exports dérivés | tests crash/idempotence/undo, PNG/SVG distincts, revue Design Space séparée | Désactiver writer ; ouvrir projet historique ou copie de compatibilité |
| **M5 IA locale optionnelle** | providers locaux installés volontairement et catalogués | licences, hash, sécurité, benchmarks RTX/CPU, refus de téléchargement et OOM ; aucun réseau implicite | Décharger modèle, repli CPU/manuel, conserver projet |

**Condition transverse :** aucune phase ne doit modifier `NODE_CLASS_MAPPINGS`, ports ComfyUI, contrats de sortie ni anciens projets sans migration testée et autorisée. Le déploiement de chaque slice reste une **future** PR d'implémentation distincte ; cette campagne produit seulement les spécifications.

## 8. Dual-run : comparateurs et preuves

**Corpus futur autorisé, sans image personnelle :** `tests/fixtures/v34_migration/{blank_alpha,flat_snails_12,photo_synthetic,legacy_project_v1,box_score_cut,stale_revision,corrupt_zip,oom_fake_provider,large_batch_50}`. Les chemins sont **proposés**, non présents. Le mode dual-run exécute deux transports sur des **copies temporaires isolées** de la même source ; un seul résultat peut être accepté, et uniquement via `ProjectAuthority`.

| Objet comparé | Oracle / assertion | Divergence admissible |
|---|---|---|
| Source | SHA-256 octets **identique** | Aucune |
| Projet legacy | IDs, chemins, opérations historiques, snapshots float32 préservés à l'ouverture | Aucune mutation à la lecture |
| Sorties PNG/SVG déterministes | pixels/paths normalisés ou métriques d'écart versionnées ; dimensions mm identiques | Différences d'encodage non sémantiques explicitement justifiées |
| Masques float32 persistés | SHA exact après round-trip si même snapshot accepté | Aucun passage silencieux à L8 |
| Segmentation IA | IoU/F1, qualité du contour, taux de rejet sur corpus annoté, provenance | Non-déterminisme admis **seulement** avec seuils et revue |
| IDs sujets | invariants de correspondance image/snapshot/révision | Aucun ID réassigné silencieusement |
| Opérations | `SCORE` reste `SCORE`, `CUT` reste `CUT` | Aucune conversion implicite |
| Performance | temps p50/p95, RAM, VRAM, latence annulation | Pas de seuil « garanti » avant mesures |
| Sécurité | zéro requête réseau sans consentement ; refus archives/chemins malveillants | Aucune fuite autorisée |

**Règle anti-faux positif :** ne jamais comparer uniquement les SHA de deux ZIP `.smartsvg` (horodatages et compression peuvent différer). Comparer manifestes et données canoniques, puis SHA des ressources immuables. Ne pas imposer une égalité pixel à pixel aux modèles IA stochastiques. **Aucun dual-run n'a été exécuté dans ce cycle.**

## 9. Sécurité, performances, ressources et confidentialité

- **Transport :** priorité à IPC/in-process. HTTP natif seulement si nécessaire : `127.0.0.1` / `::1`, jeton aléatoire éphémère stocké hors logs, contrôle Host/Origin, refus CORS, GET/POST authentifiés, limite de requête et délais, protection contre rebind/CSRF, aucune interface publique. Ne pas considérer `X-SmartSVG-UI: 1` comme authentification.
- **Stockage :** `ManagedWorkspace` borne les noms ; refuser symlinks, traversées, ZIP bomb, ressources hors racine. Aucun original écrasé, aucune photo ou modèle sous licence ajouté au dépôt public.
- **GPU :** sérialiser les inférences lourdes, budgets RAM/VRAM à mesurer sur RTX 3070 8 Go, annulation coopérative, unload/GC sans promesse de libération totale ; CPU et édition manuelle restent disponibles.
- **Consentement :** les anciens providers ComfyUI peuvent déclencher un téléchargement au premier appel ; le nouveau catalogue doit détecter le risque et **bloquer** tout appel sans consentement. Aucune dépendance à un modèle distant.
- **Objectifs candidats à mesurer, pas preuves :** p95 action UI légère <150 ms ; réponse à `CancelJob` <250 ms (accusé d'annulation, pas forcément arrêt GPU) ; 100 injections de panne sans perte de source ; 0 écriture non autorisée ; cold start à définir après spikes.
- **Observabilité locale :** journal d'erreurs à codes stables, taille bornée, opt-in export, chemins/jetons/images expurgés ; aucune télémétrie réseau par défaut.

## 10. Tests d'acceptation proposés — TOUS NON EXÉCUTÉS

| ID | Assertion exacte | Niveau / preuve attendue |
|---|---|---|
| T-V34-04-01 | Import du bootstrap natif ne charge ni `nodes`, `server`, `folder_paths` ni `torch` | auto + Windows |
| T-V34-04-02 | `smartsvg-project/1` ouvert en lecture seule : SHA source, IDs, masques f32 inchangés | auto + Windows |
| T-V34-04-03 | 2 transports observent le même projet ; seule autorité peut écrire | intégration auto |
| T-V34-04-04 | CAS sur SHA périmé renvoie `STALE_PROJECT_SHA`, archive non modifiée | unitaire + Windows |
| T-V34-04-05 | Même commande répétée après crash = un seul commit durable | injection panne auto + Windows |
| T-V34-04-06 | Même `command_id` avec payload différent → `COMMAND_ID_CONFLICT` | unitaire auto |
| T-V34-04-07 | Fichier `.pending-backup.smartsvg` → blocage et résolution explicite | intégration auto + Windows |
| T-V34-04-08 | ComfyUI absent → import/édition manuelle/export brouillon possibles | E2E Windows |
| T-V34-04-09 | Provider absent/refusé → aucune requête réseau et fallback manuel | réseau intercepté auto |
| T-V34-04-10 | OOM simulé → `GPU_OOM`, aucun commit partiel, reprise CPU | intégration auto ; RTX réelle séparée |
| T-V34-04-11 | 12 sujets synthétiques → IDs/masques persistés et planche indicative | E2E auto + Windows ; Design Space distinct |
| T-V34-04-12 | Boîte → `SCORE` et `CUT` distincts ; pas de conversion implicite | auto ; Design Space et physique séparés |
| T-V34-04-13 | Dual-run déterministe compare données canoniques, pas SHA ZIP brut | auto |
| T-V34-04-14 | Dual-run IA non déterministe produit métriques + provenance, jamais « identique » par défaut | auto ; RTX réelle séparée |
| T-V34-04-15 | GET/POST HTTP natif sans jeton, mauvais Host/Origin ou CORS → refus | sécurité auto + Windows |
| T-V34-04-16 | Ancien workflow garde IDs, noms de nœuds, ports, sorties | snapshot auto + ComfyUI réel ultérieur |
| T-V34-04-17 | Annulation + résultat tardif → `STALE/CANCELLED`, aucune mutation | race test auto |
| T-V34-04-18 | Un projet ZIP futur/corrompu ne détruit ni original ni backup | auto + Windows |
| T-V34-04-19 | 50 sujets divisés en lots ne violent ni `MAX_MASKS=32` ni budget archive | auto + Windows, mémoire à mesurer |
| T-V34-04-20 | Désactivation du transport natif rétablit le parcours historique sans conversion destructive | E2E ComfyUI/Windows |
| T-V34-04-21 | Graphe AST/ESM couvre 148 modules Python et 30 fichiers UI à SHA fixé | analyse statique auto |
| T-V34-04-22 | 100 crashs injectés pendant commit/récupération : aucune perte des octets source | auto + Windows |

**Preuves à conserver séparément :** `preuve_auto`, `preuve_windows`, `preuve_design_space`, `preuve_physique` ; chacune initialement `NON_EXECUTE`. Un test de contrat ne constitue pas un essai physique. Aucun test ci-dessus n'a été exécuté ; les nombres sont des objectifs de future recette.

## 11. Micro-tickets V34-017 à V34-024 — SPECIFIES, non implémentés

| ID / priorité | Dépendances héritées et V34 | Livrables futurs précis | Test exact, preuve, DoD et rollback |
|---|---|---|---|
| **V34-017 P0** Graphe d'import reproductible | S-022, S-046, R33-003, V34-004, V34-014 | `tools/architecture/build_import_graph.py`, `docs/roadmap-v3.4/generated/import_graph.json` | T-V34-04-01,21 ; auto ; DoD 148/148 + 30/30 à SHA fixe, imports dynamiques signalés ; rollback supprimer outil généré, conserver annexe. |
| **V34-018 P0** ProjectPort SHA/CAS | S-052, S-053, R33-004..005, V34-011, V34-013 | `engine/smartsvg_app/project_port.py`, `tests/v34/test_transport_parity.py` | T-V34-04-02..04 ; auto+Windows ; DoD aucun writer concurrent ni source mutée ; rollback adaptateur désactivé. |
| **V34-019 P0** Native bootstrap minimal | S-022, S-046, R33-003, V34-014 | `engine/smartsvg_app/adapters/native_transport.py`, `tests/v34/test_native_bootstrap.py` | T-V34-04-01,08,15 ; auto+Windows ; DoD sans ComfyUI ni torch au démarrage ; rollback entrée native désactivée. |
| **V34-020 P0** ComfyUI adapter de compatibilité | S-022, S-046, R33-009, V34-005, V34-014 | `engine/smartsvg_app/adapters/comfy_transport.py`, `tests/v34/test_migration_rollback.py` | T-V34-04-03,16,20 ; auto+ComfyUI Windows ; DoD workflows/IDs/ports identiques ; rollback route historique. |
| **V34-021 P0** Dual-run et oracles | S-063, S-101, R33-022, V34-005, V34-016 | `tests/v34/test_transport_parity.py`, `tests/fixtures/v34_migration/`, `docs/roadmap-v3.4/specs/DUAL_RUN_ORACLES.md` | T-V34-04-11..14 ; auto+Windows ; DoD métriques différenciées IA/déterministe et provenance ; rollback désactiver diagnostic. |
| **V34-022 P0** Crash/idempotence/recovery | S-053, S-095, R33-011..014, V34-013 | `engine/smartsvg_app/jobs.py`, `tests/v34/test_migration_rollback.py` | T-V34-04-05..07,17,18,22 ; auto+Windows ; DoD retry non duplicateur et sidecars intacts ; rollback writer natif désactivé. |
| **V34-023 P0** Sécurité et consentement des providers | S-063, R33-015, R33-032, V34-015 | `engine/smartsvg_app/providers.py`, `tests/v34/test_security_boundary.py` | T-V34-04-09,10,15 ; auto+Windows, RTX séparée ; DoD 0 réseau sans accord, OOM non destructif ; rollback providers désactivés. |
| **V34-024 P1** Diagnostic de capacités et migration guidée | S-022, S-046, S-084, R33-034, V34-010 | `engine/smartsvg_app/facade.py`, futur panneau `engine/web/js/smartsvg_capabilities_v34.mjs` | T-V34-04-08,19,20 ; UI+Windows ; DoD « absent/présent/non testé » distingués, retour arrière visible ; rollback panneau masqué. |

**Chaque DoD ci-dessus exige aussi** revue du diff, traçabilité exigence→ticket→test, preuve attachée au commit, aucune modification des sources protégées et absence de régression sur les quatre contrats PNG/SVG. Les chemins sont **pressentis**, pas des fichiers déjà disponibles.

## 12. Risques ouverts, dépendances et prochaine étape

1. **Graphe complet non exécuté** : annexe = inventaire exhaustif de chemins mais analyse d'imports **ciblée** ; V34-017 reste P0, et ne doit pas être déclaré résolu par la seule annexe.
2. **Sémantique de révision** : SHA de fichier existant vs entier proposé ; le cycle 05 devra formaliser versions et migrations ; le cycle 06 fixera journal durable/idempotence.
3. **Port HTTP ComfyUI** : la vérification d'Origin/header sur POST n'est pas une authentification native ; risque GET si service exposé.
4. **Poids de modèles** : premier appel ComfyUI tiers potentiellement téléchargeur ; ne pas le confondre avec IA locale consentie.
5. **Windows, RTX 3070, Design Space, Explore 5** : aucune preuve nouvelle ; essais réels et licences restent `NON_EXECUTE`.
6. **Graphe historique** : le registre `node_v*` est cumulatif et chargé au bootstrap ; isoler sans renommer les nœuds ni casser les imports.
7. **Surconception** : commencer par M1–M3 (lecture, UI, manuel/CPU), pas par un moteur de modèles universel.

**Décision de lot :** recommander la migration incrémentale, **sans promotion de V3.4**. Prochain lot 05 : schéma `.smartsvg`, identités, révisions, ressources, journal, budgets et migrations V1→V34 ; intégrer les contraintes de compatibilité établies ici.
