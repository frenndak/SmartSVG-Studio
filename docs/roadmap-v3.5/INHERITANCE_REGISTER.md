# SmartSVG V3.5 — Registre initial d'héritage intégral V3.4 (photographie, pas une certification produit)

**Datation :** 12 novembre 2026. **Sources figées par commit :** V3.4 [main@aa0ff9e7](https://github.com/frenndak/SmartSVG-Studio/commit/aa0ff9e7d0c53dba3fdc429c02c6198736cfe935), dont `docs/roadmap-v3.4/23_TRACEABILITE_BACKLOG.md` et `README.md`; audit UX [issue #134](https://github.com/frenndak/SmartSVG-Studio/issues/134). Les lignes ci-dessous sont recopiées de ces sources, sans corriger silencieusement des formulations ou transformer des mentions de tests proposés en résultats.

**Contrôle de complétude appliqué lors de la création de cette photographie :**
- **24 lots V3.4** extraits des liens README : **24 lignes uniques** ;
- **141 exigences historiques** extraites du tableau « Exigence → ticket V34 → recette de référence » : **141 IDs uniques** ;
- **140 tickets V34** extraits de l'index inverse : **140 IDs uniques** ;
- **80 capacités UX** extraites des cases de #134 : **80 IDs uniques**, distribution A16/B14/C18/D12/E20.
- **437 tests/scénarios de conception** : **chiffre déclaré par V3.4**, PAS encore inventorié ID par ID dans ce fichier : leur énumération et leur traçabilité constituent un gate V3.5 **OUVERT**.
- **Aucun de ces nombres ne prouve** que les 24 lots ont été réécrits/contre-expertisés en V3.5, que les 80 UX sont codables ou que le produit existe intégralement en Windows.

## 1. Inventaire original des 24 lots de conception V3.4

| Lot V3.4 | Fichier source (V3.4) | Traitement V3.5 |
|---|---|---|
| 01 | [01_BASELINE_AUDIT.md](../roadmap-v3.4/01_BASELINE_AUDIT.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 02 | [02_VISION_PARCOURS.md](../roadmap-v3.4/02_VISION_PARCOURS.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 03 | [03_ARCHITECTURE_ADR.md](../roadmap-v3.4/03_ARCHITECTURE_ADR.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 04 | [04_MIGRATION_AUTONOME.md](../roadmap-v3.4/04_MIGRATION_AUTONOME.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 05 | [05_PROJECT_SCHEMA.md](../roadmap-v3.4/05_PROJECT_SCHEMA.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 06 | [06_COMMAND_BUS.md](../roadmap-v3.4/06_COMMAND_BUS.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 07 | [07_UX_EXPRESS_NAVIGATION.md](../roadmap-v3.4/07_UX_EXPRESS_NAVIGATION.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 08 | [08_ASSISTANT_CONTEXTUEL.md](../roadmap-v3.4/08_ASSISTANT_CONTEXTUEL.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 09 | [09_PLANIFICATEUR_SECURISÉ.md](../roadmap-v3.4/09_PLANIFICATEUR_SECURISÉ.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 10 | [10_ANALYSE_VISUELLE.md](../roadmap-v3.4/10_ANALYSE_VISUELLE.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 11 | [11_MODELES_IA_LOCAUX.md](../roadmap-v3.4/11_MODELES_IA_LOCAUX.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 12 | [12_RASTER_PIPELINE.md](../roadmap-v3.4/12_RASTER_PIPELINE.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 13 | [13_VECTORISATION_SVG.md](../roadmap-v3.4/13_VECTORISATION_SVG.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 14 | [14_LANGAGE_FABRICATION.md](../roadmap-v3.4/14_LANGAGE_FABRICATION.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 15 | [15_PROFILS_EXPLORE5.md](../roadmap-v3.4/15_PROFILS_EXPLORE5.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 16 | [16_PATRONS_PARAMETRIQUES.md](../roadmap-v3.4/16_PATRONS_PARAMETRIQUES.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 17 | [17_EXPORTS_DESIGNSPACE.md](../roadmap-v3.4/17_EXPORTS_DESIGNSPACE.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 18 | [18_ATELIER_GRAPHIQUE.md](../roadmap-v3.4/18_ATELIER_GRAPHIQUE.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 19 | [19_PLANCHES_NESTING.md](../roadmap-v3.4/19_PLANCHES_NESTING.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 20 | [20_BIBLIOTHEQUE_VARIANTES_CSV.md](../roadmap-v3.4/20_BIBLIOTHEQUE_VARIANTES_CSV.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 21 | [21_WINDOWS_OFFLINE_RECOVERY.md](../roadmap-v3.4/21_WINDOWS_OFFLINE_RECOVERY.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 22 | [22_VALIDATION_CORPUS_PREUVES.md](../roadmap-v3.4/22_VALIDATION_CORPUS_PREUVES.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 23 | [23_TRACEABILITE_BACKLOG.md](../roadmap-v3.4/23_TRACEABILITE_BACKLOG.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |
| 24 | [24_CONTRE_EXPERTISE_PASSATION.md](../roadmap-v3.4/24_CONTRE_EXPERTISE_PASSATION.md) | SOURCE CONSERVÉE ; delta V3.5 à spécifier et valider |

## 2. Photographie des 141 exigences historiques (texte du tableau V3.4)

**Autorité des critères intégraux :** `docs/ROADMAP_MASTER_v3_3.md`, `docs/ROADMAP_TRACEABILITY_v3_3.md`, `docs/ROADMAP_HERITAGE_v3_3.md`. Ce tableau est seulement l'**abrégé de traçabilité** du document V3.4 et doit être complété par les critères historiques, jamais utilisé pour les abréger.

| Exigence | Intitulé historique abrégé | Tickets / propriétaire proposé | Test prévu de référence | Statut / justification |
|---|---|---|---|---|
| S-001 | G0-G9 (cf. V3.2) · Geler archive V21.14.1 et corpus | V34-001, V34-003, V34-002 | T-V34-22-02 | Lien de planification, preuve non exécutée |
| S-002 | G0-G9 (cf. V3.2) · Spécifier les trois contrats de sortie | V34-005, V34-129 | T-V34-22-01 | Lien de planification, preuve non exécutée |
| S-003 | G0-G9 (cf. V3.2) · Définir modèle de projet/retouches sérialisables | V34-032, V34-132, V34-010, V34-041, V34-048, V34-053, V34-059, V34-060, V34-063, V34-079, V34-087 | T-V34-22-02 | Lien de planification, preuve non exécutée |
| S-004 | G0-G9 (cf. V3.2) · Réduire la complexité visible, conserver anciens IDs | V34-041, V34-043, V34-006 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-005 | G0-G9 (cf. V3.2) · Test réel RMBG/SAM2/BiRefNet RTX 3070 | V34-078, V34-080, V34-077, V34-084, V34-092 | T-V34-22-12 | Lien de planification, preuve non exécutée |
| S-006 | G0-G9 (cf. V3.2) · Créer masques de référence des neuf images | V34-068, V34-085, V34-094 | T-V34-22-12 | Lien de planification, preuve non exécutée |
| S-007 | G0-G9 (cf. V3.2) · Validation sémantique du sujet désiré | V34-069, V34-110, V34-007, V34-071, V34-082 | T-V34-22-05 | Lien de planification, preuve non exécutée |
| S-008 | G0-G9 (cf. V3.2) · Éditeur pinceaux/undo/reload vérifié sur frontend | V34-132, V34-133, V34-035, V34-038, V34-062, V34-102 | T-V34-22-04 | Lien de planification, preuve non exécutée |
| S-009 | G0-G9 (cf. V3.2) · Assurance qualité Cricut par format | V34-101, V34-129, V34-090 | T-V34-22-01 | Lien de planification, preuve non exécutée |
| S-010 | G0-G9 (cf. V3.2) · Couper physiquement des exemplaires Explore 5 | V34-124 | T-V34-22-07 | Lien de planification, preuve non exécutée |
| S-011 | G0-G9 (cf. V3.2) · Fidélité SVG multicouche et analyse des formes | V34-098, V34-099, V34-103 | T-V34-22-01 | Lien de planification, preuve non exécutée |
| S-012 | G0-G9 (cf. V3.2) · Chemins SVG utilisables avec matériau choisi | V34-106, V34-109, V34-008, V34-012, V34-107, V34-111, V34-113, V34-120, V34-127 | T-V34-22-08 | Lien de planification, preuve non exécutée |
| S-013 | G0-G9 (cf. V3.2) · Écran Express unifié | V34-043, V34-051, V34-091 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-014 | G0-G9 (cf. V3.2) · Segmentation objets et fragments associés | V34-073 | T-V34-22-12 | Lien de planification, preuve non exécutée |
| S-015 | G0-G9 (cf. V3.2) · Nettoyage des halos / découpe et offset | V34-088, V34-095, V34-076 | T-V34-22-05 | Lien de planification, preuve non exécutée |
| S-016 | G0-G9 (cf. V3.2) · HD conditionnelle + diagnostic d'artefacts | V34-089 | T-V34-22-05 | Lien de planification, preuve non exécutée |
| S-017 | G0-G9 (cf. V3.2) · Packaging « projet SmartSVG » | V34-025, V34-137, V34-031, V34-131 | T-V34-22-02 | Lien de planification, preuve non exécutée |
| S-018 | G0-G9 (cf. V3.2) · Queue/batch/cache avec reprise | V34-074, V34-135, V34-070, V34-081, V34-093, V34-104 | T-V34-22-11 | Lien de planification, preuve non exécutée |
| S-019 | G0-G9 (cf. V3.2) · Benchmark Canva/Design Space sur corpus identique | V34-003 | T-V34-22-07 | Lien partiel : benchmark/score V3.3 reste à tester |
| S-020 | G0-G9 (cf. V3.2) · Papier découpé multicouche / dioramas | V34-126 | T-V34-22-08 | Lien de planification, preuve non exécutée |
| S-021 | G0-G9 (cf. V3.2) · OCR et gestion du texte sur affiches | V3.3 G6/G9 (sans ticket V34) | Test V3.3 à relier | V3.3 conservée ; aucune nouvelle obligation V34 |
| S-022 | G0-G9 (cf. V3.2) · App autonome hors ComfyUI, si justifiée | V34-019, V34-139, V34-004, V34-011, V34-014, V34-017, V34-020, V34-024, V34-054, V34-064 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-023 | Identité de sujet stable | V34-028, V34-132, V34-025, V34-044, V34-061, V34-072, V34-096, V34-115 | T-V34-22-02 | Lien de planification, preuve non exécutée |
| S-024 | Projet `.smartsvg` v1 | V34-025, V34-136 | T-V34-22-02 | Lien de planification, preuve non exécutée |
| S-025 | Écran Express métier | V34-043, V34-083 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-026 | Historique non destructif UI | V34-033, V34-133, V34-029 | T-V34-22-04 | Lien de planification, preuve non exécutée |
| S-027 | Contrôle GPU réel | V34-074, V34-080, V34-016, V34-036, V34-039, V34-047 | T-V34-22-12 | Lien de planification, preuve non exécutée |
| S-028 | Groupes sujet + accessoires | V34-073 | T-V34-22-04 | Lien de planification, preuve non exécutée |
| S-029 | Contrat PNG/alpha Cricut | V34-087, V34-129, V34-122 | T-V34-22-01 | Lien de planification, preuve non exécutée |
| S-030 | Contrat SVG Basic Cut | V34-097, V34-129, V34-100, V34-108, V34-128 | T-V34-22-01 | Lien de planification, preuve non exécutée |
| S-031 | Matrice d'essais Explore 5 | V34-124 | T-V34-22-07 | Lien de planification, preuve non exécutée |
| S-032 | Export SVG édition vs fabrication | V34-098, V34-129, V34-112 | T-V34-22-01 | Lien de planification, preuve non exécutée |
| S-033 | Préservation traits et petites régions | V34-099 | T-V34-22-01 | Lien de planification, preuve non exécutée |
| S-034 | Simplification de Bézier | V34-099 | T-V34-22-01 | Lien de planification, preuve non exécutée |
| S-035 | Canevas objets/textes | V34-133 | T-V34-22-04 | Lien de planification, preuve non exécutée |
| S-036 | Fonts et conversion textes → tracés | V3.3 G6/G9 (sans ticket V34) | Test V3.3 à relier | V3.3 conservée ; aucune nouvelle obligation V34 |
| S-037 | Gabarits métiers | V3.3 G6/G9 (sans ticket V34) | Test V3.3 à relier | V3.3 conservée ; aucune nouvelle obligation V34 |
| S-038 | Job manager et checkpoints | V34-074, V34-135, V34-138 | T-V34-22-11 | Lien de planification, preuve non exécutée |
| S-039 | Variables CSV | V34-138 | T-V34-22-13 | Lien de planification, preuve non exécutée |
| S-040 | Imposition mesurable | V34-134 | T-V34-22-05 | Lien de planification, preuve non exécutée |
| S-041 | Bibliothèque locale | V34-136 | T-V34-22-13 | Lien de planification, preuve non exécutée |
| S-042 | Audit de sécurité des projets | V34-031, V34-139, V34-086 | T-V34-22-03 | Lien de planification, preuve non exécutée |
| S-043 | Benchmark Canva/Design Space | V34-003 | T-V34-22-07 | Lien partiel : benchmark/score V3.3 reste à tester |
| S-044 | Dioramas multi-plans | V3.3 G6/G9 (sans ticket V34) | Test V3.3 à relier | V3.3 conservée ; aucune nouvelle obligation V34 |
| S-045 | Vinyle multi-couleur | V34-100, V34-112 | T-V34-22-01 | Lien de planification, preuve non exécutée |
| S-046 | Application autonome | V34-019, V34-139 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-047 | OCR texte de couverture | V3.3 G6/G9 (sans ticket V34) | Test V3.3 à relier | V3.3 conservée ; aucune nouvelle obligation V34 |
| S-048 | Upscale IA artistique | V34-089, V34-092 | T-V34-22-12 | Lien de planification, preuve non exécutée |
| S-049 | `corpus_manifest` et droits d'usage des fixtures | V34-001, V34-003 | T-V34-22-02 | Lien de planification, preuve non exécutée |
| S-050 | Vérité terrain versionnée + protocole annotations | V34-068, V34-085 | T-V34-22-12 | Lien de planification, preuve non exécutée |
| S-051 | Rapprochement historique S-001–S-022 et inventaire réel workflows | V34-001 | T-V34-22-02 | Lien de planification, preuve non exécutée |
| S-052 | Schéma `Subject/Source/Artifact` avec identité et coordonnées | V34-025, V34-028, V34-018, V34-026 | T-V34-22-02 | Lien de planification, preuve non exécutée |
| S-053 | Format `.smartsvg` v1, migration et recovery | V34-025, V34-027, V34-013, V34-022, V34-034, V34-040, V34-140 | T-V34-22-03 | Lien de planification, preuve non exécutée |
| S-054 | Preuves orthogonales et sidecar `manifest.json` | V34-003, V34-131 | T-V34-22-01 | Lien de planification, preuve non exécutée |
| S-055 | Profil Explore 5 A4/Letter, imprimer portrait/poser A4 paysage | V34-122, V34-130 | T-V34-22-06 | Lien de planification, preuve non exécutée |
| S-056 | QA geometry Cut en mm : holes, islands, segments, offset | V34-108, V34-109 | T-V34-22-08 | Lien de planification, preuve non exécutée |
| S-057 | Registre matériel : machine, lame, tapis, matière, tests | V34-107, V34-124 | T-V34-22-10 | Lien de planification, preuve non exécutée |
| S-058 | Matrice environnement local et fournisseur IA | V34-078, V34-080 | T-V34-22-12 | Lien de planification, preuve non exécutée |
| S-059 | Audit accessibilité clavier/contraste/labels | V34-045, V34-049 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-060 | Score qualité séparé silhouette/couleur/géométrie | V34-101, V34-109 | T-V34-22-01 | Lien de planification, preuve non exécutée |
| S-061 | Tests fichiers hostiles et bombes XML/ZIP | V34-025, V34-139 | T-V34-22-03 | Lien de planification, preuve non exécutée |
| S-062 | File de jobs avec identité, cache et pause/reprise | V34-074, V34-135 | T-V34-22-11 | Lien de planification, preuve non exécutée |
| S-063 | Matrice de compatibilité ComfyUI/frontend/node API | V34-020, V34-139, V34-021, V34-023 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-064 | Contrat typographie et licence des polices | V3.3 G6/G9 (sans ticket V34) | Test V3.3 à relier | V3.3 conservée ; aucune nouvelle obligation V34 |
| S-065 | Comparaison contrôlée Design Space/Canva/SmartSVG | V34-003 | T-V34-22-07 | Lien partiel : benchmark/score V3.3 reste à tester |
| S-066 | Prototype diorama à quatre plans alignables | V3.3 G6/G9 (sans ticket V34) | Test V3.3 à relier | V3.3 conservée ; aucune nouvelle obligation V34 |
| S-067 | Accueil 4 objectifs + Reprendre | V34-042, V34-043, V34-009, V34-015, V34-037, V34-050, V34-052, V34-105, V34-114 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-068 | Schéma unique d’écran responsive desktop | V34-045 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-069 | États vide/chargement/erreur/export | V34-009, V34-046, V34-030 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-070 | Sélection directe et croisée sujets↔vignettes | V34-075, V34-132 | T-V34-22-04 | Lien de planification, preuve non exécutée |
| S-071 | Erreurs cliquables avec région et correction réversible | V34-065, V34-114, V34-056 | T-V34-22-08 | Lien de planification, preuve non exécutée |
| S-072 | Flux Express souris + clavier | V34-049, V34-066 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-073 | Aperçus original/masque/coupe séparés | V34-091, V34-095 | T-V34-22-05 | Lien de planification, preuve non exécutée |
| S-074 | Reprise dernier projet et contexte | V34-044, V34-136, V34-055 | T-V34-22-13 | Lien de planification, preuve non exécutée |
| S-075 | Panneau de validation du format par usage | V34-043, V34-051 | T-V34-22-01 | Lien de planification, preuve non exécutée |
| S-076 | Checklist d’export et transfert Design Space | V34-130 | T-V34-22-09 | Lien de planification, preuve non exécutée |
| S-077 | Alternative clavier aux gestes souris complexes | V34-049 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-078 | Contrastes/focus/texte ajustable | V34-045 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-079 | Loupe locale et comparaison glissante | V34-095 | T-V34-22-05 | Lien de planification, preuve non exécutée |
| S-080 | Pinceau correction tactile souris + aperçu effet | V34-133 | T-V34-22-04 | Lien de planification, preuve non exécutée |
| S-081 | Réglages récents et préréglages utilisateur | V34-055, V34-057 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-082 | Disposition de panneaux persistante | V34-046, V34-055 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-083 | Recherche d’action et aide contextuelle | V34-050, V34-051 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-084 | Ouvrir dossier/export/rapport depuis la réussite | V34-130, V34-140 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-085 | Aperçu cutter-only et repères micro-détails | V34-108, V34-109, V34-118 | T-V34-22-08 | Lien de planification, preuve non exécutée |
| S-086 | Toiles avec poignées et dimensions mm | V34-133 | T-V34-22-04 | Lien de planification, preuve non exécutée |
| S-087 | Multi-sélection, groupement et menu contextuel | V34-133 | T-V34-22-04 | Lien de planification, preuve non exécutée |
| S-088 | Trois gabarits de départ guidés | V34-126 | T-V34-22-08 | Lien de planification, preuve non exécutée |
| S-089 | Tableau de lot et reprise d’un échec isolé | V34-135, V34-134 | T-V34-22-11 | Lien de planification, preuve non exécutée |
| S-090 | Comparer deux dispositions de planche | V34-134 | T-V34-22-05 | Lien de planification, preuve non exécutée |
| S-091 | Bibliothèque avec miniatures et filtre métier | V34-136 | T-V34-22-13 | Lien de planification, preuve non exécutée |
| S-092 | Choix de police avec aperçu et alertes glyphes | V3.3 G6/G9 (sans ticket V34) | Test V3.3 à relier | V3.3 conservée ; aucune nouvelle obligation V34 |
| S-093 | Protocole de test utilisateur novice/régulier | V34-058, V34-067 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-094 | Tests d’accessibilité + vérification Windows zoom | V34-045, V34-139 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-095 | Tests de récupération pendant export/IA | V34-022, V34-140 | T-V34-22-03 | Lien de planification, preuve non exécutée |
| S-096 | Instrumentation locale UX et latence (opt-in export rapport) | V34-024, V34-140 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-097 | Commandes « refaire sur sélection » | V34-137, V34-138 | T-V34-22-13 | Lien de planification, preuve non exécutée |
| S-098 | Liste de recettes/gabarits personnels | V34-137 | T-V34-22-13 | Lien de planification, preuve non exécutée |
| S-099 | Guide d’assemblage de diorama dans l’UI | V3.3 G6/G9 (sans ticket V34) | Test V3.3 à relier | V3.3 conservée ; aucune nouvelle obligation V34 |
| S-100 | Raccourcis personnalisables / commandes favorites | V34-046 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| S-101 | Comparaison de variantes avec scores séparés | V34-002, V34-134 | T-V34-22-05 | Lien partiel : benchmark/score V3.3 reste à tester |
| R33-001 | Héritage intégral et vérifiable de V3.2 | V34-001, V34-025 | T-V34-22-02 | Lien de planification, preuve non exécutée |
| R33-002 | Échelle de maturité commune sans promotion implicite | V34-003 | T-V34-22-01 | Lien de planification, preuve non exécutée |
| R33-003 | Projet unique partagé par les six espaces | V34-011, V34-132 | T-V34-22-02 | Lien de planification, preuve non exécutée |
| R33-004 | Identités et révisions sur chaque commande asynchrone | V34-028, V34-032 | T-V34-22-02 | Lien de planification, preuve non exécutée |
| R33-005 | Résultat obsolète refusé ou isolé | V34-036, V34-115 | T-V34-22-04 | Lien de planification, preuve non exécutée |
| R33-006 | Masques float32 comme autorité de retouche | V34-028, V34-133 | T-V34-22-04 | Lien de planification, preuve non exécutée |
| R33-007 | Fallback manuel ou CPU pour le parcours essentiel | V34-051, V34-086 | T-V34-22-12 | Lien de planification, preuve non exécutée |
| R33-008 | Séparation permanente PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche et SVG d'édition | V34-005, V34-129 | T-V34-22-01 | Lien de planification, preuve non exécutée |
| R33-009 | Migration transactionnelle des projets | V34-027 | T-V34-22-03 | Lien de planification, preuve non exécutée |
| R33-010 | Index de bibliothèque reconstructible | V34-136 | T-V34-22-13 | Lien de planification, preuve non exécutée |
| R33-011 | Jobs idempotents avec succès partiel | V34-074, V34-135 | T-V34-22-11 | Lien de planification, preuve non exécutée |
| R33-012 | Annulation et reprise sans doublon | V34-074, V34-135 | T-V34-22-11 | Lien de planification, preuve non exécutée |
| R33-013 | Gestion explicite disque plein et lecture seule | V34-022, V34-140 | T-V34-22-03 | Lien de planification, preuve non exécutée |
| R33-014 | Gestion de sessions concurrentes et double activation | V34-036, V34-125, V34-119 | T-V34-22-04 | Lien de planification, preuve non exécutée |
| R33-015 | Rapport de diagnostic local expurgé | V34-024, V34-140 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| R33-016 | Inventaire des licences et provenances | V34-001, V34-078 | T-V34-22-12 | Lien de planification, preuve non exécutée |
| R33-017 | Mesure CPU RAM VRAM et temps par fournisseur | V34-080, V34-085 | T-V34-22-12 | Lien de planification, preuve non exécutée |
| R33-018 | Validation responsive et zoom Windows | V34-045 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| R33-019 | Alternative clavier à chaque geste complexe | V34-049 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| R33-020 | Localisation française cohérente et messages actionnables | V34-050, V34-056 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| R33-021 | Tests d'installation mise à jour et rollback | V34-139 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| R33-022 | Versions Design Space associées aux preuves | V34-107, V34-130, V34-116, V34-117, V34-121 | T-V34-22-09 | Lien de planification, preuve non exécutée |
| R33-023 | Contexte machine matière outil associé aux preuves physiques | V34-107, V34-124 | T-V34-22-10 | Lien de planification, preuve non exécutée |
| R33-024 | Données de preuve privées hors dépôt public | V34-003, V34-140 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| R33-025 | Tests de panne pendant sauvegarde export et IA | V34-022, V34-140, V34-123 | T-V34-22-03 | Lien de planification, preuve non exécutée |
| R33-026 | Budgets pour projets et lots volumineux | V34-074, V34-135 | T-V34-22-11 | Lien de planification, preuve non exécutée |
| R33-027 | Noms de fichiers sûrs et collisions contrôlées | V34-131, V34-138 | T-V34-22-13 | Lien de planification, preuve non exécutée |
| R33-028 | Polices licences et glyphes manquants visibles | V3.3 G6/G9 (sans ticket V34) | Test V3.3 à relier | V3.3 conservée ; aucune nouvelle obligation V34 |
| R33-029 | Comparaison de rendu indépendante de la fabricabilité | V34-098, V34-109 | T-V34-22-01 | Lien de planification, preuve non exécutée |
| R33-030 | Aucune requête réseau implicite | V34-079, V34-140 | T-V34-22-12 | Lien de planification, preuve non exécutée |
| R33-031 | Rapport par objet pour planches et lots | V34-135 | T-V34-22-11 | Lien de planification, preuve non exécutée |
| R33-032 | Préférences UI séparées de l'état projet | V34-055 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| R33-033 | États vide chargement erreur annulation et reprise | V34-046, V34-050 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| R33-034 | Preuve liée au SHA exact et à l'environnement | V34-003, V34-124 | T-V34-22-10 | Lien de planification, preuve non exécutée |
| R33-035 | Gate humain pour toute certification matérielle | V34-124 | T-V34-22-10 | Lien de planification, preuve non exécutée |
| R33-036 | Rollback documenté pour chaque micro-lot | V34-027, V34-140 | T-V34-22-03 | Lien de planification, preuve non exécutée |
| R33-037 | Registre de risques relié aux tests | V34-003, V34-109 | T-V34-22-08 | Lien de planification, preuve non exécutée |
| R33-038 | Matrice de compatibilité versionnée | V34-021, V34-139 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| R33-039 | Observation utilisateur sans collecte excessive | V34-055, V34-058 | T-V34-22-14 | Lien de planification, preuve non exécutée |
| R33-040 | Gel fonctionnel avant déclaration stable | V34-002, V34-003 | T-V34-22-14 | Lien de planification, preuve non exécutée |

## 3. Photographie des 140 tickets V3.4 et de leur rattachement

**Ne pas renuméroter ces tickets pour V3.5.** Ils constituent la continuité du backlog et ne sont pas automatiquement « implémentés » : la preuve actuelle se lit sur `main`, les PR et les tests réels.

| Ticket | Spécification source | Exigences rattachées (au moins une issue du lot source) | Recette transversale associée |
|---|---|---|---|
| V34-001 | Lot 01 | R33-001, R33-016, S-001, S-049, S-051 | T-V34-22-02, T-V34-22-12 |
| V34-002 | Lot 01 | R33-040, S-001, S-101 | T-V34-22-02, T-V34-22-05, T-V34-22-14 |
| V34-003 | Lot 01 | R33-002, R33-024, R33-034, R33-037, R33-040, S-001, S-019, S-043, S-049, S-054, S-065 | T-V34-22-01, T-V34-22-02, T-V34-22-07, T-V34-22-14 |
| V34-004 | Lot 01 | S-022 | T-V34-22-14 |
| V34-005 | Lot 01 | R33-008, S-002 | T-V34-22-01 |
| V34-006 | Lot 02 | S-004 | T-V34-22-14 |
| V34-007 | Lot 02 | S-007 | T-V34-22-05 |
| V34-008 | Lot 02 | S-012 | T-V34-22-08 |
| V34-009 | Lot 02 | S-067, S-069 | T-V34-22-14 |
| V34-010 | Lot 02 | S-003 | T-V34-22-02 |
| V34-011 | Lot 03 | R33-003, S-022 | T-V34-22-14, T-V34-22-02 |
| V34-012 | Lot 03 | S-012 | T-V34-22-08 |
| V34-013 | Lot 03 | S-053 | T-V34-22-03 |
| V34-014 | Lot 03 | S-022 | T-V34-22-14 |
| V34-015 | Lot 03 | S-067 | T-V34-22-14 |
| V34-016 | Lot 03 | S-027 | T-V34-22-12 |
| V34-017 | Lot 04 | S-022 | T-V34-22-14 |
| V34-018 | Lot 04 | S-052 | T-V34-22-02 |
| V34-019 | Lot 04 | S-022, S-046 | T-V34-22-14 |
| V34-020 | Lot 04 | S-022, S-063 | T-V34-22-14 |
| V34-021 | Lot 04 | R33-038, S-063 | T-V34-22-14 |
| V34-022 | Lot 04 | R33-013, R33-025, S-053, S-095 | T-V34-22-03 |
| V34-023 | Lot 04 | S-063 | T-V34-22-14 |
| V34-024 | Lot 04 | R33-015, S-022, S-096 | T-V34-22-14 |
| V34-025 | Lot 05 | R33-001, S-017, S-023, S-024, S-052, S-053, S-061 | T-V34-22-02, T-V34-22-03 |
| V34-026 | Lot 05 | S-052 | T-V34-22-02 |
| V34-027 | Lot 05 | R33-009, R33-036, S-053 | T-V34-22-03 |
| V34-028 | Lot 05 | R33-004, R33-006, S-023, S-052 | T-V34-22-02, T-V34-22-04 |
| V34-029 | Lot 05 | S-026 | T-V34-22-04 |
| V34-030 | Lot 05 | S-069 | T-V34-22-14 |
| V34-031 | Lot 05 | S-017, S-042 | T-V34-22-02, T-V34-22-03 |
| V34-032 | Lot 06 | R33-004, S-003 | T-V34-22-02 |
| V34-033 | Lot 06 | S-026 | T-V34-22-04 |
| V34-034 | Lot 06 | S-053 | T-V34-22-03 |
| V34-035 | Lot 06 | S-008 | T-V34-22-04 |
| V34-036 | Lot 06 | R33-005, R33-014, S-027 | T-V34-22-12, T-V34-22-04 |
| V34-037 | Lot 06 | S-067 | T-V34-22-14 |
| V34-038 | Lot 06 | S-008 | T-V34-22-04 |
| V34-039 | Lot 06 | S-027 | T-V34-22-12 |
| V34-040 | Lot 06 | S-053 | T-V34-22-03 |
| V34-041 | Lot 07 | S-003, S-004 | T-V34-22-02, T-V34-22-14 |
| V34-042 | Lot 07 | S-067 | T-V34-22-14 |
| V34-043 | Lot 07 | S-004, S-013, S-025, S-067, S-075 | T-V34-22-14, T-V34-22-01 |
| V34-044 | Lot 07 | S-023, S-074 | T-V34-22-02, T-V34-22-13 |
| V34-045 | Lot 07 | R33-018, S-059, S-068, S-078, S-094 | T-V34-22-14 |
| V34-046 | Lot 07 | R33-033, S-069, S-082, S-100 | T-V34-22-14 |
| V34-047 | Lot 07 | S-027 | T-V34-22-12 |
| V34-048 | Lot 07 | S-003 | T-V34-22-02 |
| V34-049 | Lot 07 | R33-019, S-059, S-072, S-077 | T-V34-22-14 |
| V34-050 | Lot 08 | R33-020, R33-033, S-067, S-083 | T-V34-22-14 |
| V34-051 | Lot 08 | R33-007, S-013, S-075, S-083 | T-V34-22-14, T-V34-22-01, T-V34-22-12 |
| V34-052 | Lot 08 | S-067 | T-V34-22-14 |
| V34-053 | Lot 08 | S-003 | T-V34-22-02 |
| V34-054 | Lot 08 | S-022 | T-V34-22-14 |
| V34-055 | Lot 08 | R33-032, R33-039, S-074, S-081, S-082 | T-V34-22-13, T-V34-22-14 |
| V34-056 | Lot 08 | R33-020, S-071 | T-V34-22-08, T-V34-22-14 |
| V34-057 | Lot 08 | S-081 | T-V34-22-14 |
| V34-058 | Lot 08 | R33-039, S-093 | T-V34-22-14 |
| V34-059 | Lot 09 | S-003 | T-V34-22-02 |
| V34-060 | Lot 09 | S-003 | T-V34-22-02 |
| V34-061 | Lot 09 | S-023 | T-V34-22-02 |
| V34-062 | Lot 09 | S-008 | T-V34-22-04 |
| V34-063 | Lot 09 | S-003 | T-V34-22-02 |
| V34-064 | Lot 09 | S-022 | T-V34-22-14 |
| V34-065 | Lot 09 | S-071 | T-V34-22-08 |
| V34-066 | Lot 09 | S-072 | T-V34-22-14 |
| V34-067 | Lot 09 | S-093 | T-V34-22-14 |
| V34-068 | Lot 10 | S-006, S-050 | T-V34-22-12 |
| V34-069 | Lot 10 | S-007 | T-V34-22-05 |
| V34-070 | Lot 10 | S-018 | T-V34-22-11 |
| V34-071 | Lot 10 | S-007 | T-V34-22-05 |
| V34-072 | Lot 10 | S-023 | T-V34-22-02 |
| V34-073 | Lot 10 | S-014, S-028 | T-V34-22-04, T-V34-22-12 |
| V34-074 | Lot 10 | R33-011, R33-012, R33-026, S-018, S-027, S-038, S-062 | T-V34-22-12, T-V34-22-11 |
| V34-075 | Lot 10 | S-070 | T-V34-22-04 |
| V34-076 | Lot 10 | S-015 | T-V34-22-05 |
| V34-077 | Lot 10 | S-005 | T-V34-22-12 |
| V34-078 | Lot 11 | R33-016, S-005, S-058 | T-V34-22-12 |
| V34-079 | Lot 11 | R33-030, S-003 | T-V34-22-02, T-V34-22-12 |
| V34-080 | Lot 11 | R33-017, S-005, S-027, S-058 | T-V34-22-12 |
| V34-081 | Lot 11 | S-018 | T-V34-22-11 |
| V34-082 | Lot 11 | S-007 | T-V34-22-05 |
| V34-083 | Lot 11 | S-025 | T-V34-22-14 |
| V34-084 | Lot 11 | S-005 | T-V34-22-12 |
| V34-085 | Lot 11 | R33-017, S-006, S-050 | T-V34-22-12 |
| V34-086 | Lot 11 | R33-007, S-042 | T-V34-22-03, T-V34-22-12 |
| V34-087 | Lot 12 | S-003, S-029 | T-V34-22-02, T-V34-22-01 |
| V34-088 | Lot 12 | S-015 | T-V34-22-05 |
| V34-089 | Lot 12 | S-016, S-048 | T-V34-22-05, T-V34-22-12 |
| V34-090 | Lot 12 | S-009 | T-V34-22-01 |
| V34-091 | Lot 12 | S-013, S-073 | T-V34-22-14, T-V34-22-05 |
| V34-092 | Lot 12 | S-005, S-048 | T-V34-22-12 |
| V34-093 | Lot 12 | S-018 | T-V34-22-11 |
| V34-094 | Lot 12 | S-006 | T-V34-22-12 |
| V34-095 | Lot 12 | S-015, S-073, S-079 | T-V34-22-05 |
| V34-096 | Lot 13 | S-023 | T-V34-22-02 |
| V34-097 | Lot 13 | S-030 | T-V34-22-01 |
| V34-098 | Lot 13 | R33-029, S-011, S-032 | T-V34-22-01 |
| V34-099 | Lot 13 | S-011, S-033, S-034 | T-V34-22-01 |
| V34-100 | Lot 13 | S-030, S-045 | T-V34-22-01 |
| V34-101 | Lot 13 | S-009, S-060 | T-V34-22-01 |
| V34-102 | Lot 13 | S-008 | T-V34-22-04 |
| V34-103 | Lot 13 | S-011 | T-V34-22-01 |
| V34-104 | Lot 13 | S-018 | T-V34-22-11 |
| V34-105 | Lot 13 | S-067 | T-V34-22-14 |
| V34-106 | Lot 14 | S-012 | T-V34-22-08 |
| V34-107 | Lot 14 | R33-022, R33-023, S-012, S-057 | T-V34-22-08, T-V34-22-10, T-V34-22-09 |
| V34-108 | Lot 14 | S-030, S-056, S-085 | T-V34-22-01, T-V34-22-08 |
| V34-109 | Lot 14 | R33-029, R33-037, S-012, S-056, S-060, S-085 | T-V34-22-08, T-V34-22-01 |
| V34-110 | Lot 14 | S-007 | T-V34-22-05 |
| V34-111 | Lot 14 | S-012 | T-V34-22-08 |
| V34-112 | Lot 14 | S-032, S-045 | T-V34-22-01 |
| V34-113 | Lot 14 | S-012 | T-V34-22-08 |
| V34-114 | Lot 14 | S-067, S-071 | T-V34-22-14, T-V34-22-08 |
| V34-115 | Lot 14 | R33-005, S-023 | T-V34-22-02, T-V34-22-04 |
| V34-116 | Lot 15 | R33-022 | T-V34-22-09 |
| V34-117 | Lot 15 | R33-022 | T-V34-22-09 |
| V34-118 | Lot 15 | S-085 | T-V34-22-08 |
| V34-119 | Lot 15 | R33-014 | T-V34-22-04 |
| V34-120 | Lot 15 | S-012 | T-V34-22-08 |
| V34-121 | Lot 15 | R33-022 | T-V34-22-09 |
| V34-122 | Lot 15 | S-029, S-055 | T-V34-22-01, T-V34-22-06 |
| V34-123 | Lot 15 | R33-025 | T-V34-22-03 |
| V34-124 | Lot 15 | R33-023, R33-034, R33-035, S-010, S-031, S-057 | T-V34-22-10, T-V34-22-07 |
| V34-125 | Lot 15 | R33-014 | T-V34-22-04 |
| V34-126 | Lot 16 | S-020, S-088 | T-V34-22-08 |
| V34-127 | Lot 16 | S-012 | T-V34-22-08 |
| V34-128 | Lot 16 | S-030 | T-V34-22-01 |
| V34-129 | Lot 17 | R33-008, S-002, S-009, S-029, S-030, S-032 | T-V34-22-01 |
| V34-130 | Lot 17 | R33-022, S-055, S-076, S-084 | T-V34-22-09, T-V34-22-06, T-V34-22-14 |
| V34-131 | Lot 17 | R33-027, S-017, S-054 | T-V34-22-02, T-V34-22-01, T-V34-22-13 |
| V34-132 | Lot 18 | R33-003, S-003, S-008, S-023, S-070 | T-V34-22-04, T-V34-22-02 |
| V34-133 | Lot 18 | R33-006, S-008, S-026, S-035, S-080, S-086, S-087 | T-V34-22-04 |
| V34-134 | Lot 19 | S-040, S-089, S-090, S-101 | T-V34-22-11, T-V34-22-05 |
| V34-135 | Lot 19 | R33-011, R33-012, R33-026, R33-031, S-018, S-038, S-062, S-089 | T-V34-22-11 |
| V34-136 | Lot 20 | R33-010, S-024, S-041, S-074, S-091 | T-V34-22-02, T-V34-22-13 |
| V34-137 | Lot 20 | S-017, S-097, S-098 | T-V34-22-02, T-V34-22-13 |
| V34-138 | Lot 20 | R33-027, S-038, S-039, S-097 | T-V34-22-11, T-V34-22-13 |
| V34-139 | Lot 21 | R33-021, R33-038, S-022, S-042, S-046, S-061, S-063, S-094 | T-V34-22-03, T-V34-22-14 |
| V34-140 | Lot 21 | R33-013, R33-015, R33-024, R33-025, R33-030, R33-036, S-053, S-084, S-095, S-096 | T-V34-22-03, T-V34-22-14, T-V34-22-12 |

## 4. Photographie des 80 capacités candidates UX (intitulés #134)

**Une coche historique = fiche auditée et non fonction intégrée.** Ne pas réduire le corpus aux fonctions actuellement accessibles dans Windows.

### Groupe A — 16 capacités (audit historique : [#134](https://github.com/frenndak/SmartSVG-Studio/issues/134))

| ID | Intitulé et périmètre recopiés du registre #134 | État V3.5 initial |
|---|---|---|
| A01 | Smart Import : PNG/JPEG/WebP/SVG, lots, contrôles d'entrée, dimensions/alpha/DPI | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| A02 | Smart Select gestes : clic, survol, lasso libre/polygonal, rectangle/ellipse, pinceau, texte facultatif | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| A03 | Smart Select multi-zones : îlots, trous, garder/exclure, union/intersection/soustraction/inversion | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| A04 | Smart Select intelligence : prompts grossiers → contour recalé aux pixels, segmentation CPU/IA, incertitude et alternatives | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| A05 | Smart Select affinage : lissage, dilatation/érosion, détails fins, couleurs proches, bord local | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| A06 | Smart Clean détourage : retrait de fond, masque alpha, bords/transparent | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| A07 | Smart Clean nettoyage : anti-halo, RGB, défauts, micro-fragments, topologie | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| A08 | Smart Clean qualité : netteté, débruitage, artefacts, contraste, HD | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| A09 | Smart Clean contrôle : transparence sur divers fonds, zoom 100%, diff avant/après | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| A10 | Smart Color : pipette, recoloration, palettes, dégradés, transparence, quantification | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| A11 | Smart Color production : couches par couleur, fidélité/profils d'impression | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| A12 | Smart Vector conversion : silhouette, contour, centerline, multicouleur, SVG éditable | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| A13 | Smart Vector courbes : plume/crayon, Bézier, nœuds, tangentes, coins | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| A14 | Smart Vector géométrie : union/différence/intersection, trous, fermeture chemins | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| A15 | Smart Vector optimisation : simplification, nœuds, angles, fragments et intersections | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| A16 | Smart Vector intelligence : variantes et mesures fidélité/complexité/topologie. | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |


### Groupe B — 14 capacités (audit historique : [#134](https://github.com/frenndak/SmartSVG-Studio/issues/134))

| ID | Intitulé et périmètre recopiés du registre #134 | État V3.5 initial |
|---|---|---|
| B01 | objets raster/vector/texte/masques/groupes/opérations | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| B02 | calques visibles/verrouillés/groupés/ordre/opacité | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| B03 | décomposition intelligente des accessoires/illustrations en objets éditables | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| B04 | déplacer/échelle/rotation/miroir/duplication par poignées | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| B05 | alignement/distribution/grille/aimantation/mesures | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| B06 | perspective, grille de déformation, masques d'écrêtage | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| B07 | articulation locale de personnage | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| B08 | reconstruction opt-in après extraction/déplacement | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| B09 | texte éditable/polices/typographie | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| B10 | texte courbe/circulaire/chemin/monogrammes/étiquettes | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| B11 | effets de texte/contours/ombres/textures/dégradés | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| B12 | texte→chemins, fusion et contrôles de fabrication | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| B13 | OCR facultatif→texte éditable après vérification | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| B14 | Smart Compose : marges/alignement/hiérarchie/modèles visuels. | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |


### Groupe C — 18 capacités (audit historique : [#134](https://github.com/frenndak/SmartSVG-Studio/issues/134))

| ID | Intitulé et périmètre recopiés du registre #134 | État V3.5 initial |
|---|---|---|
| C01 | stickers : offset, bleed, alpha, PNG Print Then Cut | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C02 | vinyle monochrome : silhouette et simplification | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C03 | multicouche : palette, couches, alignement | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C04 | pochoirs : îlots flottants, ponts | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C05 | dessin/centerline, continuité des chemins | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C06 | CUT/SCORE/DRAW/PRINT/FOIL distincts | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C07 | prévol géométrique : détails fragiles, doubles contours, intersections | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C08 | profils machine/matière/lame/tapis/unités | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C09 | variantes fidèle/équilibré/découpe facile | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C10 | les QUATRE contrats séparés : PNG Print Then Cut / SVG Basic Cut / SVG Cut multicouche / SVG d'édition | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C11 | transfert guidé Design Space, Score/Attacher, vérification dimensions | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C12 | Smart Layout duplication/planche multi-pages/quantités | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C13 | nesting par silhouettes, rotation, marges, contraintes | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C14 | placements verrouillés, édition manuelle, réoptimisation | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C15 | économie de matière, reprises de lot | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C16 | patrons cartes/boîtes/enveloppes/pochoirs, modèles paramétriques | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C17 | géométrie mm, languettes/plis/épaisseur/preflight | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| C18 | preview patron 2D / simulation de pliage 3D éventuelle. | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |


### Groupe D — 12 capacités (audit historique : [#134](https://github.com/frenndak/SmartSVG-Studio/issues/134))

| ID | Intitulé et périmètre recopiés du registre #134 | État V3.5 initial |
|---|---|---|
| D01 | fournisseurs de segmentation CPU/SAM léger/SAM2/3 selon viabilité réelle | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| D02 | consignes clic/lasso/pinceau/texte combinées | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| D03 | variantes et choix expliqué avec confirmation | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| D04 | matting cheveux/poils/translucide | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| D05 | upscale HD conditionnel | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| D06 | génération raster/vector facultative | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| D07 | inpainting et réparation locale | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| D08 | catalogue modèles : licence, versions, hash, consentement | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| D09 | VRAM/CPU/repli/annulation/diagnostic | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| D10 | recettes et préréglages de traitement | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| D11 | batch, dossiers, CSV, reprise et erreurs individuelles | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| D12 | assistant contextuel et suggestions explicables. | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |


### Groupe E — 20 capacités (audit historique : [#134](https://github.com/frenndak/SmartSVG-Studio/issues/134))

| ID | Intitulé et périmètre recopiés du registre #134 | État V3.5 initial |
|---|---|---|
| E01 | bibliothèque, récents, miniatures, recherche/favoris | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E02 | collections/tags/modèles/duplication | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E03 | variantes/historique de création | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E04 | atelier hybride raster/vector/objets/propriétés | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E05 | canvas zoom/pan/poignées/aimants/overlays | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E06 | comparaison avant-après/sliders/superposition | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E07 | survol/context bar/gestes/raccourcis | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E08 | modes novice/avancé et divulgation progressive | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E09 | thèmes/panneaux/préférences | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E10 | accessibilité clavier/focus/contraste/DPI/motion réduite | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E11 | Undo/Redo/brouillons/transactions/historique | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E12 | sauvegarde V1 CAS/recovery et intégrité | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E13 | previews async/caches bornés/requêtes périmées | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E14 | diagnostics réparables et erreurs compréhensibles | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E15 | QA alpha/contours/couleurs/résolution | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E16 | QA SVG chemins/topologie/viewBox/mm | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E17 | QA fabrication/profil/machine et preuve physique séparée | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E18 | packaging Windows/hors ligne/update/rollback | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E19 | confidentialité/local/opt-in réseau | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |
| E20 | tutoriels/aide contextuelle. | HÉRITÉ / À CONTRE-EXPERTISER (non intégré par ce registre) |


## 5. Tests historiques, registres d'opportunités et adoption

- **437 scénarios proposés en V3.4 :** total déclaré ; inventaire détaillé à construire à partir des lots 01–22 puis confronter avec les références et les tests actuels. Critère de fin : 437 entrées traçables ou écarts expliqués et revus.
- **Registre d'opportunités V3.4 :** [OPPORTUNITIES.md](../roadmap-v3.4/OPPORTUNITIES.md), avec décisions/raisons et idées rejetées à préserver.
- **Enrichissements après V3.4 :** [#141](https://github.com/frenndak/SmartSVG-Studio/issues/141), y compris Smart Delivery V1 et V2 ; aucune capacité P1/P2 n'est intégrée à V3.5 par simple présence dans ce registre.
- **Gouvernance :** [AGENTS.md](../../AGENTS.md) maintient V3.4 ACTIVE. Toute autorité V3.5 exige PR normative revue séparément de la promotion d'AGENTS ; aucune auto-fusion horaire.
