# SmartSVG V3.5 — COV-18A-3a : six fonctions UX, revue contradictoire des critères historiques

**13 novembre 2026 — CANDIDAT, NON NORMATIF.** Complète [COV18A2C](COV18A2C_LOCAL_DOD_SIX.md) et [COV18A2D](COV18A2D_ARCHITECTURE_ARBITRATION.md). Ce lot examine **A01, A05, A06, A07, A09, A10** (6/24 autres A/B). Les libellés UX source proviennent de [#134](https://github.com/frenndak/SmartSVG-Studio/issues/134) et de [COV17A](COV17A_UX_A01_A16_SEMANTIC_AUDIT.md). La V3.4 reste la roadmap normative, les **six décisions ci-dessous ne sont ni adoptées ni certifiées**.

**Sources comparées :** `docs/ROADMAP_HERITAGE_v3_3.md` (blob `c310adf3e972638c5a67332719bb2105ec37e688`), `docs/ROADMAP_TRACEABILITY_v3_3.md` (`a56edf8b2791590464a600627fbd3efdf27b9d28`), `docs/roadmap-v3.4/23_TRACEABILITE_BACKLOG.md` (`177a0ecff5edd816e1bf879fc93c2a49efd83690`) et lots 05/10/12/13/14/18/21 à `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`. Les chemins sont des références source, pas des promesses d'API implémentées.

## 1. Confrontation des six propositions à la réalité des obligations

| UX candidate et besoin original | Critère historique intégral, dépendances et rattachements V34 source | Contre-expertise : ce que cela **ne démontre pas** | Décision / prérequis de clôture |
|---|---|---|---|
| **A01 — Smart Import** : PNG/JPEG/WebP/SVG et lots sûrs | **S-061 (P0/G1.4)** : « Tests fichiers hostiles et bombes XML/ZIP » ; preuve « aucune sortie hors projet ni épuisement incontrôlé ». **S-052 (P0/G1.2)** : modèle Source/Subject/Artifact, « rotations/crop/alpha testés ». Lot 23 : S-061→V34-025/139, S-052→V34-025/028/018/026. | Un `native_project_create_v34.py` PNG V1 **ne** prouve pas JPEG/WebP/SVG natif, orientations EXIF ou import multi-lot. V34-139 porte sur distribution/rollback Windows, **pas** sur un parseur de tous les formats adversariaux. | **RACCORDER / P0**, mais créer des contrats d'admission *distincts*, puis preuves par format et rejet de fichiers malicieux. Une image SVG chargée comme source ne devient pas automatiquement un contour CUT. |
| **A05 — Affinage Smart Select** : lissage, dilatation/érosion, îlots, bord local | **S-080 (P1/G2.3)** : « Pinceau correction tactile souris + aperçu effet », « undo, zoom et sauvegarde sans incohérence ». **S-015 (P1)** : « Nettoyage des halos / découpe et offset », dépend S-008/S-009, critère « comparatifs zoom ». Lot 23 : S-080→V34-133 ; S-015→V34-088/095/076. | Le pinceau `strokes.py` et des masques float32 ne donnent pas à eux seuls un algorithme de morphologie fiable ni les opérations booléennes. Le DoD de V34-133 concerne surtout propriétés/visibilité et clavier. | **AMÉLIORER / P1** : brouillon sur masque, préservation trous/IDs, Undo réversible, comparatifs avant/après à grossissement réel ; les outils morphologiques non démontrés doivent avoir leurs critères propres. |
| **A06 — Smart Clean détourage** : fond retiré/alpha correct | **S-014 (P1)** : « Segmentation objets et fragments associés », dépend S-005/S-006, critère « suites multiobjets ». Lot 23 : V34-073, T-V34-22-12. | La liaison d'accessoires V34-073 prouve au mieux des relations réversibles ; elle **ne démontre pas** un alpha matting précis, ni une coupe physique. Des propositions `auto_masks_v2111` non validées ne sont pas un détourage certifié. | **RACCORDER / P0 au niveau UX**, sans hausser artificiellement S-014 historique de P1 : source intacte, alpha dérivé, rejets du fond capturé comme sujet, comparaison avec truth synthétique. |
| **A07 — Nettoyage anti-halo** : RGB et bords sans artefact | **S-015 (P1)** : « comparatifs zoom » ; tickets V34-088 (alpha composition vs Cut), V34-095 (comparatif rendu imprimé), V34-076 (pixel 1:1). | Un dérivé `auto_hd` qui conserve alpha peut quand même laisser une frange RGB ; inversement un nettoyage RGB peut perdre des micro-îlots. Le test d'alpha seul ne vaut pas jugement colorimétrique ou physique. | **AMÉLIORER / P1** : contrôles RGB aux frontières, alpha/masque séparés, diff à 100 %, couleur de fond noir/blanc/damier, aucune suppression silencieuse de contours CUT. |
| **A09 — Contrôle visuel** : transparence/diff/zoom 100 % | **S-073 (P0/G2.8)** : « Aperçus original/masque/coupe séparés », critère « Dimensions constantes, aucune inversion confondue ». Lot 23 V34-091/095, T-V34-22-05. | Un simple panneau aperçu PNG ne prouve ni une vue géométrique en mm, ni un véritable pixel 1:1 à DPI 200 %, ni la distinction original / masque / prévol Cut. | **RACCORDER / P0**, trois vues sémantiques distinctes et synchronisées, checksum/ID/révision affichables à l'expert ; aucun geste de preview ne modifie le projet. |
| **A10 — Smart Color** : pipette, palette, recoloration et dégradés | **S-011 (P0)** : « Fidélité SVG multicouche et analyse des formes », dépend S-006, critère « mesures render standard ». **S-060 (P1/G5.1)** : « Score qualité séparé silhouette/couleur/géométrie », critère « benchmark reproductible/échantillon fixé ». Lot 23 : S-011→V34-098/099/103, S-060→V34-101/109. | **Point de risque** : S-060 est une obligation de **mesure**, non un ticket de pipette ou d'édition de dégradé. Une palette k-means / SVG groupé par couleurs ne démontre aucune interaction de recoloration Windows et ne doit pas transformer une couleur écran en matériau CUT. | **RAFFINER / P1** : palette source/dérivée non mutante, pipette à coordonnées définies et undo, profils couleur explicites, métriques séparées silhouette/couleur/géométrie ; tests de gradient et alpha avant certification. |

**Statuts source :** les priorités P0/P1 des exigences héritées et les décisions UX V3.5 sont **deux attributs indépendants**. Les mentionner ensemble ne remplace pas les P0/P1 d'origine. Les références de tickets sont des **liens de planification du lot 23**, pas une preuve d'un test exécuté.

## 2. DoD locaux vérifiés et rôles sans doublon

| Ticket existant | Source exacte / preuve prévue dans le ticket | Réemploi candidat |
|---|---|---|
| `V34-025` | [Lot 05](../roadmap-v3.4/05_PROJECT_SCHEMA.md) L210 : inventaire contrat V1, tests `T-V34-05-01,05..08` ; SHA fixtures et source intacte | A01 comme entrée sûre, jamais ajout automatique de formats |
| `V34-139` | [Lot 21](../roadmap-v3.4/21_WINDOWS_OFFLINE_RECOVERY.md) L77 : distribution Windows/rollback, tests `T-V34-21-02/04/05/06/07/10` | A01 = dépendance d'installation, **pas** owner du parseur SVG |
| `V34-073` | [Lot 10](../roadmap-v3.4/10_ANALYSE_VISUELLE.md) L230 : accessoires réversibles, `T-V34-10-15/20` | A06 conserve relation objet/fragment, matting séparé |
| `V34-076` | [Lot 10](../roadmap-v3.4/10_ANALYSE_VISUELLE.md) L233 : inspection pixel 1:1, `T-V34-10-15/16/27/28` | A05/A07/A09 réemploi de l'inspection, sans mutation |
| `V34-088` | [Lot 12](../roadmap-v3.4/12_RASTER_PIPELINE.md) L164 : alpha composition ≠ Cut, `T-V34-12-06..10/16..20` | A05/A07 protège la coupe pendant nettoyage couleur |
| `V34-091` | [Lot 12](../roadmap-v3.4/12_RASTER_PIPELINE.md) L167 : diff novice/expert clavier, `T-V34-12-08/10/12/13/27` | A09 prévisualisation sans faux état de QA |
| `V34-095` | [Lot 12](../roadmap-v3.4/12_RASTER_PIPELINE.md) L171 : comparatif franges/seuils `T-V34-12-06/09/11/12/17/20/27` | A05/A07/A09, **aucun score physique inventé** |
| `V34-099` | [Lot 13](../roadmap-v3.4/13_VECTORISATION_SVG.md) L221 : couches éditables/palette `T-V34-13-11..13/18` | A10 groupe artistique, pas opération CUT |
| `V34-101` | [Lot 13](../roadmap-v3.4/13_VECTORISATION_SVG.md) L223 : profils Basic/MultiCut `T-V34-13-14..18/20/26/27` | A10 dépendance aval, quatre exports préservés |
| `V34-109` | [Lot 14](../roadmap-v3.4/14_LANGAGE_FABRICATION.md) L257 : prévol PASS/WARN/BLOCKED `T-V34-14-03..11/18/19/24/30` | A10 score utilisateur ≠ QA de coupe |
| `V34-133` | [Lot 18](../roadmap-v3.4/18_ATELIER_GRAPHIQUE.md) L112 : propriétés/couches dérivées, tests `T-V34-18-07..09` | A05 UI peut consommer les previews, pas les sérialiser en V1 |

## 3. Contrat d'interaction et négatifs — spécification candidate

**Workflow novice A01→A06→A05→A07→A09→A10 :** import selon format réellement supporté → vérification de l'orientation/alpha → propositions de masque → suppression du fond en brouillon → nettoyage visuel réversible → vues original/masque/coupe séparées → recoloration facultative → prévol par rôle → sauvegarde CAS et export explicite. Les étapes non disponibles dans Windows ne doivent pas apparaître comme prêtes.

**Workflow expert :** inspecter `source_sha/subject_id/mask_id/expected_revision`, float32, mesures RGB/alpha aux bords, 1 pixel source = 1 pixel affiché en mode 100 %, unités mm/ppi, rapport de QA indépendant ; correction manuelle / repli CPU plutôt qu'un téléchargement IA silencieux.

**Négatifs reproductibles, NOT_RUN :**
1. SVG import contenant des entités externes ; ZIP/EXIF malformés ; image dépassant quotas → rejet borné et aucune source persistée.
2. Fond blanc photo présentant un faux sujet dominant → revue, jamais confirmation auto.
3. Nettoyage d'un bord translucide détruisant un trou ou micro-îlot → rollback et affichage diff.
4. Job asynchrone calculé sur un ancien `project_sha` → `STALE`, pas d'écriture.
5. Aperçu 100 % DPI 200 % trompeur → contrôle d'échelle à l'écran, sans promesse fausse.
6. Recoloration avec profil ICC inconnu ou dégradé aplati → état `UNKNOWN` / avertissement et source intacte.
7. Panne disque, permissions, fermeture ou Undo au moment du commit → sauvegarde refusée, archive précédente intègre, retour réouvrable.
8. IA refusée/OOM/modèle non licencié → mode manuel/CPU, aucun réseau ni résultat « équivalent » imaginé.

**Tests ultérieurs par axe :** contrat auto CPU et fixtures synthétiques → Windows Tk 1366×768/DPI 200 %, clavier/focus/motion réduit → modèles IA locaux (consentement/VRAM/versions) si concernés → Design Space pour sorties de fabrication → coupe physique uniquement pour contrôle matière/coupe. Mesures p50/p95, RAM/VRAM et delta visuel **à collecter**, aucun seuil inventé. La publication de cette fiche n'exécute aucune de ces étapes.

## 4. Revue contradictoire et suite

- **Corrigé conceptuellement** : S-061 ≠ support universel des quatre formats d'import ; S-060 ≠ outil Pipette ; S-014 ≠ détourage alpha complet ; V34-139 ≠ moteur d'admission SVG.
- **Conservé** : toute la portée A01–A16/B01–B14 du registre #134, les 24 lots, 141 exigences, 140 tickets et 437 scénarios hérités ; 431/437 liens historiques sans réétiqueter des tests PASS.
- **État de certification** : **0/6** fonctions prêtes à coder du seul fait de ce document, faute d'ADR/DoD complets et preuves UI/Windows/Design Space/physiques. La V3.4 reste active.
- **25 axes qualité** : normes/héritage, un projet V1/CAS, séparation raster/vecteur et quatre exports, UX novice/expert, erreurs/rollback, IA opt-in/licences, offline/security, cas négatifs, Windows/accessibilité, no-merge et gouvernance préservés. Smart Delivery, QR/CSV et diorama sont hors périmètre de ces six IDs, **non abandonnés**.

**Prochaine étape COV-18A-3b :** revoir les six IDs suivants **A11, A13, A14, A15, A16, B01** sur les vrais critères/ports/DoD, en tenant compte des divergences A16 déjà signalées ; ne pas refaire COV17A ou les arbitrages A02–B09.
