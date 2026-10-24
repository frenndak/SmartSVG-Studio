# SmartSVG V21.8 — Import direct dans Cricut Design Space

1. Fermer ComfyUI et retirer tout ancien dossier SmartSVG de `custom_nodes/` (déplacer **hors** du dossier).
2. Extraire `ComfyUI-SmartSVG-Studio-V21.8` dans `ComfyUI/custom_nodes/`, puis redémarrer.
3. Charger un des trois workflows `SmartSVG_Studio_V21_8_*.json` ou ajouter `01 · SmartSVG EXPRESS V21.8 — import direct Cricut`.
4. Utiliser les cinq réglages Express habituels, avec IMAGE et masque(s) MASK facultatif(s).
5. Dans le résultat projet, ouvrir **`00_IMPORTER_DANS_CRICUT`**. Vérifier le rapport : `PRET_POUR_IMPORT_LOCAL` n'est **pas** une validation physique.
6. Téléverser le PNG `STICKER_001_IMPRIMER_PUIS_DECOUPER.png`, ou la planche si disponible; sélectionner **Flat Graphic** et vérifier l'opération **Imprimer puis découper**.
7. Régler la largeur dans Design Space, examiner la silhouette en aperçu de couche unique, puis imprimer directement depuis Design Space et découper avec l'Explore 5.

- **Un PNG pour un sticker**, ou **un PNG planche** pour tous les stickers ensemble.
- Les fichiers SVG de `02_CONTOURS` servent à la **découpe seule** et ne doivent pas être superposés au PNG pour Print Then Cut.
- Les PNG HD de `06_HD_AUTOMATIQUE_V21_7_1` sont conservés pour usages annexes : le dossier import direct privilégie le contour autoritatif du PNG de fabrication.
- Une image source avec fond opaque n'est pas automatiquement détourée sans IA/masque : contrôler si le contour proposé est une silhouette ou un rectangle.
- Un PNG ne rend pas les sous-parties du dessin modifiables comme des objets vectoriels. Pour éditer les régions, utiliser les fichiers SVG éditables historiques lorsque disponibles.
- La première utilisation exige un contrôle visuel et une découpe test dans Design Space.
