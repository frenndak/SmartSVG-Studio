# SmartSVG Studio V21.9.1 — Installation et notes d’utilisation

1. Fermer ComfyUI ; retirer **hors du dossier `custom_nodes`** les anciens répertoires SmartSVG.
2. Extraire et copier le dossier `ComfyUI-SmartSVG-Studio-V21.9.1` dans `ComfyUI/custom_nodes/`.
3. Redémarrer ComfyUI et rafraîchir le navigateur. Utiliser les trois workflows `SmartSVG_Studio_V21_9_*.json` fournis (ce sont les workflows valides aussi pour 21.9.1).
4. Fournir une source et de vrais masques (IA ou manuels), inspecter les contours à 100 %, puis corriger dans V21.6 si nécessaire.
5. Importer un **PNG du dossier `00_IMPORTER_DANS_CRICUT`** dans Cricut Design Space, choisir **Flat Graphic / Imprimer puis découper**, vérifier la taille et la silhouette, imprimer depuis Design Space et effectuer une découpe d’essai. Ne pas empiler le SVG de contour par-dessus le PNG.
6. Pour relancer un projet identique, le même fichier d’import est maintenant reconnu sans échec de collision. Si l’image a changé et qu’un ancien PNG porte le même nom, créer un nouveau projet/dossier ou déplacer l’ancien export après vérification : aucune suppression ou réécriture automatique n’est autorisée.

**Vérification** : `python verify_package_v2191.py --integrity-only` ; pour les suites utiliser `--suite 1` ... `--suite 10` (dont `3a`/`3b`), séparément ; pour les tests frontend `--javascript` (Node.js 18+). Les tests CPU ne certifient pas la découpe physique Cricut.
