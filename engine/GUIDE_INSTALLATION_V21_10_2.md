# SmartSVG Studio V21.10.2 — Installation et contrôle

1. Fermer ComfyUI. Déplacer les anciennes versions de SmartSVG **hors** du répertoire `custom_nodes` afin de n'en laisser qu'une.
2. Extraire `ComfyUI-SmartSVG-Studio-V21.10.2` dans `ComfyUI/custom_nodes/` ; redémarrer et actualiser le navigateur.
3. Charger un workflow `example_workflows/SmartSVG_Studio_V21_10_*.json` ; le nom du workflow V21.10 reste volontairement inchangé.
4. Si l'image est opaque, apporter un `MASK` de segmentation/détourage ou dessiner un masque dans l'éditeur. **Sans masque, une découpe rectangulaire n'est pas une silhouette de personnage**.
5. Corriger dans l'éditeur, cliquer **Enregistrer les retouches**, puis **relancer le workflow** pour actualiser les exports et le QA. Le brouillon récupéré après une relance reste temporaire tant qu'il n'est pas enregistré.
6. Pour Cricut, choisir exclusivement le PNG dans `00_IMPORTER_DANS_CRICUT`, l'importer en `Flat Graphic / Image aplatie`, contrôler l'opération `Imprimer puis découper`, la taille physique et les contours à l'écran. **Ne pas superposer le SVG de contour**.
7. Les fichiers HD sont enregistrés séparément ; ils ne remplacent pas automatiquement le PNG d'import direct.

## Vérifier l'installation

Depuis le dossier de l'extension : `python verify_package_v21102.py --integrity-only` puis `python verify_package_v21102.py --targeted`; `python verify_package_v21102.py --javascript` nécessite Node.js 18+ uniquement pour les tests. Pour tous les tests historiques, exécuter séparément `python verify_package_v21102.py --suite 1`, puis `--suite 2` jusqu’à `--suite 12` : le regroupement dans un même processus peut se bloquer selon les bibliothèques numériques.

## Limites

Ces tests ne simulent pas le frontend ComfyUI en conditions réelles, l'inférence IA sur RTX 3070, l'import dans Design Space ni la découpe Cricut Explore 5. Toujours commencer par un sticker test et vérifier son contour.
