# SmartSVG Studio V3.4 — Lot 13 : vectorisation, topologie, SVG d'édition et SVG de coupe

**DRAFT DE SPÉCIFICATION — 29 octobre 2026.** V3.3 demeure ACTIVE ; suivi [#72](https://github.com/frenndak/SmartSVG-Studio/issues/72), PR [#73](https://github.com/frenndak/SmartSVG-Studio/pull/73) DRAFT. Référence code `main@fdbda304beb77d97340a8be4dd5c5e9cefde15f4` ; branche de travail documentaire issue du cycle 12. **Aucun moteur V3.4, aucun fichier de test ci-dessous, aucun SVG réel qualifié Design Space ou Cricut n'a été implémenté ou exécuté par ce lot.** Les exemples sont des **SPÉCIFICATIONS**, pas des preuves.

## 1. Résultat utilisateur, état réel et périmètre

**Besoin :** convertir une image/masque en géométrie vectorielle utile, éditable et/ou découpable sans confondre l'aspect du dessin avec le chemin de la lame. Un novice veut choisir **« contour extérieur seul »** ou **« tous les traits/couleurs utiles »** ; un expert veut inspecter les îlots, trous, intersections, Béziers, calques, dimensions, fidélité et opérations, puis revenir en arrière sans toucher à l'original. Une photo smartphone n'est pas automatiquement un dessin vectoriel fidèle. Un personnage détaillé type Pokémon est un **cas de complexité**, jamais un fichier public de fixture sans droits.

**Constats de code relu sur main :**
- `engine/web/js/smartsvg_cut_review_model_g27.mjs` inspecte localement un SVG **déjà existant** : 768 Kio, au plus 64 `path`, `viewBox` et tailles en mm, grammaire sûre ; `smartsvg_cut_review_panel_g27.mjs` permet de sélectionner des chemins et de télécharger un **brouillon**, pas de vectoriser une photo.
- `engine/web/js/smartsvg_svg_path_grammar_g29.mjs` vérifie les commandes M/L/H/V/C/S/Q/T/A/Z et fermetures, avec budget 50 000 tokens et limite de longueur par `d`. Il ne prouve pas absence d'auto-intersections ni fidélité de Bézier.
- `engine/smartsvg_governance/cut_path_preflight.py` limite à 5 000 éléments `path`, contrôle les polygones simples et marque les courbes pour revue visuelle ; pas de simulation Cricut.
- `engine/smartsvg_core/project_archive.py` valide un sous-ensemble de SVG de **stockage interne** plus riche (`clipPath`, gradients, etc.). **Un SVG sûr dans l'archive n'est donc PAS nécessairement importable par Design Space.** Le writer `smartsvg-project/1` et ses limites restent inchangés.
- `engine/production_v211.py` régénère certains SVG de contour à partir de l'alpha final et conserve la correspondance dimensionnelle PNG/SVG, mais ce contour ne représente pas une illustration multicolore entièrement éditable.
- `docs/G3_1_EXPRESS_REAL_SVG_REVIEW.md` décrit un raccordement d'inspection, **pas** une génération automatique de SVG éditable.
- **Cricut officiel, consulté le 29/10/2026 :** les SVG importés dans Design Space sont limités à **5 000 paths** ; les calques sont regroupés à l'import, puis séparables ; **tous les vecteurs importés sont initialement des lignes de coupe**, y compris les marques destinées au dessin. Les gradients, remplissages à motifs, clipping paths, textes non convertis en contours et images non vectorielles incorporées ne constituent pas un contrat d'import SVG fiable. L'upload d'images nécessite une connexion Internet, même si certaines images déjà téléchargées peuvent être utilisées hors ligne. Sources officielles §11.

**Périmètre du lot :** modèle vectoriel canonique, traçage depuis masques acceptés, géométrie des trous et courbes, calques éditables, profil d'export SVG sûr, prévol, édition réversible et passage de relais vers le lot 14. **Hors périmètre :** moteur de Score/Draw/Foil (14), profil matériel certifié (15), patrons (16), export multi-format définitif (17), canevas avancé (18), optimisation planches (19), reconnaissance IA (10–11), impression Print Then Cut (12). Les quatre sorties historiques demeurent distinctes.

## 2. Contre-expertise du lot 12 et décision ADR-034-16 (PROPOSÉE)

**Correction C13-01 :** les seuils alpha **0/20/128** du lot 12 sont des diagnostics de texture/topologie ; ils ne définissent **pas** une géométrie de coupe universelle. Choisir explicitement `source_mask_revision` et `contour_policy` avant traçage ; enregistrer le seuil effectif, l'orientation EXIF et la transformation pixel→mm. Le digest du contour accepté est indépendant de la texture raster ; un upscale ou un changement ICC ne doit jamais le recalculer silencieusement.

**Correction C13-02 :** `fill-rule=evenodd` peut exprimer un trou pour un moteur SVG, mais **ne prouve pas** que Design Space produira la bonne découpe. Le profil de fabrication doit expliciter la hiérarchie outer/hole, les sens de parcours, et produire des chemins sans `clipPath` ni transformations non résolues ; import Design Space puis coupe réelle restent des axes de preuve distincts.

**Correction C13-03 :** les limites **64 chemins G2.7** (inspection existante), **5 000 chemins Cricut documentés** et budgets V3.4 à mesurer ne sont pas interchangeables. Une scène de 50 sujets peut être répartie en fichiers/pages ; aucune capacité de 5 000 chemins ne doit être annoncée comme performance acceptable.

**Options :**
- A. SVG unique pour édition, coupe et impression — **REJETÉ** : ambiguïté des opérations, pertes de couleur et imports non fiables.
- B. Convertir chaque pixel/couleur en chemin de coupe — **REJETÉ par défaut** : milliers de chemins, doubles coupes, îlots et coût de désherbage.
- C. Géométrie vectorielle canonique dans le projet + **deux projections séparées** (`EDITABLE_SVG`, `CUT_SVG`), et PNG Print Then Cut inchangé — **RECOMMANDÉ, À PROTOTYPER**.
- D. Toute la géométrie dans des SVG libres comme seule autorité — **REJETÉ** : styles/clips/transforms externes rendent CAS, identités et prévol difficiles.

**ADR-034-16 proposée :** la vérité géométrique est un graphe canonique de chemins en coordonnées de projet, lié à des identités de sujet, masques et révisions ; les SVG sont des **artefacts dérivés**. Les propriétés graphiques d'édition ne deviennent pas automatiquement des opérations machine. Les exporteurs appliquent des profils et validations séparés. Ne pas décider la bibliothèque de géométrie avant un spike mesuré de courbes, booleans, offsets et arrondis.

## 3. Parcours novice/expert et wireframes textuels

**Parcours A — 12 escargots → stickers :**
1. Importer la planche, identifier/revoir les 12 masques (lot 10), conserver l'original et la texture (lot 12).
2. Choisir `Stickers Print Then Cut` : **PNG RGBA** et découpe dérivée de l'alpha, **pas de superposition automatique du SVG diagnostic**. Le bouton `Voir les contours` montre la géométrie en surimpression **dans SmartSVG seulement**.
3. Option `Exporter silhouette SVG Basic Cut` distincte, avec **avertissement** : le SVG ne contient pas les couleurs du dessin.
4. Revoir chaque sujet, trous et collisions, taille mm, puis exporter et contrôler dans Design Space.

**Parcours B — illustration complexe :**
1. Choisir `Contour extérieur seul` (silhouette) ou `Vectoriser couleurs et formes` (couches d'édition) ; la seconde opération n'est pas réputée fidèle sans comparaison.
2. Afficher original / rendu vectoriel / chemin de lame **en trois vues distinctes** ; zoom et loupe, légende des calques.
3. Ajuster palette et tolérance de simplification, verrouiller les détails voulus, corriger les courbes ; prévisualiser l'effet avant `Accepter`.
4. Exporter `SVG d'édition` ; **seulement sur commande distincte**, proposer `SVG Cut multicouche` après choix de matière/couleurs et prévol, sans déduire qu'un calque de couleur est une opération de coupe.

**Parcours C — boîte Score + Cut :** importer une géométrie paramétrique avec traits de pli ; l'éditeur les représente comme `GUIDE` ou `OPERATION_PENDING`, jamais comme simple `CUT` par défaut. Le lot 14 leur attribuera `SCORE` avec outil/matière validés. L'export SVG seul ne transmet pas cette sémantique à Design Space : vérifier et modifier l'opération, **Attacher**, suivre les changements d'outil.

**Wireframe novice (états accessibles au clavier) :**
```text
[← Accueil]  Projet : Escargots  [Enregistré / Brouillon / Conflit]  [Annuler] [Refaire]
[Source originale] [Vectoriel] [Découpe simulée] [Comparer]
┌ Canvas avec zoom 100 %, sélection et dimensions mm ────────────────┐
│ sujet 01  contour extérieur   ◌ trou intérieur   ⚠ détail fragile  │
└────────────────────────────────────────────────────────────────────┘
[Objectif : Sticker PNG ▾] [Contour seul | Formes et couleurs]
[Qualité : rapide | équilibrée | détaillée] [Inspecter les alertes]
[12 sujets / 12 revus] [Accepter la proposition] [Exporter...]
Statut : SVG d'édition ≠ SVG de coupe ; import Design Space non vérifié
```

**Wireframe expert :** panneau gauche sujets/calques/relations ; centre original, rendu, courbes et lame ; panneau droit source de contour, tolérance en mm, `fill-rule`, hiérarchie des trous, nombre de segments/paths, métriques fidélité/coupe, ressources et empreintes ; bas journal de jobs et erreurs localisées. Contrôles `Tab`, flèches, entrée, échappement, Undo ; aucun focus perdu après revectorisation. Aucun calque caché ne doit être exporté par surprise.

**États UX :** `EMPTY`, `ANALYSING`, `PROPOSAL`, `REVIEW_REQUIRED`, `ACCEPTED`, `STALE`, `EXPORT_BLOCKED`, `EXPORTED_UNVERIFIED`. Les erreurs indiquent objet, région, cause et correction réversible ; le résultat partiel ne remplace jamais la version acceptée.

## 4. Modèle de données, contrats et interfaces — SPÉCIFICATION

**Unités :** espace source pixels après orientation EXIF ; espace canonique projet en **mm**, transformée affine versionnée et inversible si applicable ; `viewBox` et `width/height` cohérents ; pas de déduction d'une taille physique depuis le seul DPI absent. Coordonnées finies, précision bornée, aucune NaN/Inf ; les limites numériques exactes sont à mesurer et centraliser.

**Types logiques proposés :**
- `VectorDocument`: `schema`, `project_revision`, `source_sha256`, `canvas_mm`, `units`, `objects[]`, `geometry_digest`, `proof_axes`.
- `VectorObject`: `object_id`, `subject_id?`, `parent_id?`, `source_mask_revision?`, `shape_kind`, `layer_id`, `visible`, `locked`, `contours[]`, `style`, `intent`, `provenance`.
- `Contour`: `contour_id`, `role=OUTER|HOLE|OPEN_GUIDE`, `segments`, `closed`, `winding`, `parent_contour_id?`, `tolerance_mm`. `OPEN_GUIDE` **interdit** dans un Basic Cut sans opération explicitement autorisée.
- `VectorProposal`: `job_id`, `source_digest`, `expected_project_sha256`, `algorithm_id`, `parameters`, `diff`, `warnings`, `candidate_digest`. Proposition **non mutante** jusqu'à acceptation CAS via le bus V34-032..040.
- `ExportProfile`: `EDITABLE_SVG|BASIC_CUT_SVG|MULTILAYER_CUT_SVG`, `machine_profile_ref?`, `forbidden_features[]`, `path_budget`, `target_units=mm`, `proof_state`. Le profil d'import Cricut n'est pas l'autorité de compatibilité machine.
- `VectorQualityReport`: métriques `raster_fidelity`, `geometry_topology`, `manufacturing_preflight` **indépendantes** ; `UNKNOWN` si corpus/référence absents.

**Exemple JSON de contrat (non exécuté) :**
```json
{
  "schema": "smartsvg-vector-proposal/1-draft",
  "job_id": "job-v13-001",
  "expected_project_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "source_sha256": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
  "source_mask_revision": "mask-r7",
  "subject_id": "subject-02",
  "mode": "OUTER_SILHOUETTE",
  "canvas_mm": {"width": 40.0, "height": 32.0},
  "pixel_to_mm": [0.1, 0, 0, 0.1, 0, 0],
  "contour_policy": {"alpha_threshold": 128, "holes": "PRESERVE", "simplification_tolerance_mm": 0.15},
  "objects": [
    {
      "object_id": "vec-02",
      "layer_id": "cut-silhouette",
      "intent": "CUT_CANDIDATE",
      "contours": [
        {"contour_id": "outer-02", "role": "OUTER", "closed": true, "parent_contour_id": null,
         "segments": [{"type": "M", "xy": [2, 2]}, {"type": "L", "xy": [38, 2]},
                      {"type": "L", "xy": [38, 30]}, {"type": "L", "xy": [2, 30]}, {"type": "Z"}]}
      ]
    }
  ],
  "warnings": ["MATERIAL_PROFILE_NOT_QUALIFIED"],
  "review_state": "PROPOSED",
  "proof_axes": {"auto": "NON_EXECUTE", "windows": "NON_EXECUTE",
                 "design_space": "NON_EXECUTE", "physical": "NON_EXECUTE"}
}
```

**Commandes conceptuelles** via **l'unique bus du lot 06**, sans créer de second protocole : `TraceContours`, `VectorizeColorRegions`, `SetContourRole`, `EditVectorControlPoint`, `SimplifyPath`, `SplitMergeLayer`, `AcceptVectorProposal`, `PrepareVectorExport`. Les événements `vector.proposed`, `vector.review_required`, `vector.accepted`, `vector.stale`, `vector.export_preflighted` portent les IDs, digest et révision. **L'enveloppe canonique de commande reste celle de 06_COMMAND_BUS.md (`smartsvg-command/1-draft`)** ; les versions d'exemple des lots 03/04 sont historiques et devront être réconciliées au lot 23, sans les recopier comme API.

**Ports futurs (non existants) :** `VectorTracePort.trace(mask_ref,policy)->VectorProposal` ; `VectorEditPort.apply(command,snapshot)->candidate` ; `VectorTopologyPort.inspect(candidate)->report` ; `VectorExportPort.render(candidate,profile)->staged_artifact` ; `ProjectCommandPort.commit(accepted_proposal,CAS)->receipt`. Le moteur IA ne peut pas écrire dans le projet ni sauter le prévol. La géométrie canonique V2 est **conditionnelle au writer V2 qualifié** ; ne pas sérialiser les nouveaux champs dans une archive V1 non compatible.

## 5. Déroulé déterministe, qualité et limites

**Pipeline proposé (pseudocode, NON EXÉCUTÉ) :**
```python
def propose_vectorization(snapshot, mask_revision, policy):
    verify_source_digest(snapshot, mask_revision)
    pixels = resolve_mask_view(snapshot, mask_revision)  # float32 accepté
    binary = threshold_explicitly(pixels, policy.alpha_threshold)
    rings = extract_rings_with_hierarchy(binary)         # outer / hole / nested island
    geometry = transform_to_mm(rings, snapshot.pixel_to_mm)
    geometry = normalize_winding_and_degeneracies(geometry)
    candidate = fit_curves_with_error_budget(geometry, policy.tolerance_mm)
    report = compare_topology_and_raster(candidate, binary, policy)
    if report.blocking:
        return review_only(candidate, report)
    return immutable_proposal(candidate, report)        # aucun commit
```

**Détails impératifs :**
1. **Extraction :** trouver composants connexes, anneaux et imbrications ; l'aire signée seule ne suffit pas pour tous les trous. Conserver le graphe de parenté et les petits îlots en `REVIEW_REQUIRED`, pas les supprimer silencieusement.
2. **Topologie :** détecter contours ouverts, auto-intersections, tangences, chemins dupliqués, chevauchements de lame, intersections inter-calques, trous disparus, épaisseur de ponts ; définir tolérance en mm et **vérifier les conséquences après simplification**.
3. **Courbes :** comparer polygonal vs Bézier quadratique/cubique ; erreur Hausdorff bidirectionnelle approximée avec borne d'échantillonnage, différence de surface et métrique de contour à mesurer. Le `fit` doit préserver la topologie avant toute optimisation de nombre de points.
4. **Édition multicouche :** régions colorées segmentées en couches de dessin ; palette éditable, groupements et identités stables ; `fill-rule` explicite ; éviter le `clipPath` dans l'export Cricut. Les couleurs ne deviennent jamais automatiquement des opérations `CUT` distinctes.
5. **Conversion des traits :** un trait graphique (`stroke`) n'est pas nécessairement une trajectoire de lame ; pour fabriquer, convertir en géométrie fermée **sur commande**, avec aperçu des deux bords, ou conserver en guide/opération en attente. Pour stylo/Score, attendre le contrat sémantique du lot 14.
6. **Sécurité XML :** refuser DTD, entités, scripts, `foreignObject`, événements, URLs externes, images embarquées non conformes au profil, cycles `use`, transforms non résolues, dimensions invalides et bombes de complexité. L'édition interne peut conserver des fonctionnalités SVG sûres que l'export Cricut doit **aplatir ou refuser explicitement**.
7. **Import/export :** produire `<svg xmlns=... width="...mm" height="...mm" viewBox="...">` ; garantir le même repère et la même taille. Compter les `path` **après** résolution des groupes et conversions ; refuser le profil Design Space si >5 000 paths selon la documentation actuelle, mais établir une marge de performance inférieure après essais.
8. **Résultats partiels :** accepter 11 sujets et isoler le 12e en échec ; les succès ne changent le projet qu'après acceptation explicite et commande idempotente. Un job ancien devient `STALE`, jamais fusionné silencieusement.
9. **IA :** un modèle local déjà qualifié peut **proposer** des séparations de couleurs ou contours, mais géométrie, validation, prévol et sauvegarde restent déterministes. Aucun téléchargement ni modèle requis ; OOM → CPU/manuel, 0 mutation.
10. **Matériel :** pas de seuil de micro-détail, vitesse, pression, rayon minimal, force de lame ni précision de coupe « universels ». Toutes ces valeurs dépendent du matériau, de la lame, du tapis, de la machine et de tests physiques.

**Métriques à instrumenter :** durée p50/p95 par image et nombre de segments, mémoire pic CPU, complexité de chemins, taux d'échec SVG, dérive de surface/contour, conservation des composantes/trous, nombre de points avant/après, temps d'ouverture du panneau, fidélité couleur perceptuelle avec profil déclaré. Les seuils chiffrés de PASS seront proposés à partir d'un corpus et d'un prototype, **pas inventés**. Cible de sécurité : 0 mutation sur prévol bloqué, 0 lecture réseau, 0 fichier source modifié ; assertions exactes testables.

## 6. Prévol, erreurs, persistance et rollback

**États de prévol séparés :**
- `EDITABILITY` : objets sélectionnables, calques stables, palette et courbes modifiables, sans raster dissimulé sous l'étiquette « entièrement vectoriel ».
- `SVG_STATIC` : XML sûr, viewBox/mm, IDs uniques, fermeture, intersections et complexité vérifiés dans les limites de l'analyse.
- `DESIGN_SPACE_IMPORT` : uniquement `NON_EXECUTE|PASS|FAIL|BLOQUE` après import réel sur version connue, **pas déduit** du parsing SVG.
- `PHYSICAL_CUT` : indépendant, exige matériau/outil/tapis, dimensions et mesures.

**Erreurs proposées :** `VECTOR_SOURCE_STALE`, `MASK_REVISION_MISSING`, `VECTOR_TOPOLOGY_CHANGED`, `VECTOR_OPEN_CUT`, `VECTOR_SELF_INTERSECTION`, `VECTOR_DUPLICATE_CUT`, `VECTOR_HOLE_LOST`, `VECTOR_UNSUPPORTED_SVG_FEATURE`, `VECTOR_PATH_BUDGET`, `VECTOR_SIZE_UNKNOWN`, `VECTOR_GPU_OOM`, `VECTOR_EXPORT_BLOCKED`, `VECTOR_PROJECT_CONFLICT`. Chacune porte `object_id`, région, étape, suggestion sûre, sévérité, sans média privé ni chemin personnel dans les logs publics.

**Persistance/Undo :** source et masque acceptés immuables ; paramètres, corrections de points, couche et rôle enregistrés comme commandes réversibles avec CAS/epoch/receipt (lot 06) ; les artefacts dérivés sont invalidés lorsque leur digest source change ; export et coupe physique **ne sont pas annulables** par Undo. Sur disque plein, crash ou verrou, conserver archive précédente, sidecars et proposition récupérable ; ne jamais écraser un SVG exporté sans accord explicite. L'export passe par staging et publication atomique sous réserve des spikes Windows du lot 05/06.

## 7. Corpus de référence et recette future

**Fixtures à créer, uniquement synthétiques ou sous licence compatible :**
- `V13-A` anneau troué + îlot imbriqué ; variations `evenodd/nonzero`.
- `V13-B` deux formes tangentes, croisées et chemin en double.
- `V13-C` courbe lisse vs contour pixelisé et cuspide aiguë.
- `V13-D` dessin multicouleur synthétique 4 couches, gradients et clipping interne.
- `V13-E` 12 silhouettes de type escargot **dessinées spécialement pour le test**, 24/50 formes synthétiques.
- `V13-F` XML hostile DTD/XXE, scripts, URLs externes, `foreignObject`, nombres extrêmes, 5 001 chemins.
- `V13-G` boîte 2D avec guide de pli `OPEN_GUIDE`, Cut fermé, aucun transfert Score implicite.
- `V13-H` cas photo/line-art synthétique avec contours de texture inutiles ; aucune image Pokémon publique.

**Tests d'acceptation à créer — tous `NON_EXECUTE` :**

| Test | Assertion déterminante | Axe requis |
|---|---|---|
| T-V34-13-01 | Masque/source SHA identiques → proposition déterministe avec mêmes paramètres | auto |
| T-V34-13-02 | Seuil alpha 0/20/128 change rapport, jamais contour accepté sans confirmation | auto |
| T-V34-13-03 | Source EXIF orientée + transform mm → bounding box physique cohérente | auto |
| T-V34-13-04 | Anneau + trou + îlot V13-A : hiérarchie exacte conservée | auto |
| T-V34-13-05 | `evenodd`/`nonzero` rendus distincts et trous correctement signalés | auto |
| T-V34-13-06 | Courbe Bézier fermée : aucun PASS topologique sans vérification de courbe | auto |
| T-V34-13-07 | Auto-intersection V13-B → alerte localisée et export bloqué si CUT | auto |
| T-V34-13-08 | Chemin de lame doublé → `VECTOR_DUPLICATE_CUT`, aucun silence | auto |
| T-V34-13-09 | Simplification qui supprime un trou → refus, ancien digest conservé | auto |
| T-V34-13-10 | Simplification valide : métriques de contour/surface avant-après consignées | auto |
| T-V34-13-11 | Contour extérieur seul ≠ calques couleur, UX avertit | UI/auto |
| T-V34-13-12 | Quatre calques : IDs, palette, ordre et visibilité réversibles | auto/UI |
| T-V34-13-13 | Export d'édition garde les objets éditables, aucun raster déguisé | auto |
| T-V34-13-14 | Export Basic Cut ne contient ni clipping, gradients, scripts ni images | auto |
| T-V34-13-15 | SVG mm + viewBox : dimensions contrôlées et coordonnées finies | auto |
| T-V34-13-16 | 5 001 paths V13-F → `VECTOR_PATH_BUDGET` avant handoff | auto |
| T-V34-13-17 | 64 chemins G2.7 ≠ capacité du nouveau moteur, pas de promesse de 5 000 | auto/UI |
| T-V34-13-18 | Import SVG avec texte éditable/clip/gradient → export Cricut refuse ou convertit avec diff | auto |
| T-V34-13-19 | XML hostile DTD/XXE/script/externe → rejet sans exécution ni réseau | sécurité auto |
| T-V34-13-20 | PNG Print Then Cut inchangé lorsque seul SVG diagnostic demandé | auto |
| T-V34-13-21 | 12/24/50 objets : IDs uniques, aucun objet perdu ni tronqué silencieusement | auto |
| T-V34-13-22 | Révision source modifiée durant job → `STALE`, aucun commit | intégration auto |
| T-V34-13-23 | Retry même commande après ACK perdu → un seul commit, receipt rejoué | intégration auto |
| T-V34-13-24 | OOM GPU simulé → fallback manuel/CPU, projet et source inchangés | auto ; GPU terrain séparé |
| T-V34-13-25 | Clavier : choix contour/couches, revue alerte, Undo/Redo sans perte focus | UI/Windows |
| T-V34-13-26 | V13-G : guide de pli non converti en CUT ou SCORE par couleur | auto |
| T-V34-13-27 | Import SVG Basic Cut réel, dimensions et calques constatés, version Design Space enregistrée | DesignSpace |
| T-V34-13-28 | Coupe Explore 5 d'un contour troué, mesures et matière consignées | physique |
| T-V34-13-29 | Crash/lecture seule/disque plein : projet précédent et source intacts | auto/Windows |
| T-V34-13-30 | Traçabilité test→ticket→S/R33, axe preuve et SHA présents, aucun faux PASS | documentaire/auto futur |

**Gates :** les tests 01–26, 29–30 n'ont **pas** été implémentés ici ; 27–28 exigent Design Space/Explore 5 réels. Aucun rendu dans un navigateur ne vaut import Cricut. Aucun score de fidélité ne remplace une mesure de coupe.

## 8. Micro-tickets futurs V34-096..105 — tous SPECIFIE

**Definition of Done commune :** contrat versionné, code+tests créés dans une PR ultérieure, test exact exécuté avec SHA et environnement, preuve par axe, aucun ancien ID/workflow rompu, rollback vérifié, documentation de non-promesse, sécurité et licence, validation du format de sortie sans mutation V1 silencieuse. Les chemins ci-dessous **n'existent pas encore** ; le bootstrap autonome du lot 04 peut imposer `src/` plutôt que `engine/`.

| Ticket / priorité | Dépendances héritées et V34 | Livrables FUTURS, tests, preuve et rollback |
|---|---|---|
| **V34-096 P0** géométrie canonique et repères | S-023/032/052, R33-004/008, V34-025..031/068/087 | `engine/smartsvg_app/vector/model.py`, `tests/vector/test_model.py` ; T01..03/15/22 ; auto ; DoD identités, mm, digests cohérents ; rollback lecture seule V1 |
| **V34-097 P0** anneaux, trous, intersections | S-030/056/085, R33-008/022, V34-070/088/096 | `.../vector/topology.py`, `tests/vector/test_topology.py` ; T04..08/09 ; auto ; DoD hiérarchie préservée, alertes localisées ; rollback contour source |
| **V34-098 P0** courbes et simplification sûre | S-011/033/034/060, R33-008/022, V34-096/097 | `.../vector/curve_fit.py`, `tests/vector/test_curve_fit.py` ; T06/09/10 ; auto ; DoD aucun trou perdu, métriques bornées ; rollback polyline non simplifiée |
| **V34-099 P1** couches éditables et palette | S-011/032/033/045, R33-008/019, V34-096/098 | `.../vector/layers.py`, `tests/vector/test_layers.py` ; T11..13/18 ; auto/UI ; DoD objets réellement modifiables ; rollback silhouette seule |
| **V34-100 P0** import SVG sécurisé et sérialiseur | S-030/032/042/061, R33-008/016/022, V34-096/097 | `.../vector/svg_codec.py`, `tests/vector/test_svg_codec.py` ; T14..19 ; auto/sécurité ; DoD aucun contenu actif et tailles mm explicites ; rollback refus de l'export |
| **V34-101 P0** profils SVG Basic/MultiCut | S-009/012/030/032/054, R33-008/022, V34-100/012/014 | `.../vector/export_profiles.py`, `tests/vector/test_cut_profile.py` ; T14..18/20/26/27 ; auto + DesignSpace ultérieur ; DoD 4 sorties distinctes ; rollback SVG d'édition seulement |
| **V34-102 P1** retouche non destructive de courbes | S-008/026/071/079, R33-004/005/019, V34-032..040/096/099 | `.../vector/edit_commands.py`, `tests/vector/test_vector_undo.py` ; T09/12/22/23/25 ; auto/Windows ; DoD CAS/Undo et pas de commit implicite ; rollback proposition rejetée |
| **V34-103 P1** fidélité et QA différenciées | S-011/033/034/060, R33-019/022, V34-088/090/097/098 | `.../vector/quality.py`, `tests/vector/test_quality.py` ; T04..10/21/30 ; auto ; DoD silhouette/couleur/fabrication distinctes ; rollback REVIEW_REQUIRED |
| **V34-104 P0** robustesse, quotas, jobs | S-018/042/061/095, R33-005/011/012/013, V34-036..040/074/100 | `.../vector/jobs.py`, `tests/vector/test_adversarial.py` ; T16/19/21..24/29 ; auto/Windows ; DoD stale/OOM/hostile non mutants ; rollback CPU/manuel |
| **V34-105 P1** UI Vectoriel et transfert guidé | S-067/069/071/075/076/077, R33-018/019/022, V34-041..049/099/101/102 | `engine/web/js/v34_vector_panel.mjs`, `tests/ui/test_v34_vector.spec.mjs` ; T11/12/17/25..28 ; UI+DesignSpace+physique distincts ; DoD débutant/expert et avertissements, rollback panneau G2.7 |

**Mapping inverse explicite :** T01..03→096 ; T04..09→097 ; T06/09/10→098 ; T11..13/18→099 ; T14..19→100 ; T14..18/20/26/27→101 ; T09/12/22/23/25→102 ; T04..10/21/30→103 ; T16/19/21..24/29→104 ; T11/12/17/25..28→105. Chaque ticket cite S/R33 ; le mapping **global des 141** reste à produire aux lots 23/24. Aucune exigence historique supprimée.

## 9. Opportunités du cycle, arbitrages et non-objectifs

- **O-028 — conseiller de budget de chemins** : P1, retenu pour spécification, voir `OPPORTUNITIES.md`. Basé sur la limite officielle 5 000 paths, sans transformer ce maximum en objectif de performance ; ticket V34-101/103, T16/17.
- **O-029 — verrouillage explicite des trous utiles** : P1, retenu ; raffinement de S-033/034 et V34-097/102 ; empêche la simplification de supprimer une ouverture voulue, T04/09/25.
- **O-030 — chaque couleur devient automatiquement une coupe** : REJET ; confond édition et fabrication, crée des doubles chemins et ne peut déduire matériau/outil ; test négatif T11/13/26.

**Non-objectifs :** un clone complet d'Illustrator/Inkscape ; vectorisation parfaite de toute photographie ; dessin animé automatiquement « totalement éditable » ; reconnaissance sémantique garantie des détails ; pilotage Cricut ; conversion automatique de guides en Score ; certification de l'Explore 5 ; export de SVG riche avec `clipPath` prétendument compatible Cricut ; contournement des restrictions Design Space.

## 10. Auto-relecture et risques ouverts

**Revue conceptuelle du lot 12 :** alpha de texture ≠ masque accepté ≠ contour géométrique ; le seuil 0/20/128 reste diagnostic. **Revue du lot 13 :** géométrie canonique ≠ SVG d'édition ≠ SVG de coupe ; une couleur ne devient pas une opération ; un SVG XML sûr n'est pas un SVG importable ; un `path` fermé n'est pas forcément une coupe sûre ; `evenodd` ne prouve pas un trou physique ; 5 000 paths ne garantit pas des performances. **Points P0 non levés :** choix de bibliothèque géométrique et benchmarks, writer V2, protocole CAS, bootstrap autonome, graphe d'imports, contrôle réel Design Space/Explore 5, matrice inverse globale. **Risques P1 :** path budget sur 50 sujets, booleans robustes, gradients/clip convertis, édition courbes et qualité colorimétrique, accessibilité Windows.

**Contrôles documentaires à effectuer après publication :** JSON de §4 parseable ; exactement 30 tests T-V34-13-01..30 ; 10 tickets V34-096..105 uniques ; liens vers source, 141 exigences héritées inchangées ; nouveaux O-028..030 uniques ; uniquement fichiers `docs/roadmap-v3.4/` modifiés. **Ne pas inscrire PASS logiciel/CI sur cette seule revue.**

## 11. Sources consultées le 29 octobre 2026

- Cricut, *How to upload images into Design Space*, modifié **30 mars 2026**, limite de 5 000 paths, calques groupés, conversion initiale en lignes de coupe, upload Internet : https://help.cricut.com/hc/en-us/articles/360009556313-How-to-upload-images-into-Design-Space
- Cricut, *Image uploads: unsupported items*, motifs/gradients, clipping paths, texte non vectorisé, images liées/embarquées : https://help.cricut.com/hc/en-us/articles/360009553213-Image-uploads-unsupported-items
- MDN, *SVG fill-rule*, distinction `evenodd`/`nonzero` (rendu SVG, **pas preuve Cricut**) : https://developer.mozilla.org/en-US/docs/Web/SVG/Reference/Attribute/fill-rule
- Sources internes lues sur `main` : `AGENTS.md`, `README.md`, V3.3 MASTER/TRACEABILITY/COVERAGE/HERITAGE/AUDIT, `ETAT_ACTUEL_SMARTSVG.md`, `docs/G3_1_EXPRESS_REAL_SVG_REVIEW.md`, `engine/web/js/smartsvg_cut_review_model_g27.mjs`, `smartsvg_cut_review_panel_g27.mjs`, `smartsvg_svg_path_grammar_g29.mjs`, `engine/smartsvg_governance/cut_path_preflight.py`, `engine/smartsvg_core/project_archive.py`, `engine/production_v211.py`. Lot 12 et registre V3.4 relus sur la branche documentaire. **Aucune exécution Windows, aucun import Design Space, aucune coupe physique, aucun prototype de courbe ou de géométrie mesuré.**

**Prochain lot 14 :** langage d'opérations de fabrication (Cut/Score/Draw/Print/Foil), modèles d'outil/matière, prévol, interdiction d'inférer une opération depuis une couleur SVG ; harmoniser le contrat `intent` de ce lot avec les commandes du lot 06 et les profils du lot 15.
