# V35-COV-17B — Revue UX B01–B14 : objets, calques, transformation et texte

**13/11/2026 — Décisions individuelles CANDIDATES, non normatives.** La V3.4 active conserve tous les critères V3.3. Les 14 libellés ci-dessous sont copiés depuis [#134](https://github.com/frenndak/SmartSVG-Studio/issues/134) ; l'ancien statut « audité » ne devient ni « implémenté » ni « prêt à coder ». Confrontation aux sources de la branche `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935` validée depuis l'API branche.

## 1. Ports examinés et erreurs de modèle à éviter

- `engine/smartsvg_core/project_contracts.py` blob `7bfd2d714384717c6ce0bb66659971881bd285c2` : `Subject`, `Mask`, `Artifact` sont des données typées, **pas** un éditeur universel d'objets.
- `engine/smartsvg_core/subject_identity_g33e.py` blob `2d799a34915ae7648f39c89df25b876e5ddfcee0` : liaison persistante `subject_id` / masque float32 ; n'infère pas les accessoires.
- `engine/smartsvg_core/native_atelier_v34.py` blob `bb2f03d02d556715f15821544561589aefff0eba` : `AtelierSnapshot`/sujets réellement inspectés, lecture seule pour ce module.
- `engine/native_atelier_tk_v34.py` blob `921f09fbd54b68a19b3ba9688f00a0334bafe6b3` : `NativeAtelierPanel` Tk, navigation et flux pinceau, **pas une preuve d'éditeur de calques et formes complet**.
- `engine/smartsvg_core/editor_session_g23.py` blob `dda853694d22f59252b9549b5e2fdbd59933bd59` : `editor_v216` accepte exactement `version,width,height,count,source,strokes` ; aucun `text` ou `layers` n'y est autorisé.
- `engine/smartsvg_core/project_workspace_g22.py` blob `13b8e40d6fcc9cf03ed2c935b38ad6eff0bcbe03` : `save_editor_document`, `save_base_masks`, CAS et récupération ; ne pas créer une seconde persistance.
- `engine/smartsvg_vector/layers_v2113.py` blob `486ca4f980288b55bbe89db7e9203d1f76237d03` : les groupes de couleur d'un SVG artistique sont éditables dans un logiciel vectoriel, **mais ne prouvent pas** un système de calques natif.
- [COV10C](COV10C_V1_TEXT_EXPORT_PORTS.md) : dix exigences G6/G9 avec ports et critères, dont **S-036, S-064, S-092, R33-028** sur polices et conversion texte ; éviter de réinventer un moteur OCR.

**Contre-expertise** : la tentation de déduire `TextObject` de `LoadedProject.document` dict ou des groupes SVG de couleurs est incorrecte. La compatibilité et les contrôles d'autorité du V1 priment sur l'ajout de boutons de manipulation.

## 2. Matrice décisionnelle des 14 UX sans omission

| ID #134 | Description historique | Décision candidate (non normative) | Situation vérifiée / non vérifiée | Contrat/DoD à concevoir | Négatifs prioritaires |
|---|---|---|---|---|---|
| **B01** | objets raster/vector/texte/masques/groupes/opérations | **GARDER / P0** | Subject/Artifact/masks V1; AtelierSnapshot sujet réel; objets typés texte/vector/raster non persistés comme un seul modèle | Spécifier ObjectRef identitaire en mémoire sans écrire V1 arbitraire, adapter sujet/masque et plan de composition | projet révisé après sélection; sujet effacé; vector object sans provenance |
| **B02** | calques visibles/verrouillés/groupés/ordre/opacité | **AMÉLIORER / P0** | layers_v2113 génère SVG avec groupes colorés, ne constitue pas des calques natifs avec visibilité/verrouillage/reopen | LayerDraft UI non mutant; choix de migration persistance et ordonnance de calques; groupe CUT distinct de couche visuelle | layer cyclique; ordre perdu sur reopen; calque masqué exporté sans avertissement |
| **B03** | décomposition intelligente des accessoires/illustrations en objets éditables | **RACCORDER / P1** | auto_masks_v2111, subject_identity_g33e pour sous-sujets; decomposition objets sémantiques et accessoires auto non démontrée | Proposal de séparation/rattachement sujet-accessoires avec confirmations et IDs stables | fragment artistique inventé; accessoires confondus; lien sujet perdu |
| **B04** | déplacer/échelle/rotation/miroir/duplication par poignées | **RACCORDER / P0** | NativeAtelierPanel et viewport Tk présents, mais poignées transform/rotation/duplication d'objets non prouvées | Transformer brouillon sur la même identité avec matrice 2D et cadre mm; Undo exact; révision projet liée | rotation NaN; miroir inversant CUT; échelle nulle, zoom écran appliqué aux mm |
| **B05** | alignement/distribution/grille/aimantation/mesures | **RACCORDER / P0** | template_geometry mm et image viewport; grille/snap/alignements objets non vérifiés comme UI | Guides mm, distributions avec tolérance et preview, conservation bbox et identité; jamais de conversion visuelle implicite en coupe | déplacements hors feuille; snap sur mauvais objet; précision mm perdue |
| **B06** | perspective, grille de déformation, masques d'écrêtage | **REPORTER COMPLEXITÉ / P2** | pas de preuve de perspective/warp/clip natif dans les ports inspectés | Étude contrat de transformation non destructif et masque d'écrêtage, sans forcer schéma V1 | perspective dégénérée, clipping perdu à l'export, polygone auto-intersecté |
| **B07** | articulation locale de personnage | **REPORTER AUTOMATISATION / P2** | aucune articulation squelettique/rig vérifiée; sujets et bbox historiques ne sont pas une cinématique | Proposition contraintes pivots/éléments avec zones d'influence explicites, option purement locale | membre détaché, posture incohérente, source remplacée sans consentement |
| **B08** | reconstruction opt-in après extraction/déplacement | **REPORTER AUTOMATISATION / P2** | aucune reconstruction générative validée; routage IA actuel n'affirme pas reconnaissance | Proposition opt-in après extraction, masque et provenance, diff visuel et fallback manuel | détails halluciné, ancienne révision, téléchargement non consenti |
| **B09** | texte éditable/polices/typographie | **AMÉLIORER / P1** | editor_v216 est strictement strokes ; pas d'API typographique persistante vérifiée (COV10C) | ADR TextDraft+FontRef, licences/glyphes, taille mm, save/reopen CAS avant activation de l'UI | police absente, accents corrompus, licence inconnue |
| **B10** | texte courbe/circulaire/chemin/monogrammes/étiquettes | **RACCORDER / P1** | texte sur chemin et monogrammes hérités G6 mais port vectoriel historique ne prouve pas TextOnPath natif | Courbe/chemin parent versionné, courbure et orientation prévisualisées, dérivé export seulement | glyphes inversés, baseline irrégulière, cercle dégénéré |
| **B11** | effets de texte/contours/ombres/textures/dégradés | **RACCORDER / P1** | effets texte non démontrés dans interface; smartsvg_quality/auto_hd traite PNG, pas effets texte éditables | Rendus non destructifs de contour/ombre/dégradé, signaler ceux qui ne se projettent pas en coupe | ombre interprétée CUT, couleur effacée, dégradé raster exporté faussement en SVG vectoriel |
| **B12** | texte→chemins, fusion et contrôles de fabrication | **AMÉLIORER / P1** | vectorize_flat_art color SVG réel, mais pas une conversion texte→contours fiable et vérifiée | Conversion sur copie export, glyphes et licence validés, qualité SVG et QA indépendante | ligatures/accents manquants, duplications de chemins, source texte rendue non éditable |
| **B13** | OCR facultatif→texte éditable après vérification | **RACCORDER / P1 étude ; P2 moteur OCR** | routing_v21121 énonce No OCR; source V1/image disponible, moteur OCR native non vérifié | OCRProposal non mutante avec bounding boxes source px, diff, consentement et insertion manuelle après contrat texte | confiance inconnue, OCR obsolète, texte remplacé sans validation |
| **B14** | Smart Compose : marges/alignement/hiérarchie/modèles visuels. | **RACCORDER / P1** | template_geometry propose 2 patrons; composition avec hierarchy/toppers/texte éditable pas prouvée | Smart Compose comme assistant de mise en page par règles et canevas unique, gabarits éditables | auto alignement écrasant choix utilisateur, matériaux/dimensions implicites, conflit CAS |

**Contrôle : 14/14 IDs B01–B14, chacun avec décision, limite, DoD et négatifs.** Une décision `REPORTER AUTOMATISATION` pour B06/B07/B08 signifie **conserver la capacité et son critère de conception P2**, pas suppression. Ne pas reclasser une exigence V3.3 P1/P2 par ce simple tableau.

## 3. Contrat UX novice, expert et transactions

**Novice** : importer → choisir sujet → bouger/ajuster dans brouillon → regarder aperçu avant/après → annuler sans écriture ou confirmer → vérifier un résultat persistant. Pour texte, l'écran `Texte` ne s'active comme outil d'écriture qu'après une représentation `TextDraft` compatible avec le reader V1 et writer CAS ; faute d'API validée, afficher un diagnostic clair plutôt qu'une édition factice.

**Expert** : propriétés d'objet immuables (ID, source SHA, bbox source px, transform 2D, unité mm), groupes et calques dérivés, visibilité/lock, reprise, versionnement des styles, diagnostics de glyphes/licence avant texte→chemins. Propositions IA décomposées : provenance et incertitude explicites, aucune application périmée et aucun téléchargement implicite.

**Séquence transactionnelle candidate** : `InspectProject@SHA` → `DraftTransform/EditText` (sans writer) → `Preview` → `ValidateInput` → `Confirm` → `save_with_recovery@expected_sha` **uniquement lorsque le DTO et son schéma sont approuvés**. Contraintes de `editor_v216` inchangées tant qu'aucune migration compatible n'existe. L'Undo d'un brouillon n'annule pas une découpe physique ou un fichier exporté.

**Cas négatifs transversaux** : ancien SHA et réponse tardive, identité Subject/raster mal reliée, groupe cyclique, texte non représentable ou sous licence incompatible, transformation non finie, crash/disque plein, preview de couleur confondu avec CUT, source modifiée durant OCR. Les 14 décisions ne sont jamais un prétexte pour contourner les quatre sorties typées et le tri-state matière.

**Accessibilité** : une seule fenêtre Tk, commandes clavier alternatives au drag/poignées, 1366×768/DPI 200 %, raccourcis sans collision avec Tk Text, focus après changement de panneau, contraste et transparence, mouvement réduit. Mesures Windows réelles `NOT_RUN`.

## 4. DoD des axes, décisions ouvertes et suite

- **B01–B05** : prototype d'objets/couches/transforms réversibles ; vérifier que chaque objet visualisé est réel et lié à son `project_sha`, qu'il n'existe aucune duplication d'autorité.
- **B06–B08** : études P2 et tests de faisabilité, sans hallucin­er la reconstruction d'illustration.
- **B09–B13** : sous-parcours G6 P1 (texte/polices/glyphes) et OCR G9 facultatif P2, deux responsabilités distinctes ; aucun texte n'entre arbitrairement dans `editor_v216`.
- **B14** : composer au moyen d'objets déjà enregistrables et d'un seul canevas, avec templates métiers vérifiés, pas de second workflow propriétaire.
- **Preuves de cette fiche** : documents et modules inspectés ; `CODE_MAIN` uniquement pour les ports nommés existants, pas pour les 14 features complètes ; `AUTO_UNIT, WINDOWS_UI, GPU, DESIGN_SPACE, PHYSICAL_CUT = NOT_RUN` dans ce travail documentaire. Les critères historiques 141 et tickets 140 demeurent contraignants.
- **Prochaine fiche ciblée** : `V35-COV-17C` C01–C18 (fabrication, 4 exports, nesting, patrons, matière/outil et Design Space). Puis D01–D12/E01–E20 et revue contradictoire des 80 décisions. L'adoption documentaire exige une PR revue et promotion gouvernance distincte.
