# V35-Q04L — B13 OCR : G9 original, snapshot natif et qualification Windows (14/11/2026)

**Autorité : CANDIDAT / AUDITÉ, non REVU, non ADOPTÉ ; V3.4 ACTIVE.** Aucun code, schéma, automatisation ou gouvernance modifié. Succède à Q04K ; décision **RACCORDER P2**, pas nouveau ticket V34. Sources relues sur main : `docs/ROADMAP_HERITAGE_v3_3.md` blob `c310adf3e972638c5a67332719bb2105ec37e688` ; `engine/standalone_desktop_v34.py` (lecture du fichier complet via connecteur, blob à reporter après lecture SHA dédiée) ; Q04K blob `bc4ef778747811cbf2ce04631a8454698dc0f4a7`. Recherche des commits récents retourne `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935` comme premier résultat, mais **main@HEAD NON_VÉRIFIÉ** : une recherche n'est pas une résolution de ref.

## 1. Exigences originales, pas de requalification fictive

- **G9 OCR/reconstitution :** « Conserver les textes originaux et signaler les incertitudes » ; extension après V22.0, non bloquante pour le socle.
- **S-021 :** « OCR et gestion du texte sur affiches », dépend de S-007/S-011, DoD « texte préservé / averti ».
- **S-047 :** « OCR texte de couverture », dépend de S-028/S-036, DoD « Texte vérifié avant tout remplacement ».
- **F09/G6 texte :** conserver le texte éditable dans le projet et convertir vers chemins lorsque nécessaire pour Cricut, avec avertissement ; c'est **une autre obligation**, non satisfaite par OCR ou export-only.
- **B13 #134** : capacité OCR candidate ; B12 = texte vers chemins, B09 = texte éditable. Aucun ticket V34 direct OCR n'est inventé ; tests raster du lot 12 ne deviennent pas tests de reconnaissance.

**Contradiction tranchée :** G9 autorise un outil OCR P2 avec revue humaine et original intact ; il n'autorise pas à annoncer G6.3 « texte modifiable dans projet » tant que schéma V2, migration, writer, CAS et autorisation propriétaire ne sont pas qualifiés. La conservation d'un texte OCR en mémoire ou dans un SVG externe ne satisfait pas G6.3.

## 2. Ports réels, signatures et consommateurs inspectés

`inspect_native_project(path)` délègue à `_inspect_native_project_snapshot(path)`, qui calcule `_archive_sha256` avant lecture, invoque `inspect_project_snapshot(path,expected_sha256=before)`, puis revérifie SHA ; le retour sain inclut projet V1 en mémoire et digest. `load_native_preview(path)` réutilise ce snapshot, appelle `select_source_png(project)` et `inspect_atelier_snapshot(project,before)`, revérifie SHA avant de retourner `(state,preview)`. Les états refusés `PROJECT_CHANGED_DURING_INSPECTION` et `PROJECT_INSPECTION_FAILED` ne contiennent pas de pixels.

Consommateur Tk réel : `_start_gui` instancie `LatestOnlyJob(load_native_preview)`; `refresh()` soumet le chemin sélectionné, `receive()` ignore les générations obsolètes via `jobs.current(version)`, vérifie les reçus notes/pinceau contre `atelier_snapshot.sha256`, puis `NativeImageViewport.load(original)` affiche un `tk.PhotoImage` créé à partir du PNG validé. Les widgets Tk ne sont mis à jour que sur le thread UI. `select_source_png` n'admet actuellement que l'aperçu PNG vérifié ; `NO_SOURCE`, `SOURCE_FORMAT_UNSUPPORTED`, `SOURCE_TOO_LARGE`, `SOURCE_CHANGED`, `SOURCE_INVALID_PNG` et `SOURCE_MISSING` ont des messages d'erreur dédiés. **Ce chemin ne renvoie pas de fournisseur OCR ni d'objet texte.**

**Frontière critique :** `preview.png` et `preview.width_px/height_px` représentent l'aperçu source, non une promesse de repère EXIF original ni une autorité durable. Avant un OCR, figer dans une enveloppe indépendante `project_sha256`, `source_id`, `source_sha256`, `preview_sha256`, dimensions et transformation source→aperçu vérifiée ; si le mapping n'est pas exposé/garanti, limiter la ROI à l'aperçu et interdire la réinjection géométrique dans le projet. Ne jamais passer un `PhotoImage` Tk au worker OCR. Le job OCR doit avoir son propre identifiant de génération, sans remplacer `LatestOnlyJob` ni le writer V1.

## 3. Contrat candidat de frontière

`OCRInput/1 = {project_id, project_sha256:hex64, source_id, source_sha256:hex64, preview_sha256:hex64, width_px:int, height_px:int, roi_xywh_px:[int,int,int,int], coordinate_space:"VERIFIED_PREVIEW_PX", language_bcp47, mode:"MANUAL"|"LOCAL_CPU"|"LOCAL_GPU", consent_receipt?:id, provider?:{id,version,license,model_hash}}`. Une requête est rejetée si ROI déborde, si digest ou révision ne concorde plus, si fournisseur/consentement manque ou si le repère est ambigu. Pas de copie silencieuse de l'archive vers le moteur.

`OCRProposal/1 = {input_digest, generation_id, segments:[{id,bbox_xywh_px,text_utf8,confidence_nullable,review_state:"PENDING"|"CORRECTED"|"REJECTED"}], warnings, provider_receipt?, status}`. Les coordonnées sont entières en pixels d'aperçu ; confiance non calibrée = information seulement. Un `APPROVED` explicite par segment est requis avant toute substitution externe. Source de vérité : archive V1 inchangée ; la proposition est éphémère, révisable par Undo local, sans nouveau store projet.

États : `EMPTY→PREVIEW_READY→ROI_SELECTED→MANUAL|CONSENTED_PROVIDER→RUNNING→PROPOSED→REVIEWED→EXTERNAL_STAGED→EXPORTED`, avec `STALE|CANCELLED|FAILED|REJECTED` terminaux non mutants. Changer de projet, F5, source, langue, ROI ou modèle invalide la proposition ; résultat tardif ignoré. Le retour à l'état précédent par Undo ne réécrit jamais V1. Une sortie externe doit respecter no-clobber, hash et publication atomique ; annulation/crash laissent l'ancien fichier intact.

## 4. Parcours, accessibilité et arbitrage hostile

Novice : ouvrir un projet sain → voir source PNG → sélectionner une zone → saisir le texte manuellement (toujours possible) ou consentir au moteur local présent → comparer source/transcription → corriger chaque segment → copier/exporter en dehors du projet. Expert : inspecter provenance, SHA, langue, rectangles, version/licence/hash modèle, diff et avertissements glyphes/RTL. Barre contextuelle unique « Zone / Langue / Reconnaître / Annuler / Corriger » ; états vides, pending, stale et erreur avec reprise explicite. Focus et clavier vérifiables, 1366×768/DPI 200 %, contraste/mouvement réduit ; aucune popup pour chaque correction.

Alternative simple **retenue comme fallback** : transcription manuelle, sans modèle, réseau ni installation. Option « OCR automatique puis remplacement direct » **REJETÉE** (faux positifs, licences, police et G6.3). Option « second projet OCR » **REJETÉE** (CAS et identité). CPU local uniquement après vérification des licences et modèles ; GPU RTX 8 Go optionnel, OOM → retour manuel/CPU sans promesse équivalente. Pas d'images privées, texte, EXIF, polices propriétaires ni modèles dans le dépôt ou les logs. Mesurer latence p50/p95, pic RAM/VRAM et taux de correction sur fixtures synthétiques, pas de chiffres prétendument observés.

## 5. Matrice G9→tests et qualification

| ID candidat | Preuve attendue | Statut |
|---|---|---|
| L-P01 S-021 | Affiche synthétique FR accentuée : original V1 et SHA identiques après correction OCR et réouverture | NOT_RUN |
| L-P02 S-047 | Couverture synthétique : une erreur OCR ne remplace rien avant approbation humaine | NOT_RUN |
| L-P03 B13 | Source PNG saine, ROI bornée, provenance et génération cohérentes | NOT_RUN |
| L-P04 G6.3 frontière | Tentative TextNode V1 refusée ; aucune fausse certification d'édition persistante | NOT_RUN |
| L-W01 Windows | Focus, raccourcis, F5, bascule projet, DPI 200 % et 1366×768 | NOT_RUN |
| L-N01 | Changement SHA après snapshot → STALE sans transcription publiée | NOT_RUN |
| L-N02 | Résultat tardif d'un autre projet/génération → ignoré | NOT_RUN |
| L-N03 | ROI négative, débordement ou repère EXIF non défini → refus | NOT_RUN |
| L-N04 | PNG corrompu/trop grand/non supporté → message existant, pas de job OCR | NOT_RUN |
| L-N05 | Consentement refusé, licence/hash fournisseur absent → manuel sans réseau | NOT_RUN |
| L-N06 | Crash/annulation/disque plein/collision lors d'export → no-clobber, projet inchangé | NOT_RUN |
| L-N07 | Unicode malformé, glyphes manquants, faux score confiance → avertissement/refus | NOT_RUN |
| L-N08 | Deux jobs OCR et réouverture de projet en concurrence → latest-only indépendant | NOT_RUN |

Tests unitaires non-skip, UI Windows, GPU, Design Space et coupe physique restent séparés. Design Space/coupe physique **NON APPLICABLE** à l'OCR isolé ; ils deviennent obligatoires uniquement pour une chaîne de fabrication aval. Les quatre sorties restent PNG Print Then Cut, SVG Basic Cut, SVG CUT multicouche, SVG d'édition : aucune qualification de ces exports par les tests OCR.

## 6. Micro-lots TDD, DoD et contre-expertise

L1 confirmer signatures/consommateurs et transformation ROI source↔aperçu au HEAD ; L2 fixtures et validateurs input/proposition ; L3 transcription manuelle + Undo éphémère ; L4 fournisseur OCR local optionnel avec licence/consentement ; L5 overlay Tk et génération stale, clavier/DPI ; L6 export externe atomique et relecture ; L7 essais Windows et mesures ; L8 raccordements typographiques et prévols aval, sans mutation V1. **DoD candidat :** zéro mutation V1, aucun remplacement sans approbation, erreurs explicites, reprise sans duplication, tests négatifs non-skip et preuve Windows indépendante. Réversibilité : désactiver OCR sans rendre le projet illisible. Aucune modification de format/packaging/dépendance n'est autorisée ici ; décision propriétaire distincte requise.

**Revue hostile :** un SHA du projet ne verrouille pas le fichier et un SHA de preview ne certifie pas le repère source ; un job latest-only de preview ne protège pas automatiquement un second worker OCR. Ces trois risques restent des gates explicites. Le contrôle des consommateurs est ciblé sur le shell observé ; pas d'affirmation d'exhaustivité sur tous les autres modules/PR.

## 7. Audit R3 — 25 axes

01 lots 24 conservés, non requalifiés ; 02 S-021/S-047 exacts, G6.3 ouvert ; 03 tickets V34 intacts ; 04 B13 sans certification UX ; 05 437 inventoriés, pas PASS ; 06 HEAD/PR et produit séparés ; 07 V1/CAS/Subject/float32 intacts ; 08 quatre exports distincts ; 09 opérations machine non applicables au port OCR, aval distinct ; 10 novice/expert et correction ; 11 canevas/ROI/Undo non mutant ; 12 focus/DPI Windows à tester ; 13 stale, crash, concurrence, rollback ; 14 IA opt-in, CPU/manuel, GPU facultatif ; 15 raster SHA/PNG/EXIF ; 16 géométrie SVG non applicable à la transcription isolée ; 17 Fabrique/batch hors port isolé ; 18 Smart Delivery hors port isolé ; 19 #141 sans nouvelle décision globale ; 20 protocole de mesure, aucun résultat inventé ; 21 licences/privacy ; 22 branche docs seule ; 23 pas de second writer/job confondu ; 24 non-promu, gouvernance séparée ; 25 aucune obligation compressée. **Verdict : AUDIT PARTIEL, pas certification.**

**Photographie historique non recalculée :** 24/141/140/80/437 inventoriés, 431/437 liens TEST→TICKET explicites, six exceptions, dix G6/G9 sans ticket direct, 0/80 UX certifiées ; tous nouveaux tests NOT_RUN.

**Prochaine action UNIQUE Q04M :** vérifier `source_preview_v34.select_source_png` et `native_preview_jobs_v34.LatestOnlyJob` au SHA exact, puis fermer ou maintenir explicitement le risque de mapping ROI/source et concurrence OCR avant toute fiche B13 « REVUE ».
