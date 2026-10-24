# V21.14 — Journal des modifications

Base : `ComfyUI_SmartSVG_Studio_V21_13_2_Installation.zip`, réextraite indépendamment.

- Nouveau module `smartsvg_vector/recovery_v2114.py` : couche de silhouette sous la palette existante ; chemins fermés `M/L/Z`, masques et bordures contrôlés ; aucun bitmap incorporé.
- Choix de couleur de la sous-couche parmi les couleurs existantes selon l'erreur sur les pixels initialement manquants ; marque explicitement le repli OpenCV si rendu CairoSVG indisponible.
- Avertissements de micro-formes et anneaux fins à largeur physique choisie, sans jamais prétendre certifier une découpe.
- Nouveau nœud `SmartSVGEditableColorsV2114`, conservant les quatre sorties et les paramètres de l'ancienne version.
- Nouvel exemple de workflow ; les anciens nœuds restent inscrits dans le registre, sans altération des moteurs PNG Print Then Cut ou SVG contour.
- Ajout des tests d'absence de modifications globales, protection SVG, qualité, absence de raster, non-régression, déterminisme.

## Résultats empiriques (40 mm, 8 couleurs, vrais masques des images utilisateur)

| Exemple | IoU silhouette 21.13.2 | IoU silhouette 21.14 | Erreur couleur avant/après (sur pixels recouverts) | Chemins avant/après |
|---|---:|---:|---:|---:|
| Escargot n°1 | 83,34 % | 98,71 % | 11,42 → 19,17 | 81 → 82 |
| Pokémon n°1 | 69,87 % | 98,27 % | 7,06 → 12,81 | 95 → 96 |

**Interprétation importante :** meilleure géométrie extérieure, mais plus de pixels coloriés approximativement et donc **erreur couleur accrue**. Préparer les SVG dans Inkscape ; garder PNG Print Then Cut comme sortie haute fidélité.
