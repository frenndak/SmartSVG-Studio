# SmartSVG Studio V21.12 — Changelog

- Ajout d'un orchestrateur de segmentation IA (`smartsvg_ai/provider_v2112.py`) : détection à lecture seule des signatures des nœuds ComfyUI-RMBG 3.3.0 `BiRefNetRMBG`, `RMBG` et `SAM2Segment` ; aucun chargement de modèle pendant l'autodiagnostic.
- Inférence conditionnelle : priorité au détourage sans IA lorsque la silhouette est clairement détectée ; sinon BiRefNet léger, RMBG-2.0 puis SAM2 tiny / GroundingDINO sur trois prompts génériques.
- Validation stricte : dimensions H/W, valeurs finies 0..1, masque non rectangulaire, îlots, absence de faux résultat ; arrêt lors d'une erreur de VRAM au lieu d'enchaîner d'autres modèles.
- Les paramètres optionnels sont passés **seulement s'ils existent dans `INPUT_TYPES`** (dont `unload_model=True` pour libérer la mémoire si pris en charge).
- Nouveaux nœuds : `SmartSVGAutoMasksV2112`, `SmartSVGAutoExpressV2112` et `SmartSVGReadinessV2112` ; aucun nœud historique supprimé.
- 4 workflows V21.12 et nouveaux tests de contrats/adversariaux, sans changement des moteurs PNG/SVG ni du dossier Cricut.
- Les modèles et leurs poids restent fournis par ComfyUI-RMBG ; **aucune inférence GPU réelle, aucune validation de Design Space ou découpe physique** dans cet environnement.
