# SmartSVG Studio V21.11.2 — Journal des changements

Base : archive de production V21.11.1, extraction propre.

## Ajouts

- Diagnostic des dépendances et de la signature du nœud RMBG/SAM2 sans exécuter ou télécharger de modèle (`SmartSVGReadinessV21112`).
- Nouveau nœud d'éditeur (`SmartSVGUnifiedEditorV21112`) : largeur en mm unique, liée à la sortie `FLOAT` pour Express ; diagnostic natif calculé avec cette largeur.
- Nouveau Express (`SmartSVGAutoExpressV21112`) : conserve les cinq réglages et les sorties, ajoute un état explicite de précontrôle Print Then Cut.
- Panneau ComfyUI non sérialisé « Mon sticker Cricut » avec état de fabrication et prochaines actions.
- Quatre workflows de démarrage dont un diagnostic et un parcours de capture à export initialement désactivé.
- Tests ciblés Python et JavaScript, vérificateur de paquet V21.11.2.

## Compatibilité

- Aucun moteur PNG/SVG, générateur HD, algorithme de segmentation ou contrôle Cricut historique modifié.
- Nœuds précédents conservés avec les mêmes IDs et les mêmes ports.
- `node_v2110.py` accepte deux paramètres internes facultatifs pour renseigner la nouvelle largeur QA ; l'interface de l'ancien nœud reste inchangée.
- `web/js/smartsvg_unified_v2110.js` prend en charge l'ID du nouveau nœud, sans modifier la sérialisation des corrections.

## À faire ensuite

Validation réelle des nœuds SAM2/RMBG disponibles sur le PC, essais sur RTX 3070 8 Go avec les sept exemples, inspection du rendu UI dans ComfyUI, et tests physiques Cricut Explore 5. La V21.12 devra ensuite fiabiliser le routage de segmentation des fonds complexes, pas multiplier les réglages Express.
