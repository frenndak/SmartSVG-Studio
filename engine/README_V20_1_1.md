# SmartSVG Studio V20.1.1 — Correction du mode dessin/photo/scan

## Périmètre

Mise à jour **additive** de V20.1 ; les pipelines V20, Florence-2/SAM2, matting, stickers et Cricut restent présents. La V20.2 reprendra le **chantier principal** avec raccordement des masques de segmentation IA à cette nouvelle branche.

## Correctifs vérifiés

1. **PNG avec transparence** : analyse des couleurs composites sur fond blanc (sans inventer de traits à partir des pixels RGB masqués), préservation bit à bit du RGBA original, même via le nœud ComfyUI si l'IMAGE contient quatre canaux. Attention : certains LoadImage ComfyUI livrent uniquement 3 canaux; dans ce cas l'alpha original doit être utilisé via une autre entrée ou la source directe.
2. **Découpe sticker** : agrandissement du canevas avant dilatation; la marge `marge_blanche_px` ne se perd plus sur les bords. `decalage_traits_impression_px` documente l'alignement du visuel avec le masque.
3. **SVG des traits** : rendu amélioré des traits fins par un liseré vectoriel autour des régions tracées ; les formes restent éditables, pas des calques sémantiques.
4. **Avertissements** : `pret_decoupe_personnage=false` et `validation_manuelle_obligatoire=true` même si un candidat de silhouette est produit. Aucun faux succès de segmentation.
5. **Fichiers** : protection du dossier de sortie contre les chemins contenant des liens symboliques ; nettoyage transactionnel si écriture échoue.
6. **Compatibilité** : ancien `SmartSVGLineArtV201` conservé ; nouveau `SmartSVGLineArtV2011` utilisable dans les deux workflows V20.1.1.

## Installer et utiliser

Fermer ComfyUI, déplacer l'ancienne version SmartSVG hors de `custom_nodes`, extraire **le dossier complet** `ComfyUI-SmartSVG-Studio-V20.1.1` dans `custom_nodes`, redémarrer puis charger :

- `example_workflows/SmartSVG_Studio_V20_1_1_LineArt_Express.json` pour un scan, un dessin ou une capture.
- `example_workflows/SmartSVG_Studio_V20_1_1_Photo_Ecran_Exemple.json` pour les photos d'écran.

Régler `cible_decoupe=carte` pour un rectangle de carte, `personnage` ou `sticker` **uniquement en mode brouillon**. Dans ce dernier cas, examiner le masque `personnage_CANDIDAT_A_VERIFIER.png` et le PNG `IMPRIMER_PUIS_DECOUPER_BROUILLON.png`, sans présumer d'une ligne de découpe correcte.

## Contraintes / limites

- Une photo d'écran moirée ne peut pas retrouver les pixels perdus dans le fichier original.
- La segmentation de la silhouette ne devient pas « sémantique » : les personnages aux lignes ouvertes restent des propositions.
- Les dimensions physiques de coupe ne sont pas calibrées : marges **en pixels**, pas en mm. Il faut vérifier la taille voulue dans Design Space.
- Pas de validation par webcam / scanner réel sous Windows, RTX 3070, poids IA, Design Space ou machine Cricut.
- Un contrôle automatique de SVG sans vérité terrain ne suffit pas à garantir la fidélité au dessin de départ.

## Vérifier

Dans le Python ComfyUI, depuis le dossier de l'extension : `python verify_package_v2011.py`. Consulter aussi `AUDIT_V20_1_1.md` et `SUITE_APRES_V20_1_1.md`.
