# Contre-expertise indépendante SmartSVG Studio V19.5.2

**Base examinée :** archive installable V19.5.1 réellement disponible, pas un résumé des versions. Audit du code `photo_contacts_v195.py`, `photo_geometry_v191.py`, nœuds ComfyUI, workflows Express/Expert, tests et deux images complexes fournies.

## Défauts reproduits

| Sévérité | Défaut V19.5.1 | Preuve | Correctif V19.5.2 |
|---|---|---|---|
| P1 | Masques uint8 0/1 interprétés comme vides | 255 pixels partagés réellement, 0 dans le diagnostic V19.5.1 | Support des deux encodages ; sortie 0/255 normalisée |
| P1 | Fuite par lien symbolique au niveau du dossier des masques | `03_MASQUES` symlink externe accepté par `_mask_path_inside_root` | Racine de confiance liée au staging et refus des symlinks |
| P1 | Pixels semi-transparents non couverts par la base imprimable | Masque synthétique : 814 pixels visibles sans alpha imprimable lorsque marge = 0 | Sous-couche opaque couvrant tous les pixels alpha non nuls ; contrôle fail-closed |
| P2 | Allocation de masque PNG volumineux avant vérification du budget | Lecture complète de l'image lors du `np.asarray` | Inspection du mode, des dimensions et de la somme des pixels dans l'en-tête PNG avant décodage |
| P2 | Contrôle incomplet des dimensions des masques par rapport à la source | Loader comparait les masques entre eux, pas explicitement à l'original | Validation de la forme attendue avant décodage |

## Validation des corrections

- **140 tests automatisés réussis** : 127 tests antérieurs et 13 tests ajoutés (encodages, alpha, chemins, taille/mode PNG, rollback, manifeste).
- Sur deux masques binaires normaux, six fichiers historiques (`MASQUE`, `DETOURE`, `CRICUT_TEST`) ont des octets **strictement identiques** entre V19.5.1 et V19.5.2.
- Sur les deux vraies images complexes : pixels originaux conservés, zéro extraction en mode diagnostic sans masques IA, empreintes de manifeste valides.
- Sur une forme à transparence progressive sans marge : couverture du masque imprimable passée de **814 pixels perdus à zéro** dans le test synthétique.

## Points restant hors validation

- Le moteur ne sait **pas** quel objet passe devant l'autre dans des masques superposés ; l'attribution géométrique reste exploratoire.
- L'inclusion des pixels semi-transparents dans la silhouette blanche peut créer de très petites découpes indépendantes : contrôler le rapport d'îlots et prévisualiser dans Design Space.
- L'inférence réelle de Florence-2/SAM2 sur la RTX 3070 8 Go n'est pas vérifiée ; aucun score de qualité de détourage photo réel n'est déclaré.
- Aucune impression, calibration ou découpe mécanique avec Cricut Explore n'a été effectuée dans cet environnement.
- Le changement de `CRICUT_TEST.png` en présence d'alpha faible est **intentionnel** ; les images détourées source restent identiques et les masques binaires classiques restent identiques.

## Priorités techniques suivantes

1. Vérifier la stabilité des nœuds externes sur la véritable installation ComfyUI-RMBG et les poids disponibles.
2. Construire un banc d'essai basé sur de **vrais masques** de la femme, du cadeau, du personnage et des chopes, avec annotation de vérité-terrain.
3. Ajouter une alerte de *micro-composantes imprimables* et un mode sûr qui conserve les cheveux sans multiplier les découpes parasites.
4. Comparer SAM2, matting spécialisé et masques d'objets superposés sous contrainte de 8 Go VRAM.
