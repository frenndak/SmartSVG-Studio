# SmartSVG Studio V3.4 — Lot 19/24 : planches 12/24/50, placement, cache et reprise

**DRAFT de conception, 29 octobre 2026.** V3.3 demeure **ACTIVE** ; lot documentaire sur la branche `codex/docs-roadmap-v3-4-campaign`, PR draft #73, issue #72. Aucun changement de code, d'archive V1, de workflow ou de périmètre. **Tous les tests ci-dessous : NON_EXECUTE.**

## 1. Besoin approuvé et trois écarts vérifiés dans le code

**Périmètre existant :** V3.3 `P04`, `F11`, `F12`, `S-018`, `S-062`, `S-089`, `S-090`, `R33-011/012/026/031` : sélectionner, dimensionner, placer, verrouiller, comparer deux dispositions, répartir 12/24/50 sujets, économiser la matière, reprendre les lots, produire un rapport par objet. Aucun algorithme optimal universel, aucun nouveau mode de fabrication.

1. **Plafonds différents selon les modules :** `multi_subject_v21.py` et `auto_masks_v2111.py` plafonnent à **32 masques** et **50 M valeurs** ; `mask_snapshot_g24.py` plafonne à **8 M valeurs float32**, tandis que `direct_import_v218.py` et `auto_hd.py` limitent leurs entrées à **32 objets**. `white_sheet_v21152.py` accepte des grilles **12 ou 24**, mais construit encore un tenseur de masques pleine image. **Correction :** 50 objets = 50 *entrées logiques* traitées par lots bornés, jamais un tenseur 50×H×W, et jamais un snapshot V1 invalide.
2. **Placement existant non équivalent à un nesting généralisé :** `multi_subject_v21._make_pages` choisit au plus 12 objets candidats par page, une grille de colonnes, des bornes **170×240 mm indicatives** et un espacement 3 mm ; `hd_multisticker_v206._save_sheet` compose selon la largeur/hauteur maximales d'une cellule. `engine_v9._adaptive_compose` réduit une bordure pour préserver le nombre d'îlots, mais **ne repositionne pas** les sujets. **Correction :** conserver ces moteurs comme référence/fallback ; concevoir un placement déterministe sur empreintes de découpe validées, sans confondre réduction d'offset et déplacement.
3. **Le rapport historique n'est pas un journal de reprise complet :** `_make_pages` renvoie `ELEMENT_TROP_GRAND` et `elements_restants` puis arrête la composition ; `prepare_cricut_import` refuse plus de 32 objets dans un rapport. **Correction :** état explicite par objet et par page, avec `SKIPPED/FAILED/RETRYABLE`, conservation des SHA et reprise sans doublons ; la compatibilité V1 reste bornée, sans ajout de champs arbitraires.

**État prouvé :** présence et limites des fonctions ci-dessus dans `main@fdbda304beb77d97340a8be4dd5c5e9cefde15f4 (ancêtre commun de la PR : fff374e5147689165839bd76e742713d714ff147)` ; `Subject` G1.2, `project_archive.py` et `project_recovery.py` existent. **Non prouvé :** algorithme de nesting V3.4, reprise 50 sujets, qualité d'occupation, compatibilité réelle A4/Design Space/Explore 5, mémoire Windows ou RTX 3070. Les « 12 escargots » de la maquette Atelier sont fictifs, pas un corpus validé.

## 2. Contrat de planche minimal, sans deuxième autorité

- **Entrées :** snapshot projet `.smartsvg` vérifié (`project_sha256`, `source_id`, `subject_id` stables, masques/contours approuvés, SHA des ressources), contrat de sortie parmi les **quatre contrats du lot 17**, dimensions **mm connues** des motifs, orientation autorisée, quantité, matière/opération du lot 14 et profil du lot 15. Les fichiers PNG individuels peuvent aussi être utilisés comme fixtures d'export **sans prétendre** qu'ils créent des `Subject` persistants.
- **Données éphémères :** sélection UI, positions en mm, rotations, placements verrouillés, ordre des candidats, pages et brouillon de comparaison. Une modification durable passe par le writer/CAS déjà prévu ; ne pas injecter `sheet_layout`, `job_history` ou 50 masques dans `smartsvg-project/1`. Le **manifeste de sortie externe** décrit les résultats publiés ; il n'est ni un deuxième projet, ni un journal d'édition faisant autorité.
- **Empreinte physique :** calculer la géométrie extérieure **CUT effective après offset** ou l'alpha final de coupe pour Print Then Cut, pas seulement la bbox de la texture. Vérifier trous, îlots, doubles coupes et échelle avant placement. Une bbox élargie avec marge est un filtre conservateur possible ; elle ne prouve pas l'absence de collision des vrais contours sans prévol.
- **Profil de page :** dimensions du support, unités, marges/zone utilisable et version de profil explicites. `UNKNOWN` pour une zone Print Then Cut réelle non qualifiée : produire une **composition indicative à vérifier dans Design Space**, jamais une certification « tient sur A4 ». Les opérations CUT/SCORE/DRAW/FOIL restent sémantiques, avec transfert manuel décrit aux lots 14–17.
- **Provenance :** `project_sha256`, empreintes individuelles, version de l'algorithme, paramètres de placement, version du profil et SHA des exports. Les placements verrouillés sont référencés par `subject_id` (ou ID d'instance stable en cas de copies), jamais par index de vignette. L'empreinte du cache comprend aussi **rotation, offset, dimensions mm, DPI, opération et profil**.
- **Déterminisme :** même snapshot, même profil, même liste d'instances et même graine fixée ⇒ mêmes positions/pages/ordre et mêmes diagnostics ; ne pas promettre des PNG bit-à-bit identiques si les métadonnées ou encodeurs diffèrent sans test.

## 3. Parcours, UI et dépendances minimales

**Novice — 12 escargots → stickers :** Importer → diagnostic réel ou sélection manuelle → revue des contours → « Planche » → taille et support → « Disposer » → aperçu avec nombres **12 retenus / 0 bloqué** seulement si effectivement mesurés → « Vérifier » → PNG Print Then Cut et guide du lot 17. Si l'image est la **démo des escargots**, afficher « Démonstration — non exportable » tant qu'aucune donnée réelle n'est raccordée. En cas de zone A4 inconnue : « Aperçu indicatif, vérifier la disposition et les dimensions dans Design Space ». Ne jamais superposer le SVG de contrôle au PNG Print Then Cut.

**Novice — boîte 140×110 mm :** les cinq chemins CUT et huit SCORE du lot 16 sont **un patron indivisible**, non treize stickers. La planche respecte son enveloppe et les unités ; l'utilisateur doit encore sélectionner Score puis **Attacher** dans Design Space. Si le patron dépasse le support, avertir et refuser le placement au lieu de le réduire sans accord.

**Expert — 24/50 sujets :** filtre par matière/opération, autorise explicitement des rotations compatibles, verrouille certains placements, compare A/B sans déplacer les verrous, visualise collisions et taux d'occupation **indicatif** (aire occupée/aire de zone déclarée), suit la file `DONE/PENDING/FAILED` par instance, interrompt puis reprend sur le même snapshot. Un changement de SHA/profil/paramètres invalide les résultats réutilisables, sans rebind par ordre.

```text
[Atelier > Planches]  Projet SHA…  [12 | 24 | 50 objets]  [Support ▾] [mm]
[Objets : 12 sélectionnés] [Disposition A / B] [Verrouiller] [Rotation autorisée ▾]
[Page 1 / N : aperçu]  [Collision: 0 / À vérifier]  [Zone: indicative / qualifiée]
[Disposer] [Comparer] [Annuler le brouillon] [Exporter…]
[Job : 12/50 terminés · 1 à revoir · 37 en attente] [Pause] [Reprendre]
[Erreur : sujet trop grand / profil inconnu / projet modifié] [Corriger] [Détails]
```

**Obligatoire pour le calcul :** géométries de coupe, mm, contrôle des collisions, stabilité des verrous, état du snapshot. **Parallélisable :** QA/export des PNG/SVG sur fixtures, UI, lot G3.3e-b2a, optimisation de la mémoire. **Non prérequis pour la première planche :** IA, RTX, ComfyUI autonome, assistant, V2 et bus de commandes universel. **Pour la persistance de 50 sujets en projet unique**, la migration/schéma V2 et les budgets d'archive restent à qualifier ; ne pas dissimuler cette limite sous un manifeste externe.

## 4. Algorithme déterministe et ressources (spécification, NON implémenté)

1. Valider le SHA du projet, la liste d'instances et leurs sources, mm, contour/alpha final, opération et profil. Classer `READY`, `NEEDS_REVIEW` ou `BLOCKED`. Ne pas inventer de taille depuis des pixels sans échelle connue.
2. Construire des **empreintes de coupe bornées** par objet. Vérifier l'offset, l'absence de double coupe et les dimensions. Regrouper par support/opération compatibles ; les patrons multi-opérations restent groupés. Rejeter les groupes incompatibles sans les fusionner.
3. Réserver d'abord les placements verrouillés ; les refuser s'ils sont hors zone, se chevauchent ou ont un profil périmé. Placer les autres par heuristique déterministe *first-fit* triée (aire décroissante puis ID stable), rotations **explicitement permises** seulement, contrôle final des empreintes avec marge. Préserver une option « grille historique » si l'heuristique n'améliore pas le résultat ou échoue.
4. Décomposer en pages successives ; si aucun objet restant ne tient, **signaler l'ID et la raison** et continuer avec les autres lorsque c'est sûr, sans boucle infinie. La composition `_save_sheet` peut servir de backend de grille ; ne pas la qualifier de nesting polygonal. Les résultats de placement doivent être vérifiés **après rasterisation** (alpha/îlots) et par prévol des SVG, pas seulement en coordonnées mm.
5. Émettre un résultat par instance (`PLACED`, `BLOCKED`, `FAILED`, `PENDING`), un résultat par page, les compteurs et SHA. Préparer les sorties dans un dossier temporaire ; publier les pages validées et le manifeste **en dernier** selon le lot 17. Ne pas effacer un export antérieur.
6. Sur pause/OOM/arrêt : arrêter aux frontières d'objets/pages, libérer les buffers, conserver uniquement les résultats vérifiés et un état de reprise **temporaire privé** avec digests. Reprise uniquement sur SHA/paramètres/profil identiques ; sinon `STALE_RESTART_REQUIRED`, sans doublon ni écrasement. Un cache supprimé n'invalide jamais le projet : recalcul.
7. **Budgets :** ne garder en mémoire qu'un lot limité de ROI/empreintes et une page de rendu à la fois ; ne jamais matérialiser 50 masques pleine image. Décharger le fournisseur IA facultatif avant composition CPU si nécessaire. Mesurer p50/p95, pic RAM/VRAM, nombre de pages, taux d'occupation et temps de reprise ; **aucun seuil chiffré fictif**.

**Réutilisation :** `multi_subject_v21._make_pages`, `hd_multisticker_v206._save_sheet`, `production_v211._remake_pages`, `engine_v9._adaptive_compose` (offset seulement), `direct_import_v218.prepare_cricut_import` (prévol et guide, plafond actuel 32), `project_workspace_g22.py`/`project_recovery.py` (CAS/rollback), `Subject` G1.2, lot 14 (opérations), lot 15 (profils), lot 17 (exports). Le cache est dérivé ; réutiliser V34-093, les jobs V34-074 et les ROI V34-070 : **pas de deuxième queue, cache, writer, prévol ou exporteur**.

## 5. Cas limites, erreurs et rollback

| Cas | Résultat obligatoire / message FR |
|---|---|
| 50 objets mais module legacy limité à 32 | « Traitement réparti en lots » ; aucune troncature, aucun appel 50×H×W ; rapport total 50 |
| Objet trop grand, taille mm inconnue ou profil non qualifié | `BLOCKED` ou `NEEDS_REVIEW` avec ID ; « Vérifier la taille et le support » ; ne pas réduire automatiquement |
| Alpha/coupe change après placement, marge fusionne deux îlots | Invalider le placement et recalculer ; « Contours se touchent, corriger l'espacement » |
| Placement verrouillé hors zone / collision | Conserver le verrou, ne pas le déplacer ; proposer de le déverrouiller ou changer de support |
| Source/SHA ou profil modifié, réponse de job tardive | `STALE_RESTART_REQUIRED`, aucun export de résultats périmés, pas de commit projet |
| Pause, OOM, cache corrompu, disque plein, collision de nom | Ne pas annoncer `DONE` ; conserver projet et ancien export, nettoyer les temporaires non prouvés, reprendre seulement les unités vérifiées |
| Deux pages dont la seconde échoue | Aucun manifeste final « succès total » ; signaler `PARTIAL` et permettre la reprise contrôlée |
| PNG Print Then Cut, SVG Basic Cut, multicouche, édition | Quatre choix distincts, jamais un SVG de diagnostic présenté comme seconde coupe ni `Artifact.use` V1 étendu implicitement |

**Sécurité :** bornes sur nombre d'objets, chemins, pixels, taille de pages et répertoire ; aucun chemin client arbitraire, aucune donnée privée dans les journaux publics. **Rollback :** retour à la grille historique, exports individuels et revue manuelle, sans mutation des sources ni des masques float32.

## 6. Recette proposée — toutes les assertions NON_EXECUTE

| Test | Assertion exacte attendue | Preuve future |
|---|---|---|
| T-V34-19-01 | 12 sujets synthétiques validés : 12 instances uniques dans les pages et le rapport, aucune démo fictive exportée | auto/UI |
| T-V34-19-02 | 24 sujets : aucune collision de contours de coupe, aucun hors-zone sur support **qualifié**, IDs et dimensions conservés | auto/QA |
| T-V34-19-03 | 50 instances : 50 statuts individuels sans troncature, traitement par lots ; pic de masques actifs borné | auto/Windows mémoire |
| T-V34-19-04 | Même snapshot/paramètres : placements, pages, erreurs et ordre identiques ; ordre des vignettes modifié sans effet | auto |
| T-V34-19-05 | Deux placements verrouillés inchangés après recalcul ; conflit de verrou signalé sans déplacement silencieux | auto/UI |
| T-V34-19-06 | Rotation interdite, groupe Score+Cut ou texte orienté : aucun pivot implicite ni séparation des opérations | auto/UI |
| T-V34-19-07 | Zone A4 Print Then Cut inconnue : aucune mention « compatible/garanti » ; PNG et guide distincts du SVG Cut | auto/UI puis DesignSpace |
| T-V34-19-08 | Après changement d'offset/masque/échelle/profil/SHA, cache et planche périmés refusés ; projet intact | auto/concurrence |
| T-V34-19-09 | Pause après 17/50 puis reprise : 50 états finaux, 0 instance traitée deux fois dans le manifeste publié | auto/fault-injection Windows |
| T-V34-19-10 | OOM simulé ou disque plein à la page 2 : ancien paquet intact, état PARTIAL explicite, reprise vérifiée | auto/fault-injection |
| T-V34-19-11 | Projet V1 incapable de persister 50 masques float32 : refus explicite ; exports externes bornés possibles sans falsifier V1 | auto |
| T-V34-19-12 | UI clavier : sélectionner/verrouiller/comparer/corriger/reprendre avec focus et annonces FR ; Design Space/Explore 5 restent NON_EXECUTE sans preuves séparées | UI/Windows ; DesignSpace/physique séparés |

**Fixtures publiques à produire au développement :** formes géométriques synthétiques (12/24/50), formes avec trous, rotations interdites, deux masques chevauchés, deux sujets sur un même contour, un patron boîte 140×110 mm CUT+SCORE, faux OOM/panne disque, reprise à 17/50, profil A4 `UNKNOWN`. Aucune œuvre tierce ni photo privée. **Ne pas confondre** tests de calcul, UI, Windows, Design Space et essais physiques.

## 7. Backlog minimal, dépendances et Definition of Done

Les tickets existants **restent propriétaires** de leurs responsabilités : V34-070 (ROI 12/24/50), V34-074 (jobs/OOM/reprise), V34-093 (cache), V34-090 (prévol raster), V34-107/114 (résolveur/prévol de fabrication), V34-129/131 (exports et provenance), V34-132/133 (état Atelier et calques). **Ne pas créer de ticket pour une seconde queue/cache ni pour une IA de placement.**

| Ticket nouveau | Priorité / dépendances minimales | Livrable pressenti (NON existant), tests, preuve et DoD |
|---|---|---|
| **V34-134 — placement et comparaison de planches** | **P1** ; S-089/090, R33-026/031 ; réemploi `_make_pages`/`_save_sheet`, géométrie du lot 13, opérations 14, profil 15 ; V34-100/107/129 seulement pour l'export final correspondant | Adaptateur de placement léger dans `engine/smartsvg_cricut/` et vue Atelier existante, **pas** de nouveau moteur de rendu ; T01/02/04/05/06/07 ; preuves auto+UI, DesignSpace distincte ; DoD aucune collision/hors-zone pour profil qualifié, verrous stables, rotation consentie, comparatif reproductible ; rollback grille historique |
| **V34-135 — orchestration bornée de 12/24/50 et raccord export** | **P1** ; S-018/062, R33-011/012/026/031 ; V34-070/074/093 pour les traitements et le cache, V34-129/131 pour la publication ; V34-134 pour l'optimisation de placement **mais pas** pour exporter les PNG individuels | Raccordement aux jobs/export existants dans `engine/smartsvg_cricut/` et tests de reprise, **pas** de queue parallèle ; T03/08/09/10/11/12 ; preuves auto/fault-injection, Windows mémoire ; DoD 50 statuts sans perte ni doublon, aucun snapshot V1 invalide, SHA de reprise contrôlé ; rollback lots ≤32 et exports individuels explicites |

**Ordre de vertical slices :** (A) 12 PNG sur grille existante + prévol/guide (fixtures, indépendant de G3.3e) → (B) placement/rotation/verrous/24 → (C) 50 objets par lots + reprise et rapport → (D) qualification Windows/Design Space/physique par profil. Le ticket 135 peut préparer son manifeste/reprise sur **fixtures indépendantes** pendant que 134 traite le placement. Aucun gate V3.4 ajouté au développement G3.3e-b2a.

**Mapping local bidirectionnel :** T01/02/04/05/06/07 → V34-134 ; T03/08/09/10/11/12 → V34-135 ; V34-134 → S-089/090, R33-026/031, T01/02/04/05/06/07 ; V34-135 → S-018/062, R33-011/012/026/031, T03/08/09/10/11/12. La matrice **globale** 141 exigences ↔ tickets/tests sera auditée au lot 23 ; aucune suppression historique.

## 8. Sources, risques ouverts et suite

- Code réel relu sur `main@fdbda304beb77d97340a8be4dd5c5e9cefde15f4 (ancêtre commun de la PR : fff374e5147689165839bd76e742713d714ff147)` : `engine/multi_subject_v21.py`, `hd_multisticker_v206.py`, `production_v211.py`, `engine_v9.py`, `smartsvg_quality/white_sheet_v21152.py`, `smartsvg_ai/auto_masks_v2111.py`, `smartsvg_core/mask_snapshot_g24.py`, `smartsvg_cricut/direct_import_v218.py`, `smartsvg_core/project_contracts.py`. La limite 32 n'est **pas** une limite Cricut officielle.
- Source Cricut officielle vérifiée le **29/10/2026** : [Explore 5 — Print Then Cut](https://help.cricut.com/hc/en-us/articles/38613592650903-How-to-Print-Then-Cut-with-Cricut-Explore-5) : placement A4 sur tapis en paysage, contrôle dans Design Space, impression et découpe dans une même session ; la page ne certifie pas la zone de nesting SmartSVG. [Explore 5 — Scoring Tool](https://help.cricut.com/hc/en-us/articles/38613473602455-Cricut-Explore-5-How-to-use-the-Scoring-Tool) : Score et Attacher manuels.
- **Risques ouverts :** forme réelle de la zone Print Then Cut selon version/support, limites de ressources V1, performance 50 instances, exactitude des placements après rasterisation, collision multi-opération, transactions multi-fichiers, benchmarks et qualification terrain. Aucun test V3.4, Windows/RTX, Design Space ni Cricut physique exécuté par cette rédaction.
- **Prochain lot 20 :** bibliothèque, modèles et variantes/CSV déjà prévus ; index reconstructible depuis le projet, sans autorité parallèle ni nouvelle fonctionnalité.
