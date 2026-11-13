# V35-COV-18C1 — D01–D06 : contre-expertise IA locale, segmentation, matting et HD
**Statut : CANDIDAT / REVUE DOCUMENTAIRE ; NON NORMATIF ; tests NOT_RUN.** Date : 2026-11-13. Sources consultées : V3.5 INHERITANCE_REGISTER (blob cc0dd60e), V3.4 lots 08 (e638a1b0), 10 (9c0b0648), 11 (9a169e3c), 12 (30424177), README V3.4. main HEAD NON_VÉRIFIÉ ; snapshot de référence aa0ff9e7, non preuve du HEAD. Les contrats et ports ci-dessous sont **propositions** tant que le code exact n'est pas inspecté.

## Héritage individuel et décision
| ID #134, texte exact du registre | Raccordement source pertinent, à confirmer par critères intégraux | Décision / risque contradictoire |
|---|---|---|
| D01 « fournisseurs de segmentation CPU/SAM léger/SAM2/3 selon viabilité réelle » | lot 10 V34-068..077, T-V34-10-10/21/24 ; lot 11 V34-078..086, T-V34-11-04/17/21 | **AMÉLIORER** catalogue de capacités vérifiées, sans promettre SAM3 ou téléchargement automatique. Alternative CPU déterministe pour détourage simple ; modèle non qualifié = indisponible |
| D02 « consignes clic/lasso/pinceau/texte combinées » | lot 10 T-V34-10-17/18/22 ; lot 08 V34-050..058, T-V34-08-02/06/08 | **RACCORDER** gestes au même brouillon de sélection ; texte facultatif interprété comme proposition, jamais instruction de mutation ; masque ≠ sélection |
| D03 « variantes et choix expliqué avec confirmation » | lot 10 T-V34-10-19/23 ; lot 08 T-V34-08-07/08/09 | **AMÉLIORER** variantes comparables à source/ROI identiques, explication vérifiable et commit CAS unique ; pas de confirmations pour simples gestes Undo |
| D04 « matting cheveux/poils/translucide » | lot 10 masques float32 et lot 12 T-V34-12-05/06/08/10 | **RACCORDER** à alpha/ROI/provenance existants ; la segmentation binaire n'est pas une preuve de matting ; contours transparents à mesurer |
| D05 « upscale HD conditionnel » | lot 12 T-V34-12-11/12/13/14/15/16 | **AMÉLIORER** distinguer pixels interpolés, détails inférés et résolution physique ; pas de badge « détail natif » pour CPU |
| D06 « génération raster/vector facultative » | lot 11 consentement/licence et lot 13 vectorisation ; exigences IA S-042/S-050/S-053 à vérifier contre V3.3 | **REPORTER P2** derrière moteur d'édition/export vérifié ; génération ≠ vectorisation de l'existant ; aucun modèle génératif présumé installé ou commercialement autorisé |

**Frontière de preuve :** les associations ci-dessus sont des rapprochements de conception, pas des liens normatifs exhaustifs. Vérifier les critères V3.3 et les DoD complets de chaque ticket avant certification. D01–D06 sont 6 IDs distincts du registre des 80, sans changement du compteur historique.

## Contrat transversal candidat (sans nouveau writer)
**Source de vérité** : projet unique .smartsvg V1, source originale SHA, Subject ID stable, masque float32 et provenance ; CommandPort/receipt/CAS existants restent seuls autorisés à écrire. Aucun modèle n'écrit directement le projet, ni n'active une migration V2. Les quatre sorties restent **PNG Print Then Cut / SVG Basic Cut / SVG CUT multicouche / SVG éditable** ; une sortie générative n'est jamais automatiquement certifiée CUT.

**Entrée proposée** `ProposalRequest{project_sha,revision,subject_id?,source_sha,roi_px:[x,y,w,h],view_transform_version,gesture_provenance,provider_id?,model_revision?,consent_receipt?}`. Coordonnées ROI en **pixels source orientés EXIF**, dimensions strictement positives, version de transformation obligatoire. **Sortie** `ProposalBundle{base_revision,source_sha,proposals:[{proposal_id,mask_float32_sha?,alpha_preview_sha?,raster_preview_sha?,vector_preview_sha?,provider_id,model_sha?,license_status,limitations}],qa_state:KNOWN|UNKNOWN,errors[]}`. Ces noms sont un contrat à arbitrer, **pas une API déclarée existante**. Les sorties preview sont éphémères ; l'acceptation via le bus de commandes existant revalide SHA/révision/identité et produit au plus un receipt. Échec/annulation/OOM/stale = zéro mutation, libération des ressources et reprise du brouillon.

**Machine d'états proposée** : `EMPTY → GESTURE_DRAFT → PROVIDER_CHECK → (CONSENT_REQUIRED | CPU_READY | AI_READY | BLOCKED) → RUNNING → PREVIEW → ACCEPTED/CANCELLED/STALE`. Revenir à `GESTURE_DRAFT` après annulation ou refus IA ; aucune relance réseau implicite. Le consentement couvre fournisseur, modèle, licence, poids, hash, volume et destination. Une préférence « jamais » reste effective. Modèle à licence incertaine, révision flottante, hash absent ou exécution de code distant non revue : INSTALL_BLOCKED.

## Parcours et architecture UX
**Novice** : importer → dessiner une zone au clic/lasso/pinceau → voir immédiatement le contour manuel/CPU → choisir « améliorer » si modèle qualifié présent → comparer 2–3 variantes avec étiquettes honnêtes (CPU/interpolation/IA) → corriger localement avec Undo → accepter → sauvegarder. **Expert** : inspecter SHA source/masque, ROI, fournisseur/version/licence, mesures alpha, mémoire et rapport, puis comparer sans écraser la source. La barre contextuelle affiche l'action, les poignées et la possibilité de revenir ; pas six boutons « Smart ». Sans modèle : l'outil manuel demeure visible. État vide : consigne de geste ; pending : progression et annuler ; erreur : cause et solution CPU/manuel. Prévoir clavier/focus, 1366×768, DPI 200 %, contraste et motion réduit ; aucun résultat UI revendiqué.

**CPU / GPU** : segmentation CPU et corrections manuelles prioritaires ; RTX 8 Go uniquement si budget de mémoire prévalidé par mesure et modèle qualifié, jamais supposer qu'un modèle tient en VRAM. En cas d'OOM, unload et repli explicite. D04 alpha translucide requiert validation sur fonds clair/sombre ; D05 métriques qualité (alpha/halo/différence géométrique), p50/p95, RAM/VRAM et temps mesurés sur fixtures autorisées, sans seuil inventé. D06 n'est pas une dépendance de D01–D05.

## TDD micro-lots, tests et DoD proposés — TOUS NOT_RUN
1. **D01 catalogue/fallback** : fixture de 12 sujets synthétiques, aucun modèle installé ; prévol de capacité et sortie CPU/manuelle, zéro requête réseau. Négatifs : hash absent, licence incompatible, redirection URL privée. DoD : aucun modèle non qualifié activé ; tests lot 11 (04/07/09/10/17/21) rapprochés.
2. **D02/D03 gestes et variantes** : lasso + pinceau + prompt facultatif sur même ROI ; deux variantes et un seul receipt d'acceptation ; Undo rétablit masque et identité. Négatifs : prompt hostile provenant du fichier, double clic d'acceptation, résultat d'ancienne révision. DoD : T-V34-08-04/06/08/09 et 10-17/18/22/23 couverts sans nouveau store.
3. **D04 matting** : fixture poils/cheveux synthétiques et bord semi-transparent, comparaison fond blanc/noir ; alpha float32 valide, source intacte. Négatifs : NaN dans masque, ROI hors limites, halo aggravé. DoD : T-V34-12-05/06/08/10 avec critères mesurés, pas seulement captures visuelles.
4. **D05 HD** : même source 300→600 ppi, dimensions mm explicites, badge interpolation CPU ; digest de coupe inchangé. Négatifs : taille mm inconnue présentée comme garantie, OOM IA, modification du contour accepté. DoD : T-V34-12-11..16, 0 mutation de géométrie.
5. **D06 P2 génératif** : spécifier seulement un preview raster/vector indépendant ; licence et provenance par artefact. Négatifs : poids non autorisé, téléchargement refusé, génération vectorielle confondue avec SVG CUT. DoD bloqué jusqu'à modèle officiel/version/licence/hash et gate sécurité.

**Résilience commune** : injecter annulation, crash avant acceptation, disque plein, double job GPU, conflit CAS et fermeture Windows ; aucun projet corrompu ni fichier partiel publié. Tests automatiques, UI Windows, GPU réel, Design Space et coupe physique = NOT_RUN. Design Space/coupe physique non applicables à la validation des seuls *previews* D01–D05, mais **obligatoires** avant toute revendication d'artefact fabriquable.

## Revue hostile et contrôle des 25 axes
Alternative minimale préférée : enrichir les ports de proposition/commandes, masques, catalogue IA et raster **existants**, pas créer un second moteur, writer ou assistant. Les fournisseurs, fichiers source et PR code doivent être relus avant toute spécification d'implémentation nominative. Un gain UX sans mesure ne vaut pas preuve de performance.
- **01–06** : inventaires 24/141/140/80/437 inchangés ; six IDs approfondis, aucune certification ; statuts de preuve disjoints.
- **07–09** : V1/CAS/float32, quatre sorties, KNOWN/UNKNOWN, aucun pilotage machine.
- **10–13** : gestes directs, Undo, UI accessible à tester ; annulation, stale, crash et concurrence explicités.
- **14–16** : licence/consentement/CPU-GPU, alpha/HD, vecteur éditable ≠ CUT.
- **17–19** : batch/Fabrique/Smart Delivery/33 opportunités **non modifiés dans ce sous-lot**, conservation des exigences et revue future ; D06 reporté avec raison.
- **20–21** : mesures futures, fixtures synthétiques, pas de média sous licence ni secret.
- **22–25** : branche docs seulement, anti-doublons, aucune adoption/merge/promotion, profondeur des contrôles conservée.

**Prochaine action unique V35-COV-18C2 :** contre-expertiser D07–D12 (inpainting, catalogue, budgets, recettes, batch et assistant), en lisant leurs tickets et DoD exacts et en contrôlant les frontières de reprise/consentement.
