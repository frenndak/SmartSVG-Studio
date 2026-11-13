# V35-COV-18A-3c — 12 UX B restantes : objets, typographie, OCR et composition

**13/11/2026 — CONTRE-EXPERTISE CANDIDATE, NON NORMATIVE.** Reprise des **12 IDs B02–B08 et B10–B14**, pour compléter les 30 IDs A01–A16/B01–B14 après [COV18A2C](COV18A2C_LOCAL_DOD_SIX.md), [COV18A2D](COV18A2D_ARCHITECTURE_ARBITRATION.md), [COV18A3A](COV18A3A_UX_NEXT_SIX.md) et [COV18A3B](COV18A3B_VECTOR_OBJECTS_SIX.md). **30/30 IDs maintenant confrontés à des exigences et à des frontières de code par fiche**, mais **0/30 certifiés prêts à coder**, 0 tests produits exécutés, V3.4 toujours ACTIVE. Sources du snapshot GitHub main aa0ff9e7d0c53dba3fdc429c02c6198736cfe935, V3.3 MASTER/TRACEABILITY/HERITAGE, lot 23 V3.4 et [UX #134](https://github.com/frenndak/SmartSVG-Studio/issues/134).

## 1. ERREUR DE RATTACHEMENT CORRIGÉE — B12 et B13

Le tableau candidat historique [COV18A1B](COV18A1B_AB_TRACE_REMAINING_20.md) associait **B12 (texte → chemins)** à S-021/S-047 (exigences OCR) et **B13 (OCR → texte éditable)** à S-064/R33-028 (licences, polices, glyphes). Ce n'est **pas** un raccordement principal justifié par les critères V3.3. **Correction opposable dans la conception candidate :**

- **B12 texte → chemins** → **S-036** (« Fonts et conversion textes → tracés », P1/G6.3, dépend S-035, **pas de substitution silencieuse**), **S-064** (typographie et licence, rendu reproductible ou avertissement précis) et **R33-028** (licences/glyphes manquants visibles). Les trois demeurent **sans ticket V34 direct** au lot 23. S-032 n'est qu'une dépendance d'export à vérifier par rôle, pas la preuve d'une conversion de fonte.
- **B13 OCR facultatif → texte après validation** → **S-021** (« OCR et gestion du texte sur affiches », P2, texte préservé/averti) et **S-047** (« OCR texte de couverture », P2/G9, dépend S-028/S-036, **texte vérifié avant remplacement**). **S-036/S-064** servent ensuite au rendu/édition de texte reconnu, **pas** de preuve du moteur OCR. Le routage IA inspecté ne prouve pas d'OCR natif.
- Le contenu historique COV18A1B reste disponible comme **trace d'une hypothèse rejetée**, mais les futures matrices doivent citer **COV18A3C** et ne plus réutiliser l'inversion. Ne pas changer les dix obligations G6/G9, leur priorité ni inventer de tickets V34.

## 2. Contre-expertise individuelle des 12 candidats

| ID | Intention UX #134 | Obligations historiques vérifiées ; statut du lien | Décision et DoD de conception V3.5 |
|---|---|---|---|
| **B02** | calques visibles, verrouillés, groupés, ordre/opacité | **S-087** multi-sélection/groupement (P1/G6.6, identité préservée), **S-035** composition éditable après réouverture (P1/G6.1), tous deux → **V34-133** dans lot 23 | **P0 UX, P1 héritage** ; brouillon de LayerDraft non mutant, ordre/visibilité, Undo. Les groupes SVG couleurs ne font pas des calques persistés. **ADR schéma avant sauvegarde de calques.** |
| **B03** | décomposition intelligente des accessoires | **S-028** sujet et accessoires sans perte d'identité (P0/G3.3), **S-014** segmentation multiobjets (P1), → **V34-073** | **P1** : propositions sujet/accessoire avec confiance et validation, conserver IDs, liens explicites, jamais découpage sémantique automatiquement certifié. |
| **B04** | poignées de transformation | **Déjà approfondi** COV18A2A/2B et COV18A_UX_AB_CROSS_REVIEW : S-086→V34-133 (poignées/mm), transformation persistante non prouvée | **NE PAS REFAIRE**. Reprendre DoD d'identité, coordonnées mm et brouillon, sans attribuer à un viewport raster une transformation d'objet persistante. |
| **B05** | alignement, distribution, grille, aimantation | **S-086** (P1/G6.6) « proportions, alignements, guides vérifiés » → V34-133 | **P0 UX** : guides mm avec tests rotation/zoom, snap sans déplacement de mauvaises cibles. Un rectangle de sélection ne prouve pas un moteur d'alignement. |
| **B06** | perspective, warp et masques d'écrêtage | S-035 est un **point d'entrée faible** (canevas objets/textes), pas une prescription explicite de perspective ; V34-133 ne démontre pas warp/clip | **P2 étude** : rester candidat, ne pas bloquer S-035 ni introduire de type V1 clandestin ; vérifier topologie et sortie raster/vecteur avant validation. |
| **B07** | articulation locale de personnage | S-028/V34-073 concerne accessoires et identité, **pas** un rig articulé | **P2 étude** : proposer pivots/contraintes, modèle squelettique séparé du masque ; aucune IA ou physique « reconnue » présumée. |
| **B08** | reconstruction opt-in derrière sujet déplacé | S-014/V34-073 est une **proximité de segmentation**, non une exigence d'inpainting | **P2 conditionnelle** : opt-in IA, masque et provenance, diff visible, aucune mutation si modèle absent/refusé ou SHA périmé ; mode manuel disponible. |
| **B10** | texte sur chemin, monogrammes, courbes | **S-036/S-064** fondent le contrôle police/tracés/licence mais ne prescrivent pas explicitement le texte sur chemin ; G6 sans V34 direct | **P1** : fonction supplémentaire à spécifier, parent path et orientation versionnés, glyphes FR, calcul de baseline, conversion tracés seulement sur dérivé autorisé. |
| **B11** | effets de texte, contours, ombres, dégradés | **S-092** (P1/G6.3) choix police/aperçu/alerte glyphes, **pas** une obligation d'effets texte complets ; G6 sans V34 direct | **P1** : décorations dérivées réversibles, distinguer style/rendu du chemin CUT ; palette et ombre n'annoncent pas matière validée. |
| **B12** | **texte → chemins** et contrôles de fabrication | **CORRIGÉ** : S-036/S-064/R33-028 (police/tracé/licence/glyphes), sans ticket V34 direct ; S-032 en aval export édition/coupe | **P1** : fonte/licence explicite, formes des accents/ligatures, courbes fermées lorsque profil CUT l'exige, copie export externe ; source texte reste modifiable sous un schéma autorisé. |
| **B13** | **OCR → texte éditable après validation** | **CORRIGÉ** : S-021/S-047 (OCR vérifié avant remplacement), S-036 comme dépendance de composition | **P1 étude, P2 IA** : OCRProposal non mutante, boîtes px orientées, confiance/UNKNOWN, correction manuelle et demande explicite de commit. |
| **B14** | Smart Compose : marges, hiérarchie et modèles | **S-037** (P1/G6.4) trois gabarits métiers **sans V34 direct** ; **S-088** (P1/G6.7) étiquette/carte/topper sauvegardés et repris → V34-126 | **P1** : assistant de mise en page à règles, trois gabarits vérifiés, composition non destructive, labels FR ; la géométrie d'une boîte ne remplace pas une composition avec texte/objets. |

**B04 figure dans le tableau pour la couverture 12/12, mais son analyse technique appartient déjà à la tranche précédente COV18A : elle ne compte pas comme un treizième nouvel ID.** Après contrôle d'ensemble : A01–A16 = 16, B01–B14 = 14, aucun doublon ni disparition.

## 3. Contrats de données, points de blocage et DoD

**État réel des ports à conserver :** projet unique et writer CAS, Subject/Mask float32 et Artifact V1 ; parse_editor_document V21.6 accepte exactement version,width,height,count,source,strokes ; il **rejette** les champs persistants text/layers/objects hors schéma ; SVG groupé par couleurs n'est ni calque natif ni objet typographique. V34-133 est un panneau de propriétés dérivées, pas un stockage universel. Les critères G6/G9 ne sont pas éliminés par la présence du canevas Tk.

**Contrats PROPOSÉS (non implémentés)** : LayerDraft{source_revision,subject_id,visibility,order,opacity}, TextDraft{source_text,font_ref,license_status,glyphs,layout,expected_revision}, OCRProposal{source_sha,bboxes_px,text,confidence,model_provenance}. Ce sont des **brouillons externes/non persistés** tant qu'une ADR ne fixe pas un schéma compatible, reader/writer, migration et rollback. Une API native de texte/objets doit être démontrée par code/UX Windows et tests, pas inférée du nom de classe.

**Séquencement minimal (micro-lots) :**
1. B02/B05 : panneau calques/alignements **non mutant**, sources V1 connues, tests gestes clavier/Undo, ordre et millimètres sans mutation.
2. B03 : accessoires avec IDs stables, liens proposés et revisables, repli manuel.
3. B12 et B10 : police/licence/glyphes/chemins sur un export dérivé, source éditable inchangée, QA SVG par rôle.
4. B13 : OCR en proposition locale facultative, validation humaine obligatoire, jamais remplacement silencieux.
5. B11/B14 : effets texte et modèles métiers, trois gabarits sauvegardés et rouverts **après autorité de persistance**.
6. B06/B07/B08 : recherche/expérimentation P2, seulement après socle stable et sans altérer le cycle V3.4.

**Tests de contrat/UX proposés (NOT_RUN)** : projet V1 avec champ layer non autorisé → INVALID_EDITOR_SCHEMA ; multi-sélection/groupement puis Undo/reload conserve les IDs ; 1366×768 et DPI 200 % n'escamotent pas les contrôles ; texte français ligature/accent avec police absente → avertissement sans substitution ; texte sur path avec cercle dégénéré → refus ; OCR caractères confondus → correction manuelle/diff, source immuable ; glyphes redistribués sous licence interdite → bloquer inclusion pack ; projet édité en parallèle → CAS STALE ; récupération après crash/disque plein ne remplace pas le projet sain ; profils SVG Basic/MultiCut/Editable/PNG PTC séparés ; Design Space et coupe physique sont deux validations distinctes. **Aucun test exécuté par cette fiche.**

## 4. Conclusion et suite

**Corrigé** : inversion B12/B13 dans la matrice candidate historique. **Déterminé** : 12 candidats B restants avec frontières de persistance/IA, sans retirer les dix exigences G6/G9. La **couverture de première contre-expertise approfondie des 30/30 IDs A/B** est maintenant documentée en plusieurs fiches, mais **certification prête à coder = 0/30**. Toutes les autres fonctions UX C01–C18, D01–D12, E01–E20 disposent de décisions initiales seulement ; la revue contradictoire détaillée reste à faire.

**Prochaine étape unique : V35-COV-18B** — confronter les **18 fonctions C01–C18** aux critères intégraux V3.3, tickets V34, DoD locaux et spécifications Smart Delivery / prévol Cricut ; pointer les gaps et ne pas confondre design matériel et preuve physique. Puis traiter D/E et faire contre-expertise transversale avant revue de promotion.
