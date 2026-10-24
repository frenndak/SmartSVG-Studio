# SmartSVG Studio V21.14 — Guide d'installation et SVG multicouche

**Date : 24 octobre 2026.** Nouveau moteur expérimental de récupération de silhouette, strictement séparé des PNG Print Then Cut.

## Installer

1. Arrêter ComfyUI. Sauvegarder les anciens workflows personnalisés et déplacer les anciennes copies SmartSVG **hors de** `custom_nodes`.
2. Extraire **`ComfyUI-SmartSVG-Studio-V21.14`** dans `ComfyUI/custom_nodes`.
3. Redémarrer ComfyUI puis ouvrir `example_workflows/SmartSVG_Studio_V21_14_01_Vectoriser_Sujet_Avec_Controle.json`.
4. Dans `LoadImage`, choisir une illustration. Le workflow détecte les masques, permet de sélectionner un sujet et le vectorise. Pour un fond complexe, installer/configurer l'IA ComfyUI-RMBG, puis corriger les masques avant export.
5. Utiliser `SmartSVGEditableColorsV2114` pour créer le SVG couleurs expérimental, son aperçu comparatif et un rapport JSON.

## Ce qui change

- Les masques de silhouette reconnus sont conservés à travers une couche de fond vectorielle éditable **placée sous les anciennes couches colorées**.
- La couleur du fond est choisie parmi la palette existante, en minimisant l'erreur visuelle dans les zones qui étaient absentes du rendu précédent ; sans CairoSVG, cette sélection est marquée estimée.
- Le rapport indique **IoU de silhouette avant/après**, erreur moyenne des couleurs sur la zone recouverte, nombre de chemins et avertissements pour les formes sous 0,8 mm de largeur équivalente, à taille réelle choisie.
- Le nombre d'anneaux fins est une **estimation géométrique**, pas une simulation de lame. Une sous-couche peut créer une ligne de découpe supplémentaire à l'import d'un SVG multicouche dans Design Space.

## Cricut : quel fichier importer ?

- **Imprimer puis découper :** ouvrir exclusivement les PNG transparents du dossier `00_IMPORTER_DANS_CRICUT` via Design Space, en image aplatie (*Flat Graphic*). Cette version **ne modifie pas** leur générateur.
- **SVG multicouche :** des chemins vectoriels indépendants destinés à l'édition sous Inkscape. Les couleurs, trous, courbes et sous-couches peuvent être ajustés. Ne pas supposer qu'un tel SVG est directement utilisable pour la découpe de plusieurs couches de vinyle.
- Le **SVG de contour** historique est destiné à d'autres opérations de découpe et ne doit pas être superposé automatiquement au PNG Print Then Cut.

## Interpréter le diagnostic

- `fidelite_silhouette_avant/apres` : IoU géométrique sur le rendu reconstitué. Le score ne mesure pas la correspondance des couleurs ni la facilité de découpe.
- `erreur_couleur_avant/apres` : erreur absolue moyenne RGB sur la surface commune ; **plus faible est meilleur**. Cette erreur peut augmenter lorsque les zones récupérées sont recolorées.
- `risques_decoupe.anneaux_fins_a_verifier` : nombre indicatif de contours ou anneaux fragiles, au seuil choisi. **Aucune certification physique Cricut**.
- `comparaison_v21131.rendu_standard_verifie` : indique si CairoSVG a réellement rendu le SVG. Sur Windows, Cairo peut nécessiter une installation propre ; sans lui, le diagnostic est explicitement approximatif.

## Vérifier l'archive après installation

```shell
python verify_package_v2114.py --integrity-only
python verify_package_v2114.py --targeted
python verify_package_v2114.py --javascript
python verify_package_v2114.py --suite 1
# répéter --suite 2 ... --suite 12 si un audit complet est souhaité
```

## Limites

Les SVG multicouches restent **expérimentaux** et perdent de nombreux détails de couleur. Les modèles IA, le frontal ComfyUI réel, la RTX 3070 et Design Space/Explore 5 n'ont pas été testés physiquement dans ce paquet. La sous-couche améliore les contours extérieurs, mais ne reconstruit pas sémantiquement les éléments d'une illustration.
