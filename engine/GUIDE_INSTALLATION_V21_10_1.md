# SmartSVG Studio V21.10.1 — Installation et utilisation

1. Fermer ComfyUI. Déplacer l'ancien dossier SmartSVG **hors de `ComfyUI/custom_nodes/`**, sans le supprimer si vous souhaitez une sauvegarde.
2. Extraire le dossier `ComfyUI-SmartSVG-Studio-V21.10.1` dans `ComfyUI/custom_nodes/`. Ne pas laisser plusieurs versions de SmartSVG dans `custom_nodes`.
3. Redémarrer ComfyUI ; rafraîchir le navigateur (Ctrl+F5). Charger l'un des workflows `example_workflows/SmartSVG_Studio_V21_10_*.json` (conservés et compatibles).
4. Envoyer l'image et, si disponible, le masque au nœud **SmartSVG V21.10 — corriger + inspecter (natif)**. Exécuter le nœud puis cliquer sur **Inspecter + corriger les contours**.
5. Choisir le sujet, zoomer pour inspecter, déplacer avec l'outil main, corriger avec les pinceaux vert (+ Ajouter) et orange (− Retirer), puis **Enregistrer les retouches**. Relancer le workflow ComfyUI pour fabriquer les PNG/SVG corrigés.
6. Pour Cricut Design Space, ouvrir le dossier du projet **`00_IMPORTER_DANS_CRICUT`** et importer le PNG transparent concerné, choisir **Image aplatie / Flat Graphic**, vérifier l'opération **Imprimer puis découper**, le contour et la taille physique. Ne pas superposer le SVG de contour pour un sticker simple.

Les 5 réglages Express, le format JSON de correction V21.10 et les 3 sorties du nœud restent les mêmes. La version V21.10.1 n'est **pas** un détourage IA automatique supplémentaire. Une source opaque sans masque peut encore produire une carte rectangulaire : utiliser une segmentation IA ou tracer la silhouette avant l'export.

## Vérification depuis le répertoire d'extension

```
python verify_package_v21101.py --integrity-only
python verify_package_v21101.py --javascript
python verify_package_v21101.py --suite 12
```

Pour toutes les sous-suites Python, exécuter `--suite 1` à `--suite 12` **séparément**. Cette méthode évite les blocages possibles du lanceur agrégé dans certains environnements. Le script retourne une erreur en cas de non-réussite ; un timeout n'est jamais considéré comme un succès.

**Limites** : frontend ComfyUI réel, modules IA GPU, import Design Space et découpe physique à contrôler sur votre installation.
