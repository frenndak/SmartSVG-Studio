# SmartSVG Studio V21.11 — 24 octobre 2026

## Évolution principale

- Nouveau moteur de sélection de masques `smartsvg_ai/auto_masks_v2111.py` : privilégie un canal alpha réellement détouré, reconnaît des illustrations sur fond blanc uni et sépare les sujets de planches à bandes colorées. Il ne prétend pas reconnaître les scènes complexes sans IA.
- Possibilité de solliciter un fournisseur installé `SAM2Segment` de ComfyUI-RMBG **après** refus de l'heuristique simple (sauf si l'IA est obligatoire). Signature contrôlée au moment de l'appel par le pont historique ; une version incompatible échoue explicitement.
- Nouveau nœud `SmartSVGAutoMasksV2111` : IMAGE -> MASK + IMAGE + JSON ; les masques sont à vérifier dans l'éditeur V21.10 avant fabrication.
- Nouveau nœud `SmartSVGAutoExpressV2111` : cinq contrôles Express historiques ; en l'absence de masque, propose un détourage automatique puis fabrique PNG/SVG et dossier `00_IMPORTER_DANS_CRICUT`. En cas de doute, refuse l'export au lieu de présenter un rectangle comme silhouette.
- Le mode `Carte - visuel rectangulaire` reste utilisable sans IA ; c'est une découpe rectangulaire volontaire.
- Trois workflows V21.11 : Express automatique direct, automatique + correction manuelle, capture recadrée + correction.

## Non-régression et prudence

- Aucune modification des moteurs historiques de vectorisation, de fabrication PNG/SVG, HD et Cricut.
- Les anciens identifiants de nœuds et leurs ports restent inscrits au registre.
- Le moteur CV2 **ne recrée pas** les détails absents, ne garantit pas la précision des cheveux ou des objets qui se chevauchent et ne prédit pas le comportement interne de Design Space.
- Aucun téléchargement de modèle imposé par le paquet lui-même. Un modèle ComfyUI-RMBG peut demander un téléchargement lors du premier appel IA selon sa configuration.
