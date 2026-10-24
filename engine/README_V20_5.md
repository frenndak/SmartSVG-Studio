# SmartSVG Studio V20.5 — prévol fabrication Cricut

Version additive qui conserve les moteurs de photographie, Line Art, sticker et IA V20.4.

## Nouveautés
- `SmartSVGLineArtV205` : fonctionnement V20.4 + vérification Cricut non destructive.
- `SmartSVGCricutPreflightV205` : vérifie un projet existant, sans modèle IA.
- Dossier `09_PREFLIGHT_CRICUT_V20_5` : rapport JSON + aperçu de contour PNG (diagnostic uniquement).
- SVG : tailles `mm`, proportions `viewBox`, chemins ouverts / nombreux ; XML actif refusé.
- PNG : transparence, composants, trous, marges touchant les bords et résolution estimée.

## Importer dans Design Space
1. `01_*.png` : Imprimer puis découper, **une seule variante**, vérifier l'aperçu ; Design Space définit sa zone imprimable réelle et les repères.
2. `02_*.svg` : Découpe de base du contour seulement.
3. `03_*.svg` : Découpe de base de toutes les régions de traits ; les traits épais peuvent être découpés sur DEUX bords.
4. `04_*.svg` : Dessiner au stylo, seulement si un fichier stylo a été créé.

Une image multi-couches destinée à Imprimer puis découper doit être aplatie dans Design Space pour ne découper que la forme extérieure. Les dimensions physiques sont estimées ; le PNG n'impose pas de taille finale dans Design Space. La zone Print Then Cut n'est PAS égale au format A4 complet.

**Une silhouette produite par la segmentation IA reste un candidat à vérifier. Aucun contrôle logiciel ne prouve la qualité de la découpe réelle.**

## Workflows V20.5
- `SmartSVG_Studio_V20_5_LineArt_Protection.json`
- `SmartSVG_Studio_V20_5_Photo_Ecran.json`
- `SmartSVG_Studio_V20_5_Masque_Externe.json`
- `SmartSVG_Studio_V20_5_Silhouette_Strict.json`
- `SmartSVG_Studio_V20_5_Tous_Traits.json`
- `SmartSVG_Studio_V20_5_Controle_Export_Existant.json`

## Suite du chantier
V21 : consolidation des moteurs photo, line art, SVG et planches multi-stickers. Puis tests sur RTX 3070 8 Go et Cricut physique.
