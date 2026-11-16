# V35-Q04Q — Test Tk réel retrouvé : portée des preuves ROI B13 (14/11/2026)

**Décision : AMÉLIORER Q04P ; aucune certification ROI/OCR.** V3.4 reste ACTIVE. Sources vérifiées directement : `tests/test_v34_native_image_viewport.py` sur main, blob `3707437f6c422cbb29bb33a6a64d33ef10302346` ; main HEAD `0692f804ad21bd775cd0269dd92dc6e2b1cea01f` ; branche candidate avant écriture `5eabc29f4ac1299d04ecfd5ae6374b7e1861f696`. Q04P avait cherché deux noms de fichiers inexistants ; **le fichier réel existe et comporte trois tests**. Aucun test exécuté dans cette revue.

## Constat exact : trois tests, trois niveaux de preuve

1. `test_fit_preserves_aspect_and_never_enlarges` : calcul `fit_factor` (960×470→480×235 = 2 ; 300×471→480×235 = 3 ; 8×12 = 1). Preuve arithmétique uniquement, non une ROI.
2. `test_incremental_zoom_keeps_manual_scale_across_resizes_and_clamps` : `FakeImage`/`FakeCanvas`, zoom, raccourcis appelés directement, redimensionnement, bornes 1..32 et état sans image. **Simulation**, pas événements Windows ni transformation source.
3. `test_native_pixels_pan_and_reset_on_image_replacement` : instancie un **vrai `tk.Tk()` si disponible**, sinon `skipTest`; charge `PhotoImage`, vérifie pixel (900,440), événements clavier `<Home>`/`<Key-0>`, drag souris, pan, conservation approximative du centre après zoom, remplacement et vidage. Ce test est plus fort que les simulations, mais son PASS n'est **pas démontré ici** ; un PASS sur CI non-Windows ne vaut pas preuve Windows. Aucun test ne calcule une ROI écran→source ou ne valide `canvasx/canvasy` et l'origine de l'item.

**Contre-expertise contraire :** réutiliser le troisième test comme socle est moins coûteux que créer un nouveau harnais Tk. Mais il ne fournit ni oracle de rectangle pixel exact, ni preuve DPI 200 %, ni identité SHA de source ; son seuil de centre `delta=0.08` est impropre à certifier une sélection de texte pixel-précise. Ne pas convertir « Tk réel si disponible » en `TEST_UI_WINDOWS_PASS` sans OS, résultat non-SKIP et artefact d'exécution.

## Contrat candidat B13, micro-lots TDD (sans code)

**Q04Q-T1 — Inventaire/qualification :** consigner pour chaque test `path@blob`, nom, environnement, `PASS/FAIL/SKIP/NOT_RUN`, CI run et SHA exact. DoD : aucun `skipTest` compté PASS. Tests négatifs : TclError/headless, test non collecté, exécution sur OS non Windows.

**Q04Q-T2 — ROI géométrique :** ajouter à l'avenir, sous revue producteur V3.4, un oracle synthétique avec PNG 1001×503, subsample 3, pan et zoom. Calculer `canvasx/canvasy`, soustraire l'origine réelle de l'image Canvas, convertir en pixels source avec convention demi-ouverte `[x0,x1)×[y0,y1)`, borner et enregistrer version de transformation. Ne jamais déduire les dimensions du PNG de la seule PhotoImage subsamplée. DoD : aller-retour bornes vérifié aux pixels, aucun rectangle vide accepté. Négatifs : clic hors image, pan après début de geste, remplacement image pendant geste.

**Q04Q-T3 — Session/Undo/concurrence :** source SHA et révision viewport obligatoires avant commit ; résultat OCR éphémère, refus stale et annulation sans mutation. DoD : un seul commit utilisateur réversible, aucun TextNode V1 ni migration implicite. Négatifs : deux workers concurrents, crash avant commit, source modifiée entre sélection et résultat.

**Q04Q-T4 — Windows humain :** exécuter sur Windows à 1366×768 et DPI 100/200 %, clavier/focus, pan, zoom, bord impair, puis enregistrer captures anonymisées, versions Python/Tk, SHA et résultats non-SKIP. `DESIGN_SPACE_PASS` et `COUPE_PHYSIQUE_PASS` restent N/A pour la sélection OCR isolée ; GPU N/A si fallback manuel/CPU, toute IA future requiert licence, modèle/hash, consentement et budget VRAM. Aucune assertion de performance avant mesure.

## UX et sécurité

Novice : sélectionner visuellement une zone de texte, voir rectangle/coordonnées et possibilité de corriger ou annuler ; expert : coordonnées numériques source et navigation clavier. Un seul canvas/session, feedback de stale sans popup systématique ; undo local. Ne pas modifier `.smartsvg` V1, source, Subject/masques float32, writer SHA/CAS, ni confondre sélection et masque. Sortie OCR éventuelle = proposition externe contrôlée ; les quatre exports PNG PTC / SVG Basic Cut / SVG CUT multicouche / SVG éditable restent distincts, inchangés et **non validés par cette fiche**. Aucun réseau ou téléchargement implicite. Objectifs de latence à mesurer sur fixtures, non résultats inventés.

## Audit des 25 axes R3

01–05 : héritage 24/141/140/80/437 inchangé, aucune renumérotation ; lien B13/G9/S-021/S-047 et Q04N/O/P, sémantique ouverte. 06 : main SHA vérifié, tests NOT_RUN. 07 : projet V1/CAS préservé. 08–09 : exports et opérations machine N/A au calcul ROI, invariants maintenus. 10–13 : geste novice/expert, canvas, accessibilité DPI, annulation/stale et Undo spécifiés. 14 : IA facultative et consentie, fallback manuel. 15 : dimensions PNG et subsample contrôlés. 16 : géométrie de ROI seulement, aucun chemin SVG modifié. 17–19 : fabrique, livraison et autres opportunités hors périmètre, aucune suppression ni nouveau ticket. 20 : protocoles, zéro mesure revendiquée. 21 : fixtures synthétiques, aucune donnée privée. 22 : branche docs uniquement, aucun code/AGENTS/merge/automatisation. 23 : réemploi du test réel plutôt que duplication. 24 : adoption et essais toujours bloqués par gates. 25 : correction factuelle de Q04P, pas simple répétition.

**Couverture historique déclarée, non recalculée :** 24 lots, 141 exigences, 140 tickets, 80 UX, 437 scénarios ; 431/437 liens explicites, six exceptions, dix exigences G6/G9 sans ticket direct ; 0/80 UX certifiées. **Validations de cette fiche :** lecture de source PASS ; exécution unitaire/UI Windows/GPU/Design Space/physique NOT_RUN (ou N/A par domaine). **Prochaine action UNIQUE Q04R :** lire le code `engine/native_image_viewport_v34.py` et comparer chaque binding et état à ce troisième test pour fixer l'oracle ROI écran→source avant toute prétention de PASS.
