# SmartSVG V21.12.1 — Modifications

- Routage lecture seule : classer fonds noirs/blancs uniformes, alpha possible et scènes opaques complexes. **Aucune reconnaissance de texte ni exécution IA dans ce diagnostic.**
- Nouvelle voie rapide : extraire les masques de 24 personnages séparés sur fond noir uniforme, en refusant les photos et fonds douteux.
- Détection des composants isolés oubliés (avertissement explicite) et garde-fous de taille, mémoire, quasi-rectangles et îlots hérités.
- Contrôle qualité géométrique : statistiques par masque, rapports prudents, aucune certification sémantique ou Cricut.
- Nouveaux nœuds `SmartSVGRoutingV21121`, `SmartSVGAutoMasksV21121`, `SmartSVGAutoExpressV21121`, cinq workflows V21.12.1.
- Anciennes classes, ports et moteurs PNG/SVG inchangés. Les masques externes transmis à la V21.12.1 bénéficient aussi du diagnostic géométrique.
- Tests Python d'intégration, rapport indépendant sur les neuf images fournies.
