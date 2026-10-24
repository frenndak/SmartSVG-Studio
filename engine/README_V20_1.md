# SmartSVG Studio V20.1 — Dessin photographié / scan / line-art

**Statut : alpha validée sur CPU pour le recadrage, le nettoyage, l'extraction de traits et les SVG.** Les résultats de silhouette *personnage* sont **des propositions géométriques à examiner** ; l'IA sémantique / SAM2 ne s'exécute pas dans ce nouveau mode CPU.

## Pourquoi ce module ?

Le pipeline V20 de photos et stickers reste intégralement présent. La V20.1 **ajoute** un nœud dédié aux dessins en noir et blanc photographiés, scannés ou issus de captures d'écran. Le cas de référence est la photo d'un écran présentant un personnage manga dans une carte rectangulaire, avec moiré et interface parasite.

## Installation

1. Fermer ComfyUI et retirer l'ancien dossier SmartSVG de `custom_nodes` (le sauvegarder en dehors de `custom_nodes`). Ne pas garder deux versions chargées.
2. Décompresser `ComfyUI-SmartSVG-Studio-V20.1` dans `custom_nodes`.
3. Conserver ComfyUI-RMBG pour les traitements photo V20 ; il n'est **pas nécessaire** pour le nouveau nœud Line Art CPU.
4. Redémarrer ComfyUI, ouvrir `example_workflows/SmartSVG_Studio_V20_1_LineArt_Express.json`.
5. Remplacer le nœud `LoadImage` par ton dessin, choisir le dossier global de sortie, puis lancer l'exécution.

### Paramètres

- `source`: `auto`, `scan`, `photo`, `capture_ecran`, `photo_ecran` (décrit la provenance ; le traitement actuel est identique pour ces sources).
- `cible_decoupe`: `carte` (le plus sûr), `personnage` ou `sticker` (proposition expérimentale).
- `nettoyage`: `doux` (plus de détails) ou `fort` (réduit les traits faibles et du bruit).
- `corriger_perspective`: applique une homographie si un cadre a été reconnu.
- `marge_blanche_px`: dilatation du masque de sticker, exprimée en **pixels locaux** (pas en millimètres).

### Fichiers de sortie

Le dossier global choisi contiendra `LineArt_V20_1_<id>/` :

- `01_SOURCE/original_RGB.png` — pixels RGB source conservés.
- `02_ZONE_UTILE/carte_redressee.png` — carte recadrée et corrigée si détectée, sinon image entière.
- `03_NETTOYAGE/gris_corrige_{doux,fort}.png` — gris avec fond compensé, pas reconstruction sémantique.
- `04_LINEART/traits_{fins,cricut}.png` — masques de traits noirs en blanc sur fond noir (binaires) ; le panneau QA affiche une inversion noir sur blanc.
- `05_CONTOURS/cadre.png` — masque rectangulaire de la zone recadrée.
- `05_CONTOURS/personnage_CANDIDAT_A_VERIFIER.png` — si une forme principale a été estimée.
- `05_CONTOURS/masque_selectionne.png` et `IMPRIMER_PUIS_DECOUPER_BROUILLON.png` — prévisualisation PNG RGBA **non certifiée comme ligne de coupe Cricut**.
- `06_SVG/traits_vectoriels.svg` — tracé vectoriel des régions encrées, monochrome. Éditable en tant que chemins, **pas séparé en cheveux, visage, habits**.
- `06_SVG/contour_selectionne.svg` — bord du masque cible, à vérifier avant de couper.
- `07_QA/avant_apres.png` — photo redressée, grayscale nettoyée et line-art.
- `rapport_v20_1.json` — géométrie, statut de contour, tailles et limites.

Le nom `BROUILLON` et `CANDIDAT_A_VERIFIER` est intentionnel : pour ton dessin, le buste se termine en bas du cadre. Aucun algorithme purement géométrique ne peut prouver sa silhouette réelle sous l'image.

## Vérification manuelle Cricut

1. Utiliser de préférence le PNG source ou un **scan réel / capture d'écran**, lorsqu'ils existent.
2. Sur le mode `carte`, vérifier le rectangle corrigé et importer le PNG d'essai dans Design Space.
3. Sur `personnage` ou `sticker`, examiner `personnage_CANDIDAT_A_VERIFIER.png` (oreilles, cheveux, contours du buste, coupure en bas) et `rapport_v20_1.json`.
4. Si la forme est incorrecte, utiliser le masque externe d'un modèle de segmentation dans le pipeline photo V20, ou corriger le masque dans un éditeur. Ne pas lancer la découpe en faisant confiance à la forme géométrique seule.
5. Vérifier dimensions et découpe d'essai physique. Aucune validation matérielle n'est incluse.

## Limites connues

- Le cadrage automatique repose sur des rectangles détectables ; une interface chargée ou un dessin sans cadre peut déclencher l'analyse de l'image entière.
- Sur les photos d'écrans, certains détails perdus par moiré ou défocalisation ne sont pas récupérables.
- Le SVG est une vectorisation **des pixels nettoyés**, pas une image 100 % fidèle au dessin original.
- L'algorithme de silhouette géométrique peut remplir des zones où il n'y a pas réellement de sujet, particulièrement sur des croquis incomplets.
- Les modes `source` sont disponibles pour l'expérience utilisateur, mais il n'y a pas de détecteur neuronal universel de type de source en V20.1.

## Continuité du développement

**Cette version est une branche ajoutée au socle V20 ; elle ne remplace pas la roadmap IA du projet.** Prochaine étape : contre-expertise de V20.1 (qualité scan/photo réelle, filtres, SVG, contours et QA), puis reprise des optimisations Florence-2, SAM2, BiRefNet, comparaison multi-modèles, VRAM 8 Go et validation Cricut physique. Voir `ROADMAP_APRES_V20_1.md`.

## Tests

`python verify_package.py` à partir du dossier extrait, avec le Python de ComfyUI.
