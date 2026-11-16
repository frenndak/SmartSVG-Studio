# COV-10C — Contrats V1, texte/objets et exporteurs : audit des ports réellement présents

**Date :** 13 novembre 2026. **Décision :** P0 pour préserver le contrat V1 ; P1 pour préparer les parcours G6 ; P2 maintenu pour les fonctions G9 historiquement P2. **Statut : CONTRE-EXPERTISÉ SUR SOURCES / SPÉCIFIÉ COMME CANDIDAT**, non intégré à la roadmap normative, non implémenté, **tests nouveaux NON EXÉCUTÉS**.

## 1. Référence vérifiée et sources exactes

L'endpoint GitHub **`GET /repos/frenndak/SmartSVG-Studio/branches/main`** a retourné le HEAD exact `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`, distinct d'une recherche de commits triée. La branche de conception `roadmap/v3-5-design-candidate-20261112` était au commit `5b517c2132a35a778bc44170598ff7789c8a735b` à l'ouverture ; elle évolue par commits documentaires, **pas** comme un miroir de main. Trois PR code DRAFT au contrôle : #138 (recovery), #139 (Undo/Redo disponible en lecture), #140 (viewport Tk sans taille). Elles ne constituent pas une implémentation G6/G9.

| Fichier réel sur main@aa0ff9e7 | SHA **blob** lu | Interfaces et conclusion bornée |
|---|---|---|
| `engine/smartsvg_core/project_contracts.py` | `7bfd2d714384717c6ce0bb66659971881bd285c2` | `SourceAsset`, `Mask`, `Subject`, `Artifact`, `QAResult`; `Artifact.use` ne permet que `print_then_cut_png/basic_cut_svg/editable_svg` |
| `engine/smartsvg_core/project_archive.py` | `141d825afa29f2ad893929e8630b8a4a288f0c38` | `LoadedProject`, `load_project`, `save_project`, `_validate_bundle`; `smartsvg-project/1`, ZIP borné, manifeste SHA, sauvegarde avec relecture, pas un export Cricut |
| `engine/smartsvg_core/project_workspace_g22.py` | `13b8e40d6fcc9cf03ed2c935b38ad6eff0bcbe03` | `ManagedWorkspace.create`, `save_editor_document`, `editor_document`, `save_base_masks`, identités et historique pinceau ; le document éditeur actuel **valide des traits**, pas un modèle complet de texte |
| `engine/smartsvg_core/editor_session_g23.py` | `dda853694d22f59252b9549b5e2fdbd59933bd59` | `parse_editor_document` exige exactement `version,width,height,count,source,strokes` ; aucun `text`/`font`/`layers` dans ce contrat strict |
| `engine/smartsvg_core/project_recovery.py` | `002427009d72935a6df31368289cba94970061da` | `save_with_recovery`, contrôle des SHAs et restauration explicite ; writer/récupération à réemployer |
| `engine/smartsvg_core/native_project_create_v34.py` | `4578f8304d94ed860c12f93bfe6032d27709c261` | `create_native_project` construit un V1 depuis PNG, lit et vérifie le fichier enregistré ; `sources` non vides, `subjects/artifacts/qa_results` initialement vides |
| `engine/standalone_desktop_v34.py` | `abdfe2f16be1b72375513f2a07769920d92e5dd7` | `_start_gui`, `inspect_native_project`, `load_native_preview` ; pages Accueil, Projet, Fabrique, Apparence et Atelier Tk réelles ; aucune API de création typographique n'a été identifiée **dans cette entrée native** |
| `engine/native_app_shell_v34.py` | `b5cc4f503791d6f24ac62027323cb726973b54a2` | `NativeAppShell` gère pages et navigation, **non** un deuxième writer |
| `engine/smartsvg_core/template_geometry_v34.py` | `3142c2e379fd28c2b506c343527b932780d6fcee` | `folded_card` et `open_tray` géométries nominales en mm, `CUT/SCORE`, `persisted=False` |
| `engine/smartsvg_core/template_preflight_v34.py` | `4cf83b1a12d0fbaa4c0f7cd52576ceb1c50434dd` | `preflight_template` accepte une whitelist de ces deux `template_id` ; n'autorise PAS implicitement topper, étiquette ou diorama |
| `engine/production_v211.py` | `5f71c20c3fee7fdec1edb5d3e4efdf2f57a764df` | `run_v211(pixels,destination,...)` producteur raster/stickers **historique** basé sur moteur v21, pas un port d'export d'objets texte natifs V1 |
| `engine/smartsvg_cricut/direct_import_v218.py` | `a49fc10844559d431f393a7f7f56343ebefeb1cf` | `prepare_cricut_import(report,dpi)` publie des PNG Print Then Cut avec prévol local ; la validation Design Space/Explore 5 **reste externe** |
| `engine/smartsvg_governance/artifact_qa.py` | `c47009f2a47e664dc0ee36433f7f562dc7a675f0` | `audit_project(report_path,requested_intent)` vérifie des exports historiques PNG/SVG, répond `BLOCKED` ou `REVIEW_REQUIRED`, ne certifie pas la coupe |
| `engine/smartsvg_cricut/delivery_v21122.py` | `98a2580c529f613ca732a69fda5273a317f64daf` | `delivery_manifest(report)` contrôle fichiers et SHA ; `write_delivery(root,manifest)` publie un **JSON**, **pas** une archive Smart Delivery ZIP |
| `engine/smartsvg_ai/routing_v21121.py` | `b039543450d69ff94c9a9e83e6e93c5255f1b1fe` | Module de routage annoncé explicitement **sans OCR** ; absence d'API OCR ailleurs **non prouvée de manière exhaustive** |

**Points de code inspectés précisément :** `project_contracts.py:135–190,191–219`, `project_archive.py:29–58,551–621,704–778`, `project_workspace_g22.py:213–265,420–501`, `editor_session_g23.py:43–97`, `native_project_create_v34.py:60–98`, `standalone_desktop_v34.py:44–160,187–300`, `production_v211.py:246–286`, `direct_import_v218.py:304–390`, `delivery_v21122.py:11–70,169–195`, `artifact_qa.py:26–138`.

La recherche de code ciblée sur `text_object`, `OCR`, `editable_svg`, `svg_export` n'a pas mis en évidence **un contrat d'édition de texte natif V1 vérifié** ni un exporteur natif complet pour les 4 sorties. **Absence non prouvée** au niveau du dépôt entier : d'autres ports/branches peuvent exister. Interdiction de qualifier les fonctionnalités absentes sans inventaire exhaustif et tests.

## 2. Résolution de contradictions documentaires

### C-01 — Deux exigences avaient leurs propriétaires inversés dans COV-10B

Après relecture de `docs/ROADMAP_TRACEABILITY_v3_3.md` et `docs/ROADMAP_HERITAGE_v3_3.md`, la matrice historique COV-10B avait **inversé S-037 et S-064** :
- **S-037** = *gabarits métiers* : trois créations étiquette/topper/carte, sauvegarde/relecture.
- **S-064** = *typographie et licences des polices* : rendu reproductible ou avertissement précis.
- **R33-028** = polices/licences/glyphes manquants visibles, en F09/G6–G8 ; **pas** un gate diorama G9.

**Correction appliquée à COV-10B sur cette branche** en conservant l'historique Git, sans changer la norme V3.3.

### C-02 — JSON document ouvert ≠ API d'objets texte implémentée

`LoadedProject.document` est un `dict`, mais les consommateurs existants valident des **sous-documents précis**, notamment `editor_v216` qui accepte **uniquement** `strokes` et des empreintes. Il est techniquement trompeur de considérer un champ JSON libre comme un support stable des objets `TextNode`, `FontRef`, `Layer`, de leur Undo, de leurs exports et de leur migration. Une écriture directe non concertée dans `.smartsvg` rendrait l'ensemble non interopérable.

**Décision** : la V3.5 spécifie un **contrat logique de brouillon** texte/forme dans l'Atelier, avec identité et provenance ; persistance uniquement par writer versionné après ADR de compatibilité et validation. Si une extension dans `document` V1 est prouvée compatible avec anciens lecteurs, la spécifier sous namespace strict, quotas, round-trip et CAS ; **sinon, migration V2 explicite** sans remplacer V1. Ne pas déclarer le schéma V2 nécessaire avant le test de compatibilité, mais ne pas déclarer l'API texte existante non plus.

### C-03 — Quatre contrats export ≠ trois valeurs Artifact

`Artifact.use` V1 n'autorise que `print_then_cut_png`, `basic_cut_svg`, `editable_svg`. Le **SVG Cut multicouche** reste une **projection externe**, jamais une fausse entrée `editable_svg` ; les opérations `CUT/SCORE/DRAW/PRINT/FOIL` restent métadonnées et étapes de transfert, non un nouveau type stocké frauduleusement. `run_v211` n'est pas un exporteur natif d'un document typographique. La livraison ZIP Smart Delivery n'est pas le fichier projet V1 ni l'exporteur raster.

### C-04 — Reuse historique vs architecture de packaging

`write_delivery()` crée un manifeste JSON `07_LIVRAISON_STICKERS_V21_12_2/MANIFESTE_STICKERS.json` avec publication exclusive. Pour Smart Delivery SD0–SD2, réutiliser **les données** et la vérification des chemins de `delivery_manifest` et le prévol de `artifact_qa`, sans utiliser `write_delivery` comme s'il savait produire un ZIP. Un composant d'**assemblage externe** typé et borné peut être ajouté **après contrat d'entrée commun**, sans second moteur de production ni writer de projet.

### C-05 — Port patron ne vaut pas éditeur de composition

`folded_card` et `open_tray` sont des géométries 2D paramétriques en mm, sans projet ni export. `preflight_template` refuse toute proposition hors de sa whitelist. Les trois gabarits G6 (étiquette, topper, carte) et le diorama quatre plans G9 doivent donc être rattachés à l'Atelier/Fabrique **par des adaptateurs contrôlés**, avec ADR sur le registre de patrons avant d'élargir la whitelist. Pour S-066, **exactement 4 plans** dans la recette terrain ; ne pas « satisfaire » par une carte pliée ou une boîte.

## 3. Matrice corrigée des dix obligations G6/G9 : propriétaires conceptuels et premiers DoD

| Exigences liées | Priorité héritée / fonction | Réemploi vérifié | Travail restant / blocage de conformité |
|---|---|---|---|
| **S-036, S-064, S-092, R33-028** | P1 G6 — texte, conversion glyphes en chemins, preview police, licence | `ManagedWorkspace` CAS, `LoadedProject.document` générique, UI Tk (ni éditeur texte complet ni police QA prouvés) | **G6-PORT-1** : ADR objet `TextDraft` + `FontRef`, licenciement explicite ; save/reopen + fail-closed police absente, unicode et export non destructif |
| **S-037** | P1 G6 — étiquette/topper/carte | `template_geometry_v34` propose carte pliée et boîte ouverte uniquement, prévol `template_preflight` contrôlé | **G6-PORT-2** : trois producteurs/recettes métiers adaptés, géométrie mm et test d'export réel + relecture, sans prétendre que `folded_card` vaut déjà un topper |
| **S-021, S-047** | P2 G9 — OCR affiche et couverture | `routing_v21121` sans OCR ; image/source V1 et préparation de retouche existants | **G9-PORT-1** : proposition OCR non mutante, licence/consentement, bbox pixels source, diff utilisateur, annulation et CAS ; fallback saisie manuelle sans modèle |
| **S-044, S-066, S-099** | P2 G9 — diorama multicouche et guide | conventions mm CUT/SCORE et deux patrons géométriques ; UI Fabrique Tk | **G9-PORT-2** : planification 4 calques alignés, identités et ordre, guides, réemploi prévol ; tests géométrie puis Design Space puis coupe physique **séparément** |

**Critères source détaillés à conserver** : S-021 texte préservé/averti ; S-036 aucune substitution silencieuse ; S-037 trois gabarits testés ; S-044 prototype assemblé ; S-047 OCR contrôlé avant remplacement ; S-064 rendu reproductible/avertissement ; S-066 quatre plans alignables avec tolérances réelles ; S-092 caractères FR et police absente contrôlés ; S-099 guide d'assemblage UI et prototype mesuré ; R33-028 visibilité des licences et glyphes manquants.

**Statut** : ces 10 exigences restent `GAP_HÉRITAGE_G6_G9` quant à leur rattachement à un ticket V34 direct ; elles ont ici une **orientation technique vérifiée partiellement**, pas un propriétaire produit adopté ni une preuve Windows.

## 4. Contrat d'intégration candidat : un seul état et une seule autorité

**Frontière proposée pour les fonctionnalités G6/G9** :

```text
Source V1 immuable + expected_sha256
        → propositions (OCR / gabarit / 4 plans / texte)
        → normalisation et prévol (aucune mutation)
        → Atelier/Fabrique Tk : aperçu / modifier / Undo brouillon / avertissements
        → validation explicite de l'utilisateur
        → writer CAS/récupération existant UNIQUEMENT si contrat de persistance autorisé
        → QA + 4 ports d'exports DISTINCTS, ceux réellement raccordés
        → Design Space guidé, puis essai physique humain séparé
```

**DTO proposés (non présents)** :
- `TextDraft`: `draft_id,project_sha,source_ref?,text_utf8,font_ref?,font_license_state,glyph_coverage_state,dimensions_mm,layout,warning_codes`.
- `OCRProposal`: `source_sha,revision,bbox_source_px,transcript,candidate_confidence_or_UNKNOWN,engine_version,license_state,consent_receipt?`.
- `TemplateRecipe`: `recipe_id,revision,parameters_mm,geometry_paths,operations,material_profile_state` ; **adapter** les anciens `folded_card/open_tray` au lieu de les copier.
- `DioramaProposal`: `source_sha,planes[4]{plane_id,geometry,order},alignment_marks_mm,material_thickness_mm_or_UNKNOWN,assembly_order,warning_codes`.

**Borne de sécurité** : pas de création de forme depuis un OCR seul ; pas d'affectation de `SCORE` par couleurs/pointillés ; pas de profil matière/outil inventé ; jamais d'exécution de scripts dans SVG ou HTML ; aucune police commercialement restreinte dans le dépôt public ; tout résultat après changement de SHA doit devenir `STALE` plutôt que modifier le projet. Aucun upload, téléchargement ou installation de modèle OCR sans consentement.

**Flux novice** : importer → choisir `Texte`, `Gabarit` ou `Diorama` → voir un brouillon et les limites ; aperçu direct sans commit → corriger texte/mesures → Valider uniquement si le mode sauvegarde/export correspondant existe → guide humain. Si une fonction manque : afficher `Non disponible dans cette version`, pas une maquette cliquable laissant croire à un outil opérationnel.

**Flux expert** : inspecter `source_sha/loaded_project_sha`, identités, dimensions mm, provenance de fonte/licence, état QA; comparer rendu typographique et chemins; conserver des paramètres versionnés et pouvoir annuler sans toucher à la source. Clavier et focus cohérents 1366×768/DPI 200 %, contraste/motion réduite ; mesures UI encore à réaliser.

## 5. TDD, preuves et non-régressions à fournir par l'ingénierie — NON EXÉCUTÉS

| Test proposé / ID candidat | Positif mesurable | Trois négatifs minimum, reprise et oracle |
|---|---|---|
| `V35-G6-TEXT-01` | Texte accentué sauvegardé/réouvert sans modification ; référence police et glyphes explicites | police absente ; licence inconnue ; caractère non représenté ; conflit CAS ; annulation avant commit laisse ZIP SHA inchangé |
| `V35-G6-PATH-01` | Texte exporté en chemins avec rendu comparé et unités mm ; source d'édition conservée | chemin absent ; caractères modifiés ; SVG dangereux / DTD ; export en `editable_svg` jamais usurpé en `basic_cut_svg` |
| `V35-G6-TEMPLATE-01` | Chacun des trois gabarits métier étiquette/topper/carte produit un vrai objet et reouvre un projet | NaN / mm négatif ; ID dupliqué ; format hors planche ; crash/disque plein avant commit, aucune corruption |
| `V35-G9-OCR-01` | OCR opt-in sur document synthétique, correction du texte explicitement confirmée | OCR absent ; résultat périmé ; consentement refusé ; caractères incertains / licence non autorisée ; repli manuel |
| `V35-G9-DIORAMA-01` | Quatre plans alignés, guide d'assemblage; test réel séparé à enregistrer | repère non aligné ; plan manquant/dupliqué ; matériau/épaisseur inconnus ; pseudo-PASS physique sans photo/mesures doit être refusé |
| `V35-SD-CONTRACT-01` | Smart Delivery externe produit un ZIP relu et des hashes contrôlés dès un export disponible | ZIP-slip et symlinks ; chemin Windows réservé/collision ; source modifiée pendant copie ; no-clobber/destination OneDrive non atomique ; aucune mutation du projet |

**Conditions des PASS séparées :**
- `AUTO_UNIT` : exécutions ciblées au commit SHA, non-SKIP et fixtures synthétiques licites ;
- `WINDOWS_UI` : vraie interaction Tk et DPI/keyboard/focus ;
- `GPU` : seulement si un OCR/IA local réel est installé, consentement, VRAM et log exact-SHA ;
- `DESIGN_SPACE` : preuve datée de version, import et opération contrôlée ;
- `PHYSICAL_CUT` : outil, matière, tapis, dimensions cibles et mesurées, protocole humain.
**Rien ci-dessus n'a été exécuté dans cette opération**. L'inspection de code est un audit statique, pas un benchmark.

## 6. Contre-expertise contradictoire et choix de priorités

1. **Option “utiliser document.json comme dictionnaire libre” — REFUSÉE sans contrat et tests de lecteur** ; elle serait facile à coder, mais invaliderait les hypothèses de reprise/Undo/interopérabilité. Préférer ADR d'extension compatible ou migration V2 formelle.
2. **Option “tout migrer vers un nouveau framework UI” — REFUSÉE sans benchmark** ; `standalone_desktop_v34.py` + `NativeAppShell` sont des surfaces réelles, ne pas créer une seconde application.
3. **Option “fusionner OCR et texte dans un moteur IA universel” — REFUSÉE** ; saisie/édition typographique manuelle P1 doit fonctionner sans IA ni réseau ; OCR P2 reste une proposition, pas un prérequis du texte.
4. **Option “gabarits = copies de folded_card” — REFUSÉE** ; un topper et une étiquette ne sont pas une carte pliée, même si géométrie mm et prévol peuvent être réutilisés.
5. **Option “Smart Delivery réécrit write_delivery en gros exporteur” — REFUSÉE** ; `write_delivery` ne publie que le JSON historique. Ajouter packaging externe borné et typé sans dédoubler production et QA.
6. **Option “tous les P2 bloquent la sortie stable” — REFUSÉE** ; critères V3.3 hérités restent contraignants, mais jalons A/B/C, capacité de travail en parallèle et décisions de report approuvées doivent distinguer **non livré** de **perdu**.

## 7. Vérification des 25 contrôles R3

- 01–05 héritage : **24 lots, 141 exigences, 140 tickets, 80 UX, 437 recettes** conservés ; **431/437** références TEST→TICKET explicitement relevées, **6 sans ticket direct**, et **10 exigences G6/G9** sans ticket V34 direct. Ces lacunes restent **OUVERTES**.
- 06 statuts : aucun `PASS` extrapolé ; branche/code/Windows/Design Space/physique distingués.
- 07–09 projet et fabrication : V1 et CAS, float32, quatre exports distincts, opérations typées conservés.
- 10–13 UI/recovery : parcours novice/expert, undo/local, clavier/focus, DPI et scénarios négatifs définis, tests réels non réalisés.
- 14–16 IA/raster/vectoriel : OCR optionnel, source et masques inchangés, SVG/units et sécurité à qualifier.
- 17–19 batch/bibliothèque/Smart Delivery/opportunités : aucune modification de leur autorité ; **audit global reste ouvert** et ne devient pas N/A pour promotion.
- 20 performances : objectifs à mesurer, aucun chiffre de latence inventé.
- 21 sécurité : licence polices/OCR, pas d'images privées, confidentialité, contrôle des ZIP.
- 22–25 gouvernance : branche de conception uniquement ; revue indépendante et promotion séparée requises. **COV-10C n'est PAS le DoD de toute la V3.5**.

## 8. Handoff, prochains micro-lots

**COV-10C DONE = code API cartographié au SHA exact + contradictions résolues**, pas G6/G9 “livrés”.

**Suivant (COV-11) :** produire `BACKLOG_AND_DEPENDENCIES.md` avec graphe ordonné des domaines V3.5, jalons A/B/C, micro-lots P0/P1/P2, DoD et dépendances réelles sans effacer les 140 tickets ni ajouter de doublons. Inclure text/typographie OCR/diorama et Smart Delivery, puis attaquer `UX_ARCHITECTURE_AND_WORKFLOWS.md` et `QUALITY_TESTS_AND_EVIDENCE.md` avec une contre-expertise externe.

**Preuves enregistrées :** `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935` vérifié par endpoint branche ; source blobs ci-dessus ; correction COV-10B commit `f79ca9f3eaa9e46bc0a15ba9edab8fc8b1744ba4`. Aucun code/AGENTS/pr/merge/tâche de dev modifié.
