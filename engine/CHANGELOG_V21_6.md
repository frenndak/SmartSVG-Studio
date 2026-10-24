# Journal V21.6

- Ajout du moteur `smartsvg_editor/strokes.py` et publication des aperçus `smartsvg_editor/previews.py`.
- Ajout de `SmartSVGMaskEditorV216` (MASK corrigé, image, diagnostic) sans modifier Express V21.5.1.
- Frontend optionnel `smartsvg_editor_v216.js` + modèle de validation `smartsvg_editor_model_v216.mjs`.
- Deux workflows démonstrateurs : masque PNG/alpha et peinture d'un masque initialement vide (Express muet au premier passage ; InvertMask natif pour la transparence PNG).
- Tests de sécurité du JSON, 24 objets/2 planches, persistance navigateur simulée, régression des anciens nœuds.
- Aucun changement à l'algorithme de vectorisation SVG historique.
