# Installation et utilisation de SmartSVG Studio V21.11

## Installation (ComfyUI)

1. Arrêter ComfyUI. Déplacer les anciens dossiers SmartSVG **en dehors** de `custom_nodes` afin de ne conserver qu'une version de l'extension.
2. Extraire `ComfyUI-SmartSVG-Studio-V21.11` dans `ComfyUI/custom_nodes/`.
3. Redémarrer ComfyUI ; actualiser la page (Ctrl+F5 si nécessaire).
4. Charger l'un des trois nouveaux workflows depuis `example_workflows/` :
   - `SmartSVG_Studio_V21_11_01_Auto_Simple.json` pour le traitement direct.
   - `SmartSVG_Studio_V21_11_02_Auto_Corriger_Exporter.json` pour inspecter et corriger les masques.
   - `SmartSVG_Studio_V21_11_03_Capture_Auto_Correction.json` pour une capture à recadrer avant inspection.
5. Remplacer l'image fictive de `LoadImage` par le PNG ou JPEG à traiter. Le nom `choisir_image.png` n'est qu'un emplacement fictif, pas une image fournie.
6. Pour un sticker, laisser `Sticker - contour du sujet`, vérifier la largeur en mm et choisir l'IA `Si disponible`. Si les modèles sont incompatibles/non installés pour une image complexe, le nœud refusera honnêtement de produire une silhouette.
7. Ouvrir le dossier `00_IMPORTER_DANS_CRICUT`, importer **le PNG** dans Cricut Design Space comme *Flat Graphic* / **Imprimer puis découper**. Vérifier l'opération, les dimensions et la silhouette avant impression. Ne pas ajouter le SVG de contour par-dessus le PNG.

## Comment marche le détourage automatique ?

- **Canal alpha utilisable :** reprise de la silhouette du PNG, séparation de ses composantes quand possible.
- **Illustration sur fond blanc réellement uniforme :** extraction prudente des sujets par couleurs et contours. Une planche 4×3 comme les escargots peut être découpée en 12 masques. Les cadres pointillés sont ignorés par cette méthode, mais vérifie visuellement chaque objet.
- **Photographie / affiche / capture complexe :** tentative avec le fournisseur IA ComfyUI-RMBG déjà installé si autorisée, via le pont historique `SAM2Segment` ; aucune exécution GPU n'a été validée pendant la construction du paquet. La présence d'un nœud n'assure pas que son API ou son modèle soit compatible.
- **Aucun masque fiable :** erreur explicite, pas de sticker factice. Préparer le sujet via RMBG/SAM2/Florence-2, fournir le port MASK ou utiliser l'éditeur unifié sur un masque de base.
- **Carte rectangulaire demandée :** ne nécessite pas de segmentation ; le cadre est un choix explicite.

## Retouches et export

Le workflow 02 relie : `LoadImage` -> `SmartSVGAutoMasksV2111` -> `SmartSVGUnifiedEditorV2110` -> `SmartSVGExpressV218`. Le workflow 03 ajoute le recadrage des captures. Les retouches du panneau unifié sont sauvegardées dans le workflow ; l'export est effectué avec la sortie MASK corrigée.

Le mode Express conserve ses 5 réglages et son port MASK facultatif. Les PNG HD supplémentaires restent séparés des PNG de fabrication. SVG = contour seul, pas vectorisation interne complète des couleurs / textes.

## Validation locale et limites

- Nœuds, masques, tests Python/JavaScript, exemples de workflow et précontrôle PNG ont été testés hors frontend ComfyUI.
- Le lot réel des 12 escargots a fourni 12 PNG individuels, 12 SVG de contour et une planche. Le précontrôle local classait les 12 PNG comme importables en *Print Then Cut*. **Cela ne remplace pas un essai d'import dans Design Space ni une découpe physique Cricut Explore 5**.
- Les six autres images opaques à fond complexe sont volontairement rejetées en mode sans IA.
- L'IA locale dépend de l'installation et des versions effectives de ComfyUI-RMBG, de la disponibilité des poids et de la mémoire GPU.
- Limite entrée du détecteur : 5 mégapixels, 32 masques, 50 millions d'échantillons MASK cumulés.

## Vérifier

Depuis le répertoire extrait :

```sh
python verify_package_v2111.py --integrity-only
python verify_package_v2111.py --new
python verify_package_v2111.py --javascript
python verify_package_v2111.py --suite 1
# puis --suite 2 jusqu'à 12 pour les tests historiques
```

`node` (Node.js 18+) n'est utile que pour exécuter les tests JavaScript, pas pour utiliser SmartSVG.
