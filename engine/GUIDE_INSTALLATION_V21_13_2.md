# SmartSVG Studio V21.13.2 — Installation et mode SVG fidèle

1. Fermer ComfyUI et sauvegarder les workflows existants.
2. Déplacer les anciennes versions SmartSVG **hors** de `custom_nodes`, puis extraire seulement `ComfyUI-SmartSVG-Studio-V21.13.2` dans ce dossier.
3. Redémarrer ComfyUI, rafraîchir l'interface et ouvrir `example_workflows/SmartSVG_Studio_V21_13_2_01_SVG_Fidelite.json`.
4. Choisir un sujet, régler le nombre de couleurs (2 à 16) et la largeur physique ; exécuter puis lire le diagnostic.
5. Un score élevé **n'est pas une certification de découpe**. Pour un sticker couleur, conserver **le PNG Print Then Cut** et importer ce PNG dans Design Space comme image aplatie. Pour manipuler des calques séparés, ouvrir le SVG expérimental dans Inkscape puis vérifier les chemins et les petits éléments.

## Rendu SVG de qualité (optionnel)

La V21.13.2 détecte **CairoSVG** au moment de vérifier le SVG. Si cette bibliothèque et ses dépendances natives sont disponibles, l'aperçu est calculé à partir d'un moteur SVG standard. Sinon, un reconstructeur OpenCV local continue à fournir une estimation **explicitement signalée comme approximative**, jamais automatiquement certifiée.

Installation optionnelle (dans **le Python utilisé par ComfyUI**, selon compatibilité) : `python -m pip install cairosvg`. Sur Windows, CairoSVG peut nécessiter des bibliothèques natives supplémentaires. Il reste facultatif et n'est pas téléchargé automatiquement par SmartSVG.

## Vérifier localement

```sh
python verify_package_v21132.py --integrity-only
python verify_package_v21132.py --new
python verify_package_v21132.py --javascript
python verify_package_v21132.py --suite 1
```

Répéter `--suite 2` jusqu'à `--suite 12`, dans des processus distincts. Node.js n'est requis que pour les tests JS.

## À savoir

- SVG multicouche : chemin de chaque couleur éditable, mais chaque chemin peut devenir une découpe séparée dans Design Space ; ne pas présumer une opération Print Then Cut.
- Le contrôleur analyse les chemins SVG générés ; un score OpenCV seul ne suffit plus à présenter un résultat comme prévalidé.
- Une photo réaliste ou une couverture détaillée exige toujours une segmentation IA / retouche puis une vectorisation adaptée. Les petits contours, trous et fragments doivent être vérifiés visuellement.
- Les anciens workflows et les nœuds historiques restent fonctionnels. Les moteurs PNG et de préparation Cricut n'ont pas été modifiés.
