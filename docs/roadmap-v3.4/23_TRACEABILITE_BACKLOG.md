# 23 — Traçabilité bidirectionnelle et backlog minimal V3.4 (DRAFT)

**Établi le 29 octobre 2026.** Document de **planification uniquement**, sans implémentation ni changement de périmètre. V3.3 reste **ACTIVE** ; PR #73 **DRAFT** ; issue #72. Base main relue : `fff374e5147689165839bd76e742713d714ff147` ; branche documentaire avant le lot : `099ec606ee4657ce63280e6b5bb3a131e1f89ee1`. Aucun rapprochement automatique avec main.

## 1. Méthode et frontière de preuve

Les **141 identifiants** proviennent de [HERITAGE_INDEX](HERITAGE_INDEX.md) (101 S, 40 R33) et sont conservés **sans altérer leurs critères normatifs V3.3**. Le tableau ci-dessous propose un **point d'entrée V34** par exigence, non une assertion de couverture fonctionnelle complète. Les `T-V34-22-xx` sont des **recettes transversales de référence** : lorsqu'un test est partagé, il ne prouve **que la partie correspondante** de l'exigence. Les exigences G6/G9 non détaillées dans V3.4 restent entièrement exigibles par la V3.3 ; le tiret de ticket n'est ni suppression ni report. Aucun `PASS` produit, Windows, GPU, Design Space ou physique n'est revendiqué. Les tickets V34 sont `SPECIFIE` seulement ; les tests sont `NON_EXECUTE`.

**Attention :** cette table est une **réconciliation de planification**, pas un audit ligne par ligne des assertions de tous les tests locaux des lots 01–22. La relation test↔ticket↔exigence est un **candidat de traçabilité** à confirmer lors de la future implémentation. Les renvois de coordination de l’index inverse sont désormais également reproduits dans le sens exigence→ticket (correction documentaire du lot 24) ; les liens des tests locaux détaillés restent à qualifier au niveau des assertions lors des PR de code. Aucun renvoi de coordination n'établit à lui seul une couverture fonctionnelle. Ne jamais utiliser cette matrice pour promouvoir un statut de maturité.

## 2. Exigence → ticket V34 → recette de référence (141/141)

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

## 3. Ticket V34 → exigences : index inverse (140/140)

La première exigence de chaque ligne provient du rattachement métier explicite du lot source ; les autres sont des **renvois de coordination** issus du tableau précédent. Les tests du lot 22 ne remplacent pas les tests spécifiques décrits dans chaque lot. Une exigence historique peut donc avoir plusieurs tickets et un ticket plusieurs exigences.

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

## 4. Trois incohérences réelles à corriger sans extension de périmètre

1. **Fausse dépendance V2.** Le lot 14 présente parfois le format V2 et le bootstrap natif comme « bloquants » pour la fabrication. Or les lots 16–22 autorisent explicitement la **génération de fichiers brouillons sur fixtures indépendantes** et les exports V1 compatibles. **Correction de priorité :** V2 est obligatoire uniquement pour une persistance V2 réellement nécessaire, jamais pour calculer un patron, inspecter un SVG ou générer un PNG/SVG externe.
2. **Capacités 32/50 confondues.** `engine/smartsvg_cricut/direct_import_v218.py` définit `MAX_ITEMS=32`, et les snapshots V1 restent bornés. **Correction :** 50 *instances* sont orchestrées par lots et rapportées individuellement ; **ne pas** promettre 50 masques float32 dans un snapshot V1 ni une archive V1 invalide. Un export externe en lots ne valide pas une migration de projet.
3. **Couverture V3.3 ≠ réécriture V3.4.** Les exigences de typographie/OCR et de dioramas (notamment S-021/036/037/044/047/064/066/092/099 et R33-028) n'ont pas de nouveau ticket V34 imposé. **Correction :** les conserver sous leurs propriétaires G6/G9, avec leurs propres recettes V3.3, sans les déclarer terminées par un test voisin du lot 22. Les benchmarks S-019/043/065 et scores S-101 restent également à mesurer spécifiquement.

## 5. Backlog exécutable par vertical slices, sans nouveau ticket

| Ordre pratique | Résultat vérifiable | Réemploi réel et tickets existants | Dépendances strictes | Parallèle / non bloquant |
|---|---|---|---|---|
| A — continuer G3.3e-b2a | Retouche non destructive du bon `Subject` ; annuler/recharger sans altérer float32 | `project_workspace_g22.py`, `project_recovery.py`, G2/G3, V34-132/133 seulement en conception | Contrats V1, identité G1.2, CAS SHA | **Aucun** bootstrap V3.4, IA, V2, assistant ou prévol fabrication requis |
| B — quatre sorties sur fixtures | PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche et SVG édition distincts | `direct_import_v218.py`, exporteurs historiques, V34-005/097/129/130/131 | Dimensions/units, contrat de sortie, validation XML/PNG, conservation des précédents fichiers | V2, assistant, installation Windows autonome, modèle IA |
| C — boîte Score+Cut | Géométrie mm, lignes CUT/SCORE distinctes, guide manuel Design Space | Lots 14–17, V34-106/107/109/111/126/127/128/130 | Géométrie valide, opérations typées, profil connu ou incertitude affichée, prévol | IA, V2, moteur de dessin complet, bootstrap autonome |
| D — Atelier raccordé | Sélection par ID réel, pinceau unique, Undo/CAS et calques | G2/G3, V34-032/033/132/133 | Identité, état projet unique, restauration V1 | Nouveau store, second moteur de pinceau, nouveau framework |
| E — planches 12/24/50 | Placements déterministes, reprise après 17/50, rapport par objet | `_make_pages`, `_save_sheet`, V34-070/074/093/134/135/129 | Lots mémoire bornés, empreintes de reprise, export sûr | 50 masques V1 simultanés, V2 pour exports externes, IA |
| F — bibliothèque et CSV | 105 projets retrouvables ; 30 variantes traçables, reprise sans doublon | `project_workspace_g22.py`, V34-136/137/138/135/131 | Catalogue dérivé, writer CAS, jobs/exports existants, polices vérifiées | Nouvelle base de données faisant autorité, V2 global, IA |
| G — application autonome | Démarrage hors ComfyUI, hors ligne, rollback installation et projets | `smartsvg_core`, V34-017/019/020/139/140 | Graphe d'imports réel, sécurité IPC/loopback, tests Windows | **Ne bloque pas** les slices A–F sur composants/fixtures |
| H — assistant et IA facultatifs | Propositions sûres, validation explicite, fallback manuel/CPU | V34-050..067/078..086 et adaptateurs existants | Consommateur réel, licence/consentement, CAS, ressources mesurées | Aucun modèle téléchargé implicitement ; n'empêche pas les slices précédentes |

**Graphe minimal :** V1+Subject+CAS → A et D ; géométrie+exports historiques → B ; géométrie+opérations+prévol → C ; identité+jobs+cache+exports → E ; V1+catalogue+jobs+exports → F ; graphe imports+sécurité → G ; assistant+permissions+modèles consentis → H. Les branches B/C/E peuvent être éprouvées sur fixtures **en parallèle** de G3.3. Les gates de **qualification** Windows, Design Space et Cricut physique restent inchangés : la parallélisation n'est pas une dispense.

## 6. Tests et preuve : contrôle inverse

Les **14 recettes transversales** du [lot 22](22_VALIDATION_CORPUS_PREUVES.md) sont reliées aux tickets existants et couvrent : quatre sorties (01), float32 (02), crash/archives (03), pinceau (04), planches 12 (05), A4/Design Space (06), coupon stickers (07), boîte géométrique (08), Score/Attach dans Design Space (09), coupon carton (10), 50/reprise (11), IA facultative (12), bibliothèque/CSV (13), Windows/UX (14). Chaque test de cette série est présent dans la matrice ci-dessus : **14/14** tests cités.

Pour les exigences sans test direct du lot 22, conserver le **test métier V3.3** ou les tests locaux du lot concerné, et ajouter le lien exact **lors de la PR d'implémentation** ; un test voisin n'est pas une preuve suffisante. Contrôle inverse obligatoire avant qualification : `test_id → ticket_id → S/R33 → code_sha → fixture_sha → environnement → résultat` ; et `S/R33 → ticket/test ou justification V3.3`. Les preuves `auto`, `Windows`, `RTX`, `DesignSpace`, `physique` sont indépendantes ; toutes **NON_EXECUTE dans ce cycle**.

**Definition of Done des tickets existants :** assertions ciblées réellement exécutées au SHA, régression V1/identités/float32/4 exports, erreurs FR actionnables, restauration vérifiée, test matériel spécifique si revendication matérielle ; aucune promotion implicite `SPECIFIE → QUALIFIE`. Les priorités P0/P1 des lots précédents ne sont **pas requalifiées silencieusement** ; le tableau des slices est un ordre d'exécution, pas une modification des obligations V3.3.

## 7. Risques, décisions et passation vers le lot 24

- **Ouverts :** graphe imports natif incomplet, tolérances machine non mesurées, V1 limité, fiabilité de reprise à tester, licences IA à requalifier au téléchargement, statut des preuves de fabrication, tests Windows/RTX/Design Space/physiques non réalisés.
- **Décisions de mainteneur futures :** format V2 si besoin démontré, choix UI/packaging après prototype, critères quantifiés de coupe selon outil/matière, éventuelle promotion de la V3.4. Aucun de ces arbitrages ne bloque la poursuite G3.3.
- **Lot 24 :** vérifier les liens exacts de tous les tickets/tests locaux, les faux prérequis, les exigences G6/G9 et benchmarks conservés, puis publier une **roadmap V3.4 DRAFT de passation** sans fusion, code ni planification supplémentaire.

**Sources internes relues le 29/10/2026 :** `AGENTS.md`, V3.3 MASTER/TRACEABILITY/COVERAGE/HERITAGE/FASTPATH, README/PROGRESS/HERITAGE_INDEX V3.4, lot 22, `engine/smartsvg_core/project_archive.py`, `project_workspace_g22.py`, `project_recovery.py`, `engine/smartsvg_cricut/direct_import_v218.py`. Les informations Cricut externes sont reprises **sans nouvelle revendication** des sources officielles datées du lot 22. Aucun test produit ni matériel exécuté.
