# Audit V16 (tests logiciels)

## Invariants

- Un **PNG transparent principal** contenant N silhouettes indépendantes, avec les N polygones de contrôle correspondants.
- Un **SVG couleur compact** et un **SVG par régions** sur la planche principale, plus des SVG/PNG facultatifs isolés par sticker.
- Images individuelles issues de l'image d'impression finale, en conservant UNIQUEMENT les pixels dont l'alpha appartient à la composante du bon sticker.
- Les tailles `width/height` SVG restent mesurées en mm ; les DPI PNG sont encodés depuis la largeur physique et la résolution réelle.
- Publication unique après tous contrôles, manifeste SHA-256 récursif, avertissements explicites.

## Tests

Lancer `python verify_package.py`. Couverture : 1 image simple, 2 objets transparents, PNG individuels indépendants, chaîne IA RMBG simulée, signatures d'entrées des nœuds Express/Expert, tolérance géométrique SVG, nettoyage sur échec d'export, validité XML, dimension en mm, métadonnées DPI et manifeste.

## Attention : aucun équivalent complet à Magic Layers

Les groupes de couleur sont éditables, mais ne constituent pas de vrais objets sémantiques reconstruits (œil, coquille, corps). Les mesures de fidélité sont relatives au PNG final imprimable, et ne prouvent ni une restitution photographique ni le comportement des outils d'édition Cricut.
