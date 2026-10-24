# SmartSVG V21.3.2 — interface et structure

## Démarrage en trois actions
1. Fermer ComfyUI. Retirer de `custom_nodes` les autres dossiers SmartSVG (sauvegarde hors de ce répertoire). Installer exclusivement `ComfyUI-SmartSVG-Studio-V21.3.2`.
2. Redémarrer ComfyUI et ouvrir `example_workflows/SmartSVG_Studio_V21_3_2_00_Diagnostic.json`. Ce nœud examine les interfaces RMBG et la mémoire GPU, **sans télécharger de poids, sans lancer Florence-2/SAM2**.
3. Ouvrir `..._01_Express_Simple.json` pour l'usage quotidien ou `..._02_Pokemon_24.json` pour la planche 6 x 4.

### Quel nœud choisir ?

- `00 - SmartSVG VERIFIER` : état des nœuds RMBG / CUDA et pistes de dépannage ; sans entrée.
- `01 - SmartSVG EXPRESS` : cinq options après l'image : dossier de sortie, projet, taille en mm, résolution et politique IA.
- `02 - SmartSVG GUIDAGE IA` : Florence-2 puis SAM2 par région. L'entrée JSON concerne exclusivement les boîtes manuelles, exprimées en pixels de l'image **non recadrée**.
- Les anciens nœuds restent enregistrés, identifiés `Ancien · ...` : ils assurent l'ouverture des anciens workflows, mais ne sont pas recommandés pour débuter.

### Nuances importantes

`IA = Desactivee` désactive seulement l'inférence interne du nœud Express ; un masque déjà reçu par son entrée facultative est **toujours exploité**. Dans les workflows de segmentation guidée, cette combinaison est volontaire. Un contour obtenu reste **à vérifier** pour Cricut. Le diagnostic de démarrage ne prouve ni présence physique des poids des modèles, ni exactitude de leurs détourages. Les dimensions dans Design Space doivent être contrôlées.

### Correctif SVG

Le précontrôle de largeur SVG lit maintenant le véritable élément `<svg>` via un parseur XML : les fausses balises dans les commentaires ne peuvent plus modifier le résultat ; les DTD/entities sont rejetées. C'est une correction du module `controle_export_v212.py` (le reste des moteurs historiques est conservé). Une erreur de SVG stoppe la publication du dossier incomplet.

### Vérification

Dans l'environnement Python de ComfyUI : `python verify_package_v2132.py --integrity-only` pour le contenu ; puis `python verify_package_v2132.py --suite 1`, `--suite 2` et `--suite 3` pour les 577 tests indépendants.

**Limites** : pas d'exécution réelle Florence-2/SAM2 sur RTX 3070 dans cette livraison ; pas de découpe réelle Cricut certifiée ; pas de nouvelle vectorisation sémantique par couleur. Les améliorations V21.3.2 touchent l'ergonomie, la traçabilité et la validation SVG, pas la précision des masques.
