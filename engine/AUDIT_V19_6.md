# Audit SmartSVG V19.6 — Contrat de validation

## Fonctionnement validé

- Trois tenseurs masques au maximum, chacun de la forme `(N,H,W)` avec `1<=N<=16`, en `float32` dans `[0,1]`.
- Interdiction des NaN/infinis, des masques trop volumineux, des sources incompatibles et des inversions implicites de canal/masques.
- Aucune altération du masque référence ni de l'image source en mode diagnostic.
- Sélection prudente seulement si **gain heuristique significatif** ET **similarité IoU suffisante** : ne pas interpréter comme garantie de meilleur détourage.
- Test bout-en-bout du nœud V19.6 (avec masque externe synthétique) jusqu'au PNG `*_CRICUT_TEST.png`.
- Workflow Express / Expert vérifié pour les champs exigés et les liens `MASK`.
- Diagnostic de la RTX en lecture seule ; aucun modèle importé/chargé lors de ce test.

## Ce qui n'a PAS été validé

- VRAM réelle, latence et qualité de SAM2/FeyNoBg/Finegrain sur une RTX 3070.
- Appels directs aux versions RMBG réellement présentes sur le PC utilisateur.
- Reconnaissance d'objet sémantique, segmentation correcte des cheveux, doigts, verres transparents et parties cachées.
- Import/affichage exact dans Design Space ou découpe physique sur Cricut.

## Limite conceptuelle

Le score est une **mesure heuristique de cohérence géométrique et de contraste**, pas une métrique supervisée type IoU contre vérité terrain. Pour connaître la précision réelle des modèles, il faut annoter manuellement quelques masques de référence sur les deux photos de l'utilisateur et calculer Dice/IoU contre ces annotations.

## Amélioration de l'évaluation

Entrée de référence annotée `masque_annote` : calcul IoU + Dice supervisés pour chaque variante lorsque le nombre, l'ordre et les dimensions des masques correspondent. Deux tests supplémentaires valident cette métrique et rejettent une annotation mal alignée. **Elle n'est pas générée par l'IA : l'utilisateur doit la vérifier.**
