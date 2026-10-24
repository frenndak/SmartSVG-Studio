# SmartSVG Studio V21.11.2 — Installation et mode guidé

**Édition : 24 octobre 2026.** Cette version est une stabilisation de la V21.11.1. Elle ne remplace ni les moteurs de fabrication, ni les modèles de segmentation IA.

## Installation

1. Fermer ComfyUI ; sauvegarder les anciens workflows personnels.
2. Déplacer **hors** de `ComfyUI/custom_nodes` toutes les anciennes copies SmartSVG (une seule version active).
3. Décompresser le dossier `ComfyUI-SmartSVG-Studio-V21.11.2` dans `ComfyUI/custom_nodes/`.
4. Redémarrer ComfyUI, actualiser son navigateur et charger le workflow `SmartSVG_Studio_V21_11_2_00_Diagnostic.json`.
5. Lancer « Vérifier mon installation » : lire le résultat. Un nœud SAM2 dont la signature est compatible ne prouve **ni** la présence des modèles sur disque, **ni** leur bon fonctionnement sur RTX 3070.

## Les 4 workflows conseillés

- `00_Diagnostic` : diagnostic non destructif, aucune IA exécutée.
- `01_Express_Auto_Deux_Etapes` : importer un PNG/JPG puis précontrôler l'export automatique. Relier `LoadImage/MASK` à `alpha_loadimage` (déjà prévu dans le workflow). Si le détourage est incertain, le moteur refuse l'export plutôt que d'inventer un rectangle.
- `02_Planche_Corriger_Exporter` : images multiples, correction des masques et une **seule largeur physique** choisie dans le nœud éditeur. Le port `largeur_mm_pour_express` est relié au port `largeur_mm` d'Express. Les masques peuvent être vérifiés à la résolution d'origine.
- `03_Capture_Guidee` : recadrage préalable de capture d'écran et correction. **Attention : Express démarre désactivé (mode 2)**, pour empêcher un export automatique non vérifié. Après détourage et validation, réactiver l'export puis relancer le workflow.

## Utilisation Cricut

Dans chaque projet abouti, ouvrir `00_IMPORTER_DANS_CRICUT`. Importer le **PNG transparent**, pas le SVG de contour, puis sélectionner **Image aplatie / Flat Graphic** et **Imprimer puis découper** dans Design Space. Vérifier la silhouette, le type d'opération et la taille réelle dans Design Space avant impression/découpe.

Le panneau V21.11.2 affiche **précontrôle local** et non une certification de découpe. La sortie SVG sert à d'autres usages de découpe ; elle ne transforme pas automatiquement l'illustration en objets internes modifiables.

## Nouveautés de l'interface

- Panneau « Mon sticker Cricut » sur le nouveau nœud Express : statut de préparation, carte rectangulaire ou correction nécessaire.
- Nouveau nœud `SmartSVGReadinessV21112` sous `SmartSVG / 00 DÉMARRER`.
- Nouveau nœud `SmartSVGUnifiedEditorV21112` pour diagnostiquer les contours à la largeur réellement choisie, à condition de relier son port FLOAT à Express (déjà fait dans les workflows guidés).
- Les anciens nœuds restent accessibles sous leurs identifiants historiques ; leur masquage automatique n'est **pas** effectué car il aurait pu perturber les workflows sauvegardés.

## Tests locaux

Depuis le dossier extrait :

```bash
python verify_package_v21112.py --integrity
python verify_package_v21112.py --python-new
python verify_package_v21112.py --javascript
python verify_package_v21112.py --suite 1
```

Répéter `--suite N` pour N de 1 à 12 ; suites historiques indépendantes. Node.js >=18 est utile uniquement aux tests JavaScript. Le vérificateur limite les threads numériques pour éviter des blocages observés auparavant.

## Limites honnêtes

- Les scènes complexes (photos, mèmes et affiches) exigent un fournisseur IA réellement fonctionnel ou une retouche manuelle ; SAM2/RMBG n'a pas été exécuté sur la RTX 3070 lors de cette livraison.
- Les indicateurs mm de l'éditeur supposent que la largeur fournie correspond à **chaque silhouette** exportée ; le résultat réel après marges et contours doit être vérifié.
- Les précontrôles de topologie ne prouvent pas que le bon personnage a été isolé.
- Les nœuds historiques ne sont pas supprimés et les anciens workflows restent compatibles.
- Ni ComfyUI sur ton PC, ni Design Space, ni la découpe physique Explore 5 n'ont été testés ici.
