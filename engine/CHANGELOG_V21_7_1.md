# SmartSVG Studio V21.7.1 — HD automatique prudente

- Nouveau nœud **SmartSVG EXPRESS V21.7.1** (6 champs requis dont l'entrée image : **les 5 réglages historiques inchangés**, plus MASK facultatif). Les anciens nœuds V21.7/V21.6 restent fonctionnels.
- Export sans réglage supplémentaire de PNG HD **complémentaires** en 600 ppp maximum, dans `06_HD_AUTOMATIQUE_V21_7_1/` à l'intérieur du dossier du projet. Les originaux Cricut (PNG, SVG, PNG découpé), leur profil de découpe et les planches existantes **ne sont jamais réécrits**.
- Image à 300 ppp → 600 ppp x2 ; image à 450 ppp → 600 ppp x1,33. Dimensions physiques quasi identiques lors de la mise à l'échelle si les densités sont respectées ; Cricut Design Space peut gérer la taille différemment, contrôler manuellement.
- Redimensionnement RGBA avec couleur prémultipliée pour limiter les franges ; faible accentuation intérieure seulement si le bruit et les écarts de couleur sont acceptables, sans modifier l'alpha du PNG d'origine. Aucune reconstruction miraculeuse de détails, aucune IA requise.
- Vérifications automatiques : limites de pixels (5 Mp source, 6 Mp HD par fichier, 50 Mp HD total), intégrité des chemins, alpha compatible (IoU >= 98,5 % après réduction), PNG et DPI lisibles, repli non bloquant.
- Rapport JSON `amelioration_hd_v2171` et rapport complémentaire `RAPPORT_HD_V21_7_1.json`, raisons explicites des sorties ignorées.
- Trois workflows V21.7.1 avec nouveau nœud Express, et conservation des trois V21.7 antérieurs.
- Le contour SVG reste celui du PNG de fabrication non modifié. La version HD est une option supplémentaire pour la partie impression / édition, **pas un remplacement certifié du chemin de découpe**.
- GPU RTX 3070, modèles IA, rendu frontend réel et découpe physique non testés dans cette distribution CPU.
