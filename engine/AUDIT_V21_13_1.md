# Contre-expertise V21.13.1 — Qualité des SVG et sélection des sujets

**Base :** ZIP V21.13 validé, extrait dans un répertoire de travail isolé. **Périmètre :** fonctionnalités additionnelles, non destructives. Pas de certification matérielle.

## Défaut mesuré et raison de la correction

Le moteur multicouche V21.13 fournissait un aperçu **quantifié** (palette) qui n'était pas un rendu des véritables chemins SVG. De nombreux petits éléments et contours pouvaient être omis sans être visibles dans l'aperçu. V21.13.1 apporte un comparateur fondé sur les `path` réellement écrits, avec reporting de l'erreur et des zones fines.

## Résultats sur des sources réelles

| Image / sujet n°1 | Masques sélectionnables | Recouvrement silhouette SVG reconstruit | Erreur couleur moyenne sur les pixels recouvrants | Conclusion |
|---|---:|---:|---:|---|
| Escargots, n°1 | 12 | **87,798 %** | 11,62 sur 255 | SVG éditable mais détails manquants : correction requise |
| Pokémon fond noir, n°1 | 24 | **80,939 %** | 7,02 sur 255 | SVG éditable mais détails manquants : correction requise |

Ces mesures sont calculées sur la résolution interne de chaque SVG et sur la silhouette d'origine, par **reconstruction OpenCV** des chemins. Elles ne sont pas équivalentes à la fidélité d'un rendu SVG antialiasé dans Inkscape, et ne disent rien sur une découpe réelle. La fonctionnalité sert **à détecter des pertes**, pas à prouver une perfection.

## Garde-fous

- Rejet des commandes SVG autres que M/L/Z, des balises inconnues, et des SVG contenant DOCTYPE/ENTITY ; aucune ressource externe n'est chargée.
- Budget de 600 000 pixels, 1200 formes et 110 000 points ; validation de la géométrie et de la correspondance image/masque.
- Sélection sans muter les masques. Les vignettes sont compositées en mémoire, plafonnées, et aucun clic n'entraîne d'export.
- Anciens nœuds conservés : exports Cricut historiques et API SVG V21.13 non modifiés.
- Attention : les filtres de finesse (0,9 mm à la largeur déclarée) sont des **indicateurs conservateurs** et non des simulations de l'outil de coupe.

## À améliorer en V21.13.2/V21.14

1. Améliorer la fidélité vectorielle là où les chemins de couleur perdent des détails, sans masquer ces pertes par l'intégration d'un PNG.
2. Ajouter une simplification adaptative contrôlée de contours à la bonne échelle, et un comparatif de rendu SVG standard (Inkscape/Chrome) lorsqu'il est disponible.
3. Associer davantage de fragments détachés au bon sujet avec validation visuelle ; ne jamais faire de regroupement silencieux.
4. Tester les vraies interactions du panneau sur ton ComfyUI et les exports Print Then Cut dans Design Space/Explore 5.
