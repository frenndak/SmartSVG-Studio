# SmartSVG V3.4 — Lot 02 : vision, parcours de référence et contrats de réussite

**Statut : DRAFT de conception, non normatif, non implémenté.** Référence code et V3.3 : `main@fdbda304beb77d97340a8be4dd5c5e9cefde15f4` ; branche de travail issue de PR #73. Examen : 29 octobre 2026. Cette spécification ne vaut ni import Design Space testé ni découpe physique. [Audit précédent](01_BASELINE_AUDIT.md) · [Index historique](HERITAGE_INDEX.md) · [Suivi](PROGRESS.md).

## 1. Problème, positionnement, périmètre et état réel

**Problème.** Un utilisateur non graphiste veut transformer une image ou un patron en un projet réalisable sur une Cricut Explore 5 sans apprendre les graphes ComfyUI, sans confondre une jolie prévisualisation avec un chemin réellement fabriquable, et sans perdre l'original ou les corrections.

**État vérifié du produit.** Le `README.md` décrit une prévisualisation Atelier de **12 escargots fictifs**, des modules projet/masques/SVG déjà présents et des interactions réelles encore dépendantes du serveur ComfyUI. L'existence de ces composants ne prouve ni segmentation IA depuis l'Atelier ni import physique de leurs exports. Le HEAD contient `engine/smartsvg_core/subject_identity_g33e.py` (identités persistantes pour masques validés), `engine/project_routes_g22.py` (pont HTTP same-origin facultatif) et `engine/web/js/smartsvg_express_atelier_preview.html` (maquette). **Réutiliser** ces contrats après audit ; aucun nouveau runtime, écran ou export n'est déclaré implémenté.

**Proposition V3.4.** Atelier Windows local à noyau projet unique, mode manuel/CPU complet, IA locale **facultative**, ComfyUI comme adaptateur temporaire. La source de vérité est `.smartsvg`; un export n'est qu'un artefact dérivé. Les opérations sémantiques `CUT`, `SCORE`, `DRAW`, `PRINT_THEN_CUT`, `FOIL` ne sont pas synonymes de tracés SVG. Les capacités réelles d'une machine dépendent d'un profil versionné et de vérifications humaines/physiques.

### 1.1 Personae et travaux à accomplir

| Persona | Contexte | Besoin vérifiable | Ce qu'il ne faut pas imposer |
|---|---|---|---|
| P-A « Parent créatif » | PNG multi-dessins, Cricut Explore 5, papier autocollant | 12 sujets identifiables, corrections simples, feuille préparée, explication du transfert | Nœuds ComfyUI, paramètres de modèles, édition de Bézier |
| P-B « Créateur papier » | Boîte carton avec languettes et rainures | Dimensions choisies explicitement, patron cohérent, `Score` séparé de `Basic Cut`, guide `Attacher` | Découpe garantie, outil supposé présent, dimensions inventées |
| P-C « Utilisateur avancé » | Photos complexes, lots 24/50, couches, diagnostic | Inspecter chaque chemin/masque, provenance, paramètres et limites, relancer un seul échec | Perte de contrôle par assistant IA |
| P-D « Sans GPU/modèle » | Installation hors ligne, ressources limitées | Parcours manuel fonctionnel et export conditionnel à la qualité | Téléchargement implicite, blocage de l'application |

**Non-objectifs V3.4 :** contrôle direct du firmware Cricut, contournement de Design Space, génération de marques capteur prétendument équivalentes à celles de Design Space, certification automatique de matériau/pression, duplication intégrale de Canva/Inkscape, gravure/débossage Maker-only sur Explore 5, achat ou exécution de modèles distants sans consentement.

### 1.2 Mesures cibles proposées (hypothèses à tester, non résultats)

- **Compréhension novice :** lors d'une étude supervisée de 5 utilisateurs, au moins 4/5 doivent identifier correctement « aperçu », « exporté », « import confirmé », « découpé » sans aide après onboarding ; mesurer la compréhension plutôt que promettre un résultat.
- **Découverte des commandes :** au moins 4/5 doivent trouver « Corriger le contour » et « Revenir à l'original » en 30 secondes dans un prototype interactif ; chronométrage prévu, non effectué.
- **Fiabilité projet :** pour 100 séquences synthétiques ouvrir→modifier→annuler→sauvegarder→rouvrir, conservation exacte des sources et de l'état accepté ; cible de test, pas taux observé.
- **Traçabilité :** 100 % des exports de fixtures doivent inclure source hash, révision, profil machine/matière, opérations prévues et limites de preuve.
- **Prévol :** 100 % des fixtures de chemin ouvert, collision, dimensions absentes, fichier altéré ou opération incompatible doivent être bloquées ou explicitement signalées selon la règle documentée.
- **Performances :** mesurer p50/p95 import, aperçu, placement de 12/24/50 sujets et pic RAM/VRAM sur corpus autorisé, CPU seul puis RTX 3070 8 Go ; **aucun SLA chiffré ne sera contractuel avant baseline mesurée**.
- **Réseau :** zéro requête réseau de l'application en mode local sans action explicite, à vérifier par capture et tests d'intégration ; Design Space externe n'est pas inclus dans cette garantie.

## 2. Parcours de référence A — 12 escargots → stickers Print Then Cut

**Entrée :** image PNG/JPEG/WebP autorisée, contenant 12 dessins d'escargots ; cas réel non public à fournir localement, fixture synthétique publique distincte et non présentée comme vraie photo. **Sorties proposées :** `.smartsvg`, PNG transparent/aplati conforme au parcours choisi, manifest de fabrication et guide Design Space. **Aucun SVG d'édition ou de découpe n'est implicitement dérivé du PNG.**

| Phase / état | Novice — action / retour UI | Expert — contrôle additionnel | Invariant / erreur |
|---|---|---|---|
| A0 Accueil `EMPTY` | « Importer une image » | Choisir dossier projet, profil machine | Aucun modèle téléchargé, aucun fichier exporté |
| A1 `SOURCE_READY` | Aperçu et choix « Autocollants » | Inspecter EXIF, alpha, taille, source hash | Original immuable ; fichier invalide → `BLOCKED` |
| A2 `INTENT_PENDING` | Confirmer « 12 stickers séparés » et taille physique **à saisir** | Choisir contour externe, accessoires, stratégie multi-sujets | Aucun diamètre/largeur inventé ; sujet ambigu → question ciblée |
| A3 `SUBJECT_REVIEW` | 12 vignettes numérotées reliées à 12 régions sur canevas | Masques, liens accessoires, IDs stables, tri | 11 ou 13 sujets ≠ 12 : ne pas afficher « 12 prêts » |
| A4 `EDITING` | Corriger/ajouter/retirer un masque, annuler | Inspecter alpha, halos, îlots et bordure/offset | Nouvelle révision ; retour tardif IA jamais appliqué à révision différente |
| A5 `LAYOUT_REVIEW` | Choisir A4, taille des motifs, espacement ; aperçu des planches | Paramètres de placement, orientation, marges, rotation | Zone Print Then Cut **non rectangulaire** ; profil inconnu → `NEEDS_DESIGN_SPACE_CHECK` |
| A6 `PREFLIGHT` | Alertes cliquables : détail trop fin, collision, résolution, hors zone | Géométrie exacte et rapport par sujet | Une alerte bloquante interdit « prêt à fabriquer » |
| A7 `EXPORTED` | PNG + instructions « importer en image imprimable dans Design Space » | Manifest, empreintes et alternatives | Export local ≠ import Design Space ≠ coupe physique |
| A8 `HANDOFF_UNVERIFIED` | Checklist : ouvrir Design Space, choisir Print Then Cut, vérifier dimensions, imprimer dans la session Design Space, découper | Capturer version Design Space, taille feuille, configuration imprimante | Ne pas fabriquer les marques capteur dans SmartSVG ; confirmation humaine seulement |
| A9 `USER_RECORDED` | Option « J'ai vérifié l'import / la coupe » avec observations | Journal de preuve locale sans auto-certification | Déclaration utilisateur ≠ preuve de qualification indépendante |

**Règles critiques A.** (i) Le placement doit travailler dans une **région admissible versionnée**, pas dans le produit des maxima hauteur×largeur. Si le contour précis n'est pas vérifié pour machine/format/version, exporter en mode « à vérifier dans Design Space » ; ne pas annoncer 100 % de remplissage. (ii) Pour Explore 5/A4, l'impression se prépare en portrait ; Design Space fait orienter le papier **grand côté horizontal sur le tapis** pour la découpe. (iii) La session Print Then Cut doit rester dans le flux Design Space ; ne pas proposer un PDF imprimé séparément comme équivalent aux repères capteur. (iv) Si aucun modèle de segmentation n'est installé, proposer sélection/masque manuel ou traitement alpha classique ; ne pas prétendre détecter automatiquement 12 sujets.

### 2.1 Wireframe textuel A (mêmes données, vues différentes)

```text
[SmartSVG / Projet: Escargots / révision r12 / profil Explore 5]
[Importer] [Objectif: Stickers] [12 sujets: 11 confirmés, 1 à revoir]
┌─ Vignettes sujets ─┐ ┌─ Canevas image / planche ───────┐ ┌─ Action guidée ─┐
│ 01 ✓ 02 ✓ ...     │ │ [contours + zones en surbrillance]│ │ Taille [__] mm  │
│ 12 ! cliquer      │ │ zoom, comparer, corriger          │ │ [Corriger sujet]│
└───────────────────┘ └───────────────────────────────────┘ │ [Vérifier]      │
[Alerte cliquable: sujet 12 ambigu] [Annuler] [Enregistrer]  └────────────────┘
[Fabrique: aperçu A4 / région connue? NON / validation Design Space nécessaire]
```

Accessibilité : statut textuel en plus des couleurs, focus clavier sur vignettes, labels et lecture d'alerte, zoom sans perte des actions. Une demande IA est toujours une **proposition** avant modification.

## 3. Parcours de référence B — boîte carton → Score + Basic Cut Explore 5

**Entrée :** intention « boîte carton », paramètres **fournis par l'utilisateur** : largeur/longueur/hauteur utiles en mm, type de fermeture, languettes, épaisseur du matériau si nécessaire au patron, machine/outils disponibles. Aucun chiffre implicite n'est une mesure réelle. **Sorties proposées :** projet, chemins de coupe fermés, lignes de rainurage indépendantes, schéma d'assemblage et guide Design Space.

| Phase | Novice | Expert | Précondition / preuve |
|---|---|---|---|
| B0 `TEMPLATE_SELECTED` | Choisir « Boîte simple » | Choisir famille de patron, paramètres de géométrie | Patron paramétrique **à concevoir** au cycle 16, pas existant |
| B1 `PARAMETERS_PENDING` | Saisir dimensions et confirmer unité mm | Tolérances, épaisseur, grain et jeu des languettes | Une valeur requise absente ou non positive → refus |
| B2 `GEOMETRY_REVIEW` | Prévisualiser développé et sens des plis | Inspecter coordonnées, collisions, languettes | Déterminisme : mêmes paramètres/profil → mêmes chemins |
| B3 `OPERATIONS_REVIEW` | Deux couches nommées « Découpe » et « Rainurage » | Associer `CUT` / `SCORE` à des géométries et outils distincts | Ligne `SCORE` n'est **pas** une ligne de coupe |
| B4 `COMPATIBILITY_CHECK` | Confirmer que l'outil de rainage est possédé | Profil machine/outils/matière versionné | Outil absent/incompatible → avertissement ou blocage du parcours Score |
| B5 `PREFLIGHT` | Voir les points problématiques et corriger | Auto-intersections, marges, contraintes, orientation | Dimensions hors support → refus ou découpage explicitement proposé |
| B6 `EXPORTED` | Exporter calques/guide, pas une commande machine | Manifest d'opérations, unités et repères | Aucune garantie que SVG transmet `SCORE` à Design Space |
| B7 `HANDOFF_UNVERIFIED` | Importer, définir manuellement `Score`, sélectionner Score+Cut puis **Attacher**, vérifier sur aperçu tapis | Enregistrer version Design Space et placement | Le changement d'outil et l'exécution restent pilotés par Design Space |
| B8 `USER_RECORDED` | Option consigner assemblage/coupe test | Mesures du patron découpé, jeu, erreurs | Mesure physique requise pour qualifier tolérances |

**Règles critiques B.** L'outil de rainage de l'Explore 5 se substitue à l'outil de coupe lorsque Design Space le demande ; l'interface ne doit pas suggérer une exécution simultanée sans changement. La sélection « Attacher » est une action utilisateur dans Design Space. Ne pas promettre un format propriétaire capable de préconfigurer l'opération `Score`. Une « boîte paramétrique » ne devient une fonction implémentée qu'après contrat, moteur et tests dédiés.

### 3.1 Wireframe textuel B

```text
[Créer > Patron > Boîte simple] [Projet non exporté] [Annuler / Refaire]
Dimensions utiles : largeur [__] mm  longueur [__] mm  hauteur [__] mm
Matériau [carton à sélectionner]  outil de rainage [Non confirmé]
┌─ Développé / plis ──────────────────┐ ┌─ Opérations ────────────────────┐
│ lignes pleines: découpe             │ │ CUT   1 groupe   [inspecter]   │
│ lignes pointillées: rainurage       │ │ SCORE 1 groupe   [inspecter]   │
│ languettes et repères               │ │ profil: Explore 5 [vérifier]   │
└─────────────────────────────────────┘ └──────────────────────────────────┘
[Prévol: outil non confirmé] [Choisir outil] [Exporter si conforme]
[Guide Design Space: importer → Score → sélectionner → Attacher → Make]
```

## 4. Contrat UX partagé, commandes et événements — SPÉCIFICATION

**Une seule session de projet** ; Express/Atelier/Fabrique/Vectoriel/Bibliothèque/Expert sont des vues et non des autorités de données. L'assistant peut proposer, jamais appliquer sans commande autorisée. Les noms ci-dessous sont **interfaces proposées**, pas API existantes.

- `ImportSource(source_bytes, declared_type)` → `source.imported` ou `source.rejected`; vérifier signature, taille, orientation, empreinte ; ne jamais altérer l'original.
- `ProposeIntent(project_revision, intent, confidence?, evidence_refs)` → `intent.proposed` ; `ConfirmIntent` → `intent.confirmed` ; demande de dimensions si absentes.
- `SelectSubject(subject_id)`, `AcceptMask(mask_hash)`, `EditMask(delta)` → `subject.selected`, `mask.accepted`, `project.revision_created` ; chaque commande a `expected_revision` et `command_id`.
- `SetFabricationProfile(profile_id, profile_version, material_id?, tools[])` → `profile.selected` ; ne prouve pas la compatibilité.
- `BuildLayout(layout_spec)` → `layout.proposed` ; `ValidatePreflight` → `preflight.completed` avec `PASS` / `WARN` / `BLOCKED` (résultat interne **distinct** des axes de preuve V3.3).
- `ExportArtifacts(export_plan)` → `export.started` / `export.completed` / `export.failed` ; publication atomique, conservation des réussites partielles, manifeste de provenance.
- `RecordExternalStep(step_id, user_note, evidence_path?)` → `handoff.user_recorded` ; aucune transition automatique vers `QUALIFIE`.

**Idempotence/concurrence.** Répéter `command_id` ne doit pas dupliquer une révision ; un résultat IA calculé sur `revision=r12` ne s'applique pas à `r13` ; fermeture/annulation invalide le job mais préserve la dernière révision saine. Si le projet est ouvert dans deux transports, le second doit respecter la révision attendue. Erreurs proposées : `SOURCE_INVALID`, `SUBJECT_COUNT_UNCONFIRMED`, `SIZE_REQUIRED`, `PROFILE_UNKNOWN`, `OPERATION_UNSUPPORTED`, `PREVIEW_STALE`, `CUT_PATH_INVALID`, `LAYOUT_REGION_UNKNOWN`, `AI_UNAVAILABLE`, `GPU_OOM`, `EXPORT_INTERRUPTED`.

### 4.1 Exemple de contrat JSON (proposé ; non accepté par le code actuel)

```json
{
  "contract": "v34.reference_job.draft1",
  "project_id": "project-local-001",
  "expected_revision": 12,
  "command_id": "cmd-0021",
  "source": {"asset_id": "asset-001", "sha256": "<64-hex>", "immutable": true},
  "intent": {"kind": "STICKER_SHEET", "confirmed_by_user": true},
  "subjects": [{"subject_id": "subject-001", "mask_revision": 3, "confirmed": true}],
  "fabrication": {
    "machine": {"id": "cricut-explore-5", "profile_version": "UNVERIFIED"},
    "material": {"kind": "printable_sticker_paper", "sheet": "A4"},
    "geometry_units": "mm",
    "operations": [{"kind": "PRINT_THEN_CUT", "geometry_ref": "layout-001"}],
    "region_status": "NEEDS_DESIGN_SPACE_CHECK"
  },
  "export": {"kind": "PNG_PRINT_THEN_CUT", "require_preflight": true}
}
```

**Contraintes :** `project_id` et `asset_id` uniques ; `sha256` hexadécimal réel en production ; `expected_revision` entier >=0 ; `command_id` idempotent ; géométrie finie, unités explicites, dimensions strictement positives ; `geometry_ref` doit résoudre vers une ressource locale ; tout `profile_version=UNVERIFIED` interdit une mention « certifié » ; les champs illustratifs n'affirment pas l'existence d'un schéma sérialisé dans `.smartsvg`. Le cycle 05 décidera de leur mapping exact et de la migration non destructive.

### 4.2 Frontières entre modules proposées

`UI → CommandBus → ProjectCore → {Raster, Vector, Fabrication}` ; `Assistant → ProposedCommand` (jamais accès direct au fichier projet) ; `ModelRuntime → ProposedMask` ; `Preflight → Findings[]` ; `Export → ArtifactManifest` ; `ComfyUIAdapter` et `NativeAdapter` consomment **les mêmes commandes**. Les interfaces exactes seront figées par ADR au cycle 03 ; ce schéma évite de traiter un calque SVG comme l'autorité de fabrication.

## 5. Algorithmes de référence — spécification, PAS code exécuté

```python
# PSEUDO-CODE DE CONCEPTION
def plan_sticker_sheet(project, confirmed_subjects, size_mm, profile):
    require(project.source_is_immutable and size_mm > 0)
    require(all(s.confirmed and s.project_revision == project.revision
                for s in confirmed_subjects))
    shapes = [outline_from_accepted_mask(s, offset_mm=project.offset_mm)
              for s in confirmed_subjects]
    validate_topology_and_raster_resolution(shapes)
    region = profile.print_then_cut_region(project.sheet, profile.design_space_version)
    if region is UNKNOWN:
        return ProposedExport(status="NEEDS_DESIGN_SPACE_CHECK",
                              claims=["local_layout_only"], artifacts=[])
    layout = deterministic_pack(shapes, region, spacing_mm=project.spacing_mm)
    return preflight(layout, profile)  # no machine certification

def plan_box(user_dimensions_mm, box_template, material, machine_profile):
    require(all(v is not None and v > 0 for v in user_dimensions_mm))
    developed = deterministic_unfold(box_template, user_dimensions_mm)
    cut_paths, score_paths = separate_geometry_by_operation(developed)
    require(no_invalid_intersections(cut_paths, score_paths))
    return preflight(operations={"CUT": cut_paths, "SCORE": score_paths},
                     material=material, machine=machine_profile)
```

**Limite assumée :** si la région exacte Print Then Cut n'est pas connue, un **aperçu indicatif** peut rester disponible, mais pas un placement « garanti prêt » ni un export prétendument conforme à cette zone. Le cycle 15 doit décider si un profil calibré/vérifié peut être fourni légalement et maintenu ; le cycle 19 déterminera les heuristiques de nesting et leur stabilité.

## 6. IA facultative, sécurité, récupération et erreurs

| Situation | Comportement demandé | État persistant / sécurité |
|---|---|---|
| Aucune IA installée | Sélection manuelle, alpha classique ou masque à dessiner | Aucun téléchargement, aucun appel réseau |
| IA propose 11 sujets pour 12 escargots | Montrer 11 propositions + manque à corriger, sans inventer le douzième | `SUBJECT_COUNT_UNCONFIRMED`, projet intact |
| IA masque un accessoire | Mettre en évidence l'écart, proposer inclusion manuelle | Révision explicite, undo possible |
| OOM RTX 3070 | Libérer fournisseur, conserver brouillon, proposer CPU/manuelle | `GPU_OOM`, aucun artefact corrompu |
| Réponse IA tardive après correction | Proposer rejet/relance sur révision actuelle | `PREVIEW_STALE`, pas de mutation |
| SVG importé malveillant | Refuser scripts, références externes et XML dangereux | Pas d'exécution de contenu actif |
| Image sous licence incertaine | Demander confirmation de droit d'usage pour publication/vente | Aucun média utilisateur commité dans dépôt public |
| Matériau/outils non confirmés | Proposer checklist ou blocage ciblé | Pas de « prêt à couper » |
| Fermeture pendant export | Conserver original, projet sain et exports complets | Publication atomique, reprise guidée |
| Dimension boîte absente | Demander valeur précise, refuser la fabrication | Pas de dimension cachée |

**Confidentialité :** le projet et les images restent locaux ; Design Space est un service distinct soumis à ses propres conditions et traitements. Ne pas annoncer que le transfert Design Space est hors ligne. Aucune dépendance IA ne peut télécharger du code ou des poids sans consentement, licence vérifiée et contrôle d'intégrité (détaillé au cycle 11).

## 7. Plan de tests et preuves attendues

Les identifiants `T-V34-02-xx` désignent **des tests à créer**. Aucun n'a été exécuté par ce lot. Chaque exécution future doit conserver SHA code, version machine/Design Space, date, corpus autorisé et résultat `PASS/FAIL/NON_EXECUTE/NON_APPLICABLE/BLOQUE` pour chacun des axes `auto/windows/design_space/physical` **indépendamment**.

| Test à créer | Assertion mesurable | Axe de preuve |
|---|---|---|
| T-V34-02-01 | Import et réouverture conservent octets source + SHA identiques | auto + Windows |
| T-V34-02-02 | 12 IDs confirmés restent 12 après correction, undo, réouverture | auto + Windows |
| T-V34-02-03 | 11/13 sujets proposés ne deviennent jamais « 12 confirmés » | auto + UX |
| T-V34-02-04 | Taille sticker inconnue interdit prévol `PASS` | auto + UX |
| T-V34-02-05 | Zone A4 inconnue bloque « placement garanti », sans inventer rectangle | auto + Design Space |
| T-V34-02-06 | A4 : guide d'impression portrait + placement long côté horizontal, puis vérification manuelle | UX + Design Space |
| T-V34-02-07 | Boîte : entrée mm absente, nulle, négative ou NaN rejetée | auto |
| T-V34-02-08 | Chemins `CUT` et `SCORE` distincts ; pas de score transformé en cut silencieusement | auto + Design Space |
| T-V34-02-09 | Guide indique explicitement `Score`, `Attacher` et changement d'outil | UX + Design Space |
| T-V34-02-10 | `command_id` rejoué et résultat IA obsolète ne modifient pas la révision | auto + intégration |
| T-V34-02-11 | OOM, annulation et disque plein n'altèrent ni source ni dernier projet validé | auto + Windows/RTX si applicable |
| T-V34-02-12 | Aucun réseau/modèle sans consentement, mode CPU/manuelle utilisable | auto + Windows |
| T-V34-02-13 | 5 tests utilisateurs novices : >=4 comprennent les quatre états de preuve | UX supervisé |
| T-V34-02-14 | Import réel, aperçu, Score+Attacher, impression/coupe et mesures documentés **séparément** | Design Space + physique |

**Jeux de référence à préparer :** 12 escargots synthétiques non protégés (masques/IDs attendus) ; une photo smartphone locale autorisée avec sujets et accessoires ; une illustration complexe sous licence permise ; boîte synthétique avec géométrie calculable et contre-exemples (dimensions invalides, rainure hors pièce, collisions) ; PNG alpha inversé, image trop petite, fichier corrompu ; cas d'OOM simulé. Les images privées ou sous copyright ne vont jamais dans le dépôt public.

## 8. Micro-tickets du lot 02 — SPÉCIFIÉS, non implémentés

| ID / P | Dépendances V3.3 / V34 | Livrables pressentis (futurs, sauf présente spec) | Test exact, preuve, DoD et rollback |
|---|---|---|---|
| **V34-006 P0** Vision et non-promesses | S-004, S-022, S-046, S-067, R33-007, V34-001 | `02_VISION_PARCOURS.md`, futur `docs/roadmap-v3.4/DECISIONS.md` | Relecture checklist : 4 formats distincts, IA facultative, pas de pilotage machine ; preuve revue documentaire au SHA ; DoD = décision tracée, rollback = retirer ajout V3.4 sans toucher V3.3 |
| **V34-007 P0** Parcours 12 stickers | S-007, S-008, S-023, S-028, S-029, S-070, S-071, R33-004, R33-005, V34-002 | Future `docs/roadmap-v3.4/specs/STICKER_FLOW.md`, `tests/fixtures/v34_sticker_synthetic/` | T-V34-02-01..06 ; preuve auto/Windows/Design Space distincte ; DoD = transitions, tailles, erreurs et handoff testables ; rollback = conserver P01 V3.3 |
| **V34-008 P0** Parcours boîte Score+Cut | S-012, S-030, S-085, R33-008, R33-022, R33-023, V34-005 | Future `docs/roadmap-v3.4/specs/BOX_SCORE_CUT.md`, `tests/fixtures/v34_box/` | T-V34-02-07..09 et 14 ; preuve Design Space/physique requise avant qualification ; DoD = séparation des opérations et guide Attacher ; rollback = exporter seulement Basic Cut avec avertissement explicite |
| **V34-009 P0** États UX et non-promesses | S-067, S-069, S-071, S-084, R33-014, R33-034, V34-003 | Future `docs/roadmap-v3.4/specs/UX_STATES.md` | T-V34-02-03..05,13 ; preuve tests UX et statuts ; DoD = aucune confusion aperçu/export/import/coupe ; rollback = bloquer libellé « prêt » |
| **V34-010 P1** Reprise et journal d'opérateur | S-003, S-024, S-053, S-095, R33-009, R33-012, R33-025, V34-004 | Future `docs/roadmap-v3.4/specs/HANDOFF_LOG.md` | T-V34-02-10..12 ; preuve tests d'invalidation et de restauration ; DoD = journal séparé de la certification, aucune perte ; rollback = désactiver journal facultatif sans modifier projet |

**Rattachement bidirectionnel provisoire :** ces lignes donnent le sens V34→S/R33 ; `HERITAGE_INDEX.md` conserve le sens S/R33→piste V3.4, à compléter en tickets/tests lors de la construction du registre machine lisible (V34-002). Les 141 exigences historiques restent inchangées ; la couverture exhaustive **n'est pas déclarée achevée**.

## 9. Contre-expertise croisée du lot 01 et du lot 02

- **C01 / Statuts de preuve :** l'exemple du lot 01 emploie `NON_VERIFIE` pour `proof_axes.auto`, alors que la couverture V3.3 emploie `NON_EXECUTE`. Correction de conception : réserver `NON_VERIFIE` à une décision de qualification distincte, et utiliser les cinq valeurs de preuve V3.3 pour les axes. Correction du document 01 reportée à un micro-lot documentaire ciblé pour éviter une réécriture non nécessaire.
- **C02 / SHA :** le pseudo-code du lot 01 impose `proposed.source_sha == proof.base_sha`, ce qui confond source documentaire et commit du code testé. Correction de conception : `requirement_source_sha`, `tested_code_sha`, `artifact_sha`, `test_run_id` sont distincts ; les preuves sont liées à une version précise sans égalité artificielle.
- **C03 / Handoff :** l'importation dans Design Space et la fabrication sont des preuves externes ; le journal utilisateur est informatif, jamais une certification. Les chemins `SCORE` ne transportent pas l'opération à eux seuls.
- **C04 / Placement :** la zone Print Then Cut n'est pas un rectangle complet ; un profil non vérifié interdit un calcul présenté comme garanti.
- **C05 / Machine :** Explore 5 n'est pas Maker ; les outils spécifiques Maker ne sont pas proposés. La compatibilité matière/outil reste à vérifier sur profil versionné.
- **C06 / Architecture :** introduire un **contrat minimal d'opérations** dès le cycle 03, avant le détail du cycle 14, sans modifier le programme des 24 cycles.
- **C07 / Surconception :** ne pas créer six stores UI ni plusieurs autorités `.smartsvg`; garder les fonctionnalités avancées derrière un panneau facultatif.
- **C08 / Tests :** aucune exécution réelle Windows/GPU/Design Space/physique ; les tables ci-dessus sont des **plans de recette**.

## 10. Références externes vérifiées et incertitudes (29 octobre 2026)

1. Cricut, *How to Print Then Cut with Cricut Explore 5*, https://help.cricut.com/hc/en-us/articles/38613592650903-How-to-Print-Then-Cut-with-Cricut-Explore-5 — orientation A4 sur tapis, impression portrait, repères capteur et session Design Space.
2. Cricut, *How large can I Print Then Cut?*, article modifié le **19 août 2026**, https://help.cricut.com/hc/en-us/articles/360009429814-How-large-can-I-Print-Then-Cut — région non rectangulaire, dépend de la machine, du support et des proportions ; ne pas déduire un rectangle des maxima.
3. Cricut, *Cricut Explore 5: How to use the Scoring Tool*, https://help.cricut.com/hc/en-us/articles/38613473602455-Cricut-Explore-5-How-to-use-the-Scoring-Tool — choisir `Score`, `Attach` et changer d'outil à la demande.
4. Cricut, *Calibrating your machine for Print Then Cut*, article modifié le **3 septembre 2026**, https://help.cricut.com/hc/en-us/articles/360009424974-Calibrating-your-machine-for-Print-Then-Cut — calibration réelle requise pour vérifier la précision.

**Limites de recherche :** aucune version locale de Design Space ni géométrie complète de zone admissible n'a été mesurée ; aucun résultat de licence IA, benchmark RTX 3070 ou matériel physique n'est inféré de ces sources.

## 11. Passage au cycle 03

Préparer ADR de responsabilités et interfaces, graphe de dépendances existant, comparaison PySide6/Qt vs Tauri+Python basée sur un prototype mesuré, schéma minimal `Path→Operation→Tool→Material→Machine`, et contrats d'adaptateurs ComfyUI/natif. Reprendre C01/C02 comme corrections documentaires **focalisées** si la politique de micro-lot le permet. Ne pas prétendre que les tests ci-dessus sont exécutés.
