# SmartSVG V21.10.3 — Audit global correctif

- Reprise directe de l'archive V21.10.2, extraction isolée, aucune réécriture des moteurs d'export.
- **HD relançable** : réutilisation d'un dérivé uniquement si empreintes SHA-256 de la source et du PNG HD, densité, taille et preuve latérale concordent. Sinon, aucun écrasement.
- **Nouvelle provenance** `sujet_NNN_HD.provenance.json` ajoutée aux PNG HD nouvellement produits. Les anciens fichiers HD dépourvus de preuve ne sont pas considérés comme réutilisables.
- **Échec d'écriture de provenance** : suppression du dérivé incomplet créé par l'exécution en cours, sans suppression d'un fichier utilisateur préexistant.
- **Transparence QA** : le diagnostic de l'éditeur utilise une largeur hypothétique de 40 mm ; elle est désormais explicitement signalée dans le rapport et à l'écran, plutôt que présentée comme la largeur réelle d'Express.
- **Vérificateur indépendant** : suites Python isolées, contrôle du manifeste et des workflows, tests frontend JavaScript et cinq nouveaux cas de non-régression.
- Les cinq réglages Express et les trois sorties historiques sont conservés. Les masques, PNG/SVG et contours de découpe de fabrication ne changent pas.

## Limites non levées

- Pas de démonstration réelle du chargement frontend ComfyUI / Nodes 2.0.
- Le détourage IA pour les images opaques requiert encore des masques fournis ou un workflow de segmentation distinct.
- L'inspecteur ne reçoit pas automatiquement la taille physique Express ; il ne peut donc certifier les seuils millimétriques.
- Aucun test d'import réel ni de découpe physique Cricut Explore 5.
- Le PNG Print Then Cut est aplati ; un SVG multicalque entièrement éditable est une autre fonctionnalité.
