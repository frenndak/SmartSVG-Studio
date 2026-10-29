# SmartSVG Studio V3.4 — Lot 07 : accueil, Express, navigation et ergonomie contractuelle

**DRAFT / SPÉCIFICATION NON IMPLÉMENTÉE — 29 octobre 2026.** V3.3 demeure ACTIVE (101 S + 40 R33). Issue de suivi #72 ; PR documentaire #73. Base `main` observée : `fdbda304beb77d97340a8be4dd5c5e9cefde15f4` ; branche en avance de 31 commits, 0 retard avant ce lot. Aucune preuve Windows, RTX 3070, Design Space ou Cricut physique. Tous les composants `smartsvg_app/*` et `v34_*` ci-dessous sont **des fichiers futurs proposés**.

## 1. Constat réel, besoin, frontière

**Constat par lecture du HEAD :** `engine/web/js/smartsvg_express_atelier_preview.html` contient déjà une navigation Importer / Mes sujets / Retouches / Contour & découpe / Exporter, un workflow visuel à six étapes, des raccourcis de zoom, un import de prévisualisation PNG/JPEG/WebP, 12 escargots **fictifs**, un panneau de choix Cut / Print Then Cut / SVG éditable, des commandes de sélection, une inspection SVG réelle facultative et l'accès volontaire au gestionnaire de projets ComfyUI (création PNG uniquement). Le document `docs/ETAT_ACTUEL_SMARTSVG.md` précise que l'Atelier n'effectue pas de segmentation IA depuis cet import, ne vectorise pas automatiquement, et dépend encore du serveur ComfyUI pour les modules réels. **Ne pas recréer ces composants à l'identique** ; les extraire/raccorder après audit des dépendances.

**Problème utilisateur :** l'accueil doit proposer un point d'entrée évident sans obliger un débutant à connaître les nœuds, les modes SVG ou les six étapes ; un expert doit conserver les opérations précises. Les six espaces Express / Atelier / Fabrique / Vectoriel / Bibliothèque / Expert ne doivent pas devenir six projets, six états contradictoires ou six éditeurs dupliqués.

**Non-objectifs :** aucun développement pendant ce cycle ; pas de logiciel « prêt à découper » sans prévol et preuves ; pas de pilotage direct de Design Space ; pas de dimensions physiques inventées ; pas de téléchargement IA implicite ; pas de création V2 silencieuse depuis un projet V1 ; pas de faux état « enregistré » avant receipt durable.

**Héritage applicable sans déclassification :** F01/F02/F04/F07/F10/F14/F15, P01/P02/P04/P08, S-003, S-008, S-013..016, S-023..026, S-053, S-067..084, S-093..096, S-100, R33-003..008, R33-011..014, R33-017..020, R33-022..025, R33-033, R33-039. L'index `HERITAGE_INDEX.md` conserve les 141 entrées ; ce lot **n'est pas** une matrice inverse exhaustive.

## 2. ADR-034-10 : une seule session, plusieurs espaces, navigation sans mutation

**Options comparées :** (A) six stores indépendants — **REJET**, divergence et Undo incohérent ; (B) routeur avec store UI autoritaire — **REJET**, concurrence avec archive `.smartsvg` ; (C) **RECOMMANDÉ sous spike** : `AppShell` + `ProjectSession` en lecture, commandes uniquement via `CommandPort` V34-032/037, `ViewState` éphémère et `DraftState` non canonique. Le projet V2, ses receipts et ses révisions restent la vérité ; une vue peut se démonter/recharger sans changer le document.

**Invariants contractuels :**
1. Changer de vue ne publie jamais de commande. Les paramètres non confirmés restent dans `DraftState` lié à un `base_project_sha256` ; après changement externe du SHA, le brouillon est comparé/abandonné, jamais appliqué automatiquement.
2. Toute commande de mutation passe par `CommandPort` avec `command_id`, epoch, CAS SHA et receipt. Un message `CommandCommitted` est seulement une notification ; l'UI affiche « Enregistré » après receipt durable et vérification de la révision, pas après un clic.
3. Un job IA est un producteur de **proposition**, jamais un writer. `ProposalBundle` et sa provenance sont distincts de la sélection locale ; aucun modèle installé est un état valide.
4. Un export externe est un effet non annulable. Le badge `EXPORTED_UNVERIFIED` ne vaut ni validation Design Space ni fabrication. Un Undo ne « récupère » pas une feuille imprimée.
5. Chaque vue consomme les mêmes `ProjectSummary`, `Capabilities`, `JobState`, `PreflightSummary` et `OutputContract` ; pas de champ de preuve recalculé dans le navigateur.
6. V1 ouvert dans un shell V3.4 : lecture seule ou édition historique explicitement disponible ; fonctionnalités V2 indisponibles avec bouton « Enregistrer une copie migrée » après prévol. Jamais de conversion automatique.

### 2.1 Diagramme logique (interfaces futures)

```text
                         AppShell (routeur, focus, raccourcis)
                           |              |
      Accueil / Express / Atelier / Fabrique / Vectoriel / Bibliothèque / Expert
                           |              |
                    SessionPresenter ---- DraftStore (éphémère)
                           |
        ProjectReadPort -- CommandPort -- JobPort -- CapabilityPort
              |                 |           |           |
         .smartsvg V1/V2   writer unique   propositions  profils vérifiés
              |                 |           |
        CAS SHA, receipts, history, recovery / adapters ComfyUI optionnels
```

**Frontières :** `AppShell` ne lit pas les ZIP directement ; `SessionPresenter` ne valide pas la géométrie ; `PreflightPort` seul retourne les diagnostics de fabrication ; `CapabilityPort` distingue `AVAILABLE_VERIFIED`, `AVAILABLE_UNTESTED`, `UNAVAILABLE`, `UNKNOWN`. La disponibilité du code ne prouve pas sa qualification terrain.

## 3. Parcours novices et experts

### 3.1 Accueil — premier lancement / reprise

```text
┌ SmartSVG Studio ──────────────────────────────────────────────────────┐
│ [Importer une image]   [Créer un projet]   [Reprendre un projet]       │
│ [Sans IA ✓] [Local ✓] [Explore 5 : profil à vérifier] [Aide]           │
│ Derniers projets : [Boîte carton · r7] [Escargots · r4]                │
│ Tâches interrompues : [Analyse 12 sujets · NON RELANCÉE] [Inspecter]  │
│ Aucune source personnelle affichée en miniature sans consentement.   │
└───────────────────────────────────────────────────────────────────────┘
```

**Importer :** sélection fichier ou glisser-déposer ; inspecteur de format/orientation/alpha/taille et vérification de sécurité ; **copie de travail immuable** (ou import temporaire contrôlé) ; écran d'intention. Un fichier non pris en charge est refusé sans modifier un projet. **Créer :** choisir un patron paramétrique, un document vide ou un modèle local ; dimensions obligatoires pour la fabrication, unités mm explicites. **Reprendre :** sélectionner un `.smartsvg` local, afficher sa version/compatibilité et l'état de récupération, vérifier sidecars avant toute mutation.

**Action rapide novice :** objectif de **1 à 3 décisions significatives**, non de trois clics physiques garantis. Cas nominal : (1) importer ; (2) choisir intention suggérée ou explicite ; (3) contrôler dimensions et confirmer la préparation. Les vérifications, corrections de masque, paramètres d'impression et opérations Design Space peuvent demander davantage d'actions ; ne jamais sacrifier sécurité/qualité au KPI.

### 3.2 Express — import → intention → prévol → sortie

```text
┌ Projet Escargots [r4 · Enregistré] [Annuler] [Rétablir] [Historique] ┐
│ [Express] [Atelier] [Fabrique] [Vectoriel] [Bibliothèque] [Expert]   │
├───────────────────────────┬──────────────────────────────────────────┤
│  Planche / image source   │ Que souhaitez-vous faire ?               │
│  [Avant | Après] [Zoom]   │ (•) Autocollants imprimés puis découpés   │
│  [12 sujets détectés*]    │ ( ) Silhouettes découpées                 │
│  [Sélection/correction]   │ ( ) Dessin au stylo / Patron / Autre     │
│                           │ Taille [ 40 ] mm [Vérifier]              │
│                           │ Profil [Explore 5, non qualifié]         │
│                           │ [Vérifier] [Exporter brouillon]           │
├───────────────────────────┴──────────────────────────────────────────┤
│ ⚠ Région Print Then Cut A4 non vérifiée : vérifier dans Design Space │
│ [Corriger la taille] [Voir les détails] [Continuer avec avertissement]│
└──────────────────────────────────────────────────────────────────────┘
* « détectés » uniquement si preuve de détection réelle ; démo = « exemples ».
```

**Règle d'intention :** si l'utilisateur choisit « sticker », proposer Print Then Cut **sans transformer un SVG de coupe en PNG imprimable silencieusement**. Si l'utilisateur choisit « boîte », demander dimensions et matière, puis distinguer SCORE et BASIC_CUT. Un bouton `Exporter` est inactif si une erreur bloquante du prévol existe ; en état inconnu, proposer `Exporter brouillon non vérifié` si le contrat l'autorise, jamais « Prêt Cricut ».

### 3.3 Expert et navigation inter-espaces

- **Atelier** : sélection, corrections non destructives, calques, dimensions ; ne modifie le projet qu'après commande validée.
- **Fabrique** : opérations Cut/Score/Draw/Foil, outil/matière/machine, prévol et guide Design Space ; jamais un contrôle direct de la machine.
- **Vectoriel** : contours, topologie, géométrie éditable distincte de la géométrie de coupe.
- **Bibliothèque** : copies, variantes, recettes, projets récents ; aucune importation silencieuse de données privées.
- **Expert** : diagnostics, preuves, modèles facultatifs, provenance, journaux expurgés, adaptateur ComfyUI.
- **Express** : masque la complexité mais ne masque jamais un échec ou une incertitude critique.

**Navigation :** `route = (space, project_id?, selection_ids?, panel?, return_to?)` ; seuls `space` et `panel` sont mémorisables dans des préférences locales. Les identifiants de sujet sont résolus contre le snapshot courant ; une sélection périmée devient `SELECTION_STALE` et l'UI affiche « Cet objet a changé, sélectionner à nouveau ». Aucune URL externe contenant un chemin privé.

## 4. Modèles de données, commandes et événements (SPÉCIFICATION)

```json
{
  "contract": "smartsvg-ui-session/1-draft",
  "project_id": "demo-escargots",
  "archive_schema": "smartsvg-project/2-draft",
  "file_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "logical_revision": 4,
  "command_epoch": 2,
  "route": {"space": "EXPRESS", "panel": "INTENT", "selection_ids": []},
  "capabilities": {"ai_local": "UNAVAILABLE", "print_then_cut": "AVAILABLE_UNTESTED"},
  "draft": {"kind": "INTENT", "base_project_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "intent": "STICKERS", "target_width_mm": 40},
  "jobs": [],
  "save_state": "SAVED_CONFIRMED",
  "preflight": {"state": "UNKNOWN", "blocking": [], "warnings": ["A4_REGION_UNVERIFIED"]},
  "output": {"contract": "PNG_PRINT_THEN_CUT", "status": "DRAFT_ONLY"}
}
```

**Types et contraintes :** `space ∈ {HOME,EXPRESS,ATELIER,FABRIQUE,VECTORIEL,BIBLIOTHEQUE,EXPERT}`; `save_state ∈ {NO_PROJECT,UNSAVED_DRAFT,SAVING,SAVED_CONFIRMED,CONFLICT,RECOVERY_REQUIRED,READ_ONLY}`; `preflight.state ∈ {NOT_RUN,PASS,WARNING,BLOCKED,UNKNOWN}`; `target_width_mm` nombre fini strictement positif, jamais inféré d'une photographie sans étalon explicite ; `file_sha256` 64 hex ; `logical_revision` entier ≥0 pour V2 seulement ; pour V1, valeur absente et aucune conversion implicite. Le JSON est **un exemple logique** : aucun parseur ni schéma exécutable n'existe pour ce contrat.

**Commandes (via bus V34-032) :** `ImportSource`, `ConfirmIntent`, `SetObjectTransform`, `AcceptSubjectsBatch`, `AssignOperation`, `SetFabricationProfile`, `Undo`, `Redo`, `SaveProjectCopy`. **Requêtes non mutantes :** `InspectSource`, `ReadProject`, `PreviewIntent`, `RunPreflight`, `PlanExport`, `RequestJob`, `CancelJob`, `InspectRecovery`. `ConfirmIntent` ne signifie pas que l'export est faisable. `CreateBlankProject` / `CreateTemplateDraft` sont **candidats à définir au cycle 16** ; aucun nouvel identifiant d'API n'est prétendu existant.

**Événements :** `ProjectLoaded`, `ProjectSnapshotChanged`, `CommandCommitted`, `CommandRejected`, `JobStateChanged`, `ProposalReady`, `PreflightChanged`, `CapabilitiesChanged`, `RecoveryRequired`, `ExportProduced`. Tout événement de mutation contient `project_id`, `logical_revision` si V2, `project_sha256`, `event_id`; en cas de trou d'événements, recharger `ProjectReadPort`, ne pas appliquer un delta aveuglément.

**Pseudocode déterministe, non exécuté :**
```python
def on_confirm_intent(session, intent, params):
    assert valid_intent(intent) and finite_mm(params)
    snapshot = project_read_port.read(session.project_id)
    if session.draft.base_project_sha256 != snapshot.file_sha256:
        return UIResult("CONFLICT", actions=["compare", "reload", "discard_draft"])
    preview = preview_port.plan(snapshot, intent, params)  # sans écriture
    if preview.blocking_errors:
        return UIResult("BLOCKED", fixes=preview.fixes)
    return command_port.submit(
        kind="ConfirmIntent", expected_project_sha256=snapshot.file_sha256,
        payload=preview.confirmable_payload, command_id=new_unique_id())
```

**Idempotence :** double clic « Confirmer » désactive le bouton localement, mais la protection effective est le receipt durable (V34-034). Après ACK perdu, interroger le receipt ; ne pas fabriquer un second command_id. Un état `SAVING` n'est pas `SAVED_CONFIRMED`.

## 5. Machine d'états UX, erreurs, récupération, Undo et jobs

| État | Affichage novice | Action sûre | Interdit |
|---|---|---|---|
| HOME_EMPTY | « Importer / Créer / Reprendre » | import local / créer brouillon | export sans projet |
| SOURCE_INSPECTING | « Analyse du fichier… » | annuler lecture | promettre détection |
| SOURCE_UNSUPPORTED | « Ce format ne peut pas être ouvert ici » | convertir manuellement / choisir autre | modifier source |
| INTENT_REQUIRED | « Quel résultat souhaitez-vous ? » | choix explicite | inférer dimensions |
| JOB_RUNNING | « Détourage en cours… » | annuler calcul / continuer manuellement | muter le projet |
| PROPOSAL_READY | « 12 sujets proposés, à vérifier » | sélectionner / accepter | auto-commit |
| PARTIAL_BATCH | « 10 réussis, 2 à revoir » | conserver propositions / relancer 2 | prétendre 12 réussis |
| UNSAVED_DRAFT | « Modifications non enregistrées » | enregistrer / abandonner | masquer le risque |
| SAVING | « Enregistrement en cours » | attendre / consulter état | badge « enregistré » |
| CONFLICT | « Projet modifié ailleurs » | comparer / recharger / copie | last-writer-wins |
| RECOVERY_REQUIRED | « Sauvegarde à inspecter » | inspecter sidecars, lecture seule | retry automatique |
| READ_ONLY | « Version non modifiable ici » | ouvrir / copier migrée | mutation V1→V2 implicite |
| PREFLIGHT_WARNING | « Vérification Design Space nécessaire » | corriger / brouillon marqué | « prêt machine » |
| PREFLIGHT_BLOCKED | « Export de fabrication bloqué » | voir correctif | exporter comme validé |
| EXPORTED_UNVERIFIED | « Fichier créé, import non testé » | ouvrir dossier / guide | affirmer coupe réelle |

**Récupération :** écran `RECOVERY_REQUIRED` accessible depuis Accueil et toute vue ; afficher `primary/pending/previous` avec horodatages et statut de validation **sans** proposer « restaurer le plus récent » automatiquement. Une fermeture de fenêtre pendant un job laisse l'archive inchangée ; à la réouverture, tentative `INTERRUPTED`, nouveau lancement explicite. Un brouillon non canonique peut être sauvegardé en zone locale privée avec durée de conservation déclarée, hash et chiffrement éventuel à qualifier ; ce brouillon **n'est pas** une preuve de sauvegarde `.smartsvg`.

**Undo/Redo :** boutons affichés si history disponible ; libellé « Annuler la retouche (12 sujets) », jamais « Annuler l'impression ». Après `CommandCommitted`, focus reste sur l'action pertinente, et un `aria-live=polite` annonce la nouvelle révision. Si l'archive a changé, afficher conflit sans Undo optimiste. Historique et raccourcis identiques dans tous les espaces.

**IA facultative :** `Sans IA` est la voie par défaut ; bouton « Améliorer avec IA locale » ouvre un catalogue informatif `installer maintenant / plus tard / jamais`, sans téléchargement ni appel réseau avant consentement. L'absence de modèle ne bloque ni l'import ni l'édition manuelle ni l'export déterministe quand le contrat est satisfait. Le cycle 11 décidera des modèles/licences ; **aucun nom de modèle n'est ici déclaré installé**.

## 6. Accessibilité, performance et vérification ergonomique

**Cibles de conception (non mesurées) :** 1366×768 et 1280×720 sans action essentielle cachée ; 200 % zoom texte sans perte des contrôles critiques ; navigation au clavier complète, Tab/Shift+Tab et Escape, focus visible et non masqué ; drag-and-drop toujours doublé d'un bouton ; libellés FR, contraste testé, erreurs en texte + icône (pas couleur seule), états asynchrones annoncés sans spam, réduction des animations ; pas de piège clavier. Pour un canevas non accessible directement, proposer liste d'objets avec sélection/déplacement par champs numériques et commandes clavier. **Référence W3C WCAG 2.2** : https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/ (consultée le 29 octobre 2026) ; WCAG est un objectif de recette, pas une conformité certifiée.

**Raccourcis candidats (à qualifier selon framework) :** Ctrl+O ouvrir ; Ctrl+S sauvegarder si mutation en attente ; Ctrl+Z / Ctrl+Shift+Z Undo/Redo ; Ctrl+0 ajuster à la fenêtre ; ? aide contextuelle ; Esc annuler la sélection ou fermer le panneau, **jamais** annuler silencieusement une transaction en cours. Dans un champ de texte, Ctrl+Z doit annuler le texte local, pas le projet ; exposer l'exception dans les tests.

**Cibles de performance à mesurer sur Windows :** réponse visuelle de navigation p95 <150 ms sur fixture 12 sujets ; aucun chargement de modèle IA au démarrage ; affichage initial sans blocage de l'UI ; liste 50 sujets virtualisée si nécessaire ; cache de miniatures borné et expurgé, sans fuite de média privé ; 100 changements de vue sans mutation du SHA ni hausse mémoire non bornée. Mesurer avec GPU présent/absent, ComfyUI absent, réseau débranché. Les seuils sont des **gates proposés**, pas des benchmarks obtenus.

**Sources Cricut consultées le 29 octobre 2026 :** [Importer des images](https://help.cricut.com/hc/en-us/articles/360009556313-How-to-upload-images-into-Design-Space) (éditée 30 mars 2026 : raster et SVG ont des parcours distincts) ; [Print Then Cut](https://help.cricut.com/hc/en-us/articles/360009387274-How-to-Print-Then-Cut-in-Design-Space) (éditée 15 mai 2025 : Flatten et impression/coupe dans le flux Design Space) ; [Attach](https://help.cricut.com/hc/en-us/articles/360009380514-How-to-use-Attach-in-Design-Space) (éditée 2 octobre 2024 : placement relatif et liaison Score/Draw/Foil à Cut). **Ces pages ne valident pas notre logiciel ni l'Explore 5 physique** ; aucune dimension A4 de zone admissible n'est codée en dur dans ce lot.

## 7. Deux vertical slices de référence

**A — 12 escargots → stickers (sans modèle IA obligatoire).** Import d'une planche autorisée ; choisir Print Then Cut ; vérifier les 12 sujets, les masques (si moteur disponible) et la largeur 40 mm **déclarée par l'utilisateur** ; créer une proposition de placement A4, prévol géométrique et région admissible versionnée. Si profil A4 inconnu, état `UNKNOWN`, export **brouillon** avec avertissement ; pas de repères Cricut fabriqués par SmartSVG. Générer PNG Print Then Cut distinct du SVG Basic Cut et du SVG d'édition. Importer dans Design Space, vérifier dimensions/Flatten et suivre le flux Print Then Cut. Toute validation Design Space ou coupe est une recette ultérieure. Si seulement 10/12 masques valides, afficher 10 propositions et 2 erreurs, jamais « 12 prêts ».

**B — boîte carton → Score + Basic Cut.** Accueil « Créer » → patron paramétrique, saisir L×l×h et épaisseur/matière si nécessaire ; générer **une proposition géométrique déterministe** (cycle 16), afficher les chemins par opérations sémantiques SCORE et CUT ; prévol sur machine/outils déclarés, pas d'outil supposé possédé. Exporter SVG/guide avec étapes Design Space : importer, assigner explicitement Score, sélectionner Score+Cut, **Attacher**, vérifier l'aperçu du tapis. Aucun trait SVG n'implique automatiquement Score. Un changement de vue vers Atelier n'efface pas la relation entre plis et coupes.

## 8. Tests de recette à créer — TOUS NON EXECUTES

Corpus futur autorisé : `tests/fixtures/v34_ux/{empty,one_png,12_snails_synthetic,50_shapes_synthetic,box_score_cut,stale_selection,invalid_file,conflict,pending_backup,model_absent,oom_simulated,keyboard_focus}` ; **aucune image Pokémon ou média privé**. Tests UI sur navigateur local, puis Windows/lecteur d'écran/Design Space/physique indépendamment.

| ID | Assertion exacte attendue | Axe de preuve futur |
|---|---|---|
| T-V34-07-01 | accueil vide expose Importer/Créer/Reprendre et aucun export actif | UI, auto |
| T-V34-07-02 | choix Importer sur PNG crée une source de travail sans altérer octets de l'original | auto, Windows |
| T-V34-07-03 | fichier invalide/tronqué rejeté, SHA du projet inchangé, message FR | auto, UI |
| T-V34-07-04 | JPEG/WebP affiché n'est pas déclaré « projet créé » par le gestionnaire V1 PNG | UI |
| T-V34-07-05 | 100 changements d'espaces : SHA et révision inchangés | auto, UI |
| T-V34-07-06 | 2 vues affichent même révision et même sélection résolue ; événement perdu → resync | auto, UI, Windows |
| T-V34-07-07 | double clic Confirmer : un seul receipt et une seule révision | auto, Windows |
| T-V34-07-08 | ACK perdu : état « Enregistré » seulement après receipt confirmé | auto, UI, Windows |
| T-V34-07-09 | projet modifié ailleurs : brouillon STALE, 0 mutation, options comparer/recharger | auto, UI |
| T-V34-07-10 | sidecar pending : accueil RECOVERY_REQUIRED et aucune restauration automatique | auto, Windows |
| T-V34-07-11 | V1 ouvert : pas de migration V2 sans copie et confirmation | auto, UI |
| T-V34-07-12 | job IA absent : import et édition manuelle restent disponibles, 0 réseau | auto, Windows |
| T-V34-07-13 | job IA tardif après révision : proposition STALE, 0 écriture | auto, UI |
| T-V34-07-14 | lot 12 avec 2 échecs : 10 propositions + 2 erreurs, aucune fausse validation | auto, UI |
| T-V34-07-15 | Undo dans un champ texte n'inverse pas le projet | UI, auto |
| T-V34-07-16 | Undo groupé Score+Cut ne promet jamais annulation physique | UI |
| T-V34-07-17 | au clavier, chaque action essentielle accessible et focus visible | UI, Windows |
| T-V34-07-18 | 200 % texte / 1366×768 / 1280×720 : aucun contrôle critique caché | UI, Windows |
| T-V34-07-19 | aucun statut important codé par couleur seule ; annonces aria-live non répétitives | UI, Windows |
| T-V34-07-20 | bouton Exporter désactivé si prévol BLOCKED ; UNKNOWN ne dit jamais « prêt Cricut » | auto, UI |
| T-V34-07-21 | sticker : PNG Print Then Cut distinct du SVG Cut et d'édition, guide Design Space | auto ; DesignSpace NON_EXECUTE |
| T-V34-07-22 | boîte : Score reste sémantique ; guide Attacher visible ; aucune commande machine | auto ; DesignSpace NON_EXECUTE |
| T-V34-07-23 | 50 objets : liste utilisable, pas de plafond UI hérité des 12 exemples | UI, Windows |
| T-V34-07-24 | sortie exportée garde EXPORTED_UNVERIFIED tant que preuve externe absente | auto, UI ; physique NON_EXECUTE |
| T-V34-07-25 | navigation 100 fois p95 <150 ms mesuré avec matériel/protocole enregistré | Windows (benchmark futur) |
| T-V34-07-26 | démo 12 escargots porte « fictif », aucune segmentation/vectorisation réelle revendiquée | UI |
| T-V34-07-27 | contraste et motifs d'opérations distinguables sans perception des couleurs | UI, Windows |
| T-V34-07-28 | brouillon d'import temporaire abandonné : source originale intacte, nettoyage explicite | auto, Windows |

**Règle de preuve :** chaque test doit produire fixture, SHA, OS/version, navigateur, assertion et log ; axes `auto`, `Windows`, `DesignSpace`, `physique` sont indépendants. Aucun PASS revendiqué dans ce document.

## 9. Tickets autonomes proposés — V34-041 à V34-049 (tous SPECIFIE)

Les chemins `futur:` sont **pressentis, non créés**. DoD = assertions réellement exécutées et preuves horodatées dans une PR d'implémentation ultérieure ; rollback indiqué par ticket.

| Ticket / priorité | Dépendances S/R33/V34 | Livrables futurs, tests, preuves, DoD et rollback |
|---|---|---|
| **V34-041 P0** SessionPresenter / AppShell | S-003, S-067..069, S-074 ; R33-003,014,018 ; V34-011,015,032,037 | futur: `engine/smartsvg_app/ui/session_presenter.py`, `engine/web/js/v34_app_shell.mjs`. T-V34-07-05, T-V34-07-06, T-V34-07-09 ; auto+UI+Windows ; DoD navigation sans mutation, resync ; rollback shell désactivé, UI historique conservée. |
| **V34-042 P0** Accueil Importer/Créer/Reprendre | S-067..069, S-075 ; R33-018,033 ; V34-025,030,041 | futur: `engine/web/js/v34_home.mjs`. T-V34-07-01..04, T-V34-07-10..11 ; UI+Windows ; DoD états vide/erreur/récupération explicites ; rollback ancien accueil. |
| **V34-043 P0** Express intention/validation rapide | S-013..016, S-070, S-076 ; R33-008,022,025 ; V34-006,012,014,032,041 | futur: `engine/web/js/v34_express.mjs`, `docs/roadmap-v3.4/schemas/intent_ui.schema.json`. T-V34-07-07..08, T-V34-07-20..22, T-V34-07-26 ; UI+auto+DesignSpace ultérieur ; DoD aucun faux « prêt » ; rollback Express manuel. |
| **V34-044 P0** États save/recovery/conflict | S-023..026, S-053, S-074, S-095 ; R33-009,011..014 ; V34-029,033,034,037,041 | futur: `engine/web/js/v34_project_status.mjs`. T-V34-07-07..11, T-V34-07-24 ; auto+Windows ; DoD receipt durable et blocage pending ; rollback lecture seule. |
| **V34-045 P0** Accessibilité clavier/lecteur écran | S-068, S-072, S-077..080, S-093, S-096 ; R33-018..020,039 ; V34-041..043 | futur: `engine/web/js/v34_accessibility.mjs`, `tests/ui/test_v34_a11y.spec.mjs`. T-V34-07-15, T-V34-07-17..19, T-V34-07-27 ; UI+Windows ; DoD aucun contrôle essentiel inaccessible ; rollback UI alternative liste. |
| **V34-046 P1** Navigation contextuelle et aide | S-069..075, S-081..084, S-100 ; R33-019,020,032 ; V34-041..045 | futur: `engine/web/js/v34_navigation.mjs`. T-V34-07-05..06, T-V34-07-15, T-V34-07-17..18 ; UI+Windows ; DoD sélection/focus cohérents ; rollback routeur minimal. |
| **V34-047 P1** Tableau jobs et proposition | S-027, S-028, S-069, S-074 ; R33-005,007,011,017 ; V34-036,039,041 | futur: `engine/web/js/v34_jobs_panel.mjs`. T-V34-07-12..14, T-V34-07-23 ; UI+Windows ; DoD 0 commit sans acceptation, 50 items navigables ; rollback panneau masqué. |
| **V34-048 P1** Mode brouillon sécurisé d'import (O-011) | S-003, S-023, S-067, S-074 ; R33-003,025,033 ; V34-025,041,042 | futur: `engine/smartsvg_app/ui/import_scratchpad.py`. T-V34-07-02..03, T-V34-07-09, T-V34-07-28 ; auto+Windows ; DoD original intact et brouillon explicitement jetable ; rollback import direct historique. |
| **V34-049 P1** Légende accessible d'opérations (O-012) | S-072, S-077, S-080 ; R33-019,022 ; V34-012,041,045 | futur: `engine/web/js/v34_operation_legend.mjs`. T-V34-07-17, T-V34-07-19, T-V34-07-22, T-V34-07-27 ; UI+DesignSpace ultérieur ; DoD CUT/SCORE/DRAW/FOIL identifiables par texte+motif ; rollback légende textuelle simple. |

**Dépendances transversales bloquantes :** V34-017 graphe imports, V34-021 bootstrap autonome, V34-025..031 format V2, V34-032..040 bus/jobs/receipts. Aucun ticket de l'UX ne peut être `QUALIFIE` sur seule maquette. Les futurs fichiers d'interface doivent réutiliser les composants historiques fiables et ne pas multiplier les implémentations de validation géométrique.

## 10. Contre-expertise inverse et risques ouverts

**Revue du cycle 06 :** (1) `SAVED_CONFIRMED` doit découler d'un receipt, pas de l'événement `CommandCommitted` seul ; (2) le SHA archive peut changer après publication, donc un brouillon de vue ne peut pas présumer sa révision ; (3) un double clic est protégé par l'idempotence moteur, pas seulement par un bouton désactivé ; (4) Undo n'annule pas un export ; (5) un job interrompu n'est jamais relancé silencieusement ; (6) les erreurs `COMMITTED_NEEDS_RECOVERY` restent visibles et bloquantes même si la source primaire paraît récente.

**Revue du lot 07 :** (1) ne pas confondre les 12 escargots de démonstration et 12 masques détectés ; (2) le `width=40` de la maquette n'est pas une mesure de l'image réelle ; (3) le gestionnaire ComfyUI historique crée depuis PNG uniquement malgré la prévisualisation JPEG/WebP ; (4) l'état de capacité `AVAILABLE_UNTESTED` ne vaut pas qualification ; (5) les six espaces sont des vues, non six writers ; (6) aucune zone Print Then Cut A4 figée ; (7) focus/Undo ne doivent pas se voler les raccourcis dans les champs ; (8) pas de fuite de chemin/média dans URL, logs, previews de récents ; (9) état `UNKNOWN` n'est jamais converti en `PASS` par navigation ; (10) le choix Qt/Tauri reste ouvert à prototypes, les maquettes HTML existantes ne décident pas du packaging.

**Risques P0 ouverts :** autonomie réelle de l'import Python, writer V2 et crash Windows, CAS/receipts, vraie segmentation 12/24/50, licence IA, métriques de performance, accessibilité testée, intégration Design Space, coupe physique ; matrice inverse 141 exigences à finaliser. **Rollback général :** conserver V3.3 et les workflows historiques, désactiver le shell V3.4 si un gate échoue, préserver les projets et preuves ; aucun merge ni promotion automatique.

**Prochain lot 08 :** assistant contextuel et dialogue : définir déclencheurs, questions utiles seulement, préférences locales, cas ambigus, accessibilité et refus d'actions dangereuses ; réutiliser `SessionPresenter` et `CommandPort` au lieu d'introduire un second store.
