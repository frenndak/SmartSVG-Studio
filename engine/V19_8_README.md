# SmartSVG Studio V19.8 — Appariement multi-modèles et incertitudes

**Date : 22 octobre 2026 — version bêta de comparaison, non certifiée sur Cricut.**

## Ce que fait réellement V19.8

Les masques produits par SAM2, FeyNoBg ou Finegrain peuvent arriver dans un **ordre différent** et avec un **nombre différent d'objets**. Le comparateur historique V19.6 n'autorise une comparaison que dans le même ordre. V19.8 effectue un **appariement un-à-un** optimisant l'IoU global, sans importer SciPy, puis refuse explicitement les paires trop différentes ou ambiguës. Le résultat est un masque aligné et un rapport JSON.

Le moteur renvoie aussi une **carte d'incertitudes**, qui souligne les pixels où les modèles sont en désaccord et les zones où plusieurs masques de référence se chevauchent. Cette carte **n'est pas un fichier de découpe**.

**Mode par défaut : diagnostic.** Les masques d'origine passent à l'export inchangés ; le module ne modifie ni les algorithmes de détourage, ni les fichiers Print Then Cut des versions précédentes.

## Installation

1. Fermer ComfyUI, sauvegarder l'ancien dossier et déplacer **toutes les anciennes versions SmartSVG hors de `custom_nodes`**.
2. Extraire `ComfyUI-SmartSVG-Studio-V19.8` dans le `custom_nodes` de ComfyUI.
3. Redémarrer, charger le workflow `example_workflows/SmartSVG_Studio_V19_8_Express.json`.
4. Pour comparer deux segmentations issues de différents modèles, utiliser `SmartSVG_Studio_V19_8_Comparer_Puis_Exporter.json` et **relier un vrai masque** à l'entrée `masque_reference` du nœud SmartSVGAlignMasksV198. Ne pas relier le MASK de `Load Image` d'une photo JPG comme si c'était un masque d'objet.
5. Ajouter les masques d'autres modèles aux entrées B/C ; leurs dimensions doivent correspondre au même RGB en pixels, mais leur ordre et leur nombre d'objets peuvent différer.
6. Conserver `mode=diagnostic` et `alignement_masques=diagnostic` pour les premiers essais, puis vérifier la carte d'incertitude avant toute sélection automatique.

## Modes

- **diagnostic (recommandé)** : compare, apparie et signale les divergences, mais retourne exactement le masque de référence.
- **selection_prudente** : seulement avec un appariement non ambigu, un IoU élevé et une amélioration du score heuristique. Cela ne garantit pas la qualité réelle ; vérifier visuellement avant Cricut.
- **selection_avec_annotation** : nécessite une annotation de référence créée/validée par un humain et alignée avec l'image. Peut sélectionner l'alternative lorsque son IoU **avec l'annotation** s'améliore suffisamment.

La carte d'incertitude fait partie des sorties du **nœud de comparaison** ; elle ne lance ni SAM2, ni FeyNoBg, ni Florence-2. Pour les exécuter, utiliser les nœuds de segmentation ComfyUI-RMBG installés et leurs modèles respectifs. Les rapports de profiler V19.7.1 restent disponibles pour mesurer le processus. **Aucune mesure GPU réelle n'est contenue dans les démonstrations.**

## Sorties et Cricut

- `masques_retenus` : `[N,H,W]`, valeurs 0..1. Identique à la référence en mode `diagnostic`.
- `zones_incertitude` : `[1,H,W]`, valeurs 0..1, diagnostic seulement, **ne pas relier à l'entrée Print Then Cut**.
- `rapport_appariement` : JSON avec correspondances, IoU entre modèles, refus, zones ambiguës, éventuelles annotations et état de sélection.
- Si utilisé dans l'exporteur V19.8 Express/Expert, un rapport `ALIGNEMENT_MASQUES_V19_8_*.json` est également créé dans le dossier de sortie général, **à côté** des créations, sans les modifier.

Le PNG Cricut reste un export **à vérifier dans Design Space** : qualité des bords, découpe extérieure et marge blanche doivent être inspectées avant impression. Le système ne produit pas de projet natif `.cricut` et la vérification mécanique sur Cricut Explore reste à faire.

## Limites techniques et critères de rejet

- Jusqu'à **16 objets par lot**, 28 millions de pixels cumulés parmi les masques chargés ; aucune interpolation implicite de tailles.
- Masques finis normalisés dans `[0,1]`; les masques `0/255` doivent être normalisés à l'entrée du comparateur.
- Correspondance basée sur IoU réel des masques binaires (`>=0.5`), avec seuil de rejet `0.45` par défaut et marge d'ambiguïté `0.08`. Un objet entièrement absent reste non apparié.
- **La similarité ne prouve pas la justesse**. Une mauvaise segmentation peut être identique chez deux modèles.
- Un ordre différent des personnages est géré. En revanche, deux objets trop semblables sont explicitement déclarés ambigus, et leur référence reste intacte.
- Pas de génération ni de reconstruction des zones cachées. Les photos réalistes doivent conserver leur rendu PNG fidèle.

## Tests

```powershell
python verify_package.py
```

Ce script exécute toutes les suites historiques **et les nouveaux tests V19.8**. Les tests des modèles IA sont simulés ou utilisent des masques synthétiques ; pour valider les modèles réels sur RTX 3070, il faudra fournir les logs/perf/masks issus de ComfyUI.
