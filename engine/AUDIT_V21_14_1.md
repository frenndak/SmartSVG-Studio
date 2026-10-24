# SmartSVG V21.14.1 — Audit indépendant et décisions

**Base** : ZIP V21.14 vérifié puis réextrait. Aucune modification des moteurs historiques de fabrication PNG/SVG.

## Objet de cette version

La V21.14 a réparé la silhouette en ajoutant un fond vectoriel uni mais augmenté l'erreur RGB. La V21.14.1 colore au plus dix grandes composantes initialement manquantes, insérées au-dessus du fond de silhouette et derrière les calques historiques. Chaque composante correspond à de véritables chemins SVG éditables et possède une couleur moyenne locale de l'image source.

## Contrôles

- Garantie de non-régression locale de l'IoU et de l'erreur moyenne sur la silhouette après composition sur fond blanc.
- Plafond des formes et points ajoutés ; pas de `image` SVG, de script, de référence externe ni de transformations autorisées.
- La fidélité des **couleurs** ne se confond pas avec la fidélité **des formes** : l'erreur couleur totale est désormais mesurée sur tous les pixels de la silhouette source ; l'ancienne MAE est calculée seulement sur les pixels communs.
- Anciens SVG de contour et PNG Cricut conservés intégralement. Le nœud précédent V21.14 reste utilisable et conserve ses anciens résultats.

## Mesures réelles

- Escargot : MAE sur toute la silhouette 19,8473 → 19,2220 ; IoU 0,98709 → 0,98842.
- Pokémon : MAE sur toute la silhouette 15,2914 → 14,9355 ; IoU 0,98271 → 0,98713.
- Ajout de 10 et 7 formes respectivement. Les gains ne justifient **pas** d'utiliser ces SVG comme chemin de lame sans inspection.

## À améliorer

1. Vectorisation des petites formes et des dégradés avec conservation d'une complexité compatible avec la coupe.
2. Choix intelligent du format final : PNG aplati Print Then Cut, SVG de contour ou SVG multicouche éditable.
3. Véritable comparaison sur un corpus identique avec Canva Vectorify (fidélité, temps, éditabilité et effort manuel).
4. Vérification de l'interface ComfyUI, inférence GPU et import/coupe physique Cricut Explore 5.
