# SmartSVG V3.4 — Lot 04 / Annexe A : dépendances et frontières de migration

**DRAFT de conception, 29 octobre 2026.** Base `main@fdbda304beb77d97340a8be4dd5c5e9cefde15f4`, branche documentaire `codex/docs-roadmap-v3-4-campaign`. **Inventaire du dépôt complet ; graphe d'imports ciblé, non exhaustif.** Aucune exécution Windows, inférence, installation de modèle ou modification du moteur. Cette distinction interdit d'annoncer « graphe exhaustif terminé ».

## 1. Périmètre effectivement vérifié

- L'API GitHub `git/trees/main?recursive=1` retourne **852 entrées, `truncated=false`** : **148 modules Python de production** sous `engine/` (hors `engine/tests/`, `engine/tools/`, `engine/verify_*.py`), **71 tests Python** sous `engine/tests/`, **33 tests Python** sous `tests/`, **30 fichiers JS/MJS/HTML** sous `engine/web/js/`, **51 fichiers `engine/node_v*.py`**. Ces comptes sont des **inventaires de chemins**, pas des imports analysés.
- **47 modules Python ciblés** et **7 fichiers UI** ont été lus par le connecteur GitHub, avec extraction de leurs imports/définitions ou inspection de sections pertinentes. Ce relevé permet de spécifier la frontière, **pas** de certifier les 148 modules. Un chemin présumé `engine/smartsvg_core/project_edit_g23.py` est **absent** ; le fichier réel est `editor_session_g23.py`.
- Références de contenu : `engine/__init__.py@c782d9c9`, `engine/node_v21154.py`, `engine/project_routes_g22.py@17676341`, `engine/smartsvg_core/project_workspace_g22.py@e09af39f`, `project_archive.py@3f62d3ed`, `project_recovery.py@0d78a8cc`, `engine/smartsvg_ai/provider_v2112.py@5a2c5fcb`, `engine/smartsvg_ai/auto_masks_v2111.py@4530631c`. Les SHA abrégés identifient les blobs lus, non des commits de test.

## 2. Graphe d'imports confirmé sur les chemins critiques

```text
engine/__init__.py
  ├─ node_v21154 → node_v21152 → node_v2115 → ... (chaîne historique de registres)
  │     ├─ node_v21131 → node_v2113 → ... (sélection/vectorisation)
  │     ├─ smartsvg_core.subject_inspector_v21154 → numpy, cv2
  │     └─ smartsvg_compat.registry → merge_registry
  ├─ [SMARTSVG_ENABLE_PROJECT_API=1] project_routes_g22 → aiohttp (import dans fonction)
  │     └─ smartsvg_core.project_workspace_g22 → project_archive, project_recovery,
  │           project_contracts, editor_session_g23, mask_snapshot_g24,
  │           mask_binding_g33e → subject_identity_g33e
  └─ [SMARTSVG_ENABLE_PROJECT_API=1] node_g24_mask_vault
        → project_workspace_g22, smartsvg_editor.strokes, torch, numpy, PIL, folder_paths

node_v2112 → node_v21112 → node_v2111 → node_v2110 → node_v219 → node_v218 → ...
    ├─ smartsvg_ai.auto_masks_v2111 → numpy, cv2, silhouette_guard_v21111
    │     └─ [import conditionnel] auto_segment_v192 → numpy, cv2, torch, nodes
    ├─ smartsvg_ai.provider_v2112 → numpy, torch, [import conditionnel] nodes
    ├─ smartsvg_native.inspector → cv2, numpy, PIL, smartsvg_quality.geometry
    ├─ smartsvg_vector.layers_v2113 → cv2, numpy, palette_v21132, [save_svg] folder_paths
    └─ smartsvg_compat.readiness_v21112 → auto_segment_v192, [conditionnel] nodes/torch

smartsvg_core.project_archive → project_contracts + [validation] mask_snapshot_g24
smartsvg_core.project_recovery → project_archive (chargement, sauvegarde, sidecars)
smartsvg_core.subject_identity_g33e → mask_snapshot_g24, project_contracts, project_archive
smartsvg_core.mask_binding_g33e → mask_snapshot_g24, subject_identity_g33e
smartsvg_core.__init__ → contracts, reporting ; ne charge pas torch/cv2/PIL.
```

**Précision :** les `...` sont des portions **non entièrement déroulées** de la chaîne historique ; elles ne sont pas des arêtes vérifiées. Le graphe est une représentation de frontières observées, **pas un graphe AST complet**. La présence de `torch` au chargement des nœuds ne signifie pas que `ManagedWorkspace` l'exige.

### Frontières confirmées et conséquences

| Famille / chemins | Dépendances observées | Décision de migration proposée |
|---|---|---|
| `smartsvg_core/project_contracts.py`, `project_archive.py`, `project_recovery.py`, `project_workspace_g22.py`, `mask_snapshot_g24.py`, `subject_identity_g33e.py` | Stdlib, imports relatifs internes ; `project_recovery` emploie `msvcrt` sous Windows ou `fcntl` ailleurs | **Conserver** comme base du noyau projet ; wrapper/port avant toute refonte ; tests d'atomicité Windows requis. |
| `engine/project_routes_g22.py` | `aiohttp` dans `register_project_routes`, `ManagedWorkspace` | **Garder** l'adaptateur ComfyUI historique ; **ne pas** le réutiliser comme serveur autonome sans audit sécurité. |
| `engine/__init__.py`, `node_v*.py` | Registre historique et chaîne d'imports ; `torch`, `numpy`, `folder_paths`, `server.PromptServer` conditionnel | Isoler dans `ComfyUIAdapter` ; ne jamais importer `engine` depuis le bootstrap autonome si cela déclenche les nœuds. |
| `smartsvg_ai/provider_v2112.py`, `auto_segment_v192.py`, `scene_florence_v193.py`, `rmbg_bridge.py` | `numpy`, `torch`, `cv2`, `nodes.NODE_CLASS_MAPPINGS` à l'exécution | Fournisseurs **ComfyUI uniquement** jusqu'à preuve de portabilité ; modèle local direct à concevoir séparément. |
| `smartsvg_ai/auto_masks_v2111.py`, `routing_v21121.py` | `numpy`, `cv2`, garde-fous `MAX_MASKS=32`, `MAX_PIXELS=5_000_000` | Isoler les fonctions déterministes ; mode CPU autorisé sous dépendances explicites ; 50 sujets via partition, non hausse aveugle des bornes. |
| `smartsvg_native/inspector.py`, `smartsvg_vector/layers_v2113.py`, `smartsvg_quality/geometry.py` | `cv2`, `numpy`, PIL ; `save_svg` peut importer `folder_paths` | Extraire les calculs réutilisables ; remplacer la résolution de chemin ComfyUI par un port de sortie borné. |
| `smartsvg_cricut/direct_import_v218.py`, `delivery_v21122.py` | PIL/cv2/numpy pour le premier ; stdlib pour le second | Réutilisation à évaluer par contrat de sortie ; aucune équivalence « import Design Space certifié ». |
| `engine/web/js/smartsvg_express_atelier_preview.html` | imports dynamiques de `../../scripts/api.js` (ComfyUI), `BroadcastChannel`, modules MJS locaux | Séparer logique d'écran, transport, identité et messages ; mode `file://` non réputé équivalent au serveur ComfyUI. |
| `smartsvg_project_panel_g22.mjs`, `smartsvg_subject_handoff_g33.mjs`, `smartsvg_editor_project_bridge_g23.mjs` | MJS internes, ponts UI/projet et messages | Adapter les appels via un client typé ; pas de deuxième store canonique. |

## 3. Analyse de risques de couplage

**C-01 — Import involontaire de ComfyUI :** le `engine/__init__.py` importe `node_v21154` dès le chargement du paquet ; ce n'est pas une entrée autonome sûre. **Contrôle :** bootstrap du futur `smartsvg_app` sans `engine.__init__`, `nodes`, `server`, `folder_paths` ; preuve par import smoke en environnement propre.

**C-01b — Résolution Python du paquet parent (bloquant) :** `import engine.smartsvg_core` **exécute `engine/__init__.py` avant** le sous-paquet, donc charge les nœuds historiques et `torch`. Le simple fait de créer `engine/smartsvg_app/` ne rend pas le bootstrap autonome. Deux stratégies à prototyper : **(A)** point d'entrée natif distinct avec `engine/` déclaré explicitement comme racine d'import et imports top-level `smartsvg_core`/`smartsvg_app` (attention à l'identité des modules si les deux noms coexistent dans un processus) ; **(B)** packaging séparé `src/smartsvg_app/` et distribution du noyau réutilisé sans import `engine`. Ne pas copier les sources ni modifier `engine/__init__.py` sans PR d'implémentation autorisée. **Gate :** `sys.modules` ne contient pas `engine`, `torch`, `nodes`, `server`, `folder_paths` au bootstrap natif minimal ; aucune classe `LoadedProject` dupliquée dans un même processus. La décision définitive attend un spike Windows.

**C-02 — Téléchargement implicite :** `provider_v2112.available()` vérifie les signatures sans inférence, mais `segment_adaptive()` instancie et appelle des nœuds tiers susceptibles de télécharger des poids. **Contrôle :** `ModelConsentGate` avant appel ; réseau interdit par défaut, modèle absent → `AI_UNAVAILABLE` + repli manuel ; ne pas utiliser un ancien provider pour contourner le consentement.

**C-03 — Surface HTTP :** `project_routes_g22` vérifie `X-SmartSVG-UI` et `Origin` sur POST, mais les GET exposent des données projet sans authentification propre à SmartSVG. Ce pont **hérite** du périmètre de sécurité de ComfyUI, pas d'une authentification native autonome. **Contrôle :** transport natif local privilégié ; si HTTP loopback nécessaire, jeton de session fort + validation Host/Origin + CORS fermé + limites corps/temps + vérification de droits pour GET/POST ; ne jamais exposer ce serveur sur `0.0.0.0`.

**C-04 — Identité/révision :** le workspace utilise SHA-256 du fichier comme révision observée, le nouveau bus propose un entier `expected_revision`. **Contrôle :** ne pas substituer un compteur aux SHA historiques sans contrat de correspondance, journal et migration ; CAS compare le hash réel sous verrou.

**C-05 — Sidecars de récupération :** `save_with_recovery` peut laisser `.pending-backup.smartsvg` après publication interrompue ; le prochain adaptateur doit afficher et résoudre ce cas explicitement, sans écraser `.previous.smartsvg`.

**C-06 — Format :** `smartsvg-project/1` est borné à 256 entrées, 64 MiB par membre, 256 MiB total, 280 MiB d'archive et 5 000 opérations. Les propositions de fabrication/IA doivent être versionnées et budgetées ; aucune écriture V3.4 dans un ancien projet sans migration contrôlée.

**C-07 — UI multi-onglets :** `BroadcastChannel` et l'import `../../scripts/api.js` ne sont pas des transports universels. Les événements ne font jamais autorité ; reprise par lecture de snapshot canonique et détection de révision obsolète.

## 4. Procédure de génération du graphe complet (travail encore ouvert)

**À produire en micro-ticket V34-017 :** script futur `tools/architecture/build_import_graph.py` (fichier **non existant**), entrée = arbre de fichiers Git à un SHA épinglé ; parser tous les 148 modules Python de production via `ast`, tous les 30 fichiers frontaux via parseur ECMAScript approprié ; distinguer `import`, `from`, imports conditionnels, dynamiques, dépendances externes, accès par `folder_paths`, routes, fetch, WebSocket, `BroadcastChannel` ; résoudre imports relatifs et conserver les arêtes incertaines en `UNRESOLVED`. Export proposé : `docs/roadmap-v3.4/generated/import_graph.json` + diagramme et `unresolved_imports.md`. Inclure `engine/tests` et `tests` comme vérification secondaire, pas comme modules de production.

**Assertions futures :** couverture de chemins `148/148` et `30/30` à SHA fixe, aucune arête inconnue supprimée silencieusement, aucun import ComfyUI depuis le bootstrap autonome, analyse de cycles SCC et des imports dynamiques, comparaison du graphe entre `main` et branche d'implémentation. **Aucun script n'a été exécuté** : il s'agit d'une spécification d'analyse, non d'une preuve d'exhaustivité.

## 5. Critères de revue de cette annexe

- Inventaire `git/trees` complet (`truncated=false`) : **observé** ; graphes complets AST/ESM : **NON_EXECUTE**.
- Aucun nom de fichier inexistant traité comme implémenté ; dépendances tierces seulement constatées sur le code lu.
- Les imports dynamiques et les appels réseau sont des frontières à tester, pas des dépendances résolues automatiquement.
- Relecture de `AGENTS.md`, roadmap V3.3 et lot 03 ; V3.3, archives, code, workflows et tâches planifiées inchangés.
