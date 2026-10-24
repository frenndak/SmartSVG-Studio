# Statut d'intégration au 24 octobre 2026

## Présent

- Roadmap complète et gelée V3.2, manifeste documentaire associé.
- Instructions de contributions et protections du périmètre.
- Test G0 d'admission d'archives ZIP, tests synthétiques.
- Importer d'archive candidate en `engine/`, sans autoriser la mise en production.
- Contrôle statique de contrats SVG et jeux d'exemples vectoriels originaux.
- Générateur PNG RGBA reproductible, contrôles de non-écrasement.
- Workflows privés G0 (tests) et bootstrap source (action manuelle à partir d'un asset privé).

## Non présent / non autorisé à déclarer prêt

- L'archive binaire authentique V21.15.2 n'est pas accessible depuis le dépôt actuel, malgré une référence dans la bibliothèque du projet.
- Aucun code de moteur SmartSVG V21.15.2 n'est encore importé dans `engine/`.
- Aucun manifeste interne de cette version ne peut être vérifié dans le dépôt.
- Aucun test réel ComfyUI frontend, segmentation RTX 3070, Cricut Design Space ou découpe physique n'a été effectué dans ce dépôt.
- `.automation/READY` ne doit pas être fabriqué automatiquement.

## Étapes suivantes, dans l'ordre

1. Faire contrôler le G0 par un reviewer et fusionner sa PR quand CI réussit.
2. Importer la **vraie** V21.15.2 via une release privée avec la procédure du README.
3. Vérifier les manifestes internes et garder l'historique B0 figé.
4. Mettre le moteur sous tests ComfyUI/PNG/SVG réels ; enregistrer les limites des tests GPU/Cricut.
5. Activer éventuellement l'agent automatique et sa revue croisée, après configuration explicite des coûts et des permissions.
