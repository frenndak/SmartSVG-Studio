# SmartSVG Studio V20.6 — HD et planches multi-stickers

**Nouvelle fonctionnalité additive :** le nœud `SmartSVGSimpleV206` complète la V20.5. Les moteurs Line Art, SVG, photo, Florence-2/SAM2, QA et les anciens workflows sont conservés.

## Installation

1. Sauvegarder puis retirer l'ancien dossier SmartSVG de `ComfyUI/custom_nodes` (éviter deux versions chargées simultanément).
2. Placer le dossier `ComfyUI-SmartSVG-Studio-V20.6` dans `ComfyUI/custom_nodes`, relancer ComfyUI.
3. Charger `example_workflows/SmartSVG_Studio_V20_6_Auto.json` ou un des cinq workflows par type d'image.
4. Dans `LoadImage`, sélectionner le PNG/JPG. Dans le nœud SmartSVG Simple, vérifier le dossier de sortie et la **largeur physique voulue**.
5. Exécuter le workflow et ouvrir le dossier affiché dans le rapport JSON.

## Interface simple — seulement six réglages, plus l'entrée image

- `dossier_sortie` : chemin Windows (ou vide pour dossier de sortie ComfyUI).
- `profil` : `auto`, `affiche`, `logo_cartoon`, `planche_multi`, `capture_produit`, `scene_decorative`.
- `operation` : `sticker_contour` ou `carte_rectangle`.
- `largeur_mm` : largeur **de chaque sticker (sans marge blanche)**, ou de la carte si image unique.
- `qualite_ppp` : `300` (conseillé) ou `450` (fichier plus lourd, **pas de nouveaux détails**).
- `grille_multi` : `6x4` (24 personnages), `4x3`, `3x3`, `auto` (estimation actuelle 6x4 et avertissement).

## Fichiers livrés

### Profil multi-stickers

- `INDIVIDUELS/01...24_..._CRICUT.png` : PNG de chaque personnage sur fond transparent, avec un **seul îlot** de découpe (bord blanc de 1,2 mm).
- `INDIVIDUELS/XX_CONTOUR_SEUL.svg` : contour vectoriel en millimètres, un chemin par objet. **Ne pas importer PNG et SVG comme deux découpes superposées sans configurer leurs opérations.**
- `PLANCHE_CRICUT_01_A_VERIFIER.png` et `PLANCHE_CRICUT_02_A_VERIFIER.png` : planches de 12 personnages, à dimensions demandées, sur fond transparent. 12 îlots/planche ont été mesurés pour la planche de référence.
- `APERÇU_24_PERSONNAGES.png` : aperçu de contrôle seulement, **pas une planche pour Cricut**.
- `RAPPORT_V20_6.json` : tailles, pixels source, résolutions, nombre d'îlots et alertes.

Le moteur regroupe des composantes entières dans les cases de la grille pour éviter de couper les flammes et les feuilles qui dépassent d'une case. **Les 24 formes sont reconnues grâce au fond noir simple et à une disposition régulière, pas par compréhension sémantique de Pokémon**. Dans les cas où des personnages se touchent, sont superposés ou sur un fond complexe, il faut utiliser des masques IA.

### Profils illustration, affiche, scène décorative et capture

- PNG HD complet + SVG **de cadre**. Le logiciel ne prétend pas détourer automatiquement les personnages d'une affiche complexe ni supprimer le décor d'une photographie.
- `capture_produit` : enlève la majeure partie des bandes d'interface du téléphone si une photo centrale est détectable. La sélection du sujet jaune exige encore un masque IA pour obtenir une véritable silhouette détourée.
- `logo_cartoon` : fichier HD avec cadre imprimable. L'isolement individuel des lettres ou du chien reste une évolution future.
- Une image RGBA préalablement détourée est préservée comme forme utile en mode `sticker_contour`.

## Qualité et dimensions

La cible 300 ppp signifie `px = largeur_mm × 300 / 25,4`. Le moteur **ne réduit pas** une source déjà plus précise. Si le fichier est agrandi par interpolation Lanczos, le rapport fournit :
- `densite_export_cible_ppp` : résolution cible de stockage ;
- `densite_native_estimee_ppp` : résolution native du sujet à la largeur choisie ;
- `facteur_interpolation` : agrandissement numérique ;
- `AGRANDISSEMENT_INTERPOLATION_NE_CREE_PAS_DE_DETAIL` si >1,35×.

**Important Cricut :** Design Space peut ignorer la métadonnée DPI d'un PNG. Contrôler/régler la **largeur réelle en mm** dans Design Space. Ne pas confondre un SVG de découpe (vectoriel) avec le dessin imprimé PNG (pixels). Une grande image PNG ne devient pas éditable couleur par couleur en la mettant dans un SVG.

Les planches générées sont des **candidates** Print Then Cut : la zone utile dépend de la machine, du format A4/Letter et des marges de capteur. Vérifier la zone dans Design Space ; les fichiers ne comportent pas les marques des capteurs Cricut, ajoutées par Design Space pendant l'impression. Ne pas imprimer ces planches en « Ajuster à la page ».

## Limites testées

- 431 tests automatisés (406 hérités + 24 nouveaux).
- Essais réels sur cinq images communiquées : 24 personnages séparés sur le cas Pokémon, 2 planches de 12 avec 12 îlots chacune ; quatre autres profils en découpe de cadre.
- Aucun essai physique sur Cricut Explore 5 ni inférence Florence-2/SAM2 sur GPU dans cet environnement.
- Les petits éléments qui se détachent sont **rassemblés par enveloppe convexe**, indiquée dans le rapport : utile pour obtenir une seule découpe, mais la forme peut être moins fidèle aux concavités.

## Continuité

V20.6 ne remplace pas les moteurs historiques. Après les profils HD et multi-stickers, la suite du projet est : isolation sémantique des personnages/objets sur fonds complexes, vrai essai RTX 3070 8 Go, puis validation des imports et découpes Cricut.
