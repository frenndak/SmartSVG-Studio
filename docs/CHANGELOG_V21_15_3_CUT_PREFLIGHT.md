# SmartSVG Studio — correctif V21.15.3 (précontrôle statique SVG de coupe)

**Statut :** correctif candidat sur V21.15.2, non diffusé comme version certifiée. La baseline originale, son ZIP et la roadmap v3.2 restent inchangés.

## Problème vérifié

Le précontrôle V21.15.2 se contentait de dénombrer les éléments `<path>` d'un SVG de coupe. Un tracé de surface nulle (`M0 0Z`), ouvert ou masqué par du contenu XML supplémentaire pouvait ne pas être refusé alors que le résultat avait une géométrie de lame indémontrable.

## Correctif limité

- Nouveau `engine/smartsvg_governance/cut_path_preflight.py` : tokenisation bornée et vérification des fermetures ; aire strictement non nulle pour les polygones `M/L/Z`, y compris les coordonnées relatives ; refus des balises et attributs actifs/externes/transformation, chemins vides et complexité excessive.
- `engine/smartsvg_governance/artifact_qa.py` : applique ce contrôle **aux SVG réellement exportés**, plutôt qu'aux métadonnées déclarées uniquement ; signale `FICHIER_NON_VERIFIABLE` en cas d'échec et `DIMENSIONS_MM_ABSENTES` quand une largeur en mm attendue est introuvable.
- Nouveau corpus de régression `engine/tests/test_v21153_cut_preflight.py` (5 méthodes, sous-cas multiples) ; ancien fixture SVG de surface nulle remplacé par un vrai rectangle polygonal.

**Compatibilité :** aucun nœud ComfyUI, connecteur IA, signature de workflow, sortie raster, ou module UI n'a été modifié. En cas d'audit bloqué, les artefacts existants restent des brouillons ; leur découpe n'est jamais automatiquement autorisée.

## Preuves obtenues localement

- `python -m unittest tests.test_v21153_cut_preflight tests.test_v21151_image_qa tests.test_v21152 tests.test_v21132 tests.test_v2114 tests.test_v21141_color tests.test_v2110 -q` : **55 tests OK**.
- `for script in tests/*.mjs; do node "$script"; done` : **12 scripts OK**.
- La suite Python complète n'a pas terminé dans la fenêtre d'exécution disponible. **Ne pas affirmer une validation complète.** Les 876 tests consignés précédemment concernent le socle V21.15.2 avant ce correctif.

## Limites

La validation de courbes `C/Q/A` reste non exhaustive ; le retour inclut `nonpolygonal_paths_require_visual_review=true`. Ce contrôle ne reproduit pas l'interpréteur SVG de Cricut Design Space et ne mesure ni précision du détourage, ni distance minimale de lame, ni succès du matériel. Aucune inférence RTX 3070 ni découpe Explore 5 n'a été effectuée.

## Retour arrière

Restaurer uniquement `engine/smartsvg_governance/artifact_qa.py` et `engine/tests/test_v21151_image_qa.py` depuis `main` à la base du correctif, puis supprimer les deux nouveaux fichiers Python. Ne pas effacer de projets utilisateurs ou modifier l'archive source V21.15.2.

## Suite proposée

G2/G4 : remonter dans l'interface une explication exploitable par objet et un chemin d'action corrective ; puis organiser des essais d'import Design Space et des coupons de coupe sur Explore 5. La preuve physique demeure ouverte.
