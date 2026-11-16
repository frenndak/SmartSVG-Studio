# SmartSVG V3.5 — COV-18A-2c : DoD locaux, scénarios et divergences réelles, six fonctions UX

**13 novembre 2026 · NON NORMATIF · lot documentaire COV-18A-2c.** Sources : lots V3.4 locaux à `main@aa0ff9e7d0c53dba3fdc429c02c6198736cfe935` + lot 23 (blob `177a0ecff5edd816e1bf879fc93c2a49efd83690`) ; conception antérieure [COV18A2B](COV18A2B_V33_CRITERIA_SIX.md). Les liens `UX→S/R33` restent une **interprétation candidate**, même si la liaison `S/R33→V34` est écrite dans le lot 23. **Ce travail valide la lecture des 13 micro-fiches et des 52 ID de tests locaux distincts, sans test exécuté.**

## 1. Contrôle quantifié des micro-spécifications

| Indicateur | Vérification de lecture | Valeur |
|---|---|---|
| UX traitées | A02, A03, A04, A08, A12, B09 | **6/6** |
| Tickets V34 candidats recensés | micro-fiches réelles avec ligne et blob SHA | **13**, et B09 sans ticket direct |
| Citations ticket→scénario local | déclarées explicitement dans micro-fiches | **53** références, **52** tests distincts |
| Exigences du lot 23 absentes dans la *ligne locale* | registre vs micro-fiches, expansions `S-001/002` et `R33-004..006` prises en compte | **6 tickets touchés**, interprétation à arbitrer |
| Qualification sémantique complète / fonction UX certifiée | non démontrée : tests/UI/Windows/Design Space/physique | **0/6** |
| Tests produits exécutés dans ce lot | aucune commande ni coupe matérielle | **0** |

**Attention :** une entrée « absente de la micro-fiche » n'efface pas une relation explicite du registre transversal. Les deux sources sont conservées ; la divergence est à confirmer contre les critères intégraux et le DoD, **pas corrigée automatiquement** dans V3.4.

## 2. Six confrontations assertion par assertion

### A02 — S-070

**Critère utilisateur à respecter :** 12 sujets : sélection croisée conserve le même subject_id, y compris Undo, réouverture et reordering des vignettes. **Contre-expertise hostile :** Aucun sujet fantôme ; clic/lasso/ellipse ne sont pas déduits d'un simple canevas.

| Ticket source | Références locales + DoD (exactes dans la ligne du lot) | Tests locaux cités et axes | Écarts du lot 23 non recopiés explicitement dans la micro-fiche |
|---|---|---|---|
| [V34-075](../roadmap-v3.4/10_ANALYSE_VISUELLE.md) L232 | **V34-075** Revue novice/expert accessible \| **P0** S-070/071/073/079/080, R33-018/019/020/033, V34-041..049/050..058/071 ; `engine/web/js/v34_subject_review.mjs` ; T-V34-10-16/26..28, UI + Windows UX ; DoD navigation croisée sans ID fictif ; rollback liste de propositions textuelle | `T-V34-10-16` L203 (auto) · `T-V34-10-26` L213 (UI) · `T-V34-10-27` L214 (UI) · `T-V34-10-28` L215 (Windows UX) | Aucun écart de ce sens |
| [V34-132](../roadmap-v3.4/18_ATELIER_GRAPHIQUE.md) L111 | **V34-132 P0 — Canevas raccordé au vrai sujet et à son aperçu** \| S-008/023/070/073/080, R33-003/006/014/033, V34-041 ; preuve G3.3e-b1, preview b2a ; b2b **uniquement pour persister**. Aucun V2/assistant requis. \| **Adapter** `engine/web/js/smartsvg_express_atelier_preview.html` et `smartsvg_subject_identity_g33e.mjs` ; consommer `strokes.py` via adaptateur minimal futur **si nécessaire**. T-V34-18-01..05/10, preuves auto/UI puis Windows. **DoD :** cible exacte, preview sans écriture, conflit sûr ; **rollback :** revenir à l'inspection G3.3e-b1. | `T-V34-18-01` L94 (auto/UI ; V34-041/132) · `T-V34-18-02` L95 (auto/UI ; V34-132) · `T-V34-18-03` L96 (auto/CPU ; V34-132) · `T-V34-18-04` L97 (auto/CPU ; V34-132) · `T-V34-18-05` L98 (auto/UI ; V34-041/132) · `T-V34-18-10` L103 (auto/fault-injection puis Windows ; V34-044/132) | `S-003` |

**Recettes locales :** - `T-V34-10-16` (source L203) : Un masque touchant bord n'est pas auto-accepté sans revue
- `T-V34-10-26` (source L213) : Novice sélectionne/rejette/corrige 12 propositions sans sujet fantôme
- `T-V34-10-27` (source L214) : Expert inspecte masque float32/coordonnées/rapport sans faux badge QUALIFIE
- `T-V34-10-28` (source L215) : Clavier seul, lecteur d'écran et zoom 100 % couvrent revue + correction
- `T-V34-18-01` (source L94) : Sélection des 12 escargots de démonstration : aucun `Subject` ni archive créée, aucune fonction réelle prétendue
- `T-V34-18-02` (source L95) : Choisir `subject_id` synchronise vignette/canevas/propriétés ; réordonner les vignettes ne change jamais la cible
- `T-V34-18-03` (source L96) : Deux masques float32 A/B : `add` et `erase` sur A préservent B et tous les pixels non peints bit à bit ; SHA archive inchangé en preview
- `T-V34-18-04` (source L97) : Preuve b1 absente/ambiguë ou SHA masque invalide : preview refusé, aucun `mask_index` déduit du DOM
- `T-V34-18-05` (source L98) : SHA modifié, double clic, changement de sélection, réponse tardive : aucun commit ni cible différente, message et reprise
- `T-V34-18-10` (source L103) : Conflit de notes G2.2, panne d'écriture ou backup pending : pas de faux succès, projet précédent conservé, récupération explicite

**Décision :** RACCORDER ou RAFFINER les contrats sources, sans qualifier le parcours utilisateur complet ; **statut : CRITÈRES_LOCAUX_LUS, NON_CERTIFIÉ**.

### A03 — R33-006

**Critère utilisateur à respecter :** Masque float32 comme autorité ; booléens multi-zones restent candidats et ne doivent pas modifier l'autorité sans CAS. **Contre-expertise hostile :** Ne jamais déduire union/intersection et persistance de calques du seul modèle Subject.

| Ticket source | Références locales + DoD (exactes dans la ligne du lot) | Tests locaux cités et axes | Écarts du lot 23 non recopiés explicitement dans la micro-fiche |
|---|---|---|---|
| [V34-028](../roadmap-v3.4/05_PROJECT_SCHEMA.md) L213 | **V34-028 P0** Identités et packs de masques V2 \| S-023, S-028, S-052 ; R33-004..006 ; V34-012, V34-018 \| `docs/roadmap-v3.4/specs/IDENTITIES_AND_MASK_PACKS.md`, futur `engine/smartsvg_core/mask_pack_v2.py` \| T-V34-05-03,04,16,17 ; auto+Windows ; DoD : preuves float32 exactes, IDs stables, partition 50 sans dépasser V1 | `T-V34-05-03` L183 (auto) · `T-V34-05-04` L184 (auto) · `T-V34-05-16` L196 (auto) · `T-V34-05-17` L197 (auto, Windows) | Aucun écart de ce sens |
| [V34-133](../roadmap-v3.4/18_ATELIER_GRAPHIQUE.md) L112 | **V34-133 P1 — Calques/propriétés dérivés du projet unique** \| S-035/068/071/073/077/078, R33-003/008/018/020, V34-041/045 et contrats V34-100/106/129 selon type de projet ; aucun second store. \| **Réutiliser** le canevas existant, `smartsvg_cut_review_model_g27.mjs`, `Subject` et opérations déjà prévues ; panneau futur seulement si utile. T-V34-18-07..09, auto/UI puis Windows. **DoD :** propriétés mm explicites, CUT≠SCORE, calques non destructifs, clavier ; **rollback :** panneau existant en lecture seule. | `T-V34-18-07` L100 (auto/UI ; V34-133) · `T-V34-18-08` L101 (auto/UI ; V34-133) · `T-V34-18-09` L102 (UI/a11y puis Windows ; V34-045/133) | `R33-006`, `S-008`, `S-026`, `S-080`, `S-086`, `S-087` |

**Recettes locales :** - `T-V34-05-03` (source L183) : 12 IDs sujet G3.3e et preuves exactes préservés ; aucun ID réattribué
- `T-V34-05-04` (source L184) : Snapshot float32 round-trip bit-identique ; preview L8 ne devient jamais autorité
- `T-V34-05-16` (source L196) : Masque modifié avec preuve d'identité ancienne → `IDENTITY_REVIEW_REQUIRED`
- `T-V34-05-17` (source L197) : 50 sujets partitionnés : IDs uniques, aucun pack >32, aucune fuite de source
- `T-V34-18-07` (source L100) : Boîte 140×110 : CUT et SCORE restent deux groupes sémantiques distincts, aucun transfert Score automatique
- `T-V34-18-08` (source L101) : Visibilité, solo, zoom et calques temporaires ne créent aucun champ V1 ; mm inconnus non inventés
- `T-V34-18-09` (source L102) : Sélection, outils, erreurs, validation et retour accessibles au clavier avec focus et annonces FR

**Décision :** RACCORDER ou RAFFINER les contrats sources, sans qualifier le parcours utilisateur complet ; **statut : CRITÈRES_LOCAUX_LUS, NON_CERTIFIÉ**.

### A04 — S-007

**Critère utilisateur à respecter :** Rejet de faux sujets sur corpus annoté et consentement IA facultatif ; fallback manuel et sortie tardive STALE. **Contre-expertise hostile :** Ne pas confondre préparation Print Then Cut et certification d'une sélection sémantique.

| Ticket source | Références locales + DoD (exactes dans la ligne du lot) | Tests locaux cités et axes | Écarts du lot 23 non recopiés explicitement dans la micro-fiche |
|---|---|---|---|
| [V34-007](../roadmap-v3.4/02_VISION_PARCOURS.md) L219 | **V34-007 P0** Parcours 12 stickers \| S-007, S-008, S-023, S-028, S-029, S-070, S-071, R33-004, R33-005, V34-002 \| Future `docs/roadmap-v3.4/specs/STICKER_FLOW.md`, `tests/fixtures/v34_sticker_synthetic/` \| T-V34-02-01..06 ; preuve auto/Windows/Design Space distincte ; DoD = transitions, tailles, erreurs et handoff testables ; rollback = conserver P01 V3.3 | `T-V34-02-01` L197 (auto + Windows) · `T-V34-02-02` L198 (auto + Windows) · `T-V34-02-03` L199 (auto + UX) · `T-V34-02-04` L200 (auto + UX) · `T-V34-02-05` L201 (auto + Design Space) · `T-V34-02-06` L202 (UX + Design Space) | Aucun écart de ce sens |
| [V34-069](../roadmap-v3.4/10_ANALYSE_VISUELLE.md) L226 | **V34-069** Stratégie règles alpha/dessin et fallback \| **P0** S-007/014, R33-006/007, V34-017/050/059 ; `engine/smartsvg_app/vision/rule_proposer.py` ; T-V34-10-05..08, auto ; DoD aucune silhouette rectangle inventée ; rollback outils de sélection manuelle | `T-V34-10-05` L192 (auto) · `T-V34-10-06` L193 (auto) · `T-V34-10-07` L194 (auto) · `T-V34-10-08` L195 (auto) | Aucun écart de ce sens |
| [V34-071](../roadmap-v3.4/10_ANALYSE_VISUELLE.md) L228 | **V34-071** QA masques déterministe + conflits \| **P0** S-007/014/071/073, R33-006/034, V34-012/062 ; `engine/smartsvg_app/vision/mask_qa.py` ; T-V34-10-15..17, auto ; DoD rapports reproductibles et faux badges interdits ; rollback revue manuelle obligatoire | `T-V34-10-15` L202 (auto) · `T-V34-10-16` L203 (auto) · `T-V34-10-17` L204 (auto) | Aucun écart de ce sens |
| [V34-082](../roadmap-v3.4/11_MODELES_IA_LOCAUX.md) L217 | **V34-082 P0** Intégration AnalysisPort + ROI/identités \| S-007/014/023/028 ; R33-004/006/026 ; V34-068..074/080/081 \| `engine/smartsvg_app/models/vision_adapter.py` ; T17/18/22..24 ; preuve auto + UI ; DoD propositions seulement et digest float32 ; rollback règles/manuelles | `T-V34-11-17` L190 (auto) · `T-V34-11-18` L191 (auto) · `T-V34-11-22` L195 (auto) · `T-V34-11-23` L196 (auto) · `T-V34-11-24` L197 (auto) | Aucun écart de ce sens |
| [V34-110](../roadmap-v3.4/14_LANGAGE_FABRICATION.md) L258 | **V34-110** recette Print Then Cut sémantique \| **P0** S-007/009/029/070, R33-004/022, V34-007/087..095/106/109 ; `.../fabrication/print_recipe.py`, `tests/fabrication/test_print_recipe.py` ; T05/19/20 ; auto+DesignSpace ultérieur ; DoD PNG raster distinct de CUT et A4 non rectangulaire ; rollback transfert PNG historique | `T-V34-14-05` L219 (auto) · `T-V34-14-19` L233 (auto/UI) · `T-V34-14-20` L234 (auto/Design Space) | Aucun écart de ce sens |

**Recettes locales :** - `T-V34-02-01` (source L197) : Import et réouverture conservent octets source + SHA identiques
- `T-V34-02-02` (source L198) : 12 IDs confirmés restent 12 après correction, undo, réouverture
- `T-V34-02-03` (source L199) : 11/13 sujets proposés ne deviennent jamais « 12 confirmés »
- `T-V34-02-04` (source L200) : Taille sticker inconnue interdit prévol `PASS`
- `T-V34-02-05` (source L201) : Zone A4 inconnue bloque « placement garanti », sans inventer rectangle
- `T-V34-02-06` (source L202) : A4 : guide d'impression portrait + placement long côté horizontal, puis vérification manuelle
- `T-V34-10-05` (source L192) : Alpha RGBA et LoadImage MASK concurrents → refus ambigu
- `T-V34-10-06` (source L193) : Alpha opaque/vide ne produit aucun sujet « certifié »
- `T-V34-10-07` (source L194) : Fond blanc non uniforme/photo → règles refusent rectangle arbitraire
- `T-V34-10-08` (source L195) : Source H/W permutées, NaN/Inf, shape/strides invalides → rejet
- `T-V34-10-15` (source L202) : Chevauchements/îlots/accessoires sont signalés avec régions précises
- `T-V34-10-16` (source L203) : Un masque touchant bord n'est pas auto-accepté sans revue
- `T-V34-10-17` (source L204) : Digest exact float32, forme et transformation vérifiés avant acceptation
- `T-V34-11-17` (source L190) : Inference reçoit handle local qualifié, jamais URL de repo
- `T-V34-11-18` (source L191) : Aucun modèle ne modifie `.smartsvg` sans CommandPort/receipt
- `T-V34-11-22` (source L195) : Réponse inférence tardive sur SHA projet modifié → STALE, 0 mutation
- `T-V34-11-23` (source L196) : Sortie masque NaN/ROI invalide → BLOCKED sans ID sujet
- `T-V34-11-24` (source L197) : 12/24/50 propositions : pas de troncature ni sérialisation V1 interdite
- `T-V34-14-05` (source L219) : PRINT_THEN_CUT est recette composite ; ne devient pas une opération de PATH
- `T-V34-14-19` (source L233) : A4 Print Then Cut n'utilise pas la pleine page comme zone de coupe
- `T-V34-14-20` (source L234) : 12 escargots : PNG et contrat Print Then Cut restent distincts du SVG Cut

**Décision :** RACCORDER ou RAFFINER les contrats sources, sans qualifier le parcours utilisateur complet ; **statut : CRITÈRES_LOCAUX_LUS, NON_CERTIFIÉ**.

### A08 — S-016

**Critère utilisateur à respecter :** Comparaison objective avant/après, dimension mm/ppi documentée et interpolation CPU annoncée. **Contre-expertise hostile :** Pas de fausse promesse de détails reconstruits ou de fidélité matérielle mesurée.

| Ticket source | Références locales + DoD (exactes dans la ligne du lot) | Tests locaux cités et axes | Écarts du lot 23 non recopiés explicitement dans la micro-fiche |
|---|---|---|---|
| [V34-089](../roadmap-v3.4/12_RASTER_PIPELINE.md) L165 | **V34-089 P0** tailles, rééchantillonnage et texture CPU \| S-016/029/050 ; R33-018/022 ; V34-087/088 \| `engine/smartsvg_app/raster/resize.py`, `tests/raster/test_resize.py` ; T11..13/16 ; preuve auto/Windows ; DoD unité mm explicite, pas de faux HD natif ; rollback texture originale | `T-V34-12-11` L134 (auto) · `T-V34-12-12` L135 (auto + UX) · `T-V34-12-13` L136 (auto + UX) · `T-V34-12-16` L139 (auto) | `S-048` |

**Recettes locales :** - `T-V34-12-11` (source L134) : `mm×ppi/25.4` : largeur px arrondie explicitement, metadata ppi conservée
- `T-V34-12-12` (source L135) : Taille mm absente → aucune mention « taille physique garantie »
- `T-V34-12-13` (source L136) : CPU interpolation 300→600 ne porte jamais badge « détails natifs augmentés »
- `T-V34-12-16` (source L139) : Image texture IA différente ne change pas le digest de coupe accepté

**Décision :** RACCORDER ou RAFFINER les contrats sources, sans qualifier le parcours utilisateur complet ; **statut : CRITÈRES_LOCAUX_LUS, NON_CERTIFIÉ**.

### A12 — S-032

**Critère utilisateur à respecter :** PNG Print Then Cut, SVG Basic Cut, SVG Cut multicouche et SVG éditable restent quatre projections distinctes, avec QA par rôle. **Contre-expertise hostile :** Une courbe simplifiée n'établit ni export multicouche ni validation Design Space.

| Ticket source | Références locales + DoD (exactes dans la ligne du lot) | Tests locaux cités et axes | Écarts du lot 23 non recopiés explicitement dans la micro-fiche |
|---|---|---|---|
| [V34-098](../roadmap-v3.4/13_VECTORISATION_SVG.md) L220 | **V34-098 P0** courbes et simplification sûre \| S-011/033/034/060, R33-008/022, V34-096/097 \| `.../vector/curve_fit.py`, `tests/vector/test_curve_fit.py` ; T06/09/10 ; auto ; DoD aucun trou perdu, métriques bornées ; rollback polyline non simplifiée | `T-V34-13-06` L184 (auto) · `T-V34-13-09` L187 (auto) · `T-V34-13-10` L188 (auto) | `R33-029`, `S-032` |
| [V34-112](../roadmap-v3.4/14_LANGAGE_FABRICATION.md) L260 | **V34-112** Pen/Draw + Cut \| **P1** S-032/085/093, R33-008/019/022, V34-106/107/109/111 ; `.../fabrication/draw_plan.py`, `tests/fabrication/test_draw.py` ; T04/16/29 ; auto+UI+DesignSpace futur ; DoD DRAW non transformé en CUT ; rollback guide-only | `T-V34-14-04` L218 (auto) · `T-V34-14-16` L230 (auto/UI/Design Space) · `T-V34-14-29` L243 (UI/Windows) | `S-045` |
| [V34-129](../roadmap-v3.4/17_EXPORTS_DESIGNSPACE.md) L105 | **V34-129 P0** — projection des quatre contrats approuvés \| S-002/029/030/032/075, R33-008, V34-100/101 ; **adapter** `production_v211.py`, `direct_import_v218.py` et les profils SVG du lot 13 ; éventuel routeur léger **futur** `engine/smartsvg_cricut/export_contracts.py` seulement si nécessaire \| T01..05 ; auto, Design Space ultérieur ; DoD quatre projections distinctes, V1 non élargi ; rollback exporters historiques conservés | `T-V34-17-01` L85 (auto) · `T-V34-17-02` L86 (auto) · `T-V34-17-03` L87 (auto) · `T-V34-17-04` L88 (auto) · `T-V34-17-05` L89 (auto) | `S-009` |

**Recettes locales :** - `T-V34-13-06` (source L184) : Courbe Bézier fermée : aucun PASS topologique sans vérification de courbe
- `T-V34-13-09` (source L187) : Simplification qui supprime un trou → refus, ancien digest conservé
- `T-V34-13-10` (source L188) : Simplification valide : métriques de contour/surface avant-après consignées
- `T-V34-14-04` (source L218) : PRINT sur PATH et SCORE sur RASTER_REGION refusés
- `T-V34-14-16` (source L230) : Pen + Cut garde DRAW distinct et propose guide Attacher
- `T-V34-14-29` (source L243) : Interface clavier/lecteur d'écran : opérations, avertissements, correctifs accessibles
- `T-V34-17-01` (source L85) : Les quatre choix exportent des contrats distincts ; le SVG multicouche n'est jamais stocké sous `Artifact.use=editable_svg` V1
- `T-V34-17-02` (source L86) : Un PNG Print Then Cut conserve pixels/alpha/empreinte ; aucun SVG de diagnostic n'est automatiquement ajouté comme seconde coupe
- `T-V34-17-03` (source L87) : Basic Cut refuse trou ambigu, contour ouvert non autorisé, double coupe, SVG actif et dimensions non physiques
- `T-V34-17-04` (source L88) : SVG multicouche conserve ordre, groupes, repère mm et IDs ; aucune conversion silencieuse en SVG d'édition
- `T-V34-17-05` (source L89) : SVG d'édition conserve styles/couches dans le profil autorisé ; pas de mention « Basic Cut prêt »

**Décision :** RACCORDER ou RAFFINER les contrats sources, sans qualifier le parcours utilisateur complet ; **statut : CRITÈRES_LOCAUX_LUS, NON_CERTIFIÉ**.

### B09 — S-036 — aucune micro-fiche V34 directe

**Critère utilisateur à respecter :** Composition texte/police sans substitution silencieuse ; S-035 impose réouverture éditable et S-064/R33-028 exigent licences/glyphes. **Contre-expertise hostile :** Aucun ticket V34 direct : port texte/persistance V1 doit rester brouillon avant ADR de schéma et revue.

**GAP G6/G9 connu :** `S-036` n'a pas de ticket V34 direct dans le lot 23 ; son contrat complet est issu des sources V3.3 et de COV10C, non d'une parenté supposée avec V34-133.

**Références candidates à instruire :** S-035 (édition après réouverture), S-064 et R33-028 (police/licence/glyphes). Aucun de ces liens ne doit être étiqueté « implémenté » faute d'ADR.


**Tests à ajouter en V3.5 (NON_EXÉCUTÉS) :** absence de police et de glyphe, licence non redistribuable, brouillon annulé sans mutation du V1, réouverture après une migration explicitement approuvée ; test physique non applicable à la police mais reste nécessaire si le texte devient une découpe.

**Décision :** BLOQUÉ pour persistance V1, spécification en brouillon ; **statut : CRITÈRES_LOCAUX_LUS, NON_CERTIFIÉ**.


## 3. Écarts de citations entre le registre transversal et les micro-fiches

| UX | Ticket | Exigences affichées par le lot 23 mais non citées sur sa micro-fiche V3.4 | Lecture correcte |
|---|---|---|---|
| A02 | V34-132 | `S-003` | **Delta documentaire à clarifier**, pas nécessairement une contradiction fonctionnelle |
| A03 | V34-133 | `R33-006`, `S-008`, `S-026`, `S-080`, `S-086`, `S-087` | **Delta documentaire à clarifier**, pas nécessairement une contradiction fonctionnelle |
| A08 | V34-089 | `S-048` | **Delta documentaire à clarifier**, pas nécessairement une contradiction fonctionnelle |
| A12 | V34-098 | `R33-029`, `S-032` | **Delta documentaire à clarifier**, pas nécessairement une contradiction fonctionnelle |
| A12 | V34-112 | `S-045` | **Delta documentaire à clarifier**, pas nécessairement une contradiction fonctionnelle |
| A12 | V34-129 | `S-009` | **Delta documentaire à clarifier**, pas nécessairement une contradiction fonctionnelle |

Les différences d'index vont **dans les deux sens** : de nombreuses micro-fiches citent davantage d'exigences que l'index inverse du lot 23. Il ne faut donc ni remplacer l'index transversal par les citations locales, ni conclure à `PASS` depuis une simple union de références. La décision d'autorité reste celle des critères intégraux V3.3/V3.4, avec une note de delta V3.5 si le traitement change.

**Cas particulièrement critiques :**
- **A03 / V34-133** : le registre lie R33-006 (masques float32) au ticket, la micro-fiche n'en donne pas explicitement le même rattachement ; `V34-028` cite en revanche R33-006 via `R33-004..006`. L'UI des calques ne doit pas autoriser de mutation hors writer.
- **A12 / V34-098** : le registre lie S-032 au ticket de courbes, tandis que le DoD local porte sur simplification et préservation topologique. Cela ne prouve ni export CUT multicouche ni mise en page de livraison.
- **A12 / V34-129** : rôle G4 clair et T-V34-17-01..05 cités, mais la ligne locale ne cite pas S-009 bien qu'il figure dans l'index inverse. Ce point mérite revue de critères, non changement arbitraire du code.
- **B09** : absence de ticket V34 direct **confirmée** ; les objets de texte persistants et les substitutions de fontes exigent contrat/migration/ADR, et non un champ V1 glissé dans `editor_v216`.
- **A04** : rejeter un rectangle arbitraire (`10-07`) ou un masque invalide (`11-23`) ne remplace pas un benchmark de faux sujets sur corpus annoté.
- **A08** : `12-13` impose explicitement d'éviter le badge trompeur « détails natifs augmentés » sur interpolation CPU.

## 4. Micro-lots de validation et dépendances (à faire par le producteur natif après adoption)

1. **Identité A02/A03** : fixture synthétique 12 sujets à identifiants stables, trous/îlots ; tests unitaires pour `T-V34-02-02`, `05-03/04`, `18-02/03`. Négatifs : ID dupliqué, float32 de dimensions invalides, révision CAS périmée. UI Windows/Undo et relire le projet. Sans persistance V2 adoptée, booléens restent brouillons.
2. **Sujets A04 / HD A08** : corpus autorisé avec distracteur dominant ; T-V34-10-07/15/16, 11-22/23, 12-11/12/13/16. Négatifs : alpha ambigüe, modèle absent/non consenti, résultat asynchrone tardif ; p50/p95/RAM/VRAM à **mesurer**. Aucune inférence réseau sans consentement.
3. **Quatre exports A12** : T-V34-17-01..05 + 13-09 et 14-04/16 ; valider rôles, unités mm, topologie, archive V1 intacte ; tests XML externe, NaN, calques échangés, police sous licence. **Design Space** sur version ciblée puis **coupe physique** séparée selon profil connu, pas `PASS` depuis CI.
4. **Typographie B09** : rédiger ADR de schéma et migrateur avant toute écriture persistante ; police absente/glyphe manquant, licence, collision de nom, annulation et réouverture à faire valider. Repli : brouillon visible non enregistrable et aide explicite.
5. **Qualité UX** : états vide/en cours/échec/succès non certifié, clavier/lecteur écran, 1366×768/DPI 200 %, motion réduit, Undo/Redo ; aucune déclaration de fluidité sans mesure Windows. Conserver profils tri-state (KNOWN/UNKNOWN) et les opérations CUT/SCORE/DRAW/PRINT/FOIL distinctes.

**Revue qualité 25 axes :** héritage 24/141/140/80/437 inchangé ; fonctions et preuves disjointes ; V1/CAS/float32, 4 exports, UX novice/expert, IA facultative sous consentement, données/licences, tests de reprise, non-duplication de writer, Windows/a11y et mécanismes d'échec décrits. Smart Delivery/Fabrique sont **hors portée de ces six gestes**, mais restent obligatoires dans les groupes W correspondants. **Aucun critère technique marqué PASS ni autorisation normative modifiée.**

## 5. Conclusion et relais précis

**Acquis :** lecture des DoD locaux et références des 13 micro-fiches, sans transposer des liens inférés en critères normatifs. **Ouvert :** arbitrer les écarts du registre, compléter les critères sémantiques des 24 autres UX A/B et tester les fonctions par axe. Les dix exigences G6/G9 hors tickets V34 et six scénarios historiquement sans ticket explicite restent signalés.

**Prochaine action unique COV-18A-2d :** procéder à l'**arbitrage contradictoire** des écarts `V34-098/S-032`, `V34-133/R33-006`, `V34-129/S-009`, en confrontant textes intégraux V3.3/lot 23 et signatures de ports existants ; décider dans quel groupe W se trouve le DoD réel, puis étendre le contrôle UX A/B aux 24 autres IDs sans les redéfinir. Cette étape ne saurait se substituer au backlog global, aux 33 opportunités ni aux fonctions Smart Delivery.
