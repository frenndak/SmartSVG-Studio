# SmartSVG V19.0-alpha — Rapport de développement et contre-expertise

**Date :** 22 octobre 2026. **Statut :** première branche fonctionnelle d'extraction photographique, **pas encore moteur de reconnaissance IA multi-objets entièrement automatique**.

## Fonctions développées et testées

- Routage `auto` vers la branche `photo` des grandes scènes opaques non encadrées de blanc, et `stickers` vers le moteur V18.1 (les 12 escargots restent sur sa chaîne de découpe).
- Branche photo indépendante des anciens moteurs SVG : les scènes photographiques ne déclenchent plus la vectorisation de l'image entière.
- Entrée de masques ComfyUI alignés **dans le repère source** ; export PNG RGBA recadré par sujet et masque original pleine résolution.
- PNG blanc de bordure pour essai Cricut par sujet, métadonnées de dimensions et sauvegarde de l'image source.
- Dossier unique, aperçu annoté, statut honnête, origine de chaque masque, chevauchement et contrôle SHA-256.
- Détourage global RMBG facultatif en mode auto via le nœud déjà présent dans l'environnement ComfyUI ; cette sortie n'est **pas** une séparation sémantique. En son absence, aucune image détourée n'est fabriquée.
- Boîtes JSON explicites pour assister une revue ou guider GrabCut sur petites images, avec budget CPU strict (300 000 pixels). Les boîtes de grands exemples restent uniquement des annotations sans masquage artificiel.

## Tests

- **61 tests automatisés réussis** dans l'environnement de développement (50 hérités + 11 nouveaux).
- Les trois images sources sont correctement routées : escargots → stickers, illustration cadeau → photo, photo du personnage et des chopes → photo.
- Tests de masques mal dimensionnés, NaN, scores ou boîtes aberrants, masques chevauchants, erreur RMBG forcée, transparence source, conservation exacte des pixels des calques RGBA.
- Les deux images complexes ont produit des **rapports et des aperçus de zones annotées** en mode `analyse_seule`, sans masque IA : aucune segmentation n'est déclarée réussie.

## Limites connues

- Florence-2/SAM2 sont des modèles externes **non exécutés ici**, faute d'environnement ComfyUI CUDA avec leurs poids ; V19 **consomme** leurs masques si l'utilisateur les connecte.
- Sans masque externe, RMBG peut tenter un détourage de premier plan, mais ne sépare pas indépendamment femme/cadeau/chopes. Les noms fournis dans les boîtes ne sont pas des prédictions IA.
- La transparence très fine (cheveux, verre) dépend de la qualité du masque IA fourni ; aucun filtre magique ni reconstruction des éléments cachés.
- GrabCut à partir de rectangles est heuristique, expérimentale et refusée sur les grandes scènes pour éviter les longues exécutions CPU.
- Le routage auto est une heuristique de bord. `type_fichier=photo` ou `stickers` permet de le corriger manuellement.
- Aucune validation matérielle sur la RTX 3070 de l'utilisateur, aucune importation/print/cut physiquement vérifiée dans Cricut Design Space.

## Prochaine validation V19.1

Dans ComfyUI Windows : inspection de `Florence2 Segmentation`/`SAM2Segment` et de leurs types de sorties, pipeline automatiquement connecté, alignement/format multi-masques, mesure CUDA/VRAM sur 8 Go, détourage des trois scènes avec annotations de vérité terrain (IoU et respect des pixels source), puis aperçu réel de Print Then Cut sur l'Explore 5.
