# SmartSVG Studio V21.7.1 — Installation et utilisation HD automatique

## Installation propre

1. Fermer ComfyUI.
2. Enlever les anciennes installations SmartSVG de `ComfyUI/custom_nodes/` en les plaçant **hors** du dossier (ne pas empiler plusieurs versions).
3. Extraire `ComfyUI-SmartSVG-Studio-V21.7.1` dans `ComfyUI/custom_nodes/`.
4. Redémarrer ComfyUI et recharger la page.
5. Charger l'un des trois `example_workflows/SmartSVG_Studio_V21_7_1_*.json` : Capture, PNG Alpha ou Planche 12.
6. Lancer les noeuds selon les indications du workflow. Sur le workflow Capture, Express démarre en mode non exécuté pour que vous puissiez enregistrer un masque manuel ; réactiver ensuite **Always**.

## Aucune configuration HD

Utiliser le nouveau nœud `SmartSVG EXPRESS V21.7.1 — HD automatique`. Les mêmes cinq réglages sont conservés : dossier, profil, largeur, ppp et IA locale. Le port `MASK` reste facultatif.

Le nœud produit tous les fichiers historiques **identiques** à ceux de V21.7, puis tente des PNG HD complémentaires pour les objets de fabrication, en **600 ppp** :

- `01_OBJETS/…` : fichiers de fabrication habituels, **à privilégier pour les contours de découpe**.
- `06_HD_AUTOMATIQUE_V21_7_1/sujet_001_HD.png`, `sujet_002_HD.png`, etc. : versions HD optimisées, utiles pour l'impression ou la réutilisation dans d'autres supports.
- `06_HD_AUTOMATIQUE_V21_7_1/RAPPORT_HD_V21_7_1.json` : détail de toutes les optimisations appliquées/ignorées.

Aucune correction visible ne sera nécessaire sur les images déjà assez nettes : SmartSVG choisit le rééchantillonnage seul ou une accentuation douce. Les cas incompatibles sont ignorés et l'image source reste exploitable.

**Important :** Cricut Design Space ne reprend pas toujours les dimensions du PNG depuis les métadonnées ppp. Vérifier la largeur en millimètres, la forme du tracé SVG et les contours dans l'application. L'augmentation de résolution ne recrée pas les détails absents ; les contours très fins restent à vérifier. Les planches d'origine ne sont pas remplacées par une planche HD, mais chaque sujet reçoit sa version si le budget le permet.

## Contrôle sur les cas représentatifs

- Dessin manga photographié : mise à l'échelle prudente seulement ; pas de suppression garantie du moiré.
- 12 escargots : 12 sujets HD individuels si leurs masques sont corrects ; contours des pointillés à contrôler.
- Illustration texte : légère accentuation possible, sans reconnaissance/recréation des lettres.
- Photo du personnage avec chopes : bruit photo surveillé pour éviter une suraccentuation.
- Affiche complexe : conserver l'original si la taille HD dépasse les seuils.
- Canard en capture mobile : recadrer avant le masque (module V21.7) ; aucune suppression automatique de l'UI par HD.
- Mème au PC : contour manuel et dégradés de fumée/feu restent délicats.

## Vérification technique

Depuis le dossier d'extension, lancer dans des terminaux séparés :

```
python verify_package_v2171.py --integrity-only
python verify_package_v2171.py --suite 1
python verify_package_v2171.py --suite 2
python verify_package_v2171.py --suite 3
python verify_package_v2171.py --suite 4
python verify_package_v2171.py --suite 5
python verify_package_v2171.py --suite 6
python verify_package_v2171.py --suite 7
python verify_package_v2171.py --javascript
```

Les tests JavaScript nécessitent Node.js 18+ uniquement pour la validation, pas pour l'usage de l'extension.
