# SmartSVG V19.7 — Vérification de développement

**Périmètre** : extension et workflow, outils de mesure ; ne remplace pas l'évaluation de la qualité des masques IA.

- Nouveau profiler via `contextvars` : isolé par exécution, aucun contexte global qui fuit entre appels.
- Capture de la durée des vraies étapes du nœud, pas de simulation d'une inférence qui n'a pas eu lieu.
- Capture GPU best effort : si CUDA indisponible, signale `available=false`, sans inventer la VRAM ni sa consommation.
- `global_peak_allocated_bytes` a une portée historique par processus (il n'est **pas** remis à zéro par SmartSVG), et `free_device_bytes` est une valeur globale.
- `save_profile` écrit un fichier temporaire puis le renomme. L'échec de l'écriture de télémétrie n'annule pas un export de production déjà terminé.
- Le mode désactivé est neutre ; le mode activé enregistre succès ou échec et le chemin du dossier de production.
- Scénario de non-régression : le code d'export photo est réellement exécuté sur une image et son masque synthétique ; le PNG `*_CRICUT_TEST.png` obtenu correspond octet par octet à la sortie V19.6.
- Les anciens nœuds V19.6 restent présents ; un ancien workflow ne reçoit pas de profilage supplémentaire s'il ne passe pas explicitement par V19.7.

**Limitations** : tests CPU/simulations PyTorch CUDA ; pas d'inférence Florence-2/SAM2 réelle sur RTX 3070, pas de référence empirique de VRAM ou de temps des modèles externes, pas de découpe Cricut physique.

## Résultat de la dernière livraison
- **171 tests Python réussis** dans l'environnement local : 158 cas hérités de la V19.6 et 13 tests V19.7. Ce chiffre n'est pas un benchmark GPU.
- Exécution d'un export photo avec masque synthétique, comparaison de masque et suivi des trois étapes produit un rapport JSON exploitable.
- Les deux images de référence ont été analysées en mode sans segmentation automatique ; le profiler a correctement tracé l'échec de RMBG (registre ComfyUI `nodes` absent dans ce runtime), sans faire croire qu'une inférence était réussie.
- Les anciens fichiers de production ne sont pas modifiés par le profilage, qui écrit un fichier de diagnostic **à côté** du dossier de création.
- Les exécutions enregistrées sous les anciennes classes V19.6 restent accessibles dans les workflows existants.
