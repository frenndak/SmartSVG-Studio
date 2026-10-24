# SmartSVG Studio V21.14.1 — Évolutions

- Nouveau module `smartsvg_vector/color_repair_v21141.py` : récupération déterministe des grandes zones de couleur absentes, avec un maximum de 10 groupes et 12 chemins ajoutés.
- Chaque zone récupérée reçoit une couleur moyenne calculée directement sur les pixels de l'image de référence ; aucun bitmap embarqué dans le SVG.
- Réutilisation du SVG antérieur issu de V21.14 sans refaire une seconde quantification k-means.
- Rejet des corrections qui réduisent le recouvrement de silhouette ou aggravent le rendu colorimétrique.
- Ajout d'une mesure d'erreur RVB sur **tous les pixels du sujet**, qui pénalise les régions entièrement absentes.
- Nouveau nœud `SmartSVGEditableColorsV21141` avec mêmes entrées/sorties que le nœud V21.14 ; tous les anciens IDs conservés.
- Un workflow d'exemple et des tests unitaires/d'intégrité dédiés ; les modules PNG Print Then Cut, SVG de contour et anciens moteurs restent identiques.

## Comparaison réelle (8 couleurs, 40 mm, rendus SVG standard)

| Exemple | IoU V21.14 | IoU V21.14.1 | Erreur couleur sur tout le sujet V21.14 | V21.14.1 | Formes supplémentaires |
|---|---:|---:|---:|---:|---:|
| Escargot | 98,71 % | 98,84 % | 19,85 | 19,22 | +10 |
| Pokémon | 98,27 % | 98,71 % | 15,29 | 14,94 | +7 |

Les progrès colorimétriques restent modestes ; une reconstruction multiforme précise des petits détails est un chantier futur. Aucun de ces scores ne constitue une certification Cricut.
