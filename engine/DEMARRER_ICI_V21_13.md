# SmartSVG Studio V21.13 — Sélection et SVG multicouche

## Installation

1. Fermer ComfyUI et conserver une copie de tes workflows.
2. Retirer les anciennes copies SmartSVG de `ComfyUI/custom_nodes` puis extraire **une seule** version `ComfyUI-SmartSVG-Studio-V21.13` dans ce dossier.
3. Redémarrer ComfyUI et ouvrir `example_workflows/`.

## Nouveaux workflows

- **`SmartSVG_Studio_V21_13_01_Choisir_Sujet_Puis_Cricut.json` :** importer l'image, détourer avec l'IA si nécessaire, saisir un numéro de sujet entre 1 et 32, puis fabriquer seulement ce sujet via l'Express historique V21.12.2. Le contrôle final doit encore être effectué dans Design Space.
- **`SmartSVG_Studio_V21_13_02_Sujet_vers_SVG_Couleurs.json` :** importer, détourer, sélectionner un sujet puis générer un premier SVG multicolore éditable pour les dessins **simples**.

## SVG multicouche : ce qui est réellement produit

- La zone occupée par le sujet est **recadrée automatiquement** (avec une petite marge) pour que sa taille en millimètres ne corresponde pas à la planche entière. Les couleurs sont quantifiées en **2 à 16 classes**, puis représentées par **des groupes SVG `<g>`** contenant des chemins `<path>` propres. Chaque groupe est éditable indépendamment dans Inkscape ou un autre logiciel vectoriel.
- Ce n'est **ni un PNG encapsulé dans un SVG**, ni une restitution fidèle de toutes les textures et des ombrages. L'illustration est simplifiée, et de minuscules régions peuvent être omises. Le rapport précise nombre de calques, formes et points.
- Le module refuse les images trop photographiques, le masque absent, plein cadre ou de dimensions incompatibles. Pour une photo, conserver le PNG Print Then Cut.
- Un SVG multicouche issu de cette vectorisation **n'est pas automatiquement un projet Cricut Print Then Cut prêt** : le travail des couches, la palette, le fond et le type d'opération devront être vérifiés dans Design Space.
- La **source imprimée** ne change pas dans les anciens projets. L'ancien PNG/SVG de fabrication continue d'être fourni par les nœuds de production précédents.

## Choisir un personnage

Le nouveau nœud `SmartSVGChooseSubjectV2113` conserve le masque original sélectionné (indice commençant à 1). Les petits fragments rattachés à ce masque restent présents ; le rapport avertit lorsque plusieurs îlots significatifs sont détectés. Le nœud ne décide pas tout seul si une oreille ou un petit accessoire doit être gardé.

## Limites et vérification

- Les images de fond noir et la planche d'escargots bénéficient des moteurs déjà présents dans V21.12.2. Le nouveau sélecteur a été testé sur les deux types de planches.
- Aucune exécution réelle de BiRefNet, RMBG ou SAM2 sur la RTX 3070 n'a été possible pendant cette livraison ; les anciennes simulations restent des tests de contrat, pas des tests d'inférence matérielle.
- Aucune découpe physique Cricut Explore 5 ni import dans Design Space n'a été effectué ici. **Cricut Design Space reste indispensable à l'impression/découpe.**
- Le SVG multicolore est **expérimental**. Commencer avec un dessin simple, peu de dégradés et une taille d'export autour de 40–50 mm.

## Tests

```bash
python verify_package_v2113.py --integrity-only
python verify_package_v2113.py --new
python verify_package_v2113.py --javascript
python verify_package_v2113.py --suite 1
```

Les groupes `--suite 1` à `--suite 12` sont indépendants ; Node.js est nécessaire seulement pour les tests JavaScript.
