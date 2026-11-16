# V35-Q04C — Lot 06 réel : rapprochement B09–B14, DoD et scénarios

**14 novembre 2026 — CANDIDAT / NON CERTIFIÉ.** Source exacte retrouvée : `docs/roadmap-v3.4/06_COMMAND_BUS.md` (blob `074879c0729042a77e8addc60b8c9446c176c183`). Il s'agit de **commandes, historique, transactions, jobs et concurrence**, et non d'un lot de typographie. L'hypothèse Q04B selon laquelle les DoD du lot 06 qualifieraient directement B09–B14 est **réfutée**. Aucune modification de V3.4, de schéma, de code ou de gouvernance.

## 1. Contre-expertise de la source et des six UX

Les neuf tickets du lot 06 sont V34-032..040. Les 30 scénarios `T-V34-06-01..30` concernent receipts, CAS, Undo, jobs, synchronisation UI, sûreté, annulation et reprise. **Aucun ne prouve la création, le rendu, l'enregistrement ou la réouverture d'un objet texte**. Il faut conserver la traçabilité de leurs responsabilités transversales, sans les attribuer artificiellement à un outil typographique.

| UX #134 | Obligation propre préservée | Lien lot 06 légitime, mais insuffisant | Critère manquant avant certification |
|---|---|---|---|
| B09 | texte éditable, polices et typographie | V34-032/033/035, T-06-04/05/13–16 : mutation sûre seulement si contrat persistant autorisé | G6.3 : texte encore modifiable après sauvegarde/réouverture, glyphes/licence |
| B10 | texte sur chemin, courbe, cercle, monogrammes, étiquettes | V34-035/038, T-06-13–15 : Undo futur d'une commande compatible | positionnement, dimensions mm, transformation et réouverture sans perte |
| B11 | effets contours, ombres, textures, dégradés | V34-032, T-06-27 : aucune mutation par assistant non autorisé | rendu, séparation effet visuel/chemin CUT, alpha et provenance |
| B12 | texte→chemins, fusion et fabrication | V34-035, T-06-14/24 : opérations CUT/SCORE et Undo distincts | trous, winding, unités mm, SVG éditable ≠ SVG CUT |
| B13 | OCR facultatif et correction du texte | V34-036/039, T-06-17–20/27/29 : job isolé, stale, consentement | qualité OCR mesurée, correction manuelle, police/glyphes et persistance |
| B14 | Smart Compose : marges, alignement, hiérarchie, modèles visuels | V34-037/038, T-06-23/26 : vues resynchronisées | modèles et marges éditables/reproductibles, G6.2/6.6/6.7 |

**G6.1–G6.7 :** G6.1 édition texte/formes/calques, G6.2 groupe/grille/alignement, G6.3 texte persistant et fonte manquante, G6.4 gabarits étiquette/topper/carte, G6.5 historique/variantes/réouverture, G6.6 souris/clavier/mm/Undo, G6.7 démarrage par usage. Les six UX ne couvrent pas seules les gabarits métiers ni l'intégralité de G6 ; les dix exigences G6/G9 sans ticket source explicite restent ouvertes, sans réaffectation rétroactive.

## 2. Décision architecturale et contrats

**RACCORDER** les six capacités aux contrôles transversaux du lot 06, **REPORTER** la certification G6.3 jusqu'à persistance démontrée. Le lot 06 propose un bus **V2 futur**, avec `expected_project_sha256`, `logical_revision`, receipts et epochs ; ce n'est pas une API V1 existante. La V1 `smartsvg-project/1` reste seule source de vérité via writer/SHA/CAS et Subject/masques float32. Ne jamais sérialiser un `TextNode` dans les strokes. Une proposition texte peut être temporaire et exportée honnêtement, mais ne satisfait pas « éditable dans le projet ». Tout schéma V2 exige ADR, migration en copie, autorisation propriétaire, rollback et essais Windows.

Contrat **candidat, non implémenté** : `TextProposal {version:1, project_sha256:hex64, draft_id:opaque, text_nfc:string, font_ref:string, font_license:VERIFIED|UNKNOWN|RESTRICTED, missing_glyphs:string[], geometry_space:SOURCE_PX|OUTPUT_MM, operation:PREVIEW|EXPORT_ONLY}`. Validation : nombres finis, unités explicites, texte Unicode, police/licence connue avant incorporation, SHA actuel avant commit. États `EMPTY → DRAFT → PREVIEW → REVIEWED → EXTERNAL_EXPORT` ; sorties `STALE/CANCELLED/ERROR` sans écriture. Undo du brouillon uniquement ; Undo d'une sortie externe ou coupe physique impossible.

Conserver quatre sorties distinctes : PNG Print Then Cut, SVG Basic Cut, SVG CUT multicouche, SVG d'édition. Aucun effet d'ombre, contour visuel ou OCR ne devient une opération CUT. Profil Cricut `KNOWN/UNKNOWN` et validation Design Space restent séparés. CPU/saisie manuelle disponibles sans IA ; OCR local facultatif après consentement, sans téléchargement ni transfert implicite.

## 3. Parcours et recettes TDD proposées

Novice : ajouter texte → voir aperçu sur canevas → corriger glyphes/marges → vérifier avertissement de non-persistance → consentir à l'export externe → réouvrir projet sans fausse promesse. Expert : police/licence, chemins, unités mm, hiérarchie, diagnostic topologique, QA par rôle et provenance. Barre contextuelle et poignées, pas de nouveau store ; focus clavier, 1366×768, DPI 200 %, contraste et motion réduit à éprouver sur Windows. États vides, chargement, erreur, reprise et conflit visibles.

Tests positifs futurs : P1 projet V1 et masques inchangés après preview ; P2 texte Unicode et fonte connue ; P3 chemins avec trous et dimensions mm ; P4 quatre rôles d'export vérifiés séparément ; P5 resynchronisation de deux vues. **Négatifs** : N1 fonte absente sans substitution silencieuse ; N2 licence inconnue bloque embed ; N3 SHA périmé après OCR refuse commit ; N4 DTD/entité externe SVG rejetée ; N5 NaN, trous invalides et CUT ambigu rejetés ; N6 disque plein conserve projet et sortie précédente ; N7 crash entre publication et ACK impose inspection recovery ; N8 deux writers concurrents → second refus CAS ; N9 annulation de job et résultat tardif sans mutation ; N10 Undo après export n'efface aucun fichier physique. Fixtures synthétiques autorisées, aucune police propriétaire distribuée. Cibles de latence/mémoire à fixer **après** mesure p50/p95 sur corpus et configuration documentés.

Micro-lots : (1) matrice B09–B14 vers critères V3.3 et lots **18/20/13/17** pertinents, (2) preuve des ports V1/consommateurs, (3) contrats et tests de preview, (4) décision ADR persistance, (5) QA exports et rollback, (6) essais UI Windows, (7) Design Space/physique seulement si pertinents. DoD documentaire de Q04C : source exacte identifiée, faux lien lot 06→texte corrigé, lacunes consignées. **DoD produit non satisfait**.

## 4. Audit des 25 contrôles

01–05 : inventaires 24/141/140/80/437 conservés ; 431/437 liens explicites et six exceptions non résolues ; 0/80 UX certifiées. 06 : statuts de preuve séparés, HEAD main NON_VÉRIFIÉ par lecture directe du ref. 07 : V1/CAS/float32 préservés. 08 : quatre exports séparés. 09 : aucune opération machine inventée. 10–11 : parcours et gestes/Undo proposés. 12 : clavier/DPI Windows NOT_RUN. 13 : annulation/crash/concurrence couverts en recettes. 14 : OCR facultatif, fallback manuel. 15 : raster/ICC non modifiés, PNG PTC à qualifier. 16 : géométrie/mm/topologie à tester. 17 : batch/Fabrique hors portée de cette fiche, héritage intact. 18 : ZIP Smart Delivery hors portée, non supprimé. 19 : opportunités #141 inchangées. 20 : performance non mesurée. 21 : licences/XML/confidentialité. 22 : branche documentaire seulement. 23 : aucun second store/writer. 24 : adoption et CI non revendiquées. 25 : correction substantielle du mauvais domaine du lot 06, pas un renommage.

**Preuves :** lecture du blob historique du lot 06 et du registre d'héritage ; aucun nouveau test exécuté. Les 31 PASS historiques de COV22 ne prouvent pas le texte. Windows, GPU, Design Space, physique = NOT_RUN. Statut B09–B14 : AUDITÉ PARTIELLEMENT, NON CERTIFIÉ.

**Prochaine action UNIQUE Q04D :** lire le lot 18 `18_ATELIER_GRAPHIQUE.md` et les critères V3.3 G6.1–G6.7 ; produire une matrice exacte des DoD/scénarios pertinents pour B09–B14, sans inférer une implémentation de texte.
