# SmartSVG Studio V21.14.1 — Guide d'installation

**Version de travail corrective — 24 octobre 2026.** Archive créée à partir de V21.14.

## Installation

1. Fermer ComfyUI. Sauvegarder les workflows personnalisés.
2. Déplacer les dossiers SmartSVG précédents en dehors de `custom_nodes` : ne pas charger deux versions simultanément.
3. Décompresser `ComfyUI-SmartSVG-Studio-V21.14.1` dans `ComfyUI/custom_nodes`.
4. Redémarrer ComfyUI, puis ouvrir `example_workflows/SmartSVG_Studio_V21_14_1_01_Couleurs_Vectorielles.json`.
5. Fournir `IMAGE` et un `MASK` du sujet, choisir le nombre de couleurs (2–16), la largeur en millimètres (5–300), et lancer.
6. Ouvrir le SVG final dans Inkscape pour vérifier les vrais chemins. **Ne pas l'utiliser à la place du PNG aplati pour Print Then Cut.**

## Ce qui change

- Les calques SVG V21.14 restent intactes, et les régions importantes oubliées par le premier rendu reçoivent des couleurs distinctes échantillonnées dans l'image source.
- Le nombre de nouvelles formes est plafonné à 12 (au plus 10 zones connexes, 6 500 points), et la qualité du résultat est contrôlée avant d'accepter la correction.
- Le rapport contient deux mesures complémentaires : **IoU de silhouette** (plus grand = meilleur), et **erreur RVB moyenne sur toute la silhouette** (plus petit = meilleur ; pixels absents composites sur fond blanc). Cette dernière ne doit pas être confondue avec l'ancienne erreur calculée uniquement là où le SVG était opaque.
- Un rendu CairoSVG est utilisé si le composant existe ; sinon la reconstruction géométrique interne fournit une estimation, explicitement signalée.
- La récupération des formes de couleur est **non destructive** : si le candidat n'améliore pas les mesures, le SVG V21.14 original est conservé.

## Vérification du paquet

```bash
python verify_package_v21141.py --integrity
python verify_package_v21141.py --targeted
python verify_package_v21141.py --javascript
python verify_package_v21141.py --suite 1
```

Pour l'intégralité des suites historiques, exécuter séparément `--suite 1` à `--suite 12`.

## Limitations connues

- Les nouvelles régions colorées restent des approximations : les ombrages subtils, les yeux et de nombreuses petites zones peuvent nécessiter une reprise manuelle.
- Des couleurs additionnelles créent des chemins de découpe supplémentaires si l'on convertit les calques SVG en opérations de coupe dans Design Space. **Ce SVG multicouche est d'abord un format d'édition, pas un format prêt à découper.**
- Les tests logiciels ne prouvent ni l'intégration au frontend ComfyUI du PC, ni la qualité de l'IA sur RTX 3070, ni une découpe réelle Cricut Explore 5.
- Canva Vectorify produit déjà des SVG éditables. SmartSVG vise une qualité supérieure **pour les workflows spécialisés Cricut**, mais aucune comparaison chronométrée et qualitative avec Canva n'a encore été effectuée à données et critères identiques.
