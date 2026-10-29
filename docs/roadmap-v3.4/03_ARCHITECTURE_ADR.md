# SmartSVG V3.4 — Cycle 03 : architecture cible, ADR et contrats entre moteurs

**DRAFT de conception, 29 octobre 2026.** Roadmap active : V3.3. Base `main` relue : `fdbda304beb77d97340a8be4dd5c5e9cefde15f4` ; branche V3.4 avant ce lot : `5f82b88ef2d2c79f445bb0a6df6fe4dbcc434040`. **Aucune fonction de production implémentée par ce document.** Aucun benchmark Windows, RTX 3070, Design Space ou Cricut réalisé. Les types, chemins et tests « futurs » ci-dessous sont des propositions, pas des fichiers existants.

## 1. Objectif, périmètre et revue du lot 02

**Problème.** Le logiciel dispose d'un noyau projet et de plusieurs moteurs réutilisables, mais les chemins UI/ComfyUI et les sorties de fabrication n'ont pas encore un contrat commun démontré. Définir les frontières avant d'écrire un runtime autonome, sans recréer les fonctions G1/G2/G3.3e ni faire du SVG l'autorité de fabrication.

**Cas d'usage contraignants :** (A) image → 12 sujets identifiés → corrections → planche de stickers → PNG et guide Design Space ; (B) dimensions fournies → patron de boîte → chemins CUT + SCORE → export et guide d'opérations manuelles. L'architecture doit aussi accepter une opération manuelle sans modèle IA installé, l'annulation, l'édition concurrente et les anciens projets.

**Contre-expertise du lot 02 :**
1. Le pseudo-code de placement de stickers retourne `artifacts=[]` si la région A4 est inconnue : c'est une règle de **blocage de la promesse de planche garantie**, pas une interdiction absolue de sauvegarder un brouillon local. Décision : autoriser sauvegarde du projet et export explicitement marqué **DRAFT / placement non vérifié**, sans libellé « prêt à découper » ni export de production qualifié.
2. `preflight.PASS/WARN/BLOCKED` est un diagnostic **interne** distinct des valeurs de preuve V3.3 `PASS/FAIL/NON_EXECUTE/NON_APPLICABLE/BLOQUE`. Ne jamais propager automatiquement `preflight.PASS` vers `preuve_physique=PASS`.
3. Les commandes et événements du lot 02 ne sont pas des API existantes ; préciser maintenant l'enveloppe, la concurrence et les erreurs avant de définir l'assistant (cycles 08–09).
4. L'opération Score doit être portée par une relation métier typée, **jamais** inférée d'une couleur SVG ou d'un calque importé ; la configuration dans Design Space reste manuelle.

## 2. Inventaire ciblé des dépendances RÉELLEMENT lues au HEAD

| Composant existant | Importations/frontières vérifiées par lecture | Réutilisation envisagée / réserve |
|---|---|---|
| `engine/smartsvg_core/project_contracts.py` | `SourceAsset`, `Mask`, `Subject`, `Artifact`, `QAResult`, validation des enregistrements | Base des IDs et contraintes ; extension via version de schéma/migration, **pas** remplacement des dataclasses |
| `engine/smartsvg_core/project_archive.py` | `LoadedProject`, `load_project`, `save_project`, ZIP sûr, `SCHEMA_VERSION='smartsvg-project/1'` ; bornes existantes : 256 entrées, 64 MiB par membre, 256 MiB total | Format canonique existant ; les futures pièces/ressources doivent respecter ou faire évoluer explicitement ces bornes |
| `engine/smartsvg_core/project_workspace_g22.py` | `ManagedWorkspace` importe archive, récupération, éditeur, snapshots, identité G3.3e | Autorité de mutations à préserver ; ne pas introduire un deuxième writer natif |
| `engine/smartsvg_core/project_recovery.py` | `save_with_recovery`, verrou fichier, sauvegarde atomique, restauration explicite | Réutiliser pour tout transport ; tests Windows de verrous restent à faire |
| `engine/smartsvg_core/mask_snapshot_g24.py` | snapshots float32 exacts, aperçu L8 distinct ; stdlib | Ne pas réduire les masques en PNG 8 bits pour la persistance/relecture |
| `engine/smartsvg_core/subject_identity_g33e.py` | ID persistant lié au snapshot float32 et à la révision | Conserver identité et fingerprint ; ne pas réattribuer d'ID au gré des suggestions IA |
| `engine/project_routes_g22.py` | pont HTTP ComfyUI facultatif, `ManagedWorkspace`, origine/header vérifiés | Adaptateur **réseau** seulement, pas source de vérité ; garder la politique same-origin/auth existante |
| `engine/smartsvg_ai/provider_v2112.py` | `numpy`, `torch`, découverte du registre `nodes.NODE_CLASS_MAPPINGS` | Fournisseur ComfyUI facultatif, susceptible de déclencher téléchargement de poids par nœud ; pas un runtime local autonome certifié |
| `engine/smartsvg_ai/auto_masks_v2111.py` | `numpy`, `cv2`, `generate_masks`, plafond `MAX_MASKS=32`, `MAX_PIXELS=5_000_000` | Réutiliser pipeline conservateur ; **50 sujets** implique stratégie batch/partition et tests, pas augmentation aveugle des limites |
| `engine/web/js/smartsvg_express_atelier_preview.html` | maquette 12 escargots et hooks partiels sous ComfyUI | Ne pas considérer la maquette comme segmentation/export réel ; extraire contrats UI progressivement |
| `engine/__init__.py` | enregistrement des nœuds historiques, API projet activée explicitement par variable d'environnement | Ne pas changer les IDs, ports ni l'activation par défaut pendant la conception |

**Portée de l'inventaire :** les importations principales et fonctions publiques ci-dessus ont été relues ; **ceci n'est pas** un graphe statique exhaustif de tous les imports du dépôt. Le cycle 04 doit générer/revoir le graphe complet et classifier les dépendances à ComfyUI, CUDA, HTTP et navigateur. `ETAT_ACTUEL_SMARTSVG.md` est antérieur à certaines capacités G3.3e du code.

## 3. ADR-034-01 — Une seule autorité projet, plusieurs adaptateurs (PROPOSÉE)

**Décision :** conserver les enregistrements et le workspace `.smartsvg` existants comme noyau canonique. UI, assistant, transport ComfyUI et transport natif émettent des **intentions/commandes** ; seul le service de projet valide la révision, applique une transaction et publie une nouvelle révision durable.

**Alternatives rejetées :** (a) store indépendant par écran (risque de divergence) ; (b) projet natif JSON distinct de `.smartsvg` (migration destructrice) ; (c) éditer directement le ZIP depuis JavaScript (sécurité et atomicité). **Limite :** les API de commandes ci-dessous sont à créer ; `ManagedWorkspace` ne les expose pas aujourd'hui sous cette forme.

```text
 [Express / Atelier / Fabrique / Vectoriel / Bibliothèque / Expert]
                 │ CommandEnvelope / EventEnvelope
                 ▼
      [ApplicationFacade + CommandCoordinator] ◄── [Assistant: propositions seulement]
                 │
          [ProjectAuthority]
     ┌───────────┼───────────────┐
 [Archive v1] [Recovery/Locks] [Identity + float32 Masks]
     │           │                 │
     └───────────┴─────────────────┘
                 │ immutable snapshot / revision
     ┌───────────┼────────────────┬─────────────────┐
 [Raster/AI] [Vector/Geometry] [Fabrication/Preflight] [Layout/Export]
     │             │                    │                 │
 [proposal only] [proposal only]   [findings]       [artifacts + manifest]
                 │
       [NativeTransport]     [ComfyUITransport]
           │                        │
       [Desktop UI]          [Historical nodes/UI]
```

**Frontière de confiance :** les moteurs sont calculatoires et ne reçoivent ni chemins de fichiers arbitraires ni accès direct à l'archive en écriture. Les adaptateurs ne choisissent pas l'autorité du projet. Les exports ne changent pas la révision source ; ils portent un manifeste lié à sa révision.

## 4. ADR-034-02 — Contrat minimal de fabrication en amont du cycle 14 (PROPOSÉE)

**Décision :** dès l'architecture, une géométrie n'est qu'une ressource. Une affectation d'opération associe explicitement `geometry_id → operation_kind → tool_profile → material_profile → machine_profile`. Les profils sont **versionnés et peuvent être UNKNOWN**. Les opérations détaillées, règles physiques et compatibilités seront approfondies aux cycles 14–17.

**Opérations conceptuelles :** `CUT`, `SCORE`, `DRAW`, `PRINT_THEN_CUT`, `FOIL`. Aucun `ENGRAVE` ni autre opération Maker-only déclaré disponible sur Explore 5 sans preuve spécifique. `PRINT_THEN_CUT` référence une composition raster + contour et un transfert dans Design Space ; **pas** une simple ligne de coupe.

**Contrat JSON illustratif — SPÉCIFICATION, non schéma sérialisé existant :**

```json
{
  "contract_version": "v34.fabrication-intent/0.1-draft",
  "project_id": "demo-local-01",
  "project_revision": 12,
  "geometry": [
    {"id":"g-cut-1","type":"closed_path","units":"mm","resource_ref":"geo/box-cut-1"},
    {"id":"g-score-1","type":"open_path","units":"mm","resource_ref":"geo/box-score-1"}
  ],
  "assignments": [
    {"id":"a-cut-1","geometry_id":"g-cut-1","operation":"CUT","tool_profile_id":"basic-blade","material_profile_id":"cardstock-unknown","machine_profile_id":"explore-5"},
    {"id":"a-score-1","geometry_id":"g-score-1","operation":"SCORE","tool_profile_id":"scoring-tool-unconfirmed","material_profile_id":"cardstock-unknown","machine_profile_id":"explore-5"}
  ],
  "profiles": {"machine_version":"UNVERIFIED","material_version":"UNVERIFIED","tool_version":"UNVERIFIED"},
  "handoff": {"target":"DESIGN_SPACE","requires_user_operation_mapping":true,"requires_attach":true},
  "preflight": {"status":"BLOCKED","reasons":["TOOL_UNCONFIRMED","PROFILE_UNVERIFIED"]}
}
```

**Contraintes :** ID unique et référence existante ; valeurs finies ; unités mm et transformation de coordonnées explicite ; `CUT` sur chemin fermé valide, `SCORE` peut être une ligne ouverte sans devenir `CUT` ; aucune inférence automatique de la compatibilité ; relation opération/outil/matière/machine obligatoire même si profil inconnu ; `geometry_id` ne désigne jamais un chemin externe ; interdiction de transformer silencieusement `SCORE` en `CUT`.

**Sémantique du prévol :** `PASS` = vérifications locales satisfaites selon profil déclaré ; `WARN` = transfert avec confirmation et incertitude affichées ; `BLOCKED` = sortie de production interdite, brouillon récupérable. Ces trois états ne certifient **aucun** axe V3.3.

## 5. ADR-034-03 — Choix de l'interface et du runtime : décision DIFFÉRÉE

**Options à comparer :**
- **PySide6/Qt + services Python in-process ou subprocess** : réutilisation Python et API native ; coûts à mesurer : déploiement Qt, interactions GPU/UI, packaging, accessibilité et mémoire.
- **Tauri + frontend Web + service Python local** : réutilisation UI JS, isolation frontend ; coûts à mesurer : WebView2, cycle de vie du service, transport local sécurisé, packaging, surface d'attaque et intégration Windows.
- **Web UI locale + service Python** : réutilisation maximale des composants web ; risques à mesurer : installation, démarrage/arrêt, gestion du port local et confinement navigateur.

**Critères et pondération proposés :** réutilisation de code 20 %, sécurité des frontières 20 %, packaging/offline Windows 20 %, réactivité/empreinte 15 %, accessibilité/UX 15 %, maintenance et tests 10 %. **Aucun vainqueur déclaré** sans prototype sur les mêmes fixtures. Une décision définitive sera conditionnée par un ADR avec mesures sur Windows cible ; le cycle 04 peut préparer les spikes.

**Spike minimal comparatif à exécuter plus tard :** ouvrir un `.smartsvg` synthétique, afficher 12 vignettes, lancer une tâche CPU annulable, sauvegarder/réouvrir, simuler un résultat IA obsolète, fermer proprement le service ; relever RAM, temps de lancement, crash recovery, complexité du bundle et accessibilité. Aucun de ces spikes n'a été exécuté.

## 6. ADR-034-04 — IA en dehors de la transaction projet (PROPOSÉE)

L'assistant et les fournisseurs IA produisent `ProposedIntent`, `ProposedMask`, `ProposedCommand` ou `ProposedLayout` avec `base_revision`, `source_fingerprint`, `provider_id` et `model_version` (si présents). Ils n'écrivent jamais dans `.smartsvg`. Le moteur de géométrie, la validation et la sauvegarde restent déterministes.

**Mode manuel/CPU :** si modèle absent, licence incompatible, utilisateur refuse le téléchargement, mémoire insuffisante ou provider indisponible, conserver les actions manuelles et les algorithmes classiques ; le projet ne doit pas être bloqué par une dépendance IA optionnelle. Pas de chargement de poids, réseau ou `trust_remote_code` sans politique et consentement à spécifier au cycle 11. Les licences Florence-2/SAM2/RMBG/Real-ESRGAN **ne sont pas qualifiées par ce cycle**.

**Sécurité :** tout modèle est un composant non fiable jusqu'à vérification de source, licence, hash, dépendances et conditions d'exécution ; aucun modèle recommandé ne devient automatiquement redistribuable. OOM : abandonner la proposition, libérer le worker et conserver la révision saine.

## 7. Interfaces, commandes, événements et isolation

### 7.1 Interfaces proposées (non implémentées)

| Port logique | Entrée | Sortie | Autorité / erreurs |
|---|---|---|---|
| `ProjectPort.open(name)` | nom sûr, schéma accepté | `ProjectSnapshot(revision, sha)` | noyau ; `PROJECT_INVALID`, `SCHEMA_FUTURE` |
| `CommandPort.submit(envelope)` | commande typée, `expected_revision`, `command_id` | `Applied/Rejected` + nouvelle révision | noyau ; `STALE_REVISION`, `DUPLICATE_COMMAND` |
| `SubjectPort.propose(snapshot)` | snapshot immuable + hints IA/manuels | sujets/masques proposés | calcul ; `SUBJECT_AMBIGUOUS`, `AI_UNAVAILABLE` |
| `VectorPort.derive(snapshot)` | ressource raster/masque et paramètres | géométries proposées | calcul ; `INVALID_TOPOLOGY` |
| `FabricationPort.validate(plan,profiles)` | assignations et profils versionnés | `Findings[]` + état interne | prévol ; `PROFILE_UNKNOWN`, `OPERATION_UNSUPPORTED` |
| `ExportPort.prepare(snapshot,plan)` | révision épinglée, format explicite | manifeste + artefacts temporaires | export ; `EXPORT_INTERRUPTED`, `PREFLIGHT_BLOCKED` |
| `TransportPort.dispatch(command)` | enveloppe validée côté adaptateur | résultat sans mutation directe | native/ComfyUI ; `UNAUTHORIZED`, `REQUEST_TOO_LARGE` |

### 7.2 Enveloppe de commande (pseudotype)

```typescript
// SPÉCIFICATION : ne pas traiter comme TypeScript compilé
type CommandEnvelope = {
  contract: "v34.command/0.1-draft";
  command_id: string;               // unique et stable à la répétition
  project_id: string;
  expected_revision: number;        // entier >= 0
  actor: "user" | "assistant_proposal" | "system";
  kind: "ConfirmIntent" | "AcceptMask" | "EditMask" |
        "AssignOperation" | "SetFabricationProfile" | "SaveProject";
  payload: unknown;                 // validé par schema discriminé selon kind
  source_fingerprint?: string;       // SHA256 hex, si commande issue d'un asset
};
type EventEnvelope = {
  event_id: string; command_id: string; project_id: string;
  before_revision: number; after_revision: number;
  kind: string; payload_ref?: string;
};
```

**Séquence déterministe :** (1) valider schéma/taille/identité ; (2) vérifier `expected_revision` et le fingerprint ; (3) chercher `command_id` dans journal idempotent ; (4) calculer une mutation sur snapshot ; (5) sauvegarde atomique via récupération ; (6) publier événement après commit ; (7) notifier UI. Répéter le même `command_id` avec le même payload renvoie le résultat déjà commis ; même ID avec payload différent = `COMMAND_ID_CONFLICT`. Un résultat IA arrivé après modification du projet = proposition périmée, jamais application.

**Concurrence :** une seule écriture canonique par projet ; verrou fichier/revision CAS ; lecteurs reçoivent snapshot immuable ; jobs lourds hors verrou ; à la fin, compare-and-swap sur révision. Crash avant publication : aucune notification de succès ; crash après commit mais avant accusé : retry idempotent. Le journal persistant d'idempotence est à concevoir au cycle 06, sans présumer qu'il existe.

**Undo/redo :** commandes inverses ou snapshots transactionnels, à choisir au cycle 06 ; pas de mutation destructive de l'original. Undo d'une assignation `SCORE` ne supprime pas le chemin source. Les exports déjà produits sont des artefacts externes à provenance conservée, pas annulés silencieusement.

## 8. Deux vertical slices architecturales de référence

### A — Douze escargots

`ImportSource` → `ProjectAuthority` conserve octets+SHA → `SubjectPort` propose 12 masques/IDs ou sélection manuelle → confirmation des 12 → `VectorPort` génère contours/offset en mm à partir des tailles **saisies** → `FabricationPort` contrôle `PRINT_THEN_CUT` + zone admissible **versionnée** → `LayoutPort` propose placement → `ExportPort` prépare PNG + guide et manifeste → vérification Design Space par l'utilisateur. Un modèle IA absent n'empêche pas la voie manuelle. La limite existante de 32 masques est distincte des futurs lots 50 : partitionnement/reprise à spécifier au cycle 19.

### B — Boîte carton Score + Cut

`CreateTemplate` → saisir dimensions et épaisseur si requise → `GeometryPort` calcule développé → `AssignOperation(CUT)` sur chemins fermés et `AssignOperation(SCORE)` sur lignes de plis → profil outil/matière/machine → prévol topologie/marges/compatibilité → export SVG(s) et guide → dans Design Space, choisir manuellement Score, Attacher et changer l'outil selon instructions. Une opération non supportée ne devient jamais une ligne Basic Cut par défaut. Aucun pilote direct Cricut.

**Écran novice (texte) :**
```text
[Projet r12] [Objectif: Stickers / Boîte] [Mode Express] [Atelier] [Fabrique]
[Visuel ou patron] [Sujets/calques: état + alertes accessibles]
[Action conseillée: confirmer dimensions] [Corriger] [Annuler]
[Prévol: 2 vérifications locales OK / profil machine NON VÉRIFIÉ]
[Enregistrer projet] [Exporter brouillon] [Guide Design Space]
```
**Écran expert :** panneaux `Geometry`, `OperationAssignments`, `Profiles`, `Revision/Job`, `Findings`, `ExportManifest` ; mêmes données et commandes que l'écran novice, aucune copie de store. État d'erreur : message localisé, chemin/objet surligné, action réversible et preuve non exagérée.

## 9. Performance, sécurité, limites et rollback — objectifs à mesurer

| Dimension | Objectif de conception (PAS mesure) | Méthode future |
|---|---|---|
| Interaction UI | Commandes légères sans attente GPU bloquante ; cible p95 < 150 ms sur corpus de référence | instrumenter 100 actions sur Windows cible |
| Annulation | retour UI < 250 ms, worker libéré dans délai documenté | injection d'annulation CPU/GPU et mesure |
| Sauvegarde | atomicité, aucun octet original perdu lors d'un crash | 100 injections de panne aux étapes de publication |
| Démarrage | budget à fixer après comparaison des 3 prototypes | chronométrage froid/chaud Windows |
| Mémoire GPU | aucun modèle IA obligatoire ; OOM récupérable sur RTX 3070 8 Go | benchmark VRAM et cas OOM, non exécutés |
| Données | aucune transmission réseau implicite, pas d'accès aux chemins arbitraires | test proxy réseau + corpus adversarial |
| Migration | anciens projets, IDs, ports, PNG/SVG intacts | dual-run ancien/nouveau sur fixtures autorisées |

**Sécurité supplémentaire :** filtrer ZIP/XML/chemins, taille et décompression, sources externes, liens et scripts ; ports locaux liés au loopback avec authentification/jeton si option web, protection CSRF/origine, aucun CORS permissif par défaut ; pas de secrets dans le dépôt public. Ne pas exposer `ManagedWorkspace` directement sur une interface HTTP ouverte. Les options d'authentification et de packaging seront décidées aux cycles 04 et 21.

**Rollback :** désactiver le nouvel adaptateur et conserver les anciens nœuds et routes ComfyUI ; ouvrir les projets non migrés par les fonctions historiques ; toute extension du schéma `.smartsvg` doit posséder un mode lecture seule ou un export de compatibilité explicite. Aucun fichier V3.3 ou archive n'est modifié ici.

## 10. Plan de tests (TOUS NON EXÉCUTÉS)

| ID | Assertion future exacte | Type / preuve attendue |
|---|---|---|
| T-V34-03-01 | 2 transports lisent le même projet et même SHA de source | intégration, auto+Windows |
| T-V34-03-02 | Double `command_id` identique = 1 seule révision | unitaire, auto |
| T-V34-03-03 | Même ID, payload différent → `COMMAND_ID_CONFLICT` | unitaire, auto |
| T-V34-03-04 | `expected_revision` obsolète → aucune mutation | intégration, auto |
| T-V34-03-05 | Résultat IA r12 après r13 → jamais appliqué | E2E, auto+Windows |
| T-V34-03-06 | ZIP futur/corrompu/traversal → refus sans écrasement | sécurité, auto |
| T-V34-03-07 | Snapshot float32 rechargé conserve hash et IDs | régression, auto |
| T-V34-03-08 | `SCORE` ouvert ne devient pas `CUT` | unitaire, auto |
| T-V34-03-09 | Outil/matière/profil inconnu → prévol non qualifiant | unitaire, auto |
| T-V34-03-10 | Zone A4 inconnue → brouillon possible, aucun « prêt » | intégration UI, auto+Design Space |
| T-V34-03-11 | Modèle absent/CPU manuel → parcours projet toujours accessible | E2E, Windows |
| T-V34-03-12 | OOM GPU ne détruit pas dernier projet sain | intégration, Windows+RTX |
| T-V34-03-13 | Export ne modifie pas révision ni octets source | unitaire, auto |
| T-V34-03-14 | Ancien workflow ComfyUI garde IDs/ports/sorties | dual-run, auto+Windows |
| T-V34-03-15 | Import Score+Cut nécessite requalification manuelle Score/Attach | terrain, Design Space |
| T-V34-03-16 | Une découpe réelle ne reçoit PASS physique qu'avec mesures/protocole | terrain, physique |

**Fixtures à créer (aucune image protégée)** : `tests/fixtures/v34_arch/12_snails_synthetic/`, `box_score_cut/`, `stale_job/`, `invalid_project_zip/`, `legacy_workflows/`, `oom_simulated/`. Les preuves devront référencer commit exact, OS, version de Design Space, profil, matière et date. Aucun test ni fixture de cette table n'a été créé/exécuté dans le cycle de conception.

## 11. Micro-tickets V34-011 à V34-016 — SPECIFIES uniquement

| ID / priorité | Dépendances héritées + V34 | Livrables futurs (non présents) | Test / preuve / DoD / rollback |
|---|---|---|---|
| **V34-011 P0** Autorité projet unique | S-022, S-046, S-052, S-053, R33-003..005, V34-004 | `docs/roadmap-v3.4/adr/ADR-034-01.md`, futur `engine/smartsvg_app/project_port.py` | T-V34-03-01,02,04,07 ; auto/Windows ; DoD : un seul writer et même état dans deux transports ; rollback adaptateur natif |
| **V34-012 P0** Contrat fabrication minimal | S-012, S-030, S-085, R33-008, R33-022..023, V34-008 | `docs/roadmap-v3.4/specs/FABRICATION_INTENT.md`, futur `engine/smartsvg_fabrication/operation_contracts.py` | T-V34-03-08,09,15 ; auto/Design Space ; DoD : Score distinct de Cut, profils versionnés, guide manuel ; rollback export Basic Cut sans promesse Score |
| **V34-013 P0** Bus de commandes révisionné | S-053, S-095, R33-004..005, R33-011..014, V34-009 | `docs/roadmap-v3.4/specs/COMMAND_BUS.md`, futur `engine/smartsvg_app/commands.py` | T-V34-03-02..05,13 ; auto/Windows ; DoD : CAS, idempotence et absence de mutation tardive ; rollback désactiver nouvelles commandes |
| **V34-014 P0** Adaptateurs dual-run | S-022, S-046, S-063, R33-003, R33-009, V34-004, V34-005 | `docs/roadmap-v3.4/specs/TRANSPORTS.md`, futurs `engine/smartsvg_app/adapters/` | T-V34-03-01,06,14 ; auto/Windows ; DoD : anciens workflows intacts, aucune exposition réseau non autorisée ; rollback ComfyUI-only |
| **V34-015 P1** Spike UI mesuré | S-067, S-069, S-071, R33-032, V34-006 | `docs/roadmap-v3.4/adr/ADR-034-03.md`, futurs prototypes temporaires hors code de production | T-V34-03-05,10,11 + mesures Windows ; DoD : critères pondérés et preuve comparative, aucune décision non mesurée ; rollback ne pas adopter de framework |
| **V34-016 P1** IA isolée des transactions | S-027, S-028, S-070, R33-007, R33-017, R33-030, V34-007 | `docs/roadmap-v3.4/specs/AI_PROPOSALS.md`, futur `engine/smartsvg_app/ai_port.py` | T-V34-03-05,11,12 ; auto/Windows+RTX ; DoD : proposition non mutante, consentement et OOM récupérable ; rollback fournisseur IA désactivé |

**Traçabilité :** V34→S/R33 ci-dessus est explicite ; le mapping inverse de **toutes** les 141 exigences demeure un travail à poursuivre dans `HERITAGE_INDEX.md` / futur registre. Aucun statut historique requalifié. Les six tickets sont des objets de conception, **pas** des commits de code.

## 12. Auto-contre-expertise et décisions ouvertes

- **Erreur potentielle :** « service de projet unique » n'implique pas forcément un processus unique ; garantir un **writer logique** et une politique de verrouillage, puis mesurer le meilleur mode de déploiement.
- **Compatibilité :** le `SCHEMA_VERSION='smartsvg-project/1'` existant n'est pas modifié ; le JSON d'opération proposé n'est pas injecté silencieusement dans les archives v1. Migration/version au cycle 05.
- **Cas limite :** 50 sujets ne peuvent pas être supposés compatibles avec `MAX_MASKS=32` de l'algorithme actuel ; séparer lot et segmentation individuelle.
- **Cas limite :** un `CUT` peut représenter un contour fermé avec trous et groupes ; le type simplifié `closed_path` est provisoire, la topologie complète appartient au cycle 13.
- **Risque de surconception :** les ports sont des **contrats logiques** ; ne pas créer huit services ou processus distincts par défaut.
- **Aucun résultat matériel :** ni la présence d'un module ni un prévol PASS ne démontrent la fabrication.
- **Sources Cricut :** reprendre les articles officiels datés du cycle 02 pour les hypothèses Score/A4 ; aucune nouvelle capacité matérielle n'est affirmée ici.
- **ADR ouverts :** choix Qt/Tauri/Web local, format d'extension archive, gestion du journal de commandes, profils machine réels, stratégie batch 50, authentification du transport local. Ne pas les trancher sans spike ou source vérifiée.

**Prochain lot 04 :** graphe d'import complet, stratégie runtime autonome/ComfyUI dual-run, séparation des ports, matrices de parité et plan de rollback ; relecture de cette ADR avant tout nouveau choix d'implémentation.
