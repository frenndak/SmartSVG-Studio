# SmartSVG Studio V21.9 — Guide d'installation et de prise en main

## Installation (ComfyUI sur ton PC)

1. Fermer ComfyUI.
2. Déplacer **hors de `ComfyUI/custom_nodes/`** toutes les anciennes versions `ComfyUI-SmartSVG-Studio-*` (pas deux versions en parallèle).
3. Décompresser `ComfyUI_SmartSVG_Studio_V21_9_Installation.zip` puis copier son dossier `ComfyUI-SmartSVG-Studio-V21.9` dans `ComfyUI/custom_nodes/`.
4. Redémarrer ComfyUI et forcer si besoin le rechargement de l'interface (Ctrl+F5).
5. Importer le workflow V21.9 adapté :
   - `SmartSVG_Studio_V21_9_01_Cricut_Direct_Capture.json` : capture JPG / mème, avec recadrage prudent possible ;
   - `SmartSVG_Studio_V21_9_02_Cricut_Direct_PNG_Alpha.json` : PNG transparent et inversion du masque `LoadImage` ;
   - `SmartSVG_Studio_V21_9_03_Cricut_Direct_Planche_12.json` : planche de sujets séparés.
6. Charger la source, générer le masque avec ton nœud IA ou le corriger dans l'éditeur V21.6, puis exécuter le workflow.
7. Sur `SmartSVG V21.9 — inspecter contours natifs`, cliquer sur **Inspecter contours 100 %** : la fenêtre affiche l'image réelle avec masque et alertes. Utiliser `100 % natif`, la molette et le déplacement par glissement. Cliquer sur une alerte pour rejoindre la zone exacte.
8. Si nécessaire, modifier les masques dans le nœud V21.6, sauvegarder les retouches et relancer. Cette étape reste manuelle pour les défauts non résolus.
9. Pour **Print Then Cut**, choisir un fichier PNG du dossier de projet **`00_IMPORTER_DANS_CRICUT`**. Dans Cricut Design Space, sélectionner une image aplatie (Flat Graphic), vérifier **Imprimer puis découper**, la silhouette et la largeur physique. Ne pas empiler le SVG de contour sur le PNG.

## Ce qui est automatique et ce qui ne l'est pas

- Les workflows fournis transmettent automatiquement le masque corrigé à l'inspection puis à Express. L'inspection ne modifie **jamais** les masques en sortie.
- Le rapport détecte des anomalies géométriques indicatives, mais il ne modifie pas automatiquement les cheveux, antennes, intersections ou trous.
- Les PNG originaux de Print Then Cut et les SVG de fabrication continuent d'être préparés par V21.8. La sortie HD annexe V21.7.1 reste disponible.
- Les cinq réglages historiques Express sont inchangés.
- L'éditeur V21.6 conserve son aperçu 760 px ; **c'est l'inspecteur V21.9** qui lit les copies à vraie résolution source. Un défaut identifié dans cet inspecteur doit être corrigé dans V21.6 puis réinspecté.
- En cas de source ou de lots excessivement volumineux, la copie visuelle native peut être omise : le traitement et les fichiers d'export ne sont pas remplacés par une version inférieure.

## Limites et précautions

- Maximum 5 Mp par image, 32 sujets et 50 Mp de masques cumulés pour l'inspection ; au-delà, réduire la résolution ou scinder le lot.
- Copies temporaires natives dans `ComfyUI/output/SmartSVG_Studio_Native_V219`. Jusqu'à 8 sessions, 192 Mo cumulés, 48 h de conservation avec nettoyage aux exécutions suivantes. Les fichiers de projet conservés dans les dossiers de fabrication restent intacts.
- Prévisualisation et test de code ≠ démonstration de la découpe physique sur une Cricut Explore 5. Une première découpe test reste nécessaire.
- Les fichiers PNG imprimés ne rendent pas chaque détail du dessin individuellement éditable dans Design Space : pour éditer des tracés internes, utiliser les SVG vectoriels appropriés, lorsque disponibles.

## Auto-vérification

Depuis le dossier de l'extension :

`python verify_package_v219.py --integrity-only`

Pour les tests, utiliser séparément `--suite 1`, `--suite 2`, `--suite 3a`, `--suite 3b`, `--suite 4` à `--suite 9`. Pour le frontend, `python verify_package_v219.py --javascript` (Node.js >=18 uniquement nécessaire pour les tests). Les dépendances Python sont celles de l'installation ComfyUI / SmartSVG existante.
