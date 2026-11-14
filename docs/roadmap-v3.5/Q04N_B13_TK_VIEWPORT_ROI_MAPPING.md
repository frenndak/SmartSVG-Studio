# V35-Q04N — B13 OCR : transformation viewport Tk vers pixels PNG (candidate, 2026-11-14)

## Sources et autorité
- main HEAD confirmé par API branche : `aa0ff9e7d0c53dba3fdc429c02c6198736cfe935` (état observé le 14/11/2026, identique au snapshot initial ; ne pas inférer activité de PR).
- `engine/native_image_viewport_v34.py` blob `5f2a8bb1c85cf501d8bfd521a862c0e8e1ad0110`; `engine/native_atelier_tk_v34.py` blob `921f09fbd54b68a19b3ba9688f00a0334bafe6b3`; `engine/standalone_desktop_v34.py` blob `abdfe2f16be1b72375513f2a07769920d92e5dd7`; `tests/test_v34_native_image_viewport.py` blob `3707437f6c422cbb29bb33a6a64d33ef10302346`.
- Héritage : B13 OCR, G9/S-021/S-047, lot 12 et UX atelier, Q04L/Q04M. Aucun nouveau ticket V34 ni preuve OCR. Décision **AMÉLIORER** le port viewport existant, sans créer un second store d'image ou altérer le projet V1.

## État réellement constaté
`NativeImageViewport` est **read-only**. `load(image)` réinitialise `fit_scale` et auto-fit ; `fit_factor` calcule un facteur entier de subsample Tk ; `actual_size` affiche l'original, `zoom_in/out` modifient le facteur ; `_show` positionne l'image à (0,0) dans un Canvas scrollable, restaure approximativement le centre relatif après changement d'échelle, et `scan_dragto` déplace le viewport. Le consommateur atelier lui passe un `PhotoImage` décodé depuis `preview.png`; le shell lui passe un preview natif. **Aucun port public d'inversion écran→pixels PNG ni événement ROI n'est exposé dans ces fichiers.** Les tests existants contrôlent zoom/pan/reset/focus, **pas l'inverse ni la précision des rectangles ROI**. Le rendu par `PhotoImage.subsample(k)` est un échantillonnage, non un rééchantillonnage continu : les pixels omis ne sont pas récupérables par lecture de la miniature.

## Contrat candidat Q04N/1 — sans modification du modèle .smartsvg
Le consommateur OCR fournit obligatoirement `project_sha256`, `source_id`, `source_sha256`, `preview_sha256`, dimensions PNG originales, `preview_generation`, `viewport_revision` et rectangle canonique `[x0,y0,x1,y1)` en `VERIFIED_PNG_PX`. Le viewport reste une **projection éphémère** ; ni source de vérité de masque ni objet texte persistant.

Pour un événement souris local au Canvas `(ex,ey)`, utiliser les conversions Tk `canvas.canvasx(ex)` / `canvas.canvasy(ey)`, qui incluent le défilement. Soustraire l'origine de l'item image obtenue par `canvas.coords(image_item)` (actuellement (0,0), mais ne pas la coder en dur). Pour `k=fit_scale or 1`, proposer la correspondance de cellules `x_png=floor((canvasx-ex_origin)*k)`, `y_png=floor((canvasy-ey_origin)*k)`, avec borne supérieure exclusive pour le rectangle de sélection : `x0=floor(min(u0,u1)*k)`, `x1=ceil(max(u0,u1)*k)` et idem y, puis clamp aux dimensions PNG. **Ne pas utiliser cette formule avant tests Tk réels** : `subsample`, dimension tronquée, coordonnées fractionnaires, bord droit, scroll et événement hors image exigent une validation explicite. Si ROI vide, hors image, image changée, révision zoom/pan différente, SHA/source stale ou mapping non certifié : refuser l'OCR sur ROI et proposer transcription manuelle ou OCR de l'image entière avec consentement distinct.

La capture doit figer l'identité et `viewport_revision` au press ; toute transformation pan/zoom, remplacement image, resize auto-fit ou fermeture entre press et release invalide la sélection. Ne pas réutiliser le drag bouton gauche actuel : il pilote `scan_mark/scan_dragto`. Prévoir un mode sélection ROI explicite et réversible, accessible au clavier (navigation/ajustement numérique des coordonnées), sans détourner le mode pan. Le rectangle visible est un overlay **éphémère**, jamais un masque float32 ni un tracé CUT. Ne pas lancer de worker OCR depuis un callback Tk ; transmettre une requête immuable au job OCR distinct avec garde latest-only composite décrite dans Q04M.

## UX et accessibilité
Novice : choisir une source PNG vérifiée → activer « Zone de texte » → dessiner une zone (ou saisir x/y/largeur/hauteur) → voir dimensions en pixels source → corriger/annuler → consentir à l'OCR local ou transcrire manuellement → relire chaque segment avant export externe. Expert : afficher SHA, facteur k, viewport revision et provenance. Feedback immédiat sans popup sur chaque geste ; consentement uniquement au traitement externe/coûteux. États `EMPTY/READY/SELECTING/ROI_REVIEW/STALE/RUNNING/PROPOSED/REVIEWED`; Escape annule l'overlay, Undo restaure uniquement la dernière sélection/correction locale. Vérifier Windows 1366×768 et DPI 200 %, clavier, focus, contraste, mouvement réduit, petits écrans.

## Tests candidats — NOT_RUN
1. P01 image 960×470, Canvas 480×235, k=2, pan zéro : événement (10,20) → pixel source (20,40).
2. P02 image 1920×940, k=1, xview/yview non nuls : `canvasx/canvasy` préservent la position source lors du pan.
3. P03 k=3, ROI avec coordonnées non multiples de trois : arrondi inférieur/supérieur couvre toutes les cellules sélectionnées ; comparer avec `PhotoImage.subsample` réel.
4. P04 zoom et resize auto-fit sans ROI active : image et source inchangées, génération viewport incrémentée.
5. N01 press ROI puis pan/zoom avant release → STALE, aucune proposition publiée.
6. N02 release hors image, rectangle nul/inversé, coordonnées négatives ou débordement → rejet ou clamp contrôlé ; jamais lecture hors bornes.
7. N03 source_id identique mais PNG SHA changé → rejet CAS au commit/export.
8. N04 fermeture Tk avec worker OCR actif → aucun callback UI tardif.
9. N05 OCR génération ancienne après nouvelle sélection → aucune superposition de texte.
10. N06 image sous-échantillonnée k>1 avec dernière colonne/ligne tronquée → borne exclusive correcte ou ROI désactivée.
11. N07 tentative d'utiliser drag gauche pour pan et ROI simultanément → mode explicite exclusif.
12. N08 absence de modèle/licence/consentement ou OOM GPU → manuel, sans téléchargement ni écriture V1.
13. N09 collision d'export, disque plein, crash staging → no-clobber, projet byte-identique.
14. N10 changement DPI pendant capture, focus perdu ou Canvas détruit → annulation sûre.

Tests Windows réels, GPU, Design Space, coupe physique : **NOT_RUN** ; Design Space et coupe **N/A pour transcription isolée**, redeviennent requis pour un flux fabrication. Les quatre sorties PNG Print Then Cut, SVG Basic Cut, SVG CUT multicouche, SVG d'édition demeurent distinctes et inchangées.

## Micro-lots TDD et DoD
T1 tests mathématiques sur Canvas simulé ; T2 tests Tk réels du mapping, pan/zoom/subsample, bords et DPI ; T3 API lecture seule `viewport_to_source_roi` sans second store ; T4 mode ROI exclusif, clavier, Escape/Undo ; T5 identité SHA/génération et concurrence ; T6 fournisseur OCR facultatif + fallback manuel ; T7 export externe atomique. **Aucun de ces lots n'est implémenté par cette fiche.** DoD : tests positifs/négatifs PASS non-skip au SHA code, preuve Windows, contrôle sécurité, revue hostile et aucune mutation de format V1.

## Contre-expertise adverse
Alternative « multiplier simplement x/y par k » rejetée : ignore scroll, origin item, fractionnements, changements de viewport et stale. Alternative OCR directement sur miniature rejetée : perte de résolution et provenance. Alternative « OCR toute l'image seulement » **acceptable en fallback** avec consentement, si la ROI ne peut être certifiée. Ne pas migrer Tk vers Qt/Tauri pour ce seul besoin sans benchmark.

## Contrôle R3 — 25 axes
01 héritage lots conservé ; 02 S-021/S-047/G9 et G6.3 ouverts ; 03 tickets V34 inchangés ; 04 B13 non certifié ; 05 437 scénarios planifiés non exécutés ; 06 HEAD main et blobs vérifiés ; 07 V1/CAS/float32 préservés ; 08 quatre exports séparés ; 09 machine N/A à OCR isolé ; 10 novice/expert ; 11 Undo et ROI éphémère ; 12 DPI/focus/clavier ; 13 crash/stale/concurrence ; 14 IA facultative et manuel ; 15 PNG dimensions/repères ; 16 topologie CUT N/A à OCR isolé ; 17 batch/CSV N/A à ROI isolée ; 18 Smart Delivery N/A à transcription seule ; 19 #141 non modifiée ; 20 cibles latence/mémoire à mesurer, pas de valeur inventée ; 21 licence/consentement/confidentialité ; 22 documentation sur branche candidate ; 23 réemploi du viewport existant ; 24 aucune promotion/AGENTS ; 25 non-régression de mission R3. **Audit de fiche, pas certification globale.**

Couverture historique non recalculée : 24/141/140/80/437 inventoriés, 431/437 liens explicites, 6 exceptions, 10 exigences G6/G9 sans ticket direct, 0/80 UX certifiées. Prochaine action UNIQUE Q04O : vérifier le comportement réel Tk de `canvasx/canvasy` et des bords subsample avec un protocole de test Windows reproductible, puis spécifier les oracles de mapping avant tout port OCR.
