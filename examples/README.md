# SmartSVG — Jeux d'essais synthétiques (originaux)

Ces ressources ont été conçues pour la recette du futur SmartSVG. **Elles ne sont pas des fichiers validés par Cricut Design Space ni par découpe physique.** Elles sont volontairement créées sans Pokémon, marques, photographies personnelles ou autres contenus tiers.

| Exemple | Entrée / intention | Attente statique | Vérification finale non faite |
|---|---|---|---|
| `synthetic/01_sticker_simple.svg` | Sticker fleur, plusieurs couleurs | SVG avec géométrie et dimensions 80 mm | Print Then Cut exige un PNG transparent produit séparément, puis vérification Design Space |
| `synthetic/02_decoupe_coeur.svg` | Basic Cut, silhouette unique | Un chemin fermé 50 × 46 mm | Vérifier taille, mode Basic Cut et sortie réelle |
| `synthetic/03_multicouche_editable.svg` | Calques vectoriels distincts | Plusieurs formes de couleurs différentes | Import SVG éditable et calques Design Space non testés |
| `synthetic/04_passage_fin.svg` | Pont très fin entre deux formes | Doit servir à une alerte de fragilité physique | Essai réel avec matériaux et lame |
| `synthetic/05_planche_12_formes.svg` | 12 sujets séparés sur planche | 12 groupes nommés, 240 × 180 mm | Extraction, imposition, détourage de chaque sujet |
| `synthetic/06_trou_interieur.svg` | Trou intentionnel / fill-rule | Topologie des trous non assimilée à une simple silhouette pleine | Vérifier vraie découpe intérieure |

## PNG supplémentaires générés localement

Le script `tools/make_synthetic_pngs.py` génère, sans Pillow ni modèle IA :
- `sticker_alpha.png` : raster RGBA avec transparence (candidat Print Then Cut),
- `planche_12_sur_fond_blanc.png` : séparation d'objets sur fond blanc opaque,
- `masque_touche_bord.png` : silhouette partiellement coupée,
- `photo_factice_opaque.png` : dégradé opaque difficile à isoler sans masque.

Le générateur crée les fichiers dans le dossier demandé et n'écrase pas des fichiers existants. Les PNG générés n'ont aucun repère Cricut : ces repères sont exclusivement du ressort de Design Space. Les testeurs doivent conserver les sources intactes et comparer les sorties en pixels, en mm et au rendu visuel.

## Contrats et critères

1. **Sticker Print Then Cut :** PNG transparents et aplatis, inspecter dimension physique, alpha et bord. Un SVG enveloppant une image n'est pas une vraie vectorisation.
2. **SVG Basic Cut :** contrôler une silhouette de découpe, trous, chemins isolés, petites pièces, unités en mm et dimensions sur import.
3. **SVG multicouche :** vérifier les couches réellement indépendantes dans l'application destinataire ; ne pas promettre une éditabilité parfaite sans validation.
4. **Images complexes et IA :** transparence/heuristiques avant modèle, conserver la possibilité de retouche manuelle, distinguer refus honnête et résultat imprécis.
5. **Non-régression :** comparer avec les versions source connues uniquement après import authentique de V21.15.2, pas avec ces fixtures de démonstration.

## Licence des exemples

Les exemples SVG originaux et les PNG produits par `make_synthetic_pngs.py` sont placés sous **CC0-1.0** par le projet. Cela ne s'étend **pas** au code source propriétaire SmartSVG, aux archives historiques ni aux images fournies par d'autres auteurs.
