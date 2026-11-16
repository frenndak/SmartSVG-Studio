# SmartSVG V3.5 — COV-18A-2d : arbitrage contradictoire des écarts et responsabilités de ports

**13 novembre 2026 — PROPOSITION DE CONCEPTION, NON NORMATIVE.** Suite de [COV-18A-2c](COV18A2C_LOCAL_DOD_SIX.md), [COV-18A-2b](COV18A2B_V33_CRITERIA_SIX.md), [COV-10C](COV10C_V1_TEXT_EXPORT_PORTS.md) et [lot 23](../roadmap-v3.4/23_TRACEABILITE_BACKLOG.md). Sources de code lues au snapshot `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935`, **pas une garantie sur le dernier HEAD**. Pas de test produit exécuté, pas de merge ni changement du schéma, code ou gouvernance.

## 1. Arbitrages fondés sur les critères intégraux V3.3

| Couple historique à contre-expertiser | Constat vérifiable | Décision V3.5 CANDIDATE et gardes de fermeture |
|---|---|---|
| **S-032 ↔ V34-098** | **S-032** = « Export SVG édition vs fabrication », prérequis S-011 et S-030, critère « Aucun profil confondu » (héritage G5.5). Micro-fiche V34-098 du lot 13 : **courbes et simplification sûre**, `T-V34-13-06/09/10`, aucun S-032 cité localement. | **CONSERVER comme soutien topologique, pas propriétaire unique d'export.** DoD de S-032 : V34-129 produit les quatre rôles, V34-098 garantit seulement l'étape géométrique avant prévol. Ne pas réétiqueter le ticket 098 « quatre exports livrés ». |
| **R33-006 ↔ V34-133** | R33-006 = « Masques float32 comme autorité de retouche ». Dans le lot 18, V34-133 est « Calques/propriétés dérivés du projet unique » : S-035/068/071/073/077/078, R33-003/008/018/020 ; il ne cite pas explicitement R33-006. Le lot 05/V34-028 cite `R33-004..006`. | **V34-028 détient l'invariant des masques, V34-133 est consommateur UI conditionnel.** Toute écriture passe par le writer/CAS ; calques, visibilité et propriétés dérivées ne deviennent pas des champs V1 silencieux. |
| **S-009 ↔ V34-129** | S-009 = QA Cricut par format (mesures dimensions/trajets précontrôlées). Le lot 23 le rattache à V34-129 ; la micro-fiche du lot 17 énumère S-002/029/030/032/075 et R33-008, sans S-009. | **GATE TRANSVERSAL à conserver.** V34-129 doit consommer les résultats QA par rôle (notamment V34-090 prévol raster, V34-109 prévol fabrication), sans usurper leur responsabilité. Un export écrit ≠ QA PASS ≠ import Design Space confirmé ≠ coupe physique réussie. |
| **S-045 ↔ V34-112** | S-045 = vinyle multi-couleur et test de superposition réel (G9). V34-112 est « Pen/Draw + Cut » ; test `T-V34-14-16` exige DRAW distinct et guide Attacher. | **À INVESTIGUER**, non à valider par simple présence du lien lot 23. Pen/Draw ne démontre pas une superposition de vinyles ; la validation physique et le profil matière restent séparés. |
| **S-048 ↔ V34-089** | S-048 = upscale IA artistique avec audit des détails inventés (G9, P2). V34-089 porte sur tailles/rééchantillonnage/texture **CPU** et interdit un « faux HD natif » (`T-V34-12-13`). | **NE PAS CONFONDRE les capacités** : V34-089 est une base raster, mais aucun modèle IA ni audit de détails inventés ne découle de son DoD. Maintenir S-048 comme obligation héritée P2 avec investigation de modèle/licence/consentement séparée. |

### Sources textuelles et ports vérifiés

- [V3.3 héritage](../ROADMAP_HERITAGE_v3_3.md) : S-009 « Assurance qualité Cricut par format », S-032 « Export SVG édition vs fabrication », S-045 « Vinyle multi-couleur », S-048 « Upscale IA artistique », R33-006 masque float32 (voir MASTER et TRACEABILITY historiques).
- [Lot 13](../roadmap-v3.4/13_VECTORISATION_SVG.md) : `V34-098` ligne 220, tests `T-V34-13-06/09/10` ; [lot 17](../roadmap-v3.4/17_EXPORTS_DESIGNSPACE.md) : `V34-129` ligne 105, tests `T-V34-17-01..05`.
- [Lot 18](../roadmap-v3.4/18_ATELIER_GRAPHIQUE.md) : V34-133 ligne 112, tests `T-V34-18-07..09` ; [lot 05](../roadmap-v3.4/05_PROJECT_SCHEMA.md) : V34-028 ligne 213 et `T-V34-05-03/04/16/17`.
- [Lot 12](../roadmap-v3.4/12_RASTER_PIPELINE.md) : V34-089 ligne 165, tests `T-V34-12-11/12/13/16`; [lot 14](../roadmap-v3.4/14_LANGAGE_FABRICATION.md) : V34-109/112 lignes 258/260, `T-V34-14-16`.
- Code `engine/smartsvg_core/project_contracts.py` blob `7bfd2d714384717c6ce0bb66659971881bd285c2` : `Artifact.use` accepte **3 valeurs V1** (`print_then_cut_png`, `basic_cut_svg`, `editable_svg`). **Le rôle de CUT multicouche est une projection d'export externe, pas un ajout implicite à la donnée V1.**
- Code `engine/smartsvg_core/editor_session_g23.py` blob `dda853694d22f59252b9549b5e2fdbd59933bd59` : `parse_editor_document` exige exactement `version,width,height,count,source,strokes`. Ajout de `layers/text` dans ce document = **INVALID_EDITOR_SCHEMA**. Le brouillon texte reste non persistant en V1 avant ADR et migration validées.
- Code `engine/smartsvg_vector/layers_v2113.py` blob `486ca4f980288b55bbe89db7e9203d1f76237d03` : `vectorize_flat_art()` renvoie XML + audit pour groupes artistiques de couleur ; ceci **ne garantit pas** une découpe multicouche. Prévol Cut séparé.
- Code `engine/smartsvg_cricut/delivery_v21122.py` blob `98a2580c529f613ca732a69fda5273a317f64daf` : `write_delivery()` écrit un manifeste historique `MANIFESTE_STICKERS.json`, **pas** le futur ZIP Smart Delivery ; préserver le writer historique, ne pas inventer un « ZIP existant ».
- Code `engine/smartsvg_cricut/direct_import_v218.py` blob `a49fc10844559d431f393a7f7f56343ebefeb1cf` : `_svg_preflight` traite un **SVG de contrôle diagnostic** et signale de ne pas le superposer au PNG. Aucun pilotage Design Space ni import automatisé prouvé par cette fonction.

## 2. Architecture de fermeture — responsables par *contrat*, pas par slogan

| Contrat | Responsabilité de référence V3.4 | Consommateur V3.5 | Gate de preuve envisagé |
|---|---|---|---|
| Identité Subject/mask, float32, CAS | Writer V1, V34-028, port 05 | A02/A03 et W03–W04 | 12 IDs + masque bit-exact, Undo/Redo et crash/reload ; NEVER_PASS si preuve CAS absente |
| Proposition sémantique (faux sujet) | V34-069/071/082, source corpus | A04 et Smart Select | Benchmark de faux positifs annoté, modèle opt-in, UNKNOWN si confiance non calibrée |
| Raster texture, dimensions | V34-089 ; source/ppi et rapports | A08 et Smart HD | Avant/après sur fixture et digest CUT inchangé ; IA artistique S-048 qualifiée séparément |
| Courbe/topologie | V34-098, V34-097 | A12, Cut Advisor | Trou, intersections, métriques contour/surface ; pas d'export réputé livré |
| Quatre rôles export indépendants | V34-129 + prévol V34-090/109 | A12, Smart Delivery | `T-V34-17-01..05`, mm, QA par rôle, PNG ≠ SVG de diagnostic ; DS/physique indépendants |
| Canevas propriétés/texte | V34-133 (consommateur V1), G6/G9 sans V34 direct | B09 et objets, W02 | Brouillon isolé; aucun texte ou `layers` sérialisé dans V1 ; ADR avant extension |
| Multi-vinyle | S-045 G9, exigences de matériaux | W05 fabrication, future Smart Weeding | Coupons superposés/mesures réelles, DRAW+CUT sans équivalence |
| Livraison externe | `delivery_v21122.py` historique (manifeste seulement) | Smart Delivery SD0–SD3 | ZIP externe créé à partir d'un artefact réel, hash+manifest, publication atomique, pas faux badge Cricut |

**Refus d'un raccourci de conception :** ne pas ouvrir sept nouveaux moteurs pour résoudre sept relations textuelles. Raccorder les exigences aux ports vérifiés, n'étendre le schéma de projet que sous ADR/migration autorisée, et faire une preuve par axe plutôt qu'une note QA globale.

## 3. Revue hostile, scénarios positifs, négatifs, reprise

**Tests unitaires/fichiers synthétiques à proposer (tous NOT_RUN) :**
- T1 : 12 Subjects avec ID stables ; ouvrir/retoucher/undo/reload, vérifier SHA source et float32 exact, `editor_v216` strict et CAS.
- T2 : comparer un SVG de couleurs éditables, un Basic Cut et un CUT multicouche ; injecter un trou, double contour et NaN, vérifier prévol par rôle et absence de recodage sous `editable_svg`.
- T3 : vérifier PNG PTC et SVG diagnostic en sorties distinctes ; aucune superposition/import automatique ; QA Cricut `UNKNOWN` avant validation physique.
- T4 : épreuve vinyle multicouleur et Pen+Cut préparées séparément ; aucun `T-V34-14-16` ne certifie la superposition.
- T5 : upscale CPU avec interpolation déclarée, puis modèle IA artistique facultatif uniquement avec licence/poids/confiance explicités ; ne pas inventer des détails et ne pas associer un score CPU au modèle.

**Négatifs incontournables :** licence de police non redistribuable/glyphe manquant ; schéma V1 avec clefs `layers/text` rejeté ; masque NaN ou mauvais subject_id ; cas d'impression avec unités mm inconnues ; dessin vectoriel rempli présenté comme CUT validé ; ZIP modifié entre prévol et publication ; sortie GPU tardive après changement CAS ; configuration de matériaux inconnue ou de vinyles non testée. **Crash/disque plein/annulation** : source précédente intacte, statut de reprise explicite, aucune archive/pack partiel publié.

**UX novice/expert** : novice choisit un geste direct réversible et voit les avertissements compréhensibles ; expert inspecte SHA, mm, ids, QA et un diff exact. Flux `ouvrir → brouillon → preview → corriger/Undo → prévol → confirmer export externe → pack vérifié`. Accessibilité 1366×768/DPI 200 %, clavier, focus, contraste/motion réduit à qualifier sur Windows réel, sans inventer des mesures p50/p95.

**Contrôle 25 axes :** univers 24/141/140/80/437 maintenus ; capacité G6/G9 et dioramas non supprimés ; V1/CAS/float32, quatre rôles, CLI/GUI, IA opt-in, performance mesurable, licences, négatifs et reprise, QA tri-state, Design Space/coupe physique séparés ; aucune preuve produit exécutée, aucune modification AGENTS ni PR/merge. **Les 80 décisions UX restent candidates**, aucune certification globale.

## 4. Décision, statut et suite

- **Résolus sur le plan de l'architecture candidate :** S-032/V34-098 = support topologique ; R33-006/V34-133 = consommateur UI ; S-009/V34-129 = gate QA par rôle. Les relations historiques restent visibles et leurs critères intégraux contraignants.
- **Pas encore résolus par preuve produit :** S-045/V34-112 (superposition vinyle physique), S-048/V34-089 (IA ≠ upscale CPU), S-036/G6 (sauvegarde typographique).
- **Aucun test de code, UI Windows, GPU, Design Space ou coupe physique effectué** ; aucun ticket normative modifié, aucun statut « prêt à coder » attribué sur la seule base de cette analyse.

**Prochaine étape unique COV-18A-3 :** poursuivre la revue hostile des **24 autres IDs A/B** (dont A16 et tous les objets/texte) par lots cohérents de six ; pour chacun confronter priorité UX, critère V3.3, DoD et port réel, et saisir les lacunes dans la matrice V3.5. Ne pas recommencer COV17 ni COV18A2b–d ; Smart Delivery et autres groupes W restent au programme.
