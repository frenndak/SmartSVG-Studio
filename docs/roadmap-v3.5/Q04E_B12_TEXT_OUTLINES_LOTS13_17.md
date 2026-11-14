# V35-Q04E — B12 texte→chemins : lot 13, lot 17, contrats d'export (CANDIDAT)
**14 novembre 2026.** Conception uniquement ; V3.4 ACTIVE. Sources lues sur main : `13_VECTORISATION_SVG.md` blob `f694c0016e896917084f1d70a642f67316d1cf70`, `17_EXPORTS_DESIGNSPACE.md` (texte relu), Q04A–D et INHERITANCE_REGISTER sur branche candidate. Aucun port actuel de conversion de fontes en chemins n'a été confirmé : **API NON_VÉRIFIÉE, ne pas inventer d'implémentation**.

## Décision et héritage
**B12 — conversion texte en chemins**, AMÉLIORER P1, sans remplacer B09 (texte modifiable), B13 (OCR), ni G6.3. Sources intégrales à maintenir : S-036 (polices et conversion), S-064 (typographie), R33-028 (licences/glyphes), gates G6/G9 ; ces exigences n'ont toujours pas de ticket V34 direct. Raccordements **candidats**, non liens historiques : V34-096 géométrie et repères, 097 trous, 098 simplification, 099 couches, 100 sérialisation SVG sûre, 101 profils Basic/MultiCut, 102 Undo, 103 QA, 104 quotas, 105 UI, 129 quatre exports, 130 transfert, 131 provenance. Aucun ticket supplémentaire B12 n'est déclaré source V3.4.

Matrice de recettes exactes :
- `T-V34-13-04/05/06/07/09/10` : trous/îlots, winding, courbes, auto-intersections, simplification non destructrice ; **réutilisation conditionnelle** pour contours de glyphes.
- `T-V34-13-13/14/15/16/18/19` : édition vs Basic Cut, unités mm/viewBox, budget, texte SVG non converti, XML hostile ; réutilisation conditionnelle.
- `T-V34-13-22/23/25/29` : stale, idempotence, focus/Undo, crash/disque ; réutilisation conditionnelle.
- `T-V34-17-01/03/04/05` : quatre rôles distincts, prévol Basic Cut, groupes multicouches, styles éditables.
- `T-V34-17-07/08/10/11/13` : SHA, publication partielle, UI clavier, import réel DS et coupe physique.
Ces tests sont **recettes historiques**, non preuves exécutées pour B12. La conversion fonte→contours requiert de nouveaux cas B12, sans modifier les identifiants historiques.

## Contrat candidat, sans écriture V1
Entrée éphémère `TextOutlineProposal/1` : `project_sha256` (hex64), `draft_id`, `text_nfc` (Unicode), `font_source_sha256`, `font_license_status=VERIFIED|UNKNOWN|RESTRICTED`, `font_face_index`, `glyph_map`, `size_mm` (>0), `baseline_transform` affine finie, `role` explicite, `output_path` externe ; `glyph_map` lie clusters de graphèmes, glyph IDs et substitutions documentées. Le contrat est **proposé**, pas une API existante. Pas d'incorporation de police, téléchargement ou OCR implicite. L'absence de licence vérifiée ou de glyphes bloque publication du rôle exigeant fidélité ; l'utilisateur peut corriger le texte ou choisir une police autorisée.

Sortie éphémère : `OutlineCandidate` contenant `source_revision`, `geometry_digest`, contours OUTER/HOLE et parentés, transformations résolues en mm, métriques de dérive, liste de substitutions, provenance, `warnings`, `proof_axes`. Conversion par moteur déterministe CPU choisi **après benchmark** ; aucune garantie GPU, RTX 8 Go ou IA nécessaire. Aucune écriture `TextNode` dans `smartsvg-project/1` ; source de vérité = projet V1 + brouillon non persistant. **B12 réussi à l'export ≠ B09/G6.3 persistant**. Une future persistance demande ADR V2, approbation propriétaire, migration et rollback.

États : `EMPTY→DRAFT→GLYPHS_RESOLVED→OUTLINE_PREVIEW→REVIEWED→STAGED→PUBLISHED_UNVERIFIED` ; sorties `LICENSE_BLOCKED|GLYPH_MISSING|GEOMETRY_BLOCKED|STALE|CANCELLED|ERROR`. Recalculer le SHA avant staging et publication ; un aperçu stale ne peut pas être commité. Undo/Redo n'affecte que le brouillon et ses paramètres ; un export publié reste un fichier externe. L'original demeure inchangé après annulation, échec, crash ou conflit de writers.

## Quatre rôles, jamais interchangeables
1. **PNG Print Then Cut** : raster RGBA avec texte rendu, dimensions/PPI/alpha contrôlés ; **aucun SVG de contours joint comme seconde coupe**.
2. **SVG Basic Cut** : glyphes convertis en chemins fermés, trous préservés, sans texte vivant, clips, scripts, gradients, images ni opérations implicites ; dimensions mm et budget contrôlés.
3. **SVG CUT multicouche** : groupes de contours distincts avec repères/ordre et manifeste externe ; **ne pas enregistrer comme `Artifact.use=editable_svg`** (V1 ne possède pas ce quatrième rôle interne).
4. **SVG d'édition** : styles et calques autorisés ; un texte converti en chemins reste éditable **géométriquement**, pas éditable en tant que texte. Option de texte vivant non garantie pour Design Space, donc contrat explicite.
`CUT/SCORE/DRAW/PRINT/FOIL` sont des intentions de fabrication, pas des types de fichier ni des propriétés déduites de couleur. Import DS et découpe Explore 5 requièrent essais séparés.

## UX novice et expert
Novice : saisir → choisir police autorisée → voir aperçu et dimensions → bouton « Convertir en contours (copie) » → avant/après, avertissement « lettres non modifiables après conversion » → choisir rôle de sortie → confirmer écriture externe. Retour par Undo sur brouillon ; pas de popup pour déplacements locaux. Expert : inspecter glyph IDs, substitutions, kerning, trous, nombre de chemins, winding, précision mm, source SHA et avertissements. Barre contextuelle et canevas uniques ; poignées accessibles clavier ; états vide/attente/erreur lisibles à 1366×768, DPI 200 %, contraste et mouvement réduit. Aucun état UI n'est certifié avant test Windows.

## Recettes nouvelles proposées — toutes NOT_RUN
Positifs : accents français, ligatures, caractères combinants et paires de substitution avec fonte libre ; comparaison avant/après raster et dimensions mm ; deux glyphes troués conservant les îlots ; quatre rôles vérifiés indépendamment ; réouverture du V1 original inchangé.
Négatifs : N1 police absente ou glyphe manquant → blocage sans substitution muette ; N2 licence inconnue/restrictive → refus de redistribution ; N3 taille NaN, zéro ou transformation non inversible → rejet ; N4 trou disparu après simplification → ancien digest intact ; N5 texte/DTD/script ou ressource distante injectés → aucun XML actif/réseau ; N6 source SHA changé pendant conversion → STALE ; N7 collision de destination/symlink/reparse → no-clobber ; N8 disque plein au staging → aucun faux manifeste ; N9 crash avant publication → V1 et export précédent intacts ; N10 double requête ou ACK perdu → pas de doublon ; N11 OCR B13 incertain → pas de conversion automatique ; N12 couleur/ombre B11 → pas d'opération CUT/SCORE inférée.
Mesurer p50/p95 conversion par nombre de glyphes, mémoire pic, dérive géométrique, nombre de segments et temps d'aperçu sur fixtures synthétiques ; seuils à définir **après** mesures. Matrice auto/Windows/Design Space/physique distincte, tout NOT_RUN.

## Micro-lots TDD et rollback
A fixture de police libre et inventaire licences ; B shaping/Unicode et erreurs ; C contours/holes et métriques ; D projection quatre rôles via exporteurs réels à localiser ; E staging externe SHA/no-clobber et fault injection ; F UI Windows clavier/DPI ; G DS versionné et coupon physique. DoD : pas de fonte manquante muette, pas de trou perdu, aucune mutation V1, export typé, revue hostile, SHA de test et preuve par axe. Rollback : désactiver B12, garder texte brouillon et exports V3.4. Alternative moins coûteuse : SVG texte vivant export-only, **rejetée comme substitut de B12 Basic Cut** car import non garanti ; alternative raster PNG seulement, utile PTC mais insuffisante pour B12.

## Audit 25 axes
01–05 inventaires 24/141/140/80/437 préservés, couverture sémantique ouverte ; 06 statuts disjoints, main HEAD non certifié ici ; 07 V1/CAS/float32 inchangés ; 08 quatre exports séparés ; 09 tri-state machine, aucune certification ; 10 parcours novice/expert ; 11 Undo local ; 12 Windows/accessibilité NOT_RUN ; 13 négatifs/crash/concurrence ; 14 CPU manuel, IA non requise ; 15 alpha/PPI pertinent PNG seulement ; 16 trous/mm/XML pertinents ; 17 batch/CSV hors micro-lot, héritage conservé ; 18 Smart Delivery hors micro-lot, export externe non ZIP ; 19 O-001..033 et #141 non modifiés ; 20 mesures futures ; 21 licences/Unicode/confidentialité ; 22 docs branche seulement ; 23 aucun second writer ; 24 promotion/CI/terrain non revendiqués ; 25 delta : frontières B12 vs B09/B13 et matrice 13/17 documentées. **0/80 UX certifiées**. 431/437 liens source historiques, six exceptions et dix exigences G6/G9 sans ticket direct restent ouverts.

**Prochaine action UNIQUE Q04F :** rapprocher B09–B14 aux clauses G6/G9 intégrales et décider le blocage de persistance G6.3 avec ADR V2 séparée, sans certifier un export-only.
