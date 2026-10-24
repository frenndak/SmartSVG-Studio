# SmartSVG Studio V21.10.2 — Journal des corrections

- Analyse rectangle alpha plein/opaque, y compris rectangle entouré de transparence ; avertissement « coupe rectangulaire » plutôt que fausse silhouette détourée.
- Protection de `LIRE_AVANT_IMPORT.txt` et `RAPPORT_IMPORT_CRICUT_V21_8.json` contre un écrasement silencieux ; création exclusive et refus en cas de divergence.
- Remontée du statut QA dans le message Express.
- Retouches non sauvegardées mémorisées pour le même masque lorsqu'une exécution ComfyUI ferme le panneau ; pas de réapplication sur une source différente.
- Correction de l'assertion héritée qui qualifiait un rectangle de silhouette.
- Nouveaux tests unitaires de topologie, non-écrasement et relance ; tous les moteurs historiques restent inchangés.
- Nouveau vérificateur avec `--suite N` pour éviter les blocages intermittents du lanceur monolithique.
