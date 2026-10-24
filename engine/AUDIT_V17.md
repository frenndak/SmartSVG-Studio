# Contre-expertise V17 — Résultats vérifiés

- **30 tests Python : réussis.** Les tests couvrent les cas historiques, une seule image, deux sujets transparents, la détection des détails fins, le mapping numéro/composante et un crash simulé sans publication de dossier final.
- **Planche utilisateur 1536 × 1024 : traitée intégralement.** 12 composantes, 12 stickers individuels, aperçu numéroté corrigé, une seule planche d'impression de 180 × 120 mm.
- **Écart entre stickers : minimum estimé de 2,46 mm**, calculé sur les masques raster. La tolérance pixel interdit d'y lire une mesure micrométrique de découpe.
- **Densité source effective : environ 216,75 DPI** au format 180 mm. Un avertissement est émis car inférieur à 250 DPI ; aucun upscaling artificiel présenté comme gain de détail.
- **IA : mode désactivé pour le test de la vraie planche.** Les tests de raccordement à RMBG restent simulés ; aucune validation CUDA réelle.
- **Limites :** l'app Cricut peut modifier le placement/échelle et les résultats de découpe dépendent du papier, de l'imprimante, du capteur, de la calibration, et de la lame.

**Défauts découverts pendant la validation :** ordre des 3e/4e et 11e/12e composantes raster inversé par rapport à l'ordre des stickers exportés ; correction par le mapping du moteur V16. L'aperçu posait initialement ses étiquettes sur la rangée suivante ; correction du positionnement. Les deux défauts sont couverts par des tests ou une vérification visuelle après correction.
