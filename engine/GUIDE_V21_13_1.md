# SmartSVG Studio V21.13.1 — Sélection visuelle et contrôle du SVG multicouche

## Installation

1. Fermer ComfyUI et sauvegarder les workflows personnels.
2. Déplacer les anciennes versions SmartSVG **en dehors** de `custom_nodes` : une seule version du plugin doit être active.
3. Décompresser `ComfyUI-SmartSVG-Studio-V21.13.1` dans `ComfyUI/custom_nodes/`.
4. Redémarrer ComfyUI et actualiser le navigateur ; les deux nouveaux workflows sont dans `example_workflows/`.

## Workflow 01 : choisir un personnage pour Print Then Cut

`SmartSVG_Studio_V21_13_1_01_Clic_Sujet_Puis_Cricut.json`

- Remplacer l'image du nœud `LoadImage`, puis exécuter une première fois.
- Le nœud « Choisir un sujet » publie une grille de **vignettes réelles** (32 au maximum) ; cliquer sur le dessin voulu règle le champ `numero_sujet`.
- **Relancer le workflow.** Un clic dans la grille ne lance pas de fabrication, ne change pas le masque déjà calculé et ne déclenche aucune action cachée.
- Le nœud Express fabrique ensuite le PNG transparent, les contours SVG historiques et les fichiers dans `00_IMPORTER_DANS_CRICUT` selon les mêmes règles que V21.13.
- S'il n'y a pas de grille (ancien frontend ComfyUI, DOM indisponible), utiliser directement le champ numérique `numero_sujet`. Les fichiers de fabrication ne dépendent pas du panneau visuel.

## Workflow 02 : SVG multicouche et fidélité

`SmartSVG_Studio_V21_13_1_02_Clic_Sujet_SVG_Comparatif.json`

- Choisir un personnage comme au-dessus, puis exécuter.
- Le nouveau nœud de vectorisation reprend les 2 à 16 couleurs et la largeur physique en mm, et publie **deux images** : le comparatif et l'aperçu de couleurs.
- Le nœud `PreviewImage` affiche un visuel en trois bandes, de gauche à droite : **source recadrée, SVG reconstruit depuis les chemins, différence**.
- Dans la bande de droite : **rouge = pixels du sujet manquants**, **bleu = pixels ajoutés hors silhouette**, **violet = écart important de couleur**. Les gris signalent des écarts plus faibles.
- Le rapport JSON indique le recouvrement approximatif des silhouettes (IoU), la différence moyenne de couleur, les points de géométrie et les zones fines probables à inspecter.
- Le contrôle reconstruit les `path` `M/L/Z` et `fill-rule=evenodd` réellement émis par SmartSVG ; **c'est une reconstruction OpenCV**, et non un rendu navigateur/Inkscape ni une simulation de lame Cricut.

## Interprétation pratique

- Un **SVG multicouche expérimental** est utile pour retoucher des couleurs et des formes dans Inkscape, mais peut simplifier fortement les cheveux, ombrages et petits détails. Les SVG sont des chemins réels (pas des PNG encapsulés).
- La vérification de fidélité ne certifie **ni** un SVG comme prêt à découper, **ni** un PNG comme accepté par Design Space.
- Pour reproduire fidèlement l'image en couleur sur la Cricut Explore 5, conserver le **PNG transparent de Print Then Cut**, importé comme **Flat Graphic / Imprimer puis découper**. Ne pas superposer par erreur le SVG de contour au même PNG.
- Les chiffres de géométrie en mm sont indicatifs : contrôler les dimensions et trajets dans Design Space avant une découpe d'essai.

## Limites

- ComfyUI et Nodes 2.0 n'ont pas été testés sur le PC utilisateur pendant la construction ; le panneau peut ne pas apparaître sur un frontend différent.
- Les modèles IA RMBG/SAM2 ne sont pas fournis et leur inférence sur RTX 3070 n'est pas certifiée.
- La sélection de vignette repose sur les masques existants : un fragment oublié par la segmentation n'est **pas réparé** par un clic.
- Le moteur multicouche est limité aux illustrations simples : les photos sont refusées, et l'outil est encore expérimental sur les dessins avec de nombreux détails.

## Vérifications locales (Python de ComfyUI)

```shell
python verify_package_v21131.py --integrity-only
python verify_package_v21131.py --new
python verify_package_v21131.py --javascript
python verify_package_v21131.py --suite 1
```

Répéter `--suite N` de 1 à 12 pour l'ensemble des tests historiques.
