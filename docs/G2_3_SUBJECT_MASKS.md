# SmartSVG Studio — G2.3 : masques par sujet et historique de remplacement

**Périmètre :** projets gérés G2.2, dépendances PR #19 → #18 → #14. Aucun changement des anciens nœuds, des ports ComfyUI ou de la baseline V21.15.2.

## Fonctionnalités

- Charger explicitement un masque PNG gris L8 : sélection blanche (pixel ≥128), fond noir.
- Associer ce masque à un sujet nommé (sujet_01, pikachu_02, etc.) d'un projet existant.
- Calculer la boîte utile depuis les vrais pixels sélectionnés, non depuis un rectangle estimé.
- Enregistrer les octets, empreintes, liens source/masque/sujet, bounding-box et une opération d'ajout/remplacement.
- Réouvrir le projet et lister/visualiser ses sujets, jusqu'à 32.
- Remplacer le masque d'un sujet sans changer les autres, avec sauvegarde précédente et contrôle d'empreinte de révision.
- Récupérer une précédente version intègre uniquement après confirmation et si le fichier actuel n'est plus valide.

## Contrats

Module engine/smartsvg_core/mask_inspection_g23.py : décode PNG gris 8 bits sans entrelacement, contrôle dimension source, CRC, zlib borné et filtres PNG 0–4. Retourne l'enveloppe des pixels ≥128 et le nombre de pixels sélectionnés.

Rejets : PNG non pris en charge (RGB/RGBA, indexé, interlacé), dimensions incompatibles, CRC, compression excessive, masque noir/vide ou entièrement blanc, nom de sujet invalide, empreinte de projet périmée, masque identique, format de projet déjà doté d'exports hors du périmètre.

Les enregistrements G1.2 Mask/Subject et l'archive G1.3 sont réutilisés, avec le secours G1.4. Le journal stocke SHA-256 précédent/nouveau et bbox, mais **ne constitue pas encore un système de traits de pinceau avec undo/redo complet** : seule la sauvegarde précédente conserve les anciens octets.

## Interface / API opt-in

Le panneau Express G2.2 ajoute un identifiant sujet, un choix de fichier masque, un bouton Enregistrer/corriger, la liste des sujets et la visualisation de leur masque en lecture seule.

- POST /smartsvg/g22/mask : nom projet, ID sujet, PNG masque, SHA-256 de révision.
- GET /smartsvg/g22/mask : aperçu du masque d'un sujet existant uniquement.

Ce sont les mêmes routes privées opt-in de G2.2, activables uniquement par SMARTSVG_ENABLE_PROJECT_API=1 sur un ComfyUI local/contrôlé. Les contrôles Origin + en-tête X-SmartSVG-UI ne remplacent pas l'authentification. Aucun chemin arbitraire fourni par le navigateur.

## Validation

Tests synthétiques : roundtrip exact image/masque, deux sujets indépendants, remplacement et bbox, historique, secours, ancienne révision, PNG vide/plein/RGB, mauvaises dimensions, CRC, filtres, décompression excessive et noms dangereux. Tests frontend existants complétés par le vrai formulaire masque et la vérification du SHA-256 attendu.

## Limites

- Pas de découpe vectorielle SVG garantie : la bbox n'est qu'une enveloppe, pas un tracé fermé.
- L'interface ne propose pas encore un pinceau pour peindre/corriger le masque sur l'image.
- Réouvrir un projet n'injecte pas automatiquement les images et masques dans le graphe ComfyUI.
- Pas de vérification réelle Windows ComfyUI, GPU RTX 3070, Design Space ou Cricut Explore 5.
- Les images privées de l'utilisateur ne sont pas publiées sur GitHub.

Suite : éditeur de masques visuel, réinjection contrôlée dans ComfyUI et essais physiques Cricut.
