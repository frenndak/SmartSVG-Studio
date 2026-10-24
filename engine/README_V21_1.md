# SmartSVG Studio V21.1 — Express fiabilisé

## Installation rapide

1. Fermer ComfyUI, sauvegarder l'ancien dossier SmartSVG **hors** de `custom_nodes`.
2. Extraire le dossier `ComfyUI-SmartSVG-Studio-V21.1` sous `custom_nodes`, puis redémarrer.
3. Charger `example_workflows/SmartSVG_Studio_V21_1_01_Express_Auto.json`.
4. Brancher `LoadImage → image`. Choisir le projet, la largeur, la qualité ; lancer `Queue Prompt`.
5. Lire le **résumé en français**. Ouvrir le répertoire `SmartSVG_V21_1_*` indiqué dans ce résumé.

## Cinq réglages après l'image

| Réglage | Utilisation |
|---|---|
| `dossier_sortie` | Vider le champ pour utiliser la sortie ComfyUI ; ou choisir un chemin explicite |
| `projet` | Auto, sticker sujet, planche 24, planche 12, cadre/affiche |
| `largeur_mm` | Taille du contenu avant marge ; vérifier ensuite dans Design Space |
| `qualite_ppp` | 300 ou 450 ppp, résolution d'export et **non** promesse de détails natifs |
| `ia_locale` | Désactivée, si disponible, obligatoire (sans masque = erreur) |

Entrée facultative : `masques_objets`, lot MASK conforme à la taille de l'image **originale**. Elle prend priorité sur l'IA interne. Le nom du modèle IA et l'état réel du GPU restent à vérifier sur le PC de l'utilisateur.

## Choix du fichier Cricut

- `..._IMPRIMER_DECOUPER...png` : importer en image imprimable ; contrôler taille et silhouette dans Design Space.
- `..._CONTOUR_SEUL.svg` : contour vectoriel extérieur, **ne contient pas tous les traits intérieurs**.
- Pour découper chaque trait ou dessiner au stylo, utiliser les anciens workflows spécialisés `V20_1_2` / Line Art : les opérations ne doivent pas être confondues.
- `..._DETOURE_TRANSPARENT.png` : meilleure copie raster de l'objet extraite au niveau de détail natif (si masque fourni).
- Planche de stickers : inspecter le nombre de composants **avant** de lancer l'impression et la découpe.

## Correctifs

- Alignement PNG imprimable ↔ SVG contour ↔ résolution 300/450 ppp, dans la limite des arrondis de pixels ; **Design Space peut réinterpréter la taille** lors de l'import.
- Recalcul des marges blanches **après ajout d'espace autour des masques**, même lorsque le sujet touche le bord de la source.
- Refus clair si IA obligatoire sans masque.
- Contrôle des dimensions et du budget des MASK **avant la copie GPU→CPU**.
- Publication atomique du projet, nettoyage des répertoires de staging à l'échec.
- Interface Express limitée à cinq réglages, synthèse de résultat lisible ; Expert V21 conservé.

## Important : limites

Ce correctif n'exécute ni les poids SAM2/BiRefNet ni une Cricut réelle. Le mode « sticker sujet » exige un masque valide pour les fonds complexes ; sinon il peut seulement fournir le visuel complet avec alerte. Sur une planche à fond noir/blanc, le moteur historique reste sensible aux contacts entre illustrations. Il ne certifie aucune découpe. Les métadonnées ppp ne garantissent pas la taille importée dans Cricut : il faut confirmer les millimètres dans Design Space.

L'export à 450 ppp d'une vignette peu définie ne restaure pas les détails absents de l'image source. L'agrandissement par interpolation ne constitue pas une super-résolution IA.
