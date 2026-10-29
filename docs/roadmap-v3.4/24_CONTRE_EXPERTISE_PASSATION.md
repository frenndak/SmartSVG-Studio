# SmartSVG Studio V3.4 — Lot 24/24 : contre-expertise finale et passation (DRAFT)

**Date : 29 octobre 2026. Statut : PROPOSITION DOCUMENTAIRE, non normative.** La roadmap **V3.3 demeure ACTIVE**. Issue de coordination [#72](https://github.com/frenndak/SmartSVG-Studio/issues/72), [PR #73](https://github.com/frenndak/SmartSVG-Studio/pull/73) à conserver **DRAFT**. Base `main` relue : `fff374e5147689165839bd76e742713d714ff147` ; branche avant la correction ciblée : `ea52c772170a9cd77be1367e79216985cb5b2dcf`. La branche était à **98 commits d'avance et 1 de retard** sur `main` avant ce lot. Le seul commit de `main` non intégré concerne `docs/ROADMAP_COVERAGE_v3_3.md` et le guide `docs/ROADMAP_EXECUTION_FASTPATH_v3_3.md` ; **aucun merge/rebase** n'a été réalisé.

**Mission tenue sans extension :** auditer les lots 01–23, rectifier une asymétrie documentaire, présenter l'ordre d'implémentation des **fonctions déjà prévues**, expliciter les preuves manquantes et remettre un backlog utilisable. **Aucune nouvelle fonction, aucun ticket V34, aucune obligation P0/P1, aucun framework, modèle IA, driver Cricut ni gate additionnel.** Les idées non approuvées d'[OPPORTUNITIES.md](OPPORTUNITIES.md) restent historiques, optionnelles et hors chemin critique.

## 1. Bilan vérifiable et trois constats de contre-expertise

| Contrôle | Constat au moment du lot 24 | Interprétation correcte |
| --- | --- | --- |
| Héritage | **101 S + 40 R33 = 141 identifiants** présents une seule fois dans le tableau direct du [lot 23](23_TRACEABILITE_BACKLOG.md) | Couverture d'**index**, pas preuve d'implémentation ou de recette |
| Tickets | **V34-001..V34-140 = 140 identifiants** dans l'index inverse, aucun ID nouveau au lot 24 | Tickets `SPECIFIE`, pas fonctions réalisées |
| Liens bidirectionnels | **97 liens inverse→direct absents**, répartis sur 40 exigences, détectés par comparaison mécanique des deux tableaux ; **corrigés dans le lot 23** par ajout des renvois manquants (commit `ac7b9058b33285ef7296b9af50bbca4a2bf90fc7`) | Après correction : **0 arête inverse sans réciproque** ; les renvois de coordination ne deviennent pas des preuves |
| Recettes | **437 lignes de tests T-V34** spécifiées dans les lots 02–22, dont **14** tests transversaux du lot 22 ; **34** lignes comportent directement un ID ticket dans leur propre ligne, **403** n'en comportent pas | Les 403 peuvent être décrites à proximité des tickets, mais le lien *assertion exacte → ticket* n'est **pas démontré** par la seule ligne de test. Ne pas revendiquer une traçabilité de preuve intégrale |
| Exceptions V3.3 | **10 exigences** `S-021/036/037/044/047/064/066/092/099` et `R33-028` restent sous leurs propriétaires G6/G9 | Ni supprimées, ni reportées, ni réputées testées par un test voisin ; tests V3.3 à rattacher lors de l'implémentation |
| Branches | `main` a un commit documentaire non intégré ; PR #73 ouverte DRAFT | Aucun rapprochement automatique ; relire HEAD avant toute future modification |
| Matériel | Aucune preuve d'essai Windows, RTX 3070, Design Space ou Cricut Explore 5 issue de cette campagne | Tous les axes de qualification correspondants restent **NON_EXECUTE** |

**Constat A — corrigé :** le lot 23 affichait une matrice « bidirectionnelle » avec 97 renvois présents seulement dans l'index inverse. La correction **ne modifie ni exigences, ni tickets, ni priorités** ; elle réconcilie les tableaux.

**Constat B — ouvert, non bloquant :** les **403 lignes de tests locaux** sans ticket explicite sur la même ligne ne permettent pas de prouver mécaniquement `test → ticket → exigence`. Les descriptions et tickets par lot restent utilisables. Pour chaque future PR de code, rattacher les assertions effectivement exécutées aux tickets et exigences concernés, sans créer 403 tickets ni imposer une phase de planification avant de coder. Les 14 tests transversaux du lot 22 ne remplacent pas ces recettes locales.

**Constat C — ouvert, non bloquant :** la branche est en retard d'un commit documentaire sur `main`. Le guide FASTPATH V3.3 doit être respecté dans les futurs lots de code, mais il ne transforme pas la migration V2, le bootstrap autonome ou l'IA en prérequis de G3.3. Réconcilier les branches uniquement dans une intervention de maintenance autorisée et contrôlée.

## 2. Contrats intangibles, propriétaires et réemploi du code réel

| Domaine | Autorité / module existant à réutiliser | Frontière à préserver |
| --- | --- | --- |
| Projet et sauvegarde | `engine/smartsvg_core/project_archive.py`, `project_workspace_g22.py`, `project_recovery.py` | `.smartsvg` V1 reste autorité ; CAS par SHA, publication atomique, `.previous`/`.pending-backup`, aucun second writer |
| Sujets/masques | `subject_identity_g33e.py`, `mask_snapshot_g24.py`, `mask_binding_g33e.py` et moteur de retouche G3.3e | IDs `Subject` réels, octets float32 intacts ; jamais substituer un index de masque à l'identité durable |
| Exports | `engine/smartsvg_cricut/direct_import_v218.py` et exporteurs historiques (à inventorier précisément au ticket) | **Quatre contrats distincts** : PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche, SVG d'édition ; le format V1 n'est pas modifié silencieusement |
| Prévol / géométrie | Contrôles SVG historiques, lots [13](13_VECTORISATION_SVG.md), [14](14_LANGAGE_FABRICATION.md), [15](15_PROFILS_EXPLORE5.md) et [16](16_PATRONS_PARAMETRIQUES.md) | Géométrie ≠ opération ; CUT/SCORE/DRAW/PRINT/FOIL typés ; compatibilité inconnue affichée, pas « compatible » inventé |
| Atelier / interface | G2/G3 et vue Express/Atelier existante, lots [07](07_UX_EXPRESS_NAVIGATION.md) et [18](18_ATELIER_GRAPHIQUE.md) | État projet unique ; sélection par ID ; un seul pinceau, un seul historique de mutation ; préférences UI hors projet |
| Planches / jobs | Fonctions historiques `_make_pages`/`_save_sheet`, mécanismes jobs/cache existants, lot [19](19_PLANCHES_NESTING.md) | `MAX_ITEMS=32` et snapshot V1 borné : **50 instances par lots**, jamais promesse de 50 masques V1 simultanés |
| Distribution | `engine/__init__.py` et installation ComfyUI legacy, lot [21](21_WINDOWS_OFFLINE_RECOVERY.md) | L'initialiseur importe les nœuds historiques : le futur bootstrap autonome devra l'éviter ; ComfyUI reste adaptateur facultatif |

Ces chemins sont **existants et lus** sur `main` pour les modules de projet, identité, import Cricut et initialiseur. Les fichiers d'implémentation futurs, interfaces ou réorganisations **ne sont pas créés par cette roadmap** : les choisir au ticket à partir de l'inventaire courant, avec consommateur identifié, sans doublon de store/queue/export/undo.

## 3. Ordre d'implémentation : huit vertical slices, dépendances minimales

| Slice / priorité d'exécution | Résultat observable et tickets **déjà spécifiés** | Dépendance réellement obligatoire | Ce qui peut avancer en parallèle / ne bloque pas |
| --- | --- | --- | --- |
| **A — G3.3e-b2a, immédiat** | Retouche du vrai sujet, Undo/reload, préservation float32 ; V34-132/133 comme références de conception | Identité G1.2, archive V1, CAS, pinceau existant | **Ne dépend pas** de V2, assistant, ComfyUI autonome, géométrie Cricut |
| **B — quatre sorties, immédiat sur fixtures** | Quatre artefacts distincts, prévol de format et provenance ; V34-005/097/129/130/131 | Exporteurs existants, unités, SVG/XML sûr, publication sans écrasement | IA, Windows natif, V2, G3.3e |
| **C — boîte Score+Cut, en parallèle** | Développé en mm, CUT/SCORE distincts, guide d'affectation et Attacher ; V34-106/107/109/111/126/127/128/130 | Géométrie, profil explicite/UNKNOWN, prévol, guide Design Space | V2, IA, Atelier complet, bootstrap autonome |
| **D — Atelier raccordé** | Sélection des vrais IDs, pinceau partagé, calques et Undo ; V34-032/033/132/133 | V1, identité, CAS, writer existant | Nouveau framework/store/second pinceau |
| **E — planches 12/24/50** | Placement reproductible, rapport par objet, reprise 17/50 ; V34-074/129/134/135 | Instances et lots bornés, empreintes, export sûr | 50 masques V1 simultanés, IA, V2 |
| **F — bibliothèque et CSV** | 105 projets retrouvables, 30 variantes et erreurs par ligne ; V34-131/135/136/137/138 | Projet autorité, index reconstructible, jobs/exports existants | Deuxième base d'autorité, IA, V2 |
| **G — application Windows autonome** | Démarrage sans imports ComfyUI obligatoires, hors ligne, recovery et rollback ; V34-017/019/020/139/140 | Graphe d'imports, sécurité IPC/loopback, qualification Windows | **Ne bloque pas** A–F sur fixtures/composants |
| **H — assistant et IA facultative** | Propositions sûres, consentement, fallback CPU/manuel ; V34-050..067/078..086 | Consommateur réel, licence/hash/consentement, CAS et budget mesuré | Aucun modèle imposé ; aucune dépendance pour A–G |

**Priorité produit :** terminer les engagements V3.3 en cours (A), qualifier les contrats d'export sur fixtures (B) et la boîte (C), puis raccorder les interfaces (D), volumes (E), bibliothèque (F), packaging (G) et IA facultative (H) selon dépendances réellement observées. Cet ordre **n'abaisse ni ne reporte** les obligations V3.3 ; les pistes indépendantes sont parallélisables. Les P0/P1/P2 documentés dans les lots sources restent inchangés.

## 4. Deux parcours de référence complets, sans résultat fictif

### 4.1 Douze escargots → stickers Print Then Cut

1. **Novice :** importer une image autorisée ; choisir « stickers » ; confirmer sujets, format papier et dimensions explicites. **Expert :** contrôler 12 IDs, masques, alpha, contour, marges et placement.
2. Préserver original, identités et masques float32 ; générer 12 instances distinctes et une planche déterministe, sans superposition ni hors-page ; ne pas générer de faux repères de capteur.
3. Publier le **PNG Print Then Cut** avec provenance/SHA et dimensions, sans le confondre avec un SVG Basic Cut ou SVG éditable. Le PNG seul ne certifie ni impression ni découpe.
4. **Design Space (manuel) :** importer le PNG, vérifier dimensions, orientation A4 et version de l'application ; laisser Design Space gérer les repères d'impression. **Physique :** réaliser le coupon sur Explore 5 avec imprimante, tapis, matière, calibration, photos/mesures privées et tolérances annoncées avant essai.
5. **Tests de référence :** `T-V34-22-01/02/05/06/07` et tests ciblés des lots 12, 17, 19. Assertions : 12 IDs uniques, SHA et source inchangés, aucun chevauchement, type d'artefact correct, aucun « PASS Cricut » sans essai. En cas d'échec : conserver projet et export antérieurs, exposer cause/reprise.

### 4.2 Boîte carton 80 × 50 × 30 mm → Score + Basic Cut

1. **Novice :** saisir largeur 80, profondeur 50, hauteur 30 mm et languettes 10 mm ; **expert :** vérifier épaisseur matière, contraintes de pli, segments et choix d'outil (sans inventer une tolérance).
2. Le patron de référence du [lot 16](16_PATRONS_PARAMETRIQUES.md) produit un développé théorique **140 × 110 mm**, un contour extérieur fermé, quatre fentes CUT et huit lignes SCORE. Prévol : unités mm, segments non dupliqués, intersections, bords et profil machine/outils/matière.
3. Exporter une géométrie compatible avec le contrat retenu et **un guide explicite** ; les traits SVG ne transfèrent **pas** automatiquement une opération Score.
4. **Design Space (manuel) :** importer, affecter Score aux lignes concernées, conserver Basic Cut pour les découpes, utiliser **Attacher**, contrôler échelle, outil et alignement. **Physique :** coupon carton, mesures et comportement des plis sur la machine/outils/matière réellement utilisés.
5. **Tests de référence :** `T-V34-22-08/09/10` et tests ciblés des lots 14–17. Assertions : CUT ≠ SCORE, dimensions exactes du modèle théorique, avertissement UNKNOWN si profil non qualifié, aucun succès machine présumé ; rollback vers patron/projet précédent en cas d'échec.

## 5. Plan de qualification sans nouveaux gates

**Auto/CI (sur SHA exact) :** tests ciblés existants `engine/tests/test_project_archive_g13.py`, `test_lossless_masks_g24.py`, `test_project_recovery_g14.py`, `test_v21153_cut_preflight.py`, plus les tests métier créés au fil des tickets. Assertions : ZIP hostile refusé, dernier état sain conservé, float32 bit-à-bit, CAS/concurrence, quatre sorties distinctes, chemins sûrs, 12/24/50 instances par lots, reprise sans doublon.

**UI/Windows :** parcours novice et expert, messages FR actionnables, clavier/focus/zoom, import/export, disque plein, chemins Unicode, sauvegarde et rollback ; démarrage natif hors ComfyUI seulement lorsqu'un package réel existe. **RTX 3070 :** mesurer mémoire, OOM et repli CPU uniquement si fournisseur IA consenti installé et licencié.

**Design Space :** enregistrer version, type d'import, dimensions, orientation A4, opération choisie et capture expurgée. **Physique Explore 5 :** enregistrer machine, outil, tapis, matière, imprimante, calibration, réglages, mesures et critères fixés *avant* l'essai. Une source Cricut officielle qualifie une procédure, **pas** le fichier SmartSVG.

Chaque preuve doit relier `requirement_id → ticket_id → test_id → code_sha → fixture_sha → environnement/version → résultat → axe`. Valeurs possibles `NON_EXECUTE / PASS / FAIL / BLOQUE / NON_APPLICABLE_justifié` par axe. Un `PASS` automatique ne remplit jamais les colonnes Windows, RTX, DesignSpace ou physique. Le présent lot **n'a exécuté aucun test produit, CI, Windows, GPU, Design Space ni physique** ; il ne certifie aucune capacité.

## 6. Risques et arbitrages de mainteneur, sans blocage artificiel

| Risque / décision ouverte | Action proportionnée lors de la slice concernée | Ce qui n'est pas autorisé par ce DRAFT |
| --- | --- | --- |
| V1 borné à 32 masques et ressources ZIP limitées | Lots bornés/exports externes ; évaluer V2 **seulement** si un cas réel exige la migration | Migration silencieuse de projets ou perte float32 |
| Import natif dépendant de `engine/__init__.py` | Spike d'imports et packaging avec preuve Windows ; comparer options après mesure | Choix Qt/Tauri non étayé ou réécriture complète |
| Tolérances Score/Cut et Print Then Cut non mesurées | Coupons et profils versionnés, état UNKNOWN jusqu'à preuve | Certification Explore 5, gravure Maker-only, driver/protocole machine inventé |
| 403 recettes locales sans ticket dans la ligne de test | Associer **au moment du ticket de code** les assertions exactes aux exigences, sans ralentir G3.3 | Déclarer 437/437 tests couverts par exécution ou ajouter un gate documentaire global |
| G6/G9 et benchmarks V3.3 non démontrés par le lot 22 | Conserver propriétaire et recette V3.3 ; rattacher aux PR d'implémentation correspondantes | Suppression/report caché ou « QUALIFIE » par association |
| Modèles IA/licences/VRAM | Catalogue facultatif, vérification licence/version/hash et mesure seulement à l'installation consentie | Téléchargement implicite, modèle imposé, benchmark inventé |
| Branche documentaire en retard de `main` | Relecture SHA et rapprochement séparément autorisé si nécessaire avant promotion | Merge/rebase/activation V3.4 automatique |

## 7. Passation finale et clôture de campagne

**Références de travail :** [index des 24 lots](README.md), [héritage des 141 exigences](HERITAGE_INDEX.md), [lot 23 corrigé : matrice 141↔140 et slices](23_TRACEABILITE_BACKLOG.md), [lot 22 : 14 recettes transversales](22_VALIDATION_CORPUS_PREUVES.md), [journal](PROGRESS.md), [issue #72](https://github.com/frenndak/SmartSVG-Studio/issues/72), [PR #73](https://github.com/frenndak/SmartSVG-Studio/pull/73).

**Prochaine action d'ingénierie :** reprendre le vrai G3.3e-b2a (issue #71) et les tests de fichiers B/C sur fixtures, sans attendre promotion V3.4. Pour chaque PR future : relire `main`, réutiliser le code, sélectionner un ticket déjà spécifié, écrire assertions + lien exigence, exécuter les tests disponibles, préserver rollback et qualifier séparément les axes matériels affectés.

**Ce qui est clos :** les **24 lots de conception** et la réconciliation des identifiants de traçabilité. **Ce qui reste ouvert :** preuve fine des 403 recettes, essais et licences matérielles/IA, arbitrages d'architecture et éventuelle promotion V3.4. La V3.4 n'est **ni implémentée, ni active, ni certifiée**. Aucune 25e tranche, aucune nouvelle tâche, aucune fusion et aucune modification de la roadmap V3.3.
