# SmartSVG Studio V20.0 — Guide d'installation et de validation

**Statut : bêta consolidée, 22 octobre 2026.** La V20.0 remplace V19.9 dans les nouveaux workflows. Les nœuds historiques restent utilisables dans l'installation unique.

## Objectif

Sécuriser la seconde passe IA localisée (SAM2 → BiRefNet) avant utilisation dans Cricut Design Space : éviter qu'une proposition masque l'objet voisin, éviter les faux nouveaux éléments au bord d'un recadrage, publier les résultats QA sans fichiers partiels. Aucun modèle IA n'est inclus dans l'archive.

## Installation sous Windows / ComfyUI

1. **Fermer ComfyUI.** Sauvegarder l'ancien dossier SmartSVG ; déplacer tous les anciens dossiers `ComfyUI-SmartSVG-Studio-*` en dehors de `ComfyUI/custom_nodes` afin d'éviter plusieurs chargements simultanés.
2. Extraire le dossier `ComfyUI-SmartSVG-Studio-V20.0` du ZIP directement dans le répertoire `custom_nodes` de l'installation utilisée.
3. **Conserver ComfyUI-RMBG** (version dont les nœuds réels `SAM2Segment`, `AILab_Florence2`, `BiRefNetRMBG` sont disponibles). L'installation de SmartSVG n'installe ni ne télécharge les poids.
4. Redémarrer ComfyUI. Charger `example_workflows/SmartSVG_Studio_V20_Diagnostic_Installation.json` et exécuter le nœud de diagnostic en premier. Vérifier que les trois noms de nœuds sont disponibles et contrôler CUDA/VRAM.
5. Utiliser `SmartSVG_Studio_V20_Express.json` pour les planches et le flux Cricut classique. Choisir le dossier global de sortie, sélectionner l'image et lancer `Queue Prompt`.
6. Pour comparer la retouche sur photo, ouvrir `SmartSVG_Studio_V20_Photo_Orchestration.json` et conserver **`raffinement_ia = diagnostic`**. Un `MASK` externe correct peut être branché sur `masques_objets`. Sans masque externe, le pipeline tente les modèles RMBG installés.

## Modes de traitement

- `desactiver` : voie Cricut historique, sans seconde passe matting.
- `diagnostic` : exécution possible du second modèle ; le masque retenu et les PNG de production sont ceux de la référence, non altérés par le matting.
- `proposition` : les variantes retenues après contrôles sont enregistrées uniquement en **QA**, pas promues automatiquement comme fichiers de découpe.
- `adopter_annotation` : demande un vrai masque annoté, aligné sur la source et sur l'ordre des objets ; l'adoption exige une amélioration IoU d'au moins **0,025**, un accord de base suffisant et tous les nouveaux contrôles anti-fuite.

## Nouveaux contrôles

- **Fuite vers un objet voisin :** le masque candidat est refusé si une fraction significative du premier objet s'étend sur une zone appartenant exclusivement à un autre masque, avec une tolérance morphologique de 2 pixels pour les bords. C'est un **garde-fou géométrique**, pas une preuve de séparation sémantique.
- **Fuite au bord intérieur de ROI :** un nouveau premier plan qui touche la bordure de la région recadrée est refusé lorsqu'il n'est pas expliqué par le masque initial. Les contours touchant réellement le bord de l'image ne sont pas confondus avec des bords internes.
- **Dossier QA transactionnel :** résultats enregistrés dans `QA_MATTING_V20/<id_unique>/` : originaux, propositions, carte d'incertitude et `rapport.json`. Le dossier est publié d'un seul renommage après production ; en cas d'échec, le répertoire provisoire est supprimé. Les fichiers `*_CRICUT_TEST.png` ne sont jamais écrits par ce module.
- **Échec du SAM2 de première passe :** en mode optionnel avec aucun masque externe, retour en **analyse seule**, IA historique désactivée afin de ne pas annoncer un détourage à partir d'un simple premier plan général.
- **Diagnostic d'installation :** vérifie sans inférence les noms des nœuds RMBG et la disponibilité CUDA/VRAM déclarée. L'absence de modèle téléchargé n'est pas nécessairement détectée : voir logs RMBG au premier lancement.

## Compatibilité et contrôle qualité

- **243 tests automatisés réussis**, dont 225 hérités V19.9 et 18 nouveaux V20 (les tests externes réels de modèles ne sont pas inclus).
- Les fichiers source des anciens moteurs Python restent identiques (empreintes SHA-256), sauf `__init__.py` réorienté vers le nouveau point d'entrée. Les anciens nœuds et workflows restent enregistrés.
- Deux exports PNG Cricut sur source et masques synthétiques : SHA-256 identique V19.9/V20.0 dans le mode diagnostic.
- Deux photographies personnelles d'essai : source originale préservée bit à bit pour RGB, **aucun masque automatique prétendu** puisque les modèles n'ont pas été lancés dans le laboratoire logiciel.
- RTX 3070 8 Go : pas de validation matérielle, pas de garantie anti-OOM ; la segmentation doit être testée sur ComfyUI local.

## Tests manuels conseillés

1. Tester `SmartSVG_Studio_V20_Diagnostic_Installation.json` et relever les nœuds disponibles.
2. Sur une photo, lancer d'abord `diagnostic` avec `max_passes_ia=1`, puis 2 seulement si mémoire suffisante.
3. Inspecter `QA_MATTING_V20/<id>/rapport.json` et comparer `OBJET_*_SOURCE.png` / `OBJET_*_PROPOSITION.png`.
4. Rejeter les candidats signalés `REFUSE_EMPIETEMENT_AUTRE_OBJET` ou `REFUSE_FUITE_BORD_ROI`. Ils n'affectent pas les PNG Cricut.
5. Importer dans Cricut Design Space et vérifier manuellement chaque contour, taille et marge avant toute découpe physique.

## Validation automatisée

Utiliser le Python associé à ComfyUI dans le dossier de l'extension :

```bash
python verify_package.py
```

Les sorties réelles de Florence-2 / SAM2 / BiRefNet, leur consommation GPU et le résultat physique Cricut ne sont pas certifiés par ces tests.
