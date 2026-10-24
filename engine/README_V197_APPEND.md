## Nouveauté V19.7 — Profilage réel du traitement

Deux nouveaux nœuds **SmartSVGStudioV197Express** et **SmartSVGStudioV197Expert** reprennent **exactement** les paramètres de production de V19.6, avec une option supplémentaire `profil_performances` (par défaut `activer`). Les anciens workflows et identifiants de nœuds sont conservés. Les fichiers PNG, masques et variantes Cricut sont générés par le même moteur que V19.6.

Pour l'utiliser :
1. Sauvegarder et déplacer toute ancienne version SmartSVG hors de `custom_nodes`, puis extraire le dossier complet `ComfyUI-SmartSVG-Studio-V19.7` et redémarrer ComfyUI.
2. Ouvrir `example_workflows/SmartSVG_Studio_V19_7_Express.json` (ou Expert).
3. Charger une image ; vérifier le chemin global `dossier_sortie`, puis laisser `profil_performances=activer`.
4. Pour comparer les modèles **réellement intégrés**, faire les essais avec `type_fichier=photo` et `segmentation_objets=auto` ou `forcer`. Il faut que Florence-2 et SAM2 fonctionnent réellement dans ComfyUI-RMBG. Exécuter les modèles **un par un** sur la RTX 3070 8 Go.
5. Après chaque passage, ouvrir le fichier `PERFORMANCES_V19_7_xxx.json`, créé **à côté** du dossier projet dans la destination globale. On y trouve les étapes internes effectuées, la durée, les allocations CUDA PyTorch avant/après et la mémoire libre signalée par CUDA.

### Différences entre les mesures

- `secondes_ecoulees` : temps **mural** entre deux synchronisations CUDA, incluant chargement des poids, CPU, GPU et transferts. Ce n'est pas un temps de noyaux GPU ni un benchmark indépendant.
- `global_peak_allocated_bytes` : **pic global courant du processus PyTorch** : ce n'est PAS un pic propre à l'étape. Le profiler n'appelle pas `torch.cuda.reset_peak_memory_stats()` pour ne pas perturber les autres nœuds.
- `variation_allocation_cuda_bytes` : allocation PyTorch courante à la fin moins au début de l'étape, pas une estimation fiable du pic transitoire ni de la VRAM totale utilisée par les autres bibliothèques.
- `free_device_bytes` : mémoire libre signalée par CUDA pour le périphérique, susceptible de changer pendant l'exécution d'autres tâches.
- `secondes_amorties_par_masque` : pour SAM2 uniquement si le nombre de masques acceptés est connu, durée totale de cette étape divisée par le nombre de masques ; ne signifie pas qu'un masque particulier a été calculé dans ce temps.
- `mesure_gpu_reelle_observee` indique seulement que CUDA était accessible pendant les mesures ; ne prouve **ni une bonne segmentation**, ni que tous les calculs ont été exécutés sur GPU.

**Limites :** les modèles RMBG branchés directement **en amont** sur les entrées `MASK` sont déjà exécutés lorsque SmartSVG démarre. Leurs durées d'inférence ne peuvent donc pas être mesurées a posteriori par ce nœud. Pour eux, utiliser le profiling de ComfyUI ou instrumenter leurs nœuds séparément. Le profil V19.7 mesure les appels internes faits par SmartSVG ; lorsque des masques externes sont fournis, il mesure surtout la comparaison et l'export.

Le fichier de performances est **indépendant du manifeste du projet** pour éviter toute modification après validation des exports. En cas d'échec du traitement, un rapport de performances est conservé lorsque le dossier est accessible. Aucune valeur de performance sur la RTX 3070 n'a été simulée ou certifiée.
