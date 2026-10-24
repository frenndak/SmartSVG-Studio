# SmartSVG Studio V21.3.1 — Correctif audité

**Objectif :** conservation de toutes les sorties PNG/SVG historiques et renforcement du guidage par instance (renards, Courage, canard). Cette version conserve **les 5 choix Express**. Le nœud Expert guidé conserve ses 5 entrées.

## Installer sous Windows

1. Fermer ComfyUI. Déplacer les anciens dossiers `ComfyUI-SmartSVG-Studio-*` hors de `custom_nodes` (ne pas installer deux versions simultanément).
2. Extraire `ComfyUI-SmartSVG-Studio-V21.3.1` dans `custom_nodes`.
3. Conserver ComfyUI-RMBG et ses dépendances; redémarrer ComfyUI.
4. Charger `example_workflows/SmartSVG_Studio_V21_3_1_04_Renards_Manuel.json` pour le guidage des trois renards, ou `..._03_Trois_Renards.json` pour l'essai automatique.
5. Pour le mode Express simple et la planche Pokémon, utiliser `..._01_Express_Simple.json` et `..._02_Pokemon_24.json`. Choisir la taille finale dans Design Space après import.
6. Lire `diagnostic_instances`: tout masque est une proposition et non une validation de découpe. Les recadrages ne sont pas des détourage PNG.

## Ce qui change

- Traçabilité : les détecteurs de test injectés ne sont plus annoncés comme une véritable exécution Florence-2.
- Les catégories des boîtes manuelles acceptent `renard`, `chien`, `canard`, `personne`, `chat`, `oiseau` et leurs variantes pluriel. Le prompt interne reste canonique pour SAM2.
- Les chevauchements entre masques sont notifiés sur **chaque** instance concernée.
- Empiètement sur la zone exclusivement couverte par une autre boîte : avertissement dédié, jamais effacement automatique des pixels.
- Arrêt explicite du lot en cas d'erreur CUDA « out of memory » (pas de lot partiel trompeur).
- Calcul local des croisements évitant deux cartes pleine résolution supplémentaires par instance.
- Le logiciel distingue toujours la provenance des masques et ne convertit pas une boîte en silhouette de découpe.

## Limitations encore ouvertes

- Aucune inférence des vrais poids Florence-2 / SAM2 et aucun essai sur RTX 3070 n'ont été réalisés pendant cette contre-expertise.
- Aucun algorithme géométrique ne garantit que la fourrure, les mains, les accessoires et les sujets qui se touchent sont correctement séparés.
- Une extraction synthétique réussie, ou la cohérence PNG/SVG, ne certifie pas le résultat « Imprimer puis découper » sur la Cricut.
- La V21.3 ancienne est conservée par compatibilité; les nouveaux workflows sélectionnent explicitement les **nœuds V21.3.1 corrigés**.
- Seul `verify_package_v2131.py` valide l'installation corrigée (les vérificateurs antérieurs sont destinés aux archives originales de leur version).

## Vérification autonome

Dans le Python de ComfyUI, exécuter : `python verify_package_v2131.py`.
Pour contrôler uniquement fichiers/nœuds/workflows : `python verify_package_v2131.py --integrity-only`.

**Recommandation UX :** un workflow Express pour l'utilisation quotidienne; les boîtes guidées restent facultatives et réservées aux cas où Florence-2 détecte mal plusieurs sujets semblables.
