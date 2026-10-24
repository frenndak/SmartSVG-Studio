# SmartSVG Studio V21.15.2 — planches à fond blanc et précontrôle effectif

## Fonctions livrées

- `smartsvg_quality/white_sheet_v21152.py` : segmentation déterministe CPU, 4×3 et 6×4, uniquement lorsque chaque cellule présente un fond blanc compatible, un objet dominant non rectangulaire et une géométrie bornée. Algorithme conservateur, réversible en désactivant le nouveau nœud. Pas de modèle IA requis.
- `smartsvg_quality/release_gate_v21152.py` : appelle les moteurs historiques non modifiés, puis inspecte **les PNG/SVG réellement exportés**, publie `RAPPORT_V21_15_2.json` + `CONTROLE_V21_15_2.json` et émet `BLOCKED` ou `REVIEW_REQUIRED`. Aucun label « prêt Cricut » automatique.
- `node_v21152.py` : nouvel Express recommandé `SmartSVGExpressV21152`. Identité, signatures et nœuds précédents conservés ; 6 options et entrée MASK inchangées. Le mode « IA obligatoire » conserve sa sémantique : la segmentation heuristique seule ne le satisfait pas.
- Interface : barre d'état de contrôle qualité bloquante/à vérifier, vocabulaire fond blanc vs fond noir, action corrective explicite. Fallback texte si le navigateur ComfyUI ne permet pas le widget.
- Deux workflows démonstrateurs dans `demos_v21152/` (n'augmentent pas le catalogue historique de 186 workflows).

## Tests d'intégration

- 12 escargots source projet et 12 escargots corpus : 12 objets chacun, aucune géométrie presque rectangulaire dans l'audit automatisé, `REVIEW_REQUIRED` (pas validation physique).
- 24 Pokémon fond noir : segmentation fond blanc refusée, 24 objets via branche historique, `REVIEW_REQUIRED` avec avertissements d'interpolation et fragments alpha.
- Cas négatifs : image blanche, carte rectangulaire, image partiellement vide, fond noir, classe de grille invalide, valeurs invalides ; refus, sans fausse silhouette.
- 85 tests Python ciblés et 10 tests JS ciblés OK après mise à jour des attentes de la V21.15.2 (98 anciens + 1 nouveau nœud ; seuls `__init__.py` et deux fichiers frontend d'origine B0 sont modifiés).

## Réserves et frontière fonctionnelle

- Reconnaissance d'un **objet géométrique dominant dans une grille régulière**, pas reconnaissance sémantique ni segmentation générale des photos, ailes/cheveux, textes, etc.
- Une feuille doit être contrôlée objet par objet avant Design Space ; une image non reconnue peut toujours produire un **brouillon** via le moteur historique, mais il est signalé `BLOCKED`.
- Ni Design Space, ni Explore 5, ni performance RTX 3070 8 Go testés ici.
- Les 9 masques humains G0.3 manquent toujours ; ne pas clore cette étape documentaire.
