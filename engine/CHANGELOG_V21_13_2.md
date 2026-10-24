# SmartSVG Studio V21.13.2 — Correctif de fidélité vectorielle

Base : archive ZIP V21.13.1, audit indépendant du rendu vectoriel et contrôles locaux.

## Corrections

- **Qualité du rendu SVG :** utilisation facultative de CairoSVG pour rasteriser **le SVG généré**, à sa résolution `viewBox`, au lieu de considérer OpenCV comme un rendu SVG standard. Alpha de comparaison seuillé à 128/255 pour la parité avec Inkscape. Si CairoSVG manque ou si ses bibliothèques natives ne chargent pas, estimation OpenCV conservée avec un statut **A_VERIFIER** explicite.
- **Sécurité de validation :** rejet des attributs de transformation, de style ou d'opacité non prévus, des décalages du `viewBox`, des éléments étrangers et des ressources externes. Le validateur n'accepte que le sous-ensemble de SVG généré par SmartSVG.
- **Génération de palette :** algorithme k-means déterministe avec générateur local NumPy ; aucune réinitialisation des générateurs globaux NumPy/OpenCV. Les SVG produits restent de vrais chemins éditables.
- **Diagnostics :** un nouveau nœud `SmartSVGEditableColorsV21132` affiche le score et le type de rendu effectivement utilisé, ainsi que le statut non certifié. Ancien nœud et ports conservés.
- Nouveau workflow `SmartSVG_Studio_V21_13_2_01_SVG_Fidelite.json`.
- Tests de sécurité, déterminisme, mode sans CairoSVG, compatibilité des anciens nœuds et création du SVG.

## Résultats démonstration V21.13.1 (anciens SVG, nouveau moteur d'audit)

| Exemple | Ancienne estimation OpenCV | Rendu SVG standard confirmé (CairoSVG/Inkscape) |
|---|---:|---:|
| Escargot n° 1 | 87,798 % | 83,094 % |
| Pokémon n° 1 | 80,939 % | 69,788 % |

Le nouveau moteur de palette a été testé sur ces deux sources : sa fidélité géométrique au rendu SVG standard reste du même ordre (83,34 % et 69,87 %). Ce correctif **fiabilise la mesure**, mais **ne répare pas encore automatiquement tous les détails perdus**.

## Limites

Aucun test d'import Design Space ni de découpe physique Explore 5 ; pas de certification de vectorisation fidèle pour une photo ou illustration très détaillée. CairoSVG est optionnel (peut nécessiter les bibliothèques natives Cairo sous Windows) ; en son absence le rapport ne marque pas le SVG comme prévalidé.
