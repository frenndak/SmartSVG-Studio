# SmartSVG Studio V21.12.2 — Guide d'installation

**Installation** : sauvegarder les workflows personnels ; fermer ComfyUI ; conserver une seule version SmartSVG dans `ComfyUI/custom_nodes/`. Décompresser `ComfyUI-SmartSVG-Studio-V21.12.2` dans ce dossier, redémarrer ComfyUI et recharger son interface.

## Quels workflows ouvrir ?

- `example_workflows/SmartSVG_Studio_V21_12_2_00_Diagnostic_IA.json` : diagnostic de signature des modèles installés, sans inférence.
- `..._01_Express_Auto_IA.json` : traitement direct d'une image et export PNG Cricut.
- `..._02_Corriger_Exporter_IA.json` : éditer le masque avant export.
- `..._03_Capture_IA_Guidee.json` : captures ; activer l'export **après** validation du masque.
- `..._04_Reconnaitre_Image.json` : routage d'image sans IA et sans export.

Les **cinq réglages Express** sont conservés. Le nœud conseillé est `SmartSVGAutoExpressV21122` (« Lot optimisé et fichiers Cricut »). Les anciens nœuds restent enregistrés.

## Fabrication et différence entre PNG et SVG

Lorsque les masques sont disponibles, SmartSVG fabrique les fichiers individuels et les planches, puis les inspecte localement. Les PNG de fabrication se trouvent dans `01_OBJETS`, les SVG de contours dans `02_CONTOURS` et **les fichiers à importer** dans `00_IMPORTER_DANS_CRICUT`. Le nouveau dossier `07_LIVRAISON_STICKERS_V21_12_2/MANIFESTE_STICKERS.json` contient, par sujet, les chemins relatifs, empreintes SHA-256 et avertissements. Le dossier `06_HD_AUTOMATIQUE_V21_7_1` contient les dérivés HD **séparés**.

Dans Cricut Design Space, **téléverser le PNG** comme image aplatie (*Flat Graphic*) et sélectionner *Imprimer puis découper*. Vérifier la taille réelle et les contours, imprimer depuis Design Space et faire une découpe d'essai. Le SVG `CONTOUR_SEUL.svg` n'est **pas** une reconstruction multicouche des couleurs et ne doit pas être superposé au PNG Print Then Cut (risque de double découpe).

## Optimisations / vigilance

- Le nouveau nœud évite une génération intermédiaire redondante des planches ; le nœud historique continue d'employer son ancien chemin.
- Pour les **stickers**, les petits trous dans le *fond blanc de découpe* sont comblés : la source transparente native et le dessin ne sont pas remplacés ; le SVG extérieur est recalculé à partir du masque final.
- Sur le test local fourni (24 Pokémon, 28 mm, 300 ppp), 24 PNG et deux planches ont terminé et franchi le précontrôle. **Les trois fragments potentiellement manquants signalés dans l'analyse des masques doivent toujours être examinés.**
- Un précontrôle géométrique ne démontre ni la justesse sémantique du détourage, ni la compatibilité réelle dans Design Space, ni une découpe physique correcte.
- Les modèles BiRefNet / RMBG / SAM2 ne sont pas fournis dans l'archive. La réussite sur RTX 3070 8 Go reste à mesurer avec ton installation ComfyUI.

## Vérification

Depuis le dossier extrait :

```bash
python verify_package_v21122.py --integrity-only
python verify_package_v21122.py --new
python verify_package_v21122.py --javascript
python verify_package_v21122.py --suite 1
```

Lancer les suites historiques 1 à 12 **indépendamment**. Node.js est utile uniquement pour les tests JavaScript.
