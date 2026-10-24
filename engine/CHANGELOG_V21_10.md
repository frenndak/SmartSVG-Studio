# SmartSVG Studio V21.10 — Notes de version

- **Nouveau :** nœud `SmartSVGUnifiedEditorV2110` (IMAGE + MASK facultatif → MASK corrigé, IMAGE, diagnostic).
- **Nouveau :** un seul panneau natif pour navigation 100 %, zoom 1 600 %, correction +/−, choix de sujet, alertes localisées et annuler/rétablir.
- **Nouveau :** corrections graphiques enregistrées dans le workflow (`retouches_json`) et rejouées par Python à la résolution d'origine.
- **Correctif :** les aperçus natifs publient les masques **avant** les retouches pour empêcher tout double affichage au second lancement.
- **Compatibilité :** anciennes classes, moteurs Express, cinq réglages, anciens workflows et dossier `00_IMPORTER_DANS_CRICUT` inchangés.
- **Installation :** trois nouveaux workflows V21.10 (capture manuelle, PNG alpha, planche 12 sujets).
- **Test :** comparaison intégrale SHA-256 de PNG/SVG de fabrication avec et sans passage V21.10 lorsqu'aucune retouche n'est appliquée.
- **Limites :** frontend ComfyUI réel, IA GPU et découpe Cricut physique encore non validés.
