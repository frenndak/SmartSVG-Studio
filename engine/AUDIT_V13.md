# Audit V13 — distinction tests et risques réels

## Défaut observé dans la V12

Le PNG imprimable et le SVG des contours partageaient un masque cohérent. En revanche, les fonds blancs des SVG vectoriels éditables étaient reconstruits depuis le dessin avant ajout de la marge physique et correction géométrique. Lors d'une édition vectorielle puis d'un aplatissement dans Design Space, la nouvelle découpe pouvait donc différer du PNG préparé initialement.

## Correction livrée

La V13 utilise le contour validé `CUT_XX` du SVG de découpe pour créer `STICKER_XX_BASE_DECOUPE` dans chaque groupe du SVG éditable, et compense mathématiquement les translations de groupes. Les SVG couleurs possèdent de vrais `<path>`, pas des images embarquées.

## Tests exécutés ici

- Une image seule : 1 contour, manifeste SHA-256 vérifié et base vectorielle présente.
- Planche RGBA irrégulière : 3 contours, un seul fichier PNG pour impression.
- Planche de référence : **12 contours distincts**, 12 bases blanches, **0,1138 %** d'écart entre contour SVG et silhouette PNG au niveau raster.
- Altération volontaire du chemin SVG (déplacement) : export géométriquement refusé.
- Insertion de transparence partielle sur le PNG après production : incohérence détectée.
- Crash simulé au moment de créer les nouvelles bases : aucune sortie Cricut publiée.
- Vérification des hash SHA-256 y compris des détails rangés dans `DETAILS_ELEMENTS`.

## Limites à conserver dans le statut « bêta »

1. Une erreur inférieure à 1 % est tolérée pour les pixels de frontière ; elle ne prouve rien sur la précision mécanique.
2. L'image vectorielle simplifiée peut être visuellement moins fidèle ; les groupes ne sont **pas** des objets sémantiques.
3. La vraie inférence RMBG sur ta version Windows / CUDA / GPU n'a pas été mesurée ici.
4. Il faut encore vérifier une impression A4 + Print Then Cut complète dans Design Space, notamment la calibration et les repères.
5. Les images très complexes, les objets qui se touchent et les petits morceaux détachés peuvent être bloqués.
6. Le PNG d'origine à 1536 × 1024 pixels ne donne pas une impression native à 300 DPI sur 180 mm : source environ 217 DPI.
7. Tous les paramètres de version, tailles et impressions sont indicatifs tant que l'application Cricut n'a pas validé la mise en page.
