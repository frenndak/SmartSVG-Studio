# COV-06 — Raccordement explicite des scénarios V3.4 lots 09–12

**13 novembre 2026 — candidat, non normatif.** Extraction des plages de tests des micro-tickets V3.4, et non qualification technique. Source : `09_PLANIFICATEUR_SECURISÉ.md` blob `52e61d658d47570edffb662fc4f8983cf1208512`, `10_ANALYSE_VISUELLE.md` blob `9c0b0648a6b3c2790813ff59136fdb0a88df89c0`, `11_MODELES_IA_LOCAUX.md` blob `9a169e3c7db786d6dca1123397b13fcadde6a80e`, `12_RASTER_PIPELINE.md` blob `30424177571a1e5c627cbdb0630c07c63ba344e0`. Lignes originales dans [l'inventaire](SCENARIOS_V34_09_16.md). Les plages `T01..30` des tickets de corpus sont conservées comme liens explicites mais **ne démontrent pas la couverture sémantique détaillée**.

## Résultat vérifiable

**120/120** scénarios ont au moins une référence textuelle à une plage de tests de micro-ticket ; **0** sans propriétaire textuel dans ces quatre lots. Cela ne signifie ni 120 critères entièrement vérifiés ni 120 tests PASS. Les tickets de corpus `V34-067/077/085/094` sont transversaux : ne pas les utiliser comme substitut au propriétaire fonctionnel. Le premier lot exigeant une revue contradictoire reste le lot 09 (planificateur, consentement et exécution) ; le premier problème transversal ouvert reste les 10 exigences G6/G9.

| Scénario | Tickets citant explicitement son numéro/plage | Nature du lien |
|---|---|---|
| T-V34-09-01 | V34-059, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-02 | V34-059, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-03 | V34-059, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-04 | V34-059, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-05 | V34-060, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-06 | V34-060, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-07 | V34-060, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-08 | V34-060, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-09 | V34-061, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-10 | V34-061, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-11 | V34-061, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-12 | V34-061, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-13 | V34-062, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-14 | V34-062, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-15 | V34-062, V34-065, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-16 | V34-062, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-17 | V34-063, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-18 | V34-063, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-19 | V34-063, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-20 | V34-063, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-21 | V34-064, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-22 | V34-064, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-23 | V34-064, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-24 | V34-064, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-25 | V34-065, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-26 | V34-065, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-27 | V34-066, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-28 | V34-066, V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-29 | V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-09-30 | V34-067 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-01 | V34-068, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-02 | V34-068, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-03 | V34-068, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-04 | V34-068, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-05 | V34-069, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-06 | V34-069, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-07 | V34-069, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-08 | V34-069, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-09 | V34-070, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-10 | V34-070, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-11 | V34-070, V34-074, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-12 | V34-070, V34-074, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-13 | V34-070, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-14 | V34-070, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-15 | V34-071, V34-073, V34-076, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-16 | V34-071, V34-075, V34-076, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-17 | V34-071, V34-072, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-18 | V34-072, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-19 | V34-072, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-20 | V34-073, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-21 | V34-074, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-22 | V34-072, V34-074, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-23 | V34-072, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-24 | V34-074, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-25 | V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-26 | V34-075, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-27 | V34-075, V34-076, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-28 | V34-075, V34-076, V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-29 | V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-10-30 | V34-077 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-01 | V34-078, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-02 | V34-078, V34-085, V34-086 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-03 | V34-078, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-04 | V34-078, V34-085, V34-086 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-05 | V34-078, V34-085, V34-086 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-06 | V34-078, V34-083, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-07 | V34-079, V34-083, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-08 | V34-079, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-09 | V34-079, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-10 | V34-079, V34-085, V34-086 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-11 | V34-079, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-12 | V34-079, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-13 | V34-079, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-14 | V34-079, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-15 | V34-080, V34-085, V34-086 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-16 | V34-080, V34-085, V34-086 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-17 | V34-080, V34-082, V34-085, V34-086 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-18 | V34-080, V34-082, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-19 | V34-081, V34-084, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-20 | V34-081, V34-084, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-21 | V34-081, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-22 | V34-081, V34-082, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-23 | V34-082, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-24 | V34-082, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-25 | V34-083, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-26 | V34-083, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-27 | V34-084, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-28 | V34-084, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-29 | V34-083, V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-11-30 | V34-085 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-01 | V34-087, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-02 | V34-087, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-03 | V34-087, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-04 | V34-087, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-05 | V34-087, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-06 | V34-088, V34-094, V34-095 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-07 | V34-088, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-08 | V34-088, V34-091, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-09 | V34-088, V34-090, V34-094, V34-095 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-10 | V34-088, V34-090, V34-091, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-11 | V34-089, V34-094, V34-095 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-12 | V34-089, V34-091, V34-094, V34-095 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-13 | V34-089, V34-091, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-14 | V34-092, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-15 | V34-092, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-16 | V34-088, V34-089, V34-092, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-17 | V34-088, V34-090, V34-094, V34-095 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-18 | V34-088, V34-090, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-19 | V34-088, V34-090, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-20 | V34-088, V34-090, V34-094, V34-095 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-21 | V34-093, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-22 | V34-093, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-23 | V34-093, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-24 | V34-093, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-25 | V34-090, V34-093, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-26 | V34-090, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-27 | V34-091, V34-094, V34-095 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-28 | V34-090, V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-29 | V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |
| T-V34-12-30 | V34-094 | EXPLICITE_SOURCE (plage de tests du micro-ticket) |

## Contre-expertise et contrats de validation

- **Planificateur 09 :** parser fermé, refus shell/HTTP, prévisualisation non mutante, consentement one-shot CAS/epoch et receipt idempotent. Contre-avis : un plan généré par IA ne constitue jamais une commande autorisée. Les 4 exports restent PNG PTC, SVG Basic Cut, SVG CUT multicouche, SVG éditable.
- **Vision 10 :** EXIF/ICC/ROI, masques float32, identités stables, 12/24/50 sujets sans dépassement du format V1 ; fallback manuel sans réseau. Contre-avis : un index de masque ou une vignette PNG ne constitue pas un Subject persistant.
- **Modèles 11 :** installation explicite avec licence/version/hash, quarantaine, OOM et rollback, aucun poids ni code distant activé silencieusement. Contre-avis : un modèle présent ne prouve pas la qualité d'inférence ou la compatibilité GPU.
- **Raster 12 :** préserver source/alpha/cut digest, ICC/EXIF, mm et PPI, prévol et publication atomique. Contre-avis : une interpolation 600 ppi n'invente pas des détails natifs ; le PNG PTC ne certifie pas une coupe physique.
- **Tests négatifs prioritaires NOT_RUN :** (1) JSON dupliqué/NaN/commande interdite → 0 mutation ; (2) SHA/epoch obsolète après preview → refus ; (3) masque NaN ou ROI hors bornes → refus ; (4) modèle hash invalide/redirect hostile → quarantaine ; (5) disque plein, crash, ACK perdu ou OOM → recovery sans double écriture ; (6) profil machine UNKNOWN → aucune qualification de fabrication.
- **Axes de preuve :** extraction documentaire = réalisée ; tests unitaires non-skip, Windows UI à 1366×768/DPI 200 %, RTX 8 Go, Design Space versionné et coupe physique = **NOT_RUN pour ce travail**. UX débutant/expert, Undo/Redo et reprise demeurent exigences des futures fiches, non certifiées ici. Performance p50/p95 = protocole à instrumenter, aucune mesure attribuée.
- **Contrat 25 points :** 01–05 conservation et liens contrôlés localement, 06/20 statut des preuves honnête ; 07–19/21–24 invariants et gates préservés mais **pas certifiés** par cette extraction ; 25 aucune réduction de mission. Les axes matériel/IA/UI non directement exécutés par une matrice documentaire sont N/A **pour l'exécution**, pas pour le produit.

**Décision :** RACCORDER les 120 scénarios sans nouveau ticket ; poursuivre les contrôles sémantiques indépendants et ne pas promouvoir V3.5. **Prochaine action unique :** COV-07, extraire les liens source des scénarios lots 13–16 et qualifier les exceptions, sans recopier leurs textes historiques.
