# SmartSVG Studio V19.9 — Développement et vérification

**Objectif :** permettre un second passage local ciblé sur des régions jugées difficiles, sans charge systématique de plusieurs IA ni adoption non fondée.

## Nouvelle architecture

1. Masques déjà fournis (prioritaires) **ou** détection Florence-2 guidée + segmentation SAM2/GroundingDINO du moteur existant.
2. Analyse par objet : surface, contour, fragments, alpha partiel, chevauchements.
3. Au plus 2 régions par défaut (limite 4) traitées séquentiellement par `BiRefNetRMBG`, variante `Lucida` par défaut, et libération du modèle entre passes si prise en charge.
4. Contrôle de validité, accord IoU, zones de désaccord (carte d'incertitude).
5. Modes : `diagnostic` / `proposition` = fichier de production **inchangé** ; `adopter_annotation` = adoption uniquement avec vérité terrain, +0.025 IoU et accord minimal entre les deux IA.
6. Rapport JSON et variantes PNG sauvegardés hors des dossiers de découpe.

## Contraintes

- La source RGB est limitée à 5 mégapixels et le lot des masques à 25 millions de pixels avant traitement matting.
- Nombre d'appels matting ≤4 ; valeurs NaN/infinies, modèles absents et masques non alignés refusés ou signalés.
- Le profil RTX3070 ne garantit pas à lui seul une consommation maximale de 8 Go. Le bridge libère chaque modèle entre les appels, mais la mémoire réelle et les éventuels OOM dépendent du provider et doivent être mesurés sur l'appareil.
- `Lucida` est un modèle de détourage général ; contrairement à un SAM guidé par boîte, il peut se tromper sur les régions à plusieurs objets. Il n'est jamais automatiquement promu sans annotation.
- Test GPU matériel non exécuté ; inférence réelle RMBG non vérifiée ici. Les tests utilisent des providers simulés.
- Le mode intégré photo peut revenir à l'export historique lorsque le second passage échoue ; aucun masque fictif n'est créé.

## Scénarios d'usage

- Photo femme + cadeau : commencer par `diagnostic`, vérifier si Lucida regroupe personnage et cadeau, puis noter les contours problématiques.
- Photo personnage + chopes : ne pas fusionner les mains et chopes ; comparer les cartes d'incertitude avant toute variante d'export.
- Planche des 12 escargots : conserver la voie sticker/vectorielle, second passage matting ignoré.
