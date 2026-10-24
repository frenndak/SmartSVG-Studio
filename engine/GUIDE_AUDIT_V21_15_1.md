# V21.15.1 — Diagnostiquer les sorties

1. Installer l'extension en parallèle de la sauvegarde V21.15, suivant le guide V21.15.
2. Produire une sortie comme d'habitude depuis ComfyUI.
3. Depuis le répertoire de l'extension, exécuter :

```bash
python tools/v21151_audit_exports.py "CHEMIN/VERS/RAPPORT_V21_1.json" --intent sticker_contour --output "CHEMIN/VERS/AUDIT.json"
```

Code de sortie **1** : anomalie bloquante pour l'objectif déclaré. Code **0** : aucune anomalie bloquante détectée ; revue humaine et essai Design Space restent requis.

`--intent carte_rectangle` permet une vraie carte rectangulaire voulue par l'utilisateur sans la signaler comme faux contour. Les chemins et SVG externes au dossier du projet sont refusés.

`BLOCKED` ne supprime ni ne modifie les fichiers ; ne pas les découper avant correction et revue. `REVIEW_REQUIRED` signifie **non certifié**, jamais « prêt Cricut ».

Cette livraison est un outil de diagnostic. Elle ne comprend pas les photographies ou illustrations de test.
