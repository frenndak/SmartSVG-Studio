# SmartSVG Studio V21.11.1 — Contre-expertise corrective

**Base auditée :** archive complète V21.11. **Objectif :** corriger les vulnérabilités fonctionnelles identifiées sans changer les identifiants des anciens nœuds, les cinq réglages Express ni les moteurs historiques d'export PNG/SVG.

## Résultats — points P0/P1 corrigés

| Risque initial | Correctif en V21.11.1 | Preuve locale |
|---|---|---|
| P0 : perte d'alpha des PNG ouverts par `LoadImage` | Entrée facultative `alpha_loadimage` sur les deux nouveaux nœuds ; inversion du MASK natif (`1=transparent`) vers alpha sujet (`1=opaque`). Masque vide natif ignoré pour les JPEG/PNG opaques, y compris le masque sentinelle 64×64 entièrement nul renvoyé par certaines versions de `LoadImage`. | Test de cercle RGBA via sortie `IMAGE` RGB + `MASK` inversé ; contour obtenu sans IA ; fabrication jusqu'au PNG Print Then Cut. |
| P0 : quasi-rectangle avec 1 pixel manquant annoncé comme silhouette | Mesure de couverture du rectangle englobant (seuil conservateur 98,5 %) partagée entre moteur automatique et précontrôle PNG. | Un rectangle amputé d'un pixel est refusé comme détourage, et classé « cadre » si le PNG est volontairement importé comme carte. Un cercle demeure admis. |
| P1 : >32 îlots transformés en 0 îlot | Comptage explicite avant matérialisation des composantes ; rejet d'un masque de 33 îlots significatifs, signalement de leur nombre. | Cas à 33 îlots → `SUJET_1_TROP_D_ILOTS_33`. |
| P1 : masque transposé de mêmes dimensions totales | Vérification exacte `(hauteur, largeur)`, nombre de sujets, type, finitude et bornes avant export ; aussi sur entrée `MASK` externe. | 160×190 / 190×160 → rejet explicite avant fabrication. |
| P1 : allocations trop précoces sur planches multi-sujets | Budget des masques testé avant création des grandes couches ; stockage intermédiaire en `uint8`, conversion finale uniquement. | Test sous budget mémoire artificiellement abaissé → refus correct ; sur les escargots réels, 12 masques identiques SHA-256 à V21.11. |

## Protection des compatibilités

- **Cinq contrôles Express inchangés**. L'entrée `alpha_loadimage` est **facultative**, en supplément du port déjà disponible `masques_objets`.
- **IMPORTANT :** ces deux entrées ont des sémantiques différentes : `alpha_loadimage` attend le MASK inversé produit par `LoadImage`, tandis que `masques_objets` attend déjà un masque sujet (`1=à conserver`) qui ne doit **pas** être inversé.
- Deux workflows V21.11 sont reliés au MASK de `LoadImage`. Le workflow 03 comporte un recadrage, donc n'utilise pas directement le MASK non recadré ; il nécessite de transmettre un masque recalé à la même géométrie si l'image est transparente.
- Les anciens nœuds conservent leurs identifiants et leurs signatures ; seule la logique du précontrôle PNG hérité a été modifiée pour corriger les quasi-rectangles.
- La carte volontairement rectangulaire reste accessible avec le profil « Carte - visuel rectangulaire ».
- Les contours externes PNG/SVG des 12 escargots ne sont pas réinventés : les masques d'origine et ceux de la correction sont identiques par SHA-256.

## Tests

- **12 groupes Python historiques : 720 tests réussis**, lancés séparément pour éviter le blocage intermittent du lanceur global.
- **Suites Python récentes et nouvelles : 40 tests réussis** (dont 17 nouveaux tests adversariaux).
- **JavaScript : 43 tests réussis**.
- **803 tests réussis au total** dans ces familles, avant vérification finale de l'archive réextraite.
- Contrôle de bout en bout : source RGB + MASK inversé de `LoadImage` → masque positif → Express → PNG de fabrication → fichier du dossier `00_IMPORTER_DANS_CRICUT`.

## Restent hors validation / risques ouverts

1. **ComfyUI réel et Nodes 2.0 :** vérifier la présence et le raccordement des nouveaux ports facultatifs et les anciens workflows, hors navigateur simulé.
2. **Pont IA SAM2/RMBG :** le contrat strict du fournisseur historique est conservé pour *échouer de manière explicite* en cas d'incompatibilité ; aucune compatibilité garantie avec une version installée récente, ni inférence RTX 3070 8 Go testée. Ne pas déclarer les six images complexes automatiquement détourées.
3. **Inspecteur dimensionnel :** ses seuils en mm peuvent encore reposer sur une largeur de référence hypothétique de 40 mm si la largeur Express ne lui est pas communiquée.
4. **Performance GPU et RAM :** le budget de masques est désormais vérifié plus tôt, mais aucune preuve VRAM n'a été obtenue pour les modèles lourds.
5. **Design Space :** précontrôle local uniquement. La taille utile dépend de la feuille, de la machine et de Design Space. Test réel d'import et de découpe Explore 5 nécessaire.
6. **SVG :** le fichier SVG contour ne garantit pas des couches internes séparément éditables ; pour Print Then Cut, utiliser le **PNG RGBA aplati** du dossier dédié, sans superposer un SVG de contour.

## Verdict

**GO pour V21.11.1 comme base corrective des P0 et des garde-fous P1 vérifiables localement.** **Pas de certification de bout en bout** pour l'inférence IA, l'interface ComfyUI réelle ou la découpe physique Cricut. La prochaine étape pourra reprendre l'orchestration du fournisseur IA, son test matériel, les mesures physiques exactes et l'amélioration de la qualité des masques.
