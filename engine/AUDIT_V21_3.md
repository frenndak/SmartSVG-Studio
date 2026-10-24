# Audit V21.3 — plan de validation

| Domaine | Résultat constaté | Limite explicite |
|---|---|---|
| Détections multiples même catégorie | Acceptées et dédupliquées par IoU de boîte | Dépendent du modèle Florence-2 ou de rectangles manuels |
| Segmentation par objet | SAM2 reçoit un recadrage local par boîte | Peut prendre aussi une partie d'un sujet voisin |
| Géométrie / sécurité | Boîtes bornées, coordonnées finies, masques de même taille, sous-budget mémoire | Les vérifications sont heuristiques, pas sémantiques |
| Chevauchement/doublon | Refus du masque quasi identique ; avertissement sur pixels partagés | Ne tranche pas la profondeur des objets |
| Fonctionnement Express | Cinq contrôles, MASK externe connecté | Un nœud de guidage supplémentaire sur scènes difficiles |
| Exports PNG/SVG | Moteur inchangé de V21.2 | Réglages finaux Cricut à confirmer dans Design Space |
| GPU 8 Go | Garde-fou de mémoire CUDA avant inférence | Seuil 3 Gio non certifié ; risque OOM résiduel |
| Pokémon | 24 sorties réexécutées sur source réelle | Résolution native des petites images limitée |
| Renards / Courage / Canard | Guides manuels superposés sur les images réelles | Aucune inférence des poids sur les images réelles durant l'audit |

Contre-expertise ultérieure recommandée à partir des **vrais masques** et journaux de performances de l'installation locale.
