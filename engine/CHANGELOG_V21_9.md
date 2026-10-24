# SmartSVG Studio V21.9 — Modifications

**Livraison du 24 octobre 2026** — extension de la V21.8, moteurs de production inchangés.

## Ajouts

- Nœud `SmartSVGNativeInspectorV219` : contrôle de masques *en lecture seule*, sortie `MASK`, `IMAGE`, JSON, associé à une interface modale dédiée.
- Publication d'aperçus PNG à résolution **native** de la source et des masques (sans interpolation préalable à 760 px).
- Fenêtre d'inspection : zoom 100 % réel, zoom jusqu'à 1600 %, déplacement, lecture de coordonnées sources et sélection d'un masque individuel.
- Navigation vers des points localisés : îlots parasites, trous intérieurs, bords touchés, chevauchements et passages étroits possibles.
- Politique d'espace disque : 64 Mo par session de copies d'aperçu, 8 sessions et 192 Mo maximum, expiration 48 h lors de la publication suivante.
- 3 nouveaux workflows chaînant préparation / retouche / QA / inspection native / Express V21.8.

## Préservé

- Format des retouches V21.6, ancienne interface de retouche, cinq réglages Express, sorties historiques PNG/SVG et dossier d'import `00_IMPORTER_DANS_CRICUT`.
- Compatibilité des anciens workflows grâce au maintien des IDs et des fichiers précédents.

## Vérifications

- Nouvelles vérifications Python et JavaScript, incluant comparaisons de dimensions et conservation de masques inchangés.
- Tests anciens exécutés en suites séparées pour éviter le blocage intermittent lors d'une suite monolithique.
- Pas d'accès au frontend ComfyUI réel, pas de segmentation IA validée sur GPU RTX 3070, ni de découpe physique Cricut Explore 5 pendant ce développement.
