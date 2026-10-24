# Contre-expertise Cricut V14

## Contraintes vérifiées
- Aucune image bitmap incorporée dans le SVG d'édition, uniquement `svg`, `g`, `path`.
- Couleurs unies sans dégradés ni filtres.
- Un groupe par sticker et un chemin d'offset blanc sous les couleurs.
- Transformations `translate` simples, sans masques de clipping.
- Dimensions `mm` + `viewBox` explicites.
- Comptage chemins sous le plafond Design Space de 5000.
- L'original et le SVG compact sont comparés en raster dans les tests locaux.
- Le moteur de découpe et le contour PNG restent ceux de V13.

## Risques qui persistent
- Toutes les zones de même couleur d'un sticker sont regroupées dans un seul chemin :
  impossible d'en sélectionner certaines séparément dans Design Space, sauf outil de
  découpe interne ou édition dans un logiciel vectoriel.
- Design Space peut réorganiser des groupes SVG ou interpréter certaines formes
  différemment ; les essais de rendu CairoSVG ne remplacent pas un import réel.
- Les nuances de l'illustration d'origine ne sont pas conservées dans le SVG aplati.
- Après déplacement d'un élément extérieur au contour blanc, la découpe peut changer.
- Les repères d'impression sont créés par Design Space, pas par SmartSVG.
- IA RMBG sur RTX 3070 : non exécutée physiquement ici.
- Reconstruction sémantique à la Canva Magic Layers : non implémentée.

## Références
- https://help.cricut.com/hc/fr/articles/360009556313-Comment-t%C3%A9l%C3%A9charger-des-images-dans-Design-Space
- https://help.cricut.com/hc/fr/articles/360009553213-T%C3%A9l%C3%A9chargements-d-images-%C3%A9l%C3%A9ments-non-pris-en-charge
- https://help.cricut.com/hc/fr/articles/360009387274-Comment-Imprimer-puis-d%C3%A9couper-dans-Design-Space
