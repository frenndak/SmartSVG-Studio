# Audit indépendant de SmartSVG Studio V21.13.1 et correctif V21.13.2

**Date** : 24 octobre 2026. **Base** : archive V21.13.1 réelle, vérifiée en ZIP et extraite dans un répertoire propre.

## Résultats et découvertes

### P0 — Comparateur OpenCV optimiste (confirmé)

- V21.13.1 reconstruisait les polygones SVG avec `cv2.fillPoly`, qui n'est pas équivalent à un moteur SVG standard avec remplissage, antialias et règles de contours.
- Deux SVG générés ont été rasterisés indépendamment avec Inkscape et CairoSVG aux dimensions `viewBox`. Au seuil alpha 128/255, les silhouettes produites sont identiques pixel par pixel entre les deux logiciels.
- IoU escargot n° 1 : **0,87798 OpenCV** contre **0,83094 Inkscape/CairoSVG**.
- IoU Pokémon n° 1 : **0,80939 OpenCV** contre **0,69788 Inkscape/CairoSVG**.
- **Correction** : rendu standard optionnel ; en son absence le score est marqué approximatif et le verdict reste à vérifier.

### P1 — Générateur aléatoire global modifié (confirmé)

- `np.random.seed(2113)` modifiait le générateur partagé. `cv2.setRNGSeed(2113)` modifiait également l'état global d'OpenCV.
- **Correction** : remplacement de l'initialisation k-means globale par une palette déterministe utilisant `numpy.random.default_rng(seed)` et un ajustement local. Test : état aléatoire NumPy inchangé, même SVG aux exécutions répétées.

### P1 — SVG inattendus acceptés par le comparateur (prévention)

- Le comparateur V21.13.1 acceptait certains attributs de groupe, chemin et racine qu'il ne rendait pas lui-même (transform, opacity, styles). Le score pouvait ainsi décrire une géométrie différente du SVG effectif.
- **Correction** : validation stricte des attributs et `viewBox` avant tout appel à CairoSVG. Les ressources externes ne sont jamais autorisées dans le dialecte SmartSVG pris en charge.

### P1 — Qualité visuelle des calques encore insuffisante

- La vectorisation omet de nombreux petits blocs de couleur : **1375 petits contours pour l'escargot testé, 1077 pour le Pokémon testé** selon les diagnostics précédents.
- Des formes sont volontairement écartées pour limiter la complexité des chemins. Cette perte reste mesurable. La V21.13.2 ne prétend pas la corriger ; elle fiabilise le point de départ de la prochaine optimisation.
- Le SVG généré est **éditable**, mais pas un modèle multicouche sémantique parfait ni un SVG automatiquement prêt à la découpe.

## Vérifications effectuées

- ZIP V21.13.1 testé sans erreur de compression.
- Reproduction des différences sur les deux exemples réels, comparaison Inkscape et CairoSVG.
- Anciennes suites Python exécutées séparément (12 groupes, 720 tests), derniers tests Python complétés ; interface JS testée.
- Nouveaux tests : rendu standard, signalisation du fallback, déterminisme sans état global, rejet des transformations trompeuses, maintien des anciens nœuds.
- PNG Print Then Cut, SVG de contour, génération de planches : **algorithmes historiques inchangés**, pas de validation matérielle réelle.

## Priorités recommandées après V21.13.2

| Priorité | Suite | Critère mesurable |
|---|---|---|
| P0 | Améliorer les régions vectorielles manquantes | Augmenter IoU **sur rendu SVG standard**, sans explosion du nombre de chemins |
| P0 | Prévenir l'utilisateur des micro-découpes Cricut | Afficher formes sous taille minimale réelle et rappel « chaque calque devient une découpe » |
| P1 | Séparer géométrie imprimable / géométrie de coupe | Aucun chemin de couleur envoyé par erreur au mode Print Then Cut |
| P1 | Édition des fragments / calques en interface | Pouvoir inspecter et garder/supprimer un îlot explicitement |
| P1 | Tester sur le frontend ComfyUI, RTX 3070 et Design Space | Session native de bout en bout et preuve par fichiers et captures |

## Précautions

La comparaison à 128/255 choisit un seuil de rasterisation reproductible, **pas la physique de la lame**. Les exigences de Design Space changent avec la version, le matériel et les options sélectionnées. La découpe physique et l'intégration GPU restent non testées ici.
