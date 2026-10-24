# SmartSVG Studio V21.11.2 — Contre-expertise de stabilisation

**24 octobre 2026 — Base :** archive V21.11.1 extraite intégralement dans un répertoire vierge.

## Périmètre et résultat

La V21.11.2 introduit un parcours guidé et des outils de prévalidation, sans modifier les algorithmes historiques de segmentation ou de fabrication PNG/SVG. La compatibilité des anciens identifiants ComfyUI est maintenue. Il s'agit d'une validation **locale**, et non d'une certification de Design Space, de l'IA ou de la Cricut Explore 5.

## Passes d'audit

| Contrôle | Observation et décision |
|---|---|
| Intégrité de la base | Archive V21.11.1 intacte avant modification, tous les fichiers du manifeste V21.11.1 étaient présents |
| Contrats nœuds ComfyUI | Nouveaux IDs `SmartSVGReadinessV21112`, `SmartSVGUnifiedEditorV21112`, `SmartSVGAutoExpressV21112`. Tous les anciens IDs pointent vers les mêmes classes |
| Autodiagnostic IA | Absence de SAM2, contrat incompatible ou signature compatible : trois états séparés ; aucun modèle chargé, aucune inférence déclarée |
| Largeur réelle | L'éditeur transmet sa largeur `FLOAT` à Express et l'analyse géométrique utilise la même valeur, au lieu de supposer toujours 40 mm |
| Affichage | Panneau « Mon sticker Cricut », non sérialisé, effaçant un ancien résultat lorsque le nouveau est invalide. L'éditeur reste capable de s'ouvrir sur les deux IDs |
| Print Then Cut | Aucun changement du moteur de fabrication ; comparaison des PNG de fabrication, PNG d'import et SVG de contour octet par octet sur un sticker synthétique |
| Cas images réelles | 12/12 sujets détectés sur la planche d'escargots sans IA ; les six autres exemples complexes restent bloqués sans fournisseur IA valide |
| Workflows | Diagnostic, Express, planche corrigée, capture guidée ; liens et types validés statiquement |
| Régressions | 12 suites Python historiques, tests V21.11.1 et V21.11.2, tests JavaScript, extraction et vérification du ZIP |

## Correctifs et améliorations

**P0 — Fidélité des dimensions.** Dans les workflows `02` et `03`, la valeur `largeur_mm` utilisée pour les alertes de finesse provient du nouvel éditeur et est reliée à Express ; plus de divergence silencieuse entre 40 mm théoriques et la valeur saisie. Les anciens nœuds conservent les anciens ports.

**P1 — Lisibilité de l'état IA.** Un nœud d'autodiagnostic inspecte la signature `SAM2Segment` enregistrée sans la lancer. Il distingue « absent », « incompatible », « contrat compatible mais non exécuté », et n'affirme jamais que les poids téléchargés ou la VRAM de la RTX 3070 sont suffisants.

**P1 — Guidage utilisateur.** Un petit panneau non sérialisé, visible sur le nouveau Express, affiche un état de précontrôle local et indique l'action suivante. Il n'affirme pas qu'une silhouette choisie est sémantiquement correcte. Le workflow de capture conserve l'export désactivé tant que la correction n'a pas été examinée.

**P1 — Compatibilité.** Les nœuds historiques et les moteurs PNG/SVG restent accessibles. La recherche ComfyUI comporte toujours beaucoup d'anciens nœuds ; ceux-ci n'ont pas été masqués automatiquement car une intervention sur les classes historiques aurait un risque plus élevé pour les projets sauvegardés. Les nouveaux workflows sont les points d'entrée recommandés.

## Limitations restantes

1. Aucun test matériel du frontend ComfyUI local, de RMBG/SAM2 réel, de la RTX 3070 ou de la découpe Cricut Explore 5. La compatibilité d'une signature SAM2 ne valide ni l'existence du modèle ni son exécution.
2. Les cas photo/affiche/capture opaques non simples restent non segmentés sans IA. La V21.12 est nécessaire pour une intégration de segmentation avancée réellement testée.
3. Une découpe PNG acceptée localement peut encore sélectionner le mauvais objet ; inspection humaine et contrôle dans Design Space nécessaires.
4. Les seuils millimétriques de l'éditeur sont calculés sur les masques avant les éventuelles transformations de fabrication et leur interprétation dans Design Space.
5. La mise à jour n'est pas une migration destructive des anciens workflows. Les dizaines d'anciens nœuds restent disponibles.

## Suite recommandée

**V21.12 :** détecter les capacités exactes des fournisseurs IA installés sur le PC, adapter le pont de segmentation sans supposer l'existence d'un modèle unique, mesurer CPU/VRAM et valider sur les sept images complexes, avant toute promesse de « tout automatique ».
