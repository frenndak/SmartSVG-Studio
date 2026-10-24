# SmartSVG Studio V21.6 — Retouche de masques avant fabrication Cricut

## Livraison

**V21.6 bêta fonctionnelle** : ajout du nœud **`SmartSVGMaskEditorV216`**, sans changement aux cinq réglages ni aux trois sorties de **`SmartSVGExpressV2151`**. Les moteurs historiques de vectorisation ne sont pas modifiés. Les anciens identifiants de nœuds restent enregistrés.

Le nœud V21.6 permet :
- Pinceau **+ Ajouter / − Retirer**, réglage du rayon, sélection de 1 à 32 sujets.
- **Annuler / Rétablir** par trait, raccourcis Ctrl+Z / Ctrl+Maj+Z dans le dialogue.
- Aperçu magenta sur la source PNG, séparé pour chaque masque.
- **Enregistrement dans le vrai widget `retouches_json` du workflow** : ce n'est pas un fichier caché dans un chemin temporaire. Réouvrir le workflow puis relancer pour réappliquer les mêmes traits.
- Géométrie normalisée indépendante de la taille d'affichage, application sur le masque d'origine, préservation des valeurs flottantes non retouchées.
- Contrôle strict de l'image source **et des masques initiaux** par empreinte SHA-256 (canaux RGB et alpha si présents), dimensions et nombre de masques ; refus explicite si source changée.
- Sorties `MASK` corrigé, `IMAGE` inchangée et diagnostic JSON.
- Images de prévisualisation dans `ComfyUI/output/SmartSVG_Studio_Editor` : conservation de 96 fichiers au maximum, suppression des anciennes copies au passage suivant (72 h) ; les fichiers non reconnus ne sont pas supprimés.

## Comment l'utiliser (workflow recommandé)

1. Fermer ComfyUI, enlever les versions précédentes de SmartSVG de `custom_nodes` **en les plaçant ailleurs** (sauvegarder d'abord tes workflows), puis extraire cette archive dans `custom_nodes`.
2. Redémarrer et recharger la page. Charger **`example_workflows/SmartSVG_Studio_V21_6_01_Corriger_Alpha_PNG.json`** (PNG transparent), ou **`..._02_Creer_Masque_Manuel.json`** (image opaque, création d'une sélection vide).
3. Changer `LoadImage` pour ta propre image. **Pour le PNG transparent, le workflow contient `InvertMask`** : dans ComfyUI, la sortie `LoadImage.MASK` vaut *1 − alpha*, et sélectionne donc d'abord le fond transparent au lieu du sujet. L'inversion rétablit la silhouette opaque. Sur une image sans canal alpha, préférer le workflow manuel. **Dans le workflow « masque manuel », le nœud Express est volontairement muet au premier passage** : il refuserait à juste titre d'exporter une sélection encore entièrement vide. Le nœud de retouche est lui-même un nœud de sortie ComfyUI, donc son aperçu peut être généré sans le lancement d'Express. Ajouter éventuellement une liaison `MASK` depuis ton détourage IA (sortie « masques_individuels » du nœud Guidage). Ne pas brancher un masque vide si tu souhaites conserver une sélection IA existante. **Ne pas inverser les masques de segmentation IA si le sujet est déjà blanc (valeur 1)**.
4. **Exécuter une première fois** : le backend publie les miniatures officielles de ComfyUI ; l'éditeur s'active. Si le masque est vide, le premier passage n'est pas un export sticker exploitable, ce qui est normal.
5. Sur le nœud de correction, cliquer **Ouvrir l'éditeur de masques**. Choisir un sujet, peindre / effacer. `Annuler` ou `Rétablir` si nécessaire.
6. Cliquer **Enregistrer les retouches** ; **sauvegarder le workflow JSON**. Dans le workflow « masque manuel », **réactiver le nœud Express** (mode *Always*, non muet). Puis **relancer le workflow**. Les nouveaux masques sont alors utilisés pour générer les PNG/SVG via le nœud Express V21.5.1.
7. Contrôler le contour à taille réelle, les objets séparés, le nombre de découpes, l'opération Print Then Cut et la largeur mm dans Cricut Design Space avant production.

**Si l’image ou le masque de départ a changé** : l'éditeur refusera le vieux JSON au lieu de modifier la nouvelle image en silence. Utiliser **Effacer les retouches enregistrées** puis relancer la file. L'effacement est explicite et ne touche pas les PNG/SVG déjà exportés.

**Si le navigateur ne fournit pas `addDOMWidget`** : le résultat `MASK` Python reste disponible mais la retouche visuelle ne s'ouvre pas ; mettre à jour le frontend ComfyUI et réessayer. Les tests JS inclus sont simulés, pas un essai du frontend de ton PC.

## Limites et garanties

- Il s'agit d'un éditeur **raster de masques**, pas d'un éditeur de points de contrôle des courbes Bézier d'un SVG existant. Corriger un masque améliore la base de la vectorisation, sans garantir automatiquement la qualité finale d'une découpe Cricut.
- Le masque corrigé est recalculé sur les dimensions d'origine (jusqu'à **5 millions de pixels pour l'image**, **32 masques**, et **50 millions de pixels de masques au total**). Au-delà, réduire la source ou séparer les sujets en plusieurs lots.
- 400 traits, 1 500 points par trait, 12 000 points au total et 350 Ko de JSON au maximum. La mémoire GPU des modèles d'IA n'est pas mesurée ici ; le nouvel éditeur est CPU.
- L'affichage des coups de pinceau peut différer d'un pixel de la sortie finale selon le navigateur ; **la sortie `MASK` après relance fait foi**.
- La V21.6 n'inclut pas la validation de l'interface sur ton vrai ComfyUI/Nodes 2.0, l'inférence SAM2/Florence-2 sur RTX 3070, ni la découpe physique sur Cricut Explore 5.
- **Confidentialité :** les miniatures locales transitent par `/view` sous les permissions de ton serveur ComfyUI. Ne pas exposer ComfyUI sur Internet sans authentification.
- Les copies de prévisualisation peuvent être effacées 72 h après une exécution suivante ; les strokes restent dans le workflow enregistré mais **les aperçus ne sont pas portables**. Il suffit de relancer le workflow pour les régénérer.

## Vérifications

Lancer depuis le dossier de l'extension :

```bash
python verify_package_v216.py --integrity-only
python verify_package_v216.py --suite 1
python verify_package_v216.py --suite 2
python verify_package_v216.py --suite 3
python verify_package_v216.py --suite 4
python verify_package_v216.py --suite 5
python verify_package_v216.py --javascript
```

Le test JS demande Node.js >=18 uniquement pour la vérification, pas pour utiliser ComfyUI. Le script compare aussi les hashes des fichiers V21.5.1 conservés, en dehors du point d'entrée `__init__.py` nécessaire à l'enregistrement V21.6.
