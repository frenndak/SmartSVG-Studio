# SmartSVG Studio V3.4 — Lot 21/24 : installation Windows, hors ligne, mises à jour et récupération

**DRAFT documentaire — 29 octobre 2026.** Roadmap active **V3.3** ; fonctions déjà approuvées **F10/F14/F15, P10, G8** et exigences **S-022, S-042, S-046, S-053, S-061, S-063, S-084, S-094, S-095 ; R33-009/013/015/016/021/025/030/033/034/038/040**. Aucun nouvel objectif fonctionnel, aucune implémentation, aucun installateur produit. Base réellement relue : `main@fff374e5147689165839bd76e742713d714ff147` ; branche avant lot `7f4a219ffb293774eca699dae689312b478c5e70` ; ancêtre commun `fdbda304beb77d97340a8be4dd5c5e9cefde15f4`. Tous les tests ci-dessous sont **SPÉCIFIÉS / NON_EXECUTE**.

## 1. Contre-expertise du lot 20 : trois écarts concrets

1. **La bibliothèque et la récupération existent en noyau, pas dans une application Windows autonome.** `engine/smartsvg_core/project_workspace_g22.py` et `project_recovery.py` sont indépendants du serveur ComfyUI, mais `engine/__init__.py` importe immédiatement `node_v21154` ; `engine/project_routes_g22.py` dépend de `aiohttp`/ComfyUI. **Correction :** le lancement natif doit importer les modules `smartsvg_core` depuis une racine Python isolée de l'initialiseur historique, et n'activer aucun adaptateur ComfyUI par défaut. Ne pas promettre qu'un simple raccourci vers l'HTML actuel constitue une application native.
2. **L'installation actuelle est celle d'une extension, pas celle d'un logiciel indépendant.** `engine/GUIDE_INSTALLATION_V21_15_2.md` prescrit une copie dans `ComfyUI/custom_nodes`, un redémarrage et un rollback manuel ; `engine/requirements.txt` liste `numpy>=1.24`, `Pillow>=10`, `opencv-python>=4.7` sans environnement autonome verrouillé. `INSTALLATION_MANIFEST_V21_15_2.json` est un manifeste historique d'extension, **pas** une preuve de package Windows autonome. **Correction :** conserver ce parcours legacy ; définir séparément une distribution native après le spike `V34-019`, avec inventaire reproductible de dépendances et intégrité de l'artefact livré, sans imposer maintenant Qt/Tauri/format MSI.
3. **Le rollback logiciel ne doit pas être confondu avec le recovery projet.** `project_recovery.py` possède verrou OS, `.previous.smartsvg`, `.pending-backup.smartsvg`, `inspect_project`, `resolve_pending_backup` et confirmations ; ces fonctions protègent des **projets**, pas un binaire, ses dépendances ou une mise à jour interrompue. **Correction :** isoler répertoires d'application, données utilisateur, modèles consentis et exports ; mise à jour/retour logiciel ne supprime ni ne convertit implicitement les projets. Réutiliser le recovery G1.4, sans deuxième writer.

**État prouvé par lecture de code :** modules ci-dessus, `project_archive.py` (ZIP borné et écriture atomique), `diagnostic_v2132.py` (diagnostic sans téléchargement ni inférence), `smartsvg_quality/release_gate_v21152.py` (QA export non physique), `engine/tests/test_project_recovery_g14.py` (fixtures de tests présentes). **Non prouvé :** binaire/installeur autonome, démarrage Windows sans ComfyUI, signature de livraison, mise à jour native, tests offline par interception réseau, antivirus/NTFS/OneDrive, compatibilité Windows réelle, RTX 3070 ou Cricut.

## 2. Dépendances minimales, chemins parallèles et choix de packaging

| Chemin approuvé | Obligatoire avant revendication correspondante | Parallélisable / non prérequis |
|---|---|---|
| **Extension ComfyUI existante** | Guide V21.15.2, vérification du package et anciens workflows/IDs, backup du dossier de nœuds | V3.4, format V2, installateur natif, nouveau framework : **non prérequis** à G3.3e-b2a |
| **Lecture/édition locale CPU/manuelle native** | `V34-019` bootstrap sans import ComfyUI/torch, `V34-018` port projet si mutation, V1 et CAS/recovery G1.4, UI minimale accessible | IA, téléchargement de modèle, RTX 3070, migration V2, G4 et tests Cricut : **non prérequis** au démarrage |
| **Distribution Windows autonome** | Bootstrap natif réellement testé, inventaire des dépendances transitives et licences, artefact vérifiable, chemins de données, installation/désinstallation/rollback | Choix PySide6 vs Tauri+Python **non figé** ; comparer prototypes avant engagement, pas d'installeur imposé à la V3.3 |
| **Mise à jour contrôlée** | Paquet de provenance fiable et empreinte attendue, vérification de compatibilité projet, sauvegarde de l'installation précédente, repli sans écraser les données | Service de mise à jour automatique et requête réseau en arrière-plan **non nécessaires** ; paquet local choisi manuellement accepté |
| **Modèles IA opt-in** | `V34-078/079/086` si un modèle est réellement utilisé : licence/hash/consentement | Aucun poids fourni ou téléchargé par défaut ; mode manuel/CPU reste disponible |

**Décision de proportionnalité :** deux distributions possibles du **même noyau**, extension legacy et application native future. Pas deux bases de projets, pas deux systèmes de sauvegarde, pas de copie automatique de projets depuis ComfyUI. L'absence de ComfyUI doit être un état normal du natif, non une erreur de dépendance.

## 3. Parcours novice et expert, écrans/états et messages FR

**Novice :** installer depuis une source explicitement choisie → ouvrir SmartSVG sans réseau → « Importer / Créer / Reprendre » → choisir un `.smartsvg` existant → inspection non destructive et aperçu → travailler en manuel/CPU → sauvegarder et rouvrir. Si une fonction exige un modèle absent : « Modèle facultatif non installé — Continuer sans IA / Voir les modèles », jamais un téléchargement automatique. Si archive future : « Projet créé avec une version plus récente : lecture refusée sans modification. Gardez ce fichier et ouvrez-le avec une version compatible. »

**Expert :** afficher version app, Python et bibliothèques réellement embarquées, SHA de paquet, état du projet et du recovery, transport utilisé, fournisseurs installés/consentis, erreurs expurgées ; lancer des diagnostics locaux et exporter un rapport **sans chemin personnel complet, média, token ni données privées**. Le diagnostic ne déclare pas la RTX ou la machine « testée » sur simple présence matérielle.

**Wireframe textuel minimal (mêmes espaces Express/Expert, sans écran autonome supplémentaire imposé) :**

```text
[SmartSVG Studio] [Importer] [Créer] [Reprendre]         [Mode : Manuel / IA facultative]
[Projet : nom • SHA court • état SAIN / À EXAMINER / INCOMPATIBLE]
[Actions : Ouvrir | Vérifier | Sauvegarder | Récupérer...]
[Statut : Hors ligne • Version • Source du paquet]      [Aide et diagnostic]
En cas d'incident : [Voir les détails] [Conserver] [Restaurer avec confirmation]
Mise à jour : [Choisir un paquet local] [Vérifier] [Installer] [Retour version précédente]
```

L'option « Restaurer » n'est activée qu'après `inspect_project`, lecture du SHA attendu et confirmation explicite ; elle ne doit jamais écraser un primaire sain. Les actions critiques sont accessibles au clavier, annoncent état/erreur, restent annulables avant publication et sont traduites en français. Le mode Expert n'affiche aucun secret.

## 4. Contrats d'exécution, sécurité et mise à jour (sans nouveau store)

**Frontière de lancement.** L'entrée native ne doit pas importer `engine` comme paquet : `engine/__init__.py` charge `node_v21154`. Le spike `V34-019` doit prouver un import direct et propre du noyau depuis une racine empaquetée appropriée, sans `nodes`, `server`, `folder_paths`, `torch` ni `aiohttp` obligatoires au **démarrage manuel**. Un module importé plus tard par une fonctionnalité facultative ne doit pas bloquer l'accueil. Les API de fichiers ComfyUI restent opt-in et ne sont pas exposées telles quelles en HTTP natif.

**Données et sécurité.** Les projets, backups, modèles, exports et préférences sont séparés des binaires et conservés lors d'une désinstallation par défaut (suppression de données seulement sur choix explicite et vérifiable). Aucun chemin externe arbitraire depuis l'UI/IPC ; canoniser la destination, refuser liens dangereux, traversées, ZIP hostiles, tailles hors budget et remplacements de fichiers étrangers. Conserver le SHA CAS des projets, les sources immuables et les snapshots float32. Aucune requête réseau, télémétrie ou recherche de mise à jour au démarrage ; consentement explicite pour toute connexion. Le hash contrôle l'intégrité, **pas à lui seul l'authenticité** : la provenance de distribution doit être documentée ; signature à vérifier lorsqu'elle existe, sans la présenter comme déjà disponible.

**Protocole de mise à jour proposée :** 1) choisir paquet local ou consentir explicitement à sa récupération ; 2) vérifier provenance, hash, manifestes, licences et compatibilité ; 3) fermer ou isoler le processus courant, préparer une installation parallèle dans un emplacement contrôlé ; 4) conserver l'ancienne version et **ne pas migrer** les projets automatiquement ; 5) démarrer/diagnostiquer la nouvelle version et tester ouverture **en lecture seule** d'un projet V1 synthétique ; 6) activer la nouvelle version seulement après contrôle ; 7) en échec, réactiver l'ancienne version et garder données/sidecars inchangés. Si des binaires sont verrouillés par Windows, différer l'activation au redémarrage et signaler l'état ; ne jamais effacer le paquet sain en place. La migration V1→V2 est un workflow distinct du lot 05, avec consentement et copie.

**Récupération après incident :** utiliser `inspect_project` puis `resolve_pending_backup`/`recover_previous` seulement sous leurs gardes et confirmation. État `PENDING_BACKUP_REVIEW_REQUIRED` → bloquer les écritures, afficher principal/backup/staging et empreintes, laisser choisir explicitement la récupération ; conflit `BACKUP_CONFLICT` ou `PROJECT_LOCKED` → conserver les trois candidats et expliquer la reprise, jamais supprimer le sidecar « gênant ». Un job export interrompu reprend selon les contrats des lots 17/19/20, pas via la restauration du projet.

## 5. Tests exacts proposés — tous NON_EXECUTE

| ID | Assertion et fixture / action | Preuve à produire | Ticket |
|---|---|---|---|
| T-V34-21-01 | Lancement natif avec `ComfyUI/nodes/server/folder_paths/torch` absents ; accueil + ouverture V1 synthétique + sauvegarde manuelle, aucun import obligatoire de ces modules | auto (imports interceptés) + Windows neuf | V34-019 |
| T-V34-21-02 | Extension legacy V21.15.2 chargée avec nœuds/ports/workflows inchangés après installation et rollback documenté | auto ciblé + ComfyUI Windows | V34-020, V34-139 |
| T-V34-21-03 | Réseau interdit par interception DNS/HTTP au démarrage, import, export CPU, refus IA et ouverture projet : zéro requête, zéro poids téléchargé | auto + Windows hors ligne, trace réseau expurgée | V34-023, V34-140 |
| T-V34-21-04 | Paquet modifié, incomplet, de provenance inconnue ou SHA incorrect : refus avant activation ; installation courante et données identiques | auto + Windows ; SHA avant/après | V34-139 |
| T-V34-21-05 | Coupure injectée pendant staging/activation et binaire Windows verrouillé : ancienne ou nouvelle version valide au redémarrage, jamais installation partielle active | auto simulation + Windows réel | V34-139 |
| T-V34-21-06 | Mise à jour puis rollback logiciel : mêmes octets `.smartsvg`, `.previous`, `.pending-backup`, masques float32, modèles consentis et exports | auto + Windows, empreintes comparées | V34-139, V34-022 |
| T-V34-21-07 | Chemins Unicode/espaces, compte sans admin, disque plein, fichier en lecture seule, antivirus ou répertoire synchronisé : erreur explicite et absence d'écrasement | auto injection + Windows cas réels séparés | V34-139, V34-022 |
| T-V34-21-08 | Projet sain, corrompu, version future et `PENDING_BACKUP_REVIEW_REQUIRED` : aucune restauration sans confirmation ; après accord, SHA et projet revalidés | auto existant G1.4 étendu + Windows | V34-022, V34-140 |
| T-V34-21-09 | Rapport diagnostic exporté : aucune image/chemin privé/secret ; états « présent », « testé », « absent » distincts, clavier et messages FR utilisables | auto filtrage + Windows UX | V34-024, V34-140 |
| T-V34-21-10 | Désinstallation : aucun projet/backup/modèle utilisateur supprimé par défaut ; suppression facultative exige confirmation distincte | auto + Windows réel | V34-139 |

**Preuves orthogonales :** `preuve_auto` et `preuve_windows` requises avant revendication Windows ; `preuve_design_space` et `preuve_physique` = **NON_APPLICABLE pour le seul installateur si motivé**, mais demeurent **NON_EXECUTE** pour les exports, Score/Attach, Print Then Cut et coupes. `preuve_gpu` séparée pour l'inférence RTX 3070 ; aucun succès présumé. Chaque future exécution conserve commit SHA, package SHA, OS/édition, runtime, commandes, fixture, sortie et logs expurgés.

## 6. Backlog minimal, sans duplication des tickets existants

| Ticket | Priorité, dépendances et livrables FUTURS (non créés) | DoD et rollback |
|---|---|---|
| **V34-139 — Distribution Windows réversible** | **P1** ; S-042/S-063/S-095, R33-016/021/025/034/038 ; dépend **V34-019 uniquement pour la variante native**, **V34-020** pour non-régression legacy. Candidats : `packaging/windows/`, `tests/v34/test_windows_install_update.py`, `docs/install/WINDOWS_RELEASE.md` (chemins à confirmer par prototype). | T-V34-21-02/04/05/06/07/10 ; paquet versionné et vérifié, installation/rollback/désinstallation Windows testés, données inchangées ; rollback réactiver ancienne version. Aucune technologie d'installeur imposée. |
| **V34-140 — Hors ligne, diagnostics et recovery au lancement** | **P1** ; S-053/S-061/S-084/S-095, R33-013/015/030/033 ; réutiliser **V34-022/023/024** et G1.4, sans deuxième moteur. Candidats : `tests/v34/test_offline_startup.py`, `tests/v34/test_startup_recovery.py`, adaptation du panneau existant (chemin à confirmer). | T-V34-21-03/08/09 ; aucun réseau implicite, aucune restauration silencieuse, erreurs actionnables FR, rapport expurgé, tests auto+Windows ; rollback masquer diagnostic natif et conserver recovery G1.4. |

**Réemploi des tickets existants :** `V34-019` bootstrap ; `V34-020` compatibilité ComfyUI ; `V34-022` crash/recovery ; `V34-023` providers/réseau ; `V34-024` capacités ; `V34-078/079/086` modèles facultatifs. Ne pas créer un deuxième système d'installation de modèles ni un second registre de preuves. Les tickets V34-139/140 ne sont pas des nouveaux gates pour G3.3.

## 7. Risques, arbitrages et prochaine étape

- **Risques ouverts :** graphe d'imports exhaustif `V34-017` non prouvé ; choix de framework et bundle non arbitré ; versions/licences transitives et empreintes de distribution à établir ; politique de signature/éditeur à décider ; collisions de chemins Windows, antivirus, OneDrive et fichiers verrouillés ; round-trip V1 et modèles facultatifs non qualifiés sur Windows ; aucun essai matériel.
- **Non-décisions explicites :** pas de PySide6/Tauri/ONNX obligatoire, pas de service de mise à jour, pas de signature prétendue existante, pas de migration V2 cachée, pas de lancement direct de Design Space, pas de pilotage Cricut. G3.3e-b2a et les fixtures G4 avancent en parallèle.
- **Prochain lot 22 :** corpus, protocoles de tests auto/UX/Windows/RTX/Design Space/physique, métriques et traçabilité des preuves **sans inventer de résultats**. Le lot 23 réconciliera exhaustivement les 141 exigences avec tickets/tests.

**Sources internes vérifiées le 29/10/2026 :** `AGENTS.md`, `docs/ROADMAP_MASTER_v3_3.md`, `docs/ROADMAP_TRACEABILITY_v3_3.md`, `docs/ROADMAP_COVERAGE_v3_3.md`, `docs/ROADMAP_HERITAGE_v3_3.md`, `docs/ROADMAP_EXECUTION_FASTPATH_v3_3.md`, `README.md`, `docs/ETAT_ACTUEL_SMARTSVG.md`, `engine/__init__.py`, `engine/project_routes_g22.py`, `engine/requirements.txt`, `engine/GUIDE_INSTALLATION_V21_15_2.md`, `engine/INSTALLATION_MANIFEST_V21_15_2.json`, `engine/smartsvg_core/project_archive.py`, `engine/smartsvg_core/project_recovery.py`, `engine/smartsvg_core/project_workspace_g22.py`, `engine/diagnostic_v2132.py`, `engine/tests/test_project_recovery_g14.py` et lots 04/05/11/20. Pas de nouvelle affirmation Cricut nécessitant une source externe.
