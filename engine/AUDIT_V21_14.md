# Contre-expertise de développement V21.14

**Base :** V21.13.2. **Portée :** SVG multicouche expérimental, PAS le moteur historique d'export Cricut.

## Preuves locales

Les mesures ont été recalculées depuis la planche des 12 escargots (`1000077534.jpg`) et celle des 24 Pokémon sur fond noir (`1000077309.png`). Les masques de test proviennent de leurs détecteurs locaux respectifs. Même largeur physique (40 mm), même palette de 8 couleurs et même résolution de travail.

- Escargot : IoU silhouette sur rendu SVG standard passe de **0,83340 à 0,98709**, chemins **81 → 82**. Erreur RGB sur zone de recouvrement **11,42 → 19,17**.
- Pokémon : IoU **0,69871 → 0,98271**, chemins **95 → 96**. Erreur RGB **7,06 → 12,81**.
- Beaucoup d'anneaux sont encore fins à taille réelle. Aucun des SVG n'est garanti découpable ; leurs chemins peuvent représenter des opérations de coupe supplémentaires dans Cricut Design Space.

## Architecture et sécurité

1. Les anciens modules `layers_v2113.py`, `qa_v21131.py`, palette et export PNG/SVG historiques sont **inchangés** ; un nouveau nœud V21.14 leur ajoute une couche de fond et un diagnostic.
2. Aucune dépendance additionnelle obligatoire ; CairoSVG reste optionnel et son absence est signalée. Aucune image externe embarquée dans le SVG.
3. Le masque du sujet est validé par le moteur original ; les dimensions de travail, la taille du SVG, le nombre de chemins et les points restent limités. Le nouveau SVG passe le contrôle de dialecte avant tout rendu.
4. La fabrication n'est déclenchée qu'après succès des validations. Les fichiers antérieurs ne sont pas écrasés.
5. Les anciens IDs et workflows restent accessibles. La nouvelle version n'a pas été essayée dans le frontend ComfyUI réel ni avec ta Cricut Explore 5.

## Prochains chantiers

- P0 : améliorer la **finesse des couleurs** en récupérant les petites zones manquantes, sans créer des milliers de micro-chemins.
- P0 : produire un diagnostic de micro-découpes plus interprétable (fusion / exclusion de petits îlots), et clarifier ce qui est découpable ou simplement éditable.
- P1 : permettre l'édition et la fusion des calques depuis l'interface avec historique des modifications.
- P1 : mesurer mémoire, GPU et comportement réel de ComfyUI-RMBG sur RTX 3070 8 Go.
- P2 : import et découpe réelle dans Design Space.

**Verdict :** amélioration mesurée de la couverture de silhouette, à garder comme mode **expérimental**, non comme conversion fidèle garantie de tous les dessins.
