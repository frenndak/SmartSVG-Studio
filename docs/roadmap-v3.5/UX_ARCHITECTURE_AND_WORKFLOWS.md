# SmartSVG V3.5 — Architecture UX complète et 80 capacités héritées : parcours, contrats et tests

**Statut : V35-COV-12 / SPÉCIFICATION UX CANDIDATE, NON NORMATIVE — 13/11/2026.** Il ne s'agit ni de 80 outils livrés ni de 80 tickets nouveaux. Les libellés sont repris **sans omission** de l'issue [#134](https://github.com/frenndak/SmartSVG-Studio/issues/134). La V3.4 demeure active ; aucune interface Windows/RTX/Design Space/coupe physique n'a été testée pendant cette rédaction.

**Liens :** [backlog et graphe](BACKLOG_AND_DEPENDENCIES.md) ; [COV10C ports réels](COV10C_V1_TEXT_EXPORT_PORTS.md) ; [héritage 24/141/140/80](INHERITANCE_REGISTER.md) ; [tests 437](SCENARIOS_V34_INDEX.md) ; [25 critères anti-perte](AUTOMATION_QUALITY_CONTRACT.md).

## 1. Architecture d'interface — une seule application, trois profondeurs

**Base vérifiée :** `engine/standalone_desktop_v34.py` utilise une seule fenêtre Tk et `NativeAppShell` ; pages Accueil, Projet, Fabrique, Apparence, Atelier. Les traitements `ManagedWorkspace`, `project_archive`, `project_recovery` et les panneaux Atelier/viewport existants doivent être réemployés. La barre d'actions ci-dessous est un **projet de conception**, pas une capture de l'interface déjà disponible.

**Mode Express (débutant).** Une intention à la fois — `Sticker`, `Découpe vinyle`, `Création libre`, `Carte/boîte` — avec un parcours guidé et une explication du type d'export. Afficher "Non pris en charge" quand la capacité n'est pas raccordée, jamais un bouton factice ou un « prêt à découper » sans preuve.

**Atelier (usage régulier).** Un seul canevas et une barre contextuelle évolutive qui expose sélection, objets, masque, couleur, courbes, texte, calques, historique et Prévol sans 80 boutons simultanés. Les outils de retouche agissent sur le brouillon; un commit n'est possible qu'avec le projet V1 sain et la révision CAS conservée.

**Expert.** Inspecteur de propriétés, IDs stables, source SHA, dimensions mm, profils UNKNOWN/KNOWN, aperçu topologique, gestion des couleurs/profils/licences/erreurs, choix de l'export et rapport QA détaillé. **Expert ne doit pas être une autre application ni un writer distinct**.

### Modèle de navigation candidat

```text
[SmartSVG]  [Accueil] [Atelier] [Fabrique] [Bibliothèque]     Projet: …@SHA [Sain/Modifié/Conflit]
[Importer]  [Texte] [Objets] [Vectoriser] [Exporter]         [Undo] [Redo] [Aide]
┌───────────────┬─────────────────────────────────────┬──────────────────┐
│ objets/calques│ CANEVAS / source / masque / vecteur │ propriétés outil │
│ ou projets    │ (Zoom, Pan, lasso, poignées, overlays)│ taille mm/QA      │
│ dépliable     │ Barre contextuelle au bas du canevas│ avant/après      │
└───────────────┴─────────────────────────────────────┴──────────────────┘
État : « Brouillon non enregistré » / « Projet sain » / « Prévol à vérifier »
[Valider modification] [Exporter un fichier] [Préparer un pack] si disponibles
```

**Barres d'espace** : sous 1366×768 et DPI 200 %, rétracter le volet droit, maintenir visibles état du projet et action principale, ne jamais masquer la correction ou l'annulation. Mesure Windows Tk réelle obligatoire avant de valider cet agencement.

## 2. Huit parcours de bout en bout (E2E) et limites prouvables

| Parcours | Flux novice concret → résultat honnête | Étapes expertes, récupération et garde-fous |
|---|---|---|
| **UX-FLOW-01 Source → Sticker** | Import PNG/JPEG/WebP/SVG (selon producteurs réellement raccordés), prévisualisation de l'alpha, sélection et nettoyage, taille mm, export PNG PTC | Conserver SHA source, rotations EXIF/profil DPI, rejet des SVG actifs, masque float32 intact, aperçu sur fonds contrastés ; Design Space import externe |
| **UX-FLOW-02 Objet / pinceau** | Choisir sujet réel, ajouter/effacer puis Annuler ou Valider | `subject_id` stable, `mask_id`, source/revision, `editor_v216` strokes strict, brouillon vs CAS, perte/replay/undo et conflit ; aucune démo exportée |
| **UX-FLOW-03 Vectoriel / découpe simple** | Choisir silhouette, vérifier intérieur/extérieur, simplification non destructive, exporter Basic Cut | Trous et îlots, nombre chemins, mm/viewBox/XML sûr, multiple path vs cut contour et QA géométrique ; variante originale accessible |
| **UX-FLOW-04 Texte / composition** | Saisir nom, choisir police disponible, ajuster, sauvegarder ; prévol glyphes avant chemin de découpe | G6 `S-036/064/092/R33-028` : modèle `TextDraft` **proposé**, pas API actuelle ; police/licence, OCR ultérieur non-mutant, version du projet et export texte→courbes sans perte de la source |
| **UX-FLOW-05 Fabrique carte/boîte/diorama** | Choisir un patron existant, dimensions mm, aperçu CUT/SCORE, guide d'opérations et export lorsqu'il existe | `folded_card/open_tray` existants, prévol whitelist; G6 gabarits métiers et G9 diorama 4 plans **pas encore prouvés** ; Alignements et Score/Attacher nécessitent contrôles DS manuels et coupon physique |
| **UX-FLOW-06 Planche / lot** | Choisir 12/24/50 créations, voir placements éditables, quantité et sortie multiple avec reprise | Éviter `MAX_MASKS=32` pour lot de 50, séparer batch/segmentation, instances vs `Subject`, licences CSV et collisions/retries idempotents |
| **UX-FLOW-07 IA facultative** | Fonctionnement CPU/manuel sans IA, bouton d'aide explicable si fournisseur local autorisé | Séparer proposition/commit CAS, modèle/licence/hash/VRAM, budget et OOM, aucune requête/téléchargement non consenti, annulation et résultat `STALE` |
| **UX-FLOW-08 Export / Smart Delivery** | Exporter directement PNG ou SVG du rôle effectivement pris en charge, ou Préparer un ZIP avec un artefact valide et son guide hors ligne | Quatre contrats séparés, manifest typed SHA/QA, ZIP no-clobber, données privées exclues, proof axes DS/physique UNKNOWN ; `write_delivery` historique n'est pas un ZIP |

**Enchaînements critiques à valider en priorité** : (a) import → masque → PTC ; (b) import → contours → Basic Cut/multicouche ; (c) patron mm → CUT/SCORE → guide ; (d) texte éditable → export chemin sans perdre l'éditable ; (e) lot et archive reprise → Smart Delivery. Les trois premiers relèvent des parcours natifs P0/P1, les autres sont bornés par contrats et gates.

## 3. Inventaire exhaustif 80/80 — ancrage utilisateur et classement provisoire

Le champ `P0/P1/P2` est une **hypothèse d'ordre de travail V3.5**, pas la nouvelle priorité normative des exigences V3.3. `HÉRITÉ / À SPÉCIFIER` signifie : description conservée, **pas** une fiche finale codable. Les décisions individuelles GARDER/RACCORDER/FUSIONNER/REPORTER/REJETER sont à contre-expertiser **sans supprimer l'ID historique**, même si deux expériences partagent un outil.

- **P0/A candidat** : fonctions minimales qui permettent un studio utilisable et sûr ;
- **P1/B candidat** : approfondissements de productivité et fabrication ;
- **P2/C candidat** : effets/IA avancée/réagencement non essentiels au premier E2E, toujours traçables.

### Groupe A — 16 capacités

| ID original #134 | Intitulé hérité | Point d'entrée du parcours | Priorité envisagée | Qualification |
|---|---|---|---|---|
| `A01` | Smart Import : PNG/JPEG/WebP/SVG, lots, contrôles d'entrée, dimensions/alpha/DPI | **IMPORT/RETOUCHE** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `A02` | Smart Select gestes : clic, survol, lasso libre/polygonal, rectangle/ellipse, pinceau, texte facultatif | **IMPORT/RETOUCHE** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `A03` | Smart Select multi-zones : îlots, trous, garder/exclure, union/intersection/soustraction/inversion | **IMPORT/RETOUCHE** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `A04` | Smart Select intelligence : prompts grossiers → contour recalé aux pixels, segmentation CPU/IA, incertitude et alternatives | **IMPORT/RETOUCHE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `A05` | Smart Select affinage : lissage, dilatation/érosion, détails fins, couleurs proches, bord local | **IMPORT/RETOUCHE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `A06` | Smart Clean détourage : retrait de fond, masque alpha, bords/transparent | **IMPORT/RETOUCHE** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `A07` | Smart Clean nettoyage : anti-halo, RGB, défauts, micro-fragments, topologie | **IMPORT/RETOUCHE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `A08` | Smart Clean qualité : netteté, débruitage, artefacts, contraste, HD | **IMPORT/RETOUCHE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `A09` | Smart Clean contrôle : transparence sur divers fonds, zoom 100%, diff avant/après | **IMPORT/RETOUCHE** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `A10` | Smart Color : pipette, recoloration, palettes, dégradés, transparence, quantification | **COULEUR** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `A11` | Smart Color production : couches par couleur, fidélité/profils d'impression | **COULEUR** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `A12` | Smart Vector conversion : silhouette, contour, centerline, multicouleur, SVG éditable | **VECTORIEL** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `A13` | Smart Vector courbes : plume/crayon, Bézier, nœuds, tangentes, coins | **VECTORIEL** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `A14` | Smart Vector géométrie : union/différence/intersection, trous, fermeture chemins | **VECTORIEL** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `A15` | Smart Vector optimisation : simplification, nœuds, angles, fragments et intersections | **VECTORIEL** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `A16` | Smart Vector intelligence : variantes et mesures fidélité/complexité/topologie. | **VECTORIEL** | P2 / C candidate | **HÉRITÉ / À SPÉCIFIER** |

### Groupe B — 14 capacités

| ID original #134 | Intitulé hérité | Point d'entrée du parcours | Priorité envisagée | Qualification |
|---|---|---|---|---|
| `B01` | objets raster/vector/texte/masques/groupes/opérations | **OBJETS** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `B02` | calques visibles/verrouillés/groupés/ordre/opacité | **OBJETS** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `B03` | décomposition intelligente des accessoires/illustrations en objets éditables | **OBJETS** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `B04` | déplacer/échelle/rotation/miroir/duplication par poignées | **OBJETS** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `B05` | alignement/distribution/grille/aimantation/mesures | **OBJETS** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `B06` | perspective, grille de déformation, masques d'écrêtage | **OBJETS** | P2 / C candidate | **HÉRITÉ / À SPÉCIFIER** |
| `B07` | articulation locale de personnage | **OBJETS** | P2 / C candidate | **HÉRITÉ / À SPÉCIFIER** |
| `B08` | reconstruction opt-in après extraction/déplacement | **OBJETS** | P2 / C candidate | **HÉRITÉ / À SPÉCIFIER** |
| `B09` | texte éditable/polices/typographie | **TEXTE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `B10` | texte courbe/circulaire/chemin/monogrammes/étiquettes | **TEXTE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `B11` | effets de texte/contours/ombres/textures/dégradés | **TEXTE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `B12` | texte→chemins, fusion et contrôles de fabrication | **TEXTE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `B13` | OCR facultatif→texte éditable après vérification | **TEXTE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `B14` | Smart Compose : marges/alignement/hiérarchie/modèles visuels. | **COMPOSITION** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |

### Groupe C — 18 capacités

| ID original #134 | Intitulé hérité | Point d'entrée du parcours | Priorité envisagée | Qualification |
|---|---|---|---|---|
| `C01` | stickers : offset, bleed, alpha, PNG Print Then Cut | **FABRICATION** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C02` | vinyle monochrome : silhouette et simplification | **FABRICATION** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C03` | multicouche : palette, couches, alignement | **FABRICATION** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C04` | pochoirs : îlots flottants, ponts | **FABRICATION** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C05` | dessin/centerline, continuité des chemins | **FABRICATION** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C06` | CUT/SCORE/DRAW/PRINT/FOIL distincts | **FABRICATION** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C07` | prévol géométrique : détails fragiles, doubles contours, intersections | **FABRICATION** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C08` | profils machine/matière/lame/tapis/unités | **FABRICATION** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C09` | variantes fidèle/équilibré/découpe facile | **FABRICATION** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C10` | les QUATRE contrats séparés : PNG Print Then Cut / SVG Basic Cut / SVG Cut multicouche / SVG d'édition | **FABRICATION** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C11` | transfert guidé Design Space, Score/Attacher, vérification dimensions | **FABRICATION** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C12` | Smart Layout duplication/planche multi-pages/quantités | **PLANCHES** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C13` | nesting par silhouettes, rotation, marges, contraintes | **PLANCHES** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C14` | placements verrouillés, édition manuelle, réoptimisation | **PLANCHES** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C15` | économie de matière, reprises de lot | **PLANCHES** | P2 / C candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C16` | patrons cartes/boîtes/enveloppes/pochoirs, modèles paramétriques | **FABRIQUE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C17` | géométrie mm, languettes/plis/épaisseur/preflight | **FABRIQUE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `C18` | preview patron 2D / simulation de pliage 3D éventuelle. | **FABRIQUE** | P2 / C candidate | **HÉRITÉ / À SPÉCIFIER** |

### Groupe D — 12 capacités

| ID original #134 | Intitulé hérité | Point d'entrée du parcours | Priorité envisagée | Qualification |
|---|---|---|---|---|
| `D01` | fournisseurs de segmentation CPU/SAM léger/SAM2/3 selon viabilité réelle | **IA LOCALE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `D02` | consignes clic/lasso/pinceau/texte combinées | **IA LOCALE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `D03` | variantes et choix expliqué avec confirmation | **IA LOCALE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `D04` | matting cheveux/poils/translucide | **IA LOCALE** | P2 / C candidate | **HÉRITÉ / À SPÉCIFIER** |
| `D05` | upscale HD conditionnel | **IA LOCALE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `D06` | génération raster/vector facultative | **IA LOCALE** | P2 / C candidate | **HÉRITÉ / À SPÉCIFIER** |
| `D07` | inpainting et réparation locale | **IA LOCALE** | P2 / C candidate | **HÉRITÉ / À SPÉCIFIER** |
| `D08` | catalogue modèles : licence, versions, hash, consentement | **IA LOCALE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `D09` | VRAM/CPU/repli/annulation/diagnostic | **IA LOCALE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `D10` | recettes et préréglages de traitement | **AUTOMATISATION** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `D11` | batch, dossiers, CSV, reprise et erreurs individuelles | **AUTOMATISATION** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `D12` | assistant contextuel et suggestions explicables. | **AUTOMATISATION** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |

### Groupe E — 20 capacités

| ID original #134 | Intitulé hérité | Point d'entrée du parcours | Priorité envisagée | Qualification |
|---|---|---|---|---|
| `E01` | bibliothèque, récents, miniatures, recherche/favoris | **BIBLIOTHÈQUE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E02` | collections/tags/modèles/duplication | **BIBLIOTHÈQUE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E03` | variantes/historique de création | **BIBLIOTHÈQUE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E04` | atelier hybride raster/vector/objets/propriétés | **ATELIER/UX** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E05` | canvas zoom/pan/poignées/aimants/overlays | **ATELIER/UX** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E06` | comparaison avant-après/sliders/superposition | **ATELIER/UX** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E07` | survol/context bar/gestes/raccourcis | **ATELIER/UX** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E08` | modes novice/avancé et divulgation progressive | **ATELIER/UX** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E09` | thèmes/panneaux/préférences | **ATELIER/UX** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E10` | accessibilité clavier/focus/contraste/DPI/motion réduite | **ATELIER/UX** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E11` | Undo/Redo/brouillons/transactions/historique | **ATELIER/UX** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E12` | sauvegarde V1 CAS/recovery et intégrité | **QA/PROJET** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E13` | previews async/caches bornés/requêtes périmées | **QA/PROJET** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E14` | diagnostics réparables et erreurs compréhensibles | **QA/PROJET** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E15` | QA alpha/contours/couleurs/résolution | **QA/PROJET** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E16` | QA SVG chemins/topologie/viewBox/mm | **QA/PROJET** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E17` | QA fabrication/profil/machine et preuve physique séparée | **QA/PROJET** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E18` | packaging Windows/hors ligne/update/rollback | **WINDOWS/SÉCURITÉ** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E19` | confidentialité/local/opt-in réseau | **WINDOWS/SÉCURITÉ** | P0 / A candidate | **HÉRITÉ / À SPÉCIFIER** |
| `E20` | tutoriels/aide contextuelle. | **AIDE** | P1 / B candidate | **HÉRITÉ / À SPÉCIFIER** |


**Contrôle mécanique de création de ce registre** : 80/80 IDs distincts, groupes A16/B14/C18/D12/E20. Répartition provisoire : P0/A 30, P1/B 41, P2/C 9. **Ce n'est pas** un pourcentage de réalisation du logiciel ou de revue sémantique.

## 4. Comportements et machine à états : direct quand réversible, confirmation quand risqué

**État projet** : `ABSENT` → `SOURCE_VALIDATED` → `PROJECT_OPEN@SHA` → `DRAFT_LOCAL` → `SAVE_PENDING` → `COMMITTED@SHA2`. En parallèle `STALE`, `RECOVERABLE`, `BLOCKED` si autre révision, pending backup, format non supporté, licence ou admission invalide. Seul `SAVE_PENDING` validé au CAS peut annoncer `COMMITTED`. Le rendu de canevas n'est jamais un writer.

**État export** : `NO_ARTIFACT` → `PREVIEW` → `PREFLIGHT_REVIEW_REQUIRED` → `EXPORTED_UNVERIFIED` → `DESIGN_SPACE_CONFIRMED` puis éventuellement `PHYSICAL_CUT_CONFIRMED` avec preuves séparées. Le passage de `PREVIEW` à `EXPORTED_UNVERIFIED` ne signifie jamais qu'une coupe est réalisable sur une machine particulière.

**Actions directes et Undo** : déplacer, sélectionner, zoomer, pivoter un objet temporaire et changer le panneau opèrent en brouillon sans popup. **Confirmer explicitement** : écriture projet externe, export écrasant, conversion texte→courbes, diffusion d'un pack, téléchargement de modèle, suppression de ressource, assignation d'opération machine risquée. Les effets réels, les avertissements et la possibilité de revenir en arrière sont exposés avant action.

**Retours d'erreur français** : chaque refus indique *quoi*, *pourquoi*, *comment corriger*, sans chemin privé ni stacktrace brute. Prérequis non testés : `UNKNOWN`, ne pas inventer `READY_TO_CUT`. Pour concurrence CAS : `Recharger / Comparer / Enregistrer une copie` seulement si ports réellement implémentés et validés.

**Accessibilité** : clic/double-clic et clavier avec focus stable, alternative aux gestes lasso, contraste indépendant de la couleur, zones tactiles raisonnables, texte agrandissable, DPI 200 %, motion réduit, fermeture et reprise des brouillons. Raccourcis enregistrés dans un seul registre ; éviter collision Tk Text/canevas. À 1366×768, une action principale/retour restent visibles même panneau replié.

## 5. Tests et métriques nécessaires — plan NON EXÉCUTÉ

| ID candidat de protocole | Positif | Négatifs et reprise | Preuves distinctes |
|---|---|---|---|
| `UX35-01` | PNG importé, projet V1 rouvert, source SHA identique | PNG tronqué, permissions refusées, révision CAS périmée ; aucune écriture/undo surprise | Auto et Windows Tk |
| `UX35-02` | Saisie/retouche sur sujet réel avec état brouillon/Undo, ID inchangé | sélection démo, masque absent, job tardif, conflit de révision, crash après commit | Auto, Windows Tk, recovery |
| `UX35-03` | SVG XML mm/viewBox valide, trou préservé, Basic Cut vs éditable distincts | chemins actifs, zero-size, milliers de nœuds, double coupe, SCORE deviné | Auto/QA, puis DS et terrain séparés |
| `UX35-04` | Texte français et police locale disponibles, export chemin sans confusion | glyphes manquants, licence interdite, police absente, undo après export | Auto, Windows/aperçu, DS (si revendiqué) |
| `UX35-05` | Template mm, changement d'outil documenté sans assignation automatique | NaN dimensions, Score non attaché, matériaux UNKNOWN, mauvais ordre 4 plans | Auto, Design Space et coupon humain distincts |
| `UX35-06` | 50 travaux en batches, reprise sans doublons, somme objets correcte | 32 masques/tensor exceeded, annulation, fichier CSV invalide, disque plein | Auto/Windows + benchmark mémoire |
| `UX35-07` | Mode manuel sans modèle, IA facultative installée/consentie sur config de test | téléchargement non autorisé, licence absente, OOM, réponse obsolète | CPU et GPU RTX testés séparément |
| `UX35-08` | ZIP Smart Delivery relu et manifest valide à partir d'un seul artefact sain | ZIP-slip, collisions Windows, symlink, fichier modifié pendant copie, profil matériel inconnu | Auto/Windows + DS/physique séparés, non inférés |

**Performances à mesurer**, non prétendues observées : cold start Windows, p50/p95 geste de canevas, preview avant/après PNG HD, cache/annulation, RAM+VRAM, génération 12/24/50, publication ZIP. **Fixtures** : motifs et polices synthétiques ou sous licence de tests, aucun média commercial ni original utilisateur commité.

## 6. Critères de fermeture du travail UX V3.5

- 80/80 IDs **reconduits** (fait) puis 80/80 **décidés individuellement** avec lien vers parcours/lot, alternative hostile, nouveau comportement, critères et DoD (**ouvert**).
- Décision de framework `Tk/Qt/Tauri` sur benchmark réel, pas sur préférence esthétique (**ouvert**).
- Au moins les cinq E2E critiques décrits ci-dessus testés quand le code sera disponible ; preuves Windows/Design Space/physique distinctes (**NON_RUN** ici).
- Toutes les fonctions G6/G9 historiques conservées ; smart features non dupliquées et pas de nouvel état projet concurrent.
- Prochaine rédaction nécessaire : [QUALITY_TESTS_AND_EVIDENCE.md](QUALITY_TESTS_AND_EVIDENCE.md) sur la séparation des 437 recettes documentaires et preuves d'exécution, puis `ADR_RISKS_OPPORTUNITIES.md` et `PROMOTION_CHECKLIST.md`.

**Branche :** `roadmap/v3-5-design-candidate-20261112` seulement ; aucun code, merge, AGENTS, PR ni tâches d'ingénierie modifiés par cette fiche.
