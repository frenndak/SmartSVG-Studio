# V35-Q04U — B13/G9 : matrice T0 multi-source, erreurs et identité de révision
Date : 2026-11-15. **CANDIDAT NON NORMATIF ; V3.4 ACTIVE.** Suite de Q04T, sans code produit ni changement de projet V1.

## Preuves sources et portée
- `tests/test_v34_native_source_preview.py` blob `4bf02ec1d61c1b7657a53f034f27a9d96a172054` : neuf méthodes de tests identifiées (source unique, vide/non-PNG, ressource absente, octets modifiés, signature, dimensions, limites octets/pixels, subsample). **Aucune ne construit un projet à deux PNG avec sélection explicite par ID.**
- `tests/test_v34_native_preview_jobs.py` blob `f09b099ec6db275848b232bcf335c1e6736769dc` : test du worker réel sans écriture, contrôle des appels d'archive, invalidation de génération, annulation de requête en attente, fermeture, exceptions, swap d'archive avec project_id inchangé. **Aucune preuve que le résultat OCR futur porte source_sha et project_sha ou que l'exécution OCR active soit interrompue.**
- `engine/smartsvg_core/source_preview_v34.py` blob `923caa23c1f6039f26a486768032b91a71b23ebf` : `select_source_png(project)` retourne le premier PNG dont le statut n'est pas `SOURCE_TOO_LARGE`. Une première source PNG invalide provoque un refus sans bascule automatique vers une seconde valide. DTO `SourcePreview` sans SHA. **Ceci est une politique existante, non une preuve de bug à corriger sans arbitrage.**
- Sources héritées : B13, S-021, S-047 (G9), lots 07/12/18, Q04S/T. Aucun TextNode V1, aucune substitution silencieuse de fonte, aucune révision d'AGENTS.

## Décision et contre-expertise
**RACCORDER/AMÉLIORER (P1, après prévisualisation P0)** : conserver `select_source_png` pour l'aperçu historique et concevoir un **port distinct** `select_verified_source_for_roi(project, requested_source_id)`, construit à partir de l'archive validée, sans second store. Le nom est une proposition et non une API présente. Pas de fallback implicite « deuxième PNG valide » : un utilisateur peut choisir explicitement la source B après diagnostic de A. Éviter d'ajouter `source_id` facultatif au sélecteur historique sans test de compatibilité ; alternative minimaliste : OCR manuel sur source unique, et désactivation explicite de la ROI pour multi-source tant que le port n'existe pas.

**Contexte candidat** : `project_id:string`, `project_sha256:hex64`, `source_id:string`, `source_sha256:hex64`, `png_sha256:hex64`, `width_px:int>0`, `height_px:int>0`, `roi_xywh_px:tuple[int,int,int,int]`, `viewport_generation:int`, `request_id:string`. Origine en haut à gauche, coordonnées source entières, rectangle demi-ouvert et strictement borné ; SHA PNG=SHA source pour octets originaux. Le port doit refuser si la révision d'archive, l'identité source ou la génération viewport changent entre drag, gel et réception. Le masque float32 n'est jamais source OCR.

## Matrice T0 — réemploi réel et manques
| Cas | Oracle actuel | Nouveau test TDD proposé | Niveau |
|---|---|---|---|
| T0-01 source unique intacte | `test_real_source_png_is_selected_without_mutating_project` | préserver byte-identité, SHA et source_id dans contexte ROI | unitaire |
| T0-02 sources vides/non-PNG | `test_empty_sources_and_non_png_graceful` | refus explicite sans sélection ni mutation | unitaire |
| T0-03 ressource manquante | `test_missing_resource_fails_closed` | A absente, B valide : choix explicite B uniquement ; A toujours refusée | unitaire |
| T0-04 octets modifiés | `test_modified_bytes_cannot_be_shown` | A SHA faux, B sain : pas de substitution silencieuse | unitaire |
| T0-05 PNG invalide | `test_invalid_png_header_refused` | choix A invalidé avant décodage Tk | unitaire |
| T0-06 dimensions incohérentes | `test_dimensions_must_agree_with_source_metadata` | métadonnées source_id identiques mais dimensions révisées : contexte stale | unitaire |
| T0-07 quota dimensions | `test_large_declared_dimensions_refused_before_decoder` | rejet ROI avant allocation | unitaire |
| T0-08 quota encodé | `test_encoded_bytes_bound_avoids_large_tk_allocation` | pas de décodage ni écriture | unitaire |
| T0-09 subsample | `test_large_but_allowed_png_preview_has_display_subsample` | ROI calculée en pixels originaux, non écran | unitaire + Windows |
| T0-10 changement archive même ID | `test_same_project_id_replaced_after_inspection_is_not_mixed` | comparer SHA archive avant handoff et au commit | intégration |
| T0-11 génération ancienne | `test_new_selection_invalidates_older_generation` | ancienne réponse OCR refusée même si worker actif termine | intégration |
| T0-12 fermeture | `test_close_rejects_new_requests_and_stale_results` | fermeture pendant ROI/OCR : aucun callback Tk ni export | intégration + Windows |

## Oracles additionnels et cas adversariaux (NOT_RUN)
Positifs P1 : deux PNG valides A/B, sélection B donne octets et SHA B ; P2 : sélectionner A puis B invalide ROI A ; P3 : zoom/pan sans modification de source conserve ROI gelée en pixels source ; P4 : mode manuel fonctionne sans réseau ; P5 : retour arrière local restaure uniquement la sélection éphémère.

Négatifs N1 : ID inexistant ; N2 : ID dupliqué dans archive non valide ; N3 : PNG A invalide/B valide sans consentement au changement ; N4 : SHA source altéré ; N5 : archive remplacée avec même project_id ; N6 : source remplacée avec même ID ; N7 : viewport régénéré durant drag ; N8 : ROI vide ; N9 : ROI hors limites ; N10 : OCR tardif après sélection B ; N11 : fermeture Tk pendant callback ; N12 : fournisseur OCR non consenti ; N13 : image masque substituée ; N14 : JPEG demandé au port PNG ; N15 : export destination existante ; N16 : disque plein ; N17 : Unicode/RTL + focus ; N18 : source trop grande ; N19 : source absente ; N20 : résultat OCR non vérifié tenté comme texte éditable V1. Tous attendus : refus explicite, aucun changement de projet ni export non autorisé.

## UX, sécurité, performance et plan TDD
Parcours : projet vérifié → panneau source (liste IDs, dimensions, états d'admissibilité) → source choisie → mode ROI/PAN → geste réversible → contexte figé → transcription manuelle ou OCR local consenti → revue → copie externe explicite. Pas de popup à chaque geste ; erreurs proches du sélecteur, Échap/Undo, navigation clavier, focus visible, 1366×768 et DPI 200 % à éprouver sur Windows. Aucun téléchargement/réseau sans accord, pas de promesse OCR sans modèle/licence/version/hash ; CPU manuel garanti, RTX 8 Go optionnelle seulement après profilage. Temps de sélection, décodage et latence doivent être **mesurés** sur corpus synthétique avec p50/p95 et pics mémoire, sans seuil inventé.

Micro-lots futurs : (1) fixtures multi-source V1 synthétiques et tests négatifs ; (2) port explicite lecture seule et enveloppe SHA construite au snapshot ; (3) mapping ROI et invalidation de génération ; (4) intégration Tk/Undo/erreurs ; (5) tests Windows, concurrence, fermeture et audit hostile. **Aucun micro-lot codé ici.** Les quatre exports demeurent distincts : PNG Print Then Cut, SVG Basic Cut, SVG CUT multicouche, SVG d'édition. Aucun statut Design Space ou coupe physique ne découle de ces tests.

## Contrat qualité R3 : 25 axes
01 héritage 24 lots : inchangé, audit global ouvert ; 02 141 exigences : B13/G9 ciblés, G6 non satisfait ; 03 140 tickets : pas de renumérotation ; 04 80 UX : B13 seulement, 0 certification nouvelle ; 05 437 scénarios : pas de PASS déduit ; 06 preuve code/CI/Windows : sources lues, nouveaux tests NOT_RUN ; 07 V1/SHA/CAS/masque : préservés ; 08 quatre exports : séparés ; 09 opérations machine : N/A, aucune opération émise ; 10 Express UX : parcours source décrit ; 11 gestes/Undo : ROI locale ; 12 accessibilité : tests Windows à faire ; 13 annulation/stale/crash : cas définis ; 14 IA : consentement/fallback ; 15 raster/alpha : N/A à OCR, aucune transformation ; 16 vectorisation : N/A, pas de chemin produit ; 17 fabrication/DS : N/A, pas de prévol prétendu ; 18 Smart Delivery : N/A, aucune archive ZIP livrée ; 19 bibliothèque/batch : N/A, aucun lot modifié ; 20 performances : protocole sans chiffres inventés ; 21 sécurité/chemins/quotas : refus et limites conservés ; 22 licences/confidentialité : OCR local facultatif, provenance ; 23 alternatives/dépendances : port minimal et refus de second store ; 24 TDD/DoD/rollback : matrice et micro-lots ; 25 contre-expertise/promotion : NON ADOPTÉ, revue propriétaire requise pour schéma ou dépendance.

**Statuts** : CANDIDAT/AUDITÉ documentaire seulement ; SPÉCIFIÉ partiel, REVU indépendant non démontré ; CODE_BRANCHE, CODE_MAIN, FONCTION_WINDOWS_EXPOSÉE, TEST_UNITÉ_PASS_NON_SKIP, TEST_UI_WINDOWS_PASS, GPU_PASS, DESIGN_SPACE_PASS, COUPE_PHYSIQUE_PASS : **NOT_RUN / NON DÉMONTRÉ pour cette proposition**. Les tests historiques sont inspectés, non exécutés.

**Prochaine action unique Q04V** : lire le fixture `engine/tests/test_project_recovery_g14.py` et les contrats `SourceAsset/LoadedProject` au blob exact, puis spécifier un fixture V1 multi-PNG valide (deux IDs et SHA indépendants) sans toucher au writer.
