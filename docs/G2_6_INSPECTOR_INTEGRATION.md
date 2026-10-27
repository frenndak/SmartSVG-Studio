# G2.6 — Intégration de l'inspecteur de masques dans la pile Express

## Objectif de ce micro-lot

Intégrer les développements des PR **#26 → #27 → #28** dans la chaîne déjà consolidée **#35 → #36**, en conservant les mécanismes de persistance G2.3/G2.4 et de reprise locale G2.8.

## Cohabitation des fonctions

- `SmartSVGChooseSubjectV21154` est un **nouveau nœud additif** (le registre historique reste inchangé) : inspection non destructive des masques, localisation des îlots suspects et sélection explicite de silhouette.
- L'interface `smartsvg_subject_inspector_v21154.js` présente les sujets et les zones. L'information de focus est échangée localement par l'événement `smartsvg:mask-focus:v1` lié à l'empreinte exacte image + masques.
- L'éditeur V21.6 accepte désormais **les deux** mécanismes : focus sur une zone signalée (mode panoramique, aucune retouche automatique) et brouillon de coups de pinceau G2.8 reconstituable après plantage. Les boutons de sauvegarde G2.3 restent présents.
- Le code G2.4 et l'API des projets G2.2 demeurent opt-in via `SMARTSVG_ENABLE_PROJECT_API`, sans modifier les IDs anciens.
- Le chargement de l'éditeur est précédé d'un contrôle de validité du focus. Toute décision de commencer une retouche et de sauvegarder reste manuelle.

## Limites de la preuve

Les nouveaux tests Python du module d'inspection dépendent d'OpenCV/Numpy et du runtime réel. Les tests Node.js dédiés à la sécurité de l'UI et au focus sont exécutés par le wrapper de CI G0. Le fonctionnement de la machine Cricut, de Design Space, de la GPU RTX 3070, et l'UX Windows restent non vérifiés.

## Risques encore ouverts

- Synchroniser les PR d'origine G1.3 et G1.4 avant tout merge final ; les intégrations #35/#36 corrigent la divergence dans des branches candidates **sans mettre à jour les branches originales**.
- Tester en navigateur réel les nombreuses interactions simultanées, notamment souris/clavier/tactile, chemin de sauvegarde et réouverture avec graphes multiples.
- Mesurer 12/24 sujets à résolution originale, performance preview, recoloriage, et conservation des modes contour-only vs Print Then Cut.
- Ne pas assimiler focus/inspection à une segmentation IA automatique ou à une validation Cricut.

**Gate** : CI G0/CPU sur HEAD synthétique, audit des changements `__init__.py` et `smartsvg_editor_v216.js`, revue indépendante et recette physique avant toute fusion.
