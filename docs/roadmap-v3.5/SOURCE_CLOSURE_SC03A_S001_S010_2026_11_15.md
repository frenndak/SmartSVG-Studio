# SOURCE_CLOSURE SC-03A — exigences S-001 à S-010 : revue contradictoire bornée (15/11/2026)

**Autorité : candidate documentaire seulement.** Base observée main `0692f804ad21bd775cd0269dd92dc6e2b1cea01f`, branche candidate avant publication `cb8b7ac909e704d0387b3ecea6bfab13979e0b1a`. Sources : `docs/ROADMAP_HERITAGE_v3_3.md` (héritage V3.2 intégral), `docs/roadmap-v3.4/23_TRACEABILITE_BACKLOG.md`, `docs/roadmap-v3.5/COVERAGE_V34_TO_V35.md`, SC-02F1/F2. Ce document **n'atteste pas** la confrontation intégrale des 141 critères : il identifie dix obligations et leurs sous-critères sensibles à vérifier dans les sources maîtresses avant clôture.

| ID | Propriétaire V34 explicite (planification) | Verdict V3.5 et risque de perte | Oracle de clôture à conserver |
|---|---|---|---|
| S-001 | 001,003,002 | GARDER : archive gelée V21.14.1 et corpus ne sont pas remplaçables par une simple capture main | Empreinte du gel et droits corpus vérifiés indépendamment ; jamais modifier l'archive historique |
| S-002 | 005,129 | RAFFINER : formulation historique « trois contrats » n'autorise pas à fusionner les quatre sorties actuelles | PNG PTC, SVG Basic Cut, SVG CUT multicouche et SVG édition : quatre oracles distincts, unités/provenance/QA |
| S-003 | 032,132,010,041,048,053,059,060,063,079,087 | RAFFINER : projet V1 canonique, V2 migration explicite, aucune sérialisation implicite de preview | Save/reopen/Undo float32, SHA/CAS et identité des sources ; CP2 receipt ≠ CAS V1 |
| S-004 | 041,043,006 | GARDER : Express-first sans disparition des IDs et capacités Expert | Navigation novice + accès Expert, test clavier, 1366×768 et DPI 200 %, pas de second projet/store |
| S-005 | 078,080,077,084,092 | GARDER : une proposition de modèles n'est pas un benchmark RTX 3070 8 Go | Versions/licences/hashes, VRAM mesurée, OOM, fallback CPU/manuel, consentement explicite |
| S-006 | 068,085,094 | GARDER : neuf références annotées ne sont pas neuf scores PASS | Manifest droits et vérité terrain versionnée ; protocole inter-annotateur et provenance |
| S-007 | 069,110,007,071,082 | RAFFINER : confiance géométrique ne prouve pas le bon sujet sémantique | Mauvais objet/occlusion/accessoire, correction locale, identité persistante, validation humaine |
| S-008 | 132,133,035,038,062,102 | RAFFINER : démo de pinceau ≠ round-trip frontend | Brush, Undo/Redo, fermeture/reprise, masque float32, preuve UI Windows et aucun double commit |
| S-009 | 101,129,090 | GARDER : « Cricut compatible » générique est interdit | Preuves par format et version Design Space ; géométrie locale séparée de l'import et de la coupe |
| S-010 | 124 | GARDER : CI et rendu SVG ne certifient pas la découpe Explore 5 | Matériau/lame/tapis/DS version, dimensions et mesures physiques datées ; UNKNOWN reste UNKNOWN |

## Contre-expertise et corrections contractuelles

1. **Conflit historique 3 vs 4 exports (S-002)** : conserver la provenance des trois contrats historiques, mais imposer quatre rôles actuels distincts. Ne pas annoncer que l'ancienne recette à trois sorties couvre automatiquement le quatrième SVG CUT multicouche. Une table critère source → rôle actuel est exigée dans SC-03B avant certification.
2. **S-003 vs CP2** : un receipt de publication durable ne peut être inféré d'un digest CAS ou d'une réponse UI. L'interface future doit exposer `project_revision`, `expected_sha`, `command_id`, `epoch` et résultat de publication avec codes d'erreur distincts ; toute évolution de schéma demeure soumise à la procédure propriétaire.
3. **S-009/S-010** : séparer `PREVOL_LOCAL`, `DESIGN_SPACE_IMPORT` et `COUPE_PHYSIQUE`. Un SVG bien formé n'est pas une coupe certifiée ; l'absence d'essai ne devient jamais PASS.
4. **S-005/S-007** : IA refusée, absente ou OOM ne doit ni télécharger ni écraser le sujet. Préserver une retouche manuelle réversible et une proposition IA tardive isolée de la révision active.

## Scénarios négatifs minimaux de cette tranche (spécifiés, NON EXÉCUTÉS)

- Réouverture d'un V1 avec masque modifié et SHA périmé : conflit explicite, aucune mutation ni perte d'original.
- Import Design Space échouant malgré un prévol XML local réussi : statut DS FAIL indépendant, aucune certification de coupe.
- Modèle local sans licence vérifiable ou dépassant la VRAM : refus/repli manuel, zéro téléchargement et zéro écriture silencieuse.
- Sélection du mauvais sujet avec confiance élevée : correction humaine et identité conservée ; ne pas traiter la confiance comme validation.
- Coupure après publication mais avant accusé : reprise inspectable, pas de second commit par retry.

## Contrôle qualité R3 — 25 axes

01–05 : héritages 24/141/140/80/437 inchangés, **non certifiés** par cette tranche ; 06 : main SHA observé, tests NOT_RUN ; 07–09 : frontières CAS, exports et machine précisées ; 10–13 : UX, Undo, accessibilité et récupération couverts par oracles futurs ; 14–17 : IA/raster/vecteur/fabrique à conserver, vérification détaillée des autres critères hors périmètre SC-03A ; 18–19 : Smart Delivery et opportunités NON APPLICABLE à ces dix décisions sauf dépendance aux exporteurs, sans réouverture de leur clôture ; 20 : aucun chiffre de performance revendiqué ; 21 : droits corpus et licences IA ; 22 : branche candidate uniquement, aucun code/merge ; 23 : pas de nouveau moteur ou ticket ; 24 : revue globale/promotion encore ouvertes ; 25 : aucun critère supprimé, seulement un rapprochement partiel.

**Preuves :** lecture documentaire uniquement ; nouveaux tests auto/UI Windows/GPU/Design Space/physiques = NOT_RUN. **Reste ouvert :** lecture et citation du critère intégral de chaque source V3.3, puis DoD des tickets V34 correspondants et 131 autres exigences. La correspondance ci-dessus ne constitue pas encore la clôture SC-03.

**Prochaine tranche unique : SC-03B** — rapprocher littéralement les critères intégraux S-001–S-010 et les DoD des tickets propriétaires, documenter les écarts et les décisions, puis continuer S-011–S-020.
