# Photographie des 15 groupes de périmètre #142

Photographie de lecture du 14 novembre 2026 du [programme propriétaire #142](https://github.com/frenndak/SmartSVG-Studio/issues/142), section C. Les lignes sont reproduites sans réécriture ; statut candidat, pas adoption ou preuve produit. Ce fichier sert de référence locale de non-perte au contrôleur.

SHA-256 du corps de source récupéré : `02859c1f0afa300420390810e9643c8fbb08d772f4c729886c5970c720ae8895`.

| Groupe | Valeur et fonction | Décision provisoire / dépendances |
|---|---|---|
| **Fondation produit** | Traçabilité exigences→ticket→code→UI Windows→tests→terrain ; 3 parcours E2E, qualité de sauvegarde/recovery, unités, 4 exports ; réparation gros PNG / petit preview | **P0**, prérequis seulement pour les consommateurs concernés |
| **Architecture UI** | Expertise Tkinter vs Qt/Tauri sur performances, accessibilité, packaging et maintenance ; design system, interactions progressives, ergonomie très faible friction | **P1 étude** ; migration **P0 seulement si blocage prouvé** |
| **Smart Delivery** | SD0/SD1 manifeste ZIP, SHA, no-clobber, QA, archive externe à partir d'un vrai export ; V2 guide HTML statique/hors ligne, Design Space manuel et confidentialité ; V3 reconstitution/versions, comparaison | **P1 élevé** pour SD0–SD2, **P2** pour historique avancé ; première fonction signature choisie |
| **Smart Cut Advisor** | Complexité de coupe, microchemins, fragilité/topologie, variantes fidèle/équilibrée/facile, prévol explicable | **P1**, réemploi C07/C08/C09 et lots 13–15 |
| **Smart Weeding** | Diagnostic des zones d'échenillage difficiles, aperçu non destructif ; lignes et boîtes de séparation automatiques après preuve | **P1 étude**, **P2** pour chemins générés si tests physiques insuffisants |
| **Print Then Cut Assistant** | Transparence/bleed, tailles, impression et orientation, calibration extérieure, feuille/tapis, avertissements | **P1**, réemploi lots 12/15/17/22 et O-001/002/032 |
| **Compatibilité Design Space** | Matrice versionnée, contrôle manuel taille/calques/Attach/opérations, rapport de transfert sans prétendre contrôler la machine | **P1** |
| **Smart Cost** | Estimation déclarative des consommables, prix matière, surface et pertes, options ; aucun tarif inventé | **P2**, après nesting fiable |
| **Séries personnalisées** | CSV + textes, noms/numéros/QR, variantes et packaging de lots ; pas de nouveau moteur CSV ni duplication | **P2**, réemploi lot 20, B09/B12/D11 |
| **Smart Cut Feedback** | Photo du résultat réel, comparaison géométrique, écarts et incertitudes ; pas de diagnostic garanti | **P2 recherche**, besoin de corpus physique autorisé |
| **Recettes/modèles partageables** | Fabrication paramétrique reproductible, import/export de recettes sûr, versions et provenance | **P2**, après Fabrique et Delivery |
| **Production multimarque** | Adaptateurs de profils autres machines sans pilotage non documenté ni affirmation matérielle | **P2 recherche**, Explore 5 prioritaire |
| **Optimisation multicritère** | Compromis fidélité/complexité coupe/perte matière/coût/temps ; arbitrage explicable | **P2 recherche**, métriques vérifiées |
| **80 capacités UX** | Smart Select/Clean/Vector/Objects/Color/Text/Cut/Layout/Fabrique/Assist/Library, fusion UX sans réduire les contrats | Couverture **80/80 obligatoire**, chacune décidée GARDER/ÉTENDRE/FUSIONNER/REPORTER/REJETER avec justification, pas 80 boutons |
| **Héritage intégral V3.4** | IA locale optionnelle, assistant contextuel, batch 12/24/50, patrons CUT/SCORE/DRAW/PRINT/FOIL, archive/reprise, Windows autonome, tests | **OBLIGATOIRE**, pas d'affaiblissement pendant V3.5 |
