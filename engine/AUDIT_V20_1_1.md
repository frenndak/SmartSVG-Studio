# SmartSVG V20.1.1 — Contre-expertise technique et validation

Date : 22 octobre 2026. Source de départ : archive **V20.1 réelle**, conservée avec ses modules V20.

## Verdict

La V20.1.1 corrige des défauts reproductibles du module Line Art sans changer les moteurs historiques photo/stickers. **272 tests** de l'ensemble hérités et nouveaux passent sur CPU. La précision du détourage sémantique d'un personnage reste **non validée** tant que SAM2 / matting n'ont pas été exécutés et annotés.

## Défauts, corrections et tests de reproduction

| Défaut V20.1 | Conséquence | Correction V20.1.1 | Test |
|---|---|---|---|
| Canal alpha RGBA jeté pour l'analyse de source | Les pixels RGB entièrement transparents deviennent de faux traits | Composer le contenu transparent sur blanc pour l'analyse ; conserver `original_RGBA.png` octet par octet au niveau pixels | `test_fully_transparent_black_is_not_ink`, `test_source_rgba_preserved_bit_exact` |
| Nœud ComfyUI tronquant les entrées 4 canaux | Un `IMAGE` RGBA soumis au nœud perdait l'alpha | Conversion locale RGB/RGBA 3/4 canaux, sans changer le reste des nœuds | `test_alias_node_preserves_transparent_input` |
| Dilatation de marge sticker dans l'ancien canevas | Bande blanche tronquée au bord du dessin | Agrandir le canevas de `marge+2` de chaque côté **avant** dilatation | `test_sticker_offset_extends_canvas...`, `test_offset_border_detectable...` |
| Rendu SVG des lignes fines sous-couvrant le PNG source | Disparition/affaiblissement de traits après vectorisation | Conserver les régions SVG éditables et ajouter un bord de 1 pixel autour des tracés ; test de rendu avec CairoSVG si installé | `test_svg_stroke_preserves_thin_scan_lines` |
| Sortie avec silhouette de sujet très approximative | Risque d'interprétation « prêt à découper » | `validation_manuelle_obligatoire=true`, `pret_decoupe_personnage=false`, avertissements sur repli ou bord ouvert | `test_missing_subject_explicit_fallback_to_card`, `test_never_claims_ai...` |
| Dossier de sortie vide ou via lien symbolique | Écriture à un emplacement imprévu | Rejet précoce de chemins vides et des ancêtres symlink existants | `test_invalid_output_path_rejected`, `test_symlink_ancestor_rejected` |

## Vérification sur l'image réelle du dessin manga

Source : `1000077568.jpg` de **1152 × 1536 px** (photo d'écran). Carte détectée et recadrée en **681 × 1085 px**. L'image JPEG source est conservée dans les sorties via une copie RGB sans modification de pixels après décodage.

Mesure de vectorisation comparée au **même** PNG de traits issu de V20.1 :

- Rendu du SVG V20.1, IoU masque des pixels de traits : **0,8517**.
- Rendu du SVG V20.1.1, IoU masque des pixels de traits : **0,8980**.
- PNG de traits avant/après : **identique pixel par pixel**.
- Ce test mesure la fidélité du **SVG au PNG nettoyé**, et non au fichier natif du dessin ou au détourage idéal d'une personne.
- Exemple de temps CPU : **environ 1,04 s** pour une exécution Line Art carte sur ce système; il ne décrit pas les temps du PC RTX 3070 de l'utilisateur.

Pour un sticker avec marge **16 px**, PNG créé à **717 × 1121 px** (18 px de décalage de contenu par côté, marge 16 px + sécurité 2 px). La silhouette reste un **candidat géométrique à contrôler**, pas un contour certifié.

## Conformité et compatibilité

- Classes `SmartSVGLineArtV201` et nouvelle `SmartSVGLineArtV2011` enregistrées ; workflows V20.1 et antérieurs préservés.
- `verify_package.py` V20/V20.1 **laissé intact** pour préserver le manifeste historique V20. Un vérificateur `verify_package_v2011.py` contrôle séparément les nouveautés et leurs empreintes.
- Suite d'ensemble : **272 tests** ; le lot de référence V20 243 tests et la V20.1 15 tests n'ont pas été supprimés.
- Aucun appel IA, aucun benchmark GPU, aucune connexion Cricut physique dans cette campagne.

## Limites et suites

1. La détection du cadre demeure heuristique : elle peut manquer ou prendre le mauvais rectangle dans une interface complexe. Vérifier l'aperçu.
2. La suppression systématique d'une bande à la bordure d'un cadre reconnu peut supprimer des traits légitimes très proches du bord. La V20.2 pourra lier ce diagnostic à la segmentation sémantique pour préserver la silhouette.
3. Les traits vectorisés sont des surfaces monochromes éditables, **pas** des objets sémantiques séparés cheveux/visage/vêtements.
4. La bande blanche est exprimée en pixels : taille réelle et compatibilité Print Then Cut doivent être validées dans Design Space.
5. L'amélioration géométrique ne résout pas les superpositions, les traits interrompus en bas de page ni la qualité des masques SAM2.
6. La vérification des symlinks protège les chemins présents au moment du contrôle, mais ne prétend pas éliminer toutes les courses d'écriture dans un répertoire contrôlé par un autre processus.

**Prochain jalon : V20.2, raccordement Line Art ↔ segmentation IA V20**, puis reprise de la roadmap RTX 3070 et amélioration de qualité Cricut.
