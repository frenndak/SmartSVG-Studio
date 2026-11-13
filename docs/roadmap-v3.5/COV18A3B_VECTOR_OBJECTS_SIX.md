# V35-COV-18A-3b — Revue UX A11/A13/A14/A15/A16/B01

**13 novembre 2026 — CANDIDAT, NON NORMATIF.** Cette fiche reprend les six fonctions A11, A13, A14, A15, A16 et B01 et poursuit [COV-18A-3a](COV18A3A_UX_NEXT_SIX.md). Au total, 12 des 24 autres fonctions A/B ont désormais fait l'objet de cette nouvelle revue contradictoire après la tranche COV-18A-2b–d. Cela ne les certifie pas. Source : héritage V3.3, traçabilité V3.4 lot 23, lots 05/13/14/18, audit initial UX #134 et ports historiques examinés à main aa0ff9e7d0c53dba3fdc429c02c6198736cfe935.

## 1. Six frontières fonctionnelles et arbitrages

| Fonction | Exigences héritées et critère complet pertinent | Erreur ou raccourci à refuser | Décision candidate |
|---|---|---|---|
| **A11 — Couleurs et couches de production** | S-011 P0 fidélité SVG multicouche, rendu mesuré ; S-032 P0 édition ≠ fabrication ; S-045 P2 vinyle multicouleur exige superposition testée physiquement | Un groupe de couleurs artistique ne constitue pas un plan CUT multicouche ni un test vinyle | RACCORDER / P1, profils et essais séparés |
| **A13 — Plume, nœuds, Bézier** | S-034 P1 simplification de Bézier, fidélité non dégradée ; S-035 P1 composition éditable après réouverture | Réduire des nœuds n'implémente pas une plume interactive ; afficher des chemins n'autorise pas leur persistance V1 | RAFFINER / P1, brouillon réversible puis ADR avant persistance |
| **A14 — Géométrie booléenne** | S-056 P0 QA géométrie CUT en mm (trous/îlots/segments/offset), simulation annoncée et coupon physique ; S-030 P0 Basic Cut | Prévol/diagnostic ne crée pas un outil union/différence/intersection | RACCORDER / P0 au niveau prévol, édition booléenne distincte |
| **A15 — Simplification des chemins** | S-033 P1 préservation petites régions avec IoU/MAE ; S-034 P1 simplification de Bézier à fidélité non dégradée | Un score moyen élevé n'excuse pas la disparition d'un trou | RAFFINER / P1, variantes mesurées et rollback |
| **A16 — Variantes et intelligence vectorielle** | S-060 P1 trois scores silhouette/couleur/géométrie, benchmark reproductible sur échantillon fixé ; S-056 P0 garde-fous de coupe physique | Les scores explicables ne sont ni une IA générative ni une certification Cricut | METRIQUES P1, automatisation IA P2 conditionnelle |
| **B01 — Objets graphiques** | S-052 P0 identité Source/Subject/Artifact et rotations/crop/alpha ; S-035 P1 composition objets/textes éditable après réouverture | Un Subject V1 ou un groupe SVG ne constitue pas un modèle d'objets universel persistant | BLOQUER persistance de nouveaux types avant ADR schéma/migration |

## 2. Raccordement des DoD existants

- **V34-099 (lot 13, L221)** : couches éditables/palette et tests T-V34-13-11..13/18 ; garantir des objets réellement modifiables, sinon repli silhouette. C'est une base A11/A13, pas une preuve des outils de nœuds.
- **V34-100 (lot 13, L222)** : codec SVG sûr, tests T-V34-13-14..19 ; refuser contenus actifs et dimensions non physiques.
- **V34-101 (lot 13, L223)** : Basic/MultiCut, tests T-V34-13-14..18/20/26/27 ; quatre sorties distinctes et validation Design Space ultérieure.
- **V34-108 (lot 14, L256)** : duplication et croisement de contours, T-V34-14-02/08/09/11/24 ; aucune preuve d'édition booléenne complète.
- **V34-109 (lot 14, L257)** : prévol déterministe, T-V34-14-03..11/18/19/24/30 ; PASS/WARN/BLOCKED ne prouvent jamais fabrication physique.
- **V34-112 (lot 14, L260)** : Pen/Draw + Cut, T-V34-14-04/16/29 ; DRAW distinct de CUT, sans prouver S-045 vinyle multicouleur.
- **V34-025/028 (lot 05, L210/L213)** : intégrité source, identité des masques et packs ; B01 doit conserver ces contrats.
- **V34-133 (lot 18, L112)** : propriétés et calques dérivés du projet unique, tests T-V34-18-07..09 ; panneau lecture/aperçu et clavier, pas de second stockage.

Ports consultés dans les audits précédents : engine/smartsvg_vector/layers_v2113.py::vectorize_flat_art renvoie XML SVG couleur, pas coupe multicouche certifiée ; engine/smartsvg_core/project_contracts.py::Artifact accepte en V1 uniquement print_then_cut_png, basic_cut_svg et editable_svg ; engine/smartsvg_core/editor_session_g23.py::parse_editor_document accepte exactement version,width,height,count,source,strokes. Tout champ supplémentaire objects, layers ou text doit être rejeté par le contrat V1 actuel.

## 3. Architecture et parcours candidats

**Contrat à concevoir (PAS un port existant) :** un VectorDraft avec SHA de révision attendue, identités de sujet, unités mm, paths et annotations ; modifier nœud, tangente, union, différence et simplification uniquement en brouillon sans mutation. À l'acceptation, utiliser writer/CAS existant seulement pour les types qu'il sait persister ; sinon refuser avec message d'action et conserver le brouillon ou exporter selon profil vérifié. Toute extension de schéma nécessite ADR approuvée, reader/writer, migration et rollback.

**Novice :** choisir Plume ou Simplifier, visualiser le contour et le diff, corriger avec Undo, contrôler les avertissements ; ne confirmer qu'une écriture ou livraison externe. **Expert :** inspecter nœuds, path/winding, calques, mm, trous, IoU/MAE et trois variantes avec delta de coût ou difficulté, si ces métriques sont disponibles. Les valeurs manquantes restent UNKNOWN.

## 4. Tests et échecs adversariaux — NOT_RUN

1. Source synthétique trois couleurs, trous/îlots : rendu éditable fidèle puis quatre profils distincts ; un groupe coloré ne devient pas automatiquement couche CUT.
2. Bézier avec microforme, simplification : comparaison IoU/MAE, topologie inchangée ; si un trou disparaît, FAIL et ancien digest préservé.
3. Union/différence de polygones en brouillon : identité/revision/units mm préservées ; objets NaN, chemins ouverts et winding incompatible doivent être refusés.
4. Trois scores de qualité séparés sur corpus fixé ; une variante haut classée mais topologie fautive est rejetée. Aucun pourcentage de qualité non mesuré.
5. Text/Layer/Object injecté dans éditeur V1 : INVALID_EDITOR_SCHEMA ; Undo d'un brouillon ne modifie pas le fichier source. CAS périmé, annulation, disque plein et crash → aucun état partiellement publié.
6. Coupon vinyle multicouche réel : alignement, profil matière et preuve de coupe distincts des tests géométriques. Design Space et physique ne sont jamais PASS par un test de structure SVG.

**UX et sécurité :** clavier/focus, 1366×768, DPI 200 %, contrastes et mouvement réduit à mesurer sur Windows. IA opt-in/CPU repli, licence/consentement, aucune image privée ni poids publiés ; SHA exact et statuts NOT_RUN conservés. Les 25 axes du contrat d'exhaustivité, 24 lots/141 exigences/140 tickets/80 IDs/437 scénarios restent applicables ; pas de nouveau writer ni de ticket créé artificiellement.

## 5. État et prochaine étape

**Acquis documentaire :** six arbitrages supplémentaires et propriétaires de DoD plausibles, chaque source et limite conservée. **Non acquis :** conformité exhaustive à chaque critère et exécution de tests, adoption normative, certification Windows/Design Space/coupe physique. Rien de ces fichiers ne change le code produit.

**Prochaine action COV-18A-3c :** examiner B02–B08 et B10–B14 individuellement en deux groupes de six, priorité aux calques, texte, OCR et modèles d'objets, confronter les sources V3.3/V3.4 et l'architecture V1. Ensuite passer aux domaines C/D/E, aux 33 opportunités, au backlog et à la promotion contrôlée.
