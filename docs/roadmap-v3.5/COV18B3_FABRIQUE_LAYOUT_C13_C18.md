# SmartSVG V3.5 — COV-18B-3 : nesting, coûts, Fabrique et patrons (C13–C18)

**13 novembre 2026 — CANDIDATE NON NORMATIVE.** Troisième tranche de contre-expertise des 18 UX C01–C18, suite à [COV18B1](COV18B1_CRICUT_C01_C06.md) et [COV18B2](COV18B2_CUT_LAYOUT_C07_C12.md). Critères historiques V3.3/V3.4 conservés, évaluation basée sur lots 16/19/20, patrimoine G6/G9 et port natif connu au snapshot main aa0ff9e7d0c53dba3fdc429c02c6198736cfe935. **18/18 UX C maintenant examinées sous cet angle**, sans les déclarer prêtes à coder ni exécutées.

## 1. Six fonctions, limites et décisions

| Fonction UX | Héritage et source V3.4 | Limite ou risque identifié | Décision candidate |
|---|---|---|---|
| **C13 — Nesting par silhouettes** | **S-040 P1/G7.4** « imposition mesurable », zéro collision/dimensions cohérentes ; **V34-134** lot 19 (T-V34-19-01/02/04/05/06/07) | Une grille rectangulaire n'est pas un vrai placement par silhouettes ; rotations/marges dépendent d'une géométrie en mm non ambiguë. Aucun « rendement matière garanti » sans mesure. | **P1 RAFFINER** : placement déterministe par contours avec marges/rotations autorisées, findings par page et rejet des collisions. |
| **C14 — Placements verrouillés et réoptimisation** | V34-134 lot19 prévoit verrous stables, rotation consentie et comparaison reproductible ; S-040 reste le prérequis de mesure | Un simple drag/drop ne conserve pas nécessairement des verrous après réoptimisation. Un optimiseur ne doit pas déplacer une pièce explicitement figée. | **P1 AMÉLIORER** : identifiant stable d'instance, lock/version, optimisation des seuls placements libres, undo et diff ciblé. |
| **C15 — Smart Cost / économie de matière** | S-040 imposition ; V34-134/135 placement et reprise 12/24/50. Le devis des consommables est **une extension V3.5**, pas une fonction héritée déjà implémentée. | Une surface théorique ne donne ni prix d'achat, ni consommation d'encre, ni perte réelle d'un matériau. Ne pas inventer de tarifs, ni vendre un coût de fabrication comme calcul certifié. | **P2 RACCORDER** : prix saisis par l'utilisateur, unités, surface occupée/perdue, reste et incertitude ; estimation lisible, sans métrique inventée. |
| **C16 — Fabrique : cartes, boîtes, enveloppes, pochoirs** | **S-037 P1/G6.4** trois gabarits métiers, **S-088 P1/G6.7** étiquette/carte/topper sauvegardés et repris ; **V34-126/127/128** lot 16. Dioramas **S-044/S-066/S-099** G9 restent hérités. | Les producteurs réellement examinés de carte pliée et boîte ouverte ne démontrent pas enveloppes, toppers, pochoirs ni diorama quatre plans. Ne pas appeler les types supplémentaires « déjà présents ». | **P1 RACCORDER** les deux patrons existants, compléter trois gabarits historiques, puis étendre les modèles sans deuxième fabrique. |
| **C17 — Géométrie mm, languettes, plis, épaisseur** | **S-012 P0** chemins SVG utilisables avec matériau choisi, découpes testées ; **S-056 P0** trous/îlots/offset + coupon ; lot 16 V34-127 et lot 14 V34-109 | Une géométrie 2D statiquement valide ne prouve pas pliage, épaisseur correcte ou compatibilité de matériau. SCORE et CUT doivent être distincts après transfert Design Space. | **P1 GARDER** prévol déterministe en mm, erreurs localisées, profil matière/épaisseur inconnu explicite, vérification externe avant PASS physique. |
| **C18 — Preview 2D / simulation pliage 3D** | Lot 16 prévoit des aperçus et un prévol statique ; aucun critère hérité ne permet de substituer simulation à **coupon fabriqué** S-012/S-056. | Un volume 3D animé peut tromper si languettes, épaisseur, outil ou tolérances sont UNKNOWN ; ne pas inventer un moteur physique fiable. | **P1 preview 2D**, **P2 étude 3D** conditionnelle, simulation étiquetée NON_VALIDATION_PHYSIQUE, jamais un prérequis de sortie du logiciel. |

## 2. Contrats de raccordement sans nouvel état d'autorité

**V34-126**, lot 16, L289 : génération géométrique déterministe carte/boîte, tests T-V34-16-01..04, contours/fentes/plis mm et IDs stables ; pas de store additionnel. **V34-127**, L290 : prévol en réutilisant le lot 14, tests 16-02/03/06/09/10 ; profil inconnu non promu. **V34-128**, L291 : parcours Fabrique, reprise/Score/Attacher, tests 16-04/05/07/08/09 ; brouillon avant publication.

**V34-134**, lot 19, L97 : placement sans collision sur profil qualifié, verrous stables, comparatif, tests 19-01/02/04/05/06/07 ; dépend des exporteurs existants sans créer nouveau moteur de rendu. **V34-135**, L98 : orchestration bornée 12/24/50, tests 19-03/08/09/10/11/12, jobs/reprise sans doublon, aucun V1 contenant plus de sujets que sa limite. **V34-136/137/138**, lot 20, L89–91 : catalogue reconstructible, clones CAS et CSV par ligne. Smart Cost ne crée pas un second catalogue de prix imposé.

**Contrats PROPOSÉS** : LayoutPlan {project_revision, source_subject_ids, instance_ids, page_id, paths_mm, margins, allowed_rotation, locks}; CostEstimate {unit_prices_user, measured_area, waste_area, print_consumables_optional, unknowns, currency}; TemplateDraft {profile_id, dimensions_mm, thickness_optional, operations CUT/SCORE, geometry, warnings}. Ce sont des projections de conception : **pas** de persistance V1 implicite, pas de règle matérielle certifiée sans profil/version/test.

## 3. Flux novice et expert ; micro-recettes (NOT_RUN)

**Novice** : choisir carte, boîte ou étiquette réellement prise en charge → saisir largeur/hauteur et matériau connu ou UNKNOWN → aperçu 2D → prévol ciblé → choisir export manuel → guide Score/Attacher. Pour planches, choisir quantité, voir remplissage et avertissements, confirmer ; Smart Cost calcule uniquement si les tarifs sont entrés.

**Expert** : verrouiller les placements, replanifier les autres, inspecter les coordonnées, marges, dimensions et id d'instances, comparer les variants et surfaces consommées ; choisir le scénario de reprise sans réécrire les sorties existantes.

**Négatifs/recettes** :
1. Source polygonale avec trou et marge insuffisante → aucun chevauchement autorisé, sinon BLOCKED.
2. Placement verrouillé déplacé par la réoptimisation → FAIL ; conserver état précédent sans mutation.
3. Lot 50 instances interrompu au milieu → reprise uniquement des pages manquantes, IDs uniques, aucun pack V1 invalide.
4. Smart Cost sans prix matière ou avec unités incohérentes → coût UNKNOWN, pas 0 € inventé ; correction de tarif recalcule la projection sans altérer géométrie.
5. Enveloppe/topper/diorama demandé sans port qualifié → afficher NON DISPONIBLE ou BROUILLON, jamais produire un SVG de boîte réétiqueté.
6. Plis SCORE confondus avec CUT et épaisseur non renseignée → prévol refusé/averti selon cas, pas de profil machine PASS fictif.
7. Simulation 3D plausible avec volume réel non validé → mention NON CERTIFIÉ ; coupon physique distinct.
8. Disque plein, collision de destination, annulation et SHA concurrent → aucun export partiel, sauvegarde V1 intacte et reprise contrôlée.

**Validation par axe** : tests unitaires/fichiers synthétiques, écran Windows 1366×768/DPI 200 % clavier/focus, Design Space versionné, coupons Explore 5 et métriques physiques indépendants. Performance p50/p95/mémoire à mesurer, non inventée. IA locale facultative sous consentement et licences ; aucun réseau/poids ni fichier privé ajouté. 25 axes du contrat qualité et univers 24/141/140/80/437 conservés. Tests produit/Windows/GPU/Design Space/coupe physique **NOT_RUN par cette fiche**.

## 4. Bilan et prochaine étape

**C01–C18 ont désormais 18 décisions candidates examinées en trois fiches COV18B1/B2/B3**, avec responsabilités/héritage/DoD et risques documentés, mais **0/18 certifiées prêtes à coder ni intégrées** par cette opération. Smart Delivery, Smart Cut Advisor, Smart Weeding, Smart Cost et Fabrique restent intégralement au programme.

**Prochaine étape unique V35-COV-18C :** commencer la contre-expertise des **12 UX IA D01–D12**, source V3.3, consentement/VRAM/licences/GPU et ports réellement présents ; ensuite E01–E20 et les 33 opportunités, puis revue contradictoire finale et promotion V3.5 conditionnelle.
