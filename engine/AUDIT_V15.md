# Contre-expertise V15

## Périmètre vérifié

1. Contrôle statique des éléments SVG (`svg`, `g`, `path`) sans images/texte/filtres.
2. Comparaison du masque de la planche PNG avec l'opacité du **rendu complet** des deux variantes SVG : le contrôle prend en compte le bord adouci du rendu. Une erreur au-delà de 4 pixels provoque un rejet (seuil de 0,02 % des pixels imprimés). Les écarts au-delà de 2 pixels sont reportés.
3. Préservation de la version compacte pour édition par couleur, ajout d'une version par région, avec sous-groupes éditables.
4. Préservation d'une seule planche imprimable, mais exports individuels facultatifs pour les utilisateurs qui souhaitent isoler un seul motif.
5. Contrôles de dimensions en mm et vérification de l'index SVG des stickers.
6. Prise en compte des erreurs d'export, des SVG corrompus, de l'absence de rendu CairoSVG et du cas « IA forcée ».
7. Publication unique du répertoire final après validations ; manifeste récursif vérifiable.

## Limites non levées

* Ne reproduit pas les fonctions de Canva Magic Layers de reconstruction des objets sémantiques ni les faces cachées.
* Le PNG est souvent visuellement plus fidèle que le SVG pour dégradés, ombres et reflets.
* Le masque IA local ne peut être déclaré fonctionnel sur la carte RTX 3070 tant qu'une exécution réelle via ComfyUI-RMBG n'est pas observée.
* L'importation puis l'aplatissement dans Cricut Design Space et la découpe physique ne sont pas automatisables depuis cet environnement.
* Le test de tolérance en pixels est un **contrôle géométrique logiciel**, non une garantie de précision physique. À 180 mm de largeur sur 1536 px, 4 px représentent environ 0,47 mm.

## Résultats

Les tests automatisés inclus sont la référence reproductible. Les mesures exactes de démonstration sont reprises dans `rapport_V15.json` du pack de démonstration. Ne pas annoncer une fidélité visuelle parfaite : elle n'est pas atteinte.
