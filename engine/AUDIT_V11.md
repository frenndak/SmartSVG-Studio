# Audit contradictoire SmartSVG Studio V10 → V11

## Méthode

- Inspection statique de `engine_v10.py`, `engine_v9.py`, `engine_v8.py`, `engine_legacy.py`, `__init__.py` et du workflow JSON.
- 16 tests de régression du code antérieur, **relancés sur V11**.
- 7 tests adversariaux spécifiques V11.
- Exécution sur le JPG réel de 1536 × 1024 pixels comportant 12 escargots.
- Ouverture des SVG par analyse XML et contrôles morphologiques avec OpenCV ; ne remplace pas une découpe physique.

## Défauts réellement identifiés

| Niveau | Cas | V10 | V11 |
| --- | --- | --- | --- |
| Élevé | Couleur noire/invisible d'un trou transparent rebouché | RGB masqué réinjecté | Conserve la base blanche |
| Élevé | `IA forcée` indisponible ou résultat rejeté | Pouvait continuer avec heuristique | Bloque le fichier d'import |
| Élevé | Chemin SVG simplifié mais non fidèle au masque imprimé | Avertissement même si divergence importante | Simplification adaptative, blocage au-delà du seuil |
| Moyen | Traitement de 12 images par IA | Instancie potentiellement RMBG 12 fois | Réutilise 1 instance pendant l'exécution |
| Moyen | Petits fragments perdus silencieusement | Pas de taux de perte | Mesure et seuil de blocage |
| Moyen | Dimensions physiques implicites du PNG | Champ largeur uniquement dans rapport | Inclut DPI nominal + consigne de contrôle |
| Faible | Deux distance transforms identiques consécutifs | Surcoût CPU | Corrigé |
| Faible | Alertes d'IA inutilisable | Pas toujours remontées dans le QA final | Consignées explicitement |

## Résultat expérimental escargots

- 12 dessins / 12 contours distincts conservés.
- Planche de **180 × 120 mm** au réglage d'exemple, environ **217 DPI**.
- Marge environ **1,406 mm** après quantification ; écart entre stickers le plus proche environ **2,46 mm**.
- **0 changement de pixel alpha** par rapport à la V10, mais **494 pixels de couleur corrigés** dans des zones comblées, sur la comparaison V10/V11 testée.
- Écart maximal entre chemins SVG de découpe et masque raster **0,134 %** dans les résultats de test V11.

## Risques résiduels non validés

1. **GPU RMBG réel** : interface simulée, pas de test sur Windows + RTX 3070. Les choix de paramètres / les sorties peuvent changer entre les versions du plugin.
2. **Détection automatique de planches atypiques** : sans fond transparent ou grille régulière, une image peut être reconnue comme une seule illustration. Aucun modèle généraliste ne garantit la séparation parfaite.
3. **Segments détachés** : antennes ou accessoires séparés du corps peuvent conduire à un blocage (volontaire) plutôt qu'une création de pont arbitraire.
4. **Dégradés, contours translucides, ombres douces** : la conversion SVG de couleur restera moins fidèle que l'image imprimée. Le PNG reste le fichier recommandé pour Print Then Cut.
5. **RVB/gestion des couleurs** : couleurs d'impression variables selon imprimante, support et profil ICC. Contrôle papier nécessaire.
6. **Design Space** : son aperçu peut appliquer d'autres règles de dimensions, détection ou traitement des calques. L'outil de validation interne ne peut pas reproduire son rendu à 100 %.
7. **Sémantique Magic Layers** : la structure actuelle regroupe des régions de couleur et des dessins, sans comprendre véritablement les objets ou reconstituer les zones cachées.
8. **Licence illustrations / modèles** : vérifier les droits de reproduction des dessins et les licences des poids IA avant toute commercialisation.

## Conclusion de l'audit

**V10 approuvée comme base technique, mais non comme logiciel terminé.** La V11 renforce les points critiques sans casser les 12 contours existants. Elle est distribuable en **bêta expérimentale** : validation Windows/GPU et essai Cricut encore requis. Une évolution vers des calques sémantiques nécessite des modèles de segmentation orientés objets et des tests dédiés, sans possibilité de garantie automatique universelle.
