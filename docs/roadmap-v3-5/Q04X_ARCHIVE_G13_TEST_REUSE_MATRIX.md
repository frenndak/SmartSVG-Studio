# V35-Q04X — Matrice de réemploi réelle des tests archive V1 (Q04W)

Date 2026-11-15. **CANDIDAT documentaire, V3.4 ACTIVE. Aucun test exécuté, aucune modification du code.**

## Preuve et correction
Le fichier de tests existe réellement sous `engine/tests/test_project_archive_g13.py` (blob `8c9ff514b3ec472961c39c671181e559f5e65739`, lu sur ref `main`), avec **53 méthodes `test_*`** ; `tests/test_g13_project_archive.py` (blob `b37c919fbff035ca121700e4a00f0311906dd4c3`) les charge via `load_tests`. Le chemin supposé Q04W `engine/tests/test_project_archive.py` était incorrect. Ne pas transformer existence de tests en PASS CI. `main@HEAD` NON_VÉRIFIÉ : ref de lecture et blob ne prouvent pas SHA de tête.

## Confrontation Q04W aux assertions existantes
| Oracle Q04W | Test réel précis et assertion inspectée | Verdict de réemploi |
|---|---|---|
| P1 deux PNG A/B dont B sans sujet | `test_exact_save_close_open_15_operations_and_3_undo` vérifie `load_project == initial` mais **une seule source** | PARTIEL : nouveau test deux sources obligatoire |
| P2 SHA et octets distincts A/B | `test_exact_save_close_open_15_operations_and_3_undo` vérifie SHA du ZIP, pas deux SHA source | MANQUANT |
| P3 masque/sujet A conservés, B orpheline | `test_g12_valid_mask_ids_roundtrip_with_portable_zip_members`, `test_invalid_mask_reference_rejected_before_disk_write` portent sur liens, pas sur B orpheline | PARTIEL |
| P4 deux chemins dans manifeste | `test_distinct_sources_cannot_share_one_archive_resource` rejette un même chemin pour deux IDs ; pas de manifeste A/B distinct | PARTIEL |
| P5 sélection historique A, B via port explicite | Aucun oracle d'interface dans le fichier archive ; `tests/test_v34_native_source_preview.py` à vérifier séparément | MANQUANT |
| N1 IDs dupliqués | Aucun cas à deux IDs identiques démontré par les assertions examinées | MANQUANT |
| N2 chemin ZIP A/B identique | `test_distinct_sources_cannot_share_one_archive_resource` exige `RESOURCE_PATH_COLLISION` et absence de fichier | DIRECT (même hash/dimensions) |
| N3/N4 source_paths manquant ou supplémentaire | `test_untrusted_resource_maps_fail_as_archive_errors` teste types non-dict, pas clés manquantes/supplémentaires | PARTIEL |
| N5 ressources absentes/en trop | `test_extra_unmanifested_entry_rejected`, `test_modified_asset_is_rejected_against_manifest` testent ZIP modifié ; pas cas B | PARTIEL |
| N6 SHA B falsifié | `test_bad_write_never_destroys_last_good_snapshot` teste masque incohérent et rollback ; pas source B | PARTIEL |
| N7 dimensions B fausses | `test_wrong_source_size_blocks_save` exige `SOURCE_PIXEL_DIMENSIONS_MISMATCH` pour source unique | DIRECT pour règle, extension B requise |
| N8 mode B faux | `test_png_source_color_mode_rejects_mismatched_metadata` teste mode source unique | DIRECT pour règle, extension B requise |
| N9 PNG B corrompu malgré SHA recalculé | `test_valid_crc_but_invalid_source_png_scanline_filter_is_rejected`, `test_png_chunk_structure_rejected_despite_valid_crc_and_sha` | DIRECT pour règle, extension B requise |
| N10 alias NFC/casse A/B | `test_unicode_normalization_alias_of_source_is_rejected_before_overwrite` crée deux sources alias et vérifie `CASE_COLLIDING_RESOURCE_PATHS` + rollback | DIRECT |
| N11 chemin sous fichier metadata | `test_archive_resource_paths_cannot_shadow_files_or_metadata` teste `manifest.json/detail.svg`, et rollback | DIRECT pour conflit parent ; cas source B reste à créer |
| N12/N13 quotas membre/total | `test_archive_bomb_exceeds_member_budget` teste budget membre, pas preuve spécifique B ni total deux sources | PARTIEL |
| N14/N15/N16/N17 source inconnue, stale, concurrence, annulation OCR | Aucun port OCR multi-source dans tests archive | MANQUANT, tests service/Windows futurs |
| N18 disque plein avant publication | `test_fsync_failure_preserves_existing_project_exactly` injecte échec fsync et compare octets ; disque plein exact non simulé | PARTIEL |
| N19 crash après publication | `test_readback_precedes_atomic_overwrite` vérifie ordre readback/publish ; reprise crash distincte | PARTIEL |
| N20 TextNode V1 interdit | `test_future_schema_must_not_be_silently_migrated` teste version future, pas écriture TextNode | MANQUANT |

**Contre-expertise hostile :** `test_distinct_sources_cannot_share_one_archive_resource` ne démontre **pas** le round-trip de deux chemins valides. `test_exact_save_close_open_15_operations_and_3_undo` ne démontre **pas** deux sources. Le test Unicode couvre réellement deux IDs, mais uniquement leur collision. Ne pas gonfler les 437 scénarios V3.4 avec les 25 oracles candidats Q04W.

## Décision et micro-lots TDD proposés
**RACCORDER/AMÉLIORER P1**, sans nouveau writer/store/schéma V1. M1 ajouter au fichier G13 une fixture synthétique A RGBA 8×6, B RGBA 11×7, SHA et chemins distincts, seul A lié à masque L8 et sujet ; tester P1–P4 et absence de sujet B, ordre et octets après save/load. M2 ajouter N1/N3/N4/N5/N6/N12/N13 en isolation, avec code d'erreur observé plutôt que supposé. M3 source explicite B en lecture seule, identité `project_sha/source_id/source_sha/generation`, refuser fallback A. M4 rejets stale, annulation, Undo et changement de source pendant worker OCR. M5 tests Windows Tk réels du port OCR et focus/DPI. Chaque étape doit produire test non-skip exact SHA, rollback et audit des consommateurs ; aucune implémentation autorisée par cette tâche.

Novice : choix A/B explicite, miniatures et retour d'erreur compréhensible ; expert : SHA, ID, historique et provenance. Aucune IA, aucun téléchargement, aucun réseau requis pour l'archive ; OCR reste facultatif et consenti, repli manuel. Mesurer p50/p95 sauvegarde, mémoire et latence UI sur fixtures autorisées, pas de chiffres fictifs. Préserver les **quatre sorties distinctes** PNG PTC, SVG Basic Cut, SVG CUT multicouche, SVG éditable : elles sont hors périmètre des tests archive, tout comme certification Design Space/Explore 5 et coupe physique.

## Contrôle R3 des 25 axes
01–05 inventaires historiques inchangés (24/141/140/80/437), couverture sémantique non certifiée ; 06 preuves de code/test séparées, tests NOT_RUN ; 07 projet V1, CAS, writer, masques intacts ; 08–09 quatre exports/machine N/A à archive, aucune confusion ; 10–12 UX A/B et Windows futurs, accessibilité 1366×768/DPI 200 %, focus/clavier, contraste/motion réduite ; 13 concurrence/annulation/crash et rollback M2–M5 ; 14 IA optionnelle, CPU manuel ; 15 PNG modes/SHA/CRC ; 16 vecteur N/A ; 17 batch/CSV N/A ; 18 Smart Delivery N/A, ZIP projet distinct ; 19 pas de doublon opportunité ; 20 mesures futures seulement ; 21 fixtures synthétiques, chemins ZIP hostiles et confidentialité ; 22 branche docs seule, WIP producteur intact ; 23 réemploi G13 sans nouveau store ; 24 revue propriétaire/CI/promotion restent ouvertes ; 25 25/25 axes explicités. **Statut : CANDIDAT / AUDITÉ, pas REVU, pas CODE_MAIN ajouté, tests nouveaux NOT_RUN.**

**Prochaine action UNIQUE Q04Y :** lire précisément `test_archive_bomb_exceeds_member_budget` et les branches `_validate_bundle` sur main pour distinguer quotas membre/total, ordre des erreurs N3/N4/N12/N13, et rédiger les oracles exacts avant TDD.
